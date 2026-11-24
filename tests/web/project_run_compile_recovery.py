"""Use the actual editor to confirm a contract on one target and run another."""

import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager

from playwright.sync_api import expect, sync_playwright

from editor_navigation import goto_editor

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'gui'))
from editor_logic_workflow import edit_body, find_project_item, open_main


def fixture(root, repo, title, marker):
    project = root / title
    project.mkdir()
    ns = 'RunRecovery.' + title
    shape = ns + '::Shape'
    symbol = lambda identity: 'E' + hashlib.sha256(json.dumps(identity).encode()).hexdigest()[:24]
    nominal = f'Confectory.Information.{symbol(ns)}.{symbol(shape)}'
    (project / 'project.cpack').write_text(f'''project {ns} version "1" {{ standalone true;
    registry Confectory.Build.DotNet {json.dumps(str(repo / 'targets/dotnet/pack.cpack'))};
    dependency Confectory.Build.DotNet version "0.1.0";
    target desktop Confectory.Build.DotNet::Linux; target portable Confectory.Build.DotNet::Portable;
    entry {ns}::Main;
    element Main function "Main.celem"; element MainBody implementation "MainBody.celem";
    element Make function "Make.celem"; element MakeBody implementation "MakeBody.celem";
    element Spare function "Spare.celem"; element SpareBody implementation "SpareBody.celem";
    element Shape schema "Shape.celem";
    }}''')
    (project / 'Shape.celem').write_text(f'schema {shape} {{ field Count single general int; }}')
    for name, result_type, body in (('Main', 'int', 'return 0;'),
                                    ('Make', nominal, 'return new() { Count = 23 };'),
                                    ('Spare', 'int', 'return 0;')):
        identity = f'{ns}::{name}'
        (project / f'{name}.celem').write_text(
            f'function {identity} () -> {result_type} {{ provide {identity} with {identity}Body; }}')
        linux = f'import {ns}::Make as Make () -> {nominal}; body desktop "Linux.csbody";' if name == 'Main' else ''
        (project / f'{name}Body.celem').write_text(
            f'implementation {identity}Body for {identity} () -> {result_type} {{ {linux} body common "{name}.csbody"; }}')
        (project / f'{name}.csbody').write_text(body + '\n')
    (project / 'Linux.csbody').write_text(f'''var value = calls.Make.Invoke();
long count = value.Count;
System.IO.File.AppendAllText({json.dumps(str(marker))}, $"{{value.Count.GetType().Name}}:{{count}}\\n");
return 0;
''')
    return project, ns


@contextmanager
def editor(root, repo, command, project, browser):
    env = dict(os.environ, CONFECTORY_UI='web', CONFECTORY_EDITOR_REPO=str(repo),
               CONFECTORY_HOME_STORAGE=str(root / 'profile'), CONFECTORY_ENTRY_STORAGE=str(root / 'profile'),
               CONFECTORY_MCP_DIRECTORY=str(root / 'instances'), CONFECTORY_WEB_PROJECT=str(project / 'project.cpack'),
               CONFECTORY_ELEMENT_AUTHORING_HOST=str(repo / 'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'),
               CONFECTORY_PROJECT_EXECUTION_HOST=str(repo / 'targets/project-execution-host/bin/Release/net10.0/Confectory.ProjectExecutionHost.dll'))
    log = root / (project.name + '.log')
    with log.open('w') as stream:
        host = subprocess.Popen(command, cwd=repo, env=env, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            deadline = time.monotonic() + 60
            url = None
            while time.monotonic() < deadline:
                url = next((line.split(' ', 1)[1] for line in log.read_text().splitlines()
                            if line.startswith('CONFECTORY_WEB_UI ')), None)
                if url:
                    break
                assert host.poll() is None, 'Editor exited during startup'
                time.sleep(.05)
            assert url, 'No loopback editor address'
            origin = url.split('/#', 1)[0]
            assert origin.startswith('http://127.0.0.1:')
            page = browser.new_page(viewport={'width': 1800, 'height': 1200})
            page.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
            try:
                goto_editor(page, url)
                expect(page.locator('#title')).to_contain_text(project.name)
                yield page
            except Exception:
                if not page.is_closed():
                    print('Editor status:', page.locator('#status').all_text_contents(), flush=True)
                    print('Open dialogs:', page.get_by_role('dialog').all_text_contents(), flush=True)
                raise
            finally:
                page.close()
        finally:
            if host.poll() is None:
                os.killpg(host.pid, signal.SIGTERM)
                host.wait(timeout=20)


def target(page, name):
    window = page.locator('.window[data-key=targets]')
    window.locator('[data-target-choice]').select_option(name)


def shape_edit(page, project, ns, from_type, to_type):
    source = project / 'Shape.celem'
    original = source.read_bytes()
    target(page, 'portable')
    find_project_item(page, ns + '::Shape', '정보')
    panel = page.locator('.window[data-key=schema]')
    expect(panel.locator('.object-title-name')).to_have_text('Shape')
    panel.locator('[data-property-path=\'["Count"]\'] [data-property-type]').click()
    picker = page.get_by_role('dialog', name='속성 타입 선택', exact=True)
    picker.locator(f'[data-type="{to_type}"]').click()
    panel.locator('[data-element-action=save]').click()
    panel.locator('[data-element-action=confirm]').click()
    pending = page.locator('.window[data-key=review]')
    creation = page.locator('#review-creation')
    page.locator('#review-creation:visible, .window[data-key=review]:visible').first.wait_for(timeout=30000)
    if creation.is_visible():
        creation.click()
    expect(pending).to_be_visible(timeout=120000)
    if pending.locator('[data-review-advanced]').is_visible():
        pending.locator('[data-review-advanced]').click()
    if pending.locator('[data-advanced-reviewed]').count():
        pending.locator('[data-advanced-reviewed]').check()
    assert f'general {from_type}' in original.decode() and source.read_bytes() == original
    pending.locator('#confirm').click()
    expect(pending).to_be_hidden(timeout=120000)
    expect(page.locator('#status')).to_have_text('검토한 변경을 최종 소스에 반영했습니다.')
    assert f'general {to_type}' in source.read_text()
    panel.locator(':scope > .object-header [data-close]').click()
    target(page, 'desktop')


def exercise(root, repo, command, browser):
    marker, peer_marker = root / 'runs.txt', root / 'peer-runs.txt'
    project, ns = fixture(root, repo, 'Active', marker)
    peer, _ = fixture(root, repo, 'Peer', peer_marker)
    peer_files = {path: path.read_bytes() for path in peer.iterdir()}
    with editor(root, repo, command, peer, browser) as page:
        peer_title = page.locator('#title').inner_text().removesuffix(' ▾')
        page.locator('#chat-input').fill('Peer unsent draft')
        page.locator('.brand').click()
        expect(page.locator('.home-grid')).to_be_visible()

    with editor(root, repo, command, project, browser) as page:
        dock = page.get_by_role('button', name='프로젝트 실행', exact=True)
        run = page.locator('.run-window:visible')
        latest = project / '.confectory/outputs/desktop/latest.json'
        commands = []

        def observe(request):
            if request.method == 'POST' and request.url.endswith('/api/request'):
                body = request.post_data_json
                if body.get('op') == 'invoke':
                    commands.append((body['endpoint'], body['input']))

        page.on('request', observe)
        page.locator('#chat-input').fill('Active unsent draft')
        spare = open_main(page, ns + '::Spare')
        spare.locator('[data-native-convert]').click()
        expect(spare.locator('.bp-status')).to_contain_text('C# 미리보기')
        spare.locator('[data-bp-save]').click()
        expect(spare.get_by_role('tab', name='논리 코드', exact=True)).to_be_visible(timeout=120000)
        draft = 'return 19;\n'
        edit_body(page, spare, draft, change=True)
        spare.locator('[data-bp-save]').click()
        expect(spare.locator('.bp-status')).to_have_text('저장됨', timeout=120000)
        # With two declared aliases and no default for this OS, Review opens the
        # production target picker before any source can be confirmed.
        spare.locator('[data-bp-complete]').click()
        picker = page.locator('.window[data-key=targets]')
        expect(picker).to_be_visible()
        target(page, 'desktop')
        spare.locator(':scope > .window-title [data-close]').press('Enter')

        dock.click()
        expect(run.locator('[data-run-frame]')).to_have_text('종료 코드 0', timeout=120000)
        assert marker.read_text().splitlines() == ['Int32:23']
        previous = latest.read_bytes()
        output = Path(json.loads(previous)['output'])
        previous_outputs = {path: path.read_bytes() for path in output.glob('*.dll')}
        assert previous_outputs
        page.get_by_role('tab', name='Workspace', exact=True).click()

        shape_edit(page, project, ns, 'int', 'double')
        assert latest.read_bytes() == previous
        dock.click()
        expect(run.locator('.caption strong')).to_have_text('실행 실패', timeout=120000)
        expect(run.locator('[data-run-project]')).to_contain_text('Active')
        expect(run.locator('[data-run-frame]')).not_to_have_text('종료 코드 0')
        failure = run.locator('[data-run-surface]').inner_text()
        failure_exit = run.locator('[data-run-frame]').inner_text()
        assert marker.read_text().splitlines() == ['Int32:23'] and latest.read_bytes() == previous
        assert all(path.read_bytes() == content for path, content in previous_outputs.items())
        expect(page.locator('#chat-input')).to_have_value('Active unsent draft')
        print('PASS confirmed target-specific incompatibility fails at ▶ and preserves the old build', flush=True)

        page.get_by_role('tab', name='Workspace', exact=True).click()
        shape_edit(page, project, ns, 'double', 'long')
        dock.click()
        expect(run.locator('[data-run-frame]')).to_have_text('종료 코드 0', timeout=120000)
        assert marker.read_text().splitlines() == ['Int32:23', 'Int64:23'] and latest.read_bytes() != previous
        expect(page.locator('#chat-input')).to_have_value('Active unsent draft')
        expect(page.locator('#messages')).not_to_contain_text('Active unsent draft')
        page.get_by_role('tab', name='Workspace', exact=True).click()
        edit_body(page, open_main(page, ns + '::Spare'), draft, change=False)
        assert (project / 'Spare.csbody').read_text() == 'return 0;\n' and 'blueprint' not in (project / 'SpareBody.celem').read_text()
        assert len([body for name, body in commands if name == 'confirmGroup']) == 2
        assert [body['target'] for name, body in commands if name == 'runWindow' and body.get('operation') == 'start'] == ['desktop'] * 3
        assert not {'prepareAI', 'startAI'} & {name for name, _ in commands}
        page.locator('.brand').click()
        peer_card = page.locator('.project-card').filter(has=page.get_by_role('heading', name=peer_title, exact=True))
        peer_card.locator('[data-enter]').click()
        expect(page.locator('#title')).to_contain_text('Peer')
        expect(page.locator('#chat-input')).to_have_value('Peer unsent draft')
        assert all(path.read_bytes() == content for path, content in peer_files.items()) and not peer_marker.exists()
        print('PASS repaired confirmation runs fresh code and preserves the card draft and both chat contexts', flush=True)

        assert '빌드에 실패' in failure and 'CS0266' in failure and str(root) not in failure, failure
        assert not failure_exit, failure_exit
        print('PASS Run shows the compiler error without exposing the local build path', flush=True)


if __name__ == '__main__':
    repository = Path(sys.argv[1]).resolve()
    command = json.loads(Path(sys.argv[2]).read_text())['run']
    expect.set_options(timeout=30000)
    with tempfile.TemporaryDirectory(prefix='cf-run-recovery-') as temp, sync_playwright() as playwright:
        with playwright.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--disable-gpu'],
                                        ignore_default_args=['--disable-dev-shm-usage']) as browser:
            exercise(Path(temp), repository, command, browser)
