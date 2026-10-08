using Confectory.Core;
using System.Text.Json.Nodes;
internal static class DeclaredRelations
{
 public static JsonObject Describe(Element e)
 {
  var rows=new System.Collections.Generic.List<(string Role,string Target,string? Function)>();
  if(e.Parent is not null)rows.Add(("parent",e.Parent,null));
  foreach(var r in e.Modules)rows.Add(("module",r.Id,null));
  foreach(var r in e.Includes)rows.Add(("include",r.Id,null));
  foreach(var r in e.Requires)rows.Add(("require",r.Key,null));
  foreach(var r in e.Defaults)rows.Add(("default",r.Value.Id,r.Key));
  foreach(var r in e.Provides)rows.Add(("provide",r.Value.Id,r.Key));
  var edges=new JsonArray();
  foreach(var r in System.Linq.Enumerable.ThenBy(System.Linq.Enumerable.ThenBy(System.Linq.Enumerable.OrderBy(rows,x=>x.Role,StringComparer.Ordinal),x=>x.Target,StringComparer.Ordinal),x=>x.Function,StringComparer.Ordinal))
  {
   var edge=new JsonObject{["role"]=r.Role,["target"]=r.Target,["function"]=r.Function};
   if(r.Role=="require")edge["signature"]=System.Text.Json.JsonSerializer.SerializeToNode(e.Requires[r.Target].Signature);
   edges.Add(edge);
  }
  return new JsonObject{["scope"]="declared",["owner"]=e.Id,["edges"]=edges};
 }
}
