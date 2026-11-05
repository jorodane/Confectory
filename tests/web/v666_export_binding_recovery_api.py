"""One existing owned export binding cannot grant other structural/code/contract edits."""
import copy,json,uuid
import v666_export_binding_recovery_fixture as t
x=t.x;f=x.f
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});original=t.read();before=x.checkpoint();text='right'
 def request():return dict(action='authorBatch',id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=original['checkpointHash'],sourceProof=x.proof(original),edits=[dict(action='outputNodes',node='$exports',definition=dict(edits=[dict(kind='bind',node=t.node,output=text)]))])
 def rejected(name,mutate):
  q=request();mutate(q);v=f.invoke('blueprint',q,False);assert not v['result']['ok'];assert x.checkpoint()==before;x.original();assert t.read()['sources']==original['sources'];f.checked(name)
 def edit(q):return q['edits'][0]['definition']['edits'][0]
 rejected('export binding rejects stale checkpoint',lambda q:q.update(checkpointHash='0'*64))
 def tamper(q):
  rows=json.loads(q['sourceProof']);rows[0][2]='0'*64;q['sourceProof']=json.dumps(rows)
 rejected('export binding rejects tampered source closure',tamper)
 rejected('export binding requires exact synthetic origin',lambda q:q['edits'][0].update(node='body'))
 rejected('export cannot borrow ordinary code argument admission',lambda q:q.update(edits=[dict(action='argument',node=t.node,name='value',valueJson=text)]))
 rejected('export binding requires an existing export',lambda q:edit(q).update(node='missing'))
 rejected('export binding cannot edit ordinary C# arguments',lambda q:edit(q).update(node='body'))
 rejected('export binding cannot infer owner/slot permission',lambda q:q.update(owner=f.id,ownerHash='0'*64,ownerRevision=0))
 rejected('export binding cannot infer private frame permission',lambda q:q['edits'][0].update(frame=t.graph+'/graph:missing'))
 rejected('export binding cannot mix a value edit',lambda q:edit(q).update(valueJson='{"constant":37}'))
 rejected('export binding cannot infer node creation',lambda q:edit(q).update(kind='create',output='result'))
 rejected('export binding cannot infer node deletion',lambda q:edit(q).update(kind='remove'))
 rejected('export binding requires one explicit assignment',lambda q:q['edits'][0]['definition']['edits'].append(copy.deepcopy(edit(q))))
 rejected('export binding cannot grant mixed source edits',lambda q:q['edits'].append(dict(action='source',node='body',text=t.original_source)))
 rejected('export binding cannot grant contract edits',lambda q:q['edits'].append(dict(action='rootParameters',node='$root',definition={})))
 rejected('export binding rejects extra definition fields',lambda q:q['edits'][0]['definition'].update(profile='sync-acyclic-v1'))
 rejected('export binding rejects extra assignment fields',lambda q:edit(q).update(valueJson='{"constant":17}'))
 rejected('export binding requires a declared output',lambda q:edit(q).update(output='missing'))
 rejected('export binding requires a string output identity',lambda q:edit(q).update(output=37))
 rejected('export binding preserves native incompatible-output validation',lambda q:edit(q).update(output='flag'))
 p=f.project/t.source_file;raw=p.read_bytes();p.write_bytes(raw+b' ')
 try:q=request();reply=f.invoke('blueprint',q)['result']['result'];assert reply['checkpointSaved']and reply['sourceWritten']is False;assert p.read_bytes()==raw+b' ';assert all(path.read_bytes()==value for path,value in x.physical.items()if path!=p)
 finally:p.write_bytes(raw)
 x.original();saved=x.checkpoint();assert t.current()=='right';assert f.invoke('blueprint',q)['result']['result']['checkpointSaved']and x.checkpoint()==saved;assert f.invoke('draftHistory',{'action':'inspect'})['result']['result']['undo']['available'];f.stop();f.start(1);assert x.checkpoint()==saved and t.current()=='right';x.original();query={**q,'action':'settledAuthorBatch'};assert f.invoke('blueprint',query)['result']['result']['settled'];checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));raw=checkpoint.read_bytes();doc=json.loads(raw);graph=next(u for u in doc['changes']if u['id']==t.graph);assert graph['authorSaveReceipt']['ownedOutputBinding']is True;graph['authorSaveReceipt']['sources'][t.graph]['hash']='0'*64;checkpoint.write_text(json.dumps(doc));f.stop();f.start(2);assert not f.invoke('blueprint',query)['result']['result']['settled'];x.original();f.stop();checkpoint.write_bytes(raw);f.start(3);assert f.invoke('blueprint',query)['result']['result']['settled'];x.original();f.checked('explicit export binding is durable/idempotent with shared history and verified cold receipt; physical sources remain behind final Confirm CAS')
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
print('EXPORT_BINDING_RECOVERY_API_FIXTURE',f.case,flush=True)
