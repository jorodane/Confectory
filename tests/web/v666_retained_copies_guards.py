"""A cold-capable existing receipt must retain its complete owned read scope."""
import copy,json,subprocess
import v666_retained_copies_fixture as x
x.helper_file=x.retained_graph;x.helper_body=x.retained_file
f=x.f
def rpc(action,**body):return f.invoke('blueprint',dict(action=action,**body))['result']['result']
def validate(units,ok):
 request=dict(operation='informationBodyGroupGuards',action='validate',project=str(f.manifest),namespace=f.n[:-2],units=units,selected=[x.owner]);p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(request),env=f.env,text=True,capture_output=True,check=True);reply=json.loads(p.stdout);assert bool(reply['ok'])==ok,reply
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});f.invoke('schema',dict(id=x.owner));s=f.state()['schema'];basis=rpc('readOwnerEdits',id=x.owner,hash=s['textHash']);request=x.request();reply=rpc('applySlots',id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=s['textHash'],changes=request['changes']));assert reply['atomic']and reply['checkpointSaved'];checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));saved=checkpoint.read_bytes();units=copy.deepcopy(request['units'])
 for row in json.loads(saved)['changes']:units[row['id']]=row
 validate(units,True);receipt=units[x.owner]['slotSaveReceipt'];assert len(receipt['readGuards'])>len(receipt['sources'])and x.helper_file in receipt['readGuards']and x.helper_body in receipt['readGuards'];f.checked('existing receipt keeps helper declaration/body and complete owned baselines as read checks without new write members')
 for fault in ['missing-all','missing-helper','malformed-hash','relocated','extra-source','missing-registry','missing-copy-proof','copy-context','wrong-owner','wrong-version']:
  bad=copy.deepcopy(units);r=bad[x.owner]['slotSaveReceipt'];g=r['readGuards']
  if fault=='missing-all':r.pop('readGuards')
  elif fault=='missing-helper':g.pop(x.helper_file)
  elif fault=='malformed-hash':g[x.helper_body]['hash']='not-a-sha'
  elif fault=='relocated':g[x.helper_file]['path']='../outside.celem'
  elif fault=='extra-source':g['not-observed.celem']=dict(path='not-observed.celem',hash='0'*64)
  elif fault=='missing-registry':g.pop('registered/pack.cpack')
  elif fault=='missing-copy-proof':r.pop('nativeBodyCopies');r['declaration']['changes'][0]['mapping'].pop('copies')
  elif fault=='copy-context':r['nativeBodyCopies'][x.functions[0]][x.copy_id+'/body:common']['context'][0]['hash']='0'*64
  elif fault=='wrong-owner':r['owner']=f.n+'Unit'
  elif fault=='wrong-version':r['version']=2
  validate(bad,False);assert checkpoint.read_bytes()==saved;x.unchanged();f.checked(fault+' receipt refused without changing the saved group, source or input')
 validate(units,True);assert checkpoint.read_bytes()==saved;x.unchanged()
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
