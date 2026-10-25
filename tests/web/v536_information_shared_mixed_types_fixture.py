"""Input-only and out-only edits through one caller, with original proofs."""
import copy
import json
import v536_information_shared_io_fixture as base

f, d, n, owner, mode = base.f, base.d, base.n, base.owner, base.mode
functions, old = base.functions, base.old
graphs, records, graph, snapshot = base.graphs, base.records, base.graph, base.snapshot
text_value, replacement, binding = base.text_value, base.replacement, base.binding
removed, added, destination = [], [], 'return'
unchanged = base.unchanged
nexts = [copy.deepcopy(old), copy.deepcopy(old)]
nexts[0]['args'][0]['type'] = 'string'
nexts[1]['args'][2]['type'] = 'double'
new = nexts[0]


def request():
    result = base.request()
    for index, row in enumerate(result['changes']):
        row['signature'] = copy.deepcopy(nexts[index])
        mapping = row['mapping']
        if index == 0:
            mapping.pop('outputs')
            for caller in mapping['callers'].values():
                caller.pop('outputs')
        else:
            mapping.pop('implementations')
            mapping['args']['amount'] = 'amount'
            for caller in mapping['callers'].values():
                caller['inputs']['amount'] = 'amount'
                caller['disconnect'] = {}
    return result


def caller_arguments(index, signatures=None):
    signatures = signatures or nexts
    result = copy.deepcopy(graph['nodes'][index]['arguments'])
    if signatures[index]['args'][0]['type'] == 'string':
        result['amount'] = {'constant': text_value}
    elif index == 1 and signatures[0]['args'][2]['type'] == 'double':
        result['amount'] = {'node': 'invoke'}
    return result


def caller_exits():
    return {'return': {'node': 'invoke_second'}}


def verify_rows(rows, signatures=None):
    signatures = signatures or nexts
    caller = json.loads(rows[n.caller+'Body/body:common']['draft'])
    assert caller['edges'] == graph['edges'] and caller['entry'] == graph['entry']
    assert caller['exits'] == caller_exits()
    for index, (fn, signature) in enumerate(zip(functions, signatures)):
        assert n.canonical(f.metadata('inspect', text=rows[fn]['draft'])['signature']) == signature
        assert caller['nodes'][index]['signature'] == signature
        assert caller['nodes'][index]['arguments'] == caller_arguments(index, signatures)
        assert caller['nodes'][index]['intent'] == graph['nodes'][index]['intent']
        leaf = json.loads(rows[fn+'Body/body:common']['draft'])
        assert leaf['edges'] == graphs[fn]['edges'] and leaf['entry'] == graphs[fn]['entry']
        assert {row['id'] for row in leaf['nodes']} == {row['id'] for row in graphs[fn]['nodes']}
        code = next(row for row in leaf['nodes'] if row['kind'] == 'code')
        assert code['signature'] == old
        assert code['arguments'] == {'amount': {'constant': int(replacement)} if signature['args'][0]['type'] == 'string' else {'input': 'amount'}, 'real': {'input': 'real'}}
        assert json.loads(rows[fn+'Body/body:common/node:body']['draft'])['source'] == records[fn]['source']
        writer = next(row for row in leaf['nodes'] if row['kind'] == 'export' and row['output'] == 'count')
        if signature['args'][2]['type'] == 'long':
            assert writer == next(row for row in graphs[fn]['nodes'] if row['kind'] == 'export' and row['output'] == 'count')
        else:
            assert writer['arguments'] == {'value': {'input': 'real'}} and writer['signature']['args'][0]['type'] == 'double'
        assert next(row for row in leaf['nodes'] if row['kind'] == 'export' and row['output'] == 'return') == next(row for row in graphs[fn]['nodes'] if row['kind'] == 'export' and row['output'] == 'return')
        assert f.metadata('blueprintOutputSnapshot', functionText=rows[fn]['draft'])['fields'][0]['type'] == signature['args'][2]['type']


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
