"""Reuse only sealed, byte-identical non-browser checks after a UI recovery fix."""
import json
from pathlib import Path
import re
import subprocess
import zipfile

from verification_workspace import atomic_json, sha, verify_archive


def bind(repo, record, commit, inputs, work):
    prior = json.loads(Path(record).read_text())
    manifest = json.loads(Path(record).with_suffix('.manifest.json').read_text())
    if prior['status'] != 'cleaned' or sha(prior['evidence']) != prior['evidenceSha256'] or manifest['archiveSha256'] != prior['evidenceSha256']:
        raise RuntimeError('Completed durable evidence required for reuse')
    verify_archive(prior['evidence'], manifest['files'])
    allowed = {
        'examples/editor-home/ui/feature-authoring.js',
        'examples/editor-home/WebBundle.csbody',
        'tests/web/v666_completion_recovery.mjs',
        'tools/verify_desktop.py', 'tools/verification_coupled_reuse.py',
    }
    changed = subprocess.check_output(['git','diff','--name-only',prior['source'],commit],cwd=repo,text=True).splitlines()
    if any(name not in allowed and not name.startswith('docs/') for name in changed):
        raise RuntimeError('Backend/test/build inputs changed; execute them freshly')
    bundle = 'examples/editor-home/WebBundle.csbody'
    def descriptor(version):
        text = subprocess.check_output(['git','show',version+':'+bundle],cwd=repo,text=True)
        return re.sub(r'"canonicalSize":\d+,"canonicalSha256":"[a-f0-9]{64}"',
                      '"canonicalSize":0,"canonicalSha256":"PINNED_RESOURCE"',text)
    if descriptor(prior['source']) != descriptor(commit):
        raise RuntimeError('Bundle behavior/endpoints changed; execute backend checks freshly')
    with zipfile.ZipFile(prior['evidence']) as archive:
        source = json.loads(archive.read('source.json'))
        old_inputs = source['dependencyInputs']
        if source['commit'] != prior['source'] or any(old_inputs.get(k) != inputs.get(k) for k in ['sdk','nuget','configuration','rid']):
            raise RuntimeError('SDK/dependency/configuration identity differs')
        for label, crlf in [('lf','false'),('crlf','true')]:
            checkout = json.loads(archive.read(label+'-checkout.json'))
            if checkout['commit'] != prior['source'] or checkout['coreAutocrlf'] != crlf or checkout['noSharedGitObjects'] is not True:
                raise RuntimeError('Prior independent checkout/EOL identity differs')
    suffixes = {
        'coupled-runtime', 'information-guards', 'private-guards',
        'global-guards', 'global-templates', 'declaration-restore',
        'coupled-global-api', 'coupled-information-api',
        'coupled-private-api', 'coupled-new-node-api',
        'private-returns-regression', 'async-receipt-guards',
        'coupled-final-read-cas',
    }
    rows = {r['name']:r for r in prior['results'] if r['exit'] == 0 and
            any(r['name'] == label+'-'+suffix for label in ['lf','crlf'] for suffix in suffixes)}
    proof = dict(previousRecord=str(record), previousSource=prior['source'], sourceCommit=commit,
                 previousArchive=prior['evidence'], archiveSha256=prior['evidenceSha256'],
                 allowedChangedFiles=changed, identicalBackendAndTestBlobs=True,
                 identicalSdkNugetAndConfiguration=True, browserChecksReused=False, stages=[])
    atomic_json(work.evidence/'backend-reuse.json',proof)
    original = work.run

    def run(name, command, *args, **kwargs):
        if name not in rows:
            return original(name,command,*args,**kwargs)
        row = rows[name]
        if kwargs.get('expected',0) != 0:
            raise RuntimeError('Reused check expected outcome differs: '+name)
        normalized = lambda command, root: [str(arg).replace(root,'$OWNED_WORKSPACE') for arg in command]
        if normalized(row['command'],prior['root']) != normalized(command,str(work.root)):
            raise RuntimeError('Reused check invocation differs: '+name)
        proof['stages'].append(name)
        work.state.setdefault('reusedChecks',[]).append(dict(name=name,sourceCommit=prior['source'],record=str(record),archiveSha256=prior['evidenceSha256']))
        work.save(); atomic_json(work.evidence/'backend-reuse.json',proof)
        atomic_json(work.evidence/(name+'.reused.json'),dict(proof=proof,priorResult=row))
        print(json.dumps(dict(stage=name,reused=True,sourceCommit=prior['source'])),flush=True)
        return row

    work.run = run
