"""Preserve existing ABI/source closure while composing owner presentation."""
import copy,json,hashlib,subprocess
import v666_header_bodies_fixture as x
f=x.f;r=x.request()
def prepare(request,ok=True):
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationDefinitions',**request)),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v
try:
 if x.mode=='reproduce':
  for changes in [[row]for row in r['changes']]+[[row for row in r['changes']if row['type']=='function-edit']]:
   one=copy.deepcopy(r);one['changes']=changes;prepare(one)
  x.unchanged();x.execute(x.original_result,'original-mixed-header');f.checked('both native bodies, owner description/icon and existing body-only group are independently valid; original program executes46')
  error=prepare(r,False);assert 'other input is retained'in str(error),error;(f.case/'baseline-mixed-error.json').write_text(json.dumps(error,ensure_ascii=False,indent=2));f.checked('only the authored mixed Save is rejected on published code')
 else:
  result=prepare(r)['result'];updates=result['updates']+result['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']}for row in updates}|{x.owner:{'draft':result['text']}});assert{row['id']for row in result['linkedUpdates']}=={fn+'Body/body:common'for fn in x.functions}
  for row in updates:assert row['hash']==hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest()
  reverse=copy.deepcopy(r);reverse['changes'].reverse();other=prepare(reverse)['result'];assert result['text']==other['text'];assert{row['id']:row['text']for row in updates}=={row['id']:row['text']for row in other['updates']+other['linkedUpdates']};x.unchanged();f.checked('one order-independent candidate publishes description/icon and explicit native bodies; caller source and public contracts remain unchanged')
  for fault in ['duplicate-description','duplicate-icon','extra-description-key','oversized-description','invalid-icon','structural-change','changed-contract']:
   bad=copy.deepcopy(r)
   if fault=='duplicate-description':bad['changes'].append(dict(type='description',text='other'))
   elif fault=='duplicate-icon':bad['changes'].append(dict(type='icon',text='★'))
   elif fault=='extra-description-key':bad['changes'][1]['grant']=True
   elif fault=='oversized-description':bad['changes'][1]['text']='x'*16385
   elif fault=='invalid-icon':bad['changes'][-1]['text']='not one glyph'
   elif fault=='structural-change':bad['changes'].append(dict(type='function-order',ids=x.functions[::-1]))
   else:bad['changes'][0]['signature']['return']='string'
   prepare(bad,False);x.unchanged();f.checked(fault+' rejects the whole candidate and retains every original source/input')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2))
