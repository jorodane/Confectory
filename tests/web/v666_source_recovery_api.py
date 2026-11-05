"""Plain owned root code source admission cannot grant another context or contract."""
import json,uuid
import v666_root_execution_fixture as x
f=x.f
try:
 f.start(0);f.invoke('select',dict(id=x.main_id));f.invoke('saveDraft',{});original=x.read(x.caller);before=x.checkpoint();text=x.after_source+'\n// explicit source α 😀'
 def request():return dict(action='authorBatch',id=x.caller,attempt=uuid.uuid4().hex,checkpointHash=original['checkpointHash'],sourceProof=x.proof(original),edits=[dict(action='source',node='after',text=text)])
 def rejected(name,mutate):
  q=request();mutate(q);v=f.invoke('blueprint',q,False);assert not v['result']['ok'];assert x.checkpoint()==before;x.original();assert x.read(x.caller)['sources']==original['sources'];f.checked(name)
 rejected('source candidate rejects stale checkpoint',lambda q:q.update(checkpointHash='0'*64))
 def tamper(q):
  rows=json.loads(q['sourceProof']);rows[0][2]='0'*64;q['sourceProof']=json.dumps(rows)
 rejected('source candidate rejects tampered closure',tamper)
 rejected('source candidate rejects missing node',lambda q:q['edits'][0].update(node='missing'))
 rejected('source admission cannot edit a referenced call',lambda q:q['edits'][0].update(node='invoke'))
 rejected('source admission cannot infer owner/slot permission',lambda q:q.update(owner=f.id,ownerHash='0'*64,ownerRevision=0))
 rejected('source admission cannot infer private frame permission',lambda q:q['edits'][0].update(frame=x.caller+'/graph:missing'))
 rejected('source admission does not grant mixed route edits',lambda q:q['edits'].append(dict(action='route',node='after',to='exit:return')))
 rejected('source admission does not grant parameter changes',lambda q:q['edits'].append(dict(action='parameters',node='after',definition={})))
 p=f.project/'After.node.json';raw=p.read_bytes();p.write_bytes(raw+b' ')
 try:q=request();reply=f.invoke('blueprint',q)['result']['result'];assert reply['checkpointSaved']and reply['sourceWritten']is False;assert p.read_bytes()==raw+b' ';assert all(path.read_bytes()==value for path,value in x.physical.items()if path!=p)
 finally:p.write_bytes(raw)
 x.original();saved=x.checkpoint();assert next(n['source']for n in x.read(x.caller)['nodes']if n['id']=='after')==text;assert f.invoke('blueprint',q)['result']['result']['checkpointSaved']and x.checkpoint()==saved;assert f.invoke('draftHistory',{'action':'inspect'})['result']['result']['undo']['available'];f.stop();f.start(1);assert x.checkpoint()==saved and next(n['source']for n in x.read(x.caller)['nodes']if n['id']=='after')==text;x.original();f.checked('explicit C# source is durable/idempotent with shared history; physical publication remains behind final Confirm CAS')
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
print('SOURCE_RECOVERY_API_FIXTURE',f.case,flush=True)
