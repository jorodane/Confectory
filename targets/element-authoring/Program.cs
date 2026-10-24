using Confectory.Core;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

try
{
    var request=JsonNode.Parse(Console.In.ReadToEnd())!.AsObject();
    string S(string name)=>request[name]!.GetValue<string>();
    JsonNode? reply;
    switch(S("operation"))
    {
        case "editorMenuDeclarations":reply=EditorMenuDeclarations.Query(request);break;
        case "outputsDescribe": case "outputsValidate": case "outputsBuild": case "outputsLast":
            reply=BuildParticipationOperations.Execute(S("operation"),request);break;
        case "packSource": case "packManifest": case "packUsage":
            reply=PackOperations.Execute(S("operation"),request,FormatManifest);break;
        case "featureBlueprintNodes": case "featureBlueprintDescribe": case "featureBlueprintAssemble":reply=FeatureBlueprint.Execute(request);break;
        case "blueprintDescribeOwned":reply=BlueprintDocuments.DescribeOwned(request);break;
        case "blueprintEnumPreview":reply=BlueprintEnumContract.Preview(request["contract"]!.AsObject(),request["binding"]!.AsObject());break;
        case "blueprintConversion":reply=BlueprintConversion.Query(request);break;
        case "blueprintPrepareFeature":reply=BlueprintCreation.Prepare(request,Format);break;
        case "blueprintPrepareImplementation":reply=BlueprintCreation.PrepareForOwner(request,Format);break;
        case "blueprintRootContract":reply=BlueprintRootContract.Prepare(request,Format);break;
        case "blueprintRootGroup":reply=BlueprintRootGroup.Validate(request);break;
        case "blueprintOutputSnapshot":reply=BlueprintOutputSnapshot.Prepare(new Parser(S("functionText"),"<published-output-contract>").ParseElement(),request["expected"]?.GetValue<string>());break;
        case "blueprintCallWrapper":reply=BlueprintCallWrapper.Prepare(new Parser(S("functionText"),"<wrapper-contract>").ParseElement(),request["executionEnum"]!.AsObject(),request["expected"]?.GetValue<string>(),request["source"]?.GetValue<string>(),request["helpers"]?.GetValue<string>()??"",request["returnMapping"]?.GetValue<string>());break;
        case "blueprintCallAfter":reply=BlueprintCallAfter.Prepare(new Parser(S("functionText"),"<post-call-contract>").ParseElement(),request["expected"]?.GetValue<string>(),request["source"]?.GetValue<string>(),request["helpers"]?.GetValue<string>()??"");break;
        case "blueprintCallAbi":reply=BlueprintCallAbi.Prepare(request,Format);break;
        case "blueprintCallAbiGroup":reply=BlueprintCallAbiGroup.Prepare(request,Format);break;
        case "blueprintCopyAbiBinding":reply=BlueprintCopyAbi.Bind(request);break;
        case "mixedOwnerCopyEdits":reply=MixedOwnerCopyEdits.Prepare(request,Format,FormatManifest);break;
        case "informationTypes":reply=InformationTypes.Query(request,FormatManifest);break;
        case "informationFunctionInputUses":reply=InformationFunctionInputUses.Read(request);break;
        case "informationFunctionInputs":reply=InformationFunctionContracts.Inputs(request);break;
        case "informationFunctionOutputs":reply=InformationFunctionOutputs.Read(request);break;
        case "informationFunctionOutputGraphs":reply=InformationFunctionOutputs.Graphs(request);break;
        case "informationDefinitions":reply=InformationDefinitions.Prepare(request,Format,FormatManifest);break;
        case "informationFunctionRetirement":reply=InformationFunctionRetirement.Execute(request,Format,FormatManifest);break;
        case "rawOwnerEdits":reply=RawOwnerEdits.Prepare(request,Format,FormatManifest);break;
        case "mergeDeclarationText":reply=JsonValue.Create(DeclarationTextMerge.Merge(S("text"),S("typed"),S("raw"),Format));break;
        case "blueprintAliases":reply=BlueprintAliases.Prepare(request);break;
        case "blueprintInputAdaptation":reply=BlueprintInputAdaptation.Prepare(request);break;
        case "blueprintFeatureBodies":reply=BlueprintFeatureBodies.Query(request);break;
        case "blueprintPrepareCall":reply=BlueprintCall.Prepare(request,Format);break;
        case "blueprintPropertyCatalog":reply=BlueprintProperty.Query(request);break;
        case "blueprintPrepareProperty":reply=BlueprintProperty.Prepare(request,Format);break;
        case "blueprintCallableContracts":reply=BlueprintCallableContracts.Query(request);break;
        case "blueprintSourceValidate":reply=BlueprintDocuments.Validate(S("id"),S("kind"),S("text"));break;
        case "browserFolderMove":case "browserFolderValidate":reply=BrowserFolderLayout.Execute(request,Format,S("operation")=="browserFolderValidate");break;
        case "relationsMap":reply=RelationMapBatch.Query(request);break;
        case "bodyUnits":reply=BodyUnitMetadata.Query(request);break;
        case "describe":
        {
            string project=Path.GetFullPath(S("project")),root=Path.GetDirectoryName(project)!;
            var manifest=new Parser(File.ReadAllText(project),project).ParseManifest();

            var units=new JsonArray();
            units.Add(new JsonObject{["id"]=manifest.Namespace+(manifest.Kind=="project"?"::ProjectManifest":"::PackManifest"),["kind"]=manifest.Kind,["path"]=Path.GetFileName(project)});
            void AddOwned(Manifest owner,string manifestPath,bool pin)
            {
                if(pin)units.Add(new JsonObject{["id"]=owner.Namespace+"::PackManifest",["kind"]="pack",["path"]=Path.GetRelativePath(root,manifestPath)});
                foreach(var (name,locator) in owner.Elements)
                {
                    string path=Owned(root,Path.GetRelativePath(root,Path.Combine(Path.GetDirectoryName(manifestPath)!,locator.Path)));if(request["metadataOnly"]?.GetValue<bool>()==true&&locator.Kind!="implementation"){units.Add(new JsonObject{["id"]=owner.Namespace+"::"+name,["kind"]=locator.Kind,["path"]=Path.GetRelativePath(root,path)});continue;}var element=new Parser(File.ReadAllText(path),path).ParseElement();
                    if(element.Id!=owner.Namespace+"::"+name||element.Kind!=locator.Kind)throw new ArgumentException("Manifest/declaration identity mismatch.");
                    units.Add(new JsonObject{["id"]=element.Id,["kind"]=element.Kind,["path"]=Path.GetRelativePath(root,path)});
                    foreach(var (target,body) in element.Bodies)
                    {
                        string bodyPath=Owned(root,Path.GetRelativePath(root,Path.Combine(Path.GetDirectoryName(manifestPath)!,body.Path)));
                        units.Add(new JsonObject{["id"]=element.Id+"/body:"+target,["kind"]=body.SourceKind=="blueprint"?"blueprint":"body",["path"]=Path.GetRelativePath(root,bodyPath)});
                        if(body.SourceKind=="blueprint")foreach(var node in BlueprintDocuments.NodeUnits(root,bodyPath,element.Id+"/body:"+target))units.Add(node!.DeepClone());
                    }
                }
            }
            AddOwned(manifest,project,false);
            string lockPath=Path.Combine(root,".pack-lock.json");
            if(File.Exists(lockPath))
            {
                var pins=JsonNode.Parse(File.ReadAllText(lockPath))!["pins"]!.AsObject();
                foreach(var (ns,pin) in pins.OrderBy(x=>x.Key,StringComparer.Ordinal))
                {
                    if(pin?["editable"]?.GetValue<bool>()!=true||!manifest.Registry.TryGetValue(ns,out var registration))continue;
                    string owned=Owned(root,registration.Path);if(Path.GetFullPath(Path.Combine(root,pin["path"]!.GetValue<string>()))!=owned)throw new ArgumentException("Editable pin registration mismatch.");
                    var pack=new Parser(File.ReadAllText(owned),owned).ParseManifest();if(pack.Kind!="pack"||pack.Namespace!=ns)throw new ArgumentException("Editable pin namespace mismatch.");AddOwned(pack,owned,true);
                }
            }
            reply=new JsonObject{["project"]=project,["namespace"]=manifest.Namespace,["kind"]=manifest.Kind,["supportsStandalone"]=manifest.SupportsStandalone,["units"]=units};break;
        }
        case "projectionBrowse": case "projectionDelta":reply=ProjectionDelivery.Execute(S("operation"),request);break;
        case "projectionAffected": case "projectionVersions": case "projectionQueue": case "projectionPublish": case "projectionQuery": case "projectionList": case "editorDescribe":reply=ProjectionArtifacts.Execute(S("operation"),request);break;
        case "algorithmProject":reply=AlgorithmProjectionOperations.Execute(request);break;
        case "connectionCatalog": case "connectionSettings": case "connectionSettingsRepair":
            reply=ConnectionDeclarations.Query(S("project"),S("operation")=="connectionCatalog"?null:S("id"),FormatManifest,path=>{var file=new FileInfo(path);if(!file.Exists||file.Length>1048576||file.LinkTarget is not null)throw new IOException("Connection declaration unavailable");return path;},S("operation")=="connectionSettingsRepair"?request:null);break;
        case "catalog":
            reply=SemanticCatalogService.Query(S("project"),request["request"]!.AsObject(),path=>{var file=new FileInfo(path);if(!file.Exists||file.Length>1048576||file.LinkTarget is not null)throw new IOException("Owned document unavailable");return path;});break;
        case "effective":
            reply=EffectiveMetadata.Query(S("project"),S("manifest"),S("id"),S("text"),FormatManifest,path=>{if(new FileInfo(path).Length>1048576)throw new IOException("Manifest budget");return File.ReadAllText(path);},request["drafts"]?.AsArray(),request["schemaView"]?.GetValue<bool>()==true,request["validateObjects"]?.GetValue<bool>()==true,request["observeSources"]?.GetValue<bool>()==true,request["definitionTypes"]?.GetValue<bool>()==true);break;
        case "implementationCopy":reply=ImplementationCopy.Query(request,Format);break;
        case "privateCopySeed":reply=PrivateImplementationCopy.Validate(request);break;
        case "referenceDefinition":
            reply=ReferenceDefinition.Query(S("project"),S("manifest"),S("sourceId"),S("text"),S("id"),path=>{var file=new FileInfo(path);if(!file.Exists||file.Length>1048576||file.LinkTarget is not null)throw new IOException("Definition unavailable");return File.ReadAllText(path,new System.Text.UTF8Encoding(false,true));});break;
        case "locate":
            reply=RelationLocators.Query(S("manifest"),Path.GetDirectoryName(Path.GetFullPath(S("project")))!,request["ids"]!.AsArray().Select(x=>x!.GetValue<string>()).ToArray(),path=>{var file=new FileInfo(path);if(!file.Exists||file.Length>1048576||file.LinkTarget is not null)throw new IOException("Manifest unavailable");return File.ReadAllText(path);});break;
        case "reviewSummary":reply=ReviewSummary(S("kind"),S("before"),S("after"));break;
        case "inspectManifest":reply=ManifestMetadata.Inspect(S("text"));break;
        case "inspect":
        {
            var element=new Parser(S("text"),"<draft>").ParseElement();
            reply=new JsonObject{["id"]=element.Id,["kind"]=element.Kind,["parent"]=element.Parent,["function"]=element.Function,["descriptionDefined"]=element.DescriptionPresent,["relations"]=DeclaredRelations.Describe(element),["description"]=element.Description,["signature"]=JsonSerializer.SerializeToNode(element.Signature),["editor"]=AlgorithmProjectionOperations.Editor(element),["fields"]=JsonSerializer.SerializeToNode(element.Fields),["data"]=JsonSerializer.SerializeToNode(element.Data),["values"]=JsonSerializer.SerializeToNode(element.Values.ToDictionary(x=>x.Key,x=>x.Value.Value))};break;
        }
        case "unregisterDeclarations":
        {
            var manifest=new Parser(S("text"),"<owned-registration>").ParseManifest();var entries=request["entries"]!.AsArray();if(entries.Count is <1 or >32)throw new ArgumentException("Bounded declaration group required");var seen=new HashSet<string>(StringComparer.Ordinal);
            foreach(var row in entries){string id=row!["id"]!.GetValue<string>(),prefix=manifest.Namespace+"::";if(!id.StartsWith(prefix,StringComparison.Ordinal)||!seen.Add(id)||!manifest.Elements.TryGetValue(id[prefix.Length..],out var locator)||locator.Kind!=row["kind"]!.ToString()||locator.Path!=row["path"]!.ToString())throw new ArgumentException("Exact owned declaration registration required");manifest.Elements.Remove(id[prefix.Length..]);}string formatted=FormatManifest(manifest);string? prior=request["prior"]?.GetValue<string>();if(prior is not null&&FormatManifest(new Parser(prior,"<checkpoint-registration>").ParseManifest())==formatted)formatted=prior;reply=JsonValue.Create(formatted);break;
        }
        case "editDeclaration":
        {
            var element=new Parser(S("text"),"<draft>").ParseElement();string id=element.Id,kind=element.Kind;
            if(kind is not ("category" or "concept" or "function" or "module" or "object" or "schema" or "implementation"))throw new ArgumentException("Authored declaration required");
            DeclarationAuthoring.Apply(element,request["edit"]?.AsObject()??throw new ArgumentException("Declaration edit required"));
            string formatted=Format(element);var parsed=new Parser(formatted,"<draft>").ParseElement();
            if(parsed.Id!=id||parsed.Kind!=kind)throw new ArgumentException("Stable declaration ID and kind required");
            reply=JsonValue.Create(formatted);break;
        }
        case "setDataPath": case "setField": case "setData":
        {
            var element=new Parser(S("text"),"<draft>").ParseElement();if(S("operation")=="setDataPath")SchemaContracts.SetDataPath(element,JsonSerializer.SerializeToElement(request["path"]),JsonSerializer.SerializeToElement(request["value"]));else if(S("operation")=="setField")SchemaContracts.SetField(element,S("field"),JsonSerializer.SerializeToElement(request["value"]));else SchemaContracts.SetData(element,S("field"),JsonSerializer.SerializeToElement(request["value"]));string formatted=Format(element);new Parser(formatted,"<draft>").ParseElement();reply=JsonValue.Create(formatted);break;
        }
        case "setDescription":
        {
            var element=new Parser(S("text"),"<draft>").ParseElement();
            element.Description=request["value"]?.GetValue<string>()??throw new ArgumentException("Description string required.");element.DescriptionPresent=true;
            string formatted=Format(element);new Parser(formatted,"<draft>").ParseElement();reply=JsonValue.Create(formatted);break;
        }
        case "setValue":
        {
            var element=new Parser(S("text"),"<draft>").ParseElement();var value=JsonSerializer.SerializeToElement(request["value"]);
            if(value.ValueKind is not (JsonValueKind.String or JsonValueKind.Number or JsonValueKind.True or JsonValueKind.False))throw new ArgumentException("Scalar metadata required.");
            element.Values[S("field")]=new(value,element.Id,new());string formatted=Format(element);new Parser(formatted,"<draft>").ParseElement();reply=JsonValue.Create(formatted);break;
        }
        case "create":
        {
            string kind=S("kind"),id=S("id");if(kind is not ("category" or "concept" or "function" or "module" or "object" or "schema"))throw new ArgumentException("Unsupported authored kind.");
            string text=$"{kind} {id}"+(kind=="function"?" () -> int":"")+" { }\n";
            new Parser(text,"<new>").ParseElement();reply=JsonValue.Create(text);break;
        }
        case "register":
        {
            var manifest=new Parser(S("text"),"<draft>").ParseManifest();string id=S("id");
            if(!id.StartsWith(manifest.Namespace+"::",StringComparison.Ordinal))throw new ArgumentException("Creation belongs to selected project namespace.");
            string name=id[(manifest.Namespace.Length+2)..];manifest.Elements.Add(name,new(S("kind"),S("path"),new()));
            string text=DeclarationTextMerge.MergeManifest(S("text"),FormatManifest(manifest),FormatManifest);new Parser(text,"<draft>").ParseManifest();reply=JsonValue.Create(text);break;
        }
        case "prepare":
        {
            string original=Path.GetFullPath(S("original")),candidate=Path.GetFullPath(S("candidate"));
            var manifest=new Parser(File.ReadAllText(candidate),candidate).ParseManifest();
            foreach(var ns in manifest.Registry.Keys.ToArray())
            {
                string originalRoot=Path.GetDirectoryName(original)!,resolved=Path.GetFullPath(Path.Combine(originalRoot,manifest.Registry[ns].Path));
                string prefix=originalRoot.TrimEnd(Path.DirectorySeparatorChar)+Path.DirectorySeparatorChar;
                if(resolved.StartsWith(prefix,OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal))resolved=Path.Combine(Path.GetDirectoryName(candidate)!,Path.GetRelativePath(originalRoot,resolved));
                manifest.Registry[ns]=manifest.Registry[ns] with{Path=resolved};
            }
            foreach(var item in request["additions"]!.AsArray())
            {
                string path=item!["path"]!.GetValue<string>(),kind=item["kind"]!.GetValue<string>(),id=item["id"]!.GetValue<string>();
                if(!id.StartsWith(manifest.Namespace+"::",StringComparison.Ordinal))throw new ArgumentException("Creation belongs to the selected project namespace.");
                string name=id[(manifest.Namespace.Length+2)..];manifest.Elements.Add(name,new(kind,path,new()));
            }
            reply=JsonValue.Create(FormatManifest(manifest));break;
        }
        case "run":
        {
            string project=S("project");var manifest=new Parser(File.ReadAllText(project),project).ParseManifest();if(manifest.Kind!="project"||!manifest.SupportsStandalone)throw new ArgumentException("Selected pack does not support standalone execution");var built=new Builder(project,S("target")).Build();var command=built["run"]!.AsArray().Select(x=>x!.GetValue<string>()).ToArray();
            var start=new System.Diagnostics.ProcessStartInfo(command[0]){UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true};foreach(string part in command.Skip(1))start.ArgumentList.Add(part);
            using var process=System.Diagnostics.Process.Start(start)??throw new InvalidOperationException("Preview process did not start.");
            var output=process.StandardOutput.ReadToEndAsync();var errors=process.StandardError.ReadToEndAsync();
            if(!process.WaitForExit(15000)){process.Kill(true);process.WaitForExit();throw new TimeoutException("Preview stopped after 15 seconds.");}
            reply=new JsonObject{["exit"]=process.ExitCode,["stdout"]=output.GetAwaiter().GetResult(),["stderr"]=errors.GetAwaiter().GetResult()};break;
        }
        case "checkBlueprintNode":
        {
            reply = new Builder(S("project"), S("target")).CheckBlueprintNode(S("implementation"), S("bodyTarget"), S("node")); break;
        }
        case "validate":
        {
            string candidate=S("project");var manifest=new Parser(File.ReadAllText(candidate),candidate).ParseManifest();
            if(manifest.Kind=="pack"){foreach(var (name,unit) in manifest.Elements){string path=PackPaths.Owned(Path.GetDirectoryName(candidate)!,unit.Path);var element=new Parser(File.ReadAllText(path),path).ParseElement();if(element.Id!=manifest.Namespace+"::"+name||element.Kind!=unit.Kind)throw new ArgumentException("Pack unit identity mismatch");foreach(var body in element.Bodies.Values)File.ReadAllText(PackPaths.Owned(Path.GetDirectoryName(candidate)!,body.Path));}reply=new JsonObject{["state"]="valid",["level"]="owned-syntax-only",["linkValidated"]=false};break;}
            var builder=new Builder(candidate,S("target"));builder.Validate();builder.Check(builder.Registry.Project.Namespace);builder.Build();
            reply=new JsonObject{["state"]="valid"};break;
        }
        default:throw new ArgumentException("Unknown authoring operation.");
    }
    Console.Write(JsonSerializer.Serialize(new{ok=true,result=reply}));return 0;
}
catch(Exception error)
{
    Console.Write(JsonSerializer.Serialize(new{ok=false,code=error is BuildError build?build.Diagnostic.Code:"AUTHORING",message=error.Message,namespaceDiagnostic=NamespaceDiagnostic.From(error as BuildError)}));return 0;
}
static string Owned(string root,string relative)
{
    string full=Path.GetFullPath(Path.Combine(root,relative));
    if(Path.IsPathRooted(relative)||!full.StartsWith(root.TrimEnd(Path.DirectorySeparatorChar)+Path.DirectorySeparatorChar,OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal))throw new ArgumentException("Editable unit is outside project-owned root.");
    for(string? part=full;part is not null&&part.Length>=root.Length;part=Path.GetDirectoryName(part))
        if((File.Exists(part)||Directory.Exists(part))&&(File.GetAttributes(part)&FileAttributes.ReparsePoint)!=0)throw new ArgumentException("Editable units cannot traverse symlinks.");
    return full;
}
static string Quote(string text)=>JsonSerializer.Serialize(text);
static string Signature(FunctionSignature signature,bool named)=>signature.Format(named);
static string Format(Element element)
{
    var text=new StringBuilder(element.Kind+" "+element.Id);
    if(element.Kind=="implementation")text.Append(" for "+element.Function);
    if(element.Signature is not null)text.Append(" "+Signature(element.Signature,true));
    if(element.Parent is not null)text.Append(" extends "+element.Parent);
    text.AppendLine(" {");
    if(element.DescriptionPresent)text.AppendLine("description "+Quote(element.Description)+";");
    foreach(var value in element.Modules)text.AppendLine("module "+value.Id+";");
    foreach(var value in element.Includes)text.AppendLine("include "+value.Id+";");
    foreach(var (id,value) in element.Requires)text.AppendLine("require "+id+" "+Signature(value.Signature,false)+";");
    foreach(var (id,value) in element.Defaults)text.AppendLine("default "+id+" with "+value.Id+";");
    foreach(var (id,value) in element.Provides)text.AppendLine("provide "+id+" with "+value.Id+";");
    foreach(var value in element.Uses)text.AppendLine("use "+value.Kind+" "+value.Id+";");
    foreach(var value in element.Contains)text.AppendLine("contain "+value.Kind+" "+value.Id+";");
    text.Append(SchemaContracts.FormatDeclarations(element));
    foreach(var (name,value) in element.Values)text.AppendLine("value "+name+" = "+value.Value.GetRawText()+";");
    foreach(var (alias,value) in element.Imports)text.AppendLine("import "+value.Id+" as "+alias+" "+Signature(value.Signature,false)+(value.Scope is null?"":" in "+value.Scope)+";");
    foreach(var (target,value) in element.Bodies)text.AppendLine((value.SourceKind=="blueprint"?"blueprint":"body")+" "+target+" "+Quote(value.Path)+";");
    if(element.Tool is not null)text.AppendLine("tool "+Quote(element.Tool)+";");
    foreach(var (name,value) in element.Options)text.AppendLine("option "+name+" "+Quote(value)+";");
    return text.AppendLine("}").ToString();
}
static string FormatManifest(Manifest manifest)
{
    var text=new StringBuilder(manifest.Kind+" "+manifest.Namespace+" version "+Quote(manifest.Version)+" {\n");
    if(manifest.Description!="")text.AppendLine("description "+Quote(manifest.Description)+";");
    if(manifest.Standalone is not null)text.AppendLine("standalone "+(manifest.Standalone.Value?"true":"false")+";");
    if(manifest.Entry is not null)text.AppendLine("entry "+manifest.Entry+";");
    foreach(var (id,value) in manifest.Registry)text.AppendLine("registry "+id+" "+Quote(value.Path)+";");
    foreach(var (id,value) in manifest.Dependencies)text.AppendLine("dependency "+id+" version "+Quote(value.Version)+";");
    foreach(var (id,value) in manifest.Targets)text.AppendLine("target "+id+" "+value.Id+";");
    foreach(var value in manifest.Always)text.AppendLine("always "+value.Id+";");
    foreach(var (id,value) in manifest.Elements)text.AppendLine("element "+id+" "+value.Kind+" "+Quote(value.Path)+";");
    return text.AppendLine("}").ToString();
}

static JsonObject ReviewSummary(string kind,string before,string after)
{
 var changes=new JsonArray();bool additional=false;
 void Add(string label,JsonNode? oldValue,JsonNode? newValue,bool beforeDefined=true,bool afterDefined=true)=>changes.Add(new JsonObject{["label"]=label,["before"]=oldValue,["after"]=newValue,["beforeDefined"]=beforeDefined,["afterDefined"]=afterDefined});
 string Comments(string text)=>string.Join("\n",System.Text.RegularExpressions.Regex.Matches(text,@"""(?:[^""\\]|\\.)*""|(?<comment>//[^\n]*)").Cast<System.Text.RegularExpressions.Match>().Where(m=>m.Groups["comment"].Success).Select(m=>m.Value));
 JsonNode? Datum(SchemaDatum value)=>value.Kind=="reference"?new JsonObject{["참조 대상"]=value.Reference}:value.Items is not null?new JsonArray(value.Items.Select(Datum).ToArray()):value.Members is not null?new JsonObject(value.Members.Select(x=>new KeyValuePair<string,JsonNode?>(x.Key,Datum(x.Value)))):value.Scalar is not null?JsonNode.Parse(value.Scalar.Value.GetRawText()):null;
 try{
  if(kind is "project" or "pack"){
   var old=new Parser(before,"<review>").ParseManifest();var next=new Parser(after,"<review>").ParseManifest();
   foreach(var item in next.Elements)if(!old.Elements.ContainsKey(item.Key))Add("프로젝트에 등록",null,JsonValue.Create(item.Key+" · "+item.Value.Kind),false,true);
   foreach(var item in old.Elements)if(!next.Elements.ContainsKey(item.Key))Add("프로젝트 등록 해제",JsonValue.Create(item.Key+" · "+item.Value.Kind),null,true,false);
   foreach(var item in next.Elements)if(old.Elements.TryGetValue(item.Key,out var prior)&&(prior.Path!=item.Value.Path||prior.Kind!=item.Value.Kind))additional=true;
   additional|=!old.Elements.Keys.Where(k=>next.Elements.ContainsKey(k)).SequenceEqual(next.Elements.Keys.Where(k=>old.Elements.ContainsKey(k)));next.Elements=old.Elements;additional|=FormatManifest(next)!=FormatManifest(old)||Comments(before)!=Comments(after);
  }else if(kind is "body" or "blueprint" or "blueprint-node")additional=true;
  else{
   bool created=before.Length==0;var next=new Parser(after,"<review>").ParseElement();var old=created?new Element{Kind=next.Kind,Id=next.Id}:new Parser(before,"<review>").ParseElement();
   if(created)Add(kind=="object"?"개념 생성":kind=="schema"?"스키마 생성":"선언 생성",null,JsonValue.Create(next.Id.Split("::").Last()),false,true);
   // Explain declaration contracts without hiding changes to bodies, tools, identity or comments.
   void Contract(string label,JsonNode? prior,JsonNode? current){if(!JsonNode.DeepEquals(prior,current))Add(label,prior,current,prior is not null,current is not null);}
   JsonNode? Sig(FunctionSignature? signature)=>signature is null?null:JsonValue.Create(Signature(signature,true));
   JsonArray Refs(IEnumerable<ElementReference> refs)=>new(refs.Select(r=>(JsonNode)new JsonObject{["대상"]=r.Id,["종류"]=r.Kind}).ToArray());
   JsonArray Bindings(Dictionary<string,ElementReference> refs)=>new(refs.Select(r=>(JsonNode)new JsonObject{["기능"]=r.Key,["구현"]=r.Value.Id}).ToArray());
   JsonArray Requirements(Dictionary<string,RequiredFunction> refs)=>new(refs.Select(r=>(JsonNode)new JsonObject{["기능"]=r.Key,["계약"]=Sig(r.Value.Signature)}).ToArray());
   JsonArray Imports(Dictionary<string,Import> refs)=>new(refs.Select(r=>(JsonNode)new JsonObject{["별칭"]=r.Key,["기능"]=r.Value.Id,["계약"]=Sig(r.Value.Signature),["범위"]=r.Value.Scope}).ToArray());
   Contract("기능 계약",Sig(old.Signature),Sig(next.Signature));Contract("부모",JsonValue.Create(old.Parent),JsonValue.Create(next.Parent));
   Contract("모듈",Refs(old.Modules),Refs(next.Modules));Contract("포함",Refs(old.Includes),Refs(next.Includes));Contract("필요 기능",Requirements(old.Requires),Requirements(next.Requires));
   Contract("기본 구현",Bindings(old.Defaults),Bindings(next.Defaults));Contract("제공 구현",Bindings(old.Provides),Bindings(next.Provides));Contract("사용 관계",Refs(old.Uses),Refs(next.Uses));Contract("소속 관계",Refs(old.Contains),Refs(next.Contains));Contract("외부 기능",Imports(old.Imports),Imports(next.Imports));
   next.Signature=old.Signature;next.Parent=old.Parent;next.Modules=old.Modules;next.Includes=old.Includes;next.Requires=old.Requires;next.Defaults=old.Defaults;next.Provides=old.Provides;next.Uses=old.Uses;next.Contains=old.Contains;next.Imports=old.Imports;
   if(old.Description!=next.Description||old.DescriptionPresent!=next.DescriptionPresent)Add("설명",old.DescriptionPresent?JsonValue.Create(old.Description):null,next.DescriptionPresent?JsonValue.Create(next.Description):null,old.DescriptionPresent,next.DescriptionPresent);
   JsonNode? FolderLabel(JsonNode? value){if(value is null)return null;string location=value.GetValue<string>();return JsonValue.Create(location.Length==0?"Root":location.Split("::")[^1]);}
   foreach(string name in old.Values.Keys.Union(next.Values.Keys)){var a=old.Values.TryGetValue(name,out var av)?JsonNode.Parse(av.Value.GetRawText()):null;var b=next.Values.TryGetValue(name,out var bv)?JsonNode.Parse(bv.Value.GetRawText()):null;if(a is not null&&b is not null&&JsonNode.DeepEquals(a,b)&&a.ToJsonString()!=b.ToJsonString())additional=true;if(old.Values.ContainsKey(name)!=next.Values.ContainsKey(name)||!JsonNode.DeepEquals(a,b))Add(name=="editorFolder"?"분류 위치":name=="editorName"?"표시 이름":"값 · "+name,name=="editorFolder"?FolderLabel(a):a,name=="editorFolder"?FolderLabel(b):b,old.Values.ContainsKey(name),next.Values.ContainsKey(name));}
   foreach(string name in old.Data.Keys.Union(next.Data.Keys)){var a=old.Data.TryGetValue(name,out var av)?Datum(av):null;var b=next.Data.TryGetValue(name,out var bv)?Datum(bv):null;if(a is not null&&b is not null&&JsonNode.DeepEquals(a,b)&&a.ToJsonString()!=b.ToJsonString())additional=true;if(old.Data.ContainsKey(name)!=next.Data.ContainsKey(name)||!JsonNode.DeepEquals(a,b))Add("필드 값 · "+name,a,b,old.Data.ContainsKey(name),next.Data.ContainsKey(name));}
   foreach(string name in old.Fields.Keys.Union(next.Fields.Keys)){JsonNode? Field(SchemaField? f)=>f is null?null:JsonValue.Create(f.Type+" · "+f.Kind+" · "+f.Cardinality);var a=Field(old.Fields.GetValueOrDefault(name));var b=Field(next.Fields.GetValueOrDefault(name));if(!JsonNode.DeepEquals(a,b))Add("필드 정의 · "+name,a,b,old.Fields.ContainsKey(name),next.Fields.ContainsKey(name));}
   additional|=!old.Values.Keys.Where(k=>next.Values.ContainsKey(k)).SequenceEqual(next.Values.Keys.Where(k=>old.Values.ContainsKey(k)))||!old.Data.Keys.Where(k=>next.Data.ContainsKey(k)).SequenceEqual(next.Data.Keys.Where(k=>old.Data.ContainsKey(k)))||!old.Fields.Keys.Where(k=>next.Fields.ContainsKey(k)).SequenceEqual(next.Fields.Keys.Where(k=>old.Fields.ContainsKey(k)));next.Description=old.Description;next.DescriptionPresent=old.DescriptionPresent;next.Values=old.Values;next.Data=old.Data;next.Fields=old.Fields;
   additional|=Format(next)!=Format(old)||Comments(before)!=Comments(after);
  }
 }catch{additional=true;}
 if(changes.Count==0&&before!=after)additional=true;
 return new JsonObject{["changes"]=changes,["additionalChanges"]=additional};
}
