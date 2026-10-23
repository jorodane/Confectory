using Confectory.Core;
using System.Text.Json.Nodes;
namespace Confectory.Tests;
public sealed partial class LocalBlueprintTests
{
    static JsonObject SnapshotSet(string id,string target,string output,string type,JsonNode value)
        => new(){["id"]=id,["kind"]="set",["intent"]="Store then expose "+id,["control"]="next",["local"]=target,["outputLocal"]=output,["signature"]=FeatureBlueprint.SignatureDocument(new(new(){new(type,"value")},"void")),["arguments"]=new JsonObject{["value"]=value}};
    static JsonObject Stored(string id)=>new(){["node"]=id,["output"]="stored"};
    public void test_local_set_distinct_snapshot_survives_later_target_write_and_resets_each_call()
    {
        var g=Graph();g["entry"]="first";g["locals"]=new JsonArray(Local("counter","int",JsonValue.Create(0)!),Local("firstValue","int",JsonValue.Create(0)!),Local("secondValue","int",JsonValue.Create(0)!));
        g["nodes"]=new JsonArray(SnapshotSet("first","counter","firstValue","int",Bind("input","n")),SnapshotSet("second","counter","secondValue","int",new JsonObject{["constant"]=9}),Export("result","return",Stored("first")),Export("current","count",Bind("local","counter")));
        g["edges"]=new JsonArray(Edge("first","second"),Edge("second","result"),Edge("result","current"));
        var definitions=Query(g,"featureBlueprintNodes");var first=definitions["nodes"]!.AsArray().Single(n=>n!["id"]!.ToString()=="first")!;
        Equal("stored",first["outputs"]![0]!["name"]!.ToString());Equal("firstValue",first["definition"]!["outputLocal"]!.ToString());Equal("void",first["definition"]!["signature"]!["return"]!.ToString());
        Write(g,new());f.Body("App","main.csbody","foreach(int n in new[]{1,2}){int before=calls.Value.Invoke(n,out int current);Console.WriteLine(before+\",\"+current);}return 0;");Output(Build(),"1,9\n2,9");
        var legacy=g.DeepClone().AsObject();legacy["nodes"]![0]!.AsObject().Remove("outputLocal");legacy["nodes"]![2]!["arguments"]!["value"]=Bind("local","counter");var old=Query(legacy,"featureBlueprintNodes");Equal(0,old["nodes"]!.AsArray().Single(n=>n!["id"]!.ToString()=="first")!["outputs"]!.AsArray().Count);
        var unavailable=g.DeepClone().AsObject();unavailable["entry"]="result";Equal("GRAPH_VALUE_UNAVAILABLE",Query(unavailable)["diagnostics"]![0]!["code"]!.ToString());
    }
    public void test_local_set_snapshot_rejects_missing_wrong_type_alias_and_non_set_output_contracts()
    {
        var g=Graph();g["entry"]="write";g["locals"]=new JsonArray(Local("counter","int",JsonValue.Create(0)!),Local("snapshot","int",JsonValue.Create(0)!));g["nodes"]=new JsonArray(SnapshotSet("write","counter","snapshot","int",new JsonObject{["constant"]=1}));
        Equal("source-ready",Query(g)["state"]!.ToString());
        var missing=g.DeepClone().AsObject();missing["nodes"]![0]!["outputLocal"]="missing";Equal("GRAPH_SET_OUTPUT_CONTRACT",Query(missing)["diagnostics"]![0]!["code"]!.ToString());
        var wrong=g.DeepClone().AsObject();wrong["locals"]![1]!["type"]="string";wrong["locals"]![1]!["initial"]!["constant"]="wrong";Equal("GRAPH_SET_OUTPUT_CONTRACT",Query(wrong)["diagnostics"]![0]!["code"]!.ToString());
        var alias=g.DeepClone().AsObject();alias["profile"]=FeatureBlueprint.AliasLocalsProfile;alias["locals"]![1]!.AsObject().Remove("initial");alias["locals"]![1]!["source"]=Bind("input","n");Equal("GRAPH_SET_OUTPUT_CONTRACT",Query(alias)["diagnostics"]![0]!["code"]!.ToString());
        var duplicate=g.DeepClone().AsObject();var repeated=duplicate["nodes"]![0]!.DeepClone();repeated["id"]="other";duplicate["nodes"]!.AsArray().Add(repeated);Equal("GRAPH_SET_OUTPUT_OWNER",Query(duplicate)["diagnostics"]![0]!["code"]!.ToString());
        var other=g.DeepClone().AsObject();var export=Export("export","return",new JsonObject{["constant"]=1});export["outputLocal"]="snapshot";other["nodes"]!.AsArray().Add(export);Equal("GRAPH_SET_OUTPUT_KIND",Query(other)["diagnostics"]![0]!["code"]!.ToString());
    }
    public void test_local_set_snapshot_preserves_array_identity_without_deep_copy()
    {
        var g=Graph();g["entry"]="first";g["locals"]=new JsonArray(Local("items","int[]",new JsonArray()),Local("savedItems","int[]",new JsonArray()),Local("laterItems","int[]",new JsonArray()));
        var mutate=Code("mutate","int[]","value","int");mutate["arguments"]=new JsonObject{["value"]=Stored("first")};var read=Code("read","int[]","value","int");read["arguments"]=new JsonObject{["value"]=Bind("local","items")};
        g["nodes"]=new JsonArray(SnapshotSet("first","items","savedItems","int[]",new JsonObject{["constant"]=new JsonArray(1)}),SnapshotSet("second","items","laterItems","int[]",new JsonObject{["constant"]=new JsonArray(9)}),mutate,read,Export("current","return",Bind("node","read")),Export("stored","count",Bind("node","mutate")));
        g["edges"]=new JsonArray(Edge("first","second"),Edge("second","mutate"),Edge("mutate","read"),Edge("read","current"),Edge("current","stored"));Write(g,new(){{"mutate","value[0]=23;return value[0];"},{"read","return value[0];"}});f.Body("App","main.csbody","int current=calls.Value.Invoke(0,out int stored);Console.WriteLine(current+\",\"+stored);return 0;");Output(Build(),"9,23");
    }
}
