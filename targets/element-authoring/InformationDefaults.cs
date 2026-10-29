using Confectory.Core;
using System.Text.Json;
using System.Text.Json.Nodes;

// Versioned editor metadata, not a new declaration language or runtime cache.
// Only a declaration's own explicit profile makes its default records readable.
internal static class InformationDefaults
{
 public const string Marker=SchemaContracts.InformationDefaultsMarker,Profile=SchemaContracts.InformationDefaultsProfile,Prefix=SchemaContracts.InformationDefaultsPrefix;
 public static bool Presentation(string key)=>key is "editorName" or "editorFolder" or "editorIcon"||key.StartsWith("editorFieldName_",StringComparison.Ordinal)||key.StartsWith("editorFieldIcon_",StringComparison.Ordinal);
 public static bool Recognized(string key)=>Presentation(key)||key==Marker||key==OwnedInformationDefinitions.Marker||key.StartsWith(Prefix,StringComparison.Ordinal);
 public static Dictionary<string,SchemaDatum> Stored(Registry registry,string id)=>SchemaContracts.EditorDefaults(registry,id);
 public static (Dictionary<string,SchemaDatum> Values,bool Complete,HashSet<string> Sources) Resolve(Registry registry,string id,HashSet<string>? ancestors=null,int depth=0,int[]? budget=null)
 {
  budget??=new[]{0};ancestors=ancestors is null?new(StringComparer.Ordinal):new(ancestors,StringComparer.Ordinal);if(depth>32||!ancestors.Add(id))throw new BuildError("INFORMATION_DEFAULT_CYCLE","Information defaults must be finite");var schema=registry.Effective(id);var values=Stored(registry,id);bool complete=true;var sources=new HashSet<string>(StringComparer.Ordinal){id};for(string? parent=registry.Get(id,"schema").Parent;parent is not null;parent=registry.Get(parent,"schema").Parent){if(!sources.Add(parent))throw new BuildError("INFORMATION_DEFAULT_CYCLE","Information inheritance must be finite");}
  foreach(var field in schema.Fields){if(++budget[0]>512)throw new BuildError("INFORMATION_DEFAULT_BUDGET","Information default expansion exceeds the editor row budget");sources.Add(field.Value.Origin);string kind=field.Value.Kind,type=field.Value.Type;Dictionary<string,SchemaDatum>? nestedValues=null;bool nestedComplete=true;if(kind=="compound"){var nested=Resolve(registry,type,ancestors,depth+1,budget);sources.UnionWith(nested.Sources);nestedValues=nested.Values;nestedComplete=nested.Complete;}if(values.ContainsKey(field.Key))continue;SchemaDatum? value=null;if(kind=="compound"){complete&=nestedComplete;value=new("compound",null,null,null,nestedValues!,id,new());}else if(kind=="general"){using var json=JsonDocument.Parse(type=="string"?"\"\"":type=="bool"?"false":"0");value=SchemaContracts.FromTransport(json.RootElement,id);}else complete=false;if(value is not null)values[field.Key]=field.Value.Cardinality=="multiple"?new("multiple",null,null,new(){value},null,id,new()):value;}
  foreach(var value in values.Values)sources.Add(value.Origin);SchemaContracts.Validate(registry,id,values);return(values,complete,sources);
 }
 public static JsonNode Transport(SchemaDatum value)=>value.Kind switch{"general"=>JsonNode.Parse(value.Scalar!.Value.GetRawText())!,"reference"=>new JsonObject{["$ref"]=value.Reference},"multiple"=>new JsonArray(value.Items!.Select(Transport).ToArray()),"compound"=>new JsonObject(value.Members!.Select(p=>KeyValuePair.Create<string,JsonNode?>(p.Key,Transport(p.Value)))),_=>throw new ArgumentException("Typed default required")};
 public static void Set(Element schema,string field,SchemaDatum value)
 {
  if(schema.Kind!="schema")throw new ArgumentException("Information owner required");if(schema.Values.TryGetValue(Marker,out var marker)&&(marker.Value.ValueKind!=JsonValueKind.String||marker.Value.GetString()!=Profile))throw new InvalidOperationException("Unknown information defaults profile retained");if(schema.Values.Keys.Any(k=>k.StartsWith(Prefix,StringComparison.Ordinal))&&!schema.Values.ContainsKey(Marker))throw new InvalidOperationException("Unmarked default records retained; explicit migration required");schema.Values[Marker]=new(JsonSerializer.SerializeToElement(Profile),schema.Id,new());schema.Values[Prefix+field]=new(JsonSerializer.SerializeToElement(Transport(value).ToJsonString()),schema.Id,new());
 }
}
