"""Exercise existing native candidate, rejection, durability, receipt and history."""
import copy,json,uuid
import v666_direct_creation_recovery_fixture as t
x=t.x;f=t.f;node='action_'+uuid.uuid4().hex
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});before=t.checkpoint().read_bytes();q=t.request(node)
 def reject(label,patch):
  request=copy.deepcopy(q);request['attempt']=uuid.uuid4().hex;patch(request);f.invoke('blueprint',request,False);assert t.checkpoint().read_bytes()==before and t.current(node)is None;x.original();f.checked(label)
 reject('direct creation rejects stale checkpoint',lambda q:q.update(checkpointHash='0'*64))
 reject('direct creation rejects tampered source closure',lambda q:q.update(sourceProof=q['sourceProof'].replace('Owned.Elements::Pair','Foreign.Elements::Pair')))
 reject('direct creation rejects an already existing node identity',lambda q:q['edits'][0].update(node='body'))
 reject('direct creation rejects unknown public graph ownership',lambda q:q.update(id='Foreign.Elements::PairBody/body:common'))
 checkpoint=t.checkpoint();checkpoint.chmod(0o400)
 try:f.invoke('blueprint',q,False);assert checkpoint.read_bytes()==before and t.current(node)is None;x.original()
 finally:checkpoint.chmod(0o600)
 observed=f.invoke('blueprint',{**q,'action':'settledAuthorBatch'})['result']['result'];assert observed['settled']is False and observed['baselineUnchanged']is True,observed
 tampered={**q,'action':'settledAuthorBatch','sourceProof':q['sourceProof'].replace('Owned.Elements::Pair','Foreign.Elements::Pair')};assert not f.invoke('blueprint',tampered)['result']['result']['baselineUnchanged'];assert not f.invoke('blueprint',{**q,'action':'settledAuthorBatch','checkpointHash':'0'*64})['result']['result']['baselineUnchanged']
 physical=f.project/t.source_file;raw=physical.read_bytes();physical.write_bytes(raw+b' ')
 try:assert not f.invoke('blueprint',{**q,'action':'settledAuthorBatch'})['result']['result']['baselineUnchanged']
 finally:physical.write_bytes(raw)
 x.original();assert checkpoint.read_bytes()==before and t.current(node)is None;f.checked('unapplied baseline observation requires exact checkpoint/full source closure/physical originals; tampering and physical peer changes cannot authorize correction')
 f.checked('failed candidate checkpoint preserves complete original graph/live state and physical sources')
 assert f.invoke('blueprint',q)['result']['result']['checkpointSaved'];assert t.current(node)['source']==t.text;raw=checkpoint.read_bytes();assert f.invoke('blueprint',q)['result']['result']['checkpointSaved']and checkpoint.read_bytes()==raw;x.original();assert not t.path(node).exists();f.stop();f.start(1);assert t.current(node)['source']==t.text;assert f.invoke('blueprint',{**q,'action':'settledAuthorBatch'})['result']['result']['settled'];x.original();f.checked('one native candidate durably creates source and both routes, replay is idempotent and cold receipt settles without physical writes')
 history=f.invoke('draftHistory',dict(action='inspect'))['result']['result'];assert history['boundary']=='OWNERSHIP_CHANGED'and not history['undo']['available']and not history['redo']['available'];f.invoke('saveDraft',{});f.stop();f.start(2);assert t.current(node)['source']==t.text;x.original();history=f.invoke('draftHistory',dict(action='inspect'))['result']['result'];assert history['boundary']=='OWNERSHIP_CHANGED'and not history['undo']['available'];f.checked('existing source-only history ownership boundary persists across creation/cold; no implicit inverse deletes the new owned source')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
print('DIRECT_CREATION_RECOVERY_FIXTURE',f.case,flush=True)
