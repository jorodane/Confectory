#!/usr/bin/env python3
"""Exercise the installed project's ≡ → Browser → function editor path.

Pass a Linux x64 package directory and the local GTK fixture image. A fresh
GTK profile creates both projects. The packaged Chromium shell is exercised
in the same unprivileged container, with no repository or external network.
"""

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from editor_linux_package_logic_x11 import browser_options, open_packaged_logic
from editor_project_chat_scope_x11 import gtk_home, gtk_menu, project_files


FIRST, SECOND = 'Browser Meadow', 'Browser Orchard'
CATEGORY, MODULE = 'MeadowCategory', 'MeadowModule'


def browser_workflow(projects):
    from playwright.sync_api import expect, sync_playwright
    from editor_logic_workflow import review

    expect.set_options(timeout=30000)

    def enter(page, title):
        expect(page.locator('.home-grid')).to_be_visible()
        card = page.locator('.project-card').filter(has=page.get_by_role('heading', name=title, exact=True))
        card.locator('[data-enter]').click()
        expect(page.locator('#title')).to_contain_text(title)

    def open_browser(page):
        page.get_by_role('button', name='프로젝트 메뉴', exact=True).click()
        page.locator('.context-menu').get_by_role('button', name='프로젝트 브라우저', exact=True).click()
        window = page.get_by_role('region', name='프로젝트 브라우저', exact=True)
        expect(window).to_be_visible()
        return window

    def tab(window, name, group):
        window.get_by_role('button', name=name, exact=True).click()
        expect(window.locator('.browser-tabs .selected')).to_have_attribute('data-tab', group)

    def search(window, value):
        window.locator('[data-browser-control=object-query]').fill(value)
        window.get_by_role('button', name='검색 확정', exact=True).click()

    def author_fixture(page, window, kind, name, identifier):
        window.locator('[data-new]').click()
        page.locator('.context-menu').get_by_role('button', name=kind + ' 생성', exact=True).click()
        page.locator('#new-declaration-name').fill(name)
        page.locator('#new-declaration').click()
        editor = page.locator('.window[data-key=declaration]')
        expect(editor.locator('[data-declaration-id]')).to_have_text(identifier)
        approval = review(page, editor.locator('[data-declaration-review]'))
        approval.locator('#confirm').click()
        expect(approval).to_be_hidden(timeout=120000)
        expect(page.locator('#status')).to_have_text('검토한 변경을 최종 소스에 반영했습니다.')
        editor.locator(':scope > .window-title [data-close]').click()
        source = page.locator('.window[data-key=source]:visible')
        if source.count():
            source.locator(':scope > .window-title [data-close]').click()

    def choose_namespace(window, namespace):
        tree = window.locator('.browser-folder-tree')
        if not tree.is_visible():
            window.get_by_role('button', name='폴더 계층 펼치기', exact=True).click()
        node = tree.locator(f'[data-namespace="{namespace}"]')
        node.click()
        expect(node).to_have_attribute('aria-current', 'location')
        return tree

    def assert_semantic_paths(window, project):
        path = Path(project['path'])
        for scope in (window.locator('.browser-title-path'), window.locator('.browser-file-pane')):
            for private in (str(path.parent), path.name, '.cpack', '.celem', '.csbody'):
                expect(scope).not_to_contain_text(private)
                expect(scope).not_to_have_attribute('title', re.compile(re.escape(private)))
                expect(scope.locator(f'[title*="{private}"], [aria-label*="{private}"]')).to_have_count(0)

    def find_main(window, namespace):
        search(window, 'Main')
        row = window.locator(f'[data-object="{namespace}::Main"]')
        expect(row).to_be_visible()
        expect(window.locator(f'[data-object]:not([data-object^="{namespace}::"])')).to_have_count(0)
        return row

    with sync_playwright() as playwright, playwright.chromium.launch(**browser_options()) as browser, \
            open_packaged_logic(browser) as page:
        assert os.geteuid() != 0 and not Path('/workspace').exists()
        first, second = (projects[title] for title in (FIRST, SECOND))
        alpha, beta = (project['namespace'] for project in (first, second))
        category, module = alpha + '::' + CATEGORY, alpha + '::' + MODULE
        enter(page, FIRST)
        window = open_browser(page)
        author_fixture(page, window, '카테고리', CATEGORY, category)
        author_fixture(page, window, '모듈', MODULE, module)
        originals = {title: project_files(Path(project['path']).parent) for title, project in projects.items()}

        tab(window, '개념', 'concept')
        tree = choose_namespace(window, alpha)
        for other in (module, alpha + '::Main'):
            expect(tree.locator(f'[data-tree-id="{other}"]')).to_have_count(0)
        category_node = tree.locator(f'[data-tree-id="{category}"]')
        category_node.click()
        expect(category_node).to_have_attribute('aria-current', 'location')
        expect(window.locator('.browser-title-path')).to_contain_text(CATEGORY)
        assert_semantic_paths(window, first)

        tab(window, '모듈', 'module')
        tree = choose_namespace(window, alpha)
        for other in (category, alpha + '::Main'):
            expect(tree.locator(f'[data-tree-id="{other}"]')).to_have_count(0)
        search(window, 'Meadow')
        expect(window.locator('[data-object]')).to_have_count(1)
        expect(window.locator(f'[data-object="{module}"]')).to_be_visible()
        assert_semantic_paths(window, first)

        tab(window, '기능', 'feature')
        tree = choose_namespace(window, alpha)
        for other in (category, module):
            expect(tree.locator(f'[data-tree-id="{other}"]')).to_have_count(0)
        main = find_main(window, alpha)
        assert_semantic_paths(window, first)
        main.press('Enter')
        declaration = page.locator('.window[data-key=declaration]')
        expect(declaration.get_by_role('heading', name='Main', exact=True)).to_be_visible()
        expect(declaration.locator(':scope > .window-title')).not_to_contain_text(CATEGORY)
        declaration.get_by_role('button', name='직접 작성', exact=True).click()
        panel = page.locator('.window[data-key=blueprint]')
        expect(panel.locator('[data-native-source]')).to_have_value('return 0;\n')
        panel.get_by_role('button', name='창 닫기', exact=True).click()
        declaration.get_by_role('button', name='창 닫기', exact=True).click()

        # The same declaration window is retained when it closes. Switching
        # both ways must restore the header belonging to the new declaration.
        tab(window, '모듈', 'module')
        window.locator(f'[data-object="{module}"]').click()
        expect(declaration.get_by_role('heading', name=MODULE, exact=True)).to_be_visible()
        expect(declaration.locator('[data-declaration-id]')).to_have_text(module)
        page.get_by_role('button', name='Confectory 홈으로').click()

        enter(page, SECOND)
        window = open_browser(page)
        for name, group in (('개념', 'concept'), ('모듈', 'module'), ('기능', 'feature')):
            tab(window, name, group)
            tree = choose_namespace(window, beta)
            expect(tree.locator(f'[data-namespace="{alpha}"]')).to_have_count(0)
            for label in (CATEGORY, MODULE):
                expect(window).not_to_contain_text(label)
            expect(window.locator('[data-browser-control=object-query]')).to_have_value('')
        find_main(window, beta)
        assert_semantic_paths(window, second)
        page.get_by_role('button', name='Confectory 홈으로').click()
        enter(page, FIRST)
        window = open_browser(page)
        tab(window, '개념', 'concept')
        expect(window.locator('.browser-folder-tree').locator(f'[data-tree-id="{category}"]')).to_have_attribute('aria-current', 'location')
        assert all(project_files(Path(project['path']).parent) == originals[title] for title, project in projects.items())
    print('PASS installed ≡ opens Project Browser; category, namespace and module stay separate and use semantic paths', flush=True)
    print('PASS browser opens Main in its existing editor; project switch and return preserve scope and original files', flush=True)


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
    with tempfile.TemporaryDirectory(prefix='cfbrowser-') as scratch:
        with installed_editor(Path(scratch), package, image, sdk=True, extra_mounts=mounts, shm_size='512m') as (app, roots):
            app.launch([INSTALL + '/run'])
            assert not gtk_home(app)['model']['cards']
            projects = {}
            for title in (FIRST, SECOND):
                projects[title] = app.create(title, '', roots)
                gtk_menu(app, 52)
                gtk_home(app)
            app.close()
            assert projects[FIRST]['projectId'] != projects[SECOND]['projectId']
            result = subprocess.run(app.command([sys.executable, '/test/' + Path(__file__).name,
                                                '--browser', json.dumps(projects)], PLAYWRIGHT_NODEJS_PATH='/test/node'),
                                    capture_output=True, text=True, timeout=350)
            print(result.stdout, end='', flush=True)
            assert result.returncode == 0, re.sub(r'(http://127\.0\.0\.1:\d+/#)[0-9a-f]{32}', r'\1[redacted]', result.stderr)


if __name__ == '__main__':
    if sys.argv[1] == '--browser':
        browser_workflow(json.loads(sys.argv[2]))
    else:
        test_package(Path(sys.argv[1]).resolve(), sys.argv[2])
