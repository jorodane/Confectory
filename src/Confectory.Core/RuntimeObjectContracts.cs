using System.Text.Json.Nodes;

namespace Confectory.Core;

// A type/field description for caller-owned live values. Never reads declaration
// data as runtime values, creates an instance, selects an accessor or runs a getter.
public static class RuntimeObjectContracts
{
    public const string ReferenceProfile = "information-object-reference-v1";
    public static JsonObject Describe(Registry registry, string id, string? source = null) => DescribeCore(registry, id, source, false);
    public static JsonObject DescribeReference(Registry registry, string id, string? source = null) => DescribeCore(registry, id, source, true);
    static JsonObject DescribeCore(Registry registry, string id, string? source, bool reference)
    {
        var declared = registry.Get(id, source: source);
        if (reference ? declared.Kind != "schema" : declared.Kind is not ("object" or "concept")) throw new BuildError("PROPERTY_OWNER", reference ? "An information definition is required" : "An object/concept declaration is required", declared.Loc);
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
        void AddField(string name, SchemaField field, SourceLocation location)
        {
            if (fields.TryGetValue(name, out var prior) && prior.Origin != field.Origin) throw new BuildError("SCHEMA_AMBIGUITY", "Property field has multiple schema origins: " + name, location);
            fields[name] = field;
            if (field.Kind is "reference" or "compound") {
                registry.Get(field.Type, "schema", field.Origin, field.Loc);
                Ancestors(field.Type, "schema", _ => { });
            }
            else if (field.Kind is "function" or "enum") dependencies.Add(registry.Get(field.Type, field.Kind, field.Origin, field.Loc).Id);
        }
        if (reference) foreach (var (name, field) in effective.Fields) AddField(name, field, declared.Loc);
        else foreach (var use in effective.Uses.Where(u => u.Kind == "schema"))
        {
            registry.Get(use.Id, "schema", use.Origin ?? id, use.Loc);
            Ancestors(use.Id, "schema", e => schemas.Add(e.Id));
            foreach (var (name, field) in registry.Effective(use.Id).Fields) AddField(name, field, use.Loc);
        }
        if (fields.Count > 256) throw new BuildError("PROPERTY_FIELD_BUDGET", "At most 256 effective property fields", declared.Loc);
        var rows = new JsonArray();
        foreach (var (name, field) in fields.OrderBy(p => p.Key, StringComparer.Ordinal))
        {
            string type = field.Kind == "general" ? field.Type : "object";
            bool supported = field.Kind is "general" or "reference";
            InformationStructs.Definition? nativeEnum = null;
            InformationStructs.Definition? nativeStruct = null;
            IReadOnlyList<InformationStructs.Definition>? structTypes = null;
            JsonObject? nativeFunction = null;
            if (field.Kind == "function") {
                try {
                    var selected = RuntimeFunctionContracts.Describe(registry, field); nativeFunction = selected.Contract; supported = true;
                    dependencies.UnionWith(selected.Dependencies);
                }
                catch (BuildError error) when (error.Diagnostic.Code is "INFORMATION_CLR_FIELD" or "INFORMATION_CLR_MEMBER" or "INFORMATION_CLR_CYCLE" or "ENUM_CLR_MAPPING" or "MODULE_CLR_PROFILE") {
                    // A currently unrepresentable native method type retains
                    // the existing unsupported field; never infer a provider.
                }
            }
            if (field.Kind == "enum") {
                try { nativeEnum = InformationStructs.Describe(registry, field.Type, field.Origin); type = nativeEnum.ClrType; supported = true; }
                catch (BuildError error) when (error.Diagnostic.Code == "ENUM_CLR_MAPPING") { /* Unconverted IDs remain unsupported, never assign numbers here. */ }
            }
            if (field.Kind == "compound") {
                try {
                    structTypes = InformationStructs.Closure(registry, field.Type, field.Origin, includeFunctionFields: false);
                    nativeStruct = structTypes.Single(d => d.Id == field.Type);
                    type = nativeStruct.ClrType; supported = true;
                    foreach (var definition in structTypes) {
                        if (definition.Kind == "schema") Ancestors(definition.Id, "schema", _ => { });
                        else dependencies.Add(definition.Id);
                    }
                }
                catch (BuildError error) when (error.Diagnostic.Code is "INFORMATION_CLR_FIELD" or "INFORMATION_CLR_MEMBER" or "ENUM_CLR_MAPPING") {
                    // A live reference/function field is not a native value.
                    // Keep the old unsupported descriptor; never drop a member.
                    nativeStruct = null; structTypes = null;
                }
            }
            var row = new JsonObject
            {
                ["id"] = field.Origin + "/field:" + name, ["name"] = name, ["origin"] = field.Origin,
                ["kind"] = field.Kind, ["cardinality"] = field.Cardinality, ["type"] = field.Type,
                ["clrType"] = field.Kind == "enum" && nativeEnum is null ? null : type + (field.Cardinality == "multiple" ? "[]" : ""), ["supported"] = supported
            };
            if (nativeEnum is not null) row["nativeEnum"] = new JsonObject {
                ["profile"] = InformationEnums.Profile, ["clrType"] = nativeEnum.ClrType,
                ["assembly"] = "Information_" + Generation.Symbol(PackPaths.Namespace(field.Type)), ["shapeHash"] = nativeEnum.ShapeHash,
                ["members"] = new JsonArray(nativeEnum.Members!.OrderBy(m => m!["id"]!.ToString(), StringComparer.Ordinal).Select(m => (JsonNode)new JsonObject {
                    ["id"] = m!["id"]!.DeepClone(), ["value"] = m["value"]!.DeepClone(), ["clrMember"] = m["clrMember"]!.DeepClone()
                }).ToArray())
            };
            if (nativeFunction is not null) row["nativeFunction"] = nativeFunction;
            if (nativeStruct is not null) row["nativeStruct"] = new JsonObject {
                ["profile"] = "information-struct-live-value-v1", ["clrType"] = nativeStruct.ClrType,
                ["types"] = new JsonArray(structTypes!.Select(d => {
                    var item = new JsonObject { ["id"] = d.Id, ["kind"] = d.Kind, ["clrType"] = d.ClrType,
                        ["assembly"] = "Information_" + Generation.Symbol(PackPaths.Namespace(d.Id)), ["shapeHash"] = d.ShapeHash,
                        ["fields"] = System.Text.Json.JsonSerializer.SerializeToNode(d.Fields, JsonData.Options) };
                    if (d.Kind == "enum") item["members"] = new JsonArray(d.Members!.OrderBy(m => m!["id"]!.ToString(), StringComparer.Ordinal).Select(m => (JsonNode)new JsonObject {
                        ["id"] = m!["id"]!.DeepClone(), ["value"] = m["value"]!.DeepClone(), ["clrMember"] = m["clrMember"]!.DeepClone()
                    }).ToArray());
                    return (JsonNode)item;
                }).ToArray())
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
        if (reference) {
            result.Remove("schemas"); result["profile"] = ReferenceProfile;
        }
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
        foreach (string owner in BlueprintTree.Nodes(graph).Where(e => FeatureBlueprint.IsPropertyNode(e.Node["kind"]?.ToString())).Select(e => e.Node["propertyOwner"]!.GetValue<string>()).Distinct(StringComparer.Ordinal))
        {
            try { contracts[owner] = Describe(registry, owner, implementation); }
            catch (BuildError error) when (tolerate)
            { contracts[owner] = new JsonObject { ["id"] = owner, ["fields"] = new JsonArray(), ["error"] = error.Diagnostic.Code, ["message"] = error.Message, ["dependencies"] = new JsonArray() }; }
        }
        return contracts;
    }
}
