using System.IO.Pipes;
using System.Text.Json.Nodes;
namespace Confectory.Tests;
public sealed class EmbeddedChannelTests : TestCase
{
    // Exercises the actual platform-neutral host channel, not a replacement UI.
    public void test_embedded_channel_correlates_replies_and_retires_on_eof()
    {
        using var replies = new AnonymousPipeServerStream(PipeDirection.Out);
        using var input = new AnonymousPipeClientStream(PipeDirection.In, replies.ClientSafePipeHandle);
        using var requests = new AnonymousPipeServerStream(PipeDirection.In);
        using var output = new AnonymousPipeClientStream(PipeDirection.Out, requests.ClientSafePipeHandle);
        using var reader = new StreamReader(input);
        using var writer = new StreamWriter(output) { AutoFlush = true };
        using var observed = new StreamReader(requests);
        using var response = new StreamWriter(replies) { AutoFlush = true };
        using var channel = new PackChannel(reader, writer);
        var first = channel.Call("resource", JsonValue.Create("/assets/icon.png"));
        var second = channel.Call("request", new JsonObject { ["op"] = "mount" });
        var a = JsonNode.Parse(observed.ReadLineAsync().WaitAsync(TimeSpan.FromSeconds(5)).GetAwaiter().GetResult()!)!;
        var b = JsonNode.Parse(observed.ReadLineAsync().WaitAsync(TimeSpan.FromSeconds(5)).GetAwaiter().GetResult()!)!;
        Equal("/assets/icon.png", a["input"]!.GetValue<string>());
        True(!first.IsCompleted && !second.IsCompleted, "Requests must await their own reply");
        response.WriteLine(new JsonObject { ["id"] = b["id"]!.DeepClone(), ["result"] = "second" }.ToJsonString());
        Equal("second", second.WaitAsync(TimeSpan.FromSeconds(5)).GetAwaiter().GetResult()!.GetValue<string>());
        True(!first.IsCompleted, "Out-of-order reply completed wrong request");
        response.WriteLine(new JsonObject { ["id"] = a["id"]!.DeepClone(), ["error"] = "transport_rejected" }.ToJsonString());
        bool rejected = false;
        try { first.WaitAsync(TimeSpan.FromSeconds(5)).GetAwaiter().GetResult(); } catch (IOException) { rejected = true; }
        True(rejected, "Resource rejection must not become success");
        var pending = channel.Call("request", new JsonObject { ["op"] = "update" });
        response.Dispose();
        rejected = false;
        try { pending.WaitAsync(TimeSpan.FromSeconds(5)).GetAwaiter().GetResult(); } catch (IOException) { rejected = true; }
        True(rejected && channel.IsClosed, "EOF must retire pending calls");
        try { channel.Call("request", null); throw new Exception("Closed channel accepted request"); } catch (IOException) { }
    }
}
