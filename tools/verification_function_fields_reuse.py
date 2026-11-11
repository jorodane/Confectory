"""Guarded passing facts before the packaged golden-fixture path correction.

The changed native probe, builds, packages and every restore check run fresh.
"""
import ast,copy,json,subprocess,zipfile
from pathlib import Path
from verification_workspace import atomic_json,sha,verify_archive
SOURCE='d9986adb15bc796821b4594071f7ed2b53782b48'
NAMES={'function-fields-owned-ipc-lifetime'}|{'lf-'+name for name in ['v536_mixed_declaration','v536_local_header_image','function-fields-api','function-fields-normal','function-fields-storage','function-fields-module-regression','function-fields-array-golden']}|{'crlf-'+name for name in ['v536_mixed_declaration','v536_local_header_image','function-fields-api','function-fields-normal','function-fields-cancel','function-fields-live-guard']}

def validate(repo,record,commit,inputs):
 record=Path(record);prior=json.loads(record.read_text());manifest=json.loads(record.with_suffix('.manifest.json').read_text());blob=lambda rev,n:subprocess.check_output(['git','show',rev+':'+n],cwd=repo,text=True)
 if prior['source']!=SOURCE or prior['status']!='cleaned'or sha(prior['evidence'])!=prior['evidenceSha256']or manifest['archiveSha256']!=prior['evidenceSha256']:raise RuntimeError('Sealed original function-field evidence required')
 verify_archive(prior['evidence'],manifest['files'])
 fixture='tests/probes/v666_function_fields.py';allowed={fixture,'tools/verify_desktop.py','tools/verification_function_fields_reuse.py'};changed=subprocess.check_output(['git','diff','--name-only',SOURCE,commit],cwd=repo,text=True).splitlines()
 if not changed or any(n not in allowed and not n.startswith('docs/')for n in changed):raise RuntimeError('Product or unrelated test drift requires fresh checks')
 before=blob(SOURCE,fixture);after=blob(commit,fixture);old="golden=json.loads((r/'tests/fixtures/v666_function_fields_live_guard.json').read_text())";new="golden=json.loads(Path(sys.argv[3]if len(sys.argv)>3 else r/'tests/fixtures/v666_function_fields_live_guard.json').read_text())"
 if before.count(old)!=1 or after.count(new)!=1 or after.replace(new,old)!=before:raise RuntimeError('Native fixture changed beyond explicit baseline-path input')
 harness=blob(commit,'tools/verify_desktop.py');argument="    parser.add_argument('--reuse-function-fields',type=Path,help='Exact sealed passing checks after packaged fixture-path correction; builds/native/package/restore stay fresh')\n";hook="        if args.reuse_function_fields:\n            if args.suite!='function-fields':raise ValueError('Function-field reuse requires its own suite')\n            from verification_function_fields_reuse import bind\n            bind(repo,args.reuse_function_fields,commit,inputs,work)\n"
 old_run="work.run('restored-function-fields-native',[sys.executable,str(checkout/'tests/probes/v666_function_fields.py'),str(restored/'content'),'native'],cwd=checkout,env=env)";new_run="work.run('restored-function-fields-native',[sys.executable,str(checkout/'tests/probes/v666_function_fields.py'),str(restored/'content'),'native',str(checkout/'tests/fixtures/v666_function_fields_live_guard.json')],cwd=checkout,env=env)"
 normalized=harness.replace(argument,'').replace(hook,'').replace(",'verification_function_fields_reuse.py']:","]:").replace(new_run,old_run)
 if normalized!=blob(SOURCE,'tools/verify_desktop.py'):raise RuntimeError('Harness drift beyond the fixture path and guarded reuse hook')
 failed=[row for row in prior['results']if row['exit']!=0]
 if len(prior['results'])!=33 or len(failed)!=1 or failed[0]['name']!='restored-function-fields-native':raise RuntimeError('Exact preserved package fixture failure required')
 rows={row['name']:row for row in prior['results']if row['name']in NAMES and row['exit']==0}
 if set(rows)!=NAMES or len(rows)!=14:raise RuntimeError('All exact fourteen passing facts required')
 checked=set();pending=[]
 for row in rows.values():
  for arg in row['command']:
   for prefix in ['tests/web/','tests/probes/']:
    if prefix in str(arg)and str(arg).endswith('.py'):pending.append(prefix+str(arg).split(prefix,1)[1])
 while pending:
  name=pending.pop()
  if name in checked:continue
  checked.add(name)
  if name==fixture or blob(SOURCE,name)!=blob(commit,name):raise RuntimeError('Reused check depends on changed native fixture')
  text=blob(SOURCE,name)
  for node in ast.walk(ast.parse(text)):
   imports=[n.name for n in node.names]if isinstance(node,ast.Import)else[node.module]if isinstance(node,ast.ImportFrom)and node.module else[]
   for module in imports:
    for candidate in [Path(name).parent/(module.split('.')[0]+'.py'),Path('tools')/(module.split('.')[0]+'.py')]:
     if(repo/candidate).is_file():pending.append(candidate.as_posix())
   if isinstance(node,ast.Constant)and isinstance(node.value,str)and node.value.endswith('.py'):
    candidate=Path(name).parent/node.value
    if(repo/candidate).is_file():pending.append(candidate.as_posix())
 with zipfile.ZipFile(prior['evidence'])as z:
  identity=json.loads(z.read('source.json'));failure=z.read('restored-function-fields-native.log').decode()
  if identity['commit']!=SOURCE or any(identity['dependencyInputs'].get(k)!=inputs.get(k)for k in ['sdk','nuget','configuration','rid']):raise RuntimeError('Function-field SDK/dependency identity changed')
  if 'FileNotFoundError'not in failure or 'v666_function_fields_live_guard.json'not in failure:raise RuntimeError('Different package failure cannot be reused')
  for label,eol in [('lf','false'),('crlf','true')]:
   checkout=json.loads(z.read(label+'-checkout.json'))
   if checkout['commit']!=SOURCE or checkout['coreAutocrlf']!=eol or checkout['noSharedGitObjects']is not True:raise RuntimeError('Independent checkout proof differs')
  for name,row in rows.items():
   if json.loads(z.read(name+'.result.json'))!=row:raise RuntimeError('Archived passing result differs')
 return prior,rows,changed,sorted(checked)

def bind(repo,record,commit,inputs,work):
 prior,rows,changed,checked=validate(repo,record,commit,inputs);bad=copy.deepcopy(inputs);bad['sdk']['sha256']='0'*64
 try:validate(repo,record,commit,bad)
 except RuntimeError as e:
  if str(e)!='Function-field SDK/dependency identity changed':raise
 else:raise RuntimeError('Changed SDK accepted')
 parent=subprocess.check_output(['git','rev-parse',SOURCE+'^'],cwd=repo,text=True).strip()
 try:validate(repo,record,parent,inputs)
 except RuntimeError as e:
  if str(e)!='Product or unrelated test drift requires fresh checks':raise
 else:raise RuntimeError('Changed product accepted')
 proof=dict(previousRecord=str(record),previousSource=SOURCE,sourceCommit=commit,archiveSha256=prior['evidenceSha256'],identicalProductAndPassingImportClosure=True,checkedPythonDependencies=checked,allowedChangedFiles=changed,failedOrChangedChecksReused=False,buildsPackagesRestoreReused=False,negativeGuards=['changed SDK rejected','changed product rejected'],stages=[]);original=work.run
 def run(name,command,*args,**kwargs):
  if name not in rows:return original(name,command,*args,**kwargs)
  normalize=lambda cmd,root:[str(arg).replace(root,'$OWNED_WORKSPACE')for arg in cmd]
  if kwargs.get('expected',0)!=0 or normalize(rows[name]['command'],prior['root'])!=normalize(command,str(work.root))or name in proof['stages']:raise RuntimeError('Reused command differs or repeats: '+name)
  proof['stages'].append(name);work.state.setdefault('reusedChecks',[]).append(dict(name=name,sourceCommit=SOURCE,record=str(record),archiveSha256=prior['evidenceSha256']));work.save();atomic_json(work.evidence/'function-fields-reuse.json',proof);atomic_json(work.evidence/(name+'.reused.json'),dict(proof=proof,priorResult=rows[name]));print(json.dumps(dict(stage=name,reused=True,sourceCommit=SOURCE)),flush=True);return rows[name]
 work.run=run
