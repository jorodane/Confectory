"""Exact sealed passing custom-axis facts before a transient legacy 4K API failure.

No failed/changed test, build, boundary, package or restore is reused. Default full
fresh suite remains. Every command, product/test input and dependency is checked.
"""
import copy,hashlib,json,subprocess,zipfile
from pathlib import Path
from verification_workspace import atomic_json,sha,verify_archive
SOURCE='562814b7cd260e98e8c468fe7c7a652d3e27056c'
OLD_TOOLS='dcb2479865ead0ab47062572e43e756609e0d09a5d05bd6bfda4910fb5a8b22b'
NEW_TOOLS='e7b3a8a4e7acf5e4bfa97d17c79b4a9239aa88cd49a8dcf839cc68b46f71617e'
NAMES=set(['lf-run-custom_axis-projection','lf-run-4k-projection','lf-run-qhd-projection','lf-run-fhd-projection','lf-run-hd-projection','lf-run-wide-projection','lf-run-surface-projection','lf-run-resolution-projection','lf-run-presets-projection','lf-run-fhd-native','lf-run-control-native'])

def validate(repo,record,commit,inputs):
 record=Path(record);prior=json.loads(record.read_text());manifest=json.loads(record.with_suffix('.manifest.json').read_text())
 if prior['source']!=SOURCE or prior['status']!='cleaned'or sha(prior['evidence'])!=prior['evidenceSha256']or manifest['archiveSha256']!=prior['evidenceSha256']:raise RuntimeError('Sealed identical custom-axis evidence required')
 verify_archive(prior['evidence'],manifest['files'])
 changed=subprocess.check_output(['git','diff','--name-only',prior['source'],commit],cwd=repo,text=True).splitlines();allowed={'tools/verify_desktop.py','tools/verification_custom_axis_reuse.py'}
 if any(n not in allowed and not n.startswith('docs/')for n in changed):raise RuntimeError('custom-axis product/native/other test inputs changed; execute fresh')
 def digest(version,path):return hashlib.sha256(subprocess.check_output(['git','show',version+':'+path],cwd=repo)).hexdigest()
 for version,path,expected in [(SOURCE,'tools/verify_desktop.py',OLD_TOOLS),(commit,'tools/verify_desktop.py',NEW_TOOLS)]:
  if digest(version,path)!=expected:raise RuntimeError('Only exact reuse plumbing, product and all probes unchanged allowed')
 if [(x['name'],x['exit'])for x in prior['results']if x['exit']]!=[('lf-run-4k-api-normal',1)]:raise RuntimeError('Unexpected priorcustom-axis failure')
 with zipfile.ZipFile(prior['evidence'])as z:
  identity=json.loads(z.read('source.json'))
  if identity['commit']!=prior['source'] or any(identity['dependencyInputs'].get(k)!=inputs.get(k)for k in ['sdk','nuget','configuration','rid']):raise RuntimeError('custom-axis SDK/dependency identity changed')
  for label,autocrlf in [('lf','false')]:
   checkout=json.loads(z.read(label+'-checkout.json'))
   if checkout['commit']!=prior['source'] or checkout['coreAutocrlf']!=autocrlf or checkout['noSharedGitObjects']is not True:raise RuntimeError('Independentcustom-axis checkout identity differs')
  names=NAMES
  rows={x['name']:x for x in prior['results']if x['name']in names and x['exit']==0}
  if set(rows)!=names:raise RuntimeError('All exact pinned passingcustom-axis facts required')
  for name,row in rows.items():
   if json.loads(z.read(name+'.result.json'))!=row:raise RuntimeError('Archivedcustom-axis result differs')
 return prior,rows,changed

def bind(repo,record,commit,inputs,work):
 prior,rows,changed=validate(repo,record,commit,inputs);bad=copy.deepcopy(inputs);bad['sdk']['sha256']='0'*64
 try:validate(repo,record,commit,bad)
 except RuntimeError as error:
  if str(error)!='custom-axis SDK/dependency identity changed':raise
 else:raise RuntimeError('Changed SDK accepted bycustom-axis reuse guard')
 parent=subprocess.check_output(['git','rev-parse',SOURCE+'^'],cwd=repo,text=True).strip()
 try:validate(repo,record,parent,inputs)
 except RuntimeError as error:
  if str(error)!='custom-axis product/native/other test inputs changed; execute fresh':raise
 else:raise RuntimeError('Changed product accepted bycustom-axis reuse guard')
 proof={'previousRecord':str(record),'previousSource':prior['source'],'archiveSha256':prior['evidenceSha256'],'sourceCommit':commit,'identicalProductNativeAndReusedTestInputs':True,'identicalSDKAndDependencies':True,'onlyChange':'unchanged product/probes after a legacy4K observation failure; diagnostic runs observed bounded I/O cancellation; source-bound reuse plumbing only','allowedChangedFiles':changed,'failedOrChangedChecksReused':False,'buildsOrPackagesOrBoundaryReused':False,'negativeGuards':['changed SDK rejected','changed product rejected'],'stages':[]};proofPath=work.evidence/('custom-axis-reuse-'+prior['source'][:8]+'.json');atomic_json(proofPath,proof);original=work.run
 def run(name,command,*args,**kwargs):
  if name not in rows:return original(name,command,*args,**kwargs)
  row=rows[name];normalize=lambda c,root:[str(a).replace(root,'$OWNED_WORKSPACE')for a in c]
  if kwargs.get('expected',0)!=0 or normalize(row['command'],prior['root'])!=normalize(command,str(work.root)):raise RuntimeError('custom-axis reuse invocation differs: '+name)
  if any(x['name']==name for x in work.state.get('reusedChecks',[])):raise RuntimeError('Duplicatecustom-axis reuse refused')
  entry={'name':name,'sourceCommit':commit,'previousSource':prior['source'],'previousRecord':str(record),'archiveSha256':prior['evidenceSha256'],'kind':'identical-source-and-probecustom-axis-fact','SDKAndNugetIdentical':True};work.state.setdefault('reusedChecks',[]).append(entry);proof['stages'].append(name);work.save();atomic_json(proofPath,proof);atomic_json(work.evidence/(name+'.reused.json'),{'proof':proof,'priorResult':row});print(json.dumps({'stage':name,'reused':True,'previousSource':prior['source']}),flush=True);return row
 work.run=run
