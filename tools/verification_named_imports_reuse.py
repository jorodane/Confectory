"""Guarded passing facts before the conflict-only trusted activation observer.

Only conflict invocation observes new activation events. Builds, packages and restore run fresh.
"""
import ast,copy,json,subprocess,zipfile
from pathlib import Path
from verification_workspace import atomic_json,sha,verify_archive
SOURCE='02e6c4edaf461daa244331847f1686a41ef2bc9d'
NAMES={'lf-named-imports-'+n for n in ['native','normal','storage','loss','guards','api','ref-regression','startup-observation']}|{'crlf-named-imports-native','crlf-named-imports-cancel'}

def validate(repo,record,commit,inputs):
 record=Path(record);prior=json.loads(record.read_text());manifest=json.loads(record.with_suffix('.manifest.json').read_text());blob=lambda rev,n:subprocess.check_output(['git','show',rev+':'+n],cwd=repo,text=True)
 if prior['source']!=SOURCE or prior['status']!='cleaned'or sha(prior['evidence'])!=prior['evidenceSha256']or manifest['archiveSha256']!=prior['evidenceSha256']:raise RuntimeError('Sealed original named-import evidence required')
 verify_archive(prior['evidence'],manifest['files'])
 fixture='tests/web/v666_named_imports.py';allowed={fixture,'tests/web/v666_named_imports_conflict.py','tools/verify_desktop.py','tools/verification_named_imports_reuse.py'};changed=subprocess.check_output(['git','diff','--name-only',SOURCE,commit],cwd=repo,text=True).splitlines()
 if not changed or any(n not in allowed and not n.startswith('docs/')for n in changed):raise RuntimeError('Product or unrelated test drift requires fresh checks')
 before=blob(SOURCE,fixture);after=blob(commit,fixture);old="if check=='ui':";new="if check=='ui'and x.mode=='conflict':runpy.run_path(str(pathlib.Path(__file__).with_name('v666_named_imports_conflict.py')),run_name='__main__')\nelif check=='ui':"
 if before.count(old)!=1 or after.count(new)!=1 or after.replace(new,old)!=before:raise RuntimeError('Runner changed beyond its conflict-only activation observer')
 harness=blob(commit,'tools/verify_desktop.py');argument="    parser.add_argument('--reuse-named-imports',type=Path,help='Exact sealed passing checks before the conflict-only activation observation correction; builds/packages/restore stay fresh')\n";hook="        if args.reuse_named_imports:\n            if args.suite!='named-imports':raise ValueError('Named import reuse requires its own suite')\n            from verification_named_imports_reuse import bind\n            bind(repo,args.reuse_named_imports,commit,inputs,work)\n"
 normalized=harness.replace(argument,'').replace(hook,'').replace(",'verification_named_imports_reuse.py']:","]:")
 if normalized!=blob(SOURCE,'tools/verify_desktop.py'):raise RuntimeError('Harness drift beyond the guarded reuse hook')
 failed=[row for row in prior['results']if row['exit']!=0]
 if len(prior['results'])!=28 or len(failed)!=1 or failed[0]['name']!='crlf-named-imports-conflict':raise RuntimeError('Exact preserved conflict observation failure required')
 rows={row['name']:row for row in prior['results']if row['name']in NAMES and row['exit']==0}
 if set(rows)!=NAMES or len(rows)!=10:raise RuntimeError('All exact ten passing facts required')
 checked=set();pending=[]
 for row in rows.values():
  for arg in row['command']:
   for prefix in ['tests/web/','tests/probes/']:
    if prefix in str(arg)and str(arg).endswith('.py'):pending.append(prefix+str(arg).split(prefix,1)[1])
 while pending:
  name=pending.pop()
  if name in checked:continue
  checked.add(name)
  if name!=fixture and blob(SOURCE,name)!=blob(commit,name):raise RuntimeError('Reused dependency changed')
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
  identity=json.loads(z.read('source.json'));failure=z.read('crlf-named-imports-conflict.log').decode();boundary=json.loads(z.read(next(n for n in z.namelist()if n.endswith('conflict-boundary.json'))))
  if identity['commit']!=SOURCE or any(identity['dependencyInputs'].get(k)!=inputs.get(k)for k in ['sdk','nuget','configuration','rid']):raise RuntimeError('Named import SDK/dependency identity changed')
  if 'Page.wait_for_function: Timeout 30000ms exceeded'not in failure or boundary.get('boundaryMessages')!=['Ready'] or any(row.get('invoke',{}).get('endpoint')=='blueprint'and row['invoke']['input'].get('action')=='applySlots'for row in boundary['traffic']):raise RuntimeError('Different conflict failure cannot be reused')
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
  if str(e)!='Named import SDK/dependency identity changed':raise
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
  proof['stages'].append(name);work.state.setdefault('reusedChecks',[]).append(dict(name=name,sourceCommit=SOURCE,record=str(record),archiveSha256=prior['evidenceSha256']));work.save();atomic_json(work.evidence/'named-imports-reuse.json',proof);atomic_json(work.evidence/(name+'.reused.json'),dict(proof=proof,priorResult=rows[name]));print(json.dumps(dict(stage=name,reused=True,sourceCommit=SOURCE)),flush=True);return rows[name]
 work.run=run
