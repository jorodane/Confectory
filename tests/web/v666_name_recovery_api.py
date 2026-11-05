"""Plain owned root code name admission cannot grant another context or contract."""
import json,uuid
import v666_root_execution_fixture as x
f=x.f
try:
 f.start(0);f.invoke('select',dict(id=x.main_id));f.invoke('saveDraft',{});original=x.read(x.caller);before=x.checkpoint();text='명시한 이름 α 😀'
 def request():return dict(action='authorBatch',id=x.caller,attempt=uuid.uuid4().hex,checkpointHash=original['checkpointHash'],sourceProof=x.proof(original),edits=[dict(action='rename',node='after',text=text)])
 def rejected(name,mutate):
  q=request();mutate(q);v=f.invoke('blueprint',q,False);assert not v['result']['ok'];assert x.checkpoint()==before;x.original();assert x.read(x.caller)['sources']==original['sources'];f.checked(name)
 rejected('source candidate rejects stale checkpoint',lambda q:q.update(checkpointHash='0'*64))
 def tamper(q):
  rows=json.loads(q['sourceProof']);rows[0][2]='0'*64;q['sourceProof']=json.dumps(rows)
 rejected('source candidate rejects tampered closure',tamper)
 rejected('source candidate rejects missing node',lambda q:q['edits'][0].update(node='missing'))
 rejected('name admission cannot edit a referenced call',lambda q:q['edits'][0].update(node='invoke'))
 rejected('name admission cannot infer owner/slot permission',lambda q:q.update(owner=f.id,ownerHash='0'*64,ownerRevision=0))
 rejected('name admission cannot infer private frame permission',lambda q:q['edits'][0].update(frame=x.caller+'/graph:missing'))
 rejected('name admission does not grant mixed route edits',lambda q:q['edits'].append(dict(action='route',node='after',to='exit:return')))
 rejected('name admission does not grant parameter changes',lambda q:q['edits'].append(dict(action='parameters',node='after',definition={})))
 rejected('blank display name is rejected',lambda q:q['edits'][0].update(text=' '))
 rejected('control characters are rejected',lambda q:q['edits'][0].update(text='name\ninvalid'))
 rejected('over-budget display name is rejected',lambda q:q['edits'][0].update(text='a'*257))
 rejected('rename cannot grant source mixing onto a referenced call',lambda q:q['edits'].append(dict(action='source',node='invoke',text=x.after_source)))
 p=f.project/'After.node.json';raw=p.read_bytes();p.write_bytes(raw+b' ')
 try:q=request();reply=f.invoke('blueprint',q)['result']['result'];assert reply['checkpointSaved']and reply['sourceWritten']is False;assert p.read_bytes()==raw+b' ';assert all(path.read_bytes()==value for path,value in x.physical.items()if path!=p)
 finally:p.write_bytes(raw)
 x.original();saved=x.checkpoint();assert next(n.get('displayName',n['id'])for n in x.read(x.caller)['nodes']if n['id']=='after')==text;assert f.invoke('blueprint',q)['result']['result']['checkpointSaved']and x.checkpoint()==saved;assert f.invoke('draftHistory',{'action':'inspect'})['result']['result']['undo']['available'];f.stop();f.start(1);assert x.checkpoint()==saved and next(n.get('displayName',n['id'])for n in x.read(x.caller)['nodes']if n['id']=='after')==text;x.original();query={**q,'action':'settledAuthorBatch'};assert f.invoke('blueprint',query)['result']['result']['settled'];checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));raw=checkpoint.read_bytes();doc=json.loads(raw);graph=next(u for u in doc['changes']if u['id']==x.caller);assert graph['authorSaveReceipt']['ownedRename']is True;graph['authorSaveReceipt']['sources'][x.caller]['hash']='0'*64;checkpoint.write_text(json.dumps(doc));f.stop();f.start(2);assert not f.invoke('blueprint',query)['result']['result']['settled'];x.original();f.stop();checkpoint.write_bytes(raw);f.start(3);assert f.invoke('blueprint',query)['result']['result']['settled'];x.original();f.checked('explicit display name is durable/idempotent with shared history; cold retains a receipt without changing code/IDs/contracts and rejects tampered receipt hashes; physical publication remains behind final Confirm CAS')
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
print('NAME_RECOVERY_API_FIXTURE',f.case,flush=True)
