"""Interdependent input/output contracts, only isolated project/engine fixtures."""
import copy
import json
import v536_information_output_remap_fixture as x

f, d, n, owner, fn, caller, mode = x.f, x.d, x.n, x.owner, x.fn, x.caller, x.mode
kind = mode.split('-')[0]
assert kind in ['rename', 'combined', 'remove', 'same', 'swap'], kind
old = copy.deepcopy(x.old)
new = copy.deepcopy(old)
remap = {a['name']: a['name'] for a in old['args']}
if kind == 'rename':
    new['args'][0]['name'] = 'amount2'
    new['args'][2]['name'] = 'text'
    remap.update(amount='amount2', caption='text')
elif kind == 'swap':
    new['args'][0]['name'], new['args'][1]['name'] = 'real', 'amount'
    remap.update(amount='real', real='amount')
else:
    remap['amount'] = None
    if kind == 'remove':
        new['args'].pop(0)
        new['args'] = [a for a in new['args'] if a['name'] != 'count']
        remap['count'] = None
    else:
        new['args'][0]['type'] = 'string'
    # The original form appends a newly created input after existing pin IDs;
    # visual input/output grouping does not reorder that native signature list.
    new['args'].append({'name': 'fresh', 'type': 'long'})
    if kind != 'same':
        next(a for a in new['args'] if a['name'] == 'caption')['name'] = 'text'
        remap['caption'] = 'text'
typ = 'long' if kind == 'same' else 'double' if kind == 'swap' else 'string'
if kind != 'remove':
    out = next(a for a in new['args'] if a['name'] == 'count')
    out.update(name='count2', type=typ)
    remap['count'] = 'count2'
if kind != 'same':
    new['args'].append({'name': 'added', 'type': typ, 'mode': 'out'})

# All output bindings deliberately read an input which is also renamed or
# removed. An unchanged exit and a live alias require ordinary input restoration.
graph = copy.deepcopy(x.graph)
for node in graph['nodes']:
    if node['kind'] == 'export' and node['output'] == 'count':
        node['arguments']['value'] = {'input': 'amount'}
graph['exits'].update(count={'input': 'amount'}, **{'return': {'input': 'amount'}})
graph['locals'].append({'id': 'root_alias', 'name': '보존할 입력 저장소', 'type': 'long', 'source': {'input': 'amount'}})
if kind == 'swap':
    graph['locals'].append({'id': 'typed_alias', 'name': '실수 저장소', 'type': 'double', 'source': {'input': 'real'}})
source_file = f.project / ('elements/' + fn.split('::')[1] + '.celem')
defs = f.metadata('featureBlueprintNodes', featureSource=source_file.read_text(), graph=graph)
for node in graph['nodes']:
    if node['kind'] == 'code':
        path = f.project / node['implementation']
        value = json.loads(path.read_text())
        value['definitionHash'] = next(r['definitionHash'] for r in defs['nodes'] if r['id'] == node['id'])
        path.write_text(json.dumps(value))
(f.project / 'function.graph.json').write_text(json.dumps(graph))
snapshot = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}
record = json.loads((f.project / 'function.node.json').read_text())
maps = {'return': 'return', 'count': 'count2' if kind == 'same' else 'return'}


def output_binding(row):
    if kind == 'swap':
        return {'local': 'typed_alias'} if row['node'].startswith('$exit:') else {'input': 'amount'}
    if kind == 'combined':
        return {'local': 'kept_alias'} if row['node'].startswith('$exit:') else {'input': 'amount' if row['node'] == x.writer['id'] else 'text'}
    return {'input': 'text'}


def replaced(preview):
    return {r['graph'] + '#' + r['node'] + '#value' for r in preview['functionOutputs'].values() if r['name'] == 'count' and kind != 'same'}


def input_binding(row):
    return {'input': 'fresh'}


def selections(preview):
    callers = {}
    for key, row in preview['functionInputs'].items():
        inputs = {}
        for arg in new['args']:
            if arg.get('mode') == 'out':
                continue
            if arg['name'] == 'fresh':
                inputs[arg['name']] = 'amount'
            elif arg['name'] == 'amount' and kind in ['combined', 'same']:
                inputs[arg['name']] = {'valueJson': '"명시한 새 문자열 😀"'}
            else:
                inputs[arg['name']] = next(a['name'] for a in old['args'] if remap[a['name']] == arg['name'])
        callers[key] = {k: row[k] for k in ['graph', 'node', 'hash']} | {'inputs': inputs, 'disconnect': {}, 'outputs': copy.deepcopy(maps)}
    outputs = {key: {k: row[k] for k in ['graph', 'node', 'name', 'hash', 'before']} | {'type': typ, 'source': output_binding(row)} for key, row in preview['functionOutputs'].items() if row['name'] == 'count' and kind not in ['same', 'remove']}
    skip = replaced(preview)
    uses = {key: {k: row[k] for k in ['graph', 'node', 'argument', 'hash', 'before']} | {'value': input_binding(row)} for key, row in preview['functionInputUses'].items() if key not in skip and any(remap[name] is None for name in row.get('inputs', [row['input']]))}
    graphs = {}
    if kind != 'same':
        for key, row in preview['functionOutputGraphs'].items():
            following = next((e['to'] for e in row['edges'] if e['from'] == 'body' and e['port'] == 'next'), '')
            if kind == 'remove':
                while following in row['writers']['count']:
                    following = next((e['to'] for e in row['edges'] if e['from'] == following and e['port'] == 'next'), '')
            graphs[key] = {'graph': key, 'hash': row['hash'], 'removes': [{'name': 'count', 'writers': row['writers']['count'], 'before': row['exits']['count']}] if kind == 'remove' else [], 'creates': [{'node': 'created_added', 'name': 'added', 'type': typ, 'source': {'input': 'amount' if kind in ['combined', 'swap'] else 'text'}, 'after': 'body', 'next': following}], 'publicOutputs': ['return'] if kind == 'remove' else ['count2', 'return']}
    return {'before': old, 'args': remap, 'callers': callers, 'implementations': uses, **({'outputs': outputs} if outputs else {}), **({'outputGraphs': graphs} if graphs else {})}


def verify(checkpoint):
    rows = {r['id']: r for r in json.loads(checkpoint.read_text())['changes']}
    actual = json.loads(rows[fn + 'Body/body:common']['draft'])
    by_id = {r['id']: r for r in actual['nodes']}
    for before in graph['nodes']:
        if before['kind'] == 'export' and before['output'] == 'count' and kind == 'remove':
            assert before['id'] not in by_id
            continue
        node = by_id[before['id']]
        if before['kind'] == 'code':
            assert node['signature'] == before['signature']
            assert node['arguments'] == {k: {'input': 'fresh'} if v == {'input': 'amount'} and remap['amount'] is None else {'input': remap[v['input']]} for k, v in before['arguments'].items()}
            path = before['implementation']
            assert json.loads(rows[fn + 'Body/body:common/node:' + before['id']]['draft'])['source'] == json.loads(snapshot[path])['source']
        elif before['output'] == 'count':
            assert node['output'] == 'count2' and node['signature']['args'][0]['type'] == typ
            assert node['arguments']['value'] == ({'input': 'fresh'} if kind == 'same' else output_binding({'node': before['id']}))
    expected_exits = {'return': {'input': remap['amount'] or 'fresh'}}
    if kind != 'remove':
        expected_exits['count2'] = {'input': 'fresh'} if kind == 'same' else output_binding({'node': '$exit:count'})
    else:
        assert 'count' not in actual['exits']
    for key, value in expected_exits.items():
        assert actual['exits'][key] == value, (key, actual['exits'])
    assert actual['locals'] == [{**row, **({'source': {'input': remap[row['source']['input']] or 'fresh'}} if row.get('source', {}).get('input') else {})} for row in graph['locals']]
    if kind != 'same':
        added = next(row for row in actual['nodes'] if row['kind'] == 'export' and row['output'] == 'added')
        assert added['arguments']['value'] == {'input': 'amount' if kind in ['combined', 'swap'] else 'text'}
    consumer = json.loads(rows[caller + 'Body/body:common']['draft'])
    call = consumer['nodes'][0]
    assert call['signature'] == new
    for arg in new['args']:
        if arg.get('mode') == 'out':
            continue
        if arg['name'] == 'amount' and kind in ['combined', 'same']:
            assert call['arguments'][arg['name']] == {'constant': '명시한 새 문자열 😀'}
        else:
            old_name = 'amount' if arg['name'] == 'fresh' else next(a['name'] for a in old['args'] if remap[a['name']] == arg['name'])
            assert call['arguments'][arg['name']] == x.g['nodes'][0]['arguments'][old_name]
    assert consumer['exits']['return'] == {'node': 'invoke', **({'output': 'count2'} if kind == 'same' else {})}
    pub = f.metadata('blueprintOutputSnapshot', functionText=rows[fn]['draft'])
    assert [r['name'] for r in pub['fields']] == (['return'] if kind == 'remove' else ['count2', 'return'])
    ids = rows[owner]['atomicEditGroup']
    assert {owner, fn, fn + 'Body', fn + 'Body/body:common', caller + 'Body', caller + 'Body/body:common'} <= set(ids)
    return ids
