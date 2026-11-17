"""Original caller ref storage survives one explicit selected callee ref-to-out plan."""
import copy,json
import v666_private_callee_ref_out_fixture as x
f=x.f
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));x.execute(115,'original-private-ref-out')
 for row in r['changes']:one=copy.deepcopy(r);one['changes']=[row];x.prepare(one)
 x.unchanged();f.checked('original115 and ref40 execute; both original single plans validate independently')
 if x.mode=='reproduce':
  result=x.prepare(r,False);(f.case/'group-rejection.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));x.unchanged();f.checked('published package rejects combined private/callee ref-out without original writes')
 else:
  result=x.prepare(r)['result'];rows=result['updates']+result['linkedUpdates'];x.verify_rows({v['id']:dict(draft=v['text'])for v in rows});reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.prepare(reverse)['result'];assert{v['id']:v['text']for v in rows}=={v['id']:v['text']for v in other['updates']+other['linkedUpdates']};x.unchanged();f.checked('order-independent ref-out candidate preserves original caller ref storage and explicit private sources')
  for fault in ['missing-callers','missing-private-caller','missing-shared-caller','missing-disconnect','wrong-disconnect','old-ref-input','drop-return','extra-output','native-alias','private-role','bad-code','unassigned-out','second-role','return-type']:
   bad=copy.deepcopy(r);a,b=bad['changes'];plan=next(iter(b['mapping']['bodies'].values()));caller=next(iter(b['mapping']['callers'].values()))
   if fault=='missing-callers':b['mapping'].pop('callers')
   elif fault in ['missing-private-caller','missing-shared-caller']:
    plans=b['mapping']['callers'];keys=[key for key,value in plans.items()if(value['graph']==x.whole_graph)==(fault=='missing-private-caller')];assert len(keys)==1;plans.pop(keys[0])
   elif fault=='missing-disconnect':caller['disconnect'].pop('count')
   elif fault=='wrong-disconnect':caller['disconnect']['count']='null'
   elif fault=='old-ref-input':caller['inputs']['count']='count'
   elif fault=='drop-return':caller['outputs']['return']=None
   elif fault=='extra-output':caller['outputs']['count']='return'
   elif fault=='native-alias':plan['signature']['args'][1]['name']='inferredCount'
   elif fault=='private-role':next(iter(a['mapping']['bodies'].values()))['signature']['args'][1]['mode']='out'
   elif fault=='bad-code':plan['text']='return MissingRoleValue;'
   elif fault=='unassigned-out':plan['text']='return nativeAmount-nativeCount;'
   elif fault=='second-role':b['signature']['args'][0]['mode']='out';plan['signature']['args'][0]['mode']='out';plan['contract']=copy.deepcopy(b['signature'])
   elif fault=='return-type':b['signature']['return']='double';plan['signature']['return']='double';plan['contract']=copy.deepcopy(b['signature'])
   x.prepare(bad,False);x.unchanged();f.checked(fault+' refuses incomplete original disconnection/caller evidence or another ABI without original writes')

finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
