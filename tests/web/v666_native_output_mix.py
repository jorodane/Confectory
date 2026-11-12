"""Original-source proof, atomic native out and return type replacement and existing UI lifecycle."""
import copy,hashlib,json,os,pathlib,runpy,sys
import v666_native_output_mix_fixture as x
f=x.f;check=next((a.removeprefix('--check=')for a in sys.argv if a.startswith('--check=')),'ui')
if check=='native':
 try:
  x.execute(x.original_result,'original-return-runtime');f.checked('original runtime interfaces return long40 and out long34/37; original shared caller executes38')
  r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
  for row in r['changes']:
   one=copy.deepcopy(r);one['changes']=[row];x.n.prepare(one)
  x.unchanged();f.checked('both complete explicit original single type/body/caller selections validate independently')
  if x.mode=='reproduce':x.n.prepare(r,False);x.unchanged();f.checked('published shared candidate rejects supported singles without changing original program38')
  else:
   p=x.n.prepare(r);updates=p['updates']+p['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']}for row in updates});assert len({row['id']for row in updates})==len(updates)and all(row['hash']==hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest()for row in updates)
   replacement=copy.deepcopy(r)
   for row in replacement['changes']:row['mapping']['args']['count']=None
   null_candidate=x.n.prepare(replacement);assert{row['id']:row['text']for row in updates}=={row['id']:row['text']for row in null_candidate['updates']+null_candidate['linkedUpdates']}
   reverse=copy.deepcopy(r);reverse['changes'].reverse();q=x.n.prepare(reverse);assert{row['id']:row['text']for row in updates}=={row['id']:row['text']for row in q['updates']+q['linkedUpdates']};x.unchanged();f.checked('one order-independent original-hash candidate contains both native declarations/texts, explicit out/return types and complete shared caller')
   # The original fixed row also allows one function's out edit alongside
   # another function's return edit, with every unchanged output kept exact.
   separated=copy.deepcopy(r)
   for index,row in enumerate(separated['changes']):
    if index==0:
     row['signature']['return']='long';text='count=real;saved=calls.StableHelper.Invoke(checked(amount+2));return checked(amount+10);'
     for caller in row['mapping']['callers'].values():caller['outputs']['return']='return'
    else:
     row['signature']['args'][2]['type']='long';text='count=calls.StableHelper.Invoke(checked(amount+1));saved=calls.StableHelper.Invoke(checked(amount+2));return real+0.5;'
     for caller in row['mapping']['callers'].values():caller['outputs']['count']='count'
    for body in row['mapping']['bodies'].values():body['signature']=copy.deepcopy(row['signature']);body['contract']=copy.deepcopy(row['signature']);body['text']=text
    one=copy.deepcopy(separated);one['changes']=[row];x.n.prepare(one)
   separate_candidate=x.n.prepare(separated);rev=copy.deepcopy(separated);rev['changes'].reverse();other=x.n.prepare(rev)
   assert{u['id']:u['text']for u in separate_candidate['updates']+separate_candidate['linkedUpdates']}=={u['id']:u['text']for u in other['updates']+other['linkedUpdates']}
   x.unchanged();f.checked('out-only and return-only original singles also compose across functions without rebasing or changing retained outputs')
   for fault in ['mode','out-role','return-void','out-map','missing-out-map','input-type','name','count','map','missing-body','native-header','stale-body','bad-code','missing-caller','outputs','out-identity','new-input','caller-hash','unselected-context','missing-return-map','wrong-return-type','changed-retained-out','missing-retained-output','unknown-output']:
    bad=copy.deepcopy(r);row=bad['changes'][0];plan=next(iter(row['mapping']['bodies'].values()));caller=next(iter(row['mapping']['callers'].values()))
    if fault=='mode':row['signature']['args'][0]['mode']='ref'
    elif fault=='out-role':row['signature']['args'][2].pop('mode')
    elif fault=='return-void':row['signature']['return']='void'
    elif fault=='out-map':row['mapping']['args']['count']='amount'
    elif fault=='missing-out-map':del row['mapping']['args']['count']
    elif fault=='input-type':row['signature']['args'][0]['type']='double'
    elif fault=='name':row['signature']['args'][0]['name']='inferred'
    elif fault=='count':row['signature']['args'].pop()
    elif fault=='map':row['mapping']['args']['amount']=None
    elif fault=='missing-body':row['mapping']['bodies'].clear()
    elif fault=='native-header':plan['signature']=copy.deepcopy(x.native)
    elif fault=='stale-body':plan['hash']='0'*64
    elif fault=='bad-code':plan['text']='return 1;'
    elif fault=='missing-caller':row['mapping']['callers'].clear()
    elif fault=='outputs':caller['outputs']['count']='count'
    elif fault=='out-identity':caller['outputs']['saved']='count'
    elif fault=='new-input':caller['inputs']['amount']={'valueJson':'123'}
    elif fault=='caller-hash':caller['hash']='0'*64
    elif fault=='missing-return-map':del caller['outputs']['return']
    elif fault=='wrong-return-type':caller['outputs']['return']='count'
    elif fault=='changed-retained-out':row['signature']['args'][3]['type']='double'
    elif fault=='missing-retained-output':del caller['outputs']['saved']
    elif fault=='unknown-output':caller['outputs']['count']='missing'
    else:
     key=x.n.caller+'Body/body:common';g=json.loads(bad['units'][key]['draft']);g['nodes'][0]['implementationContext']={};bad['units'][key]['draft']=json.dumps(g)
    x.n.prepare(bad,False);x.unchanged()
   f.checked('role/input/name/count changes, implicit output maps, missing/stale bodies/callers, wrong native headers/code/input/output/context reject the whole candidate')
 finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2))
elif check in ['api','guards','late','conflict']:
 runpy.run_path(str(pathlib.Path(__file__).with_name('v666_native_output_mix_'+check+'.py')),run_name='__main__')
elif check=='ui':
 sys.modules['v536_information_shared_bodies_fixture']=x;os.environ['CONFECTORY_SHARED_BODIES']='1';runpy.run_path(str(pathlib.Path(__file__).with_name('v536_information_shared_return_types_ui.py')),run_name='__main__')
else:raise ValueError(check)
