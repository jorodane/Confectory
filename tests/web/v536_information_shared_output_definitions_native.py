"""All original writer/routes and consumers must agree before any staging."""
import copy
import hashlib
import json
import v536_information_shared_output_definitions_fixture as x

request = x.request()
held = copy.deepcopy(request)
result = x.n.prepare(request)
assert request == held
updates = result['updates'] + result['linkedUpdates']
assert len({p['id'] for p in updates}) == len(updates)
x.verify_rows({p['id']: {'draft': p['text']} for p in updates})
for row in result['linkedUpdates']:
    assert row['hash'] == hashlib.sha256(request['units'][row['id']]['draft'].encode()).hexdigest()
x.unchanged()
x.f.checked('명시 출력 정의·writer·공유 소비자는 원래 hash 하나씩 가진 결합 후보이며 원본은 그대로다')
reverse = copy.deepcopy(request)
reverse['changes'].reverse()
other = x.n.prepare(reverse)
assert {p['id']: p['text'] for p in updates} == {p['id']: p['text'] for p in other['updates'] + other['linkedUpdates']}
x.f.checked('편집 역순도 같은 최종 계약·import·연결·출력이고 C# 원문과 정확한 값을 유지한다')
single = copy.deepcopy(request)
single['changes'] = single['changes'][:1]
intermediate = next(p['text'] for p in x.n.prepare(single)['linkedUpdates'] if p['id'] == x.n.caller+'Body/body:common')
faults = ['intermediate-hash', 'missing-graph', 'graph-hash', 'caller-input', 'drop-consumed', 'body', 'source', 'input-type', 'role']
if x.removed:
    faults += ['incomplete-writers', 'exit-before', 'public-output']
if x.added:
    faults += ['source-value', 'insertion', 'new-node-identity']
for fault in faults:
    bad = copy.deepcopy(request)
    row = bad['changes'][1]
    mapping = row['mapping']
    caller = next(iter(mapping['callers'].values()))
    graph = next(iter(mapping['outputGraphs'].values()))
    if fault == 'intermediate-hash':
        caller['hash'] = hashlib.sha256(intermediate.encode()).hexdigest()
    elif fault == 'missing-graph':
        mapping['outputGraphs'] = {}
    elif fault == 'graph-hash':
        graph['hash'] = '0' * 64
    elif fault == 'caller-input':
        caller['inputs']['amount'] = 'real'
    elif fault == 'drop-consumed':
        caller['outputs'][x.consumed] = None
    elif fault == 'body':
        mapping['bodies'] = {}
    elif fault == 'source':
        unit = bad['units'][x.n.caller+'Body/body:common']
        value = json.loads(unit['draft'])
        value['nodes'][1]['intent'] = '선택 후 다른 문맥'
        unit['draft'] = json.dumps(value)
    elif fault == 'input-type':
        row['signature']['args'][0]['type'] = 'double'
    elif fault == 'role':
        row['signature']['args'][0]['mode'] = 'ref'
    elif fault == 'incomplete-writers':
        graph['removes'][0]['writers'] = []
    elif fault == 'exit-before':
        graph['removes'][0]['before'] = 'changed'
    elif fault == 'public-output':
        graph['publicOutputs'] = ['unselected']
    elif fault == 'source-value':
        graph['creates'][0]['source'] = {'valueJson': '{}'}
    elif fault == 'insertion':
        graph['creates'][0]['next'] = 'wrong-route'
    elif fault == 'new-node-identity':
        graph['creates'][0]['node'] = 'body'
    x.n.prepare(bad, False)
    x.unchanged()
x.f.checked('마지막 함수의 writer/경로/값/소비 대응 및 실제 source 오류는 첫 함수도 적용하지 않는다')
print(json.dumps({'checks': x.f.checks, 'kind': x.kind, 'evidence': str(x.f.case), 'copyPolicyUsed': False, 'actualWindows': False}, ensure_ascii=False))
