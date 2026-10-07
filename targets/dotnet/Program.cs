using System.Diagnostics;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

// Compiler and packaging decisions belong to this target pack. The core only
// exchanges protocol-1 JSON requests with this executable.
try
{
    var request = JsonNode.Parse(Console.In.ReadToEnd())?.AsObject() ?? throw new InvalidOperationException("Expected a JSON request");
    Console.WriteLine(Target.Run(request).ToJsonString()); return 0;
}
catch (Exception ex)
{
    Console.WriteLine(JsonSerializer.Serialize(new { protocol = 1, ok = false, error = ex.Message })); return 1;
}

internal static class Target
{
    private sealed record Sdk(string DotNet, string Compiler, string[] Framework, string Runtime);
    private static string Hash(string path) => Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path))).ToLowerInvariant();
    private static string Required(JsonObject request, string key) => request[key]?.GetValue<string>() ?? throw new InvalidOperationException($"Missing {key}");
    private static string[] Strings(JsonObject request, string key) => request[key]?.AsArray().Select(x => x!.GetValue<string>()).ToArray() ?? [];
    private static Version VersionKey(string path) => Version.TryParse(Path.GetFileName(path), out var value) ? value : new Version(0, 0);
    private static string Resolve(string path)
    {
        var file = new FileInfo(Path.GetFullPath(path)); return file.ResolveLinkTarget(true)?.FullName ?? file.FullName;
    }
    private static Sdk FindSdk()
    {
        string? executable = Environment.GetEnvironmentVariable("CONFECTORY_DOTNET");
        if (string.IsNullOrEmpty(executable) && Environment.ProcessPath is string process && Path.GetFileNameWithoutExtension(process) == "dotnet") executable = process;
        if (string.IsNullOrEmpty(executable))
        {
            string filename = OperatingSystem.IsWindows() ? "dotnet.exe" : "dotnet";
            string? rootHint = Environment.GetEnvironmentVariable("DOTNET_ROOT");
            executable = rootHint is not null && File.Exists(Path.Combine(rootHint, filename)) ? Path.Combine(rootHint, filename) : null;
            executable ??= (Environment.GetEnvironmentVariable("PATH") ?? "").Split(Path.PathSeparator).Select(p => Path.Combine(p, filename)).FirstOrDefault(File.Exists);
        }
        if (string.IsNullOrEmpty(executable) || !File.Exists(executable)) throw new InvalidOperationException("Install the .NET 10 SDK or set CONFECTORY_DOTNET to its dotnet executable");
        string dotnet = Resolve(executable), root = Path.GetDirectoryName(dotnet)!;
        string sdkRoot = Path.Combine(root, "sdk");
        string? sdk = Directory.Exists(sdkRoot) ? Directory.EnumerateDirectories(sdkRoot, "10.*").Where(p => File.Exists(Path.Combine(p, "Roslyn", "bincore", "csc.dll"))).OrderBy(VersionKey).LastOrDefault() : null;
        if (sdk is null) throw new InvalidOperationException("The target pack requires an installed .NET 10 SDK, not only a runtime");
        string refsRoot = Path.Combine(root, "packs", "Microsoft.NETCore.App.Ref");
        string? refs = Directory.Exists(refsRoot) ? Directory.EnumerateDirectories(refsRoot, "10.*").OrderBy(VersionKey).LastOrDefault() : null;
        if (refs is null) throw new InvalidOperationException("The SDK has no .NET 10 reference pack");
        string[] framework = Directory.GetFiles(Path.Combine(refs, "ref", "net10.0"), "*.dll").Order(StringComparer.Ordinal).ToArray();
        string runtimeRoot = Path.Combine(root, "shared", "Microsoft.NETCore.App");
        string? runtime = Directory.Exists(runtimeRoot) ? Directory.EnumerateDirectories(runtimeRoot, "10.*").OrderBy(VersionKey).LastOrDefault() : null;
        if (framework.Length == 0 || runtime is null) throw new InvalidOperationException("The SDK has no complete .NET 10 references/runtime");
        return new(dotnet, Path.Combine(sdk, "Roslyn", "bincore", "csc.dll"), framework, runtime);
    }
    private static object[] FileHashes(IEnumerable<string> paths) => paths.Select(p => (object)new[] { Path.GetFileName(p), Hash(p) }).ToArray();
    public static JsonObject Run(JsonObject request)
    {
        if (request["protocol"]?.GetValue<int>() != 1) throw new InvalidOperationException("Unsupported target-tool protocol");
        var sdk = FindSdk(); string operation = Required(request, "operation"), mode = request["options"]?["mode"]?.GetValue<string>() ?? "portable";
        if (operation == "fingerprint")
        {
            var identity = new
            {
                version = 1, compiler = FileHashes(Directory.GetFiles(Path.GetDirectoryName(sdk.Compiler)!, "*.dll").Order(StringComparer.Ordinal)), framework = FileHashes(sdk.Framework),
                hostBinary = Hash(sdk.DotNet), runtime = new[] { Path.GetFileName(sdk.Runtime), Hash(Path.Combine(sdk.Runtime, "System.Private.CoreLib.dll")) },
                options = request["options"], flags = "C#12/deterministic/nullable/warnings-as-errors", host = mode == "linux" ? Environment.OSVersion.Platform.ToString() : "portable"
            };
            string fingerprint = Convert.ToHexString(SHA256.HashData(JsonSerializer.SerializeToUtf8Bytes(identity))).ToLowerInvariant();
            return JsonSerializer.SerializeToNode(new { protocol = 1, ok = true, fingerprint, sdk = Path.GetFileName(Path.GetDirectoryName(Path.GetDirectoryName(Path.GetDirectoryName(sdk.Compiler)))), framework = "net10.0", compiler = sdk.Compiler, mode })!.AsObject();
        }
        if (operation is not ("compile-contract" or "compile-pack" or "link")) throw new InvalidOperationException($"Unknown tool operation {operation}");
        return Compile(request, sdk, mode);
    }
    private static JsonObject Compile(JsonObject request, Sdk sdk, string mode)
    {
        string output = Path.GetFullPath(Required(request, "output")); Directory.CreateDirectory(output);
        string name = Required(request, "name"), assembly = Path.Combine(output, name + ".dll"), reference = Path.Combine(output, name + ".ref.dll");
        bool final = Required(request, "operation") == "link";
        string[] references = Strings(request, "references");
        var compilerArguments = new List<string> { "-nologo", "-nostdlib+", "-langversion:12", "-deterministic+", "-optimize+", "-nullable:enable", "-warnaserror+", final ? "-target:exe" : "-target:library", "-out:" + assembly };
        if (!final) compilerArguments.Add("-refout:" + reference);
        foreach (string path in sdk.Framework.Concat(references)) compilerArguments.Add("-reference:" + path);
        foreach (string source in Strings(request, "sources")) compilerArguments.Add(source);
        // Provider JSON already travels on stdin. Roslyn's reference-heavy argv
        // previously exceeded Windows CreateProcess's command-line limit.
        // Keep -noconfig outside the response file (Roslyn ignores it inside).
        string responsePath = Path.Combine(output, ".csc-" + Guid.NewGuid().ToString("N") + ".rsp");
        string QuoteResponse(string argument)
        {
            if (argument.IndexOfAny(new[] { '\r', '\n', '\0', '"' }) >= 0 || argument.EndsWith("\\", StringComparison.Ordinal))
                throw new ArgumentException("Compiler argument contains unsupported quote/newline/trailing slash; no response-file injection allowed");
            return "\"" + argument + "\"";
        }
        int expandedCharacters = sdk.DotNet.Length + sdk.Compiler.Length + 16 + compilerArguments.Sum(argument => argument.Length + 3);
        int launchCharacters = sdk.DotNet.Length + sdk.Compiler.Length + responsePath.Length + 24;
        try
        {
            File.WriteAllLines(responsePath, compilerArguments.Select(QuoteResponse), new UTF8Encoding(false));
            var start = new ProcessStartInfo(sdk.DotNet) { RedirectStandardOutput = true, RedirectStandardError = true, UseShellExecute = false };
            start.ArgumentList.Add(sdk.Compiler); start.ArgumentList.Add("-noconfig"); start.ArgumentList.Add("@" + responsePath);
            using var compiler = Process.Start(start) ?? throw new IOException("Could not start C# compiler");
            var stdout = compiler.StandardOutput.ReadToEndAsync(); var stderr = compiler.StandardError.ReadToEndAsync();
            if (!compiler.WaitForExit(90_000)) { compiler.Kill(true); compiler.WaitForExit(); throw new TimeoutException("C# compilation exceeded 90s"); }
            string compilerOutput = stdout.GetAwaiter().GetResult(), compilerError = stderr.GetAwaiter().GetResult();
            if (compiler.ExitCode != 0) throw new InvalidOperationException(compilerOutput.Trim() + "\n" + compilerError.Trim());
        }
        finally { if (File.Exists(responsePath)) File.Delete(responsePath); }
        var artifacts = new JsonObject();
        if (final) artifacts["application"] = assembly; else { artifacts["assembly"] = assembly; artifacts["reference"] = reference; }
        var result = new JsonObject { ["protocol"] = 1, ["ok"] = true, ["artifacts"] = artifacts, ["compilerTransport"] = new JsonObject { ["mode"] = "response-file", ["arguments"] = compilerArguments.Count, ["frameworkReferences"] = sdk.Framework.Length, ["projectReferences"] = references.Length, ["sources"] = Strings(request,"sources").Length, ["expandedCommandCharacters"] = expandedCharacters, ["launchCommandCharacters"] = launchCharacters, ["responseRemoved"] = !File.Exists(responsePath) } };
        if (!final) return result;
        foreach (string dependency in references)
        {
            string destination = Path.Combine(output, Path.GetFileName(dependency));
            if (File.Exists(destination) && Hash(destination) != Hash(dependency)) throw new InvalidOperationException($"Conflicting package artifact {Path.GetFileName(dependency)}");
            File.Copy(dependency, destination, true);
        }
        string config = Path.Combine(output, name + ".runtimeconfig.json");
        File.WriteAllText(config, JsonSerializer.Serialize(new { runtimeOptions = new { tfm = "net10.0", framework = new { name = "Microsoft.NETCore.App", version = "10.0.0" }, rollForward = "LatestPatch" } }, new JsonSerializerOptions { WriteIndented = true }) + "\n", new UTF8Encoding(false));
        artifacts["runtimeconfig"] = config;
        foreach (var resource in request["resources"]?.AsArray() ?? [])
        {
            string source = resource!["path"]!.GetValue<string>(), resourceName = resource["name"]!.GetValue<string>(), destination = Path.Combine(output, resourceName);
            if (source != destination) File.Copy(source, destination, true);
            if (resourceName == "public-linkage.json") artifacts["publicCatalog"] = destination;
        }
        result["run"] = new JsonArray(sdk.DotNet, assembly);
        if (mode == "linux")
        {
            if (!OperatingSystem.IsLinux()) throw new InvalidOperationException("The Linux launcher profile requires a Linux build host in this first tool pack");
            string launcher = Path.Combine(output, "run");
            File.WriteAllText(launcher, "#!/bin/sh\nexec \"${CONFECTORY_DOTNET:-dotnet}\" \"$(dirname \"$0\")/Confectory.App.dll\" \"$@\"\n", new UTF8Encoding(false));
            File.SetUnixFileMode(launcher, UnixFileMode.UserRead | UnixFileMode.UserWrite | UnixFileMode.UserExecute | UnixFileMode.GroupRead | UnixFileMode.GroupExecute | UnixFileMode.OtherRead | UnixFileMode.OtherExecute);
            artifacts["launcher"] = launcher; result["run"] = new JsonArray(launcher);
        }
        else if (mode != "portable") throw new InvalidOperationException($"Unsupported packaging mode {mode}");
        return result;
    }
}
