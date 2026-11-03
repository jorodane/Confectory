using Confectory.Core;
using System.Text.Json;
using System.Text.Json.Nodes;

namespace Confectory.Tests;

public sealed class AsyncBlueprintTests : TestCase
{
    static Element Function(string signature = "(int input,out int Branch,out string FunctionResult,out string Return) -> int") => new Parser("function Api::Value " + signature + " {}", "<async-contract>").ParseElement();
    static void Refused(Action action)
    {
        try { action(); } catch (ArgumentException) { return; }
        throw new Exception("Incompatible async contract was accepted");
    }
    public void test_explicit_async_preserves_signature_and_result_branch_identity()
    {
        var function = Function();
        BlueprintExecutionBranches.Set(function, new JsonArray(new JsonObject { ["id"] = "kept", ["name"] = "기존 결과", ["value"] = 37 }));
        string signature = function.Signature!.Format(), before = FeatureBlueprint.ContractHash(function);
        var branches = BlueprintExecutionBranches.Read(function);
        BlueprintAsync.Set(function, "completion");
        Equal(signature, function.Signature.Format()); True(JsonNode.DeepEquals(branches, BlueprintExecutionBranches.Read(function)));
        Equal("completion", BlueprintAsync.Read(function)!["completion"]!.ToString());
        True(before != FeatureBlueprint.ContractHash(function)); string current = FeatureBlueprint.ContractHash(function);
        BlueprintAsync.Set(function, "completion"); Equal(current, FeatureBlueprint.ContractHash(function));
    }
    public void test_async_ref_and_inherited_contract_changes_are_rejected_without_mutation()
    {
        var inherited = Function("(int input) -> void"); inherited.Parent = "Api::Parent";
        foreach (var function in new[] { Function("(ref int value) -> void"), inherited })
        {
            string before = JsonData.Digest(function); Refused(() => BlueprintAsync.Set(function, "completion"));
            Equal(before, JsonData.Digest(function)); True(!BlueprintAsync.Has(function));
        }
    }
    public void test_completion_cannot_replace_none_or_an_existing_result_branch()
    {
        foreach (string name in new[] { "기존 결과", "완료 시" })
        {
            var function = Function(); BlueprintExecutionBranches.Set(function, new JsonArray(new JsonObject { ["id"] = "kept", ["name"] = name, ["value"] = 37 }));
            string before = JsonData.Digest(function);
            Refused(() => BlueprintAsync.Set(function, name == "완료 시" ? "completion" : "kept"));
            Refused(() => BlueprintAsync.Set(function, "none")); Equal(before, JsonData.Digest(function));
        }
    }
    public void test_generated_task_contract_compiles_outputs_and_rejects_ordinary_sync_call()
    {
        var function = Function(); BlueprintAsync.Set(function, "completion");
        var builder = new Builder(f.Project, "portable"); string root = Path.Combine(f.Root, "async-contract"); Directory.CreateDirectory(root);
        string contract = Path.Combine(root, "contract.cs"); File.WriteAllText(contract, Generation.ContractSource(function));
        var built = builder.Tool.Invoke("compile-contract", new { output = Path.Combine(root, "contract"), name = "AsyncContract", sources = new[] { contract }, references = Array.Empty<string>() });
        string assembly = built["artifacts"]!["assembly"]!.ToString(); True(File.Exists(assembly));
        string positive = Path.Combine(root, "awaited.cs"), negative = Path.Combine(root, "ordinary.cs");
        File.WriteAllText(positive, "public static class Awaited { public static async global::System.Threading.Tasks.Task<int> Run(" + BlueprintAsync.Interface(function.Id) + " function) { var result = await function.InvokeAsync(7); return result." + BlueprintAsync.ReturnName(function.Signature!) + " + result.Branch + (int)result." + BlueprintAsync.BranchName(function.Signature!) + "; } }");
        builder.Tool.Invoke("compile-pack", new { output = Path.Combine(root, "positive"), name = "AwaitedConsumer", sources = new[] { positive }, references = new[] { assembly } });
        File.WriteAllText(negative, "public static class Ordinary { public static int Run(" + Generation.Interface(function.Id) + " function) { return function.Invoke(7,out int branch,out string result,out string native); } }");
        var error = Error("TARGET_FAILURE", () => builder.Tool.Invoke("compile-pack", new { output = Path.Combine(root, "negative"), name = "OrdinaryConsumer", sources = new[] { negative }, references = new[] { assembly } }));
        True(error.Message.Contains("explicitly convert the caller", StringComparison.Ordinal));
    }

    static string Source(string id, string signature, bool branches = false) => "function " + id + " " + signature + " { value blueprintAsync = " + JsonSerializer.Serialize(new JsonObject { ["schema"] = 1, ["completion"] = "completion" }.ToJsonString()) + ";" + (branches ? "value blueprintExecutionBranches = " + JsonSerializer.Serialize(new JsonObject { ["schema"] = 1, ["branches"] = new JsonArray(new JsonObject { ["id"] = "success", ["name"] = "성공", ["value"] = 7 }, new JsonObject { ["id"] = "failure", ["name"] = "실패", ["value"] = 13 }) }.ToJsonString()) + ";" : "") + " }";
    static JsonObject Edge(string from, string to, string port = "next") => new() { ["from"] = from, ["to"] = to, ["port"] = port };
    static JsonObject Graph(string source, string entry) { var fn = new Parser(source,"<async-graph>").ParseElement(); return new() { ["schema"] = BlueprintExecutionBranches.Has(fn) ? 2 : 1, ["profile"] = BlueprintAsync.Has(fn) ? BlueprintAsync.Profile : FeatureBlueprint.SwitchProfile, ["feature"] = fn.Id, ["contractHash"] = FeatureBlueprint.ContractHash(fn), ["entry"] = entry, ["nodes"] = new JsonArray(), ["edges"] = new JsonArray(), ["exits"] = new JsonObject() }; }
    static JsonObject Code(string id, FunctionSignature signature, JsonObject arguments, string? owner = null, bool async = false) { var node = new JsonObject { ["id"] = id, ["kind"] = "code", ["control"] = "next", ["intent"] = "Observe exact async order: " + id, ["signature"] = FeatureBlueprint.SignatureDocument(signature), ["arguments"] = arguments, ["implementation"] = id + ".node.json" }; if(owner is not null)node["branchOwner"] = owner; if(async)node["async"] = true; return node; }
    static JsonObject Query(string source, JsonObject graph, string operation = "featureBlueprintDescribe", JsonObject? contracts = null, JsonObject? records = null) => FeatureBlueprint.Execute(new() { ["operation"] = operation, ["featureSource"] = source, ["graph"] = graph.DeepClone(), ["featureContracts"] = contracts?.DeepClone(), ["implementations"] = records?.DeepClone() });
    JsonObject Write(string owner, string source, JsonObject graph, Dictionary<string,string> bodies, JsonObject? contracts = null) {
        var definitions = Query(source,graph,"featureBlueprintNodes",contracts); Equal("node-definitions", Text(definitions,"state")); var records = new JsonObject();
        foreach(var pair in bodies) { var definition = definitions["nodes"]!.AsArray().Single(n=>n!["id"]!.ToString()==pair.Key)!; var record = new JsonObject { ["schema"] = 1, ["node"] = pair.Key, ["definitionHash"] = definition["definitionHash"]!.DeepClone(), ["source"] = pair.Value }; records[pair.Key] = record.DeepClone(); f.Body(owner,pair.Key+".node.json",record.ToJsonString()); }
        var proof = Query(source,graph,contracts:contracts,records:records); Equal("source-ready",Text(proof,"state")); f.Body(owner,"async.graph.json",graph.ToJsonString()); return records;
    }
    void Runtime(bool fail = false, bool emptyCompletion = false, bool unselected = false) {
        string source=Source("Api::Value","(int n,out int audit) -> int",true), main=Source("App::Main","() -> int").Replace("{ value", "{ provide App::Main with App::MainBody; provide Api::Value with Provider::ValueBody; value",StringComparison.Ordinal); var fn=new Parser(source,"<async-value>").ParseElement(); var graph=Graph(source,"work");graph["executionExitMode"]=true;
        graph["nodes"]=new JsonArray(Code("work",fn.Signature!,new JsonObject { ["n"]=new JsonObject { ["input"]="n" } },async:true),new JsonObject { ["id"]="publish",["kind"]="export",["control"]="next",["intent"]="Publish the exact out",["signature"]=FeatureBlueprint.SignatureDocument(new(new(){new("int","value")},"void")),["output"]="audit",["arguments"]=new JsonObject { ["value"]=new JsonObject { ["node"]="work",["output"]="audit" } } });
        graph["edges"]=new JsonArray(Edge("work","publish"),Edge("publish","exit:done"));graph["exits"]=new JsonObject { ["done"]=new JsonObject { ["executionBranch"]="success",["value"]=new JsonObject { ["node"]="work" } } };
        string original=fail ? "await global::System.Threading.Tasks.Task.Delay(15); throw new InvalidOperationException(\"async-original-error\");" : "await global::System.Threading.Tasks.Task.Delay(30);audit=n*2;Console.WriteLine(\"awaited\");return n+1;";
        if(unselected)graph["exits"]!["done"]!["executionBranch"]="none";
        var records=Write("Provider",source,graph,new(){["work"]=original});
        f.Add("Api","function","Value",source);f.Add("Provider","implementation","ValueBody","implementation Provider::ValueBody for Api::Value (int n,out int audit) -> int {blueprint common \"async.graph.json\";}");
        f.Add("App","function","Main",main);var caller=Graph(main,"call");var call=new JsonObject { ["id"]="call",["kind"]="call",["control"]="switch",["intent"]="Await before publishing outputs and routing",["feature"]=fn.Id,["signature"]=FeatureBlueprint.SignatureDocument(fn.Signature!),["arguments"]=new JsonObject { ["n"]=new JsonObject { ["constant"]=5 } },["publicExecution"]=FeatureBlueprint.ContractHash(fn),["executionEnum"]=BlueprintExecutionBranches.Enum(fn) };
        var read=new FunctionSignature(new(){new("int","native"),new("int","audit")},"void");JsonObject Args()=>new() { ["native"]=new JsonObject { ["node"]="call" },["audit"]=new JsonObject { ["node"]="call",["output"]="audit" } };
        caller["nodes"]=new JsonArray(call,Code("complete",read,Args(),"call"),Code("success",read,Args(),"call"),Code("failure",read,Args(),"call"),Code("after",new(new(),"void"),new()));caller["edges"]=new JsonArray(Edge("call","complete","completion"),Edge("call","success","case:success"),Edge("call","failure","case:failure"),Edge("call","after"),Edge("after","exit:done"));caller["exits"]=new JsonObject { ["done"]=new JsonObject { ["constant"]=0 } };
        if(emptyCompletion)caller["edges"]![0]!["to"]="return:call";
        Write("App",main,caller,new(){["complete"]="Console.WriteLine(\"complete:\"+native+\",\"+audit);",["success"]="Console.WriteLine(\"success:\"+native+\",\"+audit);",["failure"]="Console.WriteLine(\"failure\");",["after"]="Console.WriteLine(\"after\");"},new(){[fn.Id]=source});
        f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import Api::Value as "+FeatureBlueprint.ImportAlias(fn.Id)+" (int,out int) -> int;blueprint common \"async.graph.json\";}");f.Sync();
        if(!fail)Output(Build(),"awaited\n"+(emptyCompletion?"":"complete:6,10\n")+(unselected?"":"success:6,10\n")+"after");else {var built=Build();var result=Processes.Run(Strings(built,"run"),timeoutSeconds:60);True(result.ExitCode!=0);True(result.Stderr.Contains("async-original-error"));True(!result.Stdout.Contains("complete:")&&!result.Stdout.Contains("failure")&&!result.Stdout.Contains("after"));}
        Equal(original,records["work"]!["source"]!.ToString());
    }
    public void test_real_await_publishes_outputs_before_completion_result_and_continuation() => Runtime();
    public void test_empty_completion_still_dispatches_the_exact_result_once() => Runtime(emptyCompletion:true);
    public void test_none_result_runs_completion_then_continuation_without_implicit_success() => Runtime(unselected:true);
    public void test_task_exception_preserves_original_error_and_does_not_route_failure() => Runtime(true);
    public void test_explicit_async_empty_root_keeps_default_return_without_fake_await() {
        string source=Source("Api::Value","(int n,out int audit) -> int"),main=Source("App::Main","() -> int").Replace("{ value","{ provide App::Main with App::MainBody; provide Api::Value with Provider::ValueBody; value",StringComparison.Ordinal);
        var empty=Graph(source,"");Write("Provider",source,empty,new());f.Add("Api","function","Value",source);f.Add("Provider","implementation","ValueBody","implementation Provider::ValueBody for Api::Value (int n,out int audit) -> int {blueprint common \"async.graph.json\";}");
        var caller=Graph(main,"call");var fn=new Parser(source,"<empty>").ParseElement();caller["nodes"]=new JsonArray(new JsonObject { ["id"]="call",["kind"]="call",["control"]="next",["intent"]="Explicitly await empty function",["feature"]=fn.Id,["signature"]=FeatureBlueprint.SignatureDocument(fn.Signature!),["arguments"]=new JsonObject { ["n"]=new JsonObject { ["constant"]=5 } } },Code("after",new(new(){new("int","native"),new("int","audit")},"void"),new(){["native"]=new JsonObject{["node"]="call"},["audit"]=new JsonObject{["node"]="call",["output"]="audit"}}));caller["edges"]=new JsonArray(Edge("call","after"),Edge("after","exit:done"));caller["exits"]=new JsonObject{["done"]=new JsonObject{["constant"]=0}};
        Write("App",main,caller,new(){["after"]="Console.WriteLine(native+\",\"+audit);"},new(){[fn.Id]=source});f.Add("App","function","Main",main);f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import Api::Value as "+FeatureBlueprint.ImportAlias(fn.Id)+" (int,out int) -> int;blueprint common \"async.graph.json\";}");f.Sync();Output(Build(),"0,0");
    }
    public void test_plain_csharp_sync_caller_cannot_access_async_entry_without_conversion() {
        string source=Source("Api::Value","(int n) -> int");var empty=Graph(source,"");Write("Provider",source,empty,new());f.Add("Api","function","Value",source);f.Add("Provider","implementation","ValueBody","implementation Provider::ValueBody for Api::Value (int n) -> int {blueprint common \"async.graph.json\";}");
        f.Body("App","main.csbody","_ = calls.Value.InvokeAsync(2);return 0;");f.Sync();var error=Error("TARGET_FAILURE",()=>Build());True(error.Message.Contains("InvokeAsync"));
    }
    public void test_sync_caller_is_rejected_until_explicitly_changed_without_inference() {
        string source=Source("Api::Value","() -> void"), main="function App::Main () -> int {}";var fn=new Parser(source,"<async>").ParseElement();var graph=Graph(main,"call");graph["nodes"]=new JsonArray(new JsonObject { ["id"]="call",["kind"]="call",["control"]="next",["intent"]="Incompatible existing sync caller",["feature"]=fn.Id,["signature"]=FeatureBlueprint.SignatureDocument(fn.Signature!),["arguments"]=new JsonObject() });
        string before=graph.ToJsonString();var result=Query(main,graph,contracts:new(){[fn.Id]=source});Equal("invalid",Text(result,"state"));Equal("GRAPH_ASYNC_CALLER_REQUIRED",Text(result["diagnostics"]![0]!,"code"));Equal(before,graph.ToJsonString());True(!BlueprintAsync.Has(new Parser(main,"<caller>").ParseElement()));
    }
}
