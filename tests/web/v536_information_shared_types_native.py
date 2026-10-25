"""Original consent and source identities survive the private sequential overlay."""
import copy
import hashlib
import json
import v536_information_shared_types_fixture as x

request=x.request();held=copy.deepcopy(request);result=x.n.prepare(request)
assert request==held
updates=result['updates']+result['linkedUpdates']
assert len({r['id'] for r in updates})==len(updates)
x.verify_rows({r['id']:{'draft':r['text']} for r in updates})
for row in result['linkedUpdates']:
    assert row['hash']==hashlib.sha256(request['units'][row['id']]['draft'].encode()).hexdigest()
x.unchanged();x.f.checked('두 값 타입과 명시 callee/caller 대체를 원래 hash 한 개씩 가진 순수 후보로 결합한다')
reverse=copy.deepcopy(request);reverse['changes'].reverse();other=x.n.prepare(reverse)
assert {r['id']:r['text'] for r in updates}=={r['id']:r['text'] for r in other['updates']+other['linkedUpdates']}
x.f.checked('서로 독립된 두 선택의 순서를 바꿔도 동일한 최종 그래프와 사용자 C# 원문을 보존한다')
scalars=copy.deepcopy(request)
for row,typ,literal in zip(scalars['changes'],['bool','double'],['true','1.25']):
    row['signature']['args'][0]['type']=typ
    next(iter(row['mapping']['callers'].values()))['inputs']['amount']={'valueJson':literal}
scalar_result=x.n.prepare(scalars)
scalar_graph=json.loads(next(r['text'] for r in scalar_result['linkedUpdates'] if r['id']==x.n.caller+'Body/body:common'))
assert [r['arguments']['amount']['constant'] for r in scalar_graph['nodes']]==[True,1.25]
x.unchanged();x.f.checked('서로 다른 bool/double 명시 값도 기존 타입 검사로 결합하며 long C# 입력과 원문을 변환하지 않는다')
for fault in ['hash','before','missing-use','value','disconnect','source','edge','postCall','return','role','callee-hash']:
    bad=copy.deepcopy(request);mapping=bad['changes'][1]['mapping'];caller=next(iter(mapping['callers'].values()));use=next(iter(mapping['implementations'].values()))
    if fault=='hash':caller['hash']='0'*64
    elif fault=='before':use['before']='{"input":"other"}'
    elif fault=='missing-use':mapping['implementations']={}
    elif fault=='value':caller['inputs']['amount']={'valueJson':'9223372036854775806'}
    elif fault=='disconnect':caller['disconnect']={}
    elif fault=='return':bad['changes'][1]['signature']['return']='string'
    elif fault=='role':bad['changes'][1]['signature']['args'][0]['mode']='ref'
    elif fault=='callee-hash':use['hash']='0'*64
    else:
        unit=bad['units'][x.n.caller+'Body/body:common'];g=json.loads(unit['draft'])
        if fault=='source':g['nodes'][1]['intent']='새 선택이 필요한 변경'
        elif fault=='edge':g['edges'][0]['to']='exit:return'
        else:g['nodes'][0]['postCall']={'source':'return;'}
        unit['draft']=json.dumps(g)
    x.n.prepare(bad,False);x.unchanged()
x.f.checked('두 번째 선택의 오래된 hash/원문·누락·타입·연결·역할·반환·source/edge 변경은 전체 거절한다')
print(json.dumps({'checks':x.f.checks,'evidence':str(x.f.case),'copyPolicyUsed':False,'actualWindows':False},ensure_ascii=False))
