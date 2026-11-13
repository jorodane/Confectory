"""Bounded reuse after migrating the former new-child rejection to a positive check.

Product and all reused tests are byte-identical; builds, changed/failed checks,
CRLF, packages and restoration always run fresh.
"""
import ast,copy,hashlib,json,subprocess,zipfile
from pathlib import Path
from verification_workspace import atomic_json,sha,verify_archive
SOURCE='abe8a0c268158537b0e77a80af090d3cd6b6d621'
ARCHIVE='2699cf2059d01681e7ae5f2b2d787dd2c80468fba64801574db8378a730260c8'
TEST='tests/web/v666_owned_structure.py'
TEST_SHA='6bd5ceddaa7825e11db6c23600a825471f7e379acdbe5d0d92831e96f38df37d'
NAMES={'lf-owned-creation-'+n for n in ['standalone-owned','native','normal','view','storage','guards','api','same-contract','owned-followup','extension-native','extension-normal','extension-guards','extension-late','extension-api']}
ARG="    parser.add_argument('--reuse-owned-creation',type=Path,help='Fourteen sealed unchanged creation checks after migrating the prior new-child rejection; builds/failed checks/CRLF/packages/restore fresh')\n"
HOOK="        if args.reuse_owned_creation:\n            if args.suite!='owned-creation':raise ValueError('Owned creation reuse requires its own suite')\n            from verification_owned_creation_reuse import bind\n            bind(repo,args.reuse_owned_creation,commit,inputs,work)\n"

def validate(repo,record,commit,inputs):
 record=Path(record);prior=json.loads(record.read_text());manifest=json.loads(record.with_suffix('.manifest.json').read_text());blob=lambda rev,n:subprocess.check_output(['git','show',rev+':'+n],cwd=repo)
 if prior['source']!=SOURCE or prior['status']!='cleaned'or prior['evidenceSha256']!=ARCHIVE or sha(prior['evidence'])!=ARCHIVE or manifest['archiveSha256']!=ARCHIVE:raise RuntimeError('Exact sealed owned creation evidence required')
 verify_archive(prior['evidence'],manifest['files'])
 allowed={TEST,'tools/verify_desktop.py','tools/verification_owned_creation_reuse.py'};changed=subprocess.check_output(['git','diff','--name-only',SOURCE,commit],cwd=repo,text=True).splitlines()
 if not changed or any(n not in allowed and not n.startswith('docs/')for n in changed):raise RuntimeError('Product or unrelated test drift requires fresh checks')
 if hashlib.sha256(blob(commit,TEST)).hexdigest()!=TEST_SHA:raise RuntimeError('Different structure regression correction requires fresh checks')
 harness=blob(commit,'tools/verify_desktop.py').decode();normalized=harness.replace(ARG,'').replace(HOOK,'').replace(",'verification_owned_creation_reuse.py']:","]:")
 if normalized.encode()!=blob(SOURCE,'tools/verify_desktop.py'):raise RuntimeError('Harness drift beyond the bounded reuse hook')
 failed=[row for row in prior['results']if row['exit']!=0]
 if len(prior['results'])!=23 or len(failed)!=1 or failed[0]['name']!='lf-owned-creation-previous-structure':raise RuntimeError('Exact preserved obsolete rejection failure required')
 rows={row['name']:row for row in prior['results']if row['name']in NAMES and row['exit']==0}
 if set(rows)!=NAMES or len(rows)!=14:raise RuntimeError('All fourteen original passing facts required')
 checked=set();pending=[]
 for row in rows.values():
  for arg in row['command']:
   for prefix in ['tests/web/','tests/probes/']:
    if prefix in str(arg)and str(arg).endswith('.py'):pending.append(prefix+str(arg).split(prefix,1)[1])
 while pending:
  name=pending.pop()
  if name in checked:continue
  checked.add(name)
  if name==TEST or blob(SOURCE,name)!=blob(commit,name):raise RuntimeError('Reused check dependency changed')
  for node in ast.walk(ast.parse(blob(SOURCE,name).decode())):
   imports=[n.name for n in node.names]if isinstance(node,ast.Import)else[node.module]if isinstance(node,ast.ImportFrom)and node.module else[]
   if isinstance(node,ast.Constant)and isinstance(node.value,str):
    value=node.value
    if value.endswith('.py'):imports.append(value[:-3])
    elif value.startswith(('v536_','v666_')):imports.append(value)
   for module in imports:
    for candidate in [Path(name).parent/(module.split('.')[0]+'.py'),Path('tools')/(module.split('.')[0]+'.py')]:
     if(repo/candidate).is_file():pending.append(candidate.as_posix())
 with zipfile.ZipFile(prior['evidence'])as z:
  identity=json.loads(z.read('source.json'));failure=z.read('lf-owned-creation-previous-structure.log').decode();faults=[json.loads(z.read(n))for n in z.namelist()if n.endswith('current-rejection.json')]
  if identity['commit']!=SOURCE or any(identity['dependencyInputs'].get(k)!=inputs.get(k)for k in ['sdk','nuget','configuration','rid']):raise RuntimeError('Owned creation SDK/dependency identity changed')
  if 'AssertionError:'not in failure or "'ok': True"not in failure or not any(row.get('fault')=='new-child'for row in faults):raise RuntimeError('Different failure cannot be reused')
  checkout=json.loads(z.read('lf-checkout.json'))
  if checkout['commit']!=SOURCE or checkout['coreAutocrlf']!='false'or checkout['noSharedGitObjects']is not True:raise RuntimeError('Independent LF checkout proof differs')
  for name,row in rows.items():
   if json.loads(z.read(name+'.result.json'))!=row:raise RuntimeError('Archived passing result differs')
 return prior,rows,changed,sorted(checked)

def bind(repo,record,commit,inputs,work):
 prior,rows,changed,checked=validate(repo,record,commit,inputs);bad=copy.deepcopy(inputs);bad['sdk']['sha256']='0'*64
 try:validate(repo,record,commit,bad)
 except RuntimeError as e:
  if str(e)!='Owned creation SDK/dependency identity changed':raise
 else:raise RuntimeError('Changed SDK accepted')
 parent=subprocess.check_output(['git','rev-parse',SOURCE+'^'],cwd=repo,text=True).strip()
 try:validate(repo,record,parent,inputs)
 except RuntimeError as e:
  if str(e)!='Product or unrelated test drift requires fresh checks':raise
 else:raise RuntimeError('Changed product accepted')
 proof=dict(previousRecord=str(record),previousSource=SOURCE,sourceCommit=commit,archiveSha256=ARCHIVE,identicalProductAndPassingImportClosure=True,checkedPythonDependencies=checked,allowedChangedFiles=changed,failedOrChangedChecksReused=False,buildsPackagesRestoreReused=False,negativeGuards=['changed SDK rejected','changed product rejected'],stages=[]);original=work.run
 def run(name,command,*args,**kwargs):
  if name not in rows:return original(name,command,*args,**kwargs)
  normalize=lambda cmd,root:[str(arg).replace(root,'$OWNED_WORKSPACE')for arg in cmd]
  if kwargs.get('expected',0)!=0 or normalize(rows[name]['command'],prior['root'])!=normalize(command,str(work.root))or name in proof['stages']:raise RuntimeError('Reused command differs or repeats: '+name)
  proof['stages'].append(name);work.state.setdefault('reusedChecks',[]).append(dict(name=name,sourceCommit=SOURCE,record=str(record),archiveSha256=ARCHIVE));work.save();atomic_json(work.evidence/'owned-creation-reuse.json',proof);atomic_json(work.evidence/(name+'.reused.json'),dict(proof=proof,priorResult=rows[name]));print(json.dumps(dict(stage=name,reused=True,sourceCommit=SOURCE)),flush=True);return rows[name]
 work.run=run
