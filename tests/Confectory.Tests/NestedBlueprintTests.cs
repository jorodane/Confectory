using Confectory.Core;
using System.Text.Json.Nodes;

namespace Confectory.Tests;

public sealed class NestedBlueprintTests : TestCase
{
    const string Plain = "function Api::Value (int n) -> int {}";
    static JsonObject Sig(string result, params Parameter[] args) => FeatureBlueprint.SignatureDocument(new(args.ToList(), result));
    static JsonObject Input(string name) => new() { ["input"] = name };
    static JsonObject Result(string name) => new() { ["node"] = name };
    static JsonObject Edge(string from, string to, string port = "next") => new() { ["from"] = from, ["to"] = to, ["port"] = port };
    static JsonObject Graph() => new() { ["schema"] = 1, ["profile"] = FeatureBlueprint.NestedProfile, ["entry"] = "", ["nodes"] = new JsonArray(), ["edges"] = new JsonArray(), ["exits"] = new JsonObject() };
    static JsonObject Root(string source = Plain)
    {
        var graph = Graph(); graph["feature"] = "Api::Value";
        graph["contractHash"] = FeatureBlueprint.ContractHash(new Parser(source, "<nested>").ParseElement()); return graph;
    }
    static JsonObject Node(string id, JsonObject signature, JsonObject args, JsonObject? graph = null) => new()
    {
        ["id"] = id, ["kind"] = graph is null ? "code" : "graph", ["control"] = "next", ["intent"] = "Compute " + id,
        ["signature"] = signature, ["arguments"] = args, [graph is null ? "implementation" : "graph"] = graph is null ? JsonValue.Create(id + ".node.json") : graph
    };
    static JsonObject Query(JsonObject graph, string source = Plain, string operation = "featureBlueprintDescribe", JsonObject? records = null, string? probe = null, JsonObject? contracts = null) => FeatureBlueprint.Execute(new()
    {
        ["operation"] = operation, ["featureSource"] = source, ["graph"] = graph.DeepClone(), ["implementations"] = records?.DeepClone(), ["bodyTarget"]="common", ["implementationContext"] = new JsonObject{["implementation"]="Provider::ValueBody"}, ["node"] = probe, ["featureContracts"] = contracts?.DeepClone()
    });
    JsonObject Write(JsonObject graph, Dictionary<string, string> bodies, string source = Plain, JsonObject? contracts = null)
    {
        // Every nested leaf deliberately retains its local ID; only its owner path differs.
        foreach (var entry in BlueprintTree.Nodes(graph).Where(e => e.Node["kind"]!.ToString() == "code")) entry.Node["implementation"] = entry.Key.Replace('/', '-') + ".node.json";
        var definitions = Query(graph, source, "featureBlueprintNodes", contracts: contracts); Equal("node-definitions", Text(definitions, "state"));
        var all = definitions["nodes"]!.AsArray().Concat(definitions["nestedNodes"]?.AsArray() ?? new JsonArray()).ToArray();
        var records = new JsonObject();
        foreach (var body in bodies)
        {
            var definition = all.Single(n => n!["id"]!.ToString() == body.Key)!;
            var record = new JsonObject { ["schema"] = 1, ["node"] = body.Key.Split('/')[^1], ["definitionHash"] = definition["definitionHash"]!.DeepClone(), ["source"] = body.Value };
            records[body.Key] = record; f.Body("Provider", body.Key.Replace('/', '-') + ".node.json", record.ToJsonString());
        }
        var sig = new Parser(source, "<nested>").ParseElement().Signature!;
        f.Add("Api", "function", "Value", source);
        f.Add("Provider", "implementation", "ValueBody", "implementation Provider::ValueBody for Api::Value " + sig.Format() + " {blueprint common \"nested.graph.json\";}");
        f.Add("App", "implementation", "MainBody", "implementation App::MainBody for App::Main () -> int {import Api::Value as Value " + sig.Format(false) + ";body common \"main.csbody\";}");
        f.Body("Provider", "nested.graph.json", graph.ToJsonString()); f.Sync(); return records;
    }
    public void test_private_nested_ref_out_aliases_return_to_parent_and_locals_reset_per_call()
    {
        const string source = "function Api::Value (ref int x,ref int y,out int audit) -> int {}";
        var sig = Sig("int", new Parameter("int", "x", "ref"), new Parameter("int", "y", "ref"), new Parameter("int", "audit", "out"));
        var inner = Graph(); inner["entry"] = "tick";
        inner["locals"] = new JsonArray(new JsonObject { ["id"] = "count", ["name"] = "count", ["type"] = "int", ["initial"] = new JsonObject { ["constant"] = 0 } });
        var tick = Node("tick", Sig("void", new Parameter("int", "counter", "ref")), new() { ["counter"] = new JsonObject { ["local"] = "count" } });
        var mutate = Node("mutate", sig.DeepClone().AsObject(), new() { ["x"] = Input("x"), ["y"] = Input("y") }); mutate["forwardCallerStorage"] = true;
        var combine = Node("combine", Sig("int", new Parameter("int", "a"), new Parameter("int", "b")), new() { ["a"] = Result("mutate"), ["b"] = new JsonObject { ["local"] = "count" } });
        inner["nodes"] = new JsonArray(tick, mutate, combine); inner["edges"] = new JsonArray(Edge("tick", "mutate"), Edge("mutate", "combine"), Edge("combine", "exit:done")); inner["exits"] = new JsonObject { ["done"] = Result("combine") };
        var middle = Graph(); middle["entry"] = "inner";
        var child = Node("inner", sig.DeepClone().AsObject(), new() { ["x"] = Input("x"), ["y"] = Input("y") }, inner); child["forwardCallerStorage"] = true;
        middle["nodes"] = new JsonArray(child); middle["edges"] = new JsonArray(Edge("inner", "exit:done")); middle["exits"] = new JsonObject { ["done"] = Result("inner") };
        var root = Root(source); root["entry"] = "first";
        var first = Node("first", sig, new() { ["x"] = Input("x"), ["y"] = Input("y") }, middle); first["forwardCallerStorage"] = true;
        root["nodes"] = new JsonArray(first); root["edges"] = new JsonArray(Edge("first", "exit:done")); root["exits"] = new JsonObject { ["done"] = Result("first") };
        Write(root, new() { ["first/inner/tick"] = "counter++;", ["first/inner/mutate"] = "x=10;y+=x;audit=x+y;return audit;", ["first/inner/combine"] = "return a+b;" }, source);
        f.Body("App", "main.csbody", "for(int i=0;i<2;i++){int n=5;int result=calls.Value.Invoke(ref n,ref n,out n);Console.WriteLine(result+\",\"+n);}int x=5,y=6;int answer=calls.Value.Invoke(ref x,ref y,out int audit);Console.WriteLine(answer+\",\"+x+\",\"+y+\",\"+audit);return 0;");
        var report = Build(); Output(report, "41,40\n41,40\n27,10,16,26");
        True(report["blueprints"]!["Provider::ValueBody"]!["nestedNodes"]!.AsArray().All(n => n!["compilerValidated"]!.GetValue<bool>()));
        var map = report["blueprints"]!["Provider::ValueBody"]!["sourceMap"]!.AsArray().Single(m => m!["node"]!.ToString() == "first/inner/mutate")!;
        True(map["path"]!.ToString().EndsWith("first-inner-mutate.node.json")); Equal("/source", Text(map, "jsonPointer"));
    }
    public void test_private_siblings_keep_same_local_ids_and_branch_return_boundary()
    {
        var left = Graph(); left["entry"] = "body"; left["nodes"] = new JsonArray(Node("body", Sig("bool", new Parameter("int", "value")), new() { ["value"] = Input("n") })); left["edges"] = new JsonArray(Edge("body", "exit:done")); left["exits"] = new JsonObject { ["done"] = Result("body") };
        var right = Graph(); right["entry"] = "body"; right["nodes"] = new JsonArray(Node("body", Sig("int", new Parameter("int", "value")), new() { ["value"] = Input("n") })); right["edges"] = new JsonArray(Edge("body", "exit:done")); right["exits"] = new JsonObject { ["done"] = Result("body") };
        var root = Root(); var condition = Node("left", Sig("bool", new Parameter("int", "n")), new() { ["n"] = Input("n") }, left); condition["control"] = "branch";
        root["entry"] = "left"; root["nodes"] = new JsonArray(condition, Node("right", Sig("int", new Parameter("int", "n")), new() { ["n"] = Input("n") }, right));
        root["edges"] = new JsonArray(Edge("left", "right", "true"), Edge("left", "exit:negative", "false"), Edge("right", "exit:done")); root["exits"] = new JsonObject { ["negative"] = new JsonObject { ["constant"] = -1 }, ["done"] = Result("right") };
        var records = Write(root, new() { ["left/body"] = "return value>0;", ["right/body"] = "return value+9;" });
        f.Body("App", "main.csbody", "foreach(int n in new[]{2,-2,3})Console.WriteLine(calls.Value.Invoke(n));return 0;"); Output(Build(), "11\n-1\n12");
        var probe = new Builder(f.Project, "portable").CheckBlueprintNode("Provider::ValueBody", "common", "right/body"); Equal("node-compiled", Text(probe, "state")); Equal("right/body", Text(probe, "node")); True(!probe["executed"]!.GetValue<bool>());
        var moved = root.DeepClone().AsObject(); moved["nodes"]![1]!["graph"]!["nodes"]![0]!["arguments"]!["value"] = new JsonObject { ["input"] = "parent_only" };
        Equal("GRAPH_INPUT_TYPE", Text(Query(moved, records: records)["diagnostics"]![0]!, "code"));
        moved = root.DeepClone().AsObject(); moved["nodes"]![1]!["graph"]!["edges"]![0]!["to"] = "body";
        Equal("GRAPH_CYCLE_PROFILE_UNSUPPORTED", Text(Query(moved, records: records)["diagnostics"]![0]!, "code"));
        moved = root.DeepClone().AsObject(); moved["nodes"]![1]!["graph"]!["nodes"]![0]!["implementation"] = "left-body.node.json";
        f.Body("Provider", "nested.graph.json", moved.ToJsonString()); Error("BLUEPRINT_NODE_OWNERSHIP", () => Build());
    }
    public void test_private_imports_are_explicit_and_unused_child_bodies_are_compiled_without_execution()
    {
        const string twice="function Api::Double (int value) -> int {}";
        var child=Graph();child["entry"]="invoke";var call=Node("invoke",Sig("int",new Parameter("int","value")),new(){["value"]=Input("value")});call["kind"]="call";call.Remove("implementation");call["feature"]="Api::Double";
        child["nodes"]=new JsonArray(call);child["edges"]=new JsonArray(Edge("invoke","exit:done"));child["exits"]=new JsonObject{["done"]=Result("invoke")};
        var root=Root();root["entry"]="private";root["nodes"]=new JsonArray(Node("private",Sig("int",new Parameter("int","value")),new(){["value"]=Input("n")},child));root["edges"]=new JsonArray(Edge("private","exit:done"));root["exits"]=new JsonObject{["done"]=Result("private")};
        Write(root,new(),contracts:new(){["Api::Double"]=twice});f.Add("Api","function","Double",twice);f.Add("Provider","implementation","DoubleBody","implementation Provider::DoubleBody for Api::Double (int value) -> int {body common \"double.csbody\";}");f.Body("Provider","double.csbody","return value*2;");f.Main("provide Api::Value with Provider::ValueBody;provide Api::Double with Provider::DoubleBody;");
        string declaration="implementation Provider::ValueBody for Api::Value (int n) -> int {import Api::Double as "+FeatureBlueprint.ImportAlias("Api::Double")+" (int) -> int;blueprint common \"nested.graph.json\";}";f.Add("Provider","implementation","ValueBody",declaration);f.Sync();Output(Build(),"4");
        // A prepared but disconnected private leaf must still reach the real compiler.
        var loose=Graph();loose["entry"]="body";loose["nodes"]=new JsonArray(Node("body",Sig("int",new Parameter("int","value")),new(){["value"]=Input("value")}));loose["edges"]=new JsonArray(Edge("body","exit:done"));loose["exits"]=new JsonObject{["done"]=Result("body")};root["nodes"]!.AsArray().Add(Node("unused",Sig("int",new Parameter("int","value")),new(){["value"]=Input("n")},loose));
        var records=Write(root,new(){["unused/body"]="throw new Exception(\"Do not execute private independent body\");"},contracts:new(){["Api::Double"]=twice});f.Add("Provider","implementation","ValueBody",declaration);f.Sync();Output(Build(),"4");
        var proof=new Builder(f.Project,"portable").CheckBlueprintNode("Provider::ValueBody","common","unused/body");Equal("unused/body",Text(proof,"node"));True(!proof["executed"]!.GetValue<bool>());
        records["unused/body"]!["source"]="return missing_in_private;";f.Body("Provider","unused-body.node.json",records["unused/body"]!.ToJsonString());var error=Error("TARGET_FAILURE",()=>Build());True(error.Message.Contains("Blueprint.Private::",StringComparison.Ordinal),error.Message);
        foreach(string invalid in new[]{"int __fg_escape=0;return __fg_escape;","#line 1 \"forged\"\nreturn value;","return n;"}){records["unused/body"]!["source"]=invalid;f.Body("Provider","unused-body.node.json",records["unused/body"]!.ToJsonString());Error("TARGET_FAILURE",()=>Build());}
    }
    public void test_private_observations_are_rechecked_after_real_compiler_and_original_proof_is_retained()
    {
        var child=Graph();child["entry"]="body";child["nodes"]=new JsonArray(Node("body",Sig("int",new Parameter("int","value")),new(){["value"]=Input("value")}));child["edges"]=new JsonArray(Edge("body","exit:done"));child["exits"]=new JsonObject{["done"]=Result("body")};var root=Root();root["entry"]="private";root["nodes"]=new JsonArray(Node("private",Sig("int",new Parameter("int","value")),new(){["value"]=Input("n")},child));root["edges"]=new JsonArray(Edge("private","exit:done"));root["exits"]=new JsonObject{["done"]=Result("private")};Write(root,new(){["private/body"]="return value+3;"});var before=Build();Output(before,"5");
        string latest=Path.Combine(Path.GetDirectoryName(Text(before,"output"))!,"latest.json"),prior=File.ReadAllText(latest),tool=Path.Combine(f.Root,"target","blueprint-probe");Directory.CreateDirectory(tool);foreach(string file in Directory.GetFiles(AppContext.BaseDirectory))File.Copy(file,Path.Combine(tool,Path.GetFileName(file)),true);string node=Path.Combine(f.Packs["Provider"].Root,"private-body.node.json");File.WriteAllText(Path.Combine(tool,"blueprint-mutate-probe.json"),new JsonObject{["node"]=node,["target"]=f.ToolPath}.ToJsonString());string target=Path.Combine(f.Root,"target","portable.celem");File.WriteAllText(target,File.ReadAllText(target).Replace("bin/Release/net10.0/Confectory.Build.DotNet.dll","blueprint-probe/Confectory.Tests.dll",StringComparison.Ordinal));Error("BLUEPRINT_SOURCE_CHANGED",()=>Build());Equal(prior,File.ReadAllText(latest));True(File.ReadAllText(node).EndsWith(" ",StringComparison.Ordinal));
    }

    public void test_private_paths_separate_identical_local_definitions_and_reject_parent_capture_and_depth()
    {
        var child=Graph();child["entry"]="body";child["nodes"]=new JsonArray(Node("body",Sig("int",new Parameter("int","value")),new(){["value"]=Input("value")}));child["edges"]=new JsonArray(Edge("body","exit:done"));child["exits"]=new JsonObject{["done"]=Result("body")};var root=Root();root["entry"]="left";root["nodes"]=new JsonArray(Node("left",Sig("int",new Parameter("int","value")),new(){["value"]=Input("n")},child.DeepClone().AsObject()),Node("right",Sig("int",new Parameter("int","value")),new(){["value"]=Input("n")},child));
        var defs=Query(root,operation:"featureBlueprintNodes");Equal("node-definitions",Text(defs,"state"));var descendants=defs["nestedNodes"]!.AsArray();True(descendants[0]!["definitionHash"]!.ToString()!=descendants[1]!["definitionHash"]!.ToString(),"owner path is part of otherwise identical leaf definition");
        foreach(var owner in new[]{("Provider::OtherBody","common"),("Provider::ValueBody","portable")}){var alternate=FeatureBlueprint.Execute(new(){["operation"]="featureBlueprintNodes",["featureSource"]=Plain,["graph"]=root.DeepClone(),["implementationContext"]=new JsonObject{["implementation"]=owner.Item1},["bodyTarget"]=owner.Item2});Equal("node-definitions",Text(alternate,"state"));True(descendants[0]!["definitionHash"]!.ToString()!=alternate["nestedNodes"]![0]!["definitionHash"]!.ToString(),"implementation and body target belong to private source identity");}
        var forged=FeatureBlueprint.Execute(new(){["operation"]="featureBlueprintNodes",["featureSource"]=Plain,["graph"]=root.DeepClone(),["sourcePath"]="forged"});Equal("GRAPH_REQUEST_FIELD",Text(forged["diagnostics"]![0]!,"code"));
        var capture=root.DeepClone().AsObject();capture["locals"]=new JsonArray(new JsonObject{["id"]="parent",["name"]="parent",["type"]="int",["initial"]=new JsonObject{["constant"] =1}});capture["nodes"]![0]!["graph"]!["nodes"]![0]!["arguments"]!["value"]=new JsonObject{["local"]="parent"};Equal("GRAPH_LOCAL_TYPE",Text(Query(capture)["diagnostics"]![0]!,"code"));
        var nested=Graph();for(int i=0;i<10;i++){var outer=Graph();outer["nodes"]=new JsonArray(Node("same",Sig("void"),new(),nested));nested=outer;}var deep=Root();deep["nodes"]=nested["nodes"]!.DeepClone();Equal("GRAPH_SHAPE",Text(Query(deep,operation:"featureBlueprintNodes")["diagnostics"]![0]!,"code"));
    }

    public void test_private_unassigned_outputs_reach_build_warnings_with_full_call_path()
    {
        var missing=Graph();var outer=Graph();outer["entry"]="inner";
        outer["nodes"]=new JsonArray(Node("inner",Sig("int",new Parameter("int","value"),new Parameter("int","audit","out")),new(){["value"]=Input("value")},missing));outer["edges"]=new JsonArray(Edge("inner","exit:done"));outer["exits"]=new JsonObject{["done"]=Result("inner")};var root=Root();root["entry"]="outer";root["nodes"]=new JsonArray(Node("outer",Sig("int",new Parameter("int","value")),new(){["value"]=Input("n")},outer));root["edges"]=new JsonArray(Edge("outer","exit:done"));root["exits"]=new JsonObject{["done"]=Result("outer")};
        var described=Query(root);Equal("source-ready",Text(described,"state"));Equal(0,described["warnings"]!.AsArray().Count);Equal(1,described["nestedWarnings"]!.AsArray().Count);var warning=described["nestedWarnings"]![0]!;Equal("outer/inner",Text(warning,"privatePath"));Sequence(new[]{"return","audit"},warning["missingOutputs"]!.AsArray().Select(o=>o!["name"]!.ToString()));
        Write(root,new());var built=Build();Output(built,"0");var report=built["blueprintWarnings"]!.AsArray();Equal(1,report.Count);Equal("Provider::ValueBody",Text(report[0]!,"implementation"));Equal("outer/inner",Text(report[0]!,"privatePath"));True(Text(report[0]!,"graphPath").EndsWith("nested.graph.json",StringComparison.Ordinal));Equal("GRAPH_RETURN_UNASSIGNED",Text(report[0]!,"code"));
    }

}
