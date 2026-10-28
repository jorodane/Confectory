"""Pure mixed targets: both source kinds remain one all-or-nothing candidate."""
import copy
import json
import v536_information_mixed_target_fixture as x

r = x.request()
prepared = x.n.prepare(r)
rows = {row['id']: row for row in prepared['linkedUpdates']}
for id, path in x.context_bodies.items():
    assert rows[id]['text'] == x.edited_files[path]
graph = json.loads(rows[x.fn + 'Body/body:common']['text'])
assert next(n for n in graph['nodes'] if n['id'] == 'body')['arguments'] == {'amount': {'input': 'count'}, 'count': {'input': 'count'}}
assert json.loads(rows[x.fn + 'Body/body:common/node:body']['text'])['source'] == x.n.record['source']
print('PASS 한 구현의 Blueprint/C# 및 호출자의 두 target을 원래 graph/source 증거·명시 매핑·한 후보에 결합한다', flush=True)
for fault in ['missing-code', 'last-code-error', 'last-graph-error', 'missing-use', 'old-graph', 'native-header', 'outside']:
    bad = x.request()
    m = bad['changes'][0]['mapping']
    if fault == 'missing-code':
        del m['bodies'][x.body_id]
    elif fault == 'last-code-error':
        m['bodies'][x.caller + 'Body/body:windows']['text'] = 'return missing;'
    elif fault == 'last-graph-error':
        next(iter(m['callers'].values()))['inputs']['text'] = 'amount'
    elif fault == 'missing-use':
        m['implementations'].clear()
    elif fault == 'old-graph':
        next(iter(m['implementations'].values()))['hash'] = '0' * 64
    elif fault == 'native-header':
        m['bodies'][x.body_id]['signature'] = x.old
    else:
        m['bodies']['Other.Project::Body/body:windows'] = copy.deepcopy(m['bodies'][x.body_id])
    x.n.prepare(bad, False)
    assert all((x.f.project / path).read_bytes() == before for path, before in x.snapshot.items())
print('PASS 마지막 graph/C# 오류·누락·오래된 증거·외부 본문은 전체 거절하며 모든 target·호출자·원문을 보존한다', flush=True)
print(json.dumps({'checks': 2, 'evidence': str(x.f.case), 'pureCandidate': True, 'executed': False}, ensure_ascii=False))
