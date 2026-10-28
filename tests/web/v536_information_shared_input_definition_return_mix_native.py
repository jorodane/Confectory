"""Input definitions and output writers share original proofs and one candidate."""
import copy
import hashlib
import json
import v536_information_shared_input_definition_return_mix_fixture as x

r = x.request()
for row in r['changes']:
    single = copy.deepcopy(r); single['changes'] = [row]; x.n.prepare(single)
x.unchanged(); x.f.checked('입력 정의/출력·반환 타입의 원래 단일 후보는 유효하고 원문은 그대로다')
if x.mode.endswith('reproduce'):
    x.n.prepare(r, False); x.unchanged(); x.f.checked('기존 그룹만 유효한 입력 정의/출력·비void 반환 결합을 거절한다')
else:
    result = x.n.prepare(r); updates = result['updates'] + result['linkedUpdates']
    (x.f.case/'prepared-candidate.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    x.verify_rows({row['id']: {'draft': row['text']} for row in updates})
    assert len({row['id'] for row in updates}) == len(updates)
    assert all(row['hash'] == hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest() for row in updates)
    reverse = copy.deepcopy(r); reverse['changes'].reverse(); other = x.n.prepare(reverse)
    assert {row['id']: row['text'] for row in updates} == {row['id']: row['text'] for row in other['updates'] + other['linkedUpdates']}
    x.unchanged(); x.f.checked('역순·원래 hash·모든 writer/소비 대응·공유 바인딩·정확64비트·본문을 한 후보로 보존한다')
    faults = ['missing-new', 'bad-new', 'extra-input', 'rename', 'role', 'order', 'out-id', 'missing-writer', 'writer-hash', 'writer-source', 'missing-consumer', 'wrong-consumer', 'return-type', 'body', 'source']
    if x.removed_input(1): faults += ['missing-use', 'bad-use', 'removed-binding']
    for fault in faults:
        bad = copy.deepcopy(r); row = bad['changes'][1 if fault not in ['missing-new', 'bad-new', 'extra-input', 'rename', 'role', 'order'] else 0]; mapping = row['mapping']
        caller = next(iter(mapping['callers'].values()))
        if fault == 'missing-new': caller['inputs'].pop('extra')
        elif fault == 'bad-new': caller['inputs']['extra'] = {'valueJson': '9223372036854775808'}
        elif fault == 'extra-input': row['signature']['args'].append({'name': 'unselected', 'type': 'long'})
        elif fault == 'rename': row['signature']['args'][0]['name'] = 'renamed'
        elif fault == 'role': row['signature']['args'][0]['mode'] = 'ref'
        elif fault == 'order': row['signature']['args'][0], row['signature']['args'][1] = row['signature']['args'][1], row['signature']['args'][0]
        elif fault == 'out-id': next(a for a in row['signature']['args'] if a['name'] == 'count')['name'] = 'renamed'
        elif fault == 'missing-writer': mapping['outputs'].pop(next(iter(mapping['outputs'])))
        elif fault == 'writer-hash': next(iter(mapping['outputs'].values()))['hash'] = '0'*64
        elif fault == 'writer-source': next(iter(mapping['outputs'].values()))['source'] = {'input': 'stable'}
        elif fault == 'missing-consumer': caller['outputs'].pop('count')
        elif fault == 'wrong-consumer': caller['outputs']['count'] = 'count'
        elif fault == 'return-type': row['signature']['return'] = 'object'
        elif fault == 'body': mapping['bodies'] = {}
        elif fault == 'missing-use': mapping.pop('implementations')
        elif fault == 'bad-use': next(iter(mapping['implementations'].values()))['value'] = {'input': 'real'}
        elif fault == 'removed-binding':
            if x.delete_only: caller['disconnect'] = {}
            else: caller['disconnect']['amount'] = json.dumps(x.graph['nodes'][1]['arguments']['amount'], separators=(',', ':'))
        else:
            unit = bad['units'][x.n.caller+'Body/body:common']; graph = json.loads(unit['draft']); graph['nodes'][1]['intent'] = '선택 이후 실제 변경'; unit['draft'] = json.dumps(graph)
        x.n.prepare(bad, False); x.unchanged()
    x.f.checked('입력 값/사용처·writer/소비·역할/순서/원문 증거 누락은 두 계약 전체 미적용이다')
    path = x.f.project/'caller.graph.json'; held = path.read_bytes()
    try:
        graph = json.loads(held); graph['nodes'][0]['intent'] = 'peer 물리 source'; path.write_text(json.dumps(graph)); x.n.prepare(r, False)
        assert all((x.f.project/name).read_bytes() == raw for name, raw in x.snapshot.items() if name != 'caller.graph.json')
    finally: path.write_bytes(held)
    x.unchanged(); x.f.checked('실제 물리 source 충돌은 전체 미적용이며 다른 원문과 입력을 보존한다')
print(json.dumps({'checks': x.f.checks, 'evidence': str(x.f.case), 'copyPolicyUsed': False, 'actualWindows': False}, ensure_ascii=False))
