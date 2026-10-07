using System.Diagnostics;
using System.Security.Cryptography;
using System.Text.Json;
using System.Text.Json.Nodes;
// This browser target owns its local .NET-host capability boundary; core remains target-neutral.
try {
 var request=JsonNode.Parse(Console.In.ReadToEnd())!.AsObject();
 string root=Path.GetFullPath(Path.Combine(AppContext.BaseDirectory,"../../../../.."));
 string assets=Path.Combine(root,"packs","browser-host","assets");
 string compiler=Path.Combine(root,"targets","dotnet","bin","Release","net8.0","Confectory.Build.DotNet.dll");
 if(!File.Exists(compiler))throw new IOException("Build trusted targets/dotnet before the local browser target");
 string dotnet=Environment.GetEnvironmentVariable("CONFECTORY_DOTNET")??"dotnet";
 var start=new ProcessStartInfo(dotnet){RedirectStandardInput=true,RedirectStandardOutput=true,RedirectStandardError=true,UseShellExecute=false};start.ArgumentList.Add(compiler);
 using var process=Process.Start(start)??throw new IOException("Cannot start trusted compiler");
 process.StandardInput.Write(request.ToJsonString());process.StandardInput.Close();
 var output=process.StandardOutput.ReadToEndAsync();var error=process.StandardError.ReadToEndAsync();process.WaitForExit();
 var result=JsonNode.Parse(output.GetAwaiter().GetResult())!.AsObject();
 if(request["operation"]?.ToString()=="link"&&process.ExitCode==0){
  string outputRoot=request["output"]!.GetValue<string>(),assetOutput=Path.Combine(outputRoot,"browser-assets");Directory.CreateDirectory(assetOutput);
  foreach(string file in new[]{"index.html","app.js","style.css"}){string destination=Path.Combine(assetOutput,file);File.Copy(Path.Combine(assets,file),destination);result["artifacts"]!["browser:"+file]=destination;}
 }
 if(request["operation"]?.ToString()=="fingerprint")result["fingerprint"]=string.Join(":",new[]{"index.html","app.js","style.css"}.Select(file=>Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(Path.Combine(assets,file))))))+":"+"browser-local-host-v1:"+Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(compiler)))+":"+result["fingerprint"];
 Console.WriteLine(result.ToJsonString());return process.ExitCode;
}catch(Exception error){Console.WriteLine(JsonSerializer.Serialize(new{protocol=1,ok=false,error=error.Message}));return 1;}
