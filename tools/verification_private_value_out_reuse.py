"""Guarded passing facts before correcting an unexecuted regression file path.

All reused tests and product code are byte-identical. Builds, failed checks, CRLF, packages and restore run fresh.
"""
import ast,copy,json,subprocess,zipfile
from pathlib import Path
from verification_workspace import atomic_json,sha,verify_archive
SOURCE='2c3bd030448b69bdcdb9fa1982fe3669d632e49d'
NAMES={'lf-private-value-out-'+n for n in ['native','normal','view','storage','guards','api','late']}|{'lf-private-value-out-regression-'+n for n in ['struct-input-native','struct-input-guards','pin-rename-native','whole-api']}

def validate(repo,record,commit,inputs):
 record=Path(record);prior=json.loads(record.read_text());manifest=json.loads(record.with_suffix('.manifest.json').read_text());blob=lambda rev,n:subprocess.check_output(['git','show',rev+':'+n],cwd=repo,text=True)
 if prior['source']!=SOURCE or prior['status']!='cleaned'or sha(prior['evidence'])!=prior['evidenceSha256']or manifest['archiveSha256']!=prior['evidenceSha256']:raise RuntimeError('Sealed original private-value-out evidence required')
 verify_archive(prior['evidence'],manifest['files'])
 allowed={'tools/verify_desktop.py','tools/verification_private_value_out_reuse.py'};changed=subprocess.check_output(['git','diff','--name-only',SOURCE,commit],cwd=repo,text=True).splitlines()
 if not changed or any(n not in allowed and not n.startswith('docs/')for n in changed):raise RuntimeError('Product or unrelated test drift requires fresh checks')
 harness=blob(commit,'tools/verify_desktop.py');argument="    parser.add_argument('--reuse-private-value-out',type=Path,help='Exact sealed passing checks before correcting native role regression path; builds/failed checks/CRLF/packages/restore stay fresh')\n";hook="        if args.reuse_private_value_out:\n            if args.suite!='private-value-out':raise ValueError('Private value out reuse requires its own suite')\n            from verification_private_value_out_reuse import bind\n            bind(repo,args.reuse_private_value_out,commit,inputs,work)\n"
 old="('native-value-out','v666_native_value_out_native.py',[])";new="('native-value-out','v666_native_value_out.py',['--check=native'])"
 if harness.count(new)!=1:raise RuntimeError('Exact missing regression path correction required')
 normalized=harness.replace(argument,'').replace(hook,'').replace(",'verification_private_value_out_reuse.py'",'').replace(new,old)
 if normalized!=blob(SOURCE,'tools/verify_desktop.py'):raise RuntimeError('Harness drift beyond path correction and guarded reuse')
 failed=[row for row in prior['results']if row['exit']!=0]
 if len(prior['results'])!=20 or len(failed)!=1 or failed[0]['name']!='lf-private-value-out-regression-native-value-out':raise RuntimeError('Exact preserved missing regression path failure required')
 rows={row['name']:row for row in prior['results']if row['name']in NAMES and row['exit']==0}
 if set(rows)!=NAMES or len(rows)!=11:raise RuntimeError('All exact eleven passing facts required')
 checked=set();pending=[]
 for row in rows.values():
  for arg in row['command']:
   for prefix in ['tests/web/','tests/probes/']:
    if prefix in str(arg)and str(arg).endswith('.py'):pending.append(prefix+str(arg).split(prefix,1)[1])
 while pending:
  name=pending.pop()
  if name in checked:continue
  checked.add(name)
  if blob(SOURCE,name)!=blob(commit,name):raise RuntimeError('Reused dependency changed')
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
  identity=json.loads(z.read('source.json'));failure=z.read('lf-private-value-out-regression-native-value-out.log').decode()
  if identity['commit']!=SOURCE or any(identity['dependencyInputs'].get(k)!=inputs.get(k)for k in ['sdk','nuget','configuration','rid']):raise RuntimeError('Private value out SDK/dependency identity changed')
  if "can't open file"not in failure or 'v666_native_value_out_native.py'not in failure or '[Errno 2] No such file or directory'not in failure:raise RuntimeError('Different regression failure cannot be reused')
  checkout=json.loads(z.read('lf-checkout.json'))
  if checkout['commit']!=SOURCE or checkout['coreAutocrlf']!='false'or checkout['noSharedGitObjects']is not True:raise RuntimeError('Independent LF checkout proof differs')
  for name,row in rows.items():
   if json.loads(z.read(name+'.result.json'))!=row:raise RuntimeError('Archived passing result differs')
 return prior,rows,changed,sorted(checked)

def bind(repo,record,commit,inputs,work):
 prior,rows,changed,checked=validate(repo,record,commit,inputs);bad=copy.deepcopy(inputs);bad['sdk']['sha256']='0'*64
 try:validate(repo,record,commit,bad)
 except RuntimeError as e:
  if str(e)!='Private value out SDK/dependency identity changed':raise
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
  proof['stages'].append(name);work.state.setdefault('reusedChecks',[]).append(dict(name=name,sourceCommit=SOURCE,record=str(record),archiveSha256=prior['evidenceSha256']));work.save();atomic_json(work.evidence/'private-value-out-reuse.json',proof);atomic_json(work.evidence/(name+'.reused.json'),dict(proof=proof,priorResult=rows[name]));print(json.dumps(dict(stage=name,reused=True,sourceCommit=SOURCE)),flush=True);return rows[name]
 work.run=run
