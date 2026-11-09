"""Keep sealed passing checks after changing only the unexecuted conflict branch."""
import ast,json,subprocess,zipfile
from pathlib import Path
from verification_workspace import atomic_json,sha,verify_archive

def bind(repo,record,commit,inputs,work):
 prior=json.loads(Path(record).read_text());manifest=json.loads(Path(record).with_suffix('.manifest.json').read_text())
 if prior['status']!='cleaned'or sha(prior['evidence'])!=prior['evidenceSha256']or manifest['archiveSha256']!=prior['evidenceSha256']:raise RuntimeError('Sealed retained caller evidence required')
 verify_archive(prior['evidence'],manifest['files']);blob=lambda revision,name:subprocess.check_output(['git','show',revision+':'+name],cwd=repo,text=True)
 changed=subprocess.check_output(['git','diff','--name-only',prior['source'],commit],cwd=repo,text=True).splitlines();adapter='tests/web/v666_retained_callers_ui.py';allowed={adapter,'tests/web/v666_retained_callers_conflict.py','tools/verify_desktop.py','tools/verification_retained_callers_reuse.py'}
 if any(name not in allowed and not name.startswith('docs/')for name in changed):raise RuntimeError('Product or other test drift requires fresh execution')
 old=ast.parse(blob(prior['source'],adapter));new=ast.parse(blob(commit,adapter));branch=new.body[-1]
 if not isinstance(branch,ast.If)or ast.unparse(branch.test)!="x.mode == 'conflict'"or len(branch.orelse)!=1 or len(branch.body)!=1 or 'v666_retained_callers_conflict.py'not in ast.unparse(branch.body[0]):raise RuntimeError('Exact conflict-only test dispatch required')
 new.body[-1]=branch.orelse[0]
 if ast.dump(old)!=ast.dump(new):raise RuntimeError('Passing UI branches changed')
 product=json.loads(blob(commit,'docs/v666-retained-callers-delta.json'))['productFiles']
 if len(product)!=6 or any(blob(prior['source'],name)!=blob(commit,name)for name in product):raise RuntimeError('Retained caller product drift')
 with zipfile.ZipFile(prior['evidence'])as z:
  source=json.loads(z.read('source.json'));checkouts={label:json.loads(z.read(label+'-checkout.json'))for label in ['lf','crlf']}
  if source['commit']!=prior['source']or any(source['dependencyInputs'].get(k)!=inputs.get(k)for k in ['sdk','nuget','configuration','rid']):raise RuntimeError('SDK/dependency identity differs')
  for label,eol in [('lf','false'),('crlf','true')]:
   row=checkouts[label]
   if row['commit']!=prior['source']or row['coreAutocrlf']!=eol or row['noSharedGitObjects']is not True:raise RuntimeError('Independent EOL evidence differs')
  failure=z.read('crlf-retained-callers-conflict.log').decode()
  if 'Timeout 30000ms exceeded'not in failure or 'boundaryMessages.some'not in failure:raise RuntimeError('Different failed boundary requires reassessment')
 failed=[r for r in prior['results']if r['exit']!=0]
 if len(prior['results'])!=32 or len(failed)!=1 or failed[0]['name']!='crlf-retained-callers-conflict':raise RuntimeError('Exact prior outcome required')
 names={'lf-'+n for n in ['v536_mixed_declaration','v536_local_header_image','retained-callers-native','retained-callers-api','retained-callers-guards','retained-callers-review','retained-callers-late','retained-callers-late-peer','retained-callers-normal','retained-callers-storage']}|{'crlf-'+n for n in ['v536_mixed_declaration','v536_local_header_image','retained-callers-native','retained-callers-legacy','retained-callers-native-regression','retained-callers-label-regression','retained-callers-normal','retained-callers-loss']};rows={r['name']:r for r in prior['results']if r['name']in names and r['exit']==0}
 if len(names)!=18 or set(rows)!=names:raise RuntimeError('All exact passing facts required')
 proof=dict(previousRecord=str(record),previousSource=prior['source'],sourceCommit=commit,archiveSha256=prior['evidenceSha256'],identicalProductAndDependencies=True,passingBranchesAstIdentical=True,failedChecksReused=False,buildsAndPackagesReused=False,independentCheckouts=checkouts,stages=[]);original=work.run
 def run(name,command,*args,**kwargs):
  if name not in rows:return original(name,command,*args,**kwargs)
  norm=lambda cmd,root:[str(arg).replace(root,'$OWNED_WORKSPACE')for arg in cmd]
  if kwargs.get('expected',0)!=0 or norm(rows[name]['command'],prior['root'])!=norm(command,str(work.root))or name in proof['stages']:raise RuntimeError('Reused invocation differs or repeats: '+name)
  proof['stages'].append(name);work.state.setdefault('reusedChecks',[]).append(dict(name=name,sourceCommit=prior['source'],record=str(record),archiveSha256=prior['evidenceSha256']));work.save();atomic_json(work.evidence/'retained-callers-reuse.json',proof);atomic_json(work.evidence/(name+'.reused.json'),dict(proof=proof,priorResult=rows[name]));print(json.dumps(dict(stage=name,reused=True,sourceCommit=prior['source'])),flush=True);return rows[name]
 work.run=run
