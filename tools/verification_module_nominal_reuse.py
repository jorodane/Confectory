"""Preserve equivalent checks after using the test source's fixture directory."""
import ast,json,subprocess,zipfile
from pathlib import Path
from verification_workspace import atomic_json,sha,verify_archive

def bind(repo,record,commit,inputs,work):
 prior=json.loads(Path(record).read_text());manifest=json.loads(Path(record).with_suffix('.manifest.json').read_text())
 if prior['status']!='cleaned'or sha(prior['evidence'])!=prior['evidenceSha256']or manifest['archiveSha256']!=prior['evidenceSha256']:raise RuntimeError('Sealed nominal module evidence required')
 verify_archive(prior['evidence'],manifest['files']);blob=lambda rev,name:subprocess.check_output(['git','show',rev+':'+name],cwd=repo,text=True)
 script='tests/probes/v666_module_nominal.py';driver='tools/verify_desktop.py';allowed={script,driver,'tools/verification_module_nominal_reuse.py'}
 changed=subprocess.check_output(['git','diff','--name-only',prior['source'],commit],cwd=repo,text=True).splitlines()
 if any(name not in allowed and not name.startswith('docs/')for name in changed):raise RuntimeError('Product or unrelated test drift requires new checks')
 old="str(r/'tests/fixtures/v666_module_basic.json')";new="str(Path(__file__).resolve().parents[1]/'fixtures/v666_module_basic.json')"
 before=blob(prior['source'],script);after=blob(commit,script)
 if before.count(old)!=1 or after!=before.replace(old,new):raise RuntimeError('Only the exact fixture-root correction is reusable')
 class StripReuse(ast.NodeTransformer):
  def visit_Expr(self,node):
   if isinstance(node.value,ast.Call)and isinstance(node.value.func,ast.Attribute)and node.value.func.attr=='add_argument'and node.value.args and isinstance(node.value.args[0],ast.Constant)and node.value.args[0].value=='--reuse-module-nominal':return None
   return self.generic_visit(node)
  def visit_If(self,node):
   if ast.unparse(node.test)=='args.reuse_module_nominal':return None
   return self.generic_visit(node)
 if ast.dump(ast.parse(blob(prior['source'],driver)))!=ast.dump(StripReuse().visit(ast.parse(blob(commit,driver)))):raise RuntimeError('Existing stage routes changed')
 product=json.loads(blob(commit,'docs/v666-module-nominal-delta.json'))['productFiles']
 if len(product)!=2 or any(blob(prior['source'],name)!=blob(commit,name)for name in product):raise RuntimeError('Nominal module product source changed')
 fixture='tests/fixtures/v666_module_basic.json'
 if blob(prior['source'],fixture)!=blob(commit,fixture):raise RuntimeError('Published basic-module oracle changed')
 with zipfile.ZipFile(prior['evidence'])as z:
  source=json.loads(z.read('source.json'));checkouts={label:json.loads(z.read(label+'-checkout.json'))for label in ['lf','crlf']}
  if source['commit']!=prior['source']or any(source['dependencyInputs'].get(k)!=inputs.get(k)for k in ['sdk','nuget','configuration','rid']):raise RuntimeError('Dependency identity differs')
  for label,eol in [('lf','false'),('crlf','true')]:
   q=checkouts[label]
   if q['commit']!=prior['source']or q['coreAutocrlf']!=eol or q['noSharedGitObjects']is not True:raise RuntimeError('Independent EOL proof differs')
  failed=z.read('restored-module-nominal-native.log').decode()
  if 'FileNotFoundError'not in failed or '/restored/content/tests/fixtures/v666_module_basic.json'not in failed or 'checks": 5'not in failed:raise RuntimeError('Different failure requires new diagnosis')
 failures=[row for row in prior['results']if row['exit']!=0]
 if len(prior['results'])!=41 or len(failures)!=1 or failures[0]['name']!='restored-module-nominal-native':raise RuntimeError('Exact previous result required')
 excluded={'clone','checkout','restore','release','mcp','engine'}
 rows={row['name']:row for row in prior['results']if row['exit']==0 and any(row['name'].startswith(label+'-')and row['name'][len(label)+1:]not in excluded for label in ['lf','crlf'])}
 if len(rows)!=23:raise RuntimeError('Exact 23 passing checks required')
 # In these two invocations the engine root and executing test checkout are the
 # same directory, so old and new oracle paths name the same unchanged file.
 for label in ['lf','crlf']:
  command=rows[label+'-module-nominal-native']['command'];root=str(Path(prior['root'])/label)
  if command[1]!=root+'/'+script or command[2]!=root:raise RuntimeError('Native invocation uses a different test/engine root')
 proof=dict(previousRecord=str(record),previousSource=prior['source'],sourceCommit=commit,archiveSha256=prior['evidenceSha256'],identicalProductAndDependencies=True,onlyTestChange='Oracle uses executing test checkout, not restored application content; LF/CRLF paths resolve to the same file.',failedChecksReused=False,buildsAndPackagesReused=False,independentCheckouts=checkouts,stages=[]);original=work.run
 def run(name,command,*args,**kwargs):
  if name not in rows:return original(name,command,*args,**kwargs)
  norm=lambda cmd,root:[str(arg).replace(root,'$OWNED_WORKSPACE')for arg in cmd]
  if kwargs.get('expected',0)!=0 or norm(rows[name]['command'],prior['root'])!=norm(command,str(work.root))or name in proof['stages']:raise RuntimeError('Equivalent invocation differs or repeats: '+name)
  proof['stages'].append(name);work.state.setdefault('reusedChecks',[]).append(dict(name=name,sourceCommit=prior['source'],record=str(record),archiveSha256=prior['evidenceSha256']));work.save();atomic_json(work.evidence/'module-nominal-reuse.json',proof);atomic_json(work.evidence/(name+'.reused.json'),dict(proof=proof,priorResult=rows[name]));print(json.dumps(dict(stage=name,reused=True,sourceCommit=prior['source'])),flush=True);return rows[name]
 work.run=run
