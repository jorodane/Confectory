using Confectory.Core;
using System.Text.Json;
using System.Text.Json.Nodes;

namespace Confectory.Tests;

public sealed class CompletionAdapterTests : TestCase
{
    static JsonObject Edge(string from,string to,string port="next")=>new(){["from"]=from,["port"]=port,["to"]=to};
    static JsonObject Code(string id,FunctionSignature signature,JsonObject args,string? owner=null)=>new(){["id"]=id,["kind"]="code",["control"]="next",["intent"]="Preserve original completion body",["signature"]=FeatureBlueprint.SignatureDocument(signature),["arguments"]=args,["implementation"]=id+".json",["branchOwner"]=owner};
    static JsonObject Query(string source,JsonObject graph,string operation,JsonObject? records=null)=>FeatureBlueprint.Execute(new(){["operation"]=operation,["featureSource"]=source,["graph"]=graph.DeepClone(),["implementations"]=records?.DeepClone()});
    void Runtime(bool native)
    {
        const string id="App::Main";string source="function "+id+" () -> int {provide App::Main with App::MainBody;value blueprintAsync = "+JsonSerializer.Serialize("{\"schema\":1,\"completion\":\"complete\"}")+";}";
        var fn=new Parser(source,"<adapter>").ParseElement();var signature=new FunctionSignature(new(){new("int","value"),new("long","audit","out")},native?"long":"void");
        var work=Code("work",signature,new(){["value"]=new JsonObject{["constant"]=4}});work.Remove("branchOwner");work["async"]=true;
        var outputArgs=new List<Parameter>{new("long","audit")};if(native)outputArgs.Add(new("long","native"));var output=new FunctionSignature(outputArgs,"void");JsonObject Args(){var values=new JsonObject{["audit"]=new JsonObject{["node"]="work",["output"]="audit"}};if(native)values["native"]=new JsonObject{["node"]="work"};return values;}
        var after=Code("after",output,Args());after.Remove("branchOwner");var complete=Code("completed",output,Args(),"work");
        var graph=new JsonObject{["schema"]=1,["profile"]=BlueprintAsync.Profile,["feature"]=id,["contractHash"]=FeatureBlueprint.ContractHash(fn),["entry"]="work",["nodes"]=new JsonArray(work,complete,after),["edges"]=new JsonArray(Edge("work","completed","completion"),Edge("completed","return:work"),Edge("work","after"),Edge("after","exit:done")),["exits"]=new JsonObject{["done"]=new JsonObject{["constant"]=0}}};
        string original="_ = Result(); audit=value*2; Console.WriteLine(\"original:\"+Caller());"+(native?"return value+1L;":"return;"),helpers="private static long Result() { return 42L; } private static string Caller([global::System.Runtime.CompilerServices.CallerMemberName] string name=\"\") { return name; }";
        if(native){original=original.Replace(";",";\r\n");helpers=helpers.Replace(";",";\r\n");}
        var records=new JsonObject{["work"]=new JsonObject{["schema"]=1,["node"]="work",["source"]=original,["helpers"]=helpers},["completed"]=new JsonObject{["schema"]=1,["node"]="completed",["source"]="Console.WriteLine(\"completed:\"+audit"+(native?"+\":\"+native":"")+");"},["after"]=new JsonObject{["schema"]=1,["node"]="after",["source"]="Console.WriteLine(\"after:\"+audit"+(native?"+\":\"+native":"")+");"}};
        JsonObject Save()
        {
            var definitions=Query(source,graph,"featureBlueprintNodes");Equal("node-definitions",Text(definitions,"state"));
            foreach(var row in records){row.Value!["definitionHash"]=definitions["nodes"]!.AsArray().Single(n=>n!["id"]!.ToString()==row.Key)!["definitionHash"]!.DeepClone();f.Body("App",row.Key+".json",row.Value.ToJsonString());}
            f.Body("App","adapter.graph.json",graph.ToJsonString());var assembled=Query(source,graph,"featureBlueprintAssemble",records);Equal("source-assembled",Text(assembled,"state"));return assembled;
        }
        f.Add("App","function","Main",source);f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {blueprint common \"adapter.graph.json\";}");
        var initial=Save();string marker=initial["sourceMap"]!.AsArray().Single(n=>n!["node"]!.ToString()=="work")!["marker"]!.ToString();f.Sync();Output(Build(),"original:Execute\ncompleted:8"+(native?":5":"")+"\nafter:8"+(native?":5":""));
        string edges=graph["edges"]!.ToJsonString(),contract=work["signature"]!.ToJsonString();BlueprintCompletionBranch.Set(work,false,"App::MainBody/body:common/node:work");var next=Save();Equal(edges,graph["edges"]!.ToJsonString());Equal(contract,work["signature"]!.ToJsonString());Equal(marker,next["sourceMap"]!.AsArray().Single(n=>n!["node"]!.ToString()=="work")!["marker"]!.ToString());f.Sync();Output(Build(),"original:Execute\nafter:8"+(native?":5":""));
        string name=work[BlueprintCompletionBranch.Metadata]!["name"]!.ToString();work[BlueprintCompletionAdapter.Metadata]!["source"]="return context."+(native?"NativeReturn == 5":"audit == 8")+" ? Result."+name+" : Result.None;";Save();f.Sync();Output(Build(),"original:Execute\ncompleted:8"+(native?":5":"")+"\nafter:8"+(native?":5":""));
        Equal(original,records["work"]!["source"]!.ToString());Equal(helpers,records["work"]!["helpers"]!.ToString());
        work[BlueprintCompletionAdapter.Metadata]!["source"]=BlueprintCompletionAdapter.DefaultSource;BlueprintCompletionBranch.Set(work,true,"App::MainBody/body:common/node:work");Save();f.Sync();Output(Build(),"original:Execute\ncompleted:8"+(native?":5":"")+"\nafter:8"+(native?":5":""));
        if(native){work[BlueprintCompletionAdapter.Metadata]!["source"]="return Result.None; } public static void Escape() {";Save();f.Sync();var error=Error("TARGET_FAILURE",()=>Build());True(error.Message.Contains("NODE_SYNTAX"));True(error.Message.Contains("completion"));}
    }
    public void test_completion_adapter_native_out_and_existing_result_helpers_keep_original_source()=>Runtime(true);
    public void test_completion_adapter_void_out_keeps_explicit_selection_and_reactivation()=>Runtime(false);
}
