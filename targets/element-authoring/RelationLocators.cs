internal static class RelationLocators
{
 public static System.Text.Json.Nodes.JsonObject Query(string text,string root,string[] ids,Func<string,string> read)
 {
  if(text.Length>1048576||ids.Length>256)throw new ArgumentException("Locator query budget exceeded.");
  var rows=new System.Text.Json.Nodes.JsonArray();var manifests=new System.Collections.Generic.Dictionary<string,(Confectory.Core.Manifest? Manifest,string Reason)>(StringComparer.Ordinal);
  Confectory.Core.Manifest? owner=null;try{owner=new Confectory.Core.Parser(text,"<draft-manifest>").ParseManifest();}catch{ }
  foreach(string id in System.Linq.Enumerable.OrderBy(System.Linq.Enumerable.Distinct(ids,StringComparer.Ordinal),x=>x,StringComparer.Ordinal))
  {
   string status="unavailable",reason="project-manifest-invalid";bool? registered=null;string? kind=null;
   try
   {
    new Confectory.Core.Parser("object "+id+" {}","<locator-query>").ParseElement();
    if(owner is not null)
    {
     int split=id.IndexOf("::",StringComparison.Ordinal);string ns=id[..split],local=id[(split+2)..];Confectory.Core.Manifest? chosen=null;
     if(ns==owner.Namespace){registered=true;chosen=owner;reason="";}
     else if(!owner.Registry.TryGetValue(ns,out var locator)){registered=false;status="unregistered";reason="namespace-not-registered";}
     else
     {
      registered=true;
      if(!manifests.TryGetValue(ns,out var cached))
      {
       try{string content=read(System.IO.Path.GetFullPath(System.IO.Path.Combine(root,locator.Path)));if(content.Length>1048576)throw new ArgumentException();var m=new Confectory.Core.Parser(content,"<registered-manifest>").ParseManifest();cached=m.Namespace==ns&&m.Kind=="pack"?(m,""):(null,"manifest-identity-mismatch");}
       catch{cached=(null,"manifest-unavailable");}
       manifests.Add(ns,cached);
      }
      chosen=cached.Manifest;reason=cached.Reason;
     }
     if(chosen is not null){if(chosen.Elements.TryGetValue(local,out var element)){status="registered";reason="locator-present";kind=element.Kind;}else{status="unregistered";reason="element-not-declared";}}
    }
   }
   catch{reason="invalid-qualified-id";}
   rows.Add(new System.Text.Json.Nodes.JsonObject{["id"]=id,["status"]=status,["namespaceRegistered"]=registered,["kind"]=kind,["reason"]=reason});
  }
  return new System.Text.Json.Nodes.JsonObject{["scope"]="manifest-locators",["projectNamespace"]=owner?.Namespace,["targets"]=rows};
 }
}
