"""V536 Set target and stored output from the real vertical Logic Code view."""
import ast
import copy
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
import uuid

from playwright.sync_api import expect, sync_playwright

from editor_navigation import goto_editor
import v536_property_plan as f

feature = f.n + 'Calc'
root_id = f.n + 'CalcBody/body:common'
graph_path = f.project / 'Calc.graph.json'
schema_path = f.project / 'Vitals.celem'
stored = {'node': 'first', 'output': 'stored'}
t = SimpleNamespace(feature=feature)
helper = Path(__file__).with_name('v821_function_document_ui.py')
names = {'panel', 'doc', 'open_document', 'review'}
exec(compile(ast.Module(body=[node for node in ast.parse(helper.read_text()).body
                              if isinstance(node, ast.FunctionDef) and node.name in names],
                        type_ignores=[]), str(helper), 'exec'), globals())


def node(cell, kind='code', args=(), result='void', **fields):
    return dict(id=cell, kind=kind, control='next', intent=cell,
                signature={'args': [dict(name=name, type=type_) for name, type_ in args], 'return': result},
                **fields)


def set_node(cell, target, output, value):
    return node(cell, 'set', [('value', 'long')], local=target, outputLocal=output, arguments={'value': value})


def local(id_, label, initial=0, type_='long'):
    return dict(id=id_, name=label, type=type_, initial={'constant': initial})


def edges(cells, tail=None):
    ids = [cell['id'] for cell in cells]
    return [dict(**{'from': left, 'port': 'next', 'to': right})
            for left, right in zip(ids, ids[1:] + ([tail] if tail else []))]


def setup_project():
    schema_path.write_text('schema '+f.n+'Vitals {field health single general long;field shield single general long;}')
    descriptor = f.metadata('blueprintPropertyCatalog', project=str(f.project/'project.cproj'),
                            sourceId=f.n+'CalcBody', owner=f.n+'Monster')['descriptor']
    fields = {field['name']: field for field in descriptor['fields']}
    profile = 'sync-acyclic-property-set-v1'
    peer_cells = [set_node('first', 'counter', 'firstValue', {'constant': 77}),
                  node('echo', args=[('value', 'long')], implementation='Peer.node.json',
                       arguments={'value': stored})]
    peer = node('peer', 'graph', arguments={}, graph=dict(
        schema=1, profile=profile, entry='first', nodes=peer_cells, edges=edges(peer_cells, 'exit:return'),
        locals=[local('counter', '현재 값'), local('firstValue', '첫 저장값')], exits={'return': None}))
    cells = [
        set_node('first', 'spare', 'firstValue', {'input': 'replacement'}),
        node('observe', args=[('counter', 'long'), ('spare', 'long')], implementation='Observe.node.json',
             arguments={'counter': {'local': 'counter'}, 'spare': {'local': 'spare'}}),
        set_node('second', 'counter', 'secondValue', {'constant': 999}),
        node('write', 'property-set', [('target', 'object'), ('value', 'long')], propertyOwner=f.n+'Monster',
             field='health', fieldContractHash=fields['health']['hash'],
             arguments={'target': {'input': 'target'}, 'value': {'constant': -3}}),
        peer,
        node('finish', 'export', [('value', 'long')], output='return', arguments={'value': stored}),
    ]
    graph = {**f.g, 'nodes': cells, 'entry': 'first', 'edges': edges(cells), 'exits': {},
             'locals': [local('counter', '현재 값'), local('spare', '이전 대상', -7),
                        local('firstValue', '첫 저장값'), local('secondValue', '다음 저장값'),
                        local('flag', '조건 저장소', False, 'bool')]}
    definitions = f.metadata('featureBlueprintNodes', featureSource=f.items['Calc'][1], graph=graph,
                             propertyContracts={f.n+'Monster': descriptor}, featureContracts=f.contracts,
                             implementationContext={'implementation': f.n+'CalcBody'}, bodyTarget='common')
    assert definitions['state'] == 'node-definitions', definitions
    records = [
        ('observe', 'Observe.node.json', 'System.Console.WriteLine($"locals:{counter},{spare}");'),
        ('peer/echo', 'Peer.node.json', 'System.Console.WriteLine("peer:" + value);'),
    ]
    for qualified, file, source in records:
        definition = next(item for item in definitions['nodes'] + definitions['nestedNodes'] if item['id'] == qualified)
        (f.project/file).write_text(json.dumps(dict(schema=1, node=qualified.split('/')[-1],
                                                   definitionHash=definition['definitionHash'], source=source)))
    graph_path.write_text(json.dumps(graph))
    main = f.project/'MainBody.celem'
    main.write_text(main.read_text().replace('body common',
                    'import '+f.model+'::Read as Inspect (object,string,string,string) -> object;body common'))
    owner = json.dumps(f.n+'Monster')
    create = ('calls.Create.Invoke('+json.dumps(json.dumps(descriptor, separators=(',', ':')))+
              ',new[]{'+','.join(json.dumps(fields[name]['id']) for name in ['health', 'shield'])+'},')
    reads = [','.join([owner, json.dumps(fields[name]['id']), json.dumps(fields[name]['hash'])])
             for name in ['health', 'shield']]
    (f.project/'Main.csbody').write_text(
        'object target='+create+'new object[]{10L,17L}); object other='+create+'new object[]{11L,18L});'
        'System.Console.WriteLine("result:"+calls.Calc.Invoke(target,42));'+
        'System.Console.WriteLine("target:"+calls.Inspect.Invoke(target,'+reads[0]+')+","+calls.Inspect.Invoke(target,'+reads[1]+'));'+
        'System.Console.WriteLine("other:"+calls.Inspect.Invoke(other,'+reads[0]+')+","+calls.Inspect.Invoke(other,'+reads[1]+'));return 0;')
    return graph


def execute(label, output):
    built = subprocess.run([f.env['CONFECTORY_DOTNET'], str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),
                            'build', str(f.project/'project.cproj'), 'portable'],
                           capture_output=True, text=True, env=f.env)
    assert built.returncode == 0, built.stderr
    result = subprocess.run(json.loads(built.stdout)['run'], capture_output=True, text=True, env=f.env)
    assert result.returncode == 0, result.stderr
    (f.case/(label+'.txt')).write_text(result.stdout)
    assert result.stdout.splitlines() == output, result.stdout


def rejected_type(checkpoint, original_checkpoint):
    current = f.current()
    proof = json.dumps(sorted((row['id'], row['revision'], row['hash']) for row in current['sources']),
                       separators=(',', ':'))
    request = {'action': 'authorBatch', 'id': root_id, 'attempt': uuid.uuid4().hex,
               'checkpointHash': current['checkpointHash'], 'sourceProof': proof,
               'edits': [{'action': 'setPlan', 'node': '$sets', 'definition': {
                   'nodes': [dict(id='first', local='flag', outputLocal='firstValue', type='long',
                                  valueJson='{"input":"replacement"}')]}}]}
    reply = f.call('blueprint', request, ok=False)
    assert reply['error']['code'] == 'consumer_error'
    assert checkpoint.read_bytes() == original_checkpoint and f.current()['nodes'] == current['nodes']
    f.unchanged()
    schema = schema_path.read_bytes()
    schema_path.write_bytes(schema.replace(b'health single general long', b'health single general bool'))
    try:
        request['attempt'] = uuid.uuid4().hex
        request['edits'][0]['definition']['nodes'][0]['local'] = 'counter'
        reply = f.call('blueprint', request, ok=False)
        assert reply['error']['code'] == 'consumer_error'
        assert checkpoint.read_bytes() == original_checkpoint
    finally:
        schema_path.write_bytes(schema)
    f.unchanged()


def open_page(browser):
    f.page = browser.new_page(viewport={'width': 1850, 'height': 1250})
    f.page.on('pageerror', lambda error: errors.append(str(error)))
    f.page.route('**/*', lambda route: route.continue_() if route.request.url.startswith(f.origin+'/') else route.abort())
    goto_editor(f.page, f.url)
    f.page.wait_for_function("() => typeof globalThis.confectoryFlushPresentation === 'function'")


def pending():
    f.page.evaluate('() => confectoryFlushPresentation()')
    return [(key, row) for key, row in f.state()['presentation']['inputs']['blueprint'] if row.get('type')]


def stable_draft(path):
    data = json.loads(path.read_bytes())
    return {row['id']: {key: value for key, value in row.items() if key != 'revision'} for row in data['changes']}


def run(browser, graph, checkpoint, before):
    open_page(browser)
    open_document()
    target = doc().locator('[data-document-set-target="first"]')
    write = doc().locator('[data-document-value="write"][data-document-port="field:value"]')
    expect(target).to_have_value('spare')
    expect(target.locator('option[value="flag"]')).to_have_attribute('disabled', '')
    target.select_option('counter')
    expect(target).to_have_value('counter')
    doc().press('Control+z')
    expect(target).to_have_value('spare')
    assert not pending() and checkpoint.read_bytes() == before
    target.select_option('counter')
    panel().get_by_role('tab', name='블루프린트 보기', exact=True).click()
    expect(panel().locator('[data-bp-node="first"] [data-set-target]')).to_have_value('counter')
    panel().get_by_role('tab', name='논리 코드', exact=True).click()
    write.click()
    values = f.page.get_by_role('dialog', name='핀 값 선택')
    values.get_by_role('button', name='중간저장 · 첫 저장값', exact=True).click()
    expect(write).to_contain_text('중간저장')
    held = pending()
    assert {row['type'] for _, row in held} == {'set-plan', 'property-plan', 'argument:value'}
    binding = next(row for _, row in held if row['type'] == 'argument:value')
    assert binding['node'] == 'write' and json.loads(binding['text']) == stored
    assert checkpoint.read_bytes() == before
    f.unchanged()
    f.checked('Logic Code reuses the Set selector. Undo cancels the target edit; the explicit property value uses stored rather than a live local.')

    schema = schema_path.read_bytes()
    schema_path.write_bytes(schema.replace(b'health single general long', b'health single general bool'))
    try:
        panel().locator('[data-bp-save]').click()
        assert pending() == held
        assert checkpoint.read_bytes() == before
        expect(target).to_have_value('counter')
        expect(write).to_contain_text('중간저장')
    finally:
        schema_path.write_bytes(schema)
    f.unchanged()
    f.checked('A stale property field contract refuses the combined Save and preserves the target and consuming input.')

    panel().locator('[data-bp-save]').click()
    expect(panel().locator('.bp-status')).to_have_text('저장됨', timeout=120000)
    assert not pending()
    f.unchanged()
    snapshot = stable_draft(checkpoint)
    saved = json.loads(checkpoint.read_bytes())
    assert saved['version'] == 1

    f.page.close()
    f.stop()
    f.start(1)
    open_page(browser)
    target = doc().locator('[data-document-set-target="first"]')
    write = doc().locator('[data-document-value="write"][data-document-port="field:value"]')
    expect(target).to_have_value('counter')
    expect(write).to_contain_text('중간저장')
    peer = f.call('blueprint', {'action': 'read', 'id': root_id+'/graph:peer'})
    sibling_set = next(row for row in peer['nodes'] if row['id'] == 'first')
    assert json.loads(sibling_set['arguments'][0]['valueJson']) == {'constant': 77}
    review().locator('[data-reject]').click()
    assert stable_draft(checkpoint) == snapshot
    f.unchanged()
    window = review()
    window.locator('#confirm').click()
    expect(window).to_be_hidden(timeout=120000)
    f.idle()
    expected = copy.deepcopy(graph)
    expected['nodes'][0]['local'] = 'counter'
    next(row for row in expected['nodes'] if row['id'] == 'write')['arguments']['value'] = stored
    assert json.loads(graph_path.read_text()) == expected
    assert all((f.project/name).read_bytes() == raw for name, raw in f.original.items() if name != graph_path.name)
    execute('confirmed', ['locals:42,-7', 'peer:77', 'result:42', 'target:42,17', 'other:11,18'])
    assert not errors, errors
    f.checked('Cold reopen, Review cancellation and Confirm preserve the exact draft, sibling and sources. CLR writes only target.health from the first Set snapshot.')


f.author = lambda: f.page.locator('.window[data-key=blueprint]')
f.idle = lambda: expect(f.page.locator('.brand')).to_be_enabled(timeout=60000)
errors = []
try:
    graph = setup_project()
    f.original = {path.name: path.read_bytes() for path in f.project.iterdir() if path.is_file()}
    execute('before', ['locals:0,42', 'peer:77', 'result:42', 'target:-3,17', 'other:11,18'])
    f.start(0)
    f.call('select', {'id': feature})
    f.call('saveDraft', {})
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    before = checkpoint.read_bytes()
    rejected_type(checkpoint, before)
    f.checked('A target-only Set rejects incompatible storage and a changed observed schema without writing the checkpoint.')
    with sync_playwright() as playwright:
        expect.set_options(timeout=30000)
        with playwright.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox']) as browser:
            run(browser, graph, checkpoint, before)
finally:
    f.stop()
    print('Evidence:', f.case)
