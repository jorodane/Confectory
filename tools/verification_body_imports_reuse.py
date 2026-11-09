"""Reuse sealed source-checkout evidence after one exact script-relative package path fix."""
import json,subprocess,zipfile
from pathlib import Path
from verification_workspace import atomic_json,sha,verify_archive

def bind(repo,record,commit,inputs,work):
 prior=json.loads(Path(record).read_text());manifest=json.loads(Path(record).with_suffix('.manifest.json').read_text())
 if prior['status']!='cleaned' or sha(prior['evidence'])!=prior['evidenceSha256'] or manifest['archiveSha256']!=prior['evidenceSha256']:raise RuntimeError('Sealed body import evidence required')
 verify_archive(prior['evidence'],manifest['files'])
 changed=subprocess.check_output(['git','diff','--name-only',prior['source'],commit],cwd=repo,text=True).splitlines();script='tests/web/v666_body_imports_ui.py';allowed={script,'tools/verify_desktop.py','tools/verification_body_imports_reuse.py'}
 if any(n not in allowed and not n.startswith('docs/')for n in changed):raise RuntimeError('Product or other tests changed; run fresh')
 blob=lambda source,name:subprocess.check_output(['git','show',source+':'+name],cwd=repo,text=True)
 before="x.f.repo/'tests/web/v536_information_shared_return_types_ui.py'";after="pathlib.Path(__file__).with_name('v536_information_shared_return_types_ui.py')";old=blob(prior['source'],script);new=blob(commit,script)
 if old.count(before)!=1 or old.replace('import os,runpy,sys','import os,runpy,sys,pathlib').replace(before,after)!=new:raise RuntimeError('Only the exact helper path correction is reusable')
 product=json.loads(blob(commit,'docs/v666-body-imports-delta.json'))['productFiles']
 if any(blob(prior['source'],n)!=blob(commit,n)for n in product):raise RuntimeError('Body import product drift')
 with zipfile.ZipFile(prior['evidence'])as z:
  source=json.loads(z.read('source.json'));checkouts={label:json.loads(z.read(label+'-checkout.json'))for label in ['lf','crlf']}
  if any(source['dependencyInputs'].get(k)!=inputs.get(k)for k in ['sdk','nuget','configuration','rid']):raise RuntimeError('Dependency/configuration drift')
  for label,eol in [('lf','false'),('crlf','true')]:
   row=checkouts[label]
   if row['commit']!=prior['source']or row['coreAutocrlf']!=eol or row['noSharedGitObjects']is not True:raise RuntimeError('Independent EOL evidence differs')
  failure=z.read('packaged-body-imports-normal.log').decode()
  if 'FileNotFoundError'not in failure or '/content/tests/web/v536_information_shared_return_types_ui.py'not in failure:raise RuntimeError('Different failure requires fresh checks')
 failed=[r for r in prior['results']if r['exit']!=0]
 if len(prior['results'])!=34 or len(failed)!=1 or failed[0]['name']!='packaged-body-imports-normal':raise RuntimeError('Exact prior outcome required')
 lf={'lf-'+n for n in ['v536_mixed_declaration','v536_local_header_image','body-imports-boundary','body-imports-native','body-imports-admission','body-imports-guards','body-imports-dependencies','body-imports-normal','body-imports-storage']};crlf={r['name']for r in prior['results']if r['name'].startswith('crlf-')};names=lf|crlf|{'body-imports-owned-ipc-lifetime'}
 rows={r['name']:r for r in prior['results']if r['name']in names and r['exit']==0}
 if len(crlf)!=15 or len(names)!=25 or set(rows)!=names:raise RuntimeError('All exact passing checks required')
 proof=dict(previousRecord=str(record),previousSource=prior['source'],sourceCommit=commit,archiveSha256=prior['evidenceSha256'],identicalProductAndDependencies=True,allowedChangedFiles=changed,sourceCheckoutHelperResolvesIdentically=True,failedChecksReused=False,packagesReused=False,independentCheckouts=checkouts,stages=[]);proofPath=work.evidence/'body-imports-reuse.json'
 def retain(name):
  if any(r['name']==name for r in work.state.get('reusedChecks',[])):raise RuntimeError('Duplicate reuse')
  proof['stages'].append(name);work.state.setdefault('reusedChecks',[]).append(dict(name=name,sourceCommit=prior['source'],record=str(record),archiveSha256=prior['evidenceSha256']));work.save();atomic_json(proofPath,proof);atomic_json(work.evidence/(name+'.reused.json'),dict(proof=proof,priorResult=rows[name]));print(json.dumps(dict(stage=name,reused=True,sourceCommit=prior['source'])),flush=True);return rows[name]
 for name in sorted(crlf):retain(name)
 original=work.run
 def run(name,command,*args,**kwargs):
  if name not in rows:return original(name,command,*args,**kwargs)
  norm=lambda cmd,root:[str(a).replace(root,'$OWNED_WORKSPACE')for a in cmd]
  if kwargs.get('expected',0)!=0 or norm(rows[name]['command'],prior['root'])!=norm(command,str(work.root)):raise RuntimeError('Reused invocation differs: '+name)
  return retain(name)
 work.run=run
