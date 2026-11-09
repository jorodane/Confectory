"""Run existing receipt/UI lifecycle coverage over a retained execution selector."""
import copy,json,os,pathlib,runpy,subprocess,sys
import v666_retained_branches_fixture as x
sys.modules['v666_retained_callers_fixture']=x
check=next((a.removeprefix('--check=')for a in sys.argv if a.startswith('--check=')),'ui')
if check=='api':x.retained_file=x.selector_file
if check!='native':
 runpy.run_path(str(pathlib.Path(__file__).with_name('v666_retained_callers_'+check+'.py')),run_name='__main__')
else:
 f=x.f
 def prepare(request,ok=True):
  p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationDefinitions',**request)),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v
 request=x.request();(f.case/'request.json').write_text(json.dumps(request,ensure_ascii=False,indent=2))
 try:
  if x.mode=='reproduce':
   for row in request['changes']:one=copy.deepcopy(request);one['changes']=[row];prepare(one)
   x.execute(x.original_result,'original-execution-choice');v=prepare(request,False);assert'Body-only groups retain copy, private, forwarding and wrapper caller boundaries'in str(v),v;x.unchanged();f.checked('each body edit and original branching program41 are valid; joint Save alone rejects the unchanged ordinary execution selector')
  else:
   result=prepare(request)['result'];updates=result['updates']+result['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']}for row in updates});assert{row['id']for row in result['linkedUpdates']}=={fn+'Body/body:common'for fn in x.functions}
   reverse=copy.deepcopy(request);reverse['changes'].reverse();other=prepare(reverse)['result'];assert{row['id']:row['text']for row in updates}=={row['id']:row['text']for row in other['updates']+other['linkedUpdates']};x.unchanged();f.checked('one order-independent candidate changes only two explicit native bodies; retained selector records, control IDs/values, exits and exact64 locals remain untouched')
   for fault in ['copy','private','forwarding','wrapper','invalid-selector']:
    bad=copy.deepcopy(request);g=json.loads(bad['units'][x.n.caller+'Body/body:common']['draft']);node=g['nodes'][-1]
    if fault=='copy':g['copySource']={}
    elif fault=='private':node['graph']={}
    elif fault=='forwarding':node['forwardCallerStorage']=True
    elif fault=='wrapper':node['postCall']={'source':'return true;'}
    else:node['control']='unknown'
    bad['units'][x.n.caller+'Body/body:common']['draft']=json.dumps(g);prepare(bad,False);x.unchanged();f.checked('unselected '+fault+' caller context rejects with original data and no inferred conversion')
   bad=copy.deepcopy(request);g=json.loads(bad['units'][x.n.caller+'Body/body:common']['draft']);node=g['nodes'][-1]
   if x.boolean:node['signature']['return']='void'
   else:node['executionEnum']['members'][1]['id']='different_case'
   bad['units'][x.n.caller+'Body/body:common']['draft']=json.dumps(g);prepare(bad,False);x.unchanged();f.checked('existing full graph/source validation rejects an inconsistent selector contract/route instead of inferring a new branch')
   bad=copy.deepcopy(request);key=next(k for k,v in bad['units'].items()if v.get('kind')=='blueprint-node'and v.get('path')==x.selector_file);record=json.loads(bad['units'][key]['draft']);record['definitionHash']='0'*64;bad['units'][key]['draft']=json.dumps(record);prepare(bad,False);x.unchanged();f.checked('a stale retained selector C# definition is rejected with both original bodies and pending input intact')
 finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2))
