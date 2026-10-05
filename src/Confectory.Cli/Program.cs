using System.Text.Json;
using Confectory.Core;

if (args.Length == 1 && args[0] is "--help" or "-h") { Usage(); return 0; }
if (args.Length < 3 || args[0] is not ("build" or "check" or "validate" or "run") || args.Length != (args[0] == "check" ? 4 : 3)) { Usage(); return 2; }
try
{
    if(args[0]=="run")Console.Error.WriteLine("[Confectory] Resolving/building "+Path.GetFullPath(args[1])+" for "+args[2]+" using "+Processes.DotNet());
    var builder = new Builder(args[1], args[2]);
    if(args[0]=="run")
    {
        var launch=builder.Build()["run"]!.Deserialize<string[]>()!;
        Console.Error.WriteLine("[Confectory 3/3] Starting "+launch[0]+" "+string.Join(" ",launch.Skip(1)));
        var start=new System.Diagnostics.ProcessStartInfo(launch[0]){UseShellExecute=false};
        foreach(string arg in launch.Skip(1))start.ArgumentList.Add(arg);
        using var process=System.Diagnostics.Process.Start(start)??throw new InvalidOperationException("Project execution did not start.");
        Console.Error.WriteLine("[Confectory] Project process started: "+process.Id);
        process.WaitForExit();Console.Error.WriteLine("[Confectory] Project exited: "+process.ExitCode);return process.ExitCode;
    }
    var report = args[0] switch { "build" => builder.Build(), "check" => builder.Check(args[3]), _ => builder.Validate() };
    Console.WriteLine(report.ToJsonString(JsonData.Options)); return 0;
}
catch (BuildError ex)
{
    Console.Error.WriteLine(ex);
    Console.WriteLine(JsonSerializer.Serialize(new { ok = false, diagnostics = new[] { ex.Diagnostic } }, JsonData.Options)); return 1;
}
catch (Exception ex) when (ex is System.ComponentModel.Win32Exception or IOException or UnauthorizedAccessException or JsonException or KeyNotFoundException or ArgumentException or InvalidOperationException or TimeoutException)
{
    Console.WriteLine(JsonSerializer.Serialize(new { ok = false, diagnostics = new[] { new Diagnostic("error", "BUILD_IO", ex.Message, new()) } }, JsonData.Options)); return 1;
}

static void Usage()
{
    Console.Error.WriteLine("Usage: Confectory.Cli build|validate|run <project.cpack> <target>\n       Confectory.Cli check <project.cpack> <target> <pack-namespace>");
}
