"""Return-pin display-order admission cannot change native ABI or other root edits."""
import copy,json,uuid
import v666_root_output_order_recovery_fixture as t
x=t.x;f=x.f
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});original=t.read();before=x.checkpoint()
 def request():return dict(action='authorBatch',id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=original['checkpointHash'],sourceProof=x.proof(original),edits=[dict(action='rootParameters',node='$root',definition=t.plan(t.selected))])
 def plan(q):return q['edits'][0]['definition']
 def rejected(name,mutate):
  q=request();mutate(q);v=f.invoke('blueprint',q,False);assert not v['result']['ok'];assert x.checkpoint()==before and t.current()==t.original_order and t.read()['signature']==original['signature'];x.original();assert t.read()['sources']==original['sources'];f.checked(name)
 rejected('root output order rejects stale checkpoint',lambda q:q.update(checkpointHash='0'*64))
 def tamper(q):
  rows=json.loads(q['sourceProof']);rows[0][2]='0'*64;q['sourceProof']=json.dumps(rows)
 rejected('root output order rejects tampered complete source proof',tamper)
 rejected('root output order requires exact synthetic origin',lambda q:q['edits'][0].update(node='body'))
 rejected('root output order cannot infer owner/slot permission',lambda q:q.update(owner=f.id,ownerHash='0'*64,ownerRevision=0))
 rejected('root output order cannot infer private frame permission',lambda q:q['edits'][0].update(frame=t.graph+'/graph:missing'))
 rejected('root output order cannot publish new outputs',lambda q:plan(q).update(publicOutputs=['left']))
 rejected('root output order cannot rewrite C# body',lambda q:plan(q).update(rootBody=dict(node='body',source='return 41;')))
 rejected('root output order cannot grant root mode changes',lambda q:plan(q).update(inputModes={'left':'ref'}))
 rejected('root output order preserves out argument positions',lambda q:plan(q)['args'].reverse())
 rejected('root output order preserves names',lambda q:plan(q)['args'][0].update(name='renamed'))
 rejected('root output order preserves types',lambda q:plan(q)['args'][0].update(type='long'))
 rejected('root output order preserves out modes',lambda q:plan(q)['args'][0].update(mode='ref'))
 rejected('root output order preserves return type',lambda q:plan(q).update(returnType='void'))
 rejected('root output order requires exact identity remap',lambda q:plan(q)['remap'].update(left='right'))
 rejected('root output order rejects remap extensions',lambda q:plan(q)['remap'].update(missing='left'))
 rejected('root output order rejects duplicate output identity',lambda q:plan(q).update(outputOrder=['left','left','return']))
 rejected('root output order rejects missing identity',lambda q:plan(q)['outputOrder'].pop())
 rejected('root output order rejects unknown identity',lambda q:plan(q).update(outputOrder=['left','missing','return']))
 rejected('root output order moves return only, not relative out positions',lambda q:plan(q).update(outputOrder=['right','return','left']))
 rejected('root output order requires string identities',lambda q:plan(q).update(outputOrder=['left',37,'return']))
 rejected('root output order rejects source mixing',lambda q:q['edits'].append(dict(action='source',node='body',text=t.original_source)))
 rejected('root output order rejects another contract edit',lambda q:q['edits'].append(copy.deepcopy(q['edits'][0])))
 q=request();result=f.invoke('blueprint',q)['result']['result'];assert result['checkpointSaved']and result['sourceWritten']is False;assert t.current()==t.selected and t.read()['signature']==original['signature'];x.original();saved=x.checkpoint();assert f.invoke('blueprint',q)['result']['result']['checkpointSaved']and x.checkpoint()==saved;assert f.invoke('draftHistory',{'action':'inspect'})['result']['result']['undo']['available'];f.stop();f.start(1);assert x.checkpoint()==saved and t.current()==t.selected;x.original();query={**q,'action':'settledAuthorBatch'};assert f.invoke('blueprint',query)['result']['result']['settled'];checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));raw=checkpoint.read_bytes();doc=json.loads(raw);g=next(u for u in doc['changes']if u['id']==t.graph);assert g['authorSaveReceipt']['ownedRootOutputOrder']is True;assert set(g['rootContractGroup'])=={t.feature,t.n+'PairBody',t.graph} and set(g['rootContractGroup'])<={u['id']for u in doc['changes']};g['authorSaveReceipt']['sources'][t.graph]['hash']='0'*64;checkpoint.write_text(json.dumps(doc));f.stop();f.start(2);assert not f.invoke('blueprint',query)['result']['result']['settled'];x.original();f.stop();checkpoint.write_bytes(raw);f.start(3);assert f.invoke('blueprint',query)['result']['result']['settled'];x.original();f.checked('root return display-order Save is durable/idempotent with full root group/shared history/cold receipt; out ABI and all physical files stay unchanged before Confirm')
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
print('ROOT_OUTPUT_ORDER_RECOVERY_API_FIXTURE',f.case,flush=True)
