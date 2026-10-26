"""Explicit positional ref pin edits retain actual caller storage and C# text."""
import copy
import hashlib
import json
import os
roles = os.environ.get('CONFECTORY_SHARED_REF_ROLES') == '1'
if roles:
    import v536_information_shared_ref_roles_fixture as x
else:
    import v536_information_shared_ref_names_fixture as x

r = x.request()
for row in r['changes']:
    one = copy.deepcopy(r); one['changes'] = [row]; x.n.prepare(one)
x.unchanged(); x.f.checked('기존 값/ref 전환의 두 단일 후보는 명시 본문·호출 저장소 검토로 유효하다' if roles else '기존 ref 계약의 두 이름 편집은 각각 유효하며 원문과 저장소를 유지한다')
if x.mode.endswith('reproduce'):
    x.n.prepare(r, False); x.unchanged(); x.f.checked('기존 그룹만 유효한 값/ref 전환의 결합 저장을 거절한다' if roles else '기존 그룹만 같은 ref 역할/타입의 명시 이름 편집을 거절한다')
else:
    result = x.n.prepare(r); updates = result['updates'] + result['linkedUpdates']
    (x.f.case/'prepared-candidate.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    x.verify_rows({row['id']: {'draft': row['text']} for row in updates})
    assert len({row['id'] for row in updates}) == len(updates)
    assert all(row['hash'] == hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest() for row in updates)
    reverse = copy.deepcopy(r); reverse['changes'].reverse(); other = x.n.prepare(reverse)
    assert {row['id']: row['text'] for row in updates} == {row['id']: row['text'] for row in other['updates'] + other['linkedUpdates']}
    x.unchanged(); x.f.checked('한 후보·역순·원래hash는 명시 value/ref와 두 호출의 같은 저장소·실행 경로·C# 원문을 보존한다' if roles else '한 후보·역순·원래hash는 두 ref 호출의 같은 저장소·실행 경로·C# 원문을 보존한다')
    for fault in ['type', 'role', 'order', 'count', 'return', 'map', 'caller', 'body', 'bad-body', 'receipt', 'native-shape', 'output-map', 'stale', 'source']:
        bad = copy.deepcopy(r); row = bad['changes'][0 if fault in ['body','bad-body','receipt','native-shape','output-map'] else 1]; mapping = row['mapping']
        if fault == 'type': row['signature']['args'][0]['type'] = 'string'
        elif fault == 'role': row['signature']['args'][1]['mode'] = 'out'
        elif fault == 'order': row['signature']['args'].reverse()
        elif fault == 'count': row['signature']['args'].append({'name': 'newInput', 'type': 'long'})
        elif fault == 'return': row['signature']['return'] = 'void'
        elif fault == 'map': mapping['args']['amount'] = row['signature']['args'][1]['name']
        elif fault == 'caller':
            mapping.setdefault('callers', copy.deepcopy(r['changes'][0]['mapping']['callers']))
            next(iter(mapping['callers'].values()))['inputs'][row['signature']['args'][1]['name']] = 'amount'
        elif fault == 'body': mapping.pop('bodies')
        elif fault == 'bad-body': next(iter(mapping['bodies'].values()))['text'] = 'return;'
        elif fault == 'receipt': next(iter(mapping['bodies'].values()))['whole']['hash'] = '0'*64
        elif fault == 'native-shape': next(iter(mapping['bodies'].values()))['signature']['args'][1]['mode']='out'
        elif fault == 'output-map': next(iter(mapping['bodies'].values()))['outputs']['return'] = None
        elif fault == 'stale': mapping['before']['args'][0]['type'] = 'string'
        else:
            unit = bad['units'][x.n.caller+'Body/body:common']; graph = json.loads(unit['draft']); graph['nodes'][1]['intent'] = '선택 이후 변경'; unit['draft'] = json.dumps(graph)
        x.n.prepare(bad, False); x.unchanged()
    path = x.f.project/'caller.graph.json'; held = path.read_bytes()
    try:
        g = json.loads(held); g['nodes'][0]['intent'] = 'peer source'; path.write_text(json.dumps(g)); x.n.prepare(r, False)
        assert all((x.f.project/name).read_bytes() == raw for name, raw in x.snapshot.items() if name != 'caller.graph.json')
    finally: path.write_bytes(held)
    x.unchanged(); x.f.checked('타입/out 역할/순서·모호한 대응·재선택/본문 확대·실제 소스 경합은 모두 미적용이다' if roles else '타입/역할/순서·모호한 대응·재선택/본문 확대·실제 소스 경합은 모두 미적용이다')
    unit = r['units'][x.n.caller+'Body/body:common']; modified = copy.deepcopy(r); graph = json.loads(unit['draft'])
    graph['nodes'][0]['arguments']['count'] = {'constant': 41}; modified['units'][x.n.caller+'Body/body:common']['draft'] = json.dumps(graph)
    x.n.prepare(modified, False); x.unchanged(); x.f.checked('ref 저장소를 임의 값으로 바꾼 선택은 거절하고 원래 입력과 정확한 값을 보존한다')
print(json.dumps({'checks': x.f.checks, 'evidence': str(x.f.case), 'actualWindows': False, 'newContractIds': False}, ensure_ascii=False))
