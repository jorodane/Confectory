"""One same-contract native Save retains existing forwarding/opaque source closure."""
import copy,hashlib,json,os,pathlib,runpy,sys
import v666_retained_forwarding_fixture as x
f=x.f;check=next((a.removeprefix('--check=')for a in sys.argv if a.startswith('--check=')),'ui')
if check=='native':
 try:
  r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
  if x.mode=='reproduce':
   x.execute(x.original_result,'original-forwarded-opaque');x.n.prepare(r,False)
   for row in r['changes']:
    one=copy.deepcopy(r);one['changes']=[row];x.n.prepare(one,False)
   x.unchanged();f.checked('original program81 is valid; current group and single preparation reject retained forwarding/opaque caller sources')
  else:
   for row in r['changes']:
    one=copy.deepcopy(r);one['changes']=[row];x.n.prepare(one)
   result=x.n.prepare(r);updates=result['updates']+result['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']}for row in updates});assert {row['id']for row in result['linkedUpdates']}=={fn+'Body/body:common'for fn in x.functions}
   reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.n.prepare(reverse);assert {row['id']:row['text']for row in updates}=={row['id']:row['text']for row in other['updates']+other['linkedUpdates']};assert all(row['hash']==hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest()for row in updates);x.unchanged();f.checked('single and order-independent joint candidates change only the two selected native bodies; all forwarded/opaque sources remain reads')
   for fault in ['type','name','context','forward-binding','record-hash','record-source','missing-record']:
    bad=copy.deepcopy(r)
    if fault in ['type','name']:
     bad['changes'][0]['signature']['args'][0]['type'if fault=='type'else'name']='int'if fault=='type'else'changed';bad['changes'][0]['mapping']['bodies'][x.functions[0]+'Body/body:common']['contract']=copy.deepcopy(bad['changes'][0]['signature'])
     if fault=='name':bad['changes'][0]['mapping']['args']['amount']='changed'
    elif fault in ['record-hash','record-source','missing-record']:
     key=next(k for k,v in bad['units'].items()if v['path']==x.opaque_record)
     if fault=='missing-record':del bad['units'][key]
     else:
      record=json.loads(bad['units'][key]['draft']);record['definitionHash'if fault=='record-hash'else'source']='0'*64 if fault=='record-hash'else'return missingOpaqueValue;';bad['units'][key]['draft']=json.dumps(record)
    else:
     key=x.opaque+'Body/body:common'if fault=='context'else x.n.caller+'Body/body:common';g=json.loads(bad['units'][key]['draft'])
     if fault=='context':g['nodes'][0]['implementationContext']['implementation']=x.f.n+'DifferentBody'
     else:g['nodes'][0]['graph']['nodes'][0]['arguments']['amount']={'constant':99}
     bad['units'][key]['draft']=json.dumps(g)
    x.n.prepare(bad,False);x.unchanged()
   f.checked('changed public ABI/name, forged context/storage binding and missing/stale/uncompilable opaque records reject without changing source')
 finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2))
elif check=='ui'and x.mode=='conflict':
 sys.modules['v666_named_imports_fixture']=x;runpy.run_path(str(pathlib.Path(__file__).with_name('v666_named_imports_conflict.py')),run_name='__main__')
elif check=='ui':
 sys.modules['v536_information_shared_bodies_fixture']=x;os.environ['CONFECTORY_SHARED_BODIES']='1';runpy.run_path(str(pathlib.Path(__file__).with_name('v536_information_shared_return_types_ui.py')),run_name='__main__')
elif check=='api':runpy.run_path(str(pathlib.Path(__file__).with_name('v666_retained_forwarding_api.py')),run_name='__main__')
elif check in ['guards','late']:
 sys.modules['v666_retained_callers_fixture']=x;runpy.run_path(str(pathlib.Path(__file__).with_name('v666_retained_callers_'+check+'.py')),run_name='__main__')
else:raise ValueError(check)
