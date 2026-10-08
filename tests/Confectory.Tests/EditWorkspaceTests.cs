using Confectory.Core;
namespace Confectory.Tests;
public sealed class EditWorkspaceTests : TestCase
{
 public void test_shared_drafts_save_restore_preview_selective_confirm_conflict_and_locality()
 {
  string sample=Path.Combine(f.Root,"draft-sample");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","edit-workspace"),sample);
  foreach(string name in new[]{"file-stream","schema-editing","edit-workspace","save","change-set"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",name),Path.Combine(f.Root,"packs",name));
  string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/",StringComparison.Ordinal).Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));
  string? host=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST"),selected=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT");
  try
  {
   Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets","element-authoring","bin","Release","net10.0","Confectory.ElementAuthoring.dll"));Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",f.Project);
   var built=new Builder(project,"portable").Build();var result=Processes.Run(Strings(built,"run"),timeoutSeconds:240);True(result.ExitCode==0,result.Stderr+result.Stdout);True(result.Stdout.Contains("EditWorkspace Save/restore selective Confirm/preview/conflict PASS",StringComparison.Ordinal),result.Stderr);
   foreach(var (pack,body,ns) in new[]{("edit-workspace","Read","Confectory.EditWorkspace"),("edit-workspace","Status","Confectory.EditWorkspace"),("edit-workspace","DiscoverBodies","Confectory.EditWorkspace"),("save","Write","Confectory.Save"),("change-set","Review","Confectory.ChangeSet"),("change-set","ConfirmReviewed","Confectory.ChangeSet")})
   {
    File.AppendAllText(Path.Combine(f.Root,"packs",pack,body+".csbody"),"\n// provider locality check\n");var changed=new Builder(project,"portable").Build();PackRebuilt(changed, new[]{ns+"::"+body+"Body"});Equal(0,Strings(changed,"statistics","compiledContracts").Length);
   }
   var windows=new Builder(project,"windows").Build();True(Strings(windows,"run").Length>1);
   File.WriteAllText(Path.Combine(sample,"main.csbody"),"""
   if(calls.FileStreamCapabilities.Invoke()[0]!="android-app-private-files")throw new Exception("Android storage scope");
   bool unavailable=false;try{calls.SchemaEditingInspect.Invoke("object App::Probe { }");}catch(PlatformNotSupportedException){unavailable=true;}
   if(!unavailable)throw new Exception("Do not substitute desktop process authoring for native Android capability");
   Console.WriteLine("Android storage/authoring capability managed probe PASS; native authoring unavailable");return 0;
   """);
   var android=new Builder(project,"android").Build();Output(android,"Android storage/authoring capability managed probe PASS; native authoring unavailable");
   var catalog=System.Text.Json.Nodes.JsonNode.Parse(File.ReadAllText(Text(android,"publicCatalog")))!;Equal("android",catalog["implementations"]!.AsArray().Single(x=>x!["id"]!.GetValue<string>()=="Confectory.SchemaEditing::CallBody")!["bodySelection"]!.GetValue<string>());
  }
  finally{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",selected);}
 }
}
