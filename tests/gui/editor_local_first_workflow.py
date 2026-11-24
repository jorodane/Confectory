#!/usr/bin/env python3
"""Use a fresh EditorHome from first launch through a cold local Run.

Build EditorHome's Linux target and the Release DesktopEntry launcher. Pass
the EditorHome build report and use a dedicated, local Xorg display as in
docs/WINDOW_VERIFICATION.md. An owned TMPDIR with a 19–59 byte path exercises
the compact inbox. GTK supplies the real folder picker and project creation.
The same build's Linux web surface supplies Logic Code. No project, editor
state, or native bridge is seeded.
"""
from contextlib import contextmanager
import json
from pathlib import Path
import os
import signal
import subprocess
import sys
import tempfile
import time

from playwright.sync_api import expect, sync_playwright

from editor_lan_chat_x11 import NativeEditor, eventually, repo

sys.path.insert(0, str(repo / 'tests/web'))
from editor_navigation import goto_editor, open_workspace_menu


TITLE = 'Local First Workflow'
ROOT = Path(tempfile.mkdtemp(prefix='confectory-local-first-'))
PROFILE = ROOT / 'profile'
PROJECTS = ROOT / 'projects'
MARKER = ROOT / 'run-result.txt'
SOURCE = f'System.IO.File.WriteAllText({json.dumps(str(MARKER))}, "confirmed local code");\nreturn 0;'
RUN = json.loads(Path(sys.argv[1]).read_text())['run']
PROFILE.mkdir()
PROJECTS.mkdir()
ENV = os.environ.copy()
for option in ('CONFECTORY_WEB_PROJECT', 'CONFECTORY_DEV_PUBLIC_CHAT_LOOPBACK',
               'CONFECTORY_TEST_PUBLIC_CHAT_RELAY'):
    ENV.pop(option, None)
ENV.update(CONFECTORY_HOME_STORAGE=str(PROFILE), CONFECTORY_ENTRY_STORAGE=str(ROOT / 'entry'),
           CONFECTORY_ENTRY_SCOPE=str(ROOT / 'bridge'), CONFECTORY_MCP_DIRECTORY=str(ROOT / 'instances'),
           CONFECTORY_EDITOR_REPO=str(repo), CONFECTORY_HOME_TRACE='1',
           CONFECTORY_ELEMENT_AUTHORING_HOST=str(repo / 'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'),
           CONFECTORY_PROJECT_EXECUTION_HOST=str(repo / 'targets/project-execution-host/bin/Release/net10.0/Confectory.ProjectExecutionHost.dll'),
           GSETTINGS_BACKEND='memory', XDG_CACHE_HOME=str(ROOT / 'cache'), XDG_CONFIG_HOME=str(ROOT / 'config'),
           XDG_DATA_HOME=str(ROOT / 'data'))


class LocalGtk(NativeEditor):
    def __init__(self, label):
        super().__init__(None, PROFILE, repo)
        self.log = ROOT / (label + '.log')

    def command(self, command, setup=False, **variables):
        return ['env', *[f'{key}={value}' for key, value in dict(ENV, CONFECTORY_UI='native', **variables).items()],
                *command]

    def run_project(self):
        self.click(36)
        def finished(row):
            execution = row['model']['execution']
            return execution and execution['state'] in ('exited', 'failed')
        result = self.wait(finished, 'GTK run completion', timeout=120)['model']['execution']
        assert result['state'] == 'exited' and str(result['exit']) == '0', result


@contextmanager
def gtk(label):
    app = LocalGtk(label)
    try:
        app.launch(RUN)
        yield app
        app.close()
    finally:
        child = getattr(app, 'child', None)
        if child is not None and child.poll() is None:
            child.terminate()
            child.wait(timeout=15)
        if hasattr(app, 'stream'):
            app.stream.close()


@contextmanager
def web(browser, label):
    with (ROOT / (label + '.log')).open('w') as log:
        env = dict(ENV, CONFECTORY_UI='web')
        host = subprocess.Popen(RUN, cwd=repo, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        page = browser.new_page(viewport={'width': 1800, 'height': 1200})
        external, errors = [], []
        try:
            def ready():
                assert host.poll() is None, 'Editor host exited at startup'
                return next((line.split(' ', 1)[1] for line in Path(log.name).read_text().splitlines()
                             if line.startswith('CONFECTORY_WEB_UI ')), None)
            address = eventually(ready, 'Local Chromium editor listener', timeout=45)
            origin = address.split('/#', 1)[0]

            def allow_owned_origin(route):
                if route.request.url.startswith(origin + '/'):
                    route.continue_()
                else:
                    external.append(route.request.url)
                    route.abort()

            page.route('**/*', allow_owned_origin)
            page.on('pageerror', lambda error: errors.append(str(error)))
            goto_editor(page, address)
            expect(page.locator('.home-grid')).to_be_visible()
            card = page.locator('#home-projects [data-enter]').filter(has_text=TITLE)
            expect(card).to_have_count(1)
            card.click()
            expect(page.locator('.work-body')).to_be_visible()
            yield page
            assert not errors and not external, (errors, external)
        finally:
            try:
                page.close()
            finally:
                if host.poll() is None:
                    host.send_signal(signal.SIGINT)
                try:
                    assert host.wait(timeout=25) == 0, 'Local Chromium host did not exit cleanly'
                except subprocess.TimeoutExpired:
                    host.kill()
                    host.wait(timeout=5)
                    raise


def find_project_item(page, item, tab):
    menu = open_workspace_menu(page)
    menu.get_by_role('button', name='프로젝트 브라우저', exact=True).click()
    browser = page.locator('.window[data-key^="browser:project:"]')
    browser.get_by_role('button', name=tab, exact=True).click()
    browser.locator('[data-browser-control=object-query]').fill(item.split('::')[-1])
    browser.locator('[data-browser-control=object-search]').click()
    browser.locator(f'[data-object="{item}"]').press('Enter')
    browser.locator('[data-close]').first.click()


def open_main(page, feature):
    panel = page.locator('.window[data-key=blueprint]')
    if panel.is_visible():
        # Recent restores both floating windows. Dismiss the separate
        # declaration window through its normal control before editing.
        declaration = page.locator('.window[data-key=declaration]')
        if declaration.is_visible():
            declaration.locator(':scope > .object-header [data-close]').click()
        return panel
    find_project_item(page, feature, '기능')
    page.locator('[data-operation=feature-author-open]').first.click()
    expect(panel).to_be_visible()
    return panel


def edit_body(page, panel, text=None):
    expect(panel.get_by_role('tab', name='논리 코드', exact=True)).to_have_attribute('aria-selected', 'true')
    panel.locator('[data-document-code=body]').click()
    dialog = page.locator('.bp-script-dialog')
    editor = dialog.locator('[data-code-source]')
    expect(editor).to_be_visible()
    body = dialog.locator('[data-code-highlight] > [data-code-region=body]')
    if text is not None:
        assert body.text_content() == 'return 0;\n'
        editor.evaluate('''el => {
            const parts = Array.from(el.closest('.bp-script-editor').querySelectorAll('[data-code-highlight] > span'));
            const body = parts.findIndex(part => part.dataset.codeRegion === 'body');
            if (body < 0) throw Error('Missing editable body');
            const start = parts.slice(0, body).reduce((offset, part) => offset + part.textContent.length, 0);
            el.focus();
            el.setSelectionRange(start, start + parts[body].textContent.length);
        }''')
        page.keyboard.insert_text(text)
        dialog.locator('[data-code-save]').click()
    else:
        assert body.text_content() == SOURCE
        dialog.locator('[data-code-cancel]').click()
    expect(dialog).to_be_hidden()


def review(page, submit):
    creation = page.locator('#review-creation')
    def request():
        submit.click()
        page.locator('#review-creation:visible,.window[data-key=review]:visible,.window[data-key=targets]:visible').first.wait_for(timeout=120000)
        if creation.is_visible():
            creation.click()
    request()
    targets = page.locator('.window[data-key=targets]')
    if targets.is_visible():
        targets.locator('[data-target-choice]').select_option('linux')
        targets.locator('[data-close]').click()
        request()
    result = page.locator('.window[data-key=review]')
    expect(result).to_be_visible(timeout=120000)
    if result.locator('[data-review-advanced]').is_visible():
        result.locator('[data-review-advanced]').click()
    if result.locator('[data-advanced-reviewed]').count():
        result.locator('[data-advanced-reviewed]').check()
    return result


def run_from_dock(page):
    MARKER.unlink(missing_ok=True)
    page.get_by_role('button', name='프로젝트 실행', exact=True).click()
    deadline = time.monotonic() + 120
    while not MARKER.is_file() and time.monotonic() < deadline:
        page.wait_for_timeout(100)
    assert MARKER.is_file(), 'Confirmed code did not run'
    expect(page.locator('.run-window:visible [data-run-frame]')).to_have_text('종료 코드 0', timeout=120000)
    assert MARKER.read_text() == 'confirmed local code'


def forward_open(manifest, app):
    # The production launcher must reach the already-running, same-profile inbox.
    launcher = repo / 'targets/desktop-entry/bin/Release/net10.0/Confectory.DesktopEntry.dll'
    result = subprocess.run([ENV['CONFECTORY_DOTNET'], str(launcher), 'open', str(manifest), '--repository', str(repo)],
                            env=ENV, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0 and json.loads(result.stdout)['status'] == 'already-open', result.stderr
    assert app.child.poll() is None


def workflow():
    with gtk('first-native') as app:
        assert app.state()['model']['cards'] == []
        assert not app.state()['model']['helperAgents']['agents']
        selected = app.create(TITLE, 'Unsent local draft')
        manifest = Path(selected['path'])
        feature = selected['namespace'] + '::Main'
        assert manifest.is_relative_to(PROJECTS)
        source = manifest.parent / 'main.csbody'
        body = manifest.parent / 'main_body.celem'
        original = (source.read_bytes(), body.read_bytes(), manifest.read_bytes())
        assert original[0] == b'return 0;\n'
        forward_open(manifest, app)
        app.run_project()
        assert not MARKER.exists()
    print('PASS native Later, folder choice, project creation, existing inbox forwarding, baseline Run and window close', flush=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        with web(browser, 'edit') as page:
            # EditorHome creates the ProjectInfo registration as a saved draft.
            # Confirm it explicitly before conversion, which observes a clean manifest.
            info = manifest.parent / 'elements' / 'ProjectInfo.celem'
            find_project_item(page, selected['namespace'] + '::ProjectInfo', '개념')
            object_editor = page.locator('.window[data-key=schema]')
            expect(object_editor.locator('.object-title-name')).to_have_text('ProjectInfo')
            info_review = review(page, object_editor.locator('[data-element-action=confirm]'))
            assert not info.exists() and manifest.read_bytes() == original[2]
            info_review.locator('#confirm').click()
            expect(info_review).to_be_hidden(timeout=120000)
            assert TITLE in info.read_text() and (source.read_bytes(), body.read_bytes()) == original[:2]
            object_editor.locator('[data-close]').first.click()
            published_manifest = manifest.read_bytes()
            info_original = info.read_bytes()
            panel = open_main(page, feature)
            expect(panel.locator('[data-native-source]')).to_have_value('return 0;\n')
            panel.locator('[data-native-convert]').click()
            expect(panel.locator('.bp-status')).to_contain_text('C# 미리보기')
            # The native conversion preview is transient. Its existing Save
            # creates the document draft; it leaves canonical sources alone.
            panel.locator('[data-bp-save]').click()
            expect(panel.get_by_role('tab', name='논리 코드', exact=True)).to_be_visible(timeout=120000)
            assert (source.read_bytes(), body.read_bytes(), manifest.read_bytes()) == (*original[:2], published_manifest)
            print('PASS explicit ProjectInfo Review/Confirm and native-to-document draft conversion', flush=True)
            edit_body(page, panel, SOURCE)
            panel.locator('[data-bp-save]').click()
            expect(panel.locator('.bp-status')).to_have_text('저장됨', timeout=120000)
            assert (source.read_bytes(), body.read_bytes(), manifest.read_bytes()) == (*original[:2], published_manifest)
            submit = panel.locator('[data-bp-complete]')
            first_review = review(page, submit)
            first_review.locator('[data-reject]').click()
            expect(first_review).to_be_hidden()
            assert (source.read_bytes(), body.read_bytes(), manifest.read_bytes()) == (*original[:2], published_manifest)
            final_review = review(page, submit)
            expect(final_review.locator('#confirm')).to_be_enabled()
            final_review.locator('#confirm').click()
            expect(final_review).to_be_hidden(timeout=120000)
            assert source.read_bytes() == original[0] and info.read_bytes() == info_original
            assert 'blueprint common' in body.read_text()
            run_from_dock(page)
            print('PASS Logic Code edit and Save, Review cancel and Confirm, first Run produced the edited result', flush=True)
        browser.close()

        browser = playwright.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        with web(browser, 'cold') as page:
            panel = open_main(page, feature)
            edit_body(page, panel)
            run_from_dock(page)
        browser.close()
    print('PASS fresh host and browser opened Recent, read the same code and ran it again', flush=True)

    with gtk('cold-native') as app:
        app.click(100)
        reopened = app.wait(lambda row: row['screen'] == 'project' and row['model']['selected'] is not None,
                            'GTK open Recent')['model']
        assert reopened['selected']['projectId'] == selected['projectId']
        assert reopened['shell']['draft'] == 'Unsent local draft'
        assert not reopened['helperAgents']['agents']
        MARKER.unlink()
        app.run_project()
        assert MARKER.read_text() == 'confirmed local code'
    assert not (PROFILE / 'project-chat').exists()
    print('PASS fresh GTK opens the same Recent, keeps the local draft and runs the confirmed code', flush=True)


if __name__ == '__main__':
    expect.set_options(timeout=30000)
    try:
        workflow()
    finally:
        print('Evidence:', ROOT, flush=True)
