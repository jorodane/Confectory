using System.Security.Cryptography;
using System.Text;
using System.Text.Json.Nodes;

internal static class OpeningViewReviewOrigin
{
    internal static JsonObject Read(string project, JsonObject request, Func<string, string> scope)
    {
        string projectId = request["projectId"]!.GetValue<string>();
        string id = request["id"]!.GetValue<string>();
        string text = request["text"]!.GetValue<string>();
        if (projectId.Length is <1 or >128 || id.Length is <1 or >512 || text.Length > 1048576)
            throw new ArgumentException("Bounded review origin required.");

        var result = new JsonObject();
        string root = Path.GetDirectoryName(project)!;
        string metadata = Path.Combine(root, ".confectory");
        string directory = Path.Combine(metadata, "draft-origins");
        if (!Directory.Exists(directory) || new DirectoryInfo(directory).LinkTarget is not null ||
            new DirectoryInfo(metadata).LinkTarget is not null) return result;
        string hash = Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(text))).ToLowerInvariant();
        var origins = new HashSet<(string Task, string Worker)>();
        long bytes = 0;
        var manifests = OperatingSystem.IsWindows() ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal;
        var files = Directory.EnumerateFiles(directory, "*.json").Take(257).ToArray();
        if (files.Length > 256) return result;
        foreach (string file in files)
        {
            if (!Guid.TryParseExact(Path.GetFileNameWithoutExtension(file), "N", out _)) continue;
            if (new FileInfo(file).LinkTarget is not null) continue;
            using var stream = File.OpenRead(scope(file));
            long size = stream.Length;
            bytes += size;
            if (size > 1048576 || bytes > 4194304) return result;
            var snapshot = new byte[(int)size];
            stream.ReadExactly(snapshot);
            if (stream.ReadByte() != -1) return result;
            var journal = JsonNode.Parse(snapshot);
            if (journal?["schema"]?.ToString() != "1" || journal["projectId"]?.ToString() != projectId ||
                !string.Equals(journal["manifest"]?.ToString(), project, manifests)) continue;
            string? ns = journal["namespace"]?.ToString();
            if (string.IsNullOrEmpty(ns) || !id.StartsWith(ns + "::", StringComparison.Ordinal)) continue;
            foreach (var row in journal["changes"]?.AsArray() ?? new JsonArray())
            {
                if (row?["id"]?.ToString() != id || row["state"]?.ToString() != "applied" ||
                    row["operation"]?.ToString() != "workspace_stage" ||
                    row["proposedHash"]?.ToString() != hash ||
                    row["origin"] is not JsonObject origin || origin["known"]?.GetValue<bool>() != true ||
                    origin["projectId"]?.ToString() != projectId ||
                    origin["task"]?.ToString() is not { Length: > 0 and <= 128 } task ||
                    origin["worker"]?.ToString() is not { Length: > 0 and <= 128 } worker ||
                    row["observed"] is not JsonArray observed ||
                    !observed.Any(item => item?["id"]?.ToString() == id && item["observedHash"]?.ToString() == hash))
                    continue;
                origins.Add((task, worker));
            }
        }

        if (origins.Count == 1)
        {
            var (task, worker) = origins.Single();
            result["origin"] = new JsonObject { ["task"] = task, ["worker"] = worker };
        }
        return result;
    }
}
