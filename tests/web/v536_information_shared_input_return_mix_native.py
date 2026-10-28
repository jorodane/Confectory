"""Original input-use/disconnect and return-writer plans share one candidate."""
import copy
import hashlib
import json
import v536_information_shared_input_return_mix_fixture as x

r = x.request(); singles = []
for row in r['changes']:
    one = copy.deepcopy(r); one['changes'] = [row]; singles.append(x.n.prepare(one))
x.unchanged(); x.f.checked('입력 타입/반환 타입의 원래 단일 후보는 각각 유효하고 원문은 그대로다')
if x.mode.endswith('reproduce'):
    x.n.prepare(r, False); x.unchanged(); x.f.checked('기존 그룹만 유효한 입력 타입/비void 반환 타입 결합을 거절한다')
else:
    result = x.n.prepare(r); updates = result['updates']+result['linkedUpdates']
    (x.f.case/'prepared-candidate.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    x.verify_rows({row['id']: {'draft': row['text']} for row in updates})
    assert len({row['id'] for row in updates}) == len(updates)
    assert all(row['hash'] == hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest() for row in updates)
    reverse = copy.deepcopy(r); reverse['changes'].reverse(); other = x.n.prepare(reverse)
    assert {row['id']: row['text'] for row in updates} == {row['id']: row['text'] for row in other['updates']+other['linkedUpdates']}
    x.unchanged(); x.f.checked('한 후보·역순·원래 hash는 명시 사용처/해제와 반환 소비·정확64비트·C# 원문을 보존한다')
    for fault in ['missing-use', 'bad-use', 'missing-value', 'wrong-value', 'disconnect', 'caller-hash', 'writer-before',
                  'writer-source', 'missing-writer', 'missing-output', 'wrong-output', 'input-name', 'new-input',
                  'order', 'role', 'void', 'body', 'source']:
        bad = copy.deepcopy(r); index = 1 if fault in ['missing-use', 'bad-use', 'missing-value', 'wrong-value', 'disconnect', 'input-name', 'new-input', 'order', 'role'] else 0
        row = bad['changes'][index]; mapping = row['mapping']; caller = next(iter(mapping['callers'].values()))
        if fault == 'missing-use': mapping.pop('implementations')
        elif fault == 'bad-use': next(iter(mapping['implementations'].values()))['value'] = {'input': 'real'}
        elif fault == 'missing-value': caller['inputs'].pop('amount')
        elif fault == 'wrong-value': caller['inputs']['amount'] = {'valueJson': '41'}
        elif fault == 'disconnect': caller['disconnect'] = {}
        elif fault == 'caller-hash': caller['hash'] = '0'*64
        elif fault == 'writer-before': next(iter(mapping['outputs'].values()))['before'] = 'null'
        elif fault == 'writer-source': next(iter(mapping['outputs'].values()))['source'] = {'input': 'amount'}
        elif fault == 'missing-writer': mapping['outputs'] = {}
        elif fault == 'missing-output': caller['outputs'].pop('return')
        elif fault == 'wrong-output': caller['outputs']['return'] = 'return'
        elif fault == 'input-name': row['signature']['args'][0]['name'] = 'renamed'
        elif fault == 'new-input': row['signature']['args'].append({'name': 'extra', 'type': 'long'})
        elif fault == 'order': row['signature']['args'][0], row['signature']['args'][1] = row['signature']['args'][1], row['signature']['args'][0]
        elif fault == 'role': row['signature']['args'][0]['mode'] = 'ref'
        elif fault == 'void': row['signature']['return'] = 'void'
        elif fault == 'body': mapping['bodies'] = {}
        else:
            unit = bad['units'][x.n.caller+'Body/body:common']; graph = json.loads(unit['draft']); graph['nodes'][1]['intent'] = '실제 선택 변경'; unit['draft'] = json.dumps(graph)
        x.n.prepare(bad, False); x.unchanged()
    x.f.checked('원래 사용처/값/해제·writer/소비 누락과 타입/이름/역할/순서/void/본문 오류는 전체 미적용이다')
    path = x.f.project/'caller.graph.json'; held = path.read_bytes()
    try:
        graph = json.loads(held); graph['nodes'][0]['intent'] = 'peer 물리 원문'; path.write_text(json.dumps(graph)); x.n.prepare(r, False)
        assert all((x.f.project/name).read_bytes() == raw for name, raw in x.snapshot.items() if name != 'caller.graph.json')
    finally: path.write_bytes(held)
    x.unchanged(); x.f.checked('실제 물리 source 경합은 두 계약을 전부 거절하고 원래 입력·다른 파일을 보존한다')
print(json.dumps({'checks': x.f.checks, 'evidence': str(x.f.case), 'copyPolicyUsed': False, 'actualWindows': False}, ensure_ascii=False))
