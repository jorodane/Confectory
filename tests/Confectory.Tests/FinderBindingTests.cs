using Confectory.Core;
namespace Confectory.Tests;
public sealed class FinderBindingTests : TestCase
{
 public void test_editor_entries_resolve_bounded_body_read_and_original_source_providers()
 {
  foreach(string name in new[]{"Main","Verify","VerifyShell"})
  {
   var stats=new BuildStatistics();var registry=new Registry(Path.Combine(Fixture.Repo,"examples","editor-home","project.cpack"),new Documents(Path.Combine(f.Root,"cache-"+name),stats),stats);string entry="Confectory.EditorHome::"+name;registry.Project.Entry=entry;var plan=new Planner(registry,"linux").Plan();
   foreach(var pair in new[]{("Confectory.EditWorkspace::ReadBoundedBody","Confectory.EditWorkspace::ReadBoundedBodyBody"),("Confectory.FileStream::BoundedSnapshot","Confectory.FileStream::BoundedSnapshotBody"),("Confectory.EditWorkspace::Read","Confectory.EditWorkspace::ReadBody"),("Confectory.EditWorkspace::History","Confectory.EditWorkspace::HistoryBody")})
    Equal(pair.Item2,plan.Bindings[new BindingKey(entry,pair.Item1)].Implementation);
  }
 }
}
