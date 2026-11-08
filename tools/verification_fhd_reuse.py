"""Reuse only sealed identical LF facts after a bounded initial-observation probe fix.

No product, native test, codec/ABI/permission input changes are permitted. Failed
checks, all API/UI, independent builds, packaging and restores always run fresh.
"""
import copy,hashlib,json,subprocess,zipfile
from pathlib import Path
from verification_workspace import atomic_json,sha,verify_archive
SOURCE='ea5c1f65bed7be86ca1585315057e7d809f2166b'
OLD_TOOLS='1afabec979de1e54a5dfebe5eafe7578e16ab5edae3a02f573993b0f3bc1db84'
NEW_TOOLS='3c0c552d358ca34ce11589a17e90c3a9d31089e942b4bbf34ac8c548b4bde053'
OLD_PROBE='3875013533148aede2dc7be8c8b42363d97b9edae6caf8d817dd6d00425a6326'
NEW_PROBE='b276df46d4dc60f19afd31f94c7afbd3f3e9d04e998f119d734a3ed3ff4fdb5c'
SUFFIXES={'v536_mixed_declaration','v536_local_header_image','run-fhd-boundary','run-fhd-projection','run-hd-projection','run-wide-projection','run-surface-projection','run-resolution-projection','run-presets-projection','run-fhd-native','run-control-native'}
def validate(repo,record,commit,inputs):
 record=Path(record);prior=json.loads(record.read_text());manifest=json.loads(record.with_suffix('.manifest.json').read_text())
 if prior['source']!=SOURCE or prior['status']!='cleaned' or sha(prior['evidence'])!=prior['evidenceSha256']or manifest['archiveSha256']!=prior['evidenceSha256']:raise RuntimeError('Sealed FHD evidence required')
 verify_archive(prior['evidence'],manifest['files'])
 changed=subprocess.check_output(['git','diff','--name-only',SOURCE,commit],cwd=repo,text=True).splitlines()
 allowed={'tools/verify_desktop.py','tools/verification_fhd_reuse.py','tests/web/v666_run_fhd_api.py'}
 if any(p not in allowed and not p.startswith('docs/')for p in changed):raise RuntimeError('FHD product/native/projection inputs changed; execute fresh checks')
 def digest(version,path):return hashlib.sha256(subprocess.check_output(['git','show',version+':'+path],cwd=repo)).hexdigest()
 if digest(SOURCE,'tools/verify_desktop.py')!=OLD_TOOLS or digest(commit,'tools/verify_desktop.py')!=NEW_TOOLS or digest(SOURCE,'tests/web/v666_run_fhd_api.py')!=OLD_PROBE or digest(commit,'tests/web/v666_run_fhd_api.py')!=NEW_PROBE:raise RuntimeError('Only exact initial read-only observation correction is reusable')
 if [(r['name'],r['exit'])for r in prior['results']if r['exit']!=0]!=[('lf-run-fhd-api-normal',1)]:raise RuntimeError('Unexpected prior FHD failure')
 with zipfile.ZipFile(prior['evidence'])as archive:
  identity=json.loads(archive.read('source.json'));checkout=json.loads(archive.read('lf-checkout.json'))
  if identity['commit']!=SOURCE or any(identity['dependencyInputs'].get(k)!=inputs.get(k)for k in ['sdk','nuget','configuration','rid']):raise RuntimeError('FHD SDK/dependency inputs changed')
  if checkout['commit']!=SOURCE or checkout['coreAutocrlf']!='false'or checkout['noSharedGitObjects']is not True:raise RuntimeError('Independent LF checkout identity differs')
  expected={'lf-'+suffix for suffix in SUFFIXES};rows={r['name']:r for r in prior['results']if r['name']in expected and r['exit']==0}
  if set(rows)!=expected:raise RuntimeError('All eleven exact passing LF checks must be present')
  for name,row in rows.items():
   if json.loads(archive.read(name+'.result.json'))!=row:raise RuntimeError('Archived FHD result differs')
 return prior,rows,changed

def bind(repo,record,commit,inputs,work):
 prior,rows,changed=validate(repo,record,commit,inputs)
 bad=copy.deepcopy(inputs);bad['sdk']['sha256']='0'*64
 try:validate(repo,record,commit,bad)
 except RuntimeError as error:
  if str(error)!='FHD SDK/dependency inputs changed':raise
 else:raise RuntimeError('Changed SDK accepted by FHD reuse guard')
 parent=subprocess.check_output(['git','rev-parse',SOURCE+'^'],cwd=repo,text=True).strip()
 try:validate(repo,record,parent,inputs)
 except RuntimeError as error:
  if str(error)!='FHD product/native/projection inputs changed; execute fresh checks':raise
 else:raise RuntimeError('Changed product accepted by FHD reuse guard')
 proof=dict(previousRecord=str(record),previousSource=SOURCE,archiveSha256=prior['evidenceSha256'],sourceCommit=commit,identicalProductNativeAndProjectionInputs=True,identicalSDKAndDependencies=True,onlyChange='exact bounded initial read-only FHD observation probe and sealed reuse plumbing',allowedChangedFiles=changed,failedChecksReused=False,buildsPackagesAPIAndUIReused=False,negativeGuards=['changed SDK rejected','changed product rejected'],stages=[])
 atomic_json(work.evidence/'fhd-reuse.json',proof);original=work.run
 def run(name,command,*args,**kwargs):
  if name not in rows:return original(name,command,*args,**kwargs)
  row=rows[name];normalize=lambda c,root:[str(arg).replace(root,'$OWNED_WORKSPACE')for arg in c]
  if kwargs.get('expected',0)!=0 or normalize(row['command'],prior['root'])!=normalize(command,str(work.root)):raise RuntimeError('FHD reuse invocation differs: '+name)
  proof['stages'].append(name);work.state.setdefault('reusedChecks',[]).append(dict(name=name,sourceCommit=commit,previousSource=SOURCE,previousRecord=str(record),archiveSha256=prior['evidenceSha256'],kind='identical-LF-FHD-native-or-projection-fact',SDKAndNugetIdentical=True,unchangedProductNativeAndProbeInputs=True))
  work.save();atomic_json(work.evidence/'fhd-reuse.json',proof);atomic_json(work.evidence/(name+'.reused.json'),dict(proof=proof,priorResult=row));print(json.dumps(dict(stage=name,reused=True,previousSource=SOURCE)),flush=True);return row
 work.run=run
