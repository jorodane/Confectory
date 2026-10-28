using Confectory.Core;
using System.Text.Json.Nodes;

// Read-only property descriptors and the three existing ObjectModel accessors.
// Never resolves a provider, reads an implementation body or creates a value.
internal sealed class InformationFunctionProperties(JsonObject request,Action<string> observe)
{
 Registry? registry;
 readonly HashSet<string> loaded=new(StringComparer.Ordinal);
 readonly Dictionary<string,(JsonObject Properties,JsonObject Functions,string? Proof)> contexts=new(StringComparer.Ordinal);
 Registry Registry()
 {
  if(registry is not null)return registry;
  string project=PackPaths.Resolve(request["project"]!.ToString());observe(project);
  var physical=new Parser(File.ReadAllText(project),project).ParseManifest();var selected=new Parser(request["manifest"]!.ToString(),"<selected-property-project>").ParseManifest();
  if(physical.Kind!="project"||physical.Namespace!=selected.Namespace||physical.Registry.Count!=selected.Registry.Count||physical.Registry.Any(p=>!selected.Registry.TryGetValue(p.Key,out var v)||v.Path!=p.Value.Path)||physical.Dependencies.Count!=selected.Dependencies.Count||physical.Dependencies.Any(p=>!selected.Dependencies.TryGetValue(p.Key,out var v)||v.Version!=p.Value.Version))throw new InvalidOperationException("Property registration changed; retain all inputs and confirm it separately");
  foreach(var locator in physical.Registry.Values)observe(PackPaths.Resolve(Path.Combine(Path.GetDirectoryName(project)!,locator.Path)));
  registry=new Registry(project,new Documents(Path.Combine(Path.GetDirectoryName(project)!,".confectory","document-cache"),new BuildStatistics()),new BuildStatistics());return registry;
 }
 Element Load(string id,string? source)
 {
  var r=Registry();string ns=PackPaths.Namespace(id);
  if(source is not null&&ns!=PackPaths.Namespace(source)&&!r.Packs[PackPaths.Namespace(source)].Dependencies.ContainsKey(ns))throw new ArgumentException("Property declaration requires its existing dependency");
  if(!r.Packs.TryGetValue(ns,out var pack)||!pack.Elements.TryGetValue(id[(ns.Length+2)..],out var locator))throw new ArgumentException("Existing property declaration locator required");
  string path=PackPaths.Owned(Path.GetDirectoryName(r.Paths[ns])!,locator.Path);observe(path);var original=r.Get(id,source:source);
  if(!loaded.Add(id))return original;if(loaded.Count>128)throw new ArgumentException("Property declaration closure budget");
  if(ns==r.Project.Namespace&&request["units"]?[id]?["draft"] is JsonNode draft&&original.Kind is "object" or "concept" or "schema"){
   var parsed=new Parser(draft.ToString(),path).ParseElement();if(parsed.Id!=id||parsed.Kind!=original.Kind)throw new ArgumentException("Exact property source identity required");r.Elements[id]=original=parsed;
  }
  if(original.Parent is not null)Load(original.Parent,original.Id);
  foreach(var use in original.Uses.Where(u=>u.Kind=="schema"))Load(use.Id,use.Origin??original.Id);
  foreach(var field in original.Fields.Values.Where(f=>f.Kind is "compound" or "reference" or "function"))Load(field.Type,field.Origin);
  return original;
 }
 public (JsonObject Properties,JsonObject Functions,string? Proof) ForGraph(Element implementation,JsonObject graph)
 {
  var owners=graph["nodes"]!.AsArray().Where(n=>FeatureBlueprint.IsPropertyNode(n!["kind"]?.ToString())).ToArray();
  if(owners.Length==0)return (new(),new(),null);string key=implementation.Id+"|"+string.Join("|",owners.Select(n=>n!["propertyOwner"]!.ToString()).Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal))+"|"+string.Join("|",owners.Select(n=>n!["kind"]!.ToString()).Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal));
  if(contexts.TryGetValue(key,out var existing))return existing;
  var r=Registry();var properties=new JsonObject();var functions=new JsonObject();
  foreach(string owner in owners.Select(n=>n!["propertyOwner"]!.ToString()).Distinct(StringComparer.Ordinal)){
   if(PackPaths.Namespace(owner)!=r.Project.Namespace)throw new ArgumentException("Select the existing owned property receiver; external property owners retain their own contract context");
   Load(owner,implementation.Id);var descriptor=RuntimeObjectContracts.Describe(r,owner,implementation.Id);
   foreach(var dependency in descriptor["dependencies"]!.AsArray()){if(!loaded.Contains(dependency!.ToString()))throw new InvalidOperationException("Complete property source observations required");Load(dependency.ToString(),null);}
   properties[owner]=descriptor;
  }
  foreach(string accessor in owners.Select(n=>n!["kind"]!.ToString()=="property-ref"?FeatureBlueprint.PropertyRefAccessor:n["kind"]!.ToString()=="property-set"?FeatureBlueprint.PropertySetter:FeatureBlueprint.PropertyReader).Distinct(StringComparer.Ordinal)){
   var declaration=Load(accessor,implementation.Id);var imported=implementation.Imports.Values.Where(i=>i.Id==accessor).ToArray();
   if(declaration.Kind!="function"||declaration.Signature is null||imported.Length!=1||!imported[0].Signature.Matches(declaration.Signature))throw new InvalidOperationException("Keep the exact existing property accessor typed import");
   functions[accessor]=File.ReadAllText(declaration.Loc.File);
  }
  var paths=new HashSet<string>(r.Paths.Values,OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);
  foreach(var descriptor in properties)foreach(var id in descriptor.Value!["dependencies"]!.AsArray())paths.Add(r.Get(id!.ToString()).Loc.File);
  foreach(var accessor in functions)paths.Add(r.Get(accessor.Key).Loc.File);
  var proof=new JsonArray();foreach(string path in paths.Select(PackPaths.Resolve).Order(StringComparer.Ordinal)){observe(path);proof.Add(new JsonObject{["path"]=OperatingSystem.IsWindows()?path.ToUpperInvariant():path,["hash"]=JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(File.ReadAllText(path)))});}
  var result=(properties,functions,(string?)JsonData.Digest(proof));contexts.Add(key,result);return result;
 }
}
