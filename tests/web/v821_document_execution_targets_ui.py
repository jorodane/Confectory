"""Select existing detached execution cells in Logic Code with real Save and Confirm."""
import ast
import copy
import json
from pathlib import Path
import sys
from types import SimpleNamespace

from playwright.sync_api import expect, sync_playwright

# Both fixtures extend the same caller graph. The detached lead already points
# to the existing entry, and the detached tail already points to the old exit.
import v666_entry_recovery_fixture as entry
import v666_route_recovery_fixture as route

x = entry.x
assert x is route.x and x.out_mode, 'Run with --out-root for the detached tail input contract.'
f = x.f
t = SimpleNamespace(feature=x.main_id)
graph_path = f.project / 'Main.graph.json'
open_start = '--open-start' in sys.argv
open_next = '--open-next' in sys.argv
assert not (open_start and open_next)
if open_start:
    x.cg['entry'] = ''
if open_next:
    x.cg['edges'] = [link for link in x.cg['edges'] if link['from'] != 'after']
graph_path.write_text(json.dumps(x.cg, ensure_ascii=False))
x.physical[graph_path] = graph_path.read_bytes()
helper = Path(__file__).with_name('v821_function_document_ui.py')
names = {'panel', 'doc', 'open_document', 'pending', 'restart', 'review'}
exec(compile(ast.Module(body=[node for node in ast.parse(helper.read_text()).body
                              if isinstance(node, ast.FunctionDef) and node.name in names],
                        type_ignores=[]), str(helper), 'exec'), globals())


def execution_button(source):
    return doc().locator(f'[data-document-execution-target="{source}"]')


def picker(source):
    button = execution_button(source)
    expect(button).to_be_visible(timeout=10000)
    button.click()
    return f.page.get_by_role('dialog', name='시작 대상 선택' if source == '$entry' else '다음 실행 대상 선택')


def choose(source, target):
    dialog = picker(source)
    choices = dialog.locator('[data-document-route-choice]')
    offered = choices.locator('option').evaluate_all('(options) => options.map(option => option.value)')
    assert target in offered and source not in offered and 'invoke' not in offered, offered
    assert ('tail' in offered) == (source == 'after'), offered
    choices.select_option(target)
    dialog.get_by_role('button', name='적용', exact=True).click()
    expect(dialog).to_be_hidden()


def main_order():
    return doc().locator(':scope > [data-document-cell]').evaluate_all(
        '(cards) => cards.map(card => card.dataset.documentCell)')


def save_one(checkpoint, source, target):
    start = len(f.traffic)
    panel().locator('[data-bp-save]').click()
    expect(panel().locator('.bp-status')).to_have_text('저장됨', timeout=120000)
    assert not pending()
    expected = {'action': 'entry', 'node': '$entry', 'to': target} if source == '$entry' else {
        'action': 'route', 'node': source, 'port': 'next', 'to': target}
    writes = [packet['input'] for row in f.traffic[start:] if (packet := row.get('invoke', {})).get('endpoint') == 'blueprint'
              and packet['input'].get('action') == 'authorBatch']
    assert len(writes) == 1 and writes[0]['edits'] == [expected], writes
    saved = json.loads(checkpoint.read_bytes())
    receipt = next(row['authorSaveReceipt'] for row in saved['changes'] if row['id'] == x.caller)
    assert receipt['ownedEntry' if source == '$entry' else 'ownedRoute'] is True, receipt


def confirm(before, checkpoint, conflicting=None):
    review().locator('[data-reject]').click()
    assert graph_path.read_bytes() == before
    dialog = review()
    if conflicting is not None:
        frozen = checkpoint.read_bytes()
        graph_path.write_text(json.dumps(conflicting))
        changed = graph_path.read_bytes()
        try:
            dialog.locator('#confirm').click()
            f.idle()
            assert graph_path.read_bytes() == changed and checkpoint.read_bytes() == frozen
        finally:
            graph_path.write_bytes(before)
        if dialog.is_visible():
            dialog.locator('[data-reject]').click()
        dialog = review()
    dialog.locator('#confirm').click()
    expect(dialog).to_be_hidden(timeout=120000)
    f.idle()


def run(checkpoint):
    baseline = graph_path.read_bytes()
    frozen = checkpoint.read_bytes()
    exit_cards = [] if open_next else ['$exit:return']
    assert main_order() == (['$entry'] if open_start else ['$entry', 'invoke', 'after'] + exit_cards)
    dialog = picker('$entry')
    expect(dialog.get_by_role('button', name='적용', exact=True)).to_be_disabled()
    dialog.locator('[data-document-route-choice]').select_option('lateLead')
    dialog.get_by_role('button', name='취소', exact=True).click()
    expect(execution_button('$entry')).to_be_focused()
    assert not pending() and checkpoint.read_bytes() == frozen
    x.original()

    choose('$entry', 'lead')
    started = ['$entry', 'lead', 'invoke', 'after']
    assert main_order() == started + exit_cards
    assert checkpoint.read_bytes() == frozen
    save_one(checkpoint, '$entry', 'lead')
    x.original()
    restart(1)
    assert main_order() == started + exit_cards
    confirm(baseline, checkpoint)
    expected = copy.deepcopy(x.cg)
    expected['entry'] = 'lead'
    assert json.loads(graph_path.read_bytes()) == expected
    x.build('logic-entry-confirmed', 0 if open_next else 10, 'lead\n'+x.initial_stdout)
    f.checked('Logic Code reconnects the explicit owned start; cancellation, cold reopen and native output agree.')

    baseline = graph_path.read_bytes()
    choose('after', 'tail')
    assert main_order() == started + ['tail', '$exit:return']
    save_one(checkpoint, 'after', 'tail')
    restart(2)
    assert main_order() == started + ['tail', '$exit:return']
    expected['edges'] = [link for link in expected['edges'] if link['from'] != 'after']
    conflicting = copy.deepcopy(expected)
    conflicting['edges'].append(x.edge('after', 'lateTail'))
    confirm(baseline, checkpoint, conflicting)
    expected['edges'].append(x.edge('after', 'tail'))
    assert json.loads(graph_path.read_bytes()) == expected
    assert all(path.read_bytes() == original for path, original in x.physical.items() if path != graph_path)
    x.build('logic-next-confirmed', 10, 'lead\n'+x.initial_stdout+'\ntail:10')
    assert not pending() and not f.errors and not f.external, (f.errors, f.external)
    f.checked('One next edge reconnects the detached cell with its existing input and exit; conflicting source bytes survive.')


try:
    x.build('logic-routes-baseline', 0 if open_start or open_next else 10, '' if open_start else x.initial_stdout)
    f.start(0)
    f.invoke('select', {'id': x.main_id})
    f.invoke('saveDraft', {})
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    with sync_playwright() as playwright:
        expect.set_options(timeout=30000)
        with playwright.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox']) as f.browser:
            f.page = f.setup()
            f.page.set_viewport_size({'width': 1800, 'height': 1350})
            open_document()
            run(checkpoint)
finally:
    f.stop()
    print('Evidence:', f.case, flush=True)
