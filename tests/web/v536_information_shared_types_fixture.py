"""Two independent leaf contracts, explicitly rebound through one shared caller."""
import copy
import json
import v536_information_shared_callers_fixture as base

f, d, n, owner, mode = base.f, base.d, base.n, base.owner, base.mode
functions, old, snapshot = base.functions, base.old, base.snapshot
unchanged = base.unchanged
nexts = [copy.deepcopy(old), copy.deepcopy(old)]
for signature in nexts:
    signature['args'][0]['type'] = 'string'

def selections(preview):
    return {'before': copy.deepcopy(old), 'args': {'amount': None, 'count': 'count'},
        'callers': {key: {k: row[k] for k in ['graph', 'node', 'hash']} | {
            'inputs': {'amount': {'valueJson': json.dumps('새 한글 값', ensure_ascii=False)}, 'count': 'count'},
            'disconnect': {'amount': row['bindings']['amount']}}
            for key, row in preview['functionInputs'].items()},
        'implementations': {key: {k: row[k] for k in ['graph', 'node', 'argument', 'hash', 'before']} | {
            'value': {'input': 'count'}} for key, row in preview['functionInputUses'].items() if row['input'] == 'amount'}}

def request():
    result = base.request()
    for row, signature in zip(result['changes'], nexts):
        row['signature'] = copy.deepcopy(signature)
        inputs = f.metadata('informationFunctionInputs', **{k: result[k] for k in ['project', 'manifest', 'id', 'units']}, function=row['id'])
        uses = f.metadata('informationFunctionInputUses', **{k: result[k] for k in ['project', 'manifest', 'id', 'units']}, function=row['id'])
        row['mapping'] = selections({'functionInputs': inputs, 'functionInputUses': uses})
    return result

def verify_rows(rows):
    caller = json.loads(rows[n.caller+'Body/body:common']['draft'])
    for node, signature in zip(caller['nodes'], nexts):
        assert node['signature'] == signature
        assert node['arguments'] == {'amount': {'constant': '새 한글 값'}, 'count': {'input': 'second'}}
    original = json.loads(snapshot['caller.graph.json'])
    assert caller['edges'] == original['edges'] and caller['exits'] == original['exits']
    for fn, signature, path, record in zip(functions, nexts, ['function.graph.json', 'second.graph.json'], ['function.node.json', 'second.node.json']):
        assert n.canonical(f.metadata('inspect', text=rows[fn]['draft'])['signature']) == signature
        graph = json.loads(rows[fn+'Body/body:common']['draft'])
        node = next(row for row in graph['nodes'] if row['id'] == 'body')
        assert node['signature'] == old and node['arguments'] == {'amount': {'input': 'count'}, 'count': {'input': 'count'}}
        assert json.loads(rows[fn+'Body/body:common/node:body']['draft'])['source'] == json.loads(snapshot[record])['source']

def verify(checkpoint):
    rows = {row['id']: row for row in json.loads(checkpoint.read_text())['changes']}
    verify_rows(rows)
    group = rows[owner]['atomicEditGroup']
    assert set(functions+[fn+'Body/body:common' for fn in functions]+[n.caller+'Body/body:common', owner]) <= set(group)
    unchanged()
    return group
