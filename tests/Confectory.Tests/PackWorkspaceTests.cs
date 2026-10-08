using Confectory.Core;
namespace Confectory.Tests;
public sealed class PackWorkspaceTests : TestCase
{
 public void test_two_contexts_revision_save_reopen_and_locality()
 {
 string sample=Path.Combine(f.Root,"workspace-consumer");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","edit-workspace"),sample);
 foreach(string name in new[]{"file-stream","schema-editing","edit-workspace","save","change-set","pack-workspace"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",name),Path.Combine(f.Root,"packs",name));
 string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/").Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack").Replace("element Main function", "registry Confectory.PackWorkspace \"../packs/pack-workspace/pack.cpack\"; dependency Confectory.PackWorkspace version \"0.1.0\";\nelement Main function"));

 for(int i=0;i<40;i++){string name="ZItem"+i.ToString("D2");f.Add("App","object",name,"object App::"+name+" {}");}f.Sync();

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
 var filtered=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(a,"filter",System.Text.Json.JsonSerializer.Serialize(new{query=id.ToUpperInvariant(),kind="body"})))!;
 if(filtered["total"]!.GetValue<int>()!=1||filtered["unit"]!["id"]!.ToString()!=id||filtered["ownedTotal"]!.GetValue<int>()!=initial["total"]!.GetValue<int>())throw new Exception("Stable ID/kind filter failed");
 var empty=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(a,"filter","{\"query\":\"missing::unit\"}"))!;
 if(empty["total"]!.GetValue<int>()!=0||empty["units"]!.AsArray().Count!=0||empty["unit"]!["id"]!.ToString()!=id)throw new Exception("Empty filter lost selection");
 if(System.Text.Json.Nodes.JsonNode.Parse(calls.Snapshot.Invoke(b))!["query"]!.ToString()!="")throw new Exception("View filter leaked");
 var page=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(a,"page","{\"page\":999}"))!;if(page["page"]!.GetValue<int>()!=0)throw new Exception("Empty page not clamped");
 bool longRejected=false;try{calls.Command.Invoke(a,"filter",System.Text.Json.JsonSerializer.Serialize(new{query=new string('x',257)}));}catch(ArgumentException){longRejected=true;}if(!longRejected)throw new Exception("Unbounded filter accepted");
 calls.Command.Invoke(a,"select","{\"id\":\"App::ZItem00\"}");
 var declared=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(a,"inspect","{}"))!;if(declared["inspection"]!["relations"]!["edges"]!.AsArray().Count!=0||declared["inspectionRevision"]!.GetValue<long>()!=0)throw new Exception("Empty declaration inspection");
 calls.Command.Invoke(a,"edit",System.Text.Json.JsonSerializer.Serialize(new{text="object App::ZItem00 extends Missing::Parent { module Missing::Role; }",expectedRevision=0}));
 var changedInspection=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(a,"inspect","{}"))!;if(changedInspection["inspection"]!["relations"]!["edges"]!.AsArray().Count!=2||changedInspection["inspectionRevision"]!.GetValue<long>()!=1)throw new Exception("Inspection ignored selected draft");
 Select(a);bool bodyRefused=false;try{calls.Command.Invoke(a,"inspect","{}");}catch(InvalidOperationException){bodyRefused=true;}if(!bodyRefused)throw new Exception("Body treated as declaration");
 var objects=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(a,"filter","{\"kind\":\"object\"}"))!;if(objects["total"]!.GetValue<int>()!=40||objects["units"]!.AsArray().Count!=32)throw new Exception("Kind pagination first page");
 var last=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(a,"page","{\"page\":1}"))!;if(last["units"]!.AsArray().Count!=8||last["units"]![0]!["id"]!.ToString()!="App::ZItem32")throw new Exception("Stable filtered page ordering");
 var reset=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(a,"filter","{}"))!;if(reset["total"]!.GetValue<int>()!=initial["total"]!.GetValue<int>()||reset["page"]!.GetValue<int>()!=0)throw new Exception("Filter reset failed");

 string edited=original+"\n// local draft one\n";
 string Edit(string h,long revision,string text)=>calls.Command.Invoke(h,"edit",System.Text.Json.JsonSerializer.Serialize(new{expectedRevision=revision,text}));
 if(System.Text.Json.Nodes.JsonNode.Parse(Edit(a,0,edited))!["conflict"]!.GetValue<bool>())throw new Exception("Unexpected conflict");
 if(!System.Text.Json.Nodes.JsonNode.Parse(Edit(a,0,"stale"))!["conflict"]!.GetValue<bool>())throw new Exception("Stale edit accepted");
 if(System.Text.Json.Nodes.JsonNode.Parse(calls.Snapshot.Invoke(b))!["unit"]!["text"]!.GetValue<string>()!=original)throw new Exception("Contexts leaked");
 string shared=calls.Open.Invoke(project,"alice","one");if(System.Text.Json.Nodes.JsonNode.Parse(Select(shared))!["unit"]!["text"]!.GetValue<string>()!=edited)throw new Exception("Same identity lost live draft");calls.Command.Invoke(a,"filter","{\"query\":\"missing::unit\"}");if(System.Text.Json.Nodes.JsonNode.Parse(calls.Snapshot.Invoke(shared))!["query"]!.ToString()!="")throw new Exception("Same-draft view filter leaked");calls.Command.Invoke(a,"filter","{}");calls.Close.Invoke(shared);calls.Close.Invoke(shared);
 calls.Command.Invoke(a,"select",System.Text.Json.JsonSerializer.Serialize(new{id=initial["units"]![0]!["id"]!.GetValue<string>()}));if(System.Text.Json.Nodes.JsonNode.Parse(Select(a))!["unit"]!["text"]!.GetValue<string>()!=edited)throw new Exception("Selection discarded draft");
 calls.Command.Invoke(a,"save","{}");string owned=System.Text.Json.Nodes.JsonNode.Parse(calls.Snapshot.Invoke(a))!["unit"]!["path"]!.GetValue<string>();if(System.IO.File.ReadAllText(System.IO.Path.Combine(System.IO.Path.GetDirectoryName(project)!,owned))!=original)throw new Exception("Save modified final source");calls.Close.Invoke(a);calls.Close.Invoke(a);
 a=calls.Open.Invoke(project,"alice","one");if(System.Text.Json.Nodes.JsonNode.Parse(Select(a))!["unit"]!["text"]!.GetValue<string>()!=edited)throw new Exception("Draft lost on reopen");
 var sources=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(a,"sources","{}"))!["files"]!.AsArray();if(!System.Linq.Enumerable.Any(sources,x=>x!["kind"]!.GetValue<string>()=="project"))throw new Exception("Manifest missing");
 var review=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(a,"review","{\"target\":\"portable\"}"))!["review"]!;
 if(review["status"]!.ToString()!="ready"||review["path"]!.ToString()!=owned||review["before"]!.ToString()!=original||review["after"]!.ToString()!=edited)throw new Exception("Review omitted owned path or exact source values");
 var reviewFiltered=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(a,"filter","{\"query\":\"missing::unit\"}"))!;if(reviewFiltered["review"]!["token"]!.ToString()!=review["token"]!.ToString()||reviewFiltered["unit"]!["text"]!.ToString()!=edited)throw new Exception("Navigation mutated reviewed draft");calls.Command.Invoke(a,"filter","{}");
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
 File.AppendAllText(Path.Combine(f.Root,"packs","pack-workspace","Command.csbody"),"\n// selected-inspection locality\n");var commandChanged=new Builder(project,"portable").Build();PackRebuilt(commandChanged,new[]{"Confectory.PackWorkspace::CommandBody"});Equal(0,Strings(commandChanged,"statistics","compiledContracts").Length);
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
 var relationships=JsonNode.Parse(MetadataAuthoring.Call(root,"inspect",System.Text.Json.JsonSerializer.Serialize(new{text="module Any.Renamed::Rules extends Missing::Parent { module Missing::Role; include Missing::Child; require Missing::Function (int) -> int; default Missing::Function with Missing::Body; provide Missing::Function with Missing::Explicit; }"})))!["relations"]!;
 if(relationships["scope"]!.ToString()!="declared"||relationships["edges"]!.AsArray().Count!=6||!System.Linq.Enumerable.Any(relationships["edges"]!.AsArray(),e=>e!["role"]!.ToString()=="provide"&&e["target"]!.ToString()=="Missing::Explicit"&&e["function"]!.ToString()=="Missing::Function"))throw new Exception("Target direct relationship contract");
 foreach(var contract in new[]{"() -> void","(string,int[],bool) -> string[]","(long[],double,float[]) -> bool"}){
 var requirement=JsonNode.Parse(MetadataAuthoring.Call(root,"inspect",System.Text.Json.JsonSerializer.Serialize(new{text="module Any.Renamed::Rules { require Missing::Function "+contract+"; }"})))!["relations"]!["edges"]![0]!;
 string named=contract.Replace("string,int[],bool","string arg0,int[] arg1,bool arg2",StringComparison.Ordinal).Replace("long[],double,float[]","long[] arg0,double arg1,float[] arg2",StringComparison.Ordinal);
 var signature=JsonNode.Parse(MetadataAuthoring.Call(root,"inspect",System.Text.Json.JsonSerializer.Serialize(new{text="function Missing::Function "+named+" {}"})))!["signature"];
 if(!JsonNode.DeepEquals(requirement["signature"],signature))throw new Exception("Target required signature format");
 }
 string created=System.Text.Json.JsonSerializer.Deserialize<string>(MetadataAuthoring.Call(root,"create",System.Text.Json.JsonSerializer.Serialize(new{kind="object",id="Any.Renamed::ProjectInfo"})))!;
 string changed=System.Text.Json.JsonSerializer.Deserialize<string>(MetadataAuthoring.Call(root,"setValue",System.Text.Json.JsonSerializer.Serialize(new{text=created,field="title",value="한글 🧁"})))!;
 if(JsonNode.Parse(MetadataAuthoring.Call(root,"inspect",System.Text.Json.JsonSerializer.Serialize(new{text=changed})))!["values"]!["title"]!.GetValue<string>()!="한글 🧁")throw new Exception("Scalar edit lost");
 string registered=System.Text.Json.JsonSerializer.Deserialize<string>(MetadataAuthoring.Call(root,"register",System.Text.Json.JsonSerializer.Serialize(new{text=File.ReadAllText(Path.Combine(root,"project.cpack")),id="Any.Renamed::ProjectInfo",kind="object",path="elements/ProjectInfo.celem"})))!;
 if(!registered.Contains("elements/ProjectInfo.celem",StringComparison.Ordinal)||!registered.Contains("../../missing-do-not-read.cpack",StringComparison.Ordinal))throw new Exception("Registration changed unrelated metadata");
 bool refused=false;try{MetadataAuthoring.Call(root,"validate",payload);}catch(PlatformNotSupportedException){refused=true;}if(!refused)throw new Exception("Compiler operation accepted");
 refused=false;try{MetadataAuthoring.Call(root,"describe",System.Text.Json.JsonSerializer.Serialize(new{project=Path.Combine(root,"..","outside.cpack")}));}catch{refused=true;}if(!refused)throw new Exception("Owned root escaped");
 string locatorManifest="project Any.Renamed version \"0.1.0\" { registry Known \"known.cpack\"; registry Broken \"missing.cpack\"; registry Unused \"must-not-read.cpack\"; element Value object \"not-read.celem\"; }";
 string knownManifest="pack Known version \"0.1.0\" { element Good module \"not-opened.celem\"; }";File.WriteAllText(Path.Combine(root,"known.cpack"),knownManifest);
 string[] requested={"Any.Renamed::Value","Any.Renamed::Absent","Known::Good","Known::Absent","Broken::Thing","Unknown::Thing","bad-id"};
 var located=JsonNode.Parse(MetadataAuthoring.Call(root,"locate",System.Text.Json.JsonSerializer.Serialize(new{project=Path.Combine(root,"project.cpack"),manifest=locatorManifest,ids=requested})))!;
 string Status(string id)=>located["targets"]!.AsArray().Single(x=>x!["id"]!.ToString()==id)!["status"]!.ToString();
 if(Status("Any.Renamed::Value")!="registered"||Status("Any.Renamed::Absent")!="unregistered"||Status("Known::Good")!="registered"||Status("Known::Absent")!="unregistered"||Status("Broken::Thing")!="unavailable"||Status("Unknown::Thing")!="unregistered"||Status("bad-id")!="unavailable")throw new Exception("Locator tri-state confusion");
 int reads=0;RelationLocators.Query(locatorManifest,root,requested,path=>{reads++;if(Path.GetFileName(path)=="known.cpack")return knownManifest;if(Path.GetFileName(path)=="missing.cpack")throw new IOException();throw new Exception("Unrequested namespace opened");});if(reads!=2)throw new Exception("Not scoped/cached to requested manifests");
 var unknown=RelationLocators.Query("broken",root,new[]{"Known::Good"},_=>throw new Exception("Invalid manifest triggered read"));if(unknown["targets"]![0]!["status"]!.ToString()!="unavailable")throw new Exception("Invalid project treated as missing namespace");
 var mismatched=RelationLocators.Query(locatorManifest,root,new[]{"Known::Good"},_=>"pack Other version \"1\" {} ");if(mismatched["targets"]![0]!["status"]!.ToString()!="unavailable")throw new Exception("Mismatched registration accepted");
 string outsideManifest=root+"-external.cpack";try{
 File.WriteAllText(outsideManifest,knownManifest);string externalRegistration="project Any.Renamed version \"1\" { registry Known \"../"+Path.GetFileName(outsideManifest)+"\"; }";
 var scoped=JsonNode.Parse(MetadataAuthoring.Call(root,"locate",System.Text.Json.JsonSerializer.Serialize(new{project=Path.Combine(root,"project.cpack"),manifest=externalRegistration,ids=new[]{"Known::Good"}})))!;
 if(scoped["targets"]![0]!["status"]!.ToString()!="unavailable"||!scoped["targets"]![0]!["namespaceRegistered"]!.GetValue<bool>())throw new Exception("Locator scope broadened outside owned root");
 }finally{File.Delete(outsideManifest);}
 Console.WriteLine("LOCATORS:"+located.ToJsonString());
 Console.WriteLine("RELATIONS:"+relationships.ToJsonString());
 Console.WriteLine("Target metadata owned units/inspect/compiler refusal PASS");
 }finally{Directory.Delete(root,true);}
 """);
 var result=Processes.Run(new[]{Environment.GetEnvironmentVariable("CONFECTORY_DOTNET")??"dotnet","run","--project",Path.Combine(folder,"check.csproj"),"-c","Release"},timeoutSeconds:120);True(result.ExitCode==0,result.Stdout+result.Stderr);True(result.Stdout.Contains("Target metadata owned units/inspect/compiler refusal PASS",StringComparison.Ordinal),result.Stdout+result.Stderr);
 var desktop=Processes.Run(new[]{Processes.DotNet(),Path.Combine(Fixture.Repo,"targets","element-authoring","bin","Release","net10.0","Confectory.ElementAuthoring.dll")},input:System.Text.Json.JsonSerializer.Serialize(new{operation="inspect",text="module Any.Renamed::Rules extends Missing::Parent { module Missing::Role; include Missing::Child; require Missing::Function (int) -> int; default Missing::Function with Missing::Body; provide Missing::Function with Missing::Explicit; }"}),timeoutSeconds:30);
 var expected=System.Text.Json.Nodes.JsonNode.Parse(desktop.Stdout)!;True(expected["ok"]!.GetValue<bool>(),desktop.Stdout);var targetRelations=System.Text.Json.Nodes.JsonNode.Parse(result.Stdout.Split('\n').Single(line=>line.StartsWith("RELATIONS:",StringComparison.Ordinal))[10..]);True(System.Text.Json.Nodes.JsonNode.DeepEquals(expected["result"]!["relations"],targetRelations),"Target relation replies differ");
 File.WriteAllText(Path.Combine(folder,"known.cpack"),"pack Known version \"0.1.0\" { element Good module \"not-opened.celem\"; }");
 var locatedDesktop=Processes.Run(new[]{Processes.DotNet(),Path.Combine(Fixture.Repo,"targets","element-authoring","bin","Release","net10.0","Confectory.ElementAuthoring.dll")},input:System.Text.Json.JsonSerializer.Serialize(new{operation="locate",project=Path.Combine(folder,"project.cpack"),manifest="project Any.Renamed version \"0.1.0\" { registry Known \"known.cpack\"; registry Broken \"missing.cpack\"; registry Unused \"must-not-read.cpack\"; element Value object \"not-read.celem\"; }",ids=new[]{"Any.Renamed::Value","Any.Renamed::Absent","Known::Good","Known::Absent","Broken::Thing","Unknown::Thing","bad-id"}}),timeoutSeconds:30);
 var locatorReply=System.Text.Json.Nodes.JsonNode.Parse(locatedDesktop.Stdout)!;True(locatorReply["ok"]!.GetValue<bool>(),locatedDesktop.Stdout);var targetLocators=System.Text.Json.Nodes.JsonNode.Parse(result.Stdout.Split('\n').Single(line=>line.StartsWith("LOCATORS:",StringComparison.Ordinal))[9..]);True(System.Text.Json.Nodes.JsonNode.DeepEquals(locatorReply["result"],targetLocators),"Locator replies differ");


 }
}
