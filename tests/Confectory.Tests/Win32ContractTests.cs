using Confectory.Core;
namespace Confectory.Tests;
public sealed class Win32ContractTests : TestCase
{
 public void test_native_callback_routing_paint_and_lifetime_contract()
 {
  if(!OperatingSystem.IsLinux())return; // explicit Linux ABI fixture; native Windows user QA remains separate
  string sample=Path.Combine(f.Root,"win32-probe"),pack=Path.Combine(f.Root,"packs","window"),native=Path.Combine(f.Root,"native");
  Fixture.CopyTree(Path.Combine(Fixture.Repo,"tests","native","win32-probe"),sample);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","window"),pack);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","render-input"),Path.Combine(f.Root,"packs","render-input"));Directory.CreateDirectory(native);
  foreach(string name in new[]{"Win32Create","Win32Pump","Win32Draw","Win32Close"})
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
