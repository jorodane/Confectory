"""One explicit existing-node name/source pair: atomicity, ownership and recovery."""
import copy,json,uuid
import v666_text_pair_recovery_fixture as t
x=t.x;f=t.f
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});original=t.read();before=t.checkpoint().read_bytes()
 def request():return dict(action='authorBatch',id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=original['checkpointHash'],sourceProof=x.proof(original),edits=[dict(action='rename',node=t.node,text=t.name),dict(action='source',node=t.node,text=t.text)])
 def unchanged():assert t.checkpoint().read_bytes()==before and t.current()['displayName']==t.original_name and t.current()['source']==t.original_source;x.original()
 def rejected(name,mutate):
  q=request();mutate(q);reply=f.invoke('blueprint',q,False);assert not reply['result']['ok'];unchanged();f.checked(name)
 rejected('paired text rejects stale checkpoint',lambda q:q.update(checkpointHash='0'*64))
 def tamper(q):
  p=json.loads(q['sourceProof']);p[0][2]='0'*64;q['sourceProof']=json.dumps(p)
 rejected('paired text rejects tampered full closure',tamper)
 rejected('paired text cannot edit two different nodes',lambda q:q['edits'][1].update(node='missing'))
 rejected('paired text cannot infer owner/slot authority',lambda q:q.update(owner=f.id,ownerHash='0'*64,ownerRevision=0))
 rejected('paired text cannot infer private frame authority',lambda q:q['edits'][1].update(frame=t.graph+'/graph:missing'))
 rejected('paired text cannot grant parameter changes',lambda q:q['edits'].append(dict(action='parameters',node=t.node,definition={})))
 rejected('paired text cannot grant mixed routes',lambda q:q['edits'].append(dict(action='route',node=t.node,port='next',to='exit:return')))
 rejected('paired text cannot grant unrelated argument mixing',lambda q:q['edits'].append(dict(action='argument',node=t.node,name='amount',valueJson='8')))
 rejected('paired text rejects blank display name',lambda q:q['edits'][0].update(text=' '))
 rejected('paired text rejects control characters in display name',lambda q:q['edits'][0].update(text='name\ninvalid'))
 rejected('paired text rejects over-budget display name',lambda q:q['edits'][0].update(text='a'*257))
 q=request();p=t.checkpoint();p.chmod(0o400)
 try:reply=f.invoke('blueprint',q,False);assert not reply['result']['ok'];unchanged()
 finally:p.chmod(0o600)
 query={**q,'action':'settledAuthorBatch'};observed=f.invoke('blueprint',query)['result']['result'];assert observed['settled']is False and observed['baselineUnchanged']is True
 bad={**query,'checkpointHash':'0'*64};assert not f.invoke('blueprint',bad)['result']['result'].get('baselineUnchanged');bad=copy.deepcopy(query);tamper(bad);assert not f.invoke('blueprint',bad)['result']['result'].get('baselineUnchanged')
 source=f.project/t.source_file;raw=source.read_bytes();source.write_bytes(raw+b' ')
 try:assert not f.invoke('blueprint',query)['result']['result'].get('baselineUnchanged')
 finally:source.write_bytes(raw)
 unchanged();f.checked('paired failure preserves live/checkpoint/originals; only exact unapplied checkpoint/closure/physical originals permit correction')
 reply=f.invoke('blueprint',q)['result']['result'];assert reply['checkpointSaved']and reply['sourceWritten']is False;assert t.current()['displayName']==t.name and t.current()['source']==t.text;x.original();saved=p.read_bytes();assert f.invoke('blueprint',q)['result']['result']['checkpointSaved']and p.read_bytes()==saved
 f.stop();f.start(1);assert p.read_bytes()==saved and f.invoke('blueprint',query)['result']['result']['settled'];assert t.current()['displayName']==t.name and t.current()['source']==t.text;x.original();doc=json.loads(saved);receipt=next(u for u in doc['changes']if u['id']==t.graph)['authorSaveReceipt'];assert receipt['ownedSource']is True
 graph=next(u for u in doc['changes']if u['id']==t.graph);graph['authorSaveReceipt']['sources'][t.graph]['hash']='0'*64;p.write_text(json.dumps(doc));f.stop();f.start(2);assert not f.invoke('blueprint',query)['result']['result']['settled'];f.stop();p.write_bytes(saved);f.start(3);assert f.invoke('blueprint',query)['result']['result']['settled'];x.original();f.checked('paired apply/cold/idempotence uses existing ownedSource receipt; tampered graph hash cannot acknowledge either text')
 for direction,wanted_name,wanted_source in [('undo',t.original_name,t.original_source),('redo',t.name,t.text)]:
  history=f.invoke('draftHistory',dict(action='inspect'))['result']['result'];assert history[direction]['available'];assert f.invoke('draftHistory',dict(action=direction,token=history[direction]['token']))['result']['result']['accepted'];assert t.current()['displayName']==wanted_name and t.current()['source']==wanted_source;x.original()
 f.invoke('saveDraft',{});f.stop();f.start(4);assert t.current()['displayName']==t.name and t.current()['source']==t.text;x.original();f.checked('one paired shared Undo/Redo/cold changes both texts together and preserves IDs/contracts/connections and physical originals')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
print('TEXT_PAIR_RECOVERY_API_FIXTURE',f.case,flush=True)
