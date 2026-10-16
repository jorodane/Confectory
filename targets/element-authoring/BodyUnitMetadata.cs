using Confectory.Core;
using System.Text.Json.Nodes;
internal static class BodyUnitMetadata
{
 public static JsonObject Query(JsonObject request)
 {
 string root=Path.GetDirectoryName(Path.GetFullPath(request["project"]!.GetValue<string>()))!;
 string declaration=PackPaths.Owned(root,request["path"]!.GetValue<string>());
 string text=request["text"]!.GetValue<string>();if(text.Length>1048576)throw new ArgumentException("Declaration budget");
 var element=new Parser(text,declaration).ParseElement();if(element.Kind!="implementation"||element.Id!=request["id"]!.GetValue<string>())throw new ArgumentException("Owned implementation identity required.");
 var manifest=new Parser(File.ReadAllText(request["project"]!.GetValue<string>()),request["project"]!.GetValue<string>()).ParseManifest();
 string bodyRoot=root,ns=PackPaths.Namespace(element.Id);
 if(ns!=manifest.Namespace){
  if(!manifest.Registry.TryGetValue(ns,out var registration))throw new ArgumentException("Owned implementation manifest required");
  string path=PackPaths.Owned(root,registration.Path);var owner=new Parser(File.ReadAllText(path),path).ParseManifest();if(owner.Kind!="pack"||owner.Namespace!=ns)throw new ArgumentException("Owned implementation namespace mismatch");bodyRoot=Path.GetDirectoryName(path)!;
 }
 if(element.Bodies.Count>256)throw new ArgumentException("Body locator budget");
 var units=new JsonArray();foreach(var item in element.Bodies.OrderBy(x=>x.Key,StringComparer.Ordinal)){
 string body=PackPaths.Owned(root,Path.GetRelativePath(root,PackPaths.Owned(bodyRoot,item.Value.Path)));
 units.Add(new JsonObject{["id"]=element.Id+"/body:"+item.Key,["kind"]=item.Value.SourceKind=="blueprint"?"blueprint":"body",["target"]=item.Key,["path"]=Path.GetRelativePath(root,body)});
 if(item.Value.SourceKind=="blueprint")foreach(var node in BlueprintDocuments.NodeUnits(root,body,element.Id+"/body:"+item.Key,request["blueprintDrafts"]?[element.Id+"/body:"+item.Key]?.GetValue<string>()))units.Add(node!.DeepClone());}
 return new JsonObject{["implementation"]=element.Id,["units"]=units};
 }
}
