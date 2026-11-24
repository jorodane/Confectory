#!/usr/bin/env python3
"""Use both production launch modes of an extracted Linux package.

Use the Xorg, SDK and local fixture image from editor_linux_package_x11.py.
The installed programs, browser and driver run as the same unprivileged UID
in one container with no external network or source checkout. Only these test
drivers are separately mounted.
"""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

INSTALL = '/opt/Confectory Linux'
TITLE = 'Packaged Logic Code'
OUTPUT = 'Packaged Logic Code ran'


def listeners():
    endpoints = set()
    for family in ('tcp', 'tcp6'):
        with open('/proc/net/' + family) as rows:
            next(rows)
            endpoints.update((family, row.split()[1]) for row in rows if row.split()[3] == '0A')
    return endpoints


@contextmanager
def open_packaged_logic(browser):
    from editor_navigation import goto_editor
    env = dict(os.environ, CONFECTORY_WEB_PORT='1')
    with subprocess.Popen([INSTALL + '/run', '--logic-code'], start_new_session=True, env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as host:
        address, page = None, None
        try:
            with selectors.DefaultSelector() as reader:
                reader.register(host.stdout, selectors.EVENT_READ)
                deadline = time.monotonic() + 30
                captured = b''
                while time.monotonic() < deadline:
                    if not reader.select(max(0, deadline - time.monotonic())):
                        break
                    data = os.read(host.stdout.fileno(), 4096)
                    if not data:
                        break
                    captured += data
                    ready = next((line for line in captured.splitlines(keepends=True)
                                  if line.startswith(b'CONFECTORY_WEB_UI ') and line.endswith(b'\n')), None)
                    if ready:
                        address = ready.decode().split()[1]
                        break
            assert address, captured.decode(errors='replace')
            origin, _ = address.split('/#', 1)
            endpoint = urllib.parse.urlsplit(origin)
            assert endpoint.scheme == 'http' and endpoint.hostname == '127.0.0.1'
            assert listeners() == {('tcp', f'0100007F:{endpoint.port:04X}')}
            request = urllib.request.Request(origin + '/api/request', data=b'{"op":"mount"}',
                                             headers={'Content-Type': 'application/json'})
            try:
                urllib.request.urlopen(request, timeout=5)
            except urllib.error.HTTPError as error:
                assert error.code == 403
            else:
                raise AssertionError('Unauthenticated browser RPC was accepted')
            page = browser.new_page(viewport={'width': 1800, 'height': 1200})
            external, errors = [], []

            def route_owned(route):
                if route.request.url.startswith(origin + '/'):
                    route.continue_()
                else:
                    external.append(route.request.url)
                    route.abort()

            page.route('**/*', route_owned)
            page.on('pageerror', lambda error: errors.append(str(error)))
            goto_editor(page, address)
            yield page
            assert not errors and not external, (errors, external)
        finally:
            if page is not None:
                page.close()
            if host.poll() is None:
                # A terminal Ctrl+C addresses the foreground launcher and engine together.
                os.killpg(host.pid, signal.SIGINT)
            try:
                assert host.wait(timeout=25) == 0, 'Packaged host did not close cleanly'
            except subprocess.TimeoutExpired:
                os.killpg(host.pid, signal.SIGKILL)
                host.wait(timeout=5)
                raise
    assert not listeners(), 'The loopback listener survived normal editor shutdown'


def browser_workflow(manifest, namespace, marker):
    from playwright.sync_api import expect, sync_playwright
    from editor_logic_workflow import edit_body, find_project_item, open_main, review, run_from_dock
    expect.set_options(timeout=30000)
    assert os.geteuid() != 0 and not Path('/workspace').exists()
    assert not listeners()
    source, body = manifest.parent / 'main.csbody', manifest.parent / 'main_body.celem'
    info = manifest.parent / 'elements/ProjectInfo.celem'
    original = (source.read_bytes(), body.read_bytes())
    source_text = f'System.IO.File.WriteAllText({json.dumps(str(marker))}, "{OUTPUT}");\nreturn 0;'

    def open_recent(page):
        card = page.locator('#home-projects [data-enter]').filter(has_text=TITLE)
        expect(card).to_have_count(1)
        card.click()
        expect(page.locator('.work-body')).to_be_visible()

    with sync_playwright() as playwright:
        options = dict(executable_path='/usr/lib/chromium/chromium',
                       args=['--no-sandbox', '--disable-gpu'],
                       ignore_default_args=['--disable-dev-shm-usage'])
        with playwright.chromium.launch(**options) as browser, open_packaged_logic(browser) as page:
            open_recent(page)
            manifest_before = manifest.read_bytes()
            find_project_item(page, namespace + '::ProjectInfo', '개념')
            info_window = page.locator('.window[data-key=schema]')
            info_review = review(page, info_window.locator('[data-element-action=confirm]'))
            assert not info.exists() and manifest.read_bytes() == manifest_before
            info_review.locator('#confirm').click()
            expect(info_review).to_be_hidden(timeout=120000)
            assert TITLE in info.read_text()
            info_window.locator('[data-close]').first.click()
            confirmed_info, confirmed_manifest = info.read_bytes(), manifest.read_bytes()

            panel = open_main(page, namespace + '::Main')
            expect(panel.locator('[data-native-source]')).to_have_value('return 0;\n')
            panel.locator('[data-native-convert]').click()
            expect(panel.locator('.bp-status')).to_contain_text('C# 미리보기')
            panel.locator('[data-bp-save]').click()
            expect(panel.get_by_role('tab', name='논리 코드', exact=True)).to_be_visible(timeout=120000)
            edit_body(page, panel, source_text, change=True)
            panel.locator('[data-bp-save]').click()
            expect(panel.locator('.bp-status')).to_have_text('저장됨', timeout=120000)
            submit = panel.locator('[data-bp-complete]')
            first_review = review(page, submit)
            first_review.locator('[data-reject]').click()
            expect(first_review).to_be_hidden()
            assert (source.read_bytes(), body.read_bytes()) == original
            assert manifest.read_bytes() == confirmed_manifest
            final_review = review(page, submit)
            final_review.locator('#confirm').click()
            expect(final_review).to_be_hidden(timeout=120000)
            assert source.read_bytes() == original[0] and info.read_bytes() == confirmed_info
            assert 'blueprint common' in body.read_text()
            run_from_dock(page, marker, OUTPUT)
        print('PASS package Logic Code card Save, Review cancel, Confirm, actual Run and clean shutdown', flush=True)

        with playwright.chromium.launch(**options) as browser, open_packaged_logic(browser) as page:
            open_recent(page)
            panel = open_main(page, namespace + '::Main')
            edit_body(page, panel, source_text, change=False)
            run_from_dock(page, marker, OUTPUT)
        print('PASS fresh packaged host and Chromium reopen Recent, read the same card and run it again', flush=True)


def test_package(package, image):
    import re
    from playwright._impl._driver import compute_driver_executable
    from editor_linux_package_x11 import extracted_package, installed_editor
    scripts = Path(__file__).resolve().parent
    test_files = (Path(__file__).resolve(), scripts / 'editor_logic_workflow.py',
                  scripts.parent / 'web/editor_navigation.py')
    mounts = [(path, '/test/' + path.name, True) for path in test_files]
    node, _ = compute_driver_executable()
    mounts += [(sys.prefix, sys.prefix, True), (Path(node).resolve(), '/test/node', True),
               ('/usr/lib/chromium', '/usr/lib/chromium', True)]
    with tempfile.TemporaryDirectory(prefix='cflogic-') as scratch:
        case = Path(scratch)
        extracted = extracted_package(package, case)
        with installed_editor(case / 'sdk', extracted, image, sdk=True, extra_mounts=mounts, shm_size="512m") as (app, projects):
            app.launch([INSTALL + '/run'])
            assert not app.state()['model']['cards'] and not app.state()['model']['helperAgents']['agents']
            created = app.create(TITLE, '', projects)
            manifest = Path(created['path'])
            assert manifest.is_relative_to(projects) and not app.listeners()

            # A live GTK owner must prevent a second surface from taking its profile.
            refused = subprocess.run(app.command([INSTALL + '/run', '--logic-code']),
                                     capture_output=True, text=True, timeout=20)
            assert refused.returncode and 'CONFECTORY_WEB_UI ' not in refused.stdout
            assert 'owner.lock' in refused.stderr
            app.close()
            print('PASS packaged GTK Later and native folder creation, duplicate Logic Code denied', flush=True)

            result = subprocess.run(app.command([sys.executable, '/test/' + test_files[0].name,
                                                  '--browser', str(manifest), created['namespace'],
                                                  str(app.home / 'logic-result.txt')], PLAYWRIGHT_NODEJS_PATH='/test/node',
                                                 DEBUG=os.environ.get('DEBUG', '')),
                                    capture_output=True, text=True, timeout=360)
            redact = lambda text: re.sub(r'(http://127\.0\.0\.1:\d+/#)[0-9a-f]{32}', r'\1[redacted]', text)
            print(redact(result.stdout), end='', flush=True)
            assert result.returncode == 0, redact(result.stderr)


if __name__ == '__main__':
    if sys.argv[1] == '--browser':
        browser_workflow(Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4]))
    else:
        test_package(Path(sys.argv[1]).resolve(), sys.argv[2])
