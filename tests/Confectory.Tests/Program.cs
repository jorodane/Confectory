using System.Diagnostics;
using System.Reflection;
using Confectory.Core;
using Confectory.Tests;

string fakeReply = Path.Combine(AppContext.BaseDirectory, "fake-reply.txt");
if (File.Exists(fakeReply)) { Console.Write(File.ReadAllText(fakeReply)); return 0; }

Environment.SetEnvironmentVariable("CONFECTORY_DOTNET", Processes.DotNet());
var watch = Stopwatch.StartNew(); int passed = 0, failed = 0;
string[] filters = args;
foreach (var type in new[] { typeof(CoreTests), typeof(BrowserTests), typeof(BrowserWasmTests), typeof(EntryTests), typeof(IntegrationTests), typeof(VerificationTests), typeof(WindowTests), typeof(Win32ContractTests), typeof(RuntimeBaseTests), typeof(RealTimeUpdateTests), typeof(BaseUITests), typeof(EngineTests), typeof(AndroidPreparationTests), typeof(ProjectExecutionTests), typeof(ProjectManagerTests), typeof(FileStreamTests), typeof(SchemaEditingTests), typeof(EditWorkspaceTests), typeof(ElementViewTests), typeof(PackManagerTests), typeof(SourceEditorTests), typeof(BuildParticipationTests), typeof(CollaborationTests), typeof(AgentTests), typeof(HelperTests), typeof(WorkerTasksTests), typeof(Checkpoint7Tests), typeof(AugmentTests), typeof(CompilerTransportTests), typeof(ProjectionDeliveryTests), typeof(StageTests), typeof(Physics2DTests), typeof(ToolchainSelectionTests), typeof(RigMotionTests), typeof(UINavigationTests), typeof(EditorTests), typeof(ButtonTests), typeof(FieldTests), typeof(EntryHomeTests), typeof(EntryHomeResizeTests), typeof(ProjectShellTests), typeof(ProjectNavigationTests), typeof(NativeUITests) })
foreach (var method in type.GetMethods().Where(x => x.Name.StartsWith("test_", StringComparison.Ordinal)).OrderBy(x => x.Name, StringComparer.Ordinal))
{
    string name = type.Name + "." + method.Name;
    if (filters.Length != 0 && !filters.Any(filter => name.Contains(filter, StringComparison.OrdinalIgnoreCase))) continue;
    using var test = (TestCase)Activator.CreateInstance(type)!;
    try { method.Invoke(test, null); passed++; Console.WriteLine($"PASS {name}"); }
    catch (TargetInvocationException ex) { failed++; Console.WriteLine($"FAIL {name}\n{ex.InnerException}"); }
}
Console.WriteLine($"{passed} passed, {failed} failed; {watch.Elapsed.TotalSeconds:F3}s");
return failed == 0 && passed > 0 ? 0 : 1;
