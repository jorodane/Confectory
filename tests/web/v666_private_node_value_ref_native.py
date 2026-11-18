"""Existing local storage and an explicit private value-to-ref role candidate."""
import copy,json,pathlib,subprocess,sys,os
import v666_private_node_value_ref_fixture as x
f=x.f
try:
 r=x.request();metadata=f.metadata('informationFunctionBodies',**{k:r[k]for k in ['project','manifest','id','units']},function=x.whole_function,includeBlueprintTargets=True);refs=metadata[x.whole_node].get('editableNativeRefs',[]);assert bool(refs)==(x.mode in ['normal','preserved-source']),metadata[x.whole_node]
 if refs:assert refs==[dict(name='secondNative',local='ref_counter',label='기존 참조 저장소')]
 (f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));x.execute(40,'original-private-node-value-ref')
 if x.mode=='preserved-source':
  x.prepare(r);x.unchanged();f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});f.invoke('schema',dict(id=x.owner));schema=f.state()['schema']
  def rpc(action,**kw):return f.invoke('blueprint',dict(action=action,**kw))['result']['result']
  basis=rpc('readOwnerEdits',id=x.owner,hash=schema['textHash']);rpc('applySlots',id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=schema['textHash'],changes=r['changes']));cp=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));ids=x.verify(cp);f.stop();f.start(1);f.invoke('select',dict(id=x.owner));assert x.verify(cp)==ids;f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review
  peer=f.project/x.graph_path;raw=peer.read_bytes();stamp=peer.stat();saved=cp.read_bytes();peer.write_bytes(raw+b'\n')
  try:
   refused=f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result'];assert refused['sourceConfirmed']is False and cp.read_bytes()==saved and peer.read_bytes()!=raw
  finally:peer.write_bytes(raw);os.utime(peer,ns=(stamp.st_atime_ns,stamp.st_mtime_ns))
  x.unchanged();f.checked('unchanged selected native source remains a complete atomic Review member after cold restore; its post-Review peer change blocks Confirm and retains checkpoint/peer input')
  f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review;reply=f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result'];assert reply.get('sourceConfirmed')is not False;assert json.loads((f.project/x.node_path).read_text())['source']==x.sources[x.whole_function]and json.loads((f.project/x.node_path).read_text())['helpers']==x.original_helpers;x.verify_live();f.checked('unchanged CSharp source/helpers and paired native body execute104 after actual Review/Confirm; reflected private actual long& writes the existing local to99 while unchanged value code leaves it35 before the explicit role change')
 else:
  unchanged=copy.deepcopy(r);plan=next(iter(unchanged['changes'][0]['mapping']['bodies'].values()));plan['signature']=copy.deepcopy(x.code_signature);x.prepare(unchanged);x.unchanged();f.checked('unchanged private/native ABI validates and original input/literal program executes with exact long values')
  if x.mode in ['reproduce','literal-original','input-original','int-local-original']:
   reply=x.prepare(r,False);(f.case/'group-rejection.json').write_text(json.dumps(reply,ensure_ascii=False,indent=2));x.unchanged();f.checked('private reference candidate rejects without changing original bindings or sources')
  else:
   for row in r['changes']:one=copy.deepcopy(r);one['changes']=[row];x.prepare(one)
   result=x.prepare(r)['result'];rows=result['updates']+result['linkedUpdates'];x.verify_rows({v['id']:dict(draft=v['text'])for v in rows});reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.prepare(reverse)['result'];assert {v['id']:v['text']for v in rows}=={v['id']:v['text']for v in other['updates']+other['linkedUpdates']};x.unchanged();f.checked('single/group private reference role candidate is plan-order independent and retains the exact original binding JSON by parameter name, parent ABI and return')
   for fault in ['source-hash','flow-hash','wrong-before','type','role','return','count','duplicate','name','public-contract','bad-source','helpers-boundary','last-body']:
    bad=copy.deepcopy(r);a,b=bad['changes'];p=next(iter(a['mapping']['bodies'].values()))
    if fault=='source-hash':p['hash']='0'*64
    elif fault=='flow-hash':p['whole']['hash']='0'*64
    elif fault=='wrong-before':p['beforeSignature']['args'][0]['name']='wrong'
    elif fault=='type':p['signature']['args'][0]['type']='double'
    elif fault=='role':p['signature']['args'][0]['mode']='ref'
    elif fault=='return':p['signature']['return']='double'
    elif fault=='count':p['signature']['args'].pop()
    elif fault=='duplicate':p['signature']['args'][1]=copy.deepcopy(p['signature']['args'][0])
    elif fault=='name':p['signature']['args'][0]['name']='inferredName'
    elif fault=='public-contract':a['signature']['args'][0]['name']='changedPublic'
    elif fault=='bad-source':p['text']='return MissingPrivateRef;'
    elif fault=='helpers-boundary':p['helpers']='} class Escape {'
    elif fault=='last-body':next(iter(b['mapping']['bodies'].values()))['text']='return MissingLastBody;'
    x.prepare(bad,False);x.unchanged();f.checked(fault+' rejects without original writes')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
if x.mode=='normal':
 for mode in ['literal-original','input-original','int-local-original','preserved-source']:subprocess.run([sys.executable,str(pathlib.Path(__file__).resolve()),*sys.argv[1:3],mode],check=True)
