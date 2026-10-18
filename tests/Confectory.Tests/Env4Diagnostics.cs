using System.Diagnostics;
using System.Text.Json;
using Confectory.Core;

namespace Confectory.Tests;

// Opt-in measurements for the existing ENV4 cases. No assertions, deadlines or operations change.
internal static class Env4Diagnostics
{
    private static readonly object Gate = new();
    private static readonly Stopwatch Clock = Stopwatch.StartNew();
    private static bool Enabled => !string.IsNullOrEmpty(Environment.GetEnvironmentVariable("CONFECTORY_ENV4_TRACE"));
    private static void Mark(string phase, object data)
    {
        if (!Enabled) return;
        var process = Process.GetCurrentProcess();
        var row = JsonSerializer.Serialize(new { utc = DateTimeOffset.UtcNow, monotonicMs = Clock.Elapsed.TotalMilliseconds,
            pid = Environment.ProcessId, phase, cpuMs = process.TotalProcessorTime.TotalMilliseconds, rss = process.WorkingSet64, data });
        lock (Gate) File.AppendAllText(Path.Combine(Environment.GetEnvironmentVariable("CONFECTORY_ENV4_TRACE")!, $"managed-{Environment.ProcessId}.jsonl"), row + "\n");
    }
    internal static T Measure<T>(string phase, Func<T> action)
    {
        var clock = Stopwatch.StartNew(); Mark(phase + ":begin", new { });
        try { return action(); }
        finally { Mark(phase + ":end", new { elapsedMs = clock.Elapsed.TotalMilliseconds }); }
    }
    internal static ProcessResult Run(IReadOnlyList<string> command, int timeoutSeconds, string phase)
    {
        var clock = Stopwatch.StartNew(); Mark(phase + ":begin", new { timeoutSeconds });
        try
        {
            var result = Processes.Run(command, timeoutSeconds: timeoutSeconds);
            Mark(phase + ":exit", new { result.ExitCode, elapsedMs = clock.Elapsed.TotalMilliseconds }); return result;
        }
        catch (TimeoutException) { Mark(phase + ":timeout", new { timeoutSeconds, elapsedMs = clock.Elapsed.TotalMilliseconds }); throw; }
    }
    private const string Prefix = """
    var env4Clock=System.Diagnostics.Stopwatch.StartNew();
    void Env4Mark(string phase,object data){var folder=Environment.GetEnvironmentVariable("CONFECTORY_ENV4_TRACE");if(string.IsNullOrEmpty(folder))return;var p=System.Diagnostics.Process.GetCurrentProcess();System.IO.File.AppendAllText(System.IO.Path.Combine(folder,"driver-"+Environment.ProcessId+".jsonl"),System.Text.Json.JsonSerializer.Serialize(new{utc=DateTimeOffset.UtcNow,monotonicMs=env4Clock.Elapsed.TotalMilliseconds,pid=Environment.ProcessId,phase,cpuMs=p.TotalProcessorTime.TotalMilliseconds,rss=p.WorkingSet64,data})+"\n");}
    """;
    internal static void Graph(string path)
    {
        if (!Enabled) return;
        string text = File.ReadAllText(path);
        foreach (string expression in new[] {
            "Json(calls.Command.Invoke(view,op,Serialize(value)))",
            "Json(calls.Blueprint.Invoke(view,op,Serialize(value)))",
            "Json(calls.Blueprint.Invoke(view,\"read\",Serialize(new{id=graphId})))",
            "Json(calls.Blueprint.Invoke(view,action,Serialize(new{id=graphId,basis=basis[\"basis\"]!.ToString(),node,definition})))" })
            text = text.Replace("=>" + expression + ";", "=>Env4Call(" + JsonSerializer.Serialize(expression.Contains("Command") ? "command" : "blueprint") + ",()=>" + expression + ");", StringComparison.Ordinal);
        File.WriteAllText(path, Prefix + "\nT Env4Call<T>(string phase,Func<T> call){var clock=System.Diagnostics.Stopwatch.StartNew();Env4Mark(phase+\":begin\",new{});try{return call();}finally{Env4Mark(phase+\":end\",new{elapsedMs=clock.Elapsed.TotalMilliseconds});}}\n" + text);
    }
    internal static void Native(string path, bool button)
    {
        if (!Enabled) return;
        string text = File.ReadAllText(path);
        string sample = """
        int env4WaitOrdinal=0;var env4Samples=new System.Collections.Generic.Dictionary<int,long>();
        System.Text.Json.Nodes.JsonObject Env4Control(System.Text.Json.Nodes.JsonNode value){var result=new System.Text.Json.Nodes.JsonObject();foreach(string key in new[]{"available","connected","mode","frame","ack","pending","sequence","reason","outcome"})if(value[key] is not null)result[key]=value[key]!.DeepClone();return result;}
        void Env4Sample(int wait,long elapsed,string state,System.Text.Json.Nodes.JsonNode value){if(env4Samples.TryGetValue(wait,out long prior)&&env4Clock.ElapsedMilliseconds-prior<1000)return;env4Samples[wait]=env4Clock.ElapsedMilliseconds;Env4Mark("native-wait:sample",new{wait,elapsedMs=elapsed,state,control=Env4Control(value)});}
        """;
        text = text.Replace("var timer=System.Diagnostics.Stopwatch.StartNew();while(timer.ElapsedMilliseconds<90000)", "int env4Wait=++env4WaitOrdinal;var timer=System.Diagnostics.Stopwatch.StartNew();while(timer.ElapsedMilliseconds<90000)", StringComparison.Ordinal);
        if (button)
            text = text.Replace("var node=Read();if(condition(node))return node;", "var node=Read();Env4Sample(env4Wait,timer.ElapsedMilliseconds,calls.Observe.Invoke(session,h)[1],node);if(condition(node)){Env4Mark(\"native-wait:done\",new{wait=env4Wait,elapsedMs=timer.ElapsedMilliseconds,control=Env4Control(node)});return node;}", StringComparison.Ordinal);
        else
            text = text.Replace("var status=Control(handle,\"observe\");if(condition(status))return status;", "var status=Control(handle,\"observe\");Env4Sample(env4Wait,timer.ElapsedMilliseconds,calls.Observe.Invoke(session,handle)[1],status);if(condition(status)){Env4Mark(\"native-wait:done\",new{wait=env4Wait,elapsedMs=timer.ElapsedMilliseconds,control=Env4Control(status)});return status;}", StringComparison.Ordinal);
        File.WriteAllText(path, Prefix + "\n" + sample + "\n" + text);
    }
}
