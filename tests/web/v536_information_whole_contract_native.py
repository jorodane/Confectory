"""Explicit native/public/return flow proof, pure candidate; no writes or Run."""
import copy
import json
import v536_information_whole_contract_fixture as x
r=x.request();prepared=x.n.prepare(r);rows={v['id']:v['text'] for v in prepared['linkedUpdates']}
assert json.loads(rows[x.body_id])['source']==x.edited
assert x.n.canonical(x.f.metadata('inspect',text=rows[x.fn+'Body'])['signature'])==x.selected
g=json.loads(rows[x.fn+'Body/body:common']);assert g['nodes'][0]['signature']==x.selected
assert len([n for n in g['nodes'] if n['kind']=='export'])==(0 if x.new['return']=='void' else 1)
if x.scenario=='types':assert g['outputOrder']==['total','return']
print('PASS '+x.scenario+' 명시 C# 타입/핀/out/반환과 positional 저장소·caller 출력이 한 후보로 연결된다',flush=True)
for fault in ['flow-hash','return-writer','native-roles','contract','syntax','compile','missing-callers','output-map','outside','extra-node','alias']:
    bad=copy.deepcopy(r);m=bad['changes'][0]['mapping'];b=m['bodies'][x.body_id]
    if fault=='flow-hash':b['whole']['hash']='0'*64
    elif fault=='return-writer':b['whole']['returnNode']='body'
    elif fault=='native-roles':b['signature']['args'].append({'name':'unexpected','type':'long'})
    elif fault=='contract':b['contract']=x.old
    elif fault=='syntax':b['text']='return ; }'
    elif fault=='compile':b['text']='return missing;'
    elif fault=='missing-callers':m['callers'].clear()
    elif fault=='output-map':next(iter(m['callers'].values()))['outputs']={}
    elif fault=='outside':m['bodies']['Other::Body/body:common/node:body']=copy.deepcopy(b)
    else:
        gid=x.fn+'Body/body:common';g=json.loads(bad['units'][gid]['draft'])
        if fault=='extra-node':g['nodes'].append({'id':'kept','kind':'code','control':'next'})
        else:g['locals']=[{'id':'kept','name':'keep alias','type':'long','source':{'input':'amount'}}]
        bad['units'][gid]['draft']=json.dumps(g);b['whole']['hash']=x.n.h(bad['units'][gid]['draft'])
    x.n.prepare(bad,False);assert all((x.f.project/p).read_bytes()==v for p,v in x.snapshot.items())
print('PASS '+x.scenario+' stale/형식·출력·호출자/컴파일 오류 및 기존 추가 노드·별칭은 전체 거절하고 원문을 보존한다',flush=True)
print(json.dumps({'checks':2,'scenario':x.scenario,'evidence':str(x.f.case),'pureCandidate':True,'executed':False},ensure_ascii=False))
