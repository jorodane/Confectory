"""Exact sealedXLSX memory facts before the captured public Office-part busy refusal on XLSX project return.

No failed/changed test, build, boundary, package or restore is reused. Default full
fresh suite remains. Every command, product/test input and dependency is checked.
"""
import copy,hashlib,json,subprocess,zipfile
from pathlib import Path
from verification_workspace import atomic_json,sha,verify_archive
SOURCE='879d5954e0723f43e6744109c471896cf84ed684'
OLD_TOOLS='c168436315bd8d95d4afaaaf539c8c2c8f0074249696c0056a043e01773901f5'
NEW_TOOLS='282aff09b9f1ae637d3ce8ea87a014a4828e199ece2adabe9c9116da9035e100'
OLD_PROBE='f2ce8f82f022483cc9dd95fc2c9b2e8b8d5b532305b5659eb269adf05b461d28'
NEW_PROBE='f3ebb20c51ba249b488e6f3a0d71499233df5ea84d9e4b06dcbd47a64c5a1955'
NAMES=set(['crlf-resource-content-regression', 'crlf-resource-docx-dom', 'crlf-resource-docx-parts-regression', 'crlf-resource-docx-provider', 'crlf-resource-docx-regression', 'crlf-resource-docx-unit', 'crlf-resource-docx_draft_cas', 'crlf-resource-docx_parts-unit', 'crlf-resource-docx_parts_cas', 'crlf-resource-office-unit', 'crlf-resource-office_large_zip-unit', 'crlf-resource-office_parts-regression', 'crlf-resource-office_parts-unit', 'crlf-resource-office_parts_cas', 'crlf-resource-xlsx-dom', 'crlf-resource-xlsx-regression', 'crlf-resource-xlsx_parts-unit', 'crlf-resource-xlsx_parts_cas', 'crlf-v536_local_header_image', 'crlf-v536_mixed_declaration', 'crlf-web-resource-contract', 'lf-resource-content-regression', 'lf-resource-docx-dom', 'lf-resource-docx-parts-regression', 'lf-resource-docx-provider', 'lf-resource-docx-regression', 'lf-resource-docx-unit', 'lf-resource-docx_draft_cas', 'lf-resource-docx_parts-unit', 'lf-resource-docx_parts_cas', 'lf-resource-office-unit', 'lf-resource-office_large_zip-unit', 'lf-resource-office_parts-regression', 'lf-resource-office_parts-unit', 'lf-resource-office_parts_cas', 'lf-resource-xlsx-dom', 'lf-resource-xlsx-regression', 'lf-resource-xlsx_parts-unit', 'lf-resource-xlsx_parts_cas', 'lf-v536_local_header_image', 'lf-v536_mixed_declaration', 'lf-web-resource-contract'])

def validate(repo,record,commit,inputs):
 record=Path(record);prior=json.loads(record.read_text());manifest=json.loads(record.with_suffix('.manifest.json').read_text())
 if prior['source']!=SOURCE or prior['status']!='cleaned'or sha(prior['evidence'])!=prior['evidenceSha256']or manifest['archiveSha256']!=prior['evidenceSha256']:raise RuntimeError('Sealed identicalXLSX evidence required')
 verify_archive(prior['evidence'],manifest['files'])
 changed=subprocess.check_output(['git','diff','--name-only',prior['source'],commit],cwd=repo,text=True).splitlines();allowed={'tools/verify_desktop.py','tools/verification_xlsx_parts_reuse.py','tests/web/v666_resource_xlsx_parts_ui.py'}
 if any(n not in allowed and not n.startswith('docs/')for n in changed):raise RuntimeError('XLSX product/native/other test inputs changed; execute fresh')
 def digest(version,path):return hashlib.sha256(subprocess.check_output(['git','show',version+':'+path],cwd=repo)).hexdigest()
 for version,path,expected in [(SOURCE,'tools/verify_desktop.py',OLD_TOOLS),(commit,'tools/verify_desktop.py',NEW_TOOLS),(SOURCE,'tests/web/v666_resource_xlsx_parts_ui.py',OLD_PROBE),(commit,'tests/web/v666_resource_xlsx_parts_ui.py',NEW_PROBE)]:
  if digest(version,path)!=expected:raise RuntimeError('Only exact XLSX project-return readonly Retry probe and reuse plumbing correction allowed')
 if [(x['name'],x['exit'])for x in prior['results']if x['exit']]!=[('restored-resource-xlsx-parts-lifecycle',1)]:raise RuntimeError('Unexpected priorXLSX memory failure')
 with zipfile.ZipFile(prior['evidence'])as z:
  identity=json.loads(z.read('source.json'))
  if identity['commit']!=prior['source'] or any(identity['dependencyInputs'].get(k)!=inputs.get(k)for k in ['sdk','nuget','configuration','rid']):raise RuntimeError('XLSX SDK/dependency identity changed')
  for label,autocrlf in [('lf','false'),('crlf','true')]:
   checkout=json.loads(z.read(label+'-checkout.json'))
   if checkout['commit']!=prior['source'] or checkout['coreAutocrlf']!=autocrlf or checkout['noSharedGitObjects']is not True:raise RuntimeError('IndependentXLSX checkout identity differs')
  names=NAMES
  rows={x['name']:x for x in prior['results']if x['name']in names and x['exit']==0}
  if set(rows)!=names:raise RuntimeError('All exact pinned passingXLSX facts required')
  for name,row in rows.items():
   if json.loads(z.read(name+'.result.json'))!=row:raise RuntimeError('ArchivedXLSX result differs')
 return prior,rows,changed

def bind(repo,record,commit,inputs,work):
 prior,rows,changed=validate(repo,record,commit,inputs);bad=copy.deepcopy(inputs);bad['sdk']['sha256']='0'*64
 try:validate(repo,record,commit,bad)
 except RuntimeError as error:
  if str(error)!='XLSX SDK/dependency identity changed':raise
 else:raise RuntimeError('Changed SDK accepted byXLSX reuse guard')
 parent=subprocess.check_output(['git','rev-parse',SOURCE+'^'],cwd=repo,text=True).strip()
 try:validate(repo,record,parent,inputs)
 except RuntimeError as error:
  if str(error)!='XLSX product/native/other test inputs changed; execute fresh':raise
 else:raise RuntimeError('Changed product accepted byXLSX reuse guard')
 proof={'previousRecord':str(record),'previousSource':prior['source'],'archiveSha256':prior['evidenceSha256'],'sourceCommit':commit,'identicalProductNativeAndReusedTestInputs':True,'identicalSDKAndDependencies':True,'onlyChange':'exact XLSX project-return existing readonly Retry with three controlled busy refusals and unchanged Source Save count; product unchanged, source-bound reuse plumbing','allowedChangedFiles':changed,'failedOrChangedChecksReused':False,'buildsOrPackagesOrBoundaryReused':False,'negativeGuards':['changed SDK rejected','changed product rejected'],'stages':[]};proofPath=work.evidence/('xlsx-parts-reuse-'+prior['source'][:8]+'.json');atomic_json(proofPath,proof);original=work.run
 def run(name,command,*args,**kwargs):
  if name not in rows:return original(name,command,*args,**kwargs)
  row=rows[name];normalize=lambda c,root:[str(a).replace(root,'$OWNED_WORKSPACE')for a in c]
  if kwargs.get('expected',0)!=0 or normalize(row['command'],prior['root'])!=normalize(command,str(work.root)):raise RuntimeError('XLSX reuse invocation differs: '+name)
  if any(x['name']==name for x in work.state.get('reusedChecks',[])):raise RuntimeError('DuplicateXLSX reuse refused')
  entry={'name':name,'sourceCommit':commit,'previousSource':prior['source'],'previousRecord':str(record),'archiveSha256':prior['evidenceSha256'],'kind':'identical-source-and-probeXLSX-memory-fact','SDKAndNugetIdentical':True};work.state.setdefault('reusedChecks',[]).append(entry);proof['stages'].append(name);work.save();atomic_json(proofPath,proof);atomic_json(work.evidence/(name+'.reused.json'),{'proof':proof,'priorResult':row});print(json.dumps({'stage':name,'reused':True,'previousSource':prior['source']}),flush=True);return row
 work.run=run
