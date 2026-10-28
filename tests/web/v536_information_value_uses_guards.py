"""Whole candidate alias/storage guards and semantic assembly; no file writes."""
import copy,json,re
import v536_information_value_uses_fixture as c
x,f,n,owner,fn=c.x,c.f,c.n,c.owner,c.fn
gid=fn+'Body/body:common'
def request():
 r=n.request(x.new,x.mapping['args']);p={k:f.metadata(op,id=owner,function=fn,units=r['units']) for k,op in [('functionInputs','informationFunctionInputs'),('functionInputUses','informationFunctionInputUses')]};assert len(p['functionInputUses'])==5;r['changes'][0]['mapping']=x.selections(p);return r
try:
 r=request();candidate=n.prepare(r);rows={v['id']:v for v in candidate['linkedUpdates']};g=json.loads(rows[gid]['text']);assert g['locals'][0]['source']=={'input':'count'} and g['locals'][1]==c.original_graphs['common']['locals'][1]
 records={'body':json.loads(rows[gid+'/node:body']['text'])};source=next(v['text'] for v in candidate['updates'] if v['id']==fn)
 ready=f.metadata('featureBlueprintAssemble',featureSource=source,graph=g,featureContracts={c.c.leaf:c.c.leaf_source},implementations=records);assert ready['state']=='source-assembled',ready
 assert records['body']['source']==n.record['source'] and 'count' in ready['body'];f.checked('whole value replacements assemble with live count storage alias, unchanged C# and exact independent local initializer')
 bad=copy.deepcopy(r);g=json.loads(bad['units'][gid]['draft']);g['locals'].append({'id':'other_alias','name':'다른 별칭','type':'long','source':{'input':'count'}});bad['units'][gid]['draft']=json.dumps(g)
 for p in bad['changes'][0]['mapping']['implementations'].values():p['hash']=n.h(bad['units'][gid]['draft'])
 n.prepare(bad,False);f.checked('alias retarget never merges another existing storage name; the entire candidate refuses and originals remain')
 live=copy.deepcopy(r);g=json.loads(live['units'][gid]['draft']);g['nodes'].append({'id':'write','kind':'set','control':'next','intent':'선택한 저장소에 쓰기','local':'root_alias','outputLocal':'kept','signature':{'args':[{'name':'value','type':'long'}],'return':'void'},'arguments':{'value':{'input':'amount'}}});g['edges']=[{'from':'inner','port':'next','to':'write'},{'from':'write','port':'next','to':'body'},*g['edges'][1:]];live['units'][gid]['draft']=json.dumps(g)
 defs=f.metadata('featureBlueprintNodes',featureSource=live['units'][fn]['draft'],graph=g,featureContracts={c.c.leaf:c.c.leaf_source});record=json.loads(live['units'][gid+'/node:body']['draft']);record['definitionHash']=next(v['definitionHash'] for v in defs['nodes'] if v['id']=='body');live['units'][gid+'/node:body']['draft']=json.dumps(record)
 p={k:f.metadata(op,id=owner,function=fn,units=live['units']) for k,op in [('functionInputs','informationFunctionInputs'),('functionInputUses','informationFunctionInputUses')]};live['changes'][0]['mapping']=x.selections(p);out=n.prepare(live);rows={v['id']:v for v in out['linkedUpdates']};g=json.loads(rows[gid]['text']);assert next(v for v in g['nodes'] if v['id']=='write')['local']=='root_alias'
 ready=f.metadata('featureBlueprintAssemble',featureSource=source,graph=g,featureContracts={c.c.leaf:c.c.leaf_source},implementations={'body':json.loads(rows[gid+'/node:body']['text'])});(f.case/'alias-set-assembled.json').write_text(json.dumps(ready,ensure_ascii=False,indent=2));assert ready['state']=='source-assembled';temporary=re.search(r'long (\w+_set_value) = 9223372036854775806L;',ready['body']);assert temporary,ready['body'];assert 'count = '+temporary[1]+';' in ready['body'];assert len(re.findall(r'\w+ = '+temporary[1]+r';',ready['body']))==2;assert 'outputLocal' in next(v for v in g['nodes'] if v['id']=='write')
 f.checked('Set writes to the selected live root storage while retaining its separate output snapshot and original C#')
 assert all((f.project/p).read_bytes()==b for p,b in x.snapshot.items())
finally:
 print(json.dumps({'checks':f.checks,'evidence':str(f.case),'pureCandidate':True,'nativeWindows':False,'projectRun':False},ensure_ascii=False));f.stop()
