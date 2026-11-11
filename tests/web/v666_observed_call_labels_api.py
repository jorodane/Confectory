"""Observed slot identity, source footprint and exact existing frame contract."""
import json,sys
import v666_observed_call_labels_fixture as t
x=t.x;f=t.f
try:
 f.start(0);f.invoke('select',dict(id=t.owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();a=t.read();b=t.read();row=next(r for r in a['nodes']if r['id']==t.node);assert a['slotContext']['owner']==t.owner and a['slotContext']['implementation']==f.n+'MainBody';assert a['signature']==b['signature']and row['signature']['args'][0]['name']==t.parameter and row['arguments']==next(r for r in b['nodes']if r['id']==t.node)['arguments'];assert sorted(s['id']for s in a['sources'])==sorted(s['id']for s in b['sources']);assert checkpoint.read_bytes()==before;x.original()
 if sys.argv[3]=='baseline':assert 'pinPresentation'not in row
 else:assert row['pinPresentation']['status']=='available'and row['pinPresentation']['argumentNames']=={t.parameter:t.input_label}and row['pinPresentation']['returnName']==t.return_label
 f.checked('existing observed slot/private proof and repeated reads preserve owner binding, source footprint, native contract/arguments, checkpoint and original source')
 info=f.invoke('schema',dict(id=t.owner))['state']['schema'];f.invoke('blueprint',dict(action='read',id=t.graph,owner=t.owner,ownerHash='0'*64,ownerRevision=info['revision']),False);assert checkpoint.read_bytes()==before;x.original();f.checked('tampered owner observation remains rejected before slot rendering or writes')
 if sys.argv[3]!='baseline':x.build('observed-slot-original-execution',10,'body');x.original();f.checked('original saved private call also executes result10 with no owner, C# or graph writes')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));f.stop()
