"""Input cardinality changes compose only individually valid original closures."""
import copy
import hashlib
import json
import v536_information_shared_input_definitions_fixture as x

r = x.request()
for change in r['changes']:
    single = copy.deepcopy(r); single['changes'] = [change]; x.n.prepare(single)
x.unchanged(); x.f.checked('새 입력 추가와 사용 중 입력 삭제/추가의 원래 단일 후보는 각각 유효하다')
if x.mode == 'reproduce':
    x.n.prepare(r, False); x.unchanged(); x.f.checked('기존 그룹 가드는 두 유효한 입력 정의 변경을 함께 저장하지 못한다')
else:
    result = x.n.prepare(r); updates = result['updates']+result['linkedUpdates']
    (x.f.case/'prepared-candidate.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    x.verify_rows({row['id']: {'draft': row['text']} for row in updates})
    assert len({row['id'] for row in updates}) == len(updates)
    assert all(row['hash'] == hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest() for row in updates)
    reverse = copy.deepcopy(r); reverse['changes'].reverse(); other = x.n.prepare(reverse)
    assert {row['id']: row['text'] for row in updates} == {row['id']: row['text'] for row in other['updates']+other['linkedUpdates']}
    x.unchanged(); x.f.checked('한 후보·역순·원래 hash는 새 exact64 값·callee 사용처와 caller 값 재사용·원래 출력/C# 원문을 보존한다')
    for fault in ['missing-value', 'bad-value', 'overflow', 'missing-use', 'bad-use', 'disconnect-reused', 'extra-output', 'retained-type', 'retained-name', 'order', 'out-role', 'return', 'body', 'source']:
        bad = copy.deepcopy(r); first, last = bad['changes']; mapping = last['mapping']
        if fault == 'missing-value': next(iter(first['mapping']['callers'].values()))['inputs'].pop('extra')
        elif fault == 'bad-value': next(iter(first['mapping']['callers'].values()))['inputs']['extra'] = {'valueJson': '"not long"'}
        elif fault == 'overflow': next(iter(first['mapping']['callers'].values()))['inputs']['extra'] = {'valueJson': '9223372036854775808'}
        elif fault == 'missing-use': mapping.pop('implementations')
        elif fault == 'bad-use': next(iter(mapping['implementations'].values()))['value'] = {'input': 'real'}
        elif fault == 'disconnect-reused':
            if x.delete_only: next(iter(mapping['callers'].values()))['disconnect'] = {}
            else: next(iter(mapping['callers'].values()))['disconnect']['amount'] = '{"node":"invoke","output":"count"}'
        elif fault == 'extra-output': next(iter(mapping['callers'].values()))['outputs'] = {'count': 'return', 'return': 'return'}
        elif fault == 'retained-type': last['signature']['args'][0]['type'] = 'string'
        elif fault == 'retained-name': last['signature']['args'][0]['name'] = 'renamed'; mapping['args']['real'] = 'renamed'
        elif fault == 'order': first['signature']['args'][0],first['signature']['args'][1] = first['signature']['args'][1],first['signature']['args'][0]
        elif fault == 'out-role': last['signature']['args'][1]['mode'] = 'ref'
        elif fault == 'return': last['signature']['return'] = 'double'
        elif fault == 'body': mapping['bodies'] = {}
        else:
            unit = bad['units'][x.n.caller+'Body/body:common']; graph = json.loads(unit['draft']); graph['nodes'][1]['intent'] = '다른 선택'; unit['draft'] = json.dumps(graph)
        x.n.prepare(bad, False); x.unchanged()
    x.f.checked('새 값/사용처 누락·타입 오류·재사용/해제 모순·기존 핀 변경·out/반환/본문·source 변경은 전부 미적용이다')
    path = x.f.project/'caller.graph.json'; held = path.read_bytes()
    try:
        peer = json.loads(held); peer['nodes'][0]['intent'] = '실제 peer 수정'; path.write_text(json.dumps(peer)); x.n.prepare(r, False)
        assert all((x.f.project/p).read_bytes() == raw for p, raw in x.snapshot.items() if p != 'caller.graph.json')
    finally:
        path.write_bytes(held)
    x.unchanged(); x.f.checked('실제 물리 source 변경은 내부 합성과 구별하여 전체 거절하고 원문과 입력을 유지한다')
print(json.dumps({'checks': x.f.checks, 'evidence': str(x.f.case), 'copyPolicyUsed': False, 'actualWindows': False}, ensure_ascii=False))
