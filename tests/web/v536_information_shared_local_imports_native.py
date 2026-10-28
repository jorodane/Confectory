"""Stable local imports compose; selected/cross-pack dependencies never slip in."""
import copy
import hashlib
import json
import v536_information_shared_local_imports_fixture as x

r = x.request()
held = copy.deepcopy(r)
result = x.n.prepare(r)
assert r == held
updates = result['updates'] + result['linkedUpdates']
rows = {row['id']: {'draft': row['text']} for row in updates}
x.verify_rows(rows)
assert len(rows) == len(updates)
assert all(row['hash'] == hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest() for row in updates)
assert not any(row['id'].startswith(x.stable) for row in updates)
observation = next(row for row in result['observations'] if row['path'] == str(x.f.project / 'StableHelper.celem'))
assert observation['hash'] == hashlib.sha256(x.stable_source.encode()).hexdigest()
x.unchanged()
x.f.checked('미선택 로컬 계약은 읽기 관측이며 두 C# import·별도 호출·명시 출력 대응을 원래 hash 후보에 보존한다')
reverse = copy.deepcopy(r)
reverse['changes'].reverse()
other = x.n.prepare(reverse)
assert {row['id']: row['text'] for row in updates} == {row['id']: row['text'] for row in other['updates'] + other['linkedUpdates']}
x.f.checked('두 편집 순서를 뒤집어도 미선택 호출 입력과 C# 원문·실행 순서가 같은 최종 후보를 만든다')
for fault in ['missing', 'external', 'stale-import', 'selected-dependency', 'changed-call', 'invalid-last-writer']:
    bad = copy.deepcopy(r)
    if fault == 'missing':
        del bad['units'][x.stable]
    elif fault == 'external':
        for fn in x.functions:
            unit = bad['units'][fn+'Body']
            unit['draft'] = unit['draft'].replace(x.stable, 'External.Pack::StableHelper')
    elif fault == 'stale-import':
        unit = bad['units'][x.functions[1]+'Body']
        unit['draft'] = unit['draft'].replace('(long) -> long;', '(string) -> long;')
    elif fault == 'selected-dependency':
        unit = bad['units'][x.functions[1]+'Body']
        unit['draft'] = unit['draft'].replace('{', '{import '+x.functions[0]+' as Other (long,double,out long) -> long;', 1)
    elif fault == 'changed-call':
        unit = bad['units'][x.n.caller+'Body/body:common']
        graph = json.loads(unit['draft'])
        graph['nodes'][-1]['arguments'] = {'value': {'constant': 9223372036854775806}}
        unit['draft'] = json.dumps(graph)
    else:
        next(iter(bad['changes'][1]['mapping']['outputs'].values()))['source'] = {'input': 'amount'}
    x.n.prepare(bad, False)
    x.unchanged()
x.f.checked('외부/누락/낡은 import·선택 callee 교차 의존·고정 호출 변경·마지막 writer 오류는 전체 미적용이다')
path = x.f.project / 'StableHelper.celem'
original = path.read_bytes()
try:
    path.write_text(x.stable_source.replace('long value', 'string value'))
    x.n.prepare(r, False)
    assert all((x.f.project/p).read_bytes() == raw for p, raw in x.snapshot.items() if p != 'StableHelper.celem')
finally:
    path.write_bytes(original)
x.unchanged()
x.f.checked('후보 조회 뒤 미선택 로컬 계약의 실제 변경도 원래 관측으로 거절하고 모든 원문을 보존한다')
print(json.dumps({'checks': x.f.checks, 'evidence': str(x.f.case), 'copyPolicyUsed': False, 'actualWindows': False}, ensure_ascii=False))
