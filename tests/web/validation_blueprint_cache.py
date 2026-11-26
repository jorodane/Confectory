"""Real candidate validation and execution of an imported Blueprint pack."""
import hashlib,json,os,shutil,subprocess,sys,tempfile,uuid
from pathlib import Path
repo=Path(sys.argv[1]).resolve()
command=[os.environ['CONFECTORY_DOTNET'],os.environ['CONFECTORY_ELEMENT_AUTHORING_HOST']]
with tempfile.TemporaryDirectory(prefix='confectory-import-blueprint-') as folder:
    root=Path(folder);pack=root/'blueprint-pack';shutil.copytree(repo/'examples/feature-blueprint',pack,ignore=shutil.ignore_patterns('.confectory','bin','obj'))
    (pack/'pack.cpack').write_text('pack Example.FeatureBlueprint version "0.1.0" { standalone false; element Main function "Main.celem"; element MainBody implementation "MainBody.celem"; element Add function "Add.celem"; element AddBody implementation "AddBody.celem"; }')
    project=root/'consumer';project.mkdir();profile=root/'profile';profile.mkdir()
    (project/'project.cpack').write_text(f'project Test.Consumer version "1" {{ standalone true; registry Example.FeatureBlueprint "{pack}/pack.cpack"; dependency Example.FeatureBlueprint version "0.1.0"; registry Confectory.Build.DotNet "{repo}/targets/dotnet/pack.cpack"; dependency Confectory.Build.DotNet version "0.1.0"; target linux Confectory.Build.DotNet::Linux; entry Test.Consumer::Main; element Main function "Main.celem"; element MainBody implementation "MainBody.celem"; }}')
    (project/'Main.celem').write_text('function Test.Consumer::Main () -> int { provide Test.Consumer::Main with Test.Consumer::MainBody; provide Example.FeatureBlueprint::Main with Example.FeatureBlueprint::MainBody; provide Example.FeatureBlueprint::Add with Example.FeatureBlueprint::AddBody; }')
    (project/'MainBody.celem').write_text('implementation Test.Consumer::MainBody for Test.Consumer::Main () -> int { import Example.FeatureBlueprint::Main as Probe () -> int; body common "Main.csbody"; }')
    (project/'Main.csbody').write_text('return calls.Probe.Invoke();')
    env=dict(os.environ,CONFECTORY_HOME_STORAGE=str(profile))
    def candidate(expected):
        path=project/'.confectory'/'candidates'/uuid.uuid4().hex
        shutil.copytree(project,path,ignore=shutil.ignore_patterns('.confectory'))
        try:
            result=subprocess.run(command,input=json.dumps(dict(operation='validate',project=str(path/'project.cpack'),target='linux')),text=True,capture_output=True,timeout=120,check=True,env=env)
            reply=json.loads(result.stdout)
            if expected is None:assert not reply['ok'],reply;return
            assert reply['ok'],reply
            report=json.loads((path/'.confectory/outputs/linux/latest.json').read_text())
            actual=subprocess.run(report['run'],cwd=path,text=True,capture_output=True,timeout=20,check=True,env=env)
            assert actual.stdout.strip()==expected,actual.stdout
        finally:shutil.rmtree(path)
    def records():return {p.parent.name:(p,p.stat().st_mtime_ns) for p in (profile/'validation-implementations-v1').glob('*/*/artifact.json')}
    candidate('5');saved=records();assert len(saved)==1,saved
    candidate('5');assert records()==saved,'unchanged Blueprint compiler inputs must reuse the same artifact'
    record=next(iter(saved.values()))[0];data=json.loads(record.read_text());assembly=record.parent/data['files']['assembly']['path'];assembly.write_bytes(b'damaged Blueprint cache')
    candidate('5');assert hashlib.sha256(assembly.read_bytes()).hexdigest()==json.loads(record.read_text())['files']['assembly']['hash']
    node=pack/'print.node.json';original=node.read_text();stamp=node.stat();changed=json.loads(original);changed['source']='Console.WriteLine(value + 1);\nreturn 0;';node.write_text(json.dumps(changed));os.utime(node,ns=(stamp.st_atime_ns,stamp.st_mtime_ns))
    candidate('6');assert len(records())==2
    changed['source']='this is not valid C#;';node.write_text(json.dumps(changed));candidate(None)
    node.write_text(original);candidate('5')
    print('PASS exact imported Blueprint artifact reuse, real linked output, changed node with same timestamp, invalid node and damaged cache recovery')
