"""Bounded reuse after correcting a package-only failure-injection target.

No product or reused test changes are allowed. Every clone/build/engine/package
and full package restore executes freshly. Failed facts are never reused.
"""
import copy,json,subprocess,zipfile
from pathlib import Path
from verification_workspace import atomic_json,sha,verify_archive
SOURCE='ee8a327ded9410c2564d7f5a118024bf1c0423a5'
PAIRS=[('        def failed_screenshot(page, *args, **kwargs):\n            screenshot(page, *args, **kwargs)\n            raise RuntimeError("isolated UI assertion after screenshot")\n', '        def failed_screenshot(page, *args, **kwargs):\n            result = screenshot(page, *args, **kwargs)\n            target = Path(kwargs.get("path") or "")\n            if target.name == "packaged-login.png":\n                assert target.is_file()\n                (target.parent / "ui-failure-injection.json").write_text(json.dumps({\n                    "target": target.name, "afterScreenshotWritten": True,\n                    "diagnosticScreenshotsUnaffected": True,\n                }, indent=2) + "\\n")\n                raise RuntimeError("isolated UI assertion after screenshot")\n            return result\n'), ('        assert {p.relative_to(package) for p in package.rglob("*") if p.is_file()} == set(files)\n', '        if mode == "ui-failure":\n            assert json.loads((fixture / "ui-failure-injection.json").read_text()) == {\n                "target": "packaged-login.png", "afterScreenshotWritten": True,\n                "diagnosticScreenshotsUnaffected": True,\n            }\n            assert json.loads((fixture / "package-login-readiness.json").read_text())["passed"] is True\n        assert {p.relative_to(package) for p in package.rglob("*") if p.is_file()} == set(files)\n')]
ARG="    parser.add_argument('--reuse-private-out-narrow',type=Path,help='Sealed identical LF/CRLF facts after final-screenshot fault injection correction; builds/packages/restore stay fresh')\n"
HOOK="        if args.reuse_private_out_narrow:\n            if args.suite!='private-node-out-narrow':raise ValueError('Private out narrowing evidence requires its own suite')\n            from verification_private_out_narrow_reuse import bind\n            bind(repo,args.reuse_private_out_narrow,commit,inputs,work)\n"

def validate(repo,record,commit,inputs):
 record=Path(record);prior=json.loads(record.read_text());manifest=json.loads(record.with_suffix('.manifest.json').read_text());blob=lambda rev,n:subprocess.check_output(['git','show',rev+':'+n],cwd=repo,text=True)
 if prior['source']!=SOURCE or prior['status']!='cleaned' or sha(prior['evidence'])!=prior['evidenceSha256'] or manifest['archiveSha256']!=prior['evidenceSha256']:raise RuntimeError('Sealed original narrowing evidence required')
 verify_archive(prior['evidence'],manifest['files'])
 subprocess.run(['git','merge-base','--is-ancestor',SOURCE,commit],cwd=repo,check=True)
 script='tests/probes/desktop_package_lifetime.py';driver='tools/verify_desktop.py';helper='tools/verification_private_out_narrow_reuse.py';changed=subprocess.check_output(['git','diff','--name-only',SOURCE,commit],cwd=repo,text=True).splitlines()
 if not changed or any(n not in {script,driver,helper} and not n.startswith('docs/')for n in changed):raise RuntimeError('Product or unrelated test inputs changed')
 fixed=blob(SOURCE,script)
 for before,after in PAIRS:
  if fixed.count(before)!=1:raise RuntimeError('Original failure injector differs')
  fixed=fixed.replace(before,after)
 if blob(commit,script)!=fixed:raise RuntimeError('Package lifetime checks changed beyond the final screenshot target and proof')
 harness=blob(commit,driver)
 if harness.count(ARG)!=1 or harness.count(HOOK)!=1 or harness.count("'verification_private_out_narrow_reuse.py',")!=1:raise RuntimeError('Reuse hook differs')
 if harness.replace(ARG,'').replace(HOOK,'').replace("'verification_private_out_narrow_reuse.py',",'')!=blob(SOURCE,driver):raise RuntimeError('Driver routing, budgets or checks changed')
 failed=[v['name']for v in prior['results']if v['exit']!=0]
 if len(prior['results'])!=48 or failed!=['package-failure-lifetime'] or prior.get('reusedChecks'):raise RuntimeError('Exact original 47-pass package injection failure required')
 prefixes=('lf-v536_','crlf-v536_','lf-private-node-out-narrow-','crlf-private-node-out-narrow-');rows={v['name']:v for v in prior['results']if v['exit']==0 and v['name'].startswith(prefixes)}
 if len(rows)!=27 or sum(n.startswith('lf-')for n in rows)!=20:raise RuntimeError('All 27 unchanged source-test facts required')
 with zipfile.ZipFile(prior['evidence'])as z:
  source=json.loads(z.read('source.json'))
  if source['commit']!=SOURCE or any(source['dependencyInputs'].get(k)!=inputs.get(k)for k in ['sdk','nuget','configuration','rid']):raise RuntimeError('Narrowing SDK or dependency identity changed')
  failure=z.read('package-failure-lifetime.log').decode()
  if 'START ui-failure'not in failure or 'packaged-login.png'not in failure or 'AssertionError'not in failure:raise RuntimeError('Different package lifetime failure')
  logs=[n for n in z.namelist()if '/ui-failure/'in n and n.endswith('/probe.log')]
  if len(logs)!=1:raise RuntimeError('Original injection log required')
  log=z.read(logs[0]).decode()
  if 'packaged-login-after-5s.png'not in log or 'isolated UI assertion after screenshot'not in log:raise RuntimeError('Original diagnostic screenshot injection required')
  cleanup=json.loads(z.read(next(n for n in z.namelist()if '/ui-failure/'in n and n.endswith('/copy-cleanup.json'))))
  if not cleanup['cleanupSucceeded'] or cleanup['operationErrorType']!='RuntimeError' or not all(v['removed']for v in cleanup['copies']):raise RuntimeError('Original failed copy cleanup unproven')
  for label,eol in [('lf','false'),('crlf','true')]:
   checkout=json.loads(z.read(label+'-checkout.json'))
   if checkout['commit']!=SOURCE or checkout['coreAutocrlf']!=eol or checkout['noSharedGitObjects']is not True:raise RuntimeError('Independent source/EOL facts differ')
  for name,row in rows.items():
   if json.loads(z.read(name+'.result.json'))!=row:raise RuntimeError('Archived passing result differs')
 return prior,rows,changed

def bind(repo,record,commit,inputs,work):
 prior,rows,changed=validate(repo,record,commit,inputs);bad=copy.deepcopy(inputs);bad['sdk']['sha256']='0'*64
 try:validate(repo,record,commit,bad)
 except RuntimeError as error:
  if str(error)!='Narrowing SDK or dependency identity changed':raise
 else:raise RuntimeError('Changed SDK accepted')
 proof=dict(previousRecord=str(record),previousSource=SOURCE,sourceCommit=commit,archiveSha256=prior['evidenceSha256'],identicalProductAndPassingTests=True,allowedChangedFiles=changed,failedChecksReused=False,buildsPackagesRestoreReused=False,negativeGuards=['changed SDK rejected'],stages=[]);original=work.run
 atomic_json(work.evidence/'private-out-narrow-reuse.json',proof)
 def run(name,command,*args,**kwargs):
  if name not in rows:return original(name,command,*args,**kwargs)
  normalize=lambda cmd,root:[str(v).replace(root,'$OWNED_WORKSPACE')for v in cmd]
  if kwargs.get('expected',0)!=0 or normalize(rows[name]['command'],prior['root'])!=normalize(command,str(work.root)) or name in proof['stages']:raise RuntimeError('Reused invocation differs or repeats: '+name)
  proof['stages'].append(name);work.state.setdefault('reusedChecks',[]).append(dict(name=name,sourceCommit=SOURCE,record=str(record),archiveSha256=prior['evidenceSha256']));work.save();atomic_json(work.evidence/'private-out-narrow-reuse.json',proof);atomic_json(work.evidence/(name+'.reused.json'),dict(proof=proof,priorResult=rows[name]));print(json.dumps(dict(stage=name,reused=True,sourceCommit=SOURCE)),flush=True);return rows[name]
 work.run=run
