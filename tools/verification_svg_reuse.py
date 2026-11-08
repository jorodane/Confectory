"""Reuse only sealed SVG checks after the exact package-suite routing correction.

Product, tests, SDK, dependency seed and normalized invocation must be identical.
Failed checks and all regenerable builds/packages are always fresh.
"""
import copy,hashlib,json,subprocess,zipfile
from pathlib import Path
from verification_workspace import atomic_json,sha,verify_archive
OLD_TOOLS='dbc42aa060d8bedeed04a2244ebcbc4e8a8dd0f075d8d9bffc8e0acd12b8795d'
NEW_TOOLS='eaa78119367f33127dd8001a3e52e0e2de9a05fc01e8ee3a4a93630f27713988'
ROUTING_PROBE='3f7ba666bc38f60dd3aff0f8da6bdce0297cd5be68ce62603c42cd2028336492'
SUFFIXES={'v536_mixed_declaration','v536_local_header_image','resource-svg-boundary','resource-avif-metadata','resource-gif-metadata','resource-images-metadata','resource-webp-metadata','resource-bmp-metadata','resource-svg-dom','resource-avif-dom','resource-gif-dom','resource-webp-dom','resource-bmp-dom','web-resource-contract','resource-svg-ui','resource-avif-ui','resource-gif-ui','resource-transfer-ui'}
def validate(repo,record,commit,inputs):
 record=Path(record);prior=json.loads(record.read_text());manifest=json.loads(record.with_suffix('.manifest.json').read_text())
 if prior['status']!='cleaned' or sha(prior['evidence'])!=prior['evidenceSha256'] or manifest['archiveSha256']!=prior['evidenceSha256']:raise RuntimeError('Sealed SVG evidence required')
 verify_archive(prior['evidence'],manifest['files'])
 changed=subprocess.check_output(['git','diff','--name-only',prior['source'],commit],cwd=repo,text=True).splitlines()
 allowed={'tools/verify_desktop.py','tools/verification_svg_reuse.py','tests/probes/verification_svg_suite.py'}
 if any(p not in allowed and not p.startswith('docs/')for p in changed):raise RuntimeError('SVG product/test inputs changed; execute fresh checks')
 def content(version,path):return subprocess.check_output(['git','show',version+':'+path],cwd=repo)
 if hashlib.sha256(content(prior['source'],'tools/verify_desktop.py')).hexdigest()!=OLD_TOOLS or hashlib.sha256(content(commit,'tools/verify_desktop.py')).hexdigest()!=NEW_TOOLS or hashlib.sha256(content(commit,'tests/probes/verification_svg_suite.py')).hexdigest()!=ROUTING_PROBE:raise RuntimeError('Only exact SVG routing correction is reusable')
 failed=[(r['name'],r['exit'])for r in prior['results']if r['exit']!=0]
 if failed!=[('packaged-feature-renderer',1)]:raise RuntimeError('Unexpected prior failure or incomplete SVG evidence')
 with zipfile.ZipFile(prior['evidence'])as archive:
  identity=json.loads(archive.read('source.json'))
  if identity['commit']!=prior['source']or any(identity['dependencyInputs'].get(k)!=inputs.get(k)for k in ['sdk','nuget','configuration','rid']):raise RuntimeError('SVG SDK/dependency inputs changed')
  for label,eol in [('lf','false'),('crlf','true')]:
   checkout=json.loads(archive.read(label+'-checkout.json'))
   if checkout['commit']!=prior['source']or checkout['coreAutocrlf']!=eol or checkout['noSharedGitObjects']is not True:raise RuntimeError('Independent SVG checkout/EOL identity differs')
  expected={label+'-'+suffix for label in ['lf','crlf']for suffix in SUFFIXES};rows={r['name']:r for r in prior['results']if r['name']in expected and r['exit']==0}
  if set(rows)!=expected:raise RuntimeError('All36 exact SVG checks must be present')
  for name,row in rows.items():
   if json.loads(archive.read(name+'.result.json'))!=row:raise RuntimeError('Archived SVG result differs')
 return prior,rows,changed

def bind(repo,record,commit,inputs,work):
 prior,rows,changed=validate(repo,record,commit,inputs)
 bad=copy.deepcopy(inputs);bad['sdk']['sha256']='0'*64
 try:validate(repo,record,commit,bad)
 except RuntimeError as error:
  if str(error)!='SVG SDK/dependency inputs changed':raise
 else:raise RuntimeError('Changed SDK accepted by SVG reuse guard')
 parent=subprocess.check_output(['git','rev-parse',prior['source']+'^'],cwd=repo,text=True).strip()
 try:validate(repo,record,parent,inputs)
 except RuntimeError as error:
  if str(error)!='SVG product/test inputs changed; execute fresh checks':raise
 else:raise RuntimeError('Changed product accepted by SVG reuse guard')
 proof=dict(previousRecord=str(record),previousSource=prior['source'],previousArchive=prior['evidence'],archiveSha256=prior['evidenceSha256'],sourceCommit=commit,identicalProductAndRuntimeTests=True,identicalSDKAndDependencies=True,onlyChange='exact SVG package/restore routing plus its guard and sealed reuse plumbing',allowedChangedFiles=changed,failedChecksReused=False,buildsAndPackagesReused=False,negativeGuards=['changed SDK rejected','changed product/test rejected'],stages=[])
 atomic_json(work.evidence/'svg-reuse.json',proof);original=work.run
 def run(name,command,*args,**kwargs):
  if name not in rows:return original(name,command,*args,**kwargs)
  row=rows[name];normalize=lambda c,root:[str(arg).replace(root,'$OWNED_WORKSPACE')for arg in c]
  if kwargs.get('expected',0)!=0 or normalize(row['command'],prior['root'])!=normalize(command,str(work.root)):raise RuntimeError('SVG reuse invocation differs: '+name)
  proof['stages'].append(name);work.state.setdefault('reusedChecks',[]).append(dict(name=name,sourceCommit=commit,previousSource=prior['source'],previousRecord=str(record),archiveSha256=prior['evidenceSha256'],kind='identical-static-svg-check',SDKAndNugetIdentical=True,unchangedNativeAndProbeInputs=True,identicalProductAndRuntimeTests=True))
  work.save();atomic_json(work.evidence/'svg-reuse.json',proof);atomic_json(work.evidence/(name+'.reused.json'),dict(proof=proof,priorResult=row));print(json.dumps(dict(stage=name,reused=True,previousSource=prior['source'])),flush=True);return row
 work.run=run
