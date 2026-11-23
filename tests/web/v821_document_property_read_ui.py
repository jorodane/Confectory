"""Real Logic Code property read and consumption in one owned synchronous child."""
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
frame = root_id + '/graph:work'
sibling = root_id + '/graph:peer'
graph_path = f.project / 'Calc.graph.json'
profile = 'sync-acyclic-methods-v1'
t = SimpleNamespace(feature=feature)
helper = Path(__file__).with_name('v821_function_document_ui.py')
names = {'panel', 'doc', 'open_document', 'review'}
exec(compile(ast.Module(body=[node for node in ast.parse(helper.read_text()).body
                              if isinstance(node, ast.FunctionDef) and node.name in names],
                        type_ignores=[]), str(helper), 'exec'), globals())


def sig(args=(), result='void'):
    return {'args': [{'name': name, 'type': kind} for name, kind in args], 'return': result}


def edge(source, target):
    return {'from': source, 'port': 'next', 'to': target}


def code(cell, file, signature, arguments):
    return {'id': cell, 'kind': 'code', 'control': 'next', 'intent': cell, 'signature': signature,
            'arguments': arguments, 'implementation': file}


def compound(cell, children, child_exits):
    ports = sig([('target', 'object'), ('replacement', 'long')], 'long')
    return {'id': cell, 'kind': 'graph', 'control': 'next', 'intent': cell, 'signature': ports,
            'arguments': {port['name']: {'input': port['name']} for port in ports['args']},
            'graph': {'schema': 1, 'profile': profile, 'entry': children[0]['id'], 'nodes': children,
                      'edges': [edge(node['id'], after['id'])
                                for node, after in zip(children, children[1:] + [{'id': 'exit:return'}])],
                      'exits': child_exits}}


def setup_project():
    child_args = sig([('value', 'long'), ('flag', 'bool')], 'long')
    exit_value = {'return': {'node': 'consume', 'output': 'return'}}
    selected = compound('work', [code('mark', 'Mark.node.json', sig(), {}),
                                 code('consume', 'Work.node.json', child_args,
                                      {'value': {'constant': 1}, 'flag': {'constant': False}})], exit_value)
    peer = compound('peer', [code('consume', 'Peer.node.json', child_args,
                                  {'value': {'constant': 9}, 'flag': {'constant': False}})], exit_value)
    graph = {**f.g, 'profile': profile, 'entry': 'work', 'nodes': [selected, peer],
             'edges': [edge('work', 'peer'), edge('peer', 'exit:return')],
             'exits': {'return': {'node': 'work', 'output': 'return'}}}
    graph.pop('locals')
    definitions = f.metadata('featureBlueprintNodes', featureSource=f.items['Calc'][1], graph=graph,
                             implementationContext={'implementation': f.n + 'CalcBody'}, bodyTarget='common')
    assert definitions['state'] == 'node-definitions', definitions
    rows = definitions['nestedNodes']
    for qualified, file, source in [
            ('work/mark', 'Mark.node.json', 'System.Console.WriteLine("mark");'),
            ('work/consume', 'Work.node.json', 'System.Console.WriteLine("work:" + value);return value;'),
            ('peer/consume', 'Peer.node.json', 'System.Console.WriteLine("peer:" + value);return value;')]:
        definition = next(row for row in rows if row['id'] == qualified)
        (f.project / file).write_text(json.dumps({'schema': 1, 'node': qualified.split('/')[-1],
                                                  'definitionHash': definition['definitionHash'], 'source': source}))
    graph_path.write_text(json.dumps(graph))
    main = f.project / 'Main.csbody'
    create = f'calls.Create.Invoke({json.dumps(json.dumps(f.descriptor, separators=(",", ":")))},' \
             f'new[]{{{json.dumps(f.field["id"])}}},new object[]{{25L}})'
    main.write_text(main.read_text().replace('calls.Calc.Invoke(target,30)', 'calls.Calc.Invoke('+create+',30)'))
    return graph


def execute(label, values):
    build = subprocess.run([f.env['CONFECTORY_DOTNET'], str(f.repo / 'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),
                            'build', str(f.project / 'project.cproj'), 'portable'],
                           env=f.env, capture_output=True, text=True)
    assert build.returncode == 0, build.stderr
    command = json.loads(build.stdout)['run']
    done = subprocess.run(command, env=f.env, capture_output=True, text=True, check=True)
    (f.case / (label + '.txt')).write_text(done.stdout)
    assert done.stdout.splitlines() == [line for value in values
                                       for line in ['mark', f'work:{value}', 'peer:9', str(value)]], done.stdout


def blueprint(action, graph=frame, *, ok=True, **options):
    return f.call('blueprint', {'action': action, 'id': graph, **options}, ok=ok)


def rejected_plans(before_checkpoint):
    current = blueprint('read')
    prepared = blueprint('readProperty', node='sample_read', owner=f.n+'Monster', field='health',
                         targetJson='{"input":"target"}', access='read')
    assert prepared['readTiming'] == 'execution-node'
    proof = json.dumps(sorted((row['id'], row['revision'], row['hash']) for row in current['sources']),
                       separators=(',', ':'))
    consumer = next(node for node in current['nodes'] if node['id'] == 'consume')
    source = next(row for row in current['sources'] if row['id'] == consumer['sourceId'])
    binding = dict(graph=frame, root=root_id, node=consumer['id'], source=source['id'],
                   definitionHash=consumer['definitionHash'], sourceHash=source['hash'])
    plan = {'reads': [dict(node='sample_read', owner=f.n+'Monster', field='health',
                           targetJson='{"input":"target"}', descriptor=prepared['descriptor'])],
            'changes': [dict(action='route', node='mark', port='next', to='sample_read'),
                        dict(action='route', node='sample_read', port='next', to='consume'),
                        dict(action='argument', node='consume', name='value',
                             valueJson='{"node":"sample_read","output":"return"}')]}

    def reject(change, graph=frame, source_binding=binding):
        reply = blueprint('authorBatch', graph, ok=False, attempt=uuid.uuid4().hex,
                          sourceProof=proof, checkpointHash=current['checkpointHash'], privateBinding=source_binding,
                          edits=[{'action': 'propertyPlan', 'node': '$properties', 'definition': change}])
        assert reply['error']['code'] == 'consumer_error', reply
        assert checkpoint.read_bytes() == before_checkpoint
        assert blueprint('read')['sources'] == current['sources']
        f.unchanged()

    wrong_receiver = copy.deepcopy(plan)
    wrong_receiver['reads'][0]['targetJson'] = '{"input":"replacement"}'
    reject(wrong_receiver)
    wrong_type = copy.deepcopy(plan)
    wrong_type['changes'][2]['name'] = 'flag'
    reject(wrong_type)
    wrong_origin = copy.deepcopy(binding)
    wrong_origin['graph'] = sibling
    reject(plan, graph=sibling, source_binding=wrong_origin)
    f.checked('An invalid receiver, incompatible input or the same local consumer ID in a sibling leaves the checkpoint unchanged.')


def open_page(browser):
    f.page = browser.new_page(viewport={'width': 1850, 'height': 1250})
    f.page.on('pageerror', lambda error: errors.append(str(error)))
    f.page.route('**/*', lambda route: route.continue_() if route.request.url.startswith(f.origin+'/') else route.abort())
    goto_editor(f.page, f.url)
    f.page.wait_for_function("() => typeof globalThis.confectoryFlushPresentation === 'function'")


def pin(name='value'):
    return doc().locator(f'[data-document-value="consume"][data-document-port="field:{name}"]')


def pending():
    f.page.evaluate('() => confectoryFlushPresentation()')
    return f.state()['presentation']['inputs']['blueprint']


def pick(name='value'):
    pin(name).click()
    f.page.get_by_role('dialog', name='핀 값 선택').get_by_role('button', name='속성 읽기 연결…').click()
    dialog = f.page.get_by_role('dialog', name='속성 읽기 연결')
    dialog.locator('[data-property-receiver]').select_option('target')
    dialog.locator('[data-property-owner]').select_option(f.n+'Monster')
    return dialog


def enter():
    doc().locator('[data-document-internal="work"]').click()
    expect(pin()).to_be_visible()


def run(browser, graph, original_checkpoint):
    open_page(browser)
    open_document()
    enter()
    dialog = pick('flag')
    expect(dialog.locator('[data-property-status]')).to_have_text('이 입력과 자료형이 같은 속성이 없습니다.')
    expect(dialog.locator('[data-property-connect]')).to_be_disabled()
    dialog.locator('[data-property-cancel]').click()
    expect(pin('flag')).to_be_focused()
    assert not pending() and checkpoint.read_bytes() == original_checkpoint
    dialog = pick()
    dialog.locator('[data-property-field]').select_option('health')
    dialog.locator('[data-property-connect]').click()
    expect(dialog).to_be_hidden()
    expect(pin()).to_contain_text('health')
    assert checkpoint.read_bytes() == original_checkpoint
    assert len(pending()) == 4
    f.checked('The Logic Code picker filters by consumer type and stages the selected receiver, read and link together.')

    schema = f.project / 'Vitals.celem'
    original_schema = schema.read_bytes()
    schema.write_bytes(original_schema.replace(b'long', b'bool'))
    try:
        panel().locator('[data-bp-save]').click()
        expect(panel().locator('.bp-status')).not_to_have_text('저장 중…', timeout=120000)
        f.idle()
        assert checkpoint.read_bytes() == original_checkpoint
        assert len([row for _, row in pending() if row.get('type')]) == 4
        expect(pin()).to_contain_text('health')
    finally:
        schema.write_bytes(original_schema)
    f.unchanged()
    f.checked('A changed field contract rejects Save and retains both the pending read and the consumed value.')

    panel().locator('[data-bp-save]').click()
    expect(panel().locator('.bp-status')).to_have_text('저장됨', timeout=120000)
    assert not pending()
    f.unchanged()
    saved = json.loads(checkpoint.read_bytes())
    f.page.close()
    f.stop()
    f.start(1)
    open_page(browser)
    expect(pin()).to_contain_text('health')
    cards = doc().locator('[data-document-cell]').evaluate_all('(cells) => cells.map(cell => cell.dataset.documentCell)')
    assert len(cards) == 5 and cards[:2] == ['$entry', 'mark'] and cards[-2:] == ['consume', '$exit:return'], cards
    assert cards[2].startswith('property_'), cards
    expect(doc().locator(f'[data-document-value="{cards[2]}"][data-document-port="field:target"]')).to_have_text('target')
    review().locator('[data-reject]').click()
    retained = json.loads(checkpoint.read_bytes())
    # Reopening and then saving rebases the live revision, while the saved
    # candidate, physical source guards and semantic history stay the same.
    def saved_units(snapshot):
        return {row['id']: {key: value for key, value in row.items() if key != 'revision'}
                for row in snapshot['changes']}
    assert saved_units(retained) == saved_units(saved)
    assert {k: v for k, v in retained['history'].items() if k != 'epoch'} == {
        k: v for k, v in saved['history'].items() if k != 'epoch'}
    f.unchanged()
    final_review = review()
    final_review.locator('#confirm').click()
    expect(final_review).to_be_hidden(timeout=120000)
    actual = json.loads(graph_path.read_text())
    expected = copy.deepcopy(graph)
    child = expected['nodes'][0]['graph']
    read_id = cards[2]
    added = next(node for node in actual['nodes'][0]['graph']['nodes'] if node['id'] == read_id)
    assert added['kind'] == 'property' and added['field'] == 'health' and added['propertyOwner'] == f.n+'Monster'
    assert added['arguments'] == {'target': {'input': 'target'}}
    child['nodes'].append(added)
    child['nodes'][1]['arguments']['value'] = {'node': read_id, 'output': 'return'}
    child['edges'] = [edge('consume', 'exit:return'), edge('mark', read_id), edge(read_id, 'consume')]
    assert actual == expected
    assert all((f.project / name).read_bytes() == raw for name, raw in f.original.items() if name != graph_path.name)
    assert not errors, errors
    execute('confirmed', [10, 25])
    f.checked('Cold Save, Review cancellation and Confirm preserve sources and the same-ID sibling. The compiled child consumes the actual property value.')


f.author = lambda: f.page.locator('.window[data-key=blueprint]')
f.idle = lambda: expect(f.page.locator('.brand')).to_be_enabled(timeout=60000)
errors = []
try:
    graph = setup_project()
    f.original = {path.name: path.read_bytes() for path in f.project.iterdir() if path.is_file()}
    execute('baseline', [1, 1])
    f.start(0)
    f.call('select', {'id': feature})
    f.call('saveDraft', {})
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    original_checkpoint = checkpoint.read_bytes()
    rejected_plans(original_checkpoint)
    with sync_playwright() as playwright:
        expect.set_options(timeout=30000)
        with playwright.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox']) as browser:
            run(browser, graph, original_checkpoint)
finally:
    f.stop()
    print('Evidence:', f.case)
