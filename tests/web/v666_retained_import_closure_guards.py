"""Explicit source, original context and caller evidence stay mandatory."""
import copy,json
import v666_retained_import_closure_fixture as x
f=x.f
try:
 r=x.request();x.prepare(r);x.unchanged()
 metadata=copy.deepcopy(r);metadata['changes'][1]['mapping']['bodies']={};result=x.prepare(metadata)['result'];rows={v['id']:v['text']for v in result['updates']+result['linkedUpdates']};assert rows.get(x.peer+'Body/body:common',x.snapshot[x.paths[x.peer]].decode())==x.snapshot[x.paths[x.peer]].decode();x.unchanged();f.checked('a peer metadata-only choice remains valid and does not infer its unselected CSharp edit')
 for fault in ['missing-caller-source','missing-native-source','incomplete-peer-source','stale-source','stale-context','caller-native-alias','caller-return','caller-helper','foreign-source','copy-context','changed-context-import','missing-disconnect','wrong-disconnect','retained-out-input','inferred-out-consumer','removed-return','unchanged-caller-text','unassigned-out','invalid-last-source','duplicate-caller-context']:
  bad=copy.deepcopy(r);first,peer=bad['changes'];plan=first['mapping']['bodies'][x.opaque_node];own=first['mapping']['bodies'][x.callee+'Body/body:common'];caller=next(iter(first['mapping']['callers'].values()))
  if fault=='missing-caller-source':first['mapping']['bodies'].pop(x.opaque_node)
  elif fault=='missing-native-source':first['mapping']['bodies'].pop(x.callee+'Body/body:common')
  elif fault=='incomplete-peer-source':next(iter(peer['mapping']['bodies'].values())).pop('text')
  elif fault=='stale-source':plan['hash']='0'*64
  elif fault=='stale-context':plan['whole']['hash']='0'*64
  elif fault=='caller-native-alias':plan['signature']['args'][0]['name']='inferredName'
  elif fault=='caller-return':plan['signature']['return']='double'
  elif fault=='caller-helper':plan['helpers']='static long Inferred(){return 0;}'
  elif fault=='foreign-source':first['mapping']['bodies']['Other.Pack::Caller/body:common/node:body']=first['mapping']['bodies'].pop(x.opaque_node)
  elif fault in ['copy-context','changed-context-import']:
   unit=bad['units'][x.opaque_graph_id];graph=json.loads(unit['draft'])
   if fault=='copy-context':graph['copySource']={'owner':'Other.Pack::Original'}
   else:next(v for v in graph['nodes']if v.get('implementationContext'))['implementationContext']['imports']['Selected']['feature']=x.peer
   unit['draft']=json.dumps(graph);plan['whole']['hash']=x.hashlib.sha256(unit['draft'].encode()).hexdigest()
  elif fault=='missing-disconnect':caller['disconnect']={}
  elif fault=='wrong-disconnect':caller['disconnect']['count']='null'
  elif fault=='retained-out-input':caller['inputs']['count']='count'
  elif fault=='inferred-out-consumer':caller['outputs']['count']='count'
  elif fault=='removed-return':caller['outputs']['return']=None
  elif fault=='unchanged-caller-text':plan['text']=x.opaque_source
  elif fault=='unassigned-out':own['text']=x.sources[x.callee]
  elif fault=='invalid-last-source':next(iter(peer['mapping']['bodies'].values()))['text']='return MissingPeerSource;'
  elif fault=='duplicate-caller-context':peer['mapping']['bodies'][x.opaque_node]=copy.deepcopy(plan);peer['mapping']['bodies'][x.opaque_node]['contract']=copy.deepcopy(x.nexts[1])
  reply=x.prepare(bad,False);x.unchanged();(f.case/(fault+'.json')).write_text(json.dumps(reply,ensure_ascii=False,indent=2));f.checked(fault+' rejects the entire candidate without changing original source, ABI or connections')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
