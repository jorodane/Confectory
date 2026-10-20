using Confectory.Core;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

internal static class NamespaceDiagnostic
{
 // Only identifiers and a closed resolution category cross this boundary. Never
 // forward exception messages, source text, file locations or configuration data.
 public static JsonObject? From(BuildError? error)
 {
  if(error?.Diagnostic.Code!="MISSING_NAMESPACE"||error.NamespaceDiagnostic is not {} value)return null;
  bool Namespace(string? text)=>text is not null&&text.Length<=192&&Regex.IsMatch(text,@"\A[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*\z");
  if(!Namespace(value.MissingNamespace)||value.Resolution is not ("dependency" or "element" or "pack-check"))return null;
  var result=new JsonObject{["missingNamespace"]=value.MissingNamespace,["resolution"]=value.Resolution};
  if(Namespace(value.OwnerNamespace))result["ownerNamespace"]=value.OwnerNamespace;
  if(value.Reference is string reference&&reference.Length<=384){string[] parts=reference.Split("::");if(parts.Length==2&&Namespace(parts[0])&&Regex.IsMatch(parts[1],@"\A[A-Za-z_][A-Za-z0-9_]*\z"))result["reference"]=reference;}
  return result;
 }
}
