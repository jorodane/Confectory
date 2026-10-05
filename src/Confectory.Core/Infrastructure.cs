using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Text.Encodings.Web;
using System.Text.Json;
using System.Text.Json.Nodes;

namespace Confectory.Core;

public static class JsonData
{
    public static JsonSerializerOptions Options { get; } = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping,
        WriteIndented = true
    };
    public static JsonObject Object(object value) => JsonSerializer.SerializeToNode(value, Options)!.AsObject();
    public static T Clone<T>(T value) => JsonSerializer.Deserialize<T>(JsonSerializer.Serialize(value, Options), Options)!;
    public static string HashBytes(byte[] bytes) => Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
    public static string Digest(object? value)
    {
        if (value is byte[] bytes) return HashBytes(bytes);
        var element = JsonSerializer.SerializeToElement(value, Options);
        using var stream = new MemoryStream();
        using (var writer = new Utf8JsonWriter(stream, new() { Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping })) WriteCanonical(writer, element);
        return HashBytes(stream.ToArray());
    }
    private static void WriteCanonical(Utf8JsonWriter writer, JsonElement value)
    {
        if (value.ValueKind == JsonValueKind.Object)
        {
            writer.WriteStartObject();
            foreach (var item in value.EnumerateObject().OrderBy(x => x.Name, StringComparer.Ordinal))
            {
                writer.WritePropertyName(item.Name); WriteCanonical(writer, item.Value);
            }
            writer.WriteEndObject();
        }
        else if (value.ValueKind == JsonValueKind.Array)
        {
            writer.WriteStartArray(); foreach (var item in value.EnumerateArray()) WriteCanonical(writer, item); writer.WriteEndArray();
        }
        else value.WriteTo(writer);
    }
    public static void AtomicWrite(string path, object data)
    {
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        string temp = path + $".{Environment.ProcessId}.{Guid.NewGuid():N}.tmp";
        try
        {
            File.WriteAllText(temp, JsonSerializer.Serialize(data, Options) + "\n", new UTF8Encoding(false));
            File.Move(temp, path, true);
        }
        finally { if (File.Exists(temp)) File.Delete(temp); }
    }
}

public static class PackPaths
{
    // Resolve each existing component, including directory symlinks. GetFullPath
    // alone would accept a path whose lexical prefix is owned but whose target is not.
    public static string Resolve(string path)
    {
        string full = Path.GetFullPath(path), current = Path.GetPathRoot(full)!;
        foreach (string component in full[current.Length..].Split(Path.DirectorySeparatorChar, StringSplitOptions.RemoveEmptyEntries))
        {
            current = Path.Combine(current, component);
            FileSystemInfo info = Directory.Exists(current) ? new DirectoryInfo(current) : new FileInfo(current);
            if (info.LinkTarget is not null) current = info.ResolveLinkTarget(true)!.FullName;
        }
        return current;
    }
    public static string Owned(string root, string path, SourceLocation? loc = null)
    {
        string resolvedRoot = Resolve(root), resolved = Resolve(Path.Combine(resolvedRoot, path));
        string relative = Path.GetRelativePath(resolvedRoot, resolved);
        if (Path.IsPathRooted(relative) || relative == ".." || relative.StartsWith(".." + Path.DirectorySeparatorChar, StringComparison.Ordinal))
            throw new BuildError("OWNERSHIP", $"Path escapes its owning pack: {path}", loc);
        return resolved;
    }
    public static string Namespace(string id) => id.Split("::", StringSplitOptions.None)[0];
}

public sealed class BuildStatistics
{
    public List<string> ReadDocuments { get; set; } = [];
    public List<string> ParsedDocuments { get; set; } = [];
    public List<string> CheckedContracts { get; set; } = [];
    public List<string> CompiledContracts { get; set; } = [];
    public List<string> ReusedContracts { get; set; } = [];
    public List<string> CompiledPacks { get; set; } = [];
    public List<string> ReusedPacks { get; set; } = [];
    public List<string> CompiledImplementations { get; set; } = [];
    public List<string> ReusedImplementations { get; set; } = [];
    public Dictionary<string, int> TargetInvocations { get; set; } = new(StringComparer.Ordinal);
    public int FullRebuilds { get; set; }
}

internal static class ChangeStamp
{
    [StructLayout(LayoutKind.Explicit, Size = 256)]
    private struct Statx
    {
        [FieldOffset(0)] public uint Mask;
        [FieldOffset(32)] public ulong Inode;
        [FieldOffset(40)] public ulong Size;
        [FieldOffset(96)] public long ChangeSeconds;
        [FieldOffset(104)] public uint ChangeNanoseconds;
        [FieldOffset(112)] public long ModifiedSeconds;
        [FieldOffset(120)] public uint ModifiedNanoseconds;
        [FieldOffset(136)] public uint DeviceMajor;
        [FieldOffset(140)] public uint DeviceMinor;
    }
    [DllImport("libc", EntryPoint = "statx", SetLastError = true)]
    private static extern int ReadStatx(int directory, [MarshalAs(UnmanagedType.LPUTF8Str)] string path, int flags, uint mask, out Statx stat);

    public static string? Read(string path)
    {
        if (!File.Exists(path)) throw new BuildError("MISSING_FILE", $"Cannot read {path}", new(path));
        if (OperatingSystem.IsLinux())
        {
            try
            {
                if (ReadStatx(-100, path, 0, 0x7ff, out var s) == 0 && (s.Mask & 0x3c0) == 0x3c0)
                    return $"{s.ModifiedSeconds}:{s.ModifiedNanoseconds}:{s.ChangeSeconds}:{s.ChangeNanoseconds}:{s.Size}:{s.Inode}:{s.DeviceMajor}:{s.DeviceMinor}";
            }
            catch (EntryPointNotFoundException) { }
            catch (DllNotFoundException) { }
        }
        // Without a reliable change time, hash the requested document rather than
        // trust mtime/size. Restoring mtime must never revive stale declarations.
        return null;
    }
}

public sealed class Documents(string cache, BuildStatistics statistics)
{
    private const string Format = "csharp-declarations-v1";
    private T Read<T>(string input, string role, Func<string, string, T> parse)
    {
        string path = PackPaths.Resolve(input);
        string? stamp = ChangeStamp.Read(path);
        string cacheFile = Path.Combine(cache, JsonData.Digest(new[] { Format, path, role }) + ".json");
        try
        {
            var cached = JsonNode.Parse(File.ReadAllText(cacheFile))!.AsObject();
            if (stamp is not null && cached["stamp"]?.GetValue<string>() == stamp && cached["checksum"]?.GetValue<string>() == JsonData.Digest(cached["data"]))
                return cached["data"]!.Deserialize<T>(JsonData.Options)!;
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or JsonException or InvalidOperationException or KeyNotFoundException or FormatException) { }
        byte[] raw; string text;
        try { raw = File.ReadAllBytes(path); text = new UTF8Encoding(false, true).GetString(raw); }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or DecoderFallbackException)
        { throw new BuildError("SOURCE_READ", $"Cannot read UTF-8 source {path}: {ex.Message}", new(path)); }
        statistics.ReadDocuments.Add(path);
        T data = parse(text, path);
        if (role != "body") statistics.ParsedDocuments.Add(path);
        JsonData.AtomicWrite(cacheFile, new { stamp, contentHash = JsonData.HashBytes(raw), checksum = JsonData.Digest(data), data });
        return data;
    }
    public Manifest Manifest(string path) => Read(path, "manifest", (text, p) => new Parser(text, p).ParseManifest());
    public Element Element(string path) => Read(path, "element", (text, p) => new Parser(text, p).ParseElement());
    public string Body(string path) => Read(path, "body", (text, _) => text);
}

public sealed record ProcessResult(int ExitCode, string Stdout, string Stderr);

public static class Processes
{
    public static string DotNet()
    {
        string? configured = Environment.GetEnvironmentVariable("CONFECTORY_DOTNET");
        if (!string.IsNullOrEmpty(configured)) return PackPaths.Resolve(configured);
        if (Environment.ProcessPath is string process && Path.GetFileNameWithoutExtension(process) == "dotnet") return PackPaths.Resolve(process);
        string filename = OperatingSystem.IsWindows() ? "dotnet.exe" : "dotnet";
        string? root = Environment.GetEnvironmentVariable("DOTNET_ROOT");
        if (!string.IsNullOrEmpty(root) && File.Exists(Path.Combine(root, filename))) return PackPaths.Resolve(Path.Combine(root, filename));
        foreach (string part in (Environment.GetEnvironmentVariable("PATH") ?? "").Split(Path.PathSeparator))
            if (File.Exists(Path.Combine(part, filename))) return PackPaths.Resolve(Path.Combine(part, filename));
        throw new BuildError("TOOL_EXECUTION", "Install .NET 8 or set CONFECTORY_DOTNET to its dotnet executable");
    }
    public static ProcessResult Run(IReadOnlyList<string> command, string? input = null, string? directory = null, int timeoutSeconds = 120)
        => RunAsync(command, input, directory, timeoutSeconds).GetAwaiter().GetResult();
    private static async Task<ProcessResult> RunAsync(IReadOnlyList<string> command, string? input, string? directory, int timeoutSeconds)
    {
        var start = new ProcessStartInfo(command[0]) { RedirectStandardInput = true, RedirectStandardOutput = true, RedirectStandardError = true, UseShellExecute = false };
        if (directory is not null) start.WorkingDirectory = directory;
        foreach (string arg in command.Skip(1)) start.ArgumentList.Add(arg);
        start.Environment["DOTNET_CLI_TELEMETRY_OPTOUT"] = "1";
        start.Environment["DOTNET_SKIP_FIRST_TIME_EXPERIENCE"] = "1";
        using var process = Process.Start(start) ?? throw new IOException("Could not start target tool");
        using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(timeoutSeconds));
        var stdout = process.StandardOutput.ReadToEndAsync(timeout.Token);
        var stderr = process.StandardError.ReadToEndAsync(timeout.Token);
        try
        {
            if (input is not null) await process.StandardInput.WriteAsync(input.AsMemory(), timeout.Token);
            process.StandardInput.Close();
            await process.WaitForExitAsync(timeout.Token);
            return new(process.ExitCode, await stdout, await stderr);
        }
        catch (OperationCanceledException)
        {
            if (!process.HasExited) process.Kill(true);
            await process.WaitForExitAsync();
            throw new TimeoutException($"Process exceeded {timeoutSeconds}s: {command[0]}");
        }
    }
}
