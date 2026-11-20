"""Keep sealed source UI results after the exact package helper-path repair.

In the old LF/CRLF invocations f.repo and the script's parent identify the same
checkout, so both expressions load identical helper bytes. Only the packaged
invocation differs. Product, helper functions, assertions and dependencies must
remain identical. Builds, every package check and restore execute fresh.
"""
import json,subprocess,zipfile
from pathlib import Path
from verification_workspace import atomic_json,sha,verify_archive

def bind(repo,record,commit,inputs,work):
 prior=json.loads(Path(record).read_text());manifest=json.loads(Path(record).with_suffix('.manifest.json').read_text())
 if prior['status']!='cleaned' or sha(prior['evidence'])!=prior['evidenceSha256'] or manifest['archiveSha256']!=prior['evidenceSha256']:raise RuntimeError('Sealed native-view evidence required')
 verify_archive(prior['evidence'],manifest['files'])
 def git(*args):return subprocess.check_output(['git',*args],cwd=repo,text=True)
 adapter='tests/web/v821_document_structure_ui.py'
 allowed={adapter,'tools/verification_native_views_reuse.py','tools/verify_native_views.py'}
 if not set(git('diff','--name-only',prior['source'],commit).splitlines())<=allowed:raise RuntimeError('Product, assertion, helper or fixture drift; execute fresh')
 before=git('show',prior['source']+':'+adapter);after=git('show',commit+':'+adapter)
 old="helpers=ast.parse((f.repo/'tests/web/v821_function_document_ui.py').read_text())\nexec(compile(ast.Module(body=[node for node in helpers.body if isinstance(node,ast.FunctionDef)],type_ignores=[]),str(f.repo/'tests/web/v821_function_document_ui.py'),'exec'),globals())"
 new="helper_path=Path(__file__).with_name('v821_function_document_ui.py')\nhelpers=ast.parse(helper_path.read_text())\nexec(compile(ast.Module(body=[node for node in helpers.body if isinstance(node,ast.FunctionDef)],type_ignores=[]),str(helper_path),'exec'),globals())"
 if before.count(old)!=1 or after!=before.replace('import ast,copy,json,sys,time,uuid\n','import ast,copy,json,sys,time,uuid\nfrom pathlib import Path\n').replace(old,new):raise RuntimeError('Only exact package helper-location repair is allowed')
 build=['clone','checkout','restore','release','mcp','engine']
 lf=['document-controlled','document-normal','document-branches','native-preview','native-native','structure-normal','structure-dependency','legacy-node-names']
 crlf=['native-preview','native-native','structure-normal']
 expected=['lf-'+s for s in build+lf]+['crlf-'+s for s in build+crlf]+['windows-package','windows-package-probe','packaged-native-preview','packaged-native-native','packaged-structure']
 if [r['name']for r in prior['results']]!=expected or any(r['exit']!=0 for r in prior['results'][:-1])or prior['results'][-1]['exit']!=1:raise RuntimeError('Different prior outcome')
 with zipfile.ZipFile(prior['evidence'])as z:
  deps=json.loads(z.read('dependencies.json'))
  if any(deps[k]!=inputs[k]for k in ['sdk','nuget','configuration','rid']):raise RuntimeError('Public dependencies changed')
  for label,eol in [('lf','false'),('crlf','true')]:
   checkout=json.loads(z.read(label+'-checkout.json'))
   if checkout['commit']!=prior['source']or checkout['coreAutocrlf']!=eol or checkout['noSharedGitObjects']is not True:raise RuntimeError('Checkout proof differs')
  failure=z.read('packaged-structure.log').decode()
  if 'FileNotFoundError'not in failure or '/Windows-x64/content/tests/web/v821_function_document_ui.py'not in failure:raise RuntimeError('Different failed boundary')
 names={'lf-'+s for s in lf}|{'crlf-'+s for s in crlf};rows={r['name']:r for r in prior['results']if r['name']in names}
 proof=dict(previousRecord=str(record),previousSource=prior['source'],sourceCommit=commit,archiveSha256=prior['evidenceSha256'],identicalProductAssertionsHelpersFixturesAndDependencies=True,sourceCheckoutHelperResolvesToIdenticalBytes=True,failedChecksReused=False,buildsAndPackagesReused=False,stages=[])
 original=work.run
 def run(name,command,*args,**kwargs):
  if name not in rows:return original(name,command,*args,**kwargs)
  row=rows[name];normalize=lambda cmd,root:[str(v).replace(root,'$OWNED_WORKSPACE')for v in cmd]
  if name in proof['stages']or kwargs.get('expected',0)!=0 or normalize(row['command'],prior['root'])!=normalize(command,str(work.root)):raise RuntimeError('Reused invocation differs or repeats')
  proof['stages'].append(name);work.state.setdefault('reusedChecks',[]).append(dict(name=name,sourceCommit=prior['source'],record=str(record),archiveSha256=prior['evidenceSha256']))
  work.save();atomic_json(work.evidence/'native-views-reuse.json',proof);atomic_json(work.evidence/(name+'.reused.json'),dict(proof=proof,priorResult=row));print(json.dumps(dict(stage=name,reused=True,sourceCommit=prior['source'])),flush=True);return row
 work.run=run
