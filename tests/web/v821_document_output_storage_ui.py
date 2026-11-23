"""Choose the exact existing Set destination from its Logic Code producer card."""
import ast
import copy
import json
import os
from pathlib import Path
import time

from playwright.sync_api import expect, sync_playwright

import v666_root_input_name_recovery_fixture as t

f, x = t.f, t.x
graph_id = t.graph
graph_file = f.project / t.graph_file
helpers = Path(__file__).with_name('v821_function_document_ui.py')
shared = {'panel', 'doc', 'open_document', 'pending', 'save', 'restart', 'review'}
exec(compile(ast.Module(body=[node for node in ast.parse(helpers.read_text()).body
                              if isinstance(node, ast.FunctionDef) and node.name in shared],
                        type_ignores=[]), str(helpers), 'exec'), globals())


def edge(source, target):
    return {'from': source, 'port': 'next', 'to': target}


def node(name, file, args, args_values, result='void'):
    return {'id': name, 'kind': 'code', 'control': 'next', 'intent': name,
            'signature': {'args': args, 'return': result},
            'arguments': args_values, 'implementation': file}


def integer(name):
    return {'type': 'int', 'name': name}


def local(name, title, value, native_type='int'):
    return {'id': name, 'name': title, 'type': native_type, 'initial': {'constant': value}}


producer = node('produce', 'Produce.node.json',
                [integer('amount'), {**integer('unused'), 'mode': 'out'}],
                {'amount': {'input': 'amount'}}, 'int')
bound_output = {'node': 'produce', 'output': 'return'}
capture = {'id': 'capture', 'kind': 'set', 'control': 'next', 'intent': 'capture',
           'signature': {'args': [integer('value')], 'return': 'void'},
           'arguments': {'value': bound_output}, 'local': 'left', 'outputLocal': 'snapshot'}
observer = node('observe', 'Observe.node.json', [integer(name) for name in ('left', 'right', 'captured')],
                {'left': {'local': 'left'}, 'right': {'local': 'right'},
                 'captured': {'node': 'capture', 'output': 'stored'}})
same_id = node('produce', 'Peer.node.json', [integer('amount')], {'amount': {'input': 'amount'}}, 'int')
peer = {'id': 'peer', 'kind': 'graph', 'control': 'next', 'intent': 'peer',
        'signature': {'args': [integer('amount')], 'return': 'int'}, 'arguments': {'amount': {'input': 'amount'}},
        'graph': {'schema': 1, 'profile': 'sync-acyclic-methods-v1', 'entry': 'produce',
                  'nodes': [same_id], 'edges': [edge('produce', 'exit:return')],
                  'exits': {'return': {'node': 'produce'}}}}
root = {**t.definition, 'profile': 'sync-acyclic-nested-v1', 'entry': 'produce',
        'nodes': [producer, capture, observer, peer],
        'edges': [edge('produce', 'capture'), edge('capture', 'observe'),
                  edge('observe', 'peer'), edge('peer', 'exit:return')],
        'locals': [local('left', '첫 지역변수', 1), local('right', '둘째 지역변수', 5),
                   local('snapshot', '저장한 값', 0), local('flag', '조건 변수', False, 'bool')],
        'exits': {'return': {'local': 'right'}}}
defs = f.metadata('blueprintDescribeOwned', project=str(f.project/'project.cproj'),
                  id=f.n+'PairBody', text=(f.project/'PairBody.celem').read_text(),
                  bodyTarget='common', graph=root, definitionsOnly=True)
assert defs['state'] == 'node-definitions', defs
bodies = {
    'produce': ('Produce.node.json', 'unused=99;return amount+3;'),
    'observe': ('Observe.node.json', 'System.Console.WriteLine($"locals:{left},{right},{captured}");'),
    'peer/produce': ('Peer.node.json', 'System.Console.WriteLine("peer:"+(amount+100));return amount+100;'),
}
for item in defs['nodes'] + defs['nestedNodes']:
    if item['id'] not in bodies:
        continue
    file, source = bodies[item['id']]
    (f.project/file).write_text(json.dumps(dict(schema=1, node=item['id'].split('/')[-1],
                                               definitionHash=item['definitionHash'], source=source)))
graph_file.write_text(json.dumps(root))
physical = {path: path.read_bytes() for path in f.project.iterdir() if path.is_file()}


def read():
    return f.invoke('blueprint', {'action': 'read', 'id': graph_id})['result']['result']


def target():
    return doc().locator('[data-document-output-storage=return]')


def confirm():
    window = review()
    window.locator('#confirm').click()
    expect(window).to_be_hidden(timeout=120000)
    f.idle()


def check_older_draft(checkpoint):
    repo = os.environ.get('CELL_CONTRACT_PREVIOUS_REPO')
    editor = os.environ.get('CELL_CONTRACT_PREVIOUS_EDITOR')
    if not repo or not editor:
        return False
    original_repo, original_report = f.repo, f.report
    frozen = json.loads(checkpoint.read_text())
    f.pending()
    f.page.close()
    f.stop()
    try:
        f.repo, f.report = Path(repo), json.loads(Path(editor).read_text())
        f.env['CONFECTORY_EDITOR_REPO'] = repo
        f.start('previous')
        observed = read()
        row = next(row for row in observed['nodes'] if row['id'] == 'capture')
        assert row['local'] == 'right' and json.loads(row['arguments'][0]['valueJson']) == bound_output
        assert frozen['version'] == 1
        assert [row['id'] for row in frozen['changes']] == [graph_id]
        reads = frozen['changes'][0]['propertyObservations']['sources']
        assert graph_id in reads and f.n + 'Vitals' not in reads
        assert set(reads) <= set(observed['reviewIds'])
        f.invoke('reviewGroup', {'ids': observed['reviewIds'], 'target': 'portable'})
        assert f.state()['review']['status'] == 'ready'
        current = json.loads(checkpoint.read_text())
        assert [{k: v for k, v in row.items() if k != 'revision'} for row in current['changes']] == [
            {k: v for k, v in row.items() if k != 'revision'} for row in frozen['changes']]
        f.checked('The previous reader reviews the exact version-1 Set draft without unrelated optional sources')
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
    x.build('output-before', 5, 'locals:10,5,10\npeer:107\n5')
    f.start(0)
    f.invoke('select', {'id': t.feature})
    f.invoke('saveDraft', {})
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    with sync_playwright() as pw:
        expect.set_options(timeout=30000)
        f.browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        f.page = f.setup()
        f.page.set_viewport_size({'width': 1900, 'height': 1500})
        open_document()
        button = doc().locator('[data-document-contract=produce]')
        button.click()
        expect(target()).to_have_value('left')
        expect(doc().locator('[data-document-output-storage=unused]')).to_have_count(0)
        expect(target().locator('option[value=flag]')).to_have_attribute('disabled', '')
        for invalid in ('flag', 'missing'):
            target().evaluate("(el,value)=>{el.value=value;el.dispatchEvent(new Event('change',{bubbles:true}));}",
                              invalid)
            expect(target()).to_have_value('left')
        button.click()
        assert not pending()
        button.click()
        old_target = target().element_handle()
        doc().locator('[data-document-internal=peer]').click()
        f.idle()
        expect(button).to_be_visible()
        old_target.evaluate("(el)=>{el.value='right';el.dispatchEvent(new Event('change',{bubbles:true}));}")
        assert not pending()
        button.click()
        expect(target()).to_have_count(0)
        panel().locator('.bp-breadcrumbs button').first.click()
        f.idle()
        expect(target()).to_have_value('left')
        f.checked('Invalid type and retired selector are inert; a sibling with the same cell ID has no root Set target')

        doc().locator('[data-document-value=produce][data-document-port="field:amount"]').click()
        search = f.page.get_by_role('dialog', name='핀 값 선택').get_by_role('searchbox', name='값 검색')
        search.fill('20')
        search.press('Enter')
        expect(target()).to_have_count(0)
        save()
        confirm()
        first = copy.deepcopy(root)
        first['nodes'][0]['arguments']['amount'] = {'constant': 20}
        assert json.loads(graph_file.read_text()) == first
        x.build('output-input-confirmed', 5, 'locals:23,5,23\npeer:107\n5')

        expect(target()).to_have_value('left')
        target().select_option('right')
        expect(target()).to_have_value('right')
        expect(doc().locator('[data-document-set-target=capture]')).to_have_value('right')
        plan = [row for _, row in pending() if row['type'] == 'set-plan']
        assert len(plan) == 1
        selected = json.loads(plan[0]['text'])
        assert selected['id'] == 'capture' and selected['local'] == 'right'
        assert selected['outputLocal'] == 'snapshot' and json.loads(selected['valueJson']) == bound_output
        save()
        assert json.loads(graph_file.read_text()) == first and not pending()
        if not check_older_draft(checkpoint):
            restart(1)
        expect(target()).to_have_value('right')
        review().locator('[data-reject]').click()
        assert json.loads(graph_file.read_text()) == first
        window = review()
        last = checkpoint.read_bytes()
        raw = graph_file.read_bytes()
        graph_file.write_bytes(raw + b' ')
        try:
            window.locator('#confirm').click()
            f.idle()
            assert graph_file.read_bytes() == raw + b' ' and checkpoint.read_bytes() == last
        finally:
            graph_file.write_bytes(raw)
        if window.is_visible():
            window.locator('[data-reject]').click()
        confirm()
        first['nodes'][1]['local'] = 'right'
        assert json.loads(graph_file.read_text()) == first
        assert all(path.read_bytes() == raw for path, raw in physical.items() if path != graph_file)
        restart(2)
        expect(target()).to_have_value('right')
        x.build('output-storage-confirmed', 23, 'locals:1,23,23\npeer:107\n23')
        assert not f.errors and not f.external, (f.errors, f.external)
        f.checked('Input 20 computed 23; after a separate Save/Review/Confirm only the linked Set writes 23 into the chosen local')
        f.browser.close()
finally:
    (f.case/'output-storage-checks.json').write_text(json.dumps(f.checks, ensure_ascii=False))
    f.stop()
print('V821_DOCUMENT_OUTPUT_STORAGE', f.case, flush=True)
