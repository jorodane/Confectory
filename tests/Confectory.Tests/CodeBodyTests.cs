using Confectory.Core;
using System.Text.Json.Nodes;
namespace Confectory.Tests;
public sealed class CodeBodyTests : TestCase
{
    JsonObject Prepare()
    {
        const string feature="function Api::Value (int n) -> int {}";
        JsonObject Node(string id,string input)=>new(){["id"]=id,["kind"]="code",["control"]="next",["intent"]="Own local helper "+id,["signature"]=FeatureBlueprint.SignatureDocument(new(new(){new("int","value")},"int")),["arguments"]=new JsonObject{["value"]=new JsonObject{[id=="first"?"input":"node"]=input}},["implementation"]=id+".node.json"};
        var graph=new JsonObject{["schema"]=1,["profile"]=FeatureBlueprint.Profile,["feature"]="Api::Value",["contractHash"]=FeatureBlueprint.ContractHash(new Parser(feature,"<local-helper>").ParseElement()),["entry"]="first",["nodes"]=new JsonArray(Node("first","n"),Node("second","first")),["edges"]=new JsonArray(new JsonObject{["from"]="first",["port"]="next",["to"]="second"},new JsonObject{["from"]="second",["port"]="next",["to"]="exit:done"}),["exits"]=new JsonObject{["done"]=new JsonObject{["node"]="second"}}};
        var definitions=FeatureBlueprint.Execute(new(){["operation"]="featureBlueprintNodes",["featureSource"]=feature,["graph"]=graph.DeepClone()});Equal("node-definitions",Text(definitions,"state"));
        var records=new JsonObject();foreach(var node in definitions["nodes"]!.AsArray()){
            string id=Text(node!,"id"),operation=id=="first"?"+3":"*2";
            var record=new JsonObject{["schema"]=1,["node"]=id,["definitionHash"]=node!["definitionHash"]!.DeepClone(),["source"]="return Helper(value);\nstatic int Helper(int candidate) => candidate"+operation+";"};records[id]=record;f.Body("Provider",id+".node.json",record.ToJsonString());
        }
        f.Add("Provider","implementation","ValueBody","implementation Provider::ValueBody for Api::Value (int n) -> int {blueprint common \"helpers.graph.json\";}");f.Body("Provider","helpers.graph.json",graph.ToJsonString());f.Sync();return records;
    }
    public void test_local_helpers_are_per_node_and_independent_probe_never_executes()
    {
        var records=Prepare();Output(Build(),"10");
        records["first"]!["source"]="throw new Exception(\"Must not execute during independent compilation\");\n#pragma warning disable CS8321\nstatic int Helper(int candidate) => candidate+3;\n#pragma warning restore CS8321";f.Body("Provider","first.node.json",records["first"]!.ToJsonString());
        var proof=new Builder(f.Project,"portable").CheckBlueprintNode("Provider::ValueBody","common","first");Equal("node-compiled",Text(proof,"state"));True(!proof["executed"]!.GetValue<bool>());
    }
    public void test_body_cannot_escape_into_a_function_signature_or_outer_member()
    {
        var records=Prepare();var before=Build();Output(before,"10");string latest=Path.Combine(Path.GetDirectoryName(Text(before,"output"))!,"latest.json"),prior=File.ReadAllText(latest);
        foreach(string bad in new[]{"return value; } public static int Injected() { return 99; } /*","#line 1 \"forged\"\nreturn value;","static int Helper(int candidate) => __fg_captured;return Helper(value);"}){
            records["first"]!["source"]=bad;f.Body("Provider","first.node.json",records["first"]!.ToJsonString());Error("TARGET_FAILURE",()=>Build());Equal(prior,File.ReadAllText(latest));
        }
    }
}
