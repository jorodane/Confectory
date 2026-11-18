"""Reuse exact sealed source facts after the output pipe closed during packaging.

All clone/build/engine/package/full-restore checks execute freshly. No failed
fact, generated runtime or unverified package is reused.
"""
import copy,json,subprocess,zipfile
from pathlib import Path
from verification_workspace import atomic_json,sha,verify_archive
SOURCE='af90e7addee961226a7999f214d83daf02eceb46'
ARG="    parser.add_argument('--reuse-retained-import-closure',type=Path,help='Sealed identical source checks after output-pipe interruption; builds/packages/restore stay fresh')\n"
HOOK="        if args.reuse_retained_import_closure:\n            if args.suite!='retained-import-closure':raise ValueError('Retained import evidence requires its own suite')\n            from verification_retained_import_reuse import bind\n            bind(repo,args.reuse_retained_import_closure,commit,inputs,work)\n"
MEMBER="'verification_retained_import_reuse.py',"

def validate(repo,record,commit,inputs):
 record=Path(record);prior=json.loads(record.read_text());manifest=json.loads(record.with_suffix('.manifest.json').read_text());blob=lambda rev,n:subprocess.check_output(['git','show',rev+':'+n],cwd=repo,text=True)
 if prior['source']!=SOURCE or prior['status']!='cleaned' or prior.get('error')!='[Errno 32] Broken pipe' or sha(prior['evidence'])!=prior['evidenceSha256'] or manifest['archiveSha256']!=prior['evidenceSha256']:raise RuntimeError('Sealed output-pipe interruption evidence required')
 verify_archive(prior['evidence'],manifest['files'])
 if subprocess.run(['git','merge-base','--is-ancestor',SOURCE,commit],cwd=repo,capture_output=True).returncode:raise RuntimeError('Recovery source ancestry changed')
 driver='tools/verify_desktop.py';helper='tools/verification_retained_import_reuse.py';probe='tests/probes/retained_import_reuse.py';changed=subprocess.check_output(['git','diff','--name-only',SOURCE,commit],cwd=repo,text=True).splitlines()
 if not changed or any(n not in {driver,helper,probe}and not n.startswith('docs/')for n in changed):raise RuntimeError('Product or passing test inputs changed')
 harness=blob(commit,driver)
 if harness.count(ARG)!=1 or harness.count(HOOK)!=1 or harness.count(MEMBER)!=1 or harness.replace(ARG,'').replace(HOOK,'').replace(MEMBER,'')!=blob(SOURCE,driver):raise RuntimeError('Driver routing, budgets or source checks changed')
 if len(prior['results'])!=35 or any(v['exit']!=0 for v in prior['results'])or prior.get('reusedChecks')or prior['results'][-1]['name']!='windows-package':raise RuntimeError('All 34 source/build stages and completed package command required')
 prefixes=('lf-v536_','crlf-v536_','lf-retained-import-closure-','crlf-retained-import-closure-');rows={v['name']:v for v in prior['results']if v['name'].startswith(prefixes)}
 if len(rows)!=22 or sum(n.startswith('lf-')for n in rows)!=15:raise RuntimeError('Exactly 22 passing source facts required')
 with zipfile.ZipFile(prior['evidence'])as z:
  source=json.loads(z.read('source.json'))
  if source['commit']!=SOURCE or any(source['dependencyInputs'].get(k)!=inputs.get(k)for k in ['sdk','nuget','configuration','rid']):raise RuntimeError('Recovery dependency identity changed')
  for label,eol in [('lf','false'),('crlf','true')]:
   checkout=json.loads(z.read(label+'-checkout.json'))
   if checkout['commit']!=SOURCE or checkout['coreAutocrlf']!=eol or checkout['noSharedGitObjects']is not True:raise RuntimeError('Independent checkout/EOL identity changed')
  for name,row in rows.items():
   if json.loads(z.read(name+'.result.json'))!=row:raise RuntimeError('Archived passing result differs')
 return prior,rows,changed

def same_invocation(row,command,old_root,new_root,expected=0):
 normalize=lambda cmd,root:[str(v).replace(root,'$OWNED_WORKSPACE')for v in cmd]
 if expected!=0 or normalize(row['command'],old_root)!=normalize(command,new_root):raise RuntimeError('Reused invocation differs')

def bind(repo,record,commit,inputs,work):
 prior,rows,changed=validate(repo,record,commit,inputs);proof=dict(previousRecord=str(record),previousSource=SOURCE,sourceCommit=commit,archiveSha256=prior['evidenceSha256'],identicalProductAndPassingTests=True,allowedChangedFiles=changed,failedChecksReused=False,buildsPackagesRestoreReused=False,stages=[]);original=work.run
 atomic_json(work.evidence/'retained-import-reuse.json',proof)
 def run(name,command,*args,**kwargs):
  if name not in rows:return original(name,command,*args,**kwargs)
  same_invocation(rows[name],command,prior['root'],str(work.root),kwargs.get('expected',0))
  if name in proof['stages']:raise RuntimeError('Reused invocation repeats')
  proof['stages'].append(name);work.state.setdefault('reusedChecks',[]).append(dict(name=name,sourceCommit=SOURCE,record=str(record),archiveSha256=prior['evidenceSha256']));work.save();atomic_json(work.evidence/'retained-import-reuse.json',proof);atomic_json(work.evidence/(name+'.reused.json'),dict(proof=proof,priorResult=rows[name]));print(json.dumps(dict(stage=name,reused=True,sourceCommit=SOURCE)),flush=True);return rows[name]
 work.run=run
