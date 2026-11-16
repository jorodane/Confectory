"""Independent original source plans and the finite private/value-out candidate."""
import copy,json
import v666_private_value_out_fixture as x
f=x.f
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));x.execute(40,'original-private-value-out')
 for row in r['changes']:one=copy.deepcopy(r);one['changes']=[row];x.prepare(one)
 x.unchanged();f.checked('original40 and independent private/helper and value-out plans validate with an explicit old-input disconnection and identity return')
 if x.mode=='reproduce':
  result=x.prepare(r,False);(f.case/'group-rejection.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));x.unchanged();f.checked('published package rejects the combined private/value-out candidate without original writes')
 else:
  result=x.prepare(r)['result'];(f.case/'candidate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));rows=result['updates']+result['linkedUpdates'];x.verify_rows({v['id']:dict(draft=v['text'])for v in rows});reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.prepare(reverse)['result'];assert{v['id']:v['text']for v in rows}=={v['id']:v['text']for v in other['updates']+other['linkedUpdates']};x.unchanged();f.checked('order-independent private/value-out candidate retains aliases, original frame ABI and caller routes/outputs')
  for fault in ['missing-caller','disconnect','stale-disconnect','keep-input','drop-return','auto-out','native-alias','private-role','unassigned-out','ref-role','second-role','return-type']:
   bad=copy.deepcopy(r);a,b=bad['changes'];plan=next(iter(b['mapping']['bodies'].values()));caller=next(iter(b['mapping']['callers'].values()))
   if fault=='missing-caller':b['mapping'].pop('callers')
   elif fault=='disconnect':caller['disconnect']={}
   elif fault=='stale-disconnect':caller['disconnect']['count']='null'
   elif fault=='keep-input':caller['inputs']['count']='count'
   elif fault=='drop-return':caller['outputs']['return']=None
   elif fault=='auto-out':caller['outputs']['count']='count'
   elif fault=='native-alias':plan['signature']['args'][1]['name']='inferredCount'
   elif fault=='private-role':next(iter(a['mapping']['bodies'].values()))['signature']['args'][1]['mode']='out'
   elif fault=='unassigned-out':plan['text']=x.sources[x.functions[1]]
   elif fault=='ref-role':b['signature']['args'][1]['mode']='ref';plan['signature']['args'][1]['mode']='ref';plan['contract']=copy.deepcopy(b['signature'])
   elif fault=='second-role':b['signature']['args'][0]['mode']='out';plan['signature']['args'][0]['mode']='out';plan['contract']=copy.deepcopy(b['signature'])
   elif fault=='return-type':b['signature']['return']='double';plan['signature']['return']='double';plan['contract']=copy.deepcopy(b['signature'])
   x.prepare(bad,False);x.unchanged();f.checked(fault+' refuses incomplete explicit role/caller evidence or a different ABI without original writes')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
