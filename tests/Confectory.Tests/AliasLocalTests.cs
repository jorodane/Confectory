using Confectory.Core;
using System.Text.Json.Nodes;
namespace Confectory.Tests;
public sealed class AliasLocalTests : TestCase
{
    const string Feature="function Api::Value (int n,out int snapshot) -> int {}";
    static JsonObject Sig(string result,params Parameter[] args)=>FeatureBlueprint.SignatureDocument(new(args.ToList(),result));
    static JsonObject Bind(string key,string value)=>new(){[key]=value};
    static JsonObject Result(string id,string name="return")=>new(){["node"]=id,["output"]=name};
    static JsonObject Edge(string from,string to,string port="next")=>new(){["from"]=from,["port"]=port,["to"]=to};
    static JsonObject Alias(string id,string type,JsonObject source)=>new(){["id"]=id,["name"]=id,["type"]=type,["source"]=source};
    static JsonObject Code(string id,JsonObject signature,JsonObject args)=>new(){["id"]=id,["kind"]="code",["control"]="next",["intent"]="Compute "+id,["signature"]=signature,["arguments"]=args,["implementation"]=id+".node.json"};
    static JsonObject Export(string name,JsonObject value)=>new(){["id"]="publish_"+name,["kind"]="export",["control"]="next",["intent"]="Assign "+name,["output"]=name,["signature"]=Sig("void",new Parameter("int","value")),["arguments"]=new JsonObject{["value"]=value}};
    static JsonObject Graph(string feature=Feature)=>new(){["schema"]=1,["profile"]=FeatureBlueprint.AliasLocalsProfile,["feature"]="Api::Value",["contractHash"]=FeatureBlueprint.ContractHash(new Parser(feature,"<alias>").ParseElement()),["entry"]="produce",["locals"]=new JsonArray(),["nodes"]=new JsonArray(),["edges"]=new JsonArray(),["exits"]=new JsonObject()};
    static JsonObject Query(JsonObject graph,string feature=Feature,string operation="featureBlueprintDescribe",JsonObject? records=null)=>FeatureBlueprint.Execute(new JsonObject{["operation"]=operation,["featureSource"]=feature,["graph"]=graph.DeepClone(),["implementations"]=records?.DeepClone()});
    JsonObject Write(JsonObject graph,Dictionary<string,string> bodies,string feature=Feature)
    {
        var defs=Query(graph,feature,"featureBlueprintNodes");Equal("node-definitions",Text(defs,"state"));var records=new JsonObject();foreach(var body in bodies){var row=defs["nodes"]!.AsArray().Single(n=>n!["id"]!.ToString()==body.Key)!;records[body.Key]=new JsonObject{["schema"]=1,["node"]=body.Key,["definitionHash"]=row["definitionHash"]!.DeepClone(),["source"]=body.Value};f.Body("Provider",body.Key+".node.json",records[body.Key]!.ToJsonString());}
        var signature=new Parser(feature,"<alias>").ParseElement().Signature!;f.Add("Api","function","Value",feature);f.Add("Provider","implementation","ValueBody","implementation Provider::ValueBody for Api::Value "+signature.Format()+" {blueprint common \"alias.graph.json\";}");f.Body("Provider","alias.graph.json",graph.ToJsonString());f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import Api::Value as Value "+signature.Format(false)+";body common \"main.csbody\";}");f.Sync();return records;
    }
    public void test_result_alias_ref_and_set_mutate_original_slot_while_value_argument_keeps_snapshot()
    {
        var graph=Graph();graph["locals"]=new JsonArray(Alias("borrowed","int",Result("produce")));
        var produce=Code("produce",Sig("int",new Parameter("int","n")),new(){["n"]=Bind("input","n")});
        var mutate=Code("mutate",Sig("int",new Parameter("int","a","ref"),new Parameter("int","b","ref")),new(){["a"]=Bind("local","borrowed"),["b"]=Bind("local","borrowed")});
        var capture=Code("capture",Sig("int",new Parameter("int","n")),new(){["n"]=Bind("local","borrowed")});
        var set=new JsonObject{["id"]="set",["kind"]="set",["control"]="next",["intent"]="Write the producer slot",["local"]="borrowed",["signature"]=Sig("void",new Parameter("int","value")),["arguments"]=new JsonObject{["value"]=new JsonObject{["constant"]=32}}};
        graph["nodes"]=new JsonArray(produce,mutate,capture,set,Export("return",Result("produce")),Export("snapshot",Result("capture")));graph["edges"]=new JsonArray(Edge("produce","mutate"),Edge("mutate","capture"),Edge("capture","set"),Edge("set","publish_return"),Edge("publish_return","publish_snapshot"));
        var records=Write(graph,new(){{"produce","return n+1;"},{"mutate","a=10;b+=a;return a+b;"},{"capture","return n;"}});f.Body("App","main.csbody","foreach(int n in new[]{6,1,6}){int value=calls.Value.Invoke(n,out int snapshot);Console.WriteLine(value+\",\"+snapshot);}return 0;");Output(Build(),"32,20\n32,20\n32,20");Equal(0,Query(graph,records:records)["warnings"]!.AsArray().Count);
    }
    public void test_input_alias_uses_real_caller_refs_or_distinct_parameter_slots()
    {
        const string feature="function Api::Value (ref int x,ref int y) -> int {}";var g=Graph(feature);g["entry"]="set";g["locals"]=new JsonArray(Alias("first","int",Bind("input","x")),Alias("second","int",Bind("input","y")));
        var set=new JsonObject{["id"]="set",["kind"]="set",["control"]="next",["intent"]="Assign first input slot",["local"]="first",["signature"]=Sig("void",new Parameter("int","value")),["arguments"]=new JsonObject{["value"]=new JsonObject{["constant"]=10}}};
        var inc=Code("inc",Sig("void",new Parameter("int","n","ref")),new(){["n"]=Bind("local","second")});var read=Code("read",Sig("int",new Parameter("int","a"),new Parameter("int","b")),new(){["a"]=Bind("local","first"),["b"]=Bind("local","second")});g["nodes"]=new JsonArray(set,inc,read);g["edges"]=new JsonArray(Edge("set","inc"),Edge("inc","read"),Edge("read","exit:done"));g["exits"]=new JsonObject{["done"]=Result("read")};Write(g,new(){{"inc","n+=5;"},{"read","return a+b;"}},feature);f.Body("App","main.csbody","int n=5;int value=calls.Value.Invoke(ref n,ref n);Console.WriteLine(value+\",\"+n);n=5;int other=6;value=calls.Value.Invoke(ref n,ref other);Console.WriteLine(value+\",\"+n+\",\"+other);return 0;");Output(Build(),"30,15\n21,10,11");
        const string owned="function App::Alias (ref int x,ref int y) -> int {}";var ownedGraph=g.DeepClone().AsObject();ownedGraph["feature"]="App::Alias";ownedGraph["contractHash"]=FeatureBlueprint.ContractHash(new Parser(owned,"<owned>").ParseElement());string declaration="implementation App::AliasBody for App::Alias (ref int x,ref int y) -> int {blueprint common \"owned-alias.graph.json\";}";f.Add("App","function","Alias",owned);f.Add("App","implementation","AliasBody",declaration);f.Body("App","owned-alias.graph.json",ownedGraph.ToJsonString());f.Sync();var preview=BlueprintDocuments.DescribeOwned(new JsonObject{["project"]=f.Project,["id"]="App::AliasBody",["text"]=declaration,["graph"]=ownedGraph,["definitionsOnly"]=true,["rebindContract"]=true});Equal("node-definitions",Text(preview,"state"));Equal(FeatureBlueprint.AliasLocalsProfile,preview["reboundGraph"]!["profile"]!.ToString());
    }
    public void test_array_result_alias_ref_replacement_changes_the_actual_result_variable()
    {
        var g=Graph();g["locals"]=new JsonArray(Alias("items","int[]",Result("produce")));
        var produce=Code("produce",Sig("int[]",new Parameter("int","n")),new(){["n"]=Bind("input","n")});var replace=Code("replace",Sig("int",new Parameter("int[]","a","ref"),new Parameter("int[]","b","ref")),new(){["a"]=Bind("local","items"),["b"]=Bind("local","items")});var read=Code("read",Sig("int",new Parameter("int[]","items")),new(){["items"]=Result("produce")});g["nodes"]=new JsonArray(produce,replace,read,Export("return",Result("replace")),Export("snapshot",Result("read")));g["edges"]=new JsonArray(Edge("produce","replace"),Edge("replace","read"),Edge("read","publish_return"),Edge("publish_return","publish_snapshot"));Write(g,new(){{"produce","return new[]{n};"},{"replace","a=new[]{10};b[0]+=a[0];return a[0]+b[0];"},{"read","return items[0];"}});f.Body("App","main.csbody","foreach(int n in new[]{1,2}){int value=calls.Value.Invoke(n,out int snapshot);Console.WriteLine(value+\",\"+snapshot);}return 0;");Output(Build(),"40,20\n40,20");
    }
    public void test_alias_contracts_and_all_use_paths_require_current_typed_storage()
    {
        var g=Graph();g["locals"]=new JsonArray(Alias("borrowed","int",Result("produce")));var choose=Code("choose",Sig("bool",new Parameter("int","n")),new(){["n"]=Bind("input","n")});choose["control"]="branch";var produce=Code("produce",Sig("int",new Parameter("int","n")),new(){["n"]=Bind("input","n")});var read=Code("read",Sig("int",new Parameter("int","n")),new(){["n"]=Bind("local","borrowed")});g["entry"]="choose";g["nodes"]=new JsonArray(choose,produce,read);g["edges"]=new JsonArray(Edge("choose","produce","true"),Edge("choose","read","false"),Edge("produce","read"),Edge("read","exit:done"));g["exits"]=new JsonObject{["done"]=Result("read")};var records=Write(g,new(){{"choose","return n>0;"},{"produce","return n+1;"},{"read","return n;"}});Equal("GRAPH_VALUE_UNAVAILABLE",Text(Query(g,records:records)["diagnostics"]![0]!,"code"));
        var bad=g.DeepClone().AsObject();bad["profile"]=FeatureBlueprint.ExternalRefsProfile;Equal("GRAPH_LOCAL_ALIAS_PROFILE",Text(Query(bad)["diagnostics"]![0]!,"code"));bad=g.DeepClone().AsObject();bad["locals"]![0]!["type"]="bool";Equal("GRAPH_LOCAL_ALIAS_TYPE",Text(Query(bad)["diagnostics"]![0]!,"code"));
        foreach(var source in new[]{new JsonObject{["constant"]=5},Bind("local","borrowed"),Result("missing"),Bind("input","snapshot"),Result("produce","not_declared")}){bad=g.DeepClone().AsObject();bad["locals"]![0]!["source"]=source.DeepClone();Equal("GRAPH_LOCAL_ALIAS_SOURCE",Text(Query(bad)["diagnostics"]![0]!,"code"));}
        // Setter target availability is checked before C# generation too.
        var setter=new JsonObject{["id"]="set",["kind"]="set",["control"]="next",["intent"]="Write unavailable producer",["local"]="borrowed",["signature"]=Sig("void",new Parameter("int","value")),["arguments"]=new JsonObject{["value"]=new JsonObject{["constant"]=3}}};bad=g.DeepClone().AsObject();bad["nodes"]!.AsArray().Add(setter);bad["edges"]![1]!["to"]="set";Equal("GRAPH_VALUE_UNAVAILABLE",Text(Query(bad,records:records)["diagnostics"]![0]!,"code"));
    }
    public void test_named_out_alias_mutates_node_snapshot_without_borrowing_external_caller_output()
    {
        const string feature="function Api::Value (ref int x,out int snapshot) -> int {}";var graph=Graph(feature);graph["locals"]=new JsonArray(Alias("borrowed","int",Result("produce","copied")));
        var produce=Code("produce",Sig("int",new Parameter("int","a","ref"),new Parameter("int","copied","out")),new(){["a"]=Bind("input","x")});produce["forwardCallerStorage"]=true;
        var mutate=Code("mutate",Sig("void",new Parameter("int","value","ref")),new(){["value"]=Bind("local","borrowed")});var read=Code("read",Sig("int",new Parameter("int","original"),new Parameter("int","copy")),new(){["original"]=Bind("input","x"),["copy"]=Bind("local","borrowed")});graph["nodes"]=new JsonArray(produce,mutate,read,Export("return",Result("read")));graph["edges"]=new JsonArray(Edge("produce","mutate"),Edge("mutate","read"),Edge("read","publish_return"));Write(graph,new(){{"produce","a=5;copied=a+1;return copied;"},{"mutate","value=40;"},{"read","return original*100+copy;"}},feature);
        f.Body("App","main.csbody","int n=2;int value=calls.Value.Invoke(ref n,out n);Console.WriteLine(value+\",\"+n);n=2;value=calls.Value.Invoke(ref n,out int audit);Console.WriteLine(value+\",\"+n+\",\"+audit);return 0;");Output(Build(),"640,6\n540,5,6");
    }

}
