"""Explicit renames and output graph changes retain all old identities atomically."""
import copy
import hashlib
import json
import v536_information_shared_input_name_output_definitions_fixture as x

r = x.request(); singles = []
for row in r['changes']:
    single = copy.deepcopy(r); single['changes'] = [row]; singles.append(x.n.prepare(single))
x.unchanged(); x.f.checked('입력 이름/출력 정의의 원래 단일 후보는 유효하고 원본은 그대로다')
if x.mode.endswith('reproduce'):
    x.n.prepare(r, False); x.unchanged(); x.f.checked('기존 그룹만 유효한 이름/출력 정의 결합을 거절한다')
else:
    result = x.n.prepare(r); updates = result['updates']+result['linkedUpdates']
    (x.f.case/'prepared-candidate.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    x.verify_rows({row['id']: {'draft': row['text']} for row in updates})
    assert len({row['id'] for row in updates}) == len(updates)
    assert all(row['hash'] == hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest() for row in updates)
    reverse = copy.deepcopy(r); reverse['changes'].reverse(); other = x.n.prepare(reverse)
    # Newly requested export identities are explicit and therefore identical in either order.
    assert {row['id']: row['text'] for row in updates} == {row['id']: row['text'] for row in other['updates']+other['linkedUpdates']}
    x.unchanged(); x.f.checked('한 후보·역순·원래 hash는 이름/기존값·모든 writer/소비·정확64비트·본문을 보존한다')
    structural = next(i for i, row in enumerate(r['changes']) if 'outputGraphs' in row['mapping'])
    for fault in ['rename-missing', 'rename-wrong', 'input-value', 'disconnect', 'missing-graph', 'graph-hash',
                  'writer-set', 'exit-before', 'public-output', 'new-value', 'insertion', 'node-id',
                  'missing-consumer', 'wrong-consumer', 'input-type', 'new-input', 'order', 'role', 'body', 'source']:
        bad = copy.deepcopy(r); row = bad['changes'][0 if fault.startswith('rename-') else structural]
        mapping = row['mapping']; caller = next(iter(mapping.get('callers', {}).values()), None)
        graph = next(iter(mapping.get('outputGraphs', {}).values()), None)
        if fault == 'rename-missing': mapping['args'].pop('amount')
        elif fault == 'rename-wrong': mapping['args']['amount'] = 'real'
        elif fault == 'input-value': caller['inputs'][row['signature']['args'][0]['name']] = {'valueJson': '99'}
        elif fault == 'disconnect': caller['disconnect'] = {'amount': json.dumps(x.graph['nodes'][structural]['arguments']['amount'], separators=(',', ':'))}
        elif fault == 'missing-graph': mapping.pop('outputGraphs')
        elif fault == 'graph-hash': graph['hash'] = '0'*64
        elif fault == 'writer-set': graph['removes'][0]['writers'] = graph['removes'][0]['writers'][:1]
        elif fault == 'exit-before': graph['removes'][0]['before'] = 'changed'
        elif fault == 'public-output': graph['publicOutputs'] = ['fresh']
        elif fault == 'new-value': graph['creates'][0]['source'] = {'valueJson': '{}'}
        elif fault == 'insertion': graph['creates'][0]['next'] = 'changed-route'
        elif fault == 'node-id': graph['creates'][0]['node'] = 'body'
        elif fault == 'missing-consumer': caller['outputs'].pop('count')
        elif fault == 'wrong-consumer': caller['outputs']['count'] = 'count'
        elif fault == 'input-type': row['signature']['args'][0]['type'] = 'string'; mapping['args']['amount'] = None
        elif fault == 'new-input': row['signature']['args'].append({'name': 'extra', 'type': 'long'})
        elif fault == 'order': row['signature']['args'][0], row['signature']['args'][1] = row['signature']['args'][1], row['signature']['args'][0]
        elif fault == 'role': row['signature']['args'][0]['mode'] = 'ref'
        elif fault == 'body': mapping['bodies'] = {}
        else:
            unit = bad['units'][x.n.caller+'Body/body:common']; value = json.loads(unit['draft']); value['nodes'][1]['intent'] = '실제 선택 변경'; unit['draft'] = json.dumps(value)
        x.n.prepare(bad, False); x.unchanged()
    x.f.checked('이름/값/전체 배치/경로/소비 대응 누락·타입/입력/순서/역할·source 오류는 전체 미적용이다')
    path = x.f.project/'caller.graph.json'; held = path.read_bytes()
    try:
        value = json.loads(held); value['nodes'][0]['intent'] = 'peer 물리 원문'; path.write_text(json.dumps(value)); x.n.prepare(r, False)
        assert all((x.f.project/name).read_bytes() == raw for name, raw in x.snapshot.items() if name != 'caller.graph.json')
    finally:
        path.write_bytes(held)
    x.unchanged(); x.f.checked('실제 물리 source 경합은 원래 입력·다른 파일을 보존하고 전부 거절한다')
print(json.dumps({'checks': x.f.checks, 'evidence': str(x.f.case), 'copyPolicyUsed': False, 'actualWindows': False}, ensure_ascii=False))
