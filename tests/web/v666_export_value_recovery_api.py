"""One existing owned export value cannot grant structural/code/contract edits."""
import copy,json,uuid
import v666_export_value_recovery_fixture as t
x=t.x;f=x.f
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});original=t.read();before=x.checkpoint();text='{"constant":37}'
 def request():return dict(action='authorBatch',id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=original['checkpointHash'],sourceProof=x.proof(original),edits=[dict(action='outputNodes',node='$exports',definition=dict(edits=[dict(kind='value',node=t.node,valueJson=text)]))])
 def rejected(name,mutate):
  q=request();mutate(q);v=f.invoke('blueprint',q,False);assert not v['result']['ok'];assert x.checkpoint()==before;x.original();assert t.read()['sources']==original['sources'];f.checked(name)
 def edit(q):return q['edits'][0]['definition']['edits'][0]
 rejected('export value rejects stale checkpoint',lambda q:q.update(checkpointHash='0'*64))
 def tamper(q):
  rows=json.loads(q['sourceProof']);rows[0][2]='0'*64;q['sourceProof']=json.dumps(rows)
 rejected('export value rejects tampered source closure',tamper)
 rejected('export value requires exact synthetic origin',lambda q:q['edits'][0].update(node='after'))
 rejected('export cannot borrow ordinary code argument admission',lambda q:q.update(edits=[dict(action='argument',node=t.node,name='value',valueJson=text)]))
 rejected('export value requires an existing export',lambda q:edit(q).update(node='missing'))
 rejected('export value cannot edit ordinary C# arguments',lambda q:edit(q).update(node='after'))
 rejected('export value cannot edit a referenced call',lambda q:edit(q).update(node='invoke'))
 rejected('export value cannot infer owner/slot permission',lambda q:q.update(owner=f.id,ownerHash='0'*64,ownerRevision=0))
 rejected('export value cannot infer private frame permission',lambda q:q['edits'][0].update(frame=t.graph+'/graph:missing'))
 rejected('export value cannot infer output binding changes',lambda q:edit(q).update(kind='bind',output='result'))
 rejected('export value cannot infer node creation',lambda q:edit(q).update(kind='create',output='result'))
 rejected('export value cannot infer node deletion',lambda q:edit(q).update(kind='remove'))
 rejected('export value requires one explicit assignment',lambda q:q['edits'][0]['definition']['edits'].append(copy.deepcopy(edit(q))))
 rejected('export value cannot grant mixed source edits',lambda q:q['edits'].append(dict(action='source',node='after',text=x.after_source)))
 rejected('export value cannot grant contract edits',lambda q:q['edits'].append(dict(action='rootParameters',node='$root',definition={})))
 rejected('export value rejects extra definition fields',lambda q:q['edits'][0]['definition'].update(profile='sync-acyclic-v1'))
 rejected('export value rejects extra assignment fields',lambda q:edit(q).update(output='result'))
 rejected('export value requires a string expression',lambda q:edit(q).update(valueJson=37))
 rejected('export value preserves native declared type validation',lambda q:edit(q).update(valueJson='{"constant":"wrong"}'))
 p=f.project/t.source_file;raw=p.read_bytes();p.write_bytes(raw+b' ')
 try:q=request();reply=f.invoke('blueprint',q)['result']['result'];assert reply['checkpointSaved']and reply['sourceWritten']is False;assert p.read_bytes()==raw+b' ';assert all(path.read_bytes()==value for path,value in x.physical.items()if path!=p)
 finally:p.write_bytes(raw)
 x.original();saved=x.checkpoint();assert t.current()=={'constant':37};assert f.invoke('blueprint',q)['result']['result']['checkpointSaved']and x.checkpoint()==saved;assert f.invoke('draftHistory',{'action':'inspect'})['result']['result']['undo']['available'];f.stop();f.start(1);assert x.checkpoint()==saved and t.current()=={'constant':37};x.original();query={**q,'action':'settledAuthorBatch'};assert f.invoke('blueprint',query)['result']['result']['settled'];checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));raw=checkpoint.read_bytes();doc=json.loads(raw);graph=next(u for u in doc['changes']if u['id']==t.graph);assert graph['authorSaveReceipt']['ownedOutputValue']is True;graph['authorSaveReceipt']['sources'][t.graph]['hash']='0'*64;checkpoint.write_text(json.dumps(doc));f.stop();f.start(2);assert not f.invoke('blueprint',query)['result']['result']['settled'];x.original();f.stop();checkpoint.write_bytes(raw);f.start(3);assert f.invoke('blueprint',query)['result']['result']['settled'];x.original();f.checked('explicit export value is durable/idempotent with shared history and verified cold receipt; physical sources remain behind final Confirm CAS')
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
print('EXPORT_VALUE_RECOVERY_API_FIXTURE',f.case,flush=True)
