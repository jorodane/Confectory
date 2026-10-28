"""Original use/disconnect and complete writer/route plans are one candidate."""
import copy
import hashlib
import json
import v536_information_shared_input_output_definition_mix_fixture as x

r = x.request(); singles = []
for row in r['changes']:
    single = copy.deepcopy(r); single['changes'] = [row]; singles.append(x.n.prepare(single))
x.unchanged(); x.f.checked('입력 타입/출력 정의 결합의 원래 단일 후보들은 유효하고 원문은 그대로다')
if x.mode.endswith('reproduce'):
    x.n.prepare(r, False); x.unchanged(); x.f.checked('기존 그룹만 유효한 입력 타입/출력 정의·void 결합을 거절한다')
else:
    result = x.n.prepare(r); updates = result['updates']+result['linkedUpdates']
    (x.f.case/'prepared-candidate.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    x.verify_rows({row['id']: {'draft': row['text']} for row in updates})
    assert len({row['id'] for row in updates}) == len(updates)
    assert all(row['hash'] == hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest() for row in updates)
    reverse = copy.deepcopy(r); reverse['changes'].reverse(); other = x.n.prepare(reverse)
    assert {row['id']: row['text'] for row in updates} == {row['id']: row['text'] for row in other['updates']+other['linkedUpdates']}
    x.unchanged(); x.f.checked('한 후보·역순·원래 hash는 명시 사용처/해제·모든 writer/경로·소비·정확64비트·C# 원문을 보존한다')
    typed = next(i for i in range(2) if x.input_changed(i)); structural = next(i for i, row in enumerate(r['changes']) if 'outputGraphs' in row['mapping'])
    input_faults = ['missing-use', 'bad-use', 'missing-value', 'wrong-value', 'disconnect', 'caller-hash', 'input-name', 'new-input', 'order', 'role']
    for fault in input_faults+['missing-graph', 'graph-hash', 'writer-set', 'exit-before', 'public-output', 'new-value', 'insertion', 'node-id', 'missing-consumer', 'wrong-consumer', 'retained-type', 'return-type', 'body', 'source']:
        bad = copy.deepcopy(r); row = bad['changes'][typed if fault in input_faults else structural]; mapping = row['mapping']
        caller = next(iter(mapping['callers'].values())); plan = next(iter(mapping.get('outputGraphs', {}).values()), None)
        if fault == 'missing-use': mapping.pop('implementations')
        elif fault == 'bad-use': next(iter(mapping['implementations'].values()))['value'] = {'input': 'real'}
        elif fault == 'missing-value': caller['inputs'].pop('amount')
        elif fault == 'wrong-value': caller['inputs']['amount'] = {'valueJson': '41'}
        elif fault == 'disconnect': caller['disconnect'] = {}
        elif fault == 'caller-hash': caller['hash'] = '0'*64
        elif fault == 'input-name': row['signature']['args'][0]['name'] = 'renamed'
        elif fault == 'new-input': row['signature']['args'].append({'name': 'extra', 'type': 'long'})
        elif fault == 'order': row['signature']['args'][0], row['signature']['args'][1] = row['signature']['args'][1], row['signature']['args'][0]
        elif fault == 'role': row['signature']['args'][0]['mode'] = 'ref'
        elif fault == 'missing-graph': mapping.pop('outputGraphs')
        elif fault == 'graph-hash': plan['hash'] = '0'*64
        elif fault == 'writer-set': plan['removes'][0]['writers'] = plan['removes'][0]['writers'][:1]
        elif fault == 'exit-before': plan['removes'][0]['before'] = 'changed'
        elif fault == 'public-output': plan['publicOutputs'] = ['fresh']
        elif fault == 'new-value': plan['creates'][0]['source'] = {'valueJson': '{}'}
        elif fault == 'insertion': plan['creates'][0]['next'] = 'changed-route'
        elif fault == 'node-id': plan['creates'][0]['node'] = 'body'
        elif fault == 'missing-consumer': caller['outputs'].pop('count')
        elif fault == 'wrong-consumer': caller['outputs']['count'] = 'count'
        elif fault == 'retained-type': next(a for a in row['signature']['args'] if a['name'] == 'stable')['type'] = 'string'
        elif fault == 'return-type': row['signature']['return'] = 'object'
        elif fault == 'body': mapping['bodies'] = {}
        else:
            unit = bad['units'][x.n.caller+'Body/body:common']; graph = json.loads(unit['draft']); graph['nodes'][1]['intent'] = '실제 선택 변경'; unit['draft'] = json.dumps(graph)
        x.n.prepare(bad, False); x.unchanged()
    x.f.checked('사용처/값/해제·전체 배치/경로/소비 증거 누락과 타입·이름·역할·순서·본문 오류는 전체 미적용이다')
    path = x.f.project/'caller.graph.json'; held = path.read_bytes()
    try:
        graph = json.loads(held); graph['nodes'][0]['intent'] = 'peer 물리 변경'; path.write_text(json.dumps(graph)); x.n.prepare(r, False)
        assert all((x.f.project/name).read_bytes() == raw for name, raw in x.snapshot.items() if name != 'caller.graph.json')
    finally: path.write_bytes(held)
    x.unchanged(); x.f.checked('실제 물리 source 경합은 두 계약 전부 미적용이며 원래 입력/다른 파일을 보존한다')
print(json.dumps({'checks': x.f.checks, 'evidence': str(x.f.case), 'copyPolicyUsed': False, 'actualWindows': False}, ensure_ascii=False))
