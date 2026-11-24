#!/usr/bin/env python3
"""Run the active ProjectPack from a fresh installed profile with two real projects.

Pass the Linux x64 package directory and the local fixture image. The GTK/X11
fixture creates the projects, the packaged Chromium editor authors and confirms
their entry code, and both surfaces launch the resulting .NET programs.
"""

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from editor_linux_package_logic_x11 import browser_options, open_packaged_logic
from editor_project_chat_scope_x11 import assert_no_history, gtk_home, gtk_menu, gtk_project, project_files


ALPHA, BETA = 'RunScopeAlpha', 'RunScopeBeta'
TITLES = (ALPHA, BETA)
OTHER = 'SelectedNonEntry'


def chat_text(title):
    return 'Unsent project draft for ' + title


def output_lines(marker):
    return marker.read_text().splitlines() if marker.exists() else []


def entry_text(marker, line):
    return f'System.IO.File.AppendAllText({json.dumps(str(marker))}, {json.dumps(line + chr(10))});\nreturn 0;'


def desktop_workflow(projects):
    from playwright.sync_api import expect, sync_playwright
    from editor_logic_workflow import edit_body, find_project_item, open_main, review
    from editor_navigation import open_workspace_menu

    marker = Path.home() / 'project-runs.txt'
    executions, calls, expected_starts, expected_output = [], [], [], []

    def observe(request):
        if request.method != 'POST' or not request.url.endswith('/api/request'):
            return
        body = request.post_data_json
        if body.get('op') != 'invoke':
            return
        endpoint = body['endpoint']
        calls.append(endpoint)
        if endpoint in ('runProject', 'startRun') or (endpoint == 'runWindow' and body['input']['operation'] == 'start'):
            executions.append((endpoint, body['scope']['projectId']))

    def home(page):
        expect(page.locator('.home-grid')).to_be_visible()
        expect(page.locator('#run, #project-menu, #chat-input')).to_have_count(0)
        expect(page.locator('.run-window:visible')).to_have_count(0)
        assert output_lines(marker) == expected_output and executions == expected_starts

    def open_project(page, title):
        home(page)
        card = page.locator('.project-card').filter(has=page.get_by_role('heading', name=title, exact=True))
        card.locator('[data-enter]').click()
        expect(page.locator('#title')).to_contain_text(title)

    def confirm(page, control):
        window = review(page, control)
        window.locator('#confirm').click()
        expect(window).to_be_hidden(timeout=120000)
        expect(page.locator('#status')).to_have_text('검토한 변경을 최종 소스에 반영했습니다.')

    def add_nonentry(page, manifest):
        open_workspace_menu(page).get_by_role('button', name='프로젝트 브라우저', exact=True).click()
        browser = page.locator('.window[data-key^="browser:project:"]')
        browser.get_by_role('button', name='기능', exact=True).click()
        browser.locator('[data-new]').click()
        page.get_by_role('button', name='기능 생성', exact=True).click()
        form = page.get_by_role('dialog', name='새 기능 만들기', exact=True)
        form.locator('#object-name').fill(OTHER)
        form.get_by_role('button', name='생성', exact=True).click()
        expect(form).to_be_hidden()
        declaration = page.locator('.window[data-key=declaration]')
        expect(declaration.locator('.object-title-name')).to_have_text(OTHER)
        confirm(page, declaration.locator('[data-feature-action=confirm]'))
        assert (manifest.parent / 'elements' / (OTHER + '.celem')).exists()
        declaration.locator(':scope > .object-header [data-close]').click()
        browser.locator(':scope > .window-title [data-close]').click()

    def prepare(page, title):
        project = projects[title]
        manifest = Path(project['path'])
        namespace = project['namespace']
        find_project_item(page, namespace + '::ProjectInfo', '개념')
        info = page.locator('.window[data-key=schema]')
        confirm(page, info.locator('[data-element-action=confirm]'))
        info.locator(':scope > .window-title [data-close]').click()
        add_nonentry(page, manifest)

        panel = open_main(page, namespace + '::Main')
        expect(panel.locator('[data-native-source]')).to_have_value('return 0;\n')
        panel.locator('[data-native-convert]').click()
        expect(panel.locator('.bp-status')).to_contain_text('C# 미리보기')
        panel.locator('[data-bp-save]').click()
        expect(panel.get_by_role('tab', name='논리 코드', exact=True)).to_be_visible(timeout=120000)
        edit_body(page, panel, entry_text(marker, title), change=True)
        panel.locator('[data-bp-save]').click()
        expect(panel.locator('.bp-status')).to_have_text('저장됨', timeout=120000)
        confirm(page, panel.locator('[data-bp-complete]'))
        assert f'entry {namespace}::Main' in manifest.read_text()
        canonical = project_files(manifest.parent)
        edit_body(page, panel, entry_text(marker, title + '-unconfirmed'), change=True, original=entry_text(marker, title))
        panel.locator('[data-bp-save]').click()
        expect(panel.locator('.bp-status')).to_have_text('저장됨', timeout=120000)
        assert project_files(manifest.parent) == canonical
        panel.locator(':scope > .window-title [data-close]').click()
        return canonical

    def check_run(page, title, canonical):
        project = projects[title]
        find_project_item(page, project['namespace'] + '::' + OTHER, '기능')
        selected = page.locator('.window[data-key=declaration]')
        expect(selected.locator('.object-title-name')).to_have_text(OTHER)
        expect(page.locator('#title')).to_contain_text(title)
        expect(page.locator('#dock #run + #project-menu')).to_be_visible()
        approvals = calls.count('confirmGroup')
        menu = page.locator('#project-menu')
        menu.click()
        expect(page.locator('.context-menu').get_by_role('button', name='프로젝트 정보', exact=True)).to_be_visible()
        page.keyboard.press('Escape')
        expect(menu).to_be_focused()
        assert output_lines(marker) == expected_output and executions == expected_starts

        page.get_by_role('button', name='프로젝트 실행', exact=True).click()
        run = page.locator('.run-window:visible')
        expect(run.locator('[data-run-project]')).to_contain_text(title)
        expect(run.locator('[data-run-frame]')).to_have_text('종료 코드 0', timeout=120000)
        expected_starts.append(('runWindow', project['projectId']))
        expected_output.append(title)
        assert output_lines(marker) == expected_output and executions == expected_starts
        assert calls.count('confirmGroup') == approvals
        expect(page.locator('#chat-input')).to_have_value(chat_text(title))
        expect(page.locator('#messages')).not_to_contain_text(chat_text(title))
        page.get_by_role('tab', name='Workspace', exact=True).click()
        panel = open_main(page, project['namespace'] + '::Main')
        edit_body(page, panel, entry_text(marker, title + '-unconfirmed'), change=False)
        assert project_files(Path(project['path']).parent) == canonical

    def close_project(page):
        page.locator('#title').click()
        page.get_by_role('button', name='프로젝트 완전 종료', exact=True).click()
        home(page)

    expect.set_options(timeout=30000)
    with sync_playwright() as playwright, playwright.chromium.launch(**browser_options()) as browser, \
            open_packaged_logic(browser) as page:
        assert os.geteuid() != 0 and not Path('/workspace').exists()
        page.on('request', observe)
        originals = {}
        for title in TITLES:
            open_project(page, title)
            originals[title] = prepare(page, title)
            page.locator('#chat-input').fill(chat_text(title))
            check_run(page, title, originals[title])
            if title == ALPHA:
                page.get_by_role('button', name='Confectory 홈으로').click()  # A is hidden while B runs.
                home(page)
            else:
                close_project(page)
        open_project(page, ALPHA)
        expect(page.locator('#chat-input')).to_have_value(chat_text(ALPHA))
        close_project(page)
        assert not {'prepareAI', 'startAI'} & set(calls)
    print('PASS packaged Chromium ▶ runs each active confirmed entry with a non-entry selected; ≡ and Home never run', flush=True)
    print('PASS both stored Logic Code drafts, chat drafts and confirmed source bytes survive Run', flush=True)


def gtk_run_projects(app, launcher, projects):
    from editor_lay_chat_x11 import open_project

    marker = app.home / 'project-runs.txt'
    expected = list(TITLES)
    app.launch(launcher)
    originals = {title: project_files(Path(projects[title]['path']).parent) for title in TITLES}
    for title in TITLES:
        assert 36 not in gtk_home(app)['hits'][::5]
        opened = open_project(app, title)
        assert opened['projectId'] == projects[title]['projectId']
        gtk_project(app, opened, chat_text(title))
        app.click(44)  # GTK's existing Navigate control.
        app.wait(lambda row: 46 in row['hits'][::5], 'GTK project navigation menu')
        app.click(44)
        assert output_lines(marker) == expected
        app.click(36)
        row = app.wait(lambda state: (state['model'].get('execution') or {}).get('state') in ('exited', 'failed'),
                       'GTK project execution completed', timeout=120)
        assert (row['model']['execution']['state'], str(row['model']['execution']['exit'])) == ('exited', '0')
        expected.append(title)
        assert output_lines(marker) == expected
        gtk_project(app, opened, chat_text(title))
        gtk_menu(app, 52)
        gtk_home(app)
    app.close()
    assert all(project_files(Path(projects[title]['path']).parent) == originals[title] for title in TITLES)
    assert_no_history(app.profile)
    assert not any(row[3] == '0A' for row in app.tcp())
    print('PASS packaged GTK Run after restart uses the same two confirmed entries; no other program or message', flush=True)


def test_package(package, image):
    from playwright._impl._driver import compute_driver_executable
    from editor_linux_package_x11 import INSTALL, installed_editor

    here = Path(__file__).resolve().parent
    sources = (Path(__file__).resolve(), here / 'editor_project_chat_scope_x11.py',
               here / 'editor_linux_package_logic_x11.py', here / 'editor_logic_workflow.py',
               here.parent / 'web/editor_navigation.py')
    node, _ = compute_driver_executable()
    mounts = [(path, '/test/' + path.name, True) for path in sources]
    mounts += [(sys.prefix, sys.prefix, True), (Path(node).resolve(), '/test/node', True),
               ('/usr/lib/chromium', '/usr/lib/chromium', True)]
    with tempfile.TemporaryDirectory(prefix='cfrun-') as scratch:
        with installed_editor(Path(scratch), package, image, sdk=True, extra_mounts=mounts, shm_size='512m') as (app, roots):
            launcher = [INSTALL + '/run']
            app.launch(launcher)
            assert not gtk_home(app)['model']['cards']
            projects = {}
            for title in TITLES:
                projects[title] = app.create(title, '', roots)
                gtk_menu(app, 52)
                gtk_home(app)
            app.close()
            assert projects[ALPHA]['projectId'] != projects[BETA]['projectId']
            result = subprocess.run(app.command([sys.executable, '/test/' + Path(__file__).name,
                                                '--browser', json.dumps(projects)], PLAYWRIGHT_NODEJS_PATH='/test/node'),
                                    capture_output=True, text=True, timeout=430)
            print(result.stdout, end='', flush=True)
            assert result.returncode == 0, re.sub(r'(http://127\.0\.0\.1:\d+/#)[0-9a-f]{32}', r'\1[redacted]', result.stderr)
            gtk_run_projects(app, launcher, projects)


if __name__ == '__main__':
    if sys.argv[1] == '--browser':
        desktop_workflow(json.loads(sys.argv[2]))
    else:
        test_package(Path(sys.argv[1]).resolve(), sys.argv[2])
