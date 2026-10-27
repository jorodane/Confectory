using Confectory.Core;
using System.Text.Json.Nodes;

// Ordinary declaration syntax transformations. The caller owns draft CAS and source publication.
internal static class DeclarationAuthoring
{
 internal static void Glyph(string value,bool allowEmpty=false)
 {
  if(allowEmpty&&value.Length==0)return;
  if(value!=value.Trim()||value.Length is <1 or >64||System.Globalization.StringInfo.ParseCombiningCharacters(value).Length!=1||value.Any(c=>char.IsControl(c)||c is '<' or '>' or '&'))throw new ArgumentException("One symbol or emoji required; original input retained");
 }
 internal static void Icon(Element element,string value)
 {
  Glyph(value);
  Apply(element,new JsonObject{["action"]="properties",["values"]=new JsonObject{["icon"]=value}});
 }
 public static void Apply(Element element, JsonObject edit)
 {
  if(edit.ToJsonString().Length>65536)throw new ArgumentException("Declaration edit budget");
  string Text(JsonNode node,string key)=>node[key]?.GetValue<string>()??throw new ArgumentException("Explicit "+key+" required");
  string action=Text(edit,"action");
  string Id(JsonNode node,string key){string id=Text(node,key);if(id.Length>256||!System.Text.RegularExpressions.Regex.IsMatch(id,@"\A[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*::[A-Za-z_][A-Za-z_0-9]*\z",System.Text.RegularExpressions.RegexOptions.CultureInvariant))throw new ArgumentException("Qualified declaration ID required");return id;}
  FunctionSignature Signature(JsonNode node,bool named)
  {
   var args=node["args"]?.AsArray()??throw new ArgumentException("Signature arguments required");if(args.Count>64)throw new ArgumentException("Signature argument budget");
   if(args.Any(arg=>arg?["mode"] is not null && arg["mode"]!.ToString() is not ("out" or "ref")))throw new ArgumentException("Only value/ref inputs and named out outputs are supported");
   return new(args.Select((arg,index)=>new Parameter(Text(arg!,"type"),named?Text(arg!,"name"):"arg"+index,arg?["mode"]?.GetValue<string>())).ToList(),Text(node,"return"));
  }
  List<JsonNode> Entries(){var rows=edit["entries"]?.AsArray()??throw new ArgumentException("Relation entries required");if(rows.Count>128)throw new ArgumentException("Relation budget");return rows.Select(row=>row??throw new ArgumentException("Relation entry required")).ToList();}
  ElementReference Reference(JsonNode row,bool typed=false)=>new(Id(row,"id"),new(),element.Id,typed?Text(row,"kind"):null);
  Dictionary<string,T> Unique<T>(IEnumerable<(string Id,T Value)> rows){var result=new Dictionary<string,T>(StringComparer.Ordinal);foreach(var row in rows)if(!result.TryAdd(row.Id,row.Value))throw new ArgumentException("Duplicate declaration edit entry");return result;}
  (Dictionary<string,SchemaDatum>? Members,List<SchemaDatum>? Items,JsonNode Segment) Parent(JsonArray path)
  {
   if(element.Kind!="object"||path.Count<1||path.Count>64)throw new ArgumentException("Bounded local object data path required");
   Dictionary<string,SchemaDatum>? members=element.Data;List<SchemaDatum>? items=null;
   for(int i=0;i<path.Count-1;i++){
    SchemaDatum datum;if(members is not null&&path[i] is JsonValue member&&member.TryGetValue<string>(out var key)&&members.TryGetValue(key,out var found))datum=found;
    else if(items is not null&&path[i] is JsonValue index&&index.TryGetValue<int>(out int n)&&n>=0&&n<items.Count)datum=items[n];
    else throw new ArgumentException("Path has no local override; inherited data is not copied");
    members=datum.Members;items=datum.Items;
   }
   return(members,items,path[^1]??throw new ArgumentException("Path segment required"));
  }
  switch(action){
   case "properties":{
    var values=edit["values"]?.AsObject()??throw new ArgumentException("Explicit declaration properties required");if(values.Count<1||values.Count>4)throw new ArgumentException("Properties budget");
    foreach(var pair in values){
     if(pair.Key=="parent"){element.Parent=pair.Value is null?null:Id(values,"parent");continue;}
     string value=pair.Value?.GetValue<string>()??throw new ArgumentException("Property string required");
     if(pair.Key=="description"){if(value.Length>16384)throw new ArgumentException("Description budget");element.Description=value;element.DescriptionPresent=true;}
     else if(pair.Key is "displayName" or "icon"){if(value.Length>(pair.Key=="displayName"?256:64))throw new ArgumentException("Display metadata budget");element.Values[pair.Key=="displayName"?"editorName":"editorIcon"]=new(System.Text.Json.JsonSerializer.SerializeToElement(value),element.Id,new());}
     else throw new ArgumentException("Supported declaration property required");
    }break;
   }
   case "signature":if(element.Kind is not ("function" or "implementation"))throw new ArgumentException("Public function signature required");element.Signature=Signature(edit["value"]??throw new ArgumentException("Signature required"),true);break;
   case "provide-function":{
    if(element.Kind!="object"||edit.Any(p=>p.Key is not ("action" or "function" or "implementation"))||!edit.ContainsKey("implementation"))throw new ArgumentException("Explicit object provider edit required");
    string function=Id(edit,"function");if(edit["implementation"] is null)element.Provides.Remove(function);else element.Provides[function]=new ElementReference(Id(edit,"implementation"),new(),element.Id);break;
   }
   case "module-function":{
    if(element.Kind!="module"||edit.Any(p=>p.Key is not ("action" or "function" or "signature" or "default"))||!edit.ContainsKey("signature")&&!edit.ContainsKey("default"))throw new ArgumentException("Explicit module contract/default edit required");
    string function=Id(edit,"function");
    if(edit.ContainsKey("signature")){if(edit["signature"] is null)element.Requires.Remove(function);else element.Requires[function]=new RequiredFunction(Signature(edit["signature"]!,false),new(),element.Id);}
    if(edit.ContainsKey("default")){if(edit["default"] is null)element.Defaults.Remove(function);else element.Defaults[function]=new ElementReference(Id(edit,"default"),new(),element.Id);}
    break;
   }
   case "parent":if(!edit.ContainsKey("value"))throw new ArgumentException("Explicit parent value required");element.Parent=edit["value"] is null?null:Id(edit,"value");break;
   case "relations":{
    string role=Text(edit,"role");var rows=Entries();
    switch(role){
     case "module":element.Modules=rows.Select(r=>Reference(r)).ToList();break;
     case "include":element.Includes=rows.Select(r=>Reference(r)).ToList();break;
     case "use":element.Uses=rows.Select(r=>Reference(r,true)).ToList();break;
     case "contain":element.Contains=rows.Select(r=>Reference(r,true)).ToList();break;
     case "require":element.Requires=Unique(rows.Select(r=>(Id(r,"id"),new RequiredFunction(Signature(r["signature"]??throw new ArgumentException("Required signature required"),false),new(),element.Id))));break;
     case "default":element.Defaults=Unique(rows.Select(r=>(Id(r,"function"),Reference(r))));break;
     case "provide":element.Provides=Unique(rows.Select(r=>(Id(r,"function"),Reference(r))));break;
     case "import":element.Imports=Unique(rows.Select(r=>(Text(r,"alias"),new Import(Id(r,"id"),Signature(r["signature"]??throw new ArgumentException("Import signature required"),false),r["scope"] is null?null:Id(r,"scope"),new(),element.Id))));break;
     default:throw new ArgumentException("Declared relation role required");
    }break;
   }
   case "unset-description":element.Description="";element.DescriptionPresent=false;break;
   case "unset-value":if(!element.Values.Remove(Text(edit,"field")))throw new ArgumentException("No local metadata override");break;
   case "remove-field":if(element.Kind!="schema"||!element.Fields.Remove(Text(edit,"field")))throw new ArgumentException("No local schema field");break;
   case "field-order":{
    var order=edit["order"]?.AsArray().Select(v=>v!.GetValue<string>()).ToArray()??throw new ArgumentException("Field order required");
    if(element.Kind!="schema"||order.Length!=element.Fields.Count||order.Distinct(StringComparer.Ordinal).Count()!=order.Length||order.Any(k=>!element.Fields.ContainsKey(k)))throw new ArgumentException("Exact local field order required");element.Fields=order.ToDictionary(k=>k,k=>element.Fields[k],StringComparer.Ordinal);break;
   }
   case "unset-data":{
    var p=Parent(edit["path"]?.AsArray()??throw new ArgumentException("Data path required"));
    if(p.Members is not null&&p.Segment is JsonValue member&&member.TryGetValue<string>(out var key)&&p.Members.Remove(key))break;
    if(p.Items is not null&&p.Segment is JsonValue index&&index.TryGetValue<int>(out int n)&&n>=0&&n<p.Items.Count){p.Items.RemoveAt(n);break;}
    throw new ArgumentException("Path has no local override");
   }
   case "move-data":{
    var path=edit["path"]?.AsArray()??throw new ArgumentException("Array path required");var p=Parent(path);SchemaDatum datum;
    if(p.Members is not null&&p.Segment is JsonValue member&&member.TryGetValue<string>(out var key)&&p.Members.TryGetValue(key,out var found))datum=found;
    else if(p.Items is not null&&p.Segment is JsonValue index&&index.TryGetValue<int>(out int n)&&n>=0&&n<p.Items.Count)datum=p.Items[n];
    else throw new ArgumentException("Array has no local override");
    int from=edit["from"]?.GetValue<int>()??-1,to=edit["to"]?.GetValue<int>()??-1;
    if(datum.Items is null||from<0||to<0||from>=datum.Items.Count||to>=datum.Items.Count)throw new ArgumentException("Existing local array positions required");var item=datum.Items[from];datum.Items.RemoveAt(from);datum.Items.Insert(to,item);break;
   }
   default:throw new ArgumentException("Supported declaration edit required");
  }
 }
}
