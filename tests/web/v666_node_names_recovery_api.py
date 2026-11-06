"""Existing ordinary node display-name Save: atomicity, ownership, receipts and shared history."""
import copy,json,uuid
import v666_node_names_recovery_fixture as t
x=t.x;f=t.f
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});original=t.read();p=t.checkpoint();before=p.read_bytes()
 def request():return dict(action='authorBatch',id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=original['checkpointHash'],sourceProof=x.proof(original),edits=t.edits(t.selected))
 def unchanged():assert p.read_bytes()==before and t.current()==t.original and t.read()['signature']==original['signature'];x.original()
 def rejected(name,mutate):
  q=request();mutate(q);reply=f.invoke('blueprint',q,False);assert not reply['result']['ok'];unchanged();f.checked(name)
 def tamper(q):
  rows=json.loads(q['sourceProof']);rows[0][2]='0'*64;q['sourceProof']=json.dumps(rows)
 rejected('names reject stale checkpoint',lambda q:q.update(checkpointHash='0'*64))
 rejected('names reject tampered full source closure',tamper)
 rejected('names reject missing node',lambda q:q['edits'][1].update(node='missing'))
 rejected('names reject duplicate node identity',lambda q:q['edits'][1].update(node='body'))
 rejected('names cannot infer owner/slot permission',lambda q:q.update(owner=f.id,ownerHash='0'*64,ownerRevision=0))
 rejected('names cannot infer private frame permission',lambda q:q['edits'][1].update(frame=t.graph+'/graph:missing'))
 rejected('names cannot rewrite another source',lambda q:q['edits'][1].update(action='source',text='return 37;'))
 rejected('names cannot change another intent',lambda q:q['edits'][1].update(action='intent',text='different intent'))
 rejected('names cannot grant parameters',lambda q:q['edits'].append(dict(action='parameters',node='body',definition={})))
 rejected('names cannot grant route changes',lambda q:q['edits'].append(dict(action='route',node='after',port='next',to='exit:return')))
 rejected('names cannot grant argument changes',lambda q:q['edits'].append(dict(action='argument',node='body',name='amount',valueJson='8')))
 for value,label in [(' ','blank'),('name\ninvalid','control'),('a'*257,'over budget'),(None,'nonstring')]:rejected('names reject '+label,lambda q,value=value:q['edits'][1].update(text=value))
 q=request();p.chmod(0o400)
 try:assert not f.invoke('blueprint',q,False)['result']['ok'];unchanged()
 finally:p.chmod(0o600)
 query={**q,'action':'settledAuthorBatch'};observed=f.invoke('blueprint',query)['result']['result'];assert observed['settled']is False and observed['baselineUnchanged']is True
 assert not f.invoke('blueprint',{**query,'checkpointHash':'0'*64})['result']['result'].get('baselineUnchanged');bad=copy.deepcopy(query);tamper(bad);assert not f.invoke('blueprint',bad)['result']['result'].get('baselineUnchanged')
 source=f.project/'Pair.after.node.json';raw=source.read_bytes();source.write_bytes(raw+b' ')
 try:assert not f.invoke('blueprint',query)['result']['result'].get('baselineUnchanged')
 finally:source.write_bytes(raw)
 unchanged();f.checked('failed name batch preserves all live names/checkpoint/C#; correction needs exact unapplied checkpoint/full closure/physical originals')
 assert f.invoke('blueprint',q)['result']['result']['checkpointSaved'];assert t.current()==t.selected;x.original();saved=p.read_bytes();assert f.invoke('blueprint',q)['result']['result']['checkpointSaved']and p.read_bytes()==saved
 f.stop();f.start(1);assert p.read_bytes()==saved and f.invoke('blueprint',query)['result']['result']['settled']and t.current()==t.selected;x.original();doc=json.loads(saved);g=next(u for u in doc['changes']if u['id']==t.graph);assert g['authorSaveReceipt']['ownedRename']is True and not g['authorSaveReceipt'].get('ownedSource');g['authorSaveReceipt']['sources'][t.graph]['hash']='0'*64;p.write_text(json.dumps(doc));f.stop();f.start(2);assert not f.invoke('blueprint',query)['result']['result']['settled'];f.stop();p.write_bytes(saved);f.start(3);assert f.invoke('blueprint',query)['result']['result']['settled'];x.original();f.checked('all names apply atomically/idempotently with existing ownedRename receipt; cold and tampered-receipt rejection preserve C#/contracts')
 for direction,wanted in [('undo',t.original),('redo',t.selected)]:
  history=f.invoke('draftHistory',dict(action='inspect'))['result']['result'];assert history[direction]['available'];assert f.invoke('draftHistory',dict(action=direction,token=history[direction]['token']))['result']['result']['accepted'];assert t.current()==wanted;x.original()
 f.invoke('saveDraft',{});f.stop();f.start(4);assert t.current()==t.selected;x.original();f.checked('shared name Undo/Redo/cold moves all selected names together without changing source/ID/contract/connection')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
print('NODE_NAMES_RECOVERY_API_FIXTURE',f.case,flush=True)
