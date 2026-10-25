"""One owned declaration, Blueprint + explicit C# targets and mixed callers."""
import copy
import json
import re
import v536_information_function_contracts_native as n

f, d, owner, fn, caller, mode = n.f, n.a.d, n.owner, n.fn, n.caller, n.a.mode
old = {'args': [{'name': 'amount', 'type': 'long'}, {'name': 'count', 'type': 'long'}], 'return': 'long'}
new = {'args': [{'name': 'text', 'type': 'string'}, {'name': 'count', 'type': 'long'}], 'return': 'long'}
remap = {'amount': None, 'count': 'count'}
body_id, body_path = fn + 'Body/body:windows', 'mixed-windows.csbody'
original = 'return amount+count; // 원래 Windows 본문 · 9223372036854775806\n'
edited = 'return checked(text.Length+count); // 직접 고친 Windows 본문 😀\r\n'
implementation = f.project / (fn.split('::')[1] + 'Body.celem')
implementation.write_text(implementation.read_text().replace('}', 'body windows "' + body_path + '";}'))
(f.project / body_path).write_bytes(original.encode())
caller_implementation = f.project / 'CallerBody.celem'
alias = re.search(r'\bas (\w+)\s*\(', caller_implementation.read_text()).group(1)
caller_implementation.write_text(caller_implementation.read_text().replace('}', 'body windows "mixed-caller-windows.csbody";}'))
(f.project / 'mixed-caller-windows.csbody').write_text('return calls.' + alias + '.Invoke(first,second); // 원래 호출자')
# Real Windows compilation can select the other target, with no project Run.
f.manifest.write_text(f.manifest.read_text().replace('target linux ', 'target windows Confectory.Build.DotNet::Portable;target linux '))
snapshot = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}
edited_files = {body_path: edited, 'mixed-caller-windows.csbody': 'return calls.' + alias + '.Invoke("직접 입력한 호출 인자",second); // 직접 고친 호출자\r\n'}
context_bodies = {body_id: body_path, caller + 'Body/body:windows': 'mixed-caller-windows.csbody'}
# Match the real information-owned provider, not a global function default.
function_file = f.project / ('elements/' + fn.split('::')[1] + '.celem')
function_file.write_text(function_file.read_text().replace('provide ' + fn + ' with ' + fn + 'Body;', ''))
info = f.project / 'FreeInfo.celem'
info.write_text(info.read_text().replace('{', '{provide ' + fn + ' with ' + fn + 'Body;', 1))
caller_implementation.write_text(re.sub(r'(import [^;]+ -> long)(;)', r'\1 in ' + owner + r'\2', caller_implementation.read_text()))
snapshot = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}
updated_files = {'function.graph.json', 'function.node.json'}
body_picker = True
mixed_target = True


def selections(preview):
    callers = {key: {k: row[k] for k in ['graph', 'node', 'hash']} | {'inputs': {'text': {'valueJson': '"직접 입력한 호출 인자"'}, 'count': 'count'}, 'disconnect': {'amount': row['bindings']['amount']}} for key, row in preview['functionInputs'].items()}
    uses = {key: {k: row[k] for k in ['graph', 'node', 'argument', 'hash', 'before']} | {'value': {'input': 'count'}} for key, row in preview['functionInputUses'].items() if 'amount' in row.get('inputs', [row['input']])}
    bodies = {id: {k: row[k] for k in ['hash', 'path']} | {'beforeSignature': row['signature'], 'signature': row['signature'] if row['caller'] else new, 'contract': new, 'text': edited_files[row['path']]} for id, row in preview['functionBodies'].items() if row.get('sourceKind') != 'blueprint'}
    return {'before': old, 'args': remap, 'callers': callers, 'implementations': uses, 'bodies': bodies}


def request():
    r = n.request(new, remap)
    preview = {key: f.metadata(op, id=owner, function=fn, units=r['units']) for key, op in [('functionInputs', 'informationFunctionInputs'), ('functionInputUses', 'informationFunctionInputUses'), ('functionBodies', 'informationFunctionBodies')]}
    r['changes'][0]['mapping'] = selections(preview)
    return r


def verify(checkpoint):
    rows = {r['id']: r for r in json.loads(checkpoint.read_text())['changes']}
    for id, path in context_bodies.items():
        assert rows[id]['draft'] == edited_files[path]
    assert n.canonical(f.metadata('inspect', text=rows[fn + 'Body']['draft'])['signature']) == new
    graph = json.loads(rows[fn + 'Body/body:common']['draft'])
    node = next(r for r in graph['nodes'] if r['id'] == 'body')
    assert node['arguments'] == {'amount': {'input': 'count'}, 'count': {'input': 'count'}}
    record = json.loads(rows[fn + 'Body/body:common/node:body']['draft'])
    assert record['source'] == n.record['source'] and node['signature'] == n.base['graph']['nodes'][0]['signature']
    consumer = json.loads(rows[caller + 'Body/body:common']['draft'])
    assert consumer['nodes'][0]['signature'] == new
    assert consumer['nodes'][0]['arguments'] == {'text': {'constant': '직접 입력한 호출 인자'}, 'count': {'input': 'second'}}
    assert consumer['exits'] == n.g['exits']
    ids = rows[owner]['atomicEditGroup']
    assert {owner, fn, fn + 'Body', fn + 'Body/body:common', fn + 'Body/body:common/node:body', caller + 'Body', caller + 'Body/body:common', *context_bodies} <= set(ids)
    assert all((f.project / p).read_bytes() == b for p, b in snapshot.items())
    return ids
