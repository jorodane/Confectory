"""Exact private/native source and lifecycle checks through the packaged engine."""
import copy,hashlib,json,os
import v666_private_body_group_fixture as x
f=x.f
h=lambda text:hashlib.sha256(text.encode()).hexdigest()
def rpc(action,ok=True,**kw):return f.invoke('blueprint',dict(action=action,**kw),ok)['result'].get('result')
def prepare(changes=None):
 f.invoke('schema',dict(id=x.owner));s=f.state()['schema'];basis=rpc('readOwnerEdits',id=x.owner,hash=s['textHash']);return dict(id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=s['textHash'],changes=x.request()['changes']if changes is None else changes))
def reviewed(ids):
 f.invoke('reviewGroup',dict(ids=ids,target='portable'));v=f.state()['review'];assert v['status']=='ready',v;return v['token']
def receipt(cp):return next(v for v in json.loads(cp.read_text())['changes']if v['id']==x.owner)['slotSaveReceipt']
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});cp=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=cp.read_bytes()
 bad=prepare();next(iter(bad['declaration']['changes'][-1]['mapping']['bodies'].values()))['text']='return MissingWholeGroupValue;';rpc('applySlots',False,**bad);assert cp.read_bytes()==baseline;x.unchanged();f.checked('invalid last native CSharp rejects both explicit sources and preserves checkpoint')
 request=prepare();path=f.project/x.retained_header;raw=path.read_bytes();path.write_bytes(raw+b'\n// peer before Save\n')
 try:rpc('applySlots',False,**request);assert cp.read_bytes()==baseline and path.read_bytes()!=raw
 finally:
  path.write_bytes(raw)
  if path.name==x.extra_path:os.utime(path,ns=(path.stat().st_atime_ns,x.extra_mtime))
 x.unchanged();f.checked('changed retained caller header before Save rejects the complete original source observation')
 reply=rpc('applySlots',**prepare());assert reply['atomic']and reply['checkpointSaved'];ids=x.verify(cp);plans=copy.deepcopy(receipt(cp)['nativeBodyContexts']);reads=copy.deepcopy(receipt(cp)['readGuards']);f.stop();f.start(1);f.invoke('select',dict(id=x.owner));assert x.verify(cp)==ids
 late='원래 private 프레임을 유지하는 후속 설명 · 😀';rpc('applySlots',**prepare([dict(type='description',text=late)]));assert receipt(cp)['nativeBodyContexts']==plans and receipt(cp)['readGuards']==reads
 rows={v['id']:v for v in json.loads(cp.read_text())['changes']};fn=x.functions[0];meta=dict(type='function-edit',id=fn,hash=h(rows[fn]['draft']),name=x.labels[0],description='후속 함수 설명',signature=copy.deepcopy(x.old));rpc('applySlots',**prepare([meta]));assert receipt(cp)['nativeBodyContexts']==plans and receipt(cp)['readGuards']==reads;x.unchanged();f.checked('cold and owner/function metadata Saves retain complete source plans and original read versions')
 # A later explicit source edit updates only its manual text, retaining the original source hash/flow receipt.
 rows={v['id']:v for v in json.loads(cp.read_text())['changes']};manual=copy.deepcopy(plans[0]);manual['hash']=h(rows[fn]['draft']);body=next(iter(manual['mapping']['bodies'].values()));body['hash']=h(rows[x.whole_node]['draft']);body['text']+='// later explicit private source 😀\n';body['helpers']+='// later explicit helpers 😀\n';rpc('applySlots',**prepare([manual]));x.selected[fn]=body['text'];x.selected_helpers=body['helpers'];assert receipt(cp)['readGuards']==reads;assert next(iter(receipt(cp)['nativeBodyContexts'][0]['mapping']['bodies'].values()))['hash']==next(iter(plans[0]['mapping']['bodies'].values()))['hash'];plans=copy.deepcopy(receipt(cp)['nativeBodyContexts']);x.verify(cp);f.checked('later manual private source edit preserves original function/source/flow proofs and replaces only the explicitly supplied text/helpers')
 # Same-contract metadata may not adopt a changed original source.
 request=prepare([dict(type='description',text=late+' next')]);path=f.project/x.graph_path;raw=path.read_bytes();path.write_bytes(raw+b'\n');saved=cp.read_bytes()
 try:rpc('applySlots',False,**request);assert cp.read_bytes()==saved
 finally:
  path.write_bytes(raw)
  if path.name==x.extra_path:os.utime(path,ns=(path.stat().st_atime_ns,x.extra_mtime))
 for index,name in enumerate([x.graph_path,x.extra_path,x.node_path]):
  token=reviewed(ids);saved=cp.read_bytes();path=f.project/name;raw=path.read_bytes();path.write_bytes(raw+b'\n// peer after Review\n'if name.endswith(('.csbody','.celem'))else raw+b'\n')
  try:
   result=f.invoke('confirmGroup',dict(ids=ids,token=token))['result']['result'];assert result['sourceConfirmed']is False,result;assert cp.read_bytes()==saved and path.read_bytes()!=raw
  finally:
   path.write_bytes(raw)
   if path.name==x.extra_path:os.utime(path,ns=(path.stat().st_atime_ns,x.extra_mtime))
  x.unchanged();f.stop();f.start(index+2);f.invoke('select',dict(id=x.owner));assert receipt(cp)['nativeBodyContexts']==plans and receipt(cp)['readGuards']==reads;f.checked(name+' post-Review conflict blocks final Confirm and preserves peer/original files')
 token=reviewed(ids);out=f.invoke('confirmGroup',dict(ids=ids,token=token))['result']['result'];assert out.get('sourceConfirmed')is not False;x.verify_live();assert f.metadata('inspect',text=x.n.a.info.read_text())['description']==late;f.checked('fresh Review/Confirm after original restoration executes both explicit bodies:20; original CSharp and private/caller graph bytes preserved')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
