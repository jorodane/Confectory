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
 if(element.Bodies.Count>256)throw new ArgumentException("Body locator budget");
 var units=new JsonArray();foreach(var item in element.Bodies.OrderBy(x=>x.Key,StringComparer.Ordinal)){
 string body=PackPaths.Owned(root,Path.GetRelativePath(root,Path.Combine(Path.GetDirectoryName(declaration)!,item.Value.Path)));
 units.Add(new JsonObject{["id"]=element.Id+"/body:"+item.Key,["kind"]="body",["target"]=item.Key,["path"]=Path.GetRelativePath(root,body)});}
 return new JsonObject{["implementation"]=element.Id,["units"]=units};
 }
}
