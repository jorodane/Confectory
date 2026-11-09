"""Original caller state must be retained, not rewritten or granted new contracts."""
import copy,json,subprocess,hashlib
import v666_retained_callers_fixture as x
f=x.f

def prepare(request,ok=True):
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationDefinitions',**request)),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v
r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
try:
 if x.mode=='reproduce':
  for row in r['changes']:one=copy.deepcopy(r);one['changes']=[row];prepare(one)
  x.execute(x.original_result,'original-retained-caller');v=prepare(r,False);assert 'Body-only groups retain copy, private, storage and wrapper caller boundaries'in str(v),v;x.unchanged();f.checked('each native edit and original program41 are valid; grouped Save alone rejects the unchanged ordinary caller code and locals')
 else:
  result=prepare(r)['result'];updates=result['updates']+result['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']}for row in updates});assert {row['id']for row in result['linkedUpdates']}=={fn+'Body/body:common'for fn in x.functions}
  for row in updates:assert row['hash']==hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest()
  reverse=copy.deepcopy(r);reverse['changes'].reverse();other=prepare(reverse)['result'];assert {row['id']:row['text']for row in updates}=={row['id']:row['text']for row in other['updates']+other['linkedUpdates']};x.unchanged();f.checked('one order-independent candidate changes only the two explicit native bodies and retains caller graph, code, locals, paths, contracts and original hashes')
  for fault in ['copy','private','forwarding','wrapper','branch']:
   bad=copy.deepcopy(r);g=json.loads(bad['units'][x.n.caller+'Body/body:common']['draft']);node=g['nodes'][-1]
   if fault=='copy':g['copySource']={}
   elif fault=='private':node['graph']={}
   elif fault=='forwarding':node['forwardCallerStorage']=True
   elif fault=='wrapper':node['postCall']={'source':'return true;'}
   else:node['control']='switch'
   bad['units'][x.n.caller+'Body/body:common']['draft']=json.dumps(g);prepare(bad,False);x.unchanged();f.checked('unselected '+fault+' caller context remains rejected without a new write scope or inferred conversion')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2))
