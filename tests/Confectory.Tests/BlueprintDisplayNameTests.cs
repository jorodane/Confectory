using Confectory.Core;
using System.Text.Json.Nodes;

namespace Confectory.Tests;

public sealed partial class FeatureBlueprintTests
{
    public void test_display_name_preserves_compiled_code_probe_reuse_and_never_renews_stale_bodies()
    {
        var graph=Graph();var records=Prepare(graph);
        var original=FeatureBlueprint.Execute(Request(graph,"featureBlueprintAssemble",records));
        var first=Build();Output(first,"5");
        var probe=new Builder(f.Project,"portable").CheckBlueprintNode("Provider::ValueBody","common","add");
        var node=graph["nodes"]![1]!.AsObject();Equal("add",FeatureBlueprint.DisplayName(node));
        node["displayName"]="계산 함수 · 합계";
        var named=FeatureBlueprint.Execute(Request(graph,"featureBlueprintAssemble",records));
        foreach(string field in new[]{"body","members","bodyHash","topologyHash","nodes","signature","sourceMap"})Equal(original[field]?.ToJsonString(),named[field]?.ToJsonString());
        f.Body("Provider","value.graph.json",graph.ToJsonString());
        var reused=Build();Output(reused,"5");Equal(0,Strings(reused,"statistics","compiledImplementations").Length);
        Equal(Text(first,"implementationArtifacts","Provider","key"),Text(reused,"implementationArtifacts","Provider","key"));
        True(first["blueprints"]!["Provider::ValueBody"]!["inputs"]!.ToJsonString()!=reused["blueprints"]!["Provider::ValueBody"]!["inputs"]!.ToJsonString(),"Fresh raw storage observations accompany reused semantic artifacts");
        var again=new Builder(f.Project,"portable").CheckBlueprintNode("Provider::ValueBody","common","add");Equal(Text(probe,"artifactKey"),Text(again,"artifactKey"));
        Equal(Text(probe,"assemblySha256"),Text(again,"assemblySha256"));Equal(Text(probe,"graphMap","topologyHash"),Text(again,"graphMap","topologyHash"));
        foreach(JsonNode? invalid in new JsonNode?[]{null,JsonValue.Create(" "),JsonValue.Create(" padded"),JsonValue.Create("line\nname"),JsonValue.Create(new string('n',257)),JsonValue.Create(42)}){
            node["displayName"]=invalid?.DeepClone();Refused(graph,"NODE_DISPLAY_NAME");
        }
        node["displayName"]="이름만 변경";node["intent"]="New behavior still requires body review";
        var stale=FeatureBlueprint.Execute(Request(graph,implementations:records));Equal("needs-implementation",Text(stale,"state"));Equal("stale",stale["nodes"]!.AsArray().Single(n=>Text(n!,"id")=="add")!["status"]!.ToString());
        node["displayName"]="다시 변경해도 미완성";Equal("needs-implementation",Text(FeatureBlueprint.Execute(Request(graph,implementations:records)),"state"));
        node["intent"]="Add three";node["signature"]!["args"]![0]!["name"]="displayName";
        var changedSignature=FeatureBlueprint.Execute(Request(graph,"featureBlueprintNodes"));True(changedSignature["nodes"]!.AsArray().Single(n=>Text(n!,"id")=="add")!["definitionHash"]!.ToString()!=records["add"]!["definitionHash"]!.ToString(),"A parameter named displayName is still semantic");
        node["signature"]!["args"]![0]!["name"]="value";records["add"]!["source"]="return nonexistent;";
        f.Body("Provider","value.graph.json",graph.ToJsonString());f.Body("Provider","add.node.json",records["add"]!.ToJsonString());Error("TARGET_FAILURE",()=>Build());
    }
}

public sealed partial class NestedBlueprintTests
{
    public void test_nested_display_names_preserve_parent_definition_and_leaf_compiler_evidence()
    {
        var child=Graph();child["entry"]="body";child["nodes"]=new JsonArray(Node("body",Sig("int",new Parameter("int","value")),new(){["value"]=Input("value")}));child["edges"]=new JsonArray(Edge("body","exit:done"));child["exits"]=new JsonObject{["done"]=Result("body")};
        var root=Root();root["entry"]="private";root["nodes"]=new JsonArray(Node("private",Sig("int",new Parameter("int","value")),new(){["value"]=Input("n")},child));root["edges"]=new JsonArray(Edge("private","exit:done"));root["exits"]=new JsonObject{["done"]=Result("private")};
        var records=Write(root,new(){["private/body"]="return value+3;"});var original=Query(root,operation:"featureBlueprintAssemble",records:records);var first=Build();Output(first,"5");
        var proof=new Builder(f.Project,"portable").CheckBlueprintNode("Provider::ValueBody","common","private/body");
        root["nodes"]![0]!["displayName"]="상위 함수";root["nodes"]![0]!["graph"]!["nodes"]![0]!["displayName"]="내부 계산";
        var named=Query(root,operation:"featureBlueprintAssemble",records:records);foreach(string field in new[]{"bodyHash","body","members","nodes","nestedNodes","sourceMap"})Equal(original[field]?.ToJsonString(),named[field]?.ToJsonString());
        f.Body("Provider","nested.graph.json",root.ToJsonString());var reused=Build();Output(reused,"5");Equal(0,Strings(reused,"statistics","compiledImplementations").Length);
        Equal(Text(proof,"artifactKey"),Text(new Builder(f.Project,"portable").CheckBlueprintNode("Provider::ValueBody","common","private/body"),"artifactKey"));
        root["nodes"]![0]!["graph"]!["nodes"]![0]!["intent"]="Changed inner intent";root["nodes"]![0]!["displayName"]="이름이 내부 미완성을 숨기지 않음";Equal("needs-implementation",Text(Query(root,records:records),"state"));
    }
}
