"""Argument label follow-up retains the complete previously saved body dependency lease."""
import copy,json,subprocess
import v666_header_bodies_fixture as x
f=x.f
def rpc(action,ok=True,**body):return f.invoke('blueprint',dict(action=action,**body),ok)['result'].get('result')
def request(changes):
 f.invoke('schema',dict(id=x.owner));schema=f.state()['schema'];basis=rpc('readOwnerEdits',id=x.owner,hash=schema['textHash']);return dict(id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=schema['textHash'],changes=changes))
def receipt():return next(r for r in json.loads(checkpoint.read_text())['changes']if r['id']==x.owner)['slotSaveReceipt']
def validate(units,ok):
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationBodyGroupGuards',action='validate',namespace=f.n[:-2],units=units,selected=[x.owner])),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});initial=x.request();reply=rpc('applySlots',**request(initial['changes']));assert reply['atomic']and reply['checkpointSaved'];checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));ids=x.verify(checkpoint);original_guards=copy.deepcopy(receipt()['readGuards']);assert x.retained_file in original_guards
 f.invoke('schema',dict(id=x.owner));schema=f.state()['schema'];changes=[];labels={'amount':'입력 값 표시','count':'반복 수 표시'}
 for fn in x.functions:
  method=next(v for v in schema['ownFunctions']if v['id']==fn);changes.append(dict(type='function-edit',id=fn,hash=method['hash'],name=method['name'],description=method['description']or'',signature=x.n.canonical(method['signature']),argumentNames=labels))
 prepared=request(changes);saved=checkpoint.read_bytes();path=f.project/x.retained_header;raw=path.read_bytes();peer=raw+b'\n// peer before argument label Save\n';path.write_bytes(peer);rpc('applySlots',False,**prepared);assert checkpoint.read_bytes()==saved and path.read_bytes()==peer;path.write_bytes(raw);x.unchanged();f.checked('argument label follow-up cannot rebase a saved native-body source scope after a peer changes its header')
 reply=rpc('applySlots',**request(changes));assert reply['atomic']and reply['checkpointSaved'] and receipt()['readGuards']==original_guards;assert x.verify(checkpoint)==ids;x.unchanged();f.stop();f.start(1);f.invoke('select',dict(id=x.owner));assert x.verify(checkpoint)==ids and receipt()['readGuards']==original_guards
 for row in json.loads(checkpoint.read_text())['changes']:
  if row['id']in x.functions:assert json.loads(f.metadata('inspect',text=row['draft'])['values']['editorArgumentNames'])==labels
 f.checked('same-contract argument aliases retain every saved native body member and exact source read hash through cold restart')
 units=copy.deepcopy(initial['units'])
 for row in json.loads(checkpoint.read_text())['changes']:units[row['id']]=row
 validate(units,True)
 for fault in ['missing-all','missing-caller','bad-hash','relocated','wrong-owner','wrong-version']:
  bad=copy.deepcopy(units);r=bad[x.owner]['slotSaveReceipt']
  if fault=='missing-all':r.pop('readGuards')
  elif fault=='missing-caller':r['readGuards'].pop(x.retained_file)
  elif fault=='bad-hash':r['readGuards'][x.retained_file]['hash']='invalid'
  elif fault=='relocated':r['readGuards'][x.retained_file]['path']='../outside'
  elif fault=='wrong-owner':r['owner']=f.n+'Other'
  else:r['version']=2
  validate(bad,False);x.unchanged();f.checked('retained header-only receipt '+fault+' is rejected without losing its saved body drafts')
 path=f.project/x.retained_file;raw=path.read_bytes();peer=raw+b'\n// peer after header Save before cold Review\n';path.write_bytes(peer);saved=copy.deepcopy(receipt());f.stop();f.start(3);f.invoke('select',dict(id=x.owner));f.invoke('reviewGroup',dict(ids=ids,target='portable'),False);assert receipt()==saved and path.read_bytes()==peer;path.write_bytes(raw);f.checked('header-only receipt still rejects a pre-Review native caller change after cold; original receipt and peer preserved')
 f.stop();f.start(4);f.invoke('select',dict(id=x.owner));f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready';phase=checkpoint.read_bytes();path=f.project/'NativeBodyCaller.celem';raw=path.read_bytes();peer=raw+b'\n// peer after Review of subsequent headers\n';path.write_bytes(peer);outcome=f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result'];assert outcome['sourceConfirmed']is False and checkpoint.read_bytes()==phase and path.read_bytes()==peer;path.write_bytes(raw);x.unchanged();f.checked('post-Review native caller change rejects final Confirm even after a label receipt; no authored source is published')
 f.stop();f.start(5);f.invoke('select',dict(id=x.owner));assert x.verify(checkpoint)==ids and receipt()['readGuards']==original_guards;f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready';f.invoke('confirmGroup',dict(ids=ids,token=review['token']));x.verify_live();f.checked('exact restoration and a new explicit Review/Confirm publish labels and existing saved bodies and execute the original caller with edited result'+str(x.edited_result))
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
