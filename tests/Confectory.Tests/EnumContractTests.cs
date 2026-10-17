using Confectory.Core;
using System.Text.Json.Nodes;

namespace Confectory.Tests;

public sealed class EnumContractTests : TestCase
{
    static JsonObject Binding() => new() { ["sourceId"]="Provider::Body/body:common/node:body", ["definitionHash"]=new string('a',64), ["sourceHash"]=new string('b',64), ["primary"]="next" };
    static JsonObject Contract() => new() { ["schema"]=1, ["kind"]="execution-enum-proposal", ["sourceId"]=Binding()["sourceId"]!.DeepClone(), ["definitionHash"]=new string('a',64), ["sourceHash"]=new string('b',64), ["primary"]="next", ["members"]=new JsonArray(new JsonObject{["id"]="next",["name"]="진행",["value"]=int.MinValue},new JsonObject{["id"]="port_stable",["name"]="@class",["value"]=int.MaxValue}) };
    static void Refused(Action action) { try { action(); } catch(ArgumentException) { return; } throw new Exception("Invalid enum authoring contract was accepted"); }
    public void test_enum_explicit_ids_values_order_and_source_binding_are_independent_of_runtime()
    {
        var contract=Contract();string original=contract.ToJsonString();var before=BlueprintEnumContract.Preview(contract,Binding());Equal(original,contract.ToJsonString());True(!before["executionEnabled"]!.GetValue<bool>()&&!before["sourceWritten"]!.GetValue<bool>()&&!before["compiled"]!.GetValue<bool>()&&!before["executed"]!.GetValue<bool>());Equal("sequential-switch-continuation",Text(before,"runtimePolicy"));
        var rows=contract["members"]!.AsArray();var first=rows[0]!.DeepClone();rows.RemoveAt(0);rows.Add(first);var reordered=BlueprintEnumContract.Preview(contract,Binding());Equal(Text(before,"contractHash"),Text(reordered,"contractHash"));True(Text(before,"declarationHash")!=Text(reordered,"declarationHash"));
        rows[0]!["name"]="Completed";rows[0]!["value"]=17;var renamed=BlueprintEnumContract.Preview(contract,Binding());Equal("port_stable",Text(renamed["contract"]!["members"]![0]!,"id"));Equal("next",Text(renamed["contract"]!["members"]![1]!,"id"));True(Text(renamed,"declaration").Contains("Completed = 17, // port: port_stable"));
        var stale=Binding();stale["sourceHash"]=new string('c',64);Refused(()=>BlueprintEnumContract.Preview(contract,stale));stale=Binding();stale["definitionHash"]=new string('d',64);Refused(()=>BlueprintEnumContract.Preview(contract,stale));stale=Binding();stale["primary"]="port_stable";Refused(()=>BlueprintEnumContract.Preview(contract,stale));
    }
    public void test_enum_refuses_duplicates_range_coercion_identity_loss_and_runtime_policy_fields()
    {
        void Bad(Action<JsonObject> mutate){var c=Contract();mutate(c);Refused(()=>BlueprintEnumContract.Preview(c,Binding()));}
        Bad(c=>c["members"]![1]!["id"]="next");Bad(c=>c["members"]![1]!["name"]="進行}");Bad(c=>c["members"]![1]!["name"]="進行\nclass Evil{}");Bad(c=>c["members"]![1]!["name"]="Result");Bad(c=>c["members"]![1]!["name"]="value__");Bad(c=>c["members"]![1]!["name"]="class");
        Bad(c=>{c["members"]![0]!["name"]="A";c["members"]![1]!["name"]="@A";});Bad(c=>c["members"]![1]!["value"]=int.MinValue);Bad(c=>c["members"]![1]!["value"]=2147483648L);Bad(c=>c["members"]![1]!["value"]=-2147483649L);Bad(c=>c["members"]![1]!["value"]=1.5);Bad(c=>c["members"]![1]!["value"]="17");Bad(c=>c["members"]!.AsArray().RemoveAt(0));Bad(c=>c["undefinedValuePolicy"]="terminate");Bad(c=>c["overflow"]="wrap");
        Bad(c=>{for(int n=2;n<33;n++)c["members"]!.AsArray().Add(new JsonObject{["id"]="p"+n,["name"]="P"+n,["value"]=n});});
    }
    public void test_enum_declaration_is_real_csharp_compile_only_and_cannot_create_an_enum_dispatcher()
    {
        f.Sync();var preview=BlueprintEnumContract.Preview(Contract(),Binding());string source=Path.Combine(f.Root,"enum-declaration.cs");File.WriteAllText(source,Text(preview,"declaration"));var builder=new Builder(f.Project,"portable");var artifact=builder.Tool.Invoke("compile-contract",new{output=Path.Combine(f.Root,"enum-artifact"),name="EnumProposal",sources=new[]{source},references=Array.Empty<string>()});True(File.Exists(artifact["artifacts"]!["assembly"]!.ToString()),artifact.ToJsonString());
        True(!File.ReadAllText(source).Contains("Execute("));True(!File.ReadAllText(source).Contains("switch"));
        var graph=new JsonObject{["schema"]=1,["profile"]="sync-acyclic-enum-v1",["feature"]="Api::Value",["contractHash"]=FeatureBlueprint.ContractHash(new Parser("function Api::Value () -> int {}","<enum>").ParseElement()),["entry"]="",["nodes"]=new JsonArray(),["edges"]=new JsonArray(),["exits"]=new JsonObject()};var result=FeatureBlueprint.Execute(new(){["operation"]="featureBlueprintAssemble",["featureSource"]="function Api::Value () -> int {}",["graph"]=graph});Equal("invalid",Text(result,"state"));Equal("GRAPH_PROFILE_UNSUPPORTED",Text(result["diagnostics"]![0]!,"code"));
    }
}
