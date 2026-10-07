using System.Text.Json.Nodes;
using Confectory.Core;
namespace Confectory.Tests;
public sealed class CompilerTransportTests : TestCase
{
 public void test_windows_limit_reference_arguments_spaced_host_unicode_paths_and_cleanup()
 {
  string original=Processes.DotNet(),selected=original,sdkRoot=Path.GetDirectoryName(original)!;
  if(!OperatingSystem.IsWindows()){string spaced=Path.Combine(f.Root,"dotnet host with spaces");Directory.CreateDirectory(spaced);selected=Path.Combine(spaced,"dotnet");File.Copy(original,selected);File.SetUnixFileMode(selected,File.GetUnixFileMode(original));foreach(string folder in new[]{"sdk","packs","shared","host","sdk-manifests"})Directory.CreateSymbolicLink(Path.Combine(spaced,folder),Path.Combine(sdkRoot,folder));sdkRoot=spaced;}
  string reference=Path.Combine(Directory.GetDirectories(Path.Combine(sdkRoot,"packs","Microsoft.NETCore.App.Ref"),"10.*").OrderBy(p=>Version.Parse(Path.GetFileName(p))).Last(),"ref","net10.0","System.Runtime.dll");string work=Path.Combine(f.Root,"한글 compiler inputs with spaces");Directory.CreateDirectory(work);string source=Path.Combine(work,"source with spaces.cs");File.WriteAllText(source,"public static class Probe { public static int Read() => 42; }");string output=Path.Combine(work,"output with spaces");string? saved=Environment.GetEnvironmentVariable("CONFECTORY_DOTNET");Environment.SetEnvironmentVariable("CONFECTORY_DOTNET",selected);
  try{
   JsonObject Compile(string name)=>JsonNode.Parse(Processes.Run([selected,f.ToolPath],new JsonObject{["protocol"]=1,["operation"]="compile-contract",["target"]="portable",["options"]=new JsonObject(),["output"]=output,["name"]=name,["sources"]=new JsonArray(source),["references"]=new JsonArray(Enumerable.Repeat((JsonNode?)JsonValue.Create(reference),600).Select(n=>n!.DeepClone()).ToArray())}.ToJsonString(),timeoutSeconds:120).Stdout)!.AsObject();
   var first=Compile("Probe");True(first["ok"]!.GetValue<bool>(),first.ToJsonString());var metrics=first["compilerTransport"]!;True(metrics["expandedCommandCharacters"]!.GetValue<int>()>32767);True(metrics["launchCommandCharacters"]!.GetValue<int>()<1024);True(metrics["responseRemoved"]!.GetValue<bool>());True(File.Exists(first["artifacts"]!["assembly"]!.GetValue<string>()));
   var parallel=new[]{System.Threading.Tasks.Task.Run(()=>Compile("ConcurrentA")),System.Threading.Tasks.Task.Run(()=>Compile("ConcurrentB"))};System.Threading.Tasks.Task.WaitAll(parallel);True(parallel.All(t=>t.Result["ok"]!.GetValue<bool>()));Equal(0,Directory.GetFiles(output,"*.rsp").Length);File.WriteAllText(source,"deliberately invalid C#");var failure=Compile("Invalid");True(!failure["ok"]!.GetValue<bool>());Equal(0,Directory.GetFiles(output,"*.rsp").Length);Console.WriteLine("COMPILER_TRANSPORT "+metrics.ToJsonString());
  }finally{Environment.SetEnvironmentVariable("CONFECTORY_DOTNET",saved);}
 }
}
