"""Pure distinct ordinary next routes share final CAS and never grant source/contract/ownership edits."""
import copy,json,uuid
import v666_route_group_recovery_fixture as t
x=t.x;f=t.f
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});original=t.read();before=x.checkpoint()
 def request():return dict(action='authorBatch',id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=original['checkpointHash'],sourceProof=x.proof(original),edits=t.edits(t.selected))
 def rejected(name,mutate):
  q=request();mutate(q);reply=f.invoke('blueprint',q,False);assert not reply['result']['ok'],reply;now=t.read();assert x.checkpoint()==before and t.current()==t.original and now['sources']==original['sources'];x.original();f.checked(name)
 rejected('group rejects stale checkpoint',lambda q:q.update(checkpointHash='0'*64))
 def tamper(q):
  rows=json.loads(q['sourceProof']);rows[0][2]='0'*64;q['sourceProof']=json.dumps(rows)
 rejected('group rejects tampered full source proof',tamper)
 rejected('group cannot infer owner/slot permission',lambda q:q.update(owner=f.id,ownerHash='0'*64,ownerRevision=0))
 rejected('group cannot infer private-frame permission',lambda q:q['edits'][0].update(frame=t.graph+'/graph:missing'))
 rejected('group requires distinct explicitly selected sources',lambda q:q['edits'].append(copy.deepcopy(q['edits'][0])))
 rejected('group cannot infer absent destination',lambda q:q['edits'][0].update(to='missing'))
 rejected('group cannot infer absent source',lambda q:q['edits'][0].update(node='missing'))
 rejected('group cannot route root entry implicitly',lambda q:q['edits'][0].update(node='$entry',action='entry'))
 rejected('group cannot route branch/completion ports',lambda q:q['edits'][0].update(port='complete'))
 rejected('group rejects extra route fields',lambda q:q['edits'][0].update(text='extra'))
 rejected('group requires string destination',lambda q:q['edits'][0].update(to=17))
 rejected('group cannot mix original C# edits',lambda q:q['edits'].append(dict(action='source',node='body',text='return 41;')))
 rejected('group cannot mix display-name edits',lambda q:q['edits'].append(dict(action='rename',node='body',text='새 이름')))
 rejected('group cannot mix contract changes',lambda q:q['edits'].append(dict(action='parameters',node='body',definition={})))
 rejected('group cannot mix node creation',lambda q:q['edits'].append(dict(action='createNode',node='new',definition={})))
 rejected('group refuses cyclic final graph',lambda q:q['edits'][0].update(to='body'))
 rejected('group refuses self route',lambda q:q['edits'][0].update(to='first'))
 rejected('group retains existing 64-edit budget',lambda q:q['edits'].extend(copy.deepcopy(q['edits'][0])for _ in range(62)))
 q=request();checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));checkpoint.chmod(0o400)
 try:assert not f.invoke('blueprint',q,False)['result']['ok'];assert x.checkpoint()==before and t.current()==t.original;x.original()
 finally:checkpoint.chmod(0o600)
 query={**q,'action':'settledAuthorBatch'};observed=f.invoke('blueprint',query)['result']['result'];assert observed['settled']is False and observed['baselineUnchanged']is True
 assert not f.invoke('blueprint',{**query,'checkpointHash':'0'*64})['result']['result'].get('baselineUnchanged');bad=copy.deepcopy(query);tamper(bad);assert not f.invoke('blueprint',bad)['result']['result'].get('baselineUnchanged')
 p=f.project/t.graph_file;physical=p.read_bytes();p.write_bytes(physical+b' ')
 try:assert not f.invoke('blueprint',query)['result']['result'].get('baselineUnchanged')
 finally:p.write_bytes(physical)
 assert x.checkpoint()==before and t.current()==t.original;x.original();f.checked('failed group keeps live/checkpoint/all C# unchanged; replacement needs exact original checkpoint/full proof/physical sources')
 q=request();reply=f.invoke('blueprint',q)['result']['result'];assert reply['checkpointSaved']and reply['sourceWritten']is False;assert t.current()==t.selected;x.original();saved=x.checkpoint();assert f.invoke('blueprint',q)['result']['result']['checkpointSaved']and x.checkpoint()==saved;assert f.invoke('draftHistory',{'action':'inspect'})['result']['result']['undo']['available'];f.stop();f.start(1);assert x.checkpoint()==saved and t.current()==t.selected;x.original();query={**q,'action':'settledAuthorBatch'};assert f.invoke('blueprint',query)['result']['result']['settled'];checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));raw=checkpoint.read_bytes();doc=json.loads(raw);g=next(row for row in doc['changes']if row['id']==t.graph);assert g['authorSaveReceipt']['ownedRoute']is True;g['authorSaveReceipt']['sources'][t.graph]['hash']='0'*64;checkpoint.write_text(json.dumps(doc));f.stop();f.start(2);assert not f.invoke('blueprint',query)['result']['result']['settled'];x.original();f.stop();checkpoint.write_bytes(raw);f.start(3);assert f.invoke('blueprint',query)['result']['result']['settled'];x.original();f.checked('three next routes commit once/idempotently and share history/cold receipt; tampered receipt cannot settle, all physical sources fixed until Confirm')
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
print('ROUTE_GROUP_RECOVERY_API_FIXTURE',f.case,flush=True)
