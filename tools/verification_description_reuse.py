"""Reuse four sealed LF checks only after the bounded description Review fixture fix."""
import json
from pathlib import Path
import subprocess
import zipfile
from verification_workspace import atomic_json,sha,verify_archive


def bind(repo,record,commit,inputs,work):
    prior=json.loads(Path(record).read_text());manifest=json.loads(Path(record).with_suffix('.manifest.json').read_text())
    if prior['status']!='cleaned' or sha(prior['evidence'])!=prior['evidenceSha256'] or manifest['archiveSha256']!=prior['evidenceSha256']:
        raise RuntimeError('Sealed description evidence required')
    verify_archive(prior['evidence'],manifest['files'])
    script='tests/web/v666_description_recovery_ui.py'
    allowed={script,'tools/verify_desktop.py','tools/verification_description_reuse.py'}
    changed=subprocess.check_output(['git','diff','--name-only',prior['source'],commit],cwd=repo,text=True).splitlines()
    if any(name not in allowed and not name.startswith('docs/')for name in changed):
        raise RuntimeError('Product or other test inputs changed; execute freshly')
    old=subprocess.check_output(['git','show',prior['source']+':'+script],cwd=repo,text=True)
    new=subprocess.check_output(['git','show',commit+':'+script],cwd=repo,text=True)
    before=" if r.locator('[data-review-advanced]').is_visible():r.locator('[data-review-advanced]').click();r.locator('[data-advanced-reviewed]').check()"
    after=" if r.locator('[data-review-advanced]').is_visible():r.locator('[data-review-advanced]').click()\n if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()"
    if old.count(before)!=1 or old.replace(before,after)!=new:
        raise RuntimeError('Only the optional Review acknowledgement fixture correction is reusable')
    with zipfile.ZipFile(prior['evidence'])as archive:
        source=json.loads(archive.read('source.json'));checkout=json.loads(archive.read('lf-checkout.json'))
        if source['commit']!=prior['source'] or any(source['dependencyInputs'].get(k)!=inputs.get(k)for k in ['sdk','nuget','configuration','rid']):
            raise RuntimeError('Dependency/configuration identity differs')
        if checkout['commit']!=prior['source']or checkout['coreAutocrlf']!='false'or checkout['noSharedGitObjects']is not True:
            raise RuntimeError('Independent LF identity differs')
    names={'lf-description-history-runtime','lf-description-api','lf-value-regression','lf-description-node-storage-new'}
    rows={r['name']:r for r in prior['results']if r['name']in names and r['exit']==0}
    if set(rows)!=names:raise RuntimeError('All four passing LF checks required; failures never reused')
    proof=dict(previousRecord=str(record),previousSource=prior['source'],sourceCommit=commit,
        archiveSha256=prior['evidenceSha256'],identicalProductAndDependencies=True,
        onlyUiChange='Check optional acknowledgement only when rendered. The passed node path already checked it; failed function path runs fresh.',
        buildsAndPackagesReused=False,failedChecksReused=False,stages=[])
    atomic_json(work.evidence/'description-reuse.json',proof);original=work.run
    def run(name,command,*args,**kwargs):
        if name not in rows:return original(name,command,*args,**kwargs)
        row=rows[name];normalize=lambda command,root:[str(a).replace(root,'$OWNED_WORKSPACE')for a in command]
        if kwargs.get('expected',0)!=0 or normalize(row['command'],prior['root'])!=normalize(command,str(work.root)):
            raise RuntimeError('Reused invocation differs: '+name)
        proof['stages'].append(name);work.state.setdefault('reusedChecks',[]).append(dict(name=name,sourceCommit=prior['source'],record=str(record),archiveSha256=prior['evidenceSha256']))
        work.save();atomic_json(work.evidence/'description-reuse.json',proof);atomic_json(work.evidence/(name+'.reused.json'),dict(proof=proof,priorResult=row))
        print(json.dumps(dict(stage=name,reused=True,sourceCommit=prior['source'])),flush=True);return row
    work.run=run
