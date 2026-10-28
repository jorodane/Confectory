"""No implicit new output or C# signature rewrite; fixture-only pure candidates."""
import copy
import json
import v536_information_output_types_fixture as x


def request(signature):
    r = x.n.request(signature, x.remap)
    preview = {'functionInputs': x.f.metadata('informationFunctionInputs', id=x.owner, function=x.fn, units=r['units']), 'functionOutputs': x.f.metadata('informationFunctionOutputs', id=x.owner, function=x.fn, units=r['units'])}
    r['changes'][0]['mapping'] = x.selections(preview)
    return r


# Previously reproduced: adding an out with no selected assignment returned a
# successful pure candidate. Never applied it or changed a user's source.
added = copy.deepcopy(x.old)
added['args'].append({'name': 'added', 'type': 'long', 'mode': 'out'})
r = request(added)
r['changes'][0]['mapping'].pop('outputs')
for plan in r['changes'][0]['mapping']['callers'].values():
    plan['outputs'] = {'return': 'return', 'count': 'count'}
x.n.prepare(r, False)
assert all((x.f.project / p).read_bytes() == b for p, b in x.snapshot.items())
print('PASS 값 선택 없는 출력 추가는 명시 대응 map만으로 통과하지 않고 전체 미적용이다', flush=True)

graph_file = x.f.project / 'caller.graph.json'
before = graph_file.read_bytes()
try:
    g = json.loads(before)
    g['profile'] = 'sync-acyclic-methods-v1'
    function = (x.f.project / ('elements/' + x.fn.split('::')[1] + '.celem')).read_text()
    after = x.f.metadata('blueprintCallAfter', functionText=function, source='return @context.@count; // 기존 형식/원문 보존')
    g['nodes'][0]['postCall'] = {k: after[k] for k in ['contractHash', 'source', 'helpers']}
    graph_file.write_text(json.dumps(g))
    described = x.f.metadata('featureBlueprintDescribe', featureSource=(x.f.project / 'Caller.celem').read_text(), featureContracts={x.fn: function}, graph=g, implementations={})
    assert described['state'] == 'source-ready', described
    original_cpp = g['nodes'][0]['postCall']['source']
    x.n.prepare(request(x.new), False)
    assert json.loads(graph_file.read_text())['nodes'][0]['postCall']['source'] == original_cpp
finally:
    graph_file.write_bytes(before)
assert all((x.f.project / p).read_bytes() == b for p, b in x.snapshot.items())
print('PASS 유효한 기존 C# After의 formal 계약 변경은 자동 재작성/재결합하지 않고 source를 보존해 거절한다', flush=True)
print(json.dumps({'checks': 2, 'evidence': str(x.f.case), 'pureCandidate': True, 'actualWindows': False}, ensure_ascii=False))
