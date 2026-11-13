"""Whole/native source plans, retained flow and read-only group proof guards."""
import copy,json,subprocess
import v666_retained_body_group_fixture as x
f=x.f
def rpc(action,**kw):return f.invoke('blueprint',dict(action=action,**kw))['result']['result']
def validate(units,ok):
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationBodyGroupGuards',action='validate',project=str(f.manifest),namespace=f.n[:-2],units=units,selected=[x.owner])),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});cp=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));f.invoke('schema',dict(id=x.owner));s=f.state()['schema'];basis=rpc('readOwnerEdits',id=x.owner,hash=s['textHash']);r=x.request();rpc('applySlots',id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=s['textHash'],changes=r['changes']));x.verify(cp);saved=cp.read_bytes();units=copy.deepcopy(r['units'])
 for row in json.loads(saved)['changes']:units[row['id']]=row
 (f.case/'captured-guard-request.json').write_text(json.dumps(dict(operation='informationBodyGroupGuards',action='validate',project=str(f.manifest),namespace=f.n[:-2],units=units,selected=[x.owner]),ensure_ascii=False,indent=2))
 assert validate(units,True)['result']['reads']==[];receipt=units[x.owner]['slotSaveReceipt'];assert len(receipt['nativeBodyContexts'])==2;assert {x.graph_path,x.retained_graph,x.retained_header,x.node_path,x.extra_path}<=set(receipt['readGuards']);f.checked('exact original whole/native source plans and complete owned snapshot remain read checks, never inferred body/graph edits')
 for fault in ['capture','capture-and-reads','missing-plan','wrong-original-hash','wrong-flow-hash','wrong-node','body-text','member','locator','read','extra-read','rebase','wrong-owner','graph','fake-type','missing-group','extra-plan-key','modified-source-and-proof','missing-independent-read','independent-source','alias','outputs','caller-binding']:
  bad=copy.deepcopy(units);v=bad[x.owner]['slotSaveReceipt'];plans=v['nativeBodyContexts']
  if fault.startswith('capture'):
   v.pop('nativeBodyContexts')
   if fault=='capture-and-reads':v['readGuards']={};v['declaration']['changes']=[dict(type='description',text='later')]
  elif fault=='missing-plan':plans.pop()
  elif fault=='wrong-original-hash':plans[0]['hash']='0'*64
  elif fault=='wrong-flow-hash':next(iter(plans[0]['mapping']['bodies'].values()))['whole']['hash']='0'*64
  elif fault=='wrong-node':next(iter(plans[0]['mapping']['bodies'].values()))['whole']['node']='unknown'
  elif fault=='body-text':next(iter(plans[0]['mapping']['bodies'].values()))['text']='return 99;'
  elif fault=='member':v['sources'].pop(x.whole_node)
  elif fault=='locator':bad[x.whole_node]['path']='other.node.json';v['sources'][x.whole_node]['path']='other.node.json'
  elif fault=='read':v['readGuards'].pop(x.graph_path)
  elif fault=='extra-read':v['readGuards']['unobserved.csbody']=dict(path='unobserved.csbody',hash='0'*64)
  elif fault=='rebase':v['readGuards'][x.retained_header]['hash']='0'*64
  elif fault=='wrong-owner':v['owner']=f.n+'Unknown'
  elif fault=='graph':g=json.loads(bad[x.whole_graph]['draft']);g['entry']='missing';bad[x.whole_graph]['draft']=json.dumps(g)
  elif fault=='fake-type':v['nativeTypeProofs']={};v['nativeTypeReads']=[]
  elif fault=='missing-group':bad[x.owner].pop('atomicEditGroup')
  elif fault=='extra-plan-key':plans[0]['unknownSourcePolicy']='implicit'
  elif fault=='missing-independent-read':v['readGuards'].pop(x.extra_path)
  elif fault=='independent-source':
   record=json.loads(bad[x.extra_id]['draft']);record['helpers']='static long Keep(long value){return 99;}';bad[x.extra_id]['draft']=json.dumps(record)
  elif fault=='alias':
   g=json.loads(bad[x.whole_graph]['draft']);g['locals'][0]['source']={'input':'count'};bad[x.whole_graph]['draft']=json.dumps(g)
  elif fault=='outputs':next(iter(plans[0]['mapping']['bodies'].values()))['outputs']={'return':None}
  elif fault=='caller-binding':next(iter(plans[0]['mapping']['callers'].values()))['inputs']['amount']='count'
  elif fault=='modified-source-and-proof':
   record=json.loads(bad[x.whole_node]['draft']);record['source']='return 99;';bad[x.whole_node]['draft']=json.dumps(record);v['sources'][x.whole_node]['hash']=x.hashlib.sha256(bad[x.whole_node]['draft'].encode()).hexdigest()
  # Physical read hashes are verified by Review/final CAS, not the pure shape guard.
  if fault=='rebase':
   assert validate(bad,True)['result']['reads']==[]
  else:validate(bad,False)
  assert cp.read_bytes()==saved;x.unchanged();f.checked(fault+' preserves sources/checkpoint; malformed plan/shape rejects, physical read versions remain final-CAS responsibilities')
 validate(units,True)
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
