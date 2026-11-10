"""Reuse five sealed passing facts after exact CRLF source fixture correction."""
import ast,json,subprocess,zipfile
from pathlib import Path
from verification_workspace import atomic_json,sha,verify_archive

def bind(repo,record,commit,inputs,work):
 prior=json.loads(Path(record).read_text());manifest=json.loads(Path(record).with_suffix('.manifest.json').read_text());blob=lambda rev,n:subprocess.check_output(['git','show',rev+':'+n],cwd=repo,text=True)
 if prior['status']!='cleaned'or sha(prior['evidence'])!=prior['evidenceSha256']or manifest['archiveSha256']!=prior['evidenceSha256']:raise RuntimeError('Sealed failed-run evidence required')
 verify_archive(prior['evidence'],manifest['files'])
 fixture='tests/web/v536_information_external_copy_ui.py';allowed={fixture,'tools/verify_desktop.py','tools/verification_native_parameters_reuse.py'};changed=subprocess.check_output(['git','diff','--name-only',prior['source'],commit],cwd=repo,text=True).splitlines()
 if not changed or any(n not in allowed and not n.startswith('docs/')for n in changed):raise RuntimeError('Product or unrelated test drift requires fresh checks')
 product=json.loads(blob(commit,'docs/v666-native-parameters-delta.json'))['productFiles']
 if len(product)!=4 or any(blob(prior['source'],n)!=blob(commit,n)for n in product):raise RuntimeError('Product source drift')
 harness=blob(commit,'tools/verify_desktop.py')
 argument="    parser.add_argument('--reuse-native-parameters',type=Path,help='Five sealed identical passing facts after exact CRLF context source fixture correction; builds and failed copy check run fresh')\n"
 hook="        if args.reuse_native_parameters:\n            if args.suite!='native-parameters':raise ValueError('Native parameter evidence requires its own suite')\n            from verification_native_parameters_reuse import bind\n            bind(repo,args.reuse_native_parameters,commit,inputs,work)\n"
 normalized_harness=harness.replace(argument,'').replace(hook,'').replace(",'verification_native_parameters_reuse.py']:","]:")
 if normalized_harness!=blob(prior['source'],'tools/verify_desktop.py'):raise RuntimeError('Harness drift beyond the guarded resume hook')
 before=blob(prior['source'],fixture);after=blob(commit,fixture)
 old="        assert any(v.get('type') == 'source' and final in v.get('text', '') for _, v in held['blueprint'])"
 new="        source_input = next(v for _, v in held['blueprint'] if v.get('type') == 'source' and v.get('text', '').replace('\\r\\n', '\\n') == final)\n        # The context editor preserves its original CRLF source transport.\n        # Compare intended C# exactly, then retain the actual bytes for Confirm.\n        final = source_input['text']"
 old_node="                        unit=next(v for v in units if v['id']==body_key+'/node:'+key.replace('/','/node:'));record=json.loads((f.project/unit['path']).read_text());assert record['source']==value and record['node']==key.split('/')[-1];original_record=json.loads((source/('Left.node.json' if key=='left/body' else 'Tap.node.json' if key=='left/tap' else 'Right.node.json')).read_text());assert record['helpers']==(enum_helpers if nested_enum and key=='left/body' else original_record['helpers'])"
 new_node="                        unit=next(v for v in units if v['id']==body_key+'/node:'+key.replace('/','/node:'));record=json.loads((f.project/unit['path']).read_text());original_record=json.loads((source/('Left.node.json' if key=='left/body' else 'Tap.node.json' if key=='left/tap' else 'Right.node.json')).read_text())\n                        expected_source=value.replace('\\r\\n','\\n');expected_source=expected_source.replace('\\n','\\r\\n') if '\\r\\n' in original_record['source'] else expected_source\n                        assert record['source']==expected_source and record['node']==key.split('/')[-1];assert record['helpers']==(enum_helpers if nested_enum and key=='left/body' else original_record['helpers'])"
 if after.replace(new,old).replace(new_node,old_node)!=before:raise RuntimeError('Fixture drift beyond exact intended C# and preserved original EOL assertions')
 failed=[r for r in prior['results']if r['exit']!=0]
 if len(prior['results'])!=12 or len(failed)!=1 or failed[0]['name']!='lf-native-parameters-copy-pins':raise RuntimeError('Exact preserved failure required')
 names={'native-parameters-owned-ipc-lifetime'}|{'lf-'+n for n in ['v536_mixed_declaration','v536_local_header_image','native-parameters-dom','native-parameters-receipts']};rows={r['name']:r for r in prior['results']if r['name']in names and r['exit']==0}
 if len(rows)!=5 or set(rows)!=names:raise RuntimeError('All exact passing facts required')
 modules=set();pending=[Path(a).name for row in rows.values()for a in row['command']if str(a).endswith('.py')]
 while pending:
  name=pending.pop();path='tests/web/'+name
  if name in modules or not(repo/path).is_file():continue
  modules.add(name);text=blob(prior['source'],path)
  if text!=blob(commit,path)or 'v536_information_external_copy_ui'in text:raise RuntimeError('Reused test depends on corrected fixture')
  for node in ast.walk(ast.parse(text)):
   imports=[n.name for n in node.names]if isinstance(node,ast.Import)else[node.module]if isinstance(node,ast.ImportFrom)and node.module else[]
   for mod in imports:
    if(repo/'tests/web'/(mod.split('.')[0]+'.py')).is_file():pending.append(mod.split('.')[0]+'.py')
 with zipfile.ZipFile(prior['evidence'])as z:
  source=json.loads(z.read('source.json'));checkout=json.loads(z.read('lf-checkout.json'));failure=z.read('lf-native-parameters-copy-pins.log').decode()
  if source['commit']!=prior['source']or any(source['dependencyInputs'].get(k)!=inputs.get(k)for k in ['sdk','nuget','configuration','rid']):raise RuntimeError('Dependency/compiler identity differs')
  if checkout['commit']!=prior['source']or checkout['coreAutocrlf']!='false'or checkout['noSharedGitObjects']is not True:raise RuntimeError('Independent LF checkout proof differs')
  if 'AssertionError'not in failure or "final in v.get('text', '')"not in failure:raise RuntimeError('Different failed copy assertion')
 proof=dict(previousRecord=str(record),previousSource=prior['source'],sourceCommit=commit,archiveSha256=prior['evidenceSha256'],identicalProductSourceAndPassingTestDependencies=True,correctedFixtureAbsentFromPassingImportClosure=sorted(modules),independentLFCheckout=checkout,failedChecksReused=False,buildsAndPackagesReused=False,stages=[]);original=work.run
 def run(name,command,*args,**kwargs):
  if name not in rows:return original(name,command,*args,**kwargs)
  normalize=lambda cmd,root:[str(arg).replace(root,'$OWNED_WORKSPACE')for arg in cmd]
  if kwargs.get('expected',0)!=0 or normalize(rows[name]['command'],prior['root'])!=normalize(command,str(work.root))or name in proof['stages']:raise RuntimeError('Reused command differs or repeats: '+name)
  proof['stages'].append(name);work.state.setdefault('reusedChecks',[]).append(dict(name=name,sourceCommit=prior['source'],record=str(record),archiveSha256=prior['evidenceSha256']));work.save();atomic_json(work.evidence/'native-parameters-reuse.json',proof);atomic_json(work.evidence/(name+'.reused.json'),dict(proof=proof,priorResult=rows[name]));print(json.dumps(dict(stage=name,reused=True,sourceCommit=prior['source'])),flush=True);return rows[name]
 work.run=run
