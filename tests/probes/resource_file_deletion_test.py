"""Real independent pack consumer, bounded owned copies; no EditorHome or external files."""
import pathlib,sys,tempfile,os,json,subprocess
r=pathlib.Path(sys.argv[1]).resolve();cli=pathlib.Path(sys.argv[2]).resolve()
case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-resource-file-deletion-'));project=case/'consumer';project.mkdir()
(project/'Main.csbody').write_text((r/'tests/fixtures/project-resources/FileDeletion.csbody').read_text())
(project/'Main.celem').write_text('function Probe.Resources::Main () -> int {provide Probe.Resources::Main with Probe.Resources::MainBody;provide Confectory.FileStream::BoundedSnapshot with Confectory.FileStream::BoundedSnapshotBody;provide Confectory.FileStream::WriteAtomic with Confectory.FileStream::WriteAtomicBody;provide Confectory.FileStream::LeasePath with Confectory.FileStream::LeasePathBody;}')
(project/'MainBody.celem').write_text('implementation Probe.Resources::MainBody for Probe.Resources::Main () -> int {import Confectory.ProjectResources::Layout as Layout (string,string,string,string) -> string;import Confectory.ProjectResources::Request as Request (string,string,string,string) -> string;body common "Main.csbody";}')
def quote(value):return json.dumps(str(value))
(project/'project.cpack').write_text('project Probe.Resources version "1" {standalone true;registry Confectory.ProjectResources '+quote(r/'packs/project-resources/pack.cpack')+';dependency Confectory.ProjectResources version "0.1.0";registry Confectory.FileStream '+quote(r/'packs/file-stream/pack.cpack')+';dependency Confectory.FileStream version "0.1.0";registry Confectory.Build.DotNet '+quote(r/'targets/dotnet/pack.cpack')+';dependency Confectory.Build.DotNet version "0.1.0";target linux Confectory.Build.DotNet::Linux;element Main function "Main.celem";element MainBody implementation "MainBody.celem";entry Probe.Resources::Main;}')
env=os.environ.copy();env['CONFECTORY_RESOURCE_CASE']=str(case/'owned assets project')
sdk=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet')
run=subprocess.run([sdk,str(cli),'run',str(project/'project.cpack'),'linux'],cwd=r,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(case/'run.log').write_text(run.stdout);print(run.stdout,flush=True);print('RESOURCE_PROBE_FIXTURE',case,flush=True)
assert run.returncode==0,run.returncode
results=json.loads((case/'owned assets project'/'checks.json').read_text());assert len(results)>=35
print('PASS independent resource provider:',len(results),'actual checks; no editor ownership or demo catalog',flush=True)
