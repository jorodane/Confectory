using Confectory.Core;

namespace Confectory.Tests;
public sealed partial class FeatureBlueprintTests
{
 public void test_blueprint_inherited_body_retains_declaring_node_owner_without_execution()
 {
  Prepare(Graph());f.Add("Provider","implementation","InheritedValueBody","implementation Provider::InheritedValueBody for Api::Value (int n) -> int extends Provider::ValueBody {}");f.Sync();
  byte[] graph=File.ReadAllBytes(Path.Combine(f.Packs["Provider"].Root,"value.graph.json")),node=File.ReadAllBytes(Path.Combine(f.Packs["Provider"].Root,"add.node.json"));
  var check=new Builder(f.Project,"portable").Check("Provider");
  True(check["blueprints"]!["Provider::ValueBody"]!["compilerValidated"]!.GetValue<bool>());True(check["blueprints"]!["Provider::InheritedValueBody"]!["compilerValidated"]!.GetValue<bool>());True(check["run"] is null);
  Sequence(graph,File.ReadAllBytes(Path.Combine(f.Packs["Provider"].Root,"value.graph.json")));Sequence(node,File.ReadAllBytes(Path.Combine(f.Packs["Provider"].Root,"add.node.json")));
 }
 public void test_blueprint_independently_declared_body_cannot_borrow_another_node_owner()
 {
  Prepare(Graph());f.Add("Provider","implementation","BorrowedValueBody","implementation Provider::BorrowedValueBody for Api::Value (int n) -> int {blueprint common \"value.graph.json\";}");f.Sync();
  Error("BLUEPRINT_NODE_OWNERSHIP",()=>new Builder(f.Project,"portable").Check("Provider"));
 }
}
