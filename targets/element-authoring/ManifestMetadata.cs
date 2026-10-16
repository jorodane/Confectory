using Confectory.Core;
using System.Text.Json.Nodes;

internal static class ManifestMetadata
{
 public static JsonObject Inspect(string text)
 {
  if(text.Length>1048576)throw new ArgumentException("Manifest budget");
  var manifest=new Parser(text,"<draft-manifest>").ParseManifest();var elements=new JsonArray();
  foreach(var pair in manifest.Elements.OrderBy(p=>p.Key,StringComparer.Ordinal))elements.Add(new JsonObject{["id"]=manifest.Namespace+"::"+pair.Key,["kind"]=pair.Value.Kind,["path"]=pair.Value.Path});
  return new(){["namespace"]=manifest.Namespace,["kind"]=manifest.Kind,["elements"]=elements};
 }
}
