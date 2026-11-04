using System.Text.Json.Nodes;

namespace Confectory.Core;

// A separate result selector calls the original next-body once. Its enum and
// snapshot live outside the original C# class, including user-defined Result.
public static class BlueprintCompletionAdapter
{
    public const string Metadata = "completionAdapter";
    public const string DefaultSource = "return Result.None;";
    public static JsonObject? Read(JsonObject node)
    {
        if(node[Metadata] is null)return null;
        if(node[Metadata] is not JsonObject adapter||adapter.Count!=2||adapter.Any(p=>p.Key is not ("schema" or "source"))||adapter["schema"]?.GetValue<int>()!=1||adapter["source"] is not JsonValue text||!text.TryGetValue<string>(out var source)||System.Text.Encoding.UTF8.GetByteCount(source)>262144)
            throw new ArgumentException("Exact versioned completion adapter source required");
        if(node["kind"]?.ToString()!="code"||node["control"]?.ToString()!="switch"||node["implementationContext"] is not null||node["forwardCallerStorage"]?.GetValue<bool>()==true||node["signature"]!["args"]!.AsArray().Any(p=>p!["mode"]?.ToString() is not (null or "out"))||node[BlueprintCompletionBranch.Metadata] is null)
            throw new ArgumentException("Owned original next body and value/out contract required");
        var contract=node["executionEnum"]?.AsObject()??throw new ArgumentException("Completion adapter Result contract required");
        var primary=contract["members"]!.AsArray().SingleOrDefault(p=>p!["id"]?.ToString()=="none");
        if(contract["primary"]?.ToString()!="none"||primary?["name"]?.ToString()!="None"||primary?["value"]?.GetValue<int>()!=0)throw new ArgumentException("Preserve the adapter's None result without choosing completion implicitly");
        return adapter;
    }
    public static void Attach(JsonObject node)
    {
        if(node["kind"]?.ToString()!="code"||node["control"]?.ToString()!="next"||node["executionEnum"] is not null||node["implementationContext"] is not null||node["forwardCallerStorage"]?.GetValue<bool>()==true||node["signature"]!["args"]!.AsArray().Any(p=>p!["mode"]?.ToString() is not (null or "out")))throw new ArgumentException("Output-preserving ordinary next completion adapter required");
        node[Metadata]=new JsonObject{["schema"]=1,["source"]=DefaultSource};node["control"]="switch";
        node["executionEnum"]=new JsonObject{["primary"]="none",["members"]=new JsonArray(new JsonObject{["id"]="none",["name"]="None",["value"]=0})};
    }
    public static JsonObject Context(FunctionSignature signature)
    {
        var used=new HashSet<string>(StringComparer.Ordinal){"SourceContext"};var fields=new JsonArray();
        foreach(var p in signature.Args){string member=p.Name;int suffix=2;while(!used.Add(member))member=p.Name+suffix++;fields.Add(new JsonObject{["name"]=p.Name,["member"]=member,["type"]=p.Type,["output"]=p.IsOut});}
        if(signature.Return!="void"){string member="NativeReturn";int suffix=2;while(!used.Add(member))member="NativeReturn"+suffix++;fields.Add(new JsonObject{["name"]="return",["member"]=member,["type"]=signature.Return,["output"]=true});}
        string backing="__snapshot";while(fields.Any(p=>p!["member"]!.ToString().StartsWith(backing,StringComparison.Ordinal)))backing="_"+backing;
        string declarations=string.Join("\n",fields.Select((p,i)=>"private readonly "+p!["type"]+" "+backing+i+"; public "+p["type"]+" @"+p["member"]+" => "+backing+i+";"));
        string parameters=string.Join(", ",fields.Select((p,i)=>p!["type"]+" value"+i));
        string assignments=string.Join(" ",fields.Select((p,i)=>backing+i+" = value"+i+";"));
        return new(){["fields"]=fields,["source"]="public sealed class SourceContext {\n"+declarations+"\npublic SourceContext("+parameters+") { "+assignments+" }\n}\n"};
    }
    public static string EnumSource(JsonObject node)=>"public enum Result : int {\n"+string.Join("\n",node["executionEnum"]!["members"]!.AsArray().Select(p=>"    "+p!["name"]+" = "+p["value"]+","))+"\n}\n";
    public static JsonObject Editor(JsonObject node,string source,string helpers)
    {
        var adapter=Read(node)??throw new ArgumentException("Observed completion adapter required");
        var signature=new FunctionSignature(node["signature"]!["args"]!.AsArray().Select(p=>new Parameter(p!["type"]!.GetValue<string>(),p["name"]!.GetValue<string>(),p["mode"]?.GetValue<string>())).ToList(),node["signature"]!["return"]!.GetValue<string>());
        var context=Context(signature);bool asynchronous=node["async"]?.GetValue<bool>()==true;
        string result=asynchronous?"async global::System.Threading.Tasks.Task"+(signature.Return=="void"?"":"<"+signature.Return+">"):signature.Return;
        string args=string.Join(", ",signature.Args.Where(p=>!asynchronous||!p.IsOut).Select(p=>p.Declaration()));
        string initialize=asynchronous?string.Join("\n",signature.Args.Where(p=>p.IsOut).Select(p=>p.Type+" "+p.Name+" = default!;"))+"\n":"";
        return new(){["fields"]=context["fields"]!.DeepClone(),["parts"]=new JsonArray(new JsonObject{["text"]="public static class OriginalCode {\npublic static "+result+" Execute("+args+") {\n"+initialize},new JsonObject{["id"]="body",["text"]=source},new JsonObject{["text"]="\n}\n"+helpers+"\n}\npublic static class CompletionFlow {\n"+EnumSource(node)+context["source"]+"public static Result Select(SourceContext context) {\n"},new JsonObject{["id"]="completion",["text"]=adapter["source"]!.DeepClone()},new JsonObject{["text"]="\n}\n}\n"})};
    }
}
