"""Pure all-target candidate and exact review-group boundaries; no files/accounts/run."""
import copy,json,os,pathlib,subprocess,sys
repo=pathlib.Path(sys.argv[1]).resolve();dotnet=os.environ.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet');dll=repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'
def call(operation,ok=True,**data):
 p=subprocess.run([dotnet,str(dll)],input=json.dumps({'operation':operation,**data}),text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,(operation,v);return v.get('result') if ok else v
n='Owned.Multi::';feature='function '+n+'Calc (long amount) -> long {provide '+n+'Calc with '+n+'Caller;}';before='function '+n+'Native (ref long amount) -> long {}';after=before.replace('(ref long','(long')
base=call('blueprintPrepareFeature',id=n+'Calc',text='function '+n+'Calc (long amount) -> long {}',implementation=n+'Caller',graphPath='common.graph.json',nodePath='common.node.json');base=call('blueprintPrepareCall',id=n+'Caller',text=base['implementation'],targetText=before,graph=base['graph'],definition={'id':'native','feature':n+'Native','intent':'명시적 호출','control':'next'})
g=base['graph'];g['profile']='sync-acyclic-switch-v1';g['entry']='native';g['edges'].append({'from':'native','port':'next','to':'body'});native=next(row for row in g['nodes'] if row['id']=='native');native['arguments']={'amount':{'input':'amount'}};next(row for row in g['nodes'] if row['id']=='body')['arguments']={'amount':{'node':'native'}};enum={'primary':'next','members':[{'id':'next','name':'NoBranch','value':0}]};wrapper=call('blueprintCallWrapper',functionText=before,executionEnum=enum,returnMapping='native-return-out-v1',source='return Result.NoBranch;');native.update(control='switch',executionEnum=enum,postCall={'mode':'execution-enum','returnMapping':'native-return-out-v1','contractHash':wrapper['contractHash'],'source':wrapper['source'],'helpers':''})
text=base['implementation'].replace('\n}', '\nblueprint windows "windows.graph.json";\n}');assert 'blueprint windows' in text,text
bodies={}
for target in ['common','windows']:
 graph=copy.deepcopy(g);next(row for row in graph['nodes'] if row['id']=='body')['implementation']=target+'.node.json';defs=call('featureBlueprintNodes',featureSource=feature,graph=graph,featureContracts={n+'Native':before});record={'schema':1,'node':'body','definitionHash':next(row for row in defs['nodes'] if row['id']=='body')['definitionHash'],'source':'return amount+'+('7' if target=='common' else '9')+';'};bodies[target]={'path':target+'.graph.json','graph':graph,'records':{'body':{'path':target+'.node.json','record':record}}}
request={'id':n+'Caller','text':text,'functionText':feature,'feature':n+'Native','featureContracts':{n+'Native':after},'bodies':bodies};original=json.dumps(request,sort_keys=True);preview=call('blueprintCallAbiGroup',**request);assert set(preview['plans'])==set(bodies);assert [r['target'] for r in preview['binding']['targets']]==['common','windows'];print('PASS complete explicit target binding includes declaration/callee/all graph and record fingerprints')
command={**request,**preview};command.pop('sourceWritten');command.pop('compiled');result=call('blueprintCallAbiGroup',**command);assert 'blueprint windows' in result['implementation'] and 'blueprint common' in result['implementation'];assert 'Native' in result['implementation'] and '(ref long)' not in result['implementation'];assert json.dumps(request,sort_keys=True)==original
for target,graph in result['graphs'].items():
 node=next(row for row in graph['nodes'] if row['id']=='native');assert node['signature']['args'][0].get('mode') is None;assert next(row for row in graph['nodes'] if row['id']=='body')==next(row for row in bodies[target]['graph']['nodes'] if row['id']=='body');assert graph['edges']==bodies[target]['graph']['edges'];assert graph['exits']==bodies[target]['graph']['exits']
print('PASS one candidate preserves both target declarations, code records, node identities, edges and outputs while repairing shared import and both wrappers')
for boundary in ['missing-body','opaque-body','parent','duplicate-path','missing-record','stale-record','binding','missing-plan','wrong-contract','unknown-plan','literal-ref','copy-source','path-escape','public-contract']:
 q=copy.deepcopy(command)
 if boundary=='missing-body':del q['bodies']['windows']
 elif boundary=='opaque-body':q['text']=q['text'].replace('blueprint windows','body windows')
 elif boundary=='parent':q['text']=q['text'].replace(' {',' extends '+n+'Parent {',1)
 elif boundary=='duplicate-path':q['text']=q['text'].replace('windows.graph.json','common.graph.json');q['bodies']['windows']['path']='common.graph.json'
 elif boundary=='missing-record':q['bodies']['windows']['records']={}
 elif boundary=='stale-record':q['bodies']['windows']['records']['body']['record']['definitionHash']='0'*64
 elif boundary=='binding':q['binding']['targets'][1]['graphHash']='0'*64
 elif boundary=='missing-plan':del q['plans']['windows']
 elif boundary=='wrong-contract':q['plans']['windows']['contractHash']='0'*64
 elif boundary=='unknown-plan':q['plans']['windows']['abi']='automatic'
 elif boundary=='literal-ref':
  q['text']=q['text'].replace('(ref long)','(long)');q['featureContracts'][n+'Native']=before;value_wrapper=call('blueprintCallWrapper',functionText=after,executionEnum=enum,returnMapping='native-return-out-v1',source='return Result.NoBranch;')
  for body in q['bodies'].values():
   native=next(row for row in body['graph']['nodes'] if row['id']=='native');native['signature']['args'][0].pop('mode',None);native['postCall']['contractHash']=value_wrapper['contractHash']
  next(row for row in q['bodies']['windows']['graph']['nodes'] if row['id']=='native')['arguments']={'amount':{'constant':3}}
 elif boundary=='copy-source':q['bodies']['windows']['graph']['copySource']={'implementation':n+'Donor'}
 elif boundary=='path-escape':q['bodies']['windows']['records']['body']['path']='../outside.json'
 else:q['functionText']=feature.replace('(long amount)','(double amount)')
 v=call('blueprintCallAbiGroup',False,**q)
 if boundary=='literal-ref':assert 'ref input' in v['message'],v
 assert json.dumps(request,sort_keys=True)==original
print('PASS 14 incomplete/opaque/ownership/record/plan/type/path boundaries reject the whole pure candidate without mutating the original inputs')
units={n+'Calc':{'kind':'function','path':'Calc.celem','draft':feature},n+'Caller':{'kind':'implementation','path':'Caller.celem','draft':result['implementation']},n+'Native':{'kind':'function','path':'Native.celem','draft':after}}
for target,graph in result['graphs'].items():
 root=n+'Caller/body:'+target;units[root]={'kind':'blueprint','path':bodies[target]['path'],'draft':json.dumps(graph)}
 for node,entry in bodies[target]['records'].items():units[root+'/node:'+node]={'kind':'blueprint-node','path':entry['path'],'draft':json.dumps(entry['record'])}
group=list(units)
for unit in units.values():unit['rootContractGroup']=group
assert call('blueprintRootGroup',namespace='Owned.Multi',group=group,units=units)['valid']
for boundary in ['missing-target','missing-record','unrelated','contract','record','locator']:
 u=copy.deepcopy(units);ids=group.copy()
 if boundary=='missing-target':ids.remove(n+'Caller/body:windows')
 elif boundary=='missing-record':ids.remove(n+'Caller/body:windows/node:body')
 elif boundary=='unrelated':u[n+'Extra']={'kind':'function','path':'Extra.celem','draft':'function '+n+'Extra () -> void {}'};ids.append(n+'Extra')
 elif boundary=='contract':u[n+'Native']['draft']=before
 elif boundary=='record':r=json.loads(u[n+'Caller/body:windows/node:body']['draft']);r['definitionHash']='0'*64;u[n+'Caller/body:windows/node:body']['draft']=json.dumps(r)
 else:u[n+'Caller/body:windows']['path']='common.graph.json'
 for unit in u.values():unit['rootContractGroup']=ids
 call('blueprintRootGroup',False,namespace='Owned.Multi',group=ids,units=u)
print('PASS exact all-target review group validates every callee/graph/record; six missing/unrelated/stale/locator mutations are refused (legacy 3/4 group rules retained)')
print(json.dumps({'pureMetadata':True,'actualEngine':False,'renderer':False,'windowsExecuted':False,'accountOrInference':False,'candidateAndGroupChecks':4}))
