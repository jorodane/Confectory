"""Atomic checkpoint and observed local native-import conflicts; isolated fixture."""
import copy,json
import v666_body_imports_fixture as x
f=x.f
def rpc(action,ok=True,**body):return f.invoke('blueprint',dict(action=action,**body),ok)['result'].get('result')
def schema():f.invoke('schema',dict(id=x.owner));return f.state()['schema']
def prepare():
 s=schema();basis=rpc('readOwnerEdits',id=x.owner,hash=s['textHash']);return dict(id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=s['textHash'],changes=x.request()['changes']))
if x.mode!='dependencies':
 import os,sys,runpy
 os.environ['CONFECTORY_SHARED_BODIES']='1';sys.modules['v536_information_shared_bodies_fixture']=x
 runpy.run_path(str(f.repo/'tests/web/v536_information_shared_callers_api.py'),run_name='__main__')
else:
 try:
  f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes();request=prepare();path=f.project/x.helper_file;original=path.read_bytes();peer=original+b'\n// peer before Save\n';path.write_bytes(peer);rpc('applySlots',False,**request);assert checkpoint.read_bytes()==baseline and path.read_bytes()==peer;assert all((f.project/p).read_bytes()==v for p,v in x.snapshot.items()if p!=x.helper_file);f.checked('local imported function change before Save rejects both native bodies and preserves peer bytes/checkpoint');path.write_bytes(original)
  f.stop();f.start(1);f.invoke('select',dict(id=x.owner));request=prepare();reply=rpc('applySlots',**request);assert reply['atomic']and reply['checkpointSaved'];ids=x.verify(checkpoint);saved=checkpoint.read_bytes();x.unchanged()
  def reviewed():
   f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review;return review['token']
  for number,name in enumerate([x.helper_file,x.helper_body]):
   phase_saved=checkpoint.read_bytes();(f.case/('before-review-'+str(number)+'.json')).write_bytes(phase_saved)
   token=reviewed();after_review=checkpoint.read_bytes()
   before_doc=json.loads(phase_saved);after_doc=json.loads(after_review)
   before_doc['history'].pop('epoch');after_doc['history'].pop('epoch')
   for document in [before_doc,after_doc]:
    for row in document['changes']:
     if row['id']==f.n+'ProjectManifest':row.pop('revision')
   assert before_doc==after_doc
   (f.case/('after-review-'+str(number)+'.json')).write_bytes(after_review)
   phase_saved=after_review;assert x.verify(checkpoint)==ids
   p=f.project/name;raw=p.read_bytes();peer=raw+b'\n// peer after Review\n';p.write_bytes(peer)
   outcome=f.invoke('confirmGroup',dict(ids=ids,token=token))['result']['result'];assert outcome['sourceConfirmed'] is False,outcome
   (f.case/('after-rejected-confirm-'+str(number)+'.json')).write_bytes(checkpoint.read_bytes())
   assert p.read_bytes()==peer and checkpoint.read_bytes()==phase_saved
   assert all((f.project/path).read_bytes()==value for path,value in x.snapshot.items()if path!=name)
   (f.case/('dependency-final-cas-'+str(number)+'.json')).write_text(json.dumps(dict(source=name,peerPreserved=True,checkpointPreserved=True,bodyFilesUnchanged=True),indent=2))
   f.checked('post-Review '+name+' change rejects final Confirm without publishing either native body')
   p.write_bytes(raw);f.stop();f.start(2+number);f.invoke('select',dict(id=x.owner));assert x.verify(checkpoint)==ids
   (f.case/('after-cold-'+str(number)+'.json')).write_bytes(checkpoint.read_bytes())
  token=reviewed();f.invoke('confirmGroup',dict(ids=ids,token=token));x.verify_live();assert all((f.project/p).read_bytes()==value for p,value in x.snapshot.items()if p not in x.changed_source_paths and p!='FreeInfo.celem'and p not in ['elements/'+fn.split('::')[1]+'.celem'for fn in x.functions]);f.checked('explicit new Review after exact dependency restoration confirms both authored bodies and executes result26')
 finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
