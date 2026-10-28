"""Mixed scalar edit categories must compose original closures, not live writes."""
import copy
import hashlib
import json
import v536_information_shared_mixed_types_fixture as x

r = x.request()
for change in r['changes']:
    single = copy.deepcopy(r)
    single['changes'] = [change]
    x.n.prepare(single)
x.unchanged()
x.f.checked('입력만/출력만의 원래 단일 후보는 각각 유효하고 원본 파일을 바꾸지 않는다')
if x.mode == 'reproduce':
    x.n.prepare(r, False)
    x.unchanged()
    x.f.checked('기존 그룹 가드는 유효한 두 단일 후보의 결합을 거절한다')
else:
    result = x.n.prepare(r)
    updates = result['updates']+result['linkedUpdates']
    (x.f.case/'prepared-candidate.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    assert len({row['id'] for row in updates}) == len(updates)
    assert all(row['hash'] == hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest() for row in updates)
    x.verify_rows({row['id']: {'draft': row['text']} for row in updates})
    reverse = copy.deepcopy(r)
    reverse['changes'].reverse()
    other = x.n.prepare(reverse)
    assert {row['id']: row['text'] for row in updates} == {row['id']: row['text'] for row in other['updates']+other['linkedUpdates']}
    x.unchanged()
    x.f.checked('다른 입력/out 편집 종류도 원래 hash의 한 후보이며 역순·정확64비트·원문과 소비 연결을 보존한다')
    both = x.base.request()
    for index in range(2):
        mixed = copy.deepcopy(r)
        mixed['changes'][index] = copy.deepcopy(both['changes'][index])
        signatures = [row['signature'] for row in mixed['changes']]
        combined = x.n.prepare(mixed)
        x.verify_rows({row['id']: {'draft': row['text']} for row in combined['updates']+combined['linkedUpdates']}, signatures)
        mixed['changes'].reverse()
        reversed_result = x.n.prepare(mixed)
        assert {row['id']: row['text'] for row in combined['updates']+combined['linkedUpdates']} == {row['id']: row['text'] for row in reversed_result['updates']+reversed_result['linkedUpdates']}
        x.unchanged()
    x.f.checked('입력/out 동시 변경도 입력 전용·출력 전용과 섞이며 양방향 후보 순서와 원래 해제 증거를 보존한다')
    for fault in ['missing-use', 'bad-use', 'missing-disconnect', 'bad-disconnect', 'extra-writer', 'missing-writer', 'bad-output', 'role', 'count', 'return', 'rename', 'body']:
        bad = copy.deepcopy(r)
        left, right = bad['changes']
        if fault == 'missing-use': left['mapping'].pop('implementations')
        elif fault == 'bad-use': next(iter(left['mapping']['implementations'].values()))['value'] = {'valueJson': '"not long"'}
        elif fault == 'missing-disconnect': next(iter(left['mapping']['callers'].values()))['disconnect'] = {}
        elif fault == 'bad-disconnect': next(iter(left['mapping']['callers'].values()))['disconnect']['amount'] = '{"constant":7}'
        elif fault == 'extra-writer': left['mapping']['outputs'] = copy.deepcopy(right['mapping']['outputs'])
        elif fault == 'missing-writer': right['mapping'].pop('outputs')
        elif fault == 'bad-output': next(iter(right['mapping']['callers'].values()))['outputs']['count'] = 'count'
        elif fault == 'role': right['signature']['args'][2]['mode'] = 'ref'
        elif fault == 'count': right['signature']['args'].append({'name': 'new', 'type': 'long'})
        elif fault == 'return': left['signature']['return'] = 'double'
        elif fault == 'rename': right['signature']['args'][0]['name'] = 'renamed'; right['mapping']['args']['amount'] = 'renamed'
        else: left['mapping']['bodies'] = {}
        x.n.prepare(bad, False)
        x.unchanged()
    x.f.checked('불완전·타입/대응 오류·추가 계획·역할/수/반환/이름/본문 변경은 원래 파일에 전부 미적용이다')
    path = x.f.project/'caller.graph.json'
    original = path.read_bytes()
    try:
        peer = json.loads(original); peer['nodes'][0]['intent'] = 'peer 원문'
        path.write_text(json.dumps(peer))
        x.n.prepare(r, False)
        assert all((x.f.project/p).read_bytes() == raw for p, raw in x.snapshot.items() if p != 'caller.graph.json')
    finally:
        path.write_bytes(original)
    x.unchanged()
    x.f.checked('실제 물리 source 변경은 내부 후보 합성과 달리 전부 거절하고 peer와 입력을 보존한다')
print(json.dumps({'checks': x.f.checks, 'evidence': str(x.f.case), 'copyPolicyUsed': False, 'actualWindows': False}, ensure_ascii=False))
