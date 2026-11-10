"""Resume sealed passing facts after correcting only an unchanged-record assertion."""
import ast,json,subprocess,zipfile
from pathlib import Path
from verification_workspace import atomic_json,sha,verify_archive

def bind(repo,record,commit,inputs,work):
 prior=json.loads(Path(record).read_text());manifest=json.loads(Path(record).with_suffix('.manifest.json').read_text());blob=lambda rev,n:subprocess.check_output(['git','show',rev+':'+n],cwd=repo,text=True)
 if prior['status']!='cleaned'or sha(prior['evidence'])!=prior['evidenceSha256']or manifest['archiveSha256']!=prior['evidenceSha256']:raise RuntimeError('Sealed failed-run evidence required')
 verify_archive(prior['evidence'],manifest['files'])
 fixture='tests/web/v536_information_retained_fixture.py';allowed={fixture,'tools/verify_desktop.py','tools/verification_native_retained_reuse.py'};changed=subprocess.check_output(['git','diff','--name-only',prior['source'],commit],cwd=repo,text=True).splitlines()
 if not changed or any(n not in allowed and not n.startswith('docs/')for n in changed):raise RuntimeError('Product or unrelated test drift requires fresh checks')
 product=json.loads(blob(commit,'docs/v666-native-retained-delta.json'))['productFiles']
 if len(product)!=4 or any(blob(prior['source'],n)!=blob(commit,n)for n in product):raise RuntimeError('Product source drift')
 harness=blob(commit,'tools/verify_desktop.py')
 argument="    parser.add_argument('--reuse-native-retained',type=Path,help='Sealed identical passing facts after the unchanged-code record fixture assertion; builds and failed check run fresh')\n"
 hook="        if args.reuse_native_retained:\n            if args.suite!='native-retained':raise ValueError('Retained native evidence requires its own suite')\n            from verification_native_retained_reuse import bind\n            bind(repo,args.reuse_native_retained,commit,inputs,work)\n"
 normalized_harness=harness.replace(argument,'').replace(hook,'').replace(",'verification_native_retained_reuse.py']:","]:")
 if normalized_harness!=blob(prior['source'],'tools/verify_desktop.py'):raise RuntimeError('Harness drift beyond the guarded resume hook')
 before=blob(prior['source'],fixture);after=blob(commit,fixture)
 old=" assert json.loads(rows[fn+'Body/body:common/node:extra']['draft'])['source']==extra_record['source']"
 new=" extra_id=fn+'Body/body:common/node:extra'\n if extra_id in rows:assert json.loads(rows[extra_id]['draft'])['source']==extra_record['source']\n else:assert(f.project/'extra.node.json').read_bytes()==snapshot['extra.node.json']"
 normalized=after.replace(new,old).replace('assert extra_id not in rows or extra_id in ids;return ids',"assert fn+'Body/body:common/node:extra' in ids;return ids")
 if normalized!=before:raise RuntimeError('Fixture drift beyond unchanged record/source assertion')
 failed=[r for r in prior['results']if r['exit']!=0]
 if len(prior['results'])!=18 or len(failed)!=1 or failed[0]['name']!='lf-native-retained-primitive-regression':raise RuntimeError('Exact preserved failure required')
 names={'native-retained-owned-ipc-lifetime'}|{'lf-'+n for n in ['v536_mixed_declaration','v536_local_header_image','native-retained-receipts','native-retained-api','native-retained-whole-regression','native-retained-normal','native-retained-storage','native-retained-conflict','native-retained-consumer-ui','native-retained-consumer-api']};rows={r['name']:r for r in prior['results']if r['name']in names and r['exit']==0}
 if len(rows)!=11 or set(rows)!=names:raise RuntimeError('All exact passing facts required')
 modules=set();pending=[Path(a).name for row in rows.values()for a in row['command']if str(a).endswith('.py')]
 while pending:
  name=pending.pop();path='tests/web/'+name
  if name in modules or not(repo/path).is_file():continue
  modules.add(name);text=blob(prior['source'],path)
  if text!=blob(commit,path)or 'v536_information_retained_fixture'in text:raise RuntimeError('Reused test depends on corrected fixture')
  for node in ast.walk(ast.parse(text)):
   imports=[n.name for n in node.names]if isinstance(node,ast.Import)else[node.module]if isinstance(node,ast.ImportFrom)and node.module else[]
   for mod in imports:
    if(repo/'tests/web'/(mod.split('.')[0]+'.py')).is_file():pending.append(mod.split('.')[0]+'.py')
 with zipfile.ZipFile(prior['evidence'])as z:
  source=json.loads(z.read('source.json'));checkout=json.loads(z.read('lf-checkout.json'));failure=z.read('lf-native-retained-primitive-regression.log').decode()
  if source['commit']!=prior['source']or any(source['dependencyInputs'].get(k)!=inputs.get(k)for k in ['sdk','nuget','configuration','rid']):raise RuntimeError('Dependency/compiler identity differs')
  if checkout['commit']!=prior['source']or checkout['coreAutocrlf']!='false'or checkout['noSharedGitObjects']is not True:raise RuntimeError('Independent LF checkout proof differs')
  if 'KeyError: 'not in failure or 'node:extra'not in failure or "rows[fn+'Body/body:common/node:extra']"not in failure:raise RuntimeError('Different failed check')
 proof=dict(previousRecord=str(record),previousSource=prior['source'],sourceCommit=commit,archiveSha256=prior['evidenceSha256'],identicalProductSourceAndPassingTestDependencies=True,correctedFixtureAbsentFromPassingImportClosure=sorted(modules),independentLFCheckout=checkout,failedChecksReused=False,buildsAndPackagesReused=False,stages=[]);original=work.run
 def run(name,command,*args,**kwargs):
  if name not in rows:return original(name,command,*args,**kwargs)
  normalize=lambda cmd,root:[str(arg).replace(root,'$OWNED_WORKSPACE')for arg in cmd]
  if kwargs.get('expected',0)!=0 or normalize(rows[name]['command'],prior['root'])!=normalize(command,str(work.root))or name in proof['stages']:raise RuntimeError('Reused command differs or repeats: '+name)
  proof['stages'].append(name);work.state.setdefault('reusedChecks',[]).append(dict(name=name,sourceCommit=prior['source'],record=str(record),archiveSha256=prior['evidenceSha256']));work.save();atomic_json(work.evidence/'native-retained-reuse.json',proof);atomic_json(work.evidence/(name+'.reused.json'),dict(proof=proof,priorResult=rows[name]));print(json.dumps(dict(stage=name,reused=True,sourceCommit=prior['source'])),flush=True);return rows[name]
 work.run=run
