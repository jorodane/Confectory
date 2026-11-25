using Confectory.Core;
using System.Text.Json.Nodes;

namespace Confectory.Tests;

public sealed class BlueprintSourceBatchTests : TestCase
{
    static JsonObject Leaf(string id, string node) => new()
    {
        ["id"] = "App::Body/body:common/node:" + id,
        ["kind"] = "blueprint-node",
        ["text"] = new JsonObject { ["schema"] = 1, ["node"] = node,
            ["definitionHash"] = new string('a',64), ["source"] = "return;" }.ToJsonString()
    };

    public void test_batch_validates_every_exact_leaf_and_refuses_mixed_invalid_or_duplicate()
    {
        var first=Leaf("first","first");var second=Leaf("second","second");
        var result=BlueprintDocuments.ValidateBatch(new JsonArray(first.DeepClone(),second.DeepClone()));
        True(result["validated"]!.GetValue<int>()==2,"Every source must be validated");
        void Refused(JsonArray documents)
        {
            try { BlueprintDocuments.ValidateBatch(documents); }
            catch (ArgumentException) { return; }
            throw new Exception("Invalid source batch accepted");
        }
        Refused(new JsonArray(first.DeepClone(),Leaf("second","wrong")));
        Refused(new JsonArray(first.DeepClone(),first.DeepClone()));
        Refused(new JsonArray());
        var extra=Leaf("second","second");extra["unexpected"]=true;
        Refused(new JsonArray(first.DeepClone(),extra));
    }
}
