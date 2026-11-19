"""Original source scope, explicit choices and direct ownership stay mandatory."""
import copy,json
import v666_retained_caller_contract_fixture as x
f=x.f
try:
 r=x.request();x.prepare(r);x.unchanged()
 for fault in ['stale-function','wrong-before','invalid-map','missing-source-text','stale-source','native-alias','invalid-last-source','foreign-function','foreign-source','unselected-caller-source','copy-context','opaque-context']:
  bad=copy.deepcopy(r);caller,callee=bad['changes'];key=x.callee+'Body/body:common';plan=callee['mapping']['bodies'][key]
  if fault=='stale-function':caller['hash']='0'*64
  elif fault=='wrong-before':caller['mapping']['before']['args'][0]['name']='notOriginal'
  elif fault=='invalid-map':caller['mapping']['args']['amount']='notSelected'
  elif fault=='missing-source-text':plan.pop('text')
  elif fault=='stale-source':plan['hash']='0'*64
  elif fault=='native-alias':plan['signature']['args'][0]['name']='inferredAlias'
  elif fault=='invalid-last-source':plan['text']='return MissingSource;'
  elif fault=='foreign-function':caller['id']='Other.Pack::Function'
  elif fault=='foreign-source':callee['mapping']['bodies']['Other.Pack::Body/body:common']=callee['mapping']['bodies'].pop(key)
  elif fault=='unselected-caller-source':caller['mapping'].setdefault('bodies',{})[x.code_id]=copy.deepcopy(plan)
  else:
   unit=bad['units'][x.caller_graph];graph=json.loads(unit['draft'])
   if fault=='copy-context':graph['copySource']={'owner':'Other.Pack::Original'}
   else:graph['nodes'][0]['implementationContext']={'feature':x.caller_function}
   unit['draft']=json.dumps(graph)
  reply=x.prepare(bad,False);x.unchanged();(f.case/(fault+'.json')).write_text(json.dumps(reply,ensure_ascii=False,indent=2));f.checked(fault+' refuses the whole candidate without modifying any original source')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
