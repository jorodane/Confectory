"""Existing output identities with multiple assignments, typed sources and callers."""
import copy
import json
import re
import v536_information_output_types_fixture as x

n, f, d, owner, fn, caller, mode = x.n, x.f, x.d, x.owner, x.fn, x.caller, x.mode
kind = mode.split('-')[0]
typ = 'double' if kind == 'multiple' else 'string[]' if kind == 'array' else 'string'
old = {'args': [{'name': 'amount', 'type': 'long'}, {'name': 'real', 'type': 'double'}, {'name': 'caption', 'type': 'string'}, {'name': 'words', 'type': 'string[]'}, {'name': 'count', 'type': 'long', 'mode': 'out'}], 'return': 'long'}
if kind == 'fromarray':
    old['args'][4]['type'] = 'string[]'
    old['return'] = 'string[]'
new = copy.deepcopy(old)
new['args'][4]['type'] = typ
if kind == 'mixed':
    new['args'][4]['name'] = 'renamed'
    new['args'].append({'name': 'spare', 'type': 'long', 'mode': 'out'})
    new['return'] = 'bool'
remap = {a['name']: 'renamed' if kind == 'mixed' and a['name'] == 'count' else a['name'] for a in old['args']}
source = 'function ' + fn + ' (long amount,double real,string caption,string[] words,out ' + old['args'][4]['type'] + ' count) -> ' + old['return'] + ' {value blueprintPublishedOutputs="[\\"count\\",\\"return\\"]";}'
base = f.metadata('blueprintPrepareFeature', id=fn, text=source, implementation=fn + 'Body', graphPath='function.graph.json', nodePath='function.node.json')
function_file = f.project / ('elements/' + fn.split('::')[1] + '.celem')
function_file.write_text(base['function'].replace('provide ' + fn + ' with ' + fn + 'Body;', ''))
(f.project / (fn.split('::')[1] + 'Body.celem')).write_text(base['implementation'])
graph = base['graph']
graph['profile'] = 'sync-acyclic-alias-locals-v1'
writer = next(r for r in graph['nodes'] if r['kind'] == 'export' and r['output'] == 'count')
second = copy.deepcopy(writer)
second['id'] = 'second_count'
graph['nodes'].append(second)
edge = next((r for r in graph['edges'] if r['from'] == writer['id']), None)
following = edge['to'] if edge else ''
if edge:
    edge['to'] = second['id']
else:
    graph['edges'].append({'from': writer['id'], 'port': 'next', 'to': second['id']})
if following:
    graph['edges'].append({'from': second['id'], 'port': 'next', 'to': following})
graph['exits']['count'] = {'node': 'body', 'output': 'count'}
if kind == 'mixed':
    graph['exits']['return'] = {'node': 'body'}
provider_input = 'real' if typ == 'double' else 'words' if typ == 'string[]' else 'caption'
provider = {'id': 'provider', 'kind': 'code', 'control': 'next', 'intent': '이미 존재하는 타입 결과', 'signature': {'args': [{'name': provider_input, 'type': typ}], 'return': typ}, 'arguments': {provider_input: {'input': provider_input}}, 'implementation': 'provider.node.json'}
graph['nodes'].insert(0, provider)
graph['edges'].insert(0, {'from': 'provider', 'port': 'next', 'to': graph['entry']})
graph['entry'] = 'provider'
graph['locals'] = [{'id': 'kept_alias', 'name': '기존 결과 별칭', 'type': typ, 'source': {'node': 'provider'}}, {'id': 'precision', 'name': '기존 정확한 수치', 'type': 'long', 'initial': {'constant': 9223372036854775805}}]
defs = f.metadata('featureBlueprintNodes', featureSource=base['function'], graph=graph)
record = {**base['node'], 'definitionHash': next(r['definitionHash'] for r in defs['nodes'] if r['id'] == 'body'), 'source': ('count=words;return words;' if kind == 'fromarray' else 'count=amount+1;return amount+2;') + ' // 기존 구현 원문'}
provider_record = {'schema': 1, 'node': 'provider', 'definitionHash': next(r['definitionHash'] for r in defs['nodes'] if r['id'] == 'provider'), 'source': 'return ' + provider_input + '; // 기존 결과 원문'}
(f.project / 'function.graph.json').write_text(json.dumps(graph))
(f.project / 'function.node.json').write_text(json.dumps(record))
(f.project / 'provider.node.json').write_text(json.dumps(provider_record))
cp = f.metadata('blueprintPrepareFeature', id=caller, text=n.caller_source.replace('-> long', '-> string[]') if kind == 'fromarray' else n.caller_source, implementation=caller + 'Body', graphPath='caller.graph.json', nodePath='unused.node.json')
g = cp['graph']
g.update(profile='sync-acyclic-implicit-out-v1', nodes=[], entry='', edges=[], exits={'return': None})
cp2 = f.metadata('blueprintPrepareCall', id=caller + 'Body', text=cp['implementation'], targetText=function_file.read_text(), graph=g, definition={'id': 'invoke', 'feature': fn, 'intent': '원래 long 출력 실제 소비자', 'control': 'next'})
g = cp2['graph']
g.update(entry='invoke', edges=[{'from': 'invoke', 'port': 'next', 'to': 'exit:return'}], exits={'return': {'node': 'invoke', 'output': 'count'}})
g['nodes'][0]['arguments'] = {'amount': {'input': 'first'}, 'real': {'constant': 1.25}, 'caption': {'constant': '원래 입력'}, 'words': {'constant': ['가', '나']}}
(f.project / 'Caller.celem').write_text(cp['function'])
(f.project / 'CallerBody.celem').write_text(re.sub(r'(import [^;]+)(;)', r'\1 in ' + owner + r'\2', cp2['implementation']))
(f.project / 'caller.graph.json').write_text(json.dumps(g))
snapshot = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}
maps = {'return': 'spare' if kind == 'mixed' else 'return', 'count': 'spare' if kind == 'mixed' else 'return'}


def binding(name, node):
    if name == 'return':
        return {'valueJson': 'false' if node.startswith('$exit:') else 'true'}
    if node == writer['id']:
        return {'input': provider_input}
    if node == second['id']:
        return {'valueJson': '1.25' if typ == 'double' else '["한글", "배열 😀"]' if typ == 'string[]' else '"한글 새 값 😀"'}
    return {'node': 'provider'} if typ == 'double' else {'local': 'kept_alias'}


def selections(preview):
    callers = {key: {k: t[k] for k in ['graph', 'node', 'hash']} | {'inputs': {a['name']: a['name'] for a in old['args'] if a.get('mode') != 'out'}, 'disconnect': {}, 'outputs': copy.deepcopy(maps)} for key, t in preview['functionInputs'].items()}
    outputs = {key: {k: t[k] for k in ['graph', 'node', 'name', 'hash', 'before']} | {'type': new['return'] if t['name'] == 'return' else typ, 'source': binding(t['name'], t['node'])} for key, t in preview['functionOutputs'].items() if t['name'] == 'count' or kind == 'mixed' and t['name'] == 'return'}
    graphs = {}
    if kind == 'mixed':
        for key, t in preview['functionOutputGraphs'].items():
            following = next((e['to'] for e in t['edges'] if e['from'] == 'body' and e['port'] == 'next'), '')
            graphs[key] = {'graph': key, 'hash': t['hash'], 'removes': [], 'creates': [{'node': 'created_spare', 'name': 'spare', 'type': 'long', 'source': {'valueJson': '9223372036854775806'}, 'after': 'body', 'next': following}], 'publicOutputs': ['renamed', 'return']}
    return {'before': old, 'args': remap, 'callers': callers, 'outputs': outputs, **({'outputGraphs': graphs} if graphs else {})}


def verify(checkpoint):
    rows = {r['id']: r for r in json.loads(checkpoint.read_text())['changes']}
    producer = json.loads(rows[fn + 'Body/body:common']['draft'])
    consumer = json.loads(rows[caller + 'Body/body:common']['draft'])
    for node in [r for r in graph['nodes'] if r['kind'] == 'export']:
        actual = next(r for r in producer['nodes'] if r['id'] == node['id'])
        name = node['output']
        if name == 'return' and kind != 'mixed':
            assert actual == node
            continue
        chosen = binding(name, node['id'])
        expected = {'constant': json.loads(chosen['valueJson'])} if 'valueJson' in chosen else chosen
        assert actual['arguments']['value'] == expected and actual['signature']['args'][0]['type'] == ('bool' if name == 'return' else typ)
        assert actual['output'] == ('renamed' if name == 'count' and kind == 'mixed' else name)
    for name in ['count'] + (['return'] if kind == 'mixed' else []):
        chosen = binding(name, '$exit:' + name)
        expected = {'constant': json.loads(chosen['valueJson'])} if 'valueJson' in chosen else chosen
        assert producer['exits']['renamed' if name == 'count' and kind == 'mixed' else name] == expected
    assert producer['locals'] == graph['locals']
    for node in [r for r in graph['nodes'] if r['kind'] == 'code']:
        assert next(r for r in producer['nodes'] if r['id'] == node['id']) == node
    for name, source_record in [('body', record), ('provider', provider_record)]:
        assert json.loads(rows[fn + 'Body/body:common/node:' + name]['draft'])['source'] == source_record['source']
    assert consumer['nodes'][0]['signature'] == new and consumer['nodes'][0]['arguments'] == g['nodes'][0]['arguments']
    assert consumer['exits']['return'] == {'node': 'invoke', **({'output': 'spare'} if kind == 'mixed' else {})}
    if kind == 'mixed':
        assert next(r for r in producer['nodes'] if r['id'].startswith('output_') or r['id'] == 'created_spare')['arguments']['value'] == {'constant': 9223372036854775806}
    else:
        assert producer['edges'] == graph['edges'] and producer['entry'] == graph['entry']
    publication = f.metadata('blueprintOutputSnapshot', functionText=rows[fn]['draft'])
    assert [p['name'] for p in publication['fields']] == ['renamed' if kind == 'mixed' else 'count', 'return']
    ids = rows[owner]['atomicEditGroup']
    assert {owner, fn, fn + 'Body', fn + 'Body/body:common', caller + 'Body', caller + 'Body/body:common'} <= set(ids)
    return ids
