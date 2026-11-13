"""Saved native out type replacement group retains source CAS after owner and function metadata Saves."""
import copy,json,stat
import v666_owned_creation_fixture as x
f=x.f
def rpc(action,ok=True,**body):return f.invoke('blueprint',dict(action=action,**body),ok)['result'].get('result')
def prepare():
 f.invoke('schema',dict(id=x.owner));s=f.state()['schema'];basis=rpc('readOwnerEdits',id=x.owner,hash=s['textHash']);return dict(id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=s['textHash'],changes=x.request()['changes']))
def read_receipt():return next(row for row in json.loads(checkpoint.read_text())['changes']if row['id']==x.owner)['slotSaveReceipt']
def peer_bytes(name,raw):
 if name.endswith(('.celem','.csbody')):return raw+b'\n// peer after Review\n'
 document=json.loads(raw)
 if name.endswith('.node.json'):document['source']+='\n// peer private code'
 else:document['nodes'][0]['intent']+=' peer graph'
 return (json.dumps(document,ensure_ascii=False)+'\n').encode()

def reviewed(number):
 (f.case/('before-review-'+str(number)+'.json')).write_bytes(checkpoint.read_bytes());f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review;assert x.verify(checkpoint)==ids and read_receipt()==saved_receipt;(f.case/('after-review-'+str(number)+'.json')).write_bytes(checkpoint.read_bytes());return review['token']
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes();request=prepare();path=f.project/x.retained_header;original=path.read_bytes();peer=original+b'\n// peer before Save\n';path.write_bytes(peer);rpc('applySlots',False,**request);assert checkpoint.read_bytes()==baseline and path.read_bytes()==peer and all((f.project/p).read_bytes()==value for p,value in x.snapshot.items()if p!=x.retained_header);f.checked('retained ordinary caller change before Save rejects the whole group and preserves peer/checkpoint/input');path.write_bytes(original)
 for mode in ['file','directory']:
  destination=f.project/next(iter(x.owned_paths.values()))
  if mode=='file':destination.write_bytes(b'// peer owns new child destination')
  else:destination.mkdir()
  rpc('applySlots',False,**request);assert checkpoint.read_bytes()==baseline
  if mode=='file':assert destination.read_bytes()==b'// peer owns new child destination';destination.unlink()
  else:assert destination.is_dir()and not list(destination.iterdir());destination.rmdir()
  x.unchanged();f.checked('pre-Save new child '+mode+' collision rejects the complete group and preserves peer, original registration, checkpoint and input')
 f.stop();f.start(1);f.invoke('select',dict(id=x.owner));reply=rpc('applySlots',**prepare());assert reply['atomic']and reply['checkpointSaved'];ids=x.verify(checkpoint);saved_receipt=read_receipt();guards=copy.deepcopy(saved_receipt['readGuards']);value_reads=copy.deepcopy(saved_receipt['nativeBodyOwnerReads']);value_plans=copy.deepcopy(saved_receipt['nativeBodyOwnerEdits']);assert (str(x.definition_source)in {row['path']for row in value_reads}if'--registered-fields'in __import__('sys').argv else'Leaf2.celem'in guards);assert str(x.definition_source)not in {str(f.project/row['path'])for row in saved_receipt['sources'].values()};assert all(p in guards for p in [x.retained_header,x.retained_file,x.retained_graph,x.paths[x.functions[0]],x.functions[0].split('::')[1]+'Body.celem']);f.checked('explicit outputs/body Save binds the original helper, caller graph and selected native declaration/body in existing version3 read guards')
 s=f.invoke('schema',dict(id=x.owner))['state']['schema'];basis=rpc('readOwnerEdits',id=x.owner,hash=s['textHash']);x.accepted_description='반환 추가와 본문 공동 저장 뒤의 실제 설명';reply=rpc('applySlots',id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=s['textHash'],changes=[dict(type='description',text=x.accepted_description)]));assert reply['atomic']and reply['checkpointSaved'];assert x.verify(checkpoint)==ids;assert read_receipt()['readGuards']==guards and read_receipt()['nativeBodyOwnerReads']==value_reads and read_receipt()['nativeBodyOwnerEdits']==value_plans;saved_receipt=copy.deepcopy(read_receipt());f.checked('subsequent explicit owner description Save retains the exact original read scope and complete native out type replacement source group')
 # The existing function metadata editor retains the already captured new ABI.
 f.invoke('schema',dict(id=x.owner));s=f.state()['schema'];basis=rpc('readOwnerEdits',id=x.owner,hash=s['textHash']);current=next(row for row in json.loads(checkpoint.read_text())['changes']if row['id']==x.functions[0]);row=dict(type='function-edit',id=x.functions[0],hash=__import__('hashlib').sha256(current['draft'].encode()).hexdigest(),name=x.labels[0],description='출력 저장 뒤 기능 설명',signature=x.nexts[0]);reply=rpc('applySlots',id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=s['textHash'],changes=[row]));assert reply['atomic']and reply['checkpointSaved'];assert x.verify(checkpoint)==ids and read_receipt()['readGuards']==guards and read_receipt()['nativeBodyOwnerReads']==value_reads and read_receipt()['nativeBodyOwnerEdits']==value_plans;saved_receipt=copy.deepcopy(read_receipt());f.checked('subsequent function metadata Save preserves the captured new native ABI, group and original dependency guards')
 sources_to_change=[x.retained_header,x.retained_file,x.retained_graph,x.paths[x.functions[0]],x.functions[0].split('::')[1]+'Body.celem',str(x.definition_source),'Leaf.celem','LeafChild.celem','RefTarget.celem',*getattr(x,'existing_paths',{}).values()]
 for number,name in enumerate(sources_to_change):
  token=reviewed(number);phase_saved=checkpoint.read_bytes();p=f.project/name;raw=p.read_bytes();peer=peer_bytes(name,raw);p.write_bytes(peer);outcome=f.invoke('confirmGroup',dict(ids=ids,token=token))['result']['result'];assert outcome['sourceConfirmed']is False,outcome;assert p.read_bytes()==peer and checkpoint.read_bytes()==phase_saved and all((f.project/path).read_bytes()==value for path,value in x.snapshot.items()if f.project/path!=p);(f.case/('after-rejected-confirm-'+str(number)+'.json')).write_bytes(checkpoint.read_bytes());f.checked('post-Review '+name+' change rejects final Confirm without writing either edited body; exact checkpoint and peer bytes retained');p.write_bytes(raw);f.stop();f.start(2+number);f.invoke('select',dict(id=x.owner));assert x.verify(checkpoint)==ids and read_receipt()==saved_receipt;f.checked('cold retry retains the complete original receipt and both explicitly authored bodies')
 for number,(path,mode)in enumerate((path,mode)for path in x.owned_paths.values()for mode in ['file','directory']):
  token=reviewed('new-'+str(number));phase_saved=checkpoint.read_bytes();p=f.project/path
  if mode=='file':p.write_bytes(b'// late peer owns missing child')
  else:p.mkdir()
  outcome=f.invoke('confirmGroup',dict(ids=ids,token=token))['result']['result'];assert outcome['sourceConfirmed']is False and checkpoint.read_bytes()==phase_saved;assert all((f.project/name).read_bytes()==raw for name,raw in x.snapshot.items())
  if mode=='file':assert p.read_bytes()==b'// late peer owns missing child';p.unlink()
  else:assert p.is_dir()and not list(p.iterdir());p.rmdir()
  x.unchanged();f.stop();f.start(30+number);f.invoke('select',dict(id=x.owner));assert x.verify(checkpoint)==ids and read_receipt()==saved_receipt;f.checked('post-Review new child '+mode+' collision preserves every source and the original missing lease; restored absence and cold retain the complete creation/native receipt')
 token=reviewed('final');original_callers={}
 # Deliberate peer mutation/restoration above changed fixture mtimes. The
 # positive Confirm must preserve the untouched sibling from this exact basis.
 if hasattr(x,'existing_paths'):
  for id,path in x.existing_paths.items():x.owned_physical[id]=x.physical(f.project/path)
 for name in [x.retained_header,x.retained_file,str(x.definition_source)]+([x.existing_paths[x.child_id([x.root_key,'Inner'])]]if hasattr(x,'existing_paths')else[]):
  p=f.project/name;t=p.stat();original_callers[name]=(p.read_bytes(),t.st_ino,t.st_size,stat.S_IMODE(t.st_mode),t.st_mtime_ns)
 f.invoke('confirmGroup',dict(ids=ids,token=token));x.verify_live()
 for name,before in original_callers.items():
  p=f.project/name;t=p.stat();assert(p.read_bytes(),t.st_ino,t.st_size,stat.S_IMODE(t.st_mode),t.st_mtime_ns)==before,name
 f.checked('new explicit Review/Confirm after exact restoration executes result'+str(x.edited_result)+' and retains caller C# bytes, inode, mode and mtime')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
