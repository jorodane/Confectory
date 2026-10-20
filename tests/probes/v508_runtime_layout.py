"""Compare the real EditorHome host with the supplied v508 prototype in isolated browsers.

The prototype runs only as a local reference fixture. Its demo providers never supply
runtime state. The production host uses temporary storage and an unused loopback URL;
this probe does not submit a project, log in, or send an inference request.
"""
import functools
import hashlib
import http.server
import json
import os
import pathlib
import signal
import subprocess
import sys
import tempfile
import threading
import time
import zipfile

from playwright.sync_api import expect, sync_playwright

repo, report_path, output = map(pathlib.Path, sys.argv[1:4])
repo = repo.resolve()
output.mkdir(parents=True, exist_ok=True)
report = json.loads(report_path.read_text())
assert report['tool']['ok']
expect.set_options(timeout=30000)
widths = [(1440, 1000), (900, 760), (600, 800)]
errors, external, captures, blocked_reference_fonts = [], [], [], []
reference_zip = repo / 'reference/site-ui/Confectory-Editor-Prototype-v508.zip'
assert hashlib.sha256(reference_zip.read_bytes()).hexdigest() == 'b306ce4deff9616c4107ae224443d864f8fce0f52cf3c3e158de8745c17c659f'

with tempfile.TemporaryDirectory(prefix='confectory-v508-layout-') as temporary:
    owned = pathlib.Path(temporary)
    reference = owned / 'reference'
    reference.mkdir()
    with zipfile.ZipFile(reference_zip) as archive:
        for item in archive.infolist():
            prefix = 'Confectory-v508/dist/'
            if item.is_dir() or not item.filename.startswith(prefix):
                continue
            relative = pathlib.PurePosixPath(item.filename[len(prefix):])
            assert not relative.is_absolute() and '..' not in relative.parts
            target = reference.joinpath(*relative.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(item))
    assert (reference / 'style.css').read_bytes() == (repo / 'examples/editor-home/ui/style.css').read_bytes()
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(reference))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    env = os.environ.copy()
    env.update(CONFECTORY_UI='web', CONFECTORY_EDITOR_REPO=str(repo),
               CONFECTORY_HOME_STORAGE=str(owned / 'storage'), CONFECTORY_ENTRY_STORAGE=str(owned / 'storage'),
               CONFECTORY_MCP_DIRECTORY=str(owned / 'instances'))
    env.pop('CONFECTORY_WEB_PROJECT', None)
    if env.get('CONFECTORY_DOTNET'):
        env['PATH'] = str(pathlib.Path(env['CONFECTORY_DOTNET']).parent) + os.pathsep + env['PATH']
    log_path = output / 'layout-host.log'
    with log_path.open('w') as log:
        host = subprocess.Popen(report['run'], cwd=repo, env=env, stdout=log,
                                stderr=subprocess.STDOUT, start_new_session=True)
        try:
            for _ in range(600):
                urls = [line.split(' ', 1)[1] for line in log_path.read_text().splitlines()
                        if line.startswith('CONFECTORY_WEB_UI ')]
                if urls:
                    break
                assert host.poll() is None, log_path.read_text()
                time.sleep(.1)
            else:
                raise AssertionError('actual host startup timeout')
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
                runtime = browser.new_page(viewport={'width':1440, 'height':1000})
                source = browser.new_page(viewport={'width':1440, 'height':1000})
                runtime_origin = urls[-1].split('/#')[0]
                reference_origin = 'http://127.0.0.1:' + str(server.server_port)
                def route_for(origin, reference_page=False):
                    def route(intercept):
                        if intercept.request.url.startswith(origin) or intercept.request.url.startswith('data:'):
                            intercept.continue_()
                        else:
                            if reference_page and intercept.request.url.startswith('https://fonts.googleapis.com/'):
                                blocked_reference_fonts.append(intercept.request.url)
                            else:
                                external.append(intercept.request.url)
                            intercept.abort()
                    return route
                for page, origin in [(runtime, runtime_origin), (source, reference_origin)]:
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    page.route('**/*', route_for(origin, page == source))
                runtime.goto(urls[-1])
                source.goto(reference_origin)
                source.evaluate('db.connected=false;db.extraAgents=[];showStart()')
                for page in (runtime, source):
                    expect(page.locator('.welcome')).to_have_attribute('aria-busy', 'false')

                def capture(name, selector, same_width=True):
                    for width, height in widths:
                        row = {'screen':name, 'width':width, 'height':height, 'bounds':{}}
                        for label, page in [('reference', source), ('runtime', runtime)]:
                            page.set_viewport_size({'width':width, 'height':height})
                            page.wait_for_timeout(300)
                            element = page.locator(selector)
                            expect(element).to_be_visible()
                            bounds = element.bounding_box()
                            assert bounds and bounds['x'] >= -1 and bounds['x'] + bounds['width'] <= width + 1, (name, label, bounds)
                            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (name, label, width)
                            row['bounds'][label] = bounds
                            page.screenshot(path=str(output / f'{label}-{name}-{width}.png'))
                        if same_width:
                            assert abs(row['bounds']['reference']['width'] - row['bounds']['runtime']['width']) <= 2, row
                        captures.append(row)
                    for page in (runtime, source):
                        page.set_viewport_size({'width':1440, 'height':1000})

                capture('start', '.welcome-inner')
                runtime.locator('#later').click()
                expect(runtime.locator('.startup-flight-layer')).to_have_count(0)
                source.evaluate('db.projects=[];db.favoriteProjectIds=[];db.extraAgents=[];helpers.splice(0,helpers.length);showHome()')
                capture('home', '.home-main')
                for page in (runtime, source):
                    page.locator('#add-agent').click()
                capture('agent', '.agent-connect-modal')
                source.locator('[data-close]').click()
                runtime.get_by_role('button', name='OpenAI Responses', exact=True).click()
                dialog = runtime.get_by_role('dialog', name='Agent 추가', exact=True)
                for key, value in [('model','layout-owned'), ('endpoint','http://127.0.0.1:1/responses'), ('credentialReference','')]:
                    dialog.locator(f'[data-connection-field="{key}"]').fill(value)
                dialog.locator('[data-agent-register]').click()
                expect(dialog.locator('[data-agent-registration-state]')).to_contain_text('Agent 등록됨')
                dialog.locator('[data-connection-cancel]').click()
                expect(dialog).to_have_count(0)
                source.evaluate("db.mainAgentName='OpenAI Responses';showHome()")
                for page in (runtime, source):
                    page.locator('#add-helper').click()
                capture('helper-add', '.helper-create-modal')
                source.locator('[data-close]').click()
                runtime.locator('#participant-name').fill('Owned layout Helper')
                runtime.locator('#participant-short-description').fill('Layout comparison')
                runtime.locator('#participant-description').fill('Owned fixture')
                runtime.locator('[data-v508-helper] button[type=submit]').click()
                expect(runtime.locator('[data-v508-helper]')).to_have_count(0)
                source.evaluate("helpers.push({id:'owned-layout',name:'Owned layout Helper',shortDescription:'Layout comparison',description:'Owned fixture',agentId:'main',initial:'O',color:'blue',workers:[]});showHome()")
                capture('sidebar', '.home-side')
                for page in (runtime, source):
                    page.locator('#new-project').click()
                capture('project', '.project-create-modal')
                for label, page in [('reference', source), ('runtime', runtime)]:
                    page.set_viewport_size({'width':600, 'height':800})
                    modal = page.locator('.project-create-modal')
                    modal.evaluate('element => element.scrollTop = element.scrollHeight')
                    footer = modal.locator('.project-create-footer')
                    expect(footer).to_be_in_viewport()
                    page.screenshot(path=str(output / f'{label}-project-footer-600.png'))
                    page.set_viewport_size({'width':1440, 'height':1000})
                    modal.evaluate('element => element.scrollTop = 0')
                for page in (runtime, source):
                    page.locator('[data-project-tab=packs]').click()
                capture('project-packs', '.project-create-modal')
                assert not errors, errors
                assert not external, external
                browser.close()
        finally:
            if host.poll() is None:
                os.killpg(host.pid, signal.SIGTERM)
                host.wait(timeout=15)
            server.shutdown()

evidence = {'referenceZipSha256':hashlib.sha256(reference_zip.read_bytes()).hexdigest(),
            'fullStylesheetIdentical':True, 'actualRuntime':report['run'], 'captures':captures,
            'pageErrors':errors, 'externalRequests':external, 'blockedReferenceFonts':blocked_reference_fonts,
            'projectSubmitted':False,
            'differences':['Only the two real adapters appear in Agent setup; prototype mock versions are not used.',
                           'Sidebar reflects registered configurations and actual Helpers; no seeded users, news or live status.',
                           'Helper import is an added real action. Image/random generation is disabled without a provider contract.',
                           'Project location uses native folder tickets; the web fixture has no native picker. Only the actual starter pack is offered.']}
(output / 'layout-comparison.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2))
print('PASS v508 reference/runtime rendered comparison: 7 screens at 1440/900/600, no horizontal overflow, identical full source stylesheet, zero page errors/external requests')
