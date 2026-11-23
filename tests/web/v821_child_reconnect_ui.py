"""Real Logic Code reconnect on an owned child, with a previous-reader check."""
import ast
import copy
import json
import os
from pathlib import Path
import sys
import uuid

from playwright.sync_api import expect, sync_playwright

import v666_node_names_recovery_fixture as t

f, x = t.f, t.x
depth = int(sys.argv[3])
assert depth in (1, 2)
leaf_profile = 'sync-acyclic-nested-v1' if '--nested-profile' in sys.argv[4:] else 'sync-acyclic-methods-v1'
path = 'body' if depth == 1 else 'body/nest'
peer = path.replace('body', 'other', 1)
frame = t.graph + '/graph:' + path.replace('/', '/graph:')
peer_frame = t.graph + '/graph:' + peer.replace('/', '/graph:')
graph_path = f.project / t.graph_file
helper = Path(__file__).with_name('v821_function_document_ui.py')
names = {'panel', 'doc', 'open_document', 'pending', 'restart', 'review'}
exec(compile(ast.Module(body=[node for node in ast.parse(helper.read_text()).body
                              if isinstance(node, ast.FunctionDef) and node.name in names],
                        type_ignores=[]), str(helper), 'exec'), globals())


def edge(source, target):
    return {'from': source, 'port': 'next', 'to': target}


def signature(args=(), result='void'):
    return {'args': [{'name': name, 'type': kind} for name, kind in args], 'return': result}


def seed():
    sources = {}

    def code(owner, cell, source, sig=None, args=None):
        key = '/'.join(part for part in [owner, cell] if part)
        name = 'Pair.' + key.replace('/', '.') + '.node.json'
        sources[key] = (name, source)
        return dict(id=cell, kind='code', control='next', intent=cell, signature=sig or signature(),
                    arguments=args or {}, implementation=name)

    def graph(nodes, entry, edges, returns=None, profile=leaf_profile):
        return dict(schema=1, profile=profile, entry=entry, nodes=nodes, edges=edges, exits={'return': returns})

    amount = signature([('amount', 'int')], 'int')
    target = graph([
        code(path, 'inner', 'System.Console.WriteLine("inner");return amount+3;', amount, {'amount': {'input': 'amount'}}),
        code(path, 'tail', 'System.Console.WriteLine("tail");'),
        code(path, 'lead', 'System.Console.WriteLine("chosen lead");'),
        code(path, 'piece', 'System.Console.WriteLine("chosen piece:"+value);', signature([('value', 'int')]),
             {'value': {'node': 'inner', 'output': 'return'}}),
    ], 'inner', [edge('inner', 'tail'), edge('tail', 'exit:return'), edge('lead', 'inner'), edge('piece', 'exit:return')],
       {'node': 'inner', 'output': 'return'})
    sibling = graph([code(peer, 'lead', 'System.Console.WriteLine("peer lead");'),
                     code(peer, 'piece', 'System.Console.WriteLine("peer piece");')],
                    'lead', [edge('lead', 'piece'), edge('piece', 'exit:return')])

    def compound(cell, child, args=None, sig=None):
        return dict(id=cell, kind='graph', control='next', intent=cell, signature=sig or signature(),
                    arguments=args or {}, graph=child)

    if depth == 2:
        target = graph([compound('nest', target, {'amount': {'input': 'amount'}}, amount),
                        code('body', 'lead', 'System.Console.WriteLine("parent lead");')], 'nest',
                       [edge('nest', 'lead'), edge('lead', 'exit:return')], {'node': 'nest'}, 'sync-acyclic-nested-v1')
        sibling = graph([compound('nest', sibling), code('other', 'piece', 'return;')], 'nest',
                        [edge('nest', 'piece'), edge('piece', 'exit:return')], profile='sync-acyclic-nested-v1')

    root = copy.deepcopy(t.definition)
    root['profile'] = 'sync-acyclic-nested-v1'
    root['nodes'] = [compound('body', target, root['nodes'][0]['arguments'], amount), compound('other', sibling),
                     code('', 'lead', 'System.Console.WriteLine("root lead");'), root['nodes'][1]]
    root['edges'] = [edge('body', 'other'), edge('other', 'lead'), edge('lead', 'after'), edge('after', 'exit:return')]
    defs = f.metadata('blueprintDescribeOwned', project=str(f.manifest), id=f.n+'PairBody',
                      text=(f.project/'PairBody.celem').read_text(), bodyTarget='common', graph=root, definitionsOnly=True)
    assert defs['state'] == 'node-definitions', defs
    declarations = {row['id']: row['definitionHash'] for row in defs['nodes'] + defs['nestedNodes']}
    for key, (file, body) in sources.items():
        (f.project/file).write_text(json.dumps(dict(schema=1, node=key.split('/')[-1], definitionHash=declarations[key], source=body)))
    after = f.project/'Pair.after.node.json'
    after.write_text(json.dumps({**json.loads(after.read_text()), 'definitionHash': declarations['after']}))
    graph_path.write_text(json.dumps(root))
    x.physical = {file: file.read_bytes() for file in f.project.iterdir() if file.is_file()}
    return root, f.project / sources[peer + '/piece'][0]


def selected(root):
    for name in path.split('/'):
        root = next(node['graph'] for node in root['nodes'] if node['id'] == name)
    return root


def read(graph=frame):
    return f.invoke('blueprint', {'action': 'read', 'id': graph})['result']['result']


def saved_content(checkpoint):
    data = json.loads(checkpoint.read_bytes())
    assert data['version'] == 1
    # Review may refresh the runtime context and live revisions. Compare the
    # actual persisted drafts, receipts, source leases and reversible history.
    return ({row['id']: {key: value for key, value in row.items() if key != 'revision'}
             for row in data['changes']}, {key: value for key, value in data['history'].items() if key != 'epoch'})


def run_ui(checkpoint, root, sibling_source):
    for name in path.split('/'):
        doc().locator(f'[data-document-internal="{name}"]').click()
        f.idle()
    button = doc().locator('[data-document-execution-target="$entry"]')
    expect(button).to_be_visible(timeout=10000)
    before = read()
    binding = before['documentFrameReconnectBinding']
    assert (binding['root'], binding['path'], binding['graph']) == (t.graph, path, frame)
    assert before['documentFrameReconnectTargets'] == {'$entry': ['lead'], 'tail': ['piece']}
    assert not read(peer_frame).get('documentFrameReconnectBinding')
    frozen = checkpoint.read_bytes()
    for graph_id, to, observed in [(t.graph, 'lead', binding), (peer_frame, 'lead', binding), (frame, peer_frame+'/node:lead', binding),
                                    (frame, 'lead', {**binding, 'path': peer})]:
        f.invoke('blueprint', dict(action='authorBatch', id=graph_id, documentFrame=observed, attempt=uuid.uuid4().hex,
                                   checkpointHash=before['checkpointHash'], sourceProof=x.proof(before),
                                   edits=[dict(action='entry', node='$entry', to=to)]), False)
    assert checkpoint.read_bytes() == frozen and not pending()

    def pick(source, chosen, cancel=False):
        trigger = doc().locator(f'[data-document-execution-target="{source}"]')
        trigger.click()
        dialog = f.page.get_by_role('dialog', name='시작 대상 선택' if source == '$entry' else '다음 실행 대상 선택')
        options = dialog.locator('[data-document-route-choice]')
        assert options.locator('option').evaluate_all('(rows)=>rows.map(row=>row.value)') == ['', chosen]
        options.select_option(chosen)
        dialog.get_by_role('button', name='취소' if cancel else '적용', exact=True).click()
        expect(dialog).to_be_hidden()

    def order():
        return doc().locator(':scope > [data-document-cell]').evaluate_all('(cards)=>cards.map(card=>card.dataset.documentCell)')

    def save():
        panel().locator('[data-bp-save]').click()
        expect(panel().locator('.bp-status')).to_have_text('저장됨', timeout=120000)
        assert not pending()
        x.original()

    pick('$entry', 'lead', cancel=True)
    expect(button).to_be_focused()
    assert not pending() and order() == ['$entry', 'inner', 'tail', '$exit:return']
    pick('$entry', 'lead')
    first = ['$entry', 'lead', 'inner', 'tail', '$exit:return']
    assert order() == first and len(pending()) == 1
    doc().press('Control+z')
    assert order() == ['$entry', 'inner', 'tail', '$exit:return'] and not pending()
    doc().press('Control+y')
    held = pending()
    assert order() == first and len(held) == 1

    # The sibling has the same local ID as the next candidate in the selected
    # child. Its actual C# bytes are in the original observation closure.
    raw = sibling_source.read_bytes()
    sibling_source.write_bytes(raw.replace(b'peer piece', b'peer changed'))
    changed = sibling_source.read_bytes()
    try:
        panel().locator('[data-bp-save]').click()
        expect(panel().locator('.bp-status')).not_to_have_text('저장 중…', timeout=120000)
        f.idle()
        assert checkpoint.read_bytes() == frozen and sibling_source.read_bytes() == changed
        assert all(dict(pending()).get(key) == value for key, value in held)
    finally:
        sibling_source.write_bytes(raw)
    save()
    restart(1)
    assert order() == first and read()['entry'] == 'lead'
    inspect = f.invoke('draftHistory', {'action': 'inspect'})['result']['result']
    assert inspect['undo']['available'] and len(inspect['undo']['units']) == 1, inspect
    pick('tail', 'piece')
    final = first[:-1] + ['piece', '$exit:return']
    assert order() == final and len(pending()) == 1
    doc().press('Control+z')
    assert order() == first and not pending()
    doc().press('Control+y')
    assert order() == final and len(pending()) == 1
    save()
    restart(2)
    assert order() == final
    x.original()
    f.checked('Local Undo/Redo, stale sibling refusal, and both exact single-edge saves survive a cold reopen')
    if os.environ.get('FRAME_RECONNECT_PREVIOUS'):
        old = Path(os.environ['FRAME_RECONNECT_PREVIOUS'])
        repo, report, host = f.repo, f.report, f.env.get('CONFECTORY_ELEMENT_AUTHORING_HOST')
        f.page.close()
        f.stop()
        try:
            f.repo, f.report = old/'checkout', json.loads((old/'report.json').read_text())
            f.env.update(CONFECTORY_EDITOR_REPO=str(f.repo),
                         CONFECTORY_ELEMENT_AUTHORING_HOST=str(old/'metadata'/'Confectory.ElementAuthoring.dll'))
            stable = saved_content(checkpoint)
            f.start(3)
            old_view = read()
            assert old_view['entry'] == 'lead' and edge('tail', 'piece') in old_view['edges']
            assert read(peer_frame)['entry'] == 'lead'
            f.invoke('reviewGroup', {'ids': old_view['reviewIds'], 'target': 'portable'})
            assert f.state()['review']['status'] == 'ready'
            assert saved_content(checkpoint) == stable
            x.original()
            f.checked('The actual previous editor and metadata reader cold-open and review the same version-1 draft and history')
        finally:
            f.stop()
            f.repo, f.report = repo, report
            f.env['CONFECTORY_EDITOR_REPO'] = str(repo)
            if host is None:
                f.env.pop('CONFECTORY_ELEMENT_AUTHORING_HOST', None)
            else:
                f.env['CONFECTORY_ELEMENT_AUTHORING_HOST'] = host
        f.start(4)
        f.page = f.setup()
        f.page.set_viewport_size({'width': 1800, 'height': 1400})
        open_document()
        assert order() == final

    if leaf_profile == 'sync-acyclic-nested-v1':
        # This existing profile publishes through the owning function window.
        panel().locator('.bp-breadcrumbs button').first.click()
        f.idle()
        expect(doc().locator('[data-document-internal="body"]')).to_be_visible()
    review().locator('[data-reject]').click()
    x.original()
    dialog = review()
    dialog.locator('#confirm').click()
    expect(dialog).to_be_hidden(timeout=120000)
    expected = copy.deepcopy(root)
    scope = selected(expected)
    scope['entry'] = 'lead'
    next(e for e in scope['edges'] if e['from'] == 'tail')['to'] = 'piece'
    assert json.loads(graph_path.read_bytes()) == expected
    assert all(file.read_bytes() == original for file, original in x.physical.items() if file != graph_path)
    parent = 'parent lead\n' if depth == 2 else ''
    x.build('child-reconnect-run', 10, 'chosen lead\ninner\ntail\nchosen piece:10\n'+parent+'peer lead\npeer piece\nroot lead\nafter\n10')
    assert not f.errors and not f.external, (f.errors, f.external)
    f.checked('Only the selected child entry and next edge change at Confirm; real C# executes the new cells with the existing value')


try:
    root, sibling_source = seed()
    parent = 'parent lead\n' if depth == 2 else ''
    x.build('child-reconnect-baseline', 10, 'inner\ntail\n'+parent+'peer lead\npeer piece\nroot lead\nafter\n10')
    f.start(0)
    f.invoke('select', {'id': t.feature})
    f.invoke('saveDraft', {})
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    with sync_playwright() as pw:
        expect.set_options(timeout=30000)
        with pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox']) as f.browser:
            f.page = f.setup()
            f.page.set_viewport_size({'width': 1800, 'height': 1400})
            open_document()
            run_ui(checkpoint, root, sibling_source)
finally:
    f.stop()
    print('Evidence:', f.case, flush=True)
