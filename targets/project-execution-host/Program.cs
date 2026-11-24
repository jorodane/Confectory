using System.Diagnostics;
using System.Text.Json;
using Confectory.Core;

try
{
 if(args.Length==1&&args[0]=="build-job"){var request=System.Text.Json.Nodes.JsonNode.Parse(Console.In.ReadToEnd())!.AsObject();var result=BuildJobs.Execute(request);Console.WriteLine(result.ToJsonString());return request["operation"]?.ToString()=="build"&&result["state"]?.ToString()=="failed"?1:0;}
 if(args.Length==2&&args[0]=="describe")
 {
  string path=Path.GetFullPath(args[1]);var manifest=new Parser(File.ReadAllText(path),path).ParseManifest();

  Console.WriteLine(JsonSerializer.Serialize(new[]{manifest.Namespace,manifest.Entry??"",string.Join(",",manifest.Targets.Keys.Order(StringComparer.Ordinal)),manifest.Kind,manifest.SupportsStandalone?"true":"false"}));return 0;
 }
 if((args.Length!=4&&args.Length!=5)||args[0]!="run")throw new ArgumentException("Usage: describe ProjectPack | run ProjectPack entry target [sourceLeasePath]");
 string project=Path.GetFullPath(args[1]);var runnable=new Parser(File.ReadAllText(project),project).ParseManifest();if(runnable.Kind!="project"||!runnable.SupportsStandalone)throw new ArgumentException("This pack does not support standalone execution; open/edit it or compose a runnable ProjectPack.");if(string.IsNullOrWhiteSpace(args[2])||string.IsNullOrWhiteSpace(args[3]))throw new ArgumentException("Explicit entry and target required.");
 string folder=Path.Combine(Path.GetDirectoryName(project)!,".confectory");Directory.CreateDirectory(folder);
 string leasePath=args.Length==5?Path.GetFullPath(args[4]):Path.Combine(folder,"execution-build.lock");Directory.CreateDirectory(Path.GetDirectoryName(leasePath)!);
 FileStream? lease=null;var watch=Stopwatch.StartNew();
 while(lease is null){try{lease=new FileStream(leasePath,FileMode.OpenOrCreate,FileAccess.ReadWrite,FileShare.None);}catch(IOException){if(watch.Elapsed>TimeSpan.FromMinutes(2))throw new TimeoutException("Build lease timeout.");Thread.Sleep(20);}}
 string[] command;
 using(lease)
 {
  Builder? builder=null;
  try
  {
   builder=new Builder(project,args[3]);builder.Registry.Project.Entry=args[2]; // in-memory selection; source unchanged
   command=builder.Build()["run"]!.Deserialize<string[]>()!;
  }
  catch(BuildError error)
  {
   string code=error.Diagnostic.Code;
   if(code=="TARGET_FAILURE")
   {
    var diagnostic=System.Text.RegularExpressions.Regex.Match(error.Message,@": error (CS[0-9]{4}):");
    if(diagnostic.Success)code=diagnostic.Groups[1].Value;
   }
   // Send only the code and an optional owned diagnostic subject to the Run view.
   string? feature=StaleBlueprintFeature(error,builder?.Registry.Project);
   Console.WriteLine(feature is null?JsonSerializer.Serialize(new{state="build-failed",code}):
    JsonSerializer.Serialize(new{state="build-failed",code,feature}));Console.Out.Flush();
   throw;
  }
 }
 var start=new ProcessStartInfo(command[0]){UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true,WorkingDirectory=Path.GetDirectoryName(project)!};
 foreach(string arg in command.Skip(1))start.ArgumentList.Add(arg);
 using var child=Process.Start(start)??throw new InvalidOperationException("Execution did not start.");
 Console.WriteLine(JsonSerializer.Serialize(new{state="running"}));Console.Out.Flush();
 child.OutputDataReceived+=(_,e)=>{if(e.Data is not null)Console.Error.WriteLine(e.Data);};child.ErrorDataReceived+=(_,e)=>{if(e.Data is not null)Console.Error.WriteLine(e.Data);};
 child.BeginOutputReadLine();child.BeginErrorReadLine();child.WaitForExit();return child.ExitCode;
}
catch(Exception ex){Console.Error.WriteLine(ex);return 1;}

static string? StaleBlueprintFeature(BuildError error,Manifest? project)
{
 if(project is null||error.Diagnostic.Code!="BLUEPRINT_NOT_READY")return null;
 string prefix=project.Namespace+"::";
 string? Owned(string id)=>id.Length<=384&&id.StartsWith(prefix,StringComparison.Ordinal)&&
  project.Elements.TryGetValue(id[prefix.Length..],out var element)&&element.Kind=="function"?id:null;
 if(error.BlueprintRepairFeature is string caller)return Owned(caller);
 if(error.Message.Length>4096)return null;
 try
 {
  // BlueprintCompilation preserves FeatureBlueprint's JSON refusal in this error.
  // GRAPH_CONTRACT_STALE uses the parsed function ID as its subject.
  using var refusal=JsonDocument.Parse(error.Message);
  var root=refusal.RootElement;
  if(!root.TryGetProperty("state",out var state)||state.GetString()!="invalid"||
     !root.TryGetProperty("diagnostics",out var diagnostics)||diagnostics.GetArrayLength()!=1)return null;
  var diagnostic=diagnostics[0];
  if(!diagnostic.TryGetProperty("code",out var code)||code.GetString()!="GRAPH_CONTRACT_STALE"||
     !diagnostic.TryGetProperty("subject",out var subject)||subject.GetString() is not string id)return null;
  return Owned(id);
 }
 catch(Exception failure) when(failure is JsonException or InvalidOperationException){return null;}
}
