using System.Diagnostics;
using System.Text.Json;
using Confectory.Core;

try
{
 if(args.Length==2&&args[0]=="describe")
 {
  string path=Path.GetFullPath(args[1]);var manifest=new Parser(File.ReadAllText(path),path).ParseManifest();
  if(manifest.Kind!="project")throw new ArgumentException("A ProjectPack is required.");
  Console.WriteLine(JsonSerializer.Serialize(new[]{manifest.Namespace,manifest.Entry??"",string.Join(",",manifest.Targets.Keys.Order(StringComparer.Ordinal))}));return 0;
 }
 if((args.Length!=4&&args.Length!=5)||args[0]!="run")throw new ArgumentException("Usage: describe ProjectPack | run ProjectPack entry target [sourceLeasePath]");
 string project=Path.GetFullPath(args[1]);if(string.IsNullOrWhiteSpace(args[2])||string.IsNullOrWhiteSpace(args[3]))throw new ArgumentException("Explicit entry and target required.");
 string folder=Path.Combine(Path.GetDirectoryName(project)!,".confectory");Directory.CreateDirectory(folder);
 string leasePath=args.Length==5?Path.GetFullPath(args[4]):Path.Combine(folder,"execution-build.lock");Directory.CreateDirectory(Path.GetDirectoryName(leasePath)!);
 FileStream? lease=null;var watch=Stopwatch.StartNew();
 while(lease is null){try{lease=new FileStream(leasePath,FileMode.OpenOrCreate,FileAccess.ReadWrite,FileShare.None);}catch(IOException){if(watch.Elapsed>TimeSpan.FromMinutes(2))throw new TimeoutException("Build lease timeout.");Thread.Sleep(20);}}
 string[] command;
 using(lease)
 {
  var builder=new Builder(project,args[3]);builder.Registry.Project.Entry=args[2]; // in-memory selection; source unchanged
  command=builder.Build()["run"]!.Deserialize<string[]>()!;
 }
 var start=new ProcessStartInfo(command[0]){UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true,WorkingDirectory=Path.GetDirectoryName(project)!};
 foreach(string arg in command.Skip(1))start.ArgumentList.Add(arg);
 using var child=Process.Start(start)??throw new InvalidOperationException("Execution did not start.");
 Console.WriteLine(JsonSerializer.Serialize(new{state="running"}));Console.Out.Flush();
 child.OutputDataReceived+=(_,e)=>{if(e.Data is not null)Console.Error.WriteLine(e.Data);};child.ErrorDataReceived+=(_,e)=>{if(e.Data is not null)Console.Error.WriteLine(e.Data);};
 child.BeginOutputReadLine();child.BeginErrorReadLine();child.WaitForExit();return child.ExitCode;
}
catch(Exception ex){Console.Error.WriteLine(ex);return 1;}
