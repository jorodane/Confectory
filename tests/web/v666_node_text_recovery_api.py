"""Closed existing-node name/intent/source fields: atomicity, ownership and recovery."""
import copy,json,uuid
import v666_node_text_recovery_fixture as t
x=t.x;f=t.f
def current_is(name,source,intent):
 now=t.current();return now["displayName"]==name and now["source"]==source and now["intent"]==intent
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});original=t.read();before=t.checkpoint().read_bytes()
 def request():return dict(action='authorBatch',id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=original['checkpointHash'],sourceProof=x.proof(original),edits=[dict(action='rename',node=t.node,text=t.name),dict(action='intent',node=t.node,text=t.intent),dict(action='source',node=t.node,text=t.text)])
 def unchanged():
  now=t.current();assert t.checkpoint().read_bytes()==before and now['displayName']==t.original_name and now['source']==t.original_source and now['intent']==t.original_intent;x.original()
 def rejected(name,mutate):
  q=request();mutate(q);reply=f.invoke('blueprint',q,False);assert not reply['result']['ok'];unchanged();f.checked(name)
 rejected('node text rejects stale checkpoint',lambda q:q.update(checkpointHash='0'*64))
 def tamper(q):
  p=json.loads(q['sourceProof']);p[0][2]='0'*64;q['sourceProof']=json.dumps(p)
 rejected('node text rejects tampered full closure',tamper)
 rejected('node text cannot edit two different nodes',lambda q:q['edits'][1].update(node='missing'))
 rejected('node text cannot infer owner/slot authority',lambda q:q.update(owner=f.id,ownerHash='0'*64,ownerRevision=0))
 rejected('node text cannot infer private frame authority',lambda q:q['edits'][1].update(frame=t.graph+'/graph:missing'))
 rejected('node text cannot grant parameter changes',lambda q:q['edits'].append(dict(action='parameters',node=t.node,definition={})))
 rejected('node text cannot grant mixed routes',lambda q:q['edits'].append(dict(action='route',node=t.node,port='next',to='exit:return')))
 rejected('node text cannot grant a duplicate description edit',lambda q:q['edits'].append(dict(action='intent',node=t.node,text='extra')))
 rejected('node text rejects blank display name',lambda q:q['edits'][0].update(text=' '))
 rejected('node text rejects control characters in display name',lambda q:q['edits'][0].update(text='name\ninvalid'))
 rejected('node text rejects over-budget display name',lambda q:q['edits'][0].update(text='a'*257))
 rejected('node text rejects a nonstring description',lambda q:q['edits'][1].update(text=37))
 rejected('node text rejects over-budget description',lambda q:q['edits'][1].update(text='a'*16385))
 rejected('node text rejects an extra argument edit',lambda q:q['edits'].append(dict(action='argument',node=t.node,name='amount',valueJson='8')))
 q=request();p=t.checkpoint();p.chmod(0o400)
 try:reply=f.invoke('blueprint',q,False);assert not reply['result']['ok'];unchanged()
 finally:p.chmod(0o600)
 query={**q,'action':'settledAuthorBatch'};observed=f.invoke('blueprint',query)['result']['result'];assert observed['settled']is False and observed['baselineUnchanged']is True
 bad={**query,'checkpointHash':'0'*64};assert not f.invoke('blueprint',bad)['result']['result'].get('baselineUnchanged');bad=copy.deepcopy(query);tamper(bad);assert not f.invoke('blueprint',bad)['result']['result'].get('baselineUnchanged')
 source=f.project/t.source_file;raw=source.read_bytes();source.write_bytes(raw+b' ')
 try:assert not f.invoke('blueprint',query)['result']['result'].get('baselineUnchanged')
 finally:source.write_bytes(raw)
 unchanged();f.checked('node text failure preserves live/checkpoint/originals; only exact unapplied checkpoint/closure/physical originals permit correction')
 reply=f.invoke('blueprint',q)['result']['result'];assert reply['checkpointSaved']and reply['sourceWritten']is False;assert current_is(t.name,t.text,t.intent);x.original();saved=p.read_bytes();assert f.invoke('blueprint',q)['result']['result']['checkpointSaved']and p.read_bytes()==saved
 f.stop();f.start(1);assert p.read_bytes()==saved and f.invoke('blueprint',query)['result']['result']['settled'];assert current_is(t.name,t.text,t.intent);x.original();doc=json.loads(saved);receipt=next(u for u in doc['changes']if u['id']==t.graph)['authorSaveReceipt'];assert receipt['ownedSource']is True
 graph=next(u for u in doc['changes']if u['id']==t.graph);graph['authorSaveReceipt']['sources'][t.graph]['hash']='0'*64;p.write_text(json.dumps(doc));f.stop();f.start(2);assert not f.invoke('blueprint',query)['result']['result']['settled'];f.stop();p.write_bytes(saved);f.start(3);assert f.invoke('blueprint',query)['result']['result']['settled'];x.original();f.checked('node text apply/cold/idempotence uses existing ownedSource receipt; tampered graph hash cannot acknowledge any text')
 for direction,wanted_name,wanted_source,wanted_intent in [('undo',t.original_name,t.original_source,t.original_intent),('redo',t.name,t.text,t.intent)]:
  history=f.invoke('draftHistory',dict(action='inspect'))['result']['result'];assert history[direction]['available'];assert f.invoke('draftHistory',dict(action=direction,token=history[direction]['token']))['result']['result']['accepted'];assert current_is(wanted_name,wanted_source,wanted_intent);x.original()
 f.invoke('saveDraft',{});f.stop();f.start(4);assert current_is(t.name,t.text,t.intent);x.original();f.checked('one node text shared Undo/Redo/cold changes all texts together and preserves IDs/contracts/connections and physical originals')
 history=f.invoke('draftHistory',dict(action='inspect'))['result']['result'];assert f.invoke('draftHistory',dict(action='undo',token=history['undo']['token']))['result']['result']['accepted'];x.original()
 for actions in [('rename','source'),('rename','intent'),('intent','source')]:
  data=t.read();q=dict(action='authorBatch',id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=x.proof(data),edits=[dict(action=a,node=t.node,text={'rename':t.name,'intent':t.intent,'source':t.text}[a])for a in actions]);assert f.invoke('blueprint',q)['result']['result']['checkpointSaved'];now=t.current();assert now['displayName']==(t.name if 'rename'in actions else t.original_name)and now['source']==(t.text if 'source'in actions else t.original_source)and now['intent']==(t.intent if 'intent'in actions else t.original_intent);assert f.invoke('blueprint',{**q,'action':'settledAuthorBatch'})['result']['result']['settled'];x.original();history=f.invoke('draftHistory',dict(action='inspect'))['result']['result'];assert f.invoke('draftHistory',dict(action='undo',token=history['undo']['token']))['result']['result']['accepted'];now=t.current();assert now['displayName']==t.original_name and now['source']==t.original_source and now['intent']==t.original_intent;x.original();f.checked('closed same-node text subset '+','.join(actions)+' preserves all other fields and existing review/history semantics')

finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
print('NODE_TEXT_RECOVERY_API_FIXTURE',f.case,flush=True)
