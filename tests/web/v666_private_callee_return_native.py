"""Original return/out consumers and independent private/native source plans."""
import copy,json
import v666_private_callee_return_fixture as x
f=x.f
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));x.execute(45,'original-private-scalar-return')
 for row in r['changes']:one=copy.deepcopy(r);one['changes']=[row];x.prepare(one)
 x.unchanged();f.checked('original45 through both original private and shared return consumers; independent private/helper and scalar-return plans validate with an explicit compatible original out choice')
 if x.mode=='reproduce':
  result=x.prepare(r,False);(f.case/'group-rejection.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));x.unchanged();f.checked('published package rejects the combined private/scalar-return candidate without original writes')
 else:
  result=x.prepare(r)['result'];(f.case/'candidate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));rows=result['updates']+result['linkedUpdates'];x.verify_rows({v['id']:dict(draft=v['text'])for v in rows});reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.prepare(reverse)['result'];assert{v['id']:v['text']for v in rows}=={v['id']:v['text']for v in other['updates']+other['linkedUpdates']};x.unchanged();f.checked('order-independent candidate retains private/native input/out ABI and explicitly redirects the old return consumer to a compatible original out')
  for fault in ['missing-caller','missing-private-caller','missing-shared-caller','input-literal','disconnect','missing-return','return-identity','wrong-out','missing-out','nonexistent-output','native-alias','native-role','private-return','bad-code','second-contract','no-type-change','void-return']:
   bad=copy.deepcopy(r);a,b=bad['changes'];plan=next(iter(b['mapping']['bodies'].values()));caller=next(iter(b['mapping']['callers'].values()))
   if fault=='missing-caller':b['mapping'].pop('callers')
   elif fault in ['missing-private-caller','missing-shared-caller']:
    plans=b['mapping']['callers'];keys=[key for key,value in plans.items()if(value['graph']==x.whole_graph)==(fault=='missing-private-caller')];assert len(keys)==1;plans.pop(keys[0])
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
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
