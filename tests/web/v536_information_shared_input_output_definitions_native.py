"""Explicit input definitions and all output writers publish one candidate."""
import copy
import hashlib
import json
import v536_information_shared_input_output_definitions_fixture as x

r = x.request()
for row in r['changes']:
    single = copy.deepcopy(r); single['changes'] = [row]; x.n.prepare(single)
x.unchanged(); x.f.checked('입력/출력 정의·void 결합의 원래 단일 후보는 유효하고 원문은 그대로다')
if x.mode.endswith('reproduce'):
    x.n.prepare(r, False); x.unchanged(); x.f.checked('기존 그룹만 유효한 입력/출력 정의·void 결합을 거절한다')
else:
    result = x.n.prepare(r); updates = result['updates'] + result['linkedUpdates']
    (x.f.case/'prepared-candidate.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    x.verify_rows({row['id']: {'draft': row['text']} for row in updates})
    assert len({row['id'] for row in updates}) == len(updates)
    assert all(row['hash'] == hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest() for row in updates)
    reverse = copy.deepcopy(r); reverse['changes'].reverse(); other = x.n.prepare(reverse)
    assert {row['id']: row['text'] for row in updates} == {row['id']: row['text'] for row in other['updates'] + other['linkedUpdates']}
    x.unchanged(); x.f.checked('역순·원래hash·입력 재사용/해제·모든 writer/경로/소비·정확64비트·본문을 한 후보로 보존한다')
    added = next(i for i in range(2) if x.extra_added(i))
    faults = ['missing-value', 'bad-value', 'new-input', 'rename', 'order', 'role', 'cross-role', 'missing-graph', 'graph-hash', 'writer-set', 'exit-before', 'public-output', 'new-output-value', 'insertion', 'node-id', 'missing-consumer', 'wrong-consumer', 'retained-type', 'return-type', 'body', 'source']
    if x.input_removed(1): faults += ['missing-use', 'bad-use', 'binding-proof']
    else: faults += ['output-only-input', 'input-only-output']
    for fault in faults:
        bad = copy.deepcopy(r); row = bad['changes'][added if fault in ['missing-value', 'bad-value', 'new-input', 'rename', 'order', 'role'] else 1 if fault in ['missing-use', 'bad-use', 'binding-proof', 'input-only-output'] else 0]; mapping = row['mapping']; caller = next(iter(mapping['callers'].values())); plan = next(iter(mapping.get('outputGraphs', {}).values()), None)
        if fault == 'missing-value': caller['inputs'].pop('extra')
        elif fault == 'bad-value': caller['inputs']['extra'] = {'valueJson': '9223372036854775808'}
        elif fault == 'new-input': row['signature']['args'].append({'name': 'unselected', 'type': 'long'})
        elif fault == 'rename': row['signature']['args'][0]['name'] = 'renamed'
        elif fault == 'order': row['signature']['args'][0], row['signature']['args'][1] = row['signature']['args'][1], row['signature']['args'][0]
        elif fault == 'role': row['signature']['args'][0]['mode'] = 'ref'
        elif fault == 'cross-role':
            row['signature']['args'].append({'name': 'count', 'type': 'long'}); caller['inputs']['count'] = {'valueJson': '23'}
        elif fault == 'missing-graph': mapping.pop('outputGraphs')
        elif fault == 'graph-hash': plan['hash'] = '0'*64
        elif fault == 'writer-set': plan['removes'][0]['writers'] = plan['removes'][0]['writers'][:1]
        elif fault == 'exit-before': plan['removes'][0]['before'] = 'changed'
        elif fault == 'public-output': plan['publicOutputs'] = ['fresh']
        elif fault == 'new-output-value': plan['creates'][0]['source'] = {'valueJson': '{}'}
        elif fault == 'insertion': plan['creates'][0]['next'] = 'changed-route'
        elif fault == 'node-id': plan['creates'][0]['node'] = 'body'
        elif fault == 'missing-consumer': caller['outputs'].pop('count')
        elif fault == 'wrong-consumer': caller['outputs']['count'] = 'count'
        elif fault == 'retained-type': next(a for a in row['signature']['args'] if a['name'] == 'stable')['type'] = 'string'
        elif fault == 'return-type': row['signature']['return'] = 'object'
        elif fault == 'body': mapping['bodies'] = {}
        elif fault == 'missing-use': mapping.pop('implementations')
        elif fault == 'bad-use': next(iter(mapping['implementations'].values()))['value'] = {'input': 'real'}
        elif fault == 'binding-proof':
            if x.to_void: caller['disconnect'] = {}
            else: caller['disconnect']['amount'] = json.dumps(x.graph['nodes'][1]['arguments']['amount'], separators=(',', ':'))
        elif fault == 'output-only-input': caller['inputs']['amount'] = {'valueJson': '41'}
        elif fault == 'input-only-output':
            mapping['outputs'] = {}; caller['outputs'] = {name: name for name in x.outs(x.old)}
        else:
            unit = bad['units'][x.n.caller+'Body/body:common']; graph = json.loads(unit['draft']); graph['nodes'][1]['intent'] = '실제 선택 변경'; unit['draft'] = json.dumps(graph)
        x.n.prepare(bad, False); x.unchanged()
    x.f.checked('입력 값/사용처·전체 writer/경로/소비 누락·역할/순서/원문 오류와 재선택 권한 확대는 전체 미적용이다')
    path = x.f.project/'caller.graph.json'; held = path.read_bytes()
    try:
        graph = json.loads(held); graph['nodes'][0]['intent'] = 'peer 물리 source'; path.write_text(json.dumps(graph)); x.n.prepare(r, False)
        assert all((x.f.project/name).read_bytes() == raw for name, raw in x.snapshot.items() if name != 'caller.graph.json')
    finally: path.write_bytes(held)
    x.unchanged(); x.f.checked('실제 물리 source 충돌은 전체 미적용이며 기존 원문과 입력을 보존한다')
print(json.dumps({'checks': x.f.checks, 'evidence': str(x.f.case), 'copyPolicyUsed': False, 'actualWindows': False}, ensure_ascii=False))
