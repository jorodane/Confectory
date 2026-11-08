"""Only sealed identical4K facts after the exact heartbeat observation probe fix.

Failed/changed checks, checkout/build/engine/boundary, package and full restore are
fresh. Every reused command must match after normalizing its owned root only.
"""
import copy,hashlib,json,subprocess,zipfile
from pathlib import Path
from verification_workspace import atomic_json,sha,verify_archive
# Exact pinned source/probe/harness identities are filled below, never inferred from a title.
SOURCE='9aa90c199ec3c055602d3472682ef00d10fdb32b'
OLD_TOOLS='43ae4fd19c76d050671a0cca6088560fd4cff35e352c88d31217ff9ad6f38247'
NEW_TOOLS='b410d1d4bc131d9827923000046497e94cf47bf01dac35fa7c25ce8292a772e7'
OLD_PROBE='a9ca92a1e225cfaf89db0fedd30df26790a4d7a54490ac7020397cb21087b006'
NEW_PROBE='fa0ae89989855800c44bac0705bfc8e8a766b95050cba9fdf4e8c1956cb06bcc'
NAMES=set(['crlf-run-4k-api-faults', 'crlf-run-4k-api-normal', 'crlf-run-4k-projection', 'crlf-run-4k-ui-lifecycle', 'crlf-run-fhd-native', 'crlf-run-fhd-projection', 'crlf-run-hd-projection', 'crlf-run-legacy-capabilities', 'crlf-run-presets-projection', 'crlf-run-qhd-projection', 'crlf-run-resolution-projection', 'crlf-run-surface-projection', 'crlf-run-wide-projection', 'crlf-run-wide-ui', 'lf-run-4k-api-faults', 'lf-run-4k-api-normal', 'lf-run-4k-projection', 'lf-run-4k-ui-normal', 'lf-run-4k-ui-parts', 'lf-run-audio-regression', 'lf-run-auto-regression', 'lf-run-bounds-regression', 'lf-run-control-native', 'lf-run-fhd-compatibility-api', 'lf-run-fhd-native', 'lf-run-fhd-projection', 'lf-run-fixed-menu-regression', 'lf-run-hd-compatibility-ui', 'lf-run-hd-projection', 'lf-run-legacy-capabilities', 'lf-run-presets-projection', 'lf-run-presets-regression', 'lf-run-qhd-compatibility-api', 'lf-run-qhd-projection', 'lf-run-rate-regression', 'lf-run-resolution-projection', 'lf-run-surface-projection', 'lf-run-wide-projection', 'lf-run-wide-ui'])

def validate(repo,record,commit,inputs):
 record=Path(record);prior=json.loads(record.read_text());manifest=json.loads(record.with_suffix('.manifest.json').read_text())
 if prior['source']!=SOURCE or prior['status']!='cleaned'or sha(prior['evidence'])!=prior['evidenceSha256']or manifest['archiveSha256']!=prior['evidenceSha256']:raise RuntimeError('Sealed identical4K evidence required')
 verify_archive(prior['evidence'],manifest['files'])
 changed=subprocess.check_output(['git','diff','--name-only',SOURCE,commit],cwd=repo,text=True).splitlines();allowed={'tools/verify_desktop.py','tools/verification_4k_reuse.py','tests/web/v666_run_surface_api.py'}
 if any(n not in allowed and not n.startswith('docs/')for n in changed):raise RuntimeError('4K product/native/other test inputs changed; execute fresh')
 def digest(version,path):return hashlib.sha256(subprocess.check_output(['git','show',version+':'+path],cwd=repo)).hexdigest()
 for version,path,expected in [(SOURCE,'tools/verify_desktop.py',OLD_TOOLS),(commit,'tools/verify_desktop.py',NEW_TOOLS),(SOURCE,'tests/web/v666_run_surface_api.py',OLD_PROBE),(commit,'tests/web/v666_run_surface_api.py',NEW_PROBE)]:
  if digest(version,path)!=expected:raise RuntimeError('Only exact4K heartbeat probe and reuse plumbing correction allowed')
 if [(x['name'],x['exit'])for x in prior['results']if x['exit']]!=[('crlf-run-legacy-heartbeat',1)]:raise RuntimeError('Unexpected prior4K failure')
 with zipfile.ZipFile(prior['evidence'])as z:
  identity=json.loads(z.read('source.json'))
  if identity['commit']!=SOURCE or any(identity['dependencyInputs'].get(k)!=inputs.get(k)for k in ['sdk','nuget','configuration','rid']):raise RuntimeError('4K SDK/dependency identity changed')
  for label,autocrlf in [('lf','false'),('crlf','true')]:
   checkout=json.loads(z.read(label+'-checkout.json'))
   if checkout['commit']!=SOURCE or checkout['coreAutocrlf']!=autocrlf or checkout['noSharedGitObjects']is not True:raise RuntimeError('Independent4K checkout identity differs')
  rows={x['name']:x for x in prior['results']if x['name']in NAMES and x['exit']==0}
  if set(rows)!=NAMES:raise RuntimeError('All39 exact passing4K facts required')
  for name,row in rows.items():
   if json.loads(z.read(name+'.result.json'))!=row:raise RuntimeError('Archived4K result differs')
 return prior,rows,changed

def bind(repo,record,commit,inputs,work):
 prior,rows,changed=validate(repo,record,commit,inputs);bad=copy.deepcopy(inputs);bad['sdk']['sha256']='0'*64
 try:validate(repo,record,commit,bad)
 except RuntimeError as error:
  if str(error)!='4K SDK/dependency identity changed':raise
 else:raise RuntimeError('Changed SDK accepted by4K reuse guard')
 parent=subprocess.check_output(['git','rev-parse',SOURCE+'^'],cwd=repo,text=True).strip()
 try:validate(repo,record,parent,inputs)
 except RuntimeError as error:
  if str(error)!='4K product/native/other test inputs changed; execute fresh':raise
 else:raise RuntimeError('Changed product accepted by4K reuse guard')
 proof={'previousRecord':str(record),'previousSource':SOURCE,'archiveSha256':prior['evidenceSha256'],'sourceCommit':commit,'identicalProductNativeAndReusedTestInputs':True,'identicalSDKAndDependencies':True,'onlyChange':'exact heartbeat observation transport-unavailable handling with late successful pixels, unchanged invoke count and actual paused control; source-bound reuse plumbing','allowedChangedFiles':changed,'failedOrChangedChecksReused':False,'buildsOrPackagesOrBoundaryReused':False,'negativeGuards':['changed SDK rejected','changed product rejected'],'stages':[]};proofPath=work.evidence/'4k-reuse.json';atomic_json(proofPath,proof);original=work.run
 def run(name,command,*args,**kwargs):
  if name not in rows:return original(name,command,*args,**kwargs)
  row=rows[name];normalize=lambda c,root:[str(a).replace(root,'$OWNED_WORKSPACE')for a in c]
  if kwargs.get('expected',0)!=0 or normalize(row['command'],prior['root'])!=normalize(command,str(work.root)):raise RuntimeError('4K reuse invocation differs: '+name)
  if any(x['name']==name for x in work.state.get('reusedChecks',[])):raise RuntimeError('Duplicate4K reuse refused')
  entry={'name':name,'sourceCommit':commit,'previousSource':SOURCE,'previousRecord':str(record),'archiveSha256':prior['evidenceSha256'],'kind':'identical-source-and-probe4K-fact','SDKAndNugetIdentical':True};work.state.setdefault('reusedChecks',[]).append(entry);proof['stages'].append(name);work.save();atomic_json(proofPath,proof);atomic_json(work.evidence/(name+'.reused.json'),{'proof':proof,'priorResult':row});print(json.dumps({'stage':name,'reused':True,'previousSource':SOURCE}),flush=True);return row
 work.run=run
