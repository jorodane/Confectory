"""Original disconnect proofs survive only explicitly projected producer outputs."""
import copy
import hashlib
import json
import v536_information_shared_io_fixture as x

r=x.request();result=x.n.prepare(r);updates=result['updates']+result['linkedUpdates']
(x.f.case/'prepared-candidate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
assert len({row['id'] for row in updates})==len(updates)
x.verify_rows({row['id']:{'draft':row['text']} for row in updates})
assert all(row['hash']==hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest() for row in updates)
x.unchanged();x.f.checked('두 입력/out 타입·명시 값·writer·해제·출력 대응은 원래 hash 하나씩의 후보로 준비한다')
reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.n.prepare(reverse)
assert {row['id']:row['text'] for row in updates}=={row['id']:row['text'] for row in other['updates']+other['linkedUpdates']}
second=next(iter(r['changes'][1]['mapping']['callers'].values()))
assert json.loads(second['disconnect']['amount'])=={'node':'invoke','output':'count'}
x.f.checked('생산자 대응 뒤에 해제하는 연결은 원래 증거를 보존하고 역순도 같은 결과·정확64비트·C# 원문을 만든다')
scalars=copy.deepcopy(r);scalars['changes'][0]['signature']['args'][0]['type']='bool';scalars['changes'][0]['signature']['args'][2]['type']='string'
for plan in scalars['changes'][0]['mapping']['callers'].values():plan['inputs']['amount']={'valueJson':'true'}
for plan in scalars['changes'][0]['mapping']['outputs'].values():plan.update(type='string',source={'valueJson':'"명시한 출력 😀"'})
scalar_result=x.n.prepare(scalars);scalar_rows={row['id']:row['text'] for row in scalar_result['updates']+scalar_result['linkedUpdates']}
scalar_caller=json.loads(scalar_rows[x.n.caller+'Body/body:common']);assert scalar_caller['nodes'][0]['arguments']['amount']=={'constant':True}
scalar_leaf=json.loads(scalar_rows[x.functions[0]+'Body/body:common']);assert next(row for row in scalar_leaf['nodes'] if row['kind']=='export' and row['output']=='count')['arguments']=={'value':{'constant':'명시한 출력 😀'}}
x.unchanged();x.f.checked('서로 다른 bool/string·string/double 조합도 명시 literal과 같은 후보의 기존 타입 검사로 준비한다')
single=copy.deepcopy(r);single['changes']=single['changes'][:1];intermediate=x.n.prepare(single)
graph=next(row['text'] for row in intermediate['linkedUpdates'] if row['id']==x.n.caller+'Body/body:common')
for fault in ['projected-proof','intermediate-hash','missing-disconnect','wrong-disconnect','missing-use','bad-use','bad-output','missing-writer','role','count','return','mixed-group','body','source']:
    bad=copy.deepcopy(r);row=bad['changes'][1];mapping=row['mapping'];caller=next(iter(mapping['callers'].values()))
    if fault=='projected-proof':caller['disconnect']['amount']='{"node":"invoke"}'
    elif fault=='intermediate-hash':caller['hash']=hashlib.sha256(graph.encode()).hexdigest()
    elif fault=='missing-disconnect':caller['disconnect']={}
    elif fault=='wrong-disconnect':caller['disconnect']['amount']='{"constant":7}'
    elif fault=='missing-use':mapping['implementations']={}
    elif fault=='bad-use':next(iter(mapping['implementations'].values()))['value']={'valueJson':'"long 아닌 값"'}
    elif fault=='bad-output':caller['outputs']['count']='count'
    elif fault=='missing-writer':mapping['outputs']={}
    elif fault=='role':row['signature']['args'][2]['mode']='ref'
    elif fault=='count':row['signature']['args'].append({'name':'new','type':'long'})
    elif fault=='return':row['signature']['return']='double'
    elif fault=='mixed-group':row['signature']['args'][0]['type']='long';mapping['args']['amount']='amount';mapping.pop('implementations')
    elif fault=='body':mapping['bodies']={}
    else:
        unit=bad['units'][x.n.caller+'Body/body:common'];g=json.loads(unit['draft']);g['nodes'][1]['intent']='실제 선택 후 변경';unit['draft']=json.dumps(g)
    x.n.prepare(bad,False);x.unchanged()
x.f.checked('이미 투영한/누락/잘못된 해제 증거·중간 hash·값/writer 오류·역할/수/반환/본문·문맥 변경은 전체 미적용이다')
path=x.f.project/'caller.graph.json';held=path.read_bytes()
try:
    changed=json.loads(held);changed['nodes'][0]['intent']='peer 물리 변경';path.write_text(json.dumps(changed));x.n.prepare(r,False)
    assert all((x.f.project/p).read_bytes()==raw for p,raw in x.snapshot.items() if p!='caller.graph.json')
finally:path.write_bytes(held)
x.unchanged();x.f.checked('실제 source 변경은 내부 투영과 구별하여 전체 거절하고 기존 입력/원문을 유지한다')
print(json.dumps({'checks':x.f.checks,'evidence':str(x.f.case),'copyPolicyUsed':False,'actualWindows':False},ensure_ascii=False))
