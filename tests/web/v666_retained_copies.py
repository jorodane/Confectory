"""Owned copy retention, exact provenance receipt and native body lifecycle."""
import copy,json,pathlib,runpy,subprocess,sys
import v666_retained_copies_fixture as x
sys.modules['v666_retained_callers_fixture']=x
check=next((a.removeprefix('--check=')for a in sys.argv if a.startswith('--check=')),'ui')
if check=='ui'and x.mode=='conflict':runpy.run_path(str(pathlib.Path(__file__).with_name('v666_retained_callers_conflict.py')),run_name='__main__')
elif check=='ui':
 sys.modules['v536_information_shared_bodies_fixture']=x;__import__('os').environ['CONFECTORY_SHARED_BODIES']='1';runpy.run_path(str(pathlib.Path(__file__).with_name('v536_information_shared_return_types_ui.py')),run_name='__main__')
elif check!='native':runpy.run_path(str(pathlib.Path(__file__).with_name(('v666_retained_copies_'if check in ['api','guards']else'v666_retained_callers_')+check+'.py')),run_name='__main__')
else:
 f=x.f
 def prepare(request,ok=True):
  p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationDefinitions',**request)),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v
 r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
 try:
  if x.mode=='reproduce':
   for row in r['changes']:one=copy.deepcopy(r);one['changes']=[row];prepare(one)
   x.execute(x.original_result,'original-copy-caller');v=prepare(r,False);x.unchanged();f.checked('individual native candidates and original assigned-copy program40 pass; grouped native candidate alone rejects exact copy receipts')
  else:
   result=prepare(r)['result'];updates=result['updates']+result['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']}for row in updates});assert{row['id']for row in result['linkedUpdates']}=={fn+'Body/body:common'for fn in x.functions};reverse=copy.deepcopy(r);reverse['changes'].reverse();again=prepare(reverse)['result'];assert{row['id']:row['text']for row in updates}=={row['id']:row['text']for row in again['updates']+again['linkedUpdates']};x.unchanged();f.checked('order-independent native group retains the assigned saved copy and donor as read-only source identities')
   # Receipt and ownership faults are tested before any candidate can escape.
   for fault in ['missing-proof','proof-owner','proof-graph','proof-context','provenance','assignment','public-contract','nested-provenance','forwarding']:
    bad=copy.deepcopy(r);key=x.copy_id+'/body:common';g=json.loads(bad['units'][key]['draft'])
    if fault=='missing-proof':bad['changes'][0]['mapping'].pop('copies')
    elif fault=='proof-owner':bad['changes'][0]['mapping']['copies'][key]['owner']=x.owner
    elif fault=='proof-graph':bad['changes'][0]['mapping']['copies'][key]['graphHash']='0'*64
    elif fault=='proof-context':bad['changes'][0]['mapping']['copies'][key]['context'][0]['hash']='0'*64
    elif fault=='provenance':g['copySource']['implementation']=x.copy_id
    elif fault=='assignment':bad['units'][x.copy_owner]['draft']=bad['units'][x.copy_owner]['draft'].replace('with '+x.copy_id,'with '+x.donor_impl)
    elif fault=='public-contract':bad['changes'][0]['signature']['return']='int'
    elif fault=='nested-provenance':g['nodes'][0]['graph']={'copySource':g['copySource']}
    else:g['nodes'][0]['forwardCallerStorage']=True
    if fault in ['provenance','nested-provenance','forwarding']:bad['units'][key]['draft']=json.dumps(g)
    prepare(bad,False);x.unchanged();f.checked('retained copy '+fault+' rejects the complete native candidate without changing originals')
 finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2))
