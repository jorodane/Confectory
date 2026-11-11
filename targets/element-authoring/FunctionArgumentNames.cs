using Confectory.Core;
using System.Text.Json;
using System.Text.Json.Nodes;

// Optional presentation indexed by the existing native parameter name.
// It never creates a pin identity or changes the executable signature.
internal static class FunctionArgumentNames
{
 internal const string Key="editorArgumentNames";
 public static JsonObject Read(Element function)
 {
  if(!function.Values.TryGetValue(Key,out var value))return new();
  if(value.Value.ValueKind!=JsonValueKind.String||value.Value.GetString()!.Length>65536)throw new ArgumentException("Bounded argument display metadata required");
  return Normalize(function,JsonNode.Parse(value.Value.GetString()!)!.AsObject());
 }
 static JsonObject Normalize(Element function,JsonObject names)
 {
  if(function.Kind!="function"||function.Signature is null||names.Count>64)throw new ArgumentException("Bounded function argument display names required");
  var args=function.Signature.Args;var result=new JsonObject();
  foreach(var pair in names.OrderBy(p=>p.Key,StringComparer.Ordinal)){
   if(!args.Any(a=>a.Name==pair.Key)||pair.Value is not JsonValue value||!value.TryGetValue<string>(out var label)||label.Length is <1 or >60||label!=label.Trim()||label.Any(char.IsControl))throw new ArgumentException("Display names must refer to exact current parameters and contain 1–60 trimmed characters");
   if(label!=pair.Key)result[pair.Key]=label;
  }
  foreach(var side in new[]{args.Where(a=>!a.IsOut),args.Where(a=>a.IsOut||a.IsRef)}){
   var entries=side.ToArray();
   foreach(var arg in entries.Where(a=>result.ContainsKey(a.Name)))if(entries.Any(other=>other.Name!=arg.Name&&string.Equals(result[arg.Name]!.GetValue<string>(),result[other.Name]?.GetValue<string>()??other.Name,StringComparison.OrdinalIgnoreCase)))throw new ArgumentException("Distinct argument display names required on each side");
  }
  return result;
 }
 public static void Set(Element function,JsonObject names)
 {
  var normalized=Normalize(function,names);
  if(normalized.Count==0)function.Values.Remove(Key);else function.Values[Key]=new(JsonSerializer.SerializeToElement(normalized.ToJsonString()),function.Id,new());
 }
 public static void Reconcile(Element function,JsonObject names,JsonObject? remap)
 {
  var next=new JsonObject();
  foreach(var pair in names){
   string? name=remap is null?pair.Key:remap[pair.Key]?.GetValue<string>();
   if(name is null||!function.Signature!.Args.Any(a=>a.Name==name))continue;
   if(next.ContainsKey(name))throw new ArgumentException("Explicit distinct argument display name correspondence required");
   next[name]=pair.Value!.DeepClone();
  }
  Set(function,next);
 }
}
