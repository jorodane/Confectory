using Confectory.Core;
using System.Text.Json;
using System.Text.Json.Nodes;

// Module-local display metadata over an unchanged, directly declared requirement.
// The existing positional contract is observed, never replaced with a new pin ID.
internal static class ModulePinPresentation
{
 internal static string Key(string function,string pin)=>"editorModulePinIcon_f"+Convert.ToHexString(System.Text.Encoding.UTF8.GetBytes(function)).ToLowerInvariant()+"_"+pin;
 internal static JsonObject Contract(FunctionSignature s)=>new(){["args"]=new JsonArray(s.Args.Select(a=>(JsonNode)new JsonObject{["type"]=a.Type,["mode"]=a.Mode??""}).ToArray()),["return"]=s.Return};
 internal static string Apply(Element owner,string text)
 {
  var edit=JsonNode.Parse(text)?.AsObject()??throw new ArgumentException("Module pin display required");
  if(owner.Kind!="module"||edit.Count!=4||edit.Any(p=>p.Key is not ("function" or "pin" or "signature" or "icon")))throw new ArgumentException("Exact module pin display required");
  string function=edit["function"]!.GetValue<string>(),pin=edit["pin"]!.GetValue<string>(),icon=edit["icon"]!.GetValue<string>();
  if(!owner.Requires.TryGetValue(function,out var requirement)||requirement.Origin!=owner.Id||!JsonNode.DeepEquals(edit["signature"],Contract(requirement.Signature)))throw new InvalidOperationException("Direct unchanged module requirement required; retain inherited and external originals");
  bool valid=pin=="return"?requirement.Signature.Return!="void":pin.StartsWith('a')&&int.TryParse(pin.AsSpan(1),out int index)&&index>=0&&index<requirement.Signature.Args.Count&&pin=="a"+index;
  if(!valid)throw new ArgumentException("Existing module pin required; identity/type/order unchanged");
  DeclarationAuthoring.PresentationIcon(icon,true);string key=Key(function,pin);
  if(icon.Length==0)owner.Values.Remove(key);else owner.Values[key]=new(JsonSerializer.SerializeToElement(edit.ToJsonString()),owner.Id,new());
  return key;
 }
}
