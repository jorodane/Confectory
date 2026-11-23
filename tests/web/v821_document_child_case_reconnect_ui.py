"""Reconnect the exact detached case in a directly owned switch child."""
import ast
import copy
import json
import os
from pathlib import Path
import uuid

from playwright.sync_api import expect, sync_playwright

import v666_node_names_recovery_fixture as t

f, x = t.f, t.x
mode = 'normal'
graph_path = f.project / t.graph_file
frame = t.graph + '/graph:body'
peer_frame = t.graph + '/graph:peer'
port = 'case:positive'
helpers = {
    'v821_switch_compound_drag_ui.py': {'edge', 'code', 'prepare_project'},
    'v821_function_document_ui.py': {'panel', 'doc', 'pending', 'open_document', 'restart', 'review'},
}
for filename, names in helpers.items():
    path = Path(__file__).with_name(filename)
    functions = [node for node in ast.parse(path.read_text()).body
                 if isinstance(node, ast.FunctionDef) and node.name in names]
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(path), 'exec'), globals())


def setup():
    root = prepare_project()
    child = root['nodes'][0]['graph']
    target = next(route for route in child['edges'] if route['from'] == 'choose' and route['port'] == port)
    target['to'] = 'return:choose'
    peer = code('positive')
    peer['implementation'] = 'Peer.positive.node.json'
    root['nodes'].insert(1, {
        'id': 'peer', 'kind': 'graph', 'control': 'next', 'intent': 'Peer',
        'signature': {'args': [], 'return': 'void'}, 'arguments': {},
        'graph': dict(schema=1, profile='sync-acyclic-nested-v1', entry='positive',
                      nodes=[peer], edges=[edge('positive', 'exit:return')], exits={'return': None}),
    })
    root['edges'] = [edge('body', 'peer'), edge('peer', 'after'), edge('after', 'exit:return')]
    definitions = f.metadata('blueprintDescribeOwned', project=str(f.manifest), id=f.n+'PairBody',
                             text=(f.project/'PairBody.celem').read_text(), bodyTarget='common',
                             graph=root, definitionsOnly=True)
    assert definitions['state'] == 'node-definitions', definitions
    hashes = {row['id']: row['definitionHash'] for row in definitions['nodes'] + definitions['nestedNodes']}
    for identity, node in [('body/'+row['id'], row) for row in child['nodes']]+[('peer/positive', peer), ('after', root['nodes'][-1])]:
        file = f.project / node['implementation']
        source = 'System.Console.WriteLine("peer");' if identity == 'peer/positive' else json.loads(file.read_text())['source']
        file.write_text(json.dumps(dict(schema=1, node=node['id'], definitionHash=hashes[identity], source=source)))
    graph_path.write_text(json.dumps(root))
    x.physical = {path: path.read_bytes() for path in f.project.iterdir() if path.is_file()}
    return root


def read(id_=frame):
    return f.invoke('blueprint', {'action': 'read', 'id': id_})['result']['result']


def branch():
    return doc().locator(f'[data-document-panel="{port}"]')


def review_draft():
    dialog = review()
    expect(dialog.locator('#confirm')).to_be_enabled()
    return dialog


try:
    original = setup()
    expected = copy.deepcopy(original)
    next(route for route in expected['nodes'][0]['graph']['edges'] if route['port'] == port)['to'] = 'positive'
    baseline_output = 'finish:7\npeer\nafter\nresult:10\nnegative:-2\nfinish:-2\npeer\nafter\nresult:1'
    x.build('child-case-reconnect-before', 11, baseline_output)
    f.start(0)
    f.invoke('select', {'id': t.feature})
    f.invoke('saveDraft', {})
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    before = checkpoint.read_bytes()
    current = read()
    binding = current['documentFrameReconnectBinding']
    assert binding['graph'] == frame and binding['path'] == 'body'
    assert current['documentFrameCaseReconnectTargets'] == {'choose': {port: ['positive']}}
    assert not read(peer_frame).get('documentFrameCaseReconnectTargets')
    edit = dict(action='route', node='choose', port=port, to='positive')
    for bad in [dict(edit, port='case:negative'), dict(edit, to='finish'), dict(edit, node='positive')]:
        f.invoke('blueprint', dict(action='authorBatch', id=frame, documentFrame=binding,
                                  attempt=uuid.uuid4().hex, checkpointHash=current['checkpointHash'],
                                  sourceProof=x.proof(current), edits=[bad]), False)
        assert checkpoint.read_bytes() == before
    f.invoke('blueprint', dict(action='authorBatch', id=peer_frame, documentFrame=binding,
                              attempt=uuid.uuid4().hex, checkpointHash=current['checkpointHash'],
                              sourceProof=x.proof(current), edits=[edit]), False)
    assert checkpoint.read_bytes() == before
    x.original()
    with sync_playwright() as pw:
        expect.set_options(timeout=30000)
        f.browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        f.page = f.setup()
        f.page.set_viewport_size({'width': 1800, 'height': 1400})
        open_document()
        doc().locator('[data-document-internal="body"]').click()
        doc().locator(f'[data-document-branch="{port}"]').click()
        button = branch().locator(f'[data-document-branch-target="{port}"]')

        def pick(cancel=False):
            button.click()
            modal = f.page.get_by_role('dialog', name='분기 실행 대상 선택')
            choices = modal.locator('[data-document-route-choice]')
            expect(choices.locator('option')).to_have_count(2)
            expect(modal.locator('[data-route-apply]')).to_be_disabled()
            choices.select_option('positive')
            modal.locator('[data-route-cancel]' if cancel else '[data-route-apply]').click()
            expect(modal).to_be_hidden()

        pick(cancel=True)
        expect(button).to_be_focused()
        assert not pending() and checkpoint.read_bytes() == before
        pick()
        expect(branch().locator('[data-document-cell=positive]')).to_be_visible()
        doc().press('Control+z')
        expect(button).to_be_visible()
        assert not pending()
        doc().press('Control+y')
        expect(branch().locator('[data-document-cell=positive]')).to_be_visible()
        panel().locator('[data-bp-save]').click()
        expect(panel().locator('.bp-status')).to_have_text('저장됨', timeout=120000)
        assert not pending()
        saved = json.loads(checkpoint.read_bytes())
        assert saved['version'] == 1
        x.original()
        restart(1)
        expect(branch().locator('[data-document-cell=positive]')).to_be_visible()
        assert read()['edges'] == expected['nodes'][0]['graph']['edges']
        f.checked('Child case reconnect preserves one Undo/Redo, restores through cold Save, and refuses a different port or sibling.')

        # The old editor and its own metadata host open the already stored draft.
        if os.environ.get('CONFECTORY_PREVIOUS_CASE_REPO'):
            previous = Path(os.environ['CONFECTORY_PREVIOUS_CASE_REPO'])
            current_report, current_env = f.report, f.env.copy()
            f.page.close()
            f.stop()
            f.env['CONFECTORY_EDITOR_REPO'] = str(previous)
            f.env['CONFECTORY_ELEMENT_AUTHORING_HOST'] = str(
                previous/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')
            f.report = json.loads(Path(os.environ['CONFECTORY_PREVIOUS_CASE_EDITOR']).read_text())
            f.start(2)
            assert read()['edges'] == expected['nodes'][0]['graph']['edges']
            f.page = f.setup()
            f.page.set_viewport_size({'width': 1800, 'height': 1400})
            open_document()
            if not doc().locator(f'[data-document-branch="{port}"]').is_visible():
                doc().locator('[data-document-internal="body"]').click()
            doc().locator(f'[data-document-branch="{port}"]').click()
            expect(branch().locator('[data-document-cell=positive]')).to_be_visible()
            x.original()
            f.checked('Version 1 child case draft opens in the previous editor and metadata host without an original write.')
            f.page.close()
            f.stop()
            f.report, f.env = current_report, current_env
            f.start(3)
            f.page = f.setup()
            f.page.set_viewport_size({'width': 1800, 'height': 1400})
            open_document()
        review_draft().locator('[data-reject]').click()
        x.original()
        result = review_draft()
        result.locator('#confirm').click()
        expect(result).to_be_hidden(timeout=120000)
        f.idle()
        restart(4)
        assert json.loads(graph_path.read_text()) == expected
        assert all(path.read_bytes() == raw for path, raw in x.physical.items() if path != graph_path)
        x.build('child-case-reconnect-confirmed', 11, 'positive:7\n'+baseline_output)
        assert not f.errors and not f.external, (f.errors, f.external)
        f.checked('After Confirm, only the restored branch runs for its input. The other branch, peer, I/O and original code remain intact.')
        f.browser.close()
finally:
    f.stop()
    print('Evidence:', f.case, flush=True)
