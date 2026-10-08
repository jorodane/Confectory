using Confectory.Core;
namespace Confectory.Tests;
public sealed class PackWorkspaceTests : TestCase
{
 public void test_two_contexts_revision_save_reopen_and_locality()
 {
 string sample=Path.Combine(f.Root,"workspace-consumer");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","edit-workspace"),sample);
 foreach(string name in new[]{"file-stream","schema-editing","edit-workspace","save","change-set","pack-workspace"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",name),Path.Combine(f.Root,"packs",name));
 string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/").Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack").Replace("element Main function", "registry Confectory.PackWorkspace \"../packs/pack-workspace/pack.cpack\"; dependency Confectory.PackWorkspace version \"0.1.0\";\nelement Main function"));
 File.WriteAllText(Path.Combine(sample,"main_body.celem"),"""
 implementation Example.EditWorkspace::MainBody for Example.EditWorkspace::Main () -> int {
 import Confectory.PackWorkspace::Open as Open (string,string,string) -> string;
 import Confectory.PackWorkspace::Snapshot as Snapshot (string) -> string;
 import Confectory.PackWorkspace::Command as Command (string,string,string) -> string;
 import Confectory.PackWorkspace::Close as Close (string) -> void;
 body common "main.csbody";
 }
 """);
 File.WriteAllText(Path.Combine(sample,"main.csbody"),"""
 string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT")!;
 string a=calls.Open.Invoke(project,"alice","one"),b=calls.Open.Invoke(project,"alice","two");
 var initial=System.Text.Json.Nodes.JsonNode.Parse(calls.Snapshot.Invoke(a))!;
 string id=System.Linq.Enumerable.First(initial["units"]!.AsArray(),x=>x!["kind"]!.GetValue<string>()=="body")!["id"]!.GetValue<string>();
 string Select(string h)=>calls.Command.Invoke(h,"select",System.Text.Json.JsonSerializer.Serialize(new{id}));
 string original=System.Text.Json.Nodes.JsonNode.Parse(Select(a))!["unit"]!["text"]!.GetValue<string>();Select(b);
 string edited=original+"\n// local draft one\n";
 string Edit(string h,long revision,string text)=>calls.Command.Invoke(h,"edit",System.Text.Json.JsonSerializer.Serialize(new{expectedRevision=revision,text}));
 if(System.Text.Json.Nodes.JsonNode.Parse(Edit(a,0,edited))!["conflict"]!.GetValue<bool>())throw new Exception("Unexpected conflict");
 if(!System.Text.Json.Nodes.JsonNode.Parse(Edit(a,0,"stale"))!["conflict"]!.GetValue<bool>())throw new Exception("Stale edit accepted");
 if(System.Text.Json.Nodes.JsonNode.Parse(calls.Snapshot.Invoke(b))!["unit"]!["text"]!.GetValue<string>()!=original)throw new Exception("Contexts leaked");
 string shared=calls.Open.Invoke(project,"alice","one");if(System.Text.Json.Nodes.JsonNode.Parse(Select(shared))!["unit"]!["text"]!.GetValue<string>()!=edited)throw new Exception("Same identity lost live draft");calls.Close.Invoke(shared);calls.Close.Invoke(shared);
 calls.Command.Invoke(a,"select",System.Text.Json.JsonSerializer.Serialize(new{id=initial["units"]![0]!["id"]!.GetValue<string>()}));if(System.Text.Json.Nodes.JsonNode.Parse(Select(a))!["unit"]!["text"]!.GetValue<string>()!=edited)throw new Exception("Selection discarded draft");
 calls.Command.Invoke(a,"save","{}");string owned=System.Text.Json.Nodes.JsonNode.Parse(calls.Snapshot.Invoke(a))!["unit"]!["path"]!.GetValue<string>();if(System.IO.File.ReadAllText(System.IO.Path.Combine(System.IO.Path.GetDirectoryName(project)!,owned))!=original)throw new Exception("Save modified final source");calls.Close.Invoke(a);calls.Close.Invoke(a);
 a=calls.Open.Invoke(project,"alice","one");if(System.Text.Json.Nodes.JsonNode.Parse(Select(a))!["unit"]!["text"]!.GetValue<string>()!=edited)throw new Exception("Draft lost on reopen");
 var sources=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(a,"sources","{}"))!["files"]!.AsArray();if(!System.Linq.Enumerable.Any(sources,x=>x!["kind"]!.GetValue<string>()=="project"))throw new Exception("Manifest missing");
 var review=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(a,"review","{\"target\":\"portable\"}"))!["review"]!;
 if(review["status"]!.ToString()!="ready"||review["path"]!.ToString()!=owned||review["before"]!.ToString()!=original||review["after"]!.ToString()!=edited)throw new Exception("Review omitted owned path or exact source values");
 bool rejected=false;try{calls.Command.Invoke(a,"confirm","{\"token\":\"forged\"}");}catch(InvalidOperationException){rejected=true;}if(!rejected)throw new Exception("Confirm bypassed review token");
 string reviewedToken=review["token"]!.ToString(),next=edited+"\n// after-review change\n";long revision=long.Parse(review["revision"]!.ToString());Edit(a,revision,next);
 rejected=false;try{calls.Command.Invoke(a,"confirm",System.Text.Json.JsonSerializer.Serialize(new{token=reviewedToken}));}catch(InvalidOperationException){rejected=true;}if(!rejected)throw new Exception("Changed draft confirmed with old review token");
 calls.Command.Invoke(a,"review","{\"target\":\"portable\"}");calls.Command.Invoke(a,"cancel-review","{}");var cancelled=System.Text.Json.Nodes.JsonNode.Parse(calls.Snapshot.Invoke(a))!;
 if(cancelled["review"] is not null||cancelled["unit"]!["text"]!.ToString()!=next||System.IO.File.ReadAllText(System.IO.Path.Combine(System.IO.Path.GetDirectoryName(project)!,owned))!=original)throw new Exception("Cancel modified final source or discarded draft");
 calls.Close.Invoke(a);calls.Close.Invoke(b);Console.WriteLine("PackWorkspace independent contexts/revision/save/reopen PASS");return 0;
 """);
 string? host=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST"),selected=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT");
 try{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets","element-authoring","bin","Release","net10.0","Confectory.ElementAuthoring.dll"));Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",f.Project);
 var built=new Builder(project,"portable").Build();Output(built,"PackWorkspace independent contexts/revision/save/reopen PASS");
 File.AppendAllText(Path.Combine(f.Root,"packs","pack-workspace","Snapshot.csbody"),"\n// locality\n");var changed=new Builder(project,"portable").Build();PackRebuilt(changed, new[]{"Confectory.PackWorkspace::SnapshotBody"});Equal(0,Strings(changed,"statistics","compiledContracts").Length);
 }finally{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",selected);}
 }
 public void test_target_metadata_owned_sources_no_registry_execution()
 {
 string folder=Path.Combine(f.Root,"metadata-adapter");Directory.CreateDirectory(folder);
 foreach(string target in new[]{"android-export","browser-wasm"})
 {
 string source=File.ReadAllText(Path.Combine(Fixture.Repo,"targets",target,"templates","MetadataAuthoring.cs"));
 if(target=="browser-wasm")Equal(File.ReadAllText(Path.Combine(Fixture.Repo,"targets","android-export","templates","MetadataAuthoring.cs")),source);
 }
 File.Copy(Path.Combine(Fixture.Repo,"targets","android-export","templates","MetadataAuthoring.cs"),Path.Combine(folder,"MetadataAuthoring.cs"));
 string core=System.Security.SecurityElement.Escape(typeof(Builder).Assembly.Location)!;
 File.WriteAllText(Path.Combine(folder,"check.csproj"),$"<Project Sdk=\"Microsoft.NET.Sdk\"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup><ItemGroup><Reference Include=\"Confectory.Core\"><HintPath>{core}</HintPath></Reference></ItemGroup></Project>");
 File.WriteAllText(Path.Combine(folder,"Program.cs"),"""
 using System.Text.Json.Nodes;
 string root=Path.Combine(Path.GetTempPath(),"confectory-metadata-"+Guid.NewGuid().ToString("N"));Directory.CreateDirectory(root);
 try {
 File.WriteAllText(Path.Combine(root,"project.cpack"),"project Any.Renamed version \"0.1.0\" { standalone true; registry Evil \"../../missing-do-not-read.cpack\"; element Main function \"main.celem\"; element MainBody implementation \"body.celem\"; }");
 File.WriteAllText(Path.Combine(root,"main.celem"),"function Any.Renamed::Main () -> int { }");
 File.WriteAllText(Path.Combine(root,"body.celem"),"implementation Any.Renamed::MainBody for Any.Renamed::Main () -> int { body common \"main.csbody\"; }");File.WriteAllText(Path.Combine(root,"main.csbody"),"throw new Exception(\"never execute\");");
 string payload=System.Text.Json.JsonSerializer.Serialize(new{project=Path.Combine(root,"project.cpack")});var metadata=JsonNode.Parse(MetadataAuthoring.Call(root,"describe",payload))!;
 if(metadata["units"]!.AsArray().Count!=4)throw new Exception("Owned unit description");
 var inspected=JsonNode.Parse(MetadataAuthoring.Call(root,"inspect","{\"text\":\"object Any.Renamed::Value { }\"}"))!;if(inspected["id"]!.GetValue<string>()!="Any.Renamed::Value")throw new Exception("Inspect identity");
 string created=System.Text.Json.JsonSerializer.Deserialize<string>(MetadataAuthoring.Call(root,"create",System.Text.Json.JsonSerializer.Serialize(new{kind="object",id="Any.Renamed::ProjectInfo"})))!;
 string changed=System.Text.Json.JsonSerializer.Deserialize<string>(MetadataAuthoring.Call(root,"setValue",System.Text.Json.JsonSerializer.Serialize(new{text=created,field="title",value="한글 🧁"})))!;
 if(JsonNode.Parse(MetadataAuthoring.Call(root,"inspect",System.Text.Json.JsonSerializer.Serialize(new{text=changed})))!["values"]!["title"]!.GetValue<string>()!="한글 🧁")throw new Exception("Scalar edit lost");
 string registered=System.Text.Json.JsonSerializer.Deserialize<string>(MetadataAuthoring.Call(root,"register",System.Text.Json.JsonSerializer.Serialize(new{text=File.ReadAllText(Path.Combine(root,"project.cpack")),id="Any.Renamed::ProjectInfo",kind="object",path="elements/ProjectInfo.celem"})))!;
 if(!registered.Contains("elements/ProjectInfo.celem",StringComparison.Ordinal)||!registered.Contains("../../missing-do-not-read.cpack",StringComparison.Ordinal))throw new Exception("Registration changed unrelated metadata");
 bool refused=false;try{MetadataAuthoring.Call(root,"validate",payload);}catch(PlatformNotSupportedException){refused=true;}if(!refused)throw new Exception("Compiler operation accepted");
 refused=false;try{MetadataAuthoring.Call(root,"describe",System.Text.Json.JsonSerializer.Serialize(new{project=Path.Combine(root,"..","outside.cpack")}));}catch{refused=true;}if(!refused)throw new Exception("Owned root escaped");
 Console.WriteLine("Target metadata owned units/inspect/compiler refusal PASS");
 }finally{Directory.Delete(root,true);}
 """);
 var result=Processes.Run(new[]{Environment.GetEnvironmentVariable("CONFECTORY_DOTNET")??"dotnet","run","--project",Path.Combine(folder,"check.csproj"),"-c","Release"},timeoutSeconds:120);True(result.ExitCode==0,result.Stdout+result.Stderr);True(result.Stdout.Contains("Target metadata owned units/inspect/compiler refusal PASS",StringComparison.Ordinal),result.Stdout+result.Stderr);
 }
}
