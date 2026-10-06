using System.Diagnostics;
using System.Reflection;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using Confectory.Core;
internal static class RunProject
{
 public static async Task<int> Execute(string project,string target)
 {
  project=Path.GetFullPath(project);string dotnet=Processes.DotNet();string cli=Assembly.GetExecutingAssembly().Location;var watch=Stopwatch.StartNew();
  Console.Error.WriteLine($"[Confectory] Resolving/building {project} for {target} using {dotnet}");
  var start=new ProcessStartInfo(dotnet){UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true,WorkingDirectory=Environment.CurrentDirectory};foreach(string argument in new[]{cli,"build",project,target})start.ArgumentList.Add(argument);start.Environment["CONFECTORY_DOTNET"]=dotnet;
  int progressSeconds=10;string? configured=Environment.GetEnvironmentVariable("CONFECTORY_BUILD_HEARTBEAT_SECONDS");if(configured is not null&&(!int.TryParse(configured,out progressSeconds)||progressSeconds<1||progressSeconds>60))throw new ArgumentException("Build heartbeat must be 1..60 seconds");
  using var build=Process.Start(start)??throw new IOException("Pack build process did not start");Console.Error.WriteLine($"[Confectory] Pack build process started: PID {build.Id}; cwd {start.WorkingDirectory}. This is the ordinary CLI build path.");
  long received=0;bool oversized=false;var output=new StringBuilder();async Task DrainOutput(){var chars=new char[8192];int count;while((count=await build.StandardOutput.ReadAsync(chars))>0){Interlocked.Add(ref received,count);if(output.Length+count<=16*1024*1024)output.Append(chars,0,count);else oversized=true;}}
  async Task DrainErrors(){string? line;while((line=await build.StandardError.ReadLineAsync()) is not null)Console.Error.WriteLine(line.Length<=4096?line:line[..4096]+" [diagnostic truncated]");}
  var stdout=DrainOutput();var stderr=DrainErrors();var exited=build.WaitForExitAsync();
  while(await Task.WhenAny(exited,Task.Delay(TimeSpan.FromSeconds(progressSeconds)))!=exited){string pending="none observed";try{string cache=Path.Combine(Path.GetDirectoryName(project)!,".confectory","cache","artifacts");var folders=Directory.Exists(cache)?Directory.EnumerateDirectories(cache,"*.pending").OrderByDescending(Directory.GetLastWriteTimeUtc).Take(3).ToArray():[];if(folders.Length>0)pending=string.Join(", ",folders.Select(folder=>Path.GetFileName(Directory.EnumerateFiles(folder,"*.cs").FirstOrDefault()??folder)));}catch(IOException){pending="cache observation unavailable";}catch(UnauthorizedAccessException){pending="cache observation unavailable";}Console.Error.WriteLine($"[Confectory] Pack build still running: {watch.Elapsed.TotalSeconds:F1}s, PID {build.Id}, report chars {Interlocked.Read(ref received)}, pending {pending}. No timeout or termination added.");}
  await exited;await Task.WhenAll(stdout,stderr);Console.Error.WriteLine($"[Confectory] Pack build finished: exit {build.ExitCode}, {watch.Elapsed.TotalSeconds:F2}s, report chars {received}.");if(build.ExitCode!=0){Console.Write(output.ToString());return build.ExitCode;}if(oversized)throw new IOException("Pack build report exceeded 16MiB; output was drained but cannot be parsed safely");
  var report=JsonNode.Parse(output.ToString())!.AsObject();string[] launch=report["run"]!.Deserialize<string[]>()??throw new IOException("Pack build supplied no run command");Console.Error.WriteLine("[Confectory 3/3] Starting "+JsonSerializer.Serialize(launch));var run=new ProcessStartInfo(launch[0]){UseShellExecute=false,WorkingDirectory=start.WorkingDirectory};foreach(string argument in launch.Skip(1))run.ArgumentList.Add(argument);run.Environment["CONFECTORY_DOTNET"]=dotnet;using var process=Process.Start(run)??throw new IOException("Project execution did not start");Console.Error.WriteLine("[Confectory] Project process started: "+process.Id);await process.WaitForExitAsync();Console.Error.WriteLine("[Confectory] Project exited: "+process.ExitCode);return process.ExitCode;
 }
}
