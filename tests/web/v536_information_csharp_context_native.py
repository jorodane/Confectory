"""All explicit C# targets and raw callers; no execution or source mutation."""
import copy
import json
import v536_information_csharp_fixture as x

f, fn, owner = x.f, x.fn, x.owner
impl = x.implementation
impl.write_text(impl.read_text().replace('}', 'body windows "manual-windows.csbody";}'))
(f.project / 'manual-windows.csbody').write_text('return amount + count; // Windows 원문')
caller_impl = f.project / 'CallerBody.celem'
caller_impl.write_text(caller_impl.read_text().replace('blueprint common "caller.graph.json";', 'body common "manual-caller.csbody";'))
(f.project / 'manual-caller.csbody').write_text('return calls.Target.Invoke(first,second); // 호출자 원문')
# Keep the existing import identity, changing only its local alias to a known
# explicit spelling for this isolated C# source.
text = caller_impl.read_text()
import re
text = re.sub(r'(import [^;]+ as )\w+( \()', r'\1Target\2', text)
caller_impl.write_text(text)
snapshot = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file()}


def request(signature=x.new, remap=x.remap):
    r = x.n.request(signature, remap)
    r['units'][x.body_id].update(draft=x.original, original=x.original, baseline=x.n.h(x.original))
    rows = f.metadata('informationFunctionBodies', id=owner, function=fn, units=r['units'])
    bodies = {}
    for id, row in rows.items():
        after = row['signature'] if row['caller'] else signature
        source = 'return calls.Target.Invoke("직접 고친 호출",second);' if row['caller'] else x.edited if signature == x.new else 'return amount + count; // 명시 순서 검토'
        bodies[id] = {k: row[k] for k in ['hash', 'path']} | {'beforeSignature': row['signature'], 'signature': after, 'contract': signature, 'text': source}
    r['changes'][0]['mapping'] = {'before': x.old, 'args': remap, 'callers': {}, 'bodies': bodies}
    return r


r = request()
prepared = x.n.prepare(r)
updates = {row['id']: row for row in prepared['linkedUpdates']}
expected = {x.body_id, fn + 'Body/body:windows', x.caller + 'Body/body:common'}
assert expected <= set(updates)
assert all(updates[id]['text'] == r['changes'][0]['mapping']['bodies'][id]['text'] for id in expected)
print('PASS C# 여러 target과 직접 쓴 호출자 본문/import를 같은 생성기·명시 후보로 검사하며 source를 재작성하지 않는다', flush=True)
for fault in ['missing-target', 'missing-caller', 'last-compile-error', 'different-header', 'shared-path']:
    bad = request()
    plans = bad['changes'][0]['mapping']['bodies']
    if fault == 'missing-target':
        del plans[fn + 'Body/body:windows']
    elif fault == 'missing-caller':
        del plans[x.caller + 'Body/body:common']
    elif fault == 'last-compile-error':
        plans[x.caller + 'Body/body:common']['text'] = 'return calls.Target.Invoke(first,second);'
    elif fault == 'different-header':
        plans[fn + 'Body/body:windows']['signature'] = copy.deepcopy(x.new)
        plans[fn + 'Body/body:windows']['signature']['args'][0]['name'] = 'otherName'
    else:
        bad['units']['Owned.Elements::Other/body:common'] = copy.deepcopy(bad['units'][x.body_id])
    x.n.prepare(bad, False)
    assert all((f.project / p).read_bytes() == b for p, b in snapshot.items())
print('PASS 마지막 C# 호출자 오류·target 누락·서명 불일치·공유 파일은 앞선 본문이나 선언도 적용하지 않는다', flush=True)
permuted = {'args': [x.old['args'][1], x.old['args'][0]], 'return': 'long'}
bad = request(permuted, {'amount': 'amount', 'count': 'count'})
del bad['changes'][0]['mapping']['bodies'][x.caller + 'Body/body:common']
x.n.prepare(bad, False)
assert all((f.project / p).read_bytes() == b for p, b in snapshot.items())
print('PASS 같은 타입의 public 핀 순서 변경도 직접 C# 호출자 확인 없이는 통과하지 않는다', flush=True)
# Explicit native C# formals can change roles only with all exact manual bodies.
roles = {'args': [{'name': 'text', 'type': 'string', 'mode': 'ref'}, {'name': 'count', 'type': 'long', 'mode': 'out'}], 'return': 'string'}
r = request()
r['changes'][0]['signature'] = roles
m = r['changes'][0]['mapping']
m['args'] = {'amount': None, 'count': None}
for id, plan in m['bodies'].items():
    plan['contract'] = roles
    if id.startswith(x.caller + 'Body/'):
        plan['text'] = 'string value="직접 입력"; long result; calls.Target.Invoke(ref value,out result); return result;'
    else:
        plan['signature'] = roles
        plan['text'] = 'count=text.Length; text += "수동"; return text;'
prepared = x.n.prepare(r)
assert {x.body_id, fn + 'Body/body:windows', x.caller + 'Body/body:common'} <= {row['id'] for row in prepared['linkedUpdates']}
assert all((f.project / p).read_bytes() == b for p, b in snapshot.items())
print('PASS 직접 편집한 native ref/out·반환 계약과 C# 호출자는 실제 형식/본문 검증을 함께 통과하고 원문을 보존한다', flush=True)
print(json.dumps({'checks': 4, 'pureCandidate': True, 'sourceWritten': False, 'executed': False, 'evidence': str(f.case)}, ensure_ascii=False))
