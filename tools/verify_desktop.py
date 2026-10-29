"""Sequential, isolated desktop verification with durable evidence/packages.

Run from Linux. This does not execute Windows apphost/WebView2, mobile, login,
inference or Library delivery. Existing repository build state is never used.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from verification_workspace import Workspace, PackageStore, MIB, atomic_json, files, sha, verify_archive


def git(repo, *args):
    return subprocess.check_output(['git', *args], cwd=repo, text=True).strip()


def resume(record):
    """Finish retention after completed integration checks, without rerunning."""
    work = Workspace.load(record)
    if work.state['status'] == 'cleaned':
        print('Already cleaned: '+str(record)); return
    for worker in work.state['workers']: work._completed(worker)
    summary = json.loads((work.evidence/'summary.json').read_text())
    entry = json.loads((work.evidence/'package.json').read_text())
    if (summary.get('allStagesPassed') is not True or entry['sourceCommit'] != work.state['source'] or
        summary['sourceCommit'] != entry['sourceCommit'] or entry['evidence'] != str(work.record.with_suffix('.zip'))):
        raise RuntimeError('No completed, source-bound package verification to resume')
    candidate = work.root/'package.zip'
    if sha(candidate) != entry['sha256']: raise RuntimeError('Prepared package changed')
    verify_archive(candidate,entry['files'])
    for label in ['lf','crlf']:
        fixtures = work.evidence/(label+'-fixtures')
        if not any(r['path'] == fixtures.relative_to(work.evidence).as_posix() for r in work.state.get('runtimeDirectories',[])):
            work.runtime_directory(fixtures)
        browser = work.root/(label+'-browser')
        if browser.exists():
            retained = work.evidence/browser.name
            shutil.move(str(browser),str(retained)); work.profile(retained)
    store = PackageStore(work.record.parent.parent/'packages')
    try:
        if entry['storeId'] != store.owner['storeId']: raise RuntimeError('Prepared package store differs')
        previous = work.evidence/'run.json'
        saved = work.evidence/'previous-archive-attempt.json'
        if previous.exists() and not saved.exists(): shutil.copy2(previous,saved)
        atomic_json(work.evidence/'retention-resume.json',{'source':entry['sourceCommit'],
            'completedStagesReused':len(work.state['results']), 'candidateSha256':sha(candidate),
            'resumerSha256':sha(__file__),'workspaceManagerSha256':sha(Path(__file__).with_name('verification_workspace.py'))})
        work.state['packagePublication']={'store':str(store.root),'candidate':candidate.name,'entry':entry}
        work.save()
    finally: store.close()
    recovered = Workspace.recover(record)
    print(json.dumps({'status':recovered.state['status'],'record':str(record),
                      'sourceCommit':entry['sourceCommit'],'diskAvailable':shutil.disk_usage(work.record.parent).free},indent=2))


def dependency_identity(sdk, seed, commit):
    result = {'sourceCommit':commit,'configuration':'Release','rid':'win-x64'}
    for label,root in [('sdk',sdk),('nuget',seed)]:
        paths = files(root); digest = hashlib.sha256(); size = 0
        for name,path in sorted(paths.items()):
            digest.update(name.encode()+b'\0'+bytes.fromhex(sha(path)));size += path.stat().st_size
        result[label]={'sha256':digest.hexdigest(),'files':len(paths),'bytes':size}
    result['identity']=hashlib.sha256(json.dumps(result,sort_keys=True).encode()).hexdigest()
    return result


def preflight(repo, persistent, commit, input_identity=None):
    # Three hard-limited 56 MiB package archives cover latest + rollback + candidate;
    # evidence/code allowance and the established 64 MiB safety stay separate.
    before = shutil.disk_usage(persistent if persistent.exists() else persistent.parent).free
    if os.stat('/tmp').st_dev == os.stat(repo).st_dev:
        raise OSError('Temporary workspace must be on the verified separate RAM filesystem')
    filesystem = subprocess.check_output(['findmnt','-T','/tmp','-n','-o','FSTYPE'],text=True).split()
    if not filesystem or any(kind not in ['tmpfs','ramfs'] for kind in filesystem):
        raise OSError('Temporary filesystem is not verified RAM: '+str(filesystem))
    memory = int(Path('/sys/fs/cgroup/memory.current').read_text())
    limit = int(Path('/sys/fs/cgroup/memory.max').read_text())
    plan = {'diskAvailable': before, 'diskSafety': 64*MIB,
            'bootstrapPeakDiskBudget': (3*56+20+4+64)*MIB,
            'ramAvailable': shutil.disk_usage('/tmp').free, 'ramFilesystemBudget': 3*1024*MIB,
            'memoryCurrent': memory, 'memoryLimit': limit,
            'additionalMemoryBudget': 7*1024*MIB, 'memorySafety': 1024*MIB,
            'existingFilesDeleted': False}
    # Once bootstrapped, existing managed archives already occupy disk. Only
    # one additional candidate plus evidence/code needs new free space.
    managed = persistent/'packages'/'index.json'
    required = (56+20+4+64)*MIB if managed.exists() else plan['bootstrapPeakDiskBudget']
    latest = json.loads(managed.read_text())['latest'] if managed.exists() else None
    if latest and latest['sourceCommit'] == commit and latest.get('inputIdentity') == input_identity:
        required = (20+4+64)*MIB  # full fresh verification; no new durable package generation
    plan['requiredAdditionalDisk'] = required
    if before < required: raise OSError('Disk preflight failed: '+json.dumps(plan))
    if plan['ramAvailable'] < plan['ramFilesystemBudget']+512*MIB:
        raise OSError('RAM filesystem preflight failed: '+json.dumps(plan))
    if limit-memory < plan['additionalMemoryBudget']+plan['memorySafety']:
        raise OSError('Memory preflight failed: '+json.dumps(plan))
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repo', type=Path)
    parser.add_argument('persistent', type=Path)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--nuget-seed', type=Path, required=True)
    parser.add_argument('--suite',choices=['headers','card-images','canvas','owned-information','owned-conversion','action-icons'],default='headers')
    args = parser.parse_args()
    repo = args.repo.resolve(); persistent = args.persistent.absolute()
    persistent.parent.mkdir(parents=True, exist_ok=True)
    commit = git(repo, 'rev-parse', args.commit+'^{commit}')
    inputs = dependency_identity(args.sdk,args.nuget_seed,commit)
    plan = preflight(repo, persistent, commit,inputs['identity'])
    if git(repo, 'status', '--porcelain', '--untracked-files=no'):
        raise RuntimeError('Tracked source has uncommitted changes')
    work = Workspace(persistent/'runs', source=commit)
    store = PackageStore(persistent/'packages')
    atomic_json(work.evidence/'preflight.json', plan)
    # The harness may be bootstrapping the previous published source. Preserve
    # the exact harness bytes as well as the product commit/tree.
    harness = work.evidence/'harness'; harness.mkdir()
    for name in ['verification_workspace.py','verify_desktop.py']:
        shutil.copy2(Path(__file__).parent/name, harness/name)
    atomic_json(work.evidence/'source.json', {'commit': commit, 'tree': git(repo,'rev-parse',commit+'^{tree}'),
                'sdk': str(args.sdk),'dependencyInputs':inputs, 'harnessSha256': {p.name:sha(p) for p in harness.iterdir()}})
    environments = {}; checkouts = {}; reports = {}
    try:
        for label, crlf in [('lf','false'),('crlf','true')]:
            checkout = work.root/label; checkouts[label] = checkout
            work.run(label+'-clone', ['git','clone','--no-hardlinks','--no-checkout','-c','core.autocrlf='+crlf,str(repo),str(checkout)])
            work.run(label+'-checkout', ['git','checkout','--detach',commit], cwd=checkout)
            if git(checkout,'rev-parse','HEAD') != commit or git(checkout,'status','--porcelain'):
                raise RuntimeError('Independent checkout differs')
            if git(checkout,'config','--get','core.autocrlf') != crlf:
                raise RuntimeError('Checkout line ending configuration differs')
            atomic_json(work.evidence/(label+'-checkout.json'), {
                'commit':commit, 'tree':git(checkout,'rev-parse','HEAD^{tree}'),
                'coreAutocrlf':crlf, 'independentGit':str(checkout/'.git'),
                'noSharedGitObjects':True, 'emptyEngineCacheBeforeBuild':not (checkout/'examples/editor-home/.confectory').exists()})
            (work.evidence/(label+'-eol.txt')).write_text(git(checkout,'ls-files','--eol')+'\n')
            dependencies = work.root/(label+'-nuget')
            shutil.copytree(args.nuget_seed, dependencies)
            state = work.root/(label+'-dotnet-home'); state.mkdir()
            fixtures = work.evidence/(label+'-fixtures'); fixtures.mkdir()
            work.runtime_directory(fixtures)
            browser = work.evidence/(label+'-browser'); browser.mkdir()
            work.profile(browser)
            # Public SDK/dependency bytes may be seeded, but engine outputs and
            # caches are independent and initially absent in each checkout.
            env = {k:v for k,v in os.environ.items() if k in ['PATH','LANG','LC_ALL','SSL_CERT_FILE','SSL_CERT_DIR','HTTPS_PROXY','HTTP_PROXY','NO_PROXY','ALL_PROXY']}
            env.update(HOME=str(state), DOTNET_ROOT=str(args.sdk), CONFECTORY_DOTNET=str(args.sdk/'dotnet'),
                DOTNET_CLI_HOME=str(state), NUGET_PACKAGES=str(dependencies),
                DOTNET_CLI_TELEMETRY_OPTOUT='1', DOTNET_SKIP_FIRST_TIME_EXPERIENCE='1',
                DOTNET_CLI_DO_NOT_USE_MSBUILD_SERVER='1', PYTHONPATH=str(checkout/'tests/web'),
                TMPDIR=str(fixtures), CONFECTORY_BROWSER_TMP=str(browser), PYTHONDONTWRITEBYTECODE='1')
            environments[label] = env
            dotnet = str(args.sdk/'dotnet')
            work.run(label+'-restore', [dotnet,'restore','Confectory.sln','--disable-parallel'], cwd=checkout, env=env)
            work.run(label+'-release', [dotnet,'build','Confectory.sln','-c','Release','--no-restore','-m:1','-nr:false','-p:UseSharedCompilation=false'], cwd=checkout, env=env)
            work.run(label+'-mcp', [dotnet,'build','targets/mcp-host','-c','Release','--no-restore','-nr:false','-p:UseSharedCompilation=false'], cwd=checkout, env=env)
            work.run(label+'-engine', [dotnet,str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'), 'build',str(checkout/'examples/editor-home/project.cpack'),'linux'], cwd=checkout, env=env)
            full = json.loads((work.evidence/(label+'-engine.log')).read_text())
            report = work.evidence/(label+'-engine.json'); reports[label] = report
            atomic_json(report, {k:full[k] for k in ['run','output','key']})
            if not Path(full['output']).is_relative_to(checkout/'examples/editor-home/.confectory'):
                raise RuntimeError('Engine wrote outside its owned checkout')
            for script in ['v536_mixed_declaration.mjs','v536_local_header_image.mjs']:
                work.run(label+'-'+Path(script).stem,['node',str(checkout/'tests/web'/script),str(checkout)],cwd=checkout,env=env)
            if args.suite in ['owned-information','owned-conversion','action-icons']:
                work.run(label+'-owned-native',[sys.executable,str(checkout/'tests/web/v666_owned_information_native.py'),str(checkout)],cwd=checkout,env=env)
                for script in ['v536_information_types.py','v536_schema_save_metadata.py']:
                    work.run(label+'-'+Path(script).stem,[sys.executable,str(checkout/'tests/web'/script),str(checkout)],cwd=checkout,env=env)
                if args.suite in ['owned-conversion','action-icons']:
                    work.run(label+'-conversion-native',[sys.executable,str(checkout/'tests/web/v666_owned_conversion_native.py'),str(checkout)],cwd=checkout,env=env)
                    cases=[('general','normal','general',[]),('reference-array','normal','ref-array',[])] if label=='lf' else [('named-detached','normal','named',['view']),('late-object','late','object',[])]
                    for name,mode,scenario,flags in cases:
                        work.run(label+'-conversion-'+name,[sys.executable,str(checkout/'tests/web/v666_owned_conversion_ui.py'),str(checkout),str(report),mode,scenario,*flags],cwd=checkout,env=env)
                    if args.suite=='action-icons':
                        work.run(label+'-action-icon-native',[sys.executable,str(checkout/'tests/web/v666_action_icon_native.py'),str(checkout)],cwd=checkout,env=env)
                        work.run(label+'-action-icon-ui',[sys.executable,str(checkout/'tests/web/v666_action_icon_ui.py'),str(checkout),str(report),'normal' if label=='lf' else 'late'],cwd=checkout,env=env)
                        work.run(label+'-action-copy-icons',[sys.executable,str(checkout/'tests/web/v666_action_icon_copy_ui.py'),str(checkout),str(report),'normal',*(['view'] if label=='crlf' else [])],cwd=checkout,env=env)
                        if label=='lf':
                            work.run(label+'-action-private-icons',[sys.executable,str(checkout/'tests/web/v666_action_icon_ui.py'),str(checkout),str(report),'normal','private'],cwd=checkout,env=env)
                    work.run(label+'-owned-regression',[sys.executable,str(checkout/'tests/web/v666_owned_information_ui.py'),str(checkout),str(report),'normal',*(['object'] if label=='crlf' else [])],cwd=checkout,env=env)
                else:
                    cases=[('primary','normal',[]),('detached','normal',['view'])] if label=='lf' else [('object','normal',['object']),('late-detached','late',['view'])]
                    for name,mode,flags in cases:
                        work.run(label+'-owned-'+name,[sys.executable,str(checkout/'tests/web/v666_owned_information_ui.py'),str(checkout),str(report),mode,*flags],cwd=checkout,env=env)
                work.run(label+'-v666-zoom-ui',[sys.executable,str(checkout/'tests/web/v666_canvas_zoom_ui.py'),str(checkout),str(report)],cwd=checkout,env=env)
                work.run(label+'-image-regression',[sys.executable,str(checkout/'tests/web/v536_card_image_ui.py'),str(checkout),str(report),'late','schema','property'],cwd=checkout,env=env)
            elif args.suite=='canvas':
                work.run(label+'-v666-zoom-reference',[sys.executable,str(checkout/'tests/probes/v666_canvas_zoom.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-v666-native-zoom',[sys.executable,str(checkout/'tests/web/v666_native_zoom_ui.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-serial-renderer',[sys.executable,str(checkout/'tests/web/v508_feature_serial_canvas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-v666-zoom-ui',[sys.executable,str(checkout/'tests/web/v666_canvas_zoom_ui.py'),str(checkout),str(report)],cwd=checkout,env=env)
                for target in ['property','function']:
                    work.run(label+'-card-'+target,[sys.executable,str(checkout/'tests/web/v536_card_image_ui.py'),str(checkout),str(report),'late','schema',target],cwd=checkout,env=env)
            elif args.suite=='card-images':
                # Same engine/renderer/CAS depth over the newly connected original cards.
                card = str(checkout/'tests/web/v536_card_image_ui.py')
                work.run(label+'-card-native',[sys.executable,str(checkout/'tests/web/v536_card_image_native.py'),str(checkout),str(report)],cwd=checkout,env=env)
                cases = ([('property-normal','normal','schema','property'),('function-normal','normal','schema','function')]
                    +[(target+'-'+mode,mode,'schema',target) for target in ['property','function'] for mode in ['storage','loss','conflict','cancel','late']]
                    +[('new-property-'+mode,mode,'schema','new-property') for mode in ['normal','late']]
                    +[('object-property-'+mode,mode,'object','object-property') for mode in ['normal','conflict']]
                    +[('new-object-'+mode,mode,'object','new-object-property') for mode in ['normal','late']]
                    +[('new-function-'+mode,mode,'schema','new-function') for mode in ['normal','late']]
                    +[('property-detached','late','schema','property','view','peer'),('function-detached','late','schema','function','view','peer')]) if label=='lf' else [
                    ('property-late','late','schema','property'),('function-late','late','schema','function'),('new-function-detached','late','schema','new-function','view','peer')]
                for name,mode,kind,*flags in cases:
                    work.run(label+'-card-'+name,[sys.executable,card,str(checkout),str(report),mode,kind,*flags],cwd=checkout,env=env)
                for kind in ['object','feature']:
                    work.run(label+'-header-'+kind,[sys.executable,str(checkout/'tests/web/v536_local_header_image_ui.py'),str(checkout),str(report),'late',kind],cwd=checkout,env=env)
                work.run(label+'-property-glyph',[sys.executable,str(checkout/'tests/web/v536_element_icon_ui.py'),str(checkout),str(report),'normal','schema','property'],cwd=checkout,env=env)
                work.run(label+'-function-glyph',[sys.executable,str(checkout/'tests/web/v536_element_icon_ui.py'),str(checkout),str(report),'normal','schema','function'],cwd=checkout,env=env)
                work.run(label+'-card-receipts',['node',str(checkout/'tests/web/v536_card_image.mjs'),str(checkout)],cwd=checkout,env=env)
                for script in ['v536_copy_read_guards_core.py','v536_local_header_image_native.py']:
                    work.run(label+'-'+Path(script).stem,[sys.executable,str(checkout/'tests/web'/script),str(checkout),str(report)],cwd=checkout,env=env)
            else:
                modes = ['normal','storage','loss','conflict','cancel','late'] if label=='lf' else ['late']
                for mode in modes:
                    work.run(label+'-ui-'+mode,[sys.executable,str(checkout/'tests/web/v536_local_header_image_ui.py'),str(checkout),str(report),mode,'object'],cwd=checkout,env=env)
                for mode in modes+(['contexts'] if label=='lf' else []):
                    work.run(label+'-feature-image-'+mode,[sys.executable,str(checkout/'tests/web/v536_local_header_image_ui.py'),str(checkout),str(report),mode,'feature'],cwd=checkout,env=env)
                work.run(label+'-feature-glyph',[sys.executable,str(checkout/'tests/web/v536_feature_icon_ui.py'),str(checkout),str(report),'contexts'],cwd=checkout,env=env)
                work.run(label+'-detached',[sys.executable,str(checkout/'tests/web/v536_local_header_image_ui.py'),str(checkout),str(report),'late','object','view','peer'],cwd=checkout,env=env)
                for script in ['v536_copy_read_guards_core.py','v536_local_header_image_native.py']:
                    work.run(label+'-'+Path(script).stem,[sys.executable,str(checkout/'tests/web'/script),str(checkout),str(report)],cwd=checkout,env=env)
            if git(checkout,'status','--porcelain'):
                raise RuntimeError('Checkout changed during verification')
        checkout = checkouts['lf']; env = environments['lf']; dotnet = str(args.sdk/'dotnet')
        package = work.root/'Windows-x64'
        work.run('windows-package',[dotnet,str(checkout/'targets/editor-desktop/bin/Release/net10.0/Confectory.dll'),'package',str(checkout),str(package)],cwd=checkout,env=env)
        work.run('windows-probe',[sys.executable,str(checkout/'tests/probes/desktop_package.py'),str(checkout),str(package)],cwd=checkout,env=env)
        packaged_report = work.evidence/'packaged-engine.json'
        atomic_json(packaged_report, {'run':[dotnet,str(package/'content/runtime/Confectory.App.dll')]})
        if args.suite in ['owned-conversion','action-icons']:
            work.run('packaged-owned-conversion',[sys.executable,str(checkout/'tests/web/v666_owned_conversion_ui.py'),str(package/'content'),str(packaged_report),'normal','ref-array'],cwd=checkout,env=env)
        elif args.suite=='owned-information':
            work.run('packaged-owned-information',[sys.executable,str(checkout/'tests/web/v666_owned_information_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        elif args.suite=='canvas':
            work.run('packaged-v666-zoom',[sys.executable,str(checkout/'tests/web/v666_canvas_zoom_ui.py'),str(package/'content'),str(packaged_report)],cwd=checkout,env=env)
            work.run('packaged-image-regression',[sys.executable,str(checkout/'tests/web/v536_local_header_image_ui.py'),str(package/'content'),str(packaged_report),'late','object'],cwd=checkout,env=env)
        elif args.suite=='card-images':
            for target in ['property','function']:
                work.run('packaged-card-'+target,[sys.executable,str(checkout/'tests/web/v536_card_image_ui.py'),str(package/'content'),str(packaged_report),'late','schema',target],cwd=checkout,env=env)
        else:
            work.run('packaged-renderer',[sys.executable,str(checkout/'tests/web/v536_local_header_image_ui.py'),str(package/'content'),str(packaged_report),'late','object'],cwd=checkout,env=env)
            work.run('packaged-feature-renderer',[sys.executable,str(checkout/'tests/web/v536_local_header_image_ui.py'),str(package/'content'),str(packaged_report),'late','feature'],cwd=checkout,env=env)
        if args.suite=='action-icons':
            work.run('packaged-action-icons',[sys.executable,str(checkout/'tests/web/v666_action_icon_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        for name in ['Confectory.Core.dll','Confectory.ElementAuthoring.dll']:
            matches = [p for p in files(package).values() if p.name==name]
            origin = checkout/('src/Confectory.Core/bin/Release/net10.0/'+name if name=='Confectory.Core.dll' else 'targets/element-authoring/bin/Release/net10.0/'+name)
            if not matches or any(sha(p)!=sha(origin) for p in matches):
                raise RuntimeError('Packaged assembly differs: '+name)
        candidate = work.root/'package.zip'
        entry = store.prepare(package,candidate,commit,work.record.with_suffix('.zip'),inputs['identity'])
        restored = work.root/'restored'; restored.mkdir()
        verify_archive(candidate, entry['files'], restored)
        # Execute the restored archive's package check, engine startup and UI,
        # not just its ZIP CRC or a manifest comparison.
        work.run('restored-probe',[sys.executable,str(checkout/'tests/probes/desktop_package.py'),str(checkout),str(restored)],cwd=checkout,env=env)
        atomic_json(packaged_report, {'run':[dotnet,str(restored/'content/runtime/Confectory.App.dll')]})
        if args.suite in ['owned-conversion','action-icons']:
            work.run('restored-owned-conversion',[sys.executable,str(checkout/'tests/web/v666_owned_conversion_ui.py'),str(restored/'content'),str(packaged_report),'late','general','view'],cwd=checkout,env=env)
        elif args.suite=='owned-information':
            work.run('restored-owned-information',[sys.executable,str(checkout/'tests/web/v666_owned_information_ui.py'),str(restored/'content'),str(packaged_report),'late','view'],cwd=checkout,env=env)
        elif args.suite=='canvas':
            work.run('restored-v666-zoom',[sys.executable,str(checkout/'tests/web/v666_canvas_zoom_ui.py'),str(restored/'content'),str(packaged_report)],cwd=checkout,env=env)
            work.run('restored-image-regression',[sys.executable,str(checkout/'tests/web/v536_local_header_image_ui.py'),str(restored/'content'),str(packaged_report),'late','feature'],cwd=checkout,env=env)
        elif args.suite=='card-images':
            for target in ['property','function']:
                work.run('restored-card-'+target,[sys.executable,str(checkout/'tests/web/v536_card_image_ui.py'),str(restored/'content'),str(packaged_report),'late','schema',target],cwd=checkout,env=env)
        else:
            work.run('restored-renderer',[sys.executable,str(checkout/'tests/web/v536_local_header_image_ui.py'),str(restored/'content'),str(packaged_report),'late','object'],cwd=checkout,env=env)
            work.run('restored-feature-renderer',[sys.executable,str(checkout/'tests/web/v536_local_header_image_ui.py'),str(restored/'content'),str(packaged_report),'late','feature'],cwd=checkout,env=env)
        if args.suite=='action-icons':
            work.run('restored-action-icons',[sys.executable,str(checkout/'tests/web/v666_action_icon_ui.py'),str(restored/'content'),str(packaged_report),'late'],cwd=checkout,env=env)
        work.run('package-failure-lifetime',[sys.executable,str(checkout/'tests/probes/desktop_package_lifetime.py'),str(checkout),str(restored)],cwd=checkout,env=env)
        if dependency_identity(args.sdk,args.nuget_seed,commit) != inputs:
            raise RuntimeError('SDK/dependency seed changed during verification; no package promotion')
        atomic_json(work.evidence/'package.json',entry)
        atomic_json(work.evidence/'summary.json',{'sourceCommit':commit,'independentCheckouts':2,
            'allStagesPassed':True,'suite':args.suite,'actualWindows':False,'actualMobile':False,'libraryDelivered':False,
            'sourceRepositoryUnchanged':git(repo,'rev-parse','HEAD'),
            'archiveBytes':candidate.stat().st_size,'diskBefore':plan['diskAvailable'],
            'diskBeforePersistence':shutil.disk_usage(persistent).free})
        # Preserve inputs/profiles/screenshots in full. Compiler/cache outputs
        # are reproducible, but keep their exact file hashes and build reports.
        generated = work.root/'generated'; generated.mkdir()
        omitted = []
        candidates = []
        for label in ['lf','crlf']:
            fixtures = work.evidence/(label+'-fixtures')
            for path in fixtures.rglob('.confectory'):
                candidates.extend(p for p in [path/'cache',path/'outputs'] if p.is_dir())
            for project in fixtures.rglob('*.csproj'):
                candidates.extend(p for p in [project.parent/'bin',project.parent/'obj'] if p.is_dir())
        for path in sorted(set(candidates),key=lambda p:len(p.parts)):
            if not path.exists(): continue  # already contained by an earlier move
            listing = {n:{'sha256':sha(p),'size':p.stat().st_size} for n,p in files(path).items()}
            omitted.append({'path':path.relative_to(work.evidence).as_posix(),'files':listing})
            shutil.move(str(path),str(generated/str(len(omitted))))
        atomic_json(work.evidence/'regenerable-outputs.json',omitted)
        # That probe deliberately puts Chromium scratch next to its checkout;
        # this parent is our new workspace, never the original repository parent.
        for path in work.root.iterdir():
            if path.name.startswith('cfb-') and path.is_dir() and not path.is_symlink():
                retained = work.evidence/path.name
                shutil.move(str(path),str(retained));work.profile(retained)
        work.state['packagePublication']={'store':str(store.root),'candidate':candidate.name,'entry':entry}
        work.save()
        work.finish(cleanup=False)
        index = store.promote(candidate,entry)
        work.cleanup()
        print(json.dumps({'status':'passed','sourceCommit':commit,'runRecord':str(work.record),
            'latest':index['latest']['sourceCommit'],'rollback':index['rollback']['sourceCommit'] if index['rollback'] else None,
            'packageBytes':entry['archiveBytes'],'diskAvailable':shutil.disk_usage(persistent).free},indent=2),flush=True)
    except BaseException as error:
        try: work.finish(error)
        except BaseException as cleanup_error:
            try: work.preserve_partial(cleanup_error)
            except BaseException as snapshot_error:
                print('Partial evidence snapshot blocked: '+str(snapshot_error),file=sys.stderr)
            print('PRESERVED workspace '+str(work.root)+'; archive/cleanup blocked: '+str(cleanup_error),file=sys.stderr)
        raise
    finally:
        store.close()


if __name__ == '__main__':
    if sys.argv[1:2] == ['--resume']:
        resume(Path(sys.argv[2]))
    else: main()
