"""Source-bound Linux native-view and document-structure checks; never claims Windows execution.

Independent LF/CRLF builds, real engine/save/CAS, controlled rendering assertions,
legacy graph regression, package/full restore and owned two-generation retention.
"""
import argparse,json,os,shutil,sys
from pathlib import Path
from verify_desktop import git,dependency_identity,preflight
from verification_workspace import Workspace,PackageStore,atomic_json,files,sha,verify_archive

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('repo',type=Path);p.add_argument('persistent',type=Path);p.add_argument('--commit',required=True);p.add_argument('--sdk',required=True,type=Path);p.add_argument('--nuget-seed',required=True,type=Path)
 p.add_argument('--branch-cells',action='store_true',help='Focused fresh LF branch structure, ordinary/native regressions and package/full restore; no CRLF or Windows execution claim')
 p.add_argument('--reuse-source-ui',type=Path,help='Sealed identical LF/CRLF UI results after the exact package helper-location correction; builds/packages/restore stay fresh')
 a=p.parse_args();
 if a.branch_cells and a.reuse_source_ui:raise ValueError('Branch product changes require fresh checks')
 repo=a.repo.resolve();commit=git(repo,'rev-parse',a.commit)
 if git(repo,'rev-parse','HEAD')!=commit or git(repo,'status','--porcelain'):raise RuntimeError('Source checkout must be clean and frozen')
 inputs=dependency_identity(a.sdk,a.nuget_seed,commit)
 plan=preflight(repo,a.persistent,commit,inputs['identity'],evidence_budget=128*1024**2)
 work=Workspace(a.persistent/'runs',source=commit);store=PackageStore(a.persistent/'packages')
 print(json.dumps({'record':str(work.record),'root':str(work.root),'source':commit}),flush=True)
 try:
  atomic_json(work.evidence/'preflight.json',plan);atomic_json(work.evidence/'dependencies.json',inputs)
  if a.reuse_source_ui:
   from verification_native_views_reuse import bind
   bind(repo,a.reuse_source_ui,commit,inputs,work)
  checkouts={};environments={}
  for label,crlf in ([('lf','false')]if a.branch_cells else[('lf','false'),('crlf','true')]):
   c=work.root/label;checkouts[label]=c
   work.run(label+'-clone',['git','clone','--no-hardlinks','--no-checkout','-c','core.autocrlf='+crlf,str(repo),str(c)])
   work.run(label+'-checkout',['git','checkout','--detach',commit],cwd=c)
   if git(c,'status','--porcelain') or git(c,'rev-parse','HEAD')!=commit:raise RuntimeError('Independent checkout differs')
   atomic_json(work.evidence/(label+'-checkout.json'),dict(commit=commit,tree=git(c,'rev-parse','HEAD^{tree}'),coreAutocrlf=git(c,'config','--get','core.autocrlf'),noSharedGitObjects=True))
   (work.evidence/(label+'-eol.txt')).write_text(git(c,'ls-files','--eol')+'\n')
   deps=work.root/(label+'-nuget');shutil.copytree(a.nuget_seed,deps);home=work.root/(label+'-home');home.mkdir()
   fixtures=work.evidence/(label+'-fixtures');fixtures.mkdir();work.runtime_directory(fixtures)
   browser=work.evidence/(label+'-browser');browser.mkdir();work.profile(browser)
   env={k:v for k,v in os.environ.items()if k in ['PATH','LANG','LC_ALL','SSL_CERT_FILE','SSL_CERT_DIR','HTTPS_PROXY','HTTP_PROXY','NO_PROXY','ALL_PROXY']}
   env.update(HOME=str(home),DOTNET_ROOT=str(a.sdk),CONFECTORY_DOTNET=str(a.sdk/'dotnet'),DOTNET_CLI_HOME=str(home),NUGET_PACKAGES=str(deps),DOTNET_CLI_TELEMETRY_OPTOUT='1',DOTNET_SKIP_FIRST_TIME_EXPERIENCE='1',DOTNET_CLI_DO_NOT_USE_MSBUILD_SERVER='1',PYTHONPATH=str(c/'tests/web'),TMPDIR=str(fixtures),CONFECTORY_BROWSER_TMP=str(browser),PYTHONDONTWRITEBYTECODE='1');environments[label]=env
   dotnet=str(a.sdk/'dotnet')
   work.run(label+'-restore',[dotnet,'restore','Confectory.sln','--disable-parallel'],cwd=c,env=env)
   work.run(label+'-release',[dotnet,'build','Confectory.sln','-c','Release','--no-restore','-m:1','-nr:false','-p:UseSharedCompilation=false'],cwd=c,env=env)
   work.run(label+'-mcp',[dotnet,'build','targets/mcp-host','-c','Release','--no-restore','-nr:false','-p:UseSharedCompilation=false'],cwd=c,env=env)
   work.run(label+'-engine',[dotnet,str(c/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(c/'examples/editor-home/project.cpack'),'linux'],cwd=c,env=env)
   full=json.loads((work.evidence/(label+'-engine.log')).read_text());report=work.evidence/(label+'-engine.json');atomic_json(report,{k:full[k]for k in ['run','output','key']})
   if a.branch_cells:
    for mode in ['normal','dependency','shared','fallback','legacy']:
     work.run(label+'-branch-'+mode,[sys.executable,str(c/'tests/web/v821_branch_structure_ui.py'),str(c),str(report),mode],cwd=c,env=env,timeout=900 if mode=='normal' else 180)
    work.run(label+'-document-branches',[sys.executable,str(c/'tests/web/v821_function_document_ui.py'),str(c),str(report),'branches'],cwd=c,env=env)
    work.run(label+'-ordinary-structure',[sys.executable,str(c/'tests/web/v821_document_structure_ui.py'),str(c),str(report),'normal'],cwd=c,env=env)
    for mode in ['preview','native']:
     work.run(label+'-native-'+mode,[sys.executable,str(c/'tests/web/v821_native_views_ui.py'),str(c),str(report),mode],cwd=c,env=env)
   else:
    if label=='lf':
     work.run(label+'-document-controlled',[sys.executable,str(c/'tests/web/v821_function_document.py'),str(c)],cwd=c,env=env)
     for mode in ['normal','branches']:
      work.run(label+'-document-'+mode,[sys.executable,str(c/'tests/web/v821_function_document_ui.py'),str(c),str(report),mode],cwd=c,env=env)
    for mode in ['preview','native']:
     work.run(label+'-native-'+mode,[sys.executable,str(c/'tests/web/v821_native_views_ui.py'),str(c),str(report),mode],cwd=c,env=env)
    for mode in (['normal','dependency']if label=='lf'else['normal']):
     work.run(label+'-structure-'+mode,[sys.executable,str(c/'tests/web/v821_document_structure_ui.py'),str(c),str(report),mode],cwd=c,env=env)
    if label=='lf':
     work.run(label+'-legacy-node-names',[sys.executable,str(c/'tests/web/v666_node_names_recovery_ui.py'),str(c),str(report),'normal'],cwd=c,env=env)
   if git(c,'status','--porcelain'):raise RuntimeError('Verification changed source checkout')
  c=checkouts['lf'];env=environments['lf'];dotnet=str(a.sdk/'dotnet');package=work.root/'Windows-x64'
  work.run('windows-package',[dotnet,str(c/'targets/editor-desktop/bin/Release/net10.0/Confectory.dll'),'package',str(c),str(package)],cwd=c,env=env)
  work.run('windows-package-probe',[sys.executable,str(c/'tests/probes/desktop_package.py'),str(c),str(package)],cwd=c,env=env)
  report=work.evidence/'packaged-engine.json';atomic_json(report,{'run':[dotnet,str(package/'content/runtime/Confectory.App.dll')]})
  if a.branch_cells:
   work.run('packaged-branch-normal',[sys.executable,str(c/'tests/web/v821_branch_structure_ui.py'),str(package/'content'),str(report),'normal'],cwd=c,env=env,timeout=900)
  else:
   for mode in ['preview','native']:
    work.run('packaged-native-'+mode,[sys.executable,str(c/'tests/web/v821_native_views_ui.py'),str(package/'content'),str(report),mode],cwd=c,env=env)
   work.run('packaged-structure',[sys.executable,str(c/'tests/web/v821_document_structure_ui.py'),str(package/'content'),str(report),'normal'],cwd=c,env=env)
  candidate=work.root/'package.zip';entry=store.prepare(package,candidate,commit,work.record.with_suffix('.zip'),inputs['identity'])
  restored=work.root/'restored';restored.mkdir();verify_archive(candidate,entry['files'],restored)
  atomic_json(work.evidence/'full-restore.json',dict(files=len(entry['files']),archiveSha256=sha(candidate),allBytesVerified=True))
  report=work.evidence/'restored-engine.json';atomic_json(report,{'run':[dotnet,str(restored/'content/runtime/Confectory.App.dll')]})
  if a.branch_cells:
   work.run('restored-branch-dependency',[sys.executable,str(c/'tests/web/v821_branch_structure_ui.py'),str(restored/'content'),str(report),'dependency'],cwd=c,env=env)
  else:
   for mode in ['branches']:
    work.run('restored-document-'+mode,[sys.executable,str(c/'tests/web/v821_function_document_ui.py'),str(restored/'content'),str(report),mode],cwd=c,env=env)
  work.run('restored-native',[sys.executable,str(c/'tests/web/v821_native_views_ui.py'),str(restored/'content'),str(report),'native'],cwd=c,env=env)
  work.run('package-failure-lifetime',[sys.executable,str(c/'tests/probes/desktop_package_lifetime.py'),str(c),str(restored)],cwd=c,env=env)
  if dependency_identity(a.sdk,a.nuget_seed,commit)!=inputs:raise RuntimeError('Public dependencies changed')
  if git(repo,'rev-parse','HEAD')!=commit or git(repo,'status','--porcelain'):raise RuntimeError('Frozen source changed')
  atomic_json(work.evidence/'package.json',entry)
  atomic_json(work.evidence/'summary.json',dict(sourceCommit=commit,allStagesPassed=True,suite='branch-cells'if a.branch_cells else'native-views',freshStages=len(work.state['results']),reusedChecks=work.state.get('reusedChecks',[]),independentCheckouts=len(checkouts),actualLinux=True,actualWindows=False,actualMobile=False,fullUI=False,mockupVisualCompared=False,archiveBytes=entry['archiveBytes']))
  # Preserve user-like fixture sources/checkpoints/profiles. Reproducible build
  # outputs retain exact hashes outside the evidence archive to bound storage.
  generated=work.root/'generated';generated.mkdir();omitted=[];candidates=[]
  for label in checkouts:
   fixtures=work.evidence/(label+'-fixtures')
   for path in fixtures.rglob('.confectory'):candidates.extend(p for p in [path/'cache',path/'outputs']if p.is_dir())
   for path in fixtures.rglob('*.csproj'):candidates.extend(p for p in [path.parent/'bin',path.parent/'obj']if p.is_dir())
  for path in sorted(set(candidates),key=lambda p:len(p.parts)):
   if not path.exists():continue
   omitted.append({'path':path.relative_to(work.evidence).as_posix(),'files':{n:{'sha256':sha(p),'size':p.stat().st_size}for n,p in files(path).items()}})
   shutil.move(str(path),str(generated/str(len(omitted))))
  atomic_json(work.evidence/'regenerable-outputs.json',omitted)
  for path in work.root.iterdir():
   if path.name.startswith('cfb-')and path.is_dir()and not path.is_symlink():
    retained=work.evidence/path.name;shutil.move(str(path),str(retained));work.profile(retained)
  work.state['packagePublication']={'store':str(store.root),'candidate':candidate.name,'entry':entry};work.save();work.finish(cleanup=False);index=store.promote(candidate,entry);work.cleanup()
  print(json.dumps(dict(status='passed',sourceCommit=commit,record=str(work.record),latest=index['latest']['sourceCommit'],rollback=index['rollback']['sourceCommit'],freshStages=len(work.state['results']),reusedChecks=work.state.get('reusedChecks',[]),packageSha256=entry['sha256'],packageBytes=entry['archiveBytes'])),flush=True)
 except BaseException as error:
  try:work.finish(error)
  except BaseException as preservation_error:
   work.preserve_partial(preservation_error);print('Preserved incomplete workspace '+str(work.root),flush=True)
  raise
 finally:store.close()

if __name__=='__main__':main()
