"""A header Save retains the complete original native out type replacement source scope."""
import copy,json,subprocess
import v666_native_presentation_followup_fixture as x
f=x.f
def rpc(action,**body):return f.invoke('blueprint',dict(action=action,**body))['result']['result']
def validate(units,ok):
 request=dict(operation='informationBodyGroupGuards',action='validate',namespace=f.n[:-2],units=units,selected=[x.owner]);p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(request),env=f.env,text=True,capture_output=True,check=True);reply=json.loads(p.stdout);assert bool(reply['ok'])==ok,reply
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});f.invoke('schema',dict(id=x.owner));s=f.state()['schema'];basis=rpc('readOwnerEdits',id=x.owner,hash=s['textHash']);request=x.request();reply=rpc('applySlots',id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=s['textHash'],changes=request['changes']));assert reply['atomic']and reply['checkpointSaved'];checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=copy.deepcopy(next(row for row in json.loads(checkpoint.read_text())['changes']if row['id']==x.owner)['slotSaveReceipt']['readGuards']);f.invoke('schema',dict(id=x.owner));s=f.state()['schema'];basis=rpc('readOwnerEdits',id=x.owner,hash=s['textHash']);rpc('applySlots',id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=s['textHash'],changes=[dict(type='description',text='후속 설명과 같은 읽기 원본')]));saved=checkpoint.read_bytes();assert next(row for row in json.loads(saved)['changes']if row['id']==x.owner)['slotSaveReceipt']['readGuards']==before;units=copy.deepcopy(request['units'])
 for row in json.loads(saved)['changes']:units[row['id']]=row
 validate(units,True);receipt=units[x.owner]['slotSaveReceipt'];assert len(receipt['readGuards'])>len(receipt['sources'])and x.retained_graph in receipt['readGuards']and x.retained_file in receipt['readGuards'];f.checked('existing receipt keeps helper declaration/body and complete owned baselines as read checks without new write members')
 for fault in ['missing-all','missing-helper','malformed-hash','relocated','extra-source','wrong-owner','wrong-version','missing-implementation-proof','unknown-declaration','raw-declaration','missing-declaration']:
  bad=copy.deepcopy(units);r=bad[x.owner]['slotSaveReceipt'];g=r['readGuards']
  if fault=='missing-all':r.pop('readGuards')
  elif fault=='missing-helper':g.pop(x.retained_graph)
  elif fault=='malformed-hash':g[x.retained_file]['hash']='not-a-sha'
  elif fault=='relocated':g[x.retained_graph]['path']='../outside.celem'
  elif fault=='extra-source':g['not-observed.celem']=dict(path='not-observed.celem',hash='0'*64)
  elif fault=='missing-implementation-proof':r['sources'].pop(x.functions[0]+'Body')
  elif fault=='wrong-owner':r['owner']=f.n+'Unit'
  elif fault=='wrong-version':r['version']=2
  elif fault=='unknown-declaration':r['declaration']['changes']=[dict(type='unrecognized',text='not a source plan')]
  elif fault=='raw-declaration':r['declaration']['raw']='not a captured native declaration'
  elif fault=='missing-declaration':r.pop('declaration')
  validate(bad,False);assert checkpoint.read_bytes()==saved;x.unchanged();f.checked(fault+' receipt refused without changing the saved group, source or input')
 validate(units,True);assert checkpoint.read_bytes()==saved;x.unchanged()
 def prepared(declaration,current_units,ok):
  req=dict(operation='informationBodyGroupGuards',action='prepare',namespace=f.n[:-2],units=current_units,declaration=declaration);proc=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(req),env=f.env,text=True,capture_output=True,check=True);out=json.loads(proc.stdout);assert bool(out['ok'])==ok,out;return out.get('result')
 declaration=dict(id=x.owner,changes=x.request()['changes']);out=prepared(declaration,units,True);assert out['required']and{v['path']:v for v in out['checks']}==before;f.checked('four-row presentation prepare inherits the exact captured checks rather than reconstructing a new source baseline')
 for changes in [[dict(type='function-order',ids=x.functions[::-1])],[dict(type='unrecognized',text='not a source plan')]]:
  prepared(dict(id=x.owner,changes=changes),units,False);assert checkpoint.read_bytes()==saved;x.unchanged()
 f.checked('unsupported declaration shapes cannot silently replace an existing native read scope with an empty one')
 extra_fn=x.owner+'_Function_'+'c'*32;unbound=copy.deepcopy(units);extra_text='function '+extra_fn+' (long value) -> long {}';unbound[extra_fn]=copy.deepcopy(units[x.functions[0]]);unbound[extra_fn].update(id=extra_fn,original=extra_text,draft=extra_text)
 prepared(dict(id=x.owner,changes=[dict(type='function-edit',id=extra_fn,hash=__import__('hashlib').sha256(extra_text.encode()).hexdigest(),name='Uncaptured',description='not part of the saved function set',signature=dict(args=[dict(name='value',type='long')],**{'return':'long'}))]),unbound,False);assert checkpoint.read_bytes()==saved;x.unchanged();f.checked('an uncaptured function cannot adopt the saved native group even if its path aliases an existing owned unit')

finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
