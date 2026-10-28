using Confectory.Core;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

// Definition choices are metadata, never providers, executable bodies or grants.
// A registered type is readable only through an already declared dependency.
internal static class FieldTypes
{
 internal static JsonArray Project(Registry registry,string owner,Func<string,string> source)
 {
  string ns=PackPaths.Namespace(owner);var packs=registry.Packs.Where(p=>p.Key==ns||registry.Packs[ns].Dependencies.ContainsKey(p.Key)).ToArray();
  var declarations=packs.SelectMany(p=>p.Value.Elements.Select(e=>(Id:p.Key+"::"+e.Key,Kind:e.Value.Kind))).ToArray();
  var result=new JsonArray();int targets=0;
  foreach(var item in declarations.Where(e=>e.Kind is "schema" or "function").OrderBy(e=>e.Id,StringComparer.Ordinal)){
   if(result.Count>=256)throw new ArgumentException("Field type catalogue budget");
   foreach(string kind in item.Kind=="schema"?new[]{"compound","reference"}:new[]{"function"}){
    var row=new JsonObject{["id"]=item.Id,["kind"]=kind,["available"]=false};result.Add(row);
    try{
     var proofs=new JsonObject();var seen=new HashSet<string>(StringComparer.Ordinal);
     void Observe(string id){if(!seen.Add(id))return;if(seen.Count>128)throw new ArgumentException("Field type proof budget");var element=registry.Get(id);proofs[id]=JsonData.HashBytes(Encoding.UTF8.GetBytes(source(id)));if(element.Parent is not null)Observe(element.Parent);foreach(var field in element.Fields.Values.Where(f=>f.Kind!="general"))Observe(field.Type);}
     Observe(item.Id);var definition=registry.Effective(item.Id);SchemaContracts.Validate(registry,item.Id);row["name"]=definition.Values.TryGetValue("editorName",out var label)&&label.Value.ValueKind==JsonValueKind.String?label.Value.GetString():item.Id.Split("::")[1];
     if(kind=="compound"){
      new Planner(registry,"metadata").Structural(item.Id);var defaults=InformationDefaults.Resolve(registry,item.Id);foreach(string id in defaults.Sources)Observe(id);var types=new JsonObject();foreach(string id in seen.Where(id=>registry.Get(id).Kind=="schema").ToArray()){var fields=new JsonObject();foreach(var field in registry.Effective(id).Fields)fields[field.Key]=JsonSerializer.SerializeToNode(new{kind=field.Value.Kind,cardinality=field.Value.Cardinality,type=field.Value.Type});types[id]=new JsonObject{["fields"]=fields};}row["types"]=types;row["valueJson"]=new JsonObject(defaults.Values.Select(p=>KeyValuePair.Create<string,JsonNode?>(p.Key,InformationDefaults.Transport(p.Value)))).ToJsonString();
     }else{
      var choices=new JsonArray();foreach(var candidate in declarations.Where(e=>e.Kind==(kind=="reference"?"object":"implementation")).OrderBy(e=>e.Id,StringComparer.Ordinal)){
       try{
        if(kind=="function")registry.Implementation(item.Id,candidate.Id,owner,new());
        else{var target=registry.Effective(candidate.Id);bool matches=false;foreach(var use in target.Uses.Where(u=>u.Kind=="schema")){var visited=new HashSet<string>(StringComparer.Ordinal);for(string? current=use.Id;current is not null&&visited.Add(current);current=registry.Get(current,"schema").Parent)if(current==item.Id){matches=true;break;}}if(!matches)continue;SchemaContracts.Validate(registry,candidate.Id);}
        if(++targets>1024)throw new ArgumentException("Field reference choice budget");Observe(candidate.Id);choices.Add(new JsonObject{["id"]=candidate.Id,["name"]=candidate.Id.Split("::")[1]});
       }catch(BuildError){/* An incompatible target is not a choice. */}
      }row["targets"]=choices;
     }
     row["sources"]=proofs;row["available"]=true;
    }catch(BuildError){row["reason"]="이 타입의 정의·참조를 확인하지 못했어요. 기존 내용은 유지됩니다.";}
   }
  }
  return result;
 }
 internal static JsonObject Contract(JsonObject row)=>row["definition"] is JsonObject definition?definition.DeepClone().AsObject():new(){["kind"]="general",["cardinality"]="single",["type"]=row["nativeType"]?.DeepClone()};
 internal static void Validate(JsonObject shape,JsonNode? sources,JsonArray choices)
 {
  if(shape.Count!=3||shape["cardinality"]?.ToString() is not ("single" or "multiple"))throw new ArgumentException("Explicit field cardinality/kind/type required");
  if(shape["kind"]?.ToString()=="general"){
   if(sources is not null||shape["type"]?.ToString() is not ("string" or "bool" or "int" or "long" or "float" or "double"))throw new ArgumentException("Supported primitive field type required");return;
  }
  var choice=choices.SingleOrDefault(v=>v?["id"]?.ToString()==shape["type"]?.ToString()&&v?["kind"]?.ToString()==shape["kind"]?.ToString());
  if(choice?["available"]?.GetValue<bool>()!=true||!JsonNode.DeepEquals(choice["sources"],sources))throw new InvalidOperationException("Selected field type changed or is outside declared dependencies; retain all input");
 }
}
