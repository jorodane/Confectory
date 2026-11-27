"""Actual local policy consumer; no accounts, credentials or external services."""
import json,os,subprocess,sys,tempfile,hashlib
from pathlib import Path

repo=Path(sys.argv[1]).resolve()
root=Path(tempfile.mkdtemp(prefix='confectory-settings-policy-'))
sample=root/'consumer';sample.mkdir()
a=root/'ai-settings'/hashlib.sha256(b'Test.Agent::Connection').hexdigest()[:16]/'project.cpack'
b=root/'ai-settings'/hashlib.sha256(b'Test.Other::Connection').hexdigest()[:16]/'project.cpack'
for owner in (a,b):
    owner.parent.mkdir(parents=True)
    owner.write_text('project Confectory.AISettings version "1" {standalone false; element Settings object "Settings.celem";}')
    owner.with_name('Settings.celem').write_text('object Confectory.AISettings::Settings {}\n')
original={f:f.read_bytes() for owner in (a,b) for f in owner.parent.iterdir() if f.is_file()}
manifest='project Test.Policy version "1" { standalone true; entry Test.Policy::Main;'
for name,path in (('Confectory.AIConnection','packs/ai-connection/pack.cpack'),('Confectory.SchemaEditing','packs/schema-editing/pack.cpack'),('Confectory.Build.DotNet','targets/dotnet/pack.cpack')):
    manifest+=' registry '+name+' '+json.dumps(str(repo/path))+'; dependency '+name+' version "0.1.0";'
manifest+=' target portable Confectory.Build.DotNet::Portable; element Main function "Main.celem"; element MainBody implementation "MainBody.celem"; }'
(sample/'project.cpack').write_text(manifest)
(sample/'Main.celem').write_text('function Test.Policy::Main () -> int {provide Test.Policy::Main with Test.Policy::MainBody; provide Confectory.SchemaEditing::Inspect with Confectory.SchemaEditing::InspectBody; provide Confectory.SchemaEditing::Call with Confectory.SchemaEditing::CallBody;}')
(sample/'MainBody.celem').write_text('''implementation Test.Policy::MainBody for Test.Policy::Main () -> int {
import Confectory.AIConnection::ValidateSettings as Plain (string) -> void;
import Confectory.AIConnection::ValidateSettingsForOwner as Scoped (string,string) -> void;
body common "Main.csbody";}''')
(sample/'Main.csbody').write_text(r'''
string a=Environment.GetEnvironmentVariable("CONFECTORY_TEST_POLICY_A")!,b=Environment.GetEnvironmentVariable("CONFECTORY_TEST_POLICY_B")!;
string Valid(string fields)=>"object Confectory.AISettings::Settings {"+fields+"}";
void Denied(Action action){try{action();}catch(ArgumentException){return;}catch(InvalidOperationException){return;}throw new Exception("unsafe setting accepted");}
string valid=Valid("data model = \"fixture\"; data credentialReference = \"\";");
calls.Plain.Invoke(valid);calls.Scoped.Invoke(valid,a);calls.Scoped.Invoke(valid,b);
foreach(string fields in new[]{"data password = \"synthetic-invalid\";","value credentialReference = \"fixture\";","data credentialReference = 42;","data credentialReference = \"not-a-binding\";"}){
 string text=Valid(fields);Denied(()=>calls.Plain.Invoke(text));Denied(()=>calls.Scoped.Invoke(text,a));Denied(()=>calls.Scoped.Invoke(text,b));
}
Denied(()=>calls.Scoped.Invoke("object Test.Other::Other {}",a));
Denied(()=>calls.Scoped.Invoke("not a declaration",a));
// Not an owned settings path: retain the ordinary validation path, including rejection.
calls.Scoped.Invoke(valid,System.IO.Path.Combine(System.IO.Path.GetDirectoryName(a)!,"other.cpack"));
Denied(()=>calls.Scoped.Invoke(Valid("data password = \"synthetic-invalid\";"),""));
Console.WriteLine("PASS exact shared policy, wrong identity, fallback and owner-switch checks");return 0;
''')
env=os.environ.copy();env.update(CONFECTORY_TEST_POLICY_A=str(a),CONFECTORY_TEST_POLICY_B=str(b))
dotnet=env['CONFECTORY_DOTNET']
cli=repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'
build=subprocess.run([dotnet,str(cli),'build',str(sample/'project.cpack'),'portable'],cwd=repo,env=env,capture_output=True,text=True,check=True,timeout=90)
report=json.loads(build.stdout)
result=subprocess.run(report['run'],cwd=sample,env=env,capture_output=True,text=True,check=True,timeout=90)
assert 'PASS exact shared policy' in result.stdout,result.stdout+result.stderr
assert all(f.read_bytes()==value for f,value in original.items())
print(result.stdout.strip());print('evidence',root)
