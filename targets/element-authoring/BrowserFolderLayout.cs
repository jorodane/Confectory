using Confectory.Core;
using System.Text.Json;
using System.Text.Json.Nodes;

// Browser classification metadata is distinct from language inheritance and typed contain/use edges.
internal static class BrowserFolderLayout
{
 internal static string Group(Element element) => element.Kind switch {
  "function" or "implementation" => "feature", "schema" => "info", "module" => "module",
  "category" when element.Values.TryGetValue("editorBrowserGroup",out var group) => group.Value.ValueKind==JsonValueKind.String && group.Value.GetString() is ("concept" or "info" or "feature" or "module") ? group.Value.GetString()! : throw new ArgumentException("Invalid Browser category group"),
  _ => "concept"
 };
 internal static (bool Defined,string? Id) Folder(Element element) {
  if(!element.Values.TryGetValue("editorFolder",out var value))return (false,null);
  if(value.Value.ValueKind!=JsonValueKind.String)throw new ArgumentException("Browser folder must be a string identity or empty Root");
  string id=value.Value.GetString()!;return (true,id.Length==0?null:id);
 }
 public static JsonObject Execute(JsonObject request,Func<Element,string> format,bool validateOnly) {
  string ns=request["namespace"]!.GetValue<string>();var rows=request["units"]!.AsArray();if(rows.Count is <1 or >256)throw new ArgumentException("Browser folder graph budget");
  var elements=new Dictionary<string,Element>(StringComparer.Ordinal);var proofs=new Dictionary<string,JsonNode>(StringComparer.Ordinal);
  foreach(var row in rows){string id=row!["id"]!.GetValue<string>();var element=new Parser(row["text"]!.GetValue<string>(),"<browser-classification>").ParseElement();if(!id.StartsWith(ns+"::",StringComparison.Ordinal)||element.Id!=id||element.Kind!=row["kind"]!.ToString()||element.Kind is not ("object" or "concept" or "category" or "schema" or "function" or "module" or "implementation")||!elements.TryAdd(id,element))throw new ArgumentException("Owned Browser classification identity required");proofs.Add(id,row);}
  void Validate(){foreach(var element in elements.Values){string? folder=Folder(element).Id;var seen=new HashSet<string>(StringComparer.Ordinal){element.Id};while(folder is not null){if(!seen.Add(folder))throw new ArgumentException("Browser category cycle");if(!elements.TryGetValue(folder,out var target)||target.Kind!="category"||Group(target)!=Group(element))throw new ArgumentException("Browser folder must be an owned category in the same tab");folder=Folder(target).Id;}}foreach(var element in elements.Values){string? Parent(string id){var row=elements[id];string? folder=Effective(id);return Folder(row).Defined?folder:row.Parent is string parent&&elements.ContainsKey(parent)&&Group(elements[parent])==Group(row)&&Effective(parent)==folder?parent:folder;}var seen=new HashSet<string>(StringComparer.Ordinal){element.Id};string? at=Parent(element.Id);while(at is not null){if(!elements.ContainsKey(at)||!seen.Add(at))throw new ArgumentException("Browser classification hierarchy cycle");at=Parent(at);}}}
  Validate();if(validateOnly)return new JsonObject{["valid"]=true};
  var moves=request["moves"]!.AsArray();if(moves.Count is <1 or >32)throw new ArgumentException("Explicit Browser folder moves required");
  var selected=new HashSet<string>(StringComparer.Ordinal);var dependencies=new HashSet<string>(StringComparer.Ordinal);var queue=new Queue<string>();
  void Depend(string? id){if(id is not null&&elements.ContainsKey(id)&&dependencies.Add(id))queue.Enqueue(id);}
  string? Effective(string id,HashSet<string>? seen=null){if(!elements.TryGetValue(id,out var element))return null;seen??=new(StringComparer.Ordinal);if(!seen.Add(id))throw new ArgumentException("Inherited Browser classification cycle");var folder=Folder(element);return folder.Defined?folder.Id:element.Parent is string parent&&elements.TryGetValue(parent,out var owner)&&Group(owner)==Group(element)?Effective(parent,seen):null;}
  void Expand(){while(queue.Count>0){if(dependencies.Count>32)throw new ArgumentException("Browser folder dependency group budget");var element=elements[queue.Dequeue()];Depend(Folder(element).Id);}}
  foreach(var value in moves){var move=value!.AsObject();if(move.Count!=6||move.Any(row=>row.Key is not ("id" or "folder" or "revision" or "hash" or "folderRevision" or "folderHash"))||!move.ContainsKey("folder"))throw new ArgumentException("Displayed source and category proof required");string id=move["id"]!.GetValue<string>();if(!selected.Add(id)||!elements.TryGetValue(id,out var element))throw new ArgumentException("Unique owned Browser source required");var proof=proofs[id];if(move["revision"]!.GetValue<long>()!=proof["revision"]!.GetValue<long>()||move["hash"]!.ToString()!=proof["hash"]!.ToString())throw new InvalidOperationException("Browser source changed; input retained");string? folder=move["folder"]?.GetValue<string>();if(folder is not null){if(!elements.TryGetValue(folder,out var target)||target.Kind!="category"||Group(element)!=Group(target)||move["folderRevision"]?.GetValue<long>()!=proofs[folder]["revision"]!.GetValue<long>()||move["folderHash"]?.ToString()!=proofs[folder]["hash"]!.ToString())throw new InvalidOperationException("Browser category changed; input retained");}else if(move["folderRevision"] is not null||move["folderHash"] is not null)throw new ArgumentException("Root has no category proof");Depend(id);Depend(Effective(id));Depend(folder);}
  Expand(); // Include the previous location as well as the new one, including inherited classification.
  var changed=new JsonArray();foreach(var value in moves){string id=value!["id"]!.GetValue<string>();var element=elements[id];string folder=value["folder"]?.GetValue<string>()??"";var prior=Folder(element);if(prior.Defined&&prior.Id==(folder.Length==0?null:folder))continue;if(!prior.Defined&&Effective(id) is null&&folder.Length==0)continue;element.Values["editorFolder"]=new(JsonSerializer.SerializeToElement(folder),element.Id,new());changed.Add(new JsonObject{["id"]=id,["text"]=format(element)});}
  Validate();foreach(string id in selected){Depend(Folder(elements[id]).Id);}Expand();
  return new JsonObject{["changes"]=changed,["group"]=JsonSerializer.SerializeToNode(dependencies.Order(StringComparer.Ordinal)),["moved"]=JsonSerializer.SerializeToNode(selected.Order(StringComparer.Ordinal)),["sourceWritten"]=false};
 }
}
