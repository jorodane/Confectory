"""Reuse three passing UI stages after the exact late-source-save count correction."""
import json,subprocess,zipfile
from pathlib import Path
from verification_workspace import atomic_json,sha,verify_archive

def bind(repo,record,commit,inputs,work):
 prior=json.loads(Path(record).read_text());manifest=json.loads(Path(record).with_suffix('.manifest.json').read_text())
 if prior['status']!='cleaned'or sha(prior['evidence'])!=prior['evidenceSha256']or manifest['archiveSha256']!=prior['evidenceSha256']:raise RuntimeError('Durable sealed prior evidence required')
 verify_archive(prior['evidence'],manifest['files'])
 script='tests/web/v666_async_coupled_first_ui.py';allowed={script,'tools/verify_desktop.py','tools/verification_review_reuse.py'}
 def git(*a):return subprocess.check_output(['git',*a],cwd=repo,text=True)
 changed=git('diff','--name-only',prior['source'],commit).splitlines()
 if any(name not in allowed and not name.startswith('docs/')for name in changed):raise RuntimeError('Product or other test inputs changed; no UI reuse')
 before=git('show',prior['source']+':'+script);after=git('show',commit+':'+script);old="(2 if information and mode=='late'else 1)";new="(2 if mode=='late'else 1)"
 if before.count(old)!=1 or after!=before.replace(old,new):raise RuntimeError('Change is not the exact late-input distinct-save count correction')
 with zipfile.ZipFile(prior['evidence'])as z:
  source=json.loads(z.read('source.json'))
  if source['commit']!=prior['source']or any(source['dependencyInputs'].get(k)!=inputs.get(k)for k in ['sdk','nuget','configuration','rid']):raise RuntimeError('Dependency inputs differ')
  for label,eol in [('lf','false'),('crlf','true')]:
   checkout=json.loads(z.read(label+'-checkout.json'))
   if checkout['commit']!=prior['source']or checkout['coreAutocrlf']!=eol or checkout['noSharedGitObjects']is not True:raise RuntimeError('Independent checkout identity differs')
 names={'lf-review-ui','crlf-review-ui','lf-review-task-regression'};rows={r['name']:r for r in prior['results']if r['name']in names and r['exit']==0}
 if set(rows)!=names:raise RuntimeError('Required passing UI evidence missing')
 proof=dict(previousRecord=str(record),previousSource=prior['source'],sourceCommit=commit,archiveSha256=prior['evidenceSha256'],identicalProductAndDependencies=True,onlyTestChange='late private source is a distinct second Save; normal mode count unchanged',failedChecksReused=False,buildsAndPackagesReused=False,stages=[])
 atomic_json(work.evidence/'review-ui-reuse.json',proof);original=work.run
 def run(name,command,*args,**kwargs):
  if name not in rows:return original(name,command,*args,**kwargs)
  row=rows[name];norm=lambda cmd,root:[str(a).replace(root,'$OWNED_WORKSPACE')for a in cmd]
  if kwargs.get('expected',0)!=0 or norm(row['command'],prior['root'])!=norm(command,str(work.root)):raise RuntimeError('UI invocation differs: '+name)
  proof['stages'].append(name);work.state.setdefault('reusedChecks',[]).append(dict(name=name,sourceCommit=prior['source'],record=str(record),archiveSha256=prior['evidenceSha256'],kind='ui'));work.save();atomic_json(work.evidence/'review-ui-reuse.json',proof);atomic_json(work.evidence/(name+'.reused.json'),dict(proof=proof,priorResult=row));print(json.dumps(dict(stage=name,reused=True,sourceCommit=prior['source'])),flush=True);return row
 work.run=run
