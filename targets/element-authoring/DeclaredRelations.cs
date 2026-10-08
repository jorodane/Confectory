using Confectory.Core;
using System.Text.Json.Nodes;
internal static class DeclaredRelations
{
 public static JsonObject Describe(Element e)
 {
  var rows=new System.Collections.Generic.List<(string Role,string Target,string? Function,string? Kind,string? Alias,string? Scope,FunctionSignature? Signature)>();
  void Add(string role,string target,string? function=null,string? kind=null,string? alias=null,string? scope=null,FunctionSignature? signature=null)=>rows.Add((role,target,function,kind,alias,scope,signature));
  if(e.Parent is not null)Add("parent",e.Parent);
  foreach(var r in e.Modules)Add("module",r.Id);
  foreach(var r in e.Includes)Add("include",r.Id);
  foreach(var r in e.Requires)Add("require",r.Key,signature:r.Value.Signature);
  foreach(var r in e.Defaults)Add("default",r.Value.Id,r.Key);
  foreach(var r in e.Provides)Add("provide",r.Value.Id,r.Key);
  foreach(var r in e.Uses)Add("use",r.Id,kind:r.Kind);
  foreach(var r in e.Contains)Add("contain",r.Id,kind:r.Kind);
  foreach(var r in e.Imports)Add("import",r.Value.Id,kind:"function",alias:r.Key,scope:r.Value.Scope,signature:r.Value.Signature);
  var edges=new JsonArray();
  foreach(var r in rows.OrderBy(x=>x.Role,StringComparer.Ordinal).ThenBy(x=>x.Target,StringComparer.Ordinal).ThenBy(x=>x.Function,StringComparer.Ordinal).ThenBy(x=>x.Kind,StringComparer.Ordinal).ThenBy(x=>x.Alias,StringComparer.Ordinal))
  {
   var edge=new JsonObject{["role"]=r.Role,["target"]=r.Target,["function"]=r.Function};
   if(r.Kind is not null)edge["kind"]=r.Kind;
   if(r.Role=="import"){edge["alias"]=r.Alias;edge["scope"]=r.Scope;}
   if(r.Signature is not null)edge["signature"]=System.Text.Json.JsonSerializer.SerializeToNode(r.Signature);
   edges.Add(edge);
  }
  return new JsonObject{["scope"]="declared",["owner"]=e.Id,["edges"]=edges};
 }
}
