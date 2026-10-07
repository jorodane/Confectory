using Confectory.Core;
namespace Confectory.Tests;
public sealed class Win32ContractTests : TestCase
{
 public void test_retained_text_services_canvas_abi_and_provider_locality()
 {
  if(!OperatingSystem.IsLinux())return;
  string sample=Path.Combine(f.Root,"text-probe"),pack=Path.Combine(f.Root,"text-services"),window=Path.Combine(f.Root,"window"),native=Path.Combine(f.Root,"native");
  Fixture.CopyTree(Path.Combine(Fixture.Repo,"tests","native","text-services-probe"),sample);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","win32-text-services"),pack);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","window"),window);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","render-input"),Path.Combine(f.Root,"render-input"));Directory.CreateDirectory(native);
  foreach(string name in new[]{"Win32Create","Win32Pump","Win32Draw","Win32Close","Win32AcquireCanvas","Win32ReleaseCanvas"}){string path=Path.Combine(window,name+".csbody");File.WriteAllText(path,System.Text.RegularExpressions.Regex.Replace(File.ReadAllText(path),"if\\(!OperatingSystem.IsWindows\\(\\)\\)throw new PlatformNotSupportedException\\([^;]+;",""));}
  string body=Path.Combine(pack,"Request.csbody");string text=System.Text.RegularExpressions.Regex.Replace(File.ReadAllText(body),"if\\(!OperatingSystem.IsWindows\\(\\)\\)throw new PlatformNotSupportedException\\([^;]+;","");text=text.Replace("System.Runtime.InteropServices.NativeLibrary.Load(\"Msftedit.dll\")","System.Runtime.InteropServices.NativeLibrary.Load("+System.Text.Json.JsonSerializer.Serialize(Path.Combine(native,"libmsftedit.dll.so"))+")");File.WriteAllText(body,text);
  Equal(0,Processes.Run(new[]{"gcc","-shared","-fPIC","-Wall","-Wextra","-Werror",Path.Combine(Fixture.Repo,"tests","native","win32-shim.c"),"-o",Path.Combine(native,"libuser32.dll.so")}).ExitCode);
  Equal(0,Processes.Run(new[]{"gcc","-shared","-fPIC","-Wall","-Wextra","-Werror",Path.Combine(Fixture.Repo,"tests","native","text-services-shim.c"),"-o",Path.Combine(native,"libmsftedit.dll.so")}).ExitCode);
  foreach(string name in new[]{"libkernel32.dll.so","libgdi32.dll.so","libimm32.dll.so","libcomctl32.dll.so","libole32.dll.so"})File.CreateSymbolicLink(Path.Combine(native,name),"libuser32.dll.so");
  string project=Path.Combine(sample,"project.cpack");var built=new Builder(project,"portable").Build();string? previous=Environment.GetEnvironmentVariable("LD_LIBRARY_PATH");
  try{Environment.SetEnvironmentVariable("LD_LIBRARY_PATH",native);Output(built,"TextServices ABI proof PASS; NOT Windows runtime/IME coverage");File.AppendAllText(body,"\n// retained text-services provider locality probe\n");var changed=new Builder(project,"portable").Build();Sequence(new[]{"Confectory.Win32TextServices::RequestBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);Output(changed,"TextServices ABI proof PASS; NOT Windows runtime/IME coverage");}
  finally{Environment.SetEnvironmentVariable("LD_LIBRARY_PATH",previous);}
 }
 public void test_windowless_consumer_owner_cleanup_after_native_failure()
 {
  if(!OperatingSystem.IsLinux())return;
  string sample=Path.Combine(f.Root,"examples","proof"),native=Path.Combine(f.Root,"native");Directory.CreateDirectory(native);
  Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","windowless-browser-proof"),sample);
  foreach(string pack in new[]{"ui-navigation","win32-text-services","ui-order","window-placement","base-ui","runtime-base","window","render-input","edit-workspace","schema-editing","file-stream"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",pack),Path.Combine(f.Root,"packs",pack));
  string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../targets/dotnet/pack.cpack","../../target/pack.cpack"));
  string window=Path.Combine(f.Root,"packs","window");
  foreach(string path in Directory.GetFiles(window,"Win32*.csbody"))File.WriteAllText(path,System.Text.RegularExpressions.Regex.Replace(File.ReadAllText(path),"if\\(!OperatingSystem.IsWindows\\(\\)\\)throw new PlatformNotSupportedException\\([^;]+;",""));
  foreach(string name in new[]{"CreateSurfaces","Close","Pump","SurfaceDimensions","Draw","DrawText"}){string path=Path.Combine(window,name+".csbody");File.WriteAllText(path,File.ReadAllText(path).Replace("OperatingSystem.IsWindows()","IntPtr.Size==8"));}
  string provider=Path.Combine(f.Root,"packs","win32-text-services","Request.csbody");string providerText=System.Text.RegularExpressions.Regex.Replace(File.ReadAllText(provider),"if\\(!OperatingSystem.IsWindows\\(\\)\\)throw new PlatformNotSupportedException\\([^;]+;","");File.WriteAllText(provider,providerText.Replace("System.Runtime.InteropServices.NativeLibrary.Load(\"Msftedit.dll\")","System.Runtime.InteropServices.NativeLibrary.Load("+System.Text.Json.JsonSerializer.Serialize(Path.Combine(native,"libmsftedit.dll.so"))+")"));
  Equal(0,Processes.Run(new[]{"gcc","-shared","-fPIC","-Wall","-Wextra","-Werror",Path.Combine(Fixture.Repo,"tests","native","win32-shim.c"),"-o",Path.Combine(native,"libuser32.dll.so")}).ExitCode);
  Equal(0,Processes.Run(new[]{"gcc","-shared","-fPIC","-Wall","-Wextra","-Werror",Path.Combine(Fixture.Repo,"tests","native","text-services-shim.c"),"-o",Path.Combine(native,"libmsftedit.dll.so")}).ExitCode);
  foreach(string name in new[]{"libkernel32.dll.so","libgdi32.dll.so","libimm32.dll.so","libcomctl32.dll.so","libole32.dll.so"})File.CreateSymbolicLink(Path.Combine(native,name),"libuser32.dll.so");
  string body=Path.Combine(sample,"Main.csbody"),text=File.ReadAllText(body);text=text[..text.LastIndexOf("if(!OperatingSystem.IsWindows())",StringComparison.Ordinal)];
  text="""
[System.Runtime.InteropServices.DllImport("msftedit.dll")]static extern void TextProofFail(int stage);
[System.Runtime.InteropServices.DllImport("msftedit.dll")]static extern int TextProofCounter(int index);
[System.Runtime.InteropServices.DllImport("user32.dll")]static extern int TextProofOleCount();
[System.Runtime.InteropServices.DllImport("user32.dll")]static extern int TextProofSubclasses();
[System.Runtime.InteropServices.DllImport("user32.dll")]static extern int TextProofTimerCount();
[System.Runtime.InteropServices.DllImport("user32.dll")]static extern int SimCounter(int index);
[System.Runtime.InteropServices.DllImport("user32.dll")]static extern void SimPost(long window,uint message,long wparam,long lparam);
"""+text;
  text=text.Replace("Console.CancelKeyPress+=interrupt;while", """
Console.CancelKeyPress+=interrupt;
foreach(string id in System.Linq.Enumerable.Take(calls.WorkspaceList.Invoke(workspace),2))Open(id);
if(editors.Count!=2)throw new Exception("Need two real consumer Views");
foreach(var data in editors.Values){calls.TextRequest.Invoke(data[1],"focus","{\"focus\":true}",0);calls.TextRequest.Invoke(data[1],"send","{\"message\":1280}",0);}
AppDomain.CurrentDomain.SetData("OwnerProofModels",System.Linq.Enumerable.ToArray(models.Values));AppDomain.CurrentDomain.SetData("OwnerProofWorkspace",workspace);AppDomain.CurrentDomain.SetData("OwnerProofOwner",owner);
long Point(int x,int y)=>unchecked((ushort)(short)x)|((long)unchecked((ushort)(short)y)<<16);
SimPost(surfaces[1],0x201,0,Point(370,185));for(int motion=0;motion<240;motion++)SimPost(surfaces[1],0x200,0,Point(370-motion,185-motion/3));SimPost(surfaces[1],0x100,65,0);SimPost(surfaces[1],0x101,65,0);SimPost(surfaces[1],0x200,0,Point(80,80));SimPost(surfaces[1],0x202,0,Point(80,80));
SimPost(surfaces[1],0x201,0,Point(80,80));SimPost(surfaces[1],0x200,0,Point(-20000,-20000));SimPost(surfaces[1],0x202,0,Point(-20000,-20000));proofComposes=0;proofUpdates=0;proofComposeTicks=0;proofUpdateTicks=0;while
""");
  text=text.Replace(" double now=watch.Elapsed.TotalSeconds;", """
var dragged=System.Linq.Enumerable.Last(editors);var checkedFrame=J(calls.OrderCompose.Invoke(state,new[]{0,0,width,height}));var draggedRow=System.Linq.Enumerable.First(checkedFrame["windows"]!.AsArray(),r=>r!["id"]!.GetValue<int>()==dragged.Key)!;int[] draggedBounds=System.Text.Json.JsonSerializer.Deserialize<int[]>(draggedRow["bounds"]!.ToJsonString())!;
if(draggedBounds[0]!=0||draggedBounds[1]!=0||draggedBounds[2]!=560||draggedBounds[3]!=430||draggedRow["focus"]!.GetValue<int>()!=10||!J(calls.TextRequest.Invoke(dragged.Value[1],"model-snapshot","{}",0))["focus"]!.GetValue<bool>())throw new Exception("Actual consumer header drag lost reachable bounds/size/independent native input focus");
long proofInputEnd=System.Diagnostics.Stopwatch.GetTimestamp();if(!dragPresentationPending)throw new Exception("Drag dirty intent lost on mouse release");double now=last+.001;
""");
  text=text.Replace("last=now;dragPresentationPending=false;", """
last=now;dragPresentationPending=false;
Console.WriteLine("DRAG_BENCH "+System.Text.Json.JsonSerializer.Serialize(new{events=events.Length/6,composes=proofComposes,updates=proofUpdates,inputMs=(proofInputEnd-proofInputBegin)*1000d/System.Diagnostics.Stopwatch.Frequency,composeMs=proofComposeTicks*1000d/System.Diagnostics.Stopwatch.Frequency,updateMs=proofUpdateTicks*1000d/System.Diagnostics.Stopwatch.Frequency,renderMs=(renderEnd-renderBegin)*1000d/System.Diagnostics.Stopwatch.Frequency}));
if(proofComposes>8||proofUpdates!=244||events.Length/6!=246||TextProofCounter(6)<1||renderReason!="drag")throw new Exception("Drag optimization dropped model moves/key input, rebuilt every intermediate scene or failed immediate dirty submission");
AppDomain.CurrentDomain.SetData("OwnerProofDragChecked",true);TextProofFail(5);stop=true;
""");
  text=text.Replace(" if(timing&&(now-lastTiming", "if(!stop)throw new Exception(\"Dirty drag waited for fixed idle interval\"); if(timing&&(now-lastTiming");
  text=text.Replace("calls.OrderCompose.Invoke(","ProofCompose(").Replace("calls.OrderUpdate.Invoke(","ProofUpdate(").Replace("var events=calls.Pump.Invoke(surfaces);","var events=calls.Pump.Invoke(surfaces);long proofInputBegin=System.Diagnostics.Stopwatch.GetTimestamp();");
  text=text.Replace("string state=", """
int proofComposes=0,proofUpdates=0;long proofComposeTicks=0,proofUpdateTicks=0;
string ProofCompose(string value,int[] viewport){long begin=System.Diagnostics.Stopwatch.GetTimestamp();try{proofComposes++;return calls.OrderCompose.Invoke(value,viewport);}finally{proofComposeTicks+=System.Diagnostics.Stopwatch.GetTimestamp()-begin;}}
string ProofUpdate(string value,string op,string payload){long begin=System.Diagnostics.Stopwatch.GetTimestamp();try{proofUpdates++;return calls.OrderUpdate.Invoke(value,op,payload);}finally{proofUpdateTicks+=System.Diagnostics.Stopwatch.GetTimestamp()-begin;}}
string state=
""");
  text+="""
bool failure=false;try{RunWindowless();}catch(AggregateException){failure=true;}finally{TextProofFail(0);}
if(!failure||AppDomain.CurrentDomain.GetData("OwnerProofDragChecked") is not true||TextProofCounter(0)!=2||TextProofCounter(1)!=2||TextProofCounter(13)!=2||TextProofOleCount()!=0||TextProofSubclasses()!=0||TextProofTimerCount()!=0||SimCounter(13)!=1)throw new Exception("Actual consumer finally skipped native host/OLE/input/surface cleanup after native focus failure");
foreach(string buffer in (string[])AppDomain.CurrentDomain.GetData("OwnerProofModels")!){bool closed=false;try{calls.TextSnapshot.Invoke(buffer);}catch(ObjectDisposedException){closed=true;}if(!closed)throw new Exception("Model was not closed");}
bool workspaceClosed=false;try{calls.WorkspaceList.Invoke((string)AppDomain.CurrentDomain.GetData("OwnerProofWorkspace")!);}catch(ObjectDisposedException){workspaceClosed=true;}if(!workspaceClosed)throw new Exception("Workspace was not closed");
bool ownerClosed=false;try{calls.FixtureInstance.Invoke((string[])AppDomain.CurrentDomain.GetData("OwnerProofOwner")!,"late");}catch(InvalidOperationException){ownerClosed=true;}if(!ownerClosed)throw new Exception("RuntimeBase Owner was not closed");
Console.WriteLine("Windowless consumer owner cleanup ABI PASS; NOT Windows runtime");return 0;
""";
  File.WriteAllText(body,text);string declaration=Path.Combine(sample,"Main.celem");File.WriteAllText(declaration,File.ReadAllText(declaration).Replace("function Example.WindowlessBrowserProof::Main () -> int {","function Example.WindowlessBrowserProof::Main () -> int { provide Confectory.RuntimeBase::CreateInstance with Confectory.RuntimeBase::CreateInstanceBody;"));string imports=Path.Combine(sample,"MainBody.celem");File.WriteAllText(imports,File.ReadAllText(imports).Replace("body common", "import Confectory.RuntimeBase::CreateInstance as FixtureInstance (string[], string) -> int; body common"));
  var built=new Builder(project,"windows").Build();var values=new Dictionary<string,string?>{{"LD_LIBRARY_PATH",native},{"CONFECTORY_WINDOWLESS_EDIT","1"},{"CONFECTORY_BROWSER_TIMING","1"},{"CONFECTORY_BROWSER_PROJECT",f.Project},{"CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets","element-authoring","bin","Release","net8.0","Confectory.ElementAuthoring.dll")},{"CONFECTORY_DOTNET",Environment.GetEnvironmentVariable("CONFECTORY_DOTNET")??"dotnet"}};var previous=values.ToDictionary(p=>p.Key,p=>Environment.GetEnvironmentVariable(p.Key));
  try{foreach(var pair in values)Environment.SetEnvironmentVariable(pair.Key,pair.Value);var run=Processes.Run(Strings(built,"run"),timeoutSeconds:120);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Windowless consumer owner cleanup ABI PASS; NOT Windows runtime"));True(run.Stdout.Contains("BROWSER_TIMING "),"Opt-in timing diagnostics must execute");var diagnostic=System.Text.Json.Nodes.JsonNode.Parse(run.Stdout.Split('\n').Single(x=>x.StartsWith("BROWSER_TIMING ",StringComparison.Ordinal))["BROWSER_TIMING ".Length..])!;Equal(242L,diagnostic["dragMoves"]!.GetValue<long>());Equal(246L,diagnostic["events"]!.GetValue<long>());Equal(1L,diagnostic["renders"]!.GetValue<long>());True(diagnostic["frequency"]!.GetValue<long>()>0&&diagnostic["pumpEnd"]!.GetValue<long>()>=diagnostic["pumpBegin"]!.GetValue<long>(),"Monotonic diagnostic timestamps");foreach(string line in run.Stdout.Split('\n').Where(x=>x.StartsWith("DRAG_BENCH ",StringComparison.Ordinal)||x.StartsWith("BROWSER_TIMING ",StringComparison.Ordinal)))Console.WriteLine(line);}finally{foreach(var pair in previous)Environment.SetEnvironmentVariable(pair.Key,pair.Value);}
  File.AppendAllText(body,"\n// drag presentation consumer locality probe\n");var local=new Builder(project,"windows").Build();Sequence(new[]{"Example.WindowlessBrowserProof::MainBody"},Strings(local,"statistics","compiledImplementations"));Equal(0,Strings(local,"statistics","compiledContracts").Length);
 }
 public void test_native_callback_routing_paint_and_lifetime_contract()
 {
  if(!OperatingSystem.IsLinux())return; // explicit Linux ABI fixture; native Windows user QA remains separate
  string sample=Path.Combine(f.Root,"win32-probe"),pack=Path.Combine(f.Root,"packs","window"),native=Path.Combine(f.Root,"native");
  Fixture.CopyTree(Path.Combine(Fixture.Repo,"tests","native","win32-probe"),sample);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","window"),pack);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","render-input"),Path.Combine(f.Root,"packs","render-input"));Directory.CreateDirectory(native);
  foreach(string name in new[]{"Win32Create","Win32Pump","Win32Draw","Win32Close","Win32MeasureText","Win32DrawText","Win32AcquireCanvas","Win32ReleaseCanvas"})
  {
   string path=Path.Combine(pack,name+".csbody");string text=File.ReadAllText(path);text=System.Text.RegularExpressions.Regex.Replace(text,"if\\(!OperatingSystem.IsWindows\\(\\)\\)throw new PlatformNotSupportedException\\([^;]+;","");File.WriteAllText(path,text);
  }
  string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../../packs/","../packs/",StringComparison.Ordinal).Replace("../../../targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));
  var compile=Processes.Run(["gcc","-shared","-fPIC","-Wall","-Wextra","-Werror",Path.Combine(Fixture.Repo,"tests","native","win32-shim.c"),"-o",Path.Combine(native,"libuser32.dll.so")]);Equal(0,compile.ExitCode);
  File.CreateSymbolicLink(Path.Combine(native,"libgdi32.dll.so"),"libuser32.dll.so");File.CreateSymbolicLink(Path.Combine(native,"libkernel32.dll.so"),"libuser32.dll.so");
  var first=new Builder(project,"portable").Build();string? previous=Environment.GetEnvironmentVariable("LD_LIBRARY_PATH");
  try{Environment.SetEnvironmentVariable("LD_LIBRARY_PATH",native);Output(first,"Win32 ABI/shim contract PASS; NOT Windows runtime coverage");}
  finally{Environment.SetEnvironmentVariable("LD_LIBRARY_PATH",previous);}
  File.AppendAllText(Path.Combine(pack,"Win32Draw.csbody"),"\n// native provider locality\n");var changed=new Builder(project,"portable").Build();Sequence(new[]{"Confectory.Window::Win32DrawBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
 }
}
