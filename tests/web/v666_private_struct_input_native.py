"""The original two single plans, and the finite mixed private/struct candidate."""
import copy,json
import v666_private_struct_input_fixture as x
f=x.f
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
 x.execute(40,'original-private-struct-input')
 for row in r['changes']:one=copy.deepcopy(r);one['changes']=[row];x.prepare(one)
 x.unchanged();f.checked('original program40 and both independent private/helper and nominal input plans validate with explicit existing caller value/disconnection')
 if x.mode=='reproduce':
  result=x.prepare(r,False);(f.case/'group-rejection.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));x.unchanged();f.checked('published mixed private/nominal group rejects without changing originals')
 else:
  result=x.prepare(r)['result'];(f.case/'candidate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));rows=result['updates']+result['linkedUpdates'];x.verify_rows({v['id']:dict(draft=v['text'])for v in rows});reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.prepare(reverse)['result'];assert{v['id']:v['text']for v in rows}=={v['id']:v['text']for v in other['updates']+other['linkedUpdates']};x.unchanged();f.checked('one order-independent private/nominal candidate retains native aliases, exact private frame/local/source and struct source proof')
  for fault in ['scope','type-proof','old-pin','disconnect','caller-value','native-alias','private-abi','array','ref','return']:
   bad=copy.deepcopy(r);a,b=bad['changes'];body=next(iter(b['mapping']['bodies'].values()));caller=next(iter(b['mapping']['callers'].values()))
   if fault=='scope':b['nativeTypes'].pop('$function:'+x.functions[1])
   elif fault=='type-proof':b['nativeTypes'].pop(x.packet)
   elif fault=='old-pin':b['mapping']['args']['amount']='amount'
   elif fault=='disconnect':caller['disconnect']={}
   elif fault=='caller-value':caller['inputs']['amount']={'binding':{'input':'first'}}
   elif fault=='native-alias':body['signature']['args'][0]['name']='inferredAlias'
   elif fault=='private-abi':next(iter(a['mapping']['bodies'].values()))['signature']['args'][0]['type']=x.packet
   elif fault=='array':b['signature']['args'][0]['type']+= '[]';body['signature']['args'][0]['type']+='[]';body['contract']=copy.deepcopy(b['signature'])
   elif fault=='ref':b['signature']['args'][0]['mode']='ref';body['signature']['args'][0]['mode']='ref';body['contract']=copy.deepcopy(b['signature'])
   elif fault=='return':b['signature']['return']=x.packet;body['signature']['return']=x.packet;body['contract']=copy.deepcopy(b['signature'])
   x.prepare(bad,False);x.unchanged();f.checked(fault+' refuses missing evidence or an unapproved conversion without original writes')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
