"""Shared browser controls for first-use Logic Code acceptance."""
import time

from playwright.sync_api import expect
from editor_navigation import open_workspace_menu


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


def edit_body(page, panel, text, *, change):
    expect(panel.get_by_role('tab', name='논리 코드', exact=True)).to_have_attribute('aria-selected', 'true')
    panel.locator('[data-document-code=body]').click()
    dialog = page.locator('.bp-script-dialog')
    editor = dialog.locator('[data-code-source]')
    expect(editor).to_be_visible()
    body = dialog.locator('[data-code-highlight] > [data-code-region=body]')
    if change:
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
        assert body.text_content() == text
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


def run_from_dock(page, marker, expected):
    marker.unlink(missing_ok=True)
    page.get_by_role('button', name='프로젝트 실행', exact=True).click()
    deadline = time.monotonic() + 120
    while not marker.is_file() and time.monotonic() < deadline:
        page.wait_for_timeout(100)
    assert marker.is_file(), 'Confirmed code did not run'
    expect(page.locator('.run-window:visible [data-run-frame]')).to_have_text('종료 코드 0', timeout=120000)
    assert marker.read_text() == expected
