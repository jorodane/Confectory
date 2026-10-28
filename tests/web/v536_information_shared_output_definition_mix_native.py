"""Original graph/writer closures are proved before the shared overlay."""
import copy
import hashlib
import json
import v536_information_shared_output_definition_mix_fixture as x

r = x.request(); singles = []
for row in r['changes']:
    single = copy.deepcopy(r); single['changes'] = [row]; singles.append(x.n.prepare(single))
x.unchanged(); x.f.checked('출력 정의/타입 결합의 원래 단일 후보는 각각 유효하고 원본은 그대로다')
if x.mode.endswith('reproduce'):
    x.n.prepare(r, False); x.unchanged(); x.f.checked('기존 그룹 가드는 유효한 출력 정의·타입 편집의 결합을 거절한다')
else:
    result = x.n.prepare(r); updates = result['updates']+result['linkedUpdates']
    (x.f.case/'prepared-candidate.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    x.verify_rows({row['id']: {'draft': row['text']} for row in updates})
    assert len({row['id'] for row in updates}) == len(updates)
    assert all(row['hash'] == hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest() for row in updates)
    reverse = copy.deepcopy(r); reverse['changes'].reverse(); other = x.n.prepare(reverse)
    assert {row['id']: row['text'] for row in updates} == {row['id']: row['text'] for row in other['updates']+other['linkedUpdates']}
    x.unchanged(); x.f.checked('한 후보·역순·원래 hash는 전체 writer/삽입 경로·공유 소비·공개 범위·정확64비트·C# 원문을 보존한다')
    intermediate = next(row['text'] for row in singles[0]['linkedUpdates'] if row['id'] == x.n.caller+'Body/body:common')
    for fault in ['intermediate-hash', 'missing-graph', 'graph-hash', 'incomplete-writers', 'exit-before', 'public-output',
                  'source-value', 'insertion', 'new-node-identity', 'writer-before', 'writer-source', 'missing-writer',
                  'missing-consumer', 'wrong-consumer', 'input-type', 'input-plan', 'order', 'role', 'return', 'body', 'source']:
        bad = copy.deepcopy(r)
        row = bad['changes'][0 if fault in ['missing-graph', 'graph-hash', 'incomplete-writers', 'exit-before', 'public-output', 'source-value', 'insertion', 'new-node-identity'] else 1]
        mapping = row['mapping']; caller = next(iter(mapping['callers'].values()))
        graph = next(iter(mapping.get('outputGraphs', {}).values()), None)
        if fault == 'intermediate-hash': caller['hash'] = hashlib.sha256(intermediate.encode()).hexdigest()
        elif fault == 'missing-graph': mapping.pop('outputGraphs')
        elif fault == 'graph-hash': graph['hash'] = '0'*64
        elif fault == 'incomplete-writers': graph['removes'][0]['writers'] = graph['removes'][0]['writers'][:1]
        elif fault == 'exit-before': graph['removes'][0]['before'] = 'changed'
        elif fault == 'public-output': graph['publicOutputs'] = ['fresh']
        elif fault == 'source-value': graph['creates'][0]['source'] = {'valueJson': '{}'}
        elif fault == 'insertion': graph['creates'][0]['next'] = 'changed-route'
        elif fault == 'new-node-identity': graph['creates'][0]['node'] = 'body'
        elif fault == 'writer-before': next(iter(mapping['outputs'].values()))['before'] = 'null'
        elif fault == 'writer-source': next(iter(mapping['outputs'].values()))['source'] = {'input': 'amount'}
        elif fault == 'missing-writer': mapping['outputs'] = {}
        elif fault == 'missing-consumer': caller['outputs'].pop('count')
        elif fault == 'wrong-consumer': caller['outputs']['count'] = 'count'
        elif fault == 'input-type': row['signature']['args'][0]['type'] = 'string'; mapping['args']['amount'] = None
        elif fault == 'input-plan': caller['inputs']['amount'] = 'real'
        elif fault == 'order': row['signature']['args'][0], row['signature']['args'][1] = row['signature']['args'][1], row['signature']['args'][0]
        elif fault == 'role': row['signature']['args'][0]['mode'] = 'ref'
        elif fault == 'return': row['signature']['return'] = 'void'
        elif fault == 'body': mapping['bodies'] = {}
        else:
            unit = bad['units'][x.n.caller+'Body/body:common']; value = json.loads(unit['draft']); value['nodes'][1]['intent'] = '실제 선택 변경'; unit['draft'] = json.dumps(value)
        x.n.prepare(bad, False); x.unchanged()
    x.f.checked('전체 배치/경로/새 값/writer/소비 누락·타입/입력/역할/순서/본문·source 오류는 전체 미적용이다')
    path = x.f.project/'caller.graph.json'; held = path.read_bytes()
    try:
        value = json.loads(held); value['nodes'][0]['intent'] = 'peer 물리 변경'; path.write_text(json.dumps(value)); x.n.prepare(r, False)
        assert all((x.f.project/name).read_bytes() == raw for name, raw in x.snapshot.items() if name != 'caller.graph.json')
    finally:
        path.write_bytes(held)
    x.unchanged(); x.f.checked('실제 물리 source 경합은 전체 거절하고 원문과 원래 입력을 보존한다')
print(json.dumps({'checks': x.f.checks, 'evidence': str(x.f.case), 'copyPolicyUsed': False, 'actualWindows': False}, ensure_ascii=False))
