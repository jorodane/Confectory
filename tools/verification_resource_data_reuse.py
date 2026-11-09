"""Exact sealed Data source facts before the restored common Agent setup timeout.

No failed/changed test, build, boundary, package or restore is reused. Default full
fresh suite remains. Every command, product/test input and dependency is checked.
"""
import copy,hashlib,json,subprocess,zipfile
from pathlib import Path
from verification_workspace import atomic_json,sha,verify_archive
SOURCE='3873c63d0a1b1b8e53b9ce09303080294c1bc9f4'
OLD_TOOLS='36afdc97c55c9f20ccee97e1ecb77c6ea8d87c0435c3919ce77aa24849cc45a2'
NEW_TOOLS='ef215e339ab5d6fc1923c919e50b67e6d804753b1b6292de5ffacb1baef16dc4'
OLD_PROBE='b17d8e6aeba238801bf9e4e8cc4b1e4381c6830e3417a79dde80dc23cc383091'
NEW_PROBE='1a1675b562d85fbfc3a8a42c7b6cf4344f5acba085c15dcea98080c34cee0e0f'
NAMES=set(['crlf-resource-data-lifecycle', 'crlf-resource-data-normal', 'crlf-resource-data-unit', 'crlf-resource-filter-regression', 'crlf-resource-keyboard-regression', 'crlf-resource-keyboard-unit', 'crlf-resource-layout-regression', 'crlf-resource-original-final-read', 'crlf-resource-original-regression', 'crlf-resource-parent-final-read', 'crlf-resource-parent-provider', 'crlf-resource-parent-regression', 'crlf-resource-sort-regression', 'crlf-v536_local_header_image', 'crlf-v536_mixed_declaration', 'crlf-web-resource-contract', 'lf-resource-data-lifecycle', 'lf-resource-data-normal', 'lf-resource-data-unit', 'lf-resource-filter-regression', 'lf-resource-keyboard-regression', 'lf-resource-keyboard-unit', 'lf-resource-layout-regression', 'lf-resource-original-final-read', 'lf-resource-original-regression', 'lf-resource-parent-final-read', 'lf-resource-parent-provider', 'lf-resource-parent-regression', 'lf-resource-sort-regression', 'lf-v536_local_header_image', 'lf-v536_mixed_declaration', 'lf-web-resource-contract'])

def validate(repo,record,commit,inputs):
 record=Path(record);prior=json.loads(record.read_text());manifest=json.loads(record.with_suffix('.manifest.json').read_text())
 if prior['source']!=SOURCE or prior['status']!='cleaned'or sha(prior['evidence'])!=prior['evidenceSha256']or manifest['archiveSha256']!=prior['evidenceSha256']:raise RuntimeError('Sealed identicalResource Data evidence required')
 verify_archive(prior['evidence'],manifest['files'])
 changed=subprocess.check_output(['git','diff','--name-only',prior['source'],commit],cwd=repo,text=True).splitlines();allowed={'tools/verify_desktop.py','tools/verification_resource_data_reuse.py','tests/probes/desktop_package.py'}
 if any(n not in allowed and not n.startswith('docs/')for n in changed):raise RuntimeError('Resource Data product/native/other test inputs changed; execute fresh')
 def digest(version,path):return hashlib.sha256(subprocess.check_output(['git','show',version+':'+path],cwd=repo)).hexdigest()
 for version,path,expected in [(SOURCE,'tools/verify_desktop.py',OLD_TOOLS),(commit,'tools/verify_desktop.py',NEW_TOOLS),(SOURCE,'tests/probes/desktop_package.py',OLD_PROBE),(commit,'tests/probes/desktop_package.py',NEW_PROBE)]:
  if digest(version,path)!=expected:raise RuntimeError('Only exact async package readiness probe diagnostics and reuse plumbing allowed')
 if [(x['name'],x['exit'])for x in prior['results']if x['exit']]!=[('restored-probe',1)]:raise RuntimeError('Unexpected prior Data failure')
 with zipfile.ZipFile(prior['evidence'])as z:
  identity=json.loads(z.read('source.json'))
  if identity['commit']!=prior['source'] or any(identity['dependencyInputs'].get(k)!=inputs.get(k)for k in ['sdk','nuget','configuration','rid']):raise RuntimeError('Resource Data SDK/dependency identity changed')
  for label,autocrlf in [('lf','false'),('crlf','true')]:
   checkout=json.loads(z.read(label+'-checkout.json'))
   if checkout['commit']!=prior['source'] or checkout['coreAutocrlf']!=autocrlf or checkout['noSharedGitObjects']is not True:raise RuntimeError('IndependentResource Data checkout identity differs')
  names=NAMES
  rows={x['name']:x for x in prior['results']if x['name']in names and x['exit']==0}
  if set(rows)!=names:raise RuntimeError('All exact pinned passingResource Data facts required')
  for name,row in rows.items():
   if json.loads(z.read(name+'.result.json'))!=row:raise RuntimeError('ArchivedResource Data result differs')
   for arg in row['command']:
    for label in ['lf','crlf']:
     prefix=prior['root']+'/'+label+'/'
     if str(arg).startswith(prefix)and str(arg).endswith(('.py','.mjs')):
      path=str(arg)[len(prefix):]
      if digest(SOURCE,path)!=digest(commit,path):raise RuntimeError('Reused test input changed: '+path)
 return prior,rows,changed

def bind(repo,record,commit,inputs,work):
 prior,rows,changed=validate(repo,record,commit,inputs);bad=copy.deepcopy(inputs);bad['sdk']['sha256']='0'*64
 try:validate(repo,record,commit,bad)
 except RuntimeError as error:
  if str(error)!='Resource Data SDK/dependency identity changed':raise
 else:raise RuntimeError('Changed SDK accepted byResource Data reuse guard')
 parent=subprocess.check_output(['git','rev-parse',SOURCE+'^'],cwd=repo,text=True).strip()
 try:validate(repo,record,parent,inputs)
 except RuntimeError as error:
  if str(error)!='Resource Data product/native/other test inputs changed; execute fresh':raise
 else:raise RuntimeError('Changed product accepted byResource Data reuse guard')
 proof={'previousRecord':str(record),'previousSource':prior['source'],'archiveSha256':prior['evidenceSha256'],'sourceCommit':commit,'identicalProductNativeAndReusedTestInputs':True,'identicalSDKAndDependencies':True,'onlyChange':'unchanged Data product and 32 source facts; common package probe observes async setup completion with diagnostics; no failed/build/package/restore fact reused','allowedChangedFiles':changed,'failedOrChangedChecksReused':False,'buildsOrPackagesOrBoundaryReused':False,'negativeGuards':['changed SDK rejected','changed product rejected'],'stages':[]};proofPath=work.evidence/('resource-data-reuse-'+prior['source'][:8]+'.json');atomic_json(proofPath,proof);original=work.run
 def run(name,command,*args,**kwargs):
  if name not in rows:return original(name,command,*args,**kwargs)
  row=rows[name];normalize=lambda c,root:[str(a).replace(root,'$OWNED_WORKSPACE')for a in c]
  if kwargs.get('expected',0)!=0 or normalize(row['command'],prior['root'])!=normalize(command,str(work.root)):raise RuntimeError('Resource Data reuse invocation differs: '+name)
  if any(x['name']==name for x in work.state.get('reusedChecks',[])):raise RuntimeError('DuplicateResource Data reuse refused')
  entry={'name':name,'sourceCommit':commit,'previousSource':prior['source'],'previousRecord':str(record),'archiveSha256':prior['evidenceSha256'],'kind':'identical-source-and-probe-resource-data-fact','SDKAndNugetIdentical':True};work.state.setdefault('reusedChecks',[]).append(entry);proof['stages'].append(name);work.save();atomic_json(proofPath,proof);atomic_json(work.evidence/(name+'.reused.json'),{'proof':proof,'priorResult':row});print(json.dumps({'stage':name,'reused':True,'previousSource':prior['source']}),flush=True);return row
 work.run=run
