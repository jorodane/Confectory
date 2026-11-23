"""Property card scope and real read-to-Set-to-write editing in Logic Code."""
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
read_value = {'node': 'read', 'output': 'return'}
second_project = f.case / 'second project'
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


def setup_project(project, object_name, write_field, read_field):
    owner_id = f.n+object_name
    if project != f.project:
        project.mkdir()
        for file, content in f.sources.items():
            if file != 'Monster.celem':
                (project/file).write_text(content)
        (project/(object_name+'.celem')).write_text(f'object {owner_id} {{use schema {f.n}Vitals;}}')
        manifest = project/'project.cproj'
        manifest.write_text(manifest.read_text().replace(
            'element Monster object "Monster.celem"', f'element {object_name} object "{object_name}.celem"'))
    (project/'Vitals.celem').write_text(
        f'schema {f.n}Vitals {{field {write_field} single general long;field {read_field} single general long;}}')
    descriptor = f.metadata('blueprintPropertyCatalog', project=str(project/'project.cproj'),
                            sourceId=f.n+'CalcBody', owner=owner_id)['descriptor']
    fields = {field['name']: field for field in descriptor['fields']}
    profile = 'sync-acyclic-property-set-v1'
    peer_cells = [set_node('first', 'counter', 'firstValue', {'constant': 77}),
                  node('echo', args=[('value', 'long')], implementation='Peer.node.json',
                       arguments={'value': stored})]
    peer = node('peer', 'graph', arguments={}, graph=dict(
        schema=1, profile=profile, entry='first', nodes=peer_cells, edges=edges(peer_cells, 'exit:return'),
        locals=[local('counter', '현재 값'), local('firstValue', '첫 저장값')], exits={'return': None}))
    cells = [
        node('read', 'property', [('target', 'object')], result='long', propertyOwner=owner_id,
             field=read_field, fieldContractHash=fields[read_field]['hash'],
             arguments={'target': {'input': 'target'}}),
        set_node('first', 'spare', 'firstValue', {'input': 'replacement'}),
        node('observe', args=[('counter', 'long'), ('spare', 'long')], implementation='Observe.node.json',
             arguments={'counter': {'local': 'counter'}, 'spare': {'local': 'spare'}}),
        set_node('second', 'counter', 'secondValue', {'constant': 999}),
        node('write', 'property-set', [('target', 'object'), ('value', 'long')], propertyOwner=owner_id,
             field=write_field, fieldContractHash=fields[write_field]['hash'],
             arguments={'target': {'input': 'target'}, 'value': {'constant': -3}}),
        peer,
        node('finish', 'export', [('value', 'long')], output='return', arguments={'value': stored}),
    ]
    graph = {**f.g, 'nodes': cells, 'entry': 'read', 'edges': edges(cells), 'exits': {},
             'locals': [local('counter', '현재 값'), local('spare', '이전 대상', -7),
                        local('firstValue', '첫 저장값'), local('secondValue', '다음 저장값'),
                        local('flag', '조건 저장소', False, 'bool')]}
    definitions = f.metadata('featureBlueprintNodes', featureSource=f.items['Calc'][1], graph=graph,
                             propertyContracts={owner_id: descriptor}, featureContracts=f.contracts,
                             implementationContext={'implementation': f.n+'CalcBody'}, bodyTarget='common')
    assert definitions['state'] == 'node-definitions', definitions
    records = [
        ('observe', 'Observe.node.json', 'System.Console.WriteLine($"locals:{counter},{spare}");'),
        ('peer/echo', 'Peer.node.json', 'System.Console.WriteLine("peer:" + value);'),
    ]
    for qualified, file, source in records:
        definition = next(item for item in definitions['nodes'] + definitions['nestedNodes'] if item['id'] == qualified)
        (project/file).write_text(json.dumps(dict(schema=1, node=qualified.split('/')[-1],
                                                 definitionHash=definition['definitionHash'], source=source)))
    (project/'Calc.graph.json').write_text(json.dumps(graph))
    main = project/'MainBody.celem'
    main.write_text(main.read_text().replace('body common',
                    'import '+f.model+'::Read as Inspect (object,string,string,string) -> object;body common'))
    owner = json.dumps(owner_id)
    create = ('calls.Create.Invoke('+json.dumps(json.dumps(descriptor, separators=(',', ':')))+
              ',new[]{'+','.join(json.dumps(fields[name]['id']) for name in [write_field, read_field])+'},')
    reads = [','.join([owner, json.dumps(fields[name]['id']), json.dumps(fields[name]['hash'])])
             for name in [write_field, read_field]]
    (project/'Main.csbody').write_text(
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


def property_card(field, owner):
    card = doc().locator('[data-document-cell="write"]')
    expect(card.locator('.fd-cell-title')).to_have_text(field)
    expect(card.locator('.fd-cell-state')).to_have_text('속성 쓰기')
    expect(card.locator('[data-document-property-owner]')).to_have_text(f.n+owner)


def enter_project(name):
    f.page.evaluate("() => globalThis.confectoryFlushPresentation()")
    f.page.locator('.brand').click()
    expect(f.page.locator('.home-grid')).to_be_visible()
    f.page.locator('.project-card').filter(
        has=f.page.get_by_role('heading', name=name, exact=True)).locator('[data-enter]').click()
    expect(f.page.locator('#title')).to_contain_text(name)
    open_document()


def run(browser, graph, checkpoint, before):
    open_page(browser)
    open_document()
    property_card('health', 'Monster')
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
    set_input = doc().locator('[data-document-value="first"][data-document-port="field:value"]')
    set_input.click()
    f.page.get_by_role('dialog', name='핀 값 선택').get_by_role('button', name='속성 · shield · shield', exact=True).click()
    expect(set_input).to_contain_text('shield')
    write.click()
    values = f.page.get_by_role('dialog', name='핀 값 선택')
    values.get_by_role('button', name='중간저장 · 첫 저장값', exact=True).click()
    expect(write).to_contain_text('중간저장')
    held = pending()
    assert {row['type'] for _, row in held} == {'set-plan', 'property-plan', 'argument:value'}
    bindings = {row['node']: json.loads(row['text']) for _, row in held if row['type'] == 'argument:value'}
    assert bindings == {'first': read_value, 'write': stored}
    assert checkpoint.read_bytes() == before
    f.unchanged()
    f.checked('Logic Code shows the verified write field and stages the existing read, Set target and stored-output link.')

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
    property_card('health', 'Monster')
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
    first = next(row for row in expected['nodes'] if row['id'] == 'first')
    first.update(local='counter', arguments={'value': read_value})
    next(row for row in expected['nodes'] if row['id'] == 'write')['arguments']['value'] = stored
    assert json.loads(graph_path.read_text()) == expected
    assert all((f.project/name).read_bytes() == raw for name, raw in f.original.items() if name != graph_path.name)
    execute('confirmed', ['locals:17,-7', 'peer:77', 'result:17', 'target:17,17', 'other:11,18'])
    f.checked('Cold reopen, Review cancellation and Confirm preserve the exact draft, sibling and sources. CLR writes only target.health from the first Set snapshot.')
    enter_project('Property Second')
    property_card('energy', 'Robot')
    expect(doc().get_by_text(f.n+'Monster', exact=True)).to_have_count(0)
    enter_project('Property First')
    property_card('health', 'Monster')
    expect(doc().get_by_text(f.n+'Robot', exact=True)).to_have_count(0)
    assert all((second_project/name).read_bytes() == raw for name, raw in second_original.items())
    assert not errors, errors
    f.checked('The same local write ID follows its verified owner and field on a project switch and return.')


f.author = lambda: f.page.locator('.window[data-key=blueprint]')
f.idle = lambda: expect(f.page.locator('.brand')).to_be_enabled(timeout=60000)
errors = []
try:
    graph = setup_project(f.project, 'Monster', 'health', 'shield')
    setup_project(second_project, 'Robot', 'energy', 'capacity')
    f.original = {path.name: path.read_bytes() for path in f.project.iterdir() if path.is_file()}
    second_original = {path.name: path.read_bytes() for path in second_project.iterdir() if path.is_file()}
    profile = Path(f.env['CONFECTORY_ENTRY_STORAGE'])
    profile.mkdir(exist_ok=True)
    (profile/'projects.json').write_text(json.dumps([
        {'path': str(project/'project.cproj'), 'title': title, 'description': ''}
        for project, title in [(f.project, 'Property First'), (second_project, 'Property Second')]
    ]))
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
