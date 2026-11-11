"""Use the existing owner UI and transaction for a bounded contract/body group."""
import copy,hashlib,json,pathlib,runpy,sys
import v666_named_body_group_fixture as x
check=next((a.removeprefix('--check=')for a in sys.argv if a.startswith('--check=')),'ui')
if check=='ui':
 sys.modules['v536_information_shared_bodies_fixture']=x;__import__('os').environ['CONFECTORY_SHARED_BODIES']='1';runpy.run_path(str(pathlib.Path(__file__).with_name('v536_information_shared_return_types_ui.py')),run_name='__main__')
elif check=='late':runpy.run_path(str(pathlib.Path(__file__).with_name('v666_named_body_group_late.py')),run_name='__main__')
elif check=='api':runpy.run_path(str(pathlib.Path(__file__).with_name('v666_named_body_group_api.py')),run_name='__main__')
elif check=='native':
 try:
  r=x.request();(x.f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
  for row in r['changes']:
   one=copy.deepcopy(r);one['changes']=[row];x.n.prepare(one)
  x.unchanged();x.f.checked('both individual explicit native-body/name candidates already validate without source writes')
  if'--imports-boundary'in sys.argv:
   prepared=x.n.prepare(r);x.verify_rows({row['id']:{'draft':row['text']}for row in prepared['updates']+prepared['linkedUpdates']});x.unchanged();x.f.checked('the formerly bounded local-import case now composes explicit names and bodies while retaining the original helper sources')
  elif x.mode=='reproduce':
   x.n.prepare(r,False);x.execute(x.original_result,'named-body-group-baseline');x.unchanged();x.f.checked('published group alone rejects valid explicit public input rename plus two native bodies; original actual result40')
  else:
   result=x.n.prepare(r);updates=result['updates']+result['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']}for row in updates});assert len({row['id']for row in updates})==len(updates)and all(row['hash']==hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest()for row in updates)
   reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.n.prepare(reverse);assert{row['id']:row['text']for row in updates}=={row['id']:row['text']for row in other['updates']+other['linkedUpdates']};x.unchanged();x.f.checked('both orders produce one exact original-hash candidate with explicit caller input remap and no native/header/C# inference')
   for fault in ['type','mode','order','return','map','out-name','native','hash','path','contract','missing','compile','boundary','caller-plan']:
    bad=copy.deepcopy(r);row=bad['changes'][0];mapping=row['mapping'];body=next(iter(mapping['bodies'].values()))
    if fault=='type':row['signature']['args'][0]['type']='int'
    elif fault=='mode':row['signature']['args'][0]['mode']='ref'
    elif fault=='order':row['signature']['args'].reverse()
    elif fault=='return':row['signature']['return']='double'
    elif fault=='map':mapping['args']['amount']='count'
    elif fault=='out-name':row['signature']['args'][1].update(mode='out',name='changedOutput')
    elif fault=='native':body['signature']['args'][0]['name']='silentlyRenamedNative'
    elif fault=='hash':body['hash']='0'*64
    elif fault=='path':body['path']='other.csbody'
    elif fault=='contract':body['contract']=copy.deepcopy(x.olds[0])
    elif fault=='missing':mapping['bodies'].clear()
    elif fault=='compile':body['text']='return missingValue;'
    elif fault=='boundary':body['text']='} public void Escape() {'
    else:mapping['callers']={}
    x.n.prepare(bad,False);x.unchanged()
   x.f.checked('type/role/order/return, nonidentity native declarations, missing/forged bodies, compile/boundary and caller-plan smuggling reject the complete group')
 finally:(x.f.case/'checks.json').write_text(json.dumps(x.f.checks,ensure_ascii=False,indent=2))
else:raise ValueError(check)
