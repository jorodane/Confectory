using Confectory.Core;
using System.Text.Json.Nodes;

// Compose existing pure closures over an internal overlay. This is not a new
// save operation: the caller publishes the complete result with its one CAS.
internal sealed class InformationFunctionBatch
{
 public JsonObject Request { get; }
 readonly JsonObject originalUnits;
 readonly HashSet<string> functions;
 readonly bool composeCallers;
 readonly Dictionary<string,JsonObject> outputPlans;
 readonly HashSet<string> completed=new(StringComparer.Ordinal);
 InformationFunctionBatch(JsonObject request,HashSet<string> functions,bool composeCallers,Dictionary<string,JsonObject> outputPlans){Request=request.DeepClone().AsObject();originalUnits=request["units"]!.AsObject();this.functions=functions;this.composeCallers=composeCallers;this.outputPlans=outputPlans;}
 public static InformationFunctionBatch? Begin(JsonObject request,JsonArray changes,Func<Element,string> format)
 {
  bool ContractEdit(JsonNode? row){
   if(row?["type"]?.ToString()!="function-edit"||row["mapping"] is not JsonObject mapping)return false;
   if((mapping["bodies"] as JsonObject)?.Count>0)return true;
   // Metadata-only edits keep the existing path, including native/ref bodies.
   if(mapping["before"] is null)return true;
   return !JsonNode.DeepEquals(FeatureBlueprint.SignatureDocument(InformationFunctionBodies.Signature(mapping["before"]!)),FeatureBlueprint.SignatureDocument(InformationFunctionBodies.Signature(row["signature"]!)));
  }
  var edits=changes.Where(ContractEdit).ToArray();
  if(edits.Length<2)return null;
  if(edits.Length>8||changes.Count!=edits.Length)throw new InvalidOperationException("Save up to eight direct function contracts together; other input is retained");
  var units=request["units"]?.AsObject()??throw new InvalidOperationException("Read every shared caller before saving the function group");if(units.Count>2048)throw new ArgumentException("Shared contract source budget");
  if(InformationFunctionBodyBatch.Prepare(request,edits,units,format) is {} bodyFunctions)return new(request,bodyFunctions,false,new());
  bool referencePins=edits.Any(row=>new[]{row?["mapping"]?["before"],row?["signature"]}.Any(s=>s?["args"] is JsonArray args&&args.Any(a=>a?["mode"]?.ToString()=="ref")));
  bool wholeValue=edits.Any(row=>row?["mapping"]?["bodies"] is JsonObject&&row["mapping"]?["before"]?["args"] is JsonArray before&&row["signature"]?["args"] is JsonArray after&&before.Count==after.Count&&before.Where((a,i)=>(a?["mode"]?.ToString()=="out"&&after[i]?["mode"] is null||a?["mode"] is null&&after[i]?["mode"]?.ToString()=="out")).Any());
  bool Permutation(FunctionSignature before,FunctionSignature next)=>before.Return==next.Return&&before.Args.Count==next.Args.Count&&!before.Args.SequenceEqual(next.Args)&&before.Args.All(a=>next.Args.Any(b=>a==b));
  bool wholeOrder=edits.Any(row=>row?["mapping"]?["before"] is JsonObject&&row["signature"] is JsonObject&&Permutation(InformationFunctionBodies.Signature(row!["mapping"]!["before"]!),InformationFunctionBodies.Signature(row["signature"]!)));
  var orderedFunctions=new HashSet<string>(StringComparer.Ordinal);
  var wholeRoleFunctions=new HashSet<string>(StringComparer.Ordinal);var wholeRolePlans=new Dictionary<string,JsonObject>(StringComparer.Ordinal);
  var functions=new HashSet<string>(StringComparer.Ordinal);var structures=new HashSet<string>(StringComparer.Ordinal);var inputDefinitions=new HashSet<string>(StringComparer.Ordinal);var returns=new HashSet<string>(StringComparer.Ordinal);var inputTypes=new HashSet<string>(StringComparer.Ordinal);var inputNames=new HashSet<string>(StringComparer.Ordinal);var outputTypes=new HashSet<string>(StringComparer.Ordinal);bool typed=false,hasOutputs=false,outputTyped=false;
  bool Scalar(string type)=>type is "bool" or "int" or "long" or "float" or "double" or "string";
  foreach(var row in edits){
   string id=row!["id"]!.ToString();if(!functions.Add(id))throw new ArgumentException("One explicit edit per function identity required");
   var mapping=row["mapping"]!.AsObject();if(mapping.Any(p=>p.Key is not ("before" or "args" or "callers" or "implementations" or "outputs" or "outputGraphs" or "bodies")||p.Key=="bodies"&&!referencePins&&!wholeValue&&!wholeOrder)||mapping["before"] is not JsonObject||mapping["args"] is not JsonObject)throw new InvalidOperationException("Shared caller batching preserves body and copy contracts; retain all input");
   var original=new Parser(units[id]?["draft"]?.ToString()??throw new InvalidOperationException("Original function snapshot missing"),"<function-group>").ParseElement();
   var before=original.Signature??throw new ArgumentException("Function signature required");var next=InformationFunctionBodies.Signature(row["signature"]!);var remap=mapping["args"]!.AsObject();
   if(original.Kind!="function"||original.Parent is not null||!JsonNode.DeepEquals(mapping["before"],FeatureBlueprint.SignatureDocument(before))||before.Args.Count!=remap.Count||before.Args.Any(a=>!remap.ContainsKey(a.Name)||a.Mode is not (null or "out" or "ref"))||next.Args.Any(a=>a.Mode is not (null or "out" or "ref")))throw new InvalidOperationException("Shared caller batching requires exact original pin identities; retain all input");
   if(Permutation(before,next)){
    // Existing native names identify the same public pins in a new order.
    // Do not turn a permutation into a role change or a new storage choice.
    if(mapping.Count!=4||mapping.Any(p=>p.Key is not ("before" or "args" or "bodies" or "callers"))||before.Args.Any(a=>remap[a.Name]?.ToString()!=a.Name)||mapping["bodies"] is not JsonObject bodies||bodies.Count==0||mapping["callers"] is not JsonObject callers)throw new InvalidOperationException("Review every original body and caller for the exact pin permutation");
    foreach(var plan in bodies.Select(p=>p.Value!.AsObject()))if(!Permutation(InformationFunctionBodies.Signature(plan["beforeSignature"]!),InformationFunctionBodies.Signature(plan["signature"]!)))throw new InvalidOperationException("Parameter order keeps each native name, type, role and return; no alias is inferred");
    foreach(var plan in callers.Select(p=>p.Value!.AsObject()))if(plan["inputs"] is not JsonObject inputs||inputs.Count!=next.Args.Count(a=>!a.IsOut)||next.Args.Where(a=>!a.IsOut).Any(a=>inputs[a.Name]?.GetValue<string>()!=a.Name)||plan["disconnect"] is not JsonObject disconnect||disconnect.Count!=0||plan.ContainsKey("outputs"))throw new InvalidOperationException("Parameter order retains every caller binding and output identity explicitly");
    orderedFunctions.Add(id);wholeRoleFunctions.Add(id);continue;
   }
   if(referencePins||wholeValue){
    bool refOut=before.Args.Count==next.Args.Count&&before.Args.Where((a,i)=>a.IsRef&&next.Args[i].IsOut).Any();
    bool outRef=before.Args.Count==next.Args.Count&&before.Args.Where((a,i)=>a.IsOut&&next.Args[i].IsRef).Any();
    bool outValue=before.Args.Count==next.Args.Count&&before.Args.Where((a,i)=>a.IsOut&&next.Args[i].Mode is null).Any();
    bool valueOut=before.Args.Count==next.Args.Count&&before.Args.Where((a,i)=>a.Mode is null&&next.Args[i].IsOut).Any();
    if(refOut||outRef||outValue||valueOut){
     // Existing whole-body proof owns the native/public cells. Caller storage,
     // removed inputs and output consumers require explicit original choices.
     if((refOut?1:0)+(outRef?1:0)+(outValue?1:0)+(valueOut?1:0)!=1||mapping.Count!=4||mapping.Any(p=>p.Key is not ("before" or "args" or "bodies" or "callers"))||mapping["bodies"] is not JsonObject bodies||bodies.Count==0||mapping["callers"] is not JsonObject callers||before.Return!=next.Return||before.Args.Where((a,i)=>a.Name!=next.Args[i].Name||a.Type!=next.Args[i].Type||remap[a.Name]?.ToString()!=a.Name||a.Mode!=next.Args[i].Mode&&!(refOut?a.IsRef&&next.Args[i].IsOut:outRef?a.IsOut&&next.Args[i].IsRef:outValue?a.IsOut&&next.Args[i].Mode is null:a.Mode is null&&next.Args[i].IsOut)).Any())throw new InvalidOperationException("Whole ref/out edits retain exact pin identities, types, count, order and return; review one explicit direction and every body and caller");
     var removed=before.Args.Where((a,i)=>(refOut?a.IsRef:a.Mode is null)&&next.Args[i].IsOut).Select(a=>a.Name).ToHashSet(StringComparer.Ordinal);var outputs=FeatureBlueprint.FeatureOutputs(before).ToArray();
     foreach(var plan in callers.Select(p=>p.Value!.AsObject())){
      if(refOut||valueOut){if(plan["inputs"] is not JsonObject inputs||inputs.Count!=next.Args.Count(a=>!a.IsOut)||next.Args.Where(a=>!a.IsOut).Any(a=>inputs[a.Name]?.GetValue<string>()!=a.Name)||plan["disconnect"] is not JsonObject disconnect||disconnect.Count!=removed.Count||disconnect.Any(p=>!removed.Contains(p.Key))||plan["outputs"] is not JsonObject outputMap||outputMap.Count!=outputs.Length||outputs.Any(a=>outputMap[a.Name]?.GetValue<string>()!=a.Name))throw new InvalidOperationException("Select each retained caller binding, exact removed ref input and original compatible output explicitly");}
      else if(plan["inputs"] is not JsonObject inputs||inputs.Count!=next.Args.Count(a=>!a.IsOut)||inputs.Any(p=>!next.Args.Any(a=>!a.IsOut&&a.Name==p.Key))||before.Args.Where((a,i)=>a.IsOut&&next.Args[i].IsRef).Any(a=>inputs[a.Name] is not JsonValue choice||!choice.TryGetValue<string>(out var from)||!before.Args.Any(b=>!b.IsOut&&b.Type==a.Type&&b.Name==from))||plan["disconnect"] is not JsonObject disconnect||disconnect.Count!=0||plan["outputs"] is not JsonObject outputMap||outputMap.Count!=outputs.Length||outputs.Any(a=>{bool converted=before.Args.Any(b=>b.IsOut&&b.Name==a.Name)&&next.Args.Any(b=>!b.IsOut&&b.Name==a.Name);return outputMap[a.Name]?.GetValue<string>()!=(converted?"return":a.Name)||converted&&a.Type!=next.Return;}))throw new InvalidOperationException("Select existing storage for every new ref, all other inputs and compatible return for each old out; no binding or output is inferred");
     }
     wholeRoleFunctions.Add(id);wholeRolePlans.Add(id,callers.DeepClone().AsObject());continue;
    }
    // Existing storage is not a new binding choice. Keep positional types
    // and allow only explicitly reviewed value/ref roles; never infer a cell.
    if(mapping.Count!=2+(mapping["bodies"] is JsonObject?1:0)+(mapping["callers"] is JsonObject?1:0)||mapping.Any(p=>p.Key is not ("before" or "args" or "bodies" or "callers"))||before.Return!=next.Return||before.Args.Count!=next.Args.Count||before.Args.Where((a,i)=>a.Type!=next.Args[i].Type||a.Mode!=next.Args[i].Mode&&(a.Mode is not (null or "ref")||next.Args[i].Mode is not (null or "ref"))||remap[a.Name]?.ToString()!=next.Args[i].Name).Any())throw new InvalidOperationException("Shared ref edits retain positional types, count, return and out roles; review value/ref storage explicitly");
    foreach(var plan in (mapping["callers"] as JsonObject??new()).Select(p=>p.Value!.AsObject()))if(plan["inputs"] is not JsonObject inputs||inputs.Count!=next.Args.Count(a=>!a.IsOut)||before.Args.Where(a=>!a.IsOut).Any(a=>inputs[remap[a.Name]!.ToString()]?.GetValue<string>()!=a.Name)||plan["disconnect"] is not JsonObject disconnect||disconnect.Count!=0||plan.ContainsKey("outputs"))throw new InvalidOperationException("Retain every exact ref/value caller binding; no storage is inferred");
    continue;
   }
   bool inputDefinition=before.Args.Any(a=>!a.IsOut&&remap[a.Name] is null&&!next.Args.Any(b=>!b.IsOut&&b.Name==a.Name))||next.Args.Any(b=>!b.IsOut&&!before.Args.Any(a=>!a.IsOut&&(a.Name==b.Name||remap[a.Name]?.ToString()==b.Name)));
   bool structural=before.Args.Any(a=>a.IsOut&&(remap[a.Name] is null||!next.Args.Any(b=>b.IsOut&&b.Name==remap[a.Name]!.ToString())))||next.Args.Any(b=>b.IsOut&&!before.Args.Any(a=>a.IsOut&&remap[a.Name]?.ToString()==b.Name))||before.Return!=next.Return&&(before.Return=="void"||next.Return=="void");
   if(structural){
    // The existing coordinated graph plan owns writer removal/insertion and
    // void transitions. Explicit input definitions/type replacements keep
    // surviving identities/order and use the original use/value closure.
    var values=before.Args.Where(a=>!a.IsOut).ToArray();var nextValues=next.Args.Where(a=>!a.IsOut).ToArray();
    if((before.Return!="void"&&next.Return!="void"&&before.Return!=next.Return&&!Scalar(before.Return))||(next.Return!="void"&&!Scalar(next.Return)))throw new InvalidOperationException("Shared output definitions require explicit scalar return contracts");
    if(inputDefinition){
     bool identities=values.All(a=>{var b=next.Args.SingleOrDefault(p=>p.Name==a.Name);if(b is null)return Scalar(a.Type)&&remap[a.Name] is null;if(a.Mode!=b.Mode)return false;return a.Type==b.Type?remap[a.Name]?.ToString()==a.Name:Scalar(a.Type)&&Scalar(b.Type)&&remap[a.Name] is null;});
     if(!identities||!values.Where(a=>nextValues.Any(b=>b.Name==a.Name)).Select(a=>a.Name).SequenceEqual(nextValues.Where(b=>values.Any(a=>a.Name==b.Name)).Select(b=>b.Name))||nextValues.Any(b=>!values.Any(a=>a.Name==b.Name)&&(before.Args.Any(a=>a.Name==b.Name)||b.Mode is not null||!Scalar(b.Type))))throw new InvalidOperationException("Explicit input definitions preserve surviving pin identities/order and input/output roles");
     inputDefinitions.Add(id);
    }else if(values.Length!=nextValues.Length||values.Where((a,i)=>{var b=nextValues[i];return a.Mode!=b.Mode||(a.Type==b.Type?remap[a.Name]?.ToString()!=b.Name:a.Name!=b.Name||!Scalar(a.Type)||!Scalar(b.Type)||remap[a.Name] is not null);}).Any())throw new InvalidOperationException("Shared output definitions retain explicit value input identities/order and scalar replacements");
    if(values.Any(a=>nextValues.Any(b=>b.Name==a.Name&&b.Type!=a.Type))){typed=true;inputTypes.Add(id);}
    string MappedName(Parameter p)=>remap[p.Name]?.ToString()??p.Name;
    var retained=before.Args.Where(a=>a.IsOut?remap[a.Name] is not null:nextValues.Any(b=>b.Name==MappedName(a))).ToArray();
    if(retained.Any(a=>a.IsOut&&remap[a.Name]?.ToString()!=a.Name)||!retained.Select(a=>(Name:MappedName(a),a.Mode)).SequenceEqual(next.Args.Where(b=>retained.Any(a=>MappedName(a)==b.Name)).Select(b=>(Name:b.Name,b.Mode)))||retained.Any(a=>{var b=next.Args.Single(p=>p.Name==MappedName(a));return a.Type!=b.Type&&(!Scalar(a.Type)||!Scalar(b.Type));})||next.Args.Any(b=>b.IsOut&&!retained.Any(a=>a.Name==b.Name)&&!Scalar(b.Type)))throw new InvalidOperationException("Explicitly remove old output identities and preserve mapped input/output order and roles");
    if(values.Any(a=>remap[a.Name] is not null&&remap[a.Name]!.ToString()!=a.Name))inputNames.Add(id);
    if(retained.Any(a=>a.IsOut&&next.Args.Any(b=>b.Name==a.Name&&b.Type!=a.Type))){outputTypes.Add(id);outputTyped=true;}
    if(before.Return!="void"&&next.Return!="void"&&before.Return!=next.Return){returns.Add(id);outputTyped=true;}
    structures.Add(id);continue;
   }
   if(inputDefinition){
    // A same-name scalar type replacement is selected exactly like a removed
    // input. Keep surviving identities/order and each retained output ID;
    // the single closure proves new values, old uses and changed writers.
    var surviving=before.Args.Where(a=>next.Args.Any(b=>b.Name==a.Name)).ToArray();
    bool inputIdentities=before.Args.All(a=>{var b=next.Args.SingleOrDefault(p=>p.Name==a.Name);if(b is null)return !a.IsOut&&Scalar(a.Type)&&remap[a.Name] is null;if(a.Mode!=b.Mode)return false;if(a.Type==b.Type)return remap[a.Name]?.ToString()==a.Name;return Scalar(a.Type)&&Scalar(b.Type)&&(a.IsOut?remap[a.Name]?.ToString()==a.Name:remap[a.Name] is null);});
    if(before.Return!=next.Return&&(!Scalar(before.Return)||!Scalar(next.Return))||!before.Args.Where(a=>a.IsOut).Select(a=>(a.Name,a.Mode)).SequenceEqual(next.Args.Where(a=>a.IsOut).Select(a=>(a.Name,a.Mode)))||!inputIdentities||!surviving.Select(a=>a.Name).SequenceEqual(next.Args.Where(b=>before.Args.Any(a=>a.Name==b.Name)).Select(b=>b.Name))||next.Args.Any(b=>!before.Args.Any(a=>a.Name==b.Name)&&(b.Mode is not null||!Scalar(b.Type))))throw new InvalidOperationException("Explicit value input definitions preserve pin identities/order and scalar output/return contracts");
    if(before.Args.Any(a=>!a.IsOut&&next.Args.Any(b=>b.Name==a.Name&&b.Type!=a.Type))){typed=true;inputTypes.Add(id);}
    if(before.Args.Any(a=>a.IsOut&&next.Args.Any(b=>b.Name==a.Name&&b.Type!=a.Type))){outputTyped=true;outputTypes.Add(id);}
    if(before.Return!=next.Return){outputTyped=true;returns.Add(id);}
    inputDefinitions.Add(id);continue;
   }
   if(before.Return!=next.Return){
    // Out and return writers share the explicit output closure. Keep value
    // identities/order here; the loop below proves unchanged maps or explicit
    // scalar input replacements and every retained output identity.
    if(!Scalar(before.Return)||!Scalar(next.Return)||!before.Args.Where(a=>!a.IsOut).Select(a=>(Name:remap[a.Name]?.ToString()??a.Name,a.Mode)).SequenceEqual(next.Args.Where(a=>!a.IsOut).Select(a=>(Name:a.Name,a.Mode))))throw new InvalidOperationException("Shared scalar returns retain explicit value input identities/order/roles");
    returns.Add(id);outputTyped=true;
   }
   if(before.Args.Count!=next.Args.Count)throw new InvalidOperationException("Shared caller batching retains original argument identities outside coordinated output definitions");
   if(before.Args.Where((a,i)=>!a.IsOut&&a.Name!=next.Args[i].Name).Any())inputNames.Add(id);
   for(int i=0;i<before.Args.Count;i++){var a=before.Args[i];var b=next.Args[i];if(a.Mode!=b.Mode)throw new InvalidOperationException("Retain the original input/output roles explicitly");hasOutputs|=a.IsOut;if(a.Type==b.Type){if(remap[a.Name]?.ToString()!=b.Name)throw new InvalidOperationException("Retain each unchanged pin identity explicitly");}else if(a.IsOut){outputTyped=true;outputTypes.Add(id);if(a.Name!=b.Name||!Scalar(a.Type)||!Scalar(b.Type)||remap[a.Name]?.ToString()!=a.Name)throw new InvalidOperationException("Changed scalar outputs retain their explicit original pin identity");}else{typed=true;inputTypes.Add(id);if(a.Mode is not null||a.Name!=b.Name||!Scalar(a.Type)||!Scalar(b.Type)||!remap.ContainsKey(a.Name)||remap[a.Name] is not null)throw new InvalidOperationException("Changed scalar inputs need explicit replacement at the same position and name");}}
  }
  if(orderedFunctions.Count>0&&!functions.SetEquals(orderedFunctions))throw new InvalidOperationException("Review parameter permutations separately from other shared contract changes");
  if(returns.Count>0&&!functions.SetEquals(returns.Concat(outputTypes).Concat(structures).Concat(inputNames).Concat(inputTypes).Concat(inputDefinitions)))throw new InvalidOperationException("Combine only explicit scalar input/output types, definitions or mapped input names; retain every input");
  var projections=new Dictionary<string,JsonObject>(wholeRolePlans,StringComparer.Ordinal);
  if(structures.Count>0){
   if(!functions.SetEquals(structures.Concat(outputTypes).Concat(returns).Concat(inputNames).Concat(inputTypes).Concat(inputDefinitions)))throw new InvalidOperationException("Combine only explicit value input definitions/replacements and output definitions/types; all input retained");
   foreach(var row in edits){var mapping=row!["mapping"]!.AsObject();var before=InformationFunctionBodies.Signature(mapping["before"]!);var next=InformationFunctionBodies.Signature(row["signature"]!);string id=row["id"]!.ToString();bool structure=structures.Contains(id),writers=outputTypes.Contains(id)||returns.Contains(id),inputsChanged=inputTypes.Contains(id)||inputDefinitions.Contains(id),uses=mapping["implementations"] is JsonObject;
    if(inputNames.Contains(id)&&!structure&&!writers&&!inputsChanged){if(mapping.Count!=2||before.Args.Where(a=>a.IsOut).Any(a=>mapping["args"]![a.Name]?.ToString()!=a.Name))throw new InvalidOperationException("A pure value pin rename retains every original output and binding");continue;}
    bool outputsChanged=structure||writers;
    if(mapping.Count!=3+(structure?1:0)+(writers?1:0)+(uses?1:0)||mapping["callers"] is not JsonObject callers||(structure?mapping["outputGraphs"] is not JsonObject:mapping.ContainsKey("outputGraphs"))||(writers?mapping["outputs"] is not JsonObject:mapping.ContainsKey("outputs"))||mapping.ContainsKey("implementations")&&(!inputsChanged||!uses))throw new InvalidOperationException("Select original input uses, graph changes and every changed writer before combining contracts");
    foreach(var plan in callers.Select(p=>p.Value!.AsObject()))if(plan["inputs"] is not JsonObject inputs||inputs.Count!=next.Args.Count(a=>!a.IsOut)||plan["disconnect"] is not JsonObject disconnect||!inputsChanged&&(before.Args.Where(a=>!a.IsOut).Any(a=>inputs[mapping["args"]![a.Name]!.ToString()]?.ToString()!=a.Name)||disconnect.Count!=0)||(outputsChanged?plan["outputs"] is not JsonObject:plan.ContainsKey("outputs")))throw new InvalidOperationException("Select original caller inputs/disconnections and compatible outputs explicitly");
    if(outputsChanged)projections.Add(id,callers.DeepClone().AsObject());
   }
  }else if(inputDefinitions.Count>0){
   if(!functions.SetEquals(inputDefinitions.Concat(inputTypes).Concat(outputTypes).Concat(returns)))throw new InvalidOperationException("Combine only explicit value input definitions and scalar output/return types; retain every input");
   foreach(var row in edits){var mapping=row!["mapping"]!.AsObject();var before=InformationFunctionBodies.Signature(mapping["before"]!);var next=InformationFunctionBodies.Signature(row["signature"]!);string id=row["id"]!.ToString();bool uses=mapping["implementations"] is JsonObject,inputsChanged=inputDefinitions.Contains(id)||inputTypes.Contains(id),outputsChanged=outputTypes.Contains(id)||returns.Contains(id);
    if(mapping.Count!=3+(uses?1:0)+(outputsChanged?1:0)||mapping["callers"] is not JsonObject callers||mapping.ContainsKey("implementations")&&(!inputsChanged||!uses)||(outputsChanged?mapping["outputs"] is not JsonObject:mapping.ContainsKey("outputs"))||mapping.ContainsKey("outputGraphs"))throw new InvalidOperationException("Select original caller bindings, removed input uses and changed output writers explicitly");
    foreach(var plan in callers.Select(p=>p.Value!.AsObject()))if(plan["inputs"] is not JsonObject inputs||inputs.Count!=next.Args.Count(a=>!a.IsOut)||plan["disconnect"] is not JsonObject disconnect||!inputsChanged&&(before.Args.Where(a=>!a.IsOut).Any(a=>inputs[a.Name]?.ToString()!=a.Name)||disconnect.Count!=0)||(outputsChanged?plan["outputs"] is not JsonObject:plan.ContainsKey("outputs")))throw new InvalidOperationException("Select every current input, unused binding removal and compatible output; preserve unchanged bindings");
    if(outputsChanged)projections.Add(id,callers.DeepClone().AsObject());
   }
  }else if(outputTyped||(typed&&hasOutputs)){
   // Each original closure owns its own selections. An input-only edit does
   // not grant an output rebind, nor does an output-only edit replace inputs.
   // Unchanged out pins still require the explicit input closure, not the
   // identity-only out-name path. No output selection is added for them.
   if(typed&&functions.Any(id=>!inputTypes.Contains(id)&&!outputTypes.Contains(id)&&!returns.Contains(id)))throw new InvalidOperationException("Select scalar input/output/return type edits for every grouped function; other input retained");
   foreach(var row in edits){var mapping=row!["mapping"]!.AsObject();var before=InformationFunctionBodies.Signature(mapping["before"]!);var next=InformationFunctionBodies.Signature(row["signature"]!);
    string id=row["id"]!.ToString();bool inputsChanged=inputTypes.Contains(id),outputsChanged=outputTypes.Contains(id)||returns.Contains(id),inputPlans=mapping["implementations"] is JsonObject;
    // A pure rename uses its exact old-pin map and the existing semantic
    // rename path. It cannot smuggle a value, writer or caller re-selection.
    if(inputNames.Contains(id)&&!inputsChanged&&!outputsChanged){if(mapping.Count!=2||before.Args.Where(a=>a.IsOut).Any(a=>mapping["args"]![a.Name]?.ToString()!=a.Name))throw new InvalidOperationException("A pure value pin rename retains every original output and binding");continue;}
    // The UI omits this object when there are no callee uses. Prepare below
    // still checks every original use and rejects any missing replacement.
    if(mapping.Count!=3+(inputPlans?1:0)+(outputsChanged?1:0)||mapping["callers"] is not JsonObject callers||(outputsChanged?mapping["outputs"] is not JsonObject:mapping.ContainsKey("outputs"))||mapping.ContainsKey("implementations")&&(!inputsChanged||!inputPlans)||before.Args.Select((a,i)=>(a.IsOut||typed||!inputNames.Contains(id))&&a.Name!=next.Args[i].Name||!inputsChanged&&!a.IsOut&&a.Type!=next.Args[i].Type).Any(v=>v))throw new InvalidOperationException("Shared scalar outputs retain mapped input identities and require original binding/writer/caller selections");
    foreach(var plan in callers.Select(p=>p.Value!.AsObject()))if(plan["inputs"] is not JsonObject inputs||inputs.Count!=before.Args.Count(a=>!a.IsOut)||plan["disconnect"] is not JsonObject disconnect||!inputsChanged&&(before.Args.Where(a=>!a.IsOut).Any(a=>inputs[mapping["args"]![a.Name]!.ToString()]?.ToString()!=a.Name)||disconnect.Count!=0)||(outputsChanged?plan["outputs"] is not JsonObject:plan.ContainsKey("outputs")))throw new InvalidOperationException("Select exact caller inputs, removed bindings and compatible outputs explicitly");
    if(outputsChanged)projections.Add(id,callers.DeepClone().AsObject());
   }
  }else if((hasOutputs&&(typed||edits.Any(row=>row!["mapping"]!.AsObject().Count!=2)))||edits.Any(row=>row!["mapping"]?["outputs"] is not null))throw new InvalidOperationException("Shared output names retain exact types and automatic identity-preserving bindings; other selected input is retained");
  // Out names propagate the explicit old-pin identity through existing semantic
  // bindings. They never select a different output, rewrite C# or replan values.
  bool independent=wholeOrder||referencePins||wholeValue||typed||hasOutputs||structures.Count>0||inputDefinitions.Count>0||returns.Count>0;
  string ns=PackPaths.Namespace(request["id"]!.ToString());
  foreach(var row in units.Where(p=>p.Value?["kind"]?.ToString()=="implementation")){
   var d=new Parser(row.Value!["draft"]!.ToString(),"<shared-caller-group>").ParseElement();if(!functions.Contains(d.Function!)&&!d.Imports.Values.Any(i=>functions.Contains(i.Id)))continue;
   bool callee=functions.Contains(d.Function!);
   if(independent)foreach(var imported in d.Imports.Values){
    // An unselected local contract is a read dependency, not another edit.
    // Existing closures observe its source and check the exact typed import;
    // the overlay never changes it or infers C# source/argument rewrites.
    if(functions.Contains(imported.Id)){if(callee)throw new InvalidOperationException("Selected callees need their own explicit dependency composition; all input retained");continue;}
    var unit=units[imported.Id];if(!imported.Id.StartsWith(ns+"::",StringComparison.Ordinal)||unit?["kind"]?.ToString()!="function")throw new InvalidOperationException("Shared contract groups retain external import boundaries; all input retained");
    var dependency=new Parser(unit["draft"]!.ToString(),"<unchanged-local-contract>").ParseElement();
    if(dependency.Id!=imported.Id||dependency.Kind!="function"||dependency.Parent is not null||dependency.Signature is null||!imported.Signature.Matches(dependency.Signature))throw new InvalidOperationException("The unselected local import contract changed; all input retained");
   }
   if(d.Parent is not null||d.Bodies.Count is <1 or >8||d.Bodies.Any(b=>b.Value.SourceKind!="blueprint"))throw new InvalidOperationException("Shared caller batching currently requires direct Blueprint targets; original sources retained");
   foreach(var body in d.Bodies){string graphId=d.Id+"/body:"+body.Key;var graph=JsonNode.Parse(units[graphId]?["draft"]?.ToString()??throw new InvalidOperationException("Complete shared caller graph required"))!.AsObject();
    bool ReviewedStorage(JsonNode n)=>referencePins&&callee&&n["kind"]?.ToString()=="code"&&n["forwardCallerStorage"]?.GetValue<bool>()==true&&edits.Single(e=>e!["id"]!.ToString()==d.Function)!["mapping"]?["bodies"]?[graphId+"/node:"+n["id"]] is JsonObject;
    bool ReviewedWhole(JsonNode n)=>callee&&wholeRoleFunctions.Contains(d.Function!)&&InformationFunctionRetained.IsLift(graph)&&n["kind"]?.ToString()=="code"&&n["implementationContext"] is JsonObject&&edits.Single(e=>e!["id"]!.ToString()==d.Function)!["mapping"]?["bodies"]?[graphId+"/node:"+n["id"]] is JsonObject;
    if(graph["copySource"] is not null||graph["nodes"] is not JsonArray nodes||nodes.Any(n=>n is not JsonObject||n["graph"] is not null||n["implementationContext"] is not null&&!ReviewedWhole(n)||n["forwardCallerStorage"] is not null&&!ReviewedStorage(n)||n["postCall"] is not null||n["kind"]?.ToString() is not ("code" or "call" or "export")||n["kind"]?.ToString()!="export"&&n["control"]?.ToString()!="next"))throw new InvalidOperationException("Shared caller batching preserves copy, private, native and wrapper contexts; save those contracts separately");
    if(independent&&(graph["locals"] is JsonArray locals&&locals.Count>0||graph["aliases"] is JsonObject aliases&&aliases.Count>0||nodes.Any(n=>n!["kind"]?.ToString()!=(callee?"code":"call")&&n["kind"]?.ToString()!="export")))throw new InvalidOperationException("Shared type/output edits preserve code-free caller and leaf callee contexts; retain all input");
   }
  }
  // Prove every original selection before composing anything. No user consent
  // is rebased onto a changed live source, and no intermediate result is saved.
  if(independent)foreach(var row in edits){var original=new Parser(units[row!["id"]!.ToString()]!["draft"]!.ToString(),"<original-group-contract>").ParseElement();var next=new Parser(units[original.Id]!["draft"]!.ToString(),"<group-contract>").ParseElement();DeclarationAuthoring.Apply(next,new JsonObject{["action"]="signature",["value"]=row["signature"]!.DeepClone()});InformationFunctionContracts.Prepare(request,original,next,row["mapping"]!.AsObject(),format);}
  return new(request,functions,wholeOrder||referencePins||wholeValue||typed||outputTyped||structures.Count>0||inputDefinitions.Count>0,projections);
 }
 public JsonObject MappingFor(string function,JsonObject mapping)
 {
  if(!composeCallers)return mapping;
  var prepared=mapping.DeepClone().AsObject();
  foreach(var entry in prepared["callers"] as JsonObject??new JsonObject()){
   var plan=entry.Value!.AsObject();string id=plan["graph"]!.ToString();string initial=originalUnits[id]!["draft"]!.ToString(),current=Request["units"]![id]!["draft"]!.ToString();
   if(plan["hash"]?.ToString()!=Hash(initial))throw new InvalidOperationException("Original shared caller selection changed; retain all input");
   if(initial==current)continue;
   var original=JsonNode.Parse(initial)!.AsObject();var before=original.DeepClone().AsObject();var after=JsonNode.Parse(current)!.AsObject();ProjectOutputs(id,before);string nodeId=plan["node"]!.ToString();
   JsonNode? Selected(JsonObject graph)=>graph["nodes"]!.AsArray().SingleOrDefault(n=>n!["id"]?.ToString()==nodeId&&n["feature"]?.ToString()==function);
   if(Selected(before) is null||!JsonNode.DeepEquals(Selected(before),Selected(after)))throw new InvalidOperationException("Selected shared call changed; repeat the explicit selection");
   void MaskOtherCalls(JsonObject graph){foreach(var node in graph["nodes"]!.AsArray().OfType<JsonObject>())if(node["kind"]?.ToString()=="call"&&node["feature"]?.ToString() is string target&&target!=function&&functions.Contains(target)){node.Remove("signature");node.Remove("arguments");}}
   MaskOtherCalls(before);MaskOtherCalls(after);
   if(!JsonNode.DeepEquals(before,after))throw new InvalidOperationException("Shared graph changed outside the prepared independent calls; retain every input");
   // Earlier explicit output choices can move a binding that THIS caller will
   // explicitly disconnect. Preserve the original proof; project only that
   // proved binding onto the verified internal overlay, never a changed source.
   foreach(var pair in (plan["disconnect"] as JsonObject??new JsonObject()).ToArray()){
    var initialArgs=Selected(original)!["arguments"]!.AsObject();var projectedArgs=Selected(before)!["arguments"]!.AsObject();
    if(!initialArgs.ContainsKey(pair.Key)||pair.Value?.GetValue<string>()!=(initialArgs[pair.Key]?.ToJsonString()??"null")||!projectedArgs.ContainsKey(pair.Key))throw new InvalidOperationException("Original disconnected binding changed; retain every input");
    plan["disconnect"]![pair.Key]=projectedArgs[pair.Key]?.ToJsonString()??"null";
   }
   // This hash names only our verified internal overlay. Final updates and CAS
   // still carry the original request's source identity and checkpoint version.
   plan["hash"]=Hash(current);
  }
  completed.Add(function);return prepared;
 }
 void ProjectOutputs(string id,JsonObject graph)
 {
  // Apply only earlier, independently proved producer choices to a clone of
  // the ORIGINAL graph. This is not consent to a changed live caller/source.
  foreach(string function in completed){if(!outputPlans.TryGetValue(function,out var plans))continue;
   foreach(var plan in plans.Select(p=>p.Value!.AsObject()).Where(p=>p["graph"]?.ToString()==id)){
    string nodeId=plan["node"]!.ToString();if(!graph["nodes"]!.AsArray().Any(n=>n!["id"]?.ToString()==nodeId&&n["feature"]?.ToString()==function))throw new InvalidOperationException("Original producer identity changed; retain every input");
    var outputs=plan["outputs"]!.AsObject();void Rebind(JsonNode? value){if(value is JsonObject o){if(o["node"]?.ToString()==nodeId){string name=o["output"]?.ToString()??"return",to=outputs[name]?.GetValue<string>()??throw new InvalidOperationException("An explicitly disconnected output is still consumed");if(to==name)return;if(to=="return")o.Remove("output");else o["output"]=to;return;}foreach(var p in o.ToArray())if(p.Key!="constant")Rebind(p.Value);}else if(value is JsonArray array)foreach(var v in array)Rebind(v);}
    InformationFunctionGraphs.Bindings(graph,Rebind);
   }
  }
 }
 public void Stage(string id,string text){var unit=Request["units"]![id]??throw new InvalidOperationException("Observed shared contract source missing");unit["draft"]=text;}
 public void Merge(JsonArray updates,JsonObject update)
 {
  string id=update["id"]!.ToString();var initial=originalUnits[id]??throw new InvalidOperationException("Original shared source missing");var current=Request["units"]![id]??throw new InvalidOperationException("Current shared source missing");
  if(update["kind"]?.ToString()!=initial["kind"]?.ToString()||update["path"]?.ToString()!=initial["path"]?.ToString()||update["hash"]?.ToString()!=Hash(current["draft"]!.ToString()))throw new InvalidOperationException("Shared source identity or preparation basis changed; no candidate applied");
  var prior=updates.SingleOrDefault(row=>row!["id"]?.ToString()==id);var merged=update.DeepClone().AsObject();merged["hash"]=Hash(initial["draft"]!.ToString());
  if(prior is null)updates.Add(merged);else updates[updates.IndexOf(prior)]=merged;
  if(updates.Count>64)throw new ArgumentException("Combined function usage closure budget");
  Stage(id,update["text"]!.ToString());
 }
 static string Hash(string text)=>JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(text));
}
