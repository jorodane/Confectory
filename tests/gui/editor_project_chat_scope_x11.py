#!/usr/bin/env python3
"""Use one fresh installed profile and two user-created projects across GTK and Chromium.

Use the local image and private Xorg display from editor_linux_package_x11.py.
Run this script with the Linux x64 package directory and the fixture image.
The package is mounted read-only in the unprivileged, network-none fixture. Only
existing UI controls change editor state; HTTP requests are observed, never injected.
"""

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from editor_linux_package_logic_x11 import browser_options, open_packaged_logic


ALPHA, BETA = 'Chat Alpha', 'Chat Beta'
GTK_DRAFT = {ALPHA: 'unsent GTK alpha only', BETA: 'unsent GTK beta only'}
WEB_DRAFT = {ALPHA: 'unsent web alpha only', BETA: 'unsent web beta only'}


def project_files(project):
    return {path.relative_to(project): path.read_bytes() for path in project.rglob('*')
            if path.is_file() and '.confectory' not in path.relative_to(project).parts}


def assert_no_history(profile):
    for directory in ('project-chat', 'helper-conversations'):
        assert not any(path.is_file() for path in (profile / directory).rglob('*')), directory


def gtk_home(app):
    return app.wait(lambda row: row['screen'] == 'home' and row['model']['selected'] is None
                    and not app.field(row, 38).get('visible'), 'GTK Home without a project composer')


def gtk_project(app, expected, draft):
    return app.wait(lambda row: row['screen'] == 'project' and row['model']['selected']
                    and row['model']['selected']['projectId'] == expected['projectId']
                    and row['model']['selected']['path'] == expected['path']
                    and app.field(row, 38).get('visible') and app.field(row, 38).get('text') == draft,
                    'GTK composer for current project and only its draft')


def gtk_menu(app, action):
    app.click(33)  # Project title menu
    app.click(action)


def gtk_chat(app, project, title):
    gtk_project(app, project, '')
    app.click(44)  # Navigate -> Project chat
    app.click(46)
    gtk_project(app, project, '')
    app.fill(38, GTK_DRAFT[title])
    app.click(40)  # The native dock hides its composer when Logs are selected.
    logs = app.wait(lambda row: app.field(row, 53).get('visible') and not app.field(row, 38).get('visible'),
                    'GTK Logs replacing the project composer')
    assert logs['model']['selected']['projectId'] == project['projectId']
    assert all(value not in app.field(logs, 53).get('text', '') for value in GTK_DRAFT.values())
    app.click(39)
    gtk_project(app, project, GTK_DRAFT[title])


def gtk_workflow(app, projects, launcher):
    from editor_lay_chat_x11 import open_project

    app.launch(launcher)
    assert not gtk_home(app)['model']['cards']
    alpha = app.create(ALPHA, '', projects)
    alpha_root = Path(alpha['path']).parent
    alpha_original = project_files(alpha_root)
    gtk_chat(app, alpha, ALPHA)
    gtk_menu(app, 15)  # Hide project via its existing explicit transition.
    gtk_home(app)

    beta = app.create(BETA, '', projects)
    assert beta['projectId'] != alpha['projectId']
    beta_root = Path(beta['path']).parent
    beta_original = project_files(beta_root)
    gtk_chat(app, beta, BETA)
    gtk_menu(app, 52)  # Completely close this project.
    gtk_home(app)
    app.click(8)  # Global Helper profile on Home, with no registered or eligible Helper.
    helper = app.wait(lambda row: row['screen'] == 'profile' and 'No eligible Helper' in app.field(row, 438).get('text', ''),
                      'GTK global Helper empty state')
    assert helper['model']['selected'] is None and not app.field(helper, 38).get('visible')
    app.click(430)
    gtk_home(app)

    assert open_project(app, ALPHA)['projectId'] == alpha['projectId']
    gtk_project(app, alpha, GTK_DRAFT[ALPHA])
    gtk_menu(app, 52)
    assert not gtk_home(app)['model']['backgroundProjects']
    app.close()
    assert_no_history(app.profile)
    print('PASS packaged GTK composer, Logs/reopen, explicit Hide/Close, global Helper empty state and same-project draft', flush=True)
    return {ALPHA: alpha_root, BETA: beta_root}, {alpha_root: alpha_original, beta_root: beta_original}


def web_workflow():
    from playwright.sync_api import expect, sync_playwright

    calls = []

    def observe(request):
        if request.method == 'POST' and request.url.endswith('/api/request'):
            body = request.post_data_json
            if body.get('op') == 'invoke':
                calls.append(body['endpoint'])

    def project_opens():
        return calls.count('openProject')

    def home(page):
        expect(page.locator('.home-grid')).to_be_visible()
        expect(page.locator('#chat-input')).to_have_count(0)
        expect(page.locator('.work-body')).to_have_count(0)

    def open_project(page, title):
        home(page)
        card = page.locator('.project-card').filter(has=page.get_by_role('heading', name=title, exact=True))
        card.locator('[data-enter]').click()
        expect(page.locator('#title')).to_contain_text(title)

    def draft(page, title, value):
        expect(page.locator('#title')).to_contain_text(title)
        expect(page.locator('#chat-input')).to_have_value(value)
        for text in (*GTK_DRAFT.values(), *WEB_DRAFT.values()):
            expect(page.locator('#messages')).not_to_contain_text(text)

    def fold_and_open(page, title, value):
        before = project_opens()
        separator = page.get_by_role('separator', name='채팅바 높이 조절')
        expanded = separator.get_attribute('aria-valuenow')
        separator.click()
        expect(separator).to_have_attribute('aria-valuenow', '44')
        expect(page.locator('#chat-input')).to_be_hidden()
        expect(page.locator('#title')).to_contain_text(title)
        separator.click()
        expect(separator).to_have_attribute('aria-valuenow', expanded)
        expect(page.locator('#chat-input')).to_be_visible()
        draft(page, title, value)
        assert project_opens() == before

    def leave(page, close):
        before = project_opens()
        if close:
            page.locator('#title').click()
            page.get_by_role('button', name='프로젝트 완전 종료', exact=True).click()
        else:
            page.get_by_role('button', name='Confectory 홈으로').click()
        home(page)
        assert project_opens() == before

    expect.set_options(timeout=30000)
    with sync_playwright() as playwright, playwright.chromium.launch(**browser_options()) as browser, \
            open_packaged_logic(browser) as page:
        assert os.geteuid() != 0 and not Path('/workspace').exists()
        page.on('request', observe)
        open_project(page, ALPHA)
        draft(page, ALPHA, GTK_DRAFT[ALPHA])
        page.locator('#chat-input').fill(WEB_DRAFT[ALPHA])
        fold_and_open(page, ALPHA, WEB_DRAFT[ALPHA])
        leave(page, close=False)

        open_project(page, BETA)
        draft(page, BETA, GTK_DRAFT[BETA])
        page.locator('#chat-input').fill(WEB_DRAFT[BETA])
        fold_and_open(page, BETA, WEB_DRAFT[BETA])
        leave(page, close=True)
        before = project_opens()
        page.locator('#add-helper').click()
        agent = page.get_by_role('dialog', name='Agent 추가', exact=True)
        expect(agent).to_be_visible()
        home(page)
        agent.locator('[data-close]').click()
        expect(agent).to_be_hidden()
        home(page)
        assert project_opens() == before

        for title in ALPHA, BETA:
            open_project(page, title)
            draft(page, title, WEB_DRAFT[title])
            leave(page, close=True)
        assert not {'prepareAI', 'startAI', 'recruitGlobalHelper'} & set(calls), calls
    print('PASS local Chromium composer fold/reopen, project transitions and account-free Helper entry', flush=True)


def test_package(package, image):
    from playwright._impl._driver import compute_driver_executable
    from editor_linux_package_x11 import INSTALL, installed_editor

    here = Path(__file__).resolve().parent
    sources = (Path(__file__).resolve(), here / 'editor_linux_package_logic_x11.py',
               here.parent / 'web/editor_navigation.py')
    node, _ = compute_driver_executable()
    mounts = [(path, '/test/' + path.name, True) for path in sources]
    mounts += [(sys.prefix, sys.prefix, True), (Path(node).resolve(), '/test/node', True),
               ('/usr/lib/chromium', '/usr/lib/chromium', True)]
    with tempfile.TemporaryDirectory(prefix='cfchat-') as scratch:
        with installed_editor(Path(scratch), package, image, sdk=False, extra_mounts=mounts, shm_size='512m') as (app, projects):
            launcher = [INSTALL + '/run']
            project_roots, originals = gtk_workflow(app, projects, launcher)
            result = subprocess.run(app.command([sys.executable, '/test/' + Path(__file__).name, '--browser'],
                                                PLAYWRIGHT_NODEJS_PATH='/test/node'),
                                    capture_output=True, text=True, timeout=180)
            assert result.returncode == 0, re.sub(r'(http://127\.0\.0\.1:\d+/#)[0-9a-f]{32}', r'\1[redacted]', result.stderr)
            print(result.stdout, end='', flush=True)
            records = [json.loads(path.read_bytes()) for path in (app.profile / 'project-chat-drafts').glob('*.json')]
            assert len(records) == 2
            assert {record['project']: record['draft'] for record in records} == {
                str(root / 'project.cproj'): WEB_DRAFT[title] for title, root in project_roots.items()
            }
            assert_no_history(app.profile)
            assert all(project_files(root) == original for root, original in originals.items())
            assert not any(row[3] == '0A' for row in app.tcp())
            print('PASS exactly two private draft records, original source bytes, no sent history or lingering listener', flush=True)


if __name__ == '__main__':
    if sys.argv[1] == '--browser':
        web_workflow()
    else:
        test_package(Path(sys.argv[1]).resolve(), sys.argv[2])
