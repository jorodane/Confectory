using Confectory.Core;
using System.Text.Json.Nodes;
namespace Confectory.Tests;
public sealed class CodeBodyTests : TestCase
{
    JsonObject Prepare(bool methods=false)
    {
        const string feature="function Api::Value (int n) -> int {}";
        JsonObject Node(string id,string input)=>new(){["id"]=id,["kind"]="code",["control"]="next",["intent"]="Own local helper "+id,["signature"]=FeatureBlueprint.SignatureDocument(new(new(){new("int","value")},"int")),["arguments"]=new JsonObject{["value"]=new JsonObject{[id=="first"?"input":"node"]=input}},["implementation"]=id+".node.json"};
        var graph=new JsonObject{["schema"]=1,["profile"]=methods?FeatureBlueprint.MethodsProfile:FeatureBlueprint.Profile,["feature"]="Api::Value",["contractHash"]=FeatureBlueprint.ContractHash(new Parser(feature,"<local-helper>").ParseElement()),["entry"]="first",["nodes"]=new JsonArray(Node("first","n"),Node("second","first")),["edges"]=new JsonArray(new JsonObject{["from"]="first",["port"]="next",["to"]="second"},new JsonObject{["from"]="second",["port"]="next",["to"]="exit:done"}),["exits"]=new JsonObject{["done"]=new JsonObject{["node"]="second"}}};
        var definitions=FeatureBlueprint.Execute(new(){["operation"]="featureBlueprintNodes",["featureSource"]=feature,["graph"]=graph.DeepClone()});Equal("node-definitions",Text(definitions,"state"));
        var records=new JsonObject();foreach(var node in definitions["nodes"]!.AsArray()){
            string id=Text(node!,"id"),operation=id=="first"?"+3":"*2";
            var record=new JsonObject{["schema"]=1,["node"]=id,["definitionHash"]=node!["definitionHash"]!.DeepClone(),["source"]="return Helper(value);\nstatic int Helper(int candidate) => candidate"+operation+";"};if(methods){record["source"]="return Helper(value);";record["helpers"]="private static int Helper(int candidate) => candidate"+operation+";";}records[id]=record;f.Body("Provider",id+".node.json",record.ToJsonString());
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
    public void test_static_helper_members_are_per_node_and_independent_probe_never_executes()
    {
        var records=Prepare(true);var before=Build();Output(before,"10");
        string hash=before["blueprints"]!["Provider::ValueBody"]!["nodes"]![0]!["implementationHash"]!.ToString();
        records["first"]!["helpers"]="private static int Helper(int candidate) => candidate+5;";f.Body("Provider","first.node.json",records["first"]!.ToJsonString());var changed=Build();Output(changed,"14");True(hash!=changed["blueprints"]!["Provider::ValueBody"]!["nodes"]![0]!["implementationHash"]!.ToString(),"helper source belongs to the implementation receipt");
        records["first"]!["source"]="throw new Exception(\"Independent methods must not execute\");";f.Body("Provider","first.node.json",records["first"]!.ToJsonString());var proof=new Builder(f.Project,"portable").CheckBlueprintNode("Provider::ValueBody","common","first");Equal("node-compiled",Text(proof,"state"));True(!proof["executed"]!.GetValue<bool>());Equal("/helpers",Text(proof["sourceMap"]![0]!["helperRegion"]!,"jsonPointer"));
    }
    public void test_static_helpers_refuse_state_outer_escape_capture_and_reserved_names()
    {
        var records=Prepare(true);var before=Build();Output(before,"10");string latest=Path.Combine(Path.GetDirectoryName(Text(before,"output"))!,"latest.json"),prior=File.ReadAllText(latest);
        foreach(string bad in new[]{"private static int state=1; private static int Helper(int candidate)=>state;","static Other(){ }","class Shared { }","private int Helper(int candidate)=>candidate;","private static int Helper(int candidate)=>value;","private static int Helper(int candidate)=>__fg_stolen;","} class Escaped { static int x; } /*","#line 1 \"forged\"\nprivate static int Helper(int candidate)=>candidate;"}){
            records["first"]!["helpers"]=bad;f.Body("Provider","first.node.json",records["first"]!.ToJsonString());Error("TARGET_FAILURE",()=>Build());Equal(prior,File.ReadAllText(latest));
        }
    }

    public void test_static_helpers_receive_typed_imports_only_as_explicit_arguments()
    {
        var records=Prepare(true);const string value="function Api::Value (int n) -> int {}",twice="function Api::Double (int candidate) -> int {}";string alias=FeatureBlueprint.ImportAlias("Api::Double");
        var graph=JsonNode.Parse(File.ReadAllText(Path.Combine(f.Packs["Provider"].Root,"helpers.graph.json")))!.AsObject();graph["nodes"]![0]!["imports"]=new JsonArray("Api::Double");var definitions=FeatureBlueprint.Execute(new(){["operation"]="featureBlueprintNodes",["featureSource"]=value,["graph"]=graph.DeepClone(),["featureContracts"]=new JsonObject{["Api::Double"]=twice}});Equal("node-definitions",Text(definitions,"state"));
        f.Add("Api","function","Double",twice);f.Add("Provider","implementation","DoubleBody","implementation Provider::DoubleBody for Api::Double (int candidate) -> int {body common \"double.csbody\";}");f.Body("Provider","double.csbody","return candidate*2;");f.Main("provide Api::Value with Provider::ValueBody;provide Api::Double with Provider::DoubleBody;");
        f.Add("Provider","implementation","ValueBody","implementation Provider::ValueBody for Api::Value (int n) -> int {import Api::Double as "+alias+" (int) -> int;blueprint common \"helpers.graph.json\";}");
        records["first"]!["definitionHash"]=definitions["nodes"]!.AsArray().Single(n=>n!["id"]!.ToString()=="first")!["definitionHash"]!.DeepClone();records["first"]!["source"]="return Helper(value,"+alias+");";records["first"]!["helpers"]="private static int Helper(int candidate,"+Generation.Interface("Api::Double")+" imported)=>imported.Invoke(candidate)+1;";f.Body("Provider","first.node.json",records["first"]!.ToJsonString());f.Body("Provider","helpers.graph.json",graph.ToJsonString());f.Sync();Output(Build(),"10");
        var proof=new Builder(f.Project,"portable").CheckBlueprintNode("Provider::ValueBody","common","first");Equal("node-compiled",Text(proof,"state"));records["first"]!["helpers"]="private static int Helper(int candidate,"+Generation.Interface("Api::Double")+" imported)=>"+alias+".Invoke(candidate);";f.Body("Provider","first.node.json",records["first"]!.ToJsonString());Error("TARGET_FAILURE",()=>Build());
    }

    public void test_methods_profile_keeps_execute_scope_when_helpers_are_cleared_or_comment_only()
    {
        var records=Prepare(true);records["first"]!["source"]="if(value<=0)return 0;return Execute(value-1)+1;";
        foreach(string? helpers in new[]{"private static int Spare(int candidate)=>candidate;","\n// no helper methods\n","",null}){
            if(helpers is null)records["first"]!.AsObject().Remove("helpers");else records["first"]!["helpers"]=helpers;
            f.Body("Provider","first.node.json",records["first"]!.ToJsonString());Output(Build(),"4");var proof=new Builder(f.Project,"portable").CheckBlueprintNode("Provider::ValueBody","common","first");Equal("node-compiled",Text(proof,"state"));True(!proof["executed"]!.GetValue<bool>());
        }
    }

}
