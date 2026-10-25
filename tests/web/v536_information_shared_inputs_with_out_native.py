"""Unchanged output contracts are observations, not permission to rebind."""
import copy
import hashlib
import json
import v536_information_shared_inputs_with_out_fixture as x

r = x.request()
for row in r['changes']:
    single = copy.deepcopy(r); single['changes'] = [row]
    x.n.prepare(single)
x.unchanged()
x.f.checked('out을 유지한 입력 타입 편집 두 개는 각각 원래 단일 closure로 유효하다')
if x.mode.endswith('reproduce'):
    x.n.prepare(r, False); x.unchanged()
    x.f.checked('기존 그룹 가드는 유효한 입력-only 선택을 함께 저장하지 못한다: '+x.mode)
else:
    result = x.n.prepare(r); updates = result['updates']+result['linkedUpdates']
    (x.f.case/'prepared-candidate.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    x.verify_rows({row['id']: {'draft': row['text']} for row in updates})
    assert len({row['id'] for row in updates}) == len(updates)
    assert all(row['hash'] == hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest() for row in updates)
    reverse = copy.deepcopy(r); reverse['changes'].reverse(); other = x.n.prepare(reverse)
    assert {row['id']: row['text'] for row in updates} == {row['id']: row['text'] for row in other['updates']+other['linkedUpdates']}
    x.unchanged()
    x.f.checked('단일 후보·역순·원래 hash는 두 입력 대체와 정확64비트·기존 out writer/공개/최종 소비 연결을 보존한다')
    for fault in ['missing-use', 'bad-use', 'disconnect', 'extra-output', 'extra-writer', 'role', 'count', 'order', 'return', 'source']:
        bad = copy.deepcopy(r); row = bad['changes'][1]; mapping = row['mapping']
        if fault == 'missing-use': mapping.pop('implementations')
        elif fault == 'bad-use': next(iter(mapping['implementations'].values()))['value'] = {'valueJson': '"not long"'}
        elif fault == 'disconnect': next(iter(mapping['callers'].values()))['disconnect']['amount'] = '{"node":"invoke"}'
        elif fault == 'extra-output': next(iter(mapping['callers'].values()))['outputs'] = {'count': 'return', 'return': 'return'}
        elif fault == 'extra-writer': mapping['outputs'] = {}
        elif fault == 'role': row['signature']['args'][2]['mode'] = 'ref'
        elif fault == 'count': row['signature']['args'].append({'name': 'extra', 'type': 'long'})
        elif fault == 'order': row['signature']['args'].reverse()
        elif fault == 'return': row['signature']['return'] = 'double'
        else:
            unit = bad['units'][x.n.caller+'Body/body:common']; graph = json.loads(unit['draft']); graph['exits']['return'] = {'node': 'invoke'}; unit['draft'] = json.dumps(graph)
        x.n.prepare(bad, False); x.unchanged()
    x.f.checked('추가 출력 선택·잘못된 사용처/해제·역할/수/순서/반환·원래 caller 변경은 전체 미적용이다')
    path = x.f.project/'caller.graph.json'; held = path.read_bytes()
    try:
        peer = json.loads(held); peer['nodes'][0]['intent'] = '다른 편집자 원문'; path.write_text(json.dumps(peer)); x.n.prepare(r, False)
        assert all((x.f.project/p).read_bytes() == raw for p, raw in x.snapshot.items() if p != 'caller.graph.json')
    finally:
        path.write_bytes(held)
    x.unchanged()
    x.f.checked('실제 물리 source 경합은 내부 합성과 구별해 입력과 기존 원문을 보존하며 거절한다')
print(json.dumps({'checks': x.f.checks, 'evidence': str(x.f.case), 'copyPolicyUsed': False, 'actualWindows': False}, ensure_ascii=False))
