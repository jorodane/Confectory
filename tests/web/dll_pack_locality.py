"""Actual editor Run and isolated Confirm candidate DLL locality.

Only generated local fixtures are edited; the dependency edits are external
file edits, not an attempt to edit registered read-only packs in the UI.
"""
import json,os,shutil,subprocess,sys,time,uuid
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import v666_workspace_finder_fixture as f
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'gui'))
from editor_logic_workflow import run_from_dock

observe_only='observe' in sys.argv[3:]
host=[os.environ['CONFECTORY_DOTNET'],os.environ['CONFECTORY_ELEMENT_AUTHORING_HOST']]
project=f.projects[0]; root=project.parent; marker=f.root/'dll-result.txt'
packs={ns:f.root/ns for ns in ('A.Probe','Z.Probe')}
for p in packs.values():p.mkdir()
def author(operation,**kwargs):
    reply=json.loads(subprocess.run(host,input=json.dumps(dict(operation=operation,**kwargs)),text=True,capture_output=True,check=True,timeout=120).stdout)
    assert reply['ok'],reply
    return reply['result']
def prepare(ns,returns,value):
    p=packs[ns];id=ns+'::Value';impl=id+'Body'
    prepared=author('blueprintPrepareFeature',id=id,text=f'function {id} () -> {returns} {{description "Local probe";}}',implementation=impl,graphPath='value.graph.json',nodePath='value.node.json')
    defs=author('featureBlueprintNodes',featureSource=prepared['function'],graph=prepared['graph'],bodyTarget='common')
    assert defs['state']=='node-definitions',defs
    record=prepared['node'];record['definitionHash']=defs['nodes'][0]['definitionHash'];record['source']=f'return {value};'
    (p/'pack.cpack').write_text(f'pack {ns} version "1" {{ element Value function "Value.celem"; element ValueBody implementation "ValueBody.celem"; }}')
    (p/'Value.celem').write_text(prepared['function']);(p/'ValueBody.celem').write_text(prepared['implementation'])
    (p/'value.graph.json').write_text(json.dumps(prepared['graph']));(p/'value.node.json').write_text(json.dumps(record))
def consumer(returns):
    (root/'DllMain.celem').write_text('function Test.DllConsumer::Main () -> int { provide Test.DllConsumer::Main with Test.DllConsumer::MainBody; provide A.Probe::Value with A.Probe::ValueBody; provide Z.Probe::Value with Z.Probe::ValueBody; }')
    (root/'DllMainBody.celem').write_text(f'implementation Test.DllConsumer::MainBody for Test.DllConsumer::Main () -> int {{ import A.Probe::Value as First () -> {returns}; import Z.Probe::Value as Last () -> int; body common "DllMain.csbody"; }}')
    (root/'DllMain.csbody').write_text(f'System.IO.File.WriteAllText({json.dumps(str(marker))}, calls.First.Invoke().ToString()+":"+calls.Last.Invoke().ToString()); return 0;')
prepare('A.Probe','int',5);prepare('Z.Probe','int',9);consumer('int')
project.write_text(f'project Test.DllConsumer version "1" {{ standalone true; registry A.Probe "{packs["A.Probe"]}/pack.cpack"; dependency A.Probe version "1"; registry Z.Probe "{packs["Z.Probe"]}/pack.cpack"; dependency Z.Probe version "1"; registry Confectory.Build.DotNet "{f.repo}/targets/dotnet/pack.cpack"; dependency Confectory.Build.DotNet version "0.1.0"; target linux Confectory.Build.DotNet::Linux; entry Test.DllConsumer::Main; element Main function "DllMain.celem"; element MainBody implementation "DllMainBody.celem"; }}')
profile=f.root/'profile';profile.mkdir(exist_ok=True)
env=dict(f.env,CONFECTORY_HOME_STORAGE=str(profile))
observations=[]
def report(kind,case,data,wall):
    s=data['statistics']
    row=dict(kind=kind,case=case,wallMs=round(wall*1000),compiled=s['compiledPacks'],reused=s['reusedPacks'],contracts=s['compiledContractPacks'],checked=s['checkedContractConsumers'],targetCalls=s['targetInvocations'],reusedLinks=s.get('reusedFinalLinks',0),targetMs={k:round(v) for k,v in s['targetElapsedMilliseconds'].items()})
    assert row['targetCalls'].get('link',0)+row['reusedLinks']==1,row
    observations.append(row);print('OBSERVATION '+json.dumps(row),flush=True)
    return row
def candidate(case,expected):
    path=root/'.confectory'/'candidates'/uuid.uuid4().hex
    shutil.copytree(root,path,ignore=shutil.ignore_patterns('.confectory'))
    try:
        start=time.perf_counter()
        result=subprocess.run(host,input=json.dumps(dict(operation='validate',project=str(path/'project.cpack'),target='linux')),text=True,capture_output=True,check=True,timeout=120,env=env)
        reply=json.loads(result.stdout)
        if expected is None:
            assert not reply['ok'] and reply.get('code')=='CONTRACT_MISMATCH',reply
            print('PASS stale consumer import rejected for changed published contract',flush=True);return None
        assert reply['ok'],reply
        data=json.loads((path/'.confectory/outputs/linux/latest.json').read_text())
        row=report('candidate',case,data,time.perf_counter()-start)
        subprocess.run(data['run'],cwd=path,check=True,timeout=20,env=env)
        assert marker.read_text()==expected
        return row
    finally:shutil.rmtree(path)
def ui_run(browser,case,expected,index):
    f.start(index)
    try:
        page=f.setup(browser);page.set_viewport_size({'width':1800,'height':1200})
        start=time.perf_counter();run_from_dock(page,marker,expected)
        data=json.loads((root/'.confectory/outputs/linux/latest.json').read_text())
        result=report('run',case,data,time.perf_counter()-start)
        page.get_by_role('tab',name='Workspace',exact=True).click();expect(page.get_by_role('button',name='프로젝트 실행',exact=True)).to_be_visible()
        page.evaluate('async()=>await confectoryFlushPresentation()');page.close();return result
    finally:f.stop()
try:
    with sync_playwright() as pw,pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) as browser:
        initial=candidate('initial','5:9');ui_run(browser,'initial','5:9',0)
        warm=candidate('unchanged','5:9');warm_run=ui_run(browser,'unchanged','5:9',1)
        assert not warm_run['compiled'] and not warm_run['contracts']
        if not observe_only:assert warm_run['reusedLinks']==1 and not warm_run['targetCalls'].get('link'),warm_run
        assert not {'A.Probe','Z.Probe'}.intersection(warm['compiled']) and {'A.Probe','Z.Probe'}.issubset(warm['reused'])
        node=packs['A.Probe']/'value.node.json';stamp=node.stat();record=json.loads(node.read_text());record['source']='return 6;';node.write_text(json.dumps(record));os.utime(node,ns=(stamp.st_atime_ns,stamp.st_mtime_ns))
        body=candidate('implementation','6:9');body_run=ui_run(browser,'implementation','6:9',2)
        assert body_run['compiled']==['A.Probe'] and not body_run['contracts'],body_run
        assert 'Z.Probe' in body_run['reused']
        prepare('A.Probe','long',7);candidate('stale-contract',None);consumer('long')
        contract=candidate('contract','7:9');contract_run=ui_run(browser,'contract','7:9',3)
        assert set(contract_run['compiled'])=={'A.Probe','Test.DllConsumer'},contract_run
        assert 'Z.Probe' in contract_run['reused'] and contract_run['contracts']==['A.Probe'],contract_run
        assert set(contract_run['checked']['A.Probe::Value']).issuperset({'A.Probe::ValueBody','Test.DllConsumer::MainBody'}),contract_run
        if not observe_only and 'quick' not in sys.argv[3:]:
            latest=root/'.confectory/outputs/linux/latest.json'
            old=json.loads(latest.read_text());output=Path(old['output'])
            (output/'Confectory.App.dll').write_bytes(b'damaged final output')
            damaged=ui_run(browser,'damaged-final','7:9',4)
            assert damaged['targetCalls'].get('link')==1 and not damaged['compiled'],damaged
            assert (output/'Confectory.App.dll').read_bytes()==b'damaged final output'
            recovered=ui_run(browser,'recovered-warm','7:9',5)
            assert recovered['reusedLinks']==1 and not recovered['compiled'],recovered
            # A dependency copy and launcher permission belong to the complete output.
            old=json.loads(latest.read_text());output=Path(old['output'])
            dep=next(output.glob('Pack_*.dll'));dep.write_bytes(b'damaged dependency copy')
            copied=ui_run(browser,'damaged-copy','7:9',6)
            assert copied['targetCalls'].get('link')==1 and not copied['compiled'],copied
            old=json.loads(latest.read_text());output=Path(old['output']);launcher=output/'run';launcher.chmod(0o600)
            perms=ui_run(browser,'damaged-launcher','7:9',7)
            assert perms['targetCalls'].get('link')==1 and not perms['compiled'],perms

        if not observe_only:
            assert 'Z.Probe' not in body['compiled'] and 'Z.Probe' in body['reused'],body
            assert 'Z.Probe' not in contract['compiled'] and 'Z.Probe' in contract['reused'],contract
        assert not f.errors and not f.external,(f.errors,f.external)
        assert all(Path(p).read_bytes()==v for p,v in f.before.items() if Path(p).is_relative_to(f.projects[1].parent))
        print('PASS unchanged, implementation-only and contract-change real editor Run and isolated candidate locality',flush=True)
finally:
    f.stop();(f.root/'dll-observations.json').write_text(json.dumps(observations,indent=2));print('evidence',f.root,flush=True)
