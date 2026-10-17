using Confectory.Core;
using System.Text.Json.Nodes;

namespace Confectory.Tests;

public sealed class ImplicitBlueprintTests : TestCase
{
    static JsonObject Signature(string result, params (string Type, string Name)[] args) => new()
    {
        ["args"] = new JsonArray(args.Select(a => (JsonNode)new JsonObject { ["type"] = a.Type, ["name"] = a.Name }).ToArray()), ["return"] = result
    };
    static string Feature(string type = "int") => "function Api::Value (int n) -> " + type + " {}";
    static JsonObject Graph(string type = "int") => new()
    {
        ["schema"] = 1, ["profile"] = FeatureBlueprint.ImplicitProfile, ["feature"] = "Api::Value",
        ["contractHash"] = FeatureBlueprint.ContractHash(new Parser(Feature(type), "<implicit-fixture>").ParseElement()),
        ["entry"] = "", ["nodes"] = new JsonArray(), ["edges"] = new JsonArray(), ["exits"] = new JsonObject()
    };
    static JsonObject Code(string id, string result = "void", string control = "next") => new()
    {
        ["id"] = id, ["kind"] = "code", ["control"] = control, ["intent"] = "Owned " + id,
        ["signature"] = Signature(result, ("int", "n")), ["arguments"] = new JsonObject { ["n"] = new JsonObject { ["input"] = "n" } }, ["implementation"] = id + ".node.json"
    };
    static JsonObject Export(string id = "publish") => new()
    {
        ["id"] = id, ["kind"] = "export", ["control"] = "next", ["intent"] = "Assign the declared return", ["output"] = "return",
        ["signature"] = Signature("void", ("int", "value")), ["arguments"] = new JsonObject { ["value"] = new JsonObject { ["input"] = "n" } }
    };
    static JsonObject Edge(string from, string port, string to) => new() { ["from"] = from, ["port"] = port, ["to"] = to };
    static JsonObject Query(JsonObject graph, string operation = "featureBlueprintDescribe", string type = "int", JsonObject? records = null) => FeatureBlueprint.Execute(new JsonObject
    {
        ["operation"] = operation, ["featureSource"] = Feature(type), ["graph"] = graph.DeepClone(), ["implementations"] = records?.DeepClone()
    });
    JsonObject Prepare(JsonObject graph, IReadOnlyDictionary<string, string> code, string type = "int")
    {
        var definitions = Query(graph, "featureBlueprintNodes", type); Equal("node-definitions", Text(definitions, "state"));
        var records = new JsonObject();
        foreach (var pair in code)
        {
            var node = definitions["nodes"]!.AsArray().Single(n => n!["id"]!.ToString() == pair.Key)!;
            var record = new JsonObject { ["schema"] = 1, ["node"] = pair.Key, ["definitionHash"] = node["definitionHash"]!.DeepClone(), ["source"] = pair.Value };
            records[pair.Key] = record.DeepClone(); f.Body("Provider", pair.Key + ".node.json", record.ToJsonString());
        }
        f.Add("Api", "function", "Value", Feature(type));
        f.Add("Provider", "implementation", "ValueBody", "implementation Provider::ValueBody for Api::Value (int n) -> " + type + " {blueprint common \"implicit.graph.json\";}");
        f.Body("Provider", "implicit.graph.json", graph.ToJsonString()); f.Sync(); return records;
    }
    public void test_implicit_branch_terminations_warn_separately_and_real_errors_remain_errors()
    {
        var graph = Graph(); graph["entry"] = "choose"; graph["nodes"]!.AsArray().Add(Code("choose", "bool", "branch")); graph["nodes"]!.AsArray().Add(Export()); graph["edges"]!.AsArray().Add(Edge("choose", "true", "publish"));
        var records = Prepare(graph, new Dictionary<string, string> { ["choose"] = "return n > 0;" });
        var described = Query(graph, records: records); Equal("source-ready", Text(described, "state")); Equal(1, described["warnings"]!.AsArray().Count); Equal("choose/false", Text(described["warnings"]![0]!, "subject")); Equal("return", Text(described["warnings"]![0]!["missingOutputs"]![0]!, "name"));
        Equal(2, described["terminations"]!.AsArray().Count); True(described["terminations"]!.AsArray().Single(n => n!["from"]!.ToString() == "publish")!["definitelyAssigned"]!.GetValue<bool>());
        var both = graph.DeepClone().AsObject(); both["edges"] = new JsonArray(); var missingBoth = Query(both, records: records); Sequence(new[] { "choose/false", "choose/true" }, missingBoth["warnings"]!.AsArray().Select(n => n!["subject"]!.ToString()).Order(StringComparer.Ordinal));
        var legacy = graph.DeepClone().AsObject(); legacy["profile"] = FeatureBlueprint.Profile; legacy["nodes"]!.AsArray().RemoveAt(1); legacy["edges"] = new JsonArray(); Equal("GRAPH_PORTS", Text(Query(legacy)["diagnostics"]![0]!, "code"));
        var wrong = graph.DeepClone().AsObject(); wrong["nodes"]![1]!["arguments"]!["value"] = new JsonObject { ["constant"] = "wrong" }; Equal("GRAPH_CONSTANT_TYPE", Text(Query(wrong, records: records)["diagnostics"]![0]!, "code"));
        var cycle = graph.DeepClone().AsObject(); cycle["edges"]!.AsArray().Add(Edge("publish", "next", "choose")); Equal("GRAPH_CYCLE_PROFILE_UNSUPPORTED", Text(Query(cycle, records: records)["diagnostics"]![0]!, "code"));
        var badPort = graph.DeepClone().AsObject(); badPort["edges"]!.AsArray().Add(Edge("choose", "other", "publish")); Equal("GRAPH_PORTS", Text(Query(badPort, records: records)["diagnostics"]![0]!, "code"));
        f.Body("App", "main.csbody", "Console.WriteLine(calls.Value.Invoke(2)+\",\"+calls.Value.Invoke(-2));return 0;"); var built = Build(); Output(built, "2,0"); var receipt = built["blueprints"]!["Provider::ValueBody"]!; Equal(FeatureBlueprint.ImplicitProfile, Text(receipt, "profile")); Equal(1, receipt["warnings"]!.AsArray().Count); True(receipt["nodes"]!.AsArray().Single(n => n!["id"]!.ToString() == "publish")!["compilerValidated"]!.GetValue<bool>());
        records["choose"]!["source"] = "return \"bad\";"; f.Body("Provider", "choose.node.json", records["choose"]!.ToJsonString()); Error("TARGET_FAILURE", () => Build());
    }
    public void test_implicit_join_tracks_must_may_and_a_specific_unassigned_branch_witness()
    {
        var graph = Graph(); graph["entry"] = "choose"; graph["nodes"] = new JsonArray(Code("choose", "bool", "branch"), Export(), Code("skip"), Code("join")); graph["edges"] = new JsonArray(Edge("choose", "true", "publish"), Edge("choose", "false", "skip"), Edge("publish", "next", "join"), Edge("skip", "next", "join"));
        var records = Prepare(graph, new Dictionary<string, string> { ["choose"] = "return n > 0;", ["skip"] = "return;", ["join"] = "return;" }); var described = Query(graph, records: records); Equal("source-ready", Text(described, "state")); Equal(1, described["warnings"]!.AsArray().Count); var warning = described["warnings"]![0]!; Equal("join/next", Text(warning, "subject")); True(warning["missingOutputs"]![0]!["assignedOnSomePaths"]!.GetValue<bool>()); True(warning["exampleUnassignedPath"]!.AsArray().Any(n => n!["from"]?.ToString() == "choose" && n["port"]?.ToString() == "false")); True(!warning["exampleUnassignedPath"]!.AsArray().Any(n => n!["from"]?.ToString() == "publish"));
        f.Body("App", "main.csbody", "Console.WriteLine(calls.Value.Invoke(2)+\",\"+calls.Value.Invoke(-2));return 0;"); Output(Build(), "2,0");
        graph["nodes"]![3]!["arguments"]!["n"] = new JsonObject { ["node"] = "publish" }; Equal("GRAPH_VALUE_UNAVAILABLE", Text(Query(graph, records: records)["diagnostics"]![0]!, "code"));
    }
    public void test_implicit_empty_start_has_typed_defaults_without_hiding_void_or_type_errors()
    {
        foreach (string type in new[] { "bool", "int", "long", "float", "double", "string", "int[]", "string[]" })
        {
            var graph = Graph(type); Prepare(graph, new Dictionary<string, string>(), type); var described = Query(graph, type: type); Equal("source-ready", Text(described, "state")); Equal("$entry/entry", Text(described["warnings"]![0]!, "subject"));
            f.Add("App", "implementation", "MainBody", "implementation App::MainBody for App::Main () -> int {import Api::Value as Value (int) -> " + type + ";body common \"main.csbody\";}");
            bool reference = type == "string" || type.EndsWith("[]", StringComparison.Ordinal); f.Body("App", "main.csbody", reference ? "Console.WriteLine(calls.Value.Invoke(2) is null ? \"null\" : \"unexpected\");return 0;" : "Console.WriteLine(calls.Value.Invoke(2));return 0;"); f.Sync(); Output(Build(), reference ? "null" : type == "bool" ? "False" : "0");
        }
        var forgedEnd=Graph();forgedEnd["entry"]="end:forged";Equal("GRAPH_TARGET",Text(Query(forgedEnd)["diagnostics"]![0]!,"code"));
        var emptyVoid = Query(Graph("void"), type: "void"); Equal("source-ready", Text(emptyVoid, "state")); Equal(0, emptyVoid["warnings"]!.AsArray().Count);
        var invalid = Graph(); invalid["nodes"] = new JsonArray(Export()); invalid["nodes"]![0]!["signature"]!["args"]![0]!["type"] = "string"; Equal("GRAPH_OUTPUT_CONTRACT", Text(Query(invalid)["diagnostics"]![0]!, "code"));
        var unknown = Graph(); unknown["profile"] = "unknown"; Equal("GRAPH_PROFILE_UNSUPPORTED", Text(Query(unknown)["diagnostics"]![0]!, "code"));
    }
}
