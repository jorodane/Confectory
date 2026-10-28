"""Original return consumers, explicit writers, unchanged arguments and C#."""
import copy
import hashlib
import json
import re
import v536_information_shared_output_types_fixture as base

f, d, n, owner, mode = base.f, base.d, base.n, base.owner, base.mode
functions, old = base.functions, base.old
nexts = [copy.deepcopy(old), copy.deepcopy(old)]
for signature in nexts:
    signature['return'] = 'double'
new = nexts[0]
removed, added = [], []
graphs, records = base.graphs, base.records
for index, fn in enumerate(functions):
    path = f.project / ('elements/' + fn.split('::')[1] + '.celem')
    text, count = re.subn(r'value blueprintPublishedOutputs\s*=\s*"(?:\\.|[^"\\])*"\s*;',
                          lambda _: 'value blueprintPublishedOutputs=' + json.dumps(json.dumps(['count', 'return'])) + ';', path.read_text())
    assert count == 1
    path.write_text(text)
    definitions = f.metadata('featureBlueprintNodes', featureSource=text, graph=graphs[fn])
    records[fn]['definitionHash'] = next(r['definitionHash'] for r in definitions['nodes'] if r['id'] == 'body')
    (f.project / ('function.node.json' if index == 0 else 'second.node.json')).write_text(json.dumps(records[fn]))
graph = copy.deepcopy(base.graph)
graph['nodes'][1]['arguments']['amount'] = {'node': 'invoke'}
graph['exits']['return'] = {'node': 'invoke_second'}
(f.project / 'caller.graph.json').write_text(json.dumps(graph))
snapshot = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}
destination = 'count'
binding = lambda node, output: {'node': node} | ({'output': output} if output != 'return' else {})


def unchanged():
    assert all((f.project/path).read_bytes() == raw for path, raw in snapshot.items())


def selections(preview):
    callers = {key: {k: row[k] for k in ['graph', 'node', 'hash']} |
               {'inputs': {'amount': 'amount', 'real': 'real'}, 'disconnect': {},
                'outputs': {'count': 'count', 'return': 'count'}} for key, row in preview['functionInputs'].items()}
    outputs = {key: {k: row[k] for k in ['graph', 'node', 'name', 'hash', 'before']} |
               {'type': 'double', 'source': {'input': 'real'}} for key, row in preview['functionOutputs'].items() if row['name'] == 'return'}
    return {'before': copy.deepcopy(old), 'args': {a['name']: a['name'] for a in old['args']}, 'callers': callers, 'outputs': outputs}


def request():
    result = n.request(nexts[0], {a['name']: a['name'] for a in old['args']})
    fn = functions[1]
    result['changes'].append({'type': 'function-edit', 'id': fn,
        'hash': hashlib.sha256(result['units'][fn]['draft'].encode()).hexdigest(),
        'name': '둘째 공유 반환', 'description': '원문과 명시 반환 대응 보존', 'signature': copy.deepcopy(nexts[1])})
    for row in result['changes']:
        args = {k: result[k] for k in ['project', 'manifest', 'id', 'units']}
        row['mapping'] = selections({'functionInputs': f.metadata('informationFunctionInputs', **args, function=row['id']),
                                     'functionOutputs': f.metadata('informationFunctionOutputs', **args, function=row['id'])})
    return result


def verify_rows(rows):
    shared = json.loads(rows[n.caller+'Body/body:common']['draft'])
    assert shared['edges'] == graph['edges'] and shared['entry'] == graph['entry']
    assert shared['nodes'][0]['arguments'] == graph['nodes'][0]['arguments']
    assert shared['nodes'][1]['arguments'] == {'amount': binding('invoke', destination), 'real': {'constant': 2.5}}
    assert shared['exits'] == {'return': binding('invoke_second', destination)}
    for index, (fn, signature) in enumerate(zip(functions, nexts)):
        assert n.canonical(f.metadata('inspect', text=rows[fn]['draft'])['signature']) == signature
        assert shared['nodes'][index]['signature'] == signature and shared['nodes'][index]['intent'] == graph['nodes'][index]['intent']
        leaf = json.loads(rows[fn+'Body/body:common']['draft'])
        assert leaf['edges'] == graphs[fn]['edges']
        code = next(r for r in leaf['nodes'] if r['kind'] == 'code')
        assert code['signature'] == old and code['arguments'] == {'amount': {'input': 'amount'}, 'real': {'input': 'real'}}
        writer = next(r for r in leaf['nodes'] if r['kind'] == 'export' and r['output'] == 'return')
        assert writer['arguments'] == {'value': {'input': 'real'}} and writer['signature']['args'][0]['type'] == 'double'
        count = next(r for r in leaf['nodes'] if r['kind'] == 'export' and r['output'] == 'count')
        assert count['arguments'] == {'value': {'node': 'body', 'output': 'count'}}
        assert {r['id'] for r in leaf['nodes']} == {r['id'] for r in graphs[fn]['nodes']}
        assert json.loads(rows[fn+'Body/body:common/node:body']['draft'])['source'] == records[fn]['source']
        fields = f.metadata('blueprintOutputSnapshot', functionText=rows[fn]['draft'])['fields']
        assert [(r['name'], r['type']) for r in fields] == [('count', 'long'), ('return', 'double')]


def verify(checkpoint):
    rows = {r['id']: r for r in json.loads(checkpoint.read_text())['changes']}
    verify_rows(rows)
    unchanged()
    group = rows[owner]['atomicEditGroup']
    assert set(functions+[fn+'Body/body:common' for fn in functions]+[n.caller+'Body', n.caller+'Body/body:common', owner]) <= set(group)
    return group


def verify_live():
    units = f.metadata('describe', project=str(f.manifest))['units']
    verify_rows({r['id']: {'draft': (f.project/r['path']).read_text()} for r in units})
