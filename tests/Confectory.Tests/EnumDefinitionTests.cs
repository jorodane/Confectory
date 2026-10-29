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
}
