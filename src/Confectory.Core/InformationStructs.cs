using System.Text;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

namespace Confectory.Core;

// Nominal information values, distinct from live object references. Generation
// reads definitions only; it never creates an object or selects a provider.
public static class InformationStructs
{
    public const string Profile = "information-struct-v1";
    public const string CompoundProfile = "information-struct-compound-v1";
    public const string NominalProfile = "information-struct-nominal-v1";
    static readonly Regex ContractName = new(@"\AConfectory\.Information\.E[0-9a-f]{24}\.E[0-9a-f]{24}\z", RegexOptions.CultureInvariant);
    static readonly Regex MemberName = new(@"\A[A-Za-z_][A-Za-z_0-9]*\z", RegexOptions.CultureInvariant);
    static readonly HashSet<string> Scalars = ["bool", "int", "long", "float", "double", "string"];
    public static string Type(string id) => "Confectory.Information." + Generation.Symbol(PackPaths.Namespace(id)) + "." + Generation.Symbol(id);
    public static string BaseType(string type) => type.EndsWith("[]", StringComparison.Ordinal) ? type[..^2] : type;
    public static bool IsType(string type) => ContractName.IsMatch(BaseType(type));
    public static IEnumerable<string> SignatureTypes(FunctionSignature signature) => signature.Args.Select(p => p.Type).Append(signature.Return).Where(IsType).Select(BaseType).Distinct(StringComparer.Ordinal);
    public sealed record Field(string Id, string Name, string Origin, string Type, string ClrMember);
    public sealed record Dependency(string Id, string ClrType, string ShapeHash);
    public sealed record Definition(string Id, string ClrType, string ShapeHash, IReadOnlyList<Field> Fields, string Source, IReadOnlyList<Dependency>? Dependencies = null, string Kind = "schema", string? NativeProfile = null, JsonArray? Members = null);

    static Definition Generate(Element schema, Func<SchemaField, Definition> resolve)
    {
        if (schema.Kind != "schema" || schema.Fields.Count > 256) throw new BuildError("INFORMATION_CLR_SCHEMA", "A bounded information definition is required", schema.Loc);
        var fields = new List<Field>(); var dependencies = new Dictionary<string, Dependency>(StringComparer.Ordinal); bool enums = false;
        foreach (var (name, field) in schema.Fields.OrderBy(p => p.Key, StringComparer.Ordinal))
        {
            // Reference/function and list representations are not
            // silently replaced by object, omitted fields or value snapshots.
            if (field.Cardinality != "single" || field.Kind is not ("compound" or "enum") && (field.Kind != "general" || !Scalars.Contains(field.Type)))
                throw new BuildError("INFORMATION_CLR_FIELD", "This information struct profile requires single primitive, compound or mapped enum fields: " + schema.Id + "/" + name, field.Loc);
            if (!MemberName.IsMatch(name) || name == Generation.Symbol(schema.Id))
                throw new BuildError("INFORMATION_CLR_MEMBER", "The stable field ID cannot be emitted as a C# struct member: " + name, field.Loc);
            string type = field.Type;
            if (field.Kind is "compound" or "enum") { var child = resolve(field); type = child.ClrType; enums |= child.Kind == "enum"; dependencies[child.Id] = new(child.Id, child.ClrType, child.ShapeHash); }
            fields.Add(new(field.Origin + "/field:" + name, name, field.Origin, type, "@" + name));
        }
        var inputs = dependencies.Values.OrderBy(d => d.Id, StringComparer.Ordinal).ToArray(); string profile = enums ? NominalProfile : inputs.Length == 0 ? Profile : CompoundProfile;
        // Keep existing primitive source/shape keys byte-for-byte unchanged.
        string hash = inputs.Length == 0 ? JsonData.Digest(new { profile = Profile, id = schema.Id, parent = schema.Parent, fields }) : JsonData.Digest(new { profile, id = schema.Id, parent = schema.Parent, fields, dependencies = inputs });
        var code = new StringBuilder("// Generated information value " + schema.Id + "; " + profile + "; " + hash + "\n");
        code.AppendLine("#nullable disable");
        code.AppendLine("namespace Confectory.Information." + Generation.Symbol(PackPaths.Namespace(schema.Id)));
        code.AppendLine("{"); code.AppendLine("    public struct " + Generation.Symbol(schema.Id)); code.AppendLine("    {");
        foreach (var field in fields) code.AppendLine("        public " + field.Type + " " + field.ClrMember + ";");
        code.AppendLine("    }"); code.AppendLine("}");
        return new(schema.Id, Type(schema.Id), hash, fields, code.ToString().Replace("\r\n", "\n", StringComparison.Ordinal), inputs, NativeProfile: profile);
    }

    public static IReadOnlyList<Definition> Closure(Registry registry, string id, string? source = null)
    {
        var element = registry.Get(id, source: source); if (element.Kind is not ("schema" or "enum" or "module")) throw new BuildError("INFORMATION_CLR_KIND", "An information, enum or module definition is required", element.Loc);
        var planner = new Planner(registry, "metadata"); planner.Structural(id);
        Element Effective(string selected) {
            var declaration = registry.Get(selected);
            // A module reached through another module's public method type
            // retains its own require/default/dependency validation as well.
            if (declaration.Kind == "module") planner.Module(selected);
            else if (declaration.Kind == "schema") planner.Structural(selected);
            return registry.Effective(selected);
        }
        return GenerateClosure(id, Effective, field => { registry.Get(field.Type, field.Kind == "enum" ? "enum" : "schema", field.Origin, field.Loc); return field.Type; }, (type, origin) => {
            string selected = TypeId(registry, type, origin); registry.Get(selected, source: origin); return selected;
        });
    }
    public static Definition Describe(Registry registry, string id, string? source = null) => Closure(registry, id, source).Single(d => d.Id == id);
    public static IReadOnlyList<Definition> ResolveAll(Registry registry, string type, string source)
    {
        return Closure(registry, TypeId(registry, type, source), source);
    }
    static string TypeId(Registry registry, string type, string source)
    {
        type = BaseType(type);
        var ids = registry.Packs.SelectMany(pack => pack.Value.Elements.Where(p => p.Value.Kind is "schema" or "enum" or "module").Select(p => pack.Key + "::" + p.Key)).Where(id => Type(id) == type).Take(2).ToArray();
        if (ids.Length != 1) throw new BuildError("INFORMATION_CLR_TYPE", "The generated information type must identify exactly one registered definition: " + type, registry.Get(source).Loc);
        return ids[0];
    }
    public static Definition Resolve(Registry registry, string type, string source) => ResolveAll(registry, type, source).Single(d => d.ClrType == BaseType(type));

    static IReadOnlyList<Definition> GenerateClosure(string id, Func<string, Element> effective, Func<SchemaField, string> target, Func<string, string, string> nominal)
    {
        var result = new Dictionary<string, Definition>(StringComparer.Ordinal); var visiting = new HashSet<string>(StringComparer.Ordinal);
        Definition Read(string current)
        {
            if (result.TryGetValue(current, out var prior)) return prior;
            if (!visiting.Add(current)) throw new BuildError("INFORMATION_CLR_CYCLE", "Unsupported selected information/module type dependency cycle; originals retained: " + current);
            if (result.Count + visiting.Count > 256) throw new BuildError("INFORMATION_CLR_BUDGET", "At most 256 selected information value types");
            var element = effective(current); var definition = element.Kind == "enum" ? InformationEnums.Generate(element) : element.Kind == "module" ? ModuleInterfaces.Generate(current, effective, (type, origin) => Read(nominal(type, origin))) : Generate(element, field => Read(target(field))); visiting.Remove(current); result.Add(current, definition); return definition;
        }
        Read(id); return result.Values.OrderBy(d => d.Id, StringComparer.Ordinal).ToArray();
    }

    // The owned C# candidate compiler uses the same shapes over its already
    // observed declaration overlay. Missing registered definitions stay errors.
    public static IReadOnlyList<Definition> ForDeclarations(IEnumerable<Element> functions, IReadOnlyDictionary<string, Element> declarations)
    {
        var result = new Dictionary<string, Definition>(StringComparer.Ordinal);
        foreach (string type in functions.SelectMany(fn => SignatureTypes(fn.Signature!)).Distinct(StringComparer.Ordinal))
        {
            var choices = declarations.Values.Where(e => e.Kind is "schema" or "enum" or "module" && Type(e.Id) == type).Take(2).ToArray();
            if (choices.Length != 1) throw new BuildError("INFORMATION_CLR_SOURCE", "Read the exact information definition before validating its C# contract: " + type);
            Element Effective(string selectedId)
            {
            if (!declarations.TryGetValue(selectedId, out var selected)) throw new BuildError("INFORMATION_CLR_SOURCE", "Read the exact information/enum/module dependency: " + selectedId);
            if (selected.Kind is not ("schema" or "module")) return selected;
            var chain = new List<Element>(); var seen = new HashSet<string>(StringComparer.Ordinal); var current = selected;
            while (true)
            {
                if (!seen.Add(current.Id)) throw new BuildError("INFORMATION_CLR_CYCLE", "Acyclic information inheritance required", selected.Loc);
                chain.Add(current); if (current.Parent is null) break;
                if (!declarations.TryGetValue(current.Parent, out var parent) || parent.Kind != selected.Kind) throw new BuildError("INFORMATION_CLR_SOURCE", "Read the original parent definition", current.Loc);
                current = parent;
            }
            var effective = new Element { Id = selected.Id, Kind = selected.Kind, Parent = selected.Parent, Loc = selected.Loc };
            foreach (var layer in chain.AsEnumerable().Reverse()) { foreach (var field in layer.Fields) {
                if (effective.Fields.TryGetValue(field.Key, out var prior) && (prior.Kind != field.Value.Kind || prior.Type != field.Value.Type || prior.Cardinality != field.Value.Cardinality)) throw new BuildError("SCHEMA_INHERITANCE", "Inherited field contract changed: " + field.Key, field.Value.Loc);
                effective.Fields[field.Key] = field.Value;
            } foreach (var requirement in layer.Requires) effective.Requires[requirement.Key] = requirement.Value; foreach (var choice in layer.Defaults) effective.Defaults[choice.Key] = choice.Value; effective.Includes.AddRange(layer.Includes); }
            return effective;
            }
            foreach (var definition in GenerateClosure(choices[0].Id, Effective, field => {
                if (!declarations.TryGetValue(field.Type, out var dependency) || dependency.Kind != (field.Kind == "enum" ? "enum" : "schema")) throw new BuildError("INFORMATION_CLR_SOURCE", "Read the exact declared field type: " + field.Type, field.Loc);
                return field.Type;
            }, (requested, origin) => {
                var candidates = declarations.Values.Where(e => e.Kind is "schema" or "enum" or "module" && Type(e.Id) == BaseType(requested)).Take(2).ToArray();
                if (candidates.Length != 1) throw new BuildError("INFORMATION_CLR_SOURCE", "Read the exact required method type: " + requested, Effective(origin).Loc);
                return candidates[0].Id;
            })) { result.TryAdd(definition.ClrType, definition); if (result.Count > 256) throw new BuildError("INFORMATION_CLR_BUDGET", "At most 256 selected information value types"); }
        }
        return result.Values.OrderBy(d => d.Id, StringComparer.Ordinal).ToArray();
    }

    public static JsonObject Document(Definition definition)
    {
        var result = JsonData.Object(new { profile = definition.NativeProfile ?? (definition.Dependencies?.Count > 0 ? CompoundProfile : Profile), id = definition.Id, clrType = definition.ClrType, shapeHash = definition.ShapeHash, valueType = true, fields = definition.Fields, source = definition.Source, sourceWritten = false, executed = false });
        if (definition.Kind == "enum") { result["kind"] = "enum"; result["underlyingType"] = "int"; result["unselectedValue"] = 0; result["members"] = definition.Members!.DeepClone(); }
        if (definition.Kind == "module") { result["kind"] = "module"; result["valueType"] = false; result["interface"] = true; result["methods"] = definition.Members!.DeepClone(); result["providerSelection"] = "not-performed"; }
        if (definition.Dependencies?.Count > 0) result["dependencies"] = System.Text.Json.JsonSerializer.SerializeToNode(definition.Dependencies, JsonData.Options);
        return result;
    }
}
