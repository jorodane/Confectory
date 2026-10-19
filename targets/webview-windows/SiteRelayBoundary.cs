using System.Text.Json.Nodes;

// Shared with portable boundary tests; the Site window uses this exact parser.
internal static class SiteRelayBoundary
{
    public const string Protocol = "confectory.editor.v1";
    public const string Address = "https://confectory-connect.jorodane.chatgpt.site/editor-bridge";
    public static bool Owned(string source) => Uri.TryCreate(source, UriKind.Absolute, out var uri) && uri.AbsoluteUri == Address;
    public static bool TryRead(string current, string source, string json, string nonce, bool helloSent, out JsonObject? message)
    {
        message = null;
        if (!Owned(current) || !Owned(source) || json.Length > 1572864) return false;
        try {
            var row = JsonNode.Parse(json)!.AsObject();
            if (row["protocol"]?.GetValue<string>() != Protocol) return false;
            foreach (var field in row) if (field.Key is not ("protocol" or "type" or "nonce" or "requestId" or "sessionId" or "expiresAt" or "job" or "hostWake")) return false;
            string type = row["type"]?.GetValue<string>() ?? "";
            if(row.ContainsKey("hostWake")&&(type!="paired"||row["hostWake"]?.GetValue<bool>()!=true))return false;
            if (type == "ready") { if (helloSent) return false; }
            else {
                if (!helloSent || row["nonce"]?.GetValue<string>() != nonce || type is not ("paired" or "pulse" or "dispatch" or "close")) return false;
                string requestId = row["requestId"]?.GetValue<string>() ?? "";
                if (requestId.Length is < 1 or > 128) return false;
            }
            message = row; return true;
        } catch { return false; }
    }
}
