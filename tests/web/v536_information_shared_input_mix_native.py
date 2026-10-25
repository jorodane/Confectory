"""Existing single closures prove mixed input definitions/types before overlay."""
import copy
import hashlib
import json
import v536_information_shared_input_mix_fixture as x

r = x.request()
for row in r['changes']:
    single = copy.deepcopy(r); single['changes'] = [row]; x.n.prepare(single)
x.unchanged(); x.f.checked('입력 정의/타입 혼합의 원래 단일 후보는 각각 유효하다')
if x.mode.endswith('reproduce'):
    x.n.prepare(r, False); x.unchanged(); x.f.checked('기존 그룹 가드는 원래 유효한 입력 정의와 타입 혼합을 함께 저장하지 못한다')
else:
    result = x.n.prepare(r); updates = result['updates']+result['linkedUpdates']
    (x.f.case/'prepared-candidate.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    x.verify_rows({row['id']: {'draft': row['text']} for row in updates})
    assert len({row['id'] for row in updates}) == len(updates)
    assert all(row['hash'] == hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest() for row in updates)
    reverse = copy.deepcopy(r); reverse['changes'].reverse(); other = x.n.prepare(reverse)
    assert {row['id']: row['text'] for row in updates} == {row['id']: row['text'] for row in other['updates']+other['linkedUpdates']}
    x.unchanged(); x.f.checked('원래 hash·한 후보·역순은 명시 새 값/기존 값 재사용과 out/return/정확64비트/C# 원문을 보존한다')
    for fault in ['missing-use', 'bad-use', 'missing-value', 'disconnect', 'extra-output', 'order', 'role', 'return', 'out-type', 'body', 'source']:
        bad = copy.deepcopy(r); typed = bad['changes'][0 if x.joint else 1]; mapping = typed['mapping']; caller = next(iter(mapping['callers'].values()))
        if fault == 'missing-use': mapping.pop('implementations')
        elif fault == 'bad-use': next(iter(mapping['implementations'].values()))['value'] = {'input': 'real'}
        elif fault == 'missing-value': caller['inputs'].pop('amount')
        elif fault == 'disconnect': caller['disconnect'] = {'amount': json.dumps(x.graph['nodes'][0]['arguments']['amount'],separators=(',',':'))} if x.joint else {}
        elif fault == 'extra-output': caller['outputs'] = {'count':'return','return':'return'}
        elif fault == 'order': typed['signature']['args'][0],typed['signature']['args'][1] = typed['signature']['args'][1],typed['signature']['args'][0]
        elif fault == 'role': typed['signature']['args'][0]['mode'] = 'ref'
        elif fault == 'return': typed['signature']['return'] = 'double'
        elif fault == 'out-type': next(a for a in typed['signature']['args'] if a.get('mode')=='out')['type'] = 'double'
        elif fault == 'body': mapping['bodies'] = {}
        else:
            unit = bad['units'][x.n.caller+'Body/body:common']; graph = json.loads(unit['draft']); graph['nodes'][1]['intent']='실제 선택 변경'; unit['draft']=json.dumps(graph)
        x.n.prepare(bad, False); x.unchanged()
    x.f.checked('사용처/값/해제 증거 누락·타입 오류·출력/순서/역할/반환/본문·선택 변경은 전체 미적용이다')
    path=x.f.project/'caller.graph.json'; held=path.read_bytes()
    try:
        peer=json.loads(held);peer['nodes'][0]['intent']='peer 물리 변경';path.write_text(json.dumps(peer));x.n.prepare(r,False)
        assert all((x.f.project/p).read_bytes()==raw for p,raw in x.snapshot.items() if p!='caller.graph.json')
    finally:path.write_bytes(held)
    x.unchanged();x.f.checked('실제 물리 source 경합은 원래 기준으로 거절하며 입력과 기존 파일을 보존한다')
print(json.dumps({'checks':x.f.checks,'evidence':str(x.f.case),'copyPolicyUsed':False,'actualWindows':False},ensure_ascii=False))
