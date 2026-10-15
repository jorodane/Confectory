using Confectory.Core;
using System.Text.Json.Nodes;

namespace Confectory.Tests;

public sealed class FeatureBlueprintTests : TestCase
{
    private const string Feature = "function Api::Value (int n) -> int {}";
    private static JsonObject Signature(string result, params (string Type, string Name)[] args) => new()
    {
        ["args"] = new JsonArray(args.Select(a => (JsonNode)new JsonObject { ["type"] = a.Type, ["name"] = a.Name }).ToArray()), ["return"] = result
    };
    private static JsonObject Node(string id, string control, string result, string intent) => new()
    {
        ["id"] = id, ["kind"] = "code", ["control"] = control, ["intent"] = intent,
        ["signature"] = Signature(result, ("int", "value")),
        ["arguments"] = new JsonObject { ["value"] = new JsonObject { ["input"] = "n" } },
        ["implementation"] = id + ".node.json"
    };
    private static JsonObject Edge(string from, string port, string to) => new() { ["from"] = from, ["port"] = port, ["to"] = to };
    private static JsonObject Graph() => new()
    {
        ["schema"] = 1, ["profile"] = FeatureBlueprint.Profile, ["feature"] = "Api::Value",
        ["contractHash"] = FeatureBlueprint.ContractHash(new Parser(Feature, "<fixture>").ParseElement()),
        ["nodes"] = new JsonArray(Node("condition", "branch", "bool", "Select positive inputs"), Node("add", "next", "int", "Add three")),
        ["entry"] = "condition",
        ["edges"] = new JsonArray(Edge("condition", "true", "add"), Edge("condition", "false", "exit:negative"), Edge("add", "next", "exit:done")),
        ["exits"] = new JsonObject { ["done"] = new JsonObject { ["node"] = "add" }, ["negative"] = new JsonObject { ["constant"] = 0 } }
    };
    private static JsonObject Request(JsonObject graph, string operation = "featureBlueprintDescribe", JsonObject? implementations = null) => new()
    {
        ["operation"] = operation, ["featureSource"] = Feature, ["graph"] = graph.DeepClone(), ["implementations"] = implementations?.DeepClone()
    };
    private JsonObject Prepare(JsonObject graph, string add = "return value + 3;")
    {
        var described = FeatureBlueprint.Execute(Request(graph));
        Equal("needs-implementation", Text(described, "state"));
        var implementations = new JsonObject();
        foreach (var node in described["nodes"]!.AsArray())
        {
            string id = node!["id"]!.GetValue<string>();
            var record = new JsonObject { ["schema"] = 1, ["node"] = id, ["definitionHash"] = node["definitionHash"]!.DeepClone(), ["source"] = id == "add" ? add : "return value > 0;" };
            implementations[id] = record;
            f.Body("Provider", id + ".node.json", record.ToJsonString());
        }
        f.Body("Provider", "value.graph.json", graph.ToJsonString());
        f.Add("Provider", "implementation", "ValueBody", "implementation Provider::ValueBody for Api::Value (int n) -> int {blueprint common \"value.graph.json\";}");
        return implementations;
    }
    private static void Refused(JsonObject graph, string code)
    {
        var result = FeatureBlueprint.Execute(Request(graph));
        Equal("invalid", Text(result, "state")); Equal(code, Text(result["diagnostics"]![0]!, "code"));
    }
    public void test_blueprint_fixed_inputs_branch_compiler_reuse_node_replacement_and_legacy_preservation()
    {
        string legacy = File.ReadAllText(Path.Combine(f.Packs["Provider"].Root, "value.csbody"));
        var graph = Graph(); var implementations = Prepare(graph);
        var assembled = FeatureBlueprint.Execute(Request(graph, "featureBlueprintAssemble", implementations));
        Equal("source-assembled", Text(assembled, "state"));
        var reordered = graph.DeepClone().AsObject(); var edges = reordered["edges"]!.AsArray(); var edge = edges[0]!.DeepClone(); edges.RemoveAt(0); edges.Add(edge);
        var same = FeatureBlueprint.Execute(Request(reordered, "featureBlueprintAssemble", implementations));
        Equal(Text(assembled, "bodyHash"), Text(same, "bodyHash"));
        Equal(Text(assembled, "topologyHash"), Text(same, "topologyHash"));
        var first = Build(); Output(first, "5");
        Equal("source-assembled", Text(first, "blueprints", "Provider::ValueBody", "state"));
        Equal(FeatureBlueprint.Profile, Text(first, "blueprints", "Provider::ValueBody", "profile"));
        True(first["blueprints"]!["Provider::ValueBody"]!["compilerIdentity"]!.ToString().Length > 10);
        True(first["blueprints"]!["Provider::ValueBody"]!["inputs"]!.AsArray().Count >= 5);
        Equal("/source", Text(first["blueprints"]!["Provider::ValueBody"]!["sourceMap"]![0]!, "jsonPointer"));
        var checkedPack = new Builder(f.Project, "portable").Check("Provider"); True(checkedPack["blueprints"]!["Provider::ValueBody"]!["compilerValidated"]!.GetValue<bool>()); True(checkedPack["run"] is null);
        var reused = Build(); Equal(0, Strings(reused, "statistics", "compiledImplementations").Length);
        True(first["blueprints"]!["Provider::ValueBody"]!["compilerValidated"]!.GetValue<bool>());
        string mirror = Path.Combine(Path.GetDirectoryName(f.Root)!, "confectory-blueprint-repro-" + Guid.NewGuid().ToString("N"));
        try
        {
            Fixture.CopyTree(f.Root, mirror);
            foreach (string file in Directory.EnumerateFiles(mirror, "*", SearchOption.AllDirectories).Where(p => p.EndsWith(".cpack", StringComparison.Ordinal) || p.EndsWith(".cproj", StringComparison.Ordinal))) File.WriteAllText(file, File.ReadAllText(file).Replace(f.Root, mirror, StringComparison.Ordinal));
            var copied = new Builder(Path.Combine(mirror, Path.GetRelativePath(f.Root, f.Project)), "portable").Build();
            Equal(JsonData.HashBytes(File.ReadAllBytes(Text(first, "implementationArtifacts", "Provider", "assembly"))), JsonData.HashBytes(File.ReadAllBytes(Text(copied, "implementationArtifacts", "Provider", "assembly"))));
        }
        finally { if (Directory.Exists(mirror)) Directory.Delete(mirror, true); }
        var record = implementations["add"]!.DeepClone().AsObject(); record["source"] = "return value + 4;";
        f.Body("Provider", "add.node.json", record.ToJsonString());
        var changed = Build(); Output(changed, "6"); PackRebuilt(changed, ["Provider::ValueBody"]);
        Equal(0, Strings(changed, "statistics", "compiledContracts").Length);
        graph["edges"]![0]!["to"] = "exit:negative";
        f.Body("Provider", "value.graph.json", graph.ToJsonString());
        Output(Build(), "0");
        Equal(legacy, File.ReadAllText(Path.Combine(f.Packs["Provider"].Root, "value.csbody")));
        // A topology edit does not replace a node file or its definition stamp.
        Equal(record.ToJsonString() + "\n", File.ReadAllText(Path.Combine(f.Packs["Provider"].Root, "add.node.json")));
    }
    public void test_blueprint_invalid_graphs_stale_contracts_and_dominating_values()
    {
        var graph = Graph(); graph["edges"]![0]!["to"] = "condition"; Refused(graph, "GRAPH_CYCLE_PROFILE_UNSUPPORTED");
        graph = Graph(); graph["contractHash"] = "stale"; Refused(graph, "GRAPH_CONTRACT_STALE");
        graph = Graph(); graph["profile"] = "async"; Refused(graph, "GRAPH_PROFILE_UNSUPPORTED");
        graph = Graph(); graph["edges"]![1]!["to"] = "exit:done"; Refused(graph, "GRAPH_VALUE_UNAVAILABLE");
        graph = Graph(); graph["nodes"]![0]!["signature"]!["return"] = "int"; Refused(graph, "GRAPH_BRANCH_TYPE");
        graph = Graph(); graph["nodes"]![1]!["arguments"]!["value"] = new JsonObject { ["constant"] = "bad" }; Refused(graph, "GRAPH_CONSTANT_TYPE");
        graph = Graph(); graph["nodes"]![1]!["id"] = "injected\";"; Refused(graph, "GRAPH_ID");
        graph = Graph(); var unconnected = Node("unconnected", "next", "int", "Independent work before wiring"); unconnected.Remove("arguments"); graph["nodes"]!.AsArray().Add(unconnected);
        var definitions = FeatureBlueprint.Execute(Request(graph, "featureBlueprintNodes")); Equal("node-definitions", Text(definitions, "state")); Equal(3, definitions["nodes"]!.AsArray().Count);
        var connected = FeatureBlueprint.Execute(Request(graph)); Equal("needs-implementation", Text(connected, "state")); Sequence(new[] { "unconnected" }, Strings(connected, "disconnected"));
        graph = Graph(); var implementations = Prepare(graph);
        graph["nodes"]![1]!["intent"] = "Different implementation request";
        var result = FeatureBlueprint.Execute(Request(graph, "featureBlueprintAssemble", implementations));
        Equal("needs-implementation", Text(result, "state"));
        True(result["nodes"]!.AsArray().Any(n => n!["id"]!.ToString() == "add" && n["status"]!.ToString() == "stale"));
        True(result["body"] is null);
    }
    public void test_blueprint_node_diagnostics_static_isolation_and_failed_build_retains_receipt()
    {
        var graph = Graph(); var records = Prepare(graph); var prior = Build(); Output(prior, "5");
        string latest = Path.Combine(Path.GetDirectoryName(Text(prior, "output"))!, "latest.json");
        string successful = File.ReadAllText(latest);
        foreach (string source in new[] { "return n + 3;", "return value + missing;", "} static int Escaped() { return 1; } {", "#line 1 \"fake\"\nreturn value;" })
        {
            var bad = records["add"]!.DeepClone().AsObject(); bad["source"] = source;
            f.Body("Provider", "add.node.json", bad.ToJsonString());
            var error = Error("TARGET_FAILURE", () => Build());
            True(error.Message.Contains("node:Api::Value/add", StringComparison.Ordinal), error.Message);
            Equal(successful, File.ReadAllText(latest));
        }
        f.Body("Provider", "add.node.json", records["add"]!.ToJsonString());
        var builder = new Builder(f.Project, "portable"); builder.Registry.Get("Api::Value");
        f.Add("Api", "function", "Value", "function Api::Value (int differentName) -> int {}");
        Error("BLUEPRINT_SOURCE_CHANGED", () => builder.Build());
        Equal(successful, File.ReadAllText(latest));
        f.Add("Api", "function", "Value", Feature);
        var manifestBuilder = new Builder(f.Project, "portable");
        File.WriteAllText(f.Project, File.ReadAllText(f.Project).Replace("version \"1\"", "version \"2\"", StringComparison.Ordinal));
        Error("BLUEPRINT_SOURCE_CHANGED", () => manifestBuilder.Build());
        Equal(successful, File.ReadAllText(latest));
    }
    public void test_blueprint_existing_feature_calls_use_typed_imports_and_contract_fences()
    {
        var graph = Graph();
        graph["nodes"]![1]!["kind"] = "call";
        graph["nodes"]![1]!["feature"] = "Api::Double";
        var request = Request(graph);
        request["featureContracts"] = new JsonObject { ["Api::Double"] = "function Api::Double (int n) -> int {}" };
        var described = FeatureBlueprint.Execute(request);
        var condition = described["nodes"]!.AsArray().Single(n => n!["id"]!.ToString() == "condition")!;
        var record = new JsonObject { ["schema"] = 1, ["node"] = "condition", ["definitionHash"] = condition["definitionHash"]!.DeepClone(), ["source"] = "return value > 0;" };
        request["operation"] = "featureBlueprintAssemble";
        request["implementations"] = new JsonObject { ["condition"] = record.DeepClone() };
        var assembled = FeatureBlueprint.Execute(request);
        Equal("source-assembled", Text(assembled, "state"));
        string alias = Text(assembled["imports"]![0]!, "alias");
        f.Add("Api", "function", "Double", "function Api::Double (int n) -> int {}");
        f.Add("Provider", "implementation", "DoubleBody", "implementation Provider::DoubleBody for Api::Double (int n) -> int {body common \"double.csbody\";}");
        f.Body("Provider", "double.csbody", "return n * 2;");
        f.Main("provide Api::Value with Provider::ValueBody;provide Api::Double with Provider::DoubleBody;");
        f.Add("Provider", "implementation", "ValueBody", "implementation Provider::ValueBody for Api::Value (int n) -> int {import Api::Double as " + alias + " (int) -> int;blueprint common \"value.graph.json\";}");
        f.Body("Provider", "condition.node.json", record.ToJsonString());
        f.Body("Provider", "value.graph.json", graph.ToJsonString()); f.Sync();
        var built = Build(); Output(built, "4");
        True(Text(built["blueprints"]!["Provider::ValueBody"]!["sourceMap"]![1]!, "marker").Length > 50);
        request["featureContracts"]!["Api::Double"] = "function Api::Double (int n) -> bool {}";
        var invalid = FeatureBlueprint.Execute(request); Equal("invalid", Text(invalid, "state"));
        Equal("GRAPH_CALLEE_SIGNATURE", Text(invalid["diagnostics"]![0]!, "code"));
    }

    public void test_blueprint_source_change_during_real_compile_is_not_published()
    {
        Prepare(Graph()); var before = Build();
        string latest = Path.Combine(Path.GetDirectoryName(Text(before, "output"))!, "latest.json"), previous = File.ReadAllText(latest);
        string tool = Path.Combine(f.Root, "target", "blueprint-probe"); Directory.CreateDirectory(tool);
        foreach (string file in Directory.GetFiles(AppContext.BaseDirectory)) File.Copy(file, Path.Combine(tool, Path.GetFileName(file)), true);
        string node = Path.Combine(f.Packs["Provider"].Root, "add.node.json");
        File.WriteAllText(Path.Combine(tool, "blueprint-mutate-probe.json"), new JsonObject { ["node"] = node, ["target"] = f.ToolPath }.ToJsonString());
        string target = Path.Combine(f.Root, "target", "portable.celem");
        File.WriteAllText(target, File.ReadAllText(target).Replace("bin/Release/net10.0/Confectory.Build.DotNet.dll", "blueprint-probe/Confectory.Tests.dll", StringComparison.Ordinal));
        Error("BLUEPRINT_SOURCE_CHANGED", () => Build());
        Equal(previous, File.ReadAllText(latest));
        True(File.ReadAllText(node).EndsWith(" ", StringComparison.Ordinal));
    }

    public void test_blueprint_node_only_worker_draft_save_restore_and_compiler_confirm()
    {
        string feature = "function App::Value (int n) -> int {}";
        var graph = Graph(); graph["feature"] = "App::Value";
        graph["contractHash"] = FeatureBlueprint.ContractHash(new Parser(feature, "<fixture>").ParseElement());
        var request = Request(graph); request["featureSource"] = feature;
        var described = FeatureBlueprint.Execute(request);
        f.Add("App", "function", "Value", feature);
        f.Add("App", "implementation", "ValueBody", "implementation App::ValueBody for App::Value (int n) -> int {blueprint common \"value.graph.json\";}");
        f.Main("provide App::Value with App::ValueBody;");
        f.Add("App", "implementation", "MainBody", "implementation App::MainBody for App::Main () -> int {import App::Value as Value (int) -> int;body common \"main.csbody\";}");
        f.Body("App", "value.graph.json", graph.ToJsonString());
        foreach (var node in described["nodes"]!.AsArray())
        {
            string id = node!["id"]!.ToString();
            f.Body("App", id + ".node.json", new JsonObject { ["schema"] = 1, ["node"] = id, ["definitionHash"] = node["definitionHash"]!.DeepClone(), ["source"] = id == "add" ? "return value + 3;" : "return value > 0;" }.ToJsonString());
        }
        f.Sync();
        string sample = Path.Combine(f.Root, "node-owner-consumer");
        Fixture.CopyTree(Path.Combine(Fixture.Repo, "examples/edit-workspace"), sample);
        foreach (string name in new[] { "file-stream", "schema-editing", "edit-workspace", "save", "change-set", "pack-workspace", "development-tools" })
            Fixture.CopyTree(Path.Combine(Fixture.Repo, "packs", name), Path.Combine(f.Root, "packs", name));
        string project = Path.Combine(sample, "project.cpack");
        File.WriteAllText(project, File.ReadAllText(project).Replace("../../packs/", "../packs/").Replace("../../targets/dotnet/pack.cpack", "../target/pack.cpack").Replace("element Main function", "registry Confectory.PackWorkspace \"../packs/pack-workspace/pack.cpack\"; dependency Confectory.PackWorkspace version \"0.1.0\";registry Confectory.DevelopmentTools \"../packs/development-tools/pack.cpack\";dependency Confectory.DevelopmentTools version \"0.1.0\";\nelement Main function"));
        File.WriteAllText(Path.Combine(sample, "main_body.celem"), """
        implementation Example.EditWorkspace::MainBody for Example.EditWorkspace::Main () -> int {
        import Confectory.PackWorkspace::Open as Open (string,string,string) -> string;
        import Confectory.PackWorkspace::Command as Command (string,string,string) -> string;
        import Confectory.PackWorkspace::Close as Close (string) -> void;
        import Confectory.DevelopmentTools::OpenNode as OpenNode (string,string,string,string,string,string) -> string;
        import Confectory.DevelopmentTools::Open as OpenGeneral (string,string,string,string,string) -> string;
        import Confectory.DevelopmentTools::Invoke as Tool (string,string,string,string) -> string;
        import Confectory.DevelopmentTools::Definitions as Definitions (string) -> string;
        import Confectory.DevelopmentTools::Close as CloseTool (string) -> void;
        body common "main.csbody";}
        """);
        File.WriteAllText(Path.Combine(sample, "main.csbody"), """
        void Check(bool value,string message){if(!value)throw new Exception(message);}
        string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT")!,id="App::ValueBody/body:common/node:add",graphId="App::ValueBody/body:common";
        string view=calls.Open.Invoke(project,"owner","nodes");
        string selected=calls.Command.Invoke(view,"select",System.Text.Json.JsonSerializer.Serialize(new{id}));
        var unit=System.Text.Json.Nodes.JsonNode.Parse(selected)!["unit"]!;string original=unit["text"]!.ToString();
        string path=System.IO.Path.Combine(System.IO.Path.GetDirectoryName(project)!,unit["path"]!.ToString());
        string capability=calls.OpenNode.Invoke(project,"fixture","App","owner","nodes",id);
        string Invoke(string op,string call,object args)=>calls.Tool.Invoke(capability,call,op,System.Text.Json.JsonSerializer.Serialize(args));
        string Hash(string text)=>Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(text))).ToLowerInvariant();
        var defs=System.Text.Json.Nodes.JsonNode.Parse(calls.Definitions.Invoke(capability))!.AsArray();Check(defs.Count==4&&!System.Linq.Enumerable.Any(defs,d=>d!["name"]!.ToString()=="workspace_create"),"node-only tool definitions");
        var assigned=System.Text.Json.Nodes.JsonNode.Parse(Invoke("workspace_read","assigned",new{projectId="fixture",id}))!;Check(assigned["assignment"]!["definition"]!["intent"]!.ToString()=="Add three"&&assigned["assignment"]!["definition"]!["signature"]!["return"]!.ToString()=="int","Worker receives only assigned node intent and contract");
        var list=System.Text.Json.Nodes.JsonNode.Parse(Invoke("workspace_list","list",new{projectId="fixture",query=""}))!.AsArray();Check(list.Count==1&&list[0]!["id"]!.ToString()==id,"only assigned node exposed");
        bool denied=false;try{Invoke("workspace_read","wrong-target",new{projectId="fixture",id=graphId});}catch(UnauthorizedAccessException){denied=true;}Check(denied,"node capability read graph denied");
        denied=false;try{Invoke("workspace_create","wrong-right",new{projectId="fixture",id="App::Injected",kind="function"});}catch(UnauthorizedAccessException){denied=true;}Check(denied,"node capability creation denied");
        string broad=calls.OpenGeneral.Invoke(project,"fixture","App","general","other");
        denied=false;try{calls.Tool.Invoke(broad,"broad-node","workspace_read",System.Text.Json.JsonSerializer.Serialize(new{projectId="fixture",id}));}catch(UnauthorizedAccessException){denied=true;}Check(denied,"broad legacy Worker not silently granted node source");calls.CloseTool.Invoke(broad);
        var record=System.Text.Json.Nodes.JsonNode.Parse(original)!.AsObject();record["source"]="return value + 4;";string changed=record.ToJsonString();
        var conflict=System.Text.Json.Nodes.JsonNode.Parse(Invoke("workspace_stage","wrong-hash",new{projectId="fixture",id,text=changed,expectedRevision=0,expectedHash=new string('0',64)}))!;Check(conflict["conflict"]!.GetValue<bool>(),"node hash CAS");
        var result=System.Text.Json.Nodes.JsonNode.Parse(Invoke("workspace_stage","stage",new{projectId="fixture",id,text=changed,expectedRevision=0,expectedHash=Hash(original)}))!;Check(result["applied"]!.GetValue<bool>()&&!result["finalSourceChanged"]!.GetValue<bool>(),"node source draft stage");
        Check(System.IO.File.ReadAllText(path)==original,"stage preserves final source");
        calls.Command.Invoke(view,"save","{}");Check(System.IO.File.ReadAllText(path)==original,"Save preserves final source");
        calls.CloseTool.Invoke(capability);calls.Close.Invoke(view);
        view=calls.Open.Invoke(project,"owner","nodes");var reopened=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(view,"select",System.Text.Json.JsonSerializer.Serialize(new{id})))!;Check(reopened["unit"]!["text"]!.ToString()==changed,"node draft restore");
        capability=calls.OpenNode.Invoke(project,"fixture","App","owner","nodes",id);
        var graphUnit=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(view,"select",System.Text.Json.JsonSerializer.Serialize(new{id=graphId})))!["unit"]!;
        string graphOriginal=graphUnit["text"]!.ToString();var graph=System.Text.Json.Nodes.JsonNode.Parse(graphOriginal)!.AsObject();graph["nodes"]![1]!["intent"]="Changed intent";
        calls.Command.Invoke(view,"edit",System.Text.Json.JsonSerializer.Serialize(new{text=graph.ToJsonString(),expectedRevision=graphUnit["revision"]!.GetValue<long>()}));
        denied=false;try{Invoke("workspace_stage","changed-definition",new{projectId="fixture",id,text=changed,expectedRevision=reopened["unit"]!["revision"]!.GetValue<long>(),expectedHash=Hash(changed)});}catch(InvalidOperationException){denied=true;}Check(denied,"changed graph revokes assigned node definition");
        var now=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(view,"select",System.Text.Json.JsonSerializer.Serialize(new{id=graphId})))!["unit"]!;
        calls.Command.Invoke(view,"edit",System.Text.Json.JsonSerializer.Serialize(new{text=graphOriginal,expectedRevision=now["revision"]!.GetValue<long>()}));
        calls.CloseTool.Invoke(capability);calls.Command.Invoke(view,"select",System.Text.Json.JsonSerializer.Serialize(new{id}));
        var review=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(view,"review","{\"target\":\"portable\"}"))!["review"]!;
        Check(review["status"]!.ToString()=="ready","node source Review");
        var confirmation=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(view,"confirm",System.Text.Json.JsonSerializer.Serialize(new{token=review["token"]!.ToString()})))!;
        Check(confirmation["confirmation"]![0]!.ToString()=="confirmed",confirmation.ToJsonString());Check(System.IO.File.ReadAllText(path)==changed,"compiler-backed node Confirm");calls.Close.Invoke(view);
        Console.WriteLine("Blueprint node-only Worker/draft/CAS/Save/restore/graph-fence/compiler Confirm PASS");return 0;
        """);
        string? host = Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST"), selectedProject = Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT");
        try
        {
            Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST", Path.Combine(Fixture.Repo, "targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll"));
            Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT", f.Project);
            Output(new Builder(project, "portable").Build(), "Blueprint node-only Worker/draft/CAS/Save/restore/graph-fence/compiler Confirm PASS");
            Output(Build(), "6");
        }
        finally { Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST", host); Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT", selectedProject); }
    }
}
