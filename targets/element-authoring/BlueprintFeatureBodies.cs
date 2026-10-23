using Confectory.Core;
using System.Text.Json.Nodes;
using System.Security.Cryptography;
using System.Text;

// A bounded snapshot of owned implementation/body identities. Never chooses or edits one.
internal static class BlueprintFeatureBodies
{
 public static JsonObject Query(JsonObject request){
  var feature=new Parser(request["featureSource"]!.GetValue<string>(),"<feature-bodies>").ParseElement();string ns=request["namespace"]!.GetValue<string>(),prefix=ns+"::";var rows=request["sources"]!.AsArray();if(feature.Kind!="function"||!feature.Id.StartsWith(prefix,StringComparison.Ordinal)||rows.Count>256)throw new ArgumentException("Owned feature/body snapshot required");
  var units=new Dictionary<string,(Element Element,JsonObject Row)>(StringComparer.Ordinal);int bytes=0;
  foreach(var item in rows){var row=item!.AsObject();string id=row["id"]!.GetValue<string>(),text=row["text"]!.GetValue<string>();bytes=checked(bytes+Encoding.UTF8.GetByteCount(text));if(bytes>2097152||!id.StartsWith(prefix,StringComparison.Ordinal)||units.ContainsKey(id))throw new ArgumentException("Bounded distinct owned implementation sources required");string hash=Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(text))).ToLowerInvariant();if(row["hash"]?.ToString()!=hash||row["revision"]!.GetValue<long>()<0)throw new ArgumentException("Exact implementation source observation required");var element=new Parser(text,"<owned-implementation>").ParseElement();if(element.Id!=id||element.Kind!="implementation")throw new ArgumentException("Exact implementation identity required");units.Add(id,(element,row));}
  var cache=new Dictionary<string,(string? Function,FunctionSignature? Signature,Dictionary<string,Body> Bodies,bool Unknown,bool Dirty)>(StringComparer.Ordinal);var visiting=new HashSet<string>(StringComparer.Ordinal);
  (string? Function,FunctionSignature? Signature,Dictionary<string,Body> Bodies,bool Unknown,bool Dirty) Resolve(string id){
   if(cache.TryGetValue(id,out var saved))return saved;if(!visiting.Add(id))throw new ArgumentException("Implementation inheritance cycle");var source=units[id].Element;string? function=null;FunctionSignature? signature=null;var bodies=new Dictionary<string,Body>(StringComparer.Ordinal);bool unknown=false,dirty=units[id].Row["dirty"]?.GetValue<bool>()==true;
   if(source.Parent is not null){if(units.ContainsKey(source.Parent)){var parent=Resolve(source.Parent);function=parent.Function;signature=parent.Signature;bodies=new(parent.Bodies,StringComparer.Ordinal);unknown=parent.Unknown;dirty|=parent.Dirty;}else unknown=true;}
   if(function is not null&&source.Function!=function||signature is not null&&source.Signature is not null&&!source.Signature.Matches(signature))throw new ArgumentException("Inherited implementation contract cannot change");
   function=source.Function??function;signature=source.Signature??signature;foreach(var body in source.Bodies)bodies[body.Key]=body.Value;visiting.Remove(id);return cache[id]=(function,signature,bodies,unknown,dirty);
  }
  var result=new JsonArray();bool unresolved=false;
  foreach(string id in units.Keys.Order(StringComparer.Ordinal)){var effective=Resolve(id);if(effective.Function is null&&effective.Unknown){unresolved=true;continue;}if(effective.Function!=feature.Id)continue;if(effective.Signature is null||!effective.Signature.Matches(feature.Signature!))throw new ArgumentException("Implementation must retain the selected function contract");if(effective.Unknown)unresolved=true;foreach(var body in effective.Bodies.OrderBy(p=>p.Key,StringComparer.Ordinal)){if(result.Count>=256)throw new ArgumentException("Body context budget");var source=units[id].Row;result.Add(new JsonObject{["id"]=id+"/body:"+body.Key,["feature"]=feature.Id,["implementation"]=id,["target"]=body.Key,["sourceKind"]=body.Value.SourceKind,["bodyOrigin"]=body.Value.Origin,["inherited"]=body.Value.Origin!=id,["revision"]=source["revision"]!.DeepClone(),["hash"]=source["hash"]!.DeepClone(),["dirty"]=effective.Dirty});}}
  return new(){["feature"]=feature.Id,["declaredImplementation"]=feature.Provides.TryGetValue(feature.Id,out var provider)?provider.Id:null,["rows"]=result,["unresolvedParents"]=unresolved,["selectionMade"]=false,["sourceWritten"]=false,["compiled"]=false};
 }
}
