"""Independent private/out-to-value plans and exact new value/output evidence."""
import copy,json
import v666_private_callee_out_value_fixture as x
f=x.f
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));x.execute(40,'original-private-out-value')
 for row in r['changes']:one=copy.deepcopy(r);one['changes']=[row];x.prepare(one)
 x.unchanged();f.checked('original40 via a real out consumer; independent private/helper and out-value plans validate with explicit literal and lost-out-to-return correspondence')
 if x.mode=='reproduce':
  result=x.prepare(r,False);(f.case/'group-rejection.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));x.unchanged();f.checked('published package rejects the combined private/out-value candidate without original writes')
 else:
  result=x.prepare(r)['result'];(f.case/'candidate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));rows=result['updates']+result['linkedUpdates'];x.verify_rows({v['id']:dict(draft=v['text'])for v in rows});reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.prepare(reverse)['result'];assert{v['id']:v['text']for v in rows}=={v['id']:v['text']for v in other['updates']+other['linkedUpdates']};x.unchanged();f.checked('order-independent candidate retains original private/native ABI and explicitly creates one value input/remaps the old out consumer')
  for fault in ['missing-caller','missing-private-caller','missing-shared-caller','missing-value','used-binding','wrong-value','missing-out-map','out-identity','disconnect','drop-return','native-alias','private-role','bad-code','ref-role','second-role','return-type']:
   bad=copy.deepcopy(r);a,b=bad['changes'];plan=next(iter(b['mapping']['bodies'].values()));caller=next(iter(b['mapping']['callers'].values()))
   if fault=='missing-caller':b['mapping'].pop('callers')
   elif fault in ['missing-private-caller','missing-shared-caller']:
    plans=b['mapping']['callers'];keys=[key for key,value in plans.items()if(value['graph']==x.whole_graph)==(fault=='missing-private-caller')];assert len(keys)==1;plans.pop(keys[0])
   elif fault=='missing-value':caller['inputs'].pop('count')
   elif fault=='used-binding':caller['inputs']['count']='amount'
   elif fault=='wrong-value':caller['inputs']['count']={'valueJson':'"wrong type"'}
   elif fault=='missing-out-map':caller['outputs'].pop('count')
   elif fault=='out-identity':caller['outputs']['count']='count'
   elif fault=='disconnect':caller['disconnect']={'amount':'null'}
   elif fault=='drop-return':caller['outputs']['return']=None
   elif fault=='native-alias':plan['signature']['args'][1]['name']='inferredCount'
   elif fault=='private-role':next(iter(a['mapping']['bodies'].values()))['signature']['args'][1]['mode']='out'
   elif fault=='bad-code':plan['text']='return MissingRoleValue;'
   elif fault=='ref-role':b['signature']['args'][1]['mode']='ref';plan['signature']['args'][1]['mode']='ref';plan['contract']=copy.deepcopy(b['signature'])
   elif fault=='second-role':b['signature']['args'][0]['mode']='out';plan['signature']['args'][0]['mode']='out';plan['contract']=copy.deepcopy(b['signature'])
   elif fault=='return-type':b['signature']['return']='double';plan['signature']['return']='double';plan['contract']=copy.deepcopy(b['signature'])
   x.prepare(bad,False);x.unchanged();f.checked(fault+' refuses incomplete explicit role/caller evidence or a different ABI without original writes')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
