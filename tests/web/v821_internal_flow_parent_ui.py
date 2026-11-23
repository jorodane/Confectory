"""v821 navigation and draft ownership across nested and sibling frames."""
import copy
import shutil

from playwright.sync_api import expect, sync_playwright

import v666_node_internal_nested_fixture as nested
from v821_internal_flow_document_ui import document, edit_child, open_feature, panel, restart, review, tab

f = nested.f
root = nested.parts[0]
parent = nested.parts[-1]


def cell(cell_id):
    return document().locator(f'[data-document-cell="{cell_id}"]')


def enter(cell_id):
    cell(cell_id).locator(f'[data-document-internal="{cell_id}"]').click()


def ancestor(index):
    panel().locator('.bp-breadcrumbs button').nth(index).click()


def selected(view):
    expect(tab(view)).to_have_attribute('aria-selected', 'true')


def fold(cell_id):
    return cell(cell_id).locator(f'[data-document-fold="{cell_id}"]')


def peer_source(expected, new_value=None):
    cell('calculate').locator('[data-document-code="calculate"]').click()
    dialog = f.page.locator('.bp-script-dialog')
    body = dialog.locator('[data-code-region="body"]')
    expect(body).to_contain_text(expected)
    if new_value is None:
        dialog.locator('[data-code-cancel]').click()
    else:
        dialog.locator('[data-code-source]').evaluate(
            '(field,body)=>{const start=field.value.indexOf(body);if(start<0)throw Error("Missing source");'
            'field.focus();field.setSelectionRange(start,start+body.length)}', body.text_content())
        f.page.keyboard.insert_text(new_value)
        dialog.locator('[data-code-save]').click()
    expect(dialog).to_be_hidden()


def run():
    second_project = f.case / 'same IDs, separate project'
    shutil.copytree(f.project, second_project)
    other_files = {p: p.read_bytes() for p in second_project.iterdir() if p.is_file()}
    original_project = f.env['CONFECTORY_WEB_PROJECT']
    f.start(0)
    f.invoke('select', {'id': nested.feature})
    f.invoke('saveDraft', {})
    before = nested.x.checkpoint()

    with sync_playwright() as playwright:
        expect.set_options(timeout=60000)
        f.browser = playwright.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        f.page = f.setup()
        f.page.set_viewport_size({'width': 1800, 'height': 1400})
        open_feature(root)
        selected('논리 코드')
        enter('peer')
        peer_source('return amount+1000;')
        fold('calculate').click()
        ancestor(0)
        enter(root)
        expect(cell(parent)).to_be_visible()
        tab('블루프린트 보기').click()
        panel().locator(f'[data-bp-node="{parent}"] [data-internal-flow]').click()
        expect(cell('calculate')).to_be_visible()
        fold('$entry').click()
        enter('calculate')
        expect(cell('body')).to_be_visible()

        edit_child('return amount+8;')
        held = copy.deepcopy(f.pending()['blueprint'])
        assert len(held) == 1 and f'|private:{nested.path}/calculate|' in held[0][0]
        fold('$entry').click()
        ancestor(2)
        selected('논리 코드')
        expect(fold('$entry')).to_have_attribute('aria-expanded', 'false')
        expect(document().locator('[data-document-code],[data-document-name],[data-document-value]')).to_have_count(0)
        ancestor(1)
        selected('블루프린트 보기')
        expect(panel().locator(f'.bp-viewport [data-bp-node="{parent}"]')).to_be_visible()
        ancestor(0)
        selected('논리 코드')
        expect(cell('peer').locator('[data-document-internal]')).to_have_count(0)
        expect(cell(root).locator('[data-document-internal]')).to_be_enabled()
        assert f.pending()['blueprint'] == held and nested.x.checkpoint() == before
        nested.x.original()
        f.checked('Parents keep their own logical folds or explicit Blueprint view; a pending child stays on its exact ancestor path')

        f.env['CONFECTORY_WEB_PROJECT'] = str(second_project / 'project.cproj')
        restart(1)
        assert not f.pending()['blueprint']
        open_feature(root)
        expect(cell('peer').locator('[data-document-internal]')).to_be_visible()
        enter('peer')
        expect(fold('calculate')).to_have_attribute('aria-expanded', 'true')
        peer_source('return amount+1000;')
        assert all(p.read_bytes() == value for p, value in other_files.items())

        f.env['CONFECTORY_WEB_PROJECT'] = original_project
        restart(2)
        selected('논리 코드')
        expect(cell(root)).to_be_visible()
        assert f.pending()['blueprint'] == held
        document().press('Control+z')
        expect(cell('calculate')).to_be_visible()
        assert not f.pending()['blueprint']
        document().press('Control+y')
        expect(cell('body')).to_be_visible()
        expect(fold('$entry')).to_have_attribute('aria-expanded', 'false')
        assert f.pending()['blueprint'] == held and nested.x.checkpoint() == before
        nested.x.original()
        f.checked('Cold roots and same-ID projects preserve separate drafts; Undo/Redo returns to the exact child')

        ancestor(0)
        panel().locator('[data-bp-save]').click()
        expect(panel().locator('.bp-status')).to_have_text('저장됨')
        assert not f.pending()['blueprint']
        nested.x.original()
        window = review()
        window.locator('[data-reject]').click()
        expect(window).to_be_hidden()
        nested.x.original()
        review().locator('#confirm').click()
        expect(window).to_be_hidden(timeout=120000)
        nested.x.build('v821-parent-round-trip', 11)
        assert (f.project / 'Flow.node.json').read_bytes() == nested.x.physical[f.project / 'Flow.node.json']
        assert (f.project / 'Peer.node.json').read_bytes() == nested.x.physical[f.project / 'Peer.node.json']
        f.checked('Only explicit Save and Confirm apply the selected child, retaining both physical C# originals')

        enter('peer')
        expect(fold('calculate')).to_have_attribute('aria-expanded', 'false')
        fold('calculate').click()
        peer_source('return amount+1000;', 'return amount+2000;')
        peer_draft = copy.deepcopy(f.pending()['blueprint'])
        assert len(peer_draft) == 1 and '|private:peer|' in peer_draft[0][0]
        after_confirm = nested.x.checkpoint()
        ancestor(0)
        enter(root)
        selected('블루프린트 보기')
        panel().locator(f'[data-bp-node="{parent}"] [data-internal-flow]').click()
        expect(cell('calculate')).to_be_visible()
        enter('calculate')
        expect(cell('body')).to_be_visible()
        expect(fold('$entry')).to_have_attribute('aria-expanded', 'false')
        ancestor(0)
        enter('peer')
        peer_source('return amount+2000;')
        assert f.pending()['blueprint'] == peer_draft and nested.x.checkpoint() == after_confirm
        assert not f.errors and not f.external, (f.errors, f.external)
        f.checked('Normal sibling navigation preserves an unapplied source input without showing it in the other frame')
        f.browser.close()


if __name__ == '__main__':
    print('Isolated fixture:', f.case, flush=True)
    try:
        run()
    finally:
        f.stop()
