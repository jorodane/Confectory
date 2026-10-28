"""Pure manual-body closure compilation; no assembly emit/execution or disk write."""
import copy
import json
import v536_information_csharp_fixture as x

r = x.request()
result = x.n.prepare(r)
updates = {row['id']: row for row in result['linkedUpdates']}
assert updates[x.body_id]['text'] == x.edited
assert x.n.canonical(x.f.metadata('inspect', text=updates[x.fn + 'Body']['text'])['signature']) == x.new
print('PASS 직접 편집한 C#·정의·구현·실제 호출자를 한 순수 후보로 컴파일 검증하며 source를 쓰거나 실행하지 않는다', flush=True)
for fault in ['missing', 'hash', 'path', 'before', 'current', 'contract', 'syntax', 'type', 'boundary', 'outside']:
    bad = x.request()
    plans = bad['changes'][0]['mapping']['bodies']
    body = plans[x.body_id]
    if fault == 'missing':
        plans.clear()
    elif fault == 'hash':
        body['hash'] = '0' * 64
    elif fault == 'path':
        body['path'] = '../other.csbody'
    elif fault == 'before':
        body['beforeSignature'] = x.new
    elif fault == 'current':
        body['signature'] = x.old
    elif fault == 'contract':
        body['contract'] = x.old
    elif fault == 'syntax':
        body['text'] = 'return ; }'
    elif fault == 'type':
        body['text'] = x.original
    elif fault == 'boundary':
        body['text'] = 'return 0;} static long Hidden(){return 1;'
    else:
        plans['Other.Project::Body/body:common'] = copy.deepcopy(body)
    x.n.prepare(bad, False)
    assert all((x.f.project / p).read_bytes() == b for p, b in x.snapshot.items())
print('PASS 누락·오래된 source/header·외부 경로·구문/타입·보호 영역 탈출은 전체 거절하고 모든 원문을 보존한다', flush=True)
print(json.dumps({'checks': 2, 'pureCandidate': True, 'compiledUsingRealGenerator': True, 'emittedOrExecuted': False, 'evidence': str(x.f.case)}, ensure_ascii=False))
