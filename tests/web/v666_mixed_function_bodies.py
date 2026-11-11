"""Existing controls and atomic transaction compose two original editing flows."""
import copy,hashlib,json,pathlib,runpy,sys
import v666_mixed_function_bodies_fixture as x
check=next((a.removeprefix('--check=')for a in sys.argv if a.startswith('--check=')),'ui')
if check=='ui':
 sys.modules['v536_information_shared_bodies_fixture']=x;__import__('os').environ['CONFECTORY_SHARED_BODIES']='1';runpy.run_path(str(pathlib.Path(__file__).with_name('v536_information_shared_return_types_ui.py')),run_name='__main__')
elif check in ['api','late']:
 if check=='late':runpy.run_path(str(pathlib.Path(__file__).with_name('v666_mixed_function_bodies_late.py')),run_name='__main__')
 else:runpy.run_path(str(pathlib.Path(__file__).with_name('v666_mixed_function_bodies_api.py')),run_name='__main__')
elif check=='native':
 try:
  r=x.request();(x.f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
  for row in r['changes']:
   one=copy.deepcopy(r);one['changes']=[row];x.n.prepare(one)
  x.unchanged();x.f.checked('both original single Blueprint name and native body candidates validate without source writes')
  if x.mode=='reproduce'or'--boundary'in sys.argv:
   x.n.prepare(r,False);x.execute(x.original_result,'mixed-original-execution');x.unchanged();x.f.checked('published mixed group refuses individually valid edits; original actual program40'if x.mode=='reproduce'else'existing caller local state remains outside the new mixed group; valid singles and original program40 retained')
  else:
   p=x.n.prepare(r);updates=p['updates']+p['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']}for row in updates});assert len({row['id']for row in updates})==len(updates)and all(row['hash']==hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest()for row in updates)
   reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.n.prepare(reverse);assert{row['id']:row['text']for row in updates}=={row['id']:row['text']for row in other['updates']+other['linkedUpdates']};x.unchanged();x.f.checked('both orders yield one original-hash candidate with explicit Blueprint/caller input remap and native text only')
   for fault in ['type','role','order','return','map','caller','native','path','hash','missing','compile','boundary','overlap']:
    bad=copy.deepcopy(r);name=bad['changes'][0];body_row=bad['changes'][1];body=next(iter(body_row['mapping']['bodies'].values()))
    if fault=='type':name['signature']['args'][0]['type']='int'
    elif fault=='role':name['signature']['args'][0]['mode']='ref'
    elif fault=='order':name['signature']['args'].reverse()
    elif fault=='return':name['signature']['return']='double'
    elif fault=='map':name['mapping']['args']['amount']='count'
    elif fault=='caller':name['mapping']['callers']={}
    elif fault=='native':body['signature']['args'][0]['name']='newNative'
    elif fault=='path':body['path']='other.csbody'
    elif fault=='hash':body['hash']='0'*64
    elif fault=='missing':body.pop('text')
    elif fault=='compile':body['text']='return missingValue;'
    elif fault=='boundary':body['text']='} public void Escape() {'
    else:body_row['id']=name['id']
    (x.f.case/'fault-current.json').write_text(json.dumps(dict(fault=fault,request=bad),ensure_ascii=False));x.n.prepare(bad,False);x.unchanged()
   x.f.checked('changed ABI/roles/order/output, forged input/body proof, C# compile/boundary and overlapping identity reject all edits')
   absent=copy.deepcopy(r);absent['changes'][1]['mapping']['bodies'].clear();only_name=x.n.prepare(absent);assert all(row['id']!=x.body_function+'Body/body:common'for row in only_name['linkedUpdates']);x.unchanged();x.f.checked('removing the entire body intent retains the existing valid name-only path without inferring a native body write')
 finally:(x.f.case/'checks.json').write_text(json.dumps(x.f.checks,ensure_ascii=False,indent=2))
else:raise ValueError(check)
