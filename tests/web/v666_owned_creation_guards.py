"""Replay a new owned tree against original missing leases, never current files."""
import copy,json,hashlib,subprocess
import v666_owned_creation_fixture as x
f=x.f
def rpc(action,**body):return f.invoke('blueprint',dict(action=action,**body))['result']['result']
def metadata(units,action='validate',declaration=None,ok=True):
 request=dict(operation='informationBodyGroupGuards',action=action,project=str(f.manifest),namespace=f.n[:-2],units=units)
 if declaration is None:request['selected']=[x.owner]
 else:request['declaration']=declaration
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(request),env=f.env,text=True,capture_output=True,check=True);reply=json.loads(p.stdout);assert bool(reply['ok'])==ok,dict(fault=globals().get('fault'),reply=reply);return reply.get('result')
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});f.invoke('schema',dict(id=x.owner));s=f.state()['schema'];basis=rpc('readOwnerEdits',id=x.owner,hash=s['textHash']);request=x.request();rpc('applySlots',id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=s['textHash'],changes=request['changes']));checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));x.verify(checkpoint);units=copy.deepcopy(request['units'])
 for row in json.loads(checkpoint.read_text())['changes']:units[row['id']]=row
 saved=checkpoint.read_bytes();receipt=units[x.owner]['slotSaveReceipt'];metadata(units);assert all(receipt['readGuards'][path]['hash']=='missing'for path in x.owned_paths.values());f.checked('complete created marker/owner/path/registration and the declared missing source leases validate under the original complete native scope')
 for fault in ['missing-guards','missing-child-check','existing-baseline','original-text','creation-owner','path','missing-proof','missing-unit','changed-text','unclaimed-text','changed-marker','changed-registration','missing-plan','missing-reads','extra-proof','changed-plan','extra-guard','missing-native','missing-helper']:
  bad=copy.deepcopy(units);r=bad[x.owner]['slotSaveReceipt'];child=next(iter(x.owned_paths));path=x.owned_paths[child]
  if fault=='missing-guards':r.pop('readGuards')
  elif fault=='missing-child-check':r['readGuards'].pop(path)
  elif fault=='existing-baseline':bad[child]['baseline']='0'*64;r['readGuards'][path]['hash']='0'*64
  elif fault=='original-text':bad[child]['original']=bad[child]['draft']
  elif fault=='creation-owner':bad[child]['creationOwner']=f.n+'Other'
  elif fault=='path':bad[child]['path']='elsewhere.celem';r['sources'][child]['path']='elsewhere.celem'
  elif fault=='missing-proof':
   r['sources'].pop(child);group=list(bad[x.owner]['atomicEditGroup']);next_group=[id for id in group if id!=child]
   for unit in bad.values():
    if unit.get('atomicEditGroup')==group:unit['atomicEditGroup']=copy.deepcopy(next_group)
  elif fault=='missing-unit':bad.pop(child)
  elif fault in ['changed-text','unclaimed-text','changed-marker']:
   bad[child]['draft']=(bad[child]['draft']+'\n// forged saved source')if fault in ['changed-text','unclaimed-text']else bad[child]['draft'].replace('owned-nested-v1','unknown-nested-v1')
   if fault!='unclaimed-text':r['sources'][child]['hash']=hashlib.sha256(bad[child]['draft'].encode()).hexdigest()
  elif fault=='changed-registration':bad[f.n+'ProjectManifest']['draft']=bad[f.n+'ProjectManifest']['original'];r['sources'][f.n+'ProjectManifest']['hash']=hashlib.sha256(bad[f.n+'ProjectManifest']['draft'].encode()).hexdigest()
  elif fault=='missing-plan':r.pop('nativeBodyOwnerEdits')
  elif fault=='missing-reads':r.pop('nativeBodyOwnerReads')
  elif fault=='extra-proof':r['sources'][f.n+'Leaf2']=dict(kind='schema',path='Leaf2.celem',hash='0'*64)
  elif fault=='changed-plan':
   for plan in [r['nativeBodyOwnerEdits'],r['declaration']['changes']]:next(v for v in plan if v['type']=='owned-definition')['tree']['fields'].pop()
  elif fault=='extra-guard':r['readGuards']['unobserved.celem']=dict(path='unobserved.celem',hash='missing')
  elif fault=='missing-native':r['sources'].pop(x.functions[0]+'Body/body:common')
  elif fault=='missing-helper':r['readGuards'].pop(x.retained_file)
  print('CHECK '+fault,flush=True);(f.case/'current-guard-fault.json').write_text(json.dumps(dict(fault=fault,units=bad),ensure_ascii=False,indent=2));metadata(bad,ok=False);assert checkpoint.read_bytes()==saved;x.unchanged()
 f.checked('omitted/forged child, source lease, owner, marker, registration, complete plan/native/helper proof or unknown extra member rejects without acquiring source authority')
 current=copy.deepcopy(request);current.update(text=units[x.owner]['draft'],manifest=units[f.n+'ProjectManifest']['draft'],drafts=[dict(id=id,text=v['draft'])for id,v in units.items()if id!=x.owner and v.get('kind')in ['object','schema','function','implementation','module','category','concept','enum']and v.get('draft')]);model=x.model(current);field=model['fields'][x.root_key];row=x.owned_change();row.update(contract={k:field[k]for k in ['kind','cardinality','type']},schema=x.owner,schemaHash=field['schemaHash'],sources=copy.deepcopy(model['ownedDefinitions'][x.root_key]['sources']));row['tree']['fields'][0]['name']='명시 새 자식 이름';value=json.loads(row['valueJson']);value[x.power_key]=9223372036854775803;row['valueJson']=json.dumps(value,ensure_ascii=False);declaration=dict(id=x.owner,hash=hashlib.sha256(units[x.owner]['draft'].encode()).hexdigest(),changes=[row]);prepared=metadata(units,action='prepare',declaration=declaration);assert prepared['required']and prepared['reads']==receipt['nativeBodyOwnerReads'];retained=next(v for v in prepared['ownerEdits']if v['type']=='owned-definition');assert all(retained[k]==next(v for v in receipt['nativeBodyOwnerEdits']if v['type']=='owned-definition')[k]for k in ['contract','schema','schemaHash','sources'])and json.loads(retained['valueJson'])[x.power_key]==9223372036854775803;assert{v['path']:v['hash']for v in prepared['checks']}=={k:v['hash']for k,v in receipt['readGuards'].items()}
 for fault in ['basis','sources','new-child','type','root-contract','overflow']:
  bad=copy.deepcopy(declaration);r=bad['changes'][0]
  if fault=='basis':r['schemaHash']='0'*64
  elif fault=='sources':r['sources'][next(iter(r['sources']))]='0'*64
  elif fault=='new-child':r['tree']['fields'].append(x.leaf('New'))
  elif fault=='type':r['tree']['fields'][0]['definition']['type']='double'
  elif fault=='root-contract':r['contract']['type']=f.n+'Leaf2'
  else:value=json.loads(r['valueJson']);value[x.power_key]=9223372036854775808;r['valueJson']=json.dumps(value)
  metadata(units,action='prepare',declaration=bad,ok=False);assert checkpoint.read_bytes()==saved;x.unchanged()
 metadata(units);f.checked('same-shape name/exact64 followup keeps null original creation basis and the declared missing leases; changed basis/source/identity/structure/type or overflow cannot rebase the creation/native group')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
