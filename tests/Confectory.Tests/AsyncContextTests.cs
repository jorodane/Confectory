using Confectory.Core;
using System.Text.Json.Nodes;

namespace Confectory.Tests;

public sealed class AsyncContextTests : TestCase
{
    static string Async(string id,string signature,string declaration="")=>"function "+id+" "+signature+" { "+declaration+"value blueprintAsync = \"{\\\"schema\\\":1,\\\"completion\\\":\\\"complete\\\"}\"; }";
    static JsonObject Signature(FunctionSignature signature)=>FeatureBlueprint.SignatureDocument(signature);
    static JsonObject Graph(string text,string entry)=>new(){["schema"]=1,["profile"]=BlueprintAsync.Profile,["feature"]=new Parser(text,"<feature>").ParseElement().Id,["contractHash"]=FeatureBlueprint.ContractHash(new Parser(text,"<feature>").ParseElement()),["entry"]=entry,["nodes"]=new JsonArray(),["edges"]=new JsonArray(),["exits"]=new JsonObject()};
    JsonObject Write(string pack,string text,JsonObject graph,JsonObject context,JsonObject records,JsonObject contracts)
    {
        var definitions=FeatureBlueprint.Execute(new(){["operation"]="featureBlueprintNodes",["featureSource"]=text,["graph"]=graph.DeepClone(),["implementationContext"]=context.DeepClone(),["featureContracts"]=contracts.DeepClone()});Equal("node-definitions",Text(definitions,"state"));
        foreach(var pair in records){pair.Value!["definitionHash"]=definitions["nodes"]!.AsArray().Single(n=>n!["id"]!.ToString()==pair.Key)!["definitionHash"]!.DeepClone();f.Body(pack,pair.Key+".node.json",pair.Value.ToJsonString());}
        f.Body(pack,"async.graph.json",graph.ToJsonString());return definitions;
    }
    void Runtime(bool native)
    {
        string result=native?"long":"void",signature="(object state,long amount,out long count) -> "+result;
        string source=Async("Api::Value",signature),main=Async("App::Main","() -> int","provide App::Main with App::MainBody;provide Api::Value with Provider::ValueBody;");
        const string imported="function Api::Double (long input) -> long {}";
        string implementation="implementation Provider::ValueBody for Api::Value (object marker,long input,out long copied) -> "+result+" {import Api::Double as Scoped (long) -> long in Provider::ChosenScope;blueprint common \"async.graph.json\";}";
        var e=new Parser(implementation,"<implementation>").ParseElement();var context=FeatureBlueprint.ImplementationContext(e);
        string body="// 원문 😀\r\n"+(native?"if(input<0)return this.Invoke(marker,-input,out copied);":"if(input<0){this.Invoke(marker,-input,out copied);return;}")+"\r\nIImports same=this.calls;\r\nstring Member([global::System.Runtime.CompilerServices.CallerMemberName] string name=\"\")=>name;\r\nstring File([global::System.Runtime.CompilerServices.CallerFilePath] string name=\"\")=>global::System.IO.Path.GetFileName(name);\r\nstring literal=@\"a\r\nb\";\r\nif(GetType()!=typeof(IImports).DeclaringType||Member()!=\"Invoke\"||File()!=\"whole original.csbody\"||!literal.Contains(\"\\r\\n\"))throw new Exception(\"original context changed\");\r\ncopied=input*10;\r\n((global::System.Collections.Generic.List<long>)marker).Add(same.Scoped.Invoke(input));\r\n"+(native?"return same.Scoped.Invoke(input);":"return;");
        f.Add("Api","function","Value",source);f.Add("Api","function","Double",imported);f.Add("Provider","implementation","DoubleBody","implementation Provider::DoubleBody for Api::Double (long input) -> long {body common \"double.csbody\";}");f.Body("Provider","double.csbody","return input+3;");f.Add("Provider","object","ChosenScope","object Provider::ChosenScope {provide Api::Double with Provider::DoubleBody;}");f.Add("Provider","implementation","ValueBody",implementation);f.Body("Provider","whole original.csbody",body);
        string path=Path.Combine(f.Packs["Provider"].Root,"whole original.csbody");byte[] original=File.ReadAllBytes(path);body=File.ReadAllText(path);
        var graph=Graph(source,"calculate");graph["nodes"]!.AsArray().Add(new JsonObject{["id"]="calculate",["kind"]="code",["control"]="next",["intent"]="Keep original native Invoke",["signature"]=Signature(e.Signature!),["arguments"]=new JsonObject{["marker"]=new JsonObject{["input"]="state"},["input"]=new JsonObject{["input"]="amount"}},["implementation"]="calculate.node.json",["implementationContext"]=context.DeepClone(),["sourceIdentity"]=path});
        if(native){graph["nodes"]!.AsArray().Add(new JsonObject{["id"]="publish",["kind"]="export",["control"]="next",["intent"]="Keep native return",["output"]="return",["signature"]=Signature(new(new(){new("long","value")},"void")),["arguments"]=new JsonObject{["value"]=new JsonObject{["node"]="calculate"}}});graph["edges"]!.AsArray().Add(new JsonObject{["from"]="calculate",["port"]="next",["to"]="publish"});}
        var records=new JsonObject{["calculate"]=new JsonObject{["schema"]=1,["node"]="calculate",["source"]=body}};Write("Provider",source,graph,context,records,new(){["Api::Double"]=imported});
        string alias=FeatureBlueprint.ImportAlias("Api::Value");var caller=Graph(main,"work");caller["nodes"]!.AsArray().Add(new JsonObject{["id"]="work",["kind"]="code",["control"]="next",["async"]=true,["intent"]="Explicit Task caller",["signature"]=Signature(new(new(),"int")),["arguments"]=new JsonObject(),["imports"]=new JsonArray("Api::Value"),["implementation"]="work.node.json"});caller["edges"]!.AsArray().Add(new JsonObject{["from"]="work",["port"]="next",["to"]="exit:done"});caller["exits"]!["done"]=new JsonObject{["node"]="work"};
        var fn=new Parser(source,"<contract>").ParseElement();string code="var seen=new global::System.Collections.Generic.List<long>();var value=await "+alias+".InvokeAsync(seen,-2);Console.WriteLine("+(native?"value."+BlueprintAsync.ReturnName(fn.Signature!)+"+\",\"+":"")+"value.count+\",\"+seen[0]+\",\"+seen.Count);return 0;";
        Write("App",main,caller,new(),new(){["work"]=new JsonObject{["schema"]=1,["node"]="work",["source"]=code}},new(){["Api::Value"]=source});f.Add("App","function","Main",main);f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import Api::Value as "+alias+" (object,long,out long) -> "+result+";blueprint common \"async.graph.json\";}");f.Sync();Output(Build(),native?"5,20,5,1":"20,5,1");Sequence(original,File.ReadAllBytes(path));Equal(body,records["calculate"]!["source"]!.ToString());
    }
    public void test_async_root_preserves_native_context_this_recursion_scope_out_and_source()=>Runtime(true);
    public void test_async_root_preserves_void_native_context_and_out_without_source_rewrite()=>Runtime(false);
}
