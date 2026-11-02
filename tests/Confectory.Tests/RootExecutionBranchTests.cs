using Confectory.Core;
using System.Text.Json;
using System.Text.Json.Nodes;

namespace Confectory.Tests;

public sealed class RootExecutionBranchTests : TestCase
{
    static JsonArray Branches() => new(new JsonObject { ["id"]="success", ["name"]="성공", ["value"]=7 }, new JsonObject { ["id"]="failure", ["name"]="실패", ["value"]=13 });
    static string Function(JsonArray? branches=null) => "function Api::Value (int mode) -> void { value blueprintExecutionBranches = " + JsonSerializer.Serialize(new JsonObject { ["schema"]=1, ["branches"]=branches??Branches() }.ToJsonString()) + "; }";
    static JsonObject Signature(string result="void", params Parameter[] args) => FeatureBlueprint.SignatureDocument(new(args.ToList(),result));
    static JsonObject Edge(string from,string to,string port="next") => new() { ["from"]=from,["to"]=to,["port"]=port };
    static JsonObject Graph(string feature,string source,string entry) => new() { ["schema"]=1,["profile"]=FeatureBlueprint.SwitchProfile,["feature"]=feature,["contractHash"]=FeatureBlueprint.ContractHash(new Parser(source,"<root-branches>").ParseElement()),["entry"]=entry,["nodes"]=new JsonArray(),["edges"]=new JsonArray(),["exits"]=new JsonObject() };
    static JsonObject Query(string source,JsonObject graph,JsonObject? contracts=null,JsonObject? records=null,string operation="featureBlueprintDescribe") => FeatureBlueprint.Execute(new() { ["operation"]=operation,["featureSource"]=source,["graph"]=graph.DeepClone(),["featureContracts"]=contracts?.DeepClone(),["implementations"]=records?.DeepClone() });
    static JsonObject Callee(string source) {
        var graph=Graph("Api::Value",source,"choose");graph["schema"]=2;graph["executionExitMode"]=true;
        graph["nodes"]=new JsonArray(new JsonObject { ["id"]="choose",["kind"]="code",["control"]="branch",["intent"]="Keep the original C# decision",["signature"]=Signature("bool",new Parameter("int","mode")),["arguments"]=new JsonObject { ["mode"]=new JsonObject { ["input"]="mode" } },["implementation"]="choose.node.json" });
        graph["edges"]=new JsonArray(Edge("choose","exit:yes","true"),Edge("choose","exit:no","false"));
        graph["exits"]=new JsonObject { ["yes"]=new JsonObject { ["executionBranch"]="success" },["no"]=new JsonObject { ["executionBranch"]="failure" } };return graph;
    }
    JsonObject Records(string owner,JsonObject graph,string source,Dictionary<string,string> bodies,JsonObject? contracts=null) {
        var definitions=Query(source,graph,contracts,operation:"featureBlueprintNodes");Equal("node-definitions",Text(definitions,"state"));var records=new JsonObject();
        foreach(var pair in bodies) { var definition=definitions["nodes"]!.AsArray().Single(n=>n!["id"]!.ToString()==pair.Key)!;var record=new JsonObject { ["schema"]=1,["node"]=pair.Key,["definitionHash"]=definition["definitionHash"]!.DeepClone(),["source"]=pair.Value }; records[pair.Key]=record.DeepClone();f.Body(owner,pair.Key+".node.json",record.ToJsonString()); }
        return records;
    }
    public void test_public_branch_returns_route_direct_blueprint_call_once_and_preserve_void_invoke() {
        string source=Function(),main="function App::Main () -> int {}";var contract=new Parser(source,"<contract>").ParseElement();var callee=Callee(source);
        const string original="Console.WriteLine(\"callee:\"+mode);return mode>0;";
        var records=Records("Provider",callee,source,new() { ["choose"]=original });var ready=Query(source,callee,records:records);True(ready["state"]?.ToString()=="source-ready",ready.ToJsonString());
        f.Add("Api","function","Value",source);f.Add("Provider","implementation","ValueBody","implementation Provider::ValueBody for Api::Value (int mode) -> void {blueprint common \"callee.graph.json\";}");f.Body("Provider","callee.graph.json",callee.ToJsonString());
        var caller=Graph("App::Main",main,"call");caller["nodes"]=new JsonArray(new JsonObject { ["id"]="call",["kind"]="call",["control"]="switch",["intent"]="Route the exact public result",["feature"]="Api::Value",["signature"]=FeatureBlueprint.SignatureDocument(contract.Signature!),["arguments"]=new JsonObject { ["mode"]=new JsonObject { ["constant"]=1 } },["publicExecution"]=FeatureBlueprint.ContractHash(contract),["executionEnum"]=BlueprintExecutionBranches.Enum(contract) });
        foreach(string id in new[]{"yes","no","after"}) {var node=new JsonObject { ["id"]=id,["kind"]="code",["control"]="next",["intent"]="Print "+id,["signature"]=Signature(),["arguments"]=new JsonObject(),["implementation"]=id+".node.json" };if(id!="after")node["branchOwner"]="call";caller["nodes"]!.AsArray().Add(node);}
        caller["edges"]=new JsonArray(Edge("call","yes","case:success"),Edge("call","no","case:failure"),Edge("call","after"),Edge("after","exit:done"));caller["exits"]=new JsonObject { ["done"]=new JsonObject { ["constant"]=0 } };
        var contracts=new JsonObject { ["Api::Value"]=source };Records("App",caller,main,new() { ["yes"]="Console.WriteLine(\"success\");",["no"]="Console.WriteLine(\"failure\");",["after"]="Console.WriteLine(\"continue\");" },contracts);
        f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import Api::Value as "+FeatureBlueprint.ImportAlias("Api::Value")+" (int) -> void;blueprint common \"caller.graph.json\";}");f.Body("App","caller.graph.json",caller.ToJsonString());f.Sync();Output(Build(),"callee:1\nsuccess\ncontinue");
        caller["nodes"]![0]!["arguments"]!["mode"]!["constant"]=-1;f.Body("App","caller.graph.json",caller.ToJsonString());Output(Build(),"callee:-1\nfailure\ncontinue");
        // The original void entry remains usable and invokes the implementation once.
        f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import Api::Value as Original (int) -> void;body common \"legacy.csbody\";}");f.Body("App","legacy.csbody","calls.Original.Invoke(1);return 0;");f.Sync();Output(Build(),"callee:1");Equal(original,records["choose"]!["source"]!.ToString());
    }
    public void test_missing_or_unknown_branch_never_selects_an_implicit_default() {
        string source=Function();var graph=Callee(source);graph["exits"]!["yes"]!["executionBranch"]="removed";Equal("GRAPH_EXECUTION_EXIT_BRANCH",Text(Query(source,graph)["diagnostics"]![0]!,"code"));
        graph=Callee(source);graph["exits"]!["yes"]=null;Equal("GRAPH_EXECUTION_EXIT_SELECTION",Text(Query(source,graph)["diagnostics"]![0]!,"code"));
        graph=Callee(source);graph.Remove("executionExitMode");Equal("GRAPH_PUBLIC_EXECUTION_EXITS",Text(Query(source,graph)["diagnostics"]![0]!,"code"));
    }
    public void test_branch_identity_survives_name_order_and_contract_hash_rejects_stale_selection() {
        var branches=Branches();string first=Function(branches.DeepClone().AsArray());var reordered=new JsonArray(branches[1]!.DeepClone(),branches[0]!.DeepClone());reordered[1]!["name"]="성공 이름 변경";string next=Function(reordered);
        var before=BlueprintExecutionBranches.Enum(new Parser(first,"<before>").ParseElement());var after=BlueprintExecutionBranches.Enum(new Parser(next,"<after>").ParseElement());Equal(before["members"]![1]!["name"]!.ToString(),after["members"]![2]!["name"]!.ToString());Equal(7,after["members"]![2]!["value"]!.GetValue<int>());
        Equal("GRAPH_CONTRACT_STALE",Text(Query(next,Callee(first))["diagnostics"]![0]!,"code"));
    }
    public void test_unconnected_public_root_returns_none_without_selecting_success_or_failure() {
        string source=Function(new JsonArray()).Replace("int mode", "int ExecuteBranches", StringComparison.Ordinal);var graph=Callee(source);graph["entry"]="";graph["nodes"]=new JsonArray();graph["edges"]=new JsonArray();graph["exits"]=new JsonObject();
        var ready=Query(source,graph);True(ready["state"]?.ToString()=="source-ready",ready.ToJsonString());
        f.Add("Api","function","Value",source);f.Add("Provider","implementation","ValueBody","implementation Provider::ValueBody for Api::Value (int ExecuteBranches) -> void {blueprint common \"empty.graph.json\";}");f.Body("Provider","empty.graph.json",graph.ToJsonString());
        f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import Api::Value as Original (int) -> void;body common \"main.csbody\";}");f.Body("App","main.csbody","Console.WriteLine((int)(("+BlueprintExecutionBranches.Interface("Api::Value")+")calls.Original).InvokeExecution(1));return 0;");f.Sync();Output(Build(),"0");
    }
    public void test_public_branches_refuse_opaque_provider_without_rewriting_its_original() {
        string source=Function();f.Add("Api","function","Value",source);f.Add("Provider","implementation","ValueBody","implementation Provider::ValueBody for Api::Value (int mode) -> void {body common \"original.csbody\";}");f.Body("Provider","original.csbody","Console.WriteLine(mode);return;");f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import Api::Value as Original (int) -> void;body common \"main.csbody\";}");f.Body("App","main.csbody","calls.Original.Invoke(1);return 0;");f.Sync();Error("BLUEPRINT_EXECUTION_PROVIDER",()=>Build());
    }
    public void test_original_exception_propagates_without_becoming_a_failure_branch() {
        string source=Function();var graph=Callee(source);Records("Provider",graph,source,new() { ["choose"]="throw new InvalidOperationException(\"original exception\");" });
        f.Add("Api","function","Value",source);f.Add("Provider","implementation","ValueBody","implementation Provider::ValueBody for Api::Value (int mode) -> void {blueprint common \"callee.graph.json\";}");f.Body("Provider","callee.graph.json",graph.ToJsonString());
        f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import Api::Value as Original (int) -> void;body common \"main.csbody\";}");f.Body("App","main.csbody","try { (("+BlueprintExecutionBranches.Interface("Api::Value")+")calls.Original).InvokeExecution(1);return 9; } catch(InvalidOperationException error) { Console.WriteLine(error.Message);return 0; }");f.Sync();Output(Build(),"original exception");
    }
    public void test_malformed_public_branch_metadata_is_a_contract_diagnostic_before_compilation() {
        var branch=new JsonObject { ["id"]=null,["name"]="Invalid",["value"]=1 };f.Add("Api","function","Value",Function(new JsonArray(branch)));
        f.Add("Provider","implementation","ValueBody","implementation Provider::ValueBody for Api::Value (int mode) -> void {body common \"original.csbody\";}");f.Body("Provider","original.csbody","return;");f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import Api::Value as Original (int) -> void;body common \"main.csbody\";}");f.Body("App","main.csbody","calls.Original.Invoke(1);return 0;");f.Sync();Error("EXECUTION_BRANCH_CONTRACT",()=>Build());
    }
    public void test_single_int_out_is_published_before_public_branch_and_continuation_without_changing_void_invoke() {
        string source=Function().Replace("int mode", "int mode,out int result", StringComparison.Ordinal),main="function App::Main () -> int {}";
        var contract=new Parser(source,"<out-contract>").ParseElement();var callee=Callee(source);callee["nodes"]![0]!["signature"]!["args"]!.AsArray().Add(new JsonObject { ["type"]="int",["name"]="result",["mode"]="out" });
        foreach(string name in new[]{"yes","no"}) {
            string id="publish_"+name;callee["nodes"]!.AsArray().Add(new JsonObject { ["id"]=id,["kind"]="export",["control"]="next",["intent"]="Publish the original int output",["output"]="result",["signature"]=Signature("void",new Parameter("int","value")),["arguments"]=new JsonObject { ["value"]=new JsonObject { ["node"]="choose",["output"]="result" } } });
            foreach(var edge in callee["edges"]!.AsArray())if(edge!["to"]!.ToString()=="exit:"+name)edge["to"]=id;
            callee["edges"]!.AsArray().Add(Edge(id,"exit:"+name));
        }
        const string original="// 원문 😀\r\nConsole.WriteLine(\"callee:\"+mode);\r\nresult=mode*10;return mode>0;\r\n";
        Records("Provider",callee,source,new() { ["choose"]=original });f.Add("Api","function","Value",source);f.Add("Provider","implementation","ValueBody","implementation Provider::ValueBody for Api::Value (int mode,out int result) -> void {blueprint common \"callee.graph.json\";}");f.Body("Provider","callee.graph.json",callee.ToJsonString());
        var caller=Graph("App::Main",main,"call");caller["nodes"]=new JsonArray(new JsonObject { ["id"]="call",["kind"]="call",["control"]="switch",["intent"]="Keep output and result separate",["feature"]="Api::Value",["signature"]=FeatureBlueprint.SignatureDocument(contract.Signature!),["arguments"]=new JsonObject { ["mode"]=new JsonObject { ["constant"]=1 } },["publicExecution"]=FeatureBlueprint.ContractHash(contract),["executionEnum"]=BlueprintExecutionBranches.Enum(contract) });
        foreach(string id in new[]{"yes","no","after"}) {var node=new JsonObject { ["id"]=id,["kind"]="code",["control"]="next",["intent"]="Read published output in "+id,["signature"]=Signature("void",new Parameter("int","value")),["arguments"]=new JsonObject { ["value"]=new JsonObject { ["node"]="call",["output"]="result" } },["implementation"]=id+".node.json" };if(id!="after")node["branchOwner"]="call";caller["nodes"]!.AsArray().Add(node);}
        caller["edges"]=new JsonArray(Edge("call","yes","case:success"),Edge("call","no","case:failure"),Edge("call","after"),Edge("after","exit:done"));caller["exits"]=new JsonObject { ["done"]=new JsonObject { ["constant"]=0 } };
        var contracts=new JsonObject { ["Api::Value"]=source };Records("App",caller,main,new() { ["yes"]="Console.WriteLine(\"success:\"+value);",["no"]="Console.WriteLine(\"failure:\"+value);",["after"]="Console.WriteLine(\"continue:\"+value);" },contracts);
        f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import Api::Value as "+FeatureBlueprint.ImportAlias("Api::Value")+" (int,out int) -> void;blueprint common \"caller.graph.json\";}");f.Body("App","caller.graph.json",caller.ToJsonString());f.Sync();byte[] before=File.ReadAllBytes(Path.Combine(f.Packs["Provider"].Root,"choose.node.json"));Output(Build(),"callee:1\nsuccess:10\ncontinue:10");
        caller["nodes"]![0]!["arguments"]!["mode"]!["constant"]=-1;f.Body("App","caller.graph.json",caller.ToJsonString());Output(Build(),"callee:-1\nfailure:-10\ncontinue:-10");
        callee["exits"]!["no"]!["executionBranch"]="none";f.Body("Provider","callee.graph.json",callee.ToJsonString());Output(Build(),"callee:-1\ncontinue:-10");
        f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import Api::Value as Original (int,out int) -> void;body common \"legacy.csbody\";}");f.Body("App","legacy.csbody","calls.Original.Invoke(3,out int value);Console.WriteLine(\"legacy:\"+value);return 0;");f.Sync();Output(Build(),"callee:3\nlegacy:30");Sequence(before,File.ReadAllBytes(Path.Combine(f.Packs["Provider"].Root,"choose.node.json")));
    }
    public void test_nonvoid_public_branch_contract_remains_rejected_without_discarding_return_data() {
        bool nonvoid=false;try{_=BlueprintExecutionBranches.Read(new Parser(Function().Replace("-> void","-> int",StringComparison.Ordinal),"<nonvoid>").ParseElement());}catch(ArgumentException){nonvoid=true;}True(nonvoid);
    }
    public void test_typed_outputs_and_aliased_refs_are_visible_before_branch_and_continuation() {
        const string parameters="(int mode,ref int x,ref int y,out long wide,out string label)";
        string source=Function().Replace("(int mode)",parameters,StringComparison.Ordinal),main="function App::Main () -> int {}";
        var contract=new Parser(source,"<data-contract>").ParseElement();var callee=Callee(source);var choose=callee["nodes"]![0]!;
        foreach(var p in contract.Signature!.Args.Skip(1))choose["signature"]!["args"]!.AsArray().Add(new JsonObject { ["type"]=p.Type,["name"]=p.Name,["mode"]=p.Mode });
        choose["arguments"]!["x"]=new JsonObject { ["input"]="x" };choose["arguments"]!["y"]=new JsonObject { ["input"]="y" };
        foreach(string name in new[]{"yes","no"}) {
            foreach(var p in contract.Signature.Args.Where(p=>p.IsOut)) {
                string id="publish_"+name+"_"+p.Name;callee["nodes"]!.AsArray().Add(new JsonObject { ["id"]=id,["kind"]="export",["control"]="next",["intent"]="Publish "+p.Name,["output"]=p.Name,["signature"]=Signature("void",new Parameter(p.Type,"value")),["arguments"]=new JsonObject { ["value"]=new JsonObject { ["node"]="choose",["output"]=p.Name } } });
                foreach(var edge in callee["edges"]!.AsArray())if(edge!["to"]!.ToString()=="exit:"+name)edge["to"]=id;
                callee["edges"]!.AsArray().Add(Edge(id,"exit:"+name));
            }
        }
        const string original="// 원문 ref/out 😀\r\nx+=mode;y+=x;wide=y*10L;label=\"value:\"+y;return mode>0;\r\n";
        Records("Provider",callee,source,new() { ["choose"]=original });f.Add("Api","function","Value",source);f.Add("Provider","implementation","ValueBody","implementation Provider::ValueBody for Api::Value "+parameters+" -> void {blueprint common \"callee.graph.json\";}");f.Body("Provider","callee.graph.json",callee.ToJsonString());
        var caller=Graph("App::Main",main,"call");caller["locals"]=new JsonArray(new JsonObject { ["id"]="counter",["name"]="counter",["type"]="int",["initial"]=new JsonObject { ["constant"]=41 } });
        caller["nodes"]=new JsonArray(new JsonObject { ["id"]="call",["kind"]="call",["control"]="switch",["intent"]="Preserve one aliased caller cell",["feature"]="Api::Value",["signature"]=FeatureBlueprint.SignatureDocument(contract.Signature),["arguments"]=new JsonObject { ["mode"]=new JsonObject { ["constant"]=1 },["x"]=new JsonObject { ["local"]="counter" },["y"]=new JsonObject { ["local"]="counter" } },["publicExecution"]=FeatureBlueprint.ContractHash(contract),["executionEnum"]=BlueprintExecutionBranches.Enum(contract) });
        foreach(string id in new[]{"yes","no","after"}) {
            var node=new JsonObject { ["id"]=id,["kind"]="code",["control"]="next",["intent"]="Read published typed data in "+id,["signature"]=Signature("void",new Parameter("long","value"),new Parameter("string","text"),new Parameter("int","cell")),["arguments"]=new JsonObject { ["value"]=new JsonObject { ["node"]="call",["output"]="wide" },["text"]=new JsonObject { ["node"]="call",["output"]="label" },["cell"]=new JsonObject { ["local"]="counter" } },["implementation"]=id+".node.json" };if(id!="after")node["branchOwner"]="call";caller["nodes"]!.AsArray().Add(node);
        }
        caller["edges"]=new JsonArray(Edge("call","yes","case:success"),Edge("call","no","case:failure"),Edge("call","after"),Edge("after","exit:done"));caller["exits"]=new JsonObject { ["done"]=new JsonObject { ["constant"]=0 } };
        var contracts=new JsonObject { ["Api::Value"]=source };var callerRecords=Records("App",caller,main,new() { ["yes"]="Console.WriteLine(\"success:\"+value+\":\"+text+\":\"+cell);",["no"]="Console.WriteLine(\"failure:\"+value+\":\"+text+\":\"+cell);",["after"]="Console.WriteLine(\"continue:\"+value+\":\"+text+\":\"+cell);" },contracts);
        var bad=caller.DeepClone().AsObject();bad["nodes"]![0]!["arguments"]!["x"]=new JsonObject { ["constant"]=41 };Equal("GRAPH_REF_STORAGE",Text(Query(main,bad,contracts,callerRecords)["diagnostics"]![0]!,"code"));
        bad=caller.DeepClone().AsObject();bad["locals"]![0]!["type"]="long";Equal("GRAPH_LOCAL_TYPE",Text(Query(main,bad,contracts,callerRecords)["diagnostics"]![0]!,"code"));
        f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import Api::Value as "+FeatureBlueprint.ImportAlias("Api::Value")+" (int,ref int,ref int,out long,out string) -> void;blueprint common \"caller.graph.json\";}");f.Body("App","caller.graph.json",caller.ToJsonString());f.Sync();byte[] before=File.ReadAllBytes(Path.Combine(f.Packs["Provider"].Root,"choose.node.json"));Output(Build(),"success:840:value:84:84\ncontinue:840:value:84:84");
        caller["nodes"]![0]!["arguments"]!["mode"]!["constant"]=-1;f.Body("App","caller.graph.json",caller.ToJsonString());Output(Build(),"failure:800:value:80:80\ncontinue:800:value:80:80");
        callee["exits"]!["no"]!["executionBranch"]="none";f.Body("Provider","callee.graph.json",callee.ToJsonString());Output(Build(),"continue:800:value:80:80");
        f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import Api::Value as Original (int,ref int,ref int,out long,out string) -> void;body common \"legacy.csbody\";}");f.Body("App","legacy.csbody","int cell=5;calls.Original.Invoke(3,ref cell,ref cell,out long wide,out string label);Console.WriteLine(cell+\":\"+wide+\":\"+label);return 0;");f.Sync();Output(Build(),"16:160:value:16");
        callee["entry"]="";callee["nodes"]=new JsonArray();callee["edges"]=new JsonArray();callee["exits"]=new JsonObject();f.Body("Provider","callee.graph.json",callee.ToJsonString());f.Body("App","legacy.csbody","int cell=7;var branch=(("+BlueprintExecutionBranches.Interface("Api::Value")+")calls.Original).InvokeExecution(3,ref cell,ref cell,out long wide,out string label);Console.WriteLine((int)branch+\":\"+cell+\":\"+wide+\":\"+(label is null));return 0;");Output(Build(),"0:7:0:True");Sequence(before,File.ReadAllBytes(Path.Combine(f.Packs["Provider"].Root,"choose.node.json")));
    }
    public void test_public_branches_refuse_opaque_unselected_target_without_a_partial_provider_contract() {
        string source=Function();var graph=Callee(source);Records("Provider",graph,source,new() { ["choose"]="return mode>0;" });
        f.Add("Api","function","Value",source);f.Add("Provider","implementation","ValueBody","implementation Provider::ValueBody for Api::Value (int mode) -> void {blueprint common \"callee.graph.json\";body linux \"original.csbody\";}");f.Body("Provider","callee.graph.json",graph.ToJsonString());f.Body("Provider","original.csbody","Console.WriteLine(mode);return;");
        f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import Api::Value as Original (int) -> void;body common \"main.csbody\";}");f.Body("App","main.csbody","calls.Original.Invoke(1);return 0;");f.Sync();byte[] original=File.ReadAllBytes(Path.Combine(f.Packs["Provider"].Root,"original.csbody"));Error("BLUEPRINT_EXECUTION_PROVIDER",()=>Build());Sequence(original,File.ReadAllBytes(Path.Combine(f.Packs["Provider"].Root,"original.csbody")));
    }
}
