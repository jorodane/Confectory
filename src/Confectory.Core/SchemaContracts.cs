using System.Text.Json;

namespace Confectory.Core;

/// <summary>Schema metadata validation. It never selects providers or executes field functions.</summary>
public static class SchemaContracts
{
    public static Dictionary<string, SchemaField> Fields(Registry registry, string objectId)
    {
        var e = registry.Effective(registry.Get(objectId, "object").Id);
        Dictionary<string, SchemaField> fields = new(StringComparer.Ordinal);
        foreach (var use in e.Uses.Where(x => x.Kind == "schema"))
        {
            var schema = registry.Effective(registry.Get(use.Id, "schema", use.Origin ?? e.Id, use.Loc).Id);
            foreach (var (name, field) in schema.Fields)
            {
                if (fields.TryGetValue(name, out var prior) && prior.Origin != field.Origin)
                    throw new BuildError("SCHEMA_AMBIGUITY", $"Field {name} has multiple schema declarations; no implicit merge is defined", use.Loc);
                fields[name] = field;
            }
        }
        return fields;
    }

    public static List<ElementReference> Validate(Registry registry, string id)
    {
        var e = registry.Effective(id);
        List<ElementReference> references = [];
        if (e.Kind == "schema") ValidateFields(e.Fields);
        if (e.Kind == "object") ValidateMembers(Fields(registry, id), e.Data);
        return references;

        void ValidateFields(Dictionary<string, SchemaField> fields)
        {
            foreach (var field in fields.Values.Where(f => f.Kind != "general"))
            {
                string kind = field.Kind == "function" ? "function" : "schema";
                registry.Get(field.Type, kind, field.Origin, field.Loc);
                references.Add(new(field.Type, field.Loc, field.Origin, kind));
            }
        }
        void ValidateMembers(Dictionary<string, SchemaField> fields, Dictionary<string, SchemaDatum> members)
        {
            ValidateFields(fields);
            foreach (var (name, datum) in members)
            {
                if (!fields.TryGetValue(name, out var field)) throw new BuildError("SCHEMA_UNKNOWN_FIELD", $"Data field {name} is not declared by an applied schema", datum.Loc);
                if (field.Cardinality == "multiple")
                {
                    if (datum.Kind != "multiple") Mismatch(name, datum);
                    foreach (var item in datum.Items!) ValidateSingle(name, field, item);
                }
                else ValidateSingle(name, field, datum);
            }
        }
        void ValidateSingle(string name, SchemaField field, SchemaDatum datum)
        {
            switch (field.Kind)
            {
                case "general":
                    if (datum.Kind != "general" || datum.Scalar is not JsonElement scalar || !Primitive(field.Type, scalar)) Mismatch(name, datum);
                    break;
                case "compound":
                    if (datum.Kind != "compound") Mismatch(name, datum);
                    ValidateMembers(registry.Effective(field.Type).Fields, datum.Members!);
                    break;
                case "reference":
                    if (datum.Kind != "reference") Mismatch(name, datum);
                    var target = registry.Effective(registry.Get(datum.Reference!, "object", datum.Origin, datum.Loc).Id);
                    if (!target.Uses.Any(u => u.Kind == "schema" && IsSchema(u.Id, field.Type)))
                        throw new BuildError("SCHEMA_REFERENCE", $"{target.Id} does not apply {field.Type} or a derived schema", datum.Loc);
                    references.Add(new(target.Id, datum.Loc, datum.Origin, "object"));
                    break;
                case "function":
                    if (datum.Kind != "reference") Mismatch(name, datum);
                    registry.Implementation(field.Type, datum.Reference!, datum.Origin, datum.Loc);
                    references.Add(new(datum.Reference!, datum.Loc, datum.Origin, "implementation"));
                    break;
            }
        }
        bool IsSchema(string current, string required)
        {
            HashSet<string> seen = new(StringComparer.Ordinal);
            while (seen.Add(current)) { if (current == required) return true; var schema = registry.Get(current, "schema"); if (schema.Parent is null) return false; current = schema.Parent; }
            registry.Effective(current); return false;
        }
    }
    private static void Mismatch(string name, SchemaDatum datum) => throw new BuildError("SCHEMA_TYPE", $"Data field {name} does not match its declared type/cardinality", datum.Loc);
    private static bool Primitive(string type, JsonElement value) => type switch
    {
        "string" => value.ValueKind == JsonValueKind.String,
        "bool" => value.ValueKind is JsonValueKind.True or JsonValueKind.False,
        "int" => value.ValueKind == JsonValueKind.Number && value.TryGetInt32(out _),
        "long" => value.ValueKind == JsonValueKind.Number && value.TryGetInt64(out _),
        "float" => value.ValueKind == JsonValueKind.Number && value.TryGetSingle(out var f) && float.IsFinite(f),
        "double" => value.ValueKind == JsonValueKind.Number && value.TryGetDouble(out var d) && double.IsFinite(d),
        _ => false
    };

    public static string FormatDeclarations(Element element) =>
        string.Concat(element.Fields.Select(p => $"field {p.Key} {p.Value.Cardinality} {p.Value.Kind} {p.Value.Type};\n")) +
        string.Concat(element.Data.Select(p => $"data {p.Key} = {FormatDatum(p.Value)};\n"));
    public static string FormatDatum(SchemaDatum datum) => datum.Kind switch
    {
        "general" => datum.Scalar!.Value.GetRawText(),
        "reference" => datum.Reference!,
        "multiple" => "[" + string.Join(", ", datum.Items!.Select(FormatDatum)) + "]",
        "compound" => "{ " + string.Join(" ", datum.Members!.Select(p => p.Key + " = " + FormatDatum(p.Value) + ";")) + " }",
        _ => throw new BuildError("SCHEMA_DATA", "Unknown typed datum", datum.Loc)
    };

    public static void SetField(Element element, string name, JsonElement value)
    {
        if (element.Kind != "schema" || value.ValueKind != JsonValueKind.Object) throw new BuildError("SCHEMA_FIELD_KIND", "Field editing requires a schema and a field declaration");
        if (value.EnumerateObject().Count() != 3) throw new BuildError("SCHEMA_FIELD_KIND", "Expected cardinality, kind and type only");
        string cardinality = value.GetProperty("cardinality").GetString()!, kind = value.GetProperty("kind").GetString()!, type = value.GetProperty("type").GetString()!;
        var probe = new Parser($"schema {element.Id} {{ field {name} {cardinality} {kind} {type}; }}", "<draft>").ParseElement();
        if (probe.Fields.Count != 1 || !probe.Fields.TryGetValue(name, out var field) || field.Cardinality != cardinality || field.Kind != kind || field.Type != type || probe.Data.Count != 0 || probe.Values.Count != 0)
            throw new BuildError("SCHEMA_FIELD_KIND", "Expected one direct field declaration");
        element.Fields[name] = field;
    }

    public static void SetData(Element element, string name, JsonElement value)
    {
        if (element.Kind != "object") throw new BuildError("SCHEMA_DATA", "Typed data requires an object declaration");
        var probe = new Parser($"object {element.Id} {{ data {name} = 0; }}", "<draft>").ParseElement();
        if (probe.Data.Count != 1 || !probe.Data.ContainsKey(name)) throw new BuildError("IDENTIFIER", "Expected one field identifier");
        element.Data[name] = FromTransport(value, element.Id);
    }

    // JSON is transport only; the resulting file stores direct declaration syntax.
    public static SchemaDatum FromTransport(JsonElement value, string origin, int depth = 0)
    {
        if (depth > 64) throw new BuildError("SCHEMA_DEPTH", "Typed data nesting exceeds 64");
        var loc = new SourceLocation("<draft>");
        if (value.ValueKind == JsonValueKind.Array)
            return new("multiple", null, null, value.EnumerateArray().Select(v => FromTransport(v, origin, depth + 1)).ToList(), null, origin, loc);
        if (value.ValueKind == JsonValueKind.Object)
        {
            if (value.TryGetProperty("$ref", out var reference))
            {
                if (value.EnumerateObject().Count() != 1 || reference.ValueKind != JsonValueKind.String) throw new BuildError("SCHEMA_DATA", "Reference transport requires only a string $ref");
                string id = reference.GetString()!;
                var parsed = new Parser($"object {origin} {{ data probe = {id}; }}", "<draft>").ParseElement();
                if (parsed.Data.Count != 1 || parsed.Data["probe"].Reference != id || parsed.Values.Count != 0) throw new BuildError("IDENTIFIER", "Expected a namespace-qualified reference");
                return new("reference", null, id, null, null, origin, loc);
            }
            Dictionary<string, SchemaDatum> members = new(StringComparer.Ordinal);
            foreach (var p in value.EnumerateObject())
            {
                if (!System.Text.RegularExpressions.Regex.IsMatch(p.Name, @"\A[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*\z", System.Text.RegularExpressions.RegexOptions.CultureInvariant)) throw new BuildError("IDENTIFIER", "Expected a compound field identifier");
                if (!members.TryAdd(p.Name, FromTransport(p.Value, origin, depth + 1))) throw new BuildError("DUPLICATE_DECLARATION", $"Duplicate data member {p.Name}");
            }
            return new("compound", null, null, null, members, origin, loc);
        }
        if (value.ValueKind is not (JsonValueKind.String or JsonValueKind.Number or JsonValueKind.True or JsonValueKind.False)) throw new BuildError("SCHEMA_DATA", "Null and unset policies are not defined");
        return new("general", value.Clone(), null, null, null, origin, loc);
    }
}
