"""Original nested source closure for explicit native contract/body groups."""
import copy,hashlib,json,pathlib,runpy,sys
import v666_named_nested_fixture as x
check=next((a.removeprefix('--check=')for a in sys.argv if a.startswith('--check=')),'ui')
if check=='ui':
 sys.modules['v536_information_shared_bodies_fixture']=x;__import__('os').environ['CONFECTORY_SHARED_BODIES']='1';runpy.run_path(str(pathlib.Path(__file__).with_name('v536_information_shared_return_types_ui.py')),run_name='__main__')
elif check=='guards':runpy.run_path(str(pathlib.Path(__file__).with_name('v666_named_nested_guards.py')),run_name='__main__')
elif check in ['api','late']:runpy.run_path(str(pathlib.Path(__file__).with_name('v666_named_nested_'+check+'.py')),run_name='__main__')
elif check=='native':
 try:
  r=x.request();(x.f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
  for row in r['changes']:one=copy.deepcopy(r);one['changes']=[row];x.n.prepare(one)
  x.unchanged();x.f.checked('each original native body/public name operation validates against the complete nested caller')
  if x.mode=='reproduce':
   x.n.prepare(r,False);x.execute(x.original_result,'original-nested-name');x.unchanged();x.f.checked('published joint name/body Save alone rejects valid singles; original nested program41')
  else:
   p=x.n.prepare(r);updates=p['updates']+p['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']}for row in updates});assert len({row['id']for row in updates})==len(updates)and all(row['hash']==hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest()for row in updates)
   reverse=copy.deepcopy(r);reverse['changes'].reverse();q=x.n.prepare(reverse);assert{row['id']:row['text']for row in updates}=={row['id']:row['text']for row in q['updates']+q['linkedUpdates']};assert not any('/node:'in row['id']for row in updates);x.unchanged();x.f.checked('both orders yield one original-hash candidate; native/header/qualified C# unchanged and only explicit nested call identity remapped')
   caller=x.n.caller+'Body/body:common';code=caller+'/node:outer/node:inner/node:preserved_code'
   for fault in ['copy','forward','context','wrapper','stale-code','missing-code','binding','type','mode','map','native']:
    bad=copy.deepcopy(r);g=json.loads(bad['units'][caller]['draft']);inner=g['nodes'][0]['graph']['nodes'][0]['graph'];row=bad['changes'][0]
    if fault=='copy':inner['copySource']={'unexpected':True}
    elif fault=='forward':inner['nodes'][-1]['forwardCallerStorage']=True
    elif fault=='context':inner['nodes'][-1]['implementationContext']={}
    elif fault=='wrapper':inner['nodes'][0]['postCall']={}
    elif fault=='stale-code':record=json.loads(bad['units'][code]['draft']);record['definitionHash']='0'*64;bad['units'][code]['draft']=json.dumps(record)
    elif fault=='missing-code':del bad['units'][code]
    elif fault=='binding':inner['nodes'][0]['arguments']['amount']={'input':'absent'}
    elif fault=='type':row['signature']['args'][0]['type']='int'
    elif fault=='mode':row['signature']['args'][0]['mode']='ref'
    elif fault=='map':row['mapping']['args']['amount']='count'
    else:next(iter(row['mapping']['bodies'].values()))['signature']['args'][0]['name']='inferredNative'
    if fault in ['copy','forward','context','wrapper','binding']:bad['units'][caller]['draft']=json.dumps(g)
    x.n.prepare(bad,False);x.unchanged()
   x.f.checked('private provenance/forward/context/wrapper boundaries, missing or stale qualified C#, absent values and ABI/native changes reject the complete group')
 finally:(x.f.case/'checks.json').write_text(json.dumps(x.f.checks,ensure_ascii=False,indent=2))
else:raise ValueError(check)
