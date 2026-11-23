"""Real Logic Code property read and consumption in an owned root or child."""
import ast
import copy
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import uuid

from playwright.sync_api import expect, sync_playwright

from editor_navigation import goto_editor
import v536_property_plan as f

feature = f.n + 'Calc'
root_id = f.n + 'CalcBody/body:common'
frame = root_id + '/graph:work'
sibling = root_id + '/graph:peer'
menu = 'menu' in sys.argv[3:]
root = menu or 'root' in sys.argv[3:]
shared = 'shared' in sys.argv[3:]
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
    if root:
        graph.update(selected['graph'])
        graph['nodes'].insert(1, code('other', 'Other.node.json', sig(), {}))
        graph['edges'] = [edge('mark', 'other'), edge('other', 'consume'), edge('consume', 'exit:return')]
    graph.pop('locals')
    definition_source = f.items['Calc'][1]
    if menu:
        for name in ['Calc', 'CalcBody', 'MainBody']:
            path = f.project / (name + '.celem')
            path.write_text(path.read_text().replace('object target,long replacement','object target,object alternate,long replacement')
                            .replace('as Calc (object,long)', 'as Calc (object,object,long)'))
        definition_source = (f.project / 'Calc.celem').read_text()
        prepared = f.metadata('blueprintPrepareFeature', id=feature, text='function '+feature+' (object target,object alternate,long replacement) -> long {}',
                              implementation=f.n+'CalcBody', graphPath='Calc.graph.json', nodePath='Work.node.json')
        graph['contractHash'] = prepared['graph']['contractHash']
    definitions = f.metadata('featureBlueprintNodes', featureSource=definition_source, graph=graph,
                             implementationContext={'implementation': f.n + 'CalcBody'}, bodyTarget='common')
    assert definitions['state'] == 'node-definitions', definitions
    rows = definitions['nodes' if root else 'nestedNodes']
    bodies = [
        ('work/mark', 'Mark.node.json', 'System.Console.WriteLine("mark");'),
        ('work/consume', 'Work.node.json', 'System.Console.WriteLine("work:" + value);return value;'),
        ('peer/consume', 'Peer.node.json', 'System.Console.WriteLine("peer:" + value);return value;'),
    ]
    if root:
        bodies = [(cell.split('/')[-1], file, source) for cell, file, source in bodies[:2]]
        bodies.append(('other', 'Other.node.json', 'System.Console.WriteLine("other");'))
    for qualified, file, source in bodies:
        definition = next(row for row in rows if row['id'] == qualified)
        (f.project / file).write_text(json.dumps({'schema': 1, 'node': qualified.split('/')[-1],
                                                  'definitionHash': definition['definitionHash'], 'source': source}))
    if shared:
        graph['copySource'] = {'implementation': f.n+'Origin', 'target': 'common',
                               'bodyOrigin': f.n+'Origin', 'sourceKind': 'blueprint'}
    graph_path.write_text(json.dumps(graph))
    main = f.project / 'Main.csbody'
    create = f'calls.Create.Invoke({json.dumps(json.dumps(f.descriptor, separators=(",", ":")))},' \
             f'new[]{{{json.dumps(f.field["id"])}}},new object[]{{25L}})'
    if menu:
        def create_with(value):
            return create.replace('25L', f'{value}L')
        main.write_text(f'object preferred = {create_with(10)};'
                        f'Console.WriteLine(calls.Calc.Invoke(preferred,{create_with(70)},20));'
                        f'Console.WriteLine(calls.Calc.Invoke(preferred,{create_with(85)},30));return 0;')
    else:
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
    expected = []
    for value in values:
        expected.extend(['mark', 'other', f'work:{value}', str(value)] if root
                        else ['mark', f'work:{value}', 'peer:9', str(value)])
    assert done.stdout.splitlines() == expected, done.stdout


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
    if not root:
        doc().locator('[data-document-internal="work"]').click()
    expect(pin()).to_be_visible()


def run(browser, graph, original_checkpoint):
    open_page(browser)
    open_document()
    enter()
    if shared:
        assert blueprint('read', root_id)['requiresCoupledCopy']
        pin().click()
        pin_menu = f.page.get_by_role('dialog', name='핀 값 선택')
        expect(pin_menu).to_be_visible()
        expect(pin_menu.get_by_role('button', name='속성 읽기 연결…')).to_have_count(0)
        f.page.keyboard.press('Escape')
        assert not pending() and checkpoint.read_bytes() == original_checkpoint
        f.unchanged()
        f.checked('The same root pin cannot create a property read in a graph with shared copy provenance.')
        return
    dialog = pick('flag')
    expect(dialog.locator('[data-property-status]')).to_have_text('이 입력과 자료형이 같은 속성이 없습니다.')
    expect(dialog.locator('[data-property-connect]')).to_be_disabled()
    dialog.locator('[data-property-cancel]').click()
    expect(pin('flag')).to_be_focused()
    assert not pending() and checkpoint.read_bytes() == original_checkpoint
    if menu:
        button = doc().locator('[data-document-add="other"]')
        def from_edge():
            expect(button).to_have_text('다음 세부기능 추가')
            button.click()
            f.page.get_by_role('dialog', name='다음 세부기능 추가').get_by_role('button', name='속성 읽기', exact=True).click()
            chooser = f.page.get_by_role('dialog', name='속성 읽기 연결')
            expect(chooser.locator('[data-property-receiver]')).to_have_value('')
            expect(chooser.locator('[data-property-consumer]')).to_be_disabled()
            chooser.locator('[data-property-receiver]').select_option('alternate')
            chooser.locator('[data-property-owner]').select_option(f.n+'Monster')
            chooser.locator('[data-property-field]').select_option('health')
            recipient = chooser.locator('[data-property-consumer]')
            expect(recipient).to_have_value('')
            expect(recipient.locator('option')).to_have_text(['선택','consume · value'])
            expect(chooser.locator('[data-property-connect]')).to_be_disabled()
            return chooser
        abandoned = from_edge()
        abandoned.locator('[data-property-consumer]').select_option('value')
        abandoned.locator('[data-property-cancel]').click()
        expect(button).to_be_focused()
        assert not pending() and checkpoint.read_bytes() == original_checkpoint
        dialog = from_edge()
        dialog.locator('[data-property-consumer]').select_option('value')
    else:
        dialog = pick()
        dialog.locator('[data-property-field]').select_option('health')
    dialog.locator('[data-property-connect]').click()
    expect(dialog).to_be_hidden()
    expect(pin()).to_contain_text('health')
    assert checkpoint.read_bytes() == original_checkpoint
    assert len(pending()) == 4
    if menu:
        held = pending()
        doc().press('Control+z')
        expect(pin()).not_to_contain_text('health')
        assert not pending()
        doc().press('Control+y')
        expect(pin()).to_contain_text('health')
        assert pending() == held and checkpoint.read_bytes() == original_checkpoint
        f.checked('Menu starts without a consumer. Cancel preserves the draft and one Undo/Redo removes and restores the explicit read and input.')
    f.checked('The Logic Code picker filters by consumer type and stages the selected receiver, read and link together.')

    conflict = graph_path if root else f.project / 'Vitals.celem'
    original_source = conflict.read_bytes()
    if root:
        reordered = copy.deepcopy(graph)
        reordered['edges'] = [edge('mark', 'consume'), edge('consume', 'other'), edge('other', 'exit:return')]
        conflict.write_text(json.dumps(reordered))
    else:
        conflict.write_bytes(original_source.replace(b'long', b'bool'))
    changed_source = conflict.read_bytes()
    try:
        panel().locator('[data-bp-save]').click()
        expect(panel().locator('.bp-status')).not_to_have_text('저장 중…', timeout=120000)
        f.idle()
        assert checkpoint.read_bytes() == original_checkpoint
        assert conflict.read_bytes() == changed_source
        assert len([row for _, row in pending() if row.get('type')]) == 4
        expect(pin()).to_contain_text('health')
    finally:
        conflict.write_bytes(original_source)
    f.unchanged()
    f.checked('An external route or field change rejects Save while retaining both the pending read and its binding.')

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
    before_read = ['$entry', 'mark', 'other'] if root else ['$entry', 'mark']
    read_id = cards[len(before_read)]
    assert read_id.startswith('property_') and cards == before_read + [read_id, 'consume', '$exit:return'], cards
    receiver = 'alternate' if menu else 'target'
    expect(doc().locator(f'[data-document-value="{read_id}"][data-document-port="field:target"]')).to_have_text(receiver)
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
    scope = expected if root else expected['nodes'][0]['graph']
    actual_scope = actual if root else actual['nodes'][0]['graph']
    added = next(node for node in actual_scope['nodes'] if node['id'] == read_id)
    assert added['kind'] == 'property' and added['field'] == 'health' and added['propertyOwner'] == f.n+'Monster'
    assert added['arguments'] == {'target': {'input': receiver}}
    scope['nodes'].append(added)
    next(node for node in scope['nodes'] if node['id'] == 'consume')['arguments']['value'] = {'node': read_id, 'output': 'return'}
    previous = 'other' if root else 'mark'
    scope['edges'] = [route for route in scope['edges'] if route['from'] != previous]
    scope['edges'].extend([edge(previous, read_id), edge(read_id, 'consume')])
    assert actual == expected
    assert all((f.project / name).read_bytes() == raw for name, raw in f.original.items() if name != graph_path.name)
    assert not errors, errors
    execute('confirmed', [70, 85] if menu else [10, 25])
    f.checked('Cold Save, Review cancellation and Confirm preserve unrelated sources. The compiled consumer receives the actual property value.')


f.author = lambda: f.page.locator('.window[data-key=blueprint]')
f.idle = lambda: expect(f.page.locator('.brand')).to_be_enabled(timeout=60000)
errors = []
try:
    graph = setup_project()
    f.original = {path.name: path.read_bytes() for path in f.project.iterdir() if path.is_file()}
    if not shared:
        execute('baseline', [1, 1])
    f.start(0)
    f.call('select', {'id': feature})
    f.call('saveDraft', {})
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    original_checkpoint = checkpoint.read_bytes()
    if not root:
        rejected_plans(original_checkpoint)
    with sync_playwright() as playwright:
        expect.set_options(timeout=30000)
        with playwright.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox']) as browser:
            run(browser, graph, original_checkpoint)
finally:
    f.stop()
    print('Evidence:', f.case)
