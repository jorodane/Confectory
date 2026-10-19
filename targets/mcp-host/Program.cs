using System.Collections.Concurrent;
using System.IO.Pipes;
using System.Net.Sockets;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

// A protocol adapter only. Domain tools execute in the existing, explicitly
// opened EditorHome capability. No project files, account store or shell here.
string directory = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Confectory", "MCP", "instances");
if (args.Length == 2 && args[0] == "--instances") directory = Path.GetFullPath(args[1]);
else if (args.Length != 0) { Console.Error.WriteLine("Usage: Confectory.Mcp [--instances <private discovery directory>]"); return 2; }
var adapter = new Adapter(directory);
await adapter.Run();
return 0;

sealed class Adapter(string directory)
{
    const int MaxFrame = 8388608;
    long completedBytes;
    readonly object outputGate = new(), bindingGate = new();
    readonly string client = Guid.NewGuid().ToString("N");
    readonly ConcurrentDictionary<string, CancellationTokenSource> pending = new();
    readonly ConcurrentDictionary<string, (string Fingerprint, JsonObject Reply)> completed = new();
    readonly SemaphoreSlim slots = new(2);
    readonly List<Task> workers = [];
    readonly CancellationTokenSource lifetime = new();
    JsonObject? binding;
    int selectionGeneration;
    string observedScope = "";
    volatile bool initialized, ready;

    static string Text(JsonNode? node, string key) => node?[key]?.GetValue<string>() ?? "";
    static JsonObject Error(int code, string message) => new() { ["code"] = code, ["message"] = message };
    void Write(JsonObject value)
    {
        lock (outputGate) { Console.Out.WriteLine(value.ToJsonString()); Console.Out.Flush(); }
    }
    void Changed() => Write(new() { ["jsonrpc"] = "2.0", ["method"] = "notifications/tools/list_changed" });
    static JsonObject ToolResult(JsonNode? value, bool error = false) => new()
    {
        ["content"] = new JsonArray(new JsonObject { ["type"] = "text", ["text"] = value?.ToJsonString() ?? "null" }), ["isError"] = error
    };
    static JsonObject Failure(string code) => ToolResult(new JsonObject { ["code"] = code, ["message"] = code switch
    {
        "engine_not_running" => "Confectory의 AI 연결에서 Codex를 선택하고 엔진 연결을 준비하세요. 프로젝트는 나중에 선택할 수 있습니다.",
        "instance_not_found" => "연결할 엔진을 다시 조회하고 표시된 instanceId를 선택하세요.",
        "engine_unavailable" => "엔진이 닫혔거나 응답하지 않습니다. 앱의 연결 상태를 확인한 뒤 다시 연결하세요.",
        "no_engine_selected" => "confectory_instances로 준비된 엔진을 조회한 뒤 confectory_connect로 하나를 선택하세요.",
        "read_only" => "읽기 전용 프로젝트 범위입니다. 앱에서 접근 범위를 해제한 뒤 편집 범위를 명시적으로 허용하세요. 엔진 연결은 유지됩니다.",
        "no_project_scope" => "엔진은 연결됐지만 프로젝트 접근 범위가 없습니다. 앱에서 대상을 선택하고 범위를 허용한 뒤 상태와 도구 목록을 갱신하세요.",
        "scope_changed" => "프로젝트 접근 범위가 바뀌었습니다. 엔진 연결을 유지한 채 상태와 도구 목록을 다시 확인하세요. 이전 요청은 재전송하지 않습니다.",
        "source_changed" => "선택한 노드 원본이나 계약이 바뀌었습니다. 앱에서 접근 범위를 해제하고 현재 원본으로 다시 허용하세요.",
        "cancelled" => "조회 대기를 취소했습니다.",
        "write_outcome_unknown" => "편집 결과를 확인하지 못했습니다. 자동 재전송하지 않습니다. 앱의 기존 변경 목록을 확인하세요.",
        "invalid_engine_response" => "엔진 응답을 검증할 수 없습니다. 앱의 연결을 다시 준비하세요.",
        _ => "현재 연결 범위에서 요청을 처리할 수 없습니다. 앱의 프로젝트·노드 선택과 변경 상태를 확인하세요."
    } }, true);

    public async Task Run()
    {
        using var input = Console.OpenStandardInput();var frames = new FrameReader(input);
        try
        {
            while (await frames.Read(lifetime.Token) is { } line)
            {
                JsonObject request;
                try { request = JsonNode.Parse(line)!.AsObject(); }
                catch { Write(new() { ["jsonrpc"] = "2.0", ["id"] = null, ["error"] = Error(-32700, "Parse error") }); continue; }
                if (Text(request, "jsonrpc") != "2.0" || request["method"] is not JsonValue methodValue || !methodValue.TryGetValue<string>(out string? method))
                { Write(new() { ["jsonrpc"] = "2.0", ["id"] = request["id"]?.DeepClone(), ["error"] = Error(-32600, "Invalid request") }); continue; }
                var parameters = request["params"] as JsonObject ?? new();
                if (request["id"] is null)
                {
                    if (method == "notifications/initialized" && initialized) ready = true;
                    if (method == "notifications/cancelled" && parameters["requestId"] is { } id && pending.TryGetValue(id.ToJsonString(), out var cancellation)) { try { cancellation.Cancel(); } catch (ObjectDisposedException) { } }
                    continue;
                }
                string requestKey = request["id"]!.ToJsonString();
                if (request["id"] is not JsonValue scalar || !(scalar.TryGetValue<string>(out _) || scalar.TryGetValue<long>(out _)) || requestKey.Length > 160)
                { Write(new() { ["jsonrpc"] = "2.0", ["id"] = request["id"]!.DeepClone(), ["error"] = Error(-32600, "Bounded scalar request ID required") }); continue; }
                string fingerprint = Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(method + parameters.ToJsonString())));
                var cts = CancellationTokenSource.CreateLinkedTokenSource(lifetime.Token);
                if (pending.Count >= 8 || (!completed.ContainsKey(requestKey) && (completed.Count >= 256 || Interlocked.Read(ref completedBytes) >= 16777216)) || !pending.TryAdd(requestKey, cts))
                { cts.Dispose(); Write(new() { ["jsonrpc"] = "2.0", ["id"] = request["id"]!.DeepClone(), ["error"] = Error(-32000, "Request budget or duplicate pending ID") }); continue; }
                // Initialization stays ordered; tool calls may be cancelled while IPC waits.
                if (method == "initialize") await Complete(request, method, parameters, requestKey, fingerprint, cts);
                else workers.Add(Complete(request, method, parameters, requestKey, fingerprint, cts));
            }
        }
        catch (InvalidDataException) { Console.Error.WriteLine("MCP frame budget exceeded"); }
        finally { lifetime.Cancel(); await Task.WhenAll(workers); }
    }

    async Task Complete(JsonObject request, string method, JsonObject parameters, string key, string fingerprint, CancellationTokenSource cts)
    {
        var reply = new JsonObject { ["jsonrpc"] = "2.0", ["id"] = request["id"]!.DeepClone() };bool entered = false;
        try
        {
            await slots.WaitAsync(cts.Token); entered = true;
            if (completed.TryGetValue(key, out var saved))
            {
                if (saved.Fingerprint != fingerprint) throw new ProtocolException(-32600, "Request ID reused with different input");
                string? scopeError = method == "tools/call" && Text(parameters, "name").StartsWith("workspace_", StringComparison.Ordinal) ? await CheckScope(parameters["arguments"] as JsonObject ?? new(), cts.Token) : null;
                reply = scopeError is null ? saved.Reply.DeepClone().AsObject() : new JsonObject { ["jsonrpc"] = "2.0", ["id"] = request["id"]!.DeepClone(), ["result"] = Failure(scopeError) };
            }
            else if (method == "initialize")
            {
                if (initialized) throw new ProtocolException(-32600, "Already initialized");
                string version = Text(parameters, "protocolVersion");
                if (version is not ("2025-11-25" or "2025-06-18" or "2025-03-26" or "2024-11-05")) version = "2025-06-18";
                initialized = true;
                reply["result"] = new JsonObject { ["protocolVersion"] = version, ["capabilities"] = new JsonObject { ["tools"] = new JsonObject { ["listChanged"] = true } }, ["serverInfo"] = new JsonObject { ["name"] = "confectory", ["version"] = "0.2.0" }, ["instructions"] = "Connect to an explicitly prepared engine before choosing a project. Connection grants no project access. After the user selects a project scope in Confectory, refresh status and tools; echo its exact projectId and scopeId. Existing drafts still require human Review/Confirm." };
            }
            else if (!ready) throw new ProtocolException(-32002, "Initialize the MCP session first");
            else if (method == "ping") reply["result"] = new JsonObject();
            else if (method == "tools/list") reply["result"] = new JsonObject { ["tools"] = await Tools(cts.Token) };
            else if (method == "tools/call") reply["result"] = await Call(Text(parameters, "name"), parameters["arguments"] as JsonObject ?? new(), key, cts.Token);
            else throw new ProtocolException(-32601, "Method not found");
        }
        catch (ProtocolException ex) { reply["error"] = Error(ex.Code, ex.Message); }
        catch (OperationCanceledException) { reply["result"] = Failure(method == "tools/call" && Text(parameters, "name") is "workspace_stage" or "workspace_create" ? "write_outcome_unknown" : "cancelled"); }
        catch { reply["result"] = Failure("operation_refused"); }
        finally { if (entered) slots.Release(); pending.TryRemove(key, out _); cts.Dispose(); }
        int replyBytes = Encoding.UTF8.GetByteCount(reply.ToJsonString());
        if (replyBytes > MaxFrame) reply = new JsonObject { ["jsonrpc"] = "2.0", ["id"] = request["id"]!.DeepClone(), ["result"] = Failure("result_budget") };
        if (!completed.ContainsKey(key)) { Interlocked.Add(ref completedBytes, Math.Min(replyBytes, MaxFrame));completed[key] = (fingerprint, reply); }
        if (!lifetime.IsCancellationRequested) Write(reply);
    }
    static JsonObject Descriptor(string name, string description, JsonObject properties, params string[] required) => new()
    {
        ["name"] = name, ["description"] = description, ["inputSchema"] = new JsonObject { ["type"] = "object", ["properties"] = properties, ["required"] = new JsonArray(required.Select(s => (JsonNode)JsonValue.Create(s)!).ToArray()), ["additionalProperties"] = false },
        ["annotations"] = new JsonObject { ["readOnlyHint"] = true, ["openWorldHint"] = false }
    };
    async Task<JsonArray> Tools(CancellationToken token)
    {
        var tools = new JsonArray(
            Descriptor("confectory_instances", "Find explicitly prepared local Confectory engines; never opens project files", new()),
            Descriptor("confectory_connect", "Select an engine by instanceId even without a project; grants no project access", new() { ["instanceId"] = new JsonObject { ["type"] = "string", ["maxLength"] = 32 } }, "instanceId"),
            Descriptor("confectory_status", "Read engine connection and separately authorized project scope; refresh tools after scope changes", new()),
            Descriptor("confectory_disconnect", "Forget this adapter's selection; does not close the engine or discard drafts", new()));
        JsonObject? selected;lock (bindingGate) selected = binding?.DeepClone().AsObject();
        if (selected is null) return tools;
        var response = await Send(selected, "tools/list", new(), token);
        if (response["ok"]?.GetValue<bool>() != true) return tools;
        if (response["result"] is not JsonArray definitions || definitions.Count > 6) throw new InvalidDataException();
        foreach (var row in definitions)
        {
            string name = Text(row, "name");if (name is not ("workspace_list" or "workspace_read" or "workspace_inspect" or "workspace_stage" or "workspace_create" or "workspace_changes") || row?["parameters"] is not JsonObject schema) throw new InvalidDataException();
            tools.Add(new JsonObject { ["name"] = name, ["description"] = Text(row, "description"), ["inputSchema"] = schema.DeepClone(), ["annotations"] = new JsonObject { ["readOnlyHint"] = name is not ("workspace_stage" or "workspace_create"), ["destructiveHint"] = false, ["openWorldHint"] = false } });
        }
        return tools;
    }
    void Observe(JsonObject status, int generation)
    {
        string scope = Text(status["scope"], "id") + ":" + (status["scopeVersion"]?.ToJsonString() ?? "");bool changed;
        lock (bindingGate) { if (generation != selectionGeneration) return;changed = scope != observedScope;observedScope = scope; }
        if (changed) Changed();
    }
    async Task<string?> CheckScope(JsonObject arguments, CancellationToken token)
    {
        JsonObject? selected;int generation;lock (bindingGate) { selected = binding?.DeepClone().AsObject();generation = selectionGeneration; }
        if (selected is null) return "no_engine_selected";
        var response = await Send(selected, "status", new(), token);
        lock (bindingGate) if (generation != selectionGeneration) return "scope_changed";
        if (response["ok"]?.GetValue<bool>() != true) return Text(response, "code");
        if (response["result"] is not JsonObject status) return "invalid_engine_response";Observe(status, generation);
        if (status["scope"] is not JsonObject scope) return "no_project_scope";
        return Text(scope, "id") == Text(arguments, "scopeId") && Text(scope, "projectId") == Text(arguments, "projectId") && Text(scope, "id").Length == 32 ? null : "scope_changed";
    }
    async Task<JsonObject> Call(string name, JsonObject arguments, string requestId, CancellationToken token)
    {
        if (name == "confectory_disconnect") { lock (bindingGate) { binding = null;selectionGeneration++; } Changed(); return ToolResult(new JsonObject { ["connected"] = false }); }
        if (name == "confectory_instances")
        {
            var rows = new JsonArray();var unavailable = new JsonArray();foreach (var descriptor in Discover())
            {
                var response = await Send(descriptor, "status", new(), token);
                if (response["ok"]?.GetValue<bool>() == true && response["result"] is JsonObject status) { status["instanceId"] = descriptor["instance"]!.DeepClone();rows.Add(status.DeepClone()); }
                else unavailable.Add(new JsonObject { ["instanceId"] = descriptor["instance"]!.DeepClone(), ["code"] = Text(response, "code") });
            }
            return rows.Count == 0 ? Failure(unavailable.Count == 0 ? "engine_not_running" : "engine_unavailable") : ToolResult(new JsonObject { ["instances"] = rows, ["unavailable"] = unavailable, ["selectionRequired"] = rows.Count > 1 });
        }
        if (name == "confectory_connect")
        {
            string id = Text(arguments, "instanceId");var descriptor = Discover().SingleOrDefault(d => Text(d, "instance") == id);
            if (descriptor is null) return Failure("instance_not_found");
            int generation;lock (bindingGate) { generation = ++selectionGeneration;binding = null; }
            var response = await Send(descriptor, "status", new(), token);if (response["ok"]?.GetValue<bool>() != true) return Failure(Text(response, "code"));
            lock (bindingGate) { if (generation != selectionGeneration) return Failure("scope_changed");binding = descriptor.DeepClone().AsObject();observedScope = ""; }Changed();return ToolResult(response["result"]);
        }
        JsonObject? selected;int selectedGeneration;lock (bindingGate) { selected = binding?.DeepClone().AsObject();selectedGeneration = selectionGeneration; }
        if (selected is null) return Failure("no_engine_selected");
        if (name == "confectory_status") { var status = await Send(selected, "status", new(), token);lock (bindingGate) if (selectedGeneration != selectionGeneration) return Failure("scope_changed");if (status["ok"]?.GetValue<bool>() == true && status["result"] is JsonObject observed) Observe(observed, selectedGeneration);return status["ok"]?.GetValue<bool>() == true ? ToolResult(status["result"]) : Failure(Text(status, "code")); }
        if (name is not ("workspace_list" or "workspace_read" or "workspace_inspect" or "workspace_stage" or "workspace_create" or "workspace_changes")) return Failure("operation_refused");
        string? scopeError = await CheckScope(arguments, token);if (scopeError is not null) return Failure(scopeError);
        var result = await Send(selected, "tools/call", new() { ["name"] = name, ["callId"] = client + ":" + Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(requestId))).ToLowerInvariant(), ["arguments"] = arguments.DeepClone() }, token);
        lock (bindingGate) if (selectedGeneration != selectionGeneration) return Failure(name is "workspace_stage" or "workspace_create" ? "write_outcome_unknown" : "scope_changed");
        if (result["ok"]?.GetValue<bool>() == true) { scopeError = await CheckScope(arguments, token);return scopeError is null ? ToolResult(result["result"]) : Failure(name is "workspace_stage" or "workspace_create" ? "write_outcome_unknown" : scopeError); }
        string code = Text(result, "code");return Failure((name is "workspace_stage" or "workspace_create") && (code is "engine_unavailable" or "invalid_engine_response") ? "write_outcome_unknown" : code);
    }
    IEnumerable<JsonObject> Discover()
    {
        if (!Directory.Exists(directory) || new DirectoryInfo(directory).LinkTarget is not null) yield break;
        if (!OperatingSystem.IsWindows() && (File.GetUnixFileMode(directory) & (UnixFileMode)63) != 0) yield break;
        foreach (string file in Directory.EnumerateFiles(directory, "*.json").Order(StringComparer.Ordinal).Take(8))
        {
            JsonObject? row = null;
            try
            {
                var info = new FileInfo(file);if (info.LinkTarget is not null || info.Length > 4096 || !Regex.IsMatch(Path.GetFileNameWithoutExtension(file), "^[a-f0-9]{32}$")) continue;
                row = JsonNode.Parse(File.ReadAllText(file))!.AsObject();
                if (row["schema"]?.GetValue<int>() != 1 || Text(row, "instance") != Path.GetFileNameWithoutExtension(file)) row = null;
                else if (Text(row, "transport") == "named-pipe") { if (!OperatingSystem.IsWindows() || Text(row, "address") != "confectory-mcp-" + Text(row, "instance")) row = null; }
                else if (Text(row, "transport") == "unix")
                {
                    string owner = Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile)))).ToLowerInvariant()[..16];
                    string expected = Path.Combine(Path.GetTempPath(), "confectory-mcp-" + owner, Text(row, "instance") + ".sock");if (Text(row, "address") != expected) row = null;
                }
                else row = null;
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or System.Text.Json.JsonException or InvalidOperationException or FormatException) { }
            if (row is not null) yield return row;
        }
    }
    static async Task<JsonObject> Send(JsonObject instance, string operation, JsonObject payload, CancellationToken token)
    {
        using var timeout = CancellationTokenSource.CreateLinkedTokenSource(token);timeout.CancelAfter(operation == "status" ? 2000 : 12000);
        try
        {
            Stream stream;
            if (Text(instance, "transport") == "named-pipe") { var pipe = new NamedPipeClientStream(".", Text(instance, "address"), PipeDirection.InOut, PipeOptions.Asynchronous | PipeOptions.CurrentUserOnly);try { await pipe.ConnectAsync(timeout.Token);stream = pipe; } catch { pipe.Dispose();throw; } }
            else { var socket = new Socket(AddressFamily.Unix, SocketType.Stream, ProtocolType.Unspecified);try { await socket.ConnectAsync(new UnixDomainSocketEndPoint(Text(instance, "address")), timeout.Token);stream = new NetworkStream(socket, true); } catch { socket.Dispose();throw; } }
            using (stream)
            {
                byte[] request = Encoding.UTF8.GetBytes(new JsonObject { ["instance"] = instance["instance"]!.DeepClone(), ["operation"] = operation, ["payload"] = payload }.ToJsonString() + "\n");if (request.Length > MaxFrame) throw new InvalidDataException();
                await stream.WriteAsync(request, timeout.Token);
                string? raw = await new FrameReader(stream).Read(timeout.Token);var result = JsonNode.Parse(raw ?? "") as JsonObject ?? throw new InvalidDataException();
                if (result["ok"] is not JsonValue ok || !ok.TryGetValue<bool>(out bool accepted) || accepted && !result.ContainsKey("result") || !accepted && result["code"] is not JsonValue) throw new InvalidDataException();
                return result;
            }
        }
        catch (OperationCanceledException) when (token.IsCancellationRequested) { throw; }
        catch (Exception ex) when (ex is System.Text.Json.JsonException or InvalidDataException or DecoderFallbackException or InvalidOperationException or FormatException) { return new() { ["ok"] = false, ["code"] = "invalid_engine_response" }; }
        catch (Exception ex) when (ex is IOException or SocketException or TimeoutException or OperationCanceledException or UnauthorizedAccessException) { return new() { ["ok"] = false, ["code"] = "engine_unavailable" }; }
    }
    sealed class FrameReader(Stream input)
    {
        readonly byte[] buffer = new byte[8192];int at, count;
        public async Task<string?> Read(CancellationToken token)
        {
            using var bytes = new MemoryStream();
            while (true)
            {
                if (at == count) { count = await input.ReadAsync(buffer, token);at = 0;if (count == 0) return bytes.Length == 0 ? null : throw new InvalidDataException("Truncated frame"); }
                int newline = Array.IndexOf(buffer, (byte)10, at, count-at), end = newline < 0 ? count : newline;
                if (bytes.Length + end-at > MaxFrame) throw new InvalidDataException("Frame budget");
                bytes.Write(buffer, at, end-at);at = newline < 0 ? count : newline+1;
                if (newline >= 0) return new UTF8Encoding(false, true).GetString(bytes.ToArray());
            }
        }
    }
    sealed class ProtocolException(int code, string message) : Exception(message) { public int Code { get; } = code; }
}
