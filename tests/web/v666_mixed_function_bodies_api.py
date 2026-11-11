"""Saved native name/body group keeps one receipt and original final CAS."""
import copy,json,stat
import v666_mixed_function_bodies_fixture as x
f=x.f

def rpc(action,ok=True,**body):return f.invoke('blueprint',dict(action=action,**body),ok)['result'].get('result')
def prepare():
 s=f.invoke('schema',dict(id=x.owner))['state']['schema'];basis=rpc('readOwnerEdits',id=x.owner,hash=s['textHash']);return dict(id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=s['textHash'],changes=x.request()['changes']))
def receipt():return next(row for row in json.loads(checkpoint.read_text())['changes']if row['id']==x.owner)['slotSaveReceipt']
def review():
 f.invoke('reviewGroup',dict(ids=ids,target='portable'));r=f.state()['review'];assert r['status']=='ready',r;assert x.verify(checkpoint)==ids and receipt()==saved;return r['token']
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes();request=prepare();p=f.project/'CallerBody.celem';raw=p.read_bytes();p.write_bytes(raw+b'\n// peer before Save\n')
 try:rpc('applySlots',False,**request);assert checkpoint.read_bytes()==baseline and all((f.project/name).read_bytes()==v for name,v in x.snapshot.items()if name!='CallerBody.celem')
 finally:p.write_bytes(raw)
 f.checked('changed original caller before Save rejects the Blueprint name and native body and public name as one candidate')
 reply=rpc('applySlots',**prepare());assert reply['atomic']and reply['checkpointSaved'];ids=x.verify(checkpoint);saved=copy.deepcopy(receipt())
 guards=saved['readGuards'];assert set(x.functions+[fn+'Body/body:common'for fn in x.functions]+[x.n.caller+'Body/body:common'])<=set(saved['sources']);f.checked('one receipt binds the explicit rename, mixed sources and shared caller source to original edited-source identities and original write CAS')
 held=checkpoint.read_bytes();view=rpc('read',id=x.n.caller+'Body/body:common');call=next(row for row in view['nodes']if row['id']=='invoke');presentation=call['pinPresentation'];assert call['signature']['args'][0]['name']=='leftAmount'and presentation['status']=='available'and presentation['signature']==call['signature']and presentation['sourceWritten']is False and presentation['executed']is False and checkpoint.read_bytes()==held;x.unchanged();f.checked('saved shared call projects the exact observed new native pin name without another write or C# execution')
 for index,name in enumerate(['caller.graph.json',x.paths[x.body_function],'CallerBody.celem']):
  token=review();held=checkpoint.read_bytes();p=f.project/name;raw=p.read_bytes()
  if name.endswith('.json'):
   peer=json.loads(raw);peer['nodes'][0]['intent']='peer after Review';peer=json.dumps(peer).encode()
  elif name=='CallerBody.celem':
   peer=raw.replace(b'long second',b'string second');assert peer!=raw
  else:peer=raw+b'\n// peer after Review\n'
  p.write_bytes(peer)
  try:
   result=f.invoke('confirmGroup',dict(ids=ids,token=token))['result']['result'];assert result['sourceConfirmed']is False,result;assert checkpoint.read_bytes()==held and p.read_bytes()==peer and all((f.project/path).read_bytes()==value for path,value in x.snapshot.items()if path!=name)
  finally:p.write_bytes(raw)
  f.stop();f.start(index+1);f.invoke('select',dict(id=x.owner));assert x.verify(checkpoint)==ids and receipt()==saved;f.checked('post-Review '+name+(' incompatible semantic change'if name=='CallerBody.celem'else' edited-source conflict')+' rejects all writes and cold retry keeps complete original receipt/name/body plans')
 token=review();unchanged={}
 for name in ['CallerBody.celem','Main.csbody',x.body_function.split('::')[1]+'Body.celem',x.paths[x.blueprint_function]]:
  p=f.project/name;t=p.stat();unchanged[name]=(p.read_bytes(),t.st_ino,t.st_size,stat.S_IMODE(t.st_mode),t.st_mtime_ns)
 f.invoke('confirmGroup',dict(ids=ids,token=token));x.verify_live()
 for name,expected in unchanged.items():
  p=f.project/name;t=p.stat();assert(p.read_bytes(),t.st_ino,t.st_size,stat.S_IMODE(t.st_mode),t.st_mtime_ns)==expected,name
 f.checked('explicit fresh Review/Confirm after restoration publishes one group and result30, retaining native/header/other C# bytes, inode, mode and mtime')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
