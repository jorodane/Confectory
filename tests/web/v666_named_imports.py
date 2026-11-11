"""Original read-only import closure for explicit native contract/body groups."""
import copy,hashlib,json,pathlib,runpy,sys
import v666_named_imports_fixture as x
check=next((a.removeprefix('--check=')for a in sys.argv if a.startswith('--check=')),'ui')
if check=='ui'and x.mode=='conflict':runpy.run_path(str(pathlib.Path(__file__).with_name('v666_named_imports_conflict.py')),run_name='__main__')
elif check=='ui':
 sys.modules['v536_information_shared_bodies_fixture']=x;__import__('os').environ['CONFECTORY_SHARED_BODIES']='1';runpy.run_path(str(pathlib.Path(__file__).with_name('v536_information_shared_return_types_ui.py')),run_name='__main__')
elif check in ['guards','api','late']:runpy.run_path(str(pathlib.Path(__file__).with_name('v666_named_imports_'+check+'.py')),run_name='__main__')
elif check=='native':
 try:
  r=x.request();(x.f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
  for row in r['changes']:one=copy.deepcopy(r);one['changes']=[row];x.n.prepare(one)
  x.unchanged();x.f.checked('each explicit original name/body operation with its owned helper validates without source writes')
  if x.mode=='reproduce':
   x.n.prepare(r,False);x.execute(x.original_result,'original-named-imports');x.unchanged();x.f.checked('published joint Save alone rejects valid singles; original imported program46')
  else:
   p=x.n.prepare(r);updates=p['updates']+p['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']}for row in updates});assert len({row['id']for row in updates})==len(updates)and all(row['hash']==hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest()for row in updates)
   reverse=copy.deepcopy(r);reverse['changes'].reverse();q=x.n.prepare(reverse);assert{row['id']:row['text']for row in updates}=={row['id']:row['text']for row in q['updates']+q['linkedUpdates']};assert all(row['id']not in [x.helper,x.helper+'Body',x.helper+'Body/body:common']for row in updates);x.unchanged();x.f.checked('one original-hash candidate is order independent; helper declaration/implementation/body remain reads, native declarations and aliases remain exact')
   for fault in ['type','mode','map','native','missing-body','body-hash','compile','helper-missing','helper-id','helper-type','helper-parent']:
    bad=copy.deepcopy(r);row=bad['changes'][0];body=next(iter(row['mapping']['bodies'].values()))
    if fault=='type':row['signature']['args'][0]['type']='int'
    elif fault=='mode':row['signature']['args'][0]['mode']='ref'
    elif fault=='map':row['mapping']['args']['amount']='count'
    elif fault=='native':body['signature']['args'][0]['name']='inferredNative'
    elif fault=='missing-body':body.pop('text')
    elif fault=='body-hash':body['hash']='0'*64
    elif fault=='compile':body['text']='return unknownValue;'
    elif fault=='helper-missing':del bad['units'][x.helper]
    else:
     text=bad['units'][x.helper]['draft']
     if fault=='helper-id':text=text.replace(x.helper+' ',x.f.n+'WrongHelper ',1)
     elif fault=='helper-type':text=text.replace('long value','string value')
     else:text=text.replace('{','{ parent '+x.f.n+'Unit;',1)
     assert text!=bad['units'][x.helper]['draft'];bad['units'][x.helper]['draft']=text
    x.n.prepare(bad,False);x.unchanged()
   x.f.checked('ABI/native/remap/invalid text and forged or missing owned import proof reject the entire name/body group')
 finally:(x.f.case/'checks.json').write_text(json.dumps(x.f.checks,ensure_ascii=False,indent=2))
else:raise ValueError(check)
