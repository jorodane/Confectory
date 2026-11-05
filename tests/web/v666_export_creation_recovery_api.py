"""One new export/value/manual serial insertion cannot grant other contracts or ownership."""
import copy,json,uuid
import v666_export_creation_recovery_fixture as t
x=t.x;f=x.f
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});original=t.read();before=x.checkpoint()
 def request():return dict(action='authorBatch',id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=original['checkpointHash'],sourceProof=x.proof(original),edits=[dict(action='outputNodes',node='$exports',definition=dict(edits=t.edits(t.node)))])
 def rows(q):return q['edits'][0]['definition']['edits']
 def rejected(name,mutate):
  q=request();mutate(q);v=f.invoke('blueprint',q,False);assert not v['result']['ok'];assert x.checkpoint()==before and t.current(t.node)is None;x.original();assert t.read()['sources']==original['sources'];f.checked(name)
 rejected('export creation rejects stale checkpoint',lambda q:q.update(checkpointHash='0'*64))
 def tamper(q):
  proof=json.loads(q['sourceProof']);proof[0][2]='0'*64;q['sourceProof']=json.dumps(proof)
 rejected('export creation rejects tampered complete source proof',tamper)
 rejected('export creation requires exact synthetic origin',lambda q:q['edits'][0].update(node='body'))
 rejected('export creation cannot infer owner/slot permission',lambda q:q.update(owner=f.id,ownerHash='0'*64,ownerRevision=0))
 rejected('export creation cannot infer private frame permission',lambda q:q['edits'][0].update(frame=t.graph+'/graph:missing'))
 rejected('export creation requires one explicit complete plan',lambda q:rows(q).pop())
 rejected('export creation cannot grant a second creation',lambda q:rows(q).append(dict(kind='create',node='other',output='right')))
 rejected('export creation cannot grant source mixing',lambda q:q['edits'].append(dict(action='source',node='body',text=t.original_source)))
 rejected('export creation cannot grant public contract edits',lambda q:q['edits'].append(dict(action='rootParameters',node='$root',definition={})))
 rejected('export creation rejects extra definition fields',lambda q:q['edits'][0]['definition'].update(profile='sync-acyclic-v1'))
 rejected('export creation rejects extra row fields',lambda q:rows(q)[0].update(source='return;'))
 def replace_id(q,chosen):
  for row in rows(q):
   for key in ['node','to']:
    if row.get(key)==t.node:row[key]=chosen
 rejected('export creation requires a new ID',lambda q:replace_id(q,'keep'))
 rejected('export creation preserves native stable-ID validation',lambda q:replace_id(q,'invalid/id'))
 rejected('export creation requires one shared new-node identity',lambda q:rows(q)[1].update(node='keep'))
 rejected('export creation cannot modify another value',lambda q:rows(q)[1].update(kind='bind',output='right'))
 rejected('export creation requires an observed direct code predecessor',lambda q:rows(q)[2].update(node='missing'))
 rejected('export creation cannot borrow an export as code predecessor',lambda q:rows(q)[2].update(node='keep'))
 rejected('export creation must preserve the observed next successor',lambda q:rows(q)[3].update(to='keep'))
 rejected('export creation requires both explicit next connections',lambda q:rows(q)[2].update(to='keep'))
 rejected('export creation cannot introduce self routing',lambda q:rows(q)[3].update(to=t.node))
 rejected('export creation requires a declared output',lambda q:rows(q)[0].update(output='missing'))
 rejected('export creation requires string identities',lambda q:rows(q)[0].update(node=37))
 rejected('export creation requires a string expression',lambda q:rows(q)[1].update(valueJson=37))
 rejected('export creation preserves declared output type validation',lambda q:rows(q)[0].update(output='flag'))
 p=f.project/t.source_file;raw=p.read_bytes();p.write_bytes(raw+b' ')
 try:q=request();reply=f.invoke('blueprint',q)['result']['result'];assert reply['checkpointSaved']and reply['sourceWritten']is False;assert p.read_bytes()==raw+b' ';assert all(path.read_bytes()==value for path,value in x.physical.items()if path!=p)
 finally:p.write_bytes(raw)
 x.original();saved=x.checkpoint();assert t.current_value(t.node)=={'constant':37};assert f.invoke('blueprint',q)['result']['result']['checkpointSaved']and x.checkpoint()==saved;assert f.invoke('draftHistory',{'action':'inspect'})['result']['result']['undo']['available'];f.stop();f.start(1);assert x.checkpoint()==saved and t.current(t.node);x.original();query={**q,'action':'settledAuthorBatch'};assert f.invoke('blueprint',query)['result']['result']['settled'];checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));raw=checkpoint.read_bytes();doc=json.loads(raw);graph=next(u for u in doc['changes']if u['id']==t.graph);assert graph['authorSaveReceipt']['ownedOutputCreation']is True;graph['authorSaveReceipt']['sources'][t.graph]['hash']='0'*64;checkpoint.write_text(json.dumps(doc));f.stop();f.start(2);assert not f.invoke('blueprint',query)['result']['result']['settled'];x.original();f.stop();checkpoint.write_bytes(raw);f.start(3);assert f.invoke('blueprint',query)['result']['result']['settled'];x.original();f.checked('explicit export create/value/both routes is durable/idempotent under the same ID; shared history and exact cold receipt precede final Confirm CAS')
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
print('EXPORT_CREATION_RECOVERY_API_FIXTURE',f.case,flush=True)
