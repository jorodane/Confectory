using System.Linq;
internal static class SemanticCatalogService
{
 public static System.Text.Json.Nodes.JsonObject Query(string project,System.Text.Json.Nodes.JsonObject request,Func<string,string> scope)
 {
  try{
   project=scope(System.IO.Path.GetFullPath(project));string root=System.IO.Path.GetDirectoryName(project)!;
   var statistics=new Confectory.Core.BuildStatistics();string cache=System.IO.Path.Combine(System.IO.Path.GetTempPath(),"confectory-semantic-catalog-v1",Confectory.Core.JsonData.Digest(project));
   var documents=new Confectory.Core.Documents(cache,statistics);var manifest=documents.Manifest(project);
   string action=request["action"]?.GetValue<string>()??"list",query=request["query"]?.GetValue<string>()??"",kind=request["kind"]?.GetValue<string>()??"";
   if(query.Length>256||kind.Length>64)throw new ArgumentException("Catalog filter budget exceeded.");
   var result=new System.Text.Json.Nodes.JsonObject{["status"]="available",["scope"]="owned-declarations",["sourceScope"]="confirmed-files",["namespace"]=manifest.Namespace,["version"]=manifest.Version,["metadataVersion"]=Confectory.Core.JsonData.Digest(manifest)};
   if(action=="list"){
    int page=request["page"]?.GetValue<int>()??0;if(page<0)throw new ArgumentOutOfRangeException("page");
    var rows=manifest.Elements.Where(e=>(manifest.Namespace+"::"+e.Key).Contains(query,StringComparison.OrdinalIgnoreCase)&&(kind.Length==0||e.Value.Kind==kind)).OrderBy(e=>e.Key,StringComparer.Ordinal).ToArray();
    page=Math.Min(page,Math.Max(0,(rows.Length-1)/32));var units=new System.Text.Json.Nodes.JsonArray();foreach(var row in rows.Skip(page*32).Take(32))units.Add(new System.Text.Json.Nodes.JsonObject{["id"]=manifest.Namespace+"::"+row.Key,["kind"]=row.Value.Kind});
    result["query"]=query;result["kind"]=kind;result["page"]=page;result["pageSize"]=32;result["total"]=rows.Length;result["units"]=units;
   }else if(action=="read"){
    string id=request["id"]!.GetValue<string>();if(!id.StartsWith(manifest.Namespace+"::",StringComparison.Ordinal))throw new ArgumentException("Catalog read requires selected owner namespace.");
    if(!manifest.Elements.TryGetValue(id[(manifest.Namespace.Length+2)..],out var locator))throw new ArgumentException("No owned declaration locator.");
    var element=documents.Element(scope(Confectory.Core.PackPaths.Owned(root,locator.Path)));if(element.Id!=id||element.Kind!=locator.Kind)throw new ArgumentException("Declaration locator identity/kind mismatch.");
    result["element"]=new System.Text.Json.Nodes.JsonObject{["id"]=element.Id,["kind"]=element.Kind,["parent"]=element.Parent,["description"]=element.Description,["signature"]=System.Text.Json.JsonSerializer.SerializeToNode(element.Signature),["fields"]=System.Text.Json.JsonSerializer.SerializeToNode(element.Fields),["data"]=System.Text.Json.JsonSerializer.SerializeToNode(element.Data),["values"]=System.Text.Json.JsonSerializer.SerializeToNode(element.Values.ToDictionary(x=>x.Key,x=>x.Value.Value)),["relations"]=DeclaredRelations.Describe(element),["metadataVersion"]=Confectory.Core.JsonData.Digest(element)};
   }else throw new ArgumentException("Unknown catalog operation.");
   result["reads"]=new System.Text.Json.Nodes.JsonObject{["manifest"]=statistics.ReadDocuments.Count(p=>p==project),["declarations"]=statistics.ReadDocuments.Count(p=>p!=project),["paths"]=System.Text.Json.JsonSerializer.SerializeToNode(statistics.ReadDocuments.Select(p=>System.IO.Path.GetRelativePath(root,p)).ToArray())};return result;
  }
  catch(Confectory.Core.BuildError error){return new System.Text.Json.Nodes.JsonObject{["status"]="unavailable",["scope"]="owned-declarations",["code"]=error.Diagnostic.Code,["message"]=error.Diagnostic.Message};}
  catch(Exception error){return new System.Text.Json.Nodes.JsonObject{["status"]="unavailable",["scope"]="owned-declarations",["code"]="CATALOG_UNAVAILABLE",["message"]=error.Message};}
 }
}
