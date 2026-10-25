"""Two explicit input/output type edits, including a soon-disconnected producer."""
import copy
import hashlib
import json
import v536_information_shared_output_types_fixture as base

f, d, n, owner, mode = base.f, base.d, base.n, base.owner, base.mode
functions, old = base.functions, base.old
graphs, records, graph, snapshot = base.graphs, base.records, base.graph, base.snapshot
nexts = copy.deepcopy(base.nexts)
for signature in nexts:
    signature['args'][0]['type'] = 'string'
new, removed, added = nexts[0], [], []
text_value = '명시한 새 입력 😀'
replacement = '9223372036854775800'
binding = lambda node, output: {'node': node} | ({'output': output} if output != 'return' else {})
destination = 'return'
unchanged = base.unchanged


def selections(preview):
    callers = {key: {k: row[k] for k in ['graph', 'node', 'hash']} |
        {'inputs': {'amount': {'valueJson': json.dumps(text_value, ensure_ascii=False)}, 'real': 'real'},
         'disconnect': {'amount': row['bindings']['amount']},
         'outputs': {'count': 'return', 'return': 'return'}} for key, row in preview['functionInputs'].items()}
    outputs = {key: {k: row[k] for k in ['graph', 'node', 'name', 'hash', 'before']} |
        {'type': 'double', 'source': {'input': 'real'}} for key, row in preview['functionOutputs'].items() if row['name'] == 'count'}
    uses = {key: {k: row[k] for k in ['graph', 'node', 'argument', 'hash', 'before']} |
        {'value': {'valueJson': replacement}} for key, row in preview['functionInputUses'].items() if row['input'] == 'amount'}
    return {'before': copy.deepcopy(old), 'args': {'amount': None, 'real': 'real', 'count': 'count'},
            'callers': callers, 'outputs': outputs, 'implementations': uses}


def request():
    result = n.request(nexts[0], {'amount': None, 'real': 'real', 'count': 'count'})
    fn = functions[1]
    result['changes'].append({'type': 'function-edit', 'id': fn,
        'hash': hashlib.sha256(result['units'][fn]['draft'].encode()).hexdigest(),
        'name': '둘째 입력·출력', 'description': '본문과 명시 연결 보존', 'signature': copy.deepcopy(nexts[1])})
    for row in result['changes']:
        args = {k: result[k] for k in ['project', 'manifest', 'id', 'units']}
        row['mapping'] = selections({name: f.metadata(op, **args, function=row['id']) for name, op in [
            ('functionInputs', 'informationFunctionInputs'), ('functionInputUses', 'informationFunctionInputUses'),
            ('functionOutputs', 'informationFunctionOutputs')]})
    return result


def caller_arguments(index):
    return {'amount': {'constant': text_value}, 'real': graph['nodes'][index]['arguments']['real']}


def caller_exits():
    return {'return': {'node': 'invoke_second'}}


def verify_rows(rows):
    caller = json.loads(rows[n.caller+'Body/body:common']['draft'])
    assert caller['edges'] == graph['edges'] and caller['entry'] == graph['entry'] and caller['exits'] == caller_exits()
    for index, (fn, signature) in enumerate(zip(functions, nexts)):
        assert n.canonical(f.metadata('inspect', text=rows[fn]['draft'])['signature']) == signature
        assert caller['nodes'][index]['signature'] == signature and caller['nodes'][index]['arguments'] == caller_arguments(index)
        assert caller['nodes'][index]['intent'] == graph['nodes'][index]['intent']
        leaf = json.loads(rows[fn+'Body/body:common']['draft'])
        assert leaf['edges'] == graphs[fn]['edges'] and leaf['entry'] == graphs[fn]['entry']
        assert {row['id'] for row in leaf['nodes']} == {row['id'] for row in graphs[fn]['nodes']}
        code = next(row for row in leaf['nodes'] if row['kind'] == 'code')
        assert code['signature'] == old and code['arguments'] == {'amount': {'constant': int(replacement)}, 'real': {'input': 'real'}}
        assert json.loads(rows[fn+'Body/body:common/node:body']['draft'])['source'] == records[fn]['source']
        count = next(row for row in leaf['nodes'] if row['kind'] == 'export' and row['output'] == 'count')
        assert count['arguments'] == {'value': {'input': 'real'}} and count['signature']['args'][0]['type'] == 'double'
        returned = next(row for row in leaf['nodes'] if row['kind'] == 'export' and row['output'] == 'return')
        assert returned == next(row for row in graphs[fn]['nodes'] if row['kind'] == 'export' and row['output'] == 'return')
        assert f.metadata('blueprintOutputSnapshot', functionText=rows[fn]['draft'])['fields'][0]['type'] == 'double'


def verify(checkpoint):
    rows = {row['id']: row for row in json.loads(checkpoint.read_text())['changes']}
    verify_rows(rows)
    unchanged()
    group = rows[owner]['atomicEditGroup']
    assert set(functions+[fn+'Body/body:common' for fn in functions]+[n.caller+'Body', n.caller+'Body/body:common', owner]) <= set(group)
    return group


def verify_live():
    units = f.metadata('describe', project=str(f.manifest))['units']
    verify_rows({row['id']: {'draft': (f.project/row['path']).read_text()} for row in units})
