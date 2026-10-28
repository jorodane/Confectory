"""Explicit native C# text and a real Blueprint consumer; isolated fixture only."""
import copy
import json
import v536_information_function_contracts_native as n

f, d, owner, fn, caller, mode = n.f, n.a.d, n.owner, n.fn, n.caller, n.a.mode
old = {'args': [{'name': 'amount', 'type': 'long'}, {'name': 'count', 'type': 'long'}], 'return': 'long'}
new = {'args': [{'name': 'text', 'type': 'string'}, {'name': 'count', 'type': 'long'}], 'return': 'long'}
remap = {'amount': None, 'count': 'count'}
body_id = fn + 'Body/body:common'
body_path = 'manual-body.csbody'
original = 'return amount + count; // 원래 본문 · 9223372036854775806\r\n'
edited = 'return checked(text.Length + count); // 사용자가 직접 고친 본문 😀\r\n'
implementation = f.project / (fn.split('::')[1] + 'Body.celem')
implementation.write_text(implementation.read_text().replace('blueprint common "function.graph.json";', 'body common "' + body_path + '";'))
(f.project / body_path).write_bytes(original.encode())
snapshot = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}


def selections(preview):
    callers = {key: {k: row[k] for k in ['graph', 'node', 'hash']} | {'inputs': {'text': {'valueJson': '"직접 입력한 호출 인자"'}, 'count': 'count'}, 'disconnect': {'amount': row['bindings']['amount']}} for key, row in preview['functionInputs'].items()}
    row = preview['functionBodies'][body_id]
    body = {'hash': row['hash'], 'path': row['path'], 'beforeSignature': row['signature'], 'signature': new, 'contract': new, 'text': edited}
    return {'before': old, 'args': remap, 'callers': callers, 'bodies': {body_id: body}}


def request():
    r = n.request(new, remap)
    r['units'][body_id].update(draft=original, original=original, baseline=n.h(original))
    preview = {key: f.metadata(op, id=owner, function=fn, units=r['units']) for key, op in [('functionInputs', 'informationFunctionInputs'), ('functionBodies', 'informationFunctionBodies')]}
    r['changes'][0]['mapping'] = selections(preview)
    return r


def verify(checkpoint):
    rows = {r['id']: r for r in json.loads(checkpoint.read_text())['changes']}
    assert rows[body_id]['draft'] == edited
    assert n.canonical(f.metadata('inspect', text=rows[fn + 'Body']['draft'])['signature']) == new
    consumer = json.loads(rows[caller + 'Body/body:common']['draft'])
    assert consumer['nodes'][0]['signature'] == new
    assert consumer['nodes'][0]['arguments'] == {'text': {'constant': '직접 입력한 호출 인자'}, 'count': {'input': 'second'}}
    assert consumer['exits'] == n.g['exits']
    ids = rows[owner]['atomicEditGroup']
    assert {owner, fn, fn + 'Body', body_id, caller + 'Body', caller + 'Body/body:common'} <= set(ids)
    assert all((f.project / p).read_bytes() == b for p, b in snapshot.items())
    return ids
