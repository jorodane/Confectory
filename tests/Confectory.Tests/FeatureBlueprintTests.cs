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

    public void test_blueprint_node_task_assignment_scoped_dispatch_adoption_and_cold_no_replay()
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
         calls.ViewCommand.Invoke(view,"select",Serialize(new{id=node}));var review=Json(calls.ViewCommand.Invoke(view,"review","{\"target\":\"portable\"}"))["review"]!;Check(review["status"]!.ToString()=="ready","actual compiler-ready node review");
         calls.Adopt.Invoke(owner,task,view,review["token"]!.ToString(),new[]{node},"Fixture accepts the implementation; runtime is independently tested below.");
         Check(Json(calls.Poll.Invoke(owner))["workers"]![task]!["status"]!.ToString()=="completed"&&Json(System.IO.File.ReadAllText(sourcePath))["source"]!.ToString()=="return value + 7;","compiler-backed node adoption");
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
            var built=new Builder(project,"linux").Build();Output(built,"Blueprint node Task assignment/scoped dispatch/adoption/cold no-replay PASS");
            Output(Build(),"9");
        }finally{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",selected);}
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
