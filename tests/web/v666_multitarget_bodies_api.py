"""All explicit native targets share one receipt, source lease and final write."""
import copy,json,stat
import v666_multitarget_bodies_fixture as x
f=x.f
def rpc(action,ok=True,**body):return f.invoke('blueprint',dict(action=action,**body),ok)['result'].get('result')
def prepare():
 f.invoke('schema',dict(id=x.owner));s=f.state()['schema'];basis=rpc('readOwnerEdits',id=x.owner,hash=s['textHash']);return dict(id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=s['textHash'],changes=x.request()['changes']))
def receipt():return next(row for row in json.loads(checkpoint.read_text())['changes']if row['id']==x.owner)['slotSaveReceipt']
def reviewed(number):
 f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review;assert x.verify(checkpoint)==ids and receipt()==saved;return review['token']
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes();request=prepare();p=f.project/x.retained_header;original=p.read_bytes();peer=original+b'\n// peer before Save\n';p.write_bytes(peer);rpc('applySlots',False,**request);assert checkpoint.read_bytes()==baseline and p.read_bytes()==peer and all((f.project/name).read_bytes()==value for name,value in x.snapshot.items()if name!=x.retained_header);p.write_bytes(original);f.checked('native target header change before Save rejects the entire four-body group with checkpoint, input and peer retained')
 f.stop();f.start(1);f.invoke('select',dict(id=x.owner));reply=rpc('applySlots',**prepare());assert reply['atomic']and reply['checkpointSaved'];ids=x.verify(checkpoint);saved=copy.deepcopy(receipt());guards=saved['readGuards'];assert set(x.body_paths.values())|{x.retained_header,x.retained_file,x.retained_graph}<=set(guards);assert set(x.body_paths)<=set(saved['sources']);f.checked('one version3 receipt contains all four explicitly edited native targets and the unchanged headers/caller in original read guards')
 for number,name in enumerate([x.retained_header,x.body_paths[x.functions[0]+'Body/body:linux'],x.retained_graph,x.retained_file]):
  token=reviewed(number);held=checkpoint.read_bytes();p=f.project/name;raw=p.read_bytes()
  if name==x.retained_graph:
   changed=json.loads(raw);changed['exits']['return']={'constant':777};peer=json.dumps(changed).encode()
  else:peer=raw+b'\n// peer after Review\n'
  p.write_bytes(peer);outcome=f.invoke('confirmGroup',dict(ids=ids,token=token))['result']['result'];assert outcome['sourceConfirmed']is False,outcome;assert checkpoint.read_bytes()==held and p.read_bytes()==peer and all((f.project/path).read_bytes()==value for path,value in x.snapshot.items()if path!=name);p.write_bytes(raw);f.stop();f.start(number+2);f.invoke('select',dict(id=x.owner));assert x.verify(checkpoint)==ids and receipt()==saved;f.checked('post-Review '+name+' change rejects all writes and cold retry retains all four original target edits and receipt')
 token=reviewed(4);kept={}
 for name in [x.retained_header,x.functions[1].split('::')[1]+'Body.celem',x.retained_file,x.retained_graph,'CallerBody.celem']:
  p=f.project/name;t=p.stat();kept[name]=(p.read_bytes(),t.st_ino,t.st_size,stat.S_IMODE(t.st_mode),t.st_mtime_ns)
 f.invoke('confirmGroup',dict(ids=ids,token=token));x.verify_live()
 for name,before in kept.items():
  p=f.project/name;t=p.stat();assert(p.read_bytes(),t.st_ino,t.st_size,stat.S_IMODE(t.st_mode),t.st_mtime_ns)==before,name
 f.checked('fresh explicit Confirm after exact restoration atomically publishes four bodies; both actual platform executions20/24 and unchanged caller/header inode, mode, mtime pass')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
