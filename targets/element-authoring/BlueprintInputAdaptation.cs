using Confectory.Core;
using System.Text.Json.Nodes;

// Pure original expression metadata; no source write, implicit body approval or execution.
internal static class BlueprintNumericValues
{
 internal static bool Numeric(string type)=>type is "int" or "long" or "float" or "double";
 internal static string SourceType(JsonObject graph,Element feature,string excluded,JsonObject value,bool alias=false){
  if(value.Count==1&&value["input"] is not null)return feature.Signature!.Args.Single(p=>!p.IsOut&&p.Name==value["input"]!.ToString()).Type;
  if(value["node"] is not null&&value.Count is 1 or 2&&value.All(p=>p.Key is "node" or "output")){
   if(value["node"]!.ToString()==excluded)throw new ArgumentException("An input cannot use its own output");var provider=graph["nodes"]!.AsArray().Single(n=>n!["id"]!.ToString()==value["node"]!.ToString())!;string output=value["output"]?.ToString()??"return";return output=="return"?provider["signature"]!["return"]!.ToString():provider["signature"]!["args"]!.AsArray().Single(a=>a!["name"]!.ToString()==output&&a["mode"]?.ToString()=="out")!["type"]!.ToString();
  }
  if(!alias&&value.Count==1&&value["local"] is not null){var local=graph["locals"]!.AsArray().Single(l=>l!["id"]!.ToString()==value["local"]!.ToString())!;if(local["source"] is JsonObject origin&&SourceType(graph,feature,excluded,origin,true)!=local["type"]!.ToString())throw new ArgumentException("Alias storage type changed");return local["type"]!.ToString();}
  throw new ArgumentException("Existing typed input, node output or local required");
 }
 internal static JsonNode Adapt(string from,string to,JsonArray path,string baseJson,JsonObject source,string? finalJson=null){
  if(!Numeric(from)||!Numeric(to)||path.Count>12||path.Any(p=>p is null||p.GetValue<int>() is <0 or >1)||path.Count==0&&from==to)throw new ArgumentException("Explicit bounded numeric adaptation required");
  JsonNode result=source.DeepClone();
  if(path.Count>0){
   result=JsonNode.Parse(baseJson)!;JsonNode probe=result;string parentType=from;
   foreach(var step in path){if(probe["binary"] is not JsonObject b||b["operands"] is not JsonArray operands||operands.Count!=2||b["operator"]?.ToString() is not ("+" or "-" or "*" or "/" or "%"))throw new ArgumentException("Existing numeric ancestor required");parentType=b["type"]?.ToString()??parentType;if(!Numeric(parentType))throw new ArgumentException("Numeric ancestor required");probe=operands[step!.GetValue<int>()]??new JsonObject();}
   if(parentType is not ("int" or "long")||to is not ("float" or "double"))throw new ArgumentException("Only an integer subexpression promotes to a selected real value");
   void Preserve(JsonNode? value,string inherited,int depth){if(depth>12)throw new ArgumentException("Expression depth budget");if(value is null)return;var obj=value.AsObject();if(obj.ContainsKey("constant")&&!obj.ContainsKey("type"))obj["type"]=inherited;if(obj["binary"] is JsonObject b){string own=b["type"]?.ToString()??inherited;if(!Numeric(own)||b["operands"] is not JsonArray operands||operands.Count!=2)throw new ArgumentException("Typed numeric expression required");b["type"]=own;foreach(var item in operands)Preserve(item,own,depth+1);}}
   Preserve(result,from,0);JsonNode cursor=result;
   for(int i=0;i<path.Count;i++){var b=cursor["binary"]!.AsObject();b["type"]=to;var operands=b["operands"]!.AsArray();int index=path[i]!.GetValue<int>();if(i==path.Count-1)operands[index]=source.DeepClone();else cursor=operands[index]!;}
  }
  return finalJson is null?result:JsonNode.Parse(finalJson)??throw new ArgumentException("Complete adapted value required");
 }
}
internal static class BlueprintInputAdaptation
{
 public static JsonObject Prepare(JsonObject request){
  var graph=request["graph"]!.DeepClone().AsObject();var feature=new Parser(request["featureSource"]!.GetValue<string>(),"<input-adaptation>").ParseElement();
  if(feature.Kind!="function"||graph["feature"]?.ToString()!=feature.Id||graph["nodes"]!.AsArray().Any(n=>n!["implementationContext"] is not null||n["forwardCallerStorage"]?.GetValue<bool>()==true))throw new ArgumentException("Ordinary owned input adaptation required");
  var plan=request["plan"]!.AsObject();if(plan.Count is not (6 or 7)||plan.Any(p=>p.Key is not ("node" or "name" or "type" or "path" or "baseJson" or "sourceJson" or "valueJson")))throw new ArgumentException("Exact selected input adaptation required");
  string id=plan["node"]!.GetValue<string>(),name=plan["name"]!.GetValue<string>(),to=plan["type"]!.GetValue<string>();var node=graph["nodes"]!.AsArray().Single(n=>n!["id"]!.ToString()==id)!;
  if(node["kind"]?.ToString()!="code"||node["control"]?.ToString()!="next"||node["implementationContext"] is not null||node["forwardCallerStorage"]?.GetValue<bool>()==true)throw new ArgumentException("Free static action input required");
  var argument=node["signature"]!["args"]!.AsArray().Single(a=>a!["name"]!.ToString()==name)!.AsObject();string from=argument["type"]!.ToString();if(argument["mode"] is not null||!node["arguments"]!.AsObject().ContainsKey(name))throw new ArgumentException("Value input required; ref/out cannot adapt");
  var source=JsonNode.Parse(plan["sourceJson"]!.GetValue<string>())!.AsObject();if(BlueprintNumericValues.SourceType(graph,feature,id,source)!=to)throw new ArgumentException("Selected storage must have the exact requested native type");
  node["arguments"]![name]=BlueprintNumericValues.Adapt(from,to,plan["path"]!.AsArray(),plan["baseJson"]!.GetValue<string>(),source,plan["valueJson"]?.GetValue<string>());argument["type"]=to;
  return new(){["graph"]=graph,["node"]=id,["name"]=name,["fromType"]=from,["toType"]=to,["bodyNeedsReview"]=true,["sourceWritten"]=false,["compiled"]=false,["executed"]=false};
 }
}
