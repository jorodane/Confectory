"""Reuse sealed identical source checks after the property-guard report argument fix."""
import json
from pathlib import Path
import subprocess
import zipfile
from verification_workspace import atomic_json,sha,verify_archive


def bind(repo,record,commit,inputs,work):
    prior=json.loads(Path(record).read_text());manifest=json.loads(Path(record).with_suffix('.manifest.json').read_text())
    if prior['status']!='cleaned'or sha(prior['evidence'])!=prior['evidenceSha256']or manifest['archiveSha256']!=prior['evidenceSha256']:
        raise RuntimeError('Sealed source verification evidence required')
    verify_archive(prior['evidence'],manifest['files'])
    allowed={'tools/verify_desktop.py','tools/verification_source_reuse.py'}
    changed=subprocess.check_output(['git','diff','--name-only',prior['source'],commit],cwd=repo,text=True).splitlines()
    if any(name not in allowed and not name.startswith('docs/')for name in changed):raise RuntimeError('Product or test inputs changed; execute freshly')
    with zipfile.ZipFile(prior['evidence'])as archive:
        source=json.loads(archive.read('source.json'))
        if source['commit']!=prior['source']or any(source['dependencyInputs'].get(k)!=inputs.get(k)for k in ['sdk','nuget','configuration','rid']):raise RuntimeError('Dependency/configuration identity differs')
        for label,eol in [('lf','false'),('crlf','true')]:
            checkout=json.loads(archive.read(label+'-checkout.json'))
            if checkout['commit']!=prior['source']or checkout['coreAutocrlf']!=eol or checkout['noSharedGitObjects']is not True:raise RuntimeError('Independent checkout/EOL identity differs')
    names={'lf-source-history-runtime','lf-source-api','lf-description-regression','lf-property-source-regression','lf-source-ui-storage-new','lf-source-ui-conflict','lf-source-ui-late','crlf-source-history-runtime','crlf-source-api','crlf-description-regression'}
    rows={row['name']:row for row in prior['results']if row['name']in names and row['exit']==0}
    if set(rows)!=names:raise RuntimeError('All ten exact passing checks required; failed guard never reused')
    proof=dict(previousRecord=str(record),previousSource=prior['source'],sourceCommit=commit,archiveSha256=prior['evidenceSha256'],identicalProductAndTests=True,identicalDependencies=True,buildsAndPackagesReused=False,failedChecksReused=False,stages=[])
    proofPath=work.evidence/'source-reuse.json';atomic_json(proofPath,proof);original=work.run
    def run(name,command,*args,**kwargs):
        if name not in rows:return original(name,command,*args,**kwargs)
        row=rows[name];normalize=lambda values,root:[str(a).replace(root,'$OWNED_WORKSPACE')for a in values]
        if kwargs.get('expected',0)!=0 or normalize(row['command'],prior['root'])!=normalize(command,str(work.root)):raise RuntimeError('Reused invocation differs: '+name)
        proof['stages'].append(name);work.state.setdefault('reusedChecks',[]).append(dict(name=name,sourceCommit=prior['source'],record=str(record),archiveSha256=prior['evidenceSha256']))
        work.save();atomic_json(proofPath,proof);atomic_json(work.evidence/(name+'.reused.json'),dict(proof=proof,priorResult=row));print(json.dumps(dict(stage=name,reused=True,sourceCommit=prior['source'])),flush=True);return row
    work.run=run
