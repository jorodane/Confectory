"""A header Save retains the complete original native out type replacement source scope."""
import copy,json,subprocess
import v666_owned_structure_fixture as x
f=x.f
def rpc(action,**body):return f.invoke('blueprint',dict(action=action,**body))['result']['result']
def validate(units,ok):
 request=dict(operation='informationBodyGroupGuards',action='validate',project=str(f.manifest),namespace=f.n[:-2],units=units,selected=[x.owner]);p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(request),env=f.env,text=True,capture_output=True,check=True);reply=json.loads(p.stdout);assert bool(reply['ok'])==ok,reply
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});f.invoke('schema',dict(id=x.owner));s=f.state()['schema'];basis=rpc('readOwnerEdits',id=x.owner,hash=s['textHash']);request=x.request();reply=rpc('applySlots',id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=s['textHash'],changes=request['changes']));assert reply['atomic']and reply['checkpointSaved'];checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=copy.deepcopy(next(row for row in json.loads(checkpoint.read_text())['changes']if row['id']==x.owner)['slotSaveReceipt']['readGuards']);f.invoke('schema',dict(id=x.owner));s=f.state()['schema'];basis=rpc('readOwnerEdits',id=x.owner,hash=s['textHash']);rpc('applySlots',id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=s['textHash'],changes=[dict(type='description',text='후속 설명과 같은 읽기 원본')]));saved=checkpoint.read_bytes();assert next(row for row in json.loads(saved)['changes']if row['id']==x.owner)['slotSaveReceipt']['readGuards']==before;units=copy.deepcopy(request['units'])
 for row in json.loads(saved)['changes']:units[row['id']]=row
 validate(units,True);receipt=units[x.owner]['slotSaveReceipt'];assert len(receipt['readGuards'])>len(receipt['sources'])and x.retained_graph in receipt['readGuards']and x.retained_file in receipt['readGuards'];f.checked('existing receipt keeps helper declaration/body and complete owned baselines as read checks without new write members')
 for fault in ['missing-all','missing-helper','malformed-hash','relocated','extra-source','wrong-owner','wrong-version','missing-implementation-proof','missing-registered','missing-selected-target','missing-enum','missing-value-plan','missing-value-reads','relocated-value-read','extra-value-read','changed-value-plan']:
  bad=copy.deepcopy(units);r=bad[x.owner]['slotSaveReceipt'];g=r['readGuards']
  if fault=='missing-all':r.pop('readGuards')
  elif fault=='missing-helper':g.pop(x.retained_graph)
  elif fault=='missing-value-plan':r.pop('nativeBodyOwnerEdits')
  elif fault=='missing-value-reads':r.pop('nativeBodyOwnerReads')
  elif fault=='relocated-value-read':r['nativeBodyOwnerReads'][0]['path']='/not-observed/source.celem'
  elif fault=='extra-value-read':r['nativeBodyOwnerReads'].append(dict(path='/not-observed/other.celem',hash='0'*64))
  elif fault=='changed-value-plan':next(v for v in r['nativeBodyOwnerEdits']if v['type']=='owned-definition')['sources']={}
  elif fault=='missing-registered':g.pop('Leaf2.celem')
  elif fault=='missing-selected-target':g.pop('Leaf.celem')
  elif fault=='missing-enum':g.pop('RefTarget.celem')
  elif fault=='malformed-hash':g[x.retained_file]['hash']='not-a-sha'
  elif fault=='relocated':g[x.retained_graph]['path']='../outside.celem'
  elif fault=='extra-source':g['not-observed.celem']=dict(path='not-observed.celem',hash='0'*64)
  elif fault=='missing-implementation-proof':r['sources'].pop(x.functions[0]+'Body')
  elif fault=='wrong-owner':r['owner']=f.n+'Unit'
  elif fault=='wrong-version':r['version']=2
  validate(bad,False);assert checkpoint.read_bytes()==saved;x.unchanged();f.checked(fault+' receipt refused without changing the saved group, source or input')
 for fault in ['missing-child-guard','missing-child-member','extra-named-schema','changed-schema-text','relocated-child','changed-original-schema','changed-original-source']:
  bad=copy.deepcopy(units);r=bad[x.owner]['slotSaveReceipt'];child=next(iter(x.owned_paths));path=x.owned_paths[child]
  if fault=='missing-child-guard':r['readGuards'].pop(path)
  elif fault=='missing-child-member':
   r['sources'].pop(child);group=list(bad[x.owner]['atomicEditGroup']);next_group=[id for id in group if id!=child]
   for unit in bad.values():
    if unit.get('atomicEditGroup')==group:unit['atomicEditGroup']=copy.deepcopy(next_group)
  elif fault=='extra-named-schema':
   id=f.n+'Leaf2';r['sources'][id]=dict(kind='schema',path=bad[id]['path'],hash=__import__('hashlib').sha256(bad[id]['draft'].encode()).hexdigest());group=list(bad[x.owner]['atomicEditGroup']);next_group=sorted(group+[id])
   for unit in bad.values():
    if unit.get('atomicEditGroup')==group:unit['atomicEditGroup']=copy.deepcopy(next_group)
  elif fault=='changed-schema-text':bad[child]['draft']+='\r\n// forged saved schema';r['sources'][child]['hash']=__import__('hashlib').sha256(bad[child]['draft'].encode()).hexdigest()
  elif fault=='relocated-child':bad[child]['path']='Leaf2.celem';r['sources'][child]['path']='Leaf2.celem'
  else:
   for row in [v for rows in [r['declaration']['changes'],r['nativeBodyOwnerEdits']]for v in rows if v['type']=='owned-definition']:
    if fault=='changed-original-schema':row['schemaHash']='0'*64
    else:row['sources'][child]='0'*64
  validate(bad,False);assert checkpoint.read_bytes()==saved;x.unchanged();f.checked(fault+' owned footprint refused without adding source authority or changing any saved input')

 # A retained same-shape owned value/presentation is revalidated on its actual
 # current draft, while the returned plan still owns the original source lease.
 row=copy.deepcopy(next(v for v in receipt['nativeBodyOwnerEdits']if v['type']=='owned-definition'));row['schemaHash']=__import__('hashlib').sha256(units[x.owner]['draft'].encode()).hexdigest();row['sources']={id:__import__('hashlib').sha256(units[id]['draft'].encode()).hexdigest()for id in x.owned_paths};row['tree']['fields'][0]['name']='명시 후속 값';value=json.loads(row['valueJson']);value['Power']=9223372036854775803;row['valueJson']=json.dumps(value,ensure_ascii=False)
 def followup(row,ok):
  query=dict(operation='informationBodyGroupGuards',action='prepare',project=str(f.manifest),namespace=f.n[:-2],units=units,declaration=dict(id=x.owner,hash=__import__('hashlib').sha256(units[x.owner]['draft'].encode()).hexdigest(),changes=[row]));p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(query),env=f.env,text=True,capture_output=True,check=True);reply=json.loads(p.stdout);assert bool(reply['ok'])==ok,reply;return reply.get('result')
 next_plan=followup(row,True);assert next_plan['required']and next_plan['reads']==receipt['nativeBodyOwnerReads'];planned=next(v for v in next_plan['ownerEdits']if v['type']=='owned-definition');original=next(v for v in receipt['nativeBodyOwnerEdits']if v['type']=='owned-definition');assert planned['sources']==original['sources']and planned['schemaHash']==original['schemaHash']and json.loads(planned['valueJson'])['Power']==9223372036854775803
 for fault in ['basis','sources','new-field','type','named-proof','overflow','malformed-value','new-child','contract']:
  bad=copy.deepcopy(row)
  if fault=='basis':bad['schemaHash']='0'*64
  elif fault=='sources':bad['sources'][next(iter(bad['sources']))]='0'*64
  elif fault=='new-field':bad['tree']['fields'].append(x.leaf('Uncaptured','long'))
  elif fault=='type':bad['tree']['fields'][0]['definition']['type']='double'
  elif fault=='named-proof':bad['tree']['fields'][2]['sources']={}
  elif fault=='overflow':value=json.loads(bad['valueJson']);value['Power']=9223372036854775808;bad['valueJson']=json.dumps(value)
  elif fault=='malformed-value':bad['valueJson']='{'
  elif fault=='new-child':bad['tree']['fields'][1]['children']['fields'].append(x.leaf('Uncaptured'))
  elif fault=='contract':bad['contract']['type']=f.n+'Leaf2'
  followup(bad,False);assert checkpoint.read_bytes()==saved;x.unchanged()
 f.checked('explicit retained name/exact64 value replays the original owner plan; stale basis/source, changed identity/type/proof/structure and malformed or overflowing values never rebase its captured native scope')
 validate(units,True);assert checkpoint.read_bytes()==saved;x.unchanged()
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
