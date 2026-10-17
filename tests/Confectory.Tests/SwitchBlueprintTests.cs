using Confectory.Core;
using System.Text.Json.Nodes;

namespace Confectory.Tests;

public sealed class SwitchBlueprintTests : TestCase
{
    const string Source="function Api::Value (int mode,int[] trace,out int audit) -> int {}";
    static JsonObject Signature(string result,params Parameter[] args)=>FeatureBlueprint.SignatureDocument(new(args.ToList(),result));
    static JsonObject Enum()=>new(){["primary"]="next",["members"]=new JsonArray(new JsonObject{["id"]="next",["name"]="Next",["value"]=-2},new JsonObject{["id"]="alternate",["name"]="Alternate",["value"]=17})};
    static JsonObject Edge(string from,string to,string port="next")=>new(){["from"]=from,["to"]=to,["port"]=port};
    static JsonObject Graph(string source=Source)=>new(){["schema"]=1,["profile"]=FeatureBlueprint.SwitchProfile,["feature"]="Api::Value",["contractHash"]=FeatureBlueprint.ContractHash(new Parser(source,"<switch>").ParseElement()),["entry"]="first",["nodes"]=new JsonArray(),["edges"]=new JsonArray(),["exits"]=new JsonObject()};
    static JsonObject Code(string id,string? owner=null,bool choose=false,bool output=false){
        var args=new List<Parameter>{new("int","mode"),new("int[]","trace")};if(output)args.Add(new("int","audit","out"));
        var n=new JsonObject{["id"]=id,["kind"]="code",["control"]=choose?"switch":"next",["intent"]="Run "+id+" once",["signature"]=Signature("void",args.ToArray()),["arguments"]=new JsonObject{["mode"]=new JsonObject{["input"]="mode"},["trace"]=new JsonObject{["input"]="trace"}},["implementation"]=id+".node.json"};
        if(choose)n["executionEnum"]=Enum();if(owner is not null)n["branchOwner"]=owner;return n;
    }
    static JsonObject Export(string output,JsonObject value,string? owner=null){var n=new JsonObject{["id"]="publish_"+output,["kind"]="export",["control"]="next",["intent"]="Publish "+output,["output"]=output,["signature"]=Signature("void",new Parameter("int","value")),["arguments"]=new JsonObject{["value"]=value}};if(owner is not null)n["branchOwner"]=owner;return n;}
    static JsonObject Query(JsonObject graph,string op="featureBlueprintDescribe",JsonObject? records=null,string source=Source)=>FeatureBlueprint.Execute(new(){["operation"]=op,["featureSource"]=source,["graph"]=graph.DeepClone(),["implementations"]=records?.DeepClone()});
    static JsonObject Standard(bool fallback=true){var g=Graph();g["nodes"]=new JsonArray(Code("first",choose:true),Code("chosen","first"),Code("fallback","first"),Code("second",choose:true,output:true),Export("audit",new(){["node"]="second",["output"]="audit"}),Export("return",new(){["constant"]=42}));g["edges"]=new JsonArray(Edge("first","second"),Edge("first","chosen","case:next"),Edge("second","publish_audit"),Edge("publish_audit","publish_return"));if(fallback)g["edges"]!.AsArray().Add(Edge("first","fallback","default"));return g;}
    JsonObject Write(JsonObject graph,Dictionary<string,string> bodies,string main,string source=Source){
        var defs=Query(graph,"featureBlueprintNodes",source:source);Equal("node-definitions",Text(defs,"state"));var records=new JsonObject();
        foreach(var pair in bodies){var d=defs["nodes"]!.AsArray().Single(n=>n!["id"]!.ToString()==pair.Key)!;var record=new JsonObject{["schema"]=1,["node"]=pair.Key,["definitionHash"]=d["definitionHash"]!.DeepClone(),["source"]=pair.Value};records[pair.Key]=record.DeepClone();f.Body("Provider",pair.Key+".node.json",record.ToJsonString());}
        var sig=new Parser(source,"<switch>").ParseElement().Signature!;f.Add("Api","function","Value",source);f.Add("Provider","implementation","ValueBody","implementation Provider::ValueBody for Api::Value "+sig.Format()+" {blueprint common \"switch.graph.json\";}");f.Body("Provider","switch.graph.json",graph.ToJsonString());f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import Api::Value as Value "+sig.Format(false)+";body common \"main.csbody\";}");f.Body("App","main.csbody",main);f.Sync();return records;
    }
    static Dictionary<string,string> Bodies()=>new(){["first"]="trace[0]++;return (Result)mode;",["chosen"]="trace[1]++;",["fallback"]="trace[2]++;",["second"]="trace[3]++;audit=trace[0]+trace[1]+trace[2]+trace[3];return Result.Next;"};
    const string Main="foreach(int mode in new[]{-2,17,99}){int[] trace=new int[6];for(int i=0;i<2;i++){int value=calls.Value.Invoke(mode,trace,out int audit);Console.WriteLine(mode+\":\"+value+\",\"+audit+\":\"+string.Join(\",\",trace));}}return 0;";
    public void test_switch_cases_default_unmatched_and_main_calls_run_once_per_invocation(){
        var graph=Standard();var records=Write(graph,Bodies(),Main);var proof=Query(graph,records:records);Equal("source-ready",Text(proof,"state"));Equal(0,proof["warnings"]!.AsArray().Count);True(proof["terminations"]!.AsArray().All(e=>e!["from"]!.ToString()=="publish_return"));True(proof["branchReturns"]!.AsArray().Any(e=>e!["from"]!.ToString()=="chosen"&&e["target"]!.ToString()=="second"));
        Output(Build(),"-2:42,3:1,1,0,1,0,0\n-2:42,6:2,2,0,2,0,0\n17:42,3:1,0,1,1,0,0\n17:42,6:2,0,2,2,0,0\n99:42,3:1,0,1,1,0,0\n99:42,6:2,0,2,2,0,0");
        var probe=new Builder(f.Project,"portable").CheckBlueprintNode("Provider::ValueBody","common","first");True(probe["compiled"]!.GetValue<bool>()&&!probe["executed"]!.GetValue<bool>());
    }
    public void test_switch_no_default_and_explicit_empty_case_continue_without_termination(){
        var graph=Standard(false);graph["edges"]!.AsArray().Add(Edge("first","return:first","case:alternate"));Write(graph,Bodies(),Main);Output(Build(),"-2:42,3:1,1,0,1,0,0\n-2:42,6:2,2,0,2,0,0\n17:42,2:1,0,0,1,0,0\n17:42,4:2,0,0,2,0,0\n99:42,2:1,0,0,1,0,0\n99:42,4:2,0,0,2,0,0");
    }
    public void test_nested_switch_returns_to_inner_then_outer_main_and_keeps_real_out_warnings(){
        var graph=Standard();graph["nodes"]!.AsArray().Add(Code("inner","first",choose:true));graph["nodes"]!.AsArray().Add(Code("leaf","inner"));graph["nodes"]!.AsArray().Add(Code("after_inner","first"));
        graph["edges"]![1]!["to"]="inner";graph["edges"]!.AsArray().Add(Edge("inner","leaf","case:next"));graph["edges"]!.AsArray().Add(Edge("inner","after_inner"));
        var bodies=Bodies();bodies["inner"]="trace[4]++;return Result.Next;";bodies["leaf"]="trace[5]++;";bodies["after_inner"]="trace[1]++;";
        var records=Write(graph,bodies,Main);var proof=Query(graph,records:records);Equal(0,proof["warnings"]!.AsArray().Count);Equal("after_inner",Text(proof["continuations"]!,"inner"));True(proof["branchReturns"]!.AsArray().Any(r=>r!["from"]!.ToString()=="leaf"&&r["target"]!.ToString()=="after_inner"));
        Output(Build(),"-2:42,3:1,1,0,1,1,1\n-2:42,6:2,2,0,2,2,2\n17:42,3:1,0,1,1,0,0\n17:42,6:2,0,2,2,0,0\n99:42,3:1,0,1,1,0,0\n99:42,6:2,0,2,2,0,0");
        var direct=graph.DeepClone().AsObject();var innerNext=direct["edges"]!.AsArray().Single(e=>e!["from"]!.ToString()=="inner"&&e["port"]!.ToString()=="next");direct["edges"]!.AsArray().Remove(innerNext);var returned=Query(direct,records:records);Equal("second",Text(returned["continuations"]!,"inner"));True(returned["branchReturns"]!.AsArray().Any(r=>r!["from"]!.ToString()=="leaf"&&r["target"]!.ToString()=="second"));Equal(0,returned["warnings"]!.AsArray().Count);
        graph["edges"]!.AsArray().Add(Edge("leaf","exit:early"));graph["exits"]!["early"]=null;var warning=Query(graph,records:records);var early=warning["terminations"]!.AsArray().Single(e=>e!["from"]!.ToString()=="leaf")!;Sequence(new[]{"return","audit"},early["missingOutputs"]!.AsArray().Select(x=>x!["name"]!.ToString()));True(warning["terminations"]!.AsArray().All(e=>e!["from"]!.ToString() is "leaf" or "publish_return"));
    }
    public void test_branch_returns_join_assignment_paths_and_never_warn_at_the_return_itself(){
        const string source="function Api::Value () -> void {}";var graph=Graph(source);var first=Code("first",choose:true);first["signature"]=Signature("void");first["arguments"]=new JsonObject();var work=Code("work","first");work["signature"]=Signature("void");work["arguments"]=new JsonObject();graph["nodes"]=new JsonArray(first,work);graph["edges"]=new JsonArray(Edge("first","work","case:next"));var result=Query(graph,source:source);Equal("needs-implementation",Text(result,"state"));True(result["terminations"]!.AsArray().All(e=>e!["from"]!.ToString()!="work"));
        var withOut=Standard();withOut["edges"]!.AsArray().RemoveAt(2);var warn=Query(withOut);True(warn["warnings"]!.AsArray().Any(w=>w!["missingOutputs"]!.AsArray().Any(x=>x!["name"]!.ToString()=="audit")));True(warn["terminations"]!.AsArray().All(e=>e!["from"]!.ToString()!="chosen"&&e["from"]!.ToString()!="fallback"));
        // Every runtime outcome, including unknown numeric values, executes default work.
        var assigned=Graph();assigned["nodes"]=new JsonArray(Code("first",choose:true),Export("audit",new(){["constant"]=7},"first"),Export("return",new(){["constant"]=9}));assigned["edges"]=new JsonArray(Edge("first","publish_return"),Edge("first","publish_audit","default"));Equal(0,Query(assigned)["warnings"]!.AsArray().Count);
        assigned["edges"]!.AsArray().Add(Edge("first","return:first","case:alternate"));True(Query(assigned)["warnings"]!.AsArray().Any(w=>w!["missingOutputs"]!.AsArray().Any(x=>x!["name"]!.ToString()=="audit")));
    }
    public void test_switch_ref_ref_out_aliases_preserve_caller_storage_through_case_and_main_return(){
        const string source="function Api::Value (ref int x,ref int y,out int audit) -> void {}";var graph=Graph(source);
        var first=new JsonObject{["id"]="first",["kind"]="code",["control"]="switch",["intent"]="Alias-visible selector",["signature"]=Signature("void",new Parameter("int","x","ref"),new Parameter("int","y","ref"),new Parameter("int","audit","out")),["arguments"]=new JsonObject{["x"]=new JsonObject{["input"]="x"},["y"]=new JsonObject{["input"]="y"}},["implementation"]="first.node.json",["executionEnum"]=Enum(),["forwardCallerStorage"]=true};
        JsonObject Increment(string id,string? owner=null){var n=new JsonObject{["id"]=id,["kind"]="code",["control"]="next",["intent"]="Increment real caller once",["signature"]=Signature("void",new Parameter("int","x","ref")),["arguments"]=new JsonObject{["x"]=new JsonObject{["input"]="x"}},["implementation"]=id+".node.json"};if(owner is not null)n["branchOwner"]=owner;return n;}
        graph["nodes"]=new JsonArray(first,Increment("work","first"),Increment("second"));graph["edges"]=new JsonArray(Edge("first","work","case:next"),Edge("first","second"));
        var records=Write(graph,new(){["first"]="x=10;y+=x;audit=x+y;return Result.Next;",["work"]="x++;",["second"]="x++;"},"for(int i=0;i<2;i++){int n=5;calls.Value.Invoke(ref n,ref n,out n);Console.WriteLine(n);}int x=5,y=6;calls.Value.Invoke(ref x,ref y,out int audit);Console.WriteLine(x+\",\"+y+\",\"+audit);return 0;",source);Equal(0,Query(graph,records:records,source:source)["warnings"]!.AsArray().Count);Output(Build(),"42\n42\n12,16,26");
    }
    public void test_legacy_bool_inside_case_returns_from_both_ports_and_does_not_repeat_main(){
        var graph=Standard(false);var decision=Code("decision","first");decision["control"]="branch";decision["signature"]!["return"]="bool";graph["nodes"]!.AsArray().Add(decision);graph["edges"]![1]!["to"]="decision";graph["edges"]!.AsArray().Add(Edge("first","decision","case:alternate"));graph["edges"]!.AsArray().Add(Edge("decision","chosen","true"));var bodies=Bodies();bodies["decision"]="trace[4]++;return mode<0;";Write(graph,bodies,Main);Output(Build(),"-2:42,3:1,1,0,1,1,0\n-2:42,6:2,2,0,2,2,0\n17:42,2:1,0,0,1,1,0\n17:42,4:2,0,0,2,2,0\n99:42,2:1,0,0,1,0,0\n99:42,4:2,0,0,2,0,0");
    }
    public void test_old_profiles_keep_their_meaning_and_refuse_switch_fields_or_cross_region_routes(){
        void Invalid(Action<JsonObject> edit,string code){var g=Standard();edit(g);var result=Query(g);Equal("invalid",Text(result,"state"));Equal(code,Text(result["diagnostics"]![0]!,"code"));}
        Invalid(g=>g["profile"]=FeatureBlueprint.MethodsProfile,"GRAPH_CONTROL");Invalid(g=>g["entry"]="chosen","GRAPH_BRANCH_ENTRY");Invalid(g=>g["entry"]="return:first","GRAPH_BRANCH_ENTRY");Invalid(g=>g["nodes"]![0]!["branchOwner"]="first","GRAPH_BRANCH_OWNER");Invalid(g=>g["edges"]![1]!["to"]="second","GRAPH_BRANCH_SCOPE");Invalid(g=>g["edges"]!.AsArray().Add(Edge("chosen","second")),"GRAPH_BRANCH_SCOPE");Invalid(g=>g["edges"]!.AsArray().Add(Edge("chosen","return:second")),"GRAPH_BRANCH_RETURN");Invalid(g=>g["nodes"]![0]!["signature"]!["return"]="int","GRAPH_SWITCH_CONTRACT");Invalid(g=>g["nodes"]![0]!["executionEnum"]!["members"]![1]!["value"]=-2,"GRAPH_SHAPE");
    }
}
