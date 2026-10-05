using System.Text.Json;
using Confectory.Core;

if (args.Length == 1 && args[0] is "--help" or "-h") { Usage(); return 0; }
if (args.Length < 3 || args[0] is not ("build" or "check" or "validate") || args.Length != (args[0] == "check" ? 4 : 3)) { Usage(); return 2; }
try
{
    var builder = new Builder(args[1], args[2]);
    var report = args[0] switch { "build" => builder.Build(), "check" => builder.Check(args[3]), _ => builder.Validate() };
    Console.WriteLine(report.ToJsonString(JsonData.Options)); return 0;
}
catch (BuildError ex)
{
    Console.Error.WriteLine(ex);
    Console.WriteLine(JsonSerializer.Serialize(new { ok = false, diagnostics = new[] { ex.Diagnostic } }, JsonData.Options)); return 1;
}
catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or JsonException or KeyNotFoundException or ArgumentException or InvalidOperationException)
{
    Console.WriteLine(JsonSerializer.Serialize(new { ok = false, diagnostics = new[] { new Diagnostic("error", "BUILD_IO", ex.Message, new()) } }, JsonData.Options)); return 1;
}

static void Usage()
{
    Console.Error.WriteLine("Usage: Confectory.Cli build|validate <project.cpack> <target>\n       Confectory.Cli check <project.cpack> <target> <pack-namespace>");
}
