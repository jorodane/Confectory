"""Out and return closures retain original source proofs before composition."""
import copy
import hashlib
import json
import v536_information_shared_output_return_mix_fixture as x

r = x.request()
singles = []
for row in r['changes']:
    single = copy.deepcopy(r); single['changes'] = [row]; singles.append(x.n.prepare(single))
x.unchanged(); x.f.checked('out/반환 결합의 원래 단일 후보는 각각 유효하고 원본은 그대로다')
if x.mode.endswith('reproduce'):
    x.n.prepare(r, False); x.unchanged(); x.f.checked('기존 그룹 가드는 유효한 out/반환 타입 편집의 결합을 거절한다')
else:
    result = x.n.prepare(r); updates = result['updates']+result['linkedUpdates']
    (x.f.case/'prepared-candidate.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    x.verify_rows({row['id']: {'draft': row['text']} for row in updates})
    assert len({row['id'] for row in updates}) == len(updates)
    assert all(row['hash'] == hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest() for row in updates)
    reverse = copy.deepcopy(r); reverse['changes'].reverse(); other = x.n.prepare(reverse)
    assert {row['id']: row['text'] for row in updates} == {row['id']: row['text'] for row in other['updates']+other['linkedUpdates']}
    x.unchanged(); x.f.checked('한 후보·역순·원래 hash는 writer/공유 소비·기존 입력·정확64비트·C# 원문을 보존한다')
    scalars = copy.deepcopy(r)
    for row, typ, literal in zip(scalars['changes'], ['bool', 'string'], ['true', '"한글 반환 😀"']):
        for writer in row['mapping']['outputs'].values():
            writer.update(type=typ, source={'valueJson': literal})
            if writer['name'] == 'return': row['signature']['return'] = typ
            else: next(a for a in row['signature']['args'] if a['name'] == writer['name'])['type'] = typ
    scalar_result = x.n.prepare(scalars)
    for row, typ, value in zip(scalars['changes'], ['bool', 'string'], [True, '한글 반환 😀']):
        leaf = json.loads(next(p['text'] for p in scalar_result['linkedUpdates'] if p['id'] == row['id']+'Body/body:common'))
        for writer in row['mapping']['outputs'].values():
            node = next(p for p in leaf['nodes'] if p['kind'] == 'export' and p['output'] == writer['name'])
            assert node['arguments'] == {'value': {'constant': value}} and node['signature']['args'][0]['type'] == typ
        stable = next(p for p in leaf['nodes'] if p['kind'] == 'export' and p['output'] == 'stable')
        assert stable == next(p for p in x.graphs[row['id']]['nodes'] if p['kind'] == 'export' and p['output'] == 'stable')
    x.unchanged(); x.f.checked('명시 bool/한글 string writer도 같은 타입 규칙과 호환 소비 대응으로 준비하며 기존 출력을 보존한다')
    intermediate = next(p['text'] for p in singles[0]['linkedUpdates'] if p['id'] == x.n.caller+'Body/body:common')
    for fault in ['intermediate-hash', 'writer-before', 'writer-source', 'missing-writer', 'missing-consumer', 'wrong-consumer',
                  'input-type', 'input-plan', 'disconnect', 'name', 'order', 'role', 'void', 'remove', 'body', 'source']:
        bad = copy.deepcopy(r); row = bad['changes'][1]; mapping = row['mapping']; caller = next(iter(mapping['callers'].values()))
        if fault == 'intermediate-hash': caller['hash'] = hashlib.sha256(intermediate.encode()).hexdigest()
        elif fault == 'writer-before': next(iter(mapping['outputs'].values()))['before'] = 'null'
        elif fault == 'writer-source': next(iter(mapping['outputs'].values()))['source'] = {'input': 'amount'}
        elif fault == 'missing-writer': mapping['outputs'] = {}
        elif fault == 'missing-consumer': caller['outputs'].pop('count')
        elif fault == 'wrong-consumer': caller['outputs']['count'] = 'count'
        elif fault == 'input-type': row['signature']['args'][0]['type'] = 'string'; mapping['args']['amount'] = None
        elif fault == 'input-plan': caller['inputs']['amount'] = 'real'
        elif fault == 'disconnect': caller['disconnect'] = {'amount': json.dumps(x.graph['nodes'][1]['arguments']['amount'], separators=(',', ':'))}
        elif fault == 'name': row['signature']['args'][2]['name'] = 'renamed'; mapping['args']['count'] = 'renamed'
        elif fault == 'order': row['signature']['args'][2], row['signature']['args'][3] = row['signature']['args'][3], row['signature']['args'][2]
        elif fault == 'role': row['signature']['args'][2]['mode'] = 'ref'
        elif fault == 'void': row['signature']['return'] = 'void'
        elif fault == 'remove': row['signature']['args'].pop(); mapping['args']['stable'] = None
        elif fault == 'body': mapping['bodies'] = {}
        else:
            unit = bad['units'][x.n.caller+'Body/body:common']; graph = json.loads(unit['draft']); graph['nodes'][1]['intent'] = '실제 선택 변경'; unit['draft'] = json.dumps(graph)
        x.n.prepare(bad, False); x.unchanged()
    x.f.checked('writer/소비 누락·타입 오류·입력/이름/순서/역할/void/수/본문·source 변경은 전체 미적용이다')
    path = x.f.project/'caller.graph.json'; held = path.read_bytes()
    try:
        graph = json.loads(held); graph['nodes'][0]['intent'] = 'peer 물리 변경'; path.write_text(json.dumps(graph)); x.n.prepare(r, False)
        assert all((x.f.project/p).read_bytes() == raw for p, raw in x.snapshot.items() if p != 'caller.graph.json')
    finally:
        path.write_bytes(held)
    x.unchanged(); x.f.checked('실제 물리 source 경합은 전체 거절하고 원래 후보와 peer/사용자 입력을 유지한다')
print(json.dumps({'checks': x.f.checks, 'evidence': str(x.f.case), 'copyPolicyUsed': False, 'actualWindows': False}, ensure_ascii=False))
