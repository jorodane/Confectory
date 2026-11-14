"""Existing registered reads remain exact before Save, cold and final CAS."""
import copy,hashlib,json
import v666_input_import_observations_fixture as x
f=x.f
def rpc(action,ok=True,**kw):return f.invoke('blueprint',dict(action=action,**kw),ok)['result'].get('result')
def prepare(changes=None):
 f.invoke('schema',dict(id=x.owner));s=f.state()['schema'];basis=rpc('readOwnerEdits',id=x.owner,hash=s['textHash']);return dict(id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=s['textHash'],changes=x.request()['changes']if changes is None else changes))
def reviewed(ids):
 f.invoke('reviewGroup',dict(ids=ids,target='portable'));v=f.state()['review'];assert v['status']=='ready',v;return v['token']
def receipt(cp):return next(v for v in json.loads(cp.read_text())['changes']if v['id']==x.owner)['slotSaveReceipt']
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});cp=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=cp.read_bytes()
 bad=prepare();next(iter(bad['declaration']['changes'][-1]['mapping']['bodies'].values()))['text']='return MissingRegisteredBodyValue;';rpc('applySlots',False,**bad);assert cp.read_bytes()==baseline;x.unchanged();f.checked('invalid last CSharp body rejects all selected bodies and preserves checkpoint/originals')
 for index,path in enumerate([x.external_function,x.external_parent,x.external_manifest]):
  request=prepare();x.edit_external(path,b'\n// peer before Save\n');peer=path.read_bytes()
  try:rpc('applySlots',False,**request);assert cp.read_bytes()==baseline and path.read_bytes()==peer
  finally:x.restore_external(path)
  x.unchanged();f.checked(path.name+' before Save change rejects the complete group, preserving peer/checkpoint/permissions')
 request=prepare();reply=rpc('applySlots',**request);assert reply['atomic']and reply['checkpointSaved'];ids=x.verify(cp);proof=copy.deepcopy(receipt(cp)['nativeBodyDependencies']);reads=copy.deepcopy(receipt(cp)['nativeBodyDependencyReads']);f.stop();f.start(1);f.invoke('select',dict(id=x.owner));assert x.verify(cp)==ids
 late='등록 원본 관측을 유지하는 후속 설명 · 😀';rpc('applySlots',**prepare([dict(type='description',text=late)]));assert receipt(cp)['nativeBodyDependencies']==proof and receipt(cp)['nativeBodyDependencyReads']==reads
 rows={v['id']:v for v in json.loads(cp.read_text())['changes']};fn=x.functions[0];meta=dict(type='function-edit',id=fn,hash=hashlib.sha256(rows[fn]['draft'].encode()).hexdigest(),name=x.labels[0],description='후속 함수 설명',signature=copy.deepcopy(x.nexts[0]));rpc('applySlots',**prepare([meta]));assert receipt(cp)['nativeBodyDependencies']==proof and receipt(cp)['nativeBodyDependencyReads']==reads;x.unchanged();f.checked('cold and successive owner/function presentation Saves retain the exact original registration receipt/read set without rebasing')
 # A changed registered input must also block a presentation-only follow-up.
 x.edit_external(x.external_parent,b'\n// peer before presentation Save\n');saved=cp.read_bytes()
 try:rpc('applySlots',False,**prepare([dict(type='description',text=late+' next')]));assert cp.read_bytes()==saved
 finally:x.restore_external(x.external_parent)
 f.checked('a metadata-only follow-up cannot adopt a changed registered parent')
 for index,path in enumerate([x.external_function,x.external_parent,x.external_manifest,f.project/x.retained_file]):
  token=reviewed(ids);saved=cp.read_bytes();external=path in x.external_bytes;raw=path.read_bytes();x.edit_external(path,b'\n// peer after Review\n')if external else path.write_bytes(raw+b'\n// peer owned helper after Review\n');peer=path.read_bytes()
  try:
   result=f.invoke('confirmGroup',dict(ids=ids,token=token))['result']['result'];assert result['sourceConfirmed']is False,result;assert cp.read_bytes()==saved and path.read_bytes()==peer
  finally:
   if external:x.restore_external(path)
   else:path.write_bytes(raw)
  x.unchanged();f.stop();f.start(index+2);f.invoke('select',dict(id=x.owner));assert receipt(cp)['nativeBodyDependencies']==proof and receipt(cp)['nativeBodyDependencyReads']==reads;f.checked(path.name+' post-Review conflict rejects final Confirm, preserving original owned sources and readonly peer')
 token=reviewed(ids);observed_paths=[f.project/x.retained_file,*x.external_bytes];before={path:(path.read_bytes(),path.stat().st_ino,path.stat().st_mode,path.stat().st_mtime_ns)for path in observed_paths};out=f.invoke('confirmGroup',dict(ids=ids,token=token))['result']['result'];assert out.get('sourceConfirmed')is not False;x.verify_live();assert f.metadata('inspect',text=x.n.a.info.read_text())['description']==late;assert all((path.read_bytes(),path.stat().st_ino,path.stat().st_mode,path.stat().st_mtime_ns)==value for path,value in before.items());f.checked('fresh explicit Review after exact restoration confirms both bodies and the later description; execution27, external bytes/modes retained')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
