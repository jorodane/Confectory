using Confectory.Core;
using System.Text.Json.Nodes;

// Read-only projection of explicit, already-owned draft texts. No registry traversal or execution.
internal static class RelationMapBatch
{
    public static JsonObject Query(JsonObject request)
    {
        // Transport grouping only: each batch still uses the exact existing
        // projection (including identity and malformed declaration diagnostics).
        if (request.ContainsKey("batches"))
        {
            if (request["batches"] is not JsonArray batches || request["units"] is not JsonArray empty || empty.Count != 0 ||
                batches.Count is < 2 or > 16 ||
                System.Text.Encoding.UTF8.GetByteCount(batches.ToJsonString()) > 1048576)
                throw new ArgumentException("Map source group budget");
            var groupedNodes = new JsonArray(); var groupedEdges = new JsonArray();
            foreach (var batch in batches)
            {
                if (batch is not JsonArray group || group.Count is < 1 or > 32)
                    throw new ArgumentException("Map source batch budget");
                var result = Query(new JsonObject { ["units"] = group.DeepClone() });
                foreach (var node in result["nodes"]!.AsArray()) groupedNodes.Add(node!.DeepClone());
                foreach (var edge in result["edges"]!.AsArray()) groupedEdges.Add(edge!.DeepClone());
            }
            return new JsonObject { ["nodes"] = groupedNodes, ["edges"] = groupedEdges,
                ["sourceWritten"] = false, ["executed"] = false, ["grouped"] = true };
        }
        var units = request["units"]?.AsArray() ?? throw new ArgumentException("Owned map source batch required");
        if (units.Count > 32) throw new ArgumentException("Map source batch budget");
        var nodes = new JsonArray(); var edges = new JsonArray();
        foreach (var source in units)
        {
            string id = source!["id"]!.GetValue<string>(), kind = source["kind"]!.GetValue<string>();
            var node = new JsonObject
            {
                ["id"] = id, ["kind"] = kind, ["title"] = id.Split("::").Last(),
                ["revision"] = source["revision"]!.DeepClone(), ["textHash"] = source["textHash"]!.DeepClone(),
                ["dirty"] = source["dirty"]!.DeepClone(), ["owned"] = true, ["valid"] = false
            };
            try
            {
                var element = new Parser(source["text"]!.GetValue<string>(), "<owned-map-draft>").ParseElement();
                if (element.Id != id || element.Kind != kind) throw new ArgumentException("Map declaration identity differs");
                if (element.Values.TryGetValue("editorName", out var label) && label.Value.ValueKind == System.Text.Json.JsonValueKind.String)
                    node["title"] = label.Value.GetString();
                if (element.Values.TryGetValue("editorIcon", out var icon) && icon.Value.ValueKind == System.Text.Json.JsonValueKind.String && icon.Value.GetString() is string iconText && (iconText.Length <= 64 || (element.Kind is "schema" or "object" or "function" or "category" or "concept" or "module" or "enum") && RasterIcon.IsImage(iconText))) node["icon"] = iconText;
                var folder=BrowserFolderLayout.Folder(element);node["folderDefined"]=folder.Defined;node["folder"]=folder.Id;node["browserGroup"]=BrowserFolderLayout.Group(element);
                node["description"] = element.Description;
                node["valid"] = true;
                foreach (var reference in DeclaredRelations.Describe(element)["edges"]!.AsArray())
                {
                    var edge = reference!.DeepClone().AsObject(); edge["source"] = id;
                    edges.Add(edge);
                }
            }
            catch (Exception error) when (error is BuildError or ArgumentException)
            {
                node["error"] = error is BuildError build ? build.Diagnostic.Code : "DECLARATION_IDENTITY";
            }
            nodes.Add(node);
        }
        return new JsonObject { ["nodes"] = nodes, ["edges"] = edges, ["sourceWritten"] = false, ["executed"] = false };
    }
}
