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
GTK_CHAT = 'Unsent GTK handoff draft'
BROWSER_CHAT = GTK_CHAT + ' · edited in Logic Code'
RETURN_MODAL = 'GTK 작업공간으로 돌아가기'


def listeners():
    endpoints = set()
    for family in ('tcp', 'tcp6'):
        with open('/proc/net/' + family) as rows:
            next(rows)
            endpoints.update((family, row.split()[1]) for row in rows if row.split()[3] == '0A')
    return endpoints


@contextmanager
def owned_page(browser, address, bootstrap=None):
    from editor_navigation import goto_editor
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
        if route.request.url.startswith(origin + '/') or route.request.url == bootstrap:
            route.continue_()
        else:
            external.append(route.request.url)
            route.abort()

    page.route('**/*', route_owned)
    page.on('pageerror', lambda error: errors.append(str(error)))
    try:
        if bootstrap is None:
            goto_editor(page, address)
        else:
            page.goto(bootstrap, wait_until='commit')
            page.wait_for_url(origin + '/**')
            page.locator('.work-body').wait_for()
        yield page
        assert not errors and not external, (errors, external)
    finally:
        page.close()


@contextmanager
def open_packaged_logic(browser):
    env = dict(os.environ, CONFECTORY_WEB_PORT='1')
    with subprocess.Popen([INSTALL + '/run', '--logic-code'], start_new_session=True, env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as host:
        address = None
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
            with owned_page(browser, address) as page:
                yield page
        finally:
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


def browser_options():
    # Keep font mappings on the fixture's shared memory mount.
    return dict(executable_path='/usr/lib/chromium/chromium',
                args=['--no-sandbox', '--disable-gpu'],
                ignore_default_args=['--disable-dev-shm-usage'])


def open_recent(page):
    from playwright.sync_api import expect
    card = page.locator('#home-projects [data-enter]').filter(has_text=TITLE)
    expect(card).to_have_count(1)
    card.click()
    expect(page.locator('.work-body')).to_be_visible()


def exercise(page, manifest, namespace, marker, *, cold, dispatched=False):
    from playwright.sync_api import expect
    from editor_logic_workflow import edit_body, find_project_item, open_main, review, run_from_dock
    if dispatched:
        expect(page.locator('#title')).to_contain_text(TITLE)
        panel = page.locator('.window[data-key=blueprint]')
        expect(panel).to_be_visible()
    else:
        open_recent(page)
    source_text = f'System.IO.File.WriteAllText({json.dumps(str(marker))}, "{OUTPUT}");\nreturn 0;'
    pending_source = source_text.replace(OUTPUT, 'Unconfirmed draft must not run')
    if cold:
        if dispatched:
            page.get_by_role('tab', name='Workspace', exact=True).click()
        panel = open_main(page, namespace + '::Main')
        edit_body(page, panel, pending_source if dispatched else source_text, change=False)
        run_from_dock(page, marker, OUTPUT)
        return
    source, body = manifest.parent / 'main.csbody', manifest.parent / 'main_body.celem'
    info = manifest.parent / 'elements/ProjectInfo.celem'
    original = (source.read_bytes(), body.read_bytes())
    manifest_before = manifest.read_bytes()
    find_project_item(page, namespace + '::ProjectInfo', '개념')
    info_window = page.locator('.window[data-key=schema]')
    info_review = review(page, info_window.locator('[data-element-action=confirm]'))
    assert not info.exists() and manifest.read_bytes() == manifest_before
    info_review.locator('#confirm').click()
    expect(info_review).to_be_hidden(timeout=120000)
    # Confirm closes Review before the completion callback refreshes the
    # schema window. Close its actual header after that refresh finishes.
    expect(page.locator('#status')).to_have_text('검토한 변경을 최종 소스에 반영했습니다.')
    assert TITLE in info.read_text()
    info_window.locator(':scope > .window-title [data-close]').click()
    expect(info_window).to_be_hidden()
    confirmed_info, confirmed_manifest = info.read_bytes(), manifest.read_bytes()

    panel = open_main(page, namespace + '::Main')
    if dispatched:
        # The initial registration draft protects the native manifest until Confirm.
        panel.locator('[data-operation=read-startup-logic]').click()
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
    if dispatched:
        expect(final_review.locator('#confirm')).to_be_enabled()
        (marker.parent / 'logic-return-stage').write_text('review')
        expect(page.locator('#status')).to_contain_text('열린 검토를 확정하거나 취소', timeout=30000)
        expect(final_review).to_be_visible()
        assert (source.read_bytes(), body.read_bytes()) == original
    final_review.locator('#confirm').click()
    expect(final_review).to_be_hidden(timeout=120000)
    assert source.read_bytes() == original[0] and info.read_bytes() == confirmed_info
    assert 'blueprint common' in body.read_text()
    run_from_dock(page, marker, OUTPUT)
    if dispatched:
        page.get_by_role('tab', name='Workspace', exact=True).click()
        confirmed = (source.read_bytes(), body.read_bytes(), manifest.read_bytes(), info.read_bytes())
        edit_body(page, panel, pending_source, change=True, original=source_text)
        panel.locator('[data-bp-save]').click()
        expect(panel.locator('.bp-status')).to_have_text('저장됨', timeout=120000)
        assert (source.read_bytes(), body.read_bytes(), manifest.read_bytes(), info.read_bytes()) == confirmed


def browser_workflow(manifest, namespace, marker):
    from playwright.sync_api import expect, sync_playwright
    expect.set_options(timeout=30000)
    assert os.geteuid() != 0 and not Path('/workspace').exists()
    assert not listeners()
    with sync_playwright() as playwright:
        for cold in (False, True):
            with playwright.chromium.launch(**browser_options()) as browser, open_packaged_logic(browser) as page:
                exercise(page, manifest, namespace, marker, cold=cold)
            print('PASS fresh packaged host and Chromium reopen Recent, read the same card and run it again' if cold
                  else 'PASS package Logic Code card Save, Review cancel, Confirm, actual Run and clean shutdown',
                  flush=True)


def dispatched_browser(manifest, namespace, marker, cold):
    from playwright.sync_api import expect, sync_playwright
    assert os.geteuid() != 0 and not Path('/workspace').exists()
    address = b''
    fd = os.open(Path.home() / 'browser-open', os.O_RDWR | os.O_NONBLOCK)
    try:
        with selectors.DefaultSelector() as reader:
            reader.register(fd, selectors.EVENT_READ)
            deadline = time.monotonic() + 15
            while b'\n' not in address and time.monotonic() < deadline:
                if reader.select(max(0, deadline - time.monotonic())):
                    address += os.read(fd, 1024)
            assert b'\n' in address, 'The registered browser did not receive an address'
    finally:
        os.close(fd)
    import re
    import stat
    received = address.decode().strip()
    # GIO may pass a local file as a path or a file URI.
    assert '/#' not in received and (received.startswith('file:///') or received.startswith('/')), \
        'Only the private bootstrap file may reach the desktop launcher'
    bootstrap = Path(received if received.startswith('/') else urllib.parse.unquote(urllib.parse.urlsplit(received).path))
    assert bootstrap.name == 'open.html' and stat.S_IMODE(bootstrap.parent.stat().st_mode) == 0o700
    local = re.search(r'url=(http://127\.0\.0\.1:\d+/#[0-9a-f]{32})"', bootstrap.read_text())
    assert local, 'Expected the local browser bootstrap'
    expect.set_options(timeout=30000)
    with sync_playwright() as playwright, playwright.chromium.launch(**browser_options()) as browser, \
            owned_page(browser, local[1], bootstrap=bootstrap.as_uri()) as page:
        assert not bootstrap.exists(), 'Authenticated browser startup must retire the bootstrap'
        chat = page.locator('#chat-input')
        if not chat.is_visible():
            page.locator('#chat').click()
        expect(chat).to_have_value(BROWSER_CHAT if cold else GTK_CHAT)
        exercise(page, manifest, namespace, marker, cold=cold, dispatched=True)
        if not cold:
            chat.fill(BROWSER_CHAT)
            dialog = page.get_by_role('dialog', name=RETURN_MODAL)
            stage = marker.parent / 'logic-return-stage'
            stage.write_text('cancel')
            dialog.locator('[data-logic-return-cancel]').click()
            expect(dialog).to_be_hidden()
            expect(chat).to_have_value(BROWSER_CHAT)
            stage.write_text('accept')
            expect(dialog).to_contain_text(TITLE)
            dialog.locator('[data-logic-return-confirm]').click()
            expect(dialog.locator('[data-logic-return-status]')).to_have_text('원래 GTK 작업공간을 여는 중…')
    print('PASS reopened saved unconfirmed card draft and ran the confirmed version again' if cold
          else 'PASS GTK-dispatched edit, Review blocked return, Confirm, Run, return cancellation and acceptance', flush=True)


def test_package(package, image, switch=False, failure=False):
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
        if switch:
            opener = case / 'browser-handler'
            opener.write_text('#!/bin/sh\nprintf "%s\\n" "$1" > "$HOME/browser-open"\n')
            opener.chmod(0o700)
            mounts.append((opener, '/test/browser-handler', True))
        if failure:
            broken = case / 'unstartable-browser'
            broken.write_text('#!/test/missing-interpreter\n')
            broken.chmod(0o700)
            unloaded = case / 'exits-without-opening'
            unloaded.write_text('#!/bin/sh\nprintf started > "$HOME/browser-started"\nexit 23\n')
            unloaded.chmod(0o700)
            mounts.extend(((broken, '/test/unstartable-browser', True), (unloaded, '/test/exits-without-opening', True)))
        with installed_editor(case / 'sdk', extracted, image, sdk=True, extra_mounts=mounts, shm_size="512m") as (app, projects):
            if switch:
                test_switch(app, projects)
                return
            if failure:
                test_launch_failure(app, projects)
                return
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


def test_switch(app, projects):
    import re
    from editor_lan_chat_x11 import eventually, native_windows, ui
    from editor_lay_chat_x11 import open_project

    def no_listener():
        assert not any(row[3] == '0A' for row in app.tcp())

    def close_project():
        app.click(33)
        app.click(52)
        app.wait(lambda row: row['screen'] == 'home', 'Closed local fixture project')

    def switch_command():
        app.click(33)
        app.click(20)

    def dispatch(created, cold):
        def redact(text):
            return re.sub(r'(http://127\.0\.0\.1:\d+/#)[0-9a-f]{32}', r'\1[redacted]', text)

        prior = app.window
        switch_command()
        window, = eventually(lambda: native_windows(b'Confectory - Logic Code'), 'Native Logic Code lifetime window')
        assert prior not in native_windows() and app.child.poll() is None
        stage = app.home / 'logic-return-stage'
        stage.unlink(missing_ok=True)
        with subprocess.Popen(app.command([sys.executable, '/test/' + Path(__file__).name, '--dispatched',
                                           created['path'], created['namespace'],
                                           str(app.home / 'logic-result.txt'), str(int(cold))],
                                          PLAYWRIGHT_NODEJS_PATH='/test/node'),
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as browser:
            if not cold:
                for expected in ('review', 'cancel', 'accept'):
                    def ready():
                        assert browser.poll() is None, redact(browser.stderr.read())
                        return stage.is_file() and stage.read_text() == expected
                    eventually(ready, f'Logic Code reached {expected}', timeout=160)
                    if expected == 'review':
                        duplicate = subprocess.run(app.command([INSTALL + '/run', '--logic-code']),
                                                   capture_output=True, text=True, timeout=20)
                        assert duplicate.returncode and 'owner.lock' in duplicate.stderr
                    assert window in native_windows(b'Confectory - Logic Code')
                    ui.click(window, 90, 115)
            stdout, stderr = browser.communicate(timeout=280)
        assert browser.returncode == 0, redact(stderr)
        print(stdout, end='', flush=True)
        if cold:
            assert window in native_windows(b'Confectory - Logic Code') and app.child.poll() is None
            app.window = window
            app.close()
        else:
            def returned(row):
                return (row['screen'] == 'project' and row['message'] == 'Returned from Logic Code.' and
                        row['model']['selected']['projectId'] == created['projectId'] and
                        row['model']['selected']['path'] == created['path'] and native_windows())
            app.wait(returned, 'Returned directly to the original project')
            app.window, = native_windows()
            app.wait(lambda row: app.field(row, 38).get('text') == BROWSER_CHAT, 'Unsent browser chat restored in GTK')
            assert not (app.profile / 'project-chat').exists()
        assert not native_windows(b'Confectory - Logic Code')
        no_listener()

    app.launch([INSTALL + '/run'])
    assert not app.state()['model']['cards'] and not app.state()['model']['helperAgents']['agents']
    created = app.create(TITLE, GTK_CHAT, projects)
    close_project()
    other = app.create('Unrelated Local Project', '', projects)
    close_project()
    assert open_project(app, TITLE)['projectId'] == created['projectId']
    other_manifest = Path(other['path'])
    other_original = other_manifest.read_bytes()

    switch_command()
    app.wait(lambda row: 'No default browser' in row['message'], 'No-browser CLI fallback')
    no_listener()
    app.click(42)

    home = app.home
    apps = home / '.local/share/applications'
    apps.mkdir(parents=True)
    (apps / 'confectory-test-browser.desktop').write_text('[Desktop Entry]\nType=Application\nName=Owned Chromium test\n'
                                                         'Exec=/test/browser-handler %u\nMimeType=x-scheme-handler/http;\n')
    (home / '.config').mkdir(exist_ok=True)
    (home / '.config/mimeapps.list').write_text('[Default Applications]\nx-scheme-handler/http=confectory-test-browser.desktop;\n')
    os.mkfifo(home / 'browser-open', 0o600)

    app.click(55)
    app.fill(54, 'return 3;\n')
    switch_command()
    app.wait(lambda row: 'unapplied editing input' in row['message'], 'Unsaved GTK source blocked the switch')
    assert Path(created['path']).with_name('main.csbody').read_text() == 'return 0;\n'
    no_listener()
    app.click(42)
    app.fill(54, 'return 0;\n')
    dispatch(created, cold=False)
    marker = app.home / 'logic-result.txt'
    marker.unlink()
    app.click(36)
    eventually(lambda: marker.is_file() and marker.read_text() == OUTPUT, 'Confirmed Logic Code runs in GTK', timeout=120)
    app.close()

    app.launch([INSTALL + '/run'])
    assert open_project(app, TITLE)['projectId'] == created['projectId']
    app.wait(lambda row: app.field(row, 38).get('text') == BROWSER_CHAT, 'Local GTK draft restored')
    dispatch(created, cold=True)
    assert other_manifest.read_bytes() == other_original
    print('PASS direct GTK return, restart, executable output, unsent chat, independent project, and exclusive session cleanup', flush=True)


def test_launch_failure(app, projects):
    import uuid
    from editor_lan_chat_x11 import eventually, native_windows
    from editor_lay_chat_x11 import open_project

    def choose_handler(executable):
        applications = app.home / '.local/share/applications'
        applications.mkdir(parents=True, exist_ok=True)
        (applications / 'confectory-failing-browser.desktop').write_text(
            '[Desktop Entry]\nType=Application\nName=Owned failing browser fixture\n'
            f'Exec={executable} %u\nMimeType=x-scheme-handler/http;\n')
        (app.home / '.config').mkdir(exist_ok=True)
        (app.home / '.config/mimeapps.list').write_text(
            '[Default Applications]\nx-scheme-handler/http=confectory-failing-browser.desktop;\n')

    def no_listener():
        for family in ('tcp', 'tcp6'):
            rows = app.invoke('cat', '/proc/net/' + family).stdout.splitlines()[1:]
            assert not any(row.split()[3] == '0A' for row in rows)

    draft = 'Unsent browser recovery ' + uuid.uuid4().hex
    app.launch([INSTALL + '/run'])
    assert not app.state()['model']['cards'] and not app.state()['model']['helperAgents']['agents']
    other = app.create('Unrelated Recovery Project', '', projects)
    app.click(33)
    app.click(52)
    app.wait(lambda row: row['screen'] == 'home', 'Closed the unrelated project')
    other_file = Path(other['path'])
    other_original = other_file.read_bytes()
    project = app.create('Browser Recovery Project', draft, projects)
    manifest = Path(project['path'])
    original = manifest.read_bytes()
    failure_message = 'Could not open the browser; this project is still open.'
    started = app.home / 'browser-started'

    app.click(33)
    app.click(20)
    app.wait(lambda row: 'No default browser' in row['message'] and
             app.field(row, 38).get('text') == draft, 'No-browser click left the existing GTK project open')
    assert app.window in native_windows() and not native_windows(b'Confectory - Logic Code')
    no_listener()
    app.click(42)
    print('PASS absent browser leaves GTK and the unsent draft in place', flush=True)

    for executable, launches in (('/test/unstartable-browser', False), ('/test/exits-without-opening', True)):
        choose_handler(executable)
        log_start = app.log.stat().st_size
        app.click(33)
        app.click(20)
        if launches:
            eventually(started.is_file, 'Registered failing browser actually started')
        def diagnostics():
            with app.log.open('rb') as stream:
                stream.seek(log_start)
                lines = stream.read().decode(errors='replace').splitlines()
            return [line for line in lines if line in ('The default browser could not be launched.',
                                                       'The default browser did not connect to Logic Code.')]

        def returned(row):
            return (row['screen'] == 'project' and row['message'] == failure_message and
                    row['model']['selected']['projectId'] == project['projectId'] and
                    app.field(row, 38).get('text') == draft and diagnostics() and
                    native_windows() and not native_windows(b'Confectory - Logic Code'))

        restored = app.wait(returned, f'Reopen original project after {executable}', timeout=45)
        window, = native_windows()
        app.window = window
        no_listener()
        assert not list((app.home.parent / 'tmp').glob('confectory-logic-*/open.html'))
        assert restored['model']['selected']['path'] == str(manifest)
        assert manifest.read_bytes() == original and other_file.read_bytes() == other_original
        assert not (app.profile / 'project-chat').exists()
        diagnostic, = diagnostics()
        if launches:
            assert diagnostic == 'The default browser did not connect to Logic Code.'
        print(f'PASS {diagnostic} GTK reopened the original project with its draft.', flush=True)

    app.fill(38, draft + ' still editable')
    app.close()
    no_listener()
    app.launch([INSTALL + '/run'])
    assert open_project(app, 'Browser Recovery Project')['projectId'] == project['projectId']
    app.wait(lambda row: app.field(row, 38).get('text') == draft + ' still editable',
             'Recovered draft remained editable and persisted on normal close')
    app.close()
    no_listener()
    print('PASS recovered chat stays unsent and editable through a full restart', flush=True)


if __name__ == '__main__':
    if sys.argv[1] == '--browser':
        browser_workflow(Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4]))
    elif sys.argv[1] == '--dispatched':
        dispatched_browser(Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4]), sys.argv[5] == '1')
    else:
        test_package(Path(sys.argv[1]).resolve(), sys.argv[2], switch='--switch' in sys.argv[3:],
                     failure='--browser-failure' in sys.argv[3:])
