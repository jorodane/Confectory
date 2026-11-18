"""Original unused return and an explicit private long-to-void return candidate."""
import copy,json,pathlib,subprocess,sys
import v666_private_node_void_fixture as x
f=x.f
try:
 r=x.request();metadata=f.metadata('informationFunctionBodies',**{k:r[k]for k in ['project','manifest','id','units']},function=x.whole_function,includeBlueprintTargets=True);assert metadata[x.whole_node].get('editableNativeReturn',False)==(x.mode not in ['consumed-original','local-consumed-original','argument-consumed-original']),metadata[x.whole_node]
 if x.mode=='unconverted-original':
  manual=next(iter(r['changes'][0]['mapping']['bodies'].values()));manual['text']=x.sources[x.whole_function];manual['helpers']=x.original_helpers
 (f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));x.execute(45 if x.mode in ['consumed-original','local-consumed-original'] else 40,'original-private-node-void')
 unchanged=copy.deepcopy(r);plan=next(iter(unchanged['changes'][0]['mapping']['bodies'].values()));plan['signature']=copy.deepcopy(x.code_signature);plan['text']=x.sources[x.whole_function];plan['helpers']=x.original_helpers;x.prepare(unchanged);x.unchanged();f.checked('unchanged private/native group validates and original unused-return program executes with original long return execution')
 if x.mode in ['reproduce','unconverted-original','consumed-original','local-consumed-original','argument-consumed-original']:
  reply=x.prepare(r,False);assert x.mode=='reproduce'or(x.mode=='unconverted-original'and'CS0127'in reply['message'])or(x.mode!='unconverted-original'and'Private return changes require an unused original output'in reply['message']),reply;(f.case/'group-rejection.json').write_text(json.dumps(reply,ensure_ascii=False,indent=2));x.unchanged();f.checked('private type candidate rejects without changing original return consumers/input bindings or sources')
 else:
  for row in r['changes']:one=copy.deepcopy(r);one['changes']=[row];x.prepare(one)
  result=x.prepare(r)['result'];rows=result['updates']+result['linkedUpdates'];x.verify_rows({v['id']:dict(draft=v['text'])for v in rows});reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.prepare(reverse)['result'];assert {v['id']:v['text']for v in rows}=={v['id']:v['text']for v in other['updates']+other['linkedUpdates']};x.unchanged();f.checked('single/group private unused void return candidate is order independent and keeps the original input bindings, parent frame/public/native ABI and all names')
  for fault in ['source-hash','flow-hash','wrong-before','second-type','role','return','count','permutation','name','public-contract','bad-source','helpers-boundary','last-body']:
   bad=copy.deepcopy(r);a,b=bad['changes'];p=next(iter(a['mapping']['bodies'].values()))
   if fault=='source-hash':p['hash']='0'*64
   elif fault=='flow-hash':p['whole']['hash']='0'*64
   elif fault=='wrong-before':p['beforeSignature']['args'][0]['name']='wrong'
   elif fault=='second-type':p['signature']['args'][0]['type']='double'
   elif fault=='role':p['signature']['args'][1]['mode']='ref'
   elif fault=='return':p['signature']['return']='float'
   elif fault=='count':p['signature']['args'].pop()
   elif fault=='permutation':p['signature']['args'].reverse()
   elif fault=='name':p['signature']['args'][1]['name']='inferredName'
   elif fault=='public-contract':a['signature']['args'][0]['name']='changedPublic'
   elif fault=='bad-source':p['text']='return MissingPrivateType;'
   elif fault=='helpers-boundary':p['helpers']='} class Escape {'
   elif fault=='last-body':next(iter(b['mapping']['bodies'].values()))['text']='return MissingLastBody;'
   x.prepare(bad,False);x.unchanged();f.checked(fault+' rejects without original writes')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
if x.mode=='normal':
 for mode in ['unconverted-original','consumed-original','local-consumed-original','argument-consumed-original']:subprocess.run([sys.executable,str(pathlib.Path(__file__).resolve()),*sys.argv[1:3],mode],check=True)
