"""An explicit single root identifier remap never grants another ABI or source edit."""
import copy,json,uuid
import v666_root_input_name_recovery_fixture as t
x=t.x;f=x.f
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});original=t.read();before=x.checkpoint()
 def request():return dict(action='authorBatch',id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=original['checkpointHash'],sourceProof=x.proof(original),edits=[dict(action='rootParameters',node='$root',definition=t.plan(t.selected))])
 def plan(q):return q['edits'][0]['definition']
 def named(q,value):plan(q)['args'][0]['name']=value;plan(q)['remap'][t.original_name]=value
 def rejected(name,mutate):
  q=request();mutate(q);v=f.invoke('blueprint',q,False);assert not v['result']['ok'];assert x.checkpoint()==before and t.current()==t.original_name and t.read()['signature']==original['signature'];x.original();assert t.read()['sources']==original['sources'];f.checked(name)
 rejected('root identifier rejects stale checkpoint',lambda q:q.update(checkpointHash='0'*64))
 def tamper(q):
  rows=json.loads(q['sourceProof']);rows[0][2]='0'*64;q['sourceProof']=json.dumps(rows)
 rejected('root identifier rejects tampered complete source proof',tamper)
 rejected('root identifier requires exact synthetic origin',lambda q:q['edits'][0].update(node='body'))
 rejected('root identifier cannot infer owner/slot permission',lambda q:q.update(owner=f.id,ownerHash='0'*64,ownerRevision=0))
 rejected('root identifier cannot infer private frame permission',lambda q:q['edits'][0].update(frame=t.graph+'/graph:missing'))
 rejected('root identifier cannot publish new outputs',lambda q:plan(q).update(publicOutputs=['return']))
 rejected('root identifier cannot rewrite C# body',lambda q:plan(q).update(rootBody=dict(node='body',source='return 41;')))
 rejected('root identifier cannot change value/ref modes',lambda q:plan(q).update(inputModes={t.original_name:'ref'}))
 rejected('root identifier cannot add arguments',lambda q:plan(q)['args'].append(dict(name='extra',type='int')))
 rejected('root identifier cannot remove arguments',lambda q:plan(q)['args'].clear())
 rejected('root identifier preserves input type',lambda q:plan(q)['args'][0].update(type='long'))
 rejected('root identifier cannot turn input into out',lambda q:plan(q)['args'][0].update(mode='out'))
 rejected('root identifier cannot turn input into ref',lambda q:plan(q)['args'][0].update(mode='ref'))
 rejected('root identifier rejects extra argument fields',lambda q:plan(q)['args'][0].update(extra='missing'))
 rejected('root identifier preserves return type',lambda q:plan(q).update(returnType='void'))
 rejected('root identifier preserves output identities',lambda q:plan(q).update(outputOrder=['missing']))
 rejected('root identifier preserves output arity',lambda q:plan(q)['outputOrder'].append('return'))
 rejected('root identifier requires complete original remap',lambda q:plan(q).update(remap={'missing':t.selected}))
 rejected('root identifier requires exact selected remap',lambda q:plan(q)['remap'].update({t.original_name:'missing'}))
 rejected('root identifier rejects remap extensions',lambda q:plan(q)['remap'].update(missing=t.selected))
 rejected('root identifier rejects whitespace names',lambda q:named(q,'not valid'))
 rejected('root identifier rejects empty names',lambda q:named(q,''))
 rejected('root identifier rejects nonstring names',lambda q:named(q,37))
 rejected('root identifier rejects over-budget names',lambda q:named(q,'a'*61))
 rejected('root identifier rejects source mixing',lambda q:q['edits'].append(dict(action='source',node='body',text=t.original_source)))
 rejected('root identifier rejects another contract edit',lambda q:q['edits'].append(copy.deepcopy(q['edits'][0])))
 q=request();result=f.invoke('blueprint',q)['result']['result'];assert result['checkpointSaved']and result['sourceWritten']is False;assert t.current()==t.selected;sig=copy.deepcopy(original['signature']);sig['args'][0]['name']=t.selected;assert t.read()['signature']==sig;x.original();saved=x.checkpoint();assert f.invoke('blueprint',q)['result']['result']['checkpointSaved']and x.checkpoint()==saved;assert f.invoke('draftHistory',{'action':'inspect'})['result']['result']['undo']['available'];f.stop();f.start(1);assert x.checkpoint()==saved and t.current()==t.selected;x.original();query={**q,'action':'settledAuthorBatch'};assert f.invoke('blueprint',query)['result']['result']['settled'];checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));raw=checkpoint.read_bytes();doc=json.loads(raw);g=next(u for u in doc['changes']if u['id']==t.graph);assert g['authorSaveReceipt']['ownedRootInputName']is True;assert set(g['rootContractGroup'])=={t.feature,t.n+'PairBody',t.graph} and set(g['rootContractGroup'])<={u['id']for u in doc['changes']};g['authorSaveReceipt']['sources'][t.graph]['hash']='0'*64;checkpoint.write_text(json.dumps(doc));f.stop();f.start(2);assert not f.invoke('blueprint',query)['result']['result']['settled'];x.original();f.stop();checkpoint.write_bytes(raw);f.start(3);assert f.invoke('blueprint',query)['result']['result']['settled'];x.original();f.checked('single root identifier Save is durable/idempotent with complete root group/shared history/cold receipt; positional ABI and all physical C# sources stay unchanged before Confirm')
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
print('ROOT_INPUT_NAME_RECOVERY_API_FIXTURE',f.case,flush=True)
