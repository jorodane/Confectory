"""One native caller is preserved as a read dependency, never rewritten."""
import copy,json,subprocess,hashlib
import v666_native_callers_fixture as x
f=x.f
def prepare(request,ok=True):
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationDefinitions',**request)),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v
r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
try:
 if x.mode=='reproduce':
  for row in r['changes']:one=copy.deepcopy(r);one['changes']=[row];prepare(one)
  x.unchanged();x.execute(x.original_result,'original-native-caller');f.checked('individual unchanged-contract body plans and original native caller are valid: result'+str(x.original_result))
  v=prepare(r,False);assert 'Retain the ordinary caller' in str(v),v;(f.case/'baseline-group-error.json').write_text(json.dumps(v,ensure_ascii=False,indent=2));x.unchanged();f.checked('published body group alone rejects a preserved native caller; authored input and original C# remain intact')
 else:
  result=prepare(r)['result'];updates=result['updates']+result['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']}for row in updates});assert {row['id']for row in result['linkedUpdates']}=={fn+'Body/body:common'for fn in x.functions}
  for row in updates:assert row['hash']==hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest()
  reverse=copy.deepcopy(r);reverse['changes'].reverse();other=prepare(reverse)['result'];assert {row['id']:row['text']for row in updates}=={row['id']:row['text']for row in other['updates']+other['linkedUpdates']};x.unchanged();f.checked('one order-independent candidate changes only explicit callee bodies, retaining native and Blueprint caller source, imports, aliases, signature and all original hashes')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2))
print('NATIVE_CALLERS',f.case,flush=True)
