"""One ordinary owned return value cannot grant contract, branch or node edits."""
import json,uuid
import v666_root_return_recovery_fixture as t
x=t.x;f=x.f
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});original=t.read();before=x.checkpoint();text='{"constant":37}'
 def request():return dict(action='authorBatch',id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=original['checkpointHash'],sourceProof=x.proof(original),edits=[dict(action='exit',node=t.node,name='return',valueJson=text)])
 def rejected(name,mutate):
  q=request();mutate(q);v=f.invoke('blueprint',q,False);assert not v['result']['ok'];assert x.checkpoint()==before;x.original();assert t.read()['sources']==original['sources'];f.checked(name)
 rejected('root return rejects stale checkpoint',lambda q:q.update(checkpointHash='0'*64))
 def tamper(q):
  rows=json.loads(q['sourceProof']);rows[0][2]='0'*64;q['sourceProof']=json.dumps(rows)
 rejected('root return rejects tampered closure',tamper)
 rejected('root return requires exact virtual pin identity',lambda q:q['edits'][0].update(node='after'))
 rejected('root return cannot infer another exit',lambda q:q['edits'][0].update(name='yes',node='$exit:yes'))
 rejected('root return cannot infer owner/slot permission',lambda q:q.update(owner=f.id,ownerHash='0'*64,ownerRevision=0))
 rejected('root return cannot infer private frame permission',lambda q:q['edits'][0].update(frame=t.graph+'/graph:missing'))
 rejected('root return cannot grant mixed node arguments',lambda q:q['edits'].append(dict(action='argument',node='after',name='value',valueJson=text)))
 rejected('root return cannot grant mixed source edits',lambda q:q['edits'].append(dict(action='source',node='after',text=x.after_source)))
 rejected('root return cannot grant public contract edits',lambda q:q['edits'].append(dict(action='rootParameters',node='$root',definition={})))
 rejected('root return cannot grant route edits',lambda q:q['edits'].append(dict(action='route',node='after',port='next',to='exit:return')))
 rejected('root return rejects extra fields',lambda q:q['edits'][0].update(port='case:positive'))
 rejected('root return requires a string expression',lambda q:q['edits'][0].update(valueJson=37))
 rejected('root return preserves declared return type validation',lambda q:q['edits'][0].update(valueJson='{"constant":"wrong"}'))
 flow=x.read(x.graph);q=request();q.update(id=x.graph,checkpointHash=flow['checkpointHash'],sourceProof=x.proof(flow));assert not f.invoke('blueprint',q,False)['result']['ok'];assert x.checkpoint()==before;x.original();f.checked('a void function cannot borrow ordinary data-return admission')
 p=f.project/t.source_file;raw=p.read_bytes();p.write_bytes(raw+b' ')
 try:q=request();reply=f.invoke('blueprint',q)['result']['result'];assert reply['checkpointSaved']and reply['sourceWritten']is False;assert p.read_bytes()==raw+b' ';assert all(path.read_bytes()==value for path,value in x.physical.items()if path!=p)
 finally:p.write_bytes(raw)
 x.original();saved=x.checkpoint();assert t.current()=={'constant':37};assert f.invoke('blueprint',q)['result']['result']['checkpointSaved']and x.checkpoint()==saved;assert f.invoke('draftHistory',{'action':'inspect'})['result']['result']['undo']['available'];f.stop();f.start(1);assert x.checkpoint()==saved and t.current()=={'constant':37};x.original();query={**q,'action':'settledAuthorBatch'};assert f.invoke('blueprint',query)['result']['result']['settled'];checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));raw=checkpoint.read_bytes();doc=json.loads(raw);graph=next(u for u in doc['changes']if u['id']==t.graph);assert graph['authorSaveReceipt']['ownedRootReturn']is True;graph['authorSaveReceipt']['sources'][t.graph]['hash']='0'*64;checkpoint.write_text(json.dumps(doc));f.stop();f.start(2);assert not f.invoke('blueprint',query)['result']['result']['settled'];x.original();f.stop();checkpoint.write_bytes(raw);f.start(3);assert f.invoke('blueprint',query)['result']['result']['settled'];x.original();f.checked('root return is durable/idempotent with shared history and verified cold receipt; physical publication remains behind final Confirm CAS')
 data=t.read();f.invoke('blueprint',dict(action='outputNodes',id=t.graph,basis=data['basis'],edits=[dict(kind='create',node='writer_guard',output='return')]));f.invoke('saveDraft',{});data=t.read();held=x.checkpoint();q=dict(action='authorBatch',id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=x.proof(data),edits=[dict(action='exit',node=t.node,name='return',valueJson=text)]);assert not f.invoke('blueprint',q,False)['result']['ok'];assert x.checkpoint()==held;x.original();f.checked('an existing export writer cannot borrow terminal-only return admission')
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
print('ROOT_RETURN_RECOVERY_API_FIXTURE',f.case,flush=True)
