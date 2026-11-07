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
    parser.add_argument('--reuse-review',type=Path,help='Three sealed passing UI checks after exact late-input Save-count correction; failed checks/builds/packages fresh')
    parser.add_argument('--reuse-source',type=Path,help='Ten sealed identical source checks after the property guard report argument correction')
    parser.add_argument('--reuse-description',type=Path,action='append',help='Sealed passing LF checks after exact bounded Review/paused-response fixture corrections')
    parser.add_argument('--reuse-coupled-backend',type=Path,help='Sealed completed backend checks after a UI-only recovery correction; all UI/build/package checks remain fresh')
    parser.add_argument('--reuse-coupled-ui',type=Path,help='Sealed passed UI checks with identical product and only the bounded response-wait fixture correction')
    parser.add_argument('--reuse-audio',type=Path,help='Sealed identical LF/CRLF audio checks after exact package raw-string parser correction')
    parser.add_argument('--suite',choices=['resource-description','resource-pdf','resource-office','resource-destination','resource-batch','resource-images','resource-content','resource-multi-deletion','resource-folder-deletion','resource-file-deletion','resource-file-names','resource-folder-names','resource-layout','resource-preview','resource-import','office-finder','office-io-poll','run-bounds','run-rate','startup-transport','office-active-io','run-grid','run-wide','run-auto','run-presets','run-audio','run-resolution','run-surface','run-developer','office-io','office-arrangement','office-workers','office-view','headers','card-images','canvas','owned-information','owned-conversion','action-icons','declaration-icons','pin-icons','enum-definitions','enum-values','enum-retirement','worker-badges','node-internal','node-internal-nested','node-internal-storage','node-internal-context','node-internal-branches','node-branch-exits','node-internal-copy','node-internal-copy-nested','node-internal-copy-storage','node-internal-copy-branches','node-internal-copy-context','node-internal-copy-creating','node-internal-copy-frames','node-internal-override','node-internal-external-override','root-execution','root-execution-out','root-execution-closure','root-execution-copy','root-execution-copy-creating','root-execution-override','root-execution-registered','root-execution-registered-copy','root-execution-registered-creating','root-execution-data-void','root-execution-compound-owned','root-execution-provider-import','root-execution-nonvoid','public-return-data','root-execution-providers','root-execution-nested','root-execution-native','root-execution-caller','root-execution-forwarding','root-execution-observers','root-execution-wrappers','root-execution-owned-updates','root-execution-import-observations','async-runtime','async-transition','async-completion','async-function','async-property','async-adapter','async-context','async-creating','async-new-function','async-private','async-private-returns','async-coupled','async-root-io','async-branch-creation','guidance-code-editor','guidance-values','description-recovery','source-recovery','name-recovery','route-recovery','entry-recovery','export-value-recovery','export-binding-recovery','root-return-recovery','export-removal-recovery','export-creation-recovery','root-output-order-recovery','root-input-name-recovery','root-followup-recovery','direct-creation-recovery','text-pair-recovery','root-value-rename-recovery','node-text-recovery','root-return-position-recovery','node-names-recovery','root-void-name-recovery','route-group-recovery','run-fullscreen','workspace-finder','finder-content','finder-definitions','finder-bodies','finder-defaults','declaration-reload','guidance-review','finder-modules','zoom-lifetime','native-zoom-lifetime','native-read-close','native-intent-late','async-information'],default='headers')
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
    for name in ['verification_workspace.py','verify_desktop.py','verification_coupled_reuse.py','verification_description_reuse.py','verification_source_reuse.py','verification_review_reuse.py','verification_audio_reuse.py']:
        shutil.copy2(Path(__file__).parent/name, harness/name)
    atomic_json(work.evidence/'source.json', {'commit': commit, 'tree': git(repo,'rev-parse',commit+'^{tree}'),
                'sdk': str(args.sdk),'dependencyInputs':inputs, 'harnessSha256': {p.name:sha(p) for p in harness.iterdir()}})
    environments = {}; checkouts = {}; reports = {}
    try:
        if args.reuse_audio:
            if args.suite!='run-audio':raise ValueError('Audio reuse requires its own suite')
            from verification_audio_reuse import bind
            bind(repo,args.reuse_audio,commit,inputs,work)
        if args.reuse_review:
            if args.suite!='guidance-review': raise ValueError('Review reuse requires its own suite')
            from verification_review_reuse import bind
            bind(repo,args.reuse_review,commit,inputs,work)
        if args.reuse_source:
            if args.suite!='source-recovery': raise ValueError('Source reuse requires its own suite')
            from verification_source_reuse import bind
            bind(repo,args.reuse_source,commit,inputs,work)
        if args.suite in ['resource-description','resource-pdf','resource-office','resource-destination','resource-batch','resource-images','resource-content','resource-multi-deletion','resource-folder-deletion','resource-file-deletion','resource-file-names','resource-folder-names','resource-layout','resource-preview','resource-import','office-finder','office-io-poll','run-bounds','run-rate','startup-transport','office-active-io','run-grid','run-wide','run-auto','run-presets','run-audio','run-resolution','run-surface','run-developer','run-fullscreen','workspace-finder','finder-content','finder-definitions','finder-bodies','finder-defaults','declaration-reload']:
            work.run(args.suite+'-owned-ipc-lifetime',
                [sys.executable,str(repo/'tests/probes/verification_workspace_test.py')],cwd=repo,
                env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
        if args.reuse_description:
            if args.suite!='description-recovery': raise ValueError('Description reuse requires its own suite')
            from verification_description_reuse import bind
            for record in args.reuse_description: bind(repo,record,commit,inputs,work)
        if args.reuse_coupled_backend:
            if args.suite!='async-coupled': raise ValueError('Reuse is limited to the coupled async suite')
            from verification_coupled_reuse import bind
            bind(repo,args.reuse_coupled_backend,commit,inputs,work)
        if args.reuse_coupled_ui:
            if args.suite!='async-coupled': raise ValueError('UI reuse is limited to the coupled async suite')
            from verification_coupled_reuse import bind_ui
            bind_ui(repo,args.reuse_coupled_ui,commit,inputs,work)
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
            # Existing suites keep their regression lists. The nested extension
            # selects the affected Root/private/source/ownership paths explicitly.
            if args.suite in ['node-internal','node-internal-nested','node-internal-storage','node-internal-context','node-internal-branches','node-branch-exits']:
                work.run(label+'-node-internal-api',[sys.executable,str(checkout/'tests/web/v666_node_internal_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                work.run(label+'-node-internal-void',[sys.executable,str(checkout/'tests/web/v666_node_internal_api.py'),str(checkout),str(report),'void'],cwd=checkout,env=env)
                work.run(label+'-node-internal-ui',[sys.executable,str(checkout/'tests/web/v666_node_internal_ui.py'),str(checkout),str(report),'normal' if label=='lf' else 'loss'],cwd=checkout,env=env)
            if args.suite in ['worker-badges','node-internal']:
                work.run(label+'-worker-badges-projection',['node',str(checkout/'tests/web/v666_worker_badges_projection.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-worker-badges-ui',[sys.executable,str(checkout/'tests/web/v666_worker_badges_ui.py'),str(checkout),str(report)],cwd=checkout,env=env)
                work.run(label+'-worker-badges-contributions',[sys.executable,str(checkout/'tests/web/v666_worker_badges_contributions.py'),str(checkout),str(report)],cwd=checkout,env=env)
            if args.suite in ['enum-retirement','worker-badges','node-internal']:
                work.run(label+'-information-enum-retirement',[sys.executable,str(checkout/'tests/web/v666_information_enum_retirement_ui.py'),str(checkout),str(report),'normal' if label=='lf' else 'loss',*(['view'] if label=='crlf' else [])],cwd=checkout,env=env)
                if label=='lf':
                    work.run('lf-information-enum-retirement-unedited',[sys.executable,str(checkout/'tests/web/v666_information_enum_retirement_ui.py'),str(checkout),str(report),'unedited'],cwd=checkout,env=env)
            if args.suite in ['enum-values','enum-retirement','worker-badges','node-internal']:
                work.run(label+'-information-enum-values-native',[sys.executable,str(checkout/'tests/web/v666_information_enum_values_native.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-information-enum-values-ui',[sys.executable,str(checkout/'tests/web/v666_information_enum_values_ui.py'),str(checkout),str(report),'normal' if label=='lf' else 'late',*(['view'] if label=='crlf' else [])],cwd=checkout,env=env)
                if label=='lf':
                    work.run('lf-information-enum-object-values',[sys.executable,str(checkout/'tests/web/v666_information_enum_values_ui.py'),str(checkout),str(report),'normal','object'],cwd=checkout,env=env)
            if args.suite in ['enum-definitions','enum-values','enum-retirement','worker-badges','node-internal']:
                work.run(label+'-information-enum-core',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'EnumDefinitionTests','EnumContractTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-information-enum-native',[sys.executable,str(checkout/'tests/web/v666_information_enum_native.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-information-enum-ui',[sys.executable,str(checkout/'tests/web/v666_information_enum_ui.py'),str(checkout),str(report),'normal' if label=='lf' else 'late',*(['view'] if label=='crlf' else [])],cwd=checkout,env=env)
                if label=='lf':
                    work.run('lf-information-enum-create',[sys.executable,str(checkout/'tests/web/v666_information_enum_create_ui.py'),str(checkout),str(report)],cwd=checkout,env=env)
            if args.suite in ['pin-icons','enum-definitions','enum-values','enum-retirement','worker-badges','node-internal']:
                work.run(label+'-module-pin-receipts',['node',str(checkout/'tests/web/v666_module_pin_receipts.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-module-pin-native',[sys.executable,str(checkout/'tests/web/v666_module_pin_native.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-module-pins',[sys.executable,str(checkout/'tests/web/v666_module_pin_ui.py'),str(checkout),str(report),'multi' if label=='lf' else 'late','view','a1'],cwd=checkout,env=env)
                work.run(label+'-set-output-icons',[sys.executable,str(checkout/'tests/web/v666_set_output_icon_ui.py'),str(checkout),str(report),'plan-preserve' if label=='lf' else 'late'],cwd=checkout,env=env)
                if label=='lf':
                    work.run('lf-new-set-output-icon',[sys.executable,str(checkout/'tests/web/v666_new_set_output_icon_ui.py'),str(checkout),str(report)],cwd=checkout,env=env)
            for script in ['v536_mixed_declaration.mjs','v536_local_header_image.mjs']:
                work.run(label+'-'+Path(script).stem,['node',str(checkout/'tests/web'/script),str(checkout)],cwd=checkout,env=env)
            if args.suite in ['owned-information','owned-conversion','action-icons','declaration-icons','pin-icons','enum-definitions','enum-values','enum-retirement','worker-badges','node-internal']:
                work.run(label+'-owned-native',[sys.executable,str(checkout/'tests/web/v666_owned_information_native.py'),str(checkout)],cwd=checkout,env=env)
                for script in ['v536_information_types.py','v536_schema_save_metadata.py']:
                    work.run(label+'-'+Path(script).stem,[sys.executable,str(checkout/'tests/web'/script),str(checkout)],cwd=checkout,env=env)
                if args.suite in ['owned-conversion','action-icons','declaration-icons','pin-icons','enum-definitions','enum-values','enum-retirement','worker-badges','node-internal']:
                    work.run(label+'-conversion-native',[sys.executable,str(checkout/'tests/web/v666_owned_conversion_native.py'),str(checkout)],cwd=checkout,env=env)
                    cases=[('general','normal','general',[]),('reference-array','normal','ref-array',[])] if label=='lf' else [('named-detached','normal','named',['view']),('late-object','late','object',[])]
                    for name,mode,scenario,flags in cases:
                        work.run(label+'-conversion-'+name,[sys.executable,str(checkout/'tests/web/v666_owned_conversion_ui.py'),str(checkout),str(report),mode,scenario,*flags],cwd=checkout,env=env)
                    if args.suite in ['action-icons','declaration-icons','pin-icons','enum-definitions','enum-values','enum-retirement','worker-badges','node-internal']:
                        work.run(label+'-action-icon-native',[sys.executable,str(checkout/'tests/web/v666_action_icon_native.py'),str(checkout)],cwd=checkout,env=env)
                        work.run(label+'-action-icon-ui',[sys.executable,str(checkout/'tests/web/v666_action_icon_ui.py'),str(checkout),str(report),'normal' if label=='lf' else 'late'],cwd=checkout,env=env)
                        work.run(label+'-action-copy-icons',[sys.executable,str(checkout/'tests/web/v666_action_icon_copy_ui.py'),str(checkout),str(report),'normal',*(['view'] if label=='crlf' else [])],cwd=checkout,env=env)
                        if label=='lf':
                            work.run(label+'-action-private-icons',[sys.executable,str(checkout/'tests/web/v666_action_icon_ui.py'),str(checkout),str(report),'normal','private'],cwd=checkout,env=env)
                    if args.suite in ['declaration-icons','pin-icons','enum-definitions','enum-values','enum-retirement','worker-badges','node-internal']:
                        work.run(label+'-declaration-icon-native',[sys.executable,str(checkout/'tests/web/v666_declaration_icon_native.py'),str(checkout)],cwd=checkout,env=env)
                        work.run(label+'-declaration-icons',[sys.executable,str(checkout/'tests/web/v666_declaration_icon_ui.py'),str(checkout),str(report),'normal' if label=='lf' else 'late','category' if label=='lf' else 'module',*(['view'] if label=='crlf' else [])],cwd=checkout,env=env)
                        if label=='lf':
                            work.run('lf-declaration-project',[sys.executable,str(checkout/'tests/web/v666_declaration_icon_ui.py'),str(checkout),str(report),'project','concept'],cwd=checkout,env=env)
                            work.run('lf-action-icon-project',[sys.executable,str(checkout/'tests/web/v666_action_icon_ui.py'),str(checkout),str(report),'project'],cwd=checkout,env=env)
                    work.run(label+'-owned-regression',[sys.executable,str(checkout/'tests/web/v666_owned_information_ui.py'),str(checkout),str(report),'normal',*(['object'] if label=='crlf' else [])],cwd=checkout,env=env)
                else:
                    cases=[('primary','normal',[]),('detached','normal',['view'])] if label=='lf' else [('object','normal',['object']),('late-detached','late',['view'])]
                    for name,mode,flags in cases:
                        work.run(label+'-owned-'+name,[sys.executable,str(checkout/'tests/web/v666_owned_information_ui.py'),str(checkout),str(report),mode,*flags],cwd=checkout,env=env)
                work.run(label+'-v666-zoom-ui',[sys.executable,str(checkout/'tests/web/v666_canvas_zoom_ui.py'),str(checkout),str(report)],cwd=checkout,env=env)
                work.run(label+'-image-regression',[sys.executable,str(checkout/'tests/web/v536_card_image_ui.py'),str(checkout),str(report),'late','schema','property'],cwd=checkout,env=env)
            elif args.suite=='root-execution-registered-creating':
                work.run(label+'-creating-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-creating-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'RootExecutionBranchTests','SwitchBlueprintTests','NestedBlueprintTests','BlueprintConversionTests','ExternalRefTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-creating-ownership',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'blueprint_inherited_body_retains_declaring_node_owner','blueprint_independently_declared_body_cannot_borrow_another_node_owner','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-creating-api',[sys.executable,str(checkout/'tests/web/v666_root_execution_copy_creating_api.py'),str(checkout),str(report),'--out-root','--registered-creating'],cwd=checkout,env=env)
                for mode in (['normal','project'] if label=='lf' else ['loss','late']):
                    work.run(label+'-creating-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_execution_copy_creating_ui.py'),str(checkout),str(report),mode,'--out-root','--registered-creating',*(['view'] if label=='crlf' and mode=='late' else [])],cwd=checkout,env=env)
                if label=='lf':
                    work.run('lf-creating-no-out-api',[sys.executable,str(checkout/'tests/web/v666_root_execution_copy_creating_api.py'),str(checkout),str(report),'--registered-creating'],cwd=checkout,env=env)
                    work.run('lf-owned-creation-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_copy_creating_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                    work.run('lf-saved-external-copy-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_registered_copy_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-public-return-final-cas',[sys.executable,str(checkout/'tests/web/v666_root_execution_override_cas_core.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-owned-final-read-cas',[sys.executable,str(checkout/'tests/web/v536_copy_read_guards_core.py'),str(checkout)],cwd=checkout,env=env)
            elif args.suite=='root-execution-registered-copy':
                work.run(label+'-registered-copy-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-registered-copy-api',[sys.executable,str(checkout/'tests/web/v666_root_execution_registered_copy_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                for mode in (['normal','project'] if label=='lf' else ['loss','late']):
                    work.run(label+'-registered-copy-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_execution_registered_ui.py'),str(checkout),str(report),mode,'--out-root','--registered-copy',*(['view'] if label=='crlf' and mode=='late' else [])],cwd=checkout,env=env)
                if label=='lf':
                    work.run('lf-registered-copy-no-out-api',[sys.executable,str(checkout/'tests/web/v666_root_execution_registered_copy_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                    work.run('lf-registered-provider-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_registered_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                    work.run('lf-owned-copy-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_copy_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-public-return-final-cas',[sys.executable,str(checkout/'tests/web/v666_root_execution_override_cas_core.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-owned-final-read-cas',[sys.executable,str(checkout/'tests/web/v536_copy_read_guards_core.py'),str(checkout)],cwd=checkout,env=env)
            elif args.suite=='root-execution-registered':
                work.run(label+'-registered-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-registered-api',[sys.executable,str(checkout/'tests/web/v666_root_execution_registered_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                for mode in (['normal','project'] if label=='lf' else ['loss','late']):
                    work.run(label+'-registered-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_execution_registered_ui.py'),str(checkout),str(report),mode,'--out-root',*(['view'] if label=='crlf' and mode=='late' else [])],cwd=checkout,env=env)
                if label=='lf':
                    work.run('lf-registered-no-out-api',[sys.executable,str(checkout/'tests/web/v666_root_execution_registered_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                    work.run('lf-owned-override-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_override_api.py'),str(checkout),str(report),'--out-root','--external-parent'],cwd=checkout,env=env)
                work.run(label+'-public-return-final-cas',[sys.executable,str(checkout/'tests/web/v666_root_execution_override_cas_core.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-owned-final-read-cas',[sys.executable,str(checkout/'tests/web/v536_copy_read_guards_core.py'),str(checkout)],cwd=checkout,env=env)
            elif args.suite=='root-execution-override':
                work.run(label+'-root-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-root-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'RootExecutionBranchTests','SwitchBlueprintTests','NestedBlueprintTests','BlueprintConversionTests','ExternalRefTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-root-ownership',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'blueprint_inherited_body_retains_declaring_node_owner','blueprint_independently_declared_body_cannot_borrow_another_node_owner','--require-runtime'],cwd=checkout,env=env)
                for external in [False,True]:
                    work.run(label+'-public-override-api-'+str(external),[sys.executable,str(checkout/'tests/web/v666_root_execution_override_api.py'),str(checkout),str(report),'--out-root',*(['--external-parent'] if external else [])],cwd=checkout,env=env)
                for mode in (['normal','cancel','storage','conflict'] if label=='lf' else ['loss','late','project']):
                    work.run(label+'-public-override-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_execution_override_ui.py'),str(checkout),str(report),mode,'--out-root','--external-parent'],cwd=checkout,env=env)
                if label=='lf':work.run('lf-public-override-no-out-api',[sys.executable,str(checkout/'tests/web/v666_root_execution_override_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                if label=='lf':work.run('lf-local-override-ui',[sys.executable,str(checkout/'tests/web/v666_root_execution_override_ui.py'),str(checkout),str(report),'normal','--out-root'],cwd=checkout,env=env)
                work.run(label+'-public-copy-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_copy_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                baseline='v666_node_internal_external_override_api.py' if label=='lf' else 'v666_node_internal_external_override_ui.py'
                work.run(label+'-m11-override-regression',[sys.executable,str(checkout/'tests/web'/baseline),str(checkout),str(report),*(['late'] if label=='crlf' else [])],cwd=checkout,env=env)
                work.run(label+'-public-return-final-cas',[sys.executable,str(checkout/'tests/web/v666_root_execution_override_cas_core.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-owned-final-read-cas',[sys.executable,str(checkout/'tests/web/v536_copy_read_guards_core.py'),str(checkout)],cwd=checkout,env=env)
            elif args.suite=='root-execution-copy-creating':
                work.run(label+'-root-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-root-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'RootExecutionBranchTests','SwitchBlueprintTests','NestedBlueprintTests','BlueprintConversionTests','ExternalRefTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-root-ownership',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'blueprint_inherited_body_retains_declaring_node_owner','blueprint_independently_declared_body_cannot_borrow_another_node_owner','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-public-copy-creating-api',[sys.executable,str(checkout/'tests/web/v666_root_execution_copy_creating_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-public-copy-api',[sys.executable,str(checkout/'tests/web/v666_root_execution_copy_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-public-copy-session',[sys.executable,str(checkout/'tests/web/v666_root_execution_copy_session_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                if label=='lf':work.run('lf-root-closure-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_multi_api.py'),str(checkout),str(report),'--multi-root'],cwd=checkout,env=env)
                else:work.run('crlf-root-closure-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_ui.py'),str(checkout),str(report),'loss','--multi-root'],cwd=checkout,env=env)
                for mode in (['normal','cancel','storage','conflict','project'] if label=='lf' else ['loss','late']):
                    work.run(label+'-public-copy-creating-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_execution_copy_creating_ui.py'),str(checkout),str(report),mode,*(['view'] if mode in ['storage','loss'] else []),'--out-root'],cwd=checkout,env=env)
                if label=='lf':work.run('lf-root-zero-ui',[sys.executable,str(checkout/'tests/web/v666_root_execution_zero_ui.py'),str(checkout),str(report),'--no-callers','--single-target'],cwd=checkout,env=env)
                baseline='v666_root_execution_api.py' if label=='lf' else 'v666_root_execution_ui.py'
                work.run(label+'-root-out-regression',[sys.executable,str(checkout/'tests/web'/baseline),str(checkout),str(report),*(['normal'] if label=='crlf' else []),'--out-root'],cwd=checkout,env=env)
                if label=='lf':work.run(label+'-m11-regression',[sys.executable,str(checkout/'tests/web/v666_node_internal_copy_creating_api.py'),str(checkout),str(report),'--context','--raw-copy','--refs'],cwd=checkout,env=env)
                else:work.run(label+'-m11-regression',[sys.executable,str(checkout/'tests/web/v666_node_internal_copy_creating_ui.py'),str(checkout),str(report),'loss','view','--branch','--nested','--refs'],cwd=checkout,env=env)
                work.run(label+'-owned-final-read-cas',[sys.executable,str(checkout/'tests/web/v536_copy_read_guards_core.py'),str(checkout)],cwd=checkout,env=env)
            elif args.suite=='root-execution-copy':
                work.run(label+'-root-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-root-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'RootExecutionBranchTests','SwitchBlueprintTests','NestedBlueprintTests','BlueprintConversionTests','ExternalRefTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-root-ownership',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'blueprint_inherited_body_retains_declaring_node_owner','blueprint_independently_declared_body_cannot_borrow_another_node_owner','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-public-copy-api',[sys.executable,str(checkout/'tests/web/v666_root_execution_copy_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-public-copy-session',[sys.executable,str(checkout/'tests/web/v666_root_execution_copy_session_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                if label=='lf':work.run('lf-root-closure-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_multi_api.py'),str(checkout),str(report),'--multi-root'],cwd=checkout,env=env)
                else:work.run('crlf-root-closure-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_ui.py'),str(checkout),str(report),'loss','--multi-root'],cwd=checkout,env=env)
                for mode in (['normal','cancel','storage','conflict','project'] if label=='lf' else ['loss','late']):
                    work.run(label+'-public-copy-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_execution_copy_ui.py'),str(checkout),str(report),mode,'--out-root'],cwd=checkout,env=env)
                if label=='lf':work.run('lf-root-zero-ui',[sys.executable,str(checkout/'tests/web/v666_root_execution_zero_ui.py'),str(checkout),str(report),'--no-callers','--single-target'],cwd=checkout,env=env)
                baseline='v666_root_execution_api.py' if label=='lf' else 'v666_root_execution_ui.py'
                work.run(label+'-root-out-regression',[sys.executable,str(checkout/'tests/web'/baseline),str(checkout),str(report),*(['normal'] if label=='crlf' else []),'--out-root'],cwd=checkout,env=env)
                regression='v666_node_internal_copy_api.py' if label=='lf' else 'v666_node_internal_external_override_api.py'
                work.run(label+'-m11-regression',[sys.executable,str(checkout/'tests/web'/regression),str(checkout),str(report)],cwd=checkout,env=env)
                work.run(label+'-owned-final-read-cas',[sys.executable,str(checkout/'tests/web/v536_copy_read_guards_core.py'),str(checkout)],cwd=checkout,env=env)
            elif args.suite=='root-execution-closure':
                work.run(label+'-root-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-root-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'RootExecutionBranchTests','SwitchBlueprintTests','NestedBlueprintTests','BlueprintConversionTests','ExternalRefTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-root-ownership',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'blueprint_inherited_body_retains_declaring_node_owner','blueprint_independently_declared_body_cannot_borrow_another_node_owner','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-root-api',[sys.executable,str(checkout/'tests/web/v666_root_execution_multi_api.py'),str(checkout),str(report),'--multi-root'],cwd=checkout,env=env)
                work.run(label+'-root-zero-api',[sys.executable,str(checkout/'tests/web/v666_root_execution_multi_api.py'),str(checkout),str(report),'--no-callers','--single-target'],cwd=checkout,env=env)
                for mode in (['normal','cancel','storage','conflict'] if label=='lf' else ['loss','late']):
                    work.run(label+'-root-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_execution_ui.py'),str(checkout),str(report),mode,'--multi-root'],cwd=checkout,env=env)
                if label=='lf':work.run('lf-root-zero-ui',[sys.executable,str(checkout/'tests/web/v666_root_execution_zero_ui.py'),str(checkout),str(report),'--no-callers','--single-target'],cwd=checkout,env=env)
                baseline='v666_root_execution_api.py' if label=='lf' else 'v666_root_execution_ui.py'
                work.run(label+'-root-void-regression',[sys.executable,str(checkout/'tests/web'/baseline),str(checkout),str(report),*(['normal'] if label=='crlf' else []),'--out-root'],cwd=checkout,env=env)
                regression='v666_node_branch_exit_api.py' if label=='lf' else 'v666_node_internal_external_override_api.py'
                work.run(label+'-m11-regression',[sys.executable,str(checkout/'tests/web'/regression),str(checkout),str(report)],cwd=checkout,env=env)
                work.run(label+'-owned-final-read-cas',[sys.executable,str(checkout/'tests/web/v536_copy_read_guards_core.py'),str(checkout)],cwd=checkout,env=env)
            elif args.suite=='run-bounds':
                work.run(label+'-run-bounds-boundary',[sys.executable,str(checkout/'tests/web/v666_run_bounds_copy.py'),str(checkout)],cwd=checkout,env=env)
                for test in ['v666_run_bounds_projection.mjs','v666_run_rate_projection.mjs','v666_run_surface_projection.mjs','v666_run_developer_projection.mjs']:
                    work.run(label+'-'+test[:-4],['node',str(checkout/'tests/web'/test),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-run-bounds-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'RunSurfaceTests','RunAudioTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-run-bounds-api',[sys.executable,str(checkout/'tests/web/v666_run_bounds_api.py'),str(checkout),str(report),'faults'if label=='lf'else'normal'],cwd=checkout,env=env)
                work.run(label+'-run-bounds-ui',[sys.executable,str(checkout/'tests/web/v666_run_bounds_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-surface-packet-regression',[sys.executable,str(checkout/'tests/web/v666_run_surface_api.py'),str(checkout),str(report),'maximum'if label=='lf'else'faults'],cwd=checkout,env=env)
                work.run(label+'-rate-regression',[sys.executable,str(checkout/'tests/web/v666_run_rate_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-wide-regression',[sys.executable,str(checkout/'tests/web/v666_run_wide_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-grid-regression',[sys.executable,str(checkout/'tests/web/v666_run_grid_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-legacy-developer-regression',[sys.executable,str(checkout/'tests/web/v666_run_developer_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)

            elif args.suite=='run-rate':
                work.run(label+'-run-rate-boundary',[sys.executable,str(checkout/'tests/web/v666_run_rate_copy.py'),str(checkout)],cwd=checkout,env=env)
                for test in ['v666_run_rate_projection.mjs','v666_run_surface_projection.mjs','v666_run_developer_projection.mjs']:
                    work.run(label+'-'+test[:-4],['node',str(checkout/'tests/web'/test),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-run-rate-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'RunSurfaceTests','RunAudioTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-run-rate-api',[sys.executable,str(checkout/'tests/web/v666_run_rate_api.py'),str(checkout),str(report),'faults'if label=='lf'else'normal'],cwd=checkout,env=env)
                work.run(label+'-surface-packet-regression',[sys.executable,str(checkout/'tests/web/v666_run_surface_api.py'),str(checkout),str(report),'maximum'if label=='lf'else'faults'],cwd=checkout,env=env)
                work.run(label+'-run-rate-ui',[sys.executable,str(checkout/'tests/web/v666_run_rate_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                if label=='lf':work.run('lf-surface-ui-regression',[sys.executable,str(checkout/'tests/web/v666_run_surface_ui.py'),str(checkout),str(report),'normal'],cwd=checkout,env=env)
                work.run(label+'-wide-regression',[sys.executable,str(checkout/'tests/web/v666_run_wide_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-grid-regression',[sys.executable,str(checkout/'tests/web/v666_run_grid_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-legacy-developer-regression',[sys.executable,str(checkout/'tests/web/v666_run_developer_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)

            elif args.suite=='startup-transport':
                work.run(label+'-transport-probe',[sys.executable,str(checkout/'tests/probes/browser_host_transport.py'),str(checkout),str(work.evidence/(label+'-transport-probe'))],cwd=checkout,env=env,timeout=180)
                work.run(label+'-web-ui-client',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'test_web_ui_client_coalescing_revision_retirement_and_unreplayed_retry','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-startup-transport-ui',[sys.executable,str(checkout/'tests/web/v666_startup_transport_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'cold'],cwd=checkout,env=env)
                work.run(label+'-startup-restore-ui',[sys.executable,str(checkout/'tests/web/web_ui.py'),str(checkout),str(report),'startup-restore'],cwd=checkout,env=env)
                work.run(label+'-office-arrangement-ui',[sys.executable,str(checkout/'tests/web/v666_office_arrangement_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late'],cwd=checkout,env=env)
                work.run(label+'-source-recovery-ui',[sys.executable,str(checkout/'tests/web/v666_source_recovery_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late','--out-root'],cwd=checkout,env=env)
                if label=='lf':work.run('lf-source-conflict-ui',[sys.executable,str(checkout/'tests/web/v666_source_recovery_ui.py'),str(checkout),str(report),'conflict','--out-root'],cwd=checkout,env=env)
            elif args.suite=='resource-description':
                work.run(label+'-resource-description-boundary',[sys.executable,str(checkout/'tests/web/v666_resource_description_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-description-cas',[sys.executable,str(checkout/'tests/probes/resource_descriptions_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-content-provider',[sys.executable,str(checkout/'tests/probes/resource_content_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-web-resource-contract',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'test_web_ui_scope_revision_cancellation_disposal_and_pack_locality','--require-runtime'],cwd=checkout,env=env)
                for name in ['description','file_names','layout','multi_deletion','content','pdf','office']:
                    work.run(label+'-resource-'+name+'-ui',[sys.executable,str(checkout/('tests/web/v666_resource_'+name+'_ui.py')),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-source-recovery-ui',[sys.executable,str(checkout/'tests/web/v666_source_recovery_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late','--out-root'],cwd=checkout,env=env)

            elif args.suite=='resource-pdf':
                work.run(label+'-resource-pdf-boundary',[sys.executable,str(checkout/'tests/web/v666_resource_pdf_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-pdf-unit',['node',str(checkout/'tests/web/v666_resource_pdf.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-web-resource-contract',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'test_web_ui_scope_revision_cancellation_disposal_and_pack_locality','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-resource-pdf-ui',[sys.executable,str(checkout/'tests/web/v666_resource_pdf_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                for name in ['office','images','content','preview','file_names','multi_deletion']:
                    work.run(label+'-resource-'+name+'-ui',[sys.executable,str(checkout/('tests/web/v666_resource_'+name+'_ui.py')),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-source-recovery-ui',[sys.executable,str(checkout/'tests/web/v666_source_recovery_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late','--out-root'],cwd=checkout,env=env)

            elif args.suite=='resource-office':
                work.run(label+'-resource-office-boundary',[sys.executable,str(checkout/'tests/web/v666_resource_office_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-office-unit',['node',str(checkout/'tests/web/v666_resource_office.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-office-ui',[sys.executable,str(checkout/'tests/web/v666_resource_office_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                for name in ['images','content','preview','file_names','multi_deletion']:
                    work.run(label+'-resource-'+name+'-ui',[sys.executable,str(checkout/('tests/web/v666_resource_'+name+'_ui.py')),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-source-recovery-ui',[sys.executable,str(checkout/'tests/web/v666_source_recovery_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late','--out-root'],cwd=checkout,env=env)
            elif args.suite=='resource-destination':
                work.run(label+'-resource-destination-boundary',[sys.executable,str(checkout/'tests/web/v666_resource_destination_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-destination-provider',[sys.executable,str(checkout/'tests/probes/resource_layout_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'--destination'],cwd=checkout,env=env)
                work.run(label+'-resource-destination-cas',[sys.executable,str(checkout/'tests/probes/resource_destination_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-layout-provider',[sys.executable,str(checkout/'tests/probes/resource_layout_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-destination-ui',[sys.executable,str(checkout/'tests/web/v666_resource_destination_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-layout-ui',[sys.executable,str(checkout/'tests/web/v666_resource_layout_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-single-provider',[sys.executable,str(checkout/'tests/probes/project_resources_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-batch-provider',[sys.executable,str(checkout/'tests/probes/project_resources_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'--batch'],cwd=checkout,env=env)
                work.run(label+'-resource-final-cas',[sys.executable,str(checkout/'tests/probes/project_resources_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-multi-deletion-provider',[sys.executable,str(checkout/'tests/probes/resource_multi_deletion_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-content-provider',[sys.executable,str(checkout/'tests/probes/resource_content_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-batch-ui',[sys.executable,str(checkout/'tests/web/v666_resource_batch_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-import-ui',[sys.executable,str(checkout/'tests/web/v666_resources_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-content-ui',[sys.executable,str(checkout/'tests/web/v666_resource_content_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-images-ui',[sys.executable,str(checkout/'tests/web/v666_resource_images_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-multi-deletion-ui',[sys.executable,str(checkout/'tests/web/v666_resource_multi_deletion_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-source-recovery-ui',[sys.executable,str(checkout/'tests/web/v666_source_recovery_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late','--out-root'],cwd=checkout,env=env)
            elif args.suite=='resource-batch':
                work.run(label+'-resource-batch-boundary',[sys.executable,str(checkout/'tests/web/v666_resource_batch_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-single-provider',[sys.executable,str(checkout/'tests/probes/project_resources_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-batch-provider',[sys.executable,str(checkout/'tests/probes/project_resources_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'--batch'],cwd=checkout,env=env)
                work.run(label+'-resource-final-cas',[sys.executable,str(checkout/'tests/probes/project_resources_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-multi-deletion-provider',[sys.executable,str(checkout/'tests/probes/resource_multi_deletion_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-content-provider',[sys.executable,str(checkout/'tests/probes/resource_content_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-batch-ui',[sys.executable,str(checkout/'tests/web/v666_resource_batch_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-import-ui',[sys.executable,str(checkout/'tests/web/v666_resources_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-content-ui',[sys.executable,str(checkout/'tests/web/v666_resource_content_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-images-ui',[sys.executable,str(checkout/'tests/web/v666_resource_images_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-multi-deletion-ui',[sys.executable,str(checkout/'tests/web/v666_resource_multi_deletion_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-source-recovery-ui',[sys.executable,str(checkout/'tests/web/v666_source_recovery_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late','--out-root'],cwd=checkout,env=env)
            elif args.suite=='resource-images':
                work.run(label+'-resource-images-boundary',[sys.executable,str(checkout/'tests/web/v666_resource_images_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-images-unit',['node',str(checkout/'tests/web/v666_resource_images.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-images-ui',[sys.executable,str(checkout/'tests/web/v666_resource_images_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-content-ui',[sys.executable,str(checkout/'tests/web/v666_resource_content_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-preview-ui',[sys.executable,str(checkout/'tests/web/v666_resource_preview_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-file-names-ui',[sys.executable,str(checkout/'tests/web/v666_resource_file_names_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-multi-deletion-ui',[sys.executable,str(checkout/'tests/web/v666_resource_multi_deletion_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-import-ui',[sys.executable,str(checkout/'tests/web/v666_resources_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-source-recovery-ui',[sys.executable,str(checkout/'tests/web/v666_source_recovery_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late','--out-root'],cwd=checkout,env=env)
            elif args.suite=='resource-content':
                work.run(label+'-resource-content-boundary',[sys.executable,str(checkout/'tests/web/v666_resource_content_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-content-codec',['node',str(checkout/'tests/web/v666_resource_content_codec.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-content-provider',[sys.executable,str(checkout/'tests/probes/resource_content_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-content-draft-cas',[sys.executable,str(checkout/'tests/probes/resource_content_draft_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-content-final-cas',[sys.executable,str(checkout/'tests/probes/resource_content_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-content-ui',[sys.executable,str(checkout/'tests/web/v666_resource_content_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-multi-deletion-final-cas',[sys.executable,str(checkout/'tests/probes/resource_multi_deletion_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-folder-deletion-final-cas',[sys.executable,str(checkout/'tests/probes/resource_folder_deletion_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-file-deletion-final-cas',[sys.executable,str(checkout/'tests/probes/resource_file_deletion_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-layout-final-cas',[sys.executable,str(checkout/'tests/probes/resource_layout_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-folder-names-final-cas',[sys.executable,str(checkout/'tests/probes/resource_folder_names_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-file-names-final-cas',[sys.executable,str(checkout/'tests/probes/resource_file_names_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-multi-deletion-ui',[sys.executable,str(checkout/'tests/web/v666_resource_multi_deletion_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-file-names-ui',[sys.executable,str(checkout/'tests/web/v666_resource_file_names_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-preview-ui',[sys.executable,str(checkout/'tests/web/v666_resource_preview_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-import-ui',[sys.executable,str(checkout/'tests/web/v666_resources_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-source-recovery-ui',[sys.executable,str(checkout/'tests/web/v666_source_recovery_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late','--out-root'],cwd=checkout,env=env)
            elif args.suite=='resource-multi-deletion':
                work.run(label+'-resource-multi-deletion-boundary',[sys.executable,str(checkout/'tests/web/v666_resource_multi_deletion_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-selection-adapter',['node',str(checkout/'tests/web/v666_resource_selection.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-multi-deletion-provider',[sys.executable,str(checkout/'tests/probes/resource_multi_deletion_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-multi-deletion-final-cas',[sys.executable,str(checkout/'tests/probes/resource_multi_deletion_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-multi-deletion-ui',[sys.executable,str(checkout/'tests/web/v666_resource_multi_deletion_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-folder-deletion-provider',[sys.executable,str(checkout/'tests/probes/resource_folder_deletion_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-folder-deletion-final-cas',[sys.executable,str(checkout/'tests/probes/resource_folder_deletion_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-folder-deletion-ui',[sys.executable,str(checkout/'tests/web/v666_resource_folder_deletion_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-file-deletion-provider',[sys.executable,str(checkout/'tests/probes/resource_file_deletion_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-file-deletion-final-cas',[sys.executable,str(checkout/'tests/probes/resource_file_deletion_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-file-deletion-import-final-cas',[sys.executable,str(checkout/'tests/probes/project_resources_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-file-deletion-ui',[sys.executable,str(checkout/'tests/web/v666_resource_file_deletion_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-layout-provider',[sys.executable,str(checkout/'tests/probes/resource_layout_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-layout-final-cas',[sys.executable,str(checkout/'tests/probes/resource_layout_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-folder-names-provider',[sys.executable,str(checkout/'tests/probes/resource_folder_names_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-folder-names-final-cas',[sys.executable,str(checkout/'tests/probes/resource_folder_names_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-file-names-provider',[sys.executable,str(checkout/'tests/probes/resource_file_names_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-file-names-final-cas',[sys.executable,str(checkout/'tests/probes/resource_file_names_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-file-names-ui',[sys.executable,str(checkout/'tests/web/v666_resource_file_names_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-folder-names-ui',[sys.executable,str(checkout/'tests/web/v666_resource_folder_names_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-layout-ui',[sys.executable,str(checkout/'tests/web/v666_resource_layout_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-preview-ui',[sys.executable,str(checkout/'tests/web/v666_resource_preview_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-import-ui',[sys.executable,str(checkout/'tests/web/v666_resources_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-source-recovery-ui',[sys.executable,str(checkout/'tests/web/v666_source_recovery_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late','--out-root'],cwd=checkout,env=env)
            elif args.suite=='resource-folder-deletion':
                work.run(label+'-resource-folder-deletion-boundary',[sys.executable,str(checkout/'tests/web/v666_resource_folder_deletion_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-folder-deletion-provider',[sys.executable,str(checkout/'tests/probes/resource_folder_deletion_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-folder-deletion-final-cas',[sys.executable,str(checkout/'tests/probes/resource_folder_deletion_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-folder-deletion-ui',[sys.executable,str(checkout/'tests/web/v666_resource_folder_deletion_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-file-deletion-provider',[sys.executable,str(checkout/'tests/probes/resource_file_deletion_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-file-deletion-final-cas',[sys.executable,str(checkout/'tests/probes/resource_file_deletion_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-file-deletion-import-final-cas',[sys.executable,str(checkout/'tests/probes/project_resources_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-file-deletion-ui',[sys.executable,str(checkout/'tests/web/v666_resource_file_deletion_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-layout-provider',[sys.executable,str(checkout/'tests/probes/resource_layout_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-layout-final-cas',[sys.executable,str(checkout/'tests/probes/resource_layout_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-folder-names-provider',[sys.executable,str(checkout/'tests/probes/resource_folder_names_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-folder-names-final-cas',[sys.executable,str(checkout/'tests/probes/resource_folder_names_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-file-names-provider',[sys.executable,str(checkout/'tests/probes/resource_file_names_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-file-names-final-cas',[sys.executable,str(checkout/'tests/probes/resource_file_names_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-file-names-ui',[sys.executable,str(checkout/'tests/web/v666_resource_file_names_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-folder-names-ui',[sys.executable,str(checkout/'tests/web/v666_resource_folder_names_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-layout-ui',[sys.executable,str(checkout/'tests/web/v666_resource_layout_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-preview-ui',[sys.executable,str(checkout/'tests/web/v666_resource_preview_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-import-ui',[sys.executable,str(checkout/'tests/web/v666_resources_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-source-recovery-ui',[sys.executable,str(checkout/'tests/web/v666_source_recovery_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late','--out-root'],cwd=checkout,env=env)
            elif args.suite=='resource-file-deletion':
                work.run(label+'-resource-file-deletion-boundary',[sys.executable,str(checkout/'tests/web/v666_resource_file_deletion_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-file-deletion-provider',[sys.executable,str(checkout/'tests/probes/resource_file_deletion_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-file-deletion-final-cas',[sys.executable,str(checkout/'tests/probes/resource_file_deletion_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-file-deletion-import-final-cas',[sys.executable,str(checkout/'tests/probes/project_resources_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-file-deletion-ui',[sys.executable,str(checkout/'tests/web/v666_resource_file_deletion_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-layout-provider',[sys.executable,str(checkout/'tests/probes/resource_layout_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-layout-final-cas',[sys.executable,str(checkout/'tests/probes/resource_layout_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-folder-names-provider',[sys.executable,str(checkout/'tests/probes/resource_folder_names_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-folder-names-final-cas',[sys.executable,str(checkout/'tests/probes/resource_folder_names_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-file-names-provider',[sys.executable,str(checkout/'tests/probes/resource_file_names_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-file-names-final-cas',[sys.executable,str(checkout/'tests/probes/resource_file_names_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-file-names-ui',[sys.executable,str(checkout/'tests/web/v666_resource_file_names_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-folder-names-ui',[sys.executable,str(checkout/'tests/web/v666_resource_folder_names_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-layout-ui',[sys.executable,str(checkout/'tests/web/v666_resource_layout_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-preview-ui',[sys.executable,str(checkout/'tests/web/v666_resource_preview_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-import-ui',[sys.executable,str(checkout/'tests/web/v666_resources_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-source-recovery-ui',[sys.executable,str(checkout/'tests/web/v666_source_recovery_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late','--out-root'],cwd=checkout,env=env)
            elif args.suite=='resource-file-names':
                work.run(label+'-resource-file-names-boundary',[sys.executable,str(checkout/'tests/web/v666_resource_file_names_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-layout-provider',[sys.executable,str(checkout/'tests/probes/resource_layout_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-layout-final-cas',[sys.executable,str(checkout/'tests/probes/resource_layout_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-folder-names-provider',[sys.executable,str(checkout/'tests/probes/resource_folder_names_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-folder-names-final-cas',[sys.executable,str(checkout/'tests/probes/resource_folder_names_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-file-names-provider',[sys.executable,str(checkout/'tests/probes/resource_file_names_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-file-names-final-cas',[sys.executable,str(checkout/'tests/probes/resource_file_names_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-file-names-ui',[sys.executable,str(checkout/'tests/web/v666_resource_file_names_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-folder-names-ui',[sys.executable,str(checkout/'tests/web/v666_resource_folder_names_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-layout-ui',[sys.executable,str(checkout/'tests/web/v666_resource_layout_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-preview-ui',[sys.executable,str(checkout/'tests/web/v666_resource_preview_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-import-ui',[sys.executable,str(checkout/'tests/web/v666_resources_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-source-recovery-ui',[sys.executable,str(checkout/'tests/web/v666_source_recovery_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late','--out-root'],cwd=checkout,env=env)
            elif args.suite=='resource-folder-names':
                work.run(label+'-resource-folder-names-boundary',[sys.executable,str(checkout/'tests/web/v666_resource_folder_names_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-layout-provider',[sys.executable,str(checkout/'tests/probes/resource_layout_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-layout-final-cas',[sys.executable,str(checkout/'tests/probes/resource_layout_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-folder-names-provider',[sys.executable,str(checkout/'tests/probes/resource_folder_names_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-folder-names-final-cas',[sys.executable,str(checkout/'tests/probes/resource_folder_names_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-folder-names-ui',[sys.executable,str(checkout/'tests/web/v666_resource_folder_names_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-layout-ui',[sys.executable,str(checkout/'tests/web/v666_resource_layout_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-preview-ui',[sys.executable,str(checkout/'tests/web/v666_resource_preview_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-import-ui',[sys.executable,str(checkout/'tests/web/v666_resources_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-source-recovery-ui',[sys.executable,str(checkout/'tests/web/v666_source_recovery_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late','--out-root'],cwd=checkout,env=env)
            elif args.suite=='resource-layout':
                work.run(label+'-resource-layout-boundary',[sys.executable,str(checkout/'tests/web/v666_resource_layout_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-layout-provider',[sys.executable,str(checkout/'tests/probes/resource_layout_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-layout-final-cas',[sys.executable,str(checkout/'tests/probes/resource_layout_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-layout-ui',[sys.executable,str(checkout/'tests/web/v666_resource_layout_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-preview-ui',[sys.executable,str(checkout/'tests/web/v666_resource_preview_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-import-ui',[sys.executable,str(checkout/'tests/web/v666_resources_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-source-recovery-ui',[sys.executable,str(checkout/'tests/web/v666_source_recovery_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late','--out-root'],cwd=checkout,env=env)
            elif args.suite=='resource-preview':
                work.run(label+'-resource-preview-boundary',[sys.executable,str(checkout/'tests/web/v666_resource_preview_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-preview-ui',[sys.executable,str(checkout/'tests/web/v666_resource_preview_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-resource-import-ui',[sys.executable,str(checkout/'tests/web/v666_resources_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-body-finder-ui',[sys.executable,str(checkout/'tests/web/v666_finder_bodies_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
            elif args.suite=='resource-import':
                work.run(label+'-resource-boundary',[sys.executable,str(checkout/'tests/web/v666_resources_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-provider',[sys.executable,str(checkout/'tests/probes/project_resources_test.py'),str(checkout),str(checkout/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll')],cwd=checkout,env=env)
                work.run(label+'-resource-final-cas',[sys.executable,str(checkout/'tests/probes/project_resources_cas.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-resource-ui',[sys.executable,str(checkout/'tests/web/v666_resources_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-office-finder-ui',[sys.executable,str(checkout/'tests/web/v666_office_finder_ui.py'),str(checkout),str(report),'live'if label=='lf'else'cold'],cwd=checkout,env=env)
                work.run(label+'-panel-finder-ui',[sys.executable,str(checkout/'tests/web/v666_workspace_finder_ui.py'),str(checkout),str(report),'basic'if label=='lf'else'scope'],cwd=checkout,env=env)
                work.run(label+'-body-finder-ui',[sys.executable,str(checkout/'tests/web/v666_finder_bodies_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-office-arrangement-ui',[sys.executable,str(checkout/'tests/web/v666_office_arrangement_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late'],cwd=checkout,env=env)
                work.run(label+'-source-recovery-ui',[sys.executable,str(checkout/'tests/web/v666_source_recovery_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late','--out-root'],cwd=checkout,env=env)
                if label=='lf':work.run('lf-source-conflict-ui',[sys.executable,str(checkout/'tests/web/v666_source_recovery_ui.py'),str(checkout),str(report),'conflict','--out-root'],cwd=checkout,env=env)
            elif args.suite=='office-finder':
                work.run(label+'-office-finder-boundary',[sys.executable,str(checkout/'tests/web/v666_office_finder_copy.py'),str(checkout)],cwd=checkout,env=env)
                for test in ['v666_office_finder_projection.mjs','v666_finder_content_projection.mjs','v666_finder_bodies_projection.mjs','v666_finder_defaults_projection.mjs']:
                    work.run(label+'-'+test[:-4],['node',str(checkout/'tests/web'/test),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-office-finder-ui',[sys.executable,str(checkout/'tests/web/v666_office_finder_ui.py'),str(checkout),str(report),'live'if label=='lf'else'cold'],cwd=checkout,env=env)
                work.run(label+'-panel-finder-ui',[sys.executable,str(checkout/'tests/web/v666_workspace_finder_ui.py'),str(checkout),str(report),'basic'if label=='lf'else'scope'],cwd=checkout,env=env)
                work.run(label+'-body-finder-ui',[sys.executable,str(checkout/'tests/web/v666_finder_bodies_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-office-view-ui',[sys.executable,str(checkout/'tests/web/v666_office_view_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'cold'],cwd=checkout,env=env)
                work.run(label+'-office-arrangement-ui',[sys.executable,str(checkout/'tests/web/v666_office_arrangement_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late'],cwd=checkout,env=env)
                if label=='lf':work.run('lf-panel-finder-load',[sys.executable,str(checkout/'tests/web/v666_workspace_finder_ui.py'),str(checkout),str(report),'load'],cwd=checkout,env=env)

            elif args.suite=='office-io-poll':
                work.run(label+'-office-poll-boundary',[sys.executable,str(checkout/'tests/web/v666_office_io_poll_copy.py'),str(checkout)],cwd=checkout,env=env)
                for test in ['v666_office_workers_projection.mjs','v666_worker_badges_projection.mjs']:
                    work.run(label+'-'+test[:-4],['node',str(checkout/'tests/web'/test),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-active-io-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'ActiveToolIOTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-completed-io-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'test_development_tools_owned_scope_shared_draft_no_confirm_and_locality','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-actual-io-ui',[sys.executable,str(checkout/'tests/web/v666_office_workers_ui.py'),str(checkout),str(report),'phase-live'if label=='lf'else'phase-fail'],cwd=checkout,env=env)
                work.run(label+'-completed-io-ui',[sys.executable,str(checkout/'tests/web/v666_office_workers_ui.py'),str(checkout),str(report),'io'if label=='lf'else'io-cold'],cwd=checkout,env=env)
                work.run(label+'-arrangement-ui',[sys.executable,str(checkout/'tests/web/v666_office_arrangement_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late'],cwd=checkout,env=env)
                work.run(label+'-source-recovery-ui',[sys.executable,str(checkout/'tests/web/v666_source_recovery_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late','--out-root'],cwd=checkout,env=env)
                if label=='lf':work.run('lf-source-conflict-ui',[sys.executable,str(checkout/'tests/web/v666_source_recovery_ui.py'),str(checkout),str(report),'conflict','--out-root'],cwd=checkout,env=env)

            elif args.suite=='office-active-io':
                work.run(label+'-office-active-boundary',[sys.executable,str(checkout/'tests/web/v666_office_active_io_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-office-active-projection',['node',str(checkout/'tests/web/v666_office_workers_projection.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-worker-badges-projection',['node',str(checkout/'tests/web/v666_worker_badges_projection.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-office-active-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'ActiveToolIOTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-office-completed-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'test_development_tools_owned_scope_shared_draft_no_confirm_and_locality','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-office-active-ui',[sys.executable,str(checkout/'tests/web/v666_office_workers_ui.py'),str(checkout),str(report),'phase-ui'if label=='lf'else'phase-cold'],cwd=checkout,env=env)
                work.run(label+'-office-completed-ui',[sys.executable,str(checkout/'tests/web/v666_office_workers_ui.py'),str(checkout),str(report),'io'if label=='lf'else'io-cold'],cwd=checkout,env=env)
                work.run(label+'-office-arrangement-ui',[sys.executable,str(checkout/'tests/web/v666_office_arrangement_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late'],cwd=checkout,env=env)
                work.run(label+'-run-grid-ui',[sys.executable,str(checkout/'tests/web/v666_run_grid_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)

            elif args.suite=='office-io':
                work.run(label+'-office-io-boundary',[sys.executable,str(checkout/'tests/web/v666_office_io_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-office-io-projection',['node',str(checkout/'tests/web/v666_office_workers_projection.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-office-io-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'test_development_tools_owned_scope_shared_draft_no_confirm_and_locality','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-office-io-ui',[sys.executable,str(checkout/'tests/web/v666_office_workers_ui.py'),str(checkout),str(report),'io'if label=='lf'else'io-cold'],cwd=checkout,env=env)
                work.run(label+'-b2-projection-regression',['node',str(checkout/'tests/web/v666_worker_badges_projection.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-office-arrangement-regression',[sys.executable,str(checkout/'tests/web/v666_office_arrangement_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late'],cwd=checkout,env=env)
                work.run(label+'-office-view-regression',[sys.executable,str(checkout/'tests/web/v666_office_view_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late'],cwd=checkout,env=env)
                if label=='crlf':work.run('crlf-office-unavailable-regression',[sys.executable,str(checkout/'tests/web/v666_office_view_ui.py'),str(checkout),str(report),'unavailable'],cwd=checkout,env=env)
            elif args.suite=='office-arrangement':
                work.run(label+'-office-arrangement-boundary',[sys.executable,str(checkout/'tests/web/v666_office_arrangement_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-office-arrangement-projection',['node',str(checkout/'tests/web/v666_office_arrangement_projection.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-office-arrangement-ui',[sys.executable,str(checkout/'tests/web/v666_office_arrangement_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late'],cwd=checkout,env=env)
                work.run(label+'-office-workers-projection',['node',str(checkout/'tests/web/v666_office_workers_projection.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-b2-projection-regression',['node',str(checkout/'tests/web/v666_worker_badges_projection.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-office-workers-regression',[sys.executable,str(checkout/'tests/web/v666_office_workers_ui.py'),str(checkout),str(report),'live'if label=='lf'else'cold'],cwd=checkout,env=env)
                work.run(label+'-office-view-regression',[sys.executable,str(checkout/'tests/web/v666_office_view_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late'],cwd=checkout,env=env)
                if label=='crlf':work.run('crlf-office-unavailable-regression',[sys.executable,str(checkout/'tests/web/v666_office_view_ui.py'),str(checkout),str(report),'unavailable'],cwd=checkout,env=env)
            elif args.suite=='office-workers':
                work.run(label+'-office-workers-boundary',[sys.executable,str(checkout/'tests/web/v666_office_workers_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-office-workers-projection',['node',str(checkout/'tests/web/v666_office_workers_projection.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-b2-projection-regression',['node',str(checkout/'tests/web/v666_worker_badges_projection.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-office-workers-ui',[sys.executable,str(checkout/'tests/web/v666_office_workers_ui.py'),str(checkout),str(report),'live'if label=='lf'else'cold'],cwd=checkout,env=env)
                work.run(label+'-office-view-regression',[sys.executable,str(checkout/'tests/web/v666_office_view_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late'],cwd=checkout,env=env)
                if label=='crlf':work.run('crlf-office-unavailable-regression',[sys.executable,str(checkout/'tests/web/v666_office_view_ui.py'),str(checkout),str(report),'unavailable'],cwd=checkout,env=env)

            elif args.suite=='office-view':
                work.run(label+'-office-source-boundary',[sys.executable,str(checkout/'tests/web/v666_office_view_copy.py'),str(checkout)],cwd=checkout,env=env)
                for mode in (['normal','interrupted']if label=='lf'else['cold','late','unavailable','tampered']):
                    work.run(label+'-office-'+mode,[sys.executable,str(checkout/'tests/web/v666_office_view_ui.py'),str(checkout),str(report),mode],cwd=checkout,env=env)
                regression='v666_native_intent_late_ui.py'if label=='lf'else'v666_zoom_lifetime_ui.py'
                work.run(label+'-existing-editor-regression',[sys.executable,str(checkout/'tests/web'/regression),str(checkout),str(report),'normal'],cwd=checkout,env=env)

            elif args.suite=='native-intent-late':
                work.run(label+'-native-intent-boundary',[sys.executable,str(checkout/'tests/web/v666_native_intent_late_copy.py'),str(checkout)],cwd=checkout,env=env)
                for mode in (['normal','aba']if label=='lf'else['failure','cold']):
                    work.run(label+'-native-intent-'+mode,[sys.executable,str(checkout/'tests/web/v666_native_intent_late_ui.py'),str(checkout),str(report),mode],cwd=checkout,env=env)
                regression='v666_native_read_close_ui.py'if label=='lf'else'v666_native_zoom_lifetime_ui.py'
                work.run(label+'-native-lifecycle-regression',[sys.executable,str(checkout/'tests/web'/regression),str(checkout),str(report),'normal'if label=='lf'else'exhausted'],cwd=checkout,env=env)

            elif args.suite=='native-read-close':
                work.run(label+'-native-read-close-boundary',[sys.executable,str(checkout/'tests/web/v666_native_read_close_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-native-read-close-ui',[sys.executable,str(checkout/'tests/web/v666_native_read_close_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'failure'],cwd=checkout,env=env)
                work.run(label+'-native-zoom-regression',[sys.executable,str(checkout/'tests/web/v666_native_zoom_lifetime_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'exhausted'],cwd=checkout,env=env)

            elif args.suite=='native-zoom-lifetime':
                work.run(label+'-native-zoom-boundary',[sys.executable,str(checkout/'tests/web/v666_native_zoom_lifetime_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-native-zoom-module',[sys.executable,str(checkout/'tests/web/v666_native_zoom_ui.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-native-zoom-engine',[sys.executable,str(checkout/'tests/web/v666_native_zoom_lifetime_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'exhausted'],cwd=checkout,env=env)
                work.run(label+'-workspace-zoom-regression',[sys.executable,str(checkout/'tests/web/v666_zoom_lifetime_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'scope'],cwd=checkout,env=env)

            elif args.suite=='zoom-lifetime':
                work.run(label+'-zoom-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_zoom_lifetime_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-zoom-authored-reference',[sys.executable,str(checkout/'tests/probes/v666_canvas_zoom.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-zoom-lifetime-ui',[sys.executable,str(checkout/'tests/web/v666_zoom_lifetime_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'scope'],cwd=checkout,env=env)
                work.run(label+'-blueprint-zoom-regression',[sys.executable,str(checkout/'tests/web/v666_canvas_zoom_ui.py'),str(checkout),str(report)],cwd=checkout,env=env)

            elif args.suite=='finder-modules':
                work.run(label+'-module-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_finder_modules_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-module-authored-reference',[sys.executable,str(checkout/'tests/web/v666_finder_modules_reference.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-module-ui',[sys.executable,str(checkout/'tests/web/v666_finder_modules_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-module-content-lifecycle',[sys.executable,str(checkout/'tests/web/v666_finder_content_ui.py'),str(checkout),str(report),'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-module-definition-regression',[sys.executable,str(checkout/'tests/web/v666_finder_definitions_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)

            elif args.suite=='declaration-reload':
                work.run(label+'-declaration-reload-boundary',[sys.executable,str(checkout/'tests/web/v666_declaration_reload_copy.py'),str(checkout)],cwd=checkout,env=env)
                cases=[('normal',[]),('late',['view']),('failure',[]),('conflict',[])] if label=='lf' else [('normal',['view']),('late',[]),('scope',[])]
                for mode,flags in cases:
                    work.run(label+'-declaration-reload-'+mode,[sys.executable,str(checkout/'tests/web/v666_declaration_reload_ui.py'),str(checkout),str(report),mode,*flags],cwd=checkout,env=env)
                headers=[('mixed-preserve','category',[]),('normal','module',['view'])] if label=='lf' else [('cancel-late','category',['view'])]
                for mode,kind,flags in headers:
                    work.run(label+'-declaration-header-'+mode,[sys.executable,str(checkout/'tests/web/v666_declaration_icon_ui.py'),str(checkout),str(report),mode,kind,*flags],cwd=checkout,env=env)
                if label=='crlf':
                    work.run(label+'-run-fullscreen-regression',[sys.executable,str(checkout/'tests/web/v666_run_fullscreen_ui.py'),str(checkout),str(report),'normal'],cwd=checkout,env=env)

            elif args.suite in ['finder-content','finder-definitions','finder-bodies','finder-defaults']:
                work.run(label+'-finder-content-source-boundary',[sys.executable,str(checkout/'tests/web/v666_finder_content_copy.py'),str(checkout)],cwd=checkout,env=env)
                if args.suite in ['finder-definitions','finder-bodies','finder-defaults']:
                    mode='normal' if label=='lf' else 'lifecycle'
                    work.run(label+'-finder-definitions-'+mode,[sys.executable,str(checkout/'tests/web/v666_finder_definitions_ui.py'),str(checkout),str(report),mode],cwd=checkout,env=env)
                if args.suite in ['finder-bodies','finder-defaults']:
                    work.run(label+'-finder-entry-bindings',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'FinderBindingTests'],cwd=checkout,env=env)
                    work.run(label+'-finder-body-receipts',['node',str(checkout/'tests/web/v666_finder_bodies_projection.mjs'),str(checkout)],cwd=checkout,env=env)
                    for mode in (['normal','guards'] if label=='lf' else ['normal','lifecycle']):
                        work.run(label+'-finder-bodies-'+mode,[sys.executable,str(checkout/'tests/web/v666_finder_bodies_ui.py'),str(checkout),str(report),mode],cwd=checkout,env=env)
                if args.suite=='finder-defaults':
                    work.run(label+'-finder-default-projection',['node',str(checkout/'tests/web/v666_finder_defaults_projection.mjs'),str(checkout)],cwd=checkout,env=env)
                    mode='normal' if label=='lf' else 'lifecycle'
                    work.run(label+'-finder-defaults-'+mode,[sys.executable,str(checkout/'tests/web/v666_finder_defaults_ui.py'),str(checkout),str(report),mode],cwd=checkout,env=env)
                work.run(label+'-finder-content-controller',['node',str(checkout/'tests/web/v666_finder_content_projection.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-finder-visible-guards',[sys.executable,str(checkout/'tests/web/v666_workspace_finder_renderer.py'),str(checkout)],cwd=checkout,env=env)
                for mode in ['basic','lifecycle']:
                    work.run(label+'-finder-content-'+mode,[sys.executable,str(checkout/'tests/web/v666_finder_content_ui.py'),str(checkout),str(report),mode],cwd=checkout,env=env)
                mode='scope' if label=='lf' else 'load'
                work.run(label+'-finder-projection-regression',[sys.executable,str(checkout/'tests/web/v666_workspace_finder_ui.py'),str(checkout),str(report),mode],cwd=checkout,env=env)
                if label=='lf':
                    work.run(label+'-placed-find-ime-regression',[sys.executable,str(checkout/'tests/web/v536_find_ime.py'),str(checkout)],cwd=checkout,env=env)
                else:
                    work.run(label+'-run-fullscreen-regression',[sys.executable,str(checkout/'tests/web/v666_run_fullscreen_ui.py'),str(checkout),str(report),'normal'],cwd=checkout,env=env)

            elif args.suite=='workspace-finder':
                work.run(label+'-workspace-finder-source-boundary',[sys.executable,str(checkout/'tests/web/v666_workspace_finder_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-workspace-finder-guards',[sys.executable,str(checkout/'tests/web/v666_workspace_finder_renderer.py'),str(checkout)],cwd=checkout,env=env)
                if label=='lf':
                    work.run(label+'-placed-find-ime-regression',[sys.executable,str(checkout/'tests/web/v536_find_ime.py'),str(checkout)],cwd=checkout,env=env)
                else:
                    work.run(label+'-run-fullscreen-regression',[sys.executable,str(checkout/'tests/web/v666_run_fullscreen_ui.py'),str(checkout),str(report),'normal'],cwd=checkout,env=env)
                for mode in (['basic','scope','load']if label=='lf'else['basic','scope']):
                    work.run(label+'-workspace-finder-'+mode,[sys.executable,str(checkout/'tests/web/v666_workspace_finder_ui.py'),str(checkout),str(report),mode],cwd=checkout,env=env)

            elif args.suite=='run-wide':
                work.run(label+'-run-wide-copy',[sys.executable,str(checkout/'tests/web/v666_run_wide_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-run-wide-projection',['node',str(checkout/'tests/web/v666_run_wide_projection.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-run-wide-ui',[sys.executable,str(checkout/'tests/web/v666_run_wide_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-run-size-legacy',['node',str(checkout/'tests/web/v666_run_resolution_projection.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-run-surface-shape',['node',str(checkout/'tests/web/v666_run_surface_projection.mjs'),str(checkout)],cwd=checkout,env=env)
                for mode in ['wide','capabilities']:
                    work.run(label+'-run-wide-api-'+mode,[sys.executable,str(checkout/'tests/web/v666_run_wide_api.py'),str(checkout),str(report),mode],cwd=checkout,env=env)
                for mode in ['maximum','faults','heartbeat']:
                    work.run(label+'-run-original-api-'+mode,[sys.executable,str(checkout/'tests/web/v666_run_surface_api.py'),str(checkout),str(report),mode],cwd=checkout,env=env)
                work.run(label+'-run-auto-ui',[sys.executable,str(checkout/'tests/web/v666_run_auto_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-run-presets-api',[sys.executable,str(checkout/'tests/web/v666_run_presets_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                work.run(label+'-run-presets-ui',[sys.executable,str(checkout/'tests/web/v666_run_presets_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-run-resolution-ui',[sys.executable,str(checkout/'tests/web/v666_run_resolution_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-run-audio-ui',[sys.executable,str(checkout/'tests/web/v666_run_audio_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-run-view-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'RunSurfaceTests','test_web_ui_read_observations','test_web_ui_scope_revision_cancellation_disposal_and_pack_locality','--require-runtime'],cwd=checkout,env=env)

            elif args.suite=='run-grid':
                work.run(label+'-run-grid-copy',[sys.executable,str(checkout/'tests/web/v666_run_grid_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-run-grid-geometry',['node',str(checkout/'tests/web/v666_run_grid_projection.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-run-grid-ui',[sys.executable,str(checkout/'tests/web/v666_run_grid_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                if label=='lf':
                    work.run(label+'-run-grid-unavailable',[sys.executable,str(checkout/'tests/web/v666_run_grid_ui.py'),str(checkout),str(report),'unsupported'],cwd=checkout,env=env)
                work.run(label+'-run-wide-ui',[sys.executable,str(checkout/'tests/web/v666_run_wide_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-run-auto-ui',[sys.executable,str(checkout/'tests/web/v666_run_auto_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-run-presets-api',[sys.executable,str(checkout/'tests/web/v666_run_presets_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                work.run(label+'-run-presets-ui',[sys.executable,str(checkout/'tests/web/v666_run_presets_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-run-resolution-ui',[sys.executable,str(checkout/'tests/web/v666_run_resolution_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-run-audio-ui',[sys.executable,str(checkout/'tests/web/v666_run_audio_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-run-view-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'RunSurfaceTests','test_web_ui_read_observations','test_web_ui_scope_revision_cancellation_disposal_and_pack_locality','--require-runtime'],cwd=checkout,env=env)

            elif args.suite=='run-auto':
                work.run(label+'-run-auto-copy',[sys.executable,str(checkout/'tests/web/v666_run_auto_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-run-auto-state',['node',str(checkout/'tests/web/v666_run_auto_state.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-run-auto-ui',[sys.executable,str(checkout/'tests/web/v666_run_auto_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-run-presets-api',[sys.executable,str(checkout/'tests/web/v666_run_presets_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                work.run(label+'-run-presets-ui',[sys.executable,str(checkout/'tests/web/v666_run_presets_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-run-resolution-ui',[sys.executable,str(checkout/'tests/web/v666_run_resolution_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-run-audio-ui',[sys.executable,str(checkout/'tests/web/v666_run_audio_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-run-view-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'RunSurfaceTests','test_web_ui_read_observations','test_web_ui_scope_revision_cancellation_disposal_and_pack_locality','--require-runtime'],cwd=checkout,env=env)

            elif args.suite=='run-presets':
                work.run(label+'-run-presets-copy',[sys.executable,str(checkout/'tests/web/v666_run_presets_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-run-presets-projection',['node',str(checkout/'tests/web/v666_run_presets_projection.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-run-presets-api',[sys.executable,str(checkout/'tests/web/v666_run_presets_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                work.run(label+'-run-presets-ui',[sys.executable,str(checkout/'tests/web/v666_run_presets_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-run-resolution-ui',[sys.executable,str(checkout/'tests/web/v666_run_resolution_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-run-audio-ui',[sys.executable,str(checkout/'tests/web/v666_run_audio_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-run-view-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'RunSurfaceTests','test_web_ui_read_observations','test_web_ui_scope_revision_cancellation_disposal_and_pack_locality','--require-runtime'],cwd=checkout,env=env)

            elif args.suite=='run-audio':
                for name,kind in [('copy','py'),('projection','mjs')]:
                    work.run(label+'-run-audio-'+name,[sys.executable if kind=='py'else'node',str(checkout/('tests/web/v666_run_audio_'+name+'.'+kind)),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-run-audio-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'RunAudioTests','RunSurfaceTests','test_web_ui_read_observations','test_web_ui_scope_revision_cancellation_disposal_and_pack_locality','test_frame_control_actual_boundary_order_repeat_thread_and_close','test_actual_owned_cooperative_frames_pause_step_reconnect_and_stop','--require-runtime'],cwd=checkout,env=env)
                for mode in ['stream','faults']:
                    work.run(label+'-run-audio-api-'+mode,[sys.executable,str(checkout/'tests/web/v666_run_audio_api.py'),str(checkout),str(report),mode],cwd=checkout,env=env)
                work.run(label+'-run-audio-ui',[sys.executable,str(checkout/'tests/web/v666_run_audio_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-run-resolution-ui',[sys.executable,str(checkout/'tests/web/v666_run_resolution_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-run-surface-faults',[sys.executable,str(checkout/'tests/web/v666_run_surface_api.py'),str(checkout),str(report),'faults'],cwd=checkout,env=env)
                work.run(label+'-run-developer-ui',[sys.executable,str(checkout/'tests/web/v666_run_developer_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)

            elif args.suite in ['run-resolution','run-surface']:
                for name in ['copy','projection','client']:
                    extension='py' if name=='copy' else 'mjs'
                    work.run(label+'-run-surface-'+name,[sys.executable if name=='copy'else'node',str(checkout/('tests/web/v666_run_surface_'+name+'.'+extension)),str(checkout)],cwd=checkout,env=env)
                if args.suite=='run-resolution':
                    work.run(label+'-run-resolution-boundary',[sys.executable,str(checkout/'tests/web/v666_run_resolution_copy.py'),str(checkout)],cwd=checkout,env=env)
                    work.run(label+'-run-resolution-projection',['node',str(checkout/'tests/web/v666_run_resolution_projection.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-run-surface-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'RunSurfaceTests','test_web_ui_read_observations','test_web_ui_scope_revision_cancellation_disposal_and_pack_locality','test_frame_control_actual_boundary_order_repeat_thread_and_close','test_actual_owned_cooperative_frames_pause_step_reconnect_and_stop','--require-runtime'],cwd=checkout,env=env)
                for mode in ['heartbeat','faults','maximum']:
                    work.run(label+'-run-surface-api-'+mode,[sys.executable,str(checkout/'tests/web/v666_run_surface_api.py'),str(checkout),str(report),mode],cwd=checkout,env=env)
                work.run(label+'-run-surface-ui',[sys.executable,str(checkout/'tests/web/v666_run_surface_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                if args.suite=='run-resolution':
                    work.run(label+'-run-resolution-receipts',[sys.executable,str(checkout/'tests/web/v666_run_resolution_receipts_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                    work.run(label+'-run-resolution-ui',[sys.executable,str(checkout/'tests/web/v666_run_resolution_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-run-developer-regression',[sys.executable,str(checkout/'tests/web/v666_run_developer_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                work.run(label+'-run-fullscreen-regression',[sys.executable,str(checkout/'tests/web/v666_run_fullscreen_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'race'],cwd=checkout,env=env)
            elif args.suite=='run-developer':
                work.run(label+'-run-developer-boundary',[sys.executable,str(checkout/'tests/web/v666_run_developer_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-run-developer-facts',['node',str(checkout/'tests/web/v666_run_developer_projection.mjs'),str(checkout)],cwd=checkout,env=env)
                if label=='lf':work.run('lf-run-owner-backend',[sys.executable,str(checkout/'tests/web/v536_run_windows_backend.py'),str(checkout),str(report)],cwd=checkout,env=env)
                work.run(label+'-run-developer-ui',[sys.executable,str(checkout/'tests/web/v666_run_developer_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'lifecycle'],cwd=checkout,env=env)
                for mode in (['normal','menu']if label=='lf'else['fallback','race','scope']):
                    work.run(label+'-run-fullscreen-'+mode,[sys.executable,str(checkout/'tests/web/v666_run_fullscreen_ui.py'),str(checkout),str(report),mode],cwd=checkout,env=env)
            elif args.suite=='run-fullscreen':
                work.run(label+'-run-fullscreen-source-boundary',[sys.executable,str(checkout/'tests/web/v666_run_fullscreen_copy.py'),str(checkout)],cwd=checkout,env=env)
                if label=='lf':
                    work.run(label+'-run-owner-backend',[sys.executable,str(checkout/'tests/web/v536_run_windows_backend.py'),str(checkout),str(report)],cwd=checkout,env=env)
                else:
                    work.run(label+'-document-floating-renderer',[sys.executable,str(checkout/'tests/web/v536_document_windows_renderer.py'),str(checkout)],cwd=checkout,env=env)
                for mode in (['normal','fallback','lifecycle']if label=='lf'else['normal','race','scope']):
                    work.run(label+'-run-fullscreen-'+mode,[sys.executable,str(checkout/'tests/web/v666_run_fullscreen_ui.py'),str(checkout),str(report),mode],cwd=checkout,env=env)

            elif args.suite=='route-group-recovery':
                work.run(label+'-route-group-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-route-group-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-route-group-history-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'DraftHistoryTests','test_display_name_preserves_compiled_code_probe_reuse_and_never_renews_stale_bodies','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-route-group-api',[sys.executable,str(checkout/'tests/web/v666_route_group_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                regression='v666_route_recovery_api.py'if label=='lf'else'v666_node_names_recovery_api.py'
                work.run(label+'-root-contract-regression',[sys.executable,str(checkout/'tests/web'/regression),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                for mode in (['storage-new','conflict','unapplied-new']if label=='lf'else['normal','loss','late']):
                    work.run(label+'-route-group-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_route_group_recovery_ui.py'),str(checkout),str(report),mode,'--out-root'],cwd=checkout,env=env)
                previous='v666_route_recovery_ui.py'if label=='lf'else'v666_root_void_name_recovery_ui.py'
                work.run(label+'-previous-owner-ui',[sys.executable,str(checkout/'tests/web'/previous),str(checkout),str(report),'normal'if label=='lf'else'late','--out-root'],cwd=checkout,env=env)
            elif args.suite=='root-void-name-recovery':
                work.run(label+'-root-void-name-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-root-void-name-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-root-void-name-history-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'DraftHistoryTests','test_display_name_preserves_compiled_code_probe_reuse_and_never_renews_stale_bodies','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-root-void-name-api',[sys.executable,str(checkout/'tests/web/v666_root_void_name_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                regression='v666_root_value_rename_recovery_api.py'if label=='lf'else'v666_root_return_position_recovery_api.py'
                work.run(label+'-root-contract-regression',[sys.executable,str(checkout/'tests/web'/regression),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                for mode in (['storage-new','conflict','unapplied-new']if label=='lf'else['normal','loss','late']):
                    work.run(label+'-root-void-name-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_void_name_recovery_ui.py'),str(checkout),str(report),mode,'--out-root'],cwd=checkout,env=env)
                previous='v666_root_value_rename_recovery_ui.py'if label=='lf'else'v666_root_followup_recovery_ui.py'
                work.run(label+'-previous-owner-ui',[sys.executable,str(checkout/'tests/web'/previous),str(checkout),str(report),'late','--out-root'],cwd=checkout,env=env)
            elif args.suite=='node-names-recovery':
                work.run(label+'-node-names-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-node-names-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-node-names-history-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'DraftHistoryTests','test_display_name_preserves_compiled_code_probe_reuse_and_never_renews_stale_bodies','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-node-names-api',[sys.executable,str(checkout/'tests/web/v666_node_names_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                regression='v666_root_return_position_recovery_api.py'if label=='lf'else'v666_node_text_recovery_api.py'
                work.run(label+'-root-contract-regression',[sys.executable,str(checkout/'tests/web'/regression),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                for mode in (['storage-new','conflict','unapplied-new']if label=='lf'else['normal','loss','late']):
                    work.run(label+'-node-names-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_node_names_recovery_ui.py'),str(checkout),str(report),mode,'--out-root'],cwd=checkout,env=env)
                previous='v666_name_recovery_ui.py'if label=='lf'else'v666_node_text_recovery_ui.py'
                work.run(label+'-previous-owner-ui',[sys.executable,str(checkout/'tests/web'/previous),str(checkout),str(report),'late','--out-root'],cwd=checkout,env=env)
            elif args.suite=='root-return-position-recovery':
                work.run(label+'-root-return-position-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-root-return-position-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-root-return-position-history-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'DraftHistoryTests','test_display_name_preserves_compiled_code_probe_reuse_and_never_renews_stale_bodies','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-root-return-position-api',[sys.executable,str(checkout/'tests/web/v666_root_return_position_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                regression='v666_root_output_order_recovery_api.py'if label=='lf'else'v666_root_value_rename_recovery_api.py'
                work.run(label+'-root-contract-regression',[sys.executable,str(checkout/'tests/web'/regression),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                for mode in (['storage-new','conflict','unapplied-new']if label=='lf'else['normal','loss','late']):
                    work.run(label+'-root-return-position-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_return_position_recovery_ui.py'),str(checkout),str(report),mode,'--out-root'],cwd=checkout,env=env)
                previous='v666_root_output_order_recovery_ui.py'if label=='lf'else'v666_node_text_recovery_ui.py'
                work.run(label+'-previous-owner-ui',[sys.executable,str(checkout/'tests/web'/previous),str(checkout),str(report),'late','--out-root'],cwd=checkout,env=env)
            elif args.suite=='node-text-recovery':
                work.run(label+'-node-text-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-node-text-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-node-text-history-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'DraftHistoryTests','test_display_name_preserves_compiled_code_probe_reuse_and_never_renews_stale_bodies','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-node-text-api',[sys.executable,str(checkout/'tests/web/v666_node_text_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                if label=='lf':work.run(label+'-previous-text-api',[sys.executable,str(checkout/'tests/web/v666_text_pair_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                for mode in (['storage-new','conflict','unapplied-new']if label=='lf'else['normal','loss','late','compiler']):
                    work.run(label+'-node-text-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_node_text_recovery_ui.py'),str(checkout),str(report),mode,'--out-root'],cwd=checkout,env=env)
                previous='v666_text_pair_recovery_ui.py'if label=='lf'else'v666_source_recovery_ui.py'
                work.run(label+'-previous-text-ui',[sys.executable,str(checkout/'tests/web'/previous),str(checkout),str(report),'late','--out-root'],cwd=checkout,env=env)
            elif args.suite=='root-value-rename-recovery':
                work.run(label+'-root-value-rename-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-root-value-rename-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-root-value-rename-history-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'DraftHistoryTests','test_display_name_preserves_compiled_code_probe_reuse_and_never_renews_stale_bodies','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-root-value-rename-api',[sys.executable,str(checkout/'tests/web/v666_root_value_rename_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                regression='v666_root_input_name_recovery_api.py'if label=='lf'else'v666_root_output_order_recovery_api.py'
                work.run(label+'-root-contract-regression',[sys.executable,str(checkout/'tests/web'/regression),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                for mode in (['storage-new','conflict','unapplied-new']if label=='lf'else['normal','loss','late']):
                    work.run(label+'-root-value-rename-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_value_rename_recovery_ui.py'),str(checkout),str(report),mode,'--out-root'],cwd=checkout,env=env)
                previous='v666_text_pair_recovery_ui.py'if label=='lf'else'v666_root_input_name_recovery_ui.py'
                work.run(label+'-previous-owner-ui',[sys.executable,str(checkout/'tests/web'/previous),str(checkout),str(report),'late','--out-root'],cwd=checkout,env=env)
            elif args.suite=='text-pair-recovery':
                work.run(label+'-text-pair-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-text-pair-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-text-pair-history-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'DraftHistoryTests','test_display_name_preserves_compiled_code_probe_reuse_and_never_renews_stale_bodies','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-text-pair-api',[sys.executable,str(checkout/'tests/web/v666_text_pair_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                if label=='lf':
                    work.run(label+'-name-regression',[sys.executable,str(checkout/'tests/web/v666_name_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                    work.run(label+'-direct-creation-regression',[sys.executable,str(checkout/'tests/web/v666_direct_creation_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                else:work.run(label+'-source-regression',[sys.executable,str(checkout/'tests/web/v666_source_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                for mode in (['storage-new','conflict','unapplied-new']if label=='lf'else['normal','loss','late','compiler']):
                    work.run(label+'-text-pair-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_text_pair_recovery_ui.py'),str(checkout),str(report),mode,'--out-root'],cwd=checkout,env=env)
                if label=='lf':work.run(label+'-direct-creation-ui-regression',[sys.executable,str(checkout/'tests/web/v666_direct_creation_recovery_ui.py'),str(checkout),str(report),'late','--out-root'],cwd=checkout,env=env)
            elif args.suite=='direct-creation-recovery':
                work.run(label+'-direct-creation-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-direct-creation-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-direct-creation-history-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'DraftHistoryTests','test_display_name_preserves_compiled_code_probe_reuse_and_never_renews_stale_bodies','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-direct-creation-api',[sys.executable,str(checkout/'tests/web/v666_direct_creation_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-root-followup-regression',[sys.executable,str(checkout/'tests/web/v666_root_followup_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                for mode in (['storage-new','conflict','unapplied-new']if label=='lf'else['normal','loss','late']):
                    work.run(label+'-direct-creation-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_direct_creation_recovery_ui.py'),str(checkout),str(report),mode,'--out-root'],cwd=checkout,env=env)
                if label=='lf':work.run(label+'-root-followup-ui-regression',[sys.executable,str(checkout/'tests/web/v666_root_followup_recovery_ui.py'),str(checkout),str(report),'late','--out-root'],cwd=checkout,env=env)
            elif args.suite=='root-followup-recovery':
                work.run(label+'-root-followup-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-root-followup-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-root-followup-history-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'DraftHistoryTests','test_display_name_preserves_compiled_code_probe_reuse_and_never_renews_stale_bodies','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-root-followup-api',[sys.executable,str(checkout/'tests/web/v666_root_followup_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-root-input-name-regression',[sys.executable,str(checkout/'tests/web/v666_root_input_name_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-root-output-order-regression',[sys.executable,str(checkout/'tests/web/v666_root_output_order_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-source-regression',[sys.executable,str(checkout/'tests/web/v666_source_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                if label=='crlf':
                    work.run(label+'-property-observation-guards',[sys.executable,str(checkout/'tests/web/v666_async_property_guards.py'),str(checkout),str(report)],cwd=checkout,env=env)
                    work.run(label+'-root-followup-compiler-ui',[sys.executable,str(checkout/'tests/web/v666_root_followup_recovery_ui.py'),str(checkout),str(report),'compiler','--out-root'],cwd=checkout,env=env)
                for mode in (['late','storage-new','conflict']if label=='lf'else['normal','loss']):
                    work.run(label+'-root-followup-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_followup_recovery_ui.py'),str(checkout),str(report),mode,'--out-root'],cwd=checkout,env=env)
            elif args.suite=='root-input-name-recovery':
                work.run(label+'-root-input-name-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-root-input-name-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-root-input-name-history-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'DraftHistoryTests','test_display_name_preserves_compiled_code_probe_reuse_and_never_renews_stale_bodies','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-root-input-name-api',[sys.executable,str(checkout/'tests/web/v666_root_input_name_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-root-output-order-regression',[sys.executable,str(checkout/'tests/web/v666_root_output_order_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-export-creation-regression',[sys.executable,str(checkout/'tests/web/v666_export_creation_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-export-removal-regression',[sys.executable,str(checkout/'tests/web/v666_export_removal_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-root-return-regression',[sys.executable,str(checkout/'tests/web/v666_root_return_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-export-binding-regression',[sys.executable,str(checkout/'tests/web/v666_export_binding_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-export-value-regression',[sys.executable,str(checkout/'tests/web/v666_export_value_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-entry-regression',[sys.executable,str(checkout/'tests/web/v666_entry_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-source-regression',[sys.executable,str(checkout/'tests/web/v666_source_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-name-regression',[sys.executable,str(checkout/'tests/web/v666_name_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-route-regression',[sys.executable,str(checkout/'tests/web/v666_route_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                if label=='crlf':
                    work.run(label+'-property-observation-guards',[sys.executable,str(checkout/'tests/web/v666_async_property_guards.py'),str(checkout),str(report)],cwd=checkout,env=env)
                    work.run(label+'-export-binding-retry-ui',[sys.executable,str(checkout/'tests/web/v666_export_binding_recovery_ui.py'),str(checkout),str(report),'storage-new','--out-root'],cwd=checkout,env=env)
                for mode in (['storage-new','conflict','late','unapplied-new']if label=='lf'else['normal','loss']):
                    work.run(label+'-root-input-name-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_input_name_recovery_ui.py'),str(checkout),str(report),mode,'--out-root'],cwd=checkout,env=env)
            elif args.suite=='root-output-order-recovery':
                work.run(label+'-root-output-order-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-root-output-order-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-root-output-order-history-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'DraftHistoryTests','test_display_name_preserves_compiled_code_probe_reuse_and_never_renews_stale_bodies','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-root-output-order-api',[sys.executable,str(checkout/'tests/web/v666_root_output_order_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-export-creation-regression',[sys.executable,str(checkout/'tests/web/v666_export_creation_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-export-removal-regression',[sys.executable,str(checkout/'tests/web/v666_export_removal_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-root-return-regression',[sys.executable,str(checkout/'tests/web/v666_root_return_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-export-binding-regression',[sys.executable,str(checkout/'tests/web/v666_export_binding_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-export-value-regression',[sys.executable,str(checkout/'tests/web/v666_export_value_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-entry-regression',[sys.executable,str(checkout/'tests/web/v666_entry_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-source-regression',[sys.executable,str(checkout/'tests/web/v666_source_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-name-regression',[sys.executable,str(checkout/'tests/web/v666_name_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-route-regression',[sys.executable,str(checkout/'tests/web/v666_route_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                if label=='crlf':
                    work.run(label+'-property-observation-guards',[sys.executable,str(checkout/'tests/web/v666_async_property_guards.py'),str(checkout),str(report)],cwd=checkout,env=env)
                    work.run(label+'-export-binding-retry-ui',[sys.executable,str(checkout/'tests/web/v666_export_binding_recovery_ui.py'),str(checkout),str(report),'storage-new','--out-root'],cwd=checkout,env=env)
                for mode in (['storage-new','conflict','late','unapplied-new']if label=='lf'else['normal','loss']):
                    work.run(label+'-root-output-order-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_output_order_recovery_ui.py'),str(checkout),str(report),mode,'--out-root'],cwd=checkout,env=env)
            elif args.suite=='export-creation-recovery':
                work.run(label+'-export-creation-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-export-creation-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-export-creation-history-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'DraftHistoryTests','test_display_name_preserves_compiled_code_probe_reuse_and_never_renews_stale_bodies','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-export-creation-api',[sys.executable,str(checkout/'tests/web/v666_export_creation_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-export-removal-regression',[sys.executable,str(checkout/'tests/web/v666_export_removal_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-root-return-regression',[sys.executable,str(checkout/'tests/web/v666_root_return_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-export-binding-regression',[sys.executable,str(checkout/'tests/web/v666_export_binding_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-export-value-regression',[sys.executable,str(checkout/'tests/web/v666_export_value_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-entry-regression',[sys.executable,str(checkout/'tests/web/v666_entry_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-source-regression',[sys.executable,str(checkout/'tests/web/v666_source_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-name-regression',[sys.executable,str(checkout/'tests/web/v666_name_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-route-regression',[sys.executable,str(checkout/'tests/web/v666_route_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                if label=='crlf':
                    work.run(label+'-property-observation-guards',[sys.executable,str(checkout/'tests/web/v666_async_property_guards.py'),str(checkout),str(report)],cwd=checkout,env=env)
                    work.run(label+'-export-binding-retry-ui',[sys.executable,str(checkout/'tests/web/v666_export_binding_recovery_ui.py'),str(checkout),str(report),'storage-new','--out-root'],cwd=checkout,env=env)
                for mode in (['storage-new','conflict','late','unapplied-new']if label=='lf'else['normal','loss']):
                    work.run(label+'-export-creation-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_export_creation_recovery_ui.py'),str(checkout),str(report),mode,'--out-root'],cwd=checkout,env=env)
            elif args.suite=='export-removal-recovery':
                work.run(label+'-export-removal-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-export-removal-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-export-removal-history-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'DraftHistoryTests','test_display_name_preserves_compiled_code_probe_reuse_and_never_renews_stale_bodies','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-export-removal-api',[sys.executable,str(checkout/'tests/web/v666_export_removal_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-root-return-regression',[sys.executable,str(checkout/'tests/web/v666_root_return_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-export-binding-regression',[sys.executable,str(checkout/'tests/web/v666_export_binding_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-export-value-regression',[sys.executable,str(checkout/'tests/web/v666_export_value_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-entry-regression',[sys.executable,str(checkout/'tests/web/v666_entry_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-source-regression',[sys.executable,str(checkout/'tests/web/v666_source_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-name-regression',[sys.executable,str(checkout/'tests/web/v666_name_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-route-regression',[sys.executable,str(checkout/'tests/web/v666_route_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                if label=='crlf':
                    work.run(label+'-property-observation-guards',[sys.executable,str(checkout/'tests/web/v666_async_property_guards.py'),str(checkout),str(report)],cwd=checkout,env=env)
                    work.run(label+'-export-binding-retry-ui',[sys.executable,str(checkout/'tests/web/v666_export_binding_recovery_ui.py'),str(checkout),str(report),'storage-new','--out-root'],cwd=checkout,env=env)
                for mode in (['storage','conflict','late','unapplied-new']if label=='lf'else['normal','loss']):
                    work.run(label+'-export-removal-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_export_removal_recovery_ui.py'),str(checkout),str(report),mode,'--out-root'],cwd=checkout,env=env)
            elif args.suite=='root-return-recovery':
                work.run(label+'-root-return-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-root-return-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-root-return-history-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'DraftHistoryTests','test_display_name_preserves_compiled_code_probe_reuse_and_never_renews_stale_bodies','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-root-return-api',[sys.executable,str(checkout/'tests/web/v666_root_return_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-export-binding-regression',[sys.executable,str(checkout/'tests/web/v666_export_binding_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-export-value-regression',[sys.executable,str(checkout/'tests/web/v666_export_value_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-entry-regression',[sys.executable,str(checkout/'tests/web/v666_entry_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-source-regression',[sys.executable,str(checkout/'tests/web/v666_source_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-name-regression',[sys.executable,str(checkout/'tests/web/v666_name_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-route-regression',[sys.executable,str(checkout/'tests/web/v666_route_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                if label=='crlf':
                    work.run(label+'-property-observation-guards',[sys.executable,str(checkout/'tests/web/v666_async_property_guards.py'),str(checkout),str(report)],cwd=checkout,env=env)
                    work.run(label+'-export-binding-retry-ui',[sys.executable,str(checkout/'tests/web/v666_export_binding_recovery_ui.py'),str(checkout),str(report),'storage-new','--out-root'],cwd=checkout,env=env)
                for mode in (['storage-new','conflict','late']if label=='lf'else['normal','loss']):
                    work.run(label+'-root-return-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_return_recovery_ui.py'),str(checkout),str(report),mode,'--out-root'],cwd=checkout,env=env)
            elif args.suite=='export-binding-recovery':
                work.run(label+'-export-binding-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-export-binding-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-export-binding-history-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'DraftHistoryTests','test_display_name_preserves_compiled_code_probe_reuse_and_never_renews_stale_bodies','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-export-binding-api',[sys.executable,str(checkout/'tests/web/v666_export_binding_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-export-value-regression',[sys.executable,str(checkout/'tests/web/v666_export_value_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-entry-regression',[sys.executable,str(checkout/'tests/web/v666_entry_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-source-regression',[sys.executable,str(checkout/'tests/web/v666_source_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-name-regression',[sys.executable,str(checkout/'tests/web/v666_name_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-route-regression',[sys.executable,str(checkout/'tests/web/v666_route_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                if label=='crlf':
                    work.run(label+'-property-observation-guards',[sys.executable,str(checkout/'tests/web/v666_async_property_guards.py'),str(checkout),str(report)],cwd=checkout,env=env)
                    work.run(label+'-export-value-retry-ui',[sys.executable,str(checkout/'tests/web/v666_export_value_recovery_ui.py'),str(checkout),str(report),'storage-new','--out-root'],cwd=checkout,env=env)
                for mode in (['storage-new','conflict','late']if label=='lf'else['normal','loss']):
                    work.run(label+'-export-binding-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_export_binding_recovery_ui.py'),str(checkout),str(report),mode,'--out-root'],cwd=checkout,env=env)
            elif args.suite=='export-value-recovery':
                work.run(label+'-export-value-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-export-value-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-export-value-history-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'DraftHistoryTests','test_display_name_preserves_compiled_code_probe_reuse_and_never_renews_stale_bodies','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-export-value-api',[sys.executable,str(checkout/'tests/web/v666_export_value_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-entry-regression',[sys.executable,str(checkout/'tests/web/v666_entry_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-source-regression',[sys.executable,str(checkout/'tests/web/v666_source_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-name-regression',[sys.executable,str(checkout/'tests/web/v666_name_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-route-regression',[sys.executable,str(checkout/'tests/web/v666_route_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                if label=='crlf':
                    work.run(label+'-property-observation-guards',[sys.executable,str(checkout/'tests/web/v666_async_property_guards.py'),str(checkout),str(report)],cwd=checkout,env=env)
                    work.run(label+'-entry-retry-ui',[sys.executable,str(checkout/'tests/web/v666_entry_recovery_ui.py'),str(checkout),str(report),'storage-new','--out-root'],cwd=checkout,env=env)
                for mode in (['storage-new','conflict','late']if label=='lf'else['normal','loss']):
                    work.run(label+'-export-value-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_export_value_recovery_ui.py'),str(checkout),str(report),mode,'--out-root'],cwd=checkout,env=env)
            elif args.suite=='entry-recovery':
                work.run(label+'-entry-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-entry-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-entry-history-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'DraftHistoryTests','test_display_name_preserves_compiled_code_probe_reuse_and_never_renews_stale_bodies','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-entry-api',[sys.executable,str(checkout/'tests/web/v666_entry_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-source-regression',[sys.executable,str(checkout/'tests/web/v666_source_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-name-regression',[sys.executable,str(checkout/'tests/web/v666_name_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-route-regression',[sys.executable,str(checkout/'tests/web/v666_route_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                if label=='crlf':
                    work.run(label+'-property-observation-guards',[sys.executable,str(checkout/'tests/web/v666_async_property_guards.py'),str(checkout),str(report)],cwd=checkout,env=env)
                    work.run(label+'-route-late-ui',[sys.executable,str(checkout/'tests/web/v666_route_recovery_ui.py'),str(checkout),str(report),'late','--out-root'],cwd=checkout,env=env)
                    work.run(label+'-source-retry-ui',[sys.executable,str(checkout/'tests/web/v666_source_recovery_ui.py'),str(checkout),str(report),'storage-new','--out-root'],cwd=checkout,env=env)
                for mode in (['storage-new','conflict','late']if label=='lf'else['normal','loss']):
                    work.run(label+'-entry-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_entry_recovery_ui.py'),str(checkout),str(report),mode,'--out-root'],cwd=checkout,env=env)
            elif args.suite=='route-recovery':
                work.run(label+'-route-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-route-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-route-history-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'DraftHistoryTests','test_display_name_preserves_compiled_code_probe_reuse_and_never_renews_stale_bodies','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-route-api',[sys.executable,str(checkout/'tests/web/v666_route_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-source-regression',[sys.executable,str(checkout/'tests/web/v666_source_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-name-regression',[sys.executable,str(checkout/'tests/web/v666_name_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                if label=='crlf':
                    work.run(label+'-property-observation-guards',[sys.executable,str(checkout/'tests/web/v666_async_property_guards.py'),str(checkout),str(report)],cwd=checkout,env=env)
                    work.run(label+'-source-retry-ui',[sys.executable,str(checkout/'tests/web/v666_source_recovery_ui.py'),str(checkout),str(report),'storage-new','--out-root'],cwd=checkout,env=env)
                for mode in (['storage-new','conflict','late']if label=='lf'else['normal','loss']):
                    work.run(label+'-route-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_route_recovery_ui.py'),str(checkout),str(report),mode,'--out-root'],cwd=checkout,env=env)
            elif args.suite=='name-recovery':
                work.run(label+'-name-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-name-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-name-history-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'DraftHistoryTests','test_display_name_preserves_compiled_code_probe_reuse_and_never_renews_stale_bodies','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-name-api',[sys.executable,str(checkout/'tests/web/v666_name_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-source-regression',[sys.executable,str(checkout/'tests/web/v666_source_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                if label=='crlf':
                    work.run(label+'-property-observation-guards',[sys.executable,str(checkout/'tests/web/v666_async_property_guards.py'),str(checkout),str(report)],cwd=checkout,env=env)
                    work.run(label+'-source-retry-ui',[sys.executable,str(checkout/'tests/web/v666_source_recovery_ui.py'),str(checkout),str(report),'storage-new','--out-root'],cwd=checkout,env=env)
                for mode in (['storage-new','conflict','late']if label=='lf'else['normal','loss','invalid']):
                    work.run(label+'-name-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_name_recovery_ui.py'),str(checkout),str(report),mode,'--out-root'],cwd=checkout,env=env)
            elif args.suite=='source-recovery':
                work.run(label+'-source-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-source-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-source-history-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'DraftHistoryTests','test_display_name_preserves_compiled_code_probe_reuse_and_never_renews_stale_bodies','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-source-api',[sys.executable,str(checkout/'tests/web/v666_source_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-description-regression',[sys.executable,str(checkout/'tests/web/v666_description_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                if label=='lf':work.run(label+'-property-source-regression',[sys.executable,str(checkout/'tests/web/v666_async_property_ui.py'),str(checkout),str(report),'normal'],cwd=checkout,env=env)
                else:work.run(label+'-property-observation-guards',[sys.executable,str(checkout/'tests/web/v666_async_property_guards.py'),str(checkout),str(report)],cwd=checkout,env=env)
                for mode in (['storage-new','conflict','late']if label=='lf'else['normal','loss','compiler']):
                    work.run(label+'-source-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_source_recovery_ui.py'),str(checkout),str(report),mode,'--out-root'],cwd=checkout,env=env)
            elif args.suite=='description-recovery':
                work.run(label+'-description-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_copy.py'),str(checkout)],cwd=checkout,env=env)
                for name in ['feature-authoring.js','feature-editor.js']:
                    work.run(label+'-description-script-'+name,[ 'node','--check',str(checkout/'examples/editor-home/ui'/name)],cwd=checkout,env=env)
                work.run(label+'-description-history-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'DraftHistoryTests','test_display_name_preserves_compiled_code_probe_reuse_and_never_renews_stale_bodies','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-description-api',[sys.executable,str(checkout/'tests/web/v666_description_recovery_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-value-regression',[sys.executable,str(checkout/'tests/web/v666_guidance_values_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                for target,mode in ([('node','storage-new'),('function','entry'),('node','late')]if label=='lf'else[('node','conflict'),('function','storage-new'),('function','loss')]):
                    work.run(label+'-description-'+target+'-'+mode,[sys.executable,str(checkout/'tests/web/v666_description_recovery_ui.py'),str(checkout),str(report),target,mode,'--out-root'],cwd=checkout,env=env)
            elif args.suite=='guidance-values':
                work.run(label+'-value-native-guards',[sys.executable,str(checkout/'tests/web/v666_guidance_values_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-value-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-value-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-value-ui',[sys.executable,str(checkout/'tests/web/v666_guidance_values_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'storage','--out-root'if label=='lf'else'--data-root'],cwd=checkout,env=env)
                work.run(label+'-value-recovery',[sys.executable,str(checkout/'tests/web/v666_guidance_values_ui.py'),str(checkout),str(report),'late'if label=='lf'else'loss','--out-root'if label=='lf'else'--data-root'],cwd=checkout,env=env)
            elif args.suite=='guidance-review':
                work.run(label+'-review-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_guidance_review_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-review-admission',['node',str(checkout/'tests/web/review_admission.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-review-layer-hit-test',[sys.executable,str(checkout/'tests/web/v666_review_layer_ui.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-review-ui',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'storage','--out-root','--review-guidance'],cwd=checkout,env=env)
                work.run(label+'-review-task-regression',[sys.executable,str(checkout/'tests/web/v666_async_coupled_first_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late','--branch-line','--out-root'],cwd=checkout,env=env)
                if label=='crlf':work.run(label+'-declaration-reread-regression',[sys.executable,str(checkout/'tests/web/v666_declaration_reload_ui.py'),str(checkout),str(report),'normal','view'],cwd=checkout,env=env)
                if label=='crlf':work.run(label+'-review-run-regression',[sys.executable,str(checkout/'tests/web/v666_run_fullscreen_ui.py'),str(checkout),str(report),'normal'],cwd=checkout,env=env)

            elif args.suite=='guidance-code-editor':
                work.run(label+'-guidance-copy-boundary',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_copy.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-guidance-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-guidance-ui',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'storage','--out-root'],cwd=checkout,env=env)
                work.run(label+'-guidance-task-regression',[sys.executable,str(checkout/'tests/web/v666_async_coupled_first_ui.py'),str(checkout),str(report),'normal'if label=='lf'else'late','--branch-line','--out-root'],cwd=checkout,env=env)
            elif args.suite=='async-branch-creation':
                work.run(label+'-branch-plans',['node',str(checkout/'tests/web/v666_async_branch_creation.mjs')],cwd=checkout,env=env)
                work.run(label+'-branch-recovery',['node',str(checkout/'tests/web/v666_completion_recovery.mjs')],cwd=checkout,env=env)
                work.run(label+'-branch-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-branch-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'AsyncContextTests','AsyncBlueprintTests','BlueprintConversionTests','--require-runtime'],cwd=checkout,env=env)
                for port,flags in [('completion',[]),('result',['--result-line'])]:
                    work.run(label+'-branch-api-'+port,[sys.executable,str(checkout/'tests/web/v666_async_branch_creation_api.py'),str(checkout),str(report),'--out-root',*flags],cwd=checkout,env=env)
                if label=='lf':work.run(label+'-branch-async-guards',[sys.executable,str(checkout/'tests/web/v666_async_transition_guards.py'),str(checkout)],cwd=checkout,env=env)
                for mode,flags in ([('normal',[]),('storage',[]),('normal',['--result-line'])] if label=='lf' else [('conflict',['--result-line']),('loss',['--result-line']),('late',[])]):
                    work.run(label+'-branch-ui-'+('result-'if flags else'completion-')+mode,[sys.executable,str(checkout/'tests/web/v666_async_coupled_first_ui.py'),str(checkout),str(report),mode,'--branch-line','--out-root',*flags],cwd=checkout,env=env)
                if label=='lf':
                    work.run(label+'-branch-root-io-regression',[sys.executable,str(checkout/'tests/web/v666_async_root_io_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                    work.run(label+'-branch-final-read-cas',[sys.executable,str(checkout/'tests/web/v536_copy_read_guards_core.py'),str(checkout)],cwd=checkout,env=env)
                else:work.run(label+'-branch-root-io-ui',[sys.executable,str(checkout/'tests/web/v666_async_coupled_first_ui.py'),str(checkout),str(report),'unsaved-declaration','--root-io'],cwd=checkout,env=env)
            elif args.suite=='async-root-io':
                work.run(label+'-root-io-recovery',['node',str(checkout/'tests/web/v666_completion_recovery.mjs')],cwd=checkout,env=env)
                work.run(label+'-root-io-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-root-io-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'AsyncContextTests','AsyncBlueprintTests','BlueprintConversionTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-root-io-ownership',[sys.executable,str(checkout/'tests/web/v666_async_root_io_guards.py'),str(checkout),str(report)],cwd=checkout,env=env)
                work.run(label+'-root-io-api',[sys.executable,str(checkout/'tests/web/v666_async_root_io_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                if label=='lf':
                    work.run(label+'-root-io-creation-guards',[sys.executable,str(checkout/'tests/web/v666_async_new_function_guards.py'),str(checkout)],cwd=checkout,env=env)
                    work.run(label+'-root-io-global-regression',[sys.executable,str(checkout/'tests/web/v666_async_coupled_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                    work.run(label+'-root-io-information-regression',[sys.executable,str(checkout/'tests/web/v666_async_coupled_api.py'),str(checkout),str(report),'--information','--defer'],cwd=checkout,env=env)
                else:
                    work.run(label+'-root-io-private-regression',[sys.executable,str(checkout/'tests/web/v666_async_coupled_private_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                    work.run(label+'-root-io-async-guards',[sys.executable,str(checkout/'tests/web/v666_async_transition_guards.py'),str(checkout)],cwd=checkout,env=env)
                for mode in (['normal','unsaved-declaration','storage'] if label=='lf' else ['no-checkpoint','conflict','loss','late','create-late']):
                    work.run(label+'-root-io-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_async_coupled_first_ui.py'),str(checkout),str(report),mode,'--root-io'],cwd=checkout,env=env)
                if label=='lf':
                    work.run(label+'-root-io-plain-ui-regression',[sys.executable,str(checkout/'tests/web/v666_async_coupled_first_ui.py'),str(checkout),str(report),'normal'],cwd=checkout,env=env)
                    work.run(label+'-root-io-final-read-cas',[sys.executable,str(checkout/'tests/web/v536_copy_read_guards_core.py'),str(checkout)],cwd=checkout,env=env)
            elif args.suite=='async-coupled':
                work.run(label+'-coupled-recovery-proof',['node',str(checkout/'tests/web/v666_completion_recovery.mjs')],cwd=checkout,env=env)
                work.run(label+'-coupled-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                if label=='crlf':work.run(label+'-coupled-new-node-ui',[sys.executable,str(checkout/'tests/web/v666_async_coupled_first_ui.py'),str(checkout),str(report),'late','--leaf'],cwd=checkout,env=env)
                if label=='lf':work.run('lf-coupled-cold-source-epoch',[sys.executable,str(checkout/'tests/web/v666_async_coupled_first_ui.py'),str(checkout),str(report),'late','--information'],cwd=checkout,env=env)
                work.run(label+'-coupled-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'AsyncContextTests','AsyncBlueprintTests','BlueprintConversionTests','--require-runtime'],cwd=checkout,env=env)
                for name,script in [('information-guards','v666_async_information_guards.py'),('private-guards','v666_async_private_guards.py'),('global-guards','v666_async_new_function_guards.py'),('global-templates','v666_async_new_function_templates.py')]:
                    work.run(label+'-'+name,[sys.executable,str(checkout/'tests/web'/script),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-declaration-restore',[sys.executable,str(checkout/'tests/web/v666_async_creation_restore_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                for name,script,flags in [('global','v666_async_coupled_api.py',[]),('information','v666_async_coupled_api.py',['--information','--defer']),('private','v666_async_coupled_private_api.py',[]),('new-node','v666_async_coupled_node_api.py',[])]:
                    work.run(label+'-coupled-'+name+'-api',[sys.executable,str(checkout/'tests/web'/script),str(checkout),str(report),*flags],cwd=checkout,env=env)
                for mode in (['normal','unsaved-declaration','storage','create-loss'] if label=='lf' else ['no-checkpoint','conflict','loss','late','create-late']):
                    work.run(label+'-coupled-first-'+mode,[sys.executable,str(checkout/'tests/web/v666_async_coupled_first_ui.py'),str(checkout),str(report),mode],cwd=checkout,env=env)
                work.run(label+'-coupled-information-ui',[sys.executable,str(checkout/'tests/web/v666_async_coupled_first_ui.py'),str(checkout),str(report),'normal' if label=='lf' else 'late','--information'],cwd=checkout,env=env)
                if label=='lf':work.run(label+'-coupled-new-node-ui',[sys.executable,str(checkout/'tests/web/v666_async_coupled_first_ui.py'),str(checkout),str(report),'normal','--leaf'],cwd=checkout,env=env)
                work.run(label+'-private-returns-regression',[sys.executable,str(checkout/'tests/web/v666_async_private_returns_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                work.run(label+'-async-receipt-guards',[sys.executable,str(checkout/'tests/web/v666_async_transition_guards.py'),str(checkout)],cwd=checkout,env=env)
                if label=='lf':work.run('lf-coupled-final-read-cas',[sys.executable,str(checkout/'tests/web/v536_copy_read_guards_core.py'),str(checkout)],cwd=checkout,env=env)

            elif args.suite in ['async-private','async-private-returns']:
                work.run(label+'-private-recovery-proof',['node',str(checkout/'tests/web/v666_completion_recovery.mjs')],cwd=checkout,env=env)
                work.run(label+'-private-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-private-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'AsyncContextTests','AsyncBlueprintTests','BlueprintConversionTests','--require-runtime'],cwd=checkout,env=env)
                for name,script in [('information-guards','v666_async_information_guards.py'),('private-guards','v666_async_private_guards.py'),('global-guards','v666_async_new_function_guards.py'),('global-templates','v666_async_new_function_templates.py'),('completion-adapter-guards','v666_async_adapter_guards.py')]:
                    work.run(label+'-'+name,[sys.executable,str(checkout/'tests/web'/script),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-private-task-execution',[sys.executable,str(checkout/'tests/probes/async_private_runtime.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-private-api',[sys.executable,str(checkout/'tests/web/v666_async_private_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                if args.suite=='async-private-returns':
                    work.run(label+'-private-returns-api',[sys.executable,str(checkout/'tests/web/v666_async_private_returns_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                private_ui='v666_async_private_returns_ui.py' if args.suite=='async-private-returns' else 'v666_async_private_ui.py'
                for mode in (['late','normal','storage'] if label=='lf' else ['loss','conflict']):
                    work.run(label+'-private-ui-'+mode,[sys.executable,str(checkout/'tests/web'/private_ui),str(checkout),str(report),mode],cwd=checkout,env=env)
                work.run(label+'-async-receipt-guards',[sys.executable,str(checkout/'tests/web/v666_async_transition_guards.py'),str(checkout)],cwd=checkout,env=env)
                regression='v666_async_information_api.py' if label=='lf' else 'v666_node_internal_nested_api.py'
                work.run(label+'-creation-regression',[sys.executable,str(checkout/'tests/web'/regression),str(checkout),str(report)],cwd=checkout,env=env)
                if label=='lf':work.run('lf-private-final-read-cas',[sys.executable,str(checkout/'tests/web/v536_copy_read_guards_core.py'),str(checkout)],cwd=checkout,env=env)

            elif args.suite=='async-information':
                work.run(label+'-information-recovery-proof',['node',str(checkout/'tests/web/v666_completion_recovery.mjs')],cwd=checkout,env=env)
                work.run(label+'-information-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-information-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'AsyncContextTests','AsyncBlueprintTests','BlueprintConversionTests','--require-runtime'],cwd=checkout,env=env)
                for name,script in [('information-guards','v666_async_information_guards.py'),('global-guards','v666_async_new_function_guards.py'),('global-templates','v666_async_new_function_templates.py'),('completion-adapter-guards','v666_async_adapter_guards.py')]:
                    work.run(label+'-'+name,[sys.executable,str(checkout/'tests/web'/script),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-information-api',[sys.executable,str(checkout/'tests/web/v666_async_information_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                for mode in (['late','normal','storage'] if label=='lf' else ['loss','conflict']):
                    work.run(label+'-information-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_async_information_ui.py'),str(checkout),str(report),mode,*(['view'] if label=='lf' and mode=='normal' else [])],cwd=checkout,env=env)
                work.run(label+'-async-receipt-guards',[sys.executable,str(checkout/'tests/web/v666_async_transition_guards.py'),str(checkout)],cwd=checkout,env=env)
                regression='v536_information_own_functions_api.py' if label=='lf' else 'v666_async_new_function_api.py'
                work.run(label+'-creation-regression',[sys.executable,str(checkout/'tests/web'/regression),str(checkout),str(report)],cwd=checkout,env=env)
                if label=='lf':work.run('lf-information-final-read-cas',[sys.executable,str(checkout/'tests/web/v536_copy_read_guards_core.py'),str(checkout)],cwd=checkout,env=env)

            elif args.suite=='async-new-function':
                work.run(label+'-new-function-recovery-proof',['node',str(checkout/'tests/web/v666_completion_recovery.mjs')],cwd=checkout,env=env)
                work.run(label+'-new-function-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-new-function-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'AsyncContextTests','AsyncBlueprintTests','BlueprintConversionTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-new-function-guards',[sys.executable,str(checkout/'tests/web/v666_async_new_function_guards.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-new-function-templates',[sys.executable,str(checkout/'tests/web/v666_async_new_function_templates.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-new-function-api',[sys.executable,str(checkout/'tests/web/v666_async_new_function_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                for mode in (['late','normal','storage'] if label=='lf' else ['loss','conflict']):
                    work.run(label+'-new-function-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_async_new_function_ui.py'),str(checkout),str(report),mode],cwd=checkout,env=env)
                work.run(label+'-async-receipt-guards',[sys.executable,str(checkout/'tests/web/v666_async_transition_guards.py'),str(checkout)],cwd=checkout,env=env)
                regression='v666_async_creating_api.py' if label=='lf' else 'v666_async_adapter_api.py'
                work.run(label+'-confirmed-body-regression',[sys.executable,str(checkout/'tests/web'/regression),str(checkout),str(report)],cwd=checkout,env=env)
                if label=='lf':
                    work.run('lf-new-function-dialog-regression',[sys.executable,str(checkout/'tests/web/v508_feature_create.py'),str(checkout),str(report)],cwd=checkout,env=env)
                    work.run('lf-new-function-final-read-cas',[sys.executable,str(checkout/'tests/web/v536_copy_read_guards_core.py'),str(checkout)],cwd=checkout,env=env)

            elif args.suite=='async-creating':
                work.run(label+'-creating-recovery-proof',['node',str(checkout/'tests/web/v666_completion_recovery.mjs')],cwd=checkout,env=env)
                work.run(label+'-creating-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-creating-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'AsyncContextTests','AsyncBlueprintTests','BlueprintConversionTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-creating-guards',[sys.executable,str(checkout/'tests/web/v666_async_creating_guards.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-creating-api',[sys.executable,str(checkout/'tests/web/v666_async_creating_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                for mode in (['late','normal','storage'] if label=='lf' else ['loss','conflict']):
                    work.run(label+'-creating-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_async_creating_ui.py'),str(checkout),str(report),mode],cwd=checkout,env=env)
                work.run(label+'-async-receipt-guards',[sys.executable,str(checkout/'tests/web/v666_async_transition_guards.py'),str(checkout)],cwd=checkout,env=env)
                regression='v666_async_context_api.py' if label=='lf' else 'v666_async_adapter_api.py'
                work.run(label+'-confirmed-body-regression',[sys.executable,str(checkout/'tests/web'/regression),str(checkout),str(report)],cwd=checkout,env=env)
                if label=='lf':
                    work.run('lf-owned-final-read-cas',[sys.executable,str(checkout/'tests/web/v536_copy_read_guards_core.py'),str(checkout)],cwd=checkout,env=env)

            elif args.suite=='async-context':
                work.run(label+'-context-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-context-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'AsyncContextTests','AsyncBlueprintTests','BlueprintConversionTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-context-api',[sys.executable,str(checkout/'tests/web/v666_async_context_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                for mode in (['normal','storage','conflict'] if label=='lf' else ['loss','late']):
                    work.run(label+'-context-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_async_context_ui.py'),str(checkout),str(report),mode],cwd=checkout,env=env)
                work.run(label+'-async-receipt-guards',[sys.executable,str(checkout/'tests/web/v666_async_transition_guards.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-original-context-regression',[sys.executable,str(checkout/'tests/web/v666_node_internal_context_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                if label=='lf':
                    work.run('lf-ordinary-adapter-regression',[sys.executable,str(checkout/'tests/web/v666_async_adapter_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                    work.run('lf-owned-final-read-cas',[sys.executable,str(checkout/'tests/web/v536_copy_read_guards_core.py'),str(checkout)],cwd=checkout,env=env)

            elif args.suite=='async-adapter':
                work.run(label+'-settled-input-proof',['node',str(checkout/'tests/web/v666_completion_recovery.mjs')],cwd=checkout,env=env)
                work.run(label+'-adapter-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-adapter-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'CompletionAdapterTests','AsyncBlueprintTests','SwitchBlueprintTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-adapter-guards',[sys.executable,str(checkout/'tests/web/v666_async_adapter_guards.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-adapter-api',[sys.executable,str(checkout/'tests/web/v666_async_adapter_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                for mode in (['normal','storage','conflict'] if label=='lf' else ['loss','late']):
                    work.run(label+'-adapter-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_async_adapter_ui.py'),str(checkout),str(report),mode],cwd=checkout,env=env)
                work.run(label+'-existing-completion-regression',[sys.executable,str(checkout/'tests/web/v666_async_completion_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-public-completion-regression',[sys.executable,str(checkout/'tests/web/v666_async_function_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-async-receipt-regression',[sys.executable,str(checkout/'tests/web/v666_async_transition_guards.py'),str(checkout)],cwd=checkout,env=env)
                if label=='lf':work.run('lf-existing-copy-ui',[sys.executable,str(checkout/'tests/web/v666_node_internal_copy_ui.py'),str(checkout),str(report),'normal'],cwd=checkout,env=env)
                if label=='lf':work.run('lf-async-property-regression',[sys.executable,str(checkout/'tests/web/v666_async_property_ui.py'),str(checkout),str(report),'normal'],cwd=checkout,env=env)

            elif args.suite=='async-property':
                for asset in ['property-authoring.js','set-authoring.js','feature-authoring.js']:
                    work.run(label+'-script-'+asset,['node','--check',str(checkout/'examples/editor-home/ui'/asset)],cwd=checkout,env=env)
                work.run(label+'-property-async-core',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'PropertyBlueprintTests','PropertyAuthoringTests','AsyncBlueprintTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-property-observation-guards',[sys.executable,str(checkout/'tests/web/v666_async_property_guards.py'),str(checkout),str(report)],cwd=checkout,env=env)
                for mode in (['normal','storage','conflict'] if label=='lf' else ['loss','late']):
                    work.run(label+'-async-property-'+mode,[sys.executable,str(checkout/'tests/web/v666_async_property_ui.py'),str(checkout),str(report),mode],cwd=checkout,env=env)
                work.run(label+'-async-function-regression',[sys.executable,str(checkout/'tests/web/v666_async_function_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-async-transition-regression',[sys.executable,str(checkout/'tests/web/v666_async_transition_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-property-plan-regression',[sys.executable,str(checkout/'tests/web/v536_property_plan.py'),str(checkout),str(report)],cwd=checkout,env=env)
                if label=='lf':work.run('lf-sync-property-ui',[sys.executable,str(checkout/'tests/web/v536_property_set_ui.py'),str(checkout),str(report)],cwd=checkout,env=env)
                if label=='lf':work.run('lf-copy-source-regression',[sys.executable,str(checkout/'tests/web/v666_node_internal_copy_ui.py'),str(checkout),str(report),'normal'],cwd=checkout,env=env)

            elif args.suite=='async-function':
                for asset in ['feature-authoring.js','set-authoring.js']:
                    work.run(label+'-script-'+asset,['node','--check',str(checkout/'examples/editor-home/ui'/asset)],cwd=checkout,env=env)
                work.run(label+'-async-core',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'AsyncBlueprintTests','SwitchBlueprintTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-function-guards',[sys.executable,str(checkout/'tests/web/v666_async_function_guards.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                work.run(label+'-local-completion-guards',[sys.executable,str(checkout/'tests/web/v666_async_completion_guards.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-async-receipt-guards',[sys.executable,str(checkout/'tests/web/v666_async_transition_guards.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-function-api',[sys.executable,str(checkout/'tests/web/v666_async_function_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                for mode in (['normal','storage','conflict'] if label=='lf' else ['loss','late']):
                    work.run(label+'-function-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_async_function_ui.py'),str(checkout),str(report),mode,'--out-root'],cwd=checkout,env=env)
                work.run(label+'-async-set',[sys.executable,str(checkout/'tests/web/v666_async_set_ui.py'),str(checkout),str(report),'normal','--out-root'],cwd=checkout,env=env)
                work.run(label+'-async-transition-regression',[sys.executable,str(checkout/'tests/web/v666_async_transition_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                regression='v666_root_execution_imports_api.py' if label=='lf' else 'v666_root_execution_api.py'
                work.run(label+'-m12-regression',[sys.executable,str(checkout/'tests/web'/regression),str(checkout),str(report),'--out-root' if label=='lf' else '--nonvoid-root'],cwd=checkout,env=env)
                if label=='lf':work.run('lf-local-completion-api',[sys.executable,str(checkout/'tests/web/v666_async_completion_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)

            elif args.suite=='async-completion':
                for asset in ['feature-authoring.js','set-authoring.js']:
                    work.run(label+'-script-'+asset,['node','--check',str(checkout/'examples/editor-home/ui'/asset)],cwd=checkout,env=env)
                work.run(label+'-async-core',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'AsyncBlueprintTests','SwitchBlueprintTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-completion-guards',[sys.executable,str(checkout/'tests/web/v666_async_completion_guards.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-completion-api',[sys.executable,str(checkout/'tests/web/v666_async_completion_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                for mode in (['normal','storage','conflict'] if label=='lf' else ['loss','late']):
                    work.run(label+'-completion-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_async_completion_ui.py'),str(checkout),str(report),mode,'--out-root'],cwd=checkout,env=env)
                work.run(label+'-async-set',[sys.executable,str(checkout/'tests/web/v666_async_set_ui.py'),str(checkout),str(report),'normal','--out-root'],cwd=checkout,env=env)
                work.run(label+'-async-transition-regression',[sys.executable,str(checkout/'tests/web/v666_async_transition_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                regression='v666_root_execution_imports_api.py' if label=='lf' else 'v666_root_execution_api.py'
                work.run(label+'-m12-regression',[sys.executable,str(checkout/'tests/web'/regression),str(checkout),str(report),'--out-root' if label=='lf' else '--nonvoid-root'],cwd=checkout,env=env)

            elif args.suite=='async-transition':
                work.run(label+'-async-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-async-core',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'AsyncBlueprintTests','SwitchBlueprintTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-async-guards',[sys.executable,str(checkout/'tests/web/v666_async_transition_guards.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-async-api',[sys.executable,str(checkout/'tests/web/v666_async_transition_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                for mode in (['normal','storage','conflict'] if label=='lf' else ['loss','late']):
                    work.run(label+'-async-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_async_transition_ui.py'),str(checkout),str(report),mode,'--out-root'],cwd=checkout,env=env)
                regression='v666_root_execution_imports_api.py' if label=='lf' else 'v666_root_execution_api.py'
                work.run(label+'-m12-regression',[sys.executable,str(checkout/'tests/web'/regression),str(checkout),str(report),'--out-root' if label=='lf' else '--nonvoid-root'],cwd=checkout,env=env)

            elif args.suite in ['root-execution-import-observations','async-runtime']:
                if args.suite=='async-runtime':
                    work.run(label+'-async-core',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'AsyncBlueprintTests','SwitchBlueprintTests','--require-runtime'],cwd=checkout,env=env)
                    work.run(label+'-async-runtime',[sys.executable,str(checkout/'tests/probes/async_runtime.py'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-imports-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-imports-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'RootExecutionBranchTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-imports-ownership',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'blueprint_inherited_body_retains_declaring_node_owner','blueprint_independently_declared_body_cannot_borrow_another_node_owner','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-imports-api',[sys.executable,str(checkout/'tests/web/v666_root_execution_imports_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                for mode in (['normal','cancel','storage','external-conflict'] if label=='lf' else ['loss','late']):
                    work.run(label+'-imports-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_execution_ui.py'),str(checkout),str(report),mode,'--out-root','--imports-root'],cwd=checkout,env=env)
                if label=='lf':
                    work.run('lf-owned-update-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_owned_update_api.py'),str(checkout),str(report),'--out-root','--child-dispatch'],cwd=checkout,env=env)
                    work.run('lf-wrapper-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_wrapper_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                else:
                    work.run('crlf-registered-child-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_override_api.py'),str(checkout),str(report),'--out-root','--external-parent'],cwd=checkout,env=env)
                    work.run('crlf-nonvoid-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_api.py'),str(checkout),str(report),'--nonvoid-root'],cwd=checkout,env=env)
                for name,script in [('registered-cas','v666_registered_read_guards_core.py'),('owned-cas','v536_copy_read_guards_core.py')]:
                    work.run(label+'-'+name,[sys.executable,str(checkout/'tests/web'/script),str(checkout)],cwd=checkout,env=env)
            elif args.suite=='root-execution-owned-updates':
                work.run(label+'-owned-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'RootExecutionBranchTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-owned-ownership',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'blueprint_inherited_body_retains_declaring_node_owner','blueprint_independently_declared_body_cannot_borrow_another_node_owner','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-owned-update-api',[sys.executable,str(checkout/'tests/web/v666_root_execution_owned_update_api.py'),str(checkout),str(report),'--out-root',*(['--inherited-dispatch'] if label=='crlf' else [])],cwd=checkout,env=env)
                if label=='lf':work.run('lf-owned-child-api',[sys.executable,str(checkout/'tests/web/v666_root_execution_owned_update_api.py'),str(checkout),str(report),'--out-root','--child-dispatch'],cwd=checkout,env=env)
                for mode in (['normal','storage','conflict'] if label=='lf' else ['loss','late']):
                    work.run(label+'-owned-update-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_execution_owned_update_ui.py'),str(checkout),str(report),mode,'--out-root',*(['--child-dispatch'] if label=='crlf' else [])],cwd=checkout,env=env)
                if label=='lf':
                    work.run('lf-public-wrapper-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_wrapper_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                    work.run('lf-saved-copy-data-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_copy_api.py'),str(checkout),str(report),'--nonvoid-root'],cwd=checkout,env=env)
                    work.run('lf-all-target-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_multi_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                else:
                    work.run('crlf-registered-child-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_override_api.py'),str(checkout),str(report),'--out-root','--external-parent'],cwd=checkout,env=env)
                    work.run('crlf-nonvoid-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_api.py'),str(checkout),str(report),'--nonvoid-root'],cwd=checkout,env=env)
                work.run(label+'-owned-final-read-cas',[sys.executable,str(checkout/'tests/web/v536_copy_read_guards_core.py'),str(checkout)],cwd=checkout,env=env)

            elif args.suite=='root-execution-wrappers':
                work.run(label+'-wrapper-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-wrapper-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'RootExecutionBranchTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-wrapper-ownership',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'blueprint_inherited_body_retains_declaring_node_owner','blueprint_independently_declared_body_cannot_borrow_another_node_owner','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-wrapper-api',[sys.executable,str(checkout/'tests/web/v666_root_execution_wrapper_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                if label=='lf':work.run('lf-wrapper-nonvoid-api',[sys.executable,str(checkout/'tests/web/v666_root_execution_wrapper_api.py'),str(checkout),str(report),'--nonvoid-root'],cwd=checkout,env=env)
                for mode in (['normal','storage','conflict'] if label=='lf' else ['loss','late']):
                    work.run(label+'-wrapper-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_execution_wrapper_ui.py'),str(checkout),str(report),mode,'--out-root'],cwd=checkout,env=env)
                if label=='lf':
                    for name in ['v508_wrapper_enum_compiler','v508_post_call_compiler']:
                        work.run('lf-'+name,[sys.executable,str(checkout/'tests/web'/(name+'.py')),str(checkout)],cwd=checkout,env=env)
                    work.run('lf-wrapper-observer-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_observers_api.py'),str(checkout),str(report),'--out-root','--observer-root'],cwd=checkout,env=env)
                else:work.run('crlf-wrapper-nonvoid-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_api.py'),str(checkout),str(report),'--nonvoid-root'],cwd=checkout,env=env)
                work.run(label+'-owned-final-read-cas',[sys.executable,str(checkout/'tests/web/v536_copy_read_guards_core.py'),str(checkout)],cwd=checkout,env=env)
            elif args.suite in ['root-execution-caller','root-execution-forwarding','root-execution-observers']:
                forwarding = args.suite == 'root-execution-forwarding'
                observers = args.suite == 'root-execution-observers'
                case = 'observers' if observers else 'forwarding' if forwarding else 'caller'
                flags = ['--out-root', '--observer-root' if observers else '--forward-caller' if forwarding else '--branch-caller']
                api = 'v666_root_execution_observers_api.py' if observers else 'v666_root_execution_forwarding_api.py' if forwarding else 'v666_root_execution_api.py'
                work.run(label+'-'+case+'-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-'+case+'-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'RootExecutionBranchTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-'+case+'-ownership',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'blueprint_inherited_body_retains_declaring_node_owner','blueprint_independently_declared_body_cannot_borrow_another_node_owner','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-'+case+'-api',[sys.executable,str(checkout/'tests/web'/api),str(checkout),str(report),*flags],cwd=checkout,env=env)
                for mode in (['normal','cancel','storage','conflict'] if label=='lf' else ['loss','late']):
                    work.run(label+'-'+case+'-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_execution_ui.py'),str(checkout),str(report),mode,*flags],cwd=checkout,env=env)
                if label=='lf':
                    work.run('lf-'+case+'-native-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_ui.py'),str(checkout),str(report),'normal','--out-root','--native-root'],cwd=checkout,env=env)
                    if observers:
                        work.run('lf-observers-private-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_forwarding_api.py'),str(checkout),str(report),'--out-root','--forward-caller'],cwd=checkout,env=env)
                    if forwarding or observers:
                        work.run('lf-'+case+'-public-caller-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_api.py'),str(checkout),str(report),'--out-root','--branch-caller'],cwd=checkout,env=env)
                    else:
                        work.run('lf-caller-private-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_nested_api.py'),str(checkout),str(report),'--out-root','--nested-root'],cwd=checkout,env=env)
                else:work.run('crlf-'+case+'-nonvoid-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_api.py'),str(checkout),str(report),'--nonvoid-root'],cwd=checkout,env=env)
                work.run(label+'-owned-final-read-cas',[sys.executable,str(checkout/'tests/web/v536_copy_read_guards_core.py'),str(checkout)],cwd=checkout,env=env)
            elif args.suite=='root-execution-native':
                work.run(label+'-native-runtime',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'RootExecutionBranchTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-native-ownership',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'blueprint_inherited_body_retains_declaring_node_owner','blueprint_independently_declared_body_cannot_borrow_another_node_owner','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-native-api',[sys.executable,str(checkout/'tests/web/v666_root_execution_native_api.py'),str(checkout),str(report),'--out-root','--native-root'],cwd=checkout,env=env)
                for mode in (['normal','cancel','storage','conflict'] if label=='lf' else ['loss','late']):
                    work.run(label+'-native-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_execution_ui.py'),str(checkout),str(report),mode,'--out-root','--native-root'],cwd=checkout,env=env)
                work.run(label+'-m11-context-regression',[sys.executable,str(checkout/'tests/web/v666_node_internal_context_api.py'),str(checkout),str(report),*(['--refs'] if label=='crlf' else [])],cwd=checkout,env=env)
                work.run(label+'-native-nonvoid-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_api.py'),str(checkout),str(report),'--nonvoid-root'],cwd=checkout,env=env)
                if label=='lf':work.run('lf-native-private-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_nested_api.py'),str(checkout),str(report),'--out-root','--nested-root'],cwd=checkout,env=env)
                work.run(label+'-owned-final-read-cas',[sys.executable,str(checkout/'tests/web/v536_copy_read_guards_core.py'),str(checkout)],cwd=checkout,env=env)
            elif args.suite=='root-execution-nested':
                work.run(label+'-nested-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-nested-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'RootExecutionBranchTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-nested-ownership',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'blueprint_inherited_body_retains_declaring_node_owner','blueprint_independently_declared_body_cannot_borrow_another_node_owner','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-nested-api',[sys.executable,str(checkout/'tests/web/v666_root_execution_nested_api.py'),str(checkout),str(report),'--out-root','--nested-root'],cwd=checkout,env=env)
                for mode in (['normal','cancel','storage','conflict'] if label=='lf' else ['loss','late']):
                    work.run(label+'-nested-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_execution_ui.py'),str(checkout),str(report),mode,'--out-root','--nested-root'],cwd=checkout,env=env)
                work.run(label+'-nested-zero-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_multi_api.py'),str(checkout),str(report),'--no-callers','--single-target'],cwd=checkout,env=env)
                work.run(label+'-nested-native-data-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_api.py'),str(checkout),str(report),'--nonvoid-root'],cwd=checkout,env=env)
                work.run(label+'-nested-copy-regression',[sys.executable,str(checkout/('tests/web/v666_root_execution_copy_'+('api.py' if label=='lf' else 'ui.py'))),str(checkout),str(report),*(['cancel'] if label=='crlf' else []),'--nonvoid-root'],cwd=checkout,env=env)
                if label=='lf':work.run('lf-nested-providers-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_multi_api.py'),str(checkout),str(report),'--multi-root','--providers-root'],cwd=checkout,env=env)
                work.run(label+'-owned-final-read-cas',[sys.executable,str(checkout/'tests/web/v536_copy_read_guards_core.py'),str(checkout)],cwd=checkout,env=env)
            elif args.suite=='root-execution-providers':
                work.run(label+'-providers-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-providers-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'RootExecutionBranchTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-providers-ownership',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'blueprint_inherited_body_retains_declaring_node_owner','blueprint_independently_declared_body_cannot_borrow_another_node_owner','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-providers-api',[sys.executable,str(checkout/'tests/web/v666_root_execution_multi_api.py'),str(checkout),str(report),'--multi-root','--providers-root'],cwd=checkout,env=env)
                for mode in (['normal','cancel','storage','conflict'] if label=='lf' else ['loss','late']):
                    work.run(label+'-providers-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_execution_ui.py'),str(checkout),str(report),mode,'--multi-root','--providers-root'],cwd=checkout,env=env)
                work.run(label+'-providers-zero-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_multi_api.py'),str(checkout),str(report),'--no-callers','--single-target'],cwd=checkout,env=env)
                work.run(label+'-providers-native-data-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_api.py'),str(checkout),str(report),'--nonvoid-root'],cwd=checkout,env=env)
                work.run(label+'-providers-copy-regression',[sys.executable,str(checkout/('tests/web/v666_root_execution_copy_'+('api.py' if label=='lf' else 'ui.py'))),str(checkout),str(report),*(['cancel'] if label=='crlf' else []),'--nonvoid-root'],cwd=checkout,env=env)
                work.run(label+'-owned-final-read-cas',[sys.executable,str(checkout/'tests/web/v536_copy_read_guards_core.py'),str(checkout)],cwd=checkout,env=env)
            elif args.suite=='public-return-data':
                work.run(label+'-return-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-return-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'RootExecutionBranchTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-return-ownership',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'blueprint_inherited_body_retains_declaring_node_owner','blueprint_independently_declared_body_cannot_borrow_another_node_owner','--require-runtime'],cwd=checkout,env=env)
                flows=[('copy','copy','cancel',[]),('creating','copy_creating','storage',[]),('child','override','conflict',[]),('registered','registered','loss',[]),('registered-copy','registered','late',['--registered-copy']),('registered-new','copy_creating','project',['--registered-creating'])]
                for name,script,mode,flags in flows:
                    work.run(label+'-return-'+name,[sys.executable,str(checkout/('tests/web/v666_root_execution_'+('registered_copy' if name=='registered-copy' and label=='lf' else script)+('_api.py' if label=='lf' else '_ui.py'))),str(checkout),str(report),*([mode] if label=='crlf' else []),'--nonvoid-root',*(['--external-parent'] if label=='lf' and name=='child' else flags)],cwd=checkout,env=env)
                if label=='lf':
                    work.run(label+'-return-void-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_copy_api.py'),str(checkout),str(report),'--out-root'],cwd=checkout,env=env)
                    work.run(label+'-return-root-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_api.py'),str(checkout),str(report),'--nonvoid-root'],cwd=checkout,env=env)
                else:
                    work.run(label+'-return-void-regression',[sys.executable,str(checkout/'tests/web/v666_root_execution_override_ui.py'),str(checkout),str(report),'normal','--out-root'],cwd=checkout,env=env)
                work.run(label+'-owned-final-read-cas',[sys.executable,str(checkout/'tests/web/v536_copy_read_guards_core.py'),str(checkout)],cwd=checkout,env=env)
            elif args.suite in ['root-execution','root-execution-out','root-execution-data-void','root-execution-compound-owned','root-execution-provider-import','root-execution-nonvoid']:
                root_args=['--nonvoid-root'] if args.suite=='root-execution-nonvoid' else ['--provider-import'] if args.suite=='root-execution-provider-import' else ['--compound-root'] if args.suite=='root-execution-compound-owned' else ['--data-root'] if args.suite=='root-execution-data-void' else ['--out-root'] if args.suite=='root-execution-out' else []
                work.run(label+'-root-script',['node','--check',str(checkout/'examples/editor-home/ui/feature-authoring.js')],cwd=checkout,env=env)
                work.run(label+'-root-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'RootExecutionBranchTests','SwitchBlueprintTests','NestedBlueprintTests','BlueprintConversionTests','ExternalRefTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-root-ownership',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'blueprint_inherited_body_retains_declaring_node_owner','blueprint_independently_declared_body_cannot_borrow_another_node_owner','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-root-api',[sys.executable,str(checkout/'tests/web/v666_root_execution_api.py'),str(checkout),str(report),*root_args],cwd=checkout,env=env)
                for mode in (['normal','cancel','storage','conflict'] if label=='lf' else ['loss','late']):
                    work.run(label+'-root-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_execution_ui.py'),str(checkout),str(report),mode,*root_args],cwd=checkout,env=env)
                if args.suite in ['root-execution-out','root-execution-data-void','root-execution-compound-owned','root-execution-provider-import','root-execution-nonvoid']:
                    baseline='v666_root_execution_api.py' if label=='lf' else 'v666_root_execution_ui.py'
                    work.run(label+'-root-void-regression',[sys.executable,str(checkout/'tests/web'/baseline),str(checkout),str(report),*(['normal'] if label=='crlf' else []),*(['--provider-import'] if args.suite=='root-execution-nonvoid' else ['--compound-root'] if args.suite=='root-execution-provider-import' else ['--data-root'] if args.suite=='root-execution-compound-owned' else ['--out-root'] if args.suite=='root-execution-data-void' else [])],cwd=checkout,env=env)
                if args.suite=='root-execution-nonvoid' and label=='lf':
                    work.run(label+'-root-multi-target-ui',[sys.executable,str(checkout/'tests/web/v666_root_execution_ui.py'),str(checkout),str(report),'normal','--multi-root'],cwd=checkout,env=env)
                regression='v666_node_branch_exit_api.py' if label=='lf' else 'v666_node_internal_external_override_api.py'
                work.run(label+'-m11-regression',[sys.executable,str(checkout/'tests/web'/regression),str(checkout),str(report)],cwd=checkout,env=env)
                work.run(label+'-owned-final-read-cas',[sys.executable,str(checkout/'tests/web/v536_copy_read_guards_core.py'),str(checkout)],cwd=checkout,env=env)
                if args.suite in ['root-execution-data-void','root-execution-compound-owned','root-execution-provider-import','root-execution-nonvoid']:
                    regression='v666_root_execution_copy_creating_api.py' if label=='lf' else 'v666_root_execution_registered_copy_api.py'
                    work.run(label+'-copy-contract-regression',[sys.executable,str(checkout/'tests/web'/regression),str(checkout),str(report),'--out-root',*(['--registered-creating'] if label=='lf' else [])],cwd=checkout,env=env)
            elif args.suite=='node-internal-nested':
                work.run(label+'-nested-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'NestedBlueprintTests','BlueprintConversionTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-nested-ownership',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'blueprint_inherited_body_retains_declaring_node_owner','blueprint_independently_declared_body_cannot_borrow_another_node_owner','--require-runtime'],cwd=checkout,env=env)
                for depth in ([2,7,8] if label=='lf' else [2]):
                    work.run(label+'-nested-api-'+str(depth),[sys.executable,str(checkout/'tests/web/v666_node_internal_nested_api.py'),str(checkout),str(report),'--depth='+str(depth)],cwd=checkout,env=env)
                for mode in (['normal','storage','conflict','project'] if label=='lf' else ['loss','late']):
                    work.run(label+'-nested-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_node_internal_nested_ui.py'),str(checkout),str(report),mode,'--depth=2'],cwd=checkout,env=env)
                work.run(label+'-action-private-icons',[sys.executable,str(checkout/'tests/web/v666_action_icon_ui.py'),str(checkout),str(report),'normal','private'],cwd=checkout,env=env)
                work.run(label+'-action-copy-icons',[sys.executable,str(checkout/'tests/web/v666_action_icon_copy_ui.py'),str(checkout),str(report),'normal'],cwd=checkout,env=env)
            elif args.suite=='node-internal-storage':
                work.run(label+'-storage-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'ExternalRefTests','static_private_helpers_preserve_repeated_ref_out_caller_storage','whole_body_context_preserves_calls_scope_this_recursion_names_targets_and_crlf','whole_out_body_conversion_preserves_original_member_scoped_import_and_other_target','--require-runtime'],cwd=checkout,env=env)
                cases=[('root',[]),('out-only',['--out-only']),('exception',['--exception'])] if label=='lf' else [('private-local',['--private','--local']),('array',['--array'])]
                for name,flags in cases:
                    work.run(label+'-storage-api-'+name,[sys.executable,str(checkout/'tests/web/v666_node_internal_storage_api.py'),str(checkout),str(report),*flags],cwd=checkout,env=env)
                for mode in (['normal','storage'] if label=='lf' else ['loss','late']):
                    work.run(label+'-storage-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_node_internal_storage_ui.py'),str(checkout),str(report),mode,*(['--private','--local'] if mode=='late' else [])],cwd=checkout,env=env)
                work.run(label+'-nested-value-regression',[sys.executable,str(checkout/'tests/web/v666_node_internal_nested_api.py'),str(checkout),str(report),'--depth=2'],cwd=checkout,env=env)
            elif args.suite=='node-internal-context':
                work.run(label+'-script-raw-edits',['node',str(checkout/'tests/web/v666_script_raw_edits.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-context-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'NestedBlueprintTests','BlueprintConversionTests','ExternalRefTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-context-ownership',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'blueprint_inherited_body_retains_declaring_node_owner','blueprint_independently_declared_body_cannot_borrow_another_node_owner','--require-runtime'],cwd=checkout,env=env)
                cases=[('root',[]),('refs',['--refs']),('repeat',['--repeat'])] if label=='lf' else [('refs',['--refs']),('void',['--void'])]
                for name,flags in cases:
                    work.run(label+'-context-api-'+name,[sys.executable,str(checkout/'tests/web/v666_node_internal_context_api.py'),str(checkout),str(report),*flags],cwd=checkout,env=env)
                for mode in (['normal','storage','conflict','project'] if label=='lf' else ['loss','late']):
                    work.run(label+'-context-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_node_internal_context_ui.py'),str(checkout),str(report),mode,*(['--refs'] if mode=='late' else [])],cwd=checkout,env=env)
                work.run(label+'-context-storage-regression',[sys.executable,str(checkout/'tests/web/v666_node_internal_storage_api.py'),str(checkout),str(report),*(['--private','--local'] if label=='crlf' else [])],cwd=checkout,env=env)
                work.run(label+'-context-nested-regression',[sys.executable,str(checkout/'tests/web/v666_node_internal_nested_api.py'),str(checkout),str(report),'--depth=2'],cwd=checkout,env=env)
            elif args.suite in ['node-internal-override','node-internal-external-override']:
                work.run(label+'-script-raw-edits',['node',str(checkout/'tests/web/v666_script_raw_edits.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-context-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'SwitchBlueprintTests','NestedBlueprintTests','BlueprintConversionTests','ExternalRefTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-copy-ownership',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'blueprint_inherited_body_retains_declaring_node_owner','blueprint_independently_declared_body_cannot_borrow_another_node_owner','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-private-copy-checkpoint',[sys.executable,str(checkout/'tests/web/v536_private_copy_checkpoint.py'),str(checkout),str(report)],cwd=checkout,env=env)
                regression='v666_node_internal_context_api.py' if label=='lf' else 'v666_node_internal_branch_api.py'
                work.run(label+'-saved-copy-regression',[sys.executable,str(checkout/'tests/web'/regression),str(checkout),str(report),'--copy',*(['--refs','--nested','--repeat'] if label=='crlf' else [])],cwd=checkout,env=env)
                external=args.suite=='node-internal-external-override'
                api='v666_node_internal_external_override_api.py' if external else 'v666_node_internal_override_api.py'
                if external:
                    for name,script in [('registered-final-read-cas','v666_registered_read_guards_core.py'),('owned-final-read-cas','v536_copy_read_guards_core.py')]:
                        work.run(label+'-'+name,[sys.executable,str(checkout/'tests/web'/script),str(checkout)],cwd=checkout,env=env)
                    work.run(label+'-owned-override-regression',[sys.executable,str(checkout/'tests/web/v666_node_internal_override_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                for name,flags in [('root',[]),('nested',['--nested'])]:
                    work.run(label+'-override-api-'+name,[sys.executable,str(checkout/'tests/web'/api),str(checkout),str(report),*flags],cwd=checkout,env=env)
                cases=[('normal',[]),('cancel',[]),('conflict',['--parent-conflict']),('storage',[])] if label=='lf' else [('loss',[]),('late',[]),('project',[])]
                for mode,flags in cases:
                    work.run(label+'-override-ui-'+mode,[sys.executable,str(checkout/'tests/web'/('v666_node_internal_external_override_ui.py' if external else 'v666_node_internal_override_ui.py')),str(checkout),str(report),mode,*flags],cwd=checkout,env=env)

            elif args.suite in ['node-internal-copy-creating','node-internal-copy-frames']:
                work.run(label+'-script-raw-edits',['node',str(checkout/'tests/web/v666_script_raw_edits.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-context-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'SwitchBlueprintTests','NestedBlueprintTests','BlueprintConversionTests','ExternalRefTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-copy-ownership',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'blueprint_inherited_body_retains_declaring_node_owner','blueprint_independently_declared_body_cannot_borrow_another_node_owner','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-private-copy-checkpoint',[sys.executable,str(checkout/'tests/web/v536_private_copy_checkpoint.py'),str(checkout),str(report)],cwd=checkout,env=env)
                regression='v666_node_internal_context_api.py' if label=='lf' else 'v666_node_internal_branch_api.py'
                work.run(label+'-saved-copy-regression',[sys.executable,str(checkout/'tests/web'/regression),str(checkout),str(report),'--copy',*(['--refs','--nested',*(['--repeat'] if args.suite=='node-internal-copy-frames' else [])] if label=='crlf' else [])],cwd=checkout,env=env)
                cases=([('nested',['--nested','--compile']),('branch',['--branch']),('root-context',['--context','--raw-copy','--refs'])] if label=='lf' else [('branch-refs',['--branch','--nested','--refs','--compile']),('legacy',['--legacy'])]) if args.suite=='node-internal-copy-frames' else ([('compile',['--compile']),('context',['--context','--raw-copy'])] if label=='lf' else [('legacy',['--legacy']),('refs',['--context','--refs'])])
                for name,flags in cases:
                    work.run(label+'-creating-copy-api-'+name,[sys.executable,str(checkout/'tests/web/v666_node_internal_copy_creating_api.py'),str(checkout),str(report),*flags],cwd=checkout,env=env)
                cases=([('normal',['--nested']),('cancel',['view','--nested']),('storage',['view','--branch','--nested']),('conflict',['--branch'])] if label=='lf' else [('loss',['view','--branch','--nested','--refs']),('late',['--branch','--nested','--refs']),('project',['--nested']),('owner',['view','--nested'])]) if args.suite=='node-internal-copy-frames' else ([('normal',[]),('cancel',['view']),('storage',['view']),('conflict',[])] if label=='lf' else [('loss',['view']),('late',[]),('project',[]),('owner',['view','--context','--refs'])])
                for mode,flags in cases:
                    work.run(label+'-creating-copy-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_node_internal_copy_creating_ui.py'),str(checkout),str(report),mode,*flags],cwd=checkout,env=env)

            elif args.suite=='node-internal-copy-context':
                work.run(label+'-script-raw-edits',['node',str(checkout/'tests/web/v666_script_raw_edits.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-context-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'SwitchBlueprintTests','NestedBlueprintTests','BlueprintConversionTests','ExternalRefTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-copy-ownership',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'blueprint_inherited_body_retains_declaring_node_owner','blueprint_independently_declared_body_cannot_borrow_another_node_owner','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-direct-context-regression',[sys.executable,str(checkout/'tests/web/v666_node_internal_context_api.py'),str(checkout),str(report),*(['--refs'] if label=='crlf' else [])],cwd=checkout,env=env)
                work.run(label+'-copy-branch-regression',[sys.executable,str(checkout/'tests/web/v666_node_internal_branch_api.py'),str(checkout),str(report),'--copy',*(['--refs','--nested'] if label=='crlf' else [])],cwd=checkout,env=env)
                cases=[('root',[]),('raw',['--raw-copy']),('shared',['--shared'])] if label=='lf' else [('refs',['--raw-copy','--refs']),('repeat',['--repeat']),('void',['--raw-copy','--void'])]
                for name,flags in cases:
                    work.run(label+'-copy-context-api-'+name,[sys.executable,str(checkout/'tests/web/v666_node_internal_context_api.py'),str(checkout),str(report),'--copy',*flags],cwd=checkout,env=env)
                cases=[('normal',['--raw-copy']),('storage',['view']),('conflict',[])] if label=='lf' else [('loss',['view','--raw-copy','--refs']),('late',['--refs']),('project',[])]
                for mode,flags in cases:
                    work.run(label+'-copy-context-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_node_internal_context_ui.py'),str(checkout),str(report),mode,'--copy',*flags],cwd=checkout,env=env)
            elif args.suite=='node-internal-copy-branches':
                work.run(label+'-script-raw-edits',['node',str(checkout/'tests/web/v666_script_raw_edits.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-branch-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'SwitchBlueprintTests','NestedBlueprintTests','BlueprintConversionTests','ExternalRefTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-copy-ownership',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'blueprint_inherited_body_retains_declaring_node_owner','blueprint_independently_declared_body_cannot_borrow_another_node_owner','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-direct-branch-regression',[sys.executable,str(checkout/'tests/web/v666_node_internal_branch_api.py'),str(checkout),str(report),*(['--nested'] if label=='crlf' else [])],cwd=checkout,env=env)
                work.run(label+'-copy-storage-regression',[sys.executable,str(checkout/'tests/web/v666_node_internal_copy_api.py'),str(checkout),str(report),'normal','--storage-copy',*(['--private','--local'] if label=='crlf' else [])],cwd=checkout,env=env)
                cases=[('root',[]),('owned-case',['--owned-case','--repeat']),('shared',['--shared'])] if label=='lf' else [('nested',['--nested']),('refs',['--refs','--nested'])]
                for name,flags in cases:
                    work.run(label+'-copy-branch-api-'+name,[sys.executable,str(checkout/'tests/web/v666_node_internal_branch_api.py'),str(checkout),str(report),'--copy',*flags],cwd=checkout,env=env)
                cases=[('normal',[]),('storage',['view','--nested']),('conflict',[])] if label=='lf' else [('loss',['view','--nested']),('late',['--refs','--nested']),('project',[])]
                for mode,flags in cases:
                    work.run(label+'-copy-branch-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_node_internal_branch_ui.py'),str(checkout),str(report),mode,'--copy',*flags],cwd=checkout,env=env)
            elif args.suite=='node-internal-copy-storage':
                work.run(label+'-script-raw-edits',['node',str(checkout/'tests/web/v666_script_raw_edits.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-copy-ownership',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'blueprint_inherited_body_retains_declaring_node_owner','blueprint_independently_declared_body_cannot_borrow_another_node_owner','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-storage-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'ExternalRefTests','static_private_helpers_preserve_repeated_ref_out_caller_storage','whole_body_context_preserves_calls_scope_this_recursion_names_targets_and_crlf','whole_out_body_conversion_preserves_original_member_scoped_import_and_other_target','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-general-copy-api',[sys.executable,str(checkout/'tests/web/v666_node_internal_copy_api.py'),str(checkout),str(report),'normal',*(['--depth=2'] if label=='crlf' else [])],cwd=checkout,env=env)
                cases=[('forwarded',[]),('out-only',['--out-only']),('exception',['--exception'])] if label=='lf' else [('private-local',['--private','--local']),('array',['--array'])]
                for name,flags in cases:
                    work.run(label+'-copy-storage-api-'+name,[sys.executable,str(checkout/'tests/web/v666_node_internal_copy_api.py'),str(checkout),str(report),'normal','--storage-copy',*flags],cwd=checkout,env=env)
                cases=[('normal',[]),('storage',['view','--private','--local']),('conflict',[])] if label=='lf' else [('loss',[]),('late',['view','--private','--local'])]
                for mode,flags in cases:
                    work.run(label+'-copy-storage-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_node_internal_copy_ui.py'),str(checkout),str(report),mode,'--storage-copy',*flags],cwd=checkout,env=env)
            elif args.suite in ['node-internal-copy','node-internal-copy-nested']:
                work.run(label+'-script-raw-edits',['node',str(checkout/'tests/web/v666_script_raw_edits.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-copy-ownership',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'blueprint_inherited_body_retains_declaring_node_owner','blueprint_independently_declared_body_cannot_borrow_another_node_owner','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-direct-api',[sys.executable,str(checkout/'tests/web/v666_node_internal_api.py'),str(checkout),str(report),*(['void'] if label=='crlf' else [])],cwd=checkout,env=env)
                if label=='lf':
                    work.run(label+'-direct-late',[sys.executable,str(checkout/'tests/web/v666_node_internal_ui.py'),str(checkout),str(report),'late'],cwd=checkout,env=env)
                    work.run(label+'-copy-icons',[sys.executable,str(checkout/'tests/web/v666_action_icon_copy_ui.py'),str(checkout),str(report),'normal','view'],cwd=checkout,env=env)
                    work.run(label+'-copy-shared',[sys.executable,str(checkout/'tests/web/v666_node_internal_copy_api.py'),str(checkout),str(report),'normal','--shared'],cwd=checkout,env=env)
                work.run(label+'-copy-api',[sys.executable,str(checkout/'tests/web/v666_node_internal_copy_api.py'),str(checkout),str(report)],cwd=checkout,env=env)
                for mode in (['normal','storage','conflict'] if label=='lf' else ['loss','late']):
                    work.run(label+'-copy-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_node_internal_copy_ui.py'),str(checkout),str(report),mode,*(['view'] if mode=='late' else [])],cwd=checkout,env=env)
                if args.suite=='node-internal-copy-nested':
                    for depth in [2]:
                        work.run(label+'-nested-copy-api-'+str(depth),[sys.executable,str(checkout/'tests/web/v666_node_internal_copy_api.py'),str(checkout),str(report),'normal','--depth='+str(depth)],cwd=checkout,env=env)
                    for mode in (['normal','project'] if label=='lf' else ['loss','late']):
                        work.run(label+'-nested-copy-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_node_internal_copy_ui.py'),str(checkout),str(report),mode,'--depth=2',*(['view'] if mode in ['late','storage'] else [])],cwd=checkout,env=env)

            elif args.suite=='node-branch-exits':
                work.run(label+'-script-raw-edits',['node',str(checkout/'tests/web/v666_script_raw_edits.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-exit-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'SwitchBlueprintTests','NestedBlueprintTests','BlueprintConversionTests','ExternalRefTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-exit-ownership',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'blueprint_inherited_body_retains_declaring_node_owner','blueprint_independently_declared_body_cannot_borrow_another_node_owner','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-exit-forward-regression',[sys.executable,str(checkout/'tests/web/v666_node_internal_branch_api.py'),str(checkout),str(report),*(['--refs'] if label=='crlf' else [])],cwd=checkout,env=env)
                if label=='lf':work.run(label+'-exit-forward-late',[sys.executable,str(checkout/'tests/web/v666_node_internal_branch_ui.py'),str(checkout),str(report),'late','--refs'],cwd=checkout,env=env)
                for name,flags in ([('root',[]),('nested',['--nested'])] if label=='lf' else [('refs',['--refs'])]):
                    work.run(label+'-exit-api-'+name,[sys.executable,str(checkout/'tests/web/v666_node_branch_exit_api.py'),str(checkout),str(report),*flags],cwd=checkout,env=env)
                for mode in (['draft','storage','conflict','root'] if label=='lf' else ['loss','late']):
                    work.run(label+'-exit-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_node_branch_exit_ui.py'),str(checkout),str(report),mode,*(['--refs'] if mode=='late' else [])],cwd=checkout,env=env)

            elif args.suite=='node-internal-branches':
                work.run(label+'-script-raw-edits',['node',str(checkout/'tests/web/v666_script_raw_edits.mjs'),str(checkout)],cwd=checkout,env=env)
                work.run(label+'-branch-native',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'SwitchBlueprintTests','NestedBlueprintTests','BlueprintConversionTests','ExternalRefTests','--require-runtime'],cwd=checkout,env=env)
                work.run(label+'-branch-ownership',[dotnet,str(checkout/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),'blueprint_inherited_body_retains_declaring_node_owner','blueprint_independently_declared_body_cannot_borrow_another_node_owner','--require-runtime'],cwd=checkout,env=env)
                for script in ['v508_wrapper_enum_compiler.py','v508_post_call_compiler.py']:
                    work.run(label+'-'+Path(script).stem,[sys.executable,str(checkout/'tests/web'/script),str(checkout)],cwd=checkout,env=env)
                cases=[('root',[]),('nested',['--nested']),('owned-case',['--owned-case']),('repeat',['--repeat'])] if label=='lf' else [('refs',['--refs']),('root',[])]
                for name,flags in cases:
                    work.run(label+'-branch-api-'+name,[sys.executable,str(checkout/'tests/web/v666_node_internal_branch_api.py'),str(checkout),str(report),*flags],cwd=checkout,env=env)
                for mode in (['normal','storage','conflict','project','loss-edit'] if label=='lf' else ['loss','late']):
                    work.run(label+'-branch-ui-'+mode,[sys.executable,str(checkout/'tests/web/v666_node_internal_branch_ui.py'),str(checkout),str(report),mode,*(['--refs'] if mode=='late' else [])],cwd=checkout,env=env)
                work.run(label+'-branch-context-regression',[sys.executable,str(checkout/'tests/web/v666_node_internal_context_api.py'),str(checkout),str(report),*(['--refs'] if label=='crlf' else [])],cwd=checkout,env=env)
                work.run(label+'-branch-storage-regression',[sys.executable,str(checkout/'tests/web/v666_node_internal_storage_api.py'),str(checkout),str(report),*(['--private','--local'] if label=='crlf' else [])],cwd=checkout,env=env)
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
        if args.suite=='node-internal-nested':
            work.run('packaged-node-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-nested-node-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_nested_ui.py'),str(package/'content'),str(packaged_report),'normal','--depth=2'],cwd=checkout,env=env)
        elif args.suite=='node-internal-storage':
            work.run('packaged-node-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-storage-node-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_storage_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        elif args.suite=='run-bounds':
            work.run('packaged-run-bounds',[sys.executable,str(checkout/'tests/web/v666_run_bounds_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        elif args.suite=='run-rate':
            work.run('packaged-run-rate',[sys.executable,str(checkout/'tests/web/v666_run_rate_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)

        elif args.suite=='startup-transport':
            work.run('packaged-startup-transport',[sys.executable,str(checkout/'tests/web/v666_startup_transport_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        elif args.suite=='resource-description':
            for name in ['description','content','pdf','office']:
                work.run('packaged-resource-'+name,[sys.executable,str(checkout/('tests/web/v666_resource_'+name+'_ui.py')),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)

        elif args.suite=='resource-pdf':
            for name in ['pdf','office','images','content']:
                work.run('packaged-resource-'+name,[sys.executable,str(checkout/('tests/web/v666_resource_'+name+'_ui.py')),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)

        elif args.suite=='resource-office':
            work.run('packaged-resource-office',[sys.executable,str(checkout/'tests/web/v666_resource_office_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-resource-images',[sys.executable,str(checkout/'tests/web/v666_resource_images_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-resource-content',[sys.executable,str(checkout/'tests/web/v666_resource_content_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)

        elif args.suite=='resource-destination':
            work.run('packaged-resource-destination',[sys.executable,str(checkout/'tests/web/v666_resource_destination_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-resource-batch',[sys.executable,str(checkout/'tests/web/v666_resource_batch_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-resource-images',[sys.executable,str(checkout/'tests/web/v666_resource_images_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-resource-content',[sys.executable,str(checkout/'tests/web/v666_resource_content_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        elif args.suite=='resource-batch':
            work.run('packaged-resource-batch',[sys.executable,str(checkout/'tests/web/v666_resource_batch_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-resource-images',[sys.executable,str(checkout/'tests/web/v666_resource_images_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-resource-content',[sys.executable,str(checkout/'tests/web/v666_resource_content_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        elif args.suite=='resource-images':
            work.run('packaged-resource-images',[sys.executable,str(checkout/'tests/web/v666_resource_images_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-resource-content',[sys.executable,str(checkout/'tests/web/v666_resource_content_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        elif args.suite=='resource-content':
            work.run('packaged-resource-content',[sys.executable,str(checkout/'tests/web/v666_resource_content_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        elif args.suite=='resource-multi-deletion':
            work.run('packaged-resource-multi-deletion',[sys.executable,str(checkout/'tests/web/v666_resource_multi_deletion_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        elif args.suite=='resource-folder-deletion':
            work.run('packaged-resource-folder-deletion',[sys.executable,str(checkout/'tests/web/v666_resource_folder_deletion_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        elif args.suite=='resource-file-deletion':
            work.run('packaged-resource-file-deletion',[sys.executable,str(checkout/'tests/web/v666_resource_file_deletion_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        elif args.suite=='resource-file-names':
            work.run('packaged-resource-file-names',[sys.executable,str(checkout/'tests/web/v666_resource_file_names_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        elif args.suite=='resource-folder-names':
            work.run('packaged-resource-folder-names',[sys.executable,str(checkout/'tests/web/v666_resource_folder_names_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        elif args.suite=='resource-layout':
            work.run('packaged-resource-layout',[sys.executable,str(checkout/'tests/web/v666_resource_layout_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        elif args.suite=='resource-preview':
            work.run('packaged-resource-preview',[sys.executable,str(checkout/'tests/web/v666_resource_preview_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        elif args.suite=='resource-import':
            work.run('packaged-resource-ui',[sys.executable,str(checkout/'tests/web/v666_resources_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        elif args.suite=='office-finder':
            work.run('packaged-office-finder',[sys.executable,str(checkout/'tests/web/v666_office_finder_ui.py'),str(package/'content'),str(packaged_report),'live'],cwd=checkout,env=env)

        elif args.suite=='office-io-poll':
            work.run('packaged-completed-io',[sys.executable,str(checkout/'tests/web/v666_office_workers_ui.py'),str(package/'content'),str(packaged_report),'io'],cwd=checkout,env=env)

        elif args.suite=='office-active-io':
            work.run('packaged-office-active',[sys.executable,str(checkout/'tests/web/v666_office_workers_ui.py'),str(package/'content'),str(packaged_report),'phase-ui'],cwd=checkout,env=env)

        elif args.suite=='office-io':
            work.run('packaged-office-io',[sys.executable,str(checkout/'tests/web/v666_office_workers_ui.py'),str(package/'content'),str(packaged_report),'io'],cwd=checkout,env=env)


        elif args.suite=='office-arrangement':
            work.run('packaged-office-arrangement',[sys.executable,str(checkout/'tests/web/v666_office_arrangement_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)

        elif args.suite=='office-workers':
            work.run('packaged-office-workers-live',[sys.executable,str(checkout/'tests/web/v666_office_workers_ui.py'),str(package/'content'),str(packaged_report),'live'],cwd=checkout,env=env)

        elif args.suite=='office-view':
            work.run('packaged-office-view',[sys.executable,str(checkout/'tests/web/v666_office_view_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)

        elif args.suite=='native-intent-late':
            work.run('packaged-native-intent-normal',[sys.executable,str(checkout/'tests/web/v666_native_intent_late_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)

        elif args.suite=='native-read-close':
            work.run('packaged-native-read-close-ui',[sys.executable,str(checkout/'tests/web/v666_native_read_close_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)

        elif args.suite=='native-zoom-lifetime':
            work.run('packaged-native-zoom-engine',[sys.executable,str(checkout/'tests/web/v666_native_zoom_lifetime_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)

        elif args.suite=='zoom-lifetime':
            work.run('packaged-zoom-lifetime-ui',[sys.executable,str(checkout/'tests/web/v666_zoom_lifetime_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)

        elif args.suite=='finder-modules':
            work.run('packaged-module-ui',[sys.executable,str(checkout/'tests/web/v666_finder_modules_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)

        elif args.suite=='declaration-reload':
            for mode,flags in [('normal',[]),('failure',['view'])]:
                work.run('packaged-declaration-reload-'+mode,[sys.executable,str(checkout/'tests/web/v666_declaration_reload_ui.py'),str(package/'content'),str(packaged_report),mode,*flags],cwd=checkout,env=env)
            work.run('packaged-declaration-header',[sys.executable,str(checkout/'tests/web/v666_declaration_icon_ui.py'),str(package/'content'),str(packaged_report),'mixed-preserve','category'],cwd=checkout,env=env)

        elif args.suite in ['finder-content','finder-definitions','finder-bodies','finder-defaults']:
            for mode in ['basic','lifecycle']:
                work.run('packaged-finder-content-'+mode,[sys.executable,str(checkout/'tests/web/v666_finder_content_ui.py'),str(package/'content'),str(packaged_report),mode],cwd=checkout,env=env)

            if args.suite in ['finder-definitions','finder-bodies','finder-defaults']:
                work.run('packaged-finder-definitions',[sys.executable,str(checkout/'tests/web/v666_finder_definitions_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)

            if args.suite in ['finder-bodies','finder-defaults']:
                for mode in ['normal','guards']:
                    work.run('packaged-finder-bodies-'+mode,[sys.executable,str(checkout/'tests/web/v666_finder_bodies_ui.py'),str(package/'content'),str(packaged_report),mode],cwd=checkout,env=env)
            if args.suite=='finder-defaults':
                work.run('packaged-finder-defaults-normal',[sys.executable,str(checkout/'tests/web/v666_finder_defaults_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)

        elif args.suite=='workspace-finder':
            for mode in ['basic','scope']:
                work.run('packaged-workspace-finder-'+mode,[sys.executable,str(checkout/'tests/web/v666_workspace_finder_ui.py'),str(package/'content'),str(packaged_report),mode],cwd=checkout,env=env)

        elif args.suite=='run-grid':
            work.run('packaged-run-grid',[sys.executable,str(checkout/'tests/web/v666_run_grid_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        elif args.suite=='run-wide':
            work.run('packaged-run-wide',[sys.executable,str(checkout/'tests/web/v666_run_wide_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        elif args.suite=='run-auto':
            work.run('packaged-run-auto',[sys.executable,str(checkout/'tests/web/v666_run_auto_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        elif args.suite=='run-presets':
            work.run('packaged-run-presets',[sys.executable,str(checkout/'tests/web/v666_run_presets_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)

        elif args.suite=='run-audio':
            work.run('packaged-run-audio',[sys.executable,str(checkout/'tests/web/v666_run_audio_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)

        elif args.suite in ['run-resolution','run-surface']:
            if args.suite=='run-resolution':work.run('packaged-run-resolution',[sys.executable,str(checkout/'tests/web/v666_run_resolution_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-run-surface',[sys.executable,str(checkout/'tests/web/v666_run_surface_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)

        elif args.suite=='run-developer':
            work.run('packaged-run-developer',[sys.executable,str(checkout/'tests/web/v666_run_developer_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)

        elif args.suite=='run-fullscreen':
            for mode in ['normal','fallback']:
                work.run('packaged-run-fullscreen-'+mode,[sys.executable,str(checkout/'tests/web/v666_run_fullscreen_ui.py'),str(package/'content'),str(packaged_report),mode],cwd=checkout,env=env)

        elif args.suite=='route-group-recovery':
            for mode in ['normal', 'loss']:
                work.run('packaged-route-group-'+mode,[sys.executable,str(checkout/'tests/web/v666_route_group_recovery_ui.py'),str(package/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='root-void-name-recovery':
            for mode in ['normal', 'loss']:
                work.run('packaged-root-void-name-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_void_name_recovery_ui.py'),str(package/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='node-names-recovery':
            for mode in ['normal', 'loss']:
                work.run('packaged-node-names-'+mode,[sys.executable,str(checkout/'tests/web/v666_node_names_recovery_ui.py'),str(package/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='root-return-position-recovery':
            for mode in ['normal', 'loss']:
                work.run('packaged-root-return-position-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_return_position_recovery_ui.py'),str(package/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='node-text-recovery':
            for mode in ['normal', 'loss']:
                work.run('packaged-node-text-'+mode,[sys.executable,str(checkout/'tests/web/v666_node_text_recovery_ui.py'),str(package/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='root-value-rename-recovery':
            for mode in ['normal', 'loss']:
                work.run('packaged-root-value-rename-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_value_rename_recovery_ui.py'),str(package/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='text-pair-recovery':
            for mode in ['normal', 'loss']:
                work.run('packaged-text-pair-'+mode,[sys.executable,str(checkout/'tests/web/v666_text_pair_recovery_ui.py'),str(package/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='direct-creation-recovery':
            for mode in ['normal', 'loss']:
                work.run('packaged-direct-creation-'+mode,[sys.executable,str(checkout/'tests/web/v666_direct_creation_recovery_ui.py'),str(package/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='root-followup-recovery':
            for mode in ['normal','loss']:
                work.run('packaged-root-followup-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_followup_recovery_ui.py'),str(package/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='root-input-name-recovery':
            for mode in ['normal','loss']:
                work.run('packaged-root-input-name-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_input_name_recovery_ui.py'),str(package/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='root-output-order-recovery':
            for mode in ['normal','loss']:
                work.run('packaged-root-output-order-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_output_order_recovery_ui.py'),str(package/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='export-creation-recovery':
            for mode in ['normal','loss']:
                work.run('packaged-export-creation-'+mode,[sys.executable,str(checkout/'tests/web/v666_export_creation_recovery_ui.py'),str(package/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='export-removal-recovery':
            for mode in ['normal','loss']:
                work.run('packaged-export-removal-'+mode,[sys.executable,str(checkout/'tests/web/v666_export_removal_recovery_ui.py'),str(package/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='root-return-recovery':
            for mode in ['normal','loss']:
                work.run('packaged-root-return-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_return_recovery_ui.py'),str(package/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='export-binding-recovery':
            for mode in ['normal','loss']:
                work.run('packaged-export-binding-'+mode,[sys.executable,str(checkout/'tests/web/v666_export_binding_recovery_ui.py'),str(package/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='export-value-recovery':
            for mode in ['normal','loss']:
                work.run('packaged-export-value-'+mode,[sys.executable,str(checkout/'tests/web/v666_export_value_recovery_ui.py'),str(package/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='entry-recovery':
            for mode in ['normal','loss']:
                work.run('packaged-entry-'+mode,[sys.executable,str(checkout/'tests/web/v666_entry_recovery_ui.py'),str(package/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='route-recovery':
            for mode in ['normal','loss']:
                work.run('packaged-route-'+mode,[sys.executable,str(checkout/'tests/web/v666_route_recovery_ui.py'),str(package/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='name-recovery':
            for mode in ['normal','loss']:
                work.run('packaged-name-'+mode,[sys.executable,str(checkout/'tests/web/v666_name_recovery_ui.py'),str(package/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='source-recovery':
            for mode in ['normal','loss']:
                work.run('packaged-source-'+mode,[sys.executable,str(checkout/'tests/web/v666_source_recovery_ui.py'),str(package/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='description-recovery':
            for target,mode in [('node','normal'),('function','conflict')]:
                work.run('packaged-description-'+target,[sys.executable,str(checkout/'tests/web/v666_description_recovery_ui.py'),str(package/'content'),str(packaged_report),target,mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='guidance-values':
            work.run('packaged-value-ui',[sys.executable,str(checkout/'tests/web/v666_guidance_values_ui.py'),str(package/'content'),str(packaged_report),'normal','--out-root'],cwd=checkout,env=env)
        elif args.suite=='guidance-review':
            work.run('packaged-review-ui',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_ui.py'),str(package/'content'),str(packaged_report),'normal','--out-root','--review-guidance'],cwd=checkout,env=env)

        elif args.suite=='guidance-code-editor':
            work.run('packaged-guidance-ui',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_ui.py'),str(package/'content'),str(packaged_report),'normal','--out-root'],cwd=checkout,env=env)

        elif args.suite=='async-branch-creation':
            work.run('packaged-branch-ui',[sys.executable,str(checkout/'tests/web/v666_async_coupled_first_ui.py'),str(package/'content'),str(packaged_report),'normal','--branch-line','--out-root'],cwd=checkout,env=env)
            work.run('packaged-branch-api',[sys.executable,str(checkout/'tests/web/v666_async_branch_creation_api.py'),str(package/'content'),str(packaged_report),'--out-root','--result-line'],cwd=checkout,env=env)

        elif args.suite=='async-root-io':
            work.run('packaged-root-io-ui',[sys.executable,str(checkout/'tests/web/v666_async_coupled_first_ui.py'),str(package/'content'),str(packaged_report),'unsaved-declaration','--root-io'],cwd=checkout,env=env)
            work.run('packaged-root-io-api',[sys.executable,str(checkout/'tests/web/v666_async_root_io_api.py'),str(package/'content'),str(packaged_report)],cwd=checkout,env=env)

        elif args.suite=='async-coupled':
            work.run('packaged-coupled-ui',[sys.executable,str(checkout/'tests/web/v666_async_coupled_first_ui.py'),str(package/'content'),str(packaged_report),'unsaved-declaration'],cwd=checkout,env=env)
            work.run('packaged-coupled-private',[sys.executable,str(checkout/'tests/web/v666_async_coupled_private_api.py'),str(package/'content'),str(packaged_report)],cwd=checkout,env=env)

        elif args.suite in ['async-private','async-private-returns']:
            work.run('packaged-private-ui',[sys.executable,str(checkout/'tests/web'/('v666_async_private_returns_ui.py' if args.suite=='async-private-returns' else 'v666_async_private_ui.py')),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-async-runtime',[sys.executable,str(checkout/'tests/probes/async_private_runtime.py'),str(package/'content')],cwd=checkout,env=env)

        elif args.suite=='async-information':
            work.run('packaged-information-ui',[sys.executable,str(checkout/'tests/web/v666_async_information_ui.py'),str(package/'content'),str(packaged_report),'normal','view'],cwd=checkout,env=env)
            work.run('packaged-async-runtime',[sys.executable,str(checkout/'tests/probes/async_runtime.py'),str(package/'content')],cwd=checkout,env=env)

        elif args.suite=='async-new-function':
            work.run('packaged-new-function-ui',[sys.executable,str(checkout/'tests/web/v666_async_new_function_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-async-runtime',[sys.executable,str(checkout/'tests/probes/async_runtime.py'),str(package/'content')],cwd=checkout,env=env)

        elif args.suite=='async-creating':
            work.run('packaged-creating-ui',[sys.executable,str(checkout/'tests/web/v666_async_creating_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-async-runtime',[sys.executable,str(checkout/'tests/probes/async_runtime.py'),str(package/'content')],cwd=checkout,env=env)

        elif args.suite=='async-context':
            work.run('packaged-context-ui',[sys.executable,str(checkout/'tests/web/v666_async_context_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-async-runtime',[sys.executable,str(checkout/'tests/probes/async_runtime.py'),str(package/'content')],cwd=checkout,env=env)

        elif args.suite=='async-adapter':
            work.run('packaged-adapter-ui',[sys.executable,str(checkout/'tests/web/v666_async_adapter_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-async-runtime',[sys.executable,str(checkout/'tests/probes/async_runtime.py'),str(package/'content')],cwd=checkout,env=env)

        elif args.suite=='async-property':
            work.run('packaged-async-property',[sys.executable,str(checkout/'tests/web/v666_async_property_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-async-runtime',[sys.executable,str(checkout/'tests/probes/async_runtime.py'),str(package/'content')],cwd=checkout,env=env)

        elif args.suite=='async-function':
            work.run('packaged-function-ui',[sys.executable,str(checkout/'tests/web/v666_async_function_ui.py'),str(package/'content'),str(packaged_report),'normal','--out-root'],cwd=checkout,env=env)
            work.run('packaged-async-set',[sys.executable,str(checkout/'tests/web/v666_async_set_ui.py'),str(package/'content'),str(packaged_report),'normal','--out-root'],cwd=checkout,env=env)
            work.run('packaged-async-runtime',[sys.executable,str(checkout/'tests/probes/async_runtime.py'),str(package/'content')],cwd=checkout,env=env)

        elif args.suite=='async-completion':
            work.run('packaged-completion-ui',[sys.executable,str(checkout/'tests/web/v666_async_completion_ui.py'),str(package/'content'),str(packaged_report),'normal','--out-root'],cwd=checkout,env=env)
            work.run('packaged-async-set',[sys.executable,str(checkout/'tests/web/v666_async_set_ui.py'),str(package/'content'),str(packaged_report),'normal','--out-root'],cwd=checkout,env=env)
            work.run('packaged-async-runtime',[sys.executable,str(checkout/'tests/probes/async_runtime.py'),str(package/'content')],cwd=checkout,env=env)

        elif args.suite=='async-transition':
            work.run('packaged-async-ui',[sys.executable,str(checkout/'tests/web/v666_async_transition_ui.py'),str(package/'content'),str(packaged_report),'normal','--out-root'],cwd=checkout,env=env)
            work.run('packaged-async-runtime',[sys.executable,str(checkout/'tests/probes/async_runtime.py'),str(package/'content')],cwd=checkout,env=env)

        elif args.suite in ['root-execution-import-observations','async-runtime']:
            work.run('packaged-imports',[sys.executable,str(checkout/'tests/web/v666_root_execution_ui.py'),str(package/'content'),str(packaged_report),'normal','--out-root','--imports-root'],cwd=checkout,env=env)
        elif args.suite=='root-execution-owned-updates':
            work.run('packaged-owned-update',[sys.executable,str(checkout/'tests/web/v666_root_execution_owned_update_ui.py'),str(package/'content'),str(packaged_report),'normal','--out-root'],cwd=checkout,env=env)

        elif args.suite=='root-execution-wrappers':
            work.run('packaged-public-wrapper',[sys.executable,str(checkout/'tests/web/v666_root_execution_wrapper_ui.py'),str(package/'content'),str(packaged_report),'normal','--out-root'],cwd=checkout,env=env)
        elif args.suite in ['root-execution-caller','root-execution-forwarding','root-execution-observers']:
            case = 'observers' if args.suite=='root-execution-observers' else 'forwarding' if args.suite=='root-execution-forwarding' else 'caller'
            work.run('packaged-'+case,[sys.executable,str(checkout/'tests/web/v666_root_execution_ui.py'),str(package/'content'),str(packaged_report),'normal','--out-root','--observer-root' if case=='observers' else '--forward-caller' if case=='forwarding' else '--branch-caller'],cwd=checkout,env=env)
        elif args.suite=='root-execution-native':
            work.run('packaged-native',[sys.executable,str(checkout/'tests/web/v666_root_execution_ui.py'),str(package/'content'),str(packaged_report),'normal','--out-root','--native-root'],cwd=checkout,env=env)
        elif args.suite=='root-execution-nested':
            work.run('packaged-nested',[sys.executable,str(checkout/'tests/web/v666_root_execution_ui.py'),str(package/'content'),str(packaged_report),'normal','--out-root','--nested-root'],cwd=checkout,env=env)
        elif args.suite=='root-execution-providers':
            work.run('packaged-providers',[sys.executable,str(checkout/'tests/web/v666_root_execution_ui.py'),str(package/'content'),str(packaged_report),'normal','--multi-root','--providers-root'],cwd=checkout,env=env)
        elif args.suite=='public-return-data':
            work.run('packaged-return-data',[sys.executable,str(checkout/'tests/web/v666_root_execution_copy_creating_ui.py'),str(package/'content'),str(packaged_report),'normal','--nonvoid-root','--registered-creating'],cwd=checkout,env=env)
        elif args.suite=='root-execution-registered-creating':
            work.run('packaged-registered-creation',[sys.executable,str(checkout/'tests/web/v666_root_execution_copy_creating_ui.py'),str(package/'content'),str(packaged_report),'normal','--out-root','--registered-creating'],cwd=checkout,env=env)
        elif args.suite=='root-execution-registered-copy':
            work.run('packaged-registered-copy-return',[sys.executable,str(checkout/'tests/web/v666_root_execution_registered_ui.py'),str(package/'content'),str(packaged_report),'normal','--out-root','--registered-copy'],cwd=checkout,env=env)
        elif args.suite=='root-execution-registered':
            work.run('packaged-registered-return',[sys.executable,str(checkout/'tests/web/v666_root_execution_registered_ui.py'),str(package/'content'),str(packaged_report),'normal','--out-root'],cwd=checkout,env=env)
        elif args.suite=='root-execution-override':
            work.run('packaged-public-override',[sys.executable,str(checkout/'tests/web/v666_root_execution_override_ui.py'),str(package/'content'),str(packaged_report),'normal','--out-root','--external-parent'],cwd=checkout,env=env)
        elif args.suite=='root-execution-copy-creating':
            work.run('packaged-public-copy-creating',[sys.executable,str(checkout/'tests/web/v666_root_execution_copy_creating_ui.py'),str(package/'content'),str(packaged_report),'normal','--out-root'],cwd=checkout,env=env)
        elif args.suite=='root-execution-copy':
            work.run('packaged-public-copy',[sys.executable,str(checkout/'tests/web/v666_root_execution_copy_ui.py'),str(package/'content'),str(packaged_report),'normal','--out-root'],cwd=checkout,env=env)
        elif args.suite in ['root-execution','root-execution-out','root-execution-closure','root-execution-data-void','root-execution-compound-owned','root-execution-provider-import','root-execution-nonvoid']:
            work.run('packaged-root-execution',[sys.executable,str(checkout/'tests/web/v666_root_execution_ui.py'),str(package/'content'),str(packaged_report),'normal',*(['--nonvoid-root'] if args.suite=='root-execution-nonvoid' else ['--provider-import'] if args.suite=='root-execution-provider-import' else ['--compound-root'] if args.suite=='root-execution-compound-owned' else ['--multi-root'] if args.suite=='root-execution-closure' else ['--data-root'] if args.suite=='root-execution-data-void' else ['--out-root'] if args.suite=='root-execution-out' else [])],cwd=checkout,env=env)
        elif args.suite in ['node-internal-override','node-internal-external-override']:
            work.run('packaged-direct-node',[sys.executable,str(checkout/'tests/web/v666_node_internal_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-owned-override',[sys.executable,str(checkout/'tests/web'/('v666_node_internal_external_override_ui.py' if args.suite=='node-internal-external-override' else 'v666_node_internal_override_ui.py')),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        elif args.suite in ['node-internal-copy-creating','node-internal-copy-frames']:
            work.run('packaged-direct-node',[sys.executable,str(checkout/'tests/web/v666_node_internal_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-creating-copy',[sys.executable,str(checkout/'tests/web/v666_node_internal_copy_creating_ui.py'),str(package/'content'),str(packaged_report),'normal',*(['--branch','--nested'] if args.suite=='node-internal-copy-frames' else [])],cwd=checkout,env=env)

        elif args.suite=='node-internal-copy-context':
            work.run('packaged-direct-context',[sys.executable,str(checkout/'tests/web/v666_node_internal_context_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-copy-context',[sys.executable,str(checkout/'tests/web/v666_node_internal_context_ui.py'),str(package/'content'),str(packaged_report),*['normal','--copy','--raw-copy']],cwd=checkout,env=env)
        elif args.suite=='node-internal-copy-branches':
            work.run('packaged-direct-branch',[sys.executable,str(checkout/'tests/web/v666_node_internal_branch_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-copy-branch',[sys.executable,str(checkout/'tests/web/v666_node_internal_branch_ui.py'),str(package/'content'),str(packaged_report),'normal','--copy',*([])],cwd=checkout,env=env)
        elif args.suite=='node-internal-copy-storage':
            work.run('packaged-node-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-copy-storage',[sys.executable,str(checkout/'tests/web/v666_node_internal_copy_ui.py'),str(package/'content'),str(packaged_report),'normal','--storage-copy'],cwd=checkout,env=env)

        elif args.suite in ['node-internal-copy','node-internal-copy-nested']:
            work.run('packaged-node-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-copy-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_copy_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            if args.suite=='node-internal-copy-nested':
                work.run('packaged-nested-copy',[sys.executable,str(checkout/'tests/web/v666_node_internal_copy_ui.py'),str(package/'content'),str(packaged_report),'normal','--depth=2'],cwd=checkout,env=env)

        elif args.suite=='node-branch-exits':
            work.run('packaged-node-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-branch-exits',[sys.executable,str(checkout/'tests/web/v666_node_branch_exit_ui.py'),str(package/'content'),str(packaged_report),'draft'],cwd=checkout,env=env)

        elif args.suite=='node-internal-branches':
            work.run('packaged-node-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-branch-node-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_branch_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        elif args.suite=='node-internal-context':
            work.run('packaged-node-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('packaged-context-node-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_context_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        elif args.suite in ['owned-conversion','action-icons','declaration-icons','pin-icons','enum-definitions','enum-values','enum-retirement','worker-badges','node-internal']:
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
        if args.suite in ['action-icons','declaration-icons','pin-icons','enum-definitions','enum-values','enum-retirement','worker-badges','node-internal']:
            work.run('packaged-action-icons',[sys.executable,str(checkout/'tests/web/v666_action_icon_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        if args.suite in ['declaration-icons','pin-icons','enum-definitions','enum-values','enum-retirement','worker-badges','node-internal']:
            work.run('packaged-declaration-icons',[sys.executable,str(checkout/'tests/web/v666_declaration_icon_ui.py'),str(package/'content'),str(packaged_report),'normal','module'],cwd=checkout,env=env)
        if args.suite in ['pin-icons','enum-definitions','enum-values','enum-retirement','worker-badges','node-internal']:
            work.run('packaged-module-pins',[sys.executable,str(checkout/'tests/web/v666_module_pin_ui.py'),str(package/'content'),str(packaged_report),'multi','view'],cwd=checkout,env=env)
            work.run('packaged-set-output-icons',[sys.executable,str(checkout/'tests/web/v666_set_output_icon_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        if args.suite in ['enum-definitions','enum-values','enum-retirement','worker-badges','node-internal']:
            work.run('packaged-information-enum',[sys.executable,str(checkout/'tests/web/v666_information_enum_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        for name in ['Confectory.Core.dll','Confectory.ElementAuthoring.dll']:
            matches = [p for p in files(package).values() if p.name==name]
            origin = checkout/('src/Confectory.Core/bin/Release/net10.0/'+name if name=='Confectory.Core.dll' else 'targets/element-authoring/bin/Release/net10.0/'+name)
            if not matches or any(sha(p)!=sha(origin) for p in matches):
                raise RuntimeError('Packaged assembly differs: '+name)
        if args.suite in ['enum-values','enum-retirement','worker-badges','node-internal']:
            work.run('packaged-information-enum-values',[sys.executable,str(checkout/'tests/web/v666_information_enum_values_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        if args.suite in ['enum-retirement','worker-badges','node-internal']:
            work.run('packaged-information-enum-retirement',[sys.executable,str(checkout/'tests/web/v666_information_enum_retirement_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        if args.suite in ['worker-badges','node-internal']:
            work.run('packaged-worker-badges',[sys.executable,str(checkout/'tests/web/v666_worker_badges_ui.py'),str(package/'content'),str(packaged_report)],cwd=checkout,env=env)
        if args.suite=='node-internal':
            work.run('packaged-node-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_ui.py'),str(package/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
        if args.suite=='async-runtime':
            work.run('packaged-async-runtime',[sys.executable,str(checkout/'tests/probes/async_runtime.py'),str(package/'content')],cwd=checkout,env=env)
        candidate = work.root/'package.zip'
        entry = store.prepare(package,candidate,commit,work.record.with_suffix('.zip'),inputs['identity'])
        restored = work.root/'restored'; restored.mkdir()
        verify_archive(candidate, entry['files'], restored)
        # Execute the restored archive's package check, engine startup and UI,
        # not just its ZIP CRC or a manifest comparison.
        work.run('restored-probe',[sys.executable,str(checkout/'tests/probes/desktop_package.py'),str(checkout),str(restored)],cwd=checkout,env=env)
        atomic_json(packaged_report, {'run':[dotnet,str(restored/'content/runtime/Confectory.App.dll')]})
        if args.suite=='async-runtime':
            work.run('restored-async-runtime',[sys.executable,str(checkout/'tests/probes/async_runtime.py'),str(restored/'content')],cwd=checkout,env=env)
        if args.suite=='node-internal-nested':
            work.run('restored-node-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_ui.py'),str(restored/'content'),str(packaged_report),'storage'],cwd=checkout,env=env)
            work.run('restored-nested-node-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_nested_ui.py'),str(restored/'content'),str(packaged_report),'loss','--depth=2'],cwd=checkout,env=env)
        elif args.suite=='node-internal-storage':
            work.run('restored-node-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_ui.py'),str(restored/'content'),str(packaged_report),'storage'],cwd=checkout,env=env)
            work.run('restored-storage-node-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_storage_ui.py'),str(restored/'content'),str(packaged_report),'loss','--private','--local'],cwd=checkout,env=env)
        elif args.suite=='run-bounds':
            work.run('restored-run-bounds',[sys.executable,str(checkout/'tests/web/v666_run_bounds_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-grid-regression',[sys.executable,str(checkout/'tests/web/v666_run_grid_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
        elif args.suite=='run-rate':
            work.run('restored-run-rate',[sys.executable,str(checkout/'tests/web/v666_run_rate_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-grid-regression',[sys.executable,str(checkout/'tests/web/v666_run_grid_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)

        elif args.suite=='startup-transport':
            work.run('restored-startup-transport',[sys.executable,str(checkout/'tests/web/v666_startup_transport_ui.py'),str(restored/'content'),str(packaged_report),'cold'],cwd=checkout,env=env)
            work.run('restored-office-arrangement',[sys.executable,str(checkout/'tests/web/v666_office_arrangement_ui.py'),str(restored/'content'),str(packaged_report),'late'],cwd=checkout,env=env)
        elif args.suite=='resource-description':
            for name in ['description','content','pdf','office']:
                work.run('restored-resource-'+name,[sys.executable,str(checkout/('tests/web/v666_resource_'+name+'_ui.py')),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)

        elif args.suite=='resource-pdf':
            for name in ['pdf','office','images','content']:
                work.run('restored-resource-'+name,[sys.executable,str(checkout/('tests/web/v666_resource_'+name+'_ui.py')),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)

        elif args.suite=='resource-office':
            work.run('restored-resource-office',[sys.executable,str(checkout/'tests/web/v666_resource_office_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-resource-images',[sys.executable,str(checkout/'tests/web/v666_resource_images_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-resource-content',[sys.executable,str(checkout/'tests/web/v666_resource_content_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
        elif args.suite=='resource-destination':
            work.run('restored-resource-destination',[sys.executable,str(checkout/'tests/web/v666_resource_destination_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-resource-batch',[sys.executable,str(checkout/'tests/web/v666_resource_batch_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-resource-images',[sys.executable,str(checkout/'tests/web/v666_resource_images_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-resource-content',[sys.executable,str(checkout/'tests/web/v666_resource_content_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
        elif args.suite=='resource-batch':
            work.run('restored-resource-batch',[sys.executable,str(checkout/'tests/web/v666_resource_batch_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-resource-images',[sys.executable,str(checkout/'tests/web/v666_resource_images_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-resource-content',[sys.executable,str(checkout/'tests/web/v666_resource_content_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
        elif args.suite=='resource-images':
            work.run('restored-resource-images',[sys.executable,str(checkout/'tests/web/v666_resource_images_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-resource-content',[sys.executable,str(checkout/'tests/web/v666_resource_content_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
        elif args.suite=='resource-content':
            work.run('restored-resource-content',[sys.executable,str(checkout/'tests/web/v666_resource_content_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-resource-multi-deletion',[sys.executable,str(checkout/'tests/web/v666_resource_multi_deletion_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
        elif args.suite=='resource-multi-deletion':
            work.run('restored-resource-multi-deletion',[sys.executable,str(checkout/'tests/web/v666_resource_multi_deletion_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-resource-folder-deletion',[sys.executable,str(checkout/'tests/web/v666_resource_folder_deletion_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-resource-file-deletion',[sys.executable,str(checkout/'tests/web/v666_resource_file_deletion_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-resource-file-names',[sys.executable,str(checkout/'tests/web/v666_resource_file_names_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-resource-preview',[sys.executable,str(checkout/'tests/web/v666_resource_preview_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
        elif args.suite=='resource-folder-deletion':
            work.run('restored-resource-folder-deletion',[sys.executable,str(checkout/'tests/web/v666_resource_folder_deletion_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-resource-file-deletion',[sys.executable,str(checkout/'tests/web/v666_resource_file_deletion_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-resource-file-names',[sys.executable,str(checkout/'tests/web/v666_resource_file_names_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-resource-preview',[sys.executable,str(checkout/'tests/web/v666_resource_preview_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
        elif args.suite=='resource-file-deletion':
            work.run('restored-resource-file-deletion',[sys.executable,str(checkout/'tests/web/v666_resource_file_deletion_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-resource-file-names',[sys.executable,str(checkout/'tests/web/v666_resource_file_names_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-resource-preview',[sys.executable,str(checkout/'tests/web/v666_resource_preview_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
        elif args.suite=='resource-file-names':
            work.run('restored-resource-file-names',[sys.executable,str(checkout/'tests/web/v666_resource_file_names_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-resource-folder-names',[sys.executable,str(checkout/'tests/web/v666_resource_folder_names_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-resource-preview',[sys.executable,str(checkout/'tests/web/v666_resource_preview_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
        elif args.suite=='resource-folder-names':
            work.run('restored-resource-folder-names',[sys.executable,str(checkout/'tests/web/v666_resource_folder_names_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-resource-layout',[sys.executable,str(checkout/'tests/web/v666_resource_layout_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-resource-preview',[sys.executable,str(checkout/'tests/web/v666_resource_preview_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
        elif args.suite=='resource-layout':
            work.run('restored-resource-layout',[sys.executable,str(checkout/'tests/web/v666_resource_layout_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-resource-preview',[sys.executable,str(checkout/'tests/web/v666_resource_preview_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
        elif args.suite=='resource-preview':
            work.run('restored-resource-preview',[sys.executable,str(checkout/'tests/web/v666_resource_preview_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-resource-import',[sys.executable,str(checkout/'tests/web/v666_resources_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
        elif args.suite=='resource-import':
            work.run('restored-resource-ui',[sys.executable,str(checkout/'tests/web/v666_resources_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-body-regression',[sys.executable,str(checkout/'tests/web/v666_finder_bodies_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
        elif args.suite=='office-finder':
            work.run('restored-office-finder',[sys.executable,str(checkout/'tests/web/v666_office_finder_ui.py'),str(restored/'content'),str(packaged_report),'cold'],cwd=checkout,env=env)
            work.run('restored-finder-load',[sys.executable,str(checkout/'tests/web/v666_workspace_finder_ui.py'),str(restored/'content'),str(packaged_report),'load'],cwd=checkout,env=env)

        elif args.suite=='office-io-poll':
            work.run('restored-io-cold',[sys.executable,str(checkout/'tests/web/v666_office_workers_ui.py'),str(restored/'content'),str(packaged_report),'phase-cold'],cwd=checkout,env=env)
            work.run('restored-arrangement',[sys.executable,str(checkout/'tests/web/v666_office_arrangement_ui.py'),str(restored/'content'),str(packaged_report),'late'],cwd=checkout,env=env)

        elif args.suite=='office-active-io':
            work.run('restored-office-active',[sys.executable,str(checkout/'tests/web/v666_office_workers_ui.py'),str(restored/'content'),str(packaged_report),'phase-cold'],cwd=checkout,env=env)

        elif args.suite=='office-io':
            work.run('restored-office-io',[sys.executable,str(checkout/'tests/web/v666_office_workers_ui.py'),str(restored/'content'),str(packaged_report),'io-cold'],cwd=checkout,env=env)
            work.run('restored-office-unavailable-regression',[sys.executable,str(checkout/'tests/web/v666_office_view_ui.py'),str(restored/'content'),str(packaged_report),'unavailable'],cwd=checkout,env=env)

        elif args.suite=='office-arrangement':
            work.run('restored-office-arrangement',[sys.executable,str(checkout/'tests/web/v666_office_arrangement_ui.py'),str(restored/'content'),str(packaged_report),'late'],cwd=checkout,env=env)
            work.run('restored-office-unavailable-regression',[sys.executable,str(checkout/'tests/web/v666_office_view_ui.py'),str(restored/'content'),str(packaged_report),'unavailable'],cwd=checkout,env=env)

        elif args.suite=='office-workers':
            work.run('restored-office-workers-cold',[sys.executable,str(checkout/'tests/web/v666_office_workers_ui.py'),str(restored/'content'),str(packaged_report),'cold'],cwd=checkout,env=env)
            work.run('restored-office-unavailable-regression',[sys.executable,str(checkout/'tests/web/v666_office_view_ui.py'),str(restored/'content'),str(packaged_report),'unavailable'],cwd=checkout,env=env)

        elif args.suite=='office-view':
            for mode in ['cold','late','unavailable','tampered']:
                work.run('restored-office-'+mode,[sys.executable,str(checkout/'tests/web/v666_office_view_ui.py'),str(restored/'content'),str(packaged_report),mode],cwd=checkout,env=env)

        elif args.suite=='native-intent-late':
            for mode in ['failure','cold']:
                work.run('restored-native-intent-'+mode,[sys.executable,str(checkout/'tests/web/v666_native_intent_late_ui.py'),str(restored/'content'),str(packaged_report),mode],cwd=checkout,env=env)

        elif args.suite=='native-read-close':
            work.run('restored-native-read-close-ui',[sys.executable,str(checkout/'tests/web/v666_native_read_close_ui.py'),str(restored/'content'),str(packaged_report),'failure'],cwd=checkout,env=env)
            work.run('restored-native-zoom-regression',[sys.executable,str(checkout/'tests/web/v666_native_zoom_lifetime_ui.py'),str(restored/'content'),str(packaged_report),'exhausted'],cwd=checkout,env=env)

        elif args.suite=='native-zoom-lifetime':
            work.run('restored-native-zoom-engine',[sys.executable,str(checkout/'tests/web/v666_native_zoom_lifetime_ui.py'),str(restored/'content'),str(packaged_report),'exhausted'],cwd=checkout,env=env)
            work.run('restored-workspace-zoom-regression',[sys.executable,str(checkout/'tests/web/v666_zoom_lifetime_ui.py'),str(restored/'content'),str(packaged_report),'scope'],cwd=checkout,env=env)

        elif args.suite=='zoom-lifetime':
            work.run('restored-zoom-lifetime-ui',[sys.executable,str(checkout/'tests/web/v666_zoom_lifetime_ui.py'),str(restored/'content'),str(packaged_report),'scope'],cwd=checkout,env=env)
            work.run('restored-blueprint-zoom-regression',[sys.executable,str(checkout/'tests/web/v666_canvas_zoom_ui.py'),str(restored/'content'),str(packaged_report)],cwd=checkout,env=env)

        elif args.suite=='finder-modules':
            work.run('restored-module-ui',[sys.executable,str(checkout/'tests/web/v666_finder_modules_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-module-content-lifecycle',[sys.executable,str(checkout/'tests/web/v666_finder_content_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)

        elif args.suite=='declaration-reload':
            for mode,flags in [('late',['view']),('scope',[])]:
                work.run('restored-declaration-reload-'+mode,[sys.executable,str(checkout/'tests/web/v666_declaration_reload_ui.py'),str(restored/'content'),str(packaged_report),mode,*flags],cwd=checkout,env=env)

        elif args.suite in ['finder-content','finder-definitions','finder-bodies','finder-defaults']:
            for mode in ['basic','lifecycle']:
                work.run('restored-finder-content-'+mode,[sys.executable,str(checkout/'tests/web/v666_finder_content_ui.py'),str(restored/'content'),str(packaged_report),mode],cwd=checkout,env=env)

            if args.suite in ['finder-definitions','finder-bodies','finder-defaults']:
                work.run('restored-finder-definitions',[sys.executable,str(checkout/'tests/web/v666_finder_definitions_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)

            if args.suite in ['finder-bodies','finder-defaults']:
                for mode in ['lifecycle','guards']:
                    work.run('restored-finder-bodies-'+mode,[sys.executable,str(checkout/'tests/web/v666_finder_bodies_ui.py'),str(restored/'content'),str(packaged_report),mode],cwd=checkout,env=env)
            if args.suite=='finder-defaults':
                work.run('restored-finder-defaults-lifecycle',[sys.executable,str(checkout/'tests/web/v666_finder_defaults_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)

        elif args.suite=='workspace-finder':
            for mode in ['basic','load']:
                work.run('restored-workspace-finder-'+mode,[sys.executable,str(checkout/'tests/web/v666_workspace_finder_ui.py'),str(restored/'content'),str(packaged_report),mode],cwd=checkout,env=env)

        elif args.suite=='run-grid':
            work.run('restored-run-grid',[sys.executable,str(checkout/'tests/web/v666_run_grid_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
        elif args.suite=='run-wide':
            work.run('restored-run-wide',[sys.executable,str(checkout/'tests/web/v666_run_wide_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
        elif args.suite=='run-auto':
            work.run('restored-run-auto',[sys.executable,str(checkout/'tests/web/v666_run_auto_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
        elif args.suite=='run-presets':
            work.run('restored-run-presets',[sys.executable,str(checkout/'tests/web/v666_run_presets_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)

        elif args.suite=='run-audio':
            work.run('restored-run-audio',[sys.executable,str(checkout/'tests/web/v666_run_audio_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)

        elif args.suite in ['run-resolution','run-surface']:
            if args.suite=='run-resolution':work.run('restored-run-resolution',[sys.executable,str(checkout/'tests/web/v666_run_resolution_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-run-surface',[sys.executable,str(checkout/'tests/web/v666_run_surface_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-run-developer',[sys.executable,str(checkout/'tests/web/v666_run_developer_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
        elif args.suite=='run-developer':
            work.run('restored-run-developer',[sys.executable,str(checkout/'tests/web/v666_run_developer_ui.py'),str(restored/'content'),str(packaged_report),'lifecycle'],cwd=checkout,env=env)
            work.run('restored-run-menu-regression',[sys.executable,str(checkout/'tests/web/v666_run_fullscreen_ui.py'),str(restored/'content'),str(packaged_report),'menu'],cwd=checkout,env=env)

        elif args.suite=='run-fullscreen':
            for mode in ['lifecycle','race']:
                work.run('restored-run-fullscreen-'+mode,[sys.executable,str(checkout/'tests/web/v666_run_fullscreen_ui.py'),str(restored/'content'),str(packaged_report),mode],cwd=checkout,env=env)

        elif args.suite=='route-group-recovery':
            for mode in ['storage-new', 'late']:
                work.run('restored-route-group-'+mode,[sys.executable,str(checkout/'tests/web/v666_route_group_recovery_ui.py'),str(restored/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='root-void-name-recovery':
            for mode in ['storage-new', 'late']:
                work.run('restored-root-void-name-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_void_name_recovery_ui.py'),str(restored/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='node-names-recovery':
            for mode in ['storage-new', 'late']:
                work.run('restored-node-names-'+mode,[sys.executable,str(checkout/'tests/web/v666_node_names_recovery_ui.py'),str(restored/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='root-return-position-recovery':
            for mode in ['storage-new', 'late']:
                work.run('restored-root-return-position-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_return_position_recovery_ui.py'),str(restored/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='node-text-recovery':
            for mode in ['storage-new', 'late']:
                work.run('restored-node-text-'+mode,[sys.executable,str(checkout/'tests/web/v666_node_text_recovery_ui.py'),str(restored/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='root-value-rename-recovery':
            for mode in ['storage-new', 'late']:
                work.run('restored-root-value-rename-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_value_rename_recovery_ui.py'),str(restored/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='text-pair-recovery':
            for mode in ['storage-new', 'late']:
                work.run('restored-text-pair-'+mode,[sys.executable,str(checkout/'tests/web/v666_text_pair_recovery_ui.py'),str(restored/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='direct-creation-recovery':
            for mode in ['storage-new', 'late']:
                work.run('restored-direct-creation-'+mode,[sys.executable,str(checkout/'tests/web/v666_direct_creation_recovery_ui.py'),str(restored/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='root-followup-recovery':
            for mode in ['storage-new','late']:
                work.run('restored-root-followup-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_followup_recovery_ui.py'),str(restored/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='root-input-name-recovery':
            for mode in ['storage-new','late']:
                work.run('restored-root-input-name-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_input_name_recovery_ui.py'),str(restored/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='root-output-order-recovery':
            for mode in ['storage-new','late']:
                work.run('restored-root-output-order-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_output_order_recovery_ui.py'),str(restored/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='export-creation-recovery':
            for mode in ['storage-new','late']:
                work.run('restored-export-creation-'+mode,[sys.executable,str(checkout/'tests/web/v666_export_creation_recovery_ui.py'),str(restored/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='export-removal-recovery':
            for mode in ['storage','late']:
                work.run('restored-export-removal-'+mode,[sys.executable,str(checkout/'tests/web/v666_export_removal_recovery_ui.py'),str(restored/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='root-return-recovery':
            for mode in ['storage-new','late']:
                work.run('restored-root-return-'+mode,[sys.executable,str(checkout/'tests/web/v666_root_return_recovery_ui.py'),str(restored/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='export-binding-recovery':
            for mode in ['storage-new','late']:
                work.run('restored-export-binding-'+mode,[sys.executable,str(checkout/'tests/web/v666_export_binding_recovery_ui.py'),str(restored/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='export-value-recovery':
            for mode in ['storage-new','late']:
                work.run('restored-export-value-'+mode,[sys.executable,str(checkout/'tests/web/v666_export_value_recovery_ui.py'),str(restored/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='entry-recovery':
            for mode in ['storage-new','late']:
                work.run('restored-entry-'+mode,[sys.executable,str(checkout/'tests/web/v666_entry_recovery_ui.py'),str(restored/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='route-recovery':
            for mode in ['storage-new','late']:
                work.run('restored-route-'+mode,[sys.executable,str(checkout/'tests/web/v666_route_recovery_ui.py'),str(restored/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='name-recovery':
            for mode in ['storage-new','late']:
                work.run('restored-name-'+mode,[sys.executable,str(checkout/'tests/web/v666_name_recovery_ui.py'),str(restored/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='source-recovery':
            for mode in ['storage-new','late']:
                work.run('restored-source-'+mode,[sys.executable,str(checkout/'tests/web/v666_source_recovery_ui.py'),str(restored/'content'),str(packaged_report),mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='description-recovery':
            for target,mode in [('node','loss'),('function','late')]:
                work.run('restored-description-'+target,[sys.executable,str(checkout/'tests/web/v666_description_recovery_ui.py'),str(restored/'content'),str(packaged_report),target,mode,'--out-root'],cwd=checkout,env=env)
        elif args.suite=='guidance-values':
            work.run('restored-value-ui',[sys.executable,str(checkout/'tests/web/v666_guidance_values_ui.py'),str(restored/'content'),str(packaged_report),'storage','--data-root'],cwd=checkout,env=env)
            work.run('restored-code-guidance-regression',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_ui.py'),str(restored/'content'),str(packaged_report),'normal','--out-root'],cwd=checkout,env=env)
        elif args.suite=='guidance-review':
            work.run('restored-review-ui',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_ui.py'),str(restored/'content'),str(packaged_report),'storage','--out-root','--review-guidance'],cwd=checkout,env=env)
            work.run('restored-review-task-late',[sys.executable,str(checkout/'tests/web/v666_async_coupled_first_ui.py'),str(restored/'content'),str(packaged_report),'late','--branch-line','--out-root'],cwd=checkout,env=env)

        elif args.suite=='guidance-code-editor':
            work.run('restored-guidance-ui',[sys.executable,str(checkout/'tests/web/v666_guidance_code_editor_ui.py'),str(restored/'content'),str(packaged_report),'storage','--out-root'],cwd=checkout,env=env)
            work.run('restored-guidance-task-late',[sys.executable,str(checkout/'tests/web/v666_async_coupled_first_ui.py'),str(restored/'content'),str(packaged_report),'late','--branch-line','--out-root'],cwd=checkout,env=env)

        elif args.suite=='async-branch-creation':
            work.run('restored-branch-late',[sys.executable,str(checkout/'tests/web/v666_async_coupled_first_ui.py'),str(restored/'content'),str(packaged_report),'late','--branch-line','--out-root'],cwd=checkout,env=env)
            work.run('restored-branch-storage',[sys.executable,str(checkout/'tests/web/v666_async_coupled_first_ui.py'),str(restored/'content'),str(packaged_report),'storage','--branch-line','--out-root','--result-line'],cwd=checkout,env=env)
            work.run('restored-branch-api',[sys.executable,str(checkout/'tests/web/v666_async_branch_creation_api.py'),str(restored/'content'),str(packaged_report),'--out-root'],cwd=checkout,env=env)

        elif args.suite=='async-root-io':
            work.run('restored-root-io-late',[sys.executable,str(checkout/'tests/web/v666_async_coupled_first_ui.py'),str(restored/'content'),str(packaged_report),'create-late','--root-io'],cwd=checkout,env=env)
            work.run('restored-root-io-storage',[sys.executable,str(checkout/'tests/web/v666_async_coupled_first_ui.py'),str(restored/'content'),str(packaged_report),'storage','--root-io'],cwd=checkout,env=env)
            work.run('restored-root-io-api',[sys.executable,str(checkout/'tests/web/v666_async_root_io_api.py'),str(restored/'content'),str(packaged_report)],cwd=checkout,env=env)

        elif args.suite=='async-coupled':
            work.run('restored-coupled-late',[sys.executable,str(checkout/'tests/web/v666_async_coupled_first_ui.py'),str(restored/'content'),str(packaged_report),'create-late'],cwd=checkout,env=env)
            work.run('restored-coupled-storage',[sys.executable,str(checkout/'tests/web/v666_async_coupled_first_ui.py'),str(restored/'content'),str(packaged_report),'storage'],cwd=checkout,env=env)
            work.run('restored-coupled-new-node',[sys.executable,str(checkout/'tests/web/v666_async_coupled_node_api.py'),str(restored/'content'),str(packaged_report)],cwd=checkout,env=env)

        elif args.suite in ['async-private','async-private-returns']:
            work.run('restored-private-ui',[sys.executable,str(checkout/'tests/web'/('v666_async_private_returns_ui.py' if args.suite=='async-private-returns' else 'v666_async_private_ui.py')),str(restored/'content'),str(packaged_report),'late'],cwd=checkout,env=env)
            work.run('restored-private-storage',[sys.executable,str(checkout/'tests/web'/('v666_async_private_returns_ui.py' if args.suite=='async-private-returns' else 'v666_async_private_ui.py')),str(restored/'content'),str(packaged_report),'storage'],cwd=checkout,env=env)
            work.run('restored-async-runtime',[sys.executable,str(checkout/'tests/probes/async_private_runtime.py'),str(restored/'content')],cwd=checkout,env=env)

        elif args.suite=='async-information':
            work.run('restored-information-ui',[sys.executable,str(checkout/'tests/web/v666_async_information_ui.py'),str(restored/'content'),str(packaged_report),'late'],cwd=checkout,env=env)
            work.run('restored-information-storage',[sys.executable,str(checkout/'tests/web/v666_async_information_ui.py'),str(restored/'content'),str(packaged_report),'storage'],cwd=checkout,env=env)
            work.run('restored-async-runtime',[sys.executable,str(checkout/'tests/probes/async_runtime.py'),str(restored/'content')],cwd=checkout,env=env)

        elif args.suite=='async-new-function':
            work.run('restored-new-function-ui',[sys.executable,str(checkout/'tests/web/v666_async_new_function_ui.py'),str(restored/'content'),str(packaged_report),'late'],cwd=checkout,env=env)
            work.run('restored-new-function-storage',[sys.executable,str(checkout/'tests/web/v666_async_new_function_ui.py'),str(restored/'content'),str(packaged_report),'storage'],cwd=checkout,env=env)
            work.run('restored-async-runtime',[sys.executable,str(checkout/'tests/probes/async_runtime.py'),str(restored/'content')],cwd=checkout,env=env)

        elif args.suite=='async-creating':
            work.run('restored-creating-ui',[sys.executable,str(checkout/'tests/web/v666_async_creating_ui.py'),str(restored/'content'),str(packaged_report),'late'],cwd=checkout,env=env)
            work.run('restored-creating-storage',[sys.executable,str(checkout/'tests/web/v666_async_creating_ui.py'),str(restored/'content'),str(packaged_report),'storage'],cwd=checkout,env=env)
            work.run('restored-async-runtime',[sys.executable,str(checkout/'tests/probes/async_runtime.py'),str(restored/'content')],cwd=checkout,env=env)

        elif args.suite=='async-context':
            work.run('restored-context-ui',[sys.executable,str(checkout/'tests/web/v666_async_context_ui.py'),str(restored/'content'),str(packaged_report),'late'],cwd=checkout,env=env)
            work.run('restored-context-storage',[sys.executable,str(checkout/'tests/web/v666_async_context_ui.py'),str(restored/'content'),str(packaged_report),'storage'],cwd=checkout,env=env)
            work.run('restored-async-runtime',[sys.executable,str(checkout/'tests/probes/async_runtime.py'),str(restored/'content')],cwd=checkout,env=env)

        elif args.suite=='async-adapter':
            work.run('restored-adapter-ui',[sys.executable,str(checkout/'tests/web/v666_async_adapter_ui.py'),str(restored/'content'),str(packaged_report),'late'],cwd=checkout,env=env)
            work.run('restored-adapter-storage',[sys.executable,str(checkout/'tests/web/v666_async_adapter_ui.py'),str(restored/'content'),str(packaged_report),'storage'],cwd=checkout,env=env)
            work.run('restored-async-runtime',[sys.executable,str(checkout/'tests/probes/async_runtime.py'),str(restored/'content')],cwd=checkout,env=env)

        elif args.suite=='async-property':
            work.run('restored-async-property',[sys.executable,str(checkout/'tests/web/v666_async_property_ui.py'),str(restored/'content'),str(packaged_report),'late'],cwd=checkout,env=env)
            work.run('restored-async-property-storage',[sys.executable,str(checkout/'tests/web/v666_async_property_ui.py'),str(restored/'content'),str(packaged_report),'storage'],cwd=checkout,env=env)
            work.run('restored-async-runtime',[sys.executable,str(checkout/'tests/probes/async_runtime.py'),str(restored/'content')],cwd=checkout,env=env)

        elif args.suite=='async-function':
            work.run('restored-function-ui',[sys.executable,str(checkout/'tests/web/v666_async_function_ui.py'),str(restored/'content'),str(packaged_report),'late','--out-root'],cwd=checkout,env=env)
            work.run('restored-function-storage',[sys.executable,str(checkout/'tests/web/v666_async_function_ui.py'),str(restored/'content'),str(packaged_report),'storage','--out-root'],cwd=checkout,env=env)
            work.run('restored-async-runtime',[sys.executable,str(checkout/'tests/probes/async_runtime.py'),str(restored/'content')],cwd=checkout,env=env)

        elif args.suite=='async-completion':
            work.run('restored-completion-ui',[sys.executable,str(checkout/'tests/web/v666_async_completion_ui.py'),str(restored/'content'),str(packaged_report),'late','--out-root'],cwd=checkout,env=env)
            work.run('restored-completion-storage',[sys.executable,str(checkout/'tests/web/v666_async_completion_ui.py'),str(restored/'content'),str(packaged_report),'storage','--out-root'],cwd=checkout,env=env)
            work.run('restored-async-runtime',[sys.executable,str(checkout/'tests/probes/async_runtime.py'),str(restored/'content')],cwd=checkout,env=env)

        elif args.suite=='async-transition':
            work.run('restored-async-ui',[sys.executable,str(checkout/'tests/web/v666_async_transition_ui.py'),str(restored/'content'),str(packaged_report),'late','--out-root'],cwd=checkout,env=env)
            work.run('restored-async-storage',[sys.executable,str(checkout/'tests/web/v666_async_transition_ui.py'),str(restored/'content'),str(packaged_report),'storage','--out-root'],cwd=checkout,env=env)
            work.run('restored-async-runtime',[sys.executable,str(checkout/'tests/probes/async_runtime.py'),str(restored/'content')],cwd=checkout,env=env)

        elif args.suite in ['root-execution-import-observations','async-runtime']:
            work.run('restored-imports',[sys.executable,str(checkout/'tests/web/v666_root_execution_ui.py'),str(restored/'content'),str(packaged_report),'late','--out-root','--imports-root'],cwd=checkout,env=env)
        elif args.suite=='root-execution-owned-updates':
            work.run('restored-owned-update',[sys.executable,str(checkout/'tests/web/v666_root_execution_owned_update_ui.py'),str(restored/'content'),str(packaged_report),'late','--out-root','--child-dispatch'],cwd=checkout,env=env)

        elif args.suite=='root-execution-wrappers':
            work.run('restored-public-wrapper',[sys.executable,str(checkout/'tests/web/v666_root_execution_wrapper_ui.py'),str(restored/'content'),str(packaged_report),'late','--out-root'],cwd=checkout,env=env)
        elif args.suite in ['root-execution-caller','root-execution-forwarding','root-execution-observers']:
            case = 'observers' if args.suite=='root-execution-observers' else 'forwarding' if args.suite=='root-execution-forwarding' else 'caller'
            work.run('restored-'+case,[sys.executable,str(checkout/'tests/web/v666_root_execution_ui.py'),str(restored/'content'),str(packaged_report),'late','--out-root','--observer-root' if case=='observers' else '--forward-caller' if case=='forwarding' else '--branch-caller'],cwd=checkout,env=env)
        elif args.suite=='root-execution-native':
            work.run('restored-native',[sys.executable,str(checkout/'tests/web/v666_root_execution_ui.py'),str(restored/'content'),str(packaged_report),'late','--out-root','--native-root'],cwd=checkout,env=env)
        elif args.suite=='root-execution-nested':
            work.run('restored-nested',[sys.executable,str(checkout/'tests/web/v666_root_execution_ui.py'),str(restored/'content'),str(packaged_report),'late','--out-root','--nested-root'],cwd=checkout,env=env)
        elif args.suite=='root-execution-providers':
            work.run('restored-providers',[sys.executable,str(checkout/'tests/web/v666_root_execution_ui.py'),str(restored/'content'),str(packaged_report),'late','--multi-root','--providers-root'],cwd=checkout,env=env)
        elif args.suite=='public-return-data':
            work.run('restored-return-data',[sys.executable,str(checkout/'tests/web/v666_root_execution_registered_ui.py'),str(restored/'content'),str(packaged_report),'late','--nonvoid-root','--registered-copy'],cwd=checkout,env=env)
        elif args.suite=='root-execution-registered-creating':
            work.run('restored-registered-creation',[sys.executable,str(checkout/'tests/web/v666_root_execution_copy_creating_ui.py'),str(restored/'content'),str(packaged_report),'late','--out-root','--registered-creating','view'],cwd=checkout,env=env)
        elif args.suite=='root-execution-registered-copy':
            work.run('restored-registered-copy-return',[sys.executable,str(checkout/'tests/web/v666_root_execution_registered_ui.py'),str(restored/'content'),str(packaged_report),'late','--out-root','--registered-copy','view'],cwd=checkout,env=env)
        elif args.suite=='root-execution-registered':
            work.run('restored-registered-return',[sys.executable,str(checkout/'tests/web/v666_root_execution_registered_ui.py'),str(restored/'content'),str(packaged_report),'late','--out-root','view'],cwd=checkout,env=env)
        elif args.suite=='root-execution-override':
            work.run('restored-public-override',[sys.executable,str(checkout/'tests/web/v666_root_execution_override_ui.py'),str(restored/'content'),str(packaged_report),'late','--out-root','--external-parent'],cwd=checkout,env=env)
        elif args.suite=='root-execution-copy-creating':
            work.run('restored-public-copy-creating',[sys.executable,str(checkout/'tests/web/v666_root_execution_copy_creating_ui.py'),str(restored/'content'),str(packaged_report),'late','view','--out-root'],cwd=checkout,env=env)
        elif args.suite=='root-execution-copy':
            work.run('restored-public-copy',[sys.executable,str(checkout/'tests/web/v666_root_execution_copy_ui.py'),str(restored/'content'),str(packaged_report),'late','--out-root'],cwd=checkout,env=env)
        elif args.suite in ['root-execution','root-execution-out','root-execution-closure','root-execution-data-void','root-execution-compound-owned','root-execution-provider-import','root-execution-nonvoid']:
            work.run('restored-root-execution',[sys.executable,str(checkout/'tests/web/v666_root_execution_ui.py'),str(restored/'content'),str(packaged_report),'late',*(['--nonvoid-root'] if args.suite=='root-execution-nonvoid' else ['--provider-import'] if args.suite=='root-execution-provider-import' else ['--compound-root'] if args.suite=='root-execution-compound-owned' else ['--multi-root'] if args.suite=='root-execution-closure' else ['--data-root'] if args.suite=='root-execution-data-void' else ['--out-root'] if args.suite=='root-execution-out' else [])],cwd=checkout,env=env)
        elif args.suite in ['node-internal-override','node-internal-external-override']:
            work.run('restored-copy-regression',[sys.executable,str(checkout/'tests/web/v666_node_internal_copy_creating_ui.py'),str(restored/'content'),str(packaged_report),'loss','view','--branch','--nested','--refs'],cwd=checkout,env=env)
            work.run('restored-owned-override',[sys.executable,str(checkout/'tests/web'/('v666_node_internal_external_override_ui.py' if args.suite=='node-internal-external-override' else 'v666_node_internal_override_ui.py')),str(restored/'content'),str(packaged_report),'late'],cwd=checkout,env=env)
        elif args.suite in ['node-internal-copy-creating','node-internal-copy-frames']:
            work.run('restored-saved-copy',[sys.executable,str(checkout/'tests/web/v666_node_internal_context_ui.py'),str(restored/'content'),str(packaged_report),'normal','--copy','--raw-copy'],cwd=checkout,env=env)
            work.run('restored-creating-copy',[sys.executable,str(checkout/'tests/web/v666_node_internal_copy_creating_ui.py'),str(restored/'content'),str(packaged_report),'loss','view',*(['--branch','--nested','--refs'] if args.suite=='node-internal-copy-frames' else ['--context','--refs','--raw-copy'])],cwd=checkout,env=env)

        elif args.suite=='node-internal-copy-context':
            work.run('restored-direct-context',[sys.executable,str(checkout/'tests/web/v666_node_internal_context_ui.py'),str(restored/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('restored-copy-context',[sys.executable,str(checkout/'tests/web/v666_node_internal_context_ui.py'),str(restored/'content'),str(packaged_report),*['loss','--copy','--raw-copy','--refs','view']],cwd=checkout,env=env)
        elif args.suite=='node-internal-copy-branches':
            work.run('restored-direct-branch',[sys.executable,str(checkout/'tests/web/v666_node_internal_branch_ui.py'),str(restored/'content'),str(packaged_report),'normal'],cwd=checkout,env=env)
            work.run('restored-copy-branch',[sys.executable,str(checkout/'tests/web/v666_node_internal_branch_ui.py'),str(restored/'content'),str(packaged_report),'loss','--copy',*(['view','--nested','--refs'])],cwd=checkout,env=env)
        elif args.suite=='node-internal-copy-storage':
            work.run('restored-node-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_ui.py'),str(restored/'content'),str(packaged_report),'storage'],cwd=checkout,env=env)
            work.run('restored-copy-storage',[sys.executable,str(checkout/'tests/web/v666_node_internal_copy_ui.py'),str(restored/'content'),str(packaged_report),'loss','view','--storage-copy','--private','--local'],cwd=checkout,env=env)

        elif args.suite in ['node-internal-copy','node-internal-copy-nested']:
            work.run('restored-node-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_ui.py'),str(restored/'content'),str(packaged_report),'storage'],cwd=checkout,env=env)
            work.run('restored-copy-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_copy_ui.py'),str(restored/'content'),str(packaged_report),'loss','view'],cwd=checkout,env=env)
            if args.suite=='node-internal-copy-nested':
                work.run('restored-nested-copy',[sys.executable,str(checkout/'tests/web/v666_node_internal_copy_ui.py'),str(restored/'content'),str(packaged_report),'loss','view','--depth=2'],cwd=checkout,env=env)

        elif args.suite=='node-branch-exits':
            work.run('restored-node-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_ui.py'),str(restored/'content'),str(packaged_report),'storage'],cwd=checkout,env=env)
            work.run('restored-branch-exits',[sys.executable,str(checkout/'tests/web/v666_node_branch_exit_ui.py'),str(restored/'content'),str(packaged_report),'loss','--refs'],cwd=checkout,env=env)

        elif args.suite=='node-internal-branches':
            work.run('restored-node-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_ui.py'),str(restored/'content'),str(packaged_report),'storage'],cwd=checkout,env=env)
            work.run('restored-branch-node-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_branch_ui.py'),str(restored/'content'),str(packaged_report),'loss','--refs'],cwd=checkout,env=env)
        elif args.suite=='node-internal-context':
            work.run('restored-node-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_ui.py'),str(restored/'content'),str(packaged_report),'storage'],cwd=checkout,env=env)
            work.run('restored-context-node-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_context_ui.py'),str(restored/'content'),str(packaged_report),'loss','--refs'],cwd=checkout,env=env)
        elif args.suite in ['owned-conversion','action-icons','declaration-icons','pin-icons','enum-definitions','enum-values','enum-retirement','worker-badges','node-internal']:
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
        if args.suite in ['action-icons','declaration-icons','pin-icons','enum-definitions','enum-values','enum-retirement','worker-badges','node-internal']:
            work.run('restored-action-icons',[sys.executable,str(checkout/'tests/web/v666_action_icon_ui.py'),str(restored/'content'),str(packaged_report),'late'],cwd=checkout,env=env)
        if args.suite in ['declaration-icons','pin-icons','enum-definitions','enum-values','enum-retirement','worker-badges','node-internal']:
            work.run('restored-declaration-icons',[sys.executable,str(checkout/'tests/web/v666_declaration_icon_ui.py'),str(restored/'content'),str(packaged_report),'late','category','view'],cwd=checkout,env=env)
        if args.suite in ['pin-icons','enum-definitions','enum-values','enum-retirement','worker-badges','node-internal']:
            work.run('restored-module-pins',[sys.executable,str(checkout/'tests/web/v666_module_pin_ui.py'),str(restored/'content'),str(packaged_report),'late','view','return'],cwd=checkout,env=env)
            work.run('restored-set-output-icons',[sys.executable,str(checkout/'tests/web/v666_set_output_icon_ui.py'),str(restored/'content'),str(packaged_report),'late'],cwd=checkout,env=env)
        if args.suite in ['enum-definitions','enum-values','enum-retirement','worker-badges','node-internal']:
            work.run('restored-information-enum',[sys.executable,str(checkout/'tests/web/v666_information_enum_ui.py'),str(restored/'content'),str(packaged_report),'late','view'],cwd=checkout,env=env)
        if args.suite in ['enum-values','enum-retirement','worker-badges','node-internal']:
            work.run('restored-information-enum-values',[sys.executable,str(checkout/'tests/web/v666_information_enum_values_ui.py'),str(restored/'content'),str(packaged_report),'late','view'],cwd=checkout,env=env)
        if args.suite in ['enum-retirement','worker-badges','node-internal']:
            work.run('restored-information-enum-retirement',[sys.executable,str(checkout/'tests/web/v666_information_enum_retirement_ui.py'),str(restored/'content'),str(packaged_report),'loss','view'],cwd=checkout,env=env)
        if args.suite in ['worker-badges','node-internal']:
            work.run('restored-worker-badges',[sys.executable,str(checkout/'tests/web/v666_worker_badges_ui.py'),str(restored/'content'),str(packaged_report)],cwd=checkout,env=env)
        if args.suite=='node-internal':
            work.run('restored-node-internal',[sys.executable,str(checkout/'tests/web/v666_node_internal_ui.py'),str(restored/'content'),str(packaged_report),'storage'],cwd=checkout,env=env)
        work.run('package-failure-lifetime',[sys.executable,str(checkout/'tests/probes/desktop_package_lifetime.py'),str(checkout),str(restored)],cwd=checkout,env=env)
        if dependency_identity(args.sdk,args.nuget_seed,commit) != inputs:
            raise RuntimeError('SDK/dependency seed changed during verification; no package promotion')
        atomic_json(work.evidence/'package.json',entry)
        atomic_json(work.evidence/'summary.json',{'sourceCommit':commit,'independentCheckouts':2,
            'allStagesPassed':True,'suite':args.suite,'actualWindows':False,'actualMobile':False,'libraryDelivered':False,
            'freshStages':len(work.state['results']),'reusedChecks':work.state.get('reusedChecks',[]),
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
