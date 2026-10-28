"""Explicit output definitions/routes and real consumers in an owned fixture."""
import copy
import json
import re
import v536_information_output_types_fixture as x

n, f, d, owner, fn, caller, mode = x.n, x.f, x.d, x.owner, x.fn, x.caller, x.mode
kind = mode.split('-')[0]
old = copy.deepcopy(x.old)
if kind == 'fromvoid':
    old['return'] = 'void'
new = copy.deepcopy(old)
if kind in ['delete', 'mixed']:
    new['args'] = [a for a in new['args'] if a['name'] != 'count']
if kind == 'void':
    new['return'] = 'void'
if kind == 'fromvoid':
    new['return'] = 'string'
if kind in ['add', 'mixed', 'many']:
    new['args'].append({'name': 'fresh', 'type': 'string' if kind == 'mixed' else 'long', 'mode': 'out'})
if kind == 'many':
    new['args'].append({'name': 'flag', 'type': 'bool', 'mode': 'out'})
remap = {a['name']: None if a['name'] == 'count' and kind in ['delete', 'mixed'] else a['name'] for a in old['args']}
published = ['count'] + ([] if old['return'] == 'void' else ['return'])
source = 'function ' + fn + ' (long amount,double real,out long count) -> ' + old['return'] + ' {value blueprintPublishedOutputs=' + json.dumps(json.dumps(published)) + ';}'
base = f.metadata('blueprintPrepareFeature', id=fn, text=source, implementation=fn + 'Body', graphPath='function.graph.json', nodePath='function.node.json')
function_file = f.project / ('elements/' + fn.split('::')[1] + '.celem')
function_file.write_text(base['function'].replace('provide ' + fn + ' with ' + fn + 'Body;', ''))
(f.project / (fn.split('::')[1] + 'Body.celem')).write_text(base['implementation'])
graph = base['graph']
if kind == 'delete':
    # The original definition can have several assignments. Deleting the
    # definition acknowledges and removes all assignments, not its C# producer.
    original_writer = next(r for r in graph['nodes'] if r['kind'] == 'export' and r['output'] == 'count')
    second = copy.deepcopy(original_writer)
    second['id'] = 'count_second'
    graph['nodes'].append(second)
    edge = next((r for r in graph['edges'] if r['from'] == original_writer['id']), None)
    following = edge['to'] if edge else ''
    if edge:
        edge['to'] = second['id']
    else:
        graph['edges'].append({'from': original_writer['id'], 'port': 'next', 'to': second['id']})
    if following:
        graph['edges'].append({'from': second['id'], 'port': 'next', 'to': following})
defs = f.metadata('featureBlueprintNodes', featureSource=base['function'], graph=graph)
record = {**base['node'], 'definitionHash': next(r['definitionHash'] for r in defs['nodes'] if r['id'] == 'body'), 'source': 'count=amount+1;' + ('return;' if old['return'] == 'void' else 'return amount+2;') + ' // C#·기존 출력 원문 보존'}
(f.project / 'function.graph.json').write_text(json.dumps(graph))
(f.project / 'function.node.json').write_text(json.dumps(record))
cp = f.metadata('blueprintPrepareFeature', id=caller, text=n.caller_source, implementation=caller + 'Body', graphPath='caller.graph.json', nodePath='unused.node.json')
g = cp['graph']
g.update(profile='sync-acyclic-implicit-out-v1', nodes=[], entry='', edges=[], exits={'return': None})
cp2 = f.metadata('blueprintPrepareCall', id=caller + 'Body', text=cp['implementation'], targetText=function_file.read_text(), graph=g, definition={'id': 'invoke', 'feature': fn, 'intent': '실제 출력 소비자', 'control': 'next'})
g = cp2['graph']
consumed = 'return' if kind == 'void' else 'count'
g.update(entry='invoke', edges=[{'from': 'invoke', 'port': 'next', 'to': 'exit:return'}], exits={'return': {'node': 'invoke', **({'output': consumed} if consumed != 'return' else {})}})
g['nodes'][0]['arguments'] = {'amount': {'input': 'first'}, 'real': {'constant': 1.25}}
(f.project / 'Caller.celem').write_text(cp['function'])
(f.project / 'CallerBody.celem').write_text(re.sub(r'(import [^;]+)(;)', r'\1 in ' + owner + r'\2', cp2['implementation']))
(f.project / 'caller.graph.json').write_text(json.dumps(g))
snapshot = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}
outs = lambda sig: ({'return': sig['return']} if sig['return'] != 'void' else {}) | {a['name']: a['type'] for a in sig['args'] if a.get('mode') == 'out'}
removed = [name for name in outs(old) if name not in outs(new)]
added = [name for name in outs(new) if name not in outs(old)]
literal = lambda name: '"한글 새 반환·출력 😀"' if name in ['return', 'fresh'] and outs(new)[name] == 'string' else 'true' if name == 'flag' else '9223372036854775806'


def selections(preview):
    maps = {name: 'return' if name == 'count' and kind in ['delete', 'mixed'] else 'count' if name == 'return' and kind == 'void' else name for name in outs(old)}
    callers = {key: {k: t[k] for k in ['graph', 'node', 'hash']} | {'inputs': {'amount': 'amount', 'real': 'real'}, 'disconnect': {}, 'outputs': maps} for key, t in preview['functionInputs'].items()}
    graphs = {}
    for key, t in preview['functionOutputGraphs'].items():
        removes = [{'name': name, 'writers': t['writers'][name], 'before': t['exits'].get(name, 'null')} for name in removed]
        deleted = {node for row in removes for node in row['writers']}
        def resolve(target):
            while target in deleted:
                target = next((e['to'] for e in t['edges'] if e['from'] == target and e['port'] == 'next'), '')
            return '' if target.startswith('exit:') and target[5:] in removed else target
        flow = {node['id']: resolve(next((e['to'] for e in t['edges'] if e['from'] == node['id'] and e['port'] == 'next'), '')) for node in t['nodes'] if node['id'] not in deleted}
        creates = []
        previous = 'body'
        for name in added:
            node = 'created_' + name
            following = flow[previous]
            creates.append({'node': node, 'name': name, 'type': outs(new)[name], 'source': {'valueJson': literal(name)}, 'after': previous, 'next': following})
            flow[previous] = node
            flow[node] = following
            previous = node
        graphs[key] = {'graph': key, 'hash': t['hash'], 'removes': removes, 'creates': creates, 'publicOutputs': [name for name in t['publicOutputs'] if name in outs(new)]}
    return {'before': old, 'args': remap, 'callers': callers, 'outputGraphs': graphs}


def verify(checkpoint):
    rows = {r['id']: r for r in json.loads(checkpoint.read_text())['changes']}
    producer = json.loads(rows[fn + 'Body/body:common']['draft'])
    consumer = json.loads(rows[caller + 'Body/body:common']['draft'])
    assert next(r for r in producer['nodes'] if r['kind'] == 'code')['signature'] == old
    assert json.loads(rows[fn + 'Body/body:common/node:body']['draft'])['source'] == record['source']
    for name in removed:
        assert not any(r.get('output') == name and r['kind'] == 'export' for r in producer['nodes'])
        assert producer['exits'].get(name) is None
    for name in added:
        writer = next(r for r in producer['nodes'] if r['kind'] == 'export' and r['output'] == name)
        assert writer['arguments']['value'] == {'constant': json.loads(literal(name))}
    assert consumer['nodes'][0]['signature'] == new and consumer['nodes'][0]['arguments'] == g['nodes'][0]['arguments']
    expected_output = 'return' if kind in ['delete', 'mixed'] else 'count'
    assert consumer['exits']['return'] == {'node': 'invoke', **({'output': expected_output} if expected_output != 'return' else {})}
    publication = f.metadata('blueprintOutputSnapshot', functionText=rows[fn]['draft'])
    assert [r['name'] for r in publication['fields']] == [name for name in published if name not in removed]
    # Every retained original node stays in the original relative execution order.
    def order(g):
        result = []
        at = g['entry']
        while at in {r['id'] for r in g['nodes']}:
            assert at not in result
            result.append(at)
            at = next((e['to'] for e in g['edges'] if e['from'] == at and e['port'] == 'next'), '')
        return result
    kept = [r['id'] for r in graph['nodes'] if not (r['kind'] == 'export' and r['output'] in removed)]
    assert [node for node in order(producer) if node in kept] == [node for node in order(graph) if node in kept]
    ids = rows[owner]['atomicEditGroup']
    assert {owner, fn, fn + 'Body', fn + 'Body/body:common', caller + 'Body', caller + 'Body/body:common'} <= set(ids)
    return ids
