using System.Collections.Concurrent;
using System.Text.Json.Nodes;

internal sealed class PackChannel : IDisposable
{
    readonly ConcurrentDictionary<string, TaskCompletionSource<JsonNode?>> pending = new();
    readonly object output = new();
    readonly TextReader reader; readonly TextWriter writer;
    int sequence; volatile bool closed;
    public event Action? Disconnected;
    public bool IsClosed => closed;
    public PackChannel(TextReader? input = null, TextWriter? outputWriter = null)
    { reader = input ?? Console.In; writer = outputWriter ?? Console.Out; _ = Task.Run(Read); }
    public Task<JsonNode?> Call(string operation, JsonNode? input)
    {
        lock (output)
        {
            if (closed || pending.Count >= 64) throw new IOException("Pack channel unavailable");
            string id = Interlocked.Increment(ref sequence).ToString();
            var completion = new TaskCompletionSource<JsonNode?>(TaskCreationOptions.RunContinuationsAsynchronously);
            pending[id] = completion;
            writer.WriteLine(new JsonObject { ["id"] = id, ["operation"] = operation, ["input"] = input }.ToJsonString());
            writer.Flush();
            return completion.Task;
        }
    }
    async Task Read()
    {
        try
        {
            while (await reader.ReadLineAsync() is string line)
            {
                if (line.Length > 6291456) throw new IOException("Oversized pack reply");
                var reply = JsonNode.Parse(line)!;
                if (pending.TryRemove(reply["id"]!.GetValue<string>(), out var task))
                    if (reply["error"] is null) task.TrySetResult(reply["result"]?.DeepClone());
                    else task.TrySetException(new IOException("Pack rejected request"));
            }
        }
        catch (Exception e) { Console.Error.WriteLine("Pack channel closed: " + e.GetType().Name); }
        finally { Dispose(); Disconnected?.Invoke(); }
    }
    public void Dispose()
    {
        lock (output) { closed = true; foreach (var task in pending.Values) task.TrySetException(new IOException("Pack channel closed")); pending.Clear(); }
    }
}
