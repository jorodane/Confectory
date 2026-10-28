"""Explicit general call ABI maps; pure owned candidates, no writes/accounts/run."""
import copy,json,os,pathlib,subprocess,sys
repo=pathlib.Path(sys.argv[1]).resolve();dotnet=os.environ.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet');dll=repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'
def call(operation,ok=True,**data):
 p=subprocess.run([dotnet,str(dll)],input=json.dumps(dict(operation=operation,**data)),text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,(operation,v);return v.get('result') if ok else v
n='Owned.Abi::';fn='function '+n+'Calc (long amount,bool ready) -> long {}';before='function '+n+'Native (ref long seed,bool enabled,out long count) -> long {}';after='function '+n+'Native (bool active,long value,int step,out long total,out bool changed) -> long {}'
b=call('blueprintPrepareFeature',id=n+'Calc',text=fn,implementation=n+'Caller',graphPath='common.graph.json',nodePath='common.node.json');b=call('blueprintPrepareCall',id=n+'Caller',text=b['implementation'],targetText=before,graph=b['graph'],definition=dict(id='native',feature=n+'Native',intent='명시적 핀 대응',control='next'));g=b['graph'];g['profile']='sync-acyclic-switch-v1';g['entry']='native';g['edges'].append(dict(**{'from':'native','port':'next','to':'body'}));node=next(x for x in g['nodes'] if x['id']=='native');node['arguments']={'seed':{'input':'amount'},'enabled':{'input':'ready'}};next(x for x in g['nodes'] if x['id']=='body')['arguments']={'amount':{'node':'native','output':'count'},'ready':{'input':'ready'}};enum=dict(primary='next',members=[dict(id='next',name='NoBranch',value=0)]);w=call('blueprintCallWrapper',functionText=before,executionEnum=enum,returnMapping='native-return-out-v1',source='return Result.NoBranch;');node.update(control='switch',executionEnum=enum,postCall=dict(mode='execution-enum',returnMapping='native-return-out-v1',contractHash=w['contractHash'],source=w['source'],helpers='// 사용자의 한글 코드'))
def sig(text):return {'args':[dict(type='bool',name='active'),dict(type='long',name='value'),dict(type='int',name='step'),dict(type='long',name='total',mode='out'),dict(type='bool',name='changed',mode='out')],'return':'long'}
request=dict(id=n+'Caller',text=b['implementation'],graph=g,node='native',signature=sig(after),contractHash='1'*64);original=copy.deepcopy(request);view=call('blueprintCallAbi',previewRemap=True,**request);assert view['requiresRemap'] and view['remap']=={'inputs':{'active':None,'value':None,'step':None},'outputs':{'return':'return','count':None}};call('blueprintCallAbi',False,**request);assert request==original;print('PASS general signature preview is unaccepted and unmatched pins are never guessed by ordinal; missing map rejects unchanged input')
remap={'inputs':{'active':'enabled','value':'seed','step':{'valueJson':'3'}},'outputs':{'return':'return','count':'total'}};result=call('blueprintCallAbi',remap=remap,**request);out=result['graph'];new=next(x for x in out['nodes'] if x['id']=='native');assert new['arguments']=={'active':{'input':'ready'},'value':{'input':'amount'},'step':{'constant':3}};assert next(x for x in out['nodes'] if x['id']=='body')['arguments']['amount']=={'node':'native','output':'total'};assert new['postCall']['source']==node['postCall']['source'] and new['postCall']['helpers']==node['postCall']['helpers'];assert out['edges']==g['edges'] and request==original;print('PASS explicit rename/order/value-ref/input addition and multi-out map change call/import/consumer identifiers together without source or route rewrites')
for kind in ['missing-input','duplicate-input','unknown-input','removed-bound','missing-output','duplicate-output','unknown-output','removed-consumed','raw-binding','ref-literal','partial-json']:
 q=copy.deepcopy(request);m=copy.deepcopy(remap)
 if kind=='missing-input':del m['inputs']['step']
 elif kind=='duplicate-input':m['inputs']['active']='seed'
 elif kind=='unknown-input':m['inputs']['value']='not-old'
 elif kind=='removed-bound':m['inputs']['active']={'valueJson':'true'}
 elif kind=='missing-output':del m['outputs']['count']
 elif kind=='duplicate-output':m['outputs']['return']='total'
 elif kind=='unknown-output':m['outputs']['count']='not-current'
 elif kind=='removed-consumed':m['outputs']['count']=None
 elif kind=='raw-binding':m['inputs']['step']={'node':'outside'}
 elif kind=='ref-literal':q['signature']['args'][2]['mode']='ref'
 else:m['inputs']['step']={'valueJson':'9223e'}
 call('blueprintCallAbi',False,remap=m,**q);assert request==original
print('PASS eleven incomplete/duplicate/unknown/consumed/type/storage/partial-value maps reject whole candidate without dropping bindings or mutating originals')
q=copy.deepcopy(request);q['signature']['args'][2]['type']='long';m=copy.deepcopy(remap);m['inputs']['step']={'valueJson':'9223372036854775806'};r=call('blueprintCallAbi',remap=m,**q);assert '9223372036854775806' in json.dumps(r['graph']);print('PASS explicit numeric literal retains exact 64-bit token')
# Current contract changed type; pure mapping preserves the binding and the real
# graph compiler, rather than a cast, is authoritative for final compatibility.
q=copy.deepcopy(request);q['signature']['args'][1]['type']='string';typed=after.replace('long value','string value');q['contractHash']=call('blueprintCallWrapper',functionText=typed,executionEnum=enum,returnMapping='native-return-out-v1',source=node['postCall']['source'])['contractHash'];r=call('blueprintCallAbi',remap=remap,**q);d=call('featureBlueprintDescribe',featureSource=fn,graph=r['graph'],featureContracts={n+'Native':typed},implementations={});assert d['state']=='invalid' and any(x['code']=='GRAPH_INPUT_TYPE' for x in d['diagnostics']),d;print('PASS incompatible mapped types remain a rejected graph; no automatic cast or connection deletion')
q=copy.deepcopy(request);q['signature']={'args':[{'type':'long','name':'seed','mode':'ref'},{'type':'bool','name':'enabled'},{'type':'long','name':'count','mode':'out'}],'return':'void'}
void=before.replace('-> long','-> void');current=call('blueprintCallWrapper',functionText=void,executionEnum=enum,source=node['postCall']['source']);q['contractHash']=current['contractHash']
r=call('blueprintCallAbi',remap={'inputs':{'seed':'seed','enabled':'enabled'},'outputs':{'return':None,'count':'count'}},**q)
assert any(n['id']=='native' and n['postCall']['returnMapping'] is None for n in r['graph']['nodes'])
nodes=call('featureBlueprintNodes',featureSource=fn,graph=r['graph'],featureContracts={n+'Native':void});assert nodes['state']=='node-definitions' and next(n for n in nodes['nodes'] if n['id']=='native')['postCallEditor']['returnMapping'] is None,nodes
print('PASS unused native return can be explicitly removed while consumed out binding survives; void wrapper mapping is validated')
print(json.dumps({'checks':6,'pureMetadata':True,'sourceWrites':False,'actualWindows':False,'accountOrInference':False}))
