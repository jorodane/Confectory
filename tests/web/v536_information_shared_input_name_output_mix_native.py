"""Rename maps prove retained values; output plans prove changed writers."""
import copy
import hashlib
import json
import v536_information_shared_input_name_output_mix_fixture as x

r = x.request(); singles = []
for row in r['changes']:
    single = copy.deepcopy(r); single['changes'] = [row]; singles.append(x.n.prepare(single))
x.unchanged(); x.f.checked('입력 이름/출력 타입 결합의 원래 단일 후보는 각각 유효하고 원본은 그대로다')
if x.mode.endswith('reproduce'):
    x.n.prepare(r, False); x.unchanged(); x.f.checked('기존 그룹 가드는 유효한 입력 이름과 out/반환 타입의 결합을 거절한다')
else:
    result = x.n.prepare(r); updates = result['updates']+result['linkedUpdates']
    (x.f.case/'prepared-candidate.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    x.verify_rows({row['id']: {'draft': row['text']} for row in updates})
    assert len({row['id'] for row in updates}) == len(updates)
    assert all(row['hash'] == hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest() for row in updates)
    reverse = copy.deepcopy(r); reverse['changes'].reverse(); other = x.n.prepare(reverse)
    assert {row['id']: row['text'] for row in updates} == {row['id']: row['text'] for row in other['updates']+other['linkedUpdates']}
    x.unchanged(); x.f.checked('한 후보·역순·원래 hash는 이름 대응의 기존 값·출력 소비·정확64비트·C# 매개변수/본문을 보존한다')
    intermediate = next(row['text'] for row in singles[0]['linkedUpdates'] if row['id'] == x.n.caller+'Body/body:common')
    faults = ['missing-rename', 'wrong-rename', 'intermediate-hash', 'missing-input', 'wrong-input', 'disconnect',
                  'writer-before', 'writer-source', 'missing-writer', 'missing-consumer', 'wrong-consumer',
                  'input-type', 'new-input', 'order', 'role', 'void', 'out-name', 'body', 'source']
    if not x.joint: faults += ['pure-rename-out', 'pure-rename-plan']
    for fault in faults:
        bad = copy.deepcopy(r); row = bad['changes'][0 if fault in ['missing-rename', 'wrong-rename', 'pure-rename-out', 'pure-rename-plan'] else 1]
        mapping = row['mapping']; caller = next(iter(mapping.get('callers', {}).values()), None)
        if fault == 'missing-rename': mapping['args'].pop('amount')
        elif fault == 'wrong-rename': mapping['args']['amount'] = 'real'
        elif fault == 'pure-rename-out': row['signature']['args'][2]['name'] = 'changedCount'; mapping['args']['count'] = 'changedCount'
        elif fault == 'pure-rename-plan': mapping['callers'] = copy.deepcopy(bad['changes'][1]['mapping']['callers'])
        elif fault == 'intermediate-hash': caller['hash'] = hashlib.sha256(intermediate.encode()).hexdigest()
        elif fault == 'missing-input': caller['inputs'].pop(row['signature']['args'][0]['name'])
        elif fault == 'wrong-input': caller['inputs'][row['signature']['args'][0]['name']] = 'real'
        elif fault == 'disconnect': caller['disconnect'] = {'amount': json.dumps(x.graph['nodes'][1]['arguments']['amount'], separators=(',', ':'))}
        elif fault == 'writer-before': next(iter(mapping['outputs'].values()))['before'] = 'null'
        elif fault == 'writer-source': next(iter(mapping['outputs'].values()))['source'] = {'input': row['signature']['args'][0]['name']}
        elif fault == 'missing-writer': mapping['outputs'] = {}
        elif fault == 'missing-consumer': caller['outputs'].pop('count')
        elif fault == 'wrong-consumer': caller['outputs']['count'] = 'count'
        elif fault == 'input-type': row['signature']['args'][0]['type'] = 'string'; mapping['args']['amount'] = None
        elif fault == 'new-input': row['signature']['args'].append({'name': 'extra', 'type': 'long'})
        elif fault == 'order': row['signature']['args'][0], row['signature']['args'][1] = row['signature']['args'][1], row['signature']['args'][0]
        elif fault == 'role': row['signature']['args'][0]['mode'] = 'ref'
        elif fault == 'void': row['signature']['return'] = 'void'
        elif fault == 'out-name': row['signature']['args'][2]['name'] = 'changedCount'; mapping['args']['count'] = 'changedCount'
        elif fault == 'body': mapping['bodies'] = {}
        else:
            unit = bad['units'][x.n.caller+'Body/body:common']; graph = json.loads(unit['draft']); graph['nodes'][1]['intent'] = '실제 선택 변경'; unit['draft'] = json.dumps(graph)
        x.n.prepare(bad, False); x.unchanged()
    x.f.checked('이름/기존 값 대응 누락·타입/입력/역할/순서·writer/소비/본문·선택 오류는 전체 미적용이다')
    path = x.f.project/'caller.graph.json'; held = path.read_bytes()
    try:
        graph = json.loads(held); graph['nodes'][0]['intent'] = 'peer 물리 변경'; path.write_text(json.dumps(graph)); x.n.prepare(r, False)
        assert all((x.f.project/name).read_bytes() == raw for name, raw in x.snapshot.items() if name != 'caller.graph.json')
    finally:
        path.write_bytes(held)
    x.unchanged(); x.f.checked('실제 물리 source 경합은 전체 거절하고 원문과 원래 입력을 보존한다')
print(json.dumps({'checks': x.f.checks, 'evidence': str(x.f.case), 'copyPolicyUsed': False, 'actualWindows': False}, ensure_ascii=False))
