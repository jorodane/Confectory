using System.Diagnostics;
using System.Text.Json.Nodes;
using Confectory.Core;
using Confectory.DesktopEntry;
try
{
 if(args.Length<2)throw new ArgumentException("Usage: inspect pack [target] | open pack [--repository repo] | registration-file output.reg --repository repo");
 string command=args[0],path=Path.GetFullPath(args[1]);
 if(command=="inspect"){Console.WriteLine(EntryProtocol.Inspect(path,args.Length>2?args[2]:OperatingSystem.IsWindows()?"windows":"linux").ToJsonString());return 0;}
 if(command=="supervise"){
  string installation=EntryProtocol.Canonical(path);if(!File.Exists(Path.Combine(installation,"examples","editor-home","project.cpack")))throw new ArgumentException("Installed engine unavailable");
  string inbox=EntryProtocol.Folder(Environment.GetEnvironmentVariable("CONFECTORY_ENTRY_SCOPE")??installation);Directory.CreateDirectory(inbox);using var file=new StreamWriter(Path.Combine(inbox,"engine.log"),true){AutoFlush=true};var logger=TextWriter.Synchronized(file);
  var launch=new ProcessStartInfo(Processes.DotNet()){UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true,CreateNoWindow=true,WorkingDirectory=installation};foreach(string arg in new[]{Path.Combine(installation,"src","Confectory.Cli","bin","Release","net8.0","Confectory.Cli.dll"),"run",Path.Combine(installation,"examples","editor-home","project.cpack"),OperatingSystem.IsWindows()?"windows":"linux"})launch.ArgumentList.Add(arg);
  using var engine=Process.Start(launch)??throw new IOException("Installed engine process did not start");async Task Drain(StreamReader stream){string? line;while((line=await stream.ReadLineAsync()) is not null)await logger.WriteLineAsync(line);}var output=Drain(engine.StandardOutput);var error=Drain(engine.StandardError);await engine.WaitForExitAsync();await Task.WhenAll(output,error);return engine.ExitCode;
 }
 if(args.Length!=2&&(args.Length!=4||args[2]!="--repository"))throw new ArgumentException("Expected --repository followed by installation path");
 string repo=EntryProtocol.Canonical(args.Length==4&&args[2]=="--repository"?args[3]:Path.Combine(AppContext.BaseDirectory,"../../../../.."));
 if(!File.Exists(Path.Combine(repo,"examples","editor-home","project.cpack")))throw new ArgumentException("An installed, trusted Confectory checkout is required");
 if(command=="registration-file"){
  if(!OperatingSystem.IsWindows())throw new PlatformNotSupportedException("Generate Windows association registration on the Windows installation");
  string dotnet=Processes.DotNet(),dll=typeof(EntryProtocol).Assembly.Location;
  string registration=WindowsAssociation.Format(dotnet,dll,repo);
  File.WriteAllText(path,registration,System.Text.Encoding.Unicode);Console.WriteLine("Registration file created; review/import it yourself. No registry setting was changed.");return 0;
 }
 if(command!="open")throw new ArgumentException("Unknown desktop entry command");
 path=EntryProtocol.Canonical(path);EntryProtocol.Read(path); // Metadata only: never build/run the requested pack.
 string scope=Environment.GetEnvironmentVariable("CONFECTORY_ENTRY_SCOPE")??repo;string folder=EntryProtocol.Folder(scope);Directory.CreateDirectory(folder);
 FileStream? lease=null;var clock=Stopwatch.StartNew();while(lease is null){try{lease=new FileStream(Path.Combine(folder,"launch.lock"),FileMode.OpenOrCreate,FileAccess.ReadWrite,FileShare.None);}catch(IOException){if(clock.Elapsed.TotalSeconds>240)throw new TimeoutException("Another file-entry request is still starting/opening; no duplicate engine was launched");await Task.Delay(50);}}
 using(lease){string id=Guid.NewGuid().ToString("N");
 try{var existing=await EntryProtocol.Send(scope,path,id);Console.WriteLine(existing.ToJsonString());return existing["status"]!.ToString() is "opened" or "already-open"?0:1;}catch(TimeoutException){} // Connection only; an acknowledgment timeout is OperationCanceledException, not a cold-start signal.
 string marker=Path.Combine(folder,"startup.json");bool starting=false;
 if(File.Exists(marker)){try{var record=JsonNode.Parse(File.ReadAllText(marker))!;using var process=Process.GetProcessById(record["pid"]!.GetValue<int>());starting=!process.HasExited&&process.StartTime.ToUniversalTime().Ticks==record["started"]!.GetValue<long>();}catch(ArgumentException){}catch(InvalidOperationException){}}
 if(EntryProtocol.OwnerActive(scope))throw new IOException("Engine exists but its entry inbox could not be reached. No replacement instance was started");
 if(!starting){string dotnet=Processes.DotNet(),cli=Path.Combine(repo,"src","Confectory.Cli","bin","Release","net8.0","Confectory.Cli.dll");if(!File.Exists(cli))throw new FileNotFoundException("Build the installed Confectory solution first",cli);
 var start=new ProcessStartInfo(dotnet){UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true,CreateNoWindow=true,WorkingDirectory=repo};foreach(string arg in new[]{typeof(EntryProtocol).Assembly.Location,"supervise",repo})start.ArgumentList.Add(arg);start.Environment["CONFECTORY_EDITOR_REPO"]=repo;start.Environment["CONFECTORY_ENTRY_SCOPE"]=scope;
 using var engine=Process.Start(start)??throw new IOException("Installed engine did not start");File.WriteAllText(marker,new JsonObject{["pid"]=engine.Id,["started"]=engine.StartTime.ToUniversalTime().Ticks}.ToJsonString());}
 while(clock.Elapsed.TotalSeconds<240){
 try{var record=JsonNode.Parse(File.ReadAllText(marker))!;using var startup=Process.GetProcessById(record["pid"]!.GetValue<int>());if(startup.HasExited||startup.StartTime.ToUniversalTime().Ticks!=record["started"]!.GetValue<long>())throw new IOException("Engine startup exited; inspect "+Path.Combine(folder,"engine.log")+" and retry. No replacement was launched");}catch(ArgumentException){throw new IOException("Engine startup exited; inspect "+Path.Combine(folder,"engine.log")+" and retry. No replacement was launched");}
 try{var opened=await EntryProtocol.Send(scope,path,id);Console.WriteLine(opened.ToJsonString());return opened["status"]!.ToString() is "opened" or "already-open"?0:1;}catch(TimeoutException){await Task.Delay(100);}}
 throw new TimeoutException("Installed engine did not expose its inbox within240 seconds; startup marker retained to avoid duplicate launches");
 }
}
catch(Exception error){Console.Error.WriteLine(error.Message);Console.WriteLine(new JsonObject{["status"]="failed",["message"]=error.Message}.ToJsonString());return 1;}
