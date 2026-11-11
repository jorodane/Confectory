using Confectory.Core;
using System.Text.Json.Nodes;

// Read-only labels over an already observed function and existing positional ABI.
// This projection never participates in a compiler contract/definition hash.
internal static class FunctionPinPresentation
{
 public static JsonObject Query(JsonObject request)
 {
  var function=new Parser(request["text"]!.GetValue<string>(),"<call-pin-presentation>").ParseElement();
  if(function.Kind!="function"||function.Signature is null||function.Id!=request["id"]!.GetValue<string>())throw new ArgumentException("Exact observed function required");
  var signature=request["signature"]!.AsObject();var args=signature["args"]!.AsArray().Select(a=>new Parameter(a!["type"]!.GetValue<string>(),a["name"]!.GetValue<string>(),a["mode"]?.GetValue<string>())).ToList();
  var current=new FunctionSignature(args,signature["return"]!.GetValue<string>());
  var result=new JsonObject{["status"]="signature-mismatch",["signature"]=signature.DeepClone(),["sourceWritten"]=false,["executed"]=false};
  if(!current.Matches(function.Signature))return result;
  JsonObject names;try{names=FunctionArgumentNames.Read(function);}catch(ArgumentException){result["status"]="invalid-labels";return result;}catch(System.Text.Json.JsonException){result["status"]="invalid-labels";return result;}catch(InvalidOperationException){result["status"]="invalid-labels";return result;}catch(NullReferenceException){result["status"]="invalid-labels";return result;}
  var mapped=new JsonObject();for(int i=0;i<args.Count;i++)if(names[function.Signature.Args[i].Name] is JsonNode name)mapped[args[i].Name]=name.DeepClone();
  // A label valid for the callee can collide with a differently named caller
  // parameter. Reuse the existing per-side distinct-label rule on the projected
  // signature; this mutates only the local parsed object, never source or ABI.
  function.Signature=current;try{FunctionArgumentNames.Set(function,mapped);}catch(ArgumentException){result["status"]="ambiguous-labels";return result;}
  result["status"]="available";result["argumentNames"]=FunctionArgumentNames.Read(function);result["returnName"]=FunctionReturnName.Read(function);return result;
 }
}
