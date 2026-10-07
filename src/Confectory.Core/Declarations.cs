using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.RegularExpressions;

namespace Confectory.Core;

public sealed record SourceLocation(string File = "<build>", int Line = 1, int Column = 1);
public sealed record Diagnostic(string Severity, string Code, string Message, SourceLocation Location);

public sealed class BuildError : Exception
{
    public Diagnostic Diagnostic { get; }
    public BuildError(string code, string message, SourceLocation? location = null) : base(message)
        => Diagnostic = new("error", code, message, location ?? new());
    public override string ToString() => $"{Diagnostic.Location.File}({Diagnostic.Location.Line},{Diagnostic.Location.Column}): {Diagnostic.Code}: {Message}";
}

public sealed record Parameter(string Type, string Name);
public sealed record FunctionSignature(List<Parameter> Args, [property: JsonPropertyName("return")] string Return)
{
    public bool Matches(FunctionSignature? other) => other is not null && Return == other.Return && Args.Select(a => a.Type).SequenceEqual(other.Args.Select(a => a.Type));
}
public sealed record Locator(string Kind, string Path, SourceLocation Loc);
public sealed record Dependency(string Version, SourceLocation Loc);
public sealed record PackRegistration(string Path, SourceLocation Loc);
public sealed record ElementReference(string Id, SourceLocation Loc, string? Origin = null, string? Kind = null);
public sealed record RequiredFunction(FunctionSignature Signature, SourceLocation Loc, string Origin);
public sealed record Import(string Id, FunctionSignature Signature, string? Scope, SourceLocation Loc, string Origin);
public sealed record Body(string Path, SourceLocation Loc, string Origin);
public sealed record MetadataValue(JsonElement Value, string Origin, SourceLocation Loc);

public sealed class Manifest
{
    public string Kind { get; set; } = "";
    public string Namespace { get; set; } = "";
    public string Version { get; set; } = "";
    public string Description { get; set; } = "";
    public SourceLocation Loc { get; set; } = new();
    public bool? Standalone { get; set; }
    public bool SupportsStandalone => Standalone ?? (Kind == "project" && Entry is not null);
    public string? Entry { get; set; }
    public Dictionary<string, Locator> Elements { get; set; } = new(StringComparer.Ordinal);
    public Dictionary<string, Dependency> Dependencies { get; set; } = new(StringComparer.Ordinal);
    public Dictionary<string, PackRegistration> Registry { get; set; } = new(StringComparer.Ordinal);
    public Dictionary<string, ElementReference> Targets { get; set; } = new(StringComparer.Ordinal);
    public List<ElementReference> Always { get; set; } = [];
}

public sealed class Element
{
    public string Kind { get; set; } = "";
    public string Id { get; set; } = "";
    public SourceLocation Loc { get; set; } = new();
    public string? Parent { get; set; }
    public List<ElementReference> Modules { get; set; } = [];
    public List<ElementReference> Includes { get; set; } = [];
    public Dictionary<string, RequiredFunction> Requires { get; set; } = new(StringComparer.Ordinal);
    public Dictionary<string, ElementReference> Defaults { get; set; } = new(StringComparer.Ordinal);
    public Dictionary<string, ElementReference> Provides { get; set; } = new(StringComparer.Ordinal);
    public List<ElementReference> Uses { get; set; } = [];
    public List<ElementReference> Contains { get; set; } = [];
    public Dictionary<string, MetadataValue> Values { get; set; } = new(StringComparer.Ordinal);
    public Dictionary<string, Import> Imports { get; set; } = new(StringComparer.Ordinal);
    public Dictionary<string, Body> Bodies { get; set; } = new(StringComparer.Ordinal);
    public Dictionary<string, string> Options { get; set; } = new(StringComparer.Ordinal);
    public string Description { get; set; } = "";
    public bool DescriptionPresent { get; set; }
    public FunctionSignature? Signature { get; set; }
    [JsonPropertyName("for")] public string? Function { get; set; }
    public string? Tool { get; set; }
    public string? ToolOrigin { get; set; }
}

public sealed class Parser
{
    private sealed record Token(string Value, SourceLocation Loc, bool Quoted = false);
    private const string NamePattern = @"[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*";
    private const string QualifiedPattern = NamePattern + @"::[A-Za-z_][A-Za-z_0-9]*";
    private static readonly Regex Tokens = new(@"\G(?:(?<space>\s+)|(?<comment>//[^\n]*)|(?<string>""(?:[^""\\]|\\.)*"")|(?<arrow>->)|(?<qid>" + QualifiedPattern + @")|(?<name>" + NamePattern + @")|(?<number>-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)|(?<punct>[{}();,=\[\]]))", RegexOptions.CultureInvariant);
    private static readonly HashSet<string> Kinds = ["function", "implementation", "module", "category", "concept", "schema", "object", "stage", "view", "buildtarget"];
    private static readonly HashSet<string> Types = ["void", "bool", "int", "long", "float", "double", "string"];
    private static readonly HashSet<string> Keywords = new(("abstract as base bool break byte case catch char checked class const continue decimal default delegate do double else enum event explicit extern false finally fixed float for foreach goto if implicit in int interface internal is lock long namespace new null object operator out override params private protected public readonly ref return sbyte sealed short sizeof stackalloc static string struct switch this throw true try typeof uint ulong unchecked unsafe ushort using virtual void volatile while").Split(' '));
    private readonly List<Token> tokens = [];
    private int index;
    private Token Current => tokens[Math.Min(index, tokens.Count - 1)];

    public Parser(string text, string path)
    {
        int position = 0, line = 1, column = 1;
        while (position < text.Length)
        {
            var match = Tokens.Match(text, position);
            var loc = new SourceLocation(path, line, column);
            if (!match.Success) throw new BuildError("SYNTAX", $"Unexpected character {text[position]}", loc);
            string raw = match.Value;
            if (!match.Groups["space"].Success && !match.Groups["comment"].Success)
            {
                bool quoted = match.Groups["string"].Success;
                string value;
                try { value = quoted ? JsonSerializer.Deserialize<string>(raw)! : raw; }
                catch (JsonException ex) { throw new BuildError("SYNTAX", $"Invalid quoted string: {ex.Message}", loc); }
                tokens.Add(new(value, loc, quoted));
            }
            int newlines = raw.Count(c => c == '\n');
            column = newlines > 0 ? raw.Length - raw.LastIndexOf('\n') : column + raw.Length;
            line += newlines;
            position += raw.Length;
        }
        tokens.Add(new("<eof>", new(path, line, column)));
    }

    private Token Pop() { var token = Current; index++; return token; }
    private bool Eat(string value)
    {
        if (Current.Value != value || Current.Quoted) return false;
        Pop(); return true;
    }
    private void Expect(string value)
    {
        if (!Eat(value)) throw new BuildError("SYNTAX", $"Expected '{value}'; found '{Current.Value}'", Current.Loc);
    }
    private string Name(bool qualified = false, bool csharp = false)
    {
        var token = Pop();
        if (token.Quoted || !Regex.IsMatch(token.Value, "\\A(?:" + (qualified ? QualifiedPattern : NamePattern) + ")\\z", RegexOptions.CultureInvariant))
            throw new BuildError("IDENTIFIER", qualified ? "Expected a namespace-qualified element ID" : "Expected an identifier", token.Loc);
        if (csharp && (token.Value.Contains('.') || Keywords.Contains(token.Value)))
            throw new BuildError("IDENTIFIER", "Expected a C# parameter/import identifier", token.Loc);
        return token.Value;
    }
    private string QuotedString()
    {
        var token = Pop();
        if (!token.Quoted) throw new BuildError("SYNTAX", "Expected a quoted string", token.Loc);
        return token.Value;
    }
    private string Kind()
    {
        var token = Pop();
        if (token.Quoted || !Kinds.Contains(token.Value)) throw new BuildError("KIND", $"Unknown element kind '{token.Value}'", token.Loc);
        return token.Value;
    }
    private string Type(bool parameter = false)
    {
        var token = Pop();
        if (token.Quoted || !Types.Contains(token.Value) || (parameter && token.Value == "void"))
            throw new BuildError("TYPE", $"Unsupported contract type '{token.Value}'", token.Loc);
        string value = token.Value;
        if (Eat("["))
        {
            Expect("]");
            if (value == "void") throw new BuildError("TYPE", "void[] is invalid", token.Loc);
            value += "[]";
        }
        return value;
    }
    private FunctionSignature Signature(bool named)
    {
        Expect("(");
        List<Parameter> args = [];
        while (!Eat(")"))
        {
            string type = Type(true), name = named ? Name(csharp: true) : $"arg{args.Count}";
            if (name == "calls" || args.Any(a => a.Name == name)) throw new BuildError("DUPLICATE_PARAMETER", $"Duplicate/reserved parameter {name}", Current.Loc);
            args.Add(new(type, name));
            if (Eat(")")) break;
            Expect(",");
        }
        Expect("->");
        return new(args, Type());
    }
    private static void Unique<T>(Dictionary<string, T> map, string key, T value, SourceLocation loc)
    {
        if (!map.TryAdd(key, value)) throw new BuildError("DUPLICATE_DECLARATION", $"Duplicate declaration {key}", loc);
    }

    public Manifest ParseManifest()
    {
        var first = Pop();
        if (first.Quoted || first.Value is not ("pack" or "project")) throw new BuildError("SYNTAX", "Expected pack or project", first.Loc);
        var manifest = new Manifest { Kind = first.Value, Namespace = Name(), Loc = first.Loc };
        Expect("version"); manifest.Version = QuotedString(); Expect("{");
        HashSet<string> seen = [];
        while (!Eat("}"))
        {
            var token = Pop();
            switch (token.Value)
            {
                case "element":
                    string name = Name();
                    if (name.Contains('.')) throw new BuildError("IDENTIFIER", "Element IDs must be simple identifiers", token.Loc);
                    Unique(manifest.Elements, name, new(Kind(), QuotedString(), token.Loc), token.Loc); break;
                case "dependency":
                    string ns = Name(); Expect("version");
                    Unique(manifest.Dependencies, ns, new(QuotedString(), token.Loc), token.Loc); break;
                case "registry": Unique(manifest.Registry, Name(), new(QuotedString(), token.Loc), token.Loc); break;
                case "target": Unique(manifest.Targets, Name(), new(Name(true), token.Loc), token.Loc); break;
                case "always": manifest.Always.Add(new(Name(true), token.Loc)); break;
                case "standalone":
                    if (!seen.Add(token.Value)) throw new BuildError("DUPLICATE_DECLARATION", "Duplicate standalone", token.Loc);
                    var flag = Pop();
                    if (flag.Quoted || flag.Value is not ("true" or "false")) throw new BuildError("SYNTAX", "standalone requires true or false", flag.Loc);
                    manifest.Standalone = flag.Value == "true"; break;
                case "entry": case "description":
                    if (!seen.Add(token.Value)) throw new BuildError("DUPLICATE_DECLARATION", $"Duplicate {token.Value}", token.Loc);
                    if (token.Value == "entry") manifest.Entry = Name(true); else manifest.Description = QuotedString(); break;
                default: throw new BuildError("SYNTAX", $"Unknown manifest statement '{token.Value}'", token.Loc);
            }
            Expect(";");
        }
        Expect("<eof>");
        if (manifest.Kind == "pack" && (manifest.Entry is not null || manifest.Registry.Count > 0 || manifest.Targets.Count > 0))
            throw new BuildError("PACK_BOUNDARY", "Only a ProjectPack may define registry, entry or targets", first.Loc);
        return manifest;
    }

    public Element ParseElement()
    {
        var start = Current;
        var e = new Element { Kind = Kind(), Id = Name(true), Loc = start.Loc };
        if (e.Kind == "implementation") { Expect("for"); e.Function = Name(true); }
        if (e.Kind is "function" or "implementation") e.Signature = Signature(true);
        if (Eat("extends")) e.Parent = Name(true);
        Expect("{");
        while (!Eat("}"))
        {
            var token = Pop();
            switch (token.Value)
            {
                case "description":
                    if (e.DescriptionPresent) throw new BuildError("DUPLICATE_DECLARATION", "Duplicate description", token.Loc);
                    e.Description = QuotedString(); e.DescriptionPresent = true; break;
                case "module": e.Modules.Add(new(Name(true), token.Loc, e.Id)); break;
                case "include" when e.Kind == "module": e.Includes.Add(new(Name(true), token.Loc, e.Id)); break;
                case "require" when e.Kind == "module": Unique(e.Requires, Name(true), new(Signature(false), token.Loc, e.Id), token.Loc); break;
                case "default" when e.Kind == "module":
                    string df = Name(true); Expect("with"); Unique(e.Defaults, df, new(Name(true), token.Loc, e.Id), token.Loc); break;
                case "provide":
                    string fn = Name(true); Expect("with"); Unique(e.Provides, fn, new(Name(true), token.Loc, e.Id), token.Loc); break;
                case "use": case "contain":
                    string kind = Kind(); var reference = new ElementReference(Name(true), token.Loc, e.Id, kind);
                    (token.Value == "use" ? e.Uses : e.Contains).Add(reference); break;
                case "value":
                    string name = Name(); Expect("="); var value = Pop(); JsonElement data;
                    try
                    {
                        data = value.Quoted ? JsonSerializer.SerializeToElement(value.Value) : JsonSerializer.Deserialize<JsonElement>(value.Value);
                        if (data.ValueKind is not (JsonValueKind.String or JsonValueKind.Number or JsonValueKind.True or JsonValueKind.False)) throw new JsonException("Only primitive metadata values are supported");
                    }
                    catch (JsonException ex) { throw new BuildError("VALUE", $"Invalid metadata value: {ex.Message}", value.Loc); }
                    Unique(e.Values, name, new(data, e.Id, token.Loc), token.Loc); break;
                case "body" when e.Kind == "implementation": Unique(e.Bodies, Name(), new(QuotedString(), token.Loc, e.Id), token.Loc); break;
                case "import" when e.Kind == "implementation":
                    string imported = Name(true); Expect("as"); string alias = Name(csharp: true);
                    var sig = Signature(false); string? scope = Eat("in") ? Name(true) : null;
                    Unique(e.Imports, alias, new(imported, sig, scope, token.Loc, e.Id), token.Loc); break;
                case "tool" when e.Kind == "buildtarget":
                    if (e.Tool is not null) throw new BuildError("DUPLICATE_DECLARATION", "Duplicate target tool", token.Loc);
                    e.Tool = QuotedString(); break;
                case "option" when e.Kind == "buildtarget": Unique(e.Options, Name(), QuotedString(), token.Loc); break;
                default: throw new BuildError("SYNTAX", $"Invalid {e.Kind} statement '{token.Value}'", token.Loc);
            }
            Expect(";");
        }
        Expect("<eof>");
        return e;
    }
}
