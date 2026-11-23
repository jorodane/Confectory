"""Edit existing owned branch exits from Logic Code, with real Save and Confirm."""
import ast
import copy
import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

import v666_node_branch_exit_fixture as fixture

f = fixture.f
x = fixture.x
feature = fixture.n.feature
helper = Path(__file__).with_name('v821_function_document_ui.py')
functions = {'panel', 'doc', 'pending', 'open_document', 'review'}
t = fixture.n
exec(compile(ast.Module(body=[node for node in ast.parse(helper.read_text()).body
                              if isinstance(node, ast.FunctionDef) and node.name in functions],
                        type_ignores=[]), str(helper), 'exec'), globals())


def exit_control(exit_id):
    return doc().locator(f'[data-document-branch-exit="$exit:{exit_id}"]')


def choose(control, option):
    control.click()
    f.page.get_by_role('listbox', name='기존 분기 선택').locator(f'[data-branch-option="{option}"]').click()


def show_alternate():
    doc().locator('[data-document-branch="case:alternate"]').click()


def fixture_graph(graph):
    return next(node['graph'] for node in graph['nodes'] if node['id'] == 'calculate')


def run():
    open_document()
    assert not doc().locator('[data-document-branch-exit]').count()
    doc().locator('[data-document-internal="calculate"]').click()
    f.idle()
    expect(doc()).to_be_visible()
    proceed = exit_control('proceed')
    finish = exit_control('finish')
    expect(proceed).to_have_text('Continue')
    proceed.press('Enter')
    expect(f.page.get_by_role('listbox', name='기존 분기 선택')).to_be_visible()
    f.page.keyboard.press('Escape')
    expect(proceed).to_be_focused()
    assert not pending() and checkpoint.read_bytes() == before

    choose(proceed, 'alternate')
    show_alternate()
    expect(finish).to_have_text('Alternate')
    choose(finish, 'next')
    assert len(pending()) == 1 and json.loads(pending()[0][1]['text']) == fixture.plan(swapped=True)
    expect(proceed).to_have_text('Alternate')
    expect(finish).to_have_text('Continue')
    assert checkpoint.read_bytes() == before
    x.original()
    f.checked('Logic Code changes only the selected existing return IDs. Escape preserves the draft and returns focus.')

    panel().get_by_role('tab', name='블루프린트 보기', exact=True).click()
    expect(panel().locator('[data-bp-node="$exit:proceed"] [data-bp-branch-name]')).to_have_value('Alternate')
    expect(panel().locator('[data-bp-node="$exit:finish"] [data-bp-branch-name]')).to_have_value('Continue')
    panel().get_by_role('tab', name='논리 코드', exact=True).click()
    panel().locator('[data-bp-save]').click()
    expect(panel().locator('.bp-status')).to_have_text('저장됨', timeout=120000)
    assert not pending()
    x.original()
    cold_open(1)
    expect(exit_control('proceed')).to_have_text('Alternate')
    show_alternate()
    expect(exit_control('finish')).to_have_text('Continue')
    f.checked('Both views see the same return binding and a new editor process restores the pending Save.')

    review().locator('[data-reject]').click()
    x.original()
    window = review()
    window.locator('#confirm').click()
    expect(window).to_be_hidden(timeout=120000)
    f.idle()
    actual = json.loads(graph_path.read_text())
    assert actual == expected
    assert all(path.read_bytes() == raw for path, raw in x.physical.items() if path != graph_path)
    fixture.run('document-branch-returns', swapped=True)
    assert not f.errors and not f.external, (f.errors, f.external)
    f.checked('Review cancellation leaves originals intact. Confirm changes only return values and real C# execution follows them.')


def cold_open(index):
    f.pending()
    f.page.close()
    f.stop()
    f.start(index)
    f.page = f.setup()
    f.page.set_viewport_size({'width': 1800, 'height': 1400})
    expect(doc()).to_be_visible()


try:
    f.start(0)
    f.invoke('select', {'id': feature})
    f.invoke('saveDraft', {})
    fixture.wrap()
    fixture.batch(fixture.plan())
    fixture.confirm()
    fixture.run('document-branch-returns-baseline')
    x.physical = {path: path.read_bytes() for path in f.project.rglob('*')
                  if path.is_file() and '.confectory' not in path.parts}
    graph_path = f.project / fixture.n.graph_file
    expected = copy.deepcopy(json.loads(graph_path.read_text()))
    assert fixture_graph(expected)['executionExitMode'] is True
    fixture_graph(expected)['exits'] = fixture.plan(swapped=True)['exits']
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    before = checkpoint.read_bytes()
    with sync_playwright() as playwright:
        expect.set_options(timeout=30000)
        with playwright.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox']) as browser:
            f.browser = browser
            f.page = f.setup()
            f.page.set_viewport_size({'width': 1800, 'height': 1400})
            run()
finally:
    (f.case / 'checks.json').write_text(json.dumps(f.checks, ensure_ascii=False, indent=2))
    f.stop()
    print('Evidence:', f.case)
