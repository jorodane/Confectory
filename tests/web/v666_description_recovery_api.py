"""Owned description candidates retain history/semantic staleness and strict admission."""
import json,sys,uuid
import v666_root_execution_fixture as x
f=x.f
try:
 f.start(0);f.invoke('select',dict(id=x.feature));f.invoke('saveDraft',{});original=x.read();before=x.checkpoint()
 def request():return dict(action='authorBatch',id=x.graph,attempt=uuid.uuid4().hex,checkpointHash=original['checkpointHash'],sourceProof=x.proof(original),edits=[dict(action='intent',node='choose',text='명시적으로 검토할 설명 α 😀'),dict(action='argument',node='choose',name='amount',valueJson='{"constant":2}')])
 def rejected(name,change):
  q=request();change(q);value=f.invoke('blueprint',q,False);assert not value['result']['ok'];assert x.checkpoint()==before;x.original();assert x.read()['sources']==original['sources'];f.checked(name)
 rejected('stale checkpoint refuses a description candidate',lambda q:q.update(checkpointHash='0'*64))
 def tamper(q):
  proof=json.loads(q['sourceProof']);proof[0][2]='0'*64;q['sourceProof']=json.dumps(proof)
 rejected('tampered closure refuses a description candidate',tamper)
 rejected('missing code node cannot borrow description admission',lambda q:q['edits'][0].update(node='missing'))
 rejected('export node cannot borrow description admission',lambda q:q['edits'][0].update(node='publish_yes'))
 rejected('owner context cannot be inferred by description admission',lambda q:q.update(owner=f.id,ownerHash='0'*64,ownerRevision=0))
 rejected('private frame cannot be inferred by description admission',lambda q:q['edits'][0].update(frame=x.graph+'/graph:missing'))
 rejected('route change is outside description-only admission',lambda q:q['edits'].append(dict(action='route',node='choose',to='exit:yes')))
 rejected('parameter change is outside description-only admission',lambda q:q['edits'].append(dict(action='parameters',node='choose',signature={'args':[],'return':'void'})))
 q=request()
 result=f.invoke('blueprint',q)['result']['result'];assert result['checkpointSaved']and result['sourceWritten']is False;after=x.read();assert after['diagnostics']['state']=='needs-implementation';saved=x.checkpoint();x.original();assert f.invoke('blueprint',q)['result']['result']['checkpointSaved']and x.checkpoint()==saved
 assert f.invoke('draftHistory',{'action':'inspect'})['result']['result']['undo']['available'];f.stop();f.start(1);assert x.checkpoint()==saved and x.read()['diagnostics']['state']=='needs-implementation';x.original();f.checked('one mixed intent/value candidate is durable/idempotent with shared history while original C# still requires explicit implementation review')
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
print('DESCRIPTION_RECOVERY_API_FIXTURE',f.case,flush=True)
