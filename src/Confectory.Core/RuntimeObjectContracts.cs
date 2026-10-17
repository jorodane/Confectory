using System.Text.Json.Nodes;

namespace Confectory.Core;

// A type/field description for caller-owned live values. Never reads declaration
// data as runtime values, creates an instance, selects an accessor or runs a getter.
public static class RuntimeObjectContracts
{
    public static JsonObject Describe(Registry registry, string id, string? source = null)
    {
        var declared = registry.Get(id, source: source);
        if (declared.Kind is not ("object" or "concept")) throw new BuildError("PROPERTY_OWNER", "An object/concept declaration is required", declared.Loc);
        var dependencies = new HashSet<string>(StringComparer.Ordinal);
        var lineage = new JsonArray(); var schemas = new HashSet<string>(StringComparer.Ordinal);
        void Ancestors(string current, string kind, Action<Element> visit)
        {
            var seen = new HashSet<string>(StringComparer.Ordinal);
            while (true)
            {
                if (!seen.Add(current) || seen.Count > 64) throw new BuildError("PROPERTY_TYPE_CYCLE", "Bounded acyclic type inheritance required", declared.Loc);
                var element = registry.Get(current, kind);
                dependencies.Add(current); visit(element);
                if (element.Parent is null) break;
                registry.Get(element.Parent, kind, element.Id, element.Loc);
                current = element.Parent;
            }
        }
        Ancestors(id, declared.Kind, e => lineage.Add(e.Id));
        var effective = registry.Effective(id);
        var fields = new Dictionary<string, SchemaField>(StringComparer.Ordinal);
        foreach (var use in effective.Uses.Where(u => u.Kind == "schema"))
        {
            registry.Get(use.Id, "schema", use.Origin ?? id, use.Loc);
            Ancestors(use.Id, "schema", e => schemas.Add(e.Id));
            foreach (var (name, field) in registry.Effective(use.Id).Fields)
            {
                if (fields.TryGetValue(name, out var prior) && prior.Origin != field.Origin) throw new BuildError("SCHEMA_AMBIGUITY", "Property field has multiple schema origins: " + name, use.Loc);
                fields[name] = field;
                if (field.Kind is "reference" or "compound")
                {
                    registry.Get(field.Type, "schema", field.Origin, field.Loc);
                    Ancestors(field.Type, "schema", _ => { });
                }
                else if (field.Kind == "function") dependencies.Add(registry.Get(field.Type, "function", field.Origin, field.Loc).Id);
            }
        }
        if (fields.Count > 256) throw new BuildError("PROPERTY_FIELD_BUDGET", "At most 256 effective property fields", declared.Loc);
        var rows = new JsonArray();
        foreach (var (name, field) in fields.OrderBy(p => p.Key, StringComparer.Ordinal))
        {
            string type = field.Kind == "general" ? field.Type : "object";
            bool supported = field.Kind is "general" or "reference";
            var row = new JsonObject
            {
                ["id"] = field.Origin + "/field:" + name, ["name"] = name, ["origin"] = field.Origin,
                ["kind"] = field.Kind, ["cardinality"] = field.Cardinality, ["type"] = field.Type,
                ["clrType"] = type + (field.Cardinality == "multiple" ? "[]" : ""), ["supported"] = supported
            };
            row["hash"] = JsonData.Digest(row);
            rows.Add(row);
        }
        var result = new JsonObject
        {
            ["schema"] = 1, ["id"] = id, ["kind"] = declared.Kind, ["lineage"] = lineage,
            ["schemas"] = new JsonArray(schemas.Order(StringComparer.Ordinal).Select(x => (JsonNode)JsonValue.Create(x)!).ToArray()),
            ["fields"] = rows, ["dependencies"] = new JsonArray(dependencies.Order(StringComparer.Ordinal).Select(x => (JsonNode)JsonValue.Create(x)!).ToArray())
        };
        result["hash"] = JsonData.Digest(result);
        return result;
    }

    public static void ApplyOwnedDrafts(Registry registry, JsonObject? drafts)
    {
        if (drafts is null) return;
        if (drafts.Count > 64) throw new ArgumentException("Property declaration source budget");
        int bytes = 0;
        foreach (var pair in drafts)
        {
            string text = pair.Value!.GetValue<string>();
            bytes = checked(bytes + System.Text.Encoding.UTF8.GetByteCount(text));
            if (bytes > 2097152 || PackPaths.Namespace(pair.Key) != registry.Project.Namespace) throw new ArgumentException("Owned bounded property declarations required");
            var original = registry.Get(pair.Key);
            var parsed = new Parser(text, original.Loc.File).ParseElement();
            if (parsed.Id != pair.Key || parsed.Kind != original.Kind || parsed.Kind is not ("object" or "concept" or "schema")) throw new ArgumentException("Published property declaration identity required");
            registry.Elements[pair.Key] = parsed;
        }
    }

    public static JsonObject ForGraph(Registry registry, string implementation, JsonObject graph, bool tolerate = false)
    {
        var contracts = new JsonObject();
        foreach (string owner in BlueprintTree.Nodes(graph).Where(e => e.Node["kind"]?.ToString() == "property").Select(e => e.Node["propertyOwner"]!.GetValue<string>()).Distinct(StringComparer.Ordinal))
        {
            try { contracts[owner] = Describe(registry, owner, implementation); }
            catch (BuildError error) when (tolerate)
            { contracts[owner] = new JsonObject { ["id"] = owner, ["fields"] = new JsonArray(), ["error"] = error.Diagnostic.Code, ["message"] = error.Message, ["dependencies"] = new JsonArray() }; }
        }
        return contracts;
    }
}
