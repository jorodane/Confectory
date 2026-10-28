using Confectory.Core;
using System.Text.Json.Nodes;
namespace Confectory.Tests;
public sealed partial class LocalBlueprintTests : TestCase
{
    const string Feature="function Api::Value (int n,out int count) -> int {}";
    static JsonObject Local(string id,string type,JsonNode initial)=>new(){["id"]=id,["name"]="Local "+id,["type"]=type,["initial"]=new JsonObject{["constant"]=initial}};
    static JsonObject Bind(string key,string value)=>new(){[key]=value};
    static JsonObject Edge(string from,string to,string port="next")=>new(){["from"]=from,["port"]=port,["to"]=to};
    static JsonObject Set(string id,JsonNode value)=>new(){["id"]=id,["kind"]="set",["intent"]="Set counter",["control"]="next",["local"]="counter",["signature"]=FeatureBlueprint.SignatureDocument(new(new(){new("int","value")},"void")),["arguments"]=new JsonObject{["value"]=value}};
    static JsonObject Export(string id,string output,JsonNode value)=>new(){["id"]=id,["kind"]="export",["intent"]="Export "+output,["control"]="next",["output"]=output,["signature"]=FeatureBlueprint.SignatureDocument(new(new(){new("int","value")},"void")),["arguments"]=new JsonObject{["value"]=value}};
    static JsonObject Code(string id,string type,string name,string result,string control="next")=>new(){["id"]=id,["kind"]="code",["intent"]="Compute "+id,["control"]=control,["signature"]=FeatureBlueprint.SignatureDocument(new(new(){new(type,name)},result)),["arguments"]=new JsonObject(),["implementation"]=id+".node.json"};
    static JsonObject Graph()=>new(){["schema"]=1,["profile"]=FeatureBlueprint.LocalsProfile,["feature"]="Api::Value",["contractHash"]=FeatureBlueprint.ContractHash(new Parser(Feature,"<local>").ParseElement()),["entry"]="",["locals"]=new JsonArray(),["nodes"]=new JsonArray(),["edges"]=new JsonArray(),["exits"]=new JsonObject()};
    static JsonObject Query(JsonObject graph,string op="featureBlueprintDescribe",JsonObject? records=null)=>FeatureBlueprint.Execute(new JsonObject{["operation"]=op,["featureSource"]=Feature,["graph"]=graph.DeepClone(),["implementations"]=records?.DeepClone()});
    JsonObject Write(JsonObject graph,Dictionary<string,string> code)
    {
        var defs=Query(graph,"featureBlueprintNodes");Equal("node-definitions",Text(defs,"state"));var records=new JsonObject();foreach(var item in code){var node=defs["nodes"]!.AsArray().Single(n=>n!["id"]!.ToString()==item.Key)!;var record=new JsonObject{["schema"]=1,["node"]=item.Key,["definitionHash"]=node["definitionHash"]!.DeepClone(),["source"]=item.Value};records[item.Key]=record;f.Body("Provider",item.Key+".node.json",record.ToJsonString());}
        f.Add("Api","function","Value",Feature);f.Add("Provider","implementation","ValueBody","implementation Provider::ValueBody for Api::Value (int input,out int result) -> int {blueprint common \"local.graph.json\";}");f.Body("Provider","local.graph.json",graph.ToJsonString());f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import Api::Value as Value (int,out int) -> int;body common \"main.csbody\";}");f.Sync();return records;
    }
    public void test_local_set_branch_order_per_call_reset_and_per_end_out_warning()
    {
        var g=Graph();g["entry"]="choose";g["locals"]=new JsonArray(Local("counter","int",JsonValue.Create(5)!));var choose=Code("choose","int","n","bool","branch");choose["arguments"]=new JsonObject{["n"]=Bind("input","n")};g["nodes"]=new JsonArray(choose,Set("set",Bind("input","n")),Export("positive","return",Bind("local","counter")),Export("count","count",Bind("local","counter")),Export("negative","return",Bind("local","counter")));g["edges"]=new JsonArray(Edge("choose","set","true"),Edge("set","positive"),Edge("positive","count"),Edge("choose","negative","false"));var records=Write(g,new(){{"choose","return n>0;"}});var described=Query(g,records:records);Equal("source-ready",Text(described,"state"));Equal(1,described["warnings"]!.AsArray().Count);Equal("negative/next",Text(described["warnings"]![0]!,"subject"));Equal("count",Text(described["warnings"]![0]!["missingOutputs"]![0]!,"name"));f.Body("App","main.csbody","foreach(int n in new[]{2,-2,3,-3}){int value=calls.Value.Invoke(n,out int count);Console.WriteLine(value+\",\"+count);}return 0;");Output(Build(),"2,2\n5,0\n3,3\n5,0");
        var old=g.DeepClone().AsObject();old["profile"]=FeatureBlueprint.MultiOutputProfile;Equal("GRAPH_LOCALS_PROFILE",Text(Query(old)["diagnostics"]![0]!,"code"));
    }
    public void test_local_set_reads_current_storage_while_node_result_retains_snapshot()
    {
        var g=Graph();g["entry"]="first";g["locals"]=new JsonArray(Local("counter","int",JsonValue.Create(0)!));var snapshot=Code("snapshot","int","value","int");snapshot["arguments"]=new JsonObject{["value"]=Bind("local","counter")};g["nodes"]=new JsonArray(Set("first",new JsonObject{["constant"]=1}),snapshot,Set("second",new JsonObject{["constant"]=2}),Export("return","return",Bind("node","snapshot")),Export("count","count",Bind("local","counter")));g["edges"]=new JsonArray(Edge("first","snapshot"),Edge("snapshot","second"),Edge("second","return"),Edge("return","count"));Write(g,new(){{"snapshot","return value;"}});f.Body("App","main.csbody","int value=calls.Value.Invoke(0,out int count);Console.WriteLine(value+\",\"+count);return 0;");Output(Build(),"1,2");var proof=new Builder(f.Project,"portable").CheckBlueprintNode("Provider::ValueBody","common","snapshot");True(proof["compiled"]!.GetValue<bool>()&&!proof["executed"]!.GetValue<bool>());
    }
    public void test_local_array_is_shared_within_call_and_fresh_across_calls_and_invalid_locals_refuse()
    {
        var g=Graph();g["entry"]="one";g["locals"]=new JsonArray(Local("items","int[]",new JsonArray(0)),Local("unused","long",JsonValue.Create(long.MaxValue)!));var one=Code("one","int[]","items","int");var two=Code("two","int[]","items","int");one["arguments"]=new JsonObject{["items"]=Bind("local","items")};two["arguments"]=one["arguments"]!.DeepClone();g["nodes"]=new JsonArray(one,two,Export("return","return",Bind("node","two")),Export("count","count",Bind("node","one")));g["edges"]=new JsonArray(Edge("one","two"),Edge("two","return"),Edge("return","count"));Write(g,new(){{"one","return ++items[0];"},{"two","return ++items[0];"}});f.Body("App","main.csbody","for(int i=0;i<2;i++){int value=calls.Value.Invoke(0,out int count);Console.WriteLine(value+\",\"+count);}return 0;");Output(Build(),"2,1\n2,1");
        var bad=g.DeepClone().AsObject();bad["nodes"]![0]!["arguments"]!["items"]=Bind("local","missing");Equal("GRAPH_LOCAL_TYPE",Text(Query(bad)["diagnostics"]![0]!,"code"));bad=g.DeepClone().AsObject();bad["locals"]![0]!["initial"]=Bind("input","n");Equal("GRAPH_LOCAL_INITIALIZER",Text(Query(bad)["diagnostics"]![0]!,"code"));bad=g.DeepClone().AsObject();bad["locals"]![0]!["initial"]=new JsonObject{["constant"]=1};Equal("GRAPH_CONSTANT_TYPE",Text(Query(bad)["diagnostics"]![0]!,"code"));
    }
    public void test_generated_unused_local_guard_does_not_assign_to_user_underscore_parameter()
    {
        const string feature="function Api::Value (string _) -> int {}";var graph=Graph();graph["contractHash"]=FeatureBlueprint.ContractHash(new Parser(feature,"<underscore>").ParseElement());graph["locals"]=new JsonArray(Local("unused","long",JsonValue.Create(long.MaxValue)!));
        f.Add("Api","function","Value",feature);f.Add("Provider","implementation","ValueBody","implementation Provider::ValueBody for Api::Value (string original) -> int {blueprint common \"local.graph.json\";}");f.Body("Provider","local.graph.json",graph.ToJsonString());f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import Api::Value as Value (string) -> int;body common \"main.csbody\";}");f.Body("App","main.csbody","Console.WriteLine(calls.Value.Invoke(\"input\"));return 0;");f.Sync();Output(Build(),"0");
    }

}
