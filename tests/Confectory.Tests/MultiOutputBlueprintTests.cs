using Confectory.Core;
using System.Text.Json.Nodes;

namespace Confectory.Tests;

public sealed class MultiOutputBlueprintTests : TestCase
{
    const string Feature="function Api::Value (int n,out int count,out bool ready) -> int {}";
    static FunctionSignature Sig(string result,params Parameter[] args)=>new(args.ToList(),result);
    static Parameter Input(string type,string name)=>new(type,name);
    static Parameter Out(string type,string name)=>new(type,name,"out");
    static JsonObject Value(string key,string value)=>new(){[key]=value};
    static JsonObject Result(string node,string output)=>new(){["node"]=node,["output"]=output};
    static JsonObject Edge(string from,string to,string port="next")=>new(){["from"]=from,["port"]=port,["to"]=to};
    static JsonObject Graph(string feature=Feature)=>new(){["schema"]=1,["profile"]=FeatureBlueprint.MultiOutputProfile,["feature"]="Api::Value",["contractHash"]=FeatureBlueprint.ContractHash(new Parser(feature,"<feature>").ParseElement()),["entry"]="",["nodes"]=new JsonArray(),["edges"]=new JsonArray(),["exits"]=new JsonObject()};
    static JsonObject Code(string id,FunctionSignature signature,string control="next")=>new(){["id"]=id,["kind"]="code",["intent"]="Owned "+id,["control"]=control,["signature"]=FeatureBlueprint.SignatureDocument(signature),["arguments"]=new JsonObject(signature.Args.Where(p=>!p.IsOut).Select(p=>new KeyValuePair<string,JsonNode?>(p.Name,Value("input",p.Name)))),["implementation"]=id+".node.json"};
    static JsonObject Export(string name,string type,JsonNode binding)=>new(){["id"]="publish_"+name,["kind"]="export",["control"]="next",["intent"]="Assign "+name,["output"]=name,["signature"]=FeatureBlueprint.SignatureDocument(Sig("void",Input(type,"value"))),["arguments"]=new JsonObject{["value"]=binding}};
    static JsonObject Query(JsonObject graph,string operation="featureBlueprintDescribe",string feature=Feature,JsonObject? records=null,JsonObject? contracts=null)=>FeatureBlueprint.Execute(new JsonObject{["operation"]=operation,["featureSource"]=feature,["graph"]=graph.DeepClone(),["implementations"]=records?.DeepClone(),["featureContracts"]=contracts?.DeepClone()});
    JsonObject Write(JsonObject graph,IReadOnlyDictionary<string,string> code,string feature=Feature,string imports="",JsonObject? contracts=null,string? implementationSignature=null)
    {
        var defs=Query(graph,"featureBlueprintNodes",feature,contracts:contracts);Equal("node-definitions",Text(defs,"state"));var records=new JsonObject();
        foreach(var p in code){var def=defs["nodes"]!.AsArray().Single(n=>n!["id"]!.ToString()==p.Key)!;var record=new JsonObject{["schema"]=1,["node"]=p.Key,["definitionHash"]=def["definitionHash"]!.DeepClone(),["source"]=p.Value};records[p.Key]=record.DeepClone();f.Body("Provider",p.Key+".node.json",record.ToJsonString());}
        f.Add("Api","function","Value",feature);var sig=new Parser(feature,"<feature>").ParseElement().Signature!;f.Add("Provider","implementation","ValueBody","implementation Provider::ValueBody for Api::Value "+(implementationSignature??sig.Format())+" {"+imports+"blueprint common \"multi.graph.json\";}");f.Body("Provider","multi.graph.json",graph.ToJsonString());f.Sync();return records;
    }
    void Main(string body,string signature="(int,out int,out bool) -> int")
    {f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import Api::Value as Value "+signature+";body common \"main.csbody\";}");f.Body("App","main.csbody",body);f.Sync();}
    public void test_out_contract_modes_and_legacy_hash_are_explicit_and_stable()
    {
        var plain=new Parser("function Api::Value (int n) -> int {}","<old>").ParseElement();Equal("dd2273f44a9886ae6f9c48906a3e7942c14d1674f21b867b44446919187f21e0",FeatureBlueprint.ContractHash(plain));
        var json=System.Text.Json.JsonSerializer.SerializeToNode(new Parameter("int","n"),JsonData.Options)!.AsObject();True(!json.ContainsKey("Mode")&&!json.ContainsKey("IsOut"));
        var sig=new Parser(Feature,"<out>").ParseElement().Signature!;True(sig.Args[1].IsOut);True(!sig.Matches(Sig("int",Input("int","n"),Input("int","count"),Input("bool","ready"))));Equal("(int n, out int count, out bool ready) -> int",sig.Format());
        Error("TYPE",()=>new Parser("function Api::Bad (in int n) -> void {}","<unsupported-in>").ParseElement());
        var graph=Graph();graph["profile"]=FeatureBlueprint.ImplicitProfile;Equal("GRAPH_PARAMETER_MODE_PROFILE",Text(Query(graph)["diagnostics"]![0]!,"code"));
    }
    public void test_named_outputs_warn_independently_at_each_branch_end_and_run_defaults()
    {
        var graph=Graph();graph["entry"]="choose";graph["nodes"]=new JsonArray(Code("choose",Sig("bool",Input("int","n")),"branch"),Export("return","int",Value("input","n")),Export("count","int",new JsonObject{["constant"]=7}),Export("ready","bool",new JsonObject{["constant"]=true}));graph["edges"]=new JsonArray(Edge("choose","publish_return","true"),Edge("publish_return","publish_count"),Edge("choose","publish_ready","false"));
        var records=Write(graph,new Dictionary<string,string>{{"choose","return n > 0;"}},implementationSignature:"(int original,out int originalCount,out bool originalReady) -> int");var result=Query(graph,records:records);Equal("source-ready",Text(result,"state"));Equal(2,result["warnings"]!.AsArray().Count);
        var ends=result["terminations"]!.AsArray();Sequence(new[]{"ready"},ends.Single(e=>e!["from"]!.ToString()=="publish_count")!["missingOutputs"]!.AsArray().Select(p=>p!["name"]!.ToString()));Sequence(new[]{"return","count"},ends.Single(e=>e!["from"]!.ToString()=="publish_ready")!["missingOutputs"]!.AsArray().Select(p=>p!["name"]!.ToString()));
        Main("int a=calls.Value.Invoke(2,out int c,out bool r);Console.WriteLine(a+\",\"+c+\",\"+r);a=calls.Value.Invoke(-2,out c,out r);Console.WriteLine(a+\",\"+c+\",\"+r);return 0;");Output(Build(),"2,7,False\n0,0,True");
        var wrong=graph.DeepClone().AsObject();wrong["nodes"]![2]!["arguments"]!["value"]=Value("input","count");Equal("GRAPH_INPUT_TYPE",Text(Query(wrong,records:records)["diagnostics"]![0]!,"code"));wrong["nodes"]![2]!["arguments"]!["value"]=Result("choose","missing");Equal("GRAPH_VALUE_UNAVAILABLE",Text(Query(wrong,records:records)["diagnostics"]![0]!,"code"));
        Main("return 0;","(int,int,bool) -> int");Error("CONTRACT_MISMATCH",()=>Build());
    }
    public void test_join_has_separate_must_may_and_unassigned_witness_for_each_output()
    {
        var graph=Graph();graph["entry"]="publish_return";graph["nodes"]=new JsonArray(Export("return","int",Value("input","n")),Code("choose",Sig("bool",Input("int","n")),"branch"),Export("count","int",new JsonObject{["constant"]=7}),Export("ready","bool",new JsonObject{["constant"]=true}),Code("join",Sig("void")));graph["edges"]=new JsonArray(Edge("publish_return","choose"),Edge("choose","publish_count","true"),Edge("choose","publish_ready","false"),Edge("publish_count","join"),Edge("publish_ready","join"));
        var records=Write(graph,new Dictionary<string,string>{{"choose","return n > 0;"},{"join","return;"}});var result=Query(graph,records:records);Equal(1,result["warnings"]!.AsArray().Count);var warning=result["warnings"]![0]!;Equal("join/next",Text(warning,"subject"));Sequence(new[]{"count","ready"},warning["missingOutputs"]!.AsArray().Select(p=>p!["name"]!.ToString()));True(warning["missingOutputs"]!.AsArray().All(p=>p!["assignedOnSomePaths"]!.GetValue<bool>()));
        True(warning["outputPaths"]!["count"]!.AsArray().Any(p=>p!["from"]?.ToString()=="choose"&&p["port"]?.ToString()=="false"));True(warning["outputPaths"]!["ready"]!.AsArray().Any(p=>p!["from"]?.ToString()=="choose"&&p["port"]?.ToString()=="true"));
        Main("int a=calls.Value.Invoke(2,out int c,out bool r);Console.WriteLine(a+\",\"+c+\",\"+r);a=calls.Value.Invoke(-2,out c,out r);Console.WriteLine(a+\",\"+c+\",\"+r);return 0;");Output(Build(),"2,7,False\n-2,0,True");
    }
    public void test_code_node_named_out_results_and_real_csharp_out_errors_remain_checked()
    {
        var signature=new Parser(Feature,"<feature>").ParseElement().Signature!;var graph=Graph();graph["entry"]="body";graph["nodes"]=new JsonArray(Code("body",signature),Export("return","int",Result("body","return")),Export("count","int",Result("body","count")),Export("ready","bool",Result("body","ready")));graph["edges"]=new JsonArray(Edge("body","publish_return"),Edge("publish_return","publish_count"),Edge("publish_count","publish_ready"));
        var records=Write(graph,new Dictionary<string,string>{{"body","count = n * 2; ready = n > 0; return n + 3;"}});Equal(0,Query(graph,records:records)["warnings"]!.AsArray().Count);Main("int a=calls.Value.Invoke(2,out int c,out bool r);Console.WriteLine(a+\",\"+c+\",\"+r);return 0;");Output(Build(),"5,4,True");
        var proof=new Builder(f.Project,"portable").CheckBlueprintNode("Provider::ValueBody","common","body");True(proof["compiled"]!.GetValue<bool>()&&!proof["executed"]!.GetValue<bool>());
        records["body"]!["source"]="count = n; return n;";f.Body("Provider","body.node.json",records["body"]!.ToJsonString());Error("TARGET_FAILURE",()=>Build());
    }
    public void test_empty_multiple_outs_have_typed_reference_defaults_without_cpp_or_execution()
    {
        const string feature="function Api::Value (int n,out long amount,out string text,out int[] items) -> void {}";var graph=Graph(feature);Write(graph,new Dictionary<string,string>(),feature);var described=Query(graph,feature:feature);Equal("source-ready",Text(described,"state"));Equal(3,described["warnings"]![0]!["missingOutputs"]!.AsArray().Count);
        Main("calls.Value.Invoke(2,out long amount,out string text,out int[] items);Console.WriteLine(amount+\",\"+(text is null?\"null\":text)+\",\"+(items is null?\"null\":\"wrong\"));return 0;","(int,out long,out string,out int[]) -> void");Output(Build(),"0,null,null");
    }
    public void test_typed_call_named_outputs_use_selected_object_scope_and_dominate_consumers()
    {
        const string split="function Api::Split (int source,out int amount,out bool flag) -> int {}";
        f.Add("Api","function","Split",split);
        foreach(var (name,factor) in new[]{("Double",2),("Wrong",9)}){f.Add("Provider","implementation",name,"implementation Provider::"+name+" for Api::Split (int value,out int result,out bool active) -> int {body common \""+name+".csbody\";}");f.Body("Provider",name+".csbody","result=value*"+factor+";active=value>0;return value+3;");}
        f.Add("Provider","object","Selected","object Provider::Selected {provide Api::Split with Provider::Double;}");f.Main("provide Api::Value with Provider::ValueBody;provide Api::Split with Provider::Wrong;");
        var contract=new JsonObject{["Api::Split"]=split};var sig=new Parser(split,"<split>").ParseElement().Signature!;var call=Code("split",sig);call["kind"]="call";call.AsObject().Remove("implementation");call["feature"]="Api::Split";call["contractHash"]=FeatureBlueprint.ContractHash(new Parser(split,"<split>").ParseElement());call["arguments"]=new JsonObject{["source"]=Value("input","n")};
        var graph=Graph();graph["entry"]="split";graph["nodes"]=new JsonArray(call,Export("return","int",Result("split","return")),Export("count","int",Result("split","amount")),Export("ready","bool",Result("split","flag")));graph["edges"]=new JsonArray(Edge("split","publish_return"),Edge("publish_return","publish_count"),Edge("publish_count","publish_ready"));
        string alias=FeatureBlueprint.ImportAlias("Api::Split");Write(graph,new Dictionary<string,string>(),imports:"import Api::Split as "+alias+" (int,out int,out bool) -> int in Provider::Selected;",contracts:contract);Main("int value=calls.Value.Invoke(2,out int amount,out bool flag);Console.WriteLine(value+\",\"+amount+\",\"+flag);return 0;");Output(Build(),"5,4,True");
        var wrong=graph.DeepClone().AsObject();wrong["edges"]=new JsonArray(Edge("publish_return","split"),Edge("split","publish_count"),Edge("publish_count","publish_ready"));wrong["entry"]="publish_return";Equal("GRAPH_VALUE_UNAVAILABLE",Text(Query(wrong,contracts:contract)["diagnostics"]![0]!,"code"));
        contract["Api::Split"]=split.Replace("out int amount","int amount");Equal("GRAPH_CALLEE_SIGNATURE",Text(Query(graph,contracts:contract)["diagnostics"]![0]!,"code"));
    }

    public void test_android_and_browser_metadata_templates_round_trip_out_roles_in_managed_code()
    {
        foreach(string platform in new[]{"android-export","browser-wasm"}){
            string root=Path.Combine(f.Root,"metadata-"+platform);Directory.CreateDirectory(root);
            File.Copy(Path.Combine(Fixture.Repo,"targets",platform,"templates/MetadataAuthoring.cs"),Path.Combine(root,"MetadataAuthoring.cs"));
            string reference=System.Security.SecurityElement.Escape(typeof(Parser).Assembly.Location)!;
            File.WriteAllText(Path.Combine(root,"probe.csproj"),"<Project Sdk=\"Microsoft.NET.Sdk\"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable><TreatWarningsAsErrors>true</TreatWarningsAsErrors></PropertyGroup><ItemGroup><Reference Include=\"Confectory.Core\"><HintPath>"+reference+"</HintPath></Reference></ItemGroup></Project>");
            File.WriteAllText(Path.Combine(root,"Program.cs"),""""
            using System.Text.Json.Nodes;
            using Confectory.Core;
            string source="function App::Value (int n) -> int {}";
            JsonNode contract=JsonNode.Parse("""{"args":[{"type":"int","name":"n"},{"type":"int","name":"count","mode":"out"}],"return":"int"}""")!;
            string Edit(string text,JsonObject edit)=>System.Text.Json.JsonSerializer.Deserialize<string>(MetadataAuthoring.Call("/tmp","editDeclaration",new JsonObject{["text"]=text,["edit"]=edit}.ToJsonString()))!;
            source=Edit(source,new JsonObject{["action"]="signature",["value"]=contract.DeepClone()});
            Console.WriteLine(source.Trim());if(!new Parser(source,"<embedded>").ParseElement().Signature!.Args[1].IsOut)throw new Exception("Embedded metadata dropped out mode");
            source=Edit(source,new JsonObject{["action"]="properties",["values"]=new JsonObject{["description"]="Changed description"}});if(!new Parser(source,"<embedded>").ParseElement().Signature!.Args[1].IsOut)throw new Exception("Properties lost out mode");
            string module=Edit("module App::Rules {}",new JsonObject{["action"]="module-function",["function"]="App::Value",["signature"]=contract.DeepClone()});if(!new Parser(module,"<embedded>").ParseElement().Requires["App::Value"].Signature.Args[1].IsOut)throw new Exception("Module out mode lost");
            string impl=Edit("implementation App::Body for App::Value (int n,out int count) -> int {}",new JsonObject{["action"]="relations",["role"]="import",["entries"]=new JsonArray(new JsonObject{["id"]="App::Value",["alias"]="Value",["scope"]=null,["signature"]=contract.DeepClone()})});var body=new Parser(impl,"<embedded>").ParseElement();if(!body.Signature!.Args[1].IsOut||!body.Imports["Value"].Signature.Args[1].IsOut)throw new Exception("Implementation/import out mode lost");
            contract["args"]![0]!["mode"]="ref";source=Edit(source,new JsonObject{["action"]="signature",["value"]=contract.DeepClone()});if(!new Parser(source,"<embedded-ref>").ParseElement().Signature!.Args[0].IsRef)throw new Exception("Embedded ref mode lost");
            contract["args"]![1]!["mode"]="in";bool refused=false;try{Edit(source,new JsonObject{["action"]="signature",["value"]=contract.DeepClone()});}catch(ArgumentException){refused=true;}if(!refused)throw new Exception("Unsupported in silently accepted");
            Console.WriteLine("Embedded metadata out mode PASS");
            """");
            var run=Processes.Run(new[]{Processes.DotNet(),"run","--project",Path.Combine(root,"probe.csproj"),"-c","Release"},timeoutSeconds:90);True(run.ExitCode==0,platform+": "+run.Stdout+run.Stderr);True(run.Stdout.Contains("Embedded metadata out mode PASS"),run.Stdout+run.Stderr);
        }
    }

}
