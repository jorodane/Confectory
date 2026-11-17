"""Original return/out consumers and independent private/native source plans."""
import copy,json
import v666_private_root_import_fixture as x
f=x.f
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));x.execute(40,'original-private-scalar-return')
 for row in r['changes']:one=copy.deepcopy(r);one['changes']=[row];x.prepare(one)
 x.unchanged();f.checked('original40 through a real return consumer; independent private/helper and scalar-return plans validate with an explicit compatible original out choice')
 if x.mode=='reproduce':
  result=x.prepare(r,False);(f.case/'group-rejection.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));x.unchanged();f.checked('published package rejects the combined private/scalar-return candidate without original writes')
 else:
  result=x.prepare(r)['result'];(f.case/'candidate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));rows=result['updates']+result['linkedUpdates'];x.verify_rows({v['id']:dict(draft=v['text'])for v in rows});reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.prepare(reverse)['result'];assert{v['id']:v['text']for v in rows}=={v['id']:v['text']for v in other['updates']+other['linkedUpdates']};x.unchanged();f.checked('order-independent candidate retains private/native input/out ABI and explicitly redirects the old return consumer to a compatible original out')
  for fault in ['missing-caller','input-literal','disconnect','missing-return','return-identity','wrong-out','missing-out','nonexistent-output','native-alias','native-role','private-return','bad-code','second-contract','no-type-change','void-return']:
   bad=copy.deepcopy(r);a,b=bad['changes'];plan=next(iter(b['mapping']['bodies'].values()));caller=next(iter(b['mapping']['callers'].values()))
   if fault=='missing-caller':b['mapping'].pop('callers')
   elif fault=='input-literal':caller['inputs']['amount']={'valueJson':'5'}
   elif fault=='disconnect':caller['disconnect']={'amount':'null'}
   elif fault=='missing-return':caller['outputs'].pop('return')
   elif fault=='return-identity':caller['outputs']['return']='return'
   elif fault=='wrong-out':caller['outputs']['count']='return'
   elif fault=='missing-out':caller['outputs'].pop('count')
   elif fault=='nonexistent-output':caller['outputs']['return']='inferredOutput'
   elif fault=='native-alias':plan['signature']['args'][0]['name']='inferredAmount'
   elif fault=='native-role':plan['signature']['args'][1].pop('mode')
   elif fault=='private-return':next(iter(a['mapping']['bodies'].values()))['signature']['return']='double'
   elif fault=='bad-code':plan['text']='count=0;return MissingScalarReturn;'
   elif fault=='second-contract':a['signature']['return']='double'
   elif fault=='no-type-change':b['signature']['return']='long';plan['signature']['return']='long';plan['contract']=copy.deepcopy(b['signature'])
   elif fault=='void-return':b['signature']['return']='void';plan['signature']['return']='void';plan['contract']=copy.deepcopy(b['signature']);plan['text']='count=5;return;'
   x.prepare(bad,False);x.unchanged();f.checked(fault+' rejects incomplete output/source evidence or a different contract without original writes')
  for fault in ['missing-helper','foreign-import','selected-callee','stale-import','helper-parent','import-alias']:
   bad=copy.deepcopy(r);key=x.functions[1]+'Body';text=bad['units'][key]['draft']
   if fault=='missing-helper':bad['units'].pop(x.helper)
   elif fault=='foreign-import':bad['units'][key]['draft']=text.replace(x.helper,'External.Unknown::Helper')
   elif fault=='selected-callee':bad['units'][key]['draft']=text.replace(x.helper,x.functions[0])
   elif fault=='stale-import':bad['units'][key]['draft']=text.replace('StableHelper (long) -> long','StableHelper (string) -> long')
   elif fault=='helper-parent':bad['units'][x.helper]['draft']=bad['units'][x.helper]['draft'].replace('-> long {','-> long extends '+x.functions[0]+' {')
   elif fault=='import-alias':bad['units'][key]['draft']=text.replace('as StableHelper','as UnselectedAlias')
   x.prepare(bad,False);x.unchanged();f.checked(fault+' rejects an uncaptured, selected or stale helper import without original writes')
  for fault in ['root-import-alias','root-import-stale','root-import-selected','root-missing-call','root-call-signature','root-call-context']:
   bad=copy.deepcopy(r);header=bad['units'][x.whole_implementation];flow=bad['units'][x.whole_graph]
   if fault=='root-import-alias':header['draft']=header['draft'].replace(x.root_alias,'UnselectedRootAlias')
   elif fault=='root-import-stale':header['draft']=header['draft'].replace('(long) -> long','(string) -> long')
   elif fault=='root-import-selected':header['draft']=header['draft'].replace(x.helper,x.functions[1])
   else:
    graph=json.loads(flow['draft']);node=next(n for n in graph['nodes']if n['id']==x.root_call)
    if fault=='root-missing-call':graph['nodes'].remove(node);graph['edges']=[e for e in graph['edges']if e['from']!=x.root_call];next(e for e in graph['edges']if e['from']=='inner')['to']='exit:return';graph['exits']={'return':{'node':'inner'}}
    elif fault=='root-call-signature':node['signature']['args'][0]['type']='string'
    elif fault=='root-call-context':node['forwardCallerStorage']=True
    flow['draft']=json.dumps(graph,ensure_ascii=False,indent=2)+'\r\n'
   x.prepare(bad,False);x.unchanged();f.checked(fault+' rejects a missing, changed or nonordinary private implementation import/call without original writes')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
