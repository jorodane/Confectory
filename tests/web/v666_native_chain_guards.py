"""Exact registered body receipt, read scope, owned member and rejection guards."""
import copy,json,subprocess,hashlib
import v666_native_chain_fixture as x
f=x.f
def rpc(action,**kw):return f.invoke('blueprint',dict(action=action,**kw))['result']['result']
def validate(units,ok):
 (f.case/'current-guard-request.json').write_text(json.dumps(dict(units=units,expected=ok),ensure_ascii=False,indent=2));p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationBodyGroupGuards',action='validate',project=str(f.manifest),namespace=f.n[:-2],units=units,selected=[x.owner])),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});cp=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));f.invoke('schema',dict(id=x.owner));s=f.state()['schema'];basis=rpc('readOwnerEdits',id=x.owner,hash=s['textHash']);r=x.request();rpc('applySlots',id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=s['textHash'],changes=r['changes']));x.verify(cp);saved=cp.read_bytes();units=copy.deepcopy(r['units'])
 for row in json.loads(saved)['changes']:units[row['id']]=row
 (f.case/'captured-guard-request.json').write_text(json.dumps(dict(operation='informationBodyGroupGuards',action='validate',project=str(f.manifest),namespace=f.n[:-2],units=units,selected=[x.owner]),ensure_ascii=False,indent=2))
 def graphscope(selected,ok):
  request=dict(operation='informationBodyGroupGuards',action='graphs',project=str(f.manifest),namespace=f.n[:-2],units=selected,selected=[x.owner]);p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(request),env=f.env,text=True,capture_output=True,check=True);value=json.loads(p.stdout);assert bool(value['ok'])==ok,value
 graphscope(units,True)
 for fault in ['header-scope','import-scope','body-proof','function-proof']:
  bad=copy.deepcopy(units);header=x.first+'Body';member=header if fault.endswith('scope')else header+'/body:common'if fault=='body-proof'else x.first
  if fault=='header-scope':bad[member]['draft']=bad[member]['draft'].replace('as Second','as RenamedSecond')
  elif fault=='import-scope':bad[member]['draft']=bad[member]['draft'].replace('as Second (string','as Second (long')
  else:bad[member]['draft']+='\n// changed captured source'
  if fault.endswith('scope'):bad[x.owner]['slotSaveReceipt']['sources'][member]['hash']=hashlib.sha256(bad[member]['draft'].encode()).hexdigest()
  graphscope(bad,False);assert cp.read_bytes()==saved;x.unchanged()
 f.checked('cold graph discovery authenticates the selected callee/consumer source set and exact native import/header delta; forged scope and body/function changes reject')
 result=validate(units,True);receipt=units[x.owner]['slotSaveReceipt'];assert result['result']['reads']==receipt['nativeBodyDependencyReads'];assert not any(row['path'].endswith(('Stable.csbody','StableBody.celem'))for row in receipt['nativeBodyDependencyReads']);f.checked('captured exact registered declaration/parent/registration observations are readonly final-CAS reads; no provider body or writable external member')
 redundant=copy.deepcopy(units);redundant[x.owner]['slotSaveReceipt'].pop('nativeBodyDependencies');assert validate(redundant,True)['result']['reads']==receipt['nativeBodyDependencyReads'];f.checked('an unchanged complete original declaration may authenticate a redundant missing capture field, without changing any saved read hash')
 for fault in ['proof','read','both','all-capture','missing-parent','rebase','extra-path','caller-hash','relocated','wrong-owner','missing-local','extra-member','fake-type-scope']:
  bad=copy.deepcopy(units);v=bad[x.owner]['slotSaveReceipt'];proof=v['nativeBodyDependencies'];reads=v['nativeBodyDependencyReads']
  if fault=='proof':
   v.pop('nativeBodyDependencies')
   for row in v['declaration']['changes']:row.get('mapping',{}).pop('dependencies',None)
  elif fault=='read':v.pop('nativeBodyDependencyReads')
  elif fault=='both':v.pop('nativeBodyDependencies');v.pop('nativeBodyDependencyReads')
  elif fault=='all-capture':
   v.pop('nativeBodyDependencies');v.pop('nativeBodyDependencyReads')
   for row in v['declaration']['changes']:row.get('mapping',{}).pop('dependencies',None)
  elif fault=='missing-parent':reads[:]=[row for row in reads if row['path']!=str(x.external_parent)]
  elif fault=='rebase':reads[0]['hash']='0'*64
  elif fault=='extra-path':reads.append(dict(path=str(x.foreign_root/'Stable.csbody'),hash='0'*64))
  elif fault=='caller-hash':next(iter(next(iter(proof.values())).values()))['callerHash']='0'*64
  elif fault=='relocated':reads[0]['path']=str(x.foreign_root/'unobserved.celem')
  elif fault=='wrong-owner':v['owner']=f.n+'Unknown'
  elif fault=='missing-local':v['readGuards'].pop(x.retained_header)
  elif fault=='extra-member':v['sources'][x.external_helper]=dict(kind='function',path=str(x.external_function),hash='0'*64)
  elif fault=='fake-type-scope':
   v.pop('nativeBodyDependencies');v.pop('nativeBodyDependencyReads');v['nativeTypeProofs']={'$function:'+x.functions[0]:dict(shapeHash='0'*64,sources={})};v['nativeTypeReads']=[]
   for row in v['declaration']['changes']:row.get('mapping',{}).pop('dependencies',None)
  validate(bad,False);assert cp.read_bytes()==saved;x.unchanged();f.checked(fault+' tampering rejects without changing source, checkpoint or external permissions')
 validate(units,True)
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
