"""Pure native closure; separate guarded admission from positive compilation."""
import copy,json,subprocess,sys,hashlib
import v666_body_imports_fixture as x
f=x.f
def prepare(request,ok=True):
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationDefinitions',**request)),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v
r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
if x.mode=='reproduce':
 for row in r['changes']:one=copy.deepcopy(r);one['changes']=[row];prepare(one)
 x.unchanged();f.checked('each unchanged-contract native body with its existing local import has a valid single candidate')
 x.execute(46,'published-original-imports');x.unchanged();f.checked('published original native imports/shared caller compile and execute result46 before editing')
 v=prepare(r,False);assert 'native leaf targets'in str(v),v;(f.case/'baseline-group-error.json').write_text(json.dumps(v,ensure_ascii=False,indent=2));x.unchanged();f.checked('published group guard alone rejects both otherwise valid native bodies and preserves all original input/source')
else:
 result=prepare(r)['result'];updates=result['updates']+result['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']}for row in updates});assert{row['id']for row in result['linkedUpdates']}=={fn+'Body/body:common'for fn in x.functions};assert len({row['id']for row in updates})==len(updates)
 for row in updates:assert row['hash']==hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest()
 reverse=copy.deepcopy(r);reverse['changes'].reverse();other=prepare(reverse)['result'];assert {row['id']:row['text']for row in updates}=={row['id']:row['text']for row in other['updates']+other['linkedUpdates']};x.unchanged();f.checked('one order-independent candidate retains original hashes, ABI/imports/helper and every shared caller byte')
print('BODY_IMPORTS_NATIVE',f.case,flush=True)
