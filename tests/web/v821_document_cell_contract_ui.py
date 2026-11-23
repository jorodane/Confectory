"""Edit owned Logic Code declarations and a value in one legacy author batch."""
import ast
import copy
import json
import os
from pathlib import Path
import sys
import time
import uuid

from playwright.sync_api import expect, sync_playwright

import v666_root_input_name_recovery_fixture as t

f, x = t.f, t.x
graph = t.graph
frame = graph + '/graph:work'
peer = graph + '/graph:peer'
graph_path = f.project / t.graph_file
work_source = f.project / 'Pair.work.node.json'
peer_source = f.project / 'Pair.peer.node.json'
helpers = Path(__file__).with_name('v821_function_document_ui.py')
shared = {'panel', 'doc', 'open_document', 'pending', 'save', 'restart', 'review'}
exec(compile(ast.Module(body=[node for node in ast.parse(helpers.read_text()).body
                              if isinstance(node, ast.FunctionDef) and node.name in shared],
                        type_ignores=[]), str(helpers), 'exec'), globals())


def edge(source, target):
    return dict(**{'from': source, 'port': 'next', 'to': target})


def signature(args, result):
    return {'args': args, 'return': result}


def parameter(name, type_='int', mode=None):
    return {'name': name, 'type': type_, **({'mode': mode} if mode else {})}


def make_frame(name, file):
    child = {
        'schema': 1, 'profile': 'sync-acyclic-methods-v1', 'entry': 'calculate',
        'nodes': [{
            'id': 'calculate', 'kind': 'code', 'control': 'next', 'intent': 'calculate',
            'signature': signature([parameter('amount'), parameter('result', mode='out')], 'void'),
            'arguments': {'amount': {'input': 'amount'}}, 'implementation': file.name,
        }],
        'edges': [edge('calculate', 'exit:return')],
        'exits': {'return': {'node': 'calculate', 'output': 'result'}},
    }
    return {'id': name, 'kind': 'graph', 'control': 'next', 'intent': name,
            'signature': signature([parameter('amount')], 'int'),
            'arguments': {'amount': {'input': 'amount'}}, 'graph': child}


root = {
    **t.definition, 'profile': 'sync-acyclic-nested-v1', 'entry': 'work',
    'nodes': [make_frame('work', work_source), make_frame('peer', peer_source)],
    'edges': [edge('work', 'peer'), edge('peer', 'exit:return')],
    'exits': {'return': {'node': 'work'}},
}
defs = f.metadata('blueprintDescribeOwned', project=str(f.project/'project.cproj'),
                  id=f.n+'PairBody', text=(f.project/'PairBody.celem').read_text(),
                  bodyTarget='common', graph=root, definitionsOnly=True)
assert defs['state'] == 'node-definitions', defs
bodies = {
    'work': 'result = amount + 3;\nSystem.Console.WriteLine("work:"+result);',
    'peer': 'result = amount + 100;\nSystem.Console.WriteLine("peer:"+result);',
}
for name, file in [('work', work_source), ('peer', peer_source)]:
    definition = next(row for row in defs['nestedNodes'] if row['id'] == name + '/calculate')
    file.write_text(json.dumps(dict(schema=1, node='calculate', definitionHash=definition['definitionHash'],
                                    source=bodies[name])))
graph_path.write_text(json.dumps(root))
x.physical = {path: path.read_bytes() for path in f.project.iterdir() if path.is_file()}
new_body = 'produced = amount + input1;\nSystem.Console.WriteLine("work:"+produced);'


def read(id_=frame):
    return f.invoke('blueprint', {'action': 'read', 'id': id_})['result']['result']


def open_frame(name):
    doc().locator(f'[data-document-internal="{name}"]').click()
    f.idle()
    expect(doc().locator('[data-document-contract=calculate]')).to_be_visible()


def contract():
    return doc().locator('[data-document-contract-panel=calculate]')


def field(name):
    return contract().locator(f'[data-mobile-contract-field="{name}"]')


def choose_type(name, type_=None):
    field(name).locator('[data-signature-type]').click()
    picker = f.page.get_by_role('dialog', name='속성 타입 선택')
    expect(picker).to_be_visible()
    if type_ is None:
        f.page.keyboard.press('Escape')
    else:
        picker.locator(f'[data-type="{type_}"]').click()
    expect(picker).to_be_hidden()


def code(text, save_source):
    doc().locator('[data-document-code=calculate]').click()
    editor = f.page.locator('.bp-script-dialog')
    textarea = editor.locator('[data-code-source]')
    expect(textarea).to_be_visible()
    before = editor.locator('[data-code-region=body]').text_content()
    textarea.evaluate('(el,text)=>{const i=el.value.indexOf(text);if(i<0)throw Error(text);el.focus();el.setSelectionRange(i,i+text.length)}', before)
    f.page.keyboard.insert_text(text)
    editor.locator('[data-code-save]' if save_source else '[data-code-cancel]').click()
    expect(editor).to_be_hidden()


def earlier_reader(checkpoint, observed):
    repo, editor = os.environ.get('CELL_CONTRACT_PREVIOUS_REPO'), os.environ.get('CELL_CONTRACT_PREVIOUS_EDITOR')
    if not repo or not editor:
        return False
    before = json.loads(checkpoint.read_text())
    f.pending()
    f.page.close()
    f.stop()
    original_repo, original_report = f.repo, f.report
    try:
        f.repo, f.report = Path(repo), json.loads(Path(editor).read_text())
        f.env['CONFECTORY_EDITOR_REPO'] = repo
        f.start('previous')
        old = read()
        assert old['nodes'][0]['signature'] == observed['nodes'][0]['signature']
        assert old['exits'] == observed['exits']
        ids = [row['id'] for row in before['changes']]
        assert set(ids) == {graph, graph + '/node:work/node:calculate'}
        f.invoke('reviewGroup', {'ids': ids, 'target': 'portable'})
        assert f.state()['review']['status'] == 'ready'
        after = json.loads(checkpoint.read_text())
        assert after['version'] == before['version'] == 1
        assert [{k: v for k, v in row.items() if k != 'revision'} for row in after['changes']] == [
            {k: v for k, v in row.items() if k != 'revision'} for row in before['changes']]
        x.original()
        f.checked('Previous reader opens and reviews the same version-1 declaration, value and body draft')
    finally:
        f.stop()
        f.repo, f.report = original_repo, original_report
        f.env['CONFECTORY_EDITOR_REPO'] = str(original_repo)
        f.start('current')
    f.page = f.setup()
    f.page.set_viewport_size({'width': 1900, 'height': 1500})
    open_document()
    return True


try:
    x.build('owned-card-before', 10, 'work:10\npeer:107\n10')
    f.start(0)
    f.invoke('select', {'id': t.feature})
    f.invoke('saveDraft', {})
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    frozen = checkpoint.read_bytes()
    with sync_playwright() as pw:
        expect.set_options(timeout=30000)
        f.browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        f.page = f.setup()
        f.page.set_viewport_size({'width': 1900, 'height': 1500})
        open_document()
        if '--baseline' in sys.argv:
            doc().locator('[data-document-internal=work]').click()
            f.idle()
            expect(doc().locator('[data-document-cell=calculate]')).to_be_visible()
            expect(doc().locator('[data-document-contract=calculate]')).to_have_count(0)
            f.checked('Previous Logic Code card has value selection but lacks its contract controls')
            sys.exit(0)
        open_frame('work')
        doc().locator('[data-document-contract=calculate]').click()
        expect(contract()).to_be_visible()
        choose_type('amount', 'string')  # A connected input cannot silently change type.
        assert not pending()
        name = field('result').locator('input')
        name.fill('cancelled')
        name.press('Escape')
        expect(name).to_have_value('result')
        assert not pending()
        choose_type('amount')
        assert not pending() and checkpoint.read_bytes() == frozen
        f.checked('Type rejection and cancellation retain the connected value, declaration and checkpoint')

        contract().locator('[data-document-contract-side=inputs] [data-mobile-contract-add]').click()
        expect(field('input1')).to_be_visible()
        choose_type('input1', 'int')
        name = field('result').locator('input')
        name.fill('produced')
        name.press('Enter')
        expect(field('produced')).to_be_visible()
        value = doc().locator('[data-document-value=calculate][data-document-port="field:input1"]')
        value.click()
        picker = f.page.get_by_role('dialog', name='핀 값 선택')
        search = picker.get_by_role('searchbox', name='값 검색')
        search.fill('16')
        search.press('Enter')
        expect(value).to_have_text('16')
        held = pending()
        code('throw new System.Exception("cancelled");', False)
        assert pending() == held
        code(new_body, True)
        held = pending()
        assert {row['type'] for _, row in held} == {'parameters', 'argument:input1', 'source'}
        assert checkpoint.read_bytes() == frozen
        x.original()

        panel().locator('.bp-breadcrumbs button').first.click()
        f.idle()
        open_frame('peer')
        doc().locator('[data-document-contract=calculate]').click()
        expect(field('result')).to_be_visible()
        expect(field('input1')).to_have_count(0)
        assert pending() == held
        panel().locator('.bp-breadcrumbs button').first.click()
        f.idle()
        open_frame('work')
        expect(field('produced')).to_be_visible()
        assert pending() == held

        observed = read()
        stale = {'action': 'authorBatch', 'id': frame, 'attempt': uuid.uuid4().hex,
                 'checkpointHash': observed['checkpointHash'], 'sourceProof': x.proof(observed),
                 'edits': [{'action': 'parameters', 'node': 'calculate',
                            'definition': json.loads(next(row['text'] for _, row in held if row['type'] == 'parameters'))},
                           {'action': 'argument', 'node': 'calculate', 'name': 'input1', 'valueJson': '{"constant":"wrong"}'},
                           {'action': 'source', 'node': 'calculate', 'text': new_body}]}
        f.invoke('blueprint', stale, False)
        assert pending() == held and checkpoint.read_bytes() == frozen
        stale['edits'][1]['valueJson'] = '{"constant":16}'
        peer_bytes = peer_source.read_bytes()
        peer_source.write_bytes(peer_bytes + b' ')
        try:
            f.invoke('blueprint', stale, False)
            assert checkpoint.read_bytes() == frozen and pending() == held
        finally:
            peer_source.write_bytes(peer_bytes)
        x.original()

        save()
        assert not pending()
        saved = read()
        assert saved['nodes'][0]['signature']['args'] == [
            parameter('amount'), parameter('produced', mode='out'), parameter('input1')]
        assert saved['exits'][0]['valueJson'] == '{"node":"calculate","output":"produced"}'
        x.original()
        if not earlier_reader(checkpoint, saved):
            restart(1)
        expect(field('produced')).to_be_visible()
        expect(doc().locator('[data-document-value=calculate][data-document-port="field:input1"]')).to_have_text('16')
        assert not pending()

        dialog = review()
        dialog.locator('[data-reject]').click()
        x.original()
        dialog = review()
        dialog.locator('#confirm').click()
        expect(dialog).to_be_hidden(timeout=120000)
        f.idle()
        result = json.loads(graph_path.read_text())
        assert result['nodes'][1] == root['nodes'][1]
        assert result['edges'] == root['edges'] and result['exits'] == root['exits']
        updated = result['nodes'][0]['graph']
        assert updated['exits']['return'] == {'node': 'calculate', 'output': 'produced'}
        assert updated['nodes'][0]['arguments'] == {'amount': {'input': 'amount'}, 'input1': {'constant': 16}}
        assert all(path.read_bytes() == raw for path, raw in x.physical.items() if path not in (graph_path, work_source))
        restart(2)
        expect(field('produced')).to_be_visible()
        x.build('owned-card-after', 23, 'work:23\npeer:107\n23')
        assert not f.errors and not f.external, (f.errors, f.external)
        f.checked('Logic Code saved one observed input, output remap and explicit body; only the selected frame changed and ran')
        f.browser.close()
finally:
    (f.case/'cell-contract-checks.json').write_text(json.dumps(f.checks, ensure_ascii=False))
    f.stop()
print('V821_DOCUMENT_CELL_CONTRACT', f.case, flush=True)
