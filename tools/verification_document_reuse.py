"""Keep four sealed LF UI results after the exact legacy-entry wait correction.

All runtime/product files and the four executed test inputs must be identical.
Builds, the failed legacy check, CRLF, packages and restore always execute fresh.
"""
import json,subprocess,zipfile
from pathlib import Path
from verification_workspace import atomic_json,sha,verify_archive

def bind(repo,record,commit,inputs,work):
 prior=json.loads(Path(record).read_text());manifest=json.loads(Path(record).with_suffix('.manifest.json').read_text())
 if prior['status']!='cleaned' or sha(prior['evidence'])!=prior['evidenceSha256'] or manifest['archiveSha256']!=prior['evidenceSha256']:raise RuntimeError('Sealed document evidence required')
 verify_archive(prior['evidence'],manifest['files'])
 def git(*args):return subprocess.check_output(['git',*args],cwd=repo,text=True)
 adapter='tests/web/v666_async_transition_ui.py'
 allowed={adapter,'tools/verification_document_reuse.py','tools/verify_document_cells.py'}
 if not set(git('diff','--name-only',prior['source'],commit).splitlines())<=allowed:raise RuntimeError('Product, passing test or fixture drift; execute fresh')
 before=git('show',prior['source']+':'+adapter);after=git('show',commit+':'+adapter)
 old="f.page.locator('[data-operation=feature-author-open]').first.click();tab=panel().get_by_role"
 new="f.page.locator('[data-operation=feature-author-open]').first.click();panel().locator('[data-bp-node=\"'+node+'\"]').wait_for(state='attached');tab=panel().get_by_role"
 if before.count(old)!=1 or after!=before.replace(old,new):raise RuntimeError('Only exact legacy attachment wait correction is allowed')
 expected=['lf-'+s for s in ['clone','checkout','restore','release','mcp','engine','document-controlled','document-normal','document-storage','document-branches','legacy-node-names']]
 if [r['name']for r in prior['results']]!=expected or any(r['exit']!=0 for r in prior['results'][:-1])or prior['results'][-1]['exit']!=1:raise RuntimeError('Different prior outcome')
 with zipfile.ZipFile(prior['evidence'])as z:
  deps=json.loads(z.read('dependencies.json'));checkout=json.loads(z.read('lf-checkout.json'))
  if any(deps[k]!=inputs[k]for k in ['sdk','nuget','configuration','rid']):raise RuntimeError('Public dependency inputs changed')
  if checkout['commit']!=prior['source']or checkout['coreAutocrlf']!='false'or checkout['noSharedGitObjects']is not True:raise RuntimeError('LF checkout proof differs')
  failure=z.read('lf-legacy-node-names.log').decode()
  if 'Locator expected to be visible'not in failure or 'unexpected value "hidden"'not in failure or '논리 코드" [selected]'not in failure:raise RuntimeError('Different failed boundary')
 names=set(expected[6:10]);rows={r['name']:r for r in prior['results']if r['name']in names}
 proof=dict(previousRecord=str(record),previousSource=prior['source'],sourceCommit=commit,archiveSha256=prior['evidenceSha256'],identicalProductTestsFixturesAndDependencies=True,failedChecksReused=False,buildsAndPackagesReused=False,stages=[])
 original=work.run
 def run(name,command,*args,**kwargs):
  if name not in rows:return original(name,command,*args,**kwargs)
  row=rows[name];normalize=lambda cmd,root:[str(v).replace(root,'$OWNED_WORKSPACE')for v in cmd]
  if name in proof['stages']or kwargs.get('expected',0)!=0 or normalize(row['command'],prior['root'])!=normalize(command,str(work.root)):raise RuntimeError('Reused invocation differs or repeats')
  proof['stages'].append(name);work.state.setdefault('reusedChecks',[]).append(dict(name=name,sourceCommit=prior['source'],record=str(record),archiveSha256=prior['evidenceSha256']))
  work.save();atomic_json(work.evidence/'document-reuse.json',proof);atomic_json(work.evidence/(name+'.reused.json'),dict(proof=proof,priorResult=row));print(json.dumps(dict(stage=name,reused=True,sourceCommit=prior['source'])),flush=True);return row
 work.run=run
