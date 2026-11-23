"""Enter the existing direct C# wrapping draft from the v821 logical document."""
from playwright.sync_api import expect, sync_playwright

import v666_node_internal_api as fixture

f = fixture.f


def panel():
    return f.author()


def document():
    return panel().locator('.function-document')


def tab(name):
    return panel().get_by_role('tab', name=name, exact=True)


def open_feature():
    f.page.locator('#workspace').click(button='right', position={'x': 1300, 'y': 300})
    f.page.get_by_role('button', name='프로젝트 브라우저', exact=True).click()
    browser = f.page.locator('.window[data-key^="browser:project:"]')
    browser.get_by_role('button', name='기능', exact=True).click()
    browser.locator('[data-browser-control="object-query"]').fill('Flow')
    browser.locator('[data-browser-control="object-search"]').click()
    browser.locator(f'[data-object="{fixture.feature}"]').press('Enter')
    browser.locator('[data-close]').first.click()
    f.idle()
    f.page.locator('[data-operation="feature-author-open"]').first.click()
    expect(document().locator('[data-document-cell="calculate"]')).to_be_visible()


def edit_child(text, cancel=False):
    document().locator('[data-document-code="body"]').click()
    dialog = f.page.locator('.bp-script-dialog')
    body = dialog.locator('[data-code-region="body"]').text_content()
    assert 'Twice(amount) + 1' in body
    dialog.locator('[data-code-source]').evaluate(
        '(field,body)=>{const at=field.value.indexOf(body);if(at<0)throw Error("Missing body");'
        'field.focus();field.setSelectionRange(at,at+body.length)}', body)
    f.page.keyboard.insert_text(text)
    dialog.locator('[data-code-cancel]' if cancel else '[data-code-save]').click()
    expect(dialog).to_be_hidden()
    f.idle()


def restart(index):
    f.pending()
    f.page.close()
    f.stop()
    f.start(index)
    f.page = f.setup()
    f.page.set_viewport_size({'width': 1800, 'height': 1400})
    f.idle()


def review():
    panel().locator('[data-bp-complete]').click()
    f.idle()
    targets = f.page.locator('.window[data-key="targets"]')
    if targets.is_visible():
        targets.locator('[data-target-choice]').select_option('portable')
        targets.locator('[data-close]').click()
        panel().locator('[data-bp-complete]').click()
        f.idle()
    window = f.page.locator('.window[data-key="review"]')
    expect(window).to_be_visible()
    advanced = window.locator('[data-review-advanced]')
    if advanced.is_visible():
        advanced.click()
        window.locator('[data-advanced-reviewed]').check()
    return window


def run():
    f.start(0)
    f.invoke('select', {'id': fixture.feature})
    f.invoke('saveDraft', {})
    before = fixture.checkpoint()
    with sync_playwright() as playwright:
        expect.set_options(timeout=45000)
        f.browser = playwright.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        f.page = f.setup()
        f.page.set_viewport_size({'width': 1800, 'height': 1400})
        open_feature()
        tab('블루프린트 보기').click()
        panel().locator('[data-bp-node="calculate"] [data-internal-flow]').click()
        expect(panel().locator('[data-bp-node="body"] [data-internal-code]')).to_be_visible()
        expect(panel().locator('.bp-status')).to_contain_text('내부 흐름 미리보기')
        panel().locator('.bp-viewport').press('Control+z')
        expect(panel().locator('[data-bp-node="calculate"]')).to_be_visible()
        tab('논리 코드').click()
        document().locator('[data-document-internal="calculate"]').click()
        expect(document().locator('[data-document-cell="body"]')).to_be_visible(timeout=6000)
        expect(tab('논리 코드')).to_have_attribute('aria-selected', 'true')
        expect(document().locator('[data-document-add],[data-document-value],[data-document-name]')).to_have_count(0)
        expect(document().locator('[data-document-drag]:enabled')).to_have_count(0)
        assert fixture.checkpoint() == before
        fixture.original()

        edit_child('return amount+99;', cancel=True)
        assert not f.pending()['blueprint']
        edit_child('return amount+8;')
        held = f.pending()['blueprint']
        assert len(held) == 1 and held[0][1]['text'] == 'return amount+8;'
        tab('블루프린트 보기').click()
        expect(panel().locator('.bp-viewport')).to_be_visible()
        tab('네이티브 미리보기').click()
        preview = panel().locator('.function-native-preview')
        expect(preview.locator('[role=status]')).to_contain_text('지원하지')
        expect(preview.locator('[data-native-body]')).to_have_text('')
        tab('논리 코드').click()
        assert f.pending()['blueprint'] == held and fixture.checkpoint() == before
        fixture.original()
        f.checked('선택된 내부 흐름만 논리 코드로 열리고 보호된 C# 편집·취소 및 보기 왕복에서 입력과 원본을 보존한다')

        restart(1)
        expect(document().locator('[data-document-cell="body"]')).to_be_visible()
        assert f.pending()['blueprint'] == held
        document().press('Control+z')
        expect(document().locator('[data-document-cell="calculate"]')).to_be_visible()
        assert not f.pending()['blueprint']
        document().press('Control+y')
        expect(document().locator('[data-document-cell="body"]')).to_be_visible()
        assert f.pending()['blueprint'] == held and fixture.checkpoint() == before
        fixture.original()
        panel().locator('[data-bp-save]').click()
        expect(panel().locator('.bp-status')).to_have_text('저장됨')
        assert not f.pending()['blueprint']
        assert next(node for node in fixture.read(fixture.child)['nodes'] if node['id']=='body')['source']=='return amount+8;'
        fixture.original()
        window = review()
        window.locator('[data-reject]').click()
        expect(window).to_be_hidden()
        fixture.original()
        window = review()
        window.locator('#confirm').click()
        expect(window).to_be_hidden(timeout=120000)
        original_node = f.project/'Flow.node.json'
        assert original_node.read_bytes() == fixture.physical[original_node]
        fixture.build('v821-current-internal-flow', 11)
        restart(2)
        expect(document().locator('[data-document-cell="body"]')).to_be_visible()
        assert not f.pending()['blueprint']
        assert not f.errors and not f.external, (f.errors, f.external)
        f.checked('냉시작과 한 번의 Undo/Redo 후 같은 저장 계약으로 Review·명시 Confirm하여 실제 실행 결과 11을 확인했다')
        f.browser.close()


if __name__ == '__main__':
    print('Isolated fixture:', f.case, flush=True)
    try:
        run()
    finally:
        f.stop()
