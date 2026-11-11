"""One explicit named native body group with existing forwarded private callers."""
import copy,hashlib,json,pathlib,runpy,sys
import v666_named_forwarding_fixture as x
f=x.f;check=next((a.removeprefix('--check=')for a in sys.argv if a.startswith('--check=')),'ui')
if check=='native':
 try:
  r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
  for row in r['changes']:
   one=copy.deepcopy(r);one['changes']=[row];x.n.prepare(one)
  x.unchanged();f.checked('each explicit original name/body candidate validates while private forwarding contracts and storage stay unchanged')
  if x.mode=='reproduce':
   x.n.prepare(r,False);x.execute(x.original_result,'original-named-forwarding');x.unchanged();f.checked('published joint candidate rejects valid single edits; original forwarded/private program41 remains valid')
  else:
   p=x.n.prepare(r);updates=p['updates']+p['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']}for row in updates});assert len({row['id']for row in updates})==len(updates)and all(row['hash']==hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest()for row in updates)
   reverse=copy.deepcopy(r);reverse['changes'].reverse();q=x.n.prepare(reverse);assert{row['id']:row['text']for row in updates}=={row['id']:row['text']for row in q['updates']+q['linkedUpdates']};assert not any('/node:'in row['id']for row in updates);x.unchanged();f.checked('one original-hash candidate is order independent; only native bodies/public contract and leaf call spelling change, preserving all private contracts, bindings, storage markers and C# records')
   for fault in ['copy','code-forward','context','wrapper','binding','stale-code','missing-code','type','mode','map','native']:
    bad=copy.deepcopy(r);key=x.n.caller+'Body/body:common';g=json.loads(bad['units'][key]['draft']);inner=g['nodes'][0]['graph']['nodes'][0]['graph'];row=bad['changes'][0];code=key+'/node:outer/node:inner/node:preserved_code'
    if fault=='copy':inner['copySource']={'unexpected':True}
    elif fault=='code-forward':inner['nodes'][-1]['forwardCallerStorage']=True
    elif fault=='context':inner['nodes'][-1]['implementationContext']={}
    elif fault=='wrapper':inner['nodes'][0]['graph']['nodes'][0]['postCall']={}
    elif fault=='binding':inner['nodes'][0]['graph']['nodes'][0]['arguments']['amount']={'constant':99}
    elif fault=='stale-code':record=json.loads(bad['units'][code]['draft']);record['definitionHash']='0'*64;bad['units'][code]['draft']=json.dumps(record)
    elif fault=='missing-code':del bad['units'][code]
    elif fault=='type':row['signature']['args'][0]['type']='int'
    elif fault=='mode':row['signature']['args'][0]['mode']='ref'
    elif fault=='map':row['mapping']['args']['amount']='count'
    else:next(iter(row['mapping']['bodies'].values()))['signature']['args'][0]['name']='inferredNative'
    if fault in ['copy','code-forward','context','wrapper','binding']:bad['units'][key]['draft']=json.dumps(g)
    x.n.prepare(bad,False);x.unchanged()
   f.checked('copy/opaque/code-storage/wrapper additions, forged forwarded bindings, missing/stale C# and incompatible ABI/native maps reject the complete group')
 finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2))
elif check=='ui'and x.mode=='conflict':
 sys.modules['v666_named_imports_fixture']=x;runpy.run_path(str(pathlib.Path(__file__).with_name('v666_named_imports_conflict.py')),run_name='__main__')
elif check=='ui':
 sys.modules['v536_information_shared_bodies_fixture']=x;__import__('os').environ['CONFECTORY_SHARED_BODIES']='1';runpy.run_path(str(pathlib.Path(__file__).with_name('v536_information_shared_return_types_ui.py')),run_name='__main__')
elif check in ['api','late','guards']:
 sys.modules['v666_named_nested_fixture']=x;runpy.run_path(str(pathlib.Path(__file__).with_name('v666_named_nested_'+check+'.py')),run_name='__main__')
else:raise ValueError(check)
