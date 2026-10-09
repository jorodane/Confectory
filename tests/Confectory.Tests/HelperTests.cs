using Confectory.Core;
namespace Confectory.Tests;
public sealed class HelperTests : TestCase
{
 public void test_persistent_memory_templates_owner_refs_conflict_and_optional_agent_locality()
 {
  string sample=Path.Combine(f.Root,"helper-sample");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","helper"),sample);foreach(string pack in new[]{"helper","agent","file-stream"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",pack),Path.Combine(f.Root,"packs",pack));string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/",StringComparison.Ordinal).Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));File.WriteAllText(Path.Combine(f.Root,"packs","agent","Start.csbody"),"unselected invalid Agent implementation");var built=new Builder(project,"portable").Build();True(!Strings(built,"includedPacks").Contains("Confectory.Agent"));Output(built,"Helper persistent private memory/immutable template/owner refs/storage conflict PASS");
  File.AppendAllText(Path.Combine(f.Root,"packs","helper","Remember.csbody"),"\n// selected memory wrapper locality\n");var changed=new Builder(project,"portable").Build();PackRebuilt(changed, new[]{"Confectory.Helper::RememberBody"});Equal(0,Strings(changed,"statistics","compiledContracts").Length);File.AppendAllText(Path.Combine(f.Root,"packs","helper","Talk.csbody"),"\n// unselected Helper conversation boundary\n");var excluded=new Builder(project,"portable").Build();Equal(0,Strings(excluded,"statistics","compiledImplementations").Length);
 }
 public void test_explicit_membership_and_project_memory_legacy_quarantine()
 {
  string sample=Path.Combine(f.Root,"scoped-helper");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","helper"),sample);
  foreach(string pack in new[]{"helper","agent","file-stream"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",pack),Path.Combine(f.Root,"packs",pack));
  string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/",StringComparison.Ordinal).Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));
  string body=Path.Combine(sample,"MainBody.celem");string text=File.ReadAllText(body);int end=text.IndexOf("body common",StringComparison.Ordinal);
  text=text.Insert(end,"import Confectory.Helper::ProjectContext as Context (string, string, string, string, bool) -> string;\nimport Confectory.Helper::RememberScoped as Scoped (string, string, string, string, string, string, string) -> void;\nimport Confectory.Helper::Membership as Membership (string, string, string, string, string) -> void;\nimport Confectory.Helper::List as List (string, string) -> string;\n");File.WriteAllText(body,text);
  File.WriteAllText(Path.Combine(sample,"MainBody.csbody"),"""
  string folder=System.IO.Path.Combine(System.IO.Path.GetTempPath(),"confectory-scoped-helper-"+Guid.NewGuid().ToString("N"));System.IO.Directory.CreateDirectory(folder);string store=calls.HelperOpen.Invoke(folder);
  void Check(bool condition,string message){if(!condition)throw new Exception(message);}
  bool Denied(Action action){try{action();return false;}catch(InvalidOperationException){return true;}catch(UnauthorizedAccessException){return true;}catch(ArgumentException){return true;}}
  try{
   calls.HelperRecruit.Invoke(store,"owner","{\"helper\":\"chief\",\"owner\":\"owner\",\"personality\":\"calm\",\"speciality\":\"development\",\"legacyNotes\":\"private template field\"}");calls.HelperRemember.Invoke(store,"chief","owner","legacy","unclassified private fact");
   Check(Denied(()=>calls.Context.Invoke(store,"chief","owner","project-A",true)),"legacy membership cannot be guessed");
   calls.Membership.Invoke(store,"chief","owner","global","");
   calls.Scoped.Invoke(store,"chief","owner","common","common","","approved common fact");calls.Scoped.Invoke(store,"chief","owner","A","project","project-A","only A");calls.Scoped.Invoke(store,"chief","owner","B","project","project-B","only B");
   string a=calls.Context.Invoke(store,"chief","owner","project-A",false);Check(a.Contains("only A")&&!a.Contains("only B")&&!a.Contains("approved common fact")&&!a.Contains("unclassified private fact"),"A without common permission");
   a=calls.Context.Invoke(store,"chief","owner","project-A",true);Check(a.Contains("only A")&&a.Contains("approved common fact")&&!a.Contains("only B")&&!a.Contains("unclassified private fact"),"A plus allowed common only");Check(!a.Contains("private template field"),"project context excludes unknown private template fields");
   string b=calls.Context.Invoke(store,"chief","owner","project-B",true);Check(b.Contains("only B")&&!b.Contains("only A")&&!b.Contains("unclassified private fact"),"B isolation");
   Check(!calls.Context.Invoke(store,"chief","owner","",true).Contains("only A"),"global conversation does not gather project memory");
   Check(Denied(()=>calls.Scoped.Invoke(store,"chief","owner","legacy","common","","unclassified private fact")),"legacy memory cannot be silently reclassified");
   Check(Denied(()=>calls.Context.Invoke(store,"chief","other","project-A",true)),"private owner boundary");
   calls.Membership.Invoke(store,"chief","owner","project","project-A");Check(Denied(()=>calls.Context.Invoke(store,"chief","owner","project-B",true)),"project membership is separate from memory scope");
   string profile=calls.List.Invoke(store,"owner");Check(profile.Contains("project-A")&&!profile.Contains("only A")&&!profile.Contains("unclassified private fact"),"profile list excludes private memory");
   calls.HelperClose.Invoke(store);store=calls.HelperOpen.Invoke(folder);Check(calls.Context.Invoke(store,"chief","owner","project-A",true).Contains("only A"),"scoped memory persists");
   string path=System.IO.Path.Combine(folder,"helpers.json");calls.FileStreamWriteAtomic.Invoke(path,calls.FileStreamSnapshot.Invoke(path)[1]+" ");Check(Denied(()=>calls.Scoped.Invoke(store,"chief","owner","new","project","project-A","not committed")),"CAS failure retains scoped memory");
   Check(!calls.HelperInspect.Invoke(store,"chief","owner").Contains("not committed"),"failed scoped write is not applied");
   Console.WriteLine("Scoped Helper membership/common/project memory/legacy quarantine PASS");return 0;
  }finally{calls.HelperClose.Invoke(store);System.IO.Directory.Delete(folder,true);}
  """);
  var built=new Builder(project,"portable").Build();True(!Strings(built,"includedPacks").Contains("Confectory.Agent"));Output(built,"Scoped Helper membership/common/project memory/legacy quarantine PASS");
  File.AppendAllText(Path.Combine(f.Root,"packs","helper","ProjectContext.csbody"),"\n// scoped context owning provider locality\n");var changed=new Builder(project,"portable").Build();PackRebuilt(changed,new[]{"Confectory.Helper::ProjectContextBody"});Equal(0,Strings(changed,"statistics","compiledContracts").Length);
 }
}
