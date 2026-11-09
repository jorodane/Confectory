"""Native, UI and original source receipt lifecycle for retained private callers."""
import copy,json,pathlib,runpy,subprocess,sys
import v666_retained_nested_fixture as x
sys.modules['v666_retained_callers_fixture']=x
check=next((a.removeprefix('--check=')for a in sys.argv if a.startswith('--check=')),'ui')
if check=='ui'and x.mode=='conflict':runpy.run_path(str(pathlib.Path(__file__).with_name('v666_retained_callers_conflict.py')),run_name='__main__')
elif check=='ui':
 sys.modules['v536_information_shared_bodies_fixture']=x;__import__('os').environ['CONFECTORY_SHARED_BODIES']='1';runpy.run_path(str(pathlib.Path(__file__).with_name('v536_information_shared_return_types_ui.py')),run_name='__main__')
elif check!='native':runpy.run_path(str(pathlib.Path(__file__).with_name(('v666_retained_nested_'if check=='api'else'v666_retained_callers_')+check+'.py')),run_name='__main__')
else:
 f=x.f
 def prepare(request,ok=True):
  p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationDefinitions',**request)),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v
 r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
 try:
  if x.mode=='reproduce':
   for row in r['changes']:one=copy.deepcopy(r);one['changes']=[row];prepare(one)
   x.execute(x.original_result,'original-private-caller');v=prepare(r,False);assert'caller boundaries'in str(v),v;x.unchanged();f.checked('each individual native-body candidate and original nested caller program41 pass; grouped same-contract candidate alone rejects')
  else:
   result=prepare(r)['result'];updates=result['updates']+result['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']}for row in updates});assert{row['id']for row in result['linkedUpdates']}=={fn+'Body/body:common'for fn in x.functions};assert all(row['id']not in {x.n.caller+'Body/body:common',x.n.caller+'Body/body:common/node:outer/node:inner/node:preserved_code',x.n.caller+'Body/body:common/node:sibling/node:preserved_code'}for row in updates)
   reverse=copy.deepcopy(r);reverse['changes'].reverse();again=prepare(reverse)['result'];assert{row['id']:row['text']for row in updates}=={row['id']:row['text']for row in again['updates']+again['linkedUpdates']};x.unchanged();f.checked('order-independent native body group retains all original nested graph and qualified code bytes without emitting caller writes')
   caller=x.n.caller+'Body/body:common';code=caller+'/node:outer/node:inner/node:preserved_code'
   for fault in ['copy','forwarding','context','wrapper','stale-code','missing-code','binding']:
    bad=copy.deepcopy(r);g=json.loads(bad['units'][caller]['draft']);inner=g['nodes'][0]['graph']['nodes'][0]['graph']
    if fault=='copy':inner['copySource']={'unexpected':True}
    elif fault=='forwarding':inner['nodes'][-1]['forwardCallerStorage']=True
    elif fault=='context':inner['nodes'][-1]['implementationContext']={}
    elif fault=='wrapper':inner['nodes'][0]['postCall']={}
    elif fault=='stale-code':record=json.loads(bad['units'][code]['draft']);record['definitionHash']='0'*64;bad['units'][code]['draft']=json.dumps(record)
    elif fault=='missing-code':del bad['units'][code]
    else:inner['nodes'][0]['arguments']['amount']={'input':'absent'}
    if fault not in ['stale-code','missing-code']:bad['units'][caller]['draft']=json.dumps(g)
    prepare(bad,False);x.unchanged();f.checked('incomplete or out-of-scope private '+fault+' rejects without emitting a partial body candidate')
 finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2))
