"""Two explicit output-definition edits and their one real shared caller."""
import copy
import hashlib
import json
import v536_information_shared_callers_fixture as base

f, d, n, owner = base.f, base.d, base.n, base.owner
functions = base.functions
kind, _, phase = base.mode.partition('-')
mode = phase or 'normal'
old = {'args': [{'name': 'amount', 'type': 'long'}, {'name': 'real', 'type': 'double'},
                {'name': 'count', 'type': 'long', 'mode': 'out'}],
       'return': 'void' if kind == 'fromvoid' else 'long'}
new = copy.deepcopy(old)
if kind in ['mixed', 'delete']:
    new['args'].pop()
if kind in ['mixed', 'add']:
    new['args'].append({'name': 'fresh', 'type': 'long', 'mode': 'out'})
if kind == 'void':
    new['return'] = 'void'
if kind == 'fromvoid':
    new['return'] = 'string'
assert kind in ['mixed', 'delete', 'add', 'void', 'fromvoid']
nexts = [copy.deepcopy(new), copy.deepcopy(new)]
remap = {a['name']: None if a['name'] == 'count' and kind in ['mixed', 'delete'] else a['name'] for a in old['args']}
outs = lambda sig: ({'return': sig['return']} if sig['return'] != 'void' else {}) | {a['name']: a['type'] for a in sig['args'] if a.get('mode') == 'out'}
removed = [name for name in outs(old) if name not in outs(new)]
added = [name for name in outs(new) if name not in outs(old)]
published = list(outs(old))
literal = lambda name, index: json.dumps('한글 반환 ' + str(index) + ' 😀', ensure_ascii=False) if outs(new)[name] == 'string' else '23' if index == 0 else '9223372036854775806'
graphs, records = {}, {}
for index, fn in enumerate(functions):
    prefix = 'function' if index == 0 else 'second'
    source = 'function ' + fn + ' (long amount,double real,out long count) -> ' + old['return'] + ' {value editorName="' + ('첫째' if index == 0 else '둘째') + ' 공유 출력";value blueprintPublishedOutputs=' + json.dumps(json.dumps(published)) + ';}'
    prepared = f.metadata('blueprintPrepareFeature', id=fn, text=source, implementation=fn+'Body', graphPath=prefix+'.graph.json', nodePath=prefix+'.node.json')
    (f.project / ('elements/' + fn.split('::')[1] + '.celem')).write_text(prepared['function'])
    (f.project / (fn.split('::')[1] + 'Body.celem')).write_text(prepared['implementation'])
    graph = prepared['graph']
    if kind in ['mixed', 'delete']:
        writer = next(p for p in graph['nodes'] if p['kind'] == 'export' and p['output'] == 'count')
        second = copy.deepcopy(writer) | {'id': 'count_second'}
        graph['nodes'].append(second)
        edge = next((e for e in graph['edges'] if e['from'] == writer['id']), None)
        following = edge['to'] if edge else ''
        if edge:
            edge['to'] = second['id']
        else:
            graph['edges'].append({'from': writer['id'], 'port': 'next', 'to': second['id']})
        if following:
            graph['edges'].append({'from': second['id'], 'port': 'next', 'to': following})
    definitions = f.metadata('featureBlueprintNodes', featureSource=prepared['function'], graph=graph)
    records[fn] = prepared['node'] | {'definitionHash': next(r['definitionHash'] for r in definitions['nodes'] if r['id'] == 'body'),
        'source': 'count=checked(amount+' + str(index+1) + ');' + ('return;' if old['return'] == 'void' else 'return amount;') + ' // C# 원문 · 9223372036854775806'}
    graphs[fn] = graph
    (f.project / (prefix + '.graph.json')).write_text(json.dumps(graph))
    (f.project / (prefix + '.node.json')).write_text(json.dumps(records[fn]))
prepared = f.metadata('blueprintPrepareFeature', id=n.caller, text=n.caller_source, implementation=n.caller+'Body', graphPath='caller.graph.json', nodePath='unused.node.json')
graph = prepared['graph']
graph.update(profile='sync-acyclic-implicit-out-v1', nodes=[], entry='', edges=[], exits={'return': None})
header = prepared['implementation']
for fn, node in zip(functions, ['invoke', 'invoke_second']):
    selected = f.metadata('blueprintPrepareCall', id=n.caller+'Body', text=header, targetText=(f.project / ('elements/' + fn.split('::')[1] + '.celem')).read_text(), graph=graph,
                          definition={'id': node, 'feature': fn, 'intent': '원본 공유 출력 연결 · '+node, 'control': 'next'})
    header, graph = selected['implementation'], selected['graph']
consumed = 'return' if kind == 'void' else 'count'
binding = lambda node, output: {'node': node} | ({'output': output} if output != 'return' else {})
graph['nodes'][0]['arguments'] = {'amount': {'input': 'first'}, 'real': {'constant': 1.25}}
graph['nodes'][1]['arguments'] = {'amount': binding('invoke', consumed), 'real': {'constant': 2.5}}
graph.update(entry='invoke', edges=[{'from': 'invoke', 'port': 'next', 'to': 'invoke_second'}, {'from': 'invoke_second', 'port': 'next', 'to': 'exit:return'}], exits={'return': binding('invoke_second', consumed)})
(f.project/'Caller.celem').write_text(prepared['function'])
(f.project/'CallerBody.celem').write_text(header)
(f.project/'caller.graph.json').write_text(json.dumps(graph))
snapshot = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}
destination = 'fresh' if kind == 'mixed' else 'return' if kind == 'delete' else 'count'


def unchanged():
    assert all((f.project/path).read_bytes() == data for path, data in snapshot.items())


def selections(preview, index):
    output_map = {name: destination if name == consumed and name in removed else name for name in outs(old)}
    callers = {key: {k: row[k] for k in ['graph', 'node', 'hash']} | {'inputs': {'amount': 'amount', 'real': 'real'}, 'disconnect': {}, 'outputs': output_map} for key, row in preview['functionInputs'].items()}
    plans = {}
    for key, row in preview['functionOutputGraphs'].items():
        removes = [{'name': name, 'writers': row['writers'][name], 'before': row['exits'].get(name, 'null')} for name in removed]
        deleted = {node for r in removes for node in r['writers']}
        def resolve(target):
            while target in deleted:
                target = next((e['to'] for e in row['edges'] if e['from'] == target and e['port'] == 'next'), '')
            return '' if target.startswith('exit:') and target[5:] in removed else target
        next_node = resolve(next((e['to'] for e in row['edges'] if e['from'] == 'body' and e['port'] == 'next'), ''))
        creates = [{'node': 'created_'+name, 'name': name, 'type': outs(new)[name], 'source': {'valueJson': literal(name, index)}, 'after': 'body', 'next': next_node} for name in added]
        plans[key] = {'graph': key, 'hash': row['hash'], 'removes': removes, 'creates': creates, 'publicOutputs': [name for name in row['publicOutputs'] if name not in removed]}
    return {'before': copy.deepcopy(old), 'args': copy.deepcopy(remap), 'callers': callers, 'outputGraphs': plans}


def request():
    result = n.request(copy.deepcopy(new), copy.deepcopy(remap))
    fn = functions[1]
    result['changes'].append({'type': 'function-edit', 'id': fn, 'hash': hashlib.sha256(result['units'][fn]['draft'].encode()).hexdigest(), 'name': '둘째 공유 출력', 'description': '명시적 출력 정의와 본문 보존', 'signature': copy.deepcopy(new)})
    for index, row in enumerate(result['changes']):
        args = {k: result[k] for k in ['project', 'manifest', 'id', 'units']}
        row['mapping'] = selections({'functionInputs': f.metadata('informationFunctionInputs', **args, function=row['id']),
                                     'functionOutputGraphs': f.metadata('informationFunctionOutputGraphs', **args, function=row['id'])}, index)
    return result


def verify_rows(rows):
    shared = json.loads(rows[n.caller+'Body/body:common']['draft'])
    assert shared['edges'] == graph['edges'] and shared['entry'] == graph['entry']
    assert shared['nodes'][0]['arguments'] == graph['nodes'][0]['arguments']
    assert shared['nodes'][1]['arguments'] == {'amount': binding('invoke', destination), 'real': {'constant': 2.5}}
    assert shared['exits'] == {'return': binding('invoke_second', destination)}
    for index, fn in enumerate(functions):
        assert n.canonical(f.metadata('inspect', text=rows[fn]['draft'])['signature']) == new
        assert shared['nodes'][index]['signature'] == new
        assert shared['nodes'][index]['intent'] == graph['nodes'][index]['intent']
        leaf = json.loads(rows[fn+'Body/body:common']['draft'])
        assert next(r for r in leaf['nodes'] if r['kind'] == 'code')['signature'] == old
        for name in removed:
            assert not any(r['kind'] == 'export' and r['output'] == name for r in leaf['nodes'])
            assert leaf['exits'].get(name) is None
        for name in added:
            writer = next(r for r in leaf['nodes'] if r['kind'] == 'export' and r['output'] == name)
            assert writer['arguments']['value'] == {'constant': json.loads(literal(name, index))}
        assert json.loads(rows[fn+'Body/body:common/node:body']['draft'])['source'] == records[fn]['source']
        assert [p['name'] for p in f.metadata('blueprintOutputSnapshot', functionText=rows[fn]['draft'])['fields']] == [name for name in published if name not in removed]


def verify(checkpoint):
    rows = {r['id']: r for r in json.loads(checkpoint.read_text())['changes']}
    verify_rows(rows)
    unchanged()
    group = rows[owner]['atomicEditGroup']
    assert set(functions+[fn+'Body/body:common' for fn in functions]+[n.caller+'Body/body:common', owner]) <= set(group)
    return group


def verify_live():
    units = f.metadata('describe', project=str(f.manifest))['units']
    verify_rows({row['id']: {'draft': (f.project/row['path']).read_text()} for row in units})
