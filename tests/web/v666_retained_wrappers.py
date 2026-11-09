"""Native, UI and original source receipt lifecycle for retained post-call wrappers."""
import copy,json,pathlib,runpy,subprocess,sys
import v666_retained_wrappers_fixture as x
sys.modules['v666_retained_callers_fixture']=x
check=next((a.removeprefix('--check=')for a in sys.argv if a.startswith('--check=')),'ui')
if check=='ui'and x.mode=='conflict':runpy.run_path(str(pathlib.Path(__file__).with_name('v666_retained_callers_conflict.py')),run_name='__main__')
elif check=='ui':
 sys.modules['v536_information_shared_bodies_fixture']=x;__import__('os').environ['CONFECTORY_SHARED_BODIES']='1';runpy.run_path(str(pathlib.Path(__file__).with_name('v536_information_shared_return_types_ui.py')),run_name='__main__')
elif check!='native':runpy.run_path(str(pathlib.Path(__file__).with_name(('v666_retained_wrappers_'if check=='api'else'v666_retained_callers_')+check+'.py')),run_name='__main__')
else:
 f=x.f
 def prepare(request,ok=True):
  p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationDefinitions',**request)),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v
 r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
 try:
  if x.mode=='reproduce':
   for row in r['changes']:one=copy.deepcopy(r);one['changes']=[row];prepare(one)
   x.execute(x.original_result,'original-private-caller');v=prepare(r,False);assert'caller boundaries'in str(v),v;x.unchanged();f.checked('each individual native-body candidate and original wrapper caller program42 pass; grouped same-contract candidate alone rejects')
  else:
   result=prepare(r)['result'];updates=result['updates']+result['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']}for row in updates});assert{row['id']for row in result['linkedUpdates']}=={fn+'Body/body:common'for fn in x.functions};assert all(row['id']not in {x.n.caller+'Body/body:common',x.n.caller+'Body/body:common/postCall:invoke',x.n.caller+'Body/body:common/postCall:invoke_second'}for row in updates)
   reverse=copy.deepcopy(r);reverse['changes'].reverse();again=prepare(reverse)['result'];assert{row['id']:row['text']for row in updates}=={row['id']:row['text']for row in again['updates']+again['linkedUpdates']};x.unchanged();f.checked('order-independent native body group retains all original wrapper graph and original C# source/helpers without emitting caller writes')
   caller=x.n.caller+'Body/body:common'
   for fault in ['hash','mapping','publication','enum-id','enum-value','control','post-mode','original-execution','csharp-type']:
    bad=copy.deepcopy(r);g=json.loads(bad['units'][caller]['draft']);serial=g['nodes'][0];call=g['nodes'][1]
    if fault=='hash':call['postCall']['contractHash']='0'*64
    elif fault=='mapping':call['postCall'].pop('returnMapping')
    elif fault=='publication':bad['units'][x.functions[1]]['draft']=bad['units'][x.functions[1]]['draft'].replace('blueprintPublishedOutputs','changedPublication')
    elif fault=='enum-id':call['executionEnum']['members'][2]['id']='missing'
    elif fault=='enum-value':call['executionEnum']['members'][2]['value']=17
    elif fault=='control':serial['control']='branch'
    elif fault=='post-mode':serial['postCall']['mode']='unknown'
    elif fault=='original-execution':call['postCall']['originalExecution']='0'*64
    else:serial['postCall']['source']='return \"wrong return type\";'
    bad['units'][caller]['draft']=json.dumps(g);prepare(bad,False);x.unchanged();f.checked('inconsistent original wrapper '+fault+' rejects the entire candidate with source and input retained')

 finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2))
