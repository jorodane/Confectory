"""Create a typed call's first branch in Logic Code and execute its existing case rail."""
import ast
import json
from pathlib import Path
import sys

from playwright.sync_api import expect, sync_playwright

import v666_root_input_name_recovery_fixture as t

f, x = t.f, t.x
graph_id = t.graph
graph_file = f.project / t.graph_file
impl_id = f.n + 'PairBody'
callee_id = f.n + 'NativeChoice'
helpers = Path(__file__).with_name('v821_function_document_ui.py')
shared = {'panel', 'doc', 'pending', 'open_document', 'restart', 'review'}
exec(compile(ast.Module(body=[node for node in ast.parse(helpers.read_text()).body
                              if isinstance(node, ast.FunctionDef) and node.name in shared],
                        type_ignores=[]), str(helpers), 'exec'), globals())


def edge(source, target, port='next'):
    return {'from': source, 'port': port, 'to': target}


def signature(args, result='void'):
    return {'args': args, 'return': result}


def integer(name, mode=None):
    return {'type': 'int', 'name': name, **({'mode': mode} if mode else {})}


def code(id_, source, args=(), arguments=None):
    return {'id': id_, 'kind': 'code', 'control': 'next', 'intent': id_,
            'signature': signature(list(args)), 'arguments': arguments or {}, 'implementation': source}


def seed():
    native_fn = ('function ' + callee_id + ' (int input,out int audit) -> int {value blueprintPublishedOutputs = '
                 + json.dumps('["return","audit"]') + ';provide ' + callee_id + ' with ' + callee_id + 'Body;}')
    (f.project/'NativeChoice.celem').write_text(native_fn)
    (f.project/'NativeChoiceBody.celem').write_text(
        'implementation ' + callee_id + 'Body for ' + callee_id
        + ' (int input,out int audit) -> int {body common "NativeChoice.csbody";}')
    (f.project/'NativeChoice.csbody').write_text('audit=10*input;System.Console.WriteLine("original:"+input);return input+3;')
    project = f.project/'project.cproj'
    project.write_text(project.read_text().replace(
        'registry Confectory.Build.DotNet',
        'element NativeChoice function "NativeChoice.celem";'
        'element NativeChoiceBody implementation "NativeChoiceBody.celem";registry Confectory.Build.DotNet', 1))
    implementation = f.project/'PairBody.celem'
    prepared = f.metadata('blueprintPrepareCall', id=impl_id, text=implementation.read_text(),
                          targetText=native_fn, graph=t.definition, definition={
                              'id': 'native', 'feature': callee_id, 'intent': 'Observed native call', 'control': 'next'})
    implementation.write_text(prepared['implementation'])
    graph = prepared['graph']
    graph['profile'] = 'sync-acyclic-methods-v1'
    call = next(row for row in graph['nodes'] if row['id'] == 'native')
    call['arguments'] = {'input': {'input': 'amount'}}
    peer = {'id': 'peer', 'kind': 'graph', 'control': 'next', 'intent': 'Sibling',
            'signature': signature([]), 'arguments': {}, 'graph': {
                'schema': 1, 'profile': 'sync-acyclic-methods-v1', 'entry': 'native',
                'nodes': [code('native', 'Peer.node.json')],
                'edges': [edge('native', 'exit:return')], 'exits': {'return': None}}}
    consumer = code('consume', 'Consume.node.json', [integer('result'), integer('audit')], {
        'result': {'node': 'native', 'output': 'return'}, 'audit': {'node': 'native', 'output': 'audit'}})
    graph.update(entry='peer', nodes=[peer, call, consumer],
                 edges=[edge('peer', 'native'), edge('native', 'consume'), edge('consume', 'exit:return')],
                 exits={'return': {'node': 'native', 'output': 'return'}})
    defs = f.metadata('blueprintDescribeOwned', project=str(project), id=impl_id,
                      text=implementation.read_text(), graph=graph, bodyTarget='common', definitionsOnly=True)
    assert defs['state'] == 'node-definitions', defs
    for qualified, name, source in [
        ('peer/native', 'Peer.node.json', 'System.Console.WriteLine("peer");'),
        ('consume', 'Consume.node.json', 'System.Console.WriteLine("consume:"+result+":"+audit);'),
    ]:
        definition = next(node for node in defs['nodes'] + defs['nestedNodes'] if node['id'] == qualified)
        (f.project/name).write_text(json.dumps(dict(schema=1, node=qualified.split('/')[-1],
                                                   definitionHash=definition['definitionHash'], source=source)))
    graph_file.write_text(json.dumps(graph))
    (f.project/'Main.csbody').write_text(
        'foreach(int amount in new int[]{5,8}) {var value=calls.Pair.Invoke(amount);'
        'System.Console.WriteLine("result:"+value);}return 7;')
    x.physical = {path: path.read_bytes() for path in f.project.iterdir() if path.is_file()}
    return graph


def read():
    return f.invoke('blueprint', {'action': 'read', 'id': graph_id})['result']['result']


def first():
    return doc().locator('[data-document-call-first-branch=native]')


def edit_body(dialog, source):
    field = dialog.locator('[data-code-source]')
    expect(field).to_be_visible()
    field.evaluate('''el => {
        const spans = Array.from(el.closest('.bp-script-editor').querySelectorAll('[data-code-highlight] > span'));
        const index = spans.findIndex(span => span.dataset.codeRegion === 'body');
        if (index < 0) throw Error('Missing editable body');
        const start = spans.slice(0, index).reduce((length, span) => length + span.textContent.length, 0);
        el.focus();
        el.setSelectionRange(start, start + spans[index].textContent.length);
    }''')
    f.page.keyboard.insert_text(source)


def save():
    panel().locator('[data-bp-save]').click()
    expect(panel().locator('.bp-status')).to_have_text('저장됨', timeout=120000)
    assert not pending()


def confirm():
    window = review()
    window.locator('#confirm').click()
    expect(window).to_be_hidden(timeout=120000)
    f.idle()


try:
    root = seed()
    before_run = 'peer\noriginal:5\nconsume:8:50\nresult:8\npeer\noriginal:8\nconsume:11:80\nresult:11'
    x.build('first-branch-before', 7, before_run)
    f.start(0)
    f.invoke('select', {'id': t.feature})
    f.invoke('saveDraft', {})
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    before = checkpoint.read_bytes()
    with sync_playwright() as pw:
        expect.set_options(timeout=30000)
        f.browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        f.page = f.setup()
        f.page.set_viewport_size({'width': 1900, 'height': 1500})
        open_document()
        if '--baseline' in sys.argv:
            expect(doc().locator('[data-document-cell=native]')).to_be_visible()
            expect(first()).to_have_count(0)
            sys.exit(0)
        assert next(row for row in read()['nodes'] if row['id'] == 'native')['wrapperEditor']
        doc().locator('[data-document-internal=peer]').click()
        f.idle()
        expect(doc().locator('[data-document-cell=native]')).to_be_visible()
        expect(first()).to_have_count(0)
        panel().locator('.bp-breadcrumbs button').first.click()
        f.idle()
        expect(first()).to_be_visible()

        first().click()
        dialog = f.page.get_by_role('dialog', name='분기 기능 편집 · NativeChoice', exact=True)
        expect(dialog.locator('[data-code-region=enum]')).to_contain_text('분기1')
        edit_body(dialog, 'throw new System.InvalidOperationException("Cancelled");')
        dialog.locator('[data-code-cancel]').click()
        expect(first()).to_be_visible()
        assert not pending() and checkpoint.read_bytes() == before
        x.original()

        source = 'return context.@return > 10 ? Result.분기1 : Result.NoBranch;'
        first().click()
        edit_body(dialog, source)
        dialog.locator('[data-code-save]').click()
        held = pending()
        assert len(held) == 1 and held[0][1]['type'] == 'wrapper'
        plan = json.loads(held[0][1]['text'])
        assert plan['returnMapping'] == 'native-return-out-v1' and plan['source'].strip() == source
        branch, = [member for member in plan['executionEnum']['members'] if member['id'] != 'next']
        case = doc().locator(f'[data-document-branch="case:{branch["id"]}"]')
        expect(case).to_be_visible()
        doc().press('Control+z')
        expect(first()).to_be_visible()
        assert not pending()
        doc().press('Control+y')
        expect(case).to_be_visible()
        assert pending() == held and checkpoint.read_bytes() == before
        x.original()

        save()
        x.original()
        restart(1)
        expect(doc().locator(f'[data-document-branch="case:{branch["id"]}"]')).to_be_visible()
        review().locator('[data-reject]').click()
        x.original()
        confirm()
        wrapped = json.loads(graph_file.read_text())
        assert wrapped['schema'] == root['schema'] == 1
        assert wrapped['edges'] == root['edges'] and wrapped['exits'] == root['exits']
        assert wrapped['nodes'][0] == root['nodes'][0] and wrapped['nodes'][2] == root['nodes'][2]
        assert wrapped['nodes'][1]['signature'] == root['nodes'][1]['signature']
        assert wrapped['nodes'][1]['arguments'] == root['nodes'][1]['arguments']
        assert wrapped['nodes'][1]['executionEnum'] == plan['executionEnum']
        assert all(path.read_bytes() == raw for path, raw in x.physical.items() if path != graph_file)
        f.checked('Logic Code creates exactly one protected first branch; Cancel, Undo/Redo, cold Save and Confirm keep the caller inputs and outputs.')

        # The legacy case rail builds the probe, so the test can exercise real branch dispatch.
        panel().get_by_role('tab', name='블루프린트 보기', exact=True).click()
        panel().locator('[data-bp-overview-node=native]').click()
        rail = panel().locator(f'[data-bp-node=native] [data-port="case:{branch["id"]}"]')
        # The overview centers the header. Pan to bring the output rail into view.
        overview = panel().locator('[data-bp-overview]')
        for _ in range(5):
            overview.press('ArrowRight')
        for _ in range(2):
            overview.press('ArrowDown')
        rail.click()
        panel().locator('.bp-viewport').click(button='right', position={'x': 415, 'y': 255})
        resources = f.page.get_by_role('dialog', name='블루프린트 노드 검색', exact=True)
        resources.get_by_role('button', name='동작 만들기', exact=True).click()
        cell = panel().locator('[data-bp-node^=action_]')
        expect(cell).to_have_count(1)
        created = cell.get_attribute('data-bp-node')
        panel().locator(f'[data-bp-overview-node="{created}"]').click()
        cell.locator('[data-inline-description]').fill('branch probe')
        cell.locator('[data-internal-code]').click()
        probe = f.page.locator('.bp-script-dialog')
        edit_body(probe, 'System.Console.WriteLine("selected branch");')
        probe.locator('[data-code-save]').click()
        save()
        confirm()
        panel().get_by_role('tab', name='논리 코드', exact=True).click()
        restart(2)
        expect(doc().locator(f'[data-document-cell="{created}"]')).to_be_visible()
        output = before_run.replace('original:8\n', 'original:8\nselected branch\n')
        x.build('first-branch-executed', 7, output)
        final = json.loads(graph_file.read_text())
        assert final['exits'] == root['exits'] and final['nodes'][0] == root['nodes'][0]
        assert edge('native', created, 'case:'+branch['id']) in final['edges']
        assert all(path.read_bytes() == raw for path, raw in x.physical.items() if path != graph_file)
        assert not f.errors and not f.external, (f.errors, f.external)
        f.checked('Existing case rail executes only the matched branch; return/out values, sibling and callee bytes remain intact.')
        f.browser.close()
finally:
    (f.case/'call-first-branch-checks.json').write_text(json.dumps(f.checks, ensure_ascii=False))
    f.stop()
print('V821_DOCUMENT_CALL_FIRST_BRANCH', f.case, flush=True)
