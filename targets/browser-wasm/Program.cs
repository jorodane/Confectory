using System.Diagnostics;
using System.Security.Cryptography;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Security;
using Confectory.Core;
try {
 var request=JsonNode.Parse(Console.In.ReadToEnd())!.AsObject();
 string compiler=OwnedOption(request,"compiler"),assets=OwnedOption(request,"assetRoot");
 string metadata=PackPaths.Owned(AppContext.BaseDirectory,"Confectory.Core.dll");
 string dotnet=Processes.DotNet(),sdkRoot=Path.GetDirectoryName(new FileInfo(dotnet).ResolveLinkTarget(true)?.FullName??dotnet)!;
 string workloadRoot=Path.Combine(sdkRoot,"packs","Microsoft.NET.Runtime.WebAssembly.Sdk");
 if(!Directory.Exists(workloadRoot))throw new IOException("Install the approved .NET 10 wasm-tools workload before browser builds");
 string operation=request["operation"]!.GetValue<string>();
 if(operation!="link"){
  var delegated=Invoke(dotnet,new[]{compiler},request.ToJsonString());var result=JsonNode.Parse(delegated.Output)!.AsObject();
  if(operation=="fingerprint"){
   var hashes=OwnedFiles(assets).Order(StringComparer.Ordinal).Select(Hash).Concat(OwnedFiles(Path.Combine(AppContext.BaseDirectory,"templates")).Order(StringComparer.Ordinal).Select(Hash));
   result["fingerprint"]="independent-browser-wasm-v1:"+Hash(compiler)+":"+Hash(metadata)+":"+string.Join(":",Directory.GetDirectories(workloadRoot).Select(Path.GetFileName))+":"+string.Join(":",hashes)+":"+result["fingerprint"];
   result["capabilities"]=JsonSerializer.SerializeToNode(new{runtime="browser-wasm",backendRequired=false,staticOutput=true,nativeFilesystem=false,dynamicCompilation=false});
  }
  Console.WriteLine(result.ToJsonString());return delegated.Exit;
 }
 string output=Path.GetFullPath(request["output"]!.GetValue<string>()),project=Path.Combine(output,"wasm-project");Directory.CreateDirectory(project);
 var references=request["references"]!.AsArray().Select(x=>x!.GetValue<string>()).Append(metadata).Distinct(StringComparer.Ordinal).ToArray();
 string items=string.Join("\n",references.Select(path=>$"<Reference Include=\"{Escape(Path.GetFileNameWithoutExtension(path))}\"><HintPath>{Escape(path)}</HintPath></Reference>"));
 foreach(var item in request["sources"]!.AsArray())File.Copy(item!.GetValue<string>(),Path.Combine(project,Path.GetFileName(item.GetValue<string>())));
 File.Copy(PackPaths.Owned(AppContext.BaseDirectory,"templates/Bridge.cs"),Path.Combine(project,"Bridge.cs"));
 File.Copy(PackPaths.Owned(AppContext.BaseDirectory,"templates/MetadataAuthoring.cs"),Path.Combine(project,"MetadataAuthoring.cs"));

 foreach(string file in OwnedFiles(assets))File.Copy(file,Path.Combine(project,Path.GetFileName(file)));
 string resources=string.Join("\n",request["resources"]!.AsArray().Select(item=>$"<EmbeddedResource Include=\"{Escape(item!["path"]!.GetValue<string>())}\"><LogicalName>{Escape(item["name"]!.GetValue<string>())}</LogicalName></EmbeddedResource>"));
 File.WriteAllText(Path.Combine(project,"App.csproj"),$"""
 <Project Sdk="Microsoft.NET.Sdk.WebAssembly">
 <PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>Exe</OutputType><AssemblyName>Confectory.Browser.App</AssemblyName><RuntimeIdentifier>browser-wasm</RuntimeIdentifier><AllowUnsafeBlocks>true</AllowUnsafeBlocks><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable><LangVersion>12</LangVersion><PublishTrimmed>false</PublishTrimmed><WasmMainJSPath>app.js</WasmMainJSPath><WasmBuildNative>true</WasmBuildNative><RunAOTCompilation>false</RunAOTCompilation><WasmEnableWebcil>false</WasmEnableWebcil><WasmStripILAfterAOT>false</WasmStripILAfterAOT><WasmGenerateAppBundle>true</WasmGenerateAppBundle><WasmEnableThreads>false</WasmEnableThreads><TreatWarningsAsErrors>false</TreatWarningsAsErrors></PropertyGroup>
 <ItemGroup>{items}</ItemGroup><ItemGroup>{resources}</ItemGroup>
 <ItemGroup><WasmExtraFilesToDeploy Include="index.html" /><WasmExtraFilesToDeploy Include="style.css" /></ItemGroup>
 </Project>
 """);
 File.WriteAllText(Path.Combine(project,"NuGet.Config"),"<configuration><packageSources><clear/><add key=\"nuget.org\" value=\"https://api.nuget.org/v3/index.json\" /></packageSources></configuration>");
 var build=Invoke(dotnet,new[]{"publish",Path.Combine(project,"App.csproj"),"-c","Release","--nologo"},null,project);
 File.WriteAllText(Path.Combine(output,"browser-build.log"),build.Output+build.Error);
 if(build.Exit!=0)throw new InvalidOperationException("Browser/WASM SDK publish failed: "+build.Output+build.Error);
 string runtimeScript=Directory.GetFiles(project,"dotnet.js",SearchOption.AllDirectories).OrderByDescending(p=>p.Contains("publish",StringComparison.Ordinal)).FirstOrDefault(p=>Path.GetFileName(Path.GetDirectoryName(p))=="_framework")??throw new IOException("WASM SDK did not produce its static framework");
 string bundle=Path.GetDirectoryName(Path.GetDirectoryName(runtimeScript))!;
 string site=Path.Combine(output,"site");CopyTree(bundle,site);
 foreach(string file in OwnedFiles(assets))File.Copy(file,Path.Combine(site,Path.GetFileName(file)),true);
 string publicCatalog=request["resources"]!.AsArray().First(x=>x!["name"]!.ToString()=="public-linkage.json")!["path"]!.GetValue<string>();
 string catalog=Path.Combine(site,"public-linkage.json");File.Copy(publicCatalog,catalog);
 var artifacts=new JsonObject{{"application",Path.Combine(site,"index.html")},{"publicCatalog",catalog}};
 foreach(string file in Directory.GetFiles(site,"*",SearchOption.AllDirectories))artifacts["site:"+Path.GetRelativePath(site,file).Replace('\\','/')]=file;
 string runtime=Directory.GetFiles(site,"*.wasm",SearchOption.AllDirectories).FirstOrDefault()??throw new IOException("Actual WASM runtime artifact is required");
 Console.WriteLine(JsonSerializer.Serialize(new{protocol=1,ok=true,artifacts,run=new[]{Environment.GetEnvironmentVariable("CONFECTORY_PYTHON")??"python3","-m","http.server","8000","--bind","127.0.0.1","--directory",site},capabilities=new{runtime="independent-browser-wasm",backendRequired=false,staticOnly=true,dynamicCompilation=false,nativeFilesystem=false},wasm=runtime}));return 0;
}catch(Exception error){Console.WriteLine(JsonSerializer.Serialize(new{protocol=1,ok=false,error=error.Message}));return 1;}
static string Hash(string path)=>Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path)));
static string Escape(string value)=>SecurityElement.Escape(value)!;
static (int Exit,string Output,string Error) Invoke(string executable,string[] args,string? input,string? cwd=null){var start=new ProcessStartInfo(executable){RedirectStandardInput=true,RedirectStandardOutput=true,RedirectStandardError=true,UseShellExecute=false,WorkingDirectory=cwd??Environment.CurrentDirectory};foreach(string arg in args)start.ArgumentList.Add(arg);using var process=Process.Start(start)??throw new IOException("Trusted tool did not start");if(input is not null)process.StandardInput.Write(input);process.StandardInput.Close();var output=process.StandardOutput.ReadToEndAsync();var error=process.StandardError.ReadToEndAsync();if(!process.WaitForExit(240000)){process.Kill(true);throw new TimeoutException("Browser target tool timed out");}return(process.ExitCode,output.GetAwaiter().GetResult(),error.GetAwaiter().GetResult());}
static void CopyTree(string source,string destination){Directory.CreateDirectory(destination);foreach(string file in Directory.GetFiles(source))File.Copy(file,Path.Combine(destination,Path.GetFileName(file)),true);foreach(string directory in Directory.GetDirectories(source))CopyTree(directory,Path.Combine(destination,Path.GetFileName(directory)));}

static string OwnedOption(JsonObject request,string name){string relative=request["options"]?[name]?.GetValue<string>()??throw new ArgumentException("Target must declare "+name);if(Path.IsPathRooted(relative))throw new ArgumentException("Declared target resource must be relative: "+name);string path=PackPaths.Owned(AppContext.BaseDirectory,relative);if(!Directory.Exists(path)&&!File.Exists(path))throw new IOException("Declared target resource missing: "+path);return path;}
static string[] OwnedFiles(string directory){directory=PackPaths.Owned(AppContext.BaseDirectory,Path.GetRelativePath(AppContext.BaseDirectory,directory));return Directory.GetFiles(directory).Select(path=>{PackPaths.Owned(AppContext.BaseDirectory,Path.GetRelativePath(AppContext.BaseDirectory,path));return path;}).ToArray();}
