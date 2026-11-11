"""Original-source proof, atomic native input replacement and existing UI lifecycle."""
import copy,hashlib,json,os,pathlib,runpy,sys
import v666_native_inputs_fixture as x
f=x.f;check=next((a.removeprefix('--check=')for a in sys.argv if a.startswith('--check=')),'ui')
if check=='native':
 try:
  r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
  for row in r['changes']:
   one=copy.deepcopy(r);one['changes']=[row];x.n.prepare(one)
  x.unchanged();f.checked('both complete explicit original single type/body/caller selections validate independently')
  if x.mode=='reproduce':x.n.prepare(r,False);x.execute(x.original_result,'original-native-inputs');x.unchanged();f.checked('published shared candidate rejects supported singles without changing original program70')
  else:
   p=x.n.prepare(r);updates=p['updates']+p['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']}for row in updates});assert len({row['id']for row in updates})==len(updates)and all(row['hash']==hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest()for row in updates)
   reverse=copy.deepcopy(r);reverse['changes'].reverse();q=x.n.prepare(reverse);assert{row['id']:row['text']for row in updates}=={row['id']:row['text']for row in q['updates']+q['linkedUpdates']};x.unchanged();f.checked('one order-independent original-hash candidate contains both native declarations/texts, public inputs and complete shared caller')
   for fault in ['mode','return','name','count','map','missing-body','native-header','stale-body','bad-code','missing-caller','disconnect','value','caller-hash','unselected-context']:
    bad=copy.deepcopy(r);row=bad['changes'][0];plan=next(iter(row['mapping']['bodies'].values()));caller=next(iter(row['mapping']['callers'].values()))
    if fault=='mode':row['signature']['args'][0]['mode']='ref'
    elif fault=='return':row['signature']['return']='double'
    elif fault=='name':row['signature']['args'][0]['name']='inferred'
    elif fault=='count':row['signature']['args'].pop()
    elif fault=='map':row['mapping']['args']['amount']='amount'
    elif fault=='missing-body':row['mapping']['bodies'].clear()
    elif fault=='native-header':plan['signature']=copy.deepcopy(x.native)
    elif fault=='stale-body':plan['hash']='0'*64
    elif fault=='bad-code':plan['text']='return amount+count;'
    elif fault=='missing-caller':row['mapping']['callers'].clear()
    elif fault=='disconnect':caller['disconnect'].clear()
    elif fault=='value':caller['inputs']['amount']={'valueJson':'123'}
    elif fault=='caller-hash':caller['hash']='0'*64
    else:
     key=x.n.caller+'Body/body:common';g=json.loads(bad['units'][key]['draft']);g['nodes'][0]['implementationContext']={};bad['units'][key]['draft']=json.dumps(g)
    x.n.prepare(bad,False);x.unchanged()
   f.checked('role/return/name/count changes, implicit type maps, missing/stale bodies/callers, wrong native headers/code/value/disconnect/context reject the whole candidate')
 finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2))
elif check in ['api','guards','late','conflict']:
 runpy.run_path(str(pathlib.Path(__file__).with_name('v666_native_inputs_'+check+'.py')),run_name='__main__')
elif check=='ui':
 sys.modules['v536_information_shared_bodies_fixture']=x;os.environ['CONFECTORY_SHARED_BODIES']='1';runpy.run_path(str(pathlib.Path(__file__).with_name('v536_information_shared_return_types_ui.py')),run_name='__main__')
else:raise ValueError(check)
