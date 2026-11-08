"""Exact sealed4K memory facts before the reproduced HD cold fixture cache-row correction.

No failed/changed test, build, boundary, package or restore is reused. Default full
fresh suite remains. Every command, product/test input and dependency is checked.
"""
import copy,hashlib,json,subprocess,zipfile
from pathlib import Path
from verification_workspace import atomic_json,sha,verify_archive
SOURCE='01b63a75f51b9ef6e59497d87e96529a86d0a6f2'
OLD_TOOLS='c3ba358c9be8096702a11339a25ad43d5656dc4038624f82b9dbb8d5a4b5fbe4'
NEW_TOOLS='521e5276cb8ca96b2d1517e643bc930f38388cc6ff22a06443f7b69fa29aa592'
OLD_PROBE='765ce02d51c2fd9a4e8970ea6da5cbc7bfe96ac21c5f24bb3759576a8d0a4a1b'
NEW_PROBE='ddfbe1ade4c5060fbda1f5e00bcc8cfb1ac2bafca51fe8af415a0cf379f6f8f2'
NAMES=set(['lf-run-4k-api-faults', 'lf-run-4k-api-normal', 'lf-run-4k-projection', 'lf-run-4k-ui-normal', 'lf-run-4k-ui-parts', 'lf-run-audio-regression', 'lf-run-auto-regression', 'lf-run-bounds-regression', 'lf-run-control-native', 'lf-run-fhd-native', 'lf-run-fhd-projection', 'lf-run-hd-projection', 'lf-run-legacy-capabilities', 'lf-run-legacy-heartbeat', 'lf-run-presets-projection', 'lf-run-presets-regression', 'lf-run-qhd-projection', 'lf-run-rate-regression', 'lf-run-resolution-projection', 'lf-run-surface-projection', 'lf-run-wide-projection', 'lf-run-wide-ui'])

def validate(repo,record,commit,inputs):
 record=Path(record);prior=json.loads(record.read_text());manifest=json.loads(record.with_suffix('.manifest.json').read_text())
 if prior['source']!=SOURCE or prior['status']!='cleaned'or sha(prior['evidence'])!=prior['evidenceSha256']or manifest['archiveSha256']!=prior['evidenceSha256']:raise RuntimeError('Sealed identical4K evidence required')
 verify_archive(prior['evidence'],manifest['files'])
 changed=subprocess.check_output(['git','diff','--name-only',prior['source'],commit],cwd=repo,text=True).splitlines();allowed={'tools/verify_desktop.py','tools/verification_4k_memory_reuse.py','tests/web/v666_run_hd_ui.py'}
 if any(n not in allowed and not n.startswith('docs/')for n in changed):raise RuntimeError('4K product/native/other test inputs changed; execute fresh')
 def digest(version,path):return hashlib.sha256(subprocess.check_output(['git','show',version+':'+path],cwd=repo)).hexdigest()
 for version,path,expected in [(SOURCE,'tools/verify_desktop.py',OLD_TOOLS),(commit,'tools/verify_desktop.py',NEW_TOOLS),(SOURCE,'tests/web/v666_run_hd_ui.py',OLD_PROBE),(commit,'tests/web/v666_run_hd_ui.py',NEW_PROBE)]:
  if digest(version,path)!=expected:raise RuntimeError('Only exact HD cold lease probe and reuse plumbing correction allowed')
 if [(x['name'],x['exit'])for x in prior['results']if x['exit']]!=[('lf-run-hd-compatibility-ui',1)]:raise RuntimeError('Unexpected prior4K memory failure')
 with zipfile.ZipFile(prior['evidence'])as z:
  identity=json.loads(z.read('source.json'))
  if identity['commit']!=prior['source'] or any(identity['dependencyInputs'].get(k)!=inputs.get(k)for k in ['sdk','nuget','configuration','rid']):raise RuntimeError('4K SDK/dependency identity changed')
  for label,autocrlf in [('lf','false')]:
   checkout=json.loads(z.read(label+'-checkout.json'))
   if checkout['commit']!=prior['source'] or checkout['coreAutocrlf']!=autocrlf or checkout['noSharedGitObjects']is not True:raise RuntimeError('Independent4K checkout identity differs')
  names=NAMES
  rows={x['name']:x for x in prior['results']if x['name']in names and x['exit']==0}
  if set(rows)!=names:raise RuntimeError('All exact pinned passing4K facts required')
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
 proof={'previousRecord':str(record),'previousSource':prior['source'],'archiveSha256':prior['evidenceSha256'],'sourceCommit':commit,'identicalProductNativeAndReusedTestInputs':True,'identicalSDKAndDependencies':True,'onlyChange':'exact HD cold fresh-native-lease/idle/empty-handle observation wait; product unchanged, source-bound reuse plumbing','allowedChangedFiles':changed,'failedOrChangedChecksReused':False,'buildsOrPackagesOrBoundaryReused':False,'negativeGuards':['changed SDK rejected','changed product rejected'],'stages':[]};proofPath=work.evidence/('4k-memory-reuse-'+prior['source'][:8]+'.json');atomic_json(proofPath,proof);original=work.run
 def run(name,command,*args,**kwargs):
  if name not in rows:return original(name,command,*args,**kwargs)
  row=rows[name];normalize=lambda c,root:[str(a).replace(root,'$OWNED_WORKSPACE')for a in c]
  if kwargs.get('expected',0)!=0 or normalize(row['command'],prior['root'])!=normalize(command,str(work.root)):raise RuntimeError('4K reuse invocation differs: '+name)
  if any(x['name']==name for x in work.state.get('reusedChecks',[])):raise RuntimeError('Duplicate4K reuse refused')
  entry={'name':name,'sourceCommit':commit,'previousSource':prior['source'],'previousRecord':str(record),'archiveSha256':prior['evidenceSha256'],'kind':'identical-source-and-probe4K-memory-fact','SDKAndNugetIdentical':True};work.state.setdefault('reusedChecks',[]).append(entry);proof['stages'].append(name);work.save();atomic_json(proofPath,proof);atomic_json(work.evidence/(name+'.reused.json'),{'proof':proof,'priorResult':row});print(json.dumps({'stage':name,'reused':True,'previousSource':prior['source']}),flush=True);return row
 work.run=run
