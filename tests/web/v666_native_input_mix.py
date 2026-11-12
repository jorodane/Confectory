"""Original-source proof, atomic native input type/definition change and existing UI lifecycle."""
import copy,hashlib,json,os,pathlib,runpy,sys
import v666_native_input_mix_fixture as x
f=x.f;check=next((a.removeprefix('--check=')for a in sys.argv if a.startswith('--check=')),'ui')
if check=='native':
 try:
  x.execute(x.original_result,'original-return-runtime');f.checked('original runtime interfaces return long34 with no out parameters; original shared caller executes38')
  r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
  for row in r['changes']:
   one=copy.deepcopy(r);one['changes']=[row];x.n.prepare(one)
  x.unchanged();f.checked('both complete explicit original single type/body/caller selections validate independently')
  if x.mode=='reproduce':x.n.prepare(r,False);x.unchanged();f.checked('published shared candidate rejects supported singles without changing original program38')
  else:
   p=x.n.prepare(r);updates=p['updates']+p['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']}for row in updates});assert len({row['id']for row in updates})==len(updates)and all(row['hash']==hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest()for row in updates)
   reverse=copy.deepcopy(r);reverse['changes'].reverse();q=x.n.prepare(reverse);assert{row['id']:row['text']for row in updates}=={row['id']:row['text']for row in q['updates']+q['linkedUpdates']};x.unchanged();f.checked('one order-independent original-hash candidate contains both native declarations/texts, explicit input type/definition change and complete shared caller')
   for fault in ['mode','new-role','return-type','arg-map','missing-map','input-type','name','no-removal','map','removed-map','missing-body','native-header','native-alias','native-return','native-role','stale-body','bad-code','missing-caller','outputs','out-identity','missing-input','replacement-value','missing-disconnect','wrong-disconnect','missing-changed-disconnect','missing-value','wrong-value-type','implicit-binding','new-role-out','public-order','native-order','implicit-changed-binding','wrong-changed-disconnect','caller-hash','unselected-context']:
    bad=copy.deepcopy(r);row=bad['changes'][0];plan=next(iter(row['mapping']['bodies'].values()));caller=next(iter(row['mapping']['callers'].values()))
    if fault=='mode':row['signature']['args'][0]['mode']='ref'
    elif fault=='new-role':row['signature']['args'][0]['mode']='out'
    elif fault=='return-type':row['signature']['return']='double'
    elif fault=='arg-map':row['mapping']['args']['unknown']=None
    elif fault=='missing-map':del row['mapping']['args']['amount']
    elif fault=='input-type':row['signature']['args'][0]['type']='bool'
    elif fault=='name':row['signature']['args'][0]['name']='inferred'
    elif fault=='no-removal':row['signature']=copy.deepcopy(x.old)
    elif fault=='map':row['mapping']['args']['real']='real'
    elif fault=='removed-map':row['mapping']['args']['amount']='real'
    elif fault=='missing-body':row['mapping']['bodies'].clear()
    elif fault=='native-header':plan['signature']=copy.deepcopy(x.native)
    elif fault=='native-alias':plan['signature']['args'][0]['name']='nativeReal'
    elif fault=='native-return':plan['signature']['return']='double'
    elif fault=='native-role':plan['signature']['args'][0]['mode']='ref'
    elif fault=='stale-body':plan['hash']='0'*64
    elif fault=='bad-code':plan['text']='return nativeAmount;'
    elif fault=='missing-caller':row['mapping']['callers'].clear()
    elif fault=='outputs':caller['outputs']={'return':None}
    elif fault=='out-identity':caller['outputs']={'return':'real'}
    elif fault=='missing-input':caller['inputs'].pop('real')
    elif fault=='replacement-value':caller['inputs']['real']={'valueJson':'1.25'}
    elif fault=='missing-disconnect':caller['disconnect'].clear()
    elif fault=='wrong-disconnect':caller['disconnect']['amount']='{"constant":30}'
    elif fault=='missing-changed-disconnect':caller['disconnect'].pop('real')
    elif fault=='missing-value':caller['inputs'].pop('step')
    elif fault=='wrong-value-type':caller['inputs']['step']={'valueJson':'true'}
    elif fault=='implicit-binding':caller['inputs']['step']='real'
    elif fault=='new-role-out':row['signature']['args'][1]['mode']='out'
    elif fault=='public-order':row['signature']['args'].reverse()
    elif fault=='native-order':plan['signature']['args'].reverse()
    elif fault=='implicit-changed-binding':caller['inputs']['real']='real'
    elif fault=='wrong-changed-disconnect':caller['disconnect']['real']='{"constant":99}'
    elif fault=='caller-hash':caller['hash']='0'*64
    else:
     key=x.n.caller+'Body/body:common';g=json.loads(bad['units'][key]['draft']);g['nodes'][0]['implementationContext']={};bad['units'][key]['draft']=json.dumps(g)
    x.n.prepare(bad,False);x.unchanged()
   f.checked('missing/wrong original disconnections or new values, survivor alias/type/role/name/order changes, implicit replacement values, stale bodies/callers/output plans and deleted-variable CSharp reject without source changes')

 finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2))
elif check in ['api','guards','late','conflict']:
 runpy.run_path(str(pathlib.Path(__file__).with_name('v666_native_input_mix_'+check+'.py')),run_name='__main__')
elif check=='ui':
 sys.modules['v536_information_shared_bodies_fixture']=x;os.environ['CONFECTORY_SHARED_BODIES']='1';runpy.run_path(str(pathlib.Path(__file__).with_name('v536_information_shared_return_types_ui.py')),run_name='__main__')
else:raise ValueError(check)
