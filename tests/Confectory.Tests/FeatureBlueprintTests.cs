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
    public void test_blueprint_disconnected_current_node_body_is_compiled_without_execution()
    {
        var graph = Graph();
        var loose = Node("loose", "next", "int", "Independent implementation before wiring");
        loose.Remove("arguments"); graph["nodes"]!.AsArray().Add(loose);
        var implementations = Prepare(graph);
        var definition = FeatureBlueprint.Execute(Request(graph, "featureBlueprintNodes"))["nodes"]!.AsArray().Single(n => Text(n!, "id") == "loose")!;
        var record = new JsonObject { ["schema"] = 1, ["node"] = "loose", ["definitionHash"] = new string('0', 64), ["source"] = "return missing;" };
        f.Body("Provider", "loose.node.json", record.ToJsonString());
        var prior = Build(); Output(prior, "5");
        var stale = prior["blueprints"]!["Provider::ValueBody"]!["nodes"]!.AsArray().Single(n => Text(n!, "id") == "loose")!;
        True(Text(stale, "status") == "stale" && !stale["includedInSource"]!.GetValue<bool>() && !stale["compilerValidated"]!.GetValue<bool>());
        string latest = Path.Combine(Path.GetDirectoryName(Text(prior, "output"))!, "latest.json"), successful = File.ReadAllText(latest);
        // A current body submitted for an independent node cannot receive a compiler receipt while ignored.
        record["definitionHash"] = definition["definitionHash"]!.DeepClone();
        implementations["loose"] = record.DeepClone();
        var described = FeatureBlueprint.Execute(Request(graph, implementations: implementations));
        var available = described["nodes"]!.AsArray().Single(n => Text(n!, "id") == "loose")!;
        True(available["compilationEligible"]!.GetValue<bool>() && !available["includedInSource"]!.GetValue<bool>() && !available["compilerValidated"]!.GetValue<bool>() && described["sourceMap"] is null, "Description is availability, not assembly or compiler evidence");
        foreach (string source in new[] { "return missing;", "int NotCalled() { return 1; } return value;", "#line 1 \"fake\"\nreturn value;" })
        {
            record["source"] = source; f.Body("Provider", "loose.node.json", record.ToJsonString());
            var error = Error("TARGET_FAILURE", () => Build());
            True(error.Message.Contains("node:Api::Value/loose", StringComparison.Ordinal), error.Message);
            if (source.Contains("NotCalled", StringComparison.Ordinal)) True(error.Message.Contains("CS8321", StringComparison.Ordinal), error.Message);
            Equal(successful, File.ReadAllText(latest));
        }
        record["source"] = "throw new System.Exception(\"Independent node must never execute\");";
        f.Body("Provider", "loose.node.json", record.ToJsonString());
        var compiled = Build(); Output(compiled, "5");
        var node = compiled["blueprints"]!["Provider::ValueBody"]!["nodes"]!.AsArray().Single(n => Text(n!, "id") == "loose")!;
        True(!node["reachable"]!.GetValue<bool>() && node["includedInSource"]!.GetValue<bool>() && node["compilerValidated"]!.GetValue<bool>());
        True(compiled["blueprints"]!["Provider::ValueBody"]!["sourceMap"]!.AsArray().Any(n => Text(n!, "node") == "loose"));
        string loosePath = Path.Combine(f.Packs["Provider"].Root, "loose.node.json"); File.Delete(loosePath);
        var missing = Build(); Output(missing, "5");
        var omitted = missing["blueprints"]!["Provider::ValueBody"]!["nodes"]!.AsArray().Single(n => Text(n!, "id") == "loose")!;
        True(Text(omitted, "status") == "missing" && !omitted["compilerValidated"]!.GetValue<bool>());
        True(missing["blueprints"]!["Provider::ValueBody"]!["inputs"]!.AsArray().All(n => n!["sha256"] is JsonValue), "Existing input path/hash shape is preserved");
        True(missing["blueprints"]!["Provider::ValueBody"]!["missingInputs"]!.AsArray().Any(n => n!["status"]?.ToString() == "missing" && n["path"]!.ToString().EndsWith("loose.node.json", StringComparison.Ordinal)));
        successful = File.ReadAllText(latest);
        string tool = Path.Combine(f.Root, "target", "blueprint-absence-probe"); Directory.CreateDirectory(tool);
        foreach (string file in Directory.GetFiles(AppContext.BaseDirectory)) File.Copy(file, Path.Combine(tool, Path.GetFileName(file)), true);
        File.WriteAllText(Path.Combine(tool, "blueprint-mutate-probe.json"), new JsonObject { ["node"] = loosePath, ["target"] = f.ToolPath, ["onlyWithBlueprintNodes"] = true }.ToJsonString());
        string target = Path.Combine(f.Root, "target", "portable.celem"); File.WriteAllText(target, File.ReadAllText(target).Replace("bin/Release/net10.0/Confectory.Build.DotNet.dll", "blueprint-absence-probe/Confectory.Tests.dll", StringComparison.Ordinal));
        Error("BLUEPRINT_SOURCE_CHANGED", () => Build());
        True(File.Exists(loosePath)); Equal(successful, File.ReadAllText(latest));
    }
    public void test_blueprint_independent_probe_checks_an_unselected_body_without_running_or_publishing()
    {
        var graph = Graph(); var records = Prepare(graph);
        f.Add("Provider", "implementation", "ValueBody", "implementation Provider::ValueBody for Api::Value (int n) -> int {blueprint common \"value.graph.json\";body portable \"alternate.csbody\";}");
        f.Body("Provider", "alternate.csbody", "return n + 100;"); f.Sync();
        var record = records["add"]!.DeepClone().AsObject(); record["source"] = "return missing_in_unselected_body;";
        f.Body("Provider", "add.node.json", record.ToJsonString());
        var selected = Build(); Output(selected, "102");
        string latest = Path.Combine(Path.GetDirectoryName(Text(selected, "output"))!, "latest.json"), prior = File.ReadAllText(latest);
        var error = Error("TARGET_FAILURE", () => new Builder(f.Project, "portable").CheckBlueprintNode("Provider::ValueBody", "common", "add"));
        True(error.Message.Contains("node:Api::Value/add", StringComparison.Ordinal), error.Message); Equal(prior, File.ReadAllText(latest));
        record["source"] = "throw new System.Exception(\"Independent compilation must not call this body\");";
        string path = f.Body("Provider", "add.node.json", record.ToJsonString());
        var result = new Builder(f.Project, "portable").CheckBlueprintNode("Provider::ValueBody", "common", "add");
        Equal("node-compiled", Text(result, "state")); Equal("common", Text(result, "bodyTarget"));
        True(result["compiled"]!.GetValue<bool>() && !result["executed"]!.GetValue<bool>() && result["nodes"]![0]!["compilerValidated"]!.GetValue<bool>());
        Equal(record["definitionHash"]!.ToString(), Text(result, "definitionHash")); Equal(JsonData.HashBytes(File.ReadAllBytes(path)), Text(result["sourceMap"]![0]!, "sourceSha256"));
        Equal("/source", Text(result["sourceMap"]![0]!, "jsonPointer")); True(Text(result, "assemblySha256").Length == 64 && Text(result, "compilerIdentity").Length == 64);
        Equal(prior, File.ReadAllText(latest)); Output(Build(), "102");
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

    public void test_blueprint_node_task_assignment_scoped_dispatch_adoption_and_cold_no_replay()
    {
        string feature = "function App::Value (int n) -> int {}";
        var graph = Graph(); graph["feature"] = "App::Value";
        graph["contractHash"] = FeatureBlueprint.ContractHash(new Parser(feature, "<fixture>").ParseElement());
        var request = Request(graph); request["featureSource"] = feature;
        var described = FeatureBlueprint.Execute(request);
        f.Add("App", "function", "Value", feature);
        f.Add("App", "implementation", "ValueBody", "implementation App::ValueBody for App::Value (int n) -> int {blueprint common \"value.graph.json\";body portable \"node-excluded.csbody\";}");
        f.Body("App", "node-excluded.csbody", "return n + 100;");
        f.Main("provide App::Value with App::ValueBody;");
        f.Add("App", "implementation", "MainBody", "implementation App::MainBody for App::Main () -> int {import App::Value as Value (int) -> int;body common \"main.csbody\";}");
        f.Body("App", "main.csbody", "Console.WriteLine(calls.Value.Invoke(2));return 0;");
        f.Body("App", "value.graph.json", graph.ToJsonString());
        foreach (var node in described["nodes"]!.AsArray())
        {
            string id = node!["id"]!.ToString();
            f.Body("App", id + ".node.json", new JsonObject { ["schema"] = 1, ["node"] = id, ["definitionHash"] = node["definitionHash"]!.DeepClone(), ["source"] = id == "add" ? "return value + 3;" : "return value > 0;" }.ToJsonString());
        }
        f.Sync();
        string sample = Path.Combine(f.Root, "node-task-consumer");
        Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","editor-home"),sample);
        string project=Path.Combine(sample,"project.cpack");
        string manifest=File.ReadAllText(project).Replace("../../",Fixture.Repo+"/",StringComparison.Ordinal);
        manifest=manifest.Insert(manifest.LastIndexOf('}'),"element NodeTaskFixture implementation \"NodeTaskFixture.celem\";\n");File.WriteAllText(project,manifest);
        string entry=Path.Combine(sample,"Main.celem");File.WriteAllText(entry,File.ReadAllText(entry).Replace("provide Confectory.Agent::Provider with Confectory.ProjectAI::Provider;","provide Confectory.Agent::Provider with Confectory.EditorHome::NodeTaskFixture;",StringComparison.Ordinal));
        File.WriteAllText(Path.Combine(sample,"NodeTaskFixture.celem"),"""
        implementation Confectory.EditorHome::NodeTaskFixture for Confectory.Agent::Provider (string config,string execution,string operation,string payload) -> string {
        import Confectory.DevelopmentTools::Invoke as Tool (string,string,string,string) -> string;
        import Confectory.DevelopmentTools::Definitions as Definitions (string) -> string;
        body common "NodeTaskFixture.csbody";}
        """);
        File.WriteAllText(Path.Combine(sample,"NodeTaskFixture.csbody"),"""
        void Check(bool yes,string why){if(!yes)throw new Exception(why);}
        string key="NodeTaskFixture."+execution;
        if(operation=="open"){
         var request=System.Text.Json.Nodes.JsonNode.Parse(payload)!;Check(request["specification"]?["kind"]?.ToString()=="blueprint-node","actual node Task execution envelope");
         AppDomain.CurrentDomain.SetData(key,request);if(request["specification"]?["rationale"]?.ToString()=="source-race-fixture")AppDomain.CurrentDomain.SetData("NodeTaskFixture.RaceOpened",true);AppDomain.CurrentDomain.SetData("NodeTaskFixture.Starts",(AppDomain.CurrentDomain.GetData("NodeTaskFixture.Starts") as int? ??0)+1);return "{}";
        }
        if(operation=="next"){
         var request=AppDomain.CurrentDomain.GetData(key) as System.Text.Json.Nodes.JsonNode;if(request is null)return "{\"kind\":\"completed\"}";
         if(request["specification"]?["rationale"]?.ToString()=="source-race-fixture"){
          if(AppDomain.CurrentDomain.GetData("NodeTaskFixture.RaceRelease") is not true)return "{\"kind\":\"wait\"}";
          string raceCap=request["input"]!["toolCapability"]!.ToString(),raceId=request["input"]!["nodeAssignment"]!["id"]!.ToString();int blocked=0;
          foreach(string op in new[]{"workspace_read","workspace_changes"})try{string output=calls.Tool.Invoke(raceCap,"race-"+op,op,op=="workspace_read"?System.Text.Json.JsonSerializer.Serialize(new{projectId="node-task-project",id=raceId}):System.Text.Json.JsonSerializer.Serialize(new{projectId="node-task-project"}));if(output.Contains("peer-content-after-approval",StringComparison.Ordinal))AppDomain.CurrentDomain.SetData("NodeTaskFixture.RaceLeak",true);}catch(InvalidOperationException){blocked++;}
          var raceCandidate=new System.Text.Json.Nodes.JsonObject{["schema"]=1,["node"]=raceId[(raceId.LastIndexOf("/node:",StringComparison.Ordinal)+6)..],["definitionHash"]=request["input"]!["nodeAssignment"]!["definitionHash"]!.DeepClone(),["source"]="return value + 99;"};
          try{calls.Tool.Invoke(raceCap,"race-stage","workspace_stage",System.Text.Json.JsonSerializer.Serialize(new{projectId="node-task-project",id=raceId,text=raceCandidate.ToJsonString(),expectedRevision=(long)AppDomain.CurrentDomain.GetData("NodeTaskFixture.RacePeerRevision")!,expectedHash=(string)AppDomain.CurrentDomain.GetData("NodeTaskFixture.RacePeerHash")!}));}catch(InvalidOperationException){blocked++;}
          AppDomain.CurrentDomain.SetData("NodeTaskFixture.RaceBlocked",blocked);AppDomain.CurrentDomain.SetData(key,null);return blocked==3?"{\"kind\":\"error\",\"errorCode\":\"provider-tool-error\"}":"{\"kind\":\"completed\"}";
         }
         AppDomain.CurrentDomain.SetData(key,null);string cap=request["input"]!["toolCapability"]!.ToString(),id=request["input"]!["nodeAssignment"]!["id"]!.ToString();
         string Invoke(string name,string call,object value)=>calls.Tool.Invoke(cap,call,name,System.Text.Json.JsonSerializer.Serialize(value));
         var defs=System.Text.Json.Nodes.JsonNode.Parse(calls.Definitions.Invoke(cap))!.AsArray();Check(defs.Count==4,"four node-only tool rights");
         var unit=System.Text.Json.Nodes.JsonNode.Parse(Invoke("workspace_read","read-node",new{projectId="node-task-project",id}))!;
         Check(unit["assignment"]!["id"]!.ToString()==id,"actual scoped node capability");
         foreach(string denied in new[]{"App::ValueBody/body:common","App::ValueBody/body:common/node:condition","App::Value"}){
          bool refused=false;try{Invoke("workspace_read","read-"+Guid.NewGuid().ToString("N"),new{projectId="node-task-project",id=denied});}catch(UnauthorizedAccessException){refused=true;}Check(refused,"other source denied: "+denied);
         }
         bool create=false;try{Invoke("workspace_create","create",new{projectId="node-task-project",id="App::Injected",kind="function"});}catch(UnauthorizedAccessException){create=true;}Check(create,"create denied");
         bool confirm=false;try{Invoke("workspace_confirm","confirm",new{projectId="node-task-project"});}catch(UnauthorizedAccessException){confirm=true;}Check(confirm,"Confirm denied");
         var record=System.Text.Json.Nodes.JsonNode.Parse(unit["text"]!.ToString())!;record["source"]="return value + 7;";
         var staged=System.Text.Json.Nodes.JsonNode.Parse(Invoke("workspace_stage","stage-node",new{projectId="node-task-project",id,text=record.ToJsonString(),expectedRevision=unit["revision"]!.GetValue<long>(),expectedHash=unit["textHash"]!.ToString()}))!;
         Check(staged["applied"]!.GetValue<bool>()&&!staged["finalSourceChanged"]!.GetValue<bool>(),"scoped real source draft stage");
         Check(System.Text.Json.Nodes.JsonNode.Parse(Invoke("workspace_read","own-stage-read",new{projectId="node-task-project",id}))!["text"]!.ToString()==record.ToJsonString(),"Worker can read its own accepted stage");
         AppDomain.CurrentDomain.SetData("NodeTaskFixture.Staged",true);return "{\"kind\":\"delta\",\"text\":\"Assigned node implemented in a scoped draft; user review and compiler confirmation required.\"}";
        }
        return "{}";
        """);
        File.WriteAllText(Path.Combine(sample,"MainBody.celem"),"""
        implementation Confectory.EditorHome::MainBody for Confectory.EditorHome::Main () -> int {
        import Confectory.Helper::Open as HelpersOpen (string) -> string;
        import Confectory.Helper::Recruit as Recruit (string,string,string) -> string;
        import Confectory.Helper::Close as HelpersClose (string) -> void;
        import Confectory.ProjectAI::Open as Open (string,string,string,string,string) -> string;
        import Confectory.ProjectAI::OpenLocal as OpenLocal (string,string,string,string) -> string;
        import Confectory.ProjectAI::EnableTasks as EnableTasks (string,string,string[],string[]) -> void;
        import Confectory.ProjectAI::NodeTask as NodeTask (string,string,string) -> string;
        import Confectory.ProjectAI::Work as Work (string,string,string,string) -> string;
        import Confectory.ProjectAI::Poll as Poll (string) -> string;
        import Confectory.ProjectAI::Close as Close (string) -> void;
        import Confectory.ProjectAI::Adopt as Adopt (string,string,string,string,string[],string) -> string;
        import Confectory.WorkerTasks::VerifyCompletion as VerifyCompletion (string,string,string) -> bool;
        import Confectory.PackWorkspace::Open as ViewOpen (string,string,string) -> string;
        import Confectory.PackWorkspace::Command as ViewCommand (string,string,string) -> string;
        import Confectory.PackWorkspace::Close as ViewClose (string) -> void;
        body common "Main.csbody";}
        """);
        File.WriteAllText(Path.Combine(sample,"Main.csbody"),"""
        void Check(bool yes,string why){if(!yes)throw new Exception(why);}
        System.Text.Json.Nodes.JsonNode Json(string text)=>System.Text.Json.Nodes.JsonNode.Parse(text)!;
        string Serialize(object value)=>System.Text.Json.JsonSerializer.Serialize(value);
        int Starts()=>AppDomain.CurrentDomain.GetData("NodeTaskFixture.Starts") as int? ??0;
        string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT")!,node="App::ValueBody/body:common/node:add",graphId="App::ValueBody/body:common";
        string directory=System.IO.Path.Combine(System.IO.Path.GetDirectoryName(project)!,"fixture-helpers");System.IO.Directory.CreateDirectory(directory);
        string helpers=calls.HelpersOpen.Invoke(directory),view=calls.ViewOpen.Invoke(project,"local-user","editor"),owner="";
        calls.Recruit.Invoke(helpers,"local-user","{\"helper\":\"main-helper\",\"owner\":\"local-user\",\"personality\":\"Fixture\",\"speciality\":\"Node scope\",\"membership\":{\"kind\":\"global\"}}");
        string context="{\"helper\":\"main-helper\",\"projectId\":\"node-task-project\",\"membership\":{\"kind\":\"global\"},\"profile\":{},\"memory\":[],\"legacyMemoryExcluded\":true}",config="{\"provider\":\"responses\",\"model\":\"owned-fixture\",\"endpoint\":\"owned-fixture\"}";
        string Inspect()=>calls.NodeTask.Invoke(owner,"inspect",Serialize(new{node}));
        try{
         owner=calls.OpenLocal.Invoke(project,"node-task-project","App",context);calls.EnableTasks.Invoke(owner,helpers,new[]{"App::Value"},new[]{"description"});
         var plan=Json(Inspect());Check(plan["definition"]!["intent"]!.ToString()=="Add three"&&Starts()==0,"plan before model approval does not invoke Agent");
         string stale="";try{calls.NodeTask.Invoke(owner,"assign",Serialize(new{node,assignmentHash=new string('0',64),commandID="stale-assign",rationale="Fixture"}));}catch(InvalidOperationException){stale="denied";}Check(stale=="denied","stale assignment hash denied");
         string assigned=calls.NodeTask.Invoke(owner,"assign",Serialize(new{node,assignmentHash=plan["assignmentHash"]!.ToString(),commandID="assign-one",rationale="Implement this inspected node"})),task=Json(assigned)["task"]!.ToString();
         Check(calls.NodeTask.Invoke(owner,"assign",Serialize(new{node,assignmentHash=plan["assignmentHash"]!.ToString(),commandID="assign-one",rationale="Implement this inspected node"}))==assigned&&Starts()==0,"durable idempotent node assignment without execution");
         bool localDenied=false;try{calls.NodeTask.Invoke(owner,"work",Serialize(new{task,commandID="start-local",authorization=new{}}));}catch(InvalidOperationException){localDenied=true;}Check(localDenied&&Starts()==0,"local planning has no model authority");
         calls.Close.Invoke(owner);owner=calls.Open.Invoke(project,"node-task-project","App",context,config);calls.EnableTasks.Invoke(owner,helpers,new[]{"App::Value"},new[]{"description"});
         var worker=Json(calls.Poll.Invoke(owner))["workers"]![task]!;Check(worker["specification"]!["blueprintNode"]!["assignmentHash"]!.ToString()==plan["assignmentHash"]!.ToString()&&worker["status"]!.ToString()=="ready"&&Starts()==0,"cold immutable assignment, no replay");
         object Grant(string hash)=>new{projectId="node-task-project",task,assignmentHash=hash,model="owned-fixture",endpoint="owned-fixture",contentApproved=true,usageApproved=true};
         bool broad=false;try{calls.Work.Invoke(owner,"broad",task,Serialize(Grant(plan["assignmentHash"]!.ToString())));}catch(UnauthorizedAccessException){broad=true;}Check(broad&&Starts()==0,"ordinary Worker cannot acquire broad node Task tools");
         bool wrong=false;try{calls.NodeTask.Invoke(owner,"work",Serialize(new{task,commandID="wrong-grant",authorization=Grant(new string('0',64))}));}catch(UnauthorizedAccessException){wrong=true;}Check(wrong&&Starts()==0,"approval binds exact node assignment");
         foreach(string field in new[]{"task","model","endpoint","usageApproved"}){var deniedGrant=Json(Serialize(Grant(plan["assignmentHash"]!.ToString())));if(field=="usageApproved")deniedGrant[field]=false;else deniedGrant[field]="other";bool denied=false;try{calls.NodeTask.Invoke(owner,"work",Serialize(new{task,commandID="deny-"+field,authorization=deniedGrant}));}catch(UnauthorizedAccessException){denied=true;}Check(denied&&Starts()==0,"exact node approval field: "+field);}

         var graphUnit=Json(calls.ViewCommand.Invoke(view,"select",Serialize(new{id=graphId})))["unit"]!;string originalGraph=graphUnit["text"]!.ToString();var changed=Json(originalGraph);changed["nodes"]![1]!["intent"]="Different node intent";
         calls.ViewCommand.Invoke(view,"edit",Serialize(new{text=changed.ToJsonString(),expectedRevision=graphUnit["revision"]!.GetValue<long>()}));
         bool definition=false;try{calls.NodeTask.Invoke(owner,"work",Serialize(new{task,commandID="changed-definition",authorization=Grant(plan["assignmentHash"]!.ToString())}));}catch(InvalidOperationException){definition=true;}Check(definition&&Starts()==0,"definition change denies before Agent");
         graphUnit=Json(calls.ViewCommand.Invoke(view,"select",Serialize(new{id=graphId})))["unit"]!;var reordered=Json(originalGraph);var edges=reordered["edges"]!.AsArray();var first=edges[0]!.DeepClone();edges.RemoveAt(0);edges.Add(first);
         calls.ViewCommand.Invoke(view,"edit",Serialize(new{text=reordered.ToJsonString(),expectedRevision=graphUnit["revision"]!.GetValue<long>()}));
         Check(Json(Inspect())["assignmentHash"]!.ToString()==plan["assignmentHash"]!.ToString(),"topology arrangement does not require node reimplementation");
         // Keep the semantically reordered graph draft while dispatching; no node reimplementation is required.
         var source=Json(calls.ViewCommand.Invoke(view,"select",Serialize(new{id=node})))["unit"]!;string original=source["text"]!.ToString(),sourcePath=System.IO.Path.Combine(System.IO.Path.GetDirectoryName(project)!,source["path"]!.ToString());
         calls.NodeTask.Invoke(owner,"work",Serialize(new{task,commandID="start-node",authorization=Grant(plan["assignmentHash"]!.ToString())}));
         var timer=System.Diagnostics.Stopwatch.StartNew();while(timer.ElapsedMilliseconds<10000){worker=Json(calls.Poll.Invoke(owner))["workers"]![task]!;if(worker["status"]!.ToString()!="running")break;System.Threading.Thread.Sleep(10);}
         Check(worker["status"]!.ToString()=="awaiting-verification"&&Starts()==1&&AppDomain.CurrentDomain.GetData("NodeTaskFixture.Staged") is true,"actual scoped Agent stages node and awaits independent verification: "+worker.ToJsonString());
         Check(System.IO.File.ReadAllText(sourcePath)==original,"Worker preserves final source");
         bool replay=false;try{calls.NodeTask.Invoke(owner,"work",Serialize(new{task,commandID="replay",authorization=Grant(plan["assignmentHash"]!.ToString())}));}catch(InvalidOperationException){replay=true;}Check(replay&&Starts()==1,"no completed execution replay");
         bool adoptOther=false;try{calls.Adopt.Invoke(owner,task,view,"unused",new[]{graphId},"Fixture user acceptance");}catch(UnauthorizedAccessException){adoptOther=true;}Check(adoptOther&&System.IO.File.ReadAllText(sourcePath)==original,"node adoption must include its assigned node");
         bool unrelated=false;try{calls.Adopt.Invoke(owner,task,view,"unused",new[]{node,"App::Main"},"Fixture acceptance");}catch(UnauthorizedAccessException){unrelated=true;}Check(unrelated&&System.IO.File.ReadAllText(sourcePath)==original,"node adoption cannot add unrelated declarations");
         var completedDraft=Json(calls.ViewCommand.Invoke(view,"select",Serialize(new{id=node})))["unit"]!;string workerDraft=completedDraft["text"]!.ToString(),projectManifest=System.IO.File.ReadAllText(project);
         var packLines=System.Linq.Enumerable.Where(projectManifest.Replace("project App ","pack App ",StringComparison.Ordinal).Split('\n'),line=>!line.TrimStart().StartsWith("entry ",StringComparison.Ordinal)&&!line.TrimStart().StartsWith("registry ",StringComparison.Ordinal)&&!line.TrimStart().StartsWith("target ",StringComparison.Ordinal)&&!line.TrimStart().StartsWith("always ",StringComparison.Ordinal));
         bool packDenied=false;
         try{
          System.IO.File.WriteAllText(project,string.Join("\n",packLines));
          var invalidNode=Json(workerDraft);invalidNode["source"]="return missing_pack_compiler_verification;";calls.ViewCommand.Invoke(view,"edit",Serialize(new{text=invalidNode.ToJsonString(),expectedRevision=completedDraft["revision"]!.GetValue<long>()}));
          var packReview=Json(calls.ViewCommand.Invoke(view,"review",Serialize(new{target="portable",ids=new[]{node}})))["review"]!;Check(packReview["status"]!.ToString()=="ready","owned pack source review is not C# compilation");
          try{calls.Adopt.Invoke(owner,task,view,packReview["token"]!.ToString(),new[]{node},"Pack syntax-only validation must not complete a compiled node Task.");}catch(InvalidOperationException){packDenied=true;}
         }finally{System.IO.File.WriteAllText(project,projectManifest);}
         Check(packDenied&&System.IO.File.ReadAllText(sourcePath)==original&&Json(calls.Poll.Invoke(owner))["workers"]![task]!["status"]!.ToString()=="awaiting-verification","pack syntax-only validation cannot publish or complete node code");
         completedDraft=Json(calls.ViewCommand.Invoke(view,"select",Serialize(new{id=node})))["unit"]!;calls.ViewCommand.Invoke(view,"edit",Serialize(new{text=workerDraft,expectedRevision=completedDraft["revision"]!.GetValue<long>()}));
         completedDraft=Json(calls.ViewCommand.Invoke(view,"select",Serialize(new{id=node})))["unit"]!;var excludedNode=Json(workerDraft);excludedNode["source"]="return missing_in_an_unselected_target_body;";calls.ViewCommand.Invoke(view,"edit",Serialize(new{text=excludedNode.ToJsonString(),expectedRevision=completedDraft["revision"]!.GetValue<long>()}));
         var excludedReview=Json(calls.ViewCommand.Invoke(view,"review",Serialize(new{target="portable",ids=new[]{node}})))["review"]!;bool excludedDenied=false;
         try{calls.Adopt.Invoke(owner,task,view,excludedReview["token"]!.ToString(),new[]{node},"An alternate target implementation must not bypass the assigned node compiler check.");}catch(InvalidOperationException){excludedDenied=true;}
         Check(excludedDenied&&System.IO.File.ReadAllText(sourcePath)==original&&Json(calls.Poll.Invoke(owner))["workers"]![task]!["status"]!.ToString()=="awaiting-verification","selected target cannot skip compilation of the assigned common node body");
         completedDraft=Json(calls.ViewCommand.Invoke(view,"select",Serialize(new{id=node})))["unit"]!;calls.ViewCommand.Invoke(view,"edit",Serialize(new{text=workerDraft,expectedRevision=completedDraft["revision"]!.GetValue<long>()}));
         var implementationUnit=Json(calls.ViewCommand.Invoke(view,"select",Serialize(new{id="App::ValueBody"})))["unit"]!;string commonImplementation=implementationUnit["text"]!.ToString().Replace("body portable \"node-excluded.csbody\";","",StringComparison.Ordinal);calls.ViewCommand.Invoke(view,"edit",Serialize(new{text=commonImplementation,expectedRevision=implementationUnit["revision"]!.GetValue<long>()}));
         graphUnit=Json(calls.ViewCommand.Invoke(view,"select",Serialize(new{id=graphId})))["unit"]!;string beforeAdoptionGraph=graphUnit["text"]!.ToString();var staleGraph=Json(beforeAdoptionGraph);staleGraph["nodes"]![1]!["intent"]="A new independent definition after the assigned work";foreach(var edge in staleGraph["edges"]!.AsArray())if(edge!["from"]!.ToString()=="condition")edge["to"]="exit:negative";
         calls.ViewCommand.Invoke(view,"edit",Serialize(new{text=staleGraph.ToJsonString(),expectedRevision=graphUnit["revision"]!.GetValue<long>()}));
         var staleReview=Json(calls.ViewCommand.Invoke(view,"review",Serialize(new{target="portable",ids=new[]{graphId,node}})))["review"]!;Check(staleReview["status"]!.ToString()=="ready","independent stale node is still a user-reviewable source draft");
         bool staleCompletion=false;try{calls.Adopt.Invoke(owner,task,view,staleReview["token"]!.ToString(),new[]{graphId,node},"The changed graph must not bypass assigned-node compiler verification.");}catch(InvalidOperationException){staleCompletion=true;}
         Check(staleCompletion&&System.IO.File.ReadAllText(sourcePath)==original&&Json(calls.Poll.Invoke(owner))["workers"]![task]!["status"]!.ToString()=="awaiting-verification","stale independent node cannot be completed by a compiler which skips it");
         graphUnit=Json(calls.ViewCommand.Invoke(view,"select",Serialize(new{id=graphId})))["unit"]!;calls.ViewCommand.Invoke(view,"edit",Serialize(new{text=beforeAdoptionGraph,expectedRevision=graphUnit["revision"]!.GetValue<long>()}));
         calls.ViewCommand.Invoke(view,"select",Serialize(new{id=node}));var review=Json(calls.ViewCommand.Invoke(view,"review",Serialize(new{target="portable",ids=new[]{node,"App::ValueBody"}})))["review"]!;Check(review["status"]!.ToString()=="ready","actual compiler-ready node review");
         string nodeProof=calls.Adopt.Invoke(owner,task,view,review["token"]!.ToString(),new[]{node,"App::ValueBody"},"Fixture accepts the implementation; runtime is independently tested below.");
         Check(Json(calls.Poll.Invoke(owner))["workers"]![task]!["status"]!.ToString()=="completed"&&Json(System.IO.File.ReadAllText(sourcePath))["source"]!.ToString()=="return value + 7;","compiler-backed node adoption");
         var nodeVerification=Json(nodeProof)["nodeVerification"]!;Check(nodeVerification["compilerConfirmed"]!.GetValue<bool>()&&nodeVerification["independentCompilerRequired"]!.GetValue<bool>()&&nodeVerification["definitionHash"]!.ToString()==plan["assignment"]!["definitionHash"]!.ToString()&&nodeVerification["sourceHash"]!.ToString()==Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(System.IO.File.ReadAllText(sourcePath)))).ToLowerInvariant(),"completion pins actual compiled node definition and source");
         Check(nodeVerification["mode"]!.ToString()=="independent-node"&&nodeVerification["bodyTarget"]!.ToString()=="common"&&nodeVerification["assemblySha256"]!.ToString().Length==64&&nodeVerification["compilerIdentity"]!.ToString().Length==64&&!nodeVerification["executed"]!.GetValue<bool>(),"actual independent node compiler evidence is retained");
         var completedWorker=Json(calls.Poll.Invoke(owner))["workers"]![task]!;
         string specification=completedWorker["specification"]!.ToJsonString(),progress=completedWorker["progress"]!.ToString();
         Check(calls.VerifyCompletion.Invoke(specification,progress,nodeProof),"actual node compiler receipt satisfies the completion verifier");
         var retainedReceipt=(System.Text.Json.Nodes.JsonObject)AppDomain.CurrentDomain.GetData("Confectory.ProjectAI.Receipt."+Json(nodeProof)["receipt"]!.ToString())!;
         var retainedVerification=retainedReceipt["nodeVerification"]!.DeepClone();
         try{
          foreach(string required in new[]{"mode","independentCompilerRequired","compilerConfirmed","executed","compilerIdentity","artifactKey","assemblySha256","referenceSha256","sourceHash","definitionHash","bodyTarget","sourcePath"}){
           var legacyProof=Json(nodeProof);legacyProof["nodeVerification"]!.AsObject().Remove(required);retainedReceipt["nodeVerification"]=legacyProof["nodeVerification"]!.DeepClone();
           Check(!calls.VerifyCompletion.Invoke(specification,progress,legacyProof.ToJsonString()),"Incomplete retained node compiler evidence cannot satisfy completion: "+required);
          }
          retainedReceipt["nodeVerification"]=retainedVerification.DeepClone();var mismatched=Json(nodeProof);mismatched["nodeVerification"]!["sourceHash"]=new string('0',64);
          Check(!calls.VerifyCompletion.Invoke(specification,progress,mismatched.ToJsonString()),"completion proof must match its retained compiler receipt");
         }finally{retainedReceipt["nodeVerification"]=retainedVerification.DeepClone();}
         var confirmedTime=System.IO.File.GetLastWriteTimeUtc(sourcePath);Check(calls.Adopt.Invoke(owner,task,view,"no-confirm-replay",new[]{node,"App::ValueBody"},"Retry only the retained receipt")==nodeProof&&System.IO.File.GetLastWriteTimeUtc(sourcePath)==confirmedTime&&Starts()==1,"same node completion proof without confirmation or Agent replay");
         calls.Close.Invoke(owner);owner=calls.OpenLocal.Invoke(project,"node-task-project","App",context);calls.EnableTasks.Invoke(owner,helpers,new[]{"App::Value"},new[]{"description"});
         Check(Json(calls.Poll.Invoke(owner))["workers"]![task]!["status"]!.ToString()=="completed"&&Starts()==1,"cold completion without Agent replay");
         var fresh=Json(Inspect());var readyTask=Json(calls.NodeTask.Invoke(owner,"assign",Serialize(new{node,assignmentHash=fresh["assignmentHash"]!.ToString(),commandID="assign-ready-cancel",rationale="Explicit ready cancellation fixture"})))["task"]!.ToString();
         string cancel=Serialize(new{task=readyTask,commandID="cancel-node-ready"});calls.NodeTask.Invoke(owner,"cancel",cancel);string saved=System.IO.File.ReadAllText(System.IO.Path.Combine(System.IO.Path.GetDirectoryName(project)!,".confectory","ai-development","tasks.json"));calls.NodeTask.Invoke(owner,"cancel",cancel);
         Check(System.IO.File.ReadAllText(System.IO.Path.Combine(System.IO.Path.GetDirectoryName(project)!,".confectory","ai-development","tasks.json"))==saved&&Json(calls.Poll.Invoke(owner))["workers"]![readyTask]!["status"]!.ToString()=="cancelled"&&Starts()==1,"node ready cancellation is durable, idempotent and starts no Agent");
         bool completedCancel=false;try{calls.NodeTask.Invoke(owner,"cancel",Serialize(new{task,commandID="cancel-completed"}));}catch(InvalidOperationException){completedCancel=true;}Check(completedCancel&&Starts()==1,"completed node Task cannot be cancelled as ready");
         calls.Close.Invoke(owner);owner=calls.Open.Invoke(project,"node-task-project","App",context,config);calls.EnableTasks.Invoke(owner,helpers,new[]{"App::Value"},new[]{"description"});
         var racePlan=Json(Inspect());string raceTask=Json(calls.NodeTask.Invoke(owner,"assign",Serialize(new{node,assignmentHash=racePlan["assignmentHash"]!.ToString(),commandID="assign-source-race",rationale="source-race-fixture"})))["task"]!.ToString();
         calls.NodeTask.Invoke(owner,"work",Serialize(new{task=raceTask,commandID="work-source-race",authorization=new{projectId="node-task-project",task=raceTask,assignmentHash=racePlan["assignmentHash"]!.ToString(),model="owned-fixture",endpoint="owned-fixture",contentApproved=true,usageApproved=true}}));
         var opened=System.Diagnostics.Stopwatch.StartNew();while(AppDomain.CurrentDomain.GetData("NodeTaskFixture.RaceOpened") is not true&&opened.ElapsedMilliseconds<5000)System.Threading.Thread.Sleep(5);Check(AppDomain.CurrentDomain.GetData("NodeTaskFixture.RaceOpened") is true,"actual owned race provider opened");
         var beforeRace=Json(calls.ViewCommand.Invoke(view,"select",Serialize(new{id=node})))["unit"]!;string retainedText=beforeRace["text"]!.ToString();
         try{
          var peer=Json(retainedText);peer["source"]=peer["source"]!.ToString()+"\n// peer-content-after-approval";string peerText=peer.ToJsonString();calls.ViewCommand.Invoke(view,"edit",Serialize(new{text=peerText,expectedRevision=beforeRace["revision"]!.GetValue<long>()}));var peerObserved=Json(calls.ViewCommand.Invoke(view,"select",Serialize(new{id=node})))["unit"]!;AppDomain.CurrentDomain.SetData("NodeTaskFixture.RacePeerRevision",peerObserved["revision"]!.GetValue<long>());AppDomain.CurrentDomain.SetData("NodeTaskFixture.RacePeerHash",Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(peerText))).ToLowerInvariant());AppDomain.CurrentDomain.SetData("NodeTaskFixture.RaceRelease",true);
          var done=System.Diagnostics.Stopwatch.StartNew();System.Text.Json.Nodes.JsonNode raceRow=Json(calls.Poll.Invoke(owner))["workers"]![raceTask]!;while(raceRow["status"]!.ToString()=="running"&&done.ElapsedMilliseconds<5000){System.Threading.Thread.Sleep(5);raceRow=Json(calls.Poll.Invoke(owner))["workers"]![raceTask]!;}
          Check(AppDomain.CurrentDomain.GetData("NodeTaskFixture.RaceBlocked") is 3&&AppDomain.CurrentDomain.GetData("NodeTaskFixture.RaceLeak") is not true&&raceRow["status"]!.ToString()=="error","Source changed after exact approval must fence read/changes/stage even with correct peer CAS metadata before returning or replacing peer text; actual blocked="+AppDomain.CurrentDomain.GetData("NodeTaskFixture.RaceBlocked")+", leak="+AppDomain.CurrentDomain.GetData("NodeTaskFixture.RaceLeak")+", state="+raceRow["status"]);
          Check(Json(calls.ViewCommand.Invoke(view,"select",Serialize(new{id=node})))["unit"]!["text"]!.ToString()==peerText,"peer source remains intact after stale Worker stage refusal");
         }finally{AppDomain.CurrentDomain.SetData("NodeTaskFixture.RaceRelease",true);var currentRace=Json(calls.ViewCommand.Invoke(view,"select",Serialize(new{id=node})))["unit"]!;calls.ViewCommand.Invoke(view,"edit",Serialize(new{text=retainedText,expectedRevision=currentRace["revision"]!.GetValue<long>()}));}

        }finally{if(owner.Length>0)calls.Close.Invoke(owner);calls.ViewClose.Invoke(view);calls.HelpersClose.Invoke(helpers);}
        Console.WriteLine("Blueprint node Task assignment/scoped dispatch/adoption/cold no-replay PASS");return 0;
        """);
        string? host=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST"),selected=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT");
        try{
            Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll"));
            Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",f.Project);
            var built=new Builder(project,"linux").Build();
            // This consumer includes real compiler probes and source Confirm, including cold caches.
            var run=Processes.Run(Strings(built,"run"),timeoutSeconds:180);True(run.ExitCode==0,run.Stdout+run.Stderr);Equal("Blueprint node Task assignment/scoped dispatch/adoption/cold no-replay PASS\n",run.Stdout.Replace("\r\n","\n",StringComparison.Ordinal));
            Output(Build(),"9");
        }finally{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",selected);}
    }

    public void test_blueprint_new_feature_registration_contract_group_compiler_and_cold_restore()
    {
        f.Sync();string sample=Path.Combine(f.Root,"feature-creation-consumer");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples/edit-workspace"),sample);
        foreach(string name in new[]{"file-stream","schema-editing","edit-workspace","save","change-set","pack-workspace","development-tools"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",name),Path.Combine(f.Root,"packs",name));
        string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/").Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack").Replace("element Main function","registry Confectory.PackWorkspace \"../packs/pack-workspace/pack.cpack\";dependency Confectory.PackWorkspace version \"0.1.0\";registry Confectory.DevelopmentTools \"../packs/development-tools/pack.cpack\";dependency Confectory.DevelopmentTools version \"0.1.0\";\nelement Main function"));
        string composition=Path.Combine(sample,"main.celem"),compositionText=File.ReadAllText(composition);File.WriteAllText(composition,compositionText.Insert(compositionText.LastIndexOf('}'),"provide Confectory.FileStream::BrowseDirectory with Confectory.FileStream::BrowseDirectoryBody;"));
        File.WriteAllText(Path.Combine(sample,"main_body.celem"),"""
        implementation Example.EditWorkspace::MainBody for Example.EditWorkspace::Main () -> int {
        import Confectory.PackWorkspace::Open as Open (string,string,string) -> string;
        import Confectory.PackWorkspace::Command as Command (string,string,string) -> string;
        import Confectory.PackWorkspace::Snapshot as Snapshot (string) -> string;
        import Confectory.PackWorkspace::Blueprint as Blueprint (string,string,string) -> string;
        import Confectory.PackWorkspace::Close as Close (string) -> void;
        import Confectory.PackWorkspace::BorrowDraft as BorrowDraft (string) -> string;
        import Confectory.EditWorkspace::Export as Export (string) -> string;
        import Confectory.EditWorkspace::Restore as Restore (string,string) -> void;
        import Confectory.EditWorkspace::BlueprintFeature as PrepareOwnedFeature (string,string,string[],long[],string[]) -> string;
        import Confectory.EditWorkspace::Changes as Changes (string,string[]) -> string[];
        import Confectory.EditWorkspace::EditBatch as EditBatch (string,string[],string[],long[],string[]) -> bool;
        import Confectory.ChangeSet::ConfirmReviewed as ConfirmDirect (string,string[],string,string[]) -> string[];
        import Confectory.DevelopmentTools::OpenNode as OpenNode (string,string,string,string,string,string) -> string;
        import Confectory.DevelopmentTools::Snapshot as ToolSnapshot (string) -> string;
        import Confectory.DevelopmentTools::Close as CloseTool (string) -> void;
        import Confectory.SchemaEditing::Call as Metadata (string,string) -> string;
        body common "main.csbody";}
        """);
        File.WriteAllText(Path.Combine(sample,"main.csbody"),"""
        void Check(bool value,string why){if(!value)throw new Exception(why);}
        System.Text.Json.Nodes.JsonNode Json(string value)=>System.Text.Json.Nodes.JsonNode.Parse(value)!;
        string Serialize(object value)=>System.Text.Json.JsonSerializer.Serialize(value);
        string Hash(string value)=>Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(value))).ToLowerInvariant();
        string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT")!,root=System.IO.Path.GetDirectoryName(project)!,feature="App::Fresh";
        string view=calls.Open.Invoke(project,"owner","create-feature"),peer=calls.Open.Invoke(project,"owner","create-feature");
        System.Text.Json.Nodes.JsonNode Cmd(string op,object value)=>Json(calls.Command.Invoke(view,op,Serialize(value)));
        System.Text.Json.Nodes.JsonNode Blueprint(string op,object value)=>Json(calls.Blueprint.Invoke(view,op,Serialize(value)));
        System.Text.Json.Nodes.JsonNode Prepare(){var unit=Cmd("select",new{id=feature})["unit"]!;return Blueprint("readFeature",new{id=feature,revision=unit["revision"]!.GetValue<long>(),hash=Hash(unit["text"]!.ToString())});}
        void Refused(Action action,string why){bool refused=false;try{action();}catch(InvalidOperationException){refused=true;}catch(ArgumentException){refused=true;}Check(refused,why);}
        var originals=new System.Collections.Generic.Dictionary<string,byte[]>();foreach(string path in System.IO.Directory.GetFiles(root))originals[path]=System.IO.File.ReadAllBytes(path);
        string[] Group(System.Text.Json.Nodes.JsonNode graph){var result=new System.Collections.Generic.List<string>();foreach(var item in graph["reviewIds"]!.AsArray())result.Add(item!.ToString());return result.ToArray();}
        bool Missing(string[] paths){foreach(string path in paths)if(System.IO.File.Exists(path))return false;return true;}
        try{
         Refused(()=>Blueprint("readFeature",new{id="App::Main",revision=0,hash=new string('0',64)}),"published function cannot be implicitly converted");
         var unit=Cmd("create",new{kind="function",id=feature})["unit"]!;string function="function App::Fresh (int n) -> int {description \"Add nine using the new feature contract\";value editorName = \"Fresh feature\";}";
         Cmd("edit",new{text=function,expectedRevision=unit["revision"]!.GetValue<long>()});var stale=Prepare();unit=Cmd("select",new{id=feature})["unit"]!;Cmd("edit",new{text=function+" ",expectedRevision=unit["revision"]!.GetValue<long>()});
         Refused(()=>Blueprint("createFeature",new{id=feature,basis=stale["basis"]!.ToString()}),"peer contract changes fence registration without partial sources");
         unit=Cmd("select",new{id=feature})["unit"]!;Cmd("edit",new{text=function,expectedRevision=unit["revision"]!.GetValue<long>()});
         int stableOwnedCount=Json(calls.Snapshot.Invoke(view))["ownedTotal"]!.GetValue<int>();string ownedHandle=calls.BorrowDraft.Invoke(view),validSaved=calls.Export.Invoke(ownedHandle);var damaged=Json(validSaved);foreach(var row in damaged["changes"]!.AsArray())if(row!["id"]!.ToString()==feature)row["draft"]="function App::WrongIdentity (int n) -> int {}";calls.Restore.Invoke(ownedHandle,damaged.ToJsonString());
         Refused(()=>Prepare(),"restored declaration identity must match the selected owned function before preview");unit=Cmd("select",new{id=feature})["unit"]!;var registration=Cmd("select",new{id="App::ProjectManifest"})["unit"]!;Refused(()=>calls.PrepareOwnedFeature.Invoke(ownedHandle,feature,new[]{feature,"App::ProjectManifest"},new[]{unit["revision"]!.GetValue<long>(),registration["revision"]!.GetValue<long>()},new[]{Hash(unit["text"]!.ToString()),Hash(registration["text"]!.ToString())}),"direct owner creation must also reject a mismatched restored contract without adding graph membership");Check(Json(calls.Snapshot.Invoke(view))["ownedTotal"]!.GetValue<int>()==stableOwnedCount,"invalid restored identity adds no source units");calls.Restore.Invoke(ownedHandle,validSaved);
         string collision=System.IO.Path.Combine(root,"elements/FreshBlueprintBody.celem");System.IO.Directory.CreateDirectory(System.IO.Path.GetDirectoryName(collision)!);System.IO.File.WriteAllText(collision,"foreign destination");var before=Json(calls.Snapshot.Invoke(view));var ready=Prepare();
         Refused(()=>Blueprint("createFeature",new{id=feature,basis=ready["basis"]!.ToString()}),"foreign destination refused");Check(System.IO.File.ReadAllText(collision)=="foreign destination"&&Json(calls.Snapshot.Invoke(view))["ownedTotal"]!.ToString()==before["ownedTotal"]!.ToString(),"foreign destination leaves drafts unchanged");System.IO.File.Delete(collision);
         string linked=System.IO.Path.Combine(root,"blueprints"),outside=System.IO.Path.Combine(root,"link-target");System.IO.Directory.CreateDirectory(outside);System.IO.Directory.CreateSymbolicLink(linked,outside);ready=Prepare();try{Refused(()=>Blueprint("createFeature",new{id=feature,basis=ready["basis"]!.ToString()}),"linked graph destination refused atomically");}finally{System.IO.Directory.Delete(linked);}
         ready=Prepare();var created=Blueprint("createFeature",new{id=feature,basis=ready["basis"]!.ToString()});string graphId=created["id"]!.ToString(),nodeId=created["node"]!.ToString();
         System.Text.Json.Nodes.JsonNode Read()=>Blueprint("read",new{id=graphId});var graph=Read();Check(graph["nodes"]!.AsArray().Count==1&&graph["signature"]!["args"]![0]!["name"]!.ToString()=="n"&&graph["diagnostics"]!["state"]!.ToString()=="needs-implementation"&&!created["compiled"]!.GetValue<bool>(),"exact external contract maps to an unimplemented independent node");
         string capability=calls.OpenNode.Invoke(project,"fixture","App","owner","create-feature",nodeId);try{var scope=Json(calls.ToolSnapshot.Invoke(capability));Check(scope["rights"]!.AsArray().Count==4&&scope["nodeScope"]!["observations"]!["App::ProjectManifest"] is not null&&scope["nodeScope"]!["observations"]![feature] is not null,"new node task keeps four rights and explicitly exposes related registration as human support");}finally{calls.CloseTool.Invoke(capability);}
         var group=Group(graph);Check(group.Length==5&&Array.IndexOf(group,feature)>=0&&Array.IndexOf(group,"App::ProjectManifest")>=0&&graph["sources"]!.AsArray().Count==5,"all five owned sources and registration are explicit");
         var pathList=new System.Collections.Generic.List<string>();foreach(var row in graph["sources"]!.AsArray())if(row!["id"]!.ToString()!="App::ProjectManifest")pathList.Add(System.IO.Path.Combine(root,row["path"]!.ToString()));var paths=pathList.ToArray();Check(Missing(paths),"creation writes no final sources");
         foreach(string omitted in group){var subset=Array.FindAll(group,id=>id!=omitted);Refused(()=>Cmd("review",new{target="portable",ids=subset}),"partial registration group refused: "+omitted);string draft=calls.BorrowDraft.Invoke(view);Check(calls.ConfirmDirect.Invoke(draft,subset,"portable",calls.Changes.Invoke(draft,subset))[0]=="invalid","direct Confirm cannot bypass group: "+omitted);}
         Cmd("save",new{});calls.Close.Invoke(peer);peer="";calls.Close.Invoke(view);view=calls.Open.Invoke(project,"owner","create-feature");graph=Read();Check(graph["reviewIds"]!.AsArray().Count==5&&Missing(paths),"genuine cold restore preserves missing source group without final writes");
         var review=Cmd("review",new{target="portable",ids=group})["review"]!;var confirmed=Cmd("confirm",new{token=review["token"]!.ToString(),ids=group});Check(confirmed["confirmation"]![0]!.ToString()=="invalid"&&Missing(paths),"unimplemented reachable body cannot pass actual compiler Confirm");
         graph=Read();string basis=graph["basis"]!.ToString();Cmd("create",new{kind="function",id="App::AnotherPending"});Refused(()=>Blueprint("source",new{id=graphId,basis,node="body",text="return n + 9;"}),"registration peer change fences node source edit");
         graph=Read();Blueprint("source",new{id=graphId,basis=graph["basis"]!.ToString(),node="body",text="return n + 9;"});graph=Read();group=Group(graph);Check(Array.IndexOf(group,"App::AnotherPending")>=0,"all new declarations in shared registration are reviewed explicitly");
         string draftHandle=calls.BorrowDraft.Invoke(view);var manifestUnit=Cmd("select",new{id="App::ProjectManifest"})["unit"]!;string manifestText=manifestUnit["text"]!.ToString();long manifestRevision=manifestUnit["revision"]!.GetValue<long>();Check(calls.EditBatch.Invoke(draftHandle,new[]{"App::ProjectManifest"},new[]{manifestText},new[]{manifestRevision},new[]{Hash(manifestText)}),"batch can observe unchanged registration");Refused(()=>calls.EditBatch.Invoke(draftHandle,new[]{"App::ProjectManifest"},new[]{manifestText+" "},new[]{manifestRevision},new[]{Hash(manifestText)}),"batch cannot edit registration");
         string foreign=paths[0];System.IO.Directory.CreateDirectory(System.IO.Path.GetDirectoryName(foreign)!);System.IO.File.WriteAllText(foreign,"preserve appeared file");review=Cmd("review",new{target="portable",ids=group})["review"]!;Check(review["status"]!.ToString()!="ready"&&System.IO.File.ReadAllText(foreign)=="preserve appeared file","appearance prevents ready publication without overwriting");System.IO.File.Delete(foreign);
         review=Cmd("review",new{target="portable",ids=group})["review"]!;confirmed=Cmd("confirm",new{token=review["token"]!.ToString(),ids=group});Check(confirmed["confirmation"]![0]!.ToString()=="confirmed",confirmed.ToJsonString());foreach(string path in paths)Check(System.IO.File.Exists(path),"verified registration publishes all owned files");
         foreach(var pair in originals)if(pair.Key!=project)Check(System.Linq.Enumerable.SequenceEqual(pair.Value,System.IO.File.ReadAllBytes(pair.Key)),"existing sources stay byte-identical");
         string packRoot=System.IO.Path.Combine(root,"plain-pack");System.IO.Directory.CreateDirectory(packRoot);string packProject=System.IO.Path.Combine(packRoot,"pack.cpack");System.IO.File.WriteAllText(packProject,"pack Plain version \"1\" {}");string packView=calls.Open.Invoke(packProject,"owner","pack-creation");try{var createdContract=Json(calls.Command.Invoke(packView,"create",Serialize(new{kind="function",id="Plain::Pending"})))["unit"]!;Refused(()=>calls.Blueprint.Invoke(packView,"readFeature",Serialize(new{id="Plain::Pending",revision=createdContract["revision"]!.GetValue<long>(),hash=Hash(createdContract["text"]!.ToString())})),"standalone pack without ProjectPack compiler context cannot create an unreadable graph");Check(Json(calls.Snapshot.Invoke(packView))["ownedTotal"]!.GetValue<int>()==2,"unsupported context keeps its function and manifest drafts without partial graph");}finally{calls.Close.Invoke(packView);}
         // Owned fixture integration: exercise the new function's own default provider without root binding copies.
         System.IO.File.WriteAllText(System.IO.Path.Combine(root,"MainBody.celem"),"implementation App::MainBody for App::Main () -> int {import App::Fresh as Fresh (int) -> int;body common \"fresh-run.csbody\";}");System.IO.File.WriteAllText(System.IO.Path.Combine(root,"fresh-run.csbody"),"Console.WriteLine(calls.Fresh.Invoke(2));return 0;");
         var run=Json(calls.Metadata.Invoke("run",Serialize(new{project,target="portable"})));Check(run["exit"]!.GetValue<int>()==0&&run["stdout"]!.ToString().Trim()=="11","new default-provided graph actually executes through existing CELEM contract");
        }finally{if(peer.Length>0)calls.Close.Invoke(peer);calls.Close.Invoke(view);}
        Console.WriteLine("Blueprint feature registration/contract/group/cold/compiler/Run11 PASS");return 0;
        """);
        string? host=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST"),selected=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT");
        try{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll"));Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",f.Project);var built=new Builder(project,"portable").Build();var run=Processes.Run(Strings(built,"run"),timeoutSeconds:240);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Blueprint feature registration/contract/group/cold/compiler/Run11 PASS"));}
        finally{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",selected);}
    }

    public void test_blueprint_owned_function_reference_call_import_cas_history_and_execution()
    {
        string feature="function App::Value (int n) -> int {}";var graph=Graph();graph["feature"]="App::Value";graph["contractHash"]=FeatureBlueprint.ContractHash(new Parser(feature,"<call wrapper fixture>").ParseElement());
        var described=FeatureBlueprint.Execute(new JsonObject{["operation"]="featureBlueprintNodes",["featureSource"]=feature,["graph"]=graph.DeepClone()});
        f.Add("App","function","Value",feature);f.Add("App","implementation","ValueBody","implementation App::ValueBody for App::Value (int n) -> int {blueprint common \"value.graph.json\";}");f.Main("provide App::Value with App::ValueBody;");
        f.Add("App","function","Double","function App::Double (int value) -> int {description \"Existing typed double feature\";provide App::Double with App::DoubleBody;}");f.Add("App","implementation","DoubleBody","implementation App::DoubleBody for App::Double (int value) -> int {body common \"double.csbody\";}");f.Body("App","double.csbody","return value * 2;");
        f.Add("App","function","Triple","function App::Triple (int value) -> int {}");f.Add("App","object","AlternateRoot","object App::AlternateRoot {provide App::Double with App::TimesTenBody;}");f.Add("App","implementation","TimesTenBody","implementation App::TimesTenBody for App::Double (int value) -> int {body common \"times-ten.csbody\";}");f.Body("App","times-ten.csbody","return value * 10;");
        f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import App::Value as Value (int) -> int;body common \"main.csbody\";}");f.Body("App","main.csbody","Console.WriteLine(calls.Value.Invoke(2));return 0;");f.Body("App","value.graph.json",graph.ToJsonString());
        foreach(var row in described["nodes"]!.AsArray()){string id=row!["id"]!.ToString();f.Body("App",id+".node.json",new JsonObject{["schema"]=1,["node"]=id,["definitionHash"]=row["definitionHash"]!.DeepClone(),["source"]=id=="add"?"return value + 3;":"return value > 0;"}.ToJsonString());}f.Sync();
        string sample=Path.Combine(f.Root,"call-wrapper-consumer");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples/edit-workspace"),sample);
        foreach(string name in new[]{"file-stream","schema-editing","edit-workspace","save","change-set","pack-workspace"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",name),Path.Combine(f.Root,"packs",name));
        string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/").Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack").Replace("element Main function","registry Confectory.PackWorkspace \"../packs/pack-workspace/pack.cpack\";dependency Confectory.PackWorkspace version \"0.1.0\";\nelement Main function"));
        File.WriteAllText(Path.Combine(sample,"main_body.celem"),"""
        implementation Example.EditWorkspace::MainBody for Example.EditWorkspace::Main () -> int {
        import Confectory.PackWorkspace::Open as Open (string,string,string) -> string;
        import Confectory.PackWorkspace::Command as Command (string,string,string) -> string;
        import Confectory.PackWorkspace::Blueprint as Blueprint (string,string,string) -> string;
        import Confectory.PackWorkspace::History as History (string,string,string) -> string;
        import Confectory.PackWorkspace::BorrowDraft as BorrowDraft (string) -> string;
        import Confectory.EditWorkspace::BlueprintCall as CreateCallDirect (string,string,string,string,string[],long[],string[]) -> string;
        import Confectory.EditWorkspace::Export as Export (string) -> string;
        import Confectory.EditWorkspace::Restore as Restore (string,string) -> void;
        import Confectory.PackWorkspace::Close as Close (string) -> void;
        import Confectory.SchemaEditing::Call as Metadata (string,string) -> string;
        body common "main.csbody";}
        """);
        File.WriteAllText(Path.Combine(sample,"main.csbody"),"""
        void Check(bool value,string why){if(!value)throw new Exception(why);}
        System.Text.Json.Nodes.JsonNode Json(string text)=>System.Text.Json.Nodes.JsonNode.Parse(text)!;
        string Serialize(object value)=>System.Text.Json.JsonSerializer.Serialize(value);
        string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT")!,root=System.IO.Path.GetDirectoryName(project)!,graphId="App::ValueBody/body:common",implementationId="App::ValueBody",node="double_wrapper";
        string view=calls.Open.Invoke(project,"owner","call-wrapper"),peer=calls.Open.Invoke(project,"owner","call-wrapper");
        System.Text.Json.Nodes.JsonNode Cmd(string op,object value)=>Json(calls.Command.Invoke(view,op,Serialize(value)));
        System.Text.Json.Nodes.JsonNode BP(string op,object value)=>Json(calls.Blueprint.Invoke(view,op,Serialize(value)));
        System.Text.Json.Nodes.JsonNode Read()=>BP("read",new{id=graphId});
        object definition=new{id=node,feature="App::Double",intent="Call the existing Double function without copying its implementation",control="next"};
        System.Text.Json.Nodes.JsonNode Preview()=>BP("readCall",new{id=graphId,definition});
        void Refused(Action action,string why){bool refused=false;try{action();}catch(InvalidOperationException){refused=true;}catch(ArgumentException){refused=true;}Check(refused,why);}
        void Confirm(string[] ids){var review=Cmd("review",new{ids,target="portable"})["review"]!;var result=Cmd("confirm",new{ids,token=review["token"]!.ToString()});Check(result["confirmation"]![0]!.ToString()=="confirmed",result.ToJsonString());}
        void Edit(string action,object value){var basis=Read();var data=System.Text.Json.JsonSerializer.SerializeToNode(value)!.AsObject();data["id"]=graphId;data["basis"]=basis["basis"]!.DeepClone();calls.Blueprint.Invoke(view,action,data.ToJsonString());}
        void Run(string expected){var result=Json(calls.Metadata.Invoke("run",Serialize(new{project,target="portable"})));Check(result["exit"]!.GetValue<int>()==0&&result["stdout"]!.ToString().Trim()==expected,"actual owned fixture result "+expected+": "+result.ToJsonString());}
        string originalGraph=System.IO.File.ReadAllText(System.IO.Path.Combine(root,"value.graph.json")),originalImplementation=System.IO.File.ReadAllText(System.IO.Path.Combine(root,"ValueBody.celem")),originalFunction=System.IO.File.ReadAllText(System.IO.Path.Combine(root,"Double.celem")),originalBody=System.IO.File.ReadAllText(System.IO.Path.Combine(root,"double.csbody"));
        try{
         Refused(()=>BP("readCall",new{id=graphId,definition=new{id="self",feature="App::Value",intent="Accidental self reference",control="next"}}),"self function reference is not silently introduced");Refused(()=>BP("readCall",new{id=graphId,definition=new{id="bad_branch",feature="App::Double",intent="Wrong branch type",control="branch"}}),"non-bool function cannot become a branch");Refused(()=>BP("readCall",new{id=graphId,definition=new{id="condition",feature="App::Double",intent="Duplicate identity",control="next"}}),"existing node identity cannot be replaced by a wrapper");
         var damagedUnit=Cmd("select",new{id="App::Double"})["unit"]!;Cmd("edit",new{text=originalFunction+" ",expectedRevision=damagedUnit["revision"]!.GetValue<long>()});string draftHandle=calls.BorrowDraft.Invoke(view),goodSaved=calls.Export.Invoke(draftHandle);var damaged=Json(goodSaved);foreach(var row in damaged["changes"]!.AsArray())if(row!["id"]!.ToString()=="App::Double")row["draft"]="function App::WrongIdentity (int value) -> int {}";calls.Restore.Invoke(draftHandle,damaged.ToJsonString());Refused(()=>Preview(),"restored target declaration identity cannot be borrowed by its former ID");calls.Restore.Invoke(draftHandle,goodSaved);damagedUnit=Cmd("select",new{id="App::Double"})["unit"]!;Cmd("edit",new{text=originalFunction,expectedRevision=damagedUnit["revision"]!.GetValue<long>()});
         var staleCaller=Preview();var callerUnit=Cmd("select",new{id=implementationId})["unit"]!;Cmd("edit",new{text=originalImplementation+" ",expectedRevision=callerUnit["revision"]!.GetValue<long>()});Refused(()=>BP("createCall",new{id=graphId,basis=staleCaller["basis"]!.ToString()}),"same-semantics caller revision change fences creation");callerUnit=Cmd("select",new{id=implementationId})["unit"]!;Cmd("edit",new{text=originalImplementation,expectedRevision=callerUnit["revision"]!.GetValue<long>()});
         var choices=BP("callables",new{id=graphId,query="Double",page=0});Check(choices["rows"]!.AsArray().Count==1&&choices["rows"]![0]!["id"]!.ToString()=="App::Double","bounded owned existing contract catalog");
         var stale=Preview();Check(stale["signature"]!["args"]![0]!["name"]!.ToString()=="value"&&!stale["compiled"]!.GetValue<bool>(),"explicit exact current target contract, no compiler success on read");
         var target=Cmd("select",new{id="App::Double"})["unit"]!;Cmd("edit",new{text=originalFunction+" ",expectedRevision=target["revision"]!.GetValue<long>()});Refused(()=>BP("createCall",new{id=graphId,basis=stale["basis"]!.ToString()}),"same-signature peer source changes fence the reference call");Check(Read()["nodes"]!.AsArray().Count==2&&Cmd("select",new{id=implementationId})["unit"]!["text"]!.ToString()==originalImplementation,"stale call leaves graph and implementation unchanged");target=Cmd("select",new{id="App::Double"})["unit"]!;Cmd("edit",new{text=originalFunction,expectedRevision=target["revision"]!.GetValue<long>()});
         var impl=Cmd("select",new{id=implementationId})["unit"]!;string collision=originalImplementation.Insert(originalImplementation.LastIndexOf('}'),"import App::Double as keep_existing (int) -> int;");Cmd("edit",new{text=collision,expectedRevision=impl["revision"]!.GetValue<long>()});Refused(()=>Preview(),"existing import alias is preserved rather than silently renamed");impl=Cmd("select",new{id=implementationId})["unit"]!;Cmd("edit",new{text=originalImplementation,expectedRevision=impl["revision"]!.GetValue<long>()});
         var preview=Preview();BP("createCall",new{id=graphId,basis=preview["basis"]!.ToString()});var created=Read();Check(created["nodes"]!.AsArray().Count==3,"reference call staged");foreach(var row in created["nodes"]!.AsArray())if(row!["id"]!.ToString()==node)Check(row["kind"]!.ToString()=="call"&&row["sourceId"] is null&&row["calledFeature"]!.ToString()=="App::Double","reference wrapper has no copied owned C# source");
         var history=Json(calls.History.Invoke(view,"inspect","{}"));Check(history["undo"]!["units"]!.AsArray().Count==2,"graph and typed import are one reversible source batch");calls.History.Invoke(view,"undo",Serialize(new{token=history["undo"]!["token"]!.ToString()}));Check(Read()["nodes"]!.AsArray().Count==2&&Cmd("select",new{id=implementationId})["unit"]!["text"]!.ToString()==originalImplementation,"atomic undo restores both sources");history=Json(calls.History.Invoke(view,"inspect","{}"));calls.History.Invoke(view,"redo",Serialize(new{token=history["redo"]!["token"]!.ToString()}));Check(Read()["nodes"]!.AsArray().Count==3,"atomic redo retains typed call");
         Cmd("save",new{});calls.Close.Invoke(peer);peer="";calls.Close.Invoke(view);view=calls.Open.Invoke(project,"owner","call-wrapper");Check(Read()["nodes"]!.AsArray().Count==3&&System.IO.File.ReadAllText(System.IO.Path.Combine(root,"value.graph.json"))==originalGraph&&System.IO.File.ReadAllText(System.IO.Path.Combine(root,"ValueBody.celem"))==originalImplementation,"true cold restore stages the graph and import without source writes");
         var review=Cmd("review",new{ids=new[]{graphId},target="portable"})["review"]!;var refused=Cmd("confirm",new{token=review["token"]!.ToString()});Check(refused["confirmation"]![0]!.ToString()=="invalid"&&System.IO.File.ReadAllText(System.IO.Path.Combine(root,"value.graph.json"))==originalGraph,"graph-only compiler Confirm cannot omit the required typed import");Confirm(new[]{graphId,implementationId});Run("5");
         Edit("argument",new{node,name="value",valueJson="{\"input\":\"n\"}"});Edit("route",new{node="condition",port="true",to=node});Edit("route",new{node,port="next",to="add"});Edit("argument",new{node="add",name="value",valueJson="{\"node\":\"double_wrapper\"}"});Confirm(new[]{graphId});Run("7");
         Refused(()=>BP("removeNode",new{id=graphId,basis=Read()["basis"]!.ToString(),node}),"connected referenced feature cannot be removed");Edit("route",new{node="condition",port="true",to="add"});Edit("route",new{node,port="next",to=""});Edit("argument",new{node="add",name="value",valueJson="{\"input\":\"n\"}"});BP("removeNode",new{id=graphId,basis=Read()["basis"]!.ToString(),node});Confirm(new[]{graphId});Run("5");Check(System.IO.File.ReadAllText(System.IO.Path.Combine(root,"Double.celem"))==originalFunction&&System.IO.File.ReadAllText(System.IO.Path.Combine(root,"double.csbody"))==originalBody,"callee source and implementation remain byte-identical through create/wire/remove");
         string importText="import App::Double as "+preview["alias"]!.ToString()+" (int) -> int;";var scopedUnit=Cmd("select",new{id=implementationId})["unit"]!;string unscopedText=scopedUnit["text"]!.ToString(),scopedText=unscopedText.Replace(importText,importText[..^1]+" in App::AlternateRoot;");Check(scopedText!=unscopedText,"scoped caller fixture uses its existing deterministic import");scopedText=scopedText.Insert(scopedText.LastIndexOf('}'),"import App::Double as keep_second (int) -> int;");Cmd("edit",new{text=scopedText,expectedRevision=scopedUnit["revision"]!.GetValue<long>()});definition=new{id="scope_wrapper",feature="App::Double",intent="Use the current explicit import scope",control="next"};var scoped=Preview();Check(scoped["scope"]!.ToString()=="App::AlternateRoot","preview exposes the preserved explicit import scope");BP("createCall",new{id=graphId,basis=scoped["basis"]!.ToString()});Check(Cmd("select",new{id=implementationId})["unit"]!["text"]!.ToString().Contains("as keep_second (int) -> int;",StringComparison.Ordinal),"an additional legacy import alias remains intact beside the canonical graph import");Edit("argument",new{node="scope_wrapper",name="value",valueJson="{\"input\":\"n\"}"});Edit("route",new{node="condition",port="true",to="scope_wrapper"});Edit("route",new{node="scope_wrapper",port="next",to="add"});Edit("argument",new{node="add",name="value",valueJson="{\"node\":\"scope_wrapper\"}"});Confirm(new[]{graphId,implementationId});Run("23");
         Edit("route",new{node="condition",port="true",to="add"});Edit("route",new{node="scope_wrapper",port="next",to=""});Edit("argument",new{node="add",name="value",valueJson="{\"input\":\"n\"}"});BP("removeNode",new{id=graphId,basis=Read()["basis"]!.ToString(),node="scope_wrapper"});scopedUnit=Cmd("select",new{id=implementationId})["unit"]!;Cmd("edit",new{text=unscopedText,expectedRevision=scopedUnit["revision"]!.GetValue<long>()});Confirm(new[]{graphId,implementationId});Run("5");Check(System.IO.File.ReadAllText(System.IO.Path.Combine(root,"Double.celem"))==originalFunction&&System.IO.File.ReadAllText(System.IO.Path.Combine(root,"double.csbody"))==originalBody&&System.IO.File.ReadAllText(System.IO.Path.Combine(root,"times-ten.csbody")).Trim()=="return value * 10;","scope selection reuses both existing implementations without copying or rewriting them");
         Cmd("create",new{kind="function",id="App::PendingCall"});Refused(()=>BP("readCall",new{id=graphId,definition=new{id="unpublished",feature="App::PendingCall",intent="Unpublished target",control="next"}}),"this reference workflow does not silently register an unpublished target");Check(BP("callables",new{id=graphId,query="PendingCall",page=0})["rows"]!.AsArray().Count==0,"unpublished functions stay outside the existing-function catalog");
         var smallGraph=Cmd("select",new{id=graphId})["unit"]!;var crowded=Json(smallGraph["text"]!.ToString());for(int index=0;index<58;index++){string budgetId="call_budget_"+index,filename=budgetId+".node.json";crowded["nodes"]!.AsArray().Add(new System.Text.Json.Nodes.JsonObject{["id"]=budgetId,["kind"]="code",["control"]="next",["intent"]="Owned source budget fixture",["signature"]=new System.Text.Json.Nodes.JsonObject{["args"]=new System.Text.Json.Nodes.JsonArray(),["return"]="void"},["implementation"]=filename});System.IO.File.WriteAllText(System.IO.Path.Combine(root,filename),new System.Text.Json.Nodes.JsonObject{["schema"]=1,["node"]=budgetId,["definitionHash"]=new string('0',64),["source"]=""}.ToJsonString());}Cmd("edit",new{text=crowded.ToJsonString(),expectedRevision=smallGraph["revision"]!.GetValue<long>()});Cmd("select",new{id=implementationId});Cmd("bodies",new{});var atLimit=Read();Check(atLimit["sources"]!.AsArray().Count==64,"existing caller source boundary is exactly64");
         string Reason(Action action){try{action();return "accepted";}catch(InvalidOperationException error){return error.Message;}catch(ArgumentException error){return error.Message;}}
         string countReason=Reason(()=>BP("readCall",new{id=graphId,definition=new{id="extra_contract",feature="App::Triple",intent="New contract exceeds the current read scope",control="next"}}));Check(countReason.Contains("budget",StringComparison.OrdinalIgnoreCase)&&Read()["sources"]!.AsArray().Count==64,"selected contract65 refused without changing the caller: "+countReason);BP("readCall",new{id=graphId,definition=new{id="already_observed",feature="App::Double",intent="Already observed contract needs no new source slot",control="next"}});
         int Bytes(string text)=>System.Text.Encoding.UTF8.GetByteCount(text);var matrix=new System.Collections.Generic.Dictionary<string,string>(StringComparer.Ordinal);int totalBytes=0;foreach(var row in atLimit["sources"]!.AsArray()){string sourceId=row!["id"]!.ToString();var source=Cmd("select",new{id=sourceId})["unit"]!;matrix[sourceId]=source["text"]!.ToString();totalBytes=checked(totalBytes+Bytes(matrix[sourceId]));}
         string conditionId=graphId+"/node:condition",addId=graphId+"/node:add";var emptyCondition=Json(matrix[conditionId]);var emptyAdd=Json(matrix[addId]);emptyCondition["source"]="";emptyAdd["source"]="";int overhead=totalBytes-Bytes(matrix[conditionId])-Bytes(matrix[addId])+Bytes(emptyCondition.ToJsonString())+Bytes(emptyAdd.ToJsonString()),available=2097152-500-overhead,firstSize=available/2,secondSize=available-firstSize;string conditionPrefix="return true; //",addPrefix="return 3; //";emptyCondition["source"]=conditionPrefix+new string('x',firstSize-conditionPrefix.Length);emptyAdd["source"]=addPrefix+new string('y',secondSize-addPrefix.Length);foreach(var pair in new[]{new System.Collections.Generic.KeyValuePair<string,string>(conditionId,emptyCondition.ToJsonString()),new System.Collections.Generic.KeyValuePair<string,string>(addId,emptyAdd.ToJsonString())}){Check(pair.Value.Length<1048576,"individual source remains within its own edit budget");var source=Cmd("select",new{id=pair.Key})["unit"]!;Cmd("edit",new{text=pair.Value,expectedRevision=source["revision"]!.GetValue<long>()});}
         var near=Read();var longDefinition=new{id="byte_budget",feature="App::Double",intent=new string('x',2000),control="next"};string graphBefore=Cmd("select",new{id=graphId})["unit"]!["text"]!.ToString(),implementationBefore=Cmd("select",new{id=implementationId})["unit"]!["text"]!.ToString();string byteReason=Reason(()=>BP("readCall",new{id=graphId,definition=longDefinition}));Check(byteReason.Contains("budget",StringComparison.OrdinalIgnoreCase),"combined UTF8 budget refused at contract preview: "+byteReason);
         var observedIds=new System.Collections.Generic.List<string>();var observedRevisions=new System.Collections.Generic.List<long>();var observedHashes=new System.Collections.Generic.List<string>();var contracts=new System.Text.Json.Nodes.JsonObject();foreach(var row in near["sources"]!.AsArray()){string sourceId=row!["id"]!.ToString();var source=Cmd("select",new{id=sourceId})["unit"]!;observedIds.Add(sourceId);observedRevisions.Add(source["revision"]!.GetValue<long>());observedHashes.Add(row["hash"]!.ToString());matrix[sourceId]=source["text"]!.ToString();if(source["kind"]!.ToString()=="function")contracts[sourceId]=matrix[sourceId];}
         var prepared=Json(calls.Metadata.Invoke("blueprintPrepareCall",new System.Text.Json.Nodes.JsonObject{["id"]=implementationId,["text"]=matrix[implementationId],["targetText"]=matrix["App::Double"],["graph"]=Json(matrix[graphId]),["definition"]=System.Text.Json.JsonSerializer.SerializeToNode(longDefinition)}.ToJsonString()));var definitions=Json(calls.Metadata.Invoke("blueprintDescribeOwned",new System.Text.Json.Nodes.JsonObject{["project"]=project,["id"]=implementationId,["text"]=prepared["implementation"]!.DeepClone(),["graph"]=prepared["graph"]!.DeepClone(),["draftContracts"]=contracts,["definitionsOnly"]=true}.ToJsonString()));string directReason=Reason(()=>calls.CreateCallDirect.Invoke(calls.BorrowDraft.Invoke(view),graphId,Serialize(longDefinition),definitions["contractVersions"]!.ToJsonString(),observedIds.ToArray(),observedRevisions.ToArray(),observedHashes.ToArray()));Check(directReason.Contains("budget",StringComparison.OrdinalIgnoreCase)&&Cmd("select",new{id=graphId})["unit"]!["text"]!.ToString()==graphBefore&&Cmd("select",new{id=implementationId})["unit"]!["text"]!.ToString()==implementationBefore,"direct owned API cannot bypass the prospective byte budget or partially add its typed import: "+directReason);
        }finally{if(peer.Length>0)calls.Close.Invoke(peer);calls.Close.Invoke(view);}
        Console.WriteLine("Blueprint owned feature reference/import/CAS/history/cold/compiler/Run5-7-5 PASS");return 0;
        """);
        Env4Diagnostics.Graph(Path.Combine(sample,"main.csbody"));
        string? host=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST"),selected=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT");
        try{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll"));Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",f.Project);var built=Env4Diagnostics.Measure("graph-call-build",()=>new Builder(project,"portable").Build());var run=Env4Diagnostics.Run(Strings(built,"run"),240,"graph-call-driver");True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Blueprint owned feature reference/import/CAS/history/cold/compiler/Run5-7-5 PASS"));}
        finally{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",selected);}
    }

    public void test_blueprint_owned_node_creation_removal_review_group_and_cold_restore()
    {
        string feature="function App::Value (int n) -> int {}";var graph=Graph();graph["feature"]="App::Value";graph["contractHash"]=FeatureBlueprint.ContractHash(new Parser(feature,"<node creation fixture>").ParseElement());
        var described=FeatureBlueprint.Execute(new JsonObject{["operation"]="featureBlueprintNodes",["featureSource"]=feature,["graph"]=graph.DeepClone()});
        f.Add("App","function","Value",feature);f.Add("App","implementation","ValueBody","implementation App::ValueBody for App::Value (int n) -> int {blueprint common \"value.graph.json\";}");f.Main("provide App::Value with App::ValueBody;");
        f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import App::Value as Value (int) -> int;body common \"main.csbody\";}");f.Body("App","main.csbody","Console.WriteLine(calls.Value.Invoke(2));return 0;");f.Body("App","value.graph.json",graph.ToJsonString());
        foreach(var row in described["nodes"]!.AsArray()){string id=row!["id"]!.ToString();f.Body("App",id+".node.json",new JsonObject{["schema"]=1,["node"]=id,["definitionHash"]=row["definitionHash"]!.DeepClone(),["source"]=id=="add"?"return value + 3;":"return value > 0;"}.ToJsonString());}f.Sync();
        string sample=Path.Combine(f.Root,"node-creation-consumer");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples/edit-workspace"),sample);
        foreach(string name in new[]{"file-stream","schema-editing","edit-workspace","save","change-set","pack-workspace","element-view"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",name),Path.Combine(f.Root,"packs",name));
        string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/").Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack").Replace("element Main function","registry Confectory.PackWorkspace \"../packs/pack-workspace/pack.cpack\";dependency Confectory.PackWorkspace version \"0.1.0\";\nelement Main function"));
        string consumerManifest=File.ReadAllText(project);File.WriteAllText(project,consumerManifest.Insert(consumerManifest.LastIndexOf('}'),"registry Confectory.ElementView \"../packs/element-view/pack.cpack\";dependency Confectory.ElementView version \"0.1.0\";"));
        string composition=Path.Combine(sample,"main.celem"),compositionText=File.ReadAllText(composition);File.WriteAllText(composition,compositionText.Insert(compositionText.LastIndexOf('}'),"provide Confectory.ElementView::Create with Confectory.ElementView::CreateBody;provide Confectory.ElementView::Poll with Confectory.ElementView::PollBody;provide Confectory.ElementView::Labels with Confectory.ElementView::LabelsBody;provide Confectory.ElementView::Close with Confectory.ElementView::CloseBody;"));
        File.WriteAllText(Path.Combine(sample,"main_body.celem"),"""
        implementation Example.EditWorkspace::MainBody for Example.EditWorkspace::Main () -> int {
        import Confectory.PackWorkspace::Open as Open (string,string,string) -> string;
        import Confectory.PackWorkspace::Command as Command (string,string,string) -> string;
        import Confectory.PackWorkspace::Snapshot as Snapshot (string) -> string;
        import Confectory.PackWorkspace::Blueprint as Blueprint (string,string,string) -> string;
        import Confectory.PackWorkspace::Close as Close (string) -> void;
        import Confectory.PackWorkspace::BorrowDraft as BorrowDraft (string) -> string;
        import Confectory.EditWorkspace::Changes as Changes (string,string[]) -> string[];
        import Confectory.ChangeSet::ConfirmReviewed as ConfirmDirect (string,string[],string,string[]) -> string[];
        import Confectory.SchemaEditing::Call as Metadata (string,string) -> string;
        import Confectory.EditWorkspace::Subscribe as Subscribe (string,string) -> string[];
        import Confectory.EditWorkspace::Poll as PollSource (string[]) -> string[];
        import Confectory.EditWorkspace::Export as Export (string) -> string;
        import Confectory.EditWorkspace::Restore as Restore (string,string) -> void;
        import Confectory.ElementView::Create as Card (string,string,string,int,int) -> string;
        import Confectory.ElementView::Poll as PollCard (string) -> bool;
        import Confectory.ElementView::Labels as CardLabels (string,string) -> string[];
        import Confectory.ElementView::Close as CloseCard (string) -> void;
        body common "main.csbody";}
        """);
        File.WriteAllText(Path.Combine(sample,"main.csbody"),"""
        void Check(bool value,string why){if(!value)throw new Exception(why);}
        System.Text.Json.Nodes.JsonNode Json(string text)=>System.Text.Json.Nodes.JsonNode.Parse(text)!;
        string Serialize(object value)=>System.Text.Json.JsonSerializer.Serialize(value);
        string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT")!,root=System.IO.Path.GetDirectoryName(project)!,graphId="App::ValueBody/body:common",id=graphId+"/node:independent";
        string view=calls.Open.Invoke(project,"owner","create-nodes"),peer=calls.Open.Invoke(project,"owner","create-nodes"),card="";
        System.Text.Json.Nodes.JsonNode Read()=>Json(calls.Blueprint.Invoke(view,"read",Serialize(new{id=graphId})));
        System.Text.Json.Nodes.JsonNode Cmd(string op,object value)=>Json(calls.Command.Invoke(view,op,Serialize(value)));
        System.Text.Json.Nodes.JsonNode Edit(string node,string action,System.Text.Json.Nodes.JsonNode basis,object? definition=null)=>Json(calls.Blueprint.Invoke(view,action,Serialize(new{id=graphId,basis=basis["basis"]!.ToString(),node,definition})));
        void Refused(Action action,string why){bool refused=false;try{action();}catch(InvalidOperationException){refused=true;}catch(ArgumentException){refused=true;}Check(refused,why);}
        object definition=new{intent="Independent before wiring",control="next",signature=new{args=new[]{new{type="int",name="value"}},@return="int"}};
        try{
         var first=Read();string originalGraph=System.IO.File.ReadAllText(System.IO.Path.Combine(root,"value.graph.json"));
         Refused(()=>Edit("bad","createNode",first,new{intent="Bad branch",control="branch",signature=new{args=Array.Empty<object>(),@return="int"}}),"invalid new definition refused before ownership changes");Check(Read()["nodes"]!.AsArray().Count==2,"invalid creation leaves graph unchanged");
         string linked=System.IO.Path.Combine(root,"nodes"),elsewhere=System.IO.Path.Combine(root,"owned-link-fixture");System.IO.Directory.CreateDirectory(elsewhere);System.IO.Directory.CreateSymbolicLink(linked,elsewhere);
         try{Refused(()=>Edit("linked","createNode",Read(),definition),"linked destination refused atomically");}finally{System.IO.Directory.Delete(linked);}
         var stale=Read();var existing=Cmd("select",new{id=graphId+"/node:add"})["unit"]!;string unchanged=existing["text"]!.ToString();Cmd("edit",new{text=unchanged+" ",expectedRevision=existing["revision"]!.GetValue<long>()});
         Refused(()=>Edit("independent","createNode",stale,definition),"peer node changes fence creation even when graph is unchanged");Check(Read()["nodes"]!.AsArray().Count==2,"stale creation adds no partial node");existing=Cmd("select",new{id=graphId+"/node:add"})["unit"]!;Cmd("edit",new{text=unchanged,expectedRevision=existing["revision"]!.GetValue<long>()});
         Edit("independent","createNode",Read(),definition);var created=Read();Check(created["nodes"]!.AsArray().Count==3&&System.IO.File.ReadAllText(System.IO.Path.Combine(root,"value.graph.json"))==originalGraph,"creation stages source only");
         var unit=Cmd("select",new{id})["unit"]!;string path=System.IO.Path.Combine(root,unit["path"]!.ToString());Check(!System.IO.File.Exists(path)&&Json(unit["text"]!.ToString())["definitionHash"]!.ToString()==new string('0',64),"new owned body is missing and unstamped, never fake compiled");
         var group=Json(calls.Snapshot.Invoke(view))["creationReviewIds"]!.ToJsonString();Check(group.Contains(graphId)&&group.Contains(id)&&!group.Contains("Manifest"),"node creation review dependency is its graph");
         calls.Command.Invoke(peer,"select",Serialize(new{id}));
         string borrowed=calls.BorrowDraft.Invoke(view);var subscription=calls.Subscribe.Invoke(borrowed,id);card=calls.Card.Invoke(borrowed,id,"card",420,300);string retainedCardText=calls.CardLabels.Invoke(card,"")[2];string savedCreation=calls.Export.Invoke(borrowed);
         System.IO.Directory.CreateDirectory(System.IO.Path.GetDirectoryName(path)!);System.IO.File.WriteAllText(path,"foreign appearance");Refused(()=>Edit("independent","removeNode",Read()),"external appearance is preserved");Check(System.IO.File.ReadAllText(path)=="foreign appearance","foreign file untouched");System.IO.File.Delete(path);
         Edit("independent","removeNode",Read());Check(Read()["nodes"]!.AsArray().Count==2&&Json(calls.Snapshot.Invoke(peer))["unit"] is null,"pending removal clears owned draft and peer selection safely");
         Check(calls.PollSource.Invoke(subscription).Length==0&&subscription[3]=="retired","removed owned source retires its public subscription without throwing or replacing retained text");Check(calls.PollCard.Invoke(card)&&calls.CardLabels.Invoke(card,"")[0].Contains("retired")&&calls.CardLabels.Invoke(card,"")[2]==retainedCardText&&!calls.PollCard.Invoke(card),"borrowed Card reports retirement once and preserves the last source projection");calls.CloseCard.Invoke(card);card="";
         calls.Restore.Invoke(borrowed,savedCreation);var restoredUnit=Cmd("select",new{id})["unit"]!;Check(restoredUnit["revision"]!.GetValue<long>()>long.Parse(subscription[2])&&calls.PollSource.Invoke(subscription).Length==0&&subscription[3]=="retired","explicit live restore advances the retired source revision and does not reactivate its old subscription");Edit("independent","removeNode",Read());
         Edit("independent","createNode",Read(),definition);unit=Cmd("select",new{id})["unit"]!;Check(unit["revision"]!.GetValue<long>()>restoredUnit["revision"]!.GetValue<long>(),"same-ID recreation cannot reuse an old live source revision");path=System.IO.Path.Combine(root,unit["path"]!.ToString());Cmd("save",new{});calls.Close.Invoke(peer);peer="";calls.Close.Invoke(view);view=calls.Open.Invoke(project,"owner","create-nodes");
         Check(Read()["nodes"]!.AsArray().Count==3&&!System.IO.File.Exists(path),"cold restore retains graph and missing owned node without applying files");
         string draft=calls.BorrowDraft.Invoke(view);var direct=calls.ConfirmDirect.Invoke(draft,new[]{id},"portable",calls.Changes.Invoke(draft,new[]{id}));Check(direct[0]=="invalid"&&!System.IO.File.Exists(path),"direct source Confirm cannot bypass the owning graph creation group");
         Refused(()=>Cmd("review",new{target="portable",ids=new[]{id}}),"node-only review cannot orphan source");Refused(()=>Cmd("review",new{target="portable",ids=new[]{graphId}}),"graph-only review cannot publish half of creation");
         var review=Cmd("review",new{target="portable",ids=new[]{graphId,id}})["review"]!;Check(review["status"]!.ToString()=="ready","graph and node review without unrelated manifest");var confirmation=Cmd("confirm",new{token=review["token"]!.ToString(),ids=new[]{graphId,id}});Check(confirmation["confirmation"]![0]!.ToString()=="confirmed"&&System.IO.File.Exists(path),confirmation.ToJsonString());
         Refused(()=>Edit("condition","removeNode",Read()),"connected start node cannot be removed");
         var basis=Read();calls.Blueprint.Invoke(view,"source",Serialize(new{id=graphId,basis=basis["basis"]!.ToString(),node="independent",text="return missing;"}));Refused(()=>Edit("independent","removeNode",Read()),"dirty existing body is preserved before graph removal");
         review=Cmd("review",new{target="portable",ids=new[]{id}})["review"]!;confirmation=Cmd("confirm",new{token=review["token"]!.ToString()});Check(confirmation["confirmation"]![0]!.ToString()=="invalid"&&Json(System.IO.File.ReadAllText(path))["source"]!.ToString()=="","current independent invalid body fails compiler and leaves originals");
         basis=Read();calls.Blueprint.Invoke(view,"source",Serialize(new{id=graphId,basis=basis["basis"]!.ToString(),node="independent",text="throw new System.Exception(\"Independent node must not run\");"}));review=Cmd("review",new{target="portable",ids=new[]{id}})["review"]!;confirmation=Cmd("confirm",new{token=review["token"]!.ToString()});Check(confirmation["confirmation"]![0]!.ToString()=="confirmed",confirmation.ToJsonString());string retained=System.IO.File.ReadAllText(path);
         basis=Read();calls.Blueprint.Invoke(view,"source",Serialize(new{id=graphId,basis=basis["basis"]!.ToString(),node="independent",text="return value + 20;"}));review=Cmd("review",new{target="portable",ids=new[]{id}})["review"]!;confirmation=Cmd("confirm",new{token=review["token"]!.ToString()});Check(confirmation["confirmation"]![0]!.ToString()=="confirmed",confirmation.ToJsonString());retained=System.IO.File.ReadAllText(path);
         void Argument(string node,string valueJson){var current=Read();calls.Blueprint.Invoke(view,"argument",Serialize(new{id=graphId,basis=current["basis"]!.ToString(),node,name="value",valueJson}));}
         void Route(string node,string port,string to){var current=Read();calls.Blueprint.Invoke(view,"route",Serialize(new{id=graphId,basis=current["basis"]!.ToString(),node,port,to}));}
         Argument("independent","{\"constant\":\"wrong type\"}");Route("independent","next","add");Route("condition","true","independent");Check(Read()["diagnostics"]!["state"]!.ToString()=="invalid","invalid typed wiring remains an explicit unfinished draft diagnostic");string beforeInvalidGraph=System.IO.File.ReadAllText(System.IO.Path.Combine(root,"value.graph.json"));review=Cmd("review",new{target="portable",ids=new[]{graphId}})["review"]!;confirmation=Cmd("confirm",new{token=review["token"]!.ToString()});Check(confirmation["confirmation"]![0]!.ToString()=="invalid"&&System.IO.File.ReadAllText(System.IO.Path.Combine(root,"value.graph.json"))==beforeInvalidGraph,"actual compiler refuses invalid typed wiring without changing the final graph");
         Argument("independent","{\"input\":\"n\"}");Route("condition","true","independent");Argument("add","{\"node\":\"independent\"}");review=Cmd("review",new{target="portable",ids=new[]{graphId}})["review"]!;confirmation=Cmd("confirm",new{token=review["token"]!.ToString()});Check(confirmation["confirmation"]![0]!.ToString()=="confirmed",confirmation.ToJsonString());
         var executed=Json(calls.Metadata.Invoke("run",Serialize(new{project,target="portable"})));Check(executed["exit"]!.GetValue<int>()==0&&executed["stdout"]!.ToString().Trim()=="25","new node uses existing feature input and supplies a typed value to the existing node in an actual owned run");Refused(()=>Edit("independent","removeNode",Read()),"wired new node cannot be removed");
         Argument("add","{\"input\":\"n\"}");Route("condition","true","add");Route("independent","next","");
         var graphUnit=Cmd("select",new{id=graphId})["unit"]!;string beforeReference=graphUnit["text"]!.ToString();var referenced=Json(beforeReference);referenced["nodes"]![1]!["arguments"]!["value"]=new System.Text.Json.Nodes.JsonObject{["node"]="independent"};Cmd("edit",new{text=referenced.ToJsonString(),expectedRevision=graphUnit["revision"]!.GetValue<long>()});Refused(()=>Edit("independent","removeNode",Read()),"remaining node value references block removal");graphUnit=Cmd("select",new{id=graphId})["unit"]!;Cmd("edit",new{text=beforeReference,expectedRevision=graphUnit["revision"]!.GetValue<long>()});
         peer=calls.Open.Invoke(project,"owner","create-nodes");calls.Command.Invoke(peer,"select",Serialize(new{id}));var existingSubscription=calls.Subscribe.Invoke(calls.BorrowDraft.Invoke(view),id);Edit("independent","removeNode",Read());Check(Json(calls.Snapshot.Invoke(peer))["unit"] is null,"removed existing node also retires its editable source identity");Check(Read()["nodes"]!.AsArray().Count==2&&System.IO.File.ReadAllText(path)==retained,"existing independent body retained on graph removal");graphUnit=Cmd("select",new{id=graphId})["unit"]!;Cmd("edit",new{text=beforeReference,expectedRevision=graphUnit["revision"]!.GetValue<long>()});Cmd("select",new{id="App::ValueBody"});Cmd("bodies",new{});var rediscovered=Cmd("select",new{id})["unit"]!;Check(rediscovered["revision"]!.GetValue<long>()>long.Parse(existingSubscription[2])&&calls.PollSource.Invoke(existingSubscription).Length==7,"explicit body rediscovery cannot reuse a retired live source revision");Edit("independent","removeNode",Read());Check(calls.PollSource.Invoke(existingSubscription).Length==0&&existingSubscription[3]=="retired","rediscovered source can retire safely again");review=Cmd("review",new{target="portable",ids=new[]{graphId}})["review"]!;confirmation=Cmd("confirm",new{token=review["token"]!.ToString()});Check(confirmation["confirmation"]![0]!.ToString()=="confirmed",confirmation.ToJsonString());Cmd("save",new{});calls.Close.Invoke(peer);peer="";calls.Close.Invoke(view);view=calls.Open.Invoke(project,"owner","create-nodes");Check(Read()["nodes"]!.AsArray().Count==2&&System.IO.File.ReadAllText(path)==retained,"removed graph and preserved body survive cold restart");
         var smallGraph=Cmd("select",new{id=graphId})["unit"]!;string smallGraphText=smallGraph["text"]!.ToString();var crowded=Json(smallGraphText);
         for(int index=0;index<59;index++){string budgetId="budget_"+index,filename=budgetId+".node.json";crowded["nodes"]!.AsArray().Add(new System.Text.Json.Nodes.JsonObject{["id"]=budgetId,["kind"]="code",["control"]="next",["intent"]="Owned read budget fixture",["signature"]=new System.Text.Json.Nodes.JsonObject{["args"]=new System.Text.Json.Nodes.JsonArray(),["return"]="void"},["implementation"]=filename});System.IO.File.WriteAllText(System.IO.Path.Combine(root,filename),new System.Text.Json.Nodes.JsonObject{["schema"]=1,["node"]=budgetId,["definitionHash"]=new string('0',64),["source"]=""}.ToJsonString());}
         Cmd("edit",new{text=crowded.ToJsonString(),expectedRevision=smallGraph["revision"]!.GetValue<long>()});Cmd("select",new{id="App::ValueBody"});Cmd("bodies",new{});var atLimit=Read();Check(atLimit["sources"]!.AsArray().Count==64,"actual source-count boundary fixture");int ownedBefore=Json(calls.Snapshot.Invoke(view))["ownedTotal"]!.GetValue<int>();bool budgetRefused=false;
         try{Edit("too_many","createNode",atLimit,definition);}catch(ArgumentException){budgetRefused=true;}catch(InvalidOperationException){budgetRefused=true;}
         if(!budgetRefused){bool unreadable=false;try{Read();}catch(InvalidOperationException){unreadable=true;}Check(!unreadable,"Creation admitted a 65th source and the actual graph read became unavailable");}
         Check(budgetRefused&&Json(calls.Snapshot.Invoke(view))["ownedTotal"]!.GetValue<int>()==ownedBefore&&System.Text.Json.Nodes.JsonNode.DeepEquals(Read()["sources"],atLimit["sources"]),"creation must reserve its next source read before mutating ownership");
         smallGraph=Cmd("select",new{id=graphId})["unit"]!;Cmd("edit",new{text=smallGraphText,expectedRevision=smallGraph["revision"]!.GetValue<long>()});
         var originals=new System.Collections.Generic.Dictionary<string,string>(StringComparer.Ordinal);
         foreach(string name in new[]{"condition","add"}){string sourceId=graphId+"/node:"+name;var source=Cmd("select",new{id=sourceId})["unit"]!;originals[sourceId]=source["text"]!.ToString();var large=Json(originals[sourceId]);large["source"]="//"+new string('x',1043500)+"\nreturn value;";Cmd("edit",new{text=large.ToJsonString(),expectedRevision=source["revision"]!.GetValue<long>()});}
         var nearBytes=Read();Check(nearBytes["sources"]!.AsArray().Count==5,"actual combined UTF8 budget fixture");int beforeBytes=Json(calls.Snapshot.Invoke(view))["ownedTotal"]!.GetValue<int>();
         Refused(()=>Edit("too_large","createNode",nearBytes,new{intent=new string('i',12000),control="next",signature=new{args=new[]{new{type="int",name="value"}},@return="int"}}),"creation cannot exceed the next combined UTF8 read budget");
         Refused(()=>calls.Blueprint.Invoke(view,"intent",Serialize(new{id=graphId,basis=nearBytes["basis"]!.ToString(),node="condition",text=new string('i',12000)})),"an ordinary graph edit cannot exceed its next combined UTF8 read budget either");
         Check(Json(calls.Snapshot.Invoke(view))["ownedTotal"]!.GetValue<int>()==beforeBytes&&System.Text.Json.Nodes.JsonNode.DeepEquals(Read()["sources"],nearBytes["sources"]),"budget refusals preserve source registration, contents and all revisions");
         foreach(var pair in originals){var source=Cmd("select",new{id=pair.Key})["unit"]!;Cmd("edit",new{text=pair.Value,expectedRevision=source["revision"]!.GetValue<long>()});}

        }finally{if(card.Length>0)calls.CloseCard.Invoke(card);if(peer.Length>0)calls.Close.Invoke(peer);calls.Close.Invoke(view);}
        Console.WriteLine("Blueprint owned create/remove/group/CAS/cold/compiler PASS");return 0;
        """);
        Env4Diagnostics.Graph(Path.Combine(sample,"main.csbody"));
        string? host=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST"),selected=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT");
        try{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll"));Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",f.Project);var built=Env4Diagnostics.Measure("graph-create-build",()=>new Builder(project,"portable").Build());var run=Env4Diagnostics.Run(Strings(built,"run"),180,"graph-create-driver");True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Blueprint owned create/remove/group/CAS/cold/compiler PASS"));Output(Build(),"5");}
        finally{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",selected);}
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
        System.IO.File.WriteAllText(path,"// A generated C# implementation is not an authored node record.\nreturn value;\n");string invalidCapability="";bool invalidSource=false;
        try{invalidCapability=calls.OpenNode.Invoke(project,"fixture","App","owner","invalid-node-record",id);}catch(InvalidOperationException){invalidSource=true;}
        finally{if(invalidCapability.Length>0)calls.CloseTool.Invoke(invalidCapability);System.IO.File.WriteAllText(path,original);}
        Check(invalidSource,"raw or generated C# must not be exposed as an owned node record");
        var locatorUnit=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(view,"select",System.Text.Json.JsonSerializer.Serialize(new{id="App::ValueBody"})))!["unit"]!;string originalLocator=locatorUnit["text"]!.ToString();
        calls.Command.Invoke(view,"edit",System.Text.Json.JsonSerializer.Serialize(new{text=originalLocator.Replace("value.graph.json","elsewhere.graph.json",StringComparison.Ordinal),expectedRevision=locatorUnit["revision"]!.GetValue<long>()}));
        string movedCapability="";bool graphLocatorDenied=false;
        try{movedCapability=calls.OpenNode.Invoke(project,"fixture","App","owner","nodes",id);}catch(InvalidOperationException){graphLocatorDenied=true;}
        finally{if(movedCapability.Length>0)calls.CloseTool.Invoke(movedCapability);locatorUnit=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(view,"select",System.Text.Json.JsonSerializer.Serialize(new{id="App::ValueBody"})))!["unit"]!;calls.Command.Invoke(view,"edit",System.Text.Json.JsonSerializer.Serialize(new{text=originalLocator,expectedRevision=locatorUnit["revision"]!.GetValue<long>()}));}
        Check(graphLocatorDenied,"implementation must still own the displayed graph before lending a node capability");
        string capability=calls.OpenNode.Invoke(project,"fixture","App","owner","nodes",id);
        string Invoke(string op,string call,object args)=>calls.Tool.Invoke(capability,call,op,System.Text.Json.JsonSerializer.Serialize(args));
        string Hash(string text)=>Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(text))).ToLowerInvariant();
        var defs=System.Text.Json.Nodes.JsonNode.Parse(calls.Definitions.Invoke(capability))!.AsArray();Check(defs.Count==4&&!System.Linq.Enumerable.Any(defs,d=>d!["name"]!.ToString()=="workspace_create"),"node-only tool definitions");
        var assigned=System.Text.Json.Nodes.JsonNode.Parse(Invoke("workspace_read","assigned",new{projectId="fixture",id}))!;Check(assigned["assignment"]!["definition"]!["intent"]!.ToString()=="Add three"&&assigned["assignment"]!["definition"]!["signature"]!["return"]!.ToString()=="int","Worker receives only assigned node intent and contract");
        var list=System.Text.Json.Nodes.JsonNode.Parse(Invoke("workspace_list","list",new{projectId="fixture",query=""}))!.AsArray();Check(list.Count==1&&list[0]!["id"]!.ToString()==id,"only assigned node exposed");
        bool denied=false;try{Invoke("workspace_read","wrong-target",new{projectId="fixture",id=graphId});}catch(UnauthorizedAccessException){denied=true;}Check(denied,"node capability read graph denied");
        denied=false;try{Invoke("workspace_create","wrong-right",new{projectId="fixture",id="App::Injected",kind="function"});}catch(UnauthorizedAccessException){denied=true;}Check(denied,"node capability creation denied");
        string broad=calls.OpenGeneral.Invoke(project,"fixture","App","general","other");
        denied=false;try{calls.Tool.Invoke(broad,"broad-node","workspace_read",System.Text.Json.JsonSerializer.Serialize(new{projectId="fixture",id}));}catch(UnauthorizedAccessException){denied=true;}Check(denied,"broad legacy Worker not silently granted node source");
        var generic=System.Text.Json.Nodes.JsonNode.Parse(calls.Tool.Invoke(broad,"generic-read","workspace_read",System.Text.Json.JsonSerializer.Serialize(new{projectId="fixture",id="App::Value"})))!;string genericOriginal=generic["text"]!.ToString(),genericChanged=genericOriginal+"\n// ordinary general capability draft\n";
        Check(System.Text.Json.Nodes.JsonNode.Parse(calls.Tool.Invoke(broad,"generic-stage","workspace_stage",System.Text.Json.JsonSerializer.Serialize(new{projectId="fixture",id="App::Value",text=genericChanged,expectedRevision=generic["revision"]!.GetValue<long>()})))!["applied"]!.GetValue<bool>(),"general capability stage remains available");
        var genericChanges=System.Text.Json.Nodes.JsonNode.Parse(calls.Tool.Invoke(broad,"generic-changes","workspace_changes","{\"projectId\":\"fixture\"}"))!.AsArray();Check(genericChanges.Count==4&&genericChanges[0]!.ToString()=="App::Value"&&genericChanges[3]!.ToString()==genericChanged,"general capability returns its owned draft changes without node source pin");
        generic=System.Text.Json.Nodes.JsonNode.Parse(calls.Tool.Invoke(broad,"generic-reread","workspace_read",System.Text.Json.JsonSerializer.Serialize(new{projectId="fixture",id="App::Value"})))!;calls.Tool.Invoke(broad,"generic-restore","workspace_stage",System.Text.Json.JsonSerializer.Serialize(new{projectId="fixture",id="App::Value",text=genericOriginal,expectedRevision=generic["revision"]!.GetValue<long>()}));calls.CloseTool.Invoke(broad);
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
        calls.CloseTool.Invoke(capability);
        // A raw graph edit must not lend a previously discovered node source to a new locator.
        now=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(view,"select",System.Text.Json.JsonSerializer.Serialize(new{id=graphId})))!["unit"]!;
        graph=System.Text.Json.Nodes.JsonNode.Parse(graphOriginal)!.AsObject();graph["nodes"]![1]!["implementation"]="different.node.json";
        calls.Command.Invoke(view,"edit",System.Text.Json.JsonSerializer.Serialize(new{text=graph.ToJsonString(),expectedRevision=now["revision"]!.GetValue<long>()}));
        denied=false;string borrowed="";
        try{borrowed=calls.OpenNode.Invoke(project,"fixture","App","owner","nodes",id);}catch(InvalidOperationException){denied=true;}
        finally{if(borrowed.Length>0)calls.CloseTool.Invoke(borrowed);now=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(view,"select",System.Text.Json.JsonSerializer.Serialize(new{id=graphId})))!["unit"]!;calls.Command.Invoke(view,"edit",System.Text.Json.JsonSerializer.Serialize(new{text=graphOriginal,expectedRevision=now["revision"]!.GetValue<long>()}));}
        Check(denied,"graph locator must still name this owned code-node source");
        calls.Command.Invoke(view,"select",System.Text.Json.JsonSerializer.Serialize(new{id}));
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
