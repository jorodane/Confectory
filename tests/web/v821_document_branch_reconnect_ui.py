"""Reconnect one declared open case through Logic Code and publish its existing cell."""
import ast
import copy
import json
import os
from pathlib import Path
import sys
import time
import uuid

from playwright.sync_api import expect, sync_playwright

import v666_root_execution_fixture as t

f = t.f
baseline_only = '--baseline' in sys.argv
helpers = Path(__file__).with_name('v821_function_document_ui.py')
shared = {'panel', 'doc', 'open_document', 'pending', 'save', 'restart', 'review'}
exec(compile(ast.Module(body=[node for node in ast.parse(helpers.read_text()).body
                              if isinstance(node, ast.FunctionDef) and node.name in shared],
                        type_ignores=[]), str(helpers), 'exec'), globals())

graph_file = f.project / 'Flow.graph.json'
graph = copy.deepcopy(t.root)
bodies = {
    'choose': t.original_source.replace('Result.Negative;', 'amount<0?Result.Negative:Result.None;'),
    'detached': 'global::System.Console.WriteLine("detached:"+amount);',
    'other': 'global::System.Console.WriteLine("other:"+amount);',
    'continuation': 'global::System.Console.WriteLine("continued:"+amount);',
}
for name in ('detached', 'other', 'continuation'):
    graph['nodes'].append({
        'id': name, 'kind': 'code', 'control': 'next', 'intent': name,
        'signature': {'args': [{'name': 'amount', 'type': 'long'}], 'return': 'void'},
        'arguments': {'amount': {'input': 'amount'}}, 'implementation': name + '.node.json',
        **({'branchOwner': 'choose'} if name != 'continuation' else {}),
    })
graph['edges'] = [
    t.edge('choose', 'continuation'),
    t.edge('choose', 'other', 'case:negative'),
    t.edge('detached', 'return:choose'),
    t.edge('other', 'return:choose'),
    t.edge('continuation', 'exit:none'),
]
definitions = f.metadata('featureBlueprintNodes', featureSource=t.function, graph=graph)
assert definitions['state'] == 'node-definitions', definitions
for node in definitions['nodes']:
    name = node['id']
    source = 'Flow.node.json' if name == 'choose' else name + '.node.json'
    (f.project / source).write_text(json.dumps({
        'schema': 1, 'node': name, 'definitionHash': node['definitionHash'], 'source': bodies[name],
    }, ensure_ascii=False))
graph_file.write_text(json.dumps(graph, ensure_ascii=False))
(f.project / 'MainBody.celem').write_text(
    'implementation ' + f.n + 'MainBody for ' + f.n + 'Main () -> int {import '
    + t.feature + ' as Flow (long) -> void;body common "Main.csbody";}')
(f.project / 'Main.csbody').write_text(
    'foreach(long amount in new long[]{42,-7,0}){calls.Flow.Invoke(amount);'
    'global::System.Console.WriteLine("main:"+amount);}return 7;')
t.physical = {path: path.read_bytes() for path in f.project.iterdir() if path.is_file()}
before_run = '\n'.join([
    'callee:42', 'continued:42', 'main:42',
    'callee:-7', 'other:-7', 'continued:-7', 'main:-7',
    'callee:0', 'continued:0', 'main:0',
])


def case_cells(port):
    return doc().locator('[data-document-panel="' + port + '"] [data-document-cell]').evaluate_all(
        '(cells) => cells.map(cell => cell.dataset.documentCell)')


def saved_content(checkpoint):
    data = json.loads(checkpoint.read_bytes())
    assert data['version'] == 1
    return (
        {row['id']: {key: value for key, value in row.items() if key != 'revision'}
         for row in data['changes']},
        {key: value for key, value in data['history'].items() if key != 'epoch'},
    )


def check_previous_reader(checkpoint, edges, repo, editor):
    stable = saved_content(checkpoint)
    current_repo, current_report = f.repo, f.report
    current_host = f.env.get('CONFECTORY_ELEMENT_AUTHORING_HOST')
    f.stop()
    try:
        f.repo, f.report = repo, json.loads(editor.read_text())
        f.env.update(CONFECTORY_EDITOR_REPO=str(repo), CONFECTORY_ELEMENT_AUTHORING_HOST=str(
            repo / 'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'))
        f.start('previous')
        older = t.read()
        assert older['edges'] == edges
        f.invoke('reviewGroup', {'ids': older['reviewIds'], 'target': 'portable'})
        assert f.state()['review']['status'] == 'ready'
        assert saved_content(checkpoint) == stable
        t.original()
        f.checked('The previous engine opened and reviewed the version-1 saved draft without changing its data or history')
    finally:
        f.stop()
        f.repo, f.report = current_repo, current_report
        f.env['CONFECTORY_EDITOR_REPO'] = str(current_repo)
        if current_host is None:
            f.env.pop('CONFECTORY_ELEMENT_AUTHORING_HOST', None)
        else:
            f.env['CONFECTORY_ELEMENT_AUTHORING_HOST'] = current_host
        f.start('current')


def request(current, port, target):
    return {
        'action': 'authorBatch', 'documentBranch': True, 'id': t.graph,
        'attempt': uuid.uuid4().hex, 'checkpointHash': current['checkpointHash'],
        'sourceProof': t.proof(current),
        'edits': [{'action': 'route', 'node': 'choose', 'port': port, 'to': target}],
    }


try:
    t.build('branch-disconnected', 7, before_run)
    f.start(0)
    f.invoke('select', {'id': t.feature})
    f.invoke('saveDraft', {})
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    original_checkpoint = checkpoint.read_bytes()
    current = t.read()
    with sync_playwright() as pw:
        f.browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        f.page = f.setup()
        f.page.set_viewport_size({'width': 1900, 'height': 1500})
        expect.set_options(timeout=30000)
        open_document()
        option = doc().locator('[data-document-branch-target="case:positive"]')
        if baseline_only:
            expect(doc().locator('[data-document-branch="case:positive"]')).to_be_visible()
            expect(option).to_have_count(0)
            assert case_cells('case:positive') == []
            f.checked('Disconnected case compiled and ran but exposed no reconnect action')
            sys.exit(0)
        assert current.get('documentBranchReconnectTargets') == {'choose': {'case:positive': ['detached']}}, (
            current.get('documentBranchReconnectTargets'), current['diagnostics']['state'])
        expect(option).to_be_visible()
        expect(doc().locator('[data-document-branch-target="case:negative"]')).to_have_count(0)
        assert case_cells('case:positive') == []
        assert case_cells('case:negative') == ['other']
        for port, target in [('case:positive', 'other'), ('case:negative', 'detached'), ('case:next', 'detached')]:
            f.invoke('blueprint', request(current, port, target), False)
        assert checkpoint.read_bytes() == original_checkpoint
        t.original()
        f.checked('Open declared case is offered only its detached cell; invalid branches and targets leave disk unchanged')

        option.click()
        chooser = f.page.locator('[data-document-route-choice]')
        assert chooser.locator('option').evaluate_all('(options) => options.map(option => option.value)') == ['', 'detached']
        chooser.select_option('detached')
        f.page.locator('[data-route-cancel]').click()
        assert not pending() and case_cells('case:positive') == []
        option.click()
        chooser.select_option('detached')
        f.page.locator('[data-route-apply]').click()
        assert case_cells('case:positive') == ['detached']
        assert case_cells('case:negative') == ['other']
        held = pending()
        assert len(held) == 1
        assert checkpoint.read_bytes() == original_checkpoint
        t.original()

        doc().press('Control+z')
        assert case_cells('case:positive') == [] and not pending()
        doc().press('Control+y')
        assert case_cells('case:positive') == ['detached'] and pending() == held
        f.checked('Picker cancel is inert and one Undo/Redo clears/restores the one pending route')
        save()
        assert not pending()
        t.original()
        saved = t.read()
        new_route = t.edge('choose', 'detached', 'case:positive')
        assert saved['edges'] == [*current['edges'], new_route]
        saved_checkpoint = checkpoint.read_bytes()
        f.invoke('blueprint', request(current, 'case:positive', 'detached'), False)
        assert checkpoint.read_bytes() == saved_checkpoint
        if os.environ.get('BRANCH_RECONNECT_PREVIOUS_REPO') and os.environ.get('BRANCH_RECONNECT_PREVIOUS_EDITOR'):
            f.pending()
            f.page.close()
            check_previous_reader(checkpoint, saved['edges'], Path(os.environ['BRANCH_RECONNECT_PREVIOUS_REPO']),
                                  Path(os.environ['BRANCH_RECONNECT_PREVIOUS_EDITOR']))
            f.page = f.setup()
            f.page.set_viewport_size({'width': 1900, 'height': 1500})
            open_document()
        else:
            restart(1)
        assert case_cells('case:positive') == ['detached'] and case_cells('case:negative') == ['other']
        assert not pending() and t.read()['edges'] == saved['edges']

        dialog = review()
        dialog.locator('[data-reject]').click()
        t.original()
        dialog = review()
        reviewed_checkpoint = checkpoint.read_bytes()
        detached_source = f.project / 'detached.node.json'
        original_source = detached_source.read_bytes()
        detached_source.write_bytes(original_source + b' ')
        try:
            dialog.locator('#confirm').click()
            f.idle()
            assert detached_source.read_bytes() == original_source + b' '
            assert graph_file.read_bytes() == t.physical[graph_file]
            assert checkpoint.read_bytes() == reviewed_checkpoint
        finally:
            detached_source.write_bytes(original_source)
        if dialog.is_visible():
            dialog.locator('[data-reject]').click()
        dialog = review()
        dialog.locator('#confirm').click()
        expect(dialog).to_be_hidden(timeout=120000)
        f.idle()
        committed = json.loads(graph_file.read_text())
        assert committed['edges'] == [*graph['edges'], new_route]
        assert committed['nodes'] == graph['nodes'] and committed['exits'] == graph['exits']
        assert all(path.read_bytes() == raw for path, raw in t.physical.items() if path != graph_file)
        restart(2)
        assert case_cells('case:positive') == ['detached'] and case_cells('case:negative') == ['other']
        t.build('branch-reconnected', 7, before_run.replace('callee:42\n', 'callee:42\ndetached:42\n'))
        assert not f.errors and not f.external, (f.errors, f.external)
        f.checked('Only one declared open case was connected, and it alone ran the pre-existing bound cell')
        f.browser.close()
finally:
    (f.case / 'branch-reconnect-checks.json').write_text(json.dumps(f.checks, ensure_ascii=False))
    f.stop()
print('V821_DOCUMENT_BRANCH_RECONNECT', f.case, flush=True)
