"""Authenticate the two original scopes before composing a public pin rename."""
import copy,json,subprocess
import v666_private_pin_rename_fixture as x
f=x.f
def prepare(r,ok=True):
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationDefinitions',**r)),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v
try:
 r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
 for row in r['changes']:one=copy.deepcopy(r);one['changes']=[row];prepare(one)
 x.unchanged();x.execute(40,'original-private-pin-rename');f.checked('each original private/helper and public pin plan independently validates; original program executes40')
 if x.mode=='reproduce':
  reply=prepare(r,False);(f.case/'group-rejection.json').write_text(json.dumps(reply,ensure_ascii=False,indent=2));x.unchanged();f.checked('published package rejects only the combined private body and exact public pin rename without writes')
 else:
  for fault in ['stale-body','stale-graph','wrong-remap','unmapped-pin','type-change','role-change','pin-permutation','new-pin','private-contract','invalid-body','helper-escape']:
   bad=copy.deepcopy(r);a,b=bad['changes'];plan=next(iter(a['mapping']['bodies'].values()))
   if fault=='stale-body':plan['hash']='0'*64
   elif fault=='stale-graph':plan['whole']['hash']='0'*64
   elif fault=='wrong-remap':b['mapping']['args']['amount']='count'
   elif fault=='unmapped-pin':b['mapping']['args']['amount']=None
   elif fault=='type-change':b['signature']['args'][0]['type']='int'
   elif fault=='role-change':b['signature']['args'][0]['mode']='ref'
   elif fault=='pin-permutation':b['signature']['args'].reverse()
   elif fault=='new-pin':b['signature']['args'].append(dict(name='extra',type='long'))
   elif fault=='private-contract':plan['signature']['args'][0]['name']='implicitNative'
   elif fault=='invalid-body':next(iter(b['mapping']['bodies'].values()))['text']='return MissingRenameValue;'
   elif fault=='helper-escape':plan['helpers']='} class Escape {'
   prepare(bad,False);x.unchanged()
  result=prepare(r)['result'];(f.case/'candidate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));rows=result['updates']+result['linkedUpdates'];x.verify_rows({v['id']:dict(draft=v['text'])for v in rows});reverse=copy.deepcopy(r);reverse['changes'].reverse();other=prepare(reverse)['result'];assert{v['id']:v['text']for v in rows}=={v['id']:v['text']for v in other['updates']+other['linkedUpdates']};x.unchanged();f.checked('one order-independent candidate keeps private/native ABIs and exact caller binding identities while renaming only the selected public pin')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
