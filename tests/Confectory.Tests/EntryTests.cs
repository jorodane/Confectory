using System.Text.Json.Nodes;
using Confectory.Core;
using Confectory.DesktopEntry;
namespace Confectory.Tests;
public sealed class EntryTests : TestCase
{
 public void test_standalone_declaration_and_cproj_compatibility()
 {
  var legacy=new Parser("project Old version \"1\" { entry Old::Main; }","legacy.cpack").ParseManifest();True(legacy.SupportsStandalone&&legacy.Standalone is null);True(!new Parser("pack Library version \"1\" {}","pack.cpack").ParseManifest().SupportsStandalone);
  var disabled=new Parser("project Disabled version \"1\" { standalone false; entry Disabled::Main; }","project.cproj").ParseManifest();True(!disabled.SupportsStandalone);
  Error("SYNTAX",()=>new Parser("pack P version \"1\" { standalone \"true\"; }","x").ParseManifest());Error("DUPLICATE_DECLARATION",()=>new Parser("pack P version \"1\" { standalone false; standalone true; }","x").ParseManifest());
  string project=Path.Combine(f.Root,"공백 프로젝트.cproj");File.Copy(f.Project,project);var inspected=EntryProtocol.Inspect(project,"portable");True(inspected["canOpen"]!.GetValue<bool>()&&inspected["supportsStandalone"]!.GetValue<bool>()&&inspected["executionAssessment"]!.ToString()=="requires-explicit-build-and-runtime-verification");True(!EntryProtocol.Inspect(project,"android")["hostEligible"]!.GetValue<bool>());
  string library=Path.Combine(f.Root,"library.cpack");File.WriteAllText(library,"pack Library version \"1\" { standalone false; }");True(EntryProtocol.Inspect(library,"portable")["canOpen"]!.GetValue<bool>()&&!EntryProtocol.Read(library).SupportsStandalone);
  File.WriteAllText(project,"pack Library version \"1\" { standalone false; }");bool wrong=false;try{EntryProtocol.Read(project);}catch(ArgumentException){wrong=true;}True(wrong,".cproj cannot disguise a plain library");
 }
 public void test_association_quoting_and_delivery_failure()
 {
  string registration=WindowsAssociation.Format(@"C:\Program Files\dotnet\dotnet.exe",@"C:\한글 작업\Entry.dll",@"C:\한글 작업");True(registration.Contains("HKEY_CURRENT_USER")&&!registration.Contains("HKEY_LOCAL_MACHINE")&&!registration.Contains("UserChoice"));True(registration.Contains("\\\"%1\\\"")&&registration.Contains("한글 작업"),"Unicode installation and exactly quoted file argument");
  string? storage=Environment.GetEnvironmentVariable("CONFECTORY_ENTRY_STORAGE");try{Environment.SetEnvironmentVariable("CONFECTORY_ENTRY_STORAGE",Path.Combine(f.Root,"inboxes"));
  string scope=Path.Combine(f.Root,"unreachable installation");string folder=EntryProtocol.Folder(scope);Directory.CreateDirectory(folder);
  using(var owner=new FileStream(Path.Combine(folder,"owner.lock"),FileMode.OpenOrCreate,FileAccess.ReadWrite,FileShare.None)){
   string? previous=Environment.GetEnvironmentVariable("CONFECTORY_ENTRY_SCOPE");try{Environment.SetEnvironmentVariable("CONFECTORY_ENTRY_SCOPE",scope);var failed=Processes.Run(new[]{Processes.DotNet(),typeof(EntryProtocol).Assembly.Location,"open",f.Project,"--repository",Fixture.Repo},timeoutSeconds:10);True(failed.ExitCode!=0&&failed.Stderr.Contains("No replacement"),failed.Stdout+failed.Stderr);True(!File.Exists(Path.Combine(folder,"startup.json")),"Unreachable existing owner must not launch replacement");}finally{Environment.SetEnvironmentVariable("CONFECTORY_ENTRY_SCOPE",previous);}
  }
  using var pipe=new System.IO.Pipes.NamedPipeServerStream("Confectory.Entry."+EntryProtocol.Key(scope),System.IO.Pipes.PipeDirection.InOut,1,System.IO.Pipes.PipeTransmissionMode.Byte,System.IO.Pipes.PipeOptions.Asynchronous|System.IO.Pipes.PipeOptions.CurrentUserOnly);
  var accept=pipe.WaitForConnectionAsync();var send=EntryProtocol.Send(scope,f.Project,Guid.NewGuid().ToString("N"),500,100);accept.GetAwaiter().GetResult();bool canceled=false;try{send.GetAwaiter().GetResult();}catch(OperationCanceledException){canceled=true;}True(canceled,"Lost acknowledgment is not a connection timeout/cold-start signal");
  }finally{Environment.SetEnvironmentVariable("CONFECTORY_ENTRY_STORAGE",storage);}
 }
 public void test_project_entry_public_protocol_and_locality()
 {
  string sample=Path.Combine(f.Root,"entry probe"),pack=Path.Combine(f.Root,"entry pack");Fixture.CopyTree(Path.Combine(Fixture.Repo,"tests","native","project-entry-probe"),sample);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","project-entry"),pack);
  string project=Path.Combine(sample,"project.cproj");File.WriteAllText(project,File.ReadAllText(project).Replace("../../../packs/project-entry/pack.cpack",Path.Combine(pack,"pack.cpack")).Replace("../../../",Fixture.Repo+"/"));var built=new Builder(project,"portable").Build();Output(built,"ProjectEntry public inbox PASS");
  File.AppendAllText(Path.Combine(pack,"Request.csbody"),"\n// transport implementation locality\n");var changed=new Builder(project,"portable").Build();Sequence(new[]{"Confectory.ProjectEntry::RequestBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);Output(changed,"ProjectEntry public inbox PASS");
  File.WriteAllText(project,File.ReadAllText(project).Replace("target portable Confectory.Build.DotNet::Portable;","target portable Confectory.Build.DotNet::Portable; target android Confectory.Build.DotNet::Portable;"));var android=new Builder(project,"android").Build();var rejected=Processes.Run(Strings(android,"run"));True(rejected.ExitCode!=0&&rejected.Stderr.Contains("Activity intent/content-URI"),"Managed Android provider selection is explicit refusal, not desktop fallback/native app coverage");
 }
 public void test_project_file_entry_actual_x11_startup_and_existing_instance()
 {
  if(string.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISPLAY"))){Console.WriteLine("SKIP file entry GUI: no DISPLAY");return;}
  var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests","gui","project_entry_x11.py"),Fixture.Repo},timeoutSeconds:300);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("ProjectEntry actual X11 PASS"));
 }
 public void test_library_open_edit_and_external_transition_policy()
 {
  string root=Path.Combine(f.Root,"library"),path=Path.Combine(root,"pack.cpack");Directory.CreateDirectory(root);File.WriteAllText(path,"pack Library version \"1\" { standalone false; element Thing concept \"Thing.celem\"; }");File.WriteAllText(Path.Combine(root,"Thing.celem"),"concept Library::Thing { }");
  string author=Path.Combine(Fixture.Repo,"targets","element-authoring","bin","Release","net8.0","Confectory.ElementAuthoring.dll");var describe=Processes.Run(new[]{Processes.DotNet(),author},new JsonObject{["operation"]="describe",["project"]=path}.ToJsonString());True(describe.ExitCode==0,describe.Stderr);var units=JsonNode.Parse(describe.Stdout)!["result"]!["units"]!.AsArray();True(units.Any(u=>u!["id"]!.ToString()=="Library::PackManifest")&&units.Any(u=>u!["id"]!.ToString()=="Library::Thing"));
  var validation=Processes.Run(new[]{Processes.DotNet(),author},new JsonObject{["operation"]="validate",["project"]=path,["target"]="portable"}.ToJsonString());True(validation.ExitCode==0&&JsonNode.Parse(validation.Stdout)!["result"]!["linkValidated"]!.GetValue<bool>()==false,"Library editing validates owned syntax without an implicit execution/build");
  string host=Path.Combine(Fixture.Repo,"targets","project-execution-host","bin","Release","net8.0","Confectory.ProjectExecutionHost.dll");var meta=Processes.Run(new[]{Processes.DotNet(),host,"describe",path});True(meta.ExitCode==0&&JsonNode.Parse(meta.Stdout)![3]!.ToString()=="pack");var execution=Processes.Run(new[]{Processes.DotNet(),host,"run",path,"Library::Thing","portable"});True(execution.ExitCode!=0&&!Directory.Exists(Path.Combine(root,".confectory")),"Open/describe does not execute or create a project build cache");
  var formatted=Processes.Run(new[]{Processes.DotNet(),author},new JsonObject{["operation"]="register",["text"]=File.ReadAllText(path),["id"]="Library::New",["kind"]="concept",["path"]="New.celem"}.ToJsonString());var updated=new Parser(JsonNode.Parse(formatted.Stdout)!["result"]!.GetValue<string>(),"<edited pack>").ParseManifest();True(updated.Kind=="pack"&&updated.Standalone==false,"Owned manifest formatting preserves standalone capability");
  string disabled=Path.Combine(root,"disabled.cproj");File.WriteAllText(disabled,"project Disabled version \"1\" { standalone false; entry Disabled::Main; registry Evil \"DO_NOT_BUILD\"; target portable Evil::Build; }");
  var noHost=Processes.Run(new[]{Processes.DotNet(),host,"run",disabled,"Disabled::Main","portable"});True(noHost.ExitCode!=0&&noHost.Stderr.Contains("standalone"));
  var noCli=Processes.Run(new[]{Processes.DotNet(),Path.Combine(Fixture.Repo,"src","Confectory.Cli","bin","Release","net8.0","Confectory.Cli.dll"),"run",disabled,"portable"});True(noCli.ExitCode!=0&&(noCli.Stdout+noCli.Stderr).Contains("Standalone"));
  var noPreview=Processes.Run(new[]{Processes.DotNet(),author},new JsonObject{["operation"]="run",["project"]=disabled,["target"]="portable"}.ToJsonString());True(JsonNode.Parse(noPreview.Stdout)!["ok"]!.GetValue<bool>()==false&&!Directory.Exists(Path.Combine(root,".confectory")),"Standalone false does not block metadata/editing, but every Run route rejects before build");
 }
}
