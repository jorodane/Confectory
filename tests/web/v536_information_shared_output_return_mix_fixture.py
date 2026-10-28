"""Original writers and explicit consumers for mixed out/return type edits."""
import copy
import hashlib
import json
import v536_information_shared_outputs_fixture as base

f, d, n, owner, mode = base.f, base.d, base.n, base.owner, base.mode
functions = base.functions
joint = mode.startswith('joint')
old = {'args': [{'name': 'amount', 'type': 'long'}, {'name': 'real', 'type': 'double'},
                {'name': 'count', 'type': 'long', 'mode': 'out'},
                {'name': 'stable', 'type': 'long', 'mode': 'out'}], 'return': 'long'}
nexts = [copy.deepcopy(old), copy.deepcopy(old)]
nexts[0]['return'] = 'double'
nexts[1]['args'][2]['type'] = 'double'
if joint:
    nexts[0]['args'][2]['type'] = 'double'
    nexts[1]['return'] = 'double'
new = nexts[0]
removed, added, destination = [], [], 'stable'
binding = lambda node, output: {'node': node} | ({'output': output} if output != 'return' else {})
graphs, records = {}, {}
for index, fn in enumerate(functions):
    prefix = 'function' if index == 0 else 'second'
    source = ('function ' + fn + ' (long amount,double real,out long count,out long stable) -> long {'
              'value editorName="' + ('첫째' if index == 0 else '둘째') + ' 공유 출력";'
              'value blueprintPublishedOutputs="[\\"count\\",\\"stable\\",\\"return\\"]";}')
    prepared = f.metadata('blueprintPrepareFeature', id=fn, text=source, implementation=fn+'Body',
                          graphPath=prefix+'.graph.json', nodePath=prefix+'.node.json')
    (f.project/('elements/'+fn.split('::')[1]+'.celem')).write_text(prepared['function'])
    (f.project/(fn.split('::')[1]+'Body.celem')).write_text(prepared['implementation'])
    graphs[fn] = prepared['graph']
    definitions = f.metadata('featureBlueprintNodes', featureSource=prepared['function'], graph=prepared['graph'])
    records[fn] = prepared['node'] | {
        'definitionHash': next(r['definitionHash'] for r in definitions['nodes'] if r['id'] == 'body'),
        'source': 'count=checked(amount+'+str(index+1)+');stable=amount;return amount; // 원문 · 9223372036854775806'}
    (f.project/(prefix+'.graph.json')).write_text(json.dumps(graphs[fn]))
    (f.project/(prefix+'.node.json')).write_text(json.dumps(records[fn]))
prepared = f.metadata('blueprintPrepareFeature', id=n.caller, text=n.caller_source,
                      implementation=n.caller+'Body', graphPath='caller.graph.json', nodePath='unused.node.json')
graph = prepared['graph']
graph.update(profile='sync-acyclic-implicit-out-v1', nodes=[], entry='', edges=[], exits={'return': None})
header = prepared['implementation']
for fn, node in zip(functions, ['invoke', 'invoke_second']):
    linked = f.metadata('blueprintPrepareCall', id=n.caller+'Body', text=header,
                        targetText=(f.project/('elements/'+fn.split('::')[1]+'.celem')).read_text(),
                        graph=graph, definition={'id': node, 'feature': fn, 'intent': 'return/count 보존 · '+node, 'control': 'next'})
    header, graph = linked['implementation'], linked['graph']
graph['nodes'][0]['arguments'] = {'amount': {'input': 'first'}, 'real': {'constant': 1.25}}
graph['nodes'][1]['arguments'] = {'amount': {'node': 'invoke'}, 'real': {'constant': 2.5}}
graph.update(entry='invoke', edges=[{'from': 'invoke', 'port': 'next', 'to': 'invoke_second'},
             {'from': 'invoke_second', 'port': 'next', 'to': 'exit:return'}],
             exits={'return': {'node': 'invoke_second', 'output': 'count'}})
(f.project/'Caller.celem').write_text(prepared['function'])
(f.project/'CallerBody.celem').write_text(header)
(f.project/'caller.graph.json').write_text(json.dumps(graph))
snapshot = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*')
            if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}


def unchanged():
    assert all((f.project/path).read_bytes() == raw for path, raw in snapshot.items())


def selections(result, fn, signature):
    args = {k: result[k] for k in ['project', 'manifest', 'id', 'units']}
    preview = f.metadata('informationFunctionInputs', **args, function=fn)
    writers = f.metadata('informationFunctionOutputs', **args, function=fn)
    changed = {a['name']: a['type'] for a in signature['args'] if a.get('mode') == 'out' and a['type'] != 'long'}
    if signature['return'] != old['return']:
        changed['return'] = signature['return']
    outputs = {key: {k: row[k] for k in ['graph', 'node', 'name', 'hash', 'before']} |
               {'type': changed[row['name']], 'source': {'input': 'real'}}
               for key, row in writers.items() if row['name'] in changed}
    callers = {key: {k: row[k] for k in ['graph', 'node', 'hash']} |
               {'inputs': {'amount': 'amount', 'real': 'real'}, 'disconnect': {},
                'outputs': {name: 'stable' if name in changed else name for name in ['count', 'stable', 'return']}}
               for key, row in preview.items()}
    return {'before': copy.deepcopy(old), 'args': {a['name']: a['name'] for a in old['args']},
            'outputs': outputs, 'callers': callers}


def request():
    result = n.request(nexts[0], {a['name']: a['name'] for a in old['args']})
    fn = functions[1]
    result['changes'].append({'type': 'function-edit', 'id': fn,
        'hash': hashlib.sha256(result['units'][fn]['draft'].encode()).hexdigest(),
        'name': '둘째 공유 출력', 'description': '원래 writer/명시 소비와 원문 보존', 'signature': copy.deepcopy(nexts[1])})
    for row, signature in zip(result['changes'], nexts):
        row['mapping'] = selections(result, row['id'], signature)
    return result


def caller_arguments(index):
    return (copy.deepcopy(graph['nodes'][0]['arguments']) if index == 0 else
            {'amount': binding('invoke', 'stable'), 'real': {'constant': 2.5}})


def caller_exits():
    return {'return': binding('invoke_second', 'stable')}


def verify_rows(rows):
    merged = {r['id']: r for r in f.metadata('describe', project=str(f.manifest))['units']}
    merged = {key: {'draft': (f.project/row['path']).read_text()} for key, row in merged.items()} | rows
    shared = json.loads(merged[n.caller+'Body/body:common']['draft'])
    assert shared['edges'] == graph['edges'] and shared['entry'] == graph['entry']
    assert shared['exits'] == caller_exits()
    for index, (fn, signature) in enumerate(zip(functions, nexts)):
        assert n.canonical(f.metadata('inspect', text=merged[fn]['draft'])['signature']) == signature
        assert shared['nodes'][index]['signature'] == signature
        assert shared['nodes'][index]['arguments'] == caller_arguments(index)
        assert shared['nodes'][index]['intent'] == graph['nodes'][index]['intent']
        leaf = json.loads(merged[fn+'Body/body:common']['draft'])
        assert leaf['edges'] == graphs[fn]['edges'] and leaf['entry'] == graphs[fn]['entry']
        assert {r['id'] for r in leaf['nodes']} == {r['id'] for r in graphs[fn]['nodes']}
        code = next(r for r in leaf['nodes'] if r['kind'] == 'code')
        assert code['signature'] == old and code['arguments'] == {'amount': {'input': 'amount'}, 'real': {'input': 'real'}}
        assert json.loads(merged[fn+'Body/body:common/node:body']['draft'])['source'] == records[fn]['source']
        for name in ['count', 'stable', 'return']:
            typ = signature['return'] if name == 'return' else next(a['type'] for a in signature['args'] if a['name'] == name)
            writer = next(r for r in leaf['nodes'] if r['kind'] == 'export' and r['output'] == name)
            if typ == 'long':
                assert writer == next(r for r in graphs[fn]['nodes'] if r['kind'] == 'export' and r['output'] == name)
            else:
                assert typ == 'double' and writer['arguments'] == {'value': {'input': 'real'}}
                assert writer['signature']['args'][0]['type'] == typ
        fields = f.metadata('blueprintOutputSnapshot', functionText=merged[fn]['draft'])['fields']
        assert [(r['name'], r['type']) for r in fields] == [('count', signature['args'][2]['type']), ('stable', 'long'), ('return', signature['return'])]


def verify(checkpoint):
    rows = {r['id']: r for r in json.loads(checkpoint.read_text())['changes']}
    verify_rows(rows); unchanged()
    group = rows[owner]['atomicEditGroup']
    assert set(functions+[fn+'Body/body:common' for fn in functions]+[n.caller+'Body', n.caller+'Body/body:common', owner]) <= set(group)
    return group


def verify_live():
    units = f.metadata('describe', project=str(f.manifest))['units']
    verify_rows({r['id']: {'draft': (f.project/r['path']).read_text()} for r in units})


def edit_contract(popover, index):
    for name, before, after in [('arg2', old['args'][2]['type'], nexts[index]['args'][2]['type']),
                                ('return', old['return'], nexts[index]['return'])]:
        if before != after:
            popover.locator('[data-signature-id='+name+'] [data-signature-type]').click()
            f.page.get_by_role('dialog', name='속성 타입 선택', exact=True).locator('[data-type='+after+']').click()


def remap_title(index):
    return '호출 계약 갱신'


def select_contract(dialog, index):
    for target in dialog.locator('[data-abi-target^="output:"]').all():
        target.locator('[data-abi-input=value]').select_option('pin:real')
    for name, typ in [('count', nexts[index]['args'][2]['type']), ('return', nexts[index]['return'])]:
        if typ != 'long':
            dialog.locator('[data-abi-output='+name+']').select_option('stable')


def verify_pins(panel, index):
    from playwright.sync_api import expect
    for name, typ in [('count', nexts[index]['args'][2]['type']), ('stable', 'long'), ('return', nexts[index]['return'])]:
        label = '결과' if name == 'return' else name
        expect(panel.locator('[data-inline-method="'+functions[index]+'"] [data-pin-side=outputs] [data-function-pin-name="'+label+'"]')).to_have_attribute('data-function-pin-type', '실수' if typ == 'double' else '정수')
