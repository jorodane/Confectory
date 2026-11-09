"""Existing UI and receipt lifecycle for explicitly reviewed native targets."""
import copy,json,pathlib,runpy,subprocess,sys
import v666_multitarget_bodies_fixture as x
sys.modules['v666_retained_callers_fixture']=x
check=next((a.removeprefix('--check=')for a in sys.argv if a.startswith('--check=')),'ui')
if check=='ui'and x.mode=='conflict':runpy.run_path(str(pathlib.Path(__file__).with_name('v666_retained_callers_conflict.py')),run_name='__main__')
elif check=='ui':
 sys.modules['v536_information_shared_bodies_fixture']=x;__import__('os').environ['CONFECTORY_SHARED_BODIES']='1';runpy.run_path(str(pathlib.Path(__file__).with_name('v536_information_shared_return_types_ui.py')),run_name='__main__')
elif check!='native':runpy.run_path(str(pathlib.Path(__file__).with_name(('v666_multitarget_bodies_'if check in ['api','review','targets']else'v666_retained_callers_')+check+'.py')),run_name='__main__')
else:
 f=x.f
 def prepare(request,ok=True):
  p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationDefinitions',**request)),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v
 r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
 try:
  if x.mode=='reproduce':
   for row in r['changes']:one=copy.deepcopy(r);one['changes']=[row];prepare(one)
   x.execute_both(False,'original-platforms');v=prepare(r,False);assert'single native target'in str(v),v;x.unchanged();f.checked('each explicit multi-target edit and both original platform programs40/44 are valid; grouped Save alone rejects')
  else:
   result=prepare(r)['result'];updates=result['updates']+result['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']}for row in updates});assert{row['id']for row in result['linkedUpdates']}==set(x.body_edits)
   other=copy.deepcopy(r);other['changes'].reverse();again=prepare(other)['result'];assert{row['id']:row['text']for row in updates}=={row['id']:row['text']for row in again['updates']+again['linkedUpdates']};x.unchanged();f.checked('one order-independent candidate contains all four explicitly reviewed native targets and preserves original headers, caller, contracts and identities')
   for fault in ['missing-target','unknown-target','signature','parent','stale-body']:
    bad=copy.deepcopy(r);bodies=bad['changes'][0]['mapping']['bodies'];key=x.functions[0]+'Body/body:linux'
    if fault=='missing-target':del bodies[key]
    elif fault=='unknown-target':bodies[key.replace(':linux',':other')]=bodies.pop(key)
    elif fault=='signature':bodies[key]['signature']['args'][0]['type']='int'
    elif fault=='parent':bad['units'][x.functions[0]+'Body']['draft']=bad['units'][x.functions[0]+'Body']['draft'].replace('{','extends '+x.functions[1]+'Body {',1)
    else:bodies[key]['hash']='0'*64
    prepare(bad,False);x.unchanged();f.checked('unreviewed or inconsistent '+fault+' rejects the whole target group without changing source or input')
 finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2))
