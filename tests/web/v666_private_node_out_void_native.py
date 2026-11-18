"""Unused private long-to-void return with exact original out connections."""
import copy,json,pathlib,subprocess,sys,os
import v666_private_node_out_void_fixture as x
f=x.f
try:
 r=x.request();metadata=f.metadata('informationFunctionBodies',**{k:r[k]for k in ['project','manifest','id','units']},function=x.whole_function,includeBlueprintTargets=True);editable=metadata[x.whole_node].get('editableNativeReturn',False);assert bool(editable)==(x.mode in ['normal','preserved-out','out-observers-original','unconverted-original']),metadata[x.whole_node]
 if editable:assert metadata[x.whole_node]['editableNativeReturnTypes']==['void']
 (f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));x.execute(134 if x.mode in ['return-exit-original','explicit-return-original','return-local-original']else 104,'original-private-node-out-void')
 if x.mode=='unconverted-original':
  original=next(iter(r['changes'][0]['mapping']['bodies'].values()));original['text']=x.sources[x.whole_function];original['helpers']=x.original_helpers
 if x.mode in ['preserved-out','out-observers-original']:
  x.prepare(r);x.unchanged();f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});f.invoke('schema',dict(id=x.owner));schema=f.state()['schema']
  def rpc(action,**kw):return f.invoke('blueprint',dict(action=action,**kw))['result']['result']
  basis=rpc('readOwnerEdits',id=x.owner,hash=schema['textHash']);rpc('applySlots',id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=schema['textHash'],changes=r['changes']));cp=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));ids=x.verify(cp);f.stop();f.start(1);f.invoke('select',dict(id=x.owner));assert x.verify(cp)==ids;f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review
  peer=f.project/x.graph_path;raw=peer.read_bytes();stamp=peer.stat();saved=cp.read_bytes();peer.write_bytes(raw+b'\n')
  try:
   refused=f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result'];assert refused['sourceConfirmed']is False and cp.read_bytes()==saved and peer.read_bytes()!=raw
  finally:peer.write_bytes(raw);os.utime(peer,ns=(stamp.st_atime_ns,stamp.st_mtime_ns))
  x.unchanged();f.checked('each explicitly selected source remains a complete atomic Review member after cold restore; its post-Review peer change blocks Confirm and retains checkpoint/peer input')
  f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review;reply=f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result'];assert reply.get('sourceConfirmed')is not False;assert json.loads((f.project/x.node_path).read_text())['source']==x.selected[x.whole_function]and json.loads((f.project/x.node_path).read_text())['helpers']==x.selected_helpers;x.verify_live();f.checked('explicit void source/helpers preserve every original out connection and reflected long&/IsOut contract; actual return is void/null and preserved out99 or manually edited out25 executes the corresponding program')
 else:
  unchanged=copy.deepcopy(r);plan=next(iter(unchanged['changes'][0]['mapping']['bodies'].values()));plan['signature']=copy.deepcopy(x.code_signature);plan['text']=x.sources[x.whole_function];plan['helpers']=x.original_helpers;x.prepare(unchanged);x.unchanged();f.checked('unchanged private/native out ABI with original all-path assignment validates and original program executes with exact long values')
  if x.mode in ['reproduce','return-exit-original','explicit-return-original','return-local-original','return-argument-original','unconverted-original']:
   reply=x.prepare(r,False);assert x.mode!='unconverted-original'or'CS0127'in reply['message'];(f.case/'group-rejection.json').write_text(json.dumps(reply,ensure_ascii=False,indent=2));x.unchanged();f.checked('private out candidate rejects without changing original bindings or sources')
  else:
   for row in r['changes']:one=copy.deepcopy(r);one['changes']=[row];x.prepare(one)
   result=x.prepare(r)['result'];rows=result['updates']+result['linkedUpdates'];x.verify_rows({v['id']:dict(draft=v['text'])for v in rows});reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.prepare(reverse)['result'];assert {v['id']:v['text']for v in rows}=={v['id']:v['text']for v in other['updates']+other['linkedUpdates']};x.unchanged();f.checked('single/group private long-to-void return is order independent and retains every original input/out binding and consumer, arity2, out role/name/type and parent ABI')
   for fault in ['source-hash','flow-hash','wrong-before','type','role','return','count','other-param','name','public-contract','bad-source','helpers-boundary','last-body','original-source','unassigned-out','read-before-out','out-role','out-name']:
    
    bad=copy.deepcopy(r);a,b=bad['changes'];p=next(iter(a['mapping']['bodies'].values()))
    if fault=='source-hash':p['hash']='0'*64
    elif fault=='flow-hash':p['whole']['hash']='0'*64
    elif fault=='wrong-before':p['beforeSignature']['args'][0]['name']='wrong'
    elif fault=='type':p['signature']['args'][0]['type']='double'
    elif fault=='role':p['signature']['args'][0]['mode']='ref'
    elif fault=='return':p['signature']['return']='double'
    elif fault=='count':p['signature']['args'].pop()
    elif fault=='other-param':p['signature']['args']=[copy.deepcopy(x.code_signature['args'][1])]
    elif fault=='name':p['signature']['args'][0]['name']='inferredName'
    elif fault=='public-contract':a['signature']['args'][0]['name']='changedPublic'
    elif fault=='bad-source':p['text']='return MissingPrivateRef;'
    elif fault=='helpers-boundary':p['helpers']='} class Escape {'
    elif fault=='last-body':next(iter(b['mapping']['bodies'].values()))['text']='return MissingLastBody;'
    if fault=='original-source':p['text']=x.sources[x.whole_function];p['helpers']=x.original_helpers
    elif fault=='unassigned-out':p['text']='Edit(firstNative); return;'
    elif fault=='read-before-out':p['text']='secondNative=Edit(firstNative+secondNative); return;'
    elif fault=='out-role':p['signature']['args'][1]['mode']='ref'
    elif fault=='out-name':p['signature']['args'][1]['name']='inferredOut'
    reply=x.prepare(bad,False)
    if fault in ['original-source','unassigned-out','read-before-out']:
     code={'original-source':'CS0127','unassigned-out':'CS0177','read-before-out':'CS0269'}[fault];assert code in reply['message'],reply;(f.case/(fault+'-rejection.json')).write_text(json.dumps(reply,ensure_ascii=False,indent=2))
    x.unchanged();f.checked(fault+' rejects without original writes')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
if x.mode=='normal':
 for mode in ['return-exit-original','explicit-return-original','return-local-original','return-argument-original','unconverted-original','preserved-out','out-observers-original']:subprocess.run([sys.executable,str(pathlib.Path(__file__).resolve()),*sys.argv[1:3],mode],check=True)
