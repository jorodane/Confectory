using Confectory.Core;
using System.Text.Json;
using System.Text.Json.Nodes;

namespace Confectory.Tests;

public sealed class EnumDefinitionTests : TestCase
{
    static Element Empty() => new Parser("enum Choices::Mood {}", "<information-enum>").ParseElement();
    static JsonArray Items() => new(new JsonObject { ["id"]="stable-ready", ["name"]="준비 됨", ["icon"]="★" }, new JsonObject { ["id"]="stable-done", ["name"]="완료" });
    static void Refused(Action action) { try { action(); } catch (Exception e) when(e is BuildError or ArgumentException or InvalidOperationException) { return; } throw new Exception("Invalid information enum accepted"); }
    public void test_information_enum_ids_names_and_order_do_not_create_execution_values()
    {
        var owner=Empty(); Equal(0,EnumDefinition.Members(owner).Count); var items=Items();EnumDefinition.SetMembers(owner,items.ToJsonString());
        var reordered=EnumDefinition.Members(owner);var first=reordered[0]!.DeepClone();reordered.RemoveAt(0);reordered.Add(first);reordered[0]!["name"]="処理完了 😀";EnumDefinition.SetMembers(owner,reordered.ToJsonString());
        var saved=EnumDefinition.Members(owner);Equal("stable-done",saved[0]!["id"]!.ToString());Equal("stable-ready",saved[1]!["id"]!.ToString());True(saved.All(row=>!row!.AsObject().ContainsKey("value")));True(owner.Signature is null&&owner.Bodies.Count==0&&owner.Requires.Count==0);
        string source="enum Choices::Mood { value "+EnumDefinition.ProfileKey+" = "+JsonSerializer.Serialize(EnumDefinition.Profile)+"; value "+EnumDefinition.MembersKey+" = "+JsonSerializer.Serialize(reordered.ToJsonString())+"; }";
        Equal(reordered.ToJsonString(),EnumDefinition.Members(new Parser(source,"<roundtrip>").ParseElement()).ToJsonString());
    }
    public void test_information_enum_invalid_members_and_unknown_profiles_are_retained()
    {
        void Bad(Action<JsonArray> mutate){var items=Items();mutate(items);Refused(()=>EnumDefinition.Validate(items.ToJsonString()));}
        Bad(rows=>rows[1]!["id"]="stable-ready");Bad(rows=>rows[1]!["name"]="준비 됨");Bad(rows=>rows[1]!["name"]=" ");Bad(rows=>rows[1]!["name"]="line\nname");Bad(rows=>rows[1]!["icon"]="ab");Bad(rows=>rows[1]!["icon"]=null);Bad(rows=>rows[1]!["id"]=null);Bad(rows=>rows[1]!["value"]=1);Bad(rows=>rows[1]!["icon"]="data:image/svg+xml;base64,PHN2Zy8+");
        Refused(()=>new Parser("enum Choices::Mood extends Choices::Other {}","<invalid>").ParseElement());
        Refused(()=>new Parser("enum Choices::Mood { module Choices::Run; }","<invalid>").ParseElement());
        Refused(()=>new Parser("enum Choices::Mood { value editorEnumProfile=\"unknown\";value editorEnumValues=\"[]\"; }","<unknown>").ParseElement());
    }
    public void test_information_choice_data_is_nominal_and_never_a_clr_contract()
    {
        string Source(JsonArray members)=>"enum App::Mood {value editorEnumProfile=\"nominal-members-v1\";value editorEnumValues="+JsonSerializer.Serialize(members.ToJsonString())+";}";
        f.Add("App","enum","Mood",Source(Items()));
        f.Add("App","schema","Shape","schema App::Shape {field mood single enum App::Mood;field moods multiple enum App::Mood;}");
        f.Add("App","object","O","object App::O {use schema App::Shape;data mood=\"stable-done\";data moods=[\"stable-ready\",\"\"];}");f.Sync();
        SchemaContracts.Validate(f.Registry(),"App::O");
        var members=Items();members[1]!["name"]="新しい表示名";var done=members[1]!.DeepClone();members.RemoveAt(1);members.Insert(0,done);f.Add("App","enum","Mood",Source(members));f.Sync();
        SchemaContracts.Validate(f.Registry(),"App::O");Equal("stable-done",f.Registry().Effective("App::O").Data["mood"].Scalar!.Value.GetString());
        var descriptor=RuntimeObjectContracts.Describe(f.Registry(),"App::O");True(descriptor["fields"]!.AsArray().All(row=>!row!["supported"]!.GetValue<bool>() && row["clrType"] is null));
        members.RemoveAt(0);f.Add("App","enum","Mood",Source(members));f.Sync();Error("SCHEMA_TYPE",()=>SchemaContracts.Validate(f.Registry(),"App::O"));
    }
    public void test_information_choice_rejects_labels_ordinals_and_wrong_type_owners()
    {
        f.Add("App","enum","Mood","enum App::Mood {value editorEnumProfile=\"nominal-members-v1\";value editorEnumValues="+JsonSerializer.Serialize(Items().ToJsonString())+";}");
        f.Add("App","schema","Shape","schema App::Shape {field mood single enum App::Mood;}");
        foreach(string value in new[]{"0","\"완료\"","\"missing-id\"","null","[\"stable-done\"]"}){f.Add("App","object","O","object App::O {use schema App::Shape;data mood="+value+";}");f.Sync();if(value=="null")Refused(()=>f.Registry().Get("App::O"));else Error("SCHEMA_TYPE",()=>SchemaContracts.Validate(f.Registry(),"App::O"));}
        f.Add("App","schema","Wrong","schema App::Wrong {field mood single enum App::Shape;}");f.Sync();Error("ELEMENT_KIND",()=>SchemaContracts.Validate(f.Registry(),"App::Wrong"));
        f.Add("App","schema","Child","schema App::Child extends App::Shape {field mood multiple enum App::Mood;}");f.Sync();Error("SCHEMA_INHERITANCE",()=>f.Registry().Effective("App::Child"));
    }
}
