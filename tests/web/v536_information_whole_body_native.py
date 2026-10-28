"""Explicit whole-body value/ref candidate with retained native out storage."""
import copy
import json
import v536_information_whole_body_fixture as x
r=x.request()
p=x.n.prepare(r)
rows={v['id']:v['text'] for v in p['linkedUpdates']}
g=json.loads(rows[x.fn+'Body/body:common']);node=g['nodes'][0]
assert node['signature']==x.selected and node['arguments']=={'nativeAmount':{'input':'amount'}}
assert json.loads(rows[x.body_id])['source']==x.edited
assert x.n.canonical(x.f.metadata('inspect',text=rows[x.fn+'Body'])['signature'])==x.selected
print('PASS explicit whole-body/native aliases, retained out storage and caller ref binding share one candidate',flush=True)
for fault in ['missing','hash','native-name','contract','syntax','compile','caller','out-role','outside','storage','boundary','shared','copy-provenance']:
    bad=copy.deepcopy(r);m=bad['changes'][0]['mapping'];b=m['bodies'][x.body_id]
    if fault=='missing':m.pop('bodies')
    elif fault=='hash':b['hash']='0'*64
    elif fault=='native-name':b['signature']['args'][0]['name']='guessed'
    elif fault=='contract':b['contract']=x.old
    elif fault=='syntax':b['text']='return ; }'
    elif fault=='compile':b['text']='nativeTotal="wrong";return nativeAmount;'
    elif fault=='caller':m['callers'].clear()
    elif fault=='out-role':bad['changes'][0]['signature']['args'][1].pop('mode')
    elif fault=='outside':m['bodies']['Other::Fake/body:common/node:body']=copy.deepcopy(b)
    elif fault=='boundary':b['text']='nativeTotal=nativeAmount;return nativeAmount;\n}\npublic long Extra(){return 1;'
    elif fault=='shared':bad['units'][x.fn+'Other/body:common/node:body']=copy.deepcopy(bad['units'][x.body_id])
    elif fault=='copy-provenance':
        gid=x.fn+'Body/body:common';g=json.loads(bad['units'][gid]['draft']);g['copySource']={'implementation':'Other::Original','target':'common','bodyOrigin':'Other::Original','sourceKind':'csharp'};bad['units'][gid]['draft']=json.dumps(g)
    else:
        gid=x.fn+'Body/body:common';g=json.loads(bad['units'][gid]['draft']);g['nodes'][0]['arguments']['nativeAmount']={'constant':1};bad['units'][gid]['draft']=json.dumps(g)
    x.n.prepare(bad,False)
    assert all((x.f.project/path).read_bytes()==v for path,v in x.snapshot.items())
print('PASS missing text/mapping, stale source, compile/type/out-role/foreign/guessed storage reject every update',flush=True)
print(json.dumps({'checks':2,'evidence':str(x.f.case),'pureCandidate':True,'executed':False},ensure_ascii=False))
