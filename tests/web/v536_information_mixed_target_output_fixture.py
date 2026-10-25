"""Mixed sources coordinate an explicitly written C# out/void body and BP writers."""
import copy
import json
import v536_information_mixed_target_fixture as base
from v536_information_mixed_target_fixture import *

new = copy.deepcopy(base.new)
new['args'].append({'name': 'result', 'type': 'long', 'mode': 'out'})
new['return'] = 'void'
edited = 'result=checked(text.Length+count);return; // 직접 쓴 out/void 본문\r\n'
edited_files = {body_path: edited, 'mixed-caller-windows.csbody': 'calls.' + alias + '.Invoke("직접 입력한 호출 인자",second,out long result);return result; // 직접 쓴 호출자\r\n'}
mixed_output = True


def selections(preview):
    m = base.selections(preview)
    for id, plan in m['bodies'].items():
        plan['contract'] = new
        plan['text'] = edited_files[plan['path']]
        if id == body_id:
            plan['signature'] = new
    for plan in m['callers'].values():
        plan['outputs'] = {'return': 'result'}
    m['outputGraphs'] = {id: {'graph': id, 'hash': row['hash'], 'removes': [{'name': 'return', 'writers': row['writers']['return'], 'before': row['exits']['return']}], 'creates': [{'node': 'explicit_result', 'name': 'result', 'type': 'long', 'source': {'input': 'count'}, 'after': 'body', 'next': ''}], 'publicOutputs': []} for id, row in preview['functionOutputGraphs'].items()}
    return m


def verify(checkpoint):
    rows = {r['id']: r for r in json.loads(checkpoint.read_text())['changes']}
    for id, path in context_bodies.items():
        assert rows[id]['draft'] == edited_files[path]
    assert n.canonical(f.metadata('inspect', text=rows[fn + 'Body']['draft'])['signature']) == new
    graph = json.loads(rows[fn + 'Body/body:common']['draft'])
    assert next(row for row in graph['nodes'] if row['id'] == 'explicit_result')['arguments']['value'] == {'input': 'count'}
    assert not any(row['kind'] == 'export' and row['output'] == 'return' for row in graph['nodes'])
    assert json.loads(rows[fn + 'Body/body:common/node:body']['draft'])['source'] == n.record['source']
    consumer = json.loads(rows[caller + 'Body/body:common']['draft'])
    assert consumer['nodes'][0]['signature'] == new
    assert consumer['exits']['return'] == {'node': 'invoke', 'output': 'result'}
    ids = rows[owner]['atomicEditGroup']
    assert {owner, fn, fn + 'Body', fn + 'Body/body:common', fn + 'Body/body:common/node:body', caller + 'Body', caller + 'Body/body:common', *context_bodies} <= set(ids)
    assert all((f.project / p).read_bytes() == b for p, b in snapshot.items())
    return ids
