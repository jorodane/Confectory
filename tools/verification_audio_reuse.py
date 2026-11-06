"""Reuse only exact sealed audio checks after the single package manifest parser fix."""
import copy,json,subprocess,zipfile
from pathlib import Path
from verification_workspace import atomic_json,sha,verify_archive
OLD_PARSE="resources=json.loads(re.search(r'\\n(\\{.*\\})\\n',(content/'examples/editor-home/WebBundle.csbody').read_text()).group(1))"
NEW_PARSE="bundle=(content/'examples/editor-home/WebBundle.csbody').read_text().split('\"\"\"');assert len(bundle)==3;resources=json.loads(bundle[1])"
SUFFIXES={'v536_mixed_declaration','v536_local_header_image','run-audio-copy','run-audio-projection','run-audio-native','run-audio-api-stream','run-audio-api-faults','run-audio-ui','run-resolution-ui','run-surface-faults','run-developer-ui'}
def validate(repo,record,commit,inputs):
 record=Path(record);prior=json.loads(record.read_text());manifest=json.loads(record.with_suffix('.manifest.json').read_text())
 if prior['status']!='cleaned' or sha(prior['evidence'])!=prior['evidenceSha256'] or manifest['archiveSha256']!=prior['evidenceSha256']:raise RuntimeError('Sealed audio evidence required')
 verify_archive(prior['evidence'],manifest['files'])
 changed=subprocess.check_output(['git','diff','--name-only',prior['source'],commit],cwd=repo,text=True).splitlines()
 allowed={'tests/probes/desktop_package.py','tools/verify_desktop.py','tools/verification_audio_reuse.py'}
 if any(p not in allowed and not p.startswith('docs/')for p in changed):raise RuntimeError('Audio product/test inputs changed; execute fresh checks')
 def source(version,path):return subprocess.check_output(['git','show',version+':'+path],cwd=repo,text=True)
 probe='tests/probes/desktop_package.py';old=source(prior['source'],probe);new=source(commit,probe)
 if old.count(OLD_PARSE)!=1 or new!=old.replace(OLD_PARSE,NEW_PARSE):raise RuntimeError('Only the exact package raw-string parser correction is reusable')
 failed=[(r['name'],r['exit'])for r in prior['results']if r['exit']!=0]
 if failed!=[('windows-probe',1)]:raise RuntimeError('Unexpected failure or incomplete audio evidence')
 with zipfile.ZipFile(prior['evidence'])as archive:
  identity=json.loads(archive.read('source.json'))
  if identity['commit']!=prior['source']or any(identity['dependencyInputs'].get(k)!=inputs.get(k)for k in ['sdk','nuget','configuration','rid']):raise RuntimeError('Audio SDK/dependency inputs changed')
  for label,eol in [('lf','false'),('crlf','true')]:
   checkout=json.loads(archive.read(label+'-checkout.json'))
   if checkout['commit']!=prior['source']or checkout['coreAutocrlf']!=eol or checkout['noSharedGitObjects']is not True:raise RuntimeError('Independent audio checkout/EOL identity differs')
  expected={label+'-'+suffix for label in ['lf','crlf']for suffix in SUFFIXES};rows={r['name']:r for r in prior['results']if r['name']in expected and r['exit']==0}
  if set(rows)!=expected:raise RuntimeError('All 22 exact audio checks must be present')
  for name,row in rows.items():
   if json.loads(archive.read(name+'.result.json'))!=row:raise RuntimeError('Archived audio result differs')
 return prior,rows,changed

def bind(repo,record,commit,inputs,work):
 prior,rows,changed=validate(repo,record,commit,inputs)
 # Fail-closed guards are exercised with real sealed evidence and commits.
 bad=copy.deepcopy(inputs);bad['sdk']['sha256']='0'*64
 try:validate(repo,record,commit,bad)
 except RuntimeError as error:
  if str(error)!='Audio SDK/dependency inputs changed':raise
 else:raise RuntimeError('Changed SDK accepted by reuse guard')
 parent=subprocess.check_output(['git','rev-parse',prior['source']+'^'],cwd=repo,text=True).strip()
 try:validate(repo,record,parent,inputs)
 except RuntimeError as error:
  if str(error)!='Audio product/test inputs changed; execute fresh checks':raise
 else:raise RuntimeError('Changed product accepted by reuse guard')
 proof=dict(previousRecord=str(record),previousSource=prior['source'],previousArchive=prior['evidence'],archiveSha256=prior['evidenceSha256'],sourceCommit=commit,identicalProductAndRuntimeTests=True,identicalSDKAndDependencies=True,onlyTestChange='one raw JSON string parser accepts inline or newline-delimited literals; all integrity/assertion checks unchanged',allowedChangedFiles=changed,failedChecksReused=False,buildsAndPackagesReused=False,negativeGuards=['changed SDK rejected','changed product/test rejected'],stages=[])
 atomic_json(work.evidence/'audio-reuse.json',proof);original=work.run
 def run(name,command,*args,**kwargs):
  if name not in rows:return original(name,command,*args,**kwargs)
  row=rows[name];normalize=lambda c,root:[str(arg).replace(root,'$OWNED_WORKSPACE')for arg in c]
  if kwargs.get('expected',0)!=0 or normalize(row['command'],prior['root'])!=normalize(command,str(work.root)):raise RuntimeError('Audio reuse invocation differs: '+name)
  proof['stages'].append(name);work.state.setdefault('reusedChecks',[]).append(dict(name=name,sourceCommit=prior['source'],record=str(record),archiveSha256=prior['evidenceSha256'],kind='exact-audio-check'))
  work.save();atomic_json(work.evidence/'audio-reuse.json',proof);atomic_json(work.evidence/(name+'.reused.json'),dict(proof=proof,priorResult=row));print(json.dumps(dict(stage=name,reused=True,sourceCommit=prior['source'])),flush=True);return row
 work.run=run
