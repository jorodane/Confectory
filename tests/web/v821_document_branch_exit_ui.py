"""Edit or split an owned M11 return from Logic Code, with real Save and Confirm."""
import ast
import copy
import json
import os
from pathlib import Path
import sys

from playwright.sync_api import expect, sync_playwright

from editor_navigation import choose_project_tool
import v666_node_branch_exit_fixture as fixture

f = fixture.f
x = fixture.x
feature = fixture.n.feature
insert_shared = '--insert-shared' in sys.argv[3:]
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
    return next(node['graph'] for node in t.at(graph)['nodes'] if node['id'] == 'calculate')


def enter_child():
    for segment in t.path.split('/'):
        doc().locator(f'[data-document-internal="{segment}"]').click()
        f.idle()


def checkpoint_content():
    saved = json.loads(checkpoint.read_bytes())
    assert saved['version'] == 1
    return ({row['id']: {key: value for key, value in row.items() if key != 'revision'}
             for row in saved['changes']},
            {key: value for key, value in saved['history'].items() if key != 'epoch'})


def check_previous(new_id, changed):
    report = os.environ.get('CONFECTORY_PREVIOUS_EXIT_EDITOR')
    if not report:
        return
    current_report, current_env = f.report, f.env.copy()
    saved = checkpoint_content()
    f.page.close()
    f.stop()
    try:
        f.report = json.loads(Path(report).read_text())
        f.env['CONFECTORY_EDITOR_REPO'] = os.environ.get('CONFECTORY_PREVIOUS_EXIT_REPO', str(f.repo))
        f.start(2)
        loaded = fixture.read()
        assert loaded['edges'] == changed['edges']
        f.page = f.setup()
        f.page.set_viewport_size({'width': 1800, 'height': 1400})
        expect(doc()).to_be_visible()
        show_alternate()
        expect(exit_control(new_id)).to_have_text('Continue')
        assert checkpoint_content() == saved
        x.original()
        f.page.close()
    finally:
        f.stop()
        f.report, f.env = current_report, current_env
    f.start(3)
    f.page = f.setup()
    f.page.set_viewport_size({'width': 1800, 'height': 1400})
    expect(doc()).to_be_visible()
    f.checked('The previous editor reads the same saved version-1 exit, source edits and history.')


def check_saved_history(changed):
    history = checkpoint_content()[1]
    assert history['undo'][:-1] == prior_history['undo']
    assert [unit['id'] for unit in history['undo'][-1]['units']] == [t.root]
    choose_project_tool(f.page, '의미 편집 이력')
    window = f.page.locator('.window[data-key=history]')
    expect(window.locator('[data-history-tip=undo]')).to_contain_text(t.root)
    window.locator('[data-history-move=undo]').click()
    f.idle()
    assert fixture.read()['edges'] == shared_plan['edges']
    expect(window.locator('[data-history-tip=undo]')).to_contain_text(other_id)
    expect(window.locator('[data-history-tip=redo]')).to_contain_text(t.root)
    window.locator('[data-history-move=redo]').click()
    f.idle()
    assert fixture.read()['edges'] == changed['edges']
    window.locator('[data-close]').first.click()
    f.invoke('saveDraft', {})
    assert checkpoint_content()[0][other_id] == other_draft
    assert checkpoint_content()[1]['undo'] == history['undo']
    x.original()
    f.checked('One saved return edit is reversible after process restart and retains the preceding source edit.')


def run():
    open_document()
    assert not doc().locator('[data-document-branch-exit]').count()
    enter_child()
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


def run_insert():
    open_document()
    expect(doc().locator('[data-document-branch-return]')).to_have_count(0)
    if t.nested:
        doc().locator('[data-document-internal="frame"]').click()
        f.idle()
        doc().locator('[data-document-internal="peer"]').click()
        f.idle()
        expect(doc().locator('[data-document-branch="case:alternate"]')).to_have_text('Alternate')
        expect(doc().locator('[data-document-branch-return]')).to_have_count(0)
        panel().locator('.bp-breadcrumbs button').first.click()
        f.idle()
    enter_child()
    existing = exit_control('shared')
    expect(existing).to_have_text('Alternate')
    show_alternate()
    branch = doc().locator('[data-document-panel="case:alternate"]')
    add = branch.locator('[data-document-branch-return="$exit:shared"]')
    expect(add).to_have_attribute('data-document-return-port', 'case:alternate')
    expect(doc().locator('[data-document-branch-return][data-document-return-port="next"]')).to_be_visible()
    expect(add).to_have_text('다음 세부기능 추가')
    category = f.page.get_by_role('dialog', name='다음 세부기능 추가')
    basic = f.page.get_by_role('dialog', name='기본 기능')
    menu = f.page.get_by_role('listbox', name='새 분기 반환 선택')

    def open_return():
        add.press('Enter')
        category.get_by_role('button', name='기본 기능', exact=True).click()
        basic.get_by_role('button', name='분기 반환', exact=True).click()
        expect(menu).to_be_visible()

    add.press('Enter')
    expect(category.get_by_role('button', name='기본 기능')).to_be_focused()
    f.page.keyboard.press('Escape')
    expect(add).to_be_focused()
    open_return()
    f.page.keyboard.press('Escape')
    expect(add).to_be_focused()
    assert not pending() and checkpoint.read_bytes() == before
    x.original()

    open_return()
    menu.locator('[data-branch-option="next"]').click()
    held = pending()
    assert len(held) == 1 and held[0][1]['type'] == 'branch-exits'
    plan = json.loads(held[0][1]['text'])
    new_id, = (key for key in plan['exits'] if key != 'shared')
    assert new_id.startswith('branch_')
    changed = copy.deepcopy(shared_plan)
    changed['exits'][new_id] = {'executionBranch': 'next'}
    changed['edges'][1]['to'] = 'exit:' + new_id
    assert plan == changed
    if t.nested:
        invalid = copy.deepcopy(plan)
        invalid['exits'][new_id]['executionBranch'] = 'peer/alternate'
        fixture.batch(invalid, ok=False)
        assert pending() == held and checkpoint.read_bytes() == before
    expect(existing).to_have_text('Alternate')
    expect(branch.locator(f'[data-document-branch-exit="$exit:{new_id}"]')).to_have_text('Continue')
    expect(doc().locator('[data-document-branch-return]')).to_have_count(0)
    doc().press('Control+z')
    expect(add).to_be_visible()
    assert not pending()
    doc().press('Control+y')
    assert pending() == held
    assert checkpoint.read_bytes() == before

    panel().get_by_role('tab', name='블루프린트 보기', exact=True).click()
    expect(panel().locator(f'[data-bp-node="$exit:{new_id}"] [data-bp-branch-name]')).to_have_value('Continue')
    expect(panel().locator('[data-bp-node="$exit:shared"] [data-bp-branch-name]')).to_have_value('Alternate')
    panel().get_by_role('tab', name='논리 코드', exact=True).click()
    panel().locator('[data-bp-save]').click()
    expect(panel().locator('.bp-status')).to_have_text('저장됨', timeout=120000)
    assert not pending()
    x.original()
    cold_open(1)
    show_alternate()
    expect(exit_control('shared')).to_have_text('Alternate')
    expect(doc().locator('[data-document-panel="case:alternate"]').locator(
        f'[data-document-branch-exit="$exit:{new_id}"]')).to_have_text('Continue')
    assert fixture.read()['edges'] == changed['edges']
    if t.nested:
        assert checkpoint_content()[0][other_id] == other_draft
    f.checked('Cancel, one Undo/Redo, both views and cold Save retain exactly the selected return insertion.')

    check_previous(new_id, changed)
    if t.nested:
        check_saved_history(changed)
    saved = checkpoint_content()
    review().locator('[data-reject]').click()
    x.original()
    assert checkpoint_content() == saved
    window = review()
    window.locator('#confirm').click()
    expect(window).to_be_hidden(timeout=120000)
    f.idle()
    fixture_graph(expected).update(changed)
    assert json.loads(graph_path.read_text()) == expected
    assert all(path.read_bytes() == raw for path, raw in x.physical.items() if path != graph_path)
    if t.nested:
        assert checkpoint_content()[0][other_id] == other_draft
    fixture.run('document-shared-return-split', swapped=True)
    assert not f.errors and not f.external, (f.errors, f.external)
    f.checked('Confirm adds one new return to the chosen case; real C# returns Continue only there and preserves other paths and outputs.')


def cold_open(index):
    f.pending()
    f.page.close()
    f.stop()
    f.start(index)
    f.page = f.setup()
    f.page.set_viewport_size({'width': 1800, 'height': 1400})
    expect(doc()).to_be_visible()


def seed_same_named_peer():
    n = fixture.n
    file = f.project / n.graph_file
    graph = json.loads(file.read_text())
    peer_source = 'Peer.body.node.json'
    peer = {'id': 'peer', 'kind': 'graph', 'intent': 'Unchanged sibling', 'control': 'next',
            'signature': n.sig([]), 'arguments': {}, 'graph': {
                'schema': 1, 'profile': 'sync-acyclic-methods-v1', 'entry': 'body',
                'nodes': [{'id': 'body', 'kind': 'code', 'intent': 'Same local ID', 'control': 'next',
                           'signature': n.sig([]), 'arguments': {}, 'implementation': peer_source}],
                'edges': [n.edge('body', 'exit:return')], 'exits': {'return': None},
            }}
    source = 'return;'
    if t.nested:
        peer_graph = peer['graph']
        peer_graph['profile'] = 'sync-acyclic-switch-v1'
        peer_graph['nodes'][0].update(control='switch', executionEnum=copy.deepcopy(n.execution))
        peer_graph['edges'].append(n.edge('body', 'return:body', 'case:alternate'))
        source = 'return Result.Alternate;'
    parent = n.at(graph)
    parent['nodes'].append(peer)
    after = next((edge for edge in parent['edges'] if edge['from'] == 'after'), None)
    if after:
        parent['edges'].append(n.edge('peer', after['to']))
        after['to'] = 'peer'
    else:
        parent['edges'].append(n.edge('after', 'peer'))
    definitions = f.metadata('featureBlueprintNodes', featureSource=n.function, graph=graph,
                             implementationContext={'implementation': x.impl}, bodyTarget='common')
    known = next(row for row in definitions['nestedNodes'] if row['id'] == (n.frame+'/' if n.frame else '')+'peer/body')
    (f.project/peer_source).write_text(json.dumps({'schema': 1, 'node': 'body',
                                                  'definitionHash': known['definitionHash'], 'source': source}))
    file.write_text(json.dumps(graph, ensure_ascii=False))


try:
    if insert_shared and not fixture.n.copy_mode:
        seed_same_named_peer()
    f.start(0)
    f.invoke('select', {'id': feature})
    f.invoke('saveDraft', {})
    fixture.wrap()
    shared_plan = {'entry': 'body', 'exits': {'shared': {'executionBranch': 'alternate'}},
                   'edges': [fixture.n.edge('body', 'exit:shared'), fixture.n.edge('body', 'exit:shared', 'case:alternate')]}
    fixture.batch(shared_plan if insert_shared else fixture.plan())
    fixture.confirm()
    fixture.run('document-branch-returns-baseline', all_alternate=insert_shared)
    x.physical = {path: path.read_bytes() for path in f.project.rglob('*')
                  if path.is_file() and '.confectory' not in path.parts}
    graph_path = f.project / fixture.n.graph_file
    expected = copy.deepcopy(json.loads(graph_path.read_text()))
    assert fixture_graph(expected)['executionExitMode'] is True
    if not insert_shared:
        fixture_graph(expected)['exits'] = fixture.plan(swapped=True)['exits']
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    if insert_shared and t.nested:
        other_id = f.n + 'SlotBody/body:common/node:body'
        other_graph = f.n + 'SlotBody/body:common'
        other = t.read(other_graph)
        t.rpc('source', id=other_graph, node='body', basis=other['basis'],
              text='slotCount=amount+7;slotReady=true;return amount+3;')
        f.invoke('saveDraft', {})
        other_changes, prior_history = checkpoint_content()
        other_draft = other_changes[other_id]
        assert [unit['id'] for unit in prior_history['undo'][-1]['units']] == [other_id]
    before = checkpoint.read_bytes()
    with sync_playwright() as playwright:
        expect.set_options(timeout=30000)
        with playwright.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'],
                                        ignore_default_args=['--disable-dev-shm-usage']) as browser:
            f.browser = browser
            f.page = f.setup()
            f.page.set_viewport_size({'width': 1800, 'height': 1400})
            (run_insert if insert_shared else run)()
finally:
    (f.case / 'checks.json').write_text(json.dumps(f.checks, ensure_ascii=False, indent=2))
    f.stop()
    print('Evidence:', f.case)
