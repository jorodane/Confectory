using System.Text;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

namespace Confectory.Core;

// Nominal information values, distinct from live object references. Generation
// reads definitions only; it never creates an object or selects a provider.
public static class InformationStructs
{
    public const string Profile = "information-struct-v1";
    static readonly Regex ContractName = new(@"\AConfectory\.Information\.E[0-9a-f]{24}\.E[0-9a-f]{24}\z", RegexOptions.CultureInvariant);
    static readonly Regex MemberName = new(@"\A[A-Za-z_][A-Za-z_0-9]*\z", RegexOptions.CultureInvariant);
    static readonly HashSet<string> Scalars = ["bool", "int", "long", "float", "double", "string"];
    public static string Type(string id) => "Confectory.Information." + Generation.Symbol(PackPaths.Namespace(id)) + "." + Generation.Symbol(id);
    public static string BaseType(string type) => type.EndsWith("[]", StringComparison.Ordinal) ? type[..^2] : type;
    public static bool IsType(string type) => ContractName.IsMatch(BaseType(type));
    public static IEnumerable<string> SignatureTypes(FunctionSignature signature) => signature.Args.Select(p => p.Type).Append(signature.Return).Where(IsType).Select(BaseType).Distinct(StringComparer.Ordinal);
    public sealed record Field(string Id, string Name, string Origin, string Type, string ClrMember);
    public sealed record Definition(string Id, string ClrType, string ShapeHash, IReadOnlyList<Field> Fields, string Source);

    static Definition Generate(Element schema)
    {
        if (schema.Kind != "schema" || schema.Fields.Count > 256) throw new BuildError("INFORMATION_CLR_SCHEMA", "A bounded information definition is required", schema.Loc);
        var fields = new List<Field>();
        foreach (var (name, field) in schema.Fields.OrderBy(p => p.Key, StringComparer.Ordinal))
        {
            // Reference/function/enum and compound representations are not
            // silently replaced by object, omitted fields or value snapshots.
            if (field.Kind != "general" || field.Cardinality != "single" || !Scalars.Contains(field.Type))
                throw new BuildError("INFORMATION_CLR_FIELD", "This information struct profile requires single primitive fields: " + schema.Id + "/" + name, field.Loc);
            if (!MemberName.IsMatch(name) || name == Generation.Symbol(schema.Id))
                throw new BuildError("INFORMATION_CLR_MEMBER", "The stable field ID cannot be emitted as a C# struct member: " + name, field.Loc);
            fields.Add(new(field.Origin + "/field:" + name, name, field.Origin, field.Type, "@" + name));
        }
        string hash = JsonData.Digest(new { profile = Profile, id = schema.Id, parent = schema.Parent, fields });
        var code = new StringBuilder("// Generated information value " + schema.Id + "; " + Profile + "; " + hash + "\n");
        code.AppendLine("#nullable disable");
        code.AppendLine("namespace Confectory.Information." + Generation.Symbol(PackPaths.Namespace(schema.Id)));
        code.AppendLine("{"); code.AppendLine("    public struct " + Generation.Symbol(schema.Id)); code.AppendLine("    {");
        foreach (var field in fields) code.AppendLine("        public " + field.Type + " " + field.ClrMember + ";");
        code.AppendLine("    }"); code.AppendLine("}");
        return new(schema.Id, Type(schema.Id), hash, fields, code.ToString().Replace("\r\n", "\n", StringComparison.Ordinal));
    }

    public static Definition Describe(Registry registry, string id, string? source = null)
    {
        registry.Get(id, "schema", source);
        new Planner(registry, "metadata").Structural(id);
        return Generate(registry.Effective(id));
    }
    public static Definition Resolve(Registry registry, string type, string source)
    {
        type = BaseType(type);
        var ids = registry.Packs.SelectMany(pack => pack.Value.Elements.Where(p => p.Value.Kind == "schema").Select(p => pack.Key + "::" + p.Key)).Where(id => Type(id) == type).Take(2).ToArray();
        if (ids.Length != 1) throw new BuildError("INFORMATION_CLR_TYPE", "The generated information type must identify exactly one registered definition: " + type, registry.Get(source).Loc);
        return Describe(registry, ids[0], source);
    }

    // The owned C# candidate compiler uses the same shapes over its already
    // observed declaration overlay. Missing registered definitions stay errors.
    public static IReadOnlyList<Definition> ForDeclarations(IEnumerable<Element> functions, IReadOnlyDictionary<string, Element> declarations)
    {
        var result = new Dictionary<string, Definition>(StringComparer.Ordinal);
        foreach (string type in functions.SelectMany(fn => SignatureTypes(fn.Signature!)).Distinct(StringComparer.Ordinal))
        {
            var choices = declarations.Values.Where(e => e.Kind == "schema" && Type(e.Id) == type).Take(2).ToArray();
            if (choices.Length != 1) throw new BuildError("INFORMATION_CLR_SOURCE", "Read the exact information definition before validating its C# contract: " + type);
            var selected = choices[0]; var chain = new List<Element>(); var seen = new HashSet<string>(StringComparer.Ordinal); var current = selected;
            while (true)
            {
                if (!seen.Add(current.Id) || seen.Count > 64) throw new BuildError("INFORMATION_CLR_CYCLE", "Acyclic information inheritance required", selected.Loc);
                chain.Add(current); if (current.Parent is null) break;
                if (!declarations.TryGetValue(current.Parent, out var parent) || parent.Kind != "schema") throw new BuildError("INFORMATION_CLR_SOURCE", "Read the original parent information definition", current.Loc);
                current = parent;
            }
            var effective = new Element { Id = selected.Id, Kind = "schema", Parent = selected.Parent, Loc = selected.Loc };
            foreach (var layer in chain.AsEnumerable().Reverse()) foreach (var field in layer.Fields) effective.Fields[field.Key] = field.Value;
            result.Add(type, Generate(effective));
        }
        return result.Values.OrderBy(d => d.Id, StringComparer.Ordinal).ToArray();
    }

    public static JsonObject Document(Definition definition) => JsonData.Object(new { profile = Profile, id = definition.Id, clrType = definition.ClrType, shapeHash = definition.ShapeHash, valueType = true, fields = definition.Fields, source = definition.Source, sourceWritten = false, executed = false });
}
