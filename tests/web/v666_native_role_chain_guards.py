"""A header Save retains the complete original native value-to-ref source scope."""
import copy,json,subprocess,hashlib,re
import v666_native_role_chain_fixture as x
f=x.f
def rpc(action,**body):return f.invoke('blueprint',dict(action=action,**body))['result']['result']
def validate(units,ok):
 request=dict(operation='informationBodyGroupGuards',action='validate',namespace=f.n[:-2],units=units,selected=[x.owner]);p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(request),env=f.env,text=True,capture_output=True,check=True);reply=json.loads(p.stdout);assert bool(reply['ok'])==ok,reply
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});f.invoke('schema',dict(id=x.owner));s=f.state()['schema'];basis=rpc('readOwnerEdits',id=x.owner,hash=s['textHash']);request=x.request();reply=rpc('applySlots',id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=s['textHash'],changes=request['changes']));assert reply['atomic']and reply['checkpointSaved'];checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=copy.deepcopy(next(row for row in json.loads(checkpoint.read_text())['changes']if row['id']==x.owner)['slotSaveReceipt']['readGuards']);f.invoke('schema',dict(id=x.owner));s=f.state()['schema'];basis=rpc('readOwnerEdits',id=x.owner,hash=s['textHash']);rpc('applySlots',id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=s['textHash'],changes=[dict(type='description',text='후속 설명과 같은 읽기 원본')]));saved=checkpoint.read_bytes();assert next(row for row in json.loads(saved)['changes']if row['id']==x.owner)['slotSaveReceipt']['readGuards']==before;units=copy.deepcopy(request['units'])
 for row in json.loads(saved)['changes']:units[row['id']]=row
 def graphscope(selected,ok):
  request=dict(operation='informationBodyGroupGuards',action='graphs',project=str(f.manifest),namespace=f.n[:-2],units=selected,selected=[x.owner]);p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(request),env=f.env,text=True,capture_output=True,check=True);value=json.loads(p.stdout);assert bool(value['ok'])==ok,value
 (f.case/'captured-guard-request.json').write_text(json.dumps(dict(operation='informationBodyGroupGuards',action='validate',project=str(f.manifest),namespace=f.n[:-2],units=units,selected=[x.owner]),ensure_ascii=False,indent=2))
 graphscope(units,True)
 for fault in ['header-scope','import-scope','native-alias','body-proof','function-proof','mixed-direction','mixed-family']:
  bad=copy.deepcopy(units);header=x.first+'Body';member=header if fault in ['header-scope','import-scope','native-alias']else header+'/body:common'if fault=='body-proof'else x.first
  if fault=='header-scope':bad[member]['draft']=bad[member]['draft'].replace('as Second','as RenamedSecond')
  elif fault=='import-scope':bad[member]['draft']=re.sub(r'(as Second \([^;]*?)ref long',r'\1out long',bad[member]['draft'])
  elif fault=='native-alias':bad[member]['draft']=bad[member]['draft'].replace('nativeAmount','inferred',1)
  elif fault=='mixed-family':
   for key,old,new in [(x.first,'ref long count','string count'),(x.first+'Body','ref long nativeCount','string nativeCount')]:
    assert old in bad[key]['draft'];bad[key]['draft']=bad[key]['draft'].replace(old,new,1);bad[x.owner]['slotSaveReceipt']['sources'][key]['hash']=hashlib.sha256(bad[key]['draft'].encode()).hexdigest()
  elif fault=='mixed-direction':
   for key in [x.second,x.second+'Body']:
    bad[key]['draft']=bad[key]['draft'].replace('ref long','out long',1);bad[x.owner]['slotSaveReceipt']['sources'][key]['hash']=hashlib.sha256(bad[key]['draft'].encode()).hexdigest()
  else:bad[member]['draft']+='\n// changed captured role source'
  if fault in ['header-scope','import-scope','native-alias']:bad[x.owner]['slotSaveReceipt']['sources'][member]['hash']=hashlib.sha256(bad[member]['draft'].encode()).hexdigest()
  graphscope(bad,False);assert checkpoint.read_bytes()==saved;x.unchanged()
 f.checked('cold discovery retains exact native aliases, captured body/function hashes, import delta and one role direction; forged scope rejects')
 validate(units,True);receipt=units[x.owner]['slotSaveReceipt'];assert len(receipt['readGuards'])>len(receipt['sources'])and x.retained_graph in receipt['readGuards']and x.retained_file in receipt['readGuards'];f.checked('existing receipt keeps helper declaration/body and complete owned baselines as read checks without new write members')
 for fault in ['missing-all','missing-helper','malformed-hash','relocated','extra-source','wrong-owner','wrong-version','missing-implementation-proof']:
  bad=copy.deepcopy(units);r=bad[x.owner]['slotSaveReceipt'];g=r['readGuards']
  if fault=='missing-all':r.pop('readGuards')
  elif fault=='missing-helper':g.pop(x.retained_graph)
  elif fault=='malformed-hash':g[x.retained_file]['hash']='not-a-sha'
  elif fault=='relocated':g[x.retained_graph]['path']='../outside.celem'
  elif fault=='extra-source':g['not-observed.celem']=dict(path='not-observed.celem',hash='0'*64)
  elif fault=='missing-implementation-proof':r['sources'].pop(x.functions[0]+'Body')
  elif fault=='wrong-owner':r['owner']=f.n+'Unit'
  elif fault=='wrong-version':r['version']=2
  validate(bad,False);assert checkpoint.read_bytes()==saved;x.unchanged();f.checked(fault+' receipt refused without changing the saved group, source or input')
 validate(units,True);assert checkpoint.read_bytes()==saved;x.unchanged()
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
