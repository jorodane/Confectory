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
  foreach(string pack in new[]{"ui-navigation","win32-text-services","ui-order","base-ui","runtime-base","window","render-input","edit-workspace","schema-editing","file-stream"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",pack),Path.Combine(f.Root,"packs",pack));
  string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../targets/dotnet/pack.cpack","../../target/pack.cpack"));
  string window=Path.Combine(f.Root,"packs","window");
  foreach(string path in Directory.GetFiles(window,"Win32*.csbody"))File.WriteAllText(path,System.Text.RegularExpressions.Regex.Replace(File.ReadAllText(path),"if\\(!OperatingSystem.IsWindows\\(\\)\\)throw new PlatformNotSupportedException\\([^;]+;",""));
  foreach(string name in new[]{"CreateSurfaces","Close"}){string path=Path.Combine(window,name+".csbody");File.WriteAllText(path,File.ReadAllText(path).Replace("OperatingSystem.IsWindows()","IntPtr.Size==8"));}
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
"""+text;
  text=text.Replace("Console.CancelKeyPress+=interrupt;while", """
Console.CancelKeyPress+=interrupt;
foreach(string id in System.Linq.Enumerable.Take(calls.WorkspaceList.Invoke(workspace),2))Open(id);
if(editors.Count!=2)throw new Exception("Need two real consumer Views");
foreach(var data in editors.Values){calls.TextRequest.Invoke(data[1],"focus","{\"focus\":true}",0);calls.TextRequest.Invoke(data[1],"send","{\"message\":1280}",0);}
AppDomain.CurrentDomain.SetData("OwnerProofModels",System.Linq.Enumerable.ToArray(models.Values));AppDomain.CurrentDomain.SetData("OwnerProofWorkspace",workspace);AppDomain.CurrentDomain.SetData("OwnerProofOwner",owner);
TextProofFail(5);stop=true;while
""");
  text+="""
bool failure=false;try{RunWindowless();}catch(AggregateException){failure=true;}finally{TextProofFail(0);}
if(!failure||TextProofCounter(0)!=2||TextProofCounter(1)!=2||TextProofCounter(13)!=2||TextProofOleCount()!=0||TextProofSubclasses()!=0||TextProofTimerCount()!=0||SimCounter(13)!=1)throw new Exception("Actual consumer finally skipped native host/OLE/input/surface cleanup after native focus failure");
foreach(string buffer in (string[])AppDomain.CurrentDomain.GetData("OwnerProofModels")!){bool closed=false;try{calls.TextSnapshot.Invoke(buffer);}catch(ObjectDisposedException){closed=true;}if(!closed)throw new Exception("Model was not closed");}
bool workspaceClosed=false;try{calls.WorkspaceList.Invoke((string)AppDomain.CurrentDomain.GetData("OwnerProofWorkspace")!);}catch(ObjectDisposedException){workspaceClosed=true;}if(!workspaceClosed)throw new Exception("Workspace was not closed");
bool ownerClosed=false;try{calls.FixtureInstance.Invoke((string[])AppDomain.CurrentDomain.GetData("OwnerProofOwner")!,"late");}catch(InvalidOperationException){ownerClosed=true;}if(!ownerClosed)throw new Exception("RuntimeBase Owner was not closed");
Console.WriteLine("Windowless consumer owner cleanup ABI PASS; NOT Windows runtime");return 0;
""";
  File.WriteAllText(body,text);string declaration=Path.Combine(sample,"Main.celem");File.WriteAllText(declaration,File.ReadAllText(declaration).Replace("function Example.WindowlessBrowserProof::Main () -> int {","function Example.WindowlessBrowserProof::Main () -> int { provide Confectory.RuntimeBase::CreateInstance with Confectory.RuntimeBase::CreateInstanceBody;"));string imports=Path.Combine(sample,"MainBody.celem");File.WriteAllText(imports,File.ReadAllText(imports).Replace("body common", "import Confectory.RuntimeBase::CreateInstance as FixtureInstance (string[], string) -> int; body common"));
  var built=new Builder(project,"windows").Build();var values=new Dictionary<string,string?>{{"LD_LIBRARY_PATH",native},{"CONFECTORY_WINDOWLESS_EDIT","1"},{"CONFECTORY_BROWSER_PROJECT",f.Project},{"CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets","element-authoring","bin","Release","net8.0","Confectory.ElementAuthoring.dll")},{"CONFECTORY_DOTNET",Environment.GetEnvironmentVariable("CONFECTORY_DOTNET")??"dotnet"}};var previous=values.ToDictionary(p=>p.Key,p=>Environment.GetEnvironmentVariable(p.Key));
  try{foreach(var pair in values)Environment.SetEnvironmentVariable(pair.Key,pair.Value);Output(built,"Windowless consumer owner cleanup ABI PASS; NOT Windows runtime");}finally{foreach(var pair in previous)Environment.SetEnvironmentVariable(pair.Key,pair.Value);}
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
