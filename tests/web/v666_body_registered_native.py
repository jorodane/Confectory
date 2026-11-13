"""Each registered single plan is valid; only the old grouped guard rejects."""
import copy,json,subprocess
import v666_body_registered_fixture as x
f=x.f
def prepare(r,ok=True):
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationDefinitions',**r)),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v
r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
try:
 for row in r['changes']:one=copy.deepcopy(r);one['changes']=[row];prepare(one)
 x.unchanged();x.execute(46,'original-registered');f.checked('each original single body/receipt validates and unchanged program executes46 with the registered helper/parent')
 if x.mode=='reproduce':
  rejected=prepare(r,False);(f.case/'group-rejection.json').write_text(json.dumps(rejected,ensure_ascii=False,indent=2));x.unchanged();f.checked('published grouped Save alone rejects valid readonly registered imports; original data, external files and permissions retained')
 else:
  for fault in ['missing-receipt','missing-contract','wrong-receipt-schema','caller-hash','changed-public-name','stale-body','invalid-last-body']:
   bad=copy.deepcopy(r);row=bad['changes'][1];mapping=row['mapping'];proof=next(iter(mapping['dependencies'].values()))
   if fault=='missing-receipt':mapping.pop('dependencies')
   elif fault=='missing-contract':proof['contracts'].pop(x.helper)
   elif fault=='wrong-receipt-schema':proof['schema']=2
   elif fault=='caller-hash':proof['callerHash']='0'*64
   elif fault=='changed-public-name':
    row['signature']['args'][0]['name']='renamed';mapping['args']['amount']='renamed'
    for body in mapping['bodies'].values():body['contract']=copy.deepcopy(row['signature'])
   elif fault=='stale-body':next(iter(mapping['bodies'].values()))['hash']='0'*64
   elif fault=='invalid-last-body':next(iter(mapping['bodies'].values()))['text']='return MissingRegisteredBodyValue;'
   (f.case/'current-rejection.json').write_text(json.dumps(dict(fault=fault,request=bad),ensure_ascii=False,indent=2));prepare(bad,False);x.unchanged()
  f.checked('missing/stale/foreign receipt claims, changed public contract and stale selected body reject atomically without external access expansion')
  result=prepare(r)['result'];updates=result['updates']+result['linkedUpdates'];x.verify_rows({row['id']:dict(draft=row['text'])for row in updates});assert {row['id']for row in result['linkedUpdates']}=={fn+'Body/body:common'for fn in x.functions}
  rev=copy.deepcopy(r);rev['changes'].reverse();other=prepare(rev)['result'];assert{row['id']:row['text']for row in updates}=={row['id']:row['text']for row in other['updates']+other['linkedUpdates']};x.unchanged();f.checked('registered body group is order independent, exact original hashes/contracts/aliases/callers retained, and only selected bodies change')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
