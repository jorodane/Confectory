using Confectory.Core;
using System.Globalization;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

namespace Confectory.Core;
// Pure compiler input processing: no source-file writes, activation, AI request or runtime invocation.
public static partial class FeatureBlueprint
{
    public const string Profile = "sync-acyclic-v1", Generator = "feature-blueprint-source-v2";
    public static string ContractHash(Element feature) => Hash(CanonicalText(new JsonObject { ["feature"] = feature.Id, ["signature"] = SignatureNode(feature.Signature!) }));
    public static string ImportAlias(string featureId) => "fg_call_" + Hash(featureId)[..24];
    sealed class Refusal(string code, string subject) : Exception(code)
    {
        public string Code = code, Subject = subject;
    }

    sealed record Node(string Id, string Kind, string Control, FunctionSignature Signature, JsonObject Definition, JsonObject Arguments, string DefinitionHash, string? Feature);
    static string Hash(string text) => Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(text))).ToLowerInvariant();
    static string S(JsonNode? node, string key) => node?[key]?.GetValue<string>() ?? throw new Refusal("GRAPH_FIELD", key);
    static void Need(bool ok, string code, string subject)
    {
        if (!ok)
            throw new Refusal(code, subject);
    }

    static string Id(JsonNode? node, string key)
    {
        string id = S(node, key);
        Need(id.Length <= 128 && Regex.IsMatch(id, @"\A[A-Za-z_][A-Za-z_0-9.-]*\z", RegexOptions.CultureInvariant), "GRAPH_ID", key);
        return id;
    }

    static JsonNode? Canonical(JsonNode? node) => node is JsonObject obj ? new JsonObject(obj.OrderBy(p => p.Key, StringComparer.Ordinal).Select(p => new KeyValuePair<string, JsonNode?>(p.Key, Canonical(p.Value)))) : node is JsonArray array ? new JsonArray(array.Select(Canonical).ToArray()) : node?.DeepClone();
    static string CanonicalText(JsonNode? node) => Canonical(node)?.ToJsonString() ?? "null";
    public static JsonObject SignatureDocument(FunctionSignature signature) => new()
    {
        ["args"] = new JsonArray(signature.Args.Select(p => { var row=new JsonObject { ["type"] = p.Type, ["name"] = p.Name }; if(p.Mode is not null)row["mode"]=p.Mode; return (JsonNode)row; }).ToArray()),
        ["return"] = signature.Return
    };
    static JsonObject SignatureNode(FunctionSignature signature) => SignatureDocument(signature);
    static string SignatureText(FunctionSignature signature, bool names) => signature.Format(names);
    static FunctionSignature Signature(JsonNode value)
    {
        var args = value["args"]!.AsArray();
        var signature = new FunctionSignature(args.Select(p => new Parameter(S(p, "type"), S(p, "name"), p?["mode"]?.GetValue<string>())).ToList(), S(value, "return"));
        Need(signature.Args.All(p => p.Mode is null or "out" or "ref"), "GRAPH_PARAMETER_MODE", "signature");
        var parsed = new Parser("function Blueprint.Validation::Node " + SignatureText(signature, true) + " {}", "<node-contract>").ParseElement();
        Need(parsed.Signature is not null, "NODE_CONTRACT", "signature");
        return parsed.Signature!;
    }

    public static JsonObject Execute(JsonObject request)
    {
        try
        {
            Need(!request.ContainsKey("sourcePath")&&!request.ContainsKey("sourceOwner")&&!request.ContainsKey("privateChildren"),"GRAPH_REQUEST_FIELD","private compiler context");
            if(SupportsPrivateGraphs(request["graph"]?["profile"]?.ToString()))BlueprintTree.Nodes(request["graph"]!.AsObject()).ToArray();
            return Process(request);
        }
        catch (BuildError error)
        {
            return Invalid(error.Diagnostic.Code, error.Diagnostic.Message);
        }
        catch (Exception error)when (error is ArgumentException or InvalidOperationException or NullReferenceException or JsonException or FormatException or OverflowException)
        {
            return Invalid("GRAPH_SHAPE", error.Message);
        }
        catch (Refusal error)
        {
            return new()
            {
                ["state"] = "invalid",
                ["diagnostics"] = new JsonArray(new JsonObject { ["code"] = error.Code, ["subject"] = error.Subject }),
                ["sourceWritten"] = false,
                ["executed"] = false
            };
        }
    }

    static JsonObject Invalid(string code, string subject) => new()
    {
        ["state"] = "invalid",
        ["diagnostics"] = new JsonArray(new JsonObject { ["code"] = code, ["subject"] = subject }),
        ["sourceWritten"] = false,
        ["executed"] = false
    };
    static JsonObject ProcessCore(JsonObject request)
    {
        string operation = S(request, "operation");
        bool inspectStalePostCalls = operation == "featureBlueprintNodes" && request["inspectStalePostCalls"]?.GetValue<bool>() == true;
        Need(operation is "featureBlueprintDescribe" or "featureBlueprintAssemble" or "featureBlueprintNodes" or "featureBlueprintNodeProbe", "GRAPH_OPERATION", operation);
        var feature = new Parser(S(request, "featureSource"), "<feature-contract>").ParseElement();
        Need(feature.Kind == "function" && feature.Signature is not null, "GRAPH_FEATURE_CONTRACT", feature.Id);
        _ = BlueprintOutputSnapshot.Read(feature);
        var contract = SignatureNode(feature.Signature!);
        string contractHash = Hash(CanonicalText(new JsonObject { ["feature"] = feature.Id, ["signature"] = contract.DeepClone() }));
        var graph = request["graph"]!.AsObject();
        Need(graph["schema"]?.GetValue<int>() == 1, "GRAPH_SCHEMA", "schema");
        string profile=S(graph,"profile");bool switchFlow=SupportsSwitches(profile),properties=SupportsProperties(profile),nested=SupportsPrivateGraphs(profile),aliasLocals=nested||profile==AliasLocalsProfile,externalRefs=SupportsExternalRefs(profile),refProfile=externalRefs||profile==RefNodesProfile,localProfile=profile==LocalsProfile||refProfile,multiOutput=profile==MultiOutputProfile||localProfile, implicitEnd=profile==ImplicitProfile||multiOutput;string generator=profile==PropertyRefProfile?PropertyRefGenerator:profile==PropertySetProfile?PropertySetGenerator:switchFlow?SwitchGenerator:profile==MethodsProfile?MethodsGenerator:properties?PropertyGenerator:nested?NestedGenerator:aliasLocals?AliasLocalsGenerator:externalRefs?ExternalRefsGenerator:refProfile?RefNodesGenerator:localProfile?LocalsGenerator:multiOutput?MultiOutputGenerator:implicitEnd?ImplicitGenerator:Generator;
        Need(profile==Profile||implicitEnd,"GRAPH_PROFILE_UNSUPPORTED",profile);
        Need(properties||!HasObjectSignature(feature.Signature!),"GRAPH_OBJECT_PROFILE",feature.Id);
        Need(externalRefs||!feature.Signature!.Args.Any(p=>p.IsRef),"GRAPH_REF_FEATURE_UNSUPPORTED",feature.Id);
        Need(multiOutput || !feature.Signature!.Args.Any(p=>p.IsOut), "GRAPH_PARAMETER_MODE_PROFILE", profile);
        Need(S(graph, "feature") == feature.Id, "GRAPH_FEATURE_MISMATCH", "feature");
        Need(S(graph, "contractHash") == contractHash, "GRAPH_CONTRACT_STALE", feature.Id);
        var canonicalImports = new HashSet<string>(StringComparer.Ordinal);
        var imports = new Dictionary<string, (Element Element, string Alias, string Hash, string SourceHash)>(StringComparer.Ordinal);
        (Element Element, string Alias, string Hash, string SourceHash) Import(string id, bool canonical = true)
        {
            if (canonical) canonicalImports.Add(id);
            if (imports.TryGetValue(id, out var known))
                return known;
            string source = id == feature.Id ? S(request, "featureSource") : request["featureContracts"]?[id]?.GetValue<string>() ?? throw new Refusal("GRAPH_CALLEE_MISSING", id);
            var element = new Parser(source, "<called-feature>").ParseElement();
            Need(element.Id == id && element.Kind == "function" && element.Signature is not null, "GRAPH_CALLEE_CONTRACT", id);
            _ = BlueprintOutputSnapshot.Read(element);
            string hash = Hash(CanonicalText(new JsonObject { ["feature"] = id, ["signature"] = SignatureNode(element.Signature!) }));
            var result = (element, ImportAlias(id), hash, Hash(source));
            imports.Add(id, result);
            return result;
        }

        if(multiOutput)Need(feature.Signature!.Args.Count<=64&&graph["nodes"]!.AsArray().Count<=256,"GRAPH_MULTI_OUTPUT_BUDGET",feature.Id);
        var locals=ReadLocals(graph,localProfile,aliasLocals);
        Need(properties||!locals.Values.Any(local=>IsObjectType(S(local,"type"))),"GRAPH_OBJECT_PROFILE","locals");
        var nodes = new Dictionary<string, Node>(StringComparer.Ordinal);
        foreach (var item in graph["nodes"]!.AsArray())
        {
            var value = item!.AsObject();
            string id = Id(value, "id"), kind = S(value, "kind"), control = S(value, "control"), intent = S(value, "intent");
            Need(!nodes.ContainsKey(id), "GRAPH_DUPLICATE_NODE", id);
            _ = DisplayName(value);
            Need(kind is "code" or "call" || nested && kind=="graph" || properties && kind=="property" || SupportsPropertySets(profile) && kind=="property-set" || profile==PropertyRefProfile && kind=="property-ref" || implicitEnd && kind=="export" || localProfile && kind=="set", "GRAPH_NODE_KIND", id);
            Need(control is "next" or "branch" || switchFlow && control=="switch", "GRAPH_CONTROL", id);
            Need(!string.IsNullOrWhiteSpace(intent), "NODE_INTENT", id);
            var signature = Signature(value["signature"]!);
            Need(properties||!HasObjectSignature(signature),"GRAPH_OBJECT_PROFILE",id);
            Need(refProfile || !signature.Args.Any(p=>p.IsRef),"GRAPH_REF_PROFILE",id);
            Need(multiOutput || !signature.Args.Any(p=>p.IsOut), "GRAPH_PARAMETER_MODE_PROFILE", id);
            Need(value["implementationContext"] is JsonObject || !signature.Args.Any(p => (p.Name.StartsWith("__fg_", StringComparison.Ordinal) || p.Name.StartsWith("fg_call_", StringComparison.Ordinal))), "NODE_RESERVED_NAME", id);
            Need(control != "branch" || signature.Return == "bool", "GRAPH_BRANCH_TYPE", id);
            if(kind=="export")Need(signature.Args.Count==1&&signature.Args[0].Mode is null&&signature.Args[0].Name=="value"&&FeatureOutputs(feature.Signature!).Any(p=>p.Name==S(value,"output")&&p.Type==signature.Args[0].Type)&&control=="next"&&signature.Return=="void","GRAPH_OUTPUT_CONTRACT",id);
            if(kind=="set")Need(signature.Args.Count==1&&signature.Args[0].Mode is null&&signature.Args[0].Name=="value"&&signature.Return=="void"&&control=="next"&&locals.TryGetValue(S(value,"local"),out var storage)&&S(storage,"type")==signature.Args[0].Type,"GRAPH_LOCAL_CONTRACT",id);
            Need(kind=="set"||!value.ContainsKey("outputLocal"),"GRAPH_SET_OUTPUT_KIND",id);
            if(kind=="set"&&value.ContainsKey("outputLocal"))Need(locals.TryGetValue(S(value,"outputLocal"),out var stored)&&stored["source"] is null&&S(stored,"type")==signature.Args[0].Type,"GRAPH_SET_OUTPUT_CONTRACT",id);
            var references = new JsonObject();
            string? called = null;
            if (kind == "call")
            {
                called = S(value, "feature");
                var imported = Import(called);
                Need(signature.Matches(imported.Element.Signature) || inspectStalePostCalls && value.ContainsKey("postCall"), "GRAPH_CALLEE_SIGNATURE", id);
                references[called] = imported.Hash;
            }
            if (value.ContainsKey("postCall")) {
                Need(kind == "call" && (control == "next" || control == "switch" && switchFlow) && SupportsMethods(profile), "GRAPH_POST_CALL_PROFILE", id);
                var after = value["postCall"] as JsonObject;
                Need(after is not null && after.All(p => p.Key is "contractHash" or "source" or "helpers" or "mode" or "returnMapping") && after["contractHash"] is JsonValue && after["source"] is JsonValue && (!after.ContainsKey("helpers") || after["helpers"] is JsonValue), "GRAPH_POST_CALL_SHAPE", id);
                var snapshot = BlueprintOutputSnapshot.Prepare(Import(called!).Element);
                Need(after!["contractHash"]!.ToString() == snapshot["contractHash"]!.ToString() || inspectStalePostCalls, "GRAPH_PUBLIC_OUTPUT_CONTRACT_STALE", id);
                Need(control == "switch" ? after["mode"]?.ToString() == "execution-enum" : !after.ContainsKey("mode") && !after.ContainsKey("returnMapping"), "GRAPH_POST_CALL_MODE", id);
                if (control == "switch") _ = BlueprintCallWrapper.Prepare(Import(called!).Element, value["executionEnum"]!.AsObject(), inspectStalePostCalls ? null : after["contractHash"]!.GetValue<string>(), after["source"]!.GetValue<string>(), after["helpers"]?.GetValue<string>() ?? "", after["returnMapping"]?.GetValue<string>());
                else _ = BlueprintCallAfter.Prepare(Import(called!).Element, inspectStalePostCalls ? null : after["contractHash"]!.GetValue<string>(), after["source"]!.GetValue<string>(), after.ContainsKey("helpers") ? after["helpers"]!.GetValue<string>() : "");
            }

            foreach (var imported in value["imports"]?.AsArray() ?? new JsonArray())
            {
                string target = imported!.GetValue<string>();
                references[target] = Import(target).Hash;
            }

            var definition = new JsonObject
            {
                ["id"] = id,
                ["kind"] = kind,
                ["control"] = control,
                ["intent"] = intent,
                ["signature"] = SignatureNode(signature),
                ["calledFeature"] = called,
                ["featureContracts"] = references
            };
            if (value.ContainsKey("postCall")) definition["postCall"] = value["postCall"]!.DeepClone();
            if(nested&&(request["sourcePath"] is not null||kind=="graph"))definition["ownerPath"]=S(request,"sourceOwner")+"/"+(request["sourcePath"]?.ToString()??"");
            if(kind=="graph"){
                var childRequest=PrivateRequest(request,value,signature);
                var child=Process(childRequest);request["privateChildren"]![id]=child;
                definition["graph"]=SemanticGraph(value["graph"]!.AsObject());
                foreach(var imported in child["imports"]?.AsArray()??new JsonArray())references[S(imported,"feature")]=Import(S(imported,"feature")).Hash;
            }
            Need(switchFlow||!value.ContainsKey("branchOwner")&&!value.ContainsKey("executionEnum"),"GRAPH_SWITCH_PROFILE",id);
            if(value.ContainsKey("branchOwner"))definition["branchOwner"]=Id(value,"branchOwner");
            if(control=="switch"){
                Need((kind=="code"&&signature.Return=="void"||kind=="call"&&value["postCall"]?["mode"]?.ToString()=="execution-enum")&&!value.ContainsKey("implementationContext"),"GRAPH_SWITCH_CONTRACT",id);
                definition["executionEnum"]=EnumContract(value["executionEnum"]??throw new Refusal("GRAPH_ENUM_REQUIRED",id));
            }else Need(!value.ContainsKey("executionEnum"),"GRAPH_ENUM_CONTROL",id);
            if(IsPropertyNode(kind)){
                bool writing=kind=="property-set",referencing=kind=="property-ref";
                Need(signature.Args.Count==(writing?2:1)&&signature.Args[0].Type=="object"&&signature.Args[0].Name=="target"&&signature.Args.All(p=>p.Mode is null)&&(writing?signature.Return=="void"&&control=="next"&&signature.Args[1].Name=="value":signature.Return!="void"&&(!referencing||control=="next")),"PROPERTY_SIGNATURE",id);
                try{
                    var property=PropertyContract(request,value);Need((writing?signature.Args[1].Type:signature.Return)==S(property,"clrType"),"PROPERTY_SIGNATURE_STALE",id);
                    definition["property"]=property;
                    string accessor=referencing?PropertyRefAccessor:writing?PropertySetter:PropertyReader;var imported=Import(accessor);
                    var args=new List<Parameter>{new("object","target"),new("string","owner"),new("string","field"),new("string","contractHash")};if(writing)args.Add(new("object","value"));
                    Need(imported.Element.Signature!.Matches(new FunctionSignature(args,writing?"void":"object")),referencing?"PROPERTY_REF_ACCESSOR_CONTRACT":writing?"PROPERTY_SETTER_CONTRACT":"PROPERTY_READER_CONTRACT",id);references[accessor]=imported.Hash;
                }catch(Refusal error)when(operation is "featureBlueprintNodes" or "featureBlueprintNodeProbe"){
                    definition["propertyError"]=error.Code;definition["propertySubject"]=error.Subject;
                }
            }
            if(kind=="export")definition["output"]=S(value,"output");
            if(kind=="set"){definition["local"]=S(value,"local");if(value.ContainsKey("outputLocal"))definition["outputLocal"]=S(value,"outputLocal");}
            if (value["implementationContext"] is JsonObject context)
            {
                var actualContext = request["implementationContext"] as JsonObject;
                Need(implicitEnd && kind == "code" && actualContext is not null && context["implementation"]?.ToString() == actualContext["implementation"]?.ToString() && context["feature"]?.ToString() == actualContext["feature"]?.ToString() && (multiOutput || JsonNode.DeepEquals(context["signature"], actualContext["signature"])) && context["imports"]!.AsObject().All(p => actualContext["imports"]!.AsObject().ContainsKey(p.Key) && JsonNode.DeepEquals(p.Value, actualContext["imports"]![p.Key])), "GRAPH_IMPLEMENTATION_CONTEXT_STALE", id);
                Need(context["feature"]?.ToString() == feature.Id && CanonicalText(context["signature"]) == CanonicalText(SignatureNode(signature)), "GRAPH_IMPLEMENTATION_CONTEXT_CONTRACT", id);
                Need(!nodes.Values.Any(HasContext), "GRAPH_IMPLEMENTATION_CONTEXT_DUPLICATE", id);
                foreach (var binding in actualContext!["imports"]!.AsObject()) references[S(binding.Value, "feature")] = Import(S(binding.Value, "feature"), false).Hash;
                var boundContext=actualContext!.DeepClone().AsObject();
                if(multiOutput&&!JsonNode.DeepEquals(context["signature"],actualContext["signature"])){
                    boundContext["interfaceSignature"]=actualContext["signature"]!.DeepClone();
                    boundContext["signature"]=context["signature"]!.DeepClone();
                }
                definition["implementationContext"] = boundContext;
                if (value["sourceIdentity"] is JsonValue sourceIdentity)
                {
                    string identity = sourceIdentity.GetValue<string>();
                    Need(identity.Length is > 0 and <= 4096 && !identity.Any(c => c is '\r' or '\n' or '\0'), "GRAPH_SOURCE_IDENTITY", id);
                    definition["sourceIdentity"] = identity;
                }
            }
            bool forwarding=value.ContainsKey("forwardCallerStorage");
            if(forwarding){Need(externalRefs&&value["forwardCallerStorage"]?.GetValue<bool>()==true&&kind is "code" or "call" or "graph","GRAPH_CALLER_STORAGE_PROFILE",id);definition["forwardCallerStorage"]=true;}
            if(externalRefs&&(forwarding||value["implementationContext"] is JsonObject&&(signature.Args.Any(p=>p.Mode is "ref" or "out")||feature.Signature!.Args.Any(p=>p.Mode is "ref" or "out")))){
                Need(signature.Matches(feature.Signature),"GRAPH_CALLER_STORAGE_CONTRACT",id);
                var arguments=value["arguments"] as JsonObject;
                Need(arguments is not null&&arguments.Count==signature.Args.Count(p=>!p.IsOut)&&signature.Args.Select((p,index)=>(p,index)).Where(x=>!x.p.IsOut).All(x=>arguments[x.p.Name] is JsonObject binding&&binding.Count==1&&binding["input"]?.ToString()==feature.Signature!.Args[x.index].Name),"GRAPH_CALLER_STORAGE_BINDING",id);
            }
            nodes.Add(id, new(id, kind, control, signature, definition, value["arguments"]?.AsObject() ?? new JsonObject(), Hash(CanonicalText(definition)), called));
        }

        var outputCells=nodes.Values.Where(n=>n.Kind=="set"&&n.Definition["outputLocal"] is not null).Select(n=>S(n.Definition,"outputLocal")).ToArray();
        Need(outputCells.Distinct(StringComparer.Ordinal).Count()==outputCells.Length,"GRAPH_SET_OUTPUT_OWNER",feature.Id);
        ValidateAliasLocals(locals,feature,nodes);
        foreach(var node in nodes.Values.Where(n=>n.Kind is "property-set" or "property-ref"))CheckPropertyInputBindings(node,feature.Signature!,nodes,locals);
        bool ForwardCaller(Node node)=>externalRefs&&(node.Definition["forwardCallerStorage"]?.GetValue<bool>()==true||HasContext(node)&&node.Signature.Args.Any(p=>p.Mode is "ref" or "out"));
        string CallerOut(Node node,string name)=>feature.Signature!.Args[node.Signature.Args.FindIndex(p=>p.Name==name)].Name;
        var forwardedOutputs=nodes.Values.Where(ForwardCaller).ToDictionary(n=>n.Id,n=>n.Signature.Args.Where(p=>p.IsOut).Select(p=>CallerOut(n,p.Name)).ToArray(),StringComparer.Ordinal);

        if(operation=="featureBlueprintNodeProbe"&&S(request,"node").Contains('/')){
            string first=S(request,"node").Split('/')[0];Need(nodes.ContainsKey(first)&&nodes[first].Kind=="graph","NODE_CODE_REQUIRED",S(request,"node"));
            return request["privateChildren"]![first]!.DeepClone().AsObject();
        }
        if (operation == "featureBlueprintNodeProbe")
        {
            string id = S(request, "node");
            Need(nodes.TryGetValue(id, out var selected) && selected.Kind == "code", "NODE_CODE_REQUIRED", id);
            var node = selected!;
            var record = request["implementations"]?[RecordKey(request,id)];
            Need(record?["schema"]?.GetValue<int>() == 1 && record["node"]?.ToString() == id && record["definitionHash"]?.ToString() == node.DefinitionHash, "NODE_IMPLEMENTATION_STALE", id);
            string source = HasContext(node) ? S(record,"source") : S(record, "source").Replace("\r\n", "\n"), helper = Helpers(record, profile, node);
            string marker = "node:" + feature.Id + "/" + id + "@" + NodeCodeHash(node,source,helper);
            var used = node.Definition["featureContracts"]!.AsObject().Select(p => p.Key).Order(StringComparer.Ordinal).ToArray();
            string code = "#pragma warning disable CS8321\nstatic " + node.Signature.Return + " __fg_probe_" + Hash(id)[..24] + "(" + string.Join(",", node.Signature.Args.Select(p => p.Declaration()).Concat(used.Select(f => Generation.Interface(f) + " " + Import(f).Alias))) + ") {\n#pragma warning restore CS8321\n#line 1 " + JsonSerializer.Serialize(marker) + "\n" + source + "\n#line default\n}\n";
            marker = ContextMarker(node,marker);
            string members = HasContext(node) ? ContextMember(node, source, marker) : "";
            if (HasContext(node)) code = "throw new global::System.InvalidOperationException(\"Independent context probe must never execute\");";
            if(SupportsMethods(profile) && !HasContext(node)) {
                string declarations = string.Join(",", node.Signature.Args.Select(p=>p.Declaration()).Concat(used.Select(f=>Generation.Interface(f)+" "+Import(f).Alias)));
                members = MethodsMember(MethodClass(request,id),node,declarations,source,helper,marker);
                code = "throw new global::System.InvalidOperationException(\"Independent static method probe must never execute\");";
            }
            string graphHash = Hash(CanonicalText(SemanticGraph(graph)));
            return new JsonObject
            {
                ["state"] = "node-source-assembled", ["mode"] = "independent-node", ["profile"] = profile, ["generator"] = generator, ["feature"] = feature.Id,
                ["node"] = id, ["definitionHash"] = node.DefinitionHash, ["body"] = code, ["members"] = members, ["explicitEntry"] = HasContext(node), ["entrySignature"] = contract.DeepClone(), ["bodyHash"] = Hash(code+members),
                ["nodes"] = new JsonArray(new JsonObject { ["id"] = id, ["definitionHash"] = node.DefinitionHash, ["definition"] = node.Definition.DeepClone(), ["status"] = "available", ["compilationEligible"] = true, ["includedInSource"] = true, ["compilerValidated"] = false }),
                ["sourceMap"] = new JsonArray(new JsonObject { ["node"] = id, ["definitionHash"] = node.DefinitionHash, ["marker"] = marker }),
                ["nodeSources"] = new JsonArray(new JsonObject { ["id"] = id, ["source"] = source, ["helpers"] = helper, ["marker"] = marker, ["preserveImplementationContext"] = HasContext(node) }),
                ["graphMap"] = new JsonObject { ["marker"] = "graph:" + feature.Id + "@" + graphHash, ["jsonPointer"] = "/nodes/" + graph["nodes"]!.AsArray().IndexOf(graph["nodes"]!.AsArray().Single(n => n!["id"]!.ToString() == id)), ["topologyHash"] = graphHash },
                ["imports"] = new JsonArray(used.Select(f => (JsonNode)new JsonObject { ["feature"] = f, ["alias"] = Import(f).Alias, ["contractHash"] = Import(f,false).Hash, ["binding"] = HasContext(node) ? "implementation-context" : "canonical" }).ToArray()),
                ["sourceWritten"] = false, ["compiled"] = false, ["executed"] = false
            };
        }

        if(switchFlow){
            var rawEdges=new Dictionary<(string,string),string>();
            foreach(var edge in graph["edges"]!.AsArray()){
                string from=S(edge,"from"),port=S(edge,"port"),to=S(edge,"to");
                Need(nodes.ContainsKey(from),"GRAPH_EDGE_SOURCE",from);
                Need(nodes.ContainsKey(to)||to.StartsWith("return:",StringComparison.Ordinal)||to.StartsWith("exit:",StringComparison.Ordinal)&&graph["exits"]!.AsObject().ContainsKey(to[5..]),"GRAPH_TARGET",to);
                Need(rawEdges.TryAdd((from,port),to),"GRAPH_DUPLICATE_PORT",from+"/"+port);
            }
            SwitchFlow(nodes,rawEdges);
            string start=S(graph,"entry");
            Need(!start.StartsWith("return:",StringComparison.Ordinal),"GRAPH_BRANCH_ENTRY",start);
            if(nodes.TryGetValue(start,out var first))Need(Owner(first).Length==0,"GRAPH_BRANCH_ENTRY",start);
        }
        if (operation == "featureBlueprintNodes")
        {
            var versions = new JsonObject(imports.OrderBy(p => p.Key, StringComparer.Ordinal).Select(p => new KeyValuePair<string, JsonNode?>(p.Key, JsonValue.Create(p.Value.Hash))));
            versions[feature.Id] = contractHash;
            return new JsonObject
            {
                ["state"] = "node-definitions", ["feature"] = feature.Id, ["profile"] = profile, ["contractHash"] = contractHash, ["signature"] = contract.DeepClone(),
                ["nodes"] = new JsonArray(nodes.OrderBy(p => p.Key, StringComparer.Ordinal).Select(p => (JsonNode)new JsonObject { ["id"] = p.Key, ["definitionHash"] = p.Value.DefinitionHash, ["definition"] = p.Value.Definition.DeepClone(), ["outputs"] = NodeOutputDocument(p.Value), ["currentCallSignature"] = p.Value.Kind == "call" ? SignatureDocument(Import(p.Value.Feature!).Element.Signature!) : null, ["callAbiSourceHash"] = p.Value.Kind == "call" ? Import(p.Value.Feature!).SourceHash : null, ["postCallStale"] = p.Value.Definition["postCall"] is not null && p.Value.Definition["postCall"]!["contractHash"]!.ToString() != BlueprintOutputSnapshot.Prepare(Import(p.Value.Feature!).Element)["contractHash"]!.ToString(), ["postCallSignatureMatches"] = p.Value.Kind != "call" || p.Value.Signature.Args.Select(a => (a.Name,a.Type,a.Mode)).SequenceEqual(Import(p.Value.Feature!).Element.Signature!.Args.Select(a => (a.Name,a.Type,a.Mode))) && p.Value.Signature.Return == Import(p.Value.Feature!).Element.Signature!.Return, ["postCallEditor"] = p.Value.Kind == "call" && p.Value.Control == "switch" ? BlueprintCallWrapper.Prepare(Import(p.Value.Feature!).Element, p.Value.Definition["executionEnum"]!.AsObject(), inspectStalePostCalls ? null : p.Value.Definition["postCall"]?["contractHash"]?.ToString(), p.Value.Definition["postCall"]?["source"]?.GetValue<string>(), p.Value.Definition["postCall"]?["helpers"]?.GetValue<string>()??"", p.Value.Definition["postCall"]?["returnMapping"]?.GetValue<string>()) : p.Value.Kind == "call" ? BlueprintCallAfter.Prepare(Import(p.Value.Feature!).Element, inspectStalePostCalls ? null : p.Value.Definition["postCall"]?["contractHash"]?.ToString(), p.Value.Definition["postCall"]?["source"]?.GetValue<string>(), p.Value.Definition["postCall"]?["helpers"]?.GetValue<string>()??"") : null, ["wrapperEditor"] = p.Value.Kind == "call" && p.Value.Control == "next" && p.Value.Definition["postCall"] is null ? BlueprintCallWrapper.Prepare(Import(p.Value.Feature!).Element, new JsonObject { ["primary"] = "next", ["members"] = new JsonArray(new JsonObject { ["id"] = "next", ["name"] = "NoBranch", ["value"] = 0 }) }, returnMapping: p.Value.Signature.Return == "void" ? null : BlueprintCallWrapper.NativeReturnMapping) : null }).ToArray()),
                ["locals"] = LocalDocument(locals), ["outputs"] = OutputDocument(feature.Signature!), ["contractVersions"] = versions,
                ["imports"] = new JsonArray(imports.OrderBy(i => i.Key, StringComparer.Ordinal).Select(i => (JsonNode)new JsonObject { ["feature"] = i.Key, ["alias"] = i.Value.Alias, ["contractHash"] = i.Value.Hash, ["binding"] = canonicalImports.Contains(i.Key) ? "canonical" : "implementation-context", ["signature"] = SignatureNode(i.Value.Element.Signature!) }).ToArray()),
                ["independentNodeCompilation"] = true, ["sourceWritten"] = false, ["compiled"] = false, ["executed"] = false
            };
        }

        string entry = S(graph, "entry");
        var exits = graph["exits"]!.AsObject();
        var edges = new Dictionary<(string, string), string>();
        bool Exit(string target) => target.StartsWith("exit:", StringComparison.Ordinal) && exits.ContainsKey(target[5..]);
        void Target(string target) => Need(nodes.ContainsKey(target) || Exit(target) || switchFlow && target.StartsWith("return:",StringComparison.Ordinal), "GRAPH_TARGET", target);
        bool Terminal(string target)=>implicitEnd&&target.StartsWith("end:",StringComparison.Ordinal);
        bool emptyEntry=implicitEnd&&entry.Length==0;
        if(emptyEntry)entry="end:$entry";else Target(entry);
        foreach (var edge in graph["edges"]!.AsArray())
        {
            string from = S(edge, "from"), port = S(edge, "port"), to = S(edge, "to");
            Need(nodes.ContainsKey(from), "GRAPH_EDGE_SOURCE", from);
            Target(to);
            Need(edges.TryAdd((from, port), to), "GRAPH_DUPLICATE_PORT", from + "/" + port);
        }

        var switchRouting=switchFlow?SwitchFlow(nodes,edges):(new Dictionary<string,string>(StringComparer.Ordinal),new JsonArray(),new Dictionary<(string,string),(string,string)>());
        var continuations=switchRouting.Item1;var branchReturns=switchRouting.Item2;
        if(switchFlow&&nodes.TryGetValue(entry,out var firstNode))Need(Owner(firstNode).Length==0,"GRAPH_BRANCH_ENTRY",entry);
        var reachable = new HashSet<string>(StringComparer.Ordinal);
        var stack = new HashSet<string>(StringComparer.Ordinal);
        var order = new List<string>();
        void Visit(string id)
        {
            if (Exit(id) || Terminal(id) || reachable.Contains(id))
                return;
            Need(stack.Add(id), "GRAPH_CYCLE_PROFILE_UNSUPPORTED", id);
            if(implicitEnd&&!switchFlow){string[] expected=nodes[id].Control=="branch"?["true","false"]:["next"];Need(edges.Keys.Where(k=>k.Item1==id).All(k=>expected.Contains(k.Item2)),"GRAPH_PORTS",id);foreach(string port in expected)edges.TryAdd((id,port),"end:"+id+"/"+port);}
            foreach (var target in edges.Where(p => p.Key.Item1 == id).OrderBy(p => p.Key.Item2, StringComparer.Ordinal))
                Visit(target.Value);
            stack.Remove(id);
            reachable.Add(id);
            order.Add(id);
        }

        Visit(entry);
        foreach (var node in nodes.Values.Where(n => reachable.Contains(n.Id)))
        {
            string[] ports = node.Control == "switch" ? edges.Keys.Where(k=>k.Item1==node.Id).Select(k=>k.Item2).ToArray() : node.Control == "branch" ? ["true", "false"] : ["next"];
            Need(edges.Keys.Where(k => k.Item1 == node.Id).Select(k => k.Item2).Order().SequenceEqual(ports.Order()), "GRAPH_PORTS", node.Id);
        }

        order.Reverse();
        var predecessors = order.ToDictionary(id => id, id => edges.Where(e => e.Value == id && reachable.Contains(e.Key.Item1)).Select(e => e.Key.Item1).ToArray(), StringComparer.Ordinal);
        var dominators = new Dictionary<string, HashSet<string>>(StringComparer.Ordinal);
        foreach (string id in order)
        {
            var before = predecessors[id];
            var own = before.Length == 0 ? new HashSet<string>(StringComparer.Ordinal) : new HashSet<string>(dominators[before[0]], StringComparer.Ordinal);
            foreach (string p in before.Skip(1))
                own.IntersectWith(dominators[p]);
            own.Add(id);
            dominators[id] = own;
        }

        var sourceMaps = new JsonArray();
        var manifestNodes = new JsonArray();
        var bodies = new Dictionary<string, string>(StringComparer.Ordinal);
        var helpers = new Dictionary<string, string>(StringComparer.Ordinal);
        var missing = new List<string>();
        var definitionOrder = order.Concat(nodes.Keys.Where(id => !reachable.Contains(id)).Order(StringComparer.Ordinal)).ToArray();
        foreach (string id in definitionOrder)
        {
            var node = nodes[id];
            JsonNode? record = request["implementations"]?[RecordKey(request,id)];
            string? body = node.Kind=="property-ref" ? null : IsPropertyNode(node.Kind) ? PropertyBody(node) : node.Kind == "graph" ? request["privateChildren"]![id]?["body"]?.GetValue<string>() : node.Kind == "call" ? null : record?["source"]?.GetValue<string>();
            string helper = node.Kind == "code" ? Helpers(record, profile, node) : "";
            helpers[id] = helper;
            string? codeHash = body is null ? null : node.Kind == "graph" ? request["privateChildren"]![id]!["bodyHash"]!.GetValue<string>() : NodeCodeHash(node, body, helper);
            string status = node.Kind=="property-ref" ? "property-reference" : node.Kind=="property-set" ? "property-write" : node.Kind=="property" ? "property-read" : node.Kind=="graph" ? (request["privateChildren"]![id]?["state"]?.ToString() is "source-ready" or "source-assembled" ? "private-graph" : "missing") : node.Kind == "export" ? "output-assignment" : node.Kind == "set" ? "local-assignment" : node.Kind == "call" ? "feature-reference" : body is null ? "missing" : record?["definitionHash"]?.ToString() != node.DefinitionHash ? "stale" : "available";
            manifestNodes.Add(new JsonObject { ["id"] = id, ["definitionHash"] = node.DefinitionHash, ["definition"] = node.Definition.DeepClone(), ["implementationHash"] = codeHash, ["status"] = status, ["reachable"] = reachable.Contains(id), ["compilationEligible"] = status is "available" or "feature-reference" or "output-assignment" or "local-assignment" or "private-graph" or "property-read" or "property-write" or "property-reference", ["includedInSource"] = false, ["compilerValidated"] = false });
            if (status is "missing" or "stale")
            { if (reachable.Contains(id)) missing.Add(id); }
            else if (body is not null)
            {
                bodies[id] = HasContext(node) ? body : body.Replace("\r\n", "\n");
            }
        }

        var sortedEdges = new JsonArray(edges.OrderBy(e => e.Key.Item1, StringComparer.Ordinal).ThenBy(e => e.Key.Item2, StringComparer.Ordinal).Select(e => (JsonNode)new JsonObject { ["from"] = e.Key.Item1, ["port"] = e.Key.Item2, ["to"] = e.Value }).ToArray());
        var topology=new JsonObject { ["entry"] = entry, ["edges"] = sortedEdges, ["exits"] = exits.DeepClone(), ["arguments"] = new JsonObject(nodes.OrderBy(n => n.Key, StringComparer.Ordinal).Select(n => new KeyValuePair<string, JsonNode?>(n.Key, n.Value.Arguments.DeepClone()))) };if(localProfile)topology["locals"]=LocalDocument(locals);
        string topologyHash = Hash(CanonicalText(topology));
        var reply = new JsonObject
        {
            ["state"] = missing.Count > 0 ? "needs-implementation" : "source-ready",
            ["feature"] = feature.Id,
            ["signature"] = contract.DeepClone(),
            ["profile"] = profile,
            ["generator"] = generator,
            ["contractHash"] = contractHash,
            ["topologyHash"] = topologyHash,
            ["nodes"] = manifestNodes,
            ["locals"] = LocalDocument(locals),
            ["disconnected"] = new JsonArray(nodes.Keys.Where(id => !reachable.Contains(id)).Order(StringComparer.Ordinal).Select(id => (JsonNode)JsonValue.Create(id)!).ToArray()),
            ["sourceWritten"] = false,
            ["compiled"] = false,
            ["executed"] = false
        };
        IEnumerable<string> NodeImports(Node node) => ((JsonObject)node.Definition["featureContracts"]!).Select(p => p.Key).Order(StringComparer.Ordinal);
        string ImportParameter(string feature) => Import(feature).Alias;
        string prefix="__fg_";if(nested)prefix+="p"+Hash(feature.Id+"/"+request["sourcePath"])[..16]+"_";if(multiOutput)while(feature.Signature!.Args.Any(p=>p.Name.StartsWith(prefix,StringComparison.Ordinal)))prefix="_"+prefix;
        string Symbol(string id) => prefix + Hash(id)[..32];
        string Cell(string id)=>Symbol(id)+"_field_cell";
        string Value(string id,string result="return") => nodes[id].Kind=="set"&&result=="stored"&&nodes[id].Definition["outputLocal"] is JsonValue storedLocal?LocalValue(storedLocal.GetValue<string>()):nodes[id].Kind=="property-ref"?Cell(id)+".Value":Symbol(id) + (result=="return"?"_value":"_out_"+Hash(result)[..16]);
        string Assigned(string name)=>prefix+"assigned_"+Hash(name)[..16];
        string ExecutionValue(string id)=>WrappedReturn(nodes[id])?Symbol(id)+"_branch":Value(id);
        string FeatureValue(string name)=>name=="return"?prefix+"output_return":name;
        string Label(string target) => Exit(target)||Terminal(target) ? prefix+"exit_" + Hash(target)[..32] : Symbol(target) + "_run";
        string Literal(JsonNode? value,string type)=>ConstantLiteral(value,type);
        string LocalValue(string id)=>prefix+"local_"+Hash(id)[..24];
        var finiteExpressionTypes=new HashSet<string>(StringComparer.Ordinal);
        var promotedExpressionTypes=new HashSet<(string From,string To)>();
        bool NumericPromotion(string from,string to)=>from is "int" or "long"&&to is "float" or "double";
        string Promote(string value,string from,string to){promotedExpressionTypes.Add((from,to));return prefix+"promote_"+from+"_"+to+"("+value+")";}
        string Binding(JsonNode? data, string type, HashSet<string> available, string subject,int depth=0,bool exact=false)
        {
            Need(depth<=12,"GRAPH_EXPRESSION_BUDGET",subject);
            var binding = data?.AsObject() ?? throw new Refusal("GRAPH_VALUE", subject);
            Need(binding.Count == 1 || binding.Count==2&&binding.ContainsKey("constant")&&binding.ContainsKey("type") || multiOutput && binding.Count == 2 && binding.ContainsKey("node") && binding.ContainsKey("output"), "GRAPH_VALUE", subject);
            if(binding.ContainsKey("constant")&&binding.ContainsKey("type")){
                string from=S(binding,"type");Need(from is "int" or "long" or "float" or "double","GRAPH_CONSTANT_TYPE",subject);string literal=Literal(binding["constant"],from);if(from==type)return literal;Need(!exact&&NumericPromotion(from,type),"GRAPH_NUMERIC_PROMOTION",subject);
                var datum=JsonSerializer.SerializeToElement(binding["constant"]);long original=datum.GetInt64();bool preserves=false;try{preserves=type=="float"?checked((long)(float)original)==original:checked((long)(double)original)==original;}catch(OverflowException){}Need(preserves,"GRAPH_NUMERIC_PRECISION",subject);return Promote(literal,from,type);
            }
            if(binding["binary"] is JsonObject binary){
                string op=S(binary,"operator"),valueType=binary["type"]?.GetValue<string>()??type;var operands=binary["operands"] as JsonArray;
                Need((binary.Count==2||binary.Count==3&&binary.ContainsKey("type"))&&binary.All(p=>p.Key is "operator" or "operands" or "type")&&operands?.Count==2,"GRAPH_EXPRESSION_SHAPE",subject);
                Need(valueType==type||!exact&&NumericPromotion(valueType,type),"GRAPH_EXPRESSION_TYPE",subject);
                Need(valueType is "int" or "long" or "float" or "double" ? op is "+" or "-" or "*" or "/" or "%" : valueType=="string" ? op=="+" : valueType=="bool"&&op is "AND" or "OR" or "XOR","GRAPH_EXPRESSION_OPERATOR",subject);
                if(op is "/" or "%" && operands![1] is JsonObject divisor && divisor["constant"] is JsonValue constant){var number=JsonSerializer.SerializeToElement(constant);if(number.ValueKind==JsonValueKind.Number)Need(number.GetDouble()!=0,"GRAPH_EXPRESSION_ZERO",subject);}
                string left=Binding(operands![0],valueType,available,subject+"/0",depth+1),right=Binding(operands[1],valueType,available,subject+"/1",depth+1);
                string result="("+left+") "+(op=="AND"?"&":op=="OR"?"|":op=="XOR"?"^":op)+" ("+right+")";
                if(valueType is "int" or "long")result="checked("+result+")";
                else if(valueType is "float" or "double"){finiteExpressionTypes.Add(valueType);result=prefix+"finite_"+valueType+"("+result+")";}
                else result="("+result+")";
                return valueType==type?result:Promote(result,valueType,type);
            }
            if (binding.ContainsKey("input"))
            {
                string name = S(binding, "input");
                var parameter = feature.Signature!.Args.SingleOrDefault(p => p.Name == name && !p.IsOut);
                Need(parameter is not null&&(parameter.Type==type||!exact&&NumericPromotion(parameter.Type,type)), "GRAPH_INPUT_TYPE", subject);
                return parameter!.Type==type?name:Promote(name,parameter.Type,type);
            }

            if (binding.ContainsKey("node"))
            {
                string source = S(binding, "node");
                string result=multiOutput&&binding.ContainsKey("output")?S(binding,"output"):"return";
                Need(available.Contains(source),"GRAPH_VALUE_UNAVAILABLE",subject);var output=NodeOutputs(nodes[source]).SingleOrDefault(p=>p.Name==result);Need(output is not null&&(output.Type==type||!exact&&NumericPromotion(output.Type,type)), "GRAPH_VALUE_UNAVAILABLE", subject);
                return output!.Type==type?Value(source,result):Promote(Value(source,result),output.Type,type);
            }

            if(binding.ContainsKey("local")){string id=S(binding,"local");Need(localProfile&&locals.ContainsKey(id),"GRAPH_LOCAL_TYPE",subject);var local=locals[id];string from=S(local,"type");Need(from==type||!exact&&NumericPromotion(from,type),"GRAPH_LOCAL_TYPE",subject);string value=local["source"] is JsonObject source?Binding(source,from,available,subject+"/alias:"+id,exact:true):LocalValue(id);return from==type?value:Promote(value,from,type);}
            if (binding.ContainsKey("constant"))
                return Literal(binding["constant"], type);
            throw new Refusal("GRAPH_VALUE", subject);
        }

        string ArgumentBinding(Parameter parameter,JsonNode? value,HashSet<string> available,string subject)
        {
            string expression=Binding(value,parameter.Type,available,subject,exact:parameter.IsRef);if(!parameter.IsRef)return expression;
            var binding=value!.AsObject();Need(refProfile&&!binding.ContainsKey("constant")&&(binding.ContainsKey("input")||binding.ContainsKey("local")||binding.ContainsKey("node")),"GRAPH_REF_STORAGE",subject);return "ref "+expression;
        }

        foreach (string id in order)
        {
            var node = nodes[id];
            var available = new HashSet<string>(dominators[id], StringComparer.Ordinal);
            available.Remove(id);
            Need(node.Arguments.Count == node.Signature.Args.Count(p=>!p.IsOut) && node.Signature.Args.Where(p=>!p.IsOut).All(p => node.Arguments.ContainsKey(p.Name)), "GRAPH_ARGUMENTS", id);
            foreach (var p in node.Signature.Args.Where(p=>!p.IsOut))
                ArgumentBinding(p,node.Arguments[p.Name],available,id+"/"+p.Name);
            if(node.Kind=="set"&&locals[S(node.Definition,"local")]["source"] is JsonObject source)Binding(source,S(locals[S(node.Definition,"local")],"type"),available,id+"/target");
        }

        foreach (var exit in exits)
        {
            string target = "exit:" + exit.Key;
            var incoming = edges.Where(e => e.Value == target && reachable.Contains(e.Key.Item1)).Select(e => e.Key.Item1).ToArray();
            if (incoming.Length == 0 && entry != target)
                continue;
            var available = incoming.Length == 0 ? new HashSet<string>(StringComparer.Ordinal) : new HashSet<string>(dominators[incoming[0]], StringComparer.Ordinal);
            foreach (string p in incoming.Skip(1))
                available.IntersectWith(dominators[p]);
            if (feature.Signature!.Return != "void"&&(!implicitEnd||exit.Value is not null))
                Binding(exit.Value, feature.Signature.Return, available, target);
        }

        if(implicitEnd){var flow=switchFlow?DescribeSwitchTerminations(entry,feature,nodes,edges,order,predecessors,exits,forwardedOutputs,switchRouting.Item3):multiOutput?DescribeMultiTerminations(entry,feature,nodes,edges,order,predecessors,exits,externalRefs?forwardedOutputs:null):DescribeImplicitTerminations(entry,feature,nodes,edges,order,predecessors,exits);reply["outputs"]=OutputDocument(feature.Signature!);reply["terminations"]=flow.Ends;reply["warnings"]=flow.Warnings;reply["unassignedReturnPolicy"]="csharp-type-default";}
        if(switchFlow){reply["branchReturns"]=branchReturns;reply["continuations"]=new JsonObject(continuations.Select(p=>new KeyValuePair<string,JsonNode?>(p.Key,JsonValue.Create(p.Value))));reply["executionModel"]="sequential-switch-continuation";}
        reply["contractVersions"] = new JsonObject(imports.OrderBy(p => p.Key, StringComparer.Ordinal).Select(p => new KeyValuePair<string, JsonNode?>(p.Key, JsonValue.Create(p.Value.Hash))));
        reply["contractVersions"]![feature.Id] = contractHash;
        reply["imports"] = new JsonArray(imports.OrderBy(i => i.Key, StringComparer.Ordinal).Select(i => (JsonNode)new JsonObject { ["feature"] = i.Key, ["alias"] = i.Value.Alias, ["contractHash"] = i.Value.Hash, ["binding"] = canonicalImports.Contains(i.Key) ? "canonical" : "implementation-context", ["signature"] = SignatureNode(i.Value.Element.Signature!) }).ToArray());
        if (operation == "featureBlueprintDescribe" || missing.Count > 0)
            return reply;
        var output = new StringBuilder();
        var membersOutput = new StringBuilder();
        foreach(string type in finiteExpressionTypes.OrderBy(t=>t,StringComparer.Ordinal))output.AppendLine("static "+type+" "+prefix+"finite_"+type+"("+type+" value) => global::System."+(type=="float"?"Single":"Double")+".IsFinite(value) ? value : throw new global::System.ArithmeticException(\"Non-finite Blueprint expression\");");
        foreach(var pair in promotedExpressionTypes.OrderBy(p=>p.From,StringComparer.Ordinal).ThenBy(p=>p.To,StringComparer.Ordinal))output.AppendLine("static "+pair.To+" "+prefix+"promote_"+pair.From+"_"+pair.To+"("+pair.From+" value) { "+pair.To+" result = value; if (checked((long)result) != (long)value) throw new global::System.ArithmeticException(\"Blueprint integer promotion loses precision\"); return result; }");
        if(localProfile)output.AppendLine("#pragma warning disable CS0219");
        if(implicitEnd&&feature.Signature!.Return!="void")output.AppendLine(feature.Signature.Return+" "+FeatureValue("return")+" = default("+feature.Signature.Return+")!;"+(localProfile?"":"\n_ = "+FeatureValue("return")+";"));
        if(multiOutput)foreach(var parameter in feature.Signature!.Args.Where(p=>p.IsOut)){
            // Definite-assignment marker only: SkipInit does not write caller storage.
            // A missing graph out gets its default at termination, after all alias-visible work.
            if(externalRefs)output.AppendLine("global::System.Runtime.CompilerServices.Unsafe.SkipInit(out "+parameter.Name+");\nbool "+Assigned(parameter.Name)+" = false;");
            else output.AppendLine(parameter.Name+" = default("+parameter.Type+")!;");
        }
        foreach(var local in locals.Where(p=>p.Value["source"] is null))output.AppendLine(S(local.Value,"type")+" "+LocalValue(local.Key)+" = "+Literal(local.Value["initial"]!["constant"],S(local.Value,"type"))+";");
        if(localProfile)output.AppendLine("#pragma warning restore CS0219");
        foreach (string id in order.Where(id=>nodes[id].Kind!="set"))foreach(var result in NodeOutputs(nodes[id]))
            output.AppendLine(nodes[id].Kind=="property-ref"?FieldCellType(nodes[id])+" "+Cell(id)+";":result.Type + " " + Value(id,result.Name) + ";");
        if(switchFlow)foreach(string id in order.Where(id=>nodes[id].Control=="switch"))output.AppendLine("int "+ExecutionValue(id)+";");
        foreach (string id in definitionOrder.Where(id => bodies.ContainsKey(id) || nodes[id].Kind == "call"))
        {
            var node = nodes[id];
            if (HasContext(node))
            {
                string contextMarker = ContextMarker(node,"node:" + feature.Id + "/" + id + "@" + manifestNodes.Single(n => n!["id"]!.ToString() == id)!["implementationHash"]!.ToString());
                membersOutput.Append(ContextMember(node, bodies[id], contextMarker));
                sourceMaps.Add(new JsonObject { ["node"] = id, ["definitionHash"] = node.DefinitionHash, ["marker"] = contextMarker });
                manifestNodes.Single(n => n!["id"]!.ToString() == id)!["includedInSource"] = true;
                continue;
            }
            // A prepared independent node is checked without calling it or allocating a delegate.
            // Suppress only the generated local function declaration's unused warning.
            if (!reachable.Contains(id)) output.AppendLine("#pragma warning disable CS8321");
            output.AppendLine("static " + ExecutionType(node) + " " + Symbol(id) + "(" + string.Join(",", node.Signature.Args.Select(p => p.Declaration()).Concat(WrappedReturn(node) ? new[] { "out " + node.Signature.Return + " __fg_wrapped_return" } : Array.Empty<string>()).Concat(NodeImports(node).Select(f => Generation.Interface(f) + " " + ImportParameter(f)))) + ") {");
            if (!reachable.Contains(id)) output.AppendLine("#pragma warning restore CS8321");
            string marker = "node:" + feature.Id + "/" + id + "@" + manifestNodes.Single(n => n!["id"]!.ToString() == id)![node.Kind == "call" ? "definitionHash" : "implementationHash"]!.ToString();
            output.AppendLine("#line 1 " + JsonSerializer.Serialize(marker));
            if (node.Kind == "call" && node.Definition["postCall"] is JsonObject postCall) {
                string type = MethodClass(request, id) + "_after";
                membersOutput.Append(node.Control == "switch" ? BlueprintCallWrapper.Member(Import(node.Feature!).Element, postCall, node.Definition["executionEnum"]!.AsObject(), type, Generation.Interface(node.Feature!), marker) : BlueprintCallAfter.Member(Import(node.Feature!).Element, postCall, type, Generation.Interface(node.Feature!), marker));
                output.AppendLine((ExecutionType(node) == "void" ? "" : "return ") + (node.Control == "switch" ? "(int)" : "") + type + ".Execute(" + ImportParameter(node.Feature!) + (node.Signature.Args.Count > 0 ? ", " : "") + string.Join(", ", node.Signature.Args.Select(p => (p.Mode is "out" or "ref" ? p.Mode + " " : "") + p.Name)) + (WrappedReturn(node) ? ", out __fg_wrapped_return" : "") + ");");
            }
            else if (node.Kind == "call")
                output.AppendLine((node.Signature.Return == "void" ? "" : "return ") + ImportParameter(node.Feature!) + ".Invoke(" + string.Join(",", node.Signature.Args.Select(p => (p.Mode is "out" or "ref"?p.Mode+" ":"")+p.Name)) + ");");
            else if (node.Kind == "code" && SupportsMethods(profile)) {
                string type=MethodClass(request,id);
                membersOutput.Append(MethodsMember(type,node,string.Join(",",node.Signature.Args.Select(p=>p.Declaration()).Concat(NodeImports(node).Select(f=>Generation.Interface(f)+" "+ImportParameter(f)))),bodies[id],helpers[id],marker));
                output.AppendLine((ExecutionType(node)=="void"?"":"return ")+(node.Control=="switch"?"(int)":"")+type+".Execute("+string.Join(",",node.Signature.Args.Select(p=>(p.Mode is "ref" or "out"?p.Mode+" ":"")+p.Name).Concat(NodeImports(node).Select(ImportParameter)))+");");
            }
            else
                output.AppendLine(bodies[id]);
            output.AppendLine("#line default\n}");
            sourceMaps.Add(new JsonObject { ["node"] = id, ["definitionHash"] = node.DefinitionHash, ["marker"] = marker });
            manifestNodes.Single(n => n!["id"]!.ToString() == id)!["includedInSource"] = true;
        }

        output.AppendLine("#line 1 " + JsonSerializer.Serialize("graph:" + feature.Id + "@" + topologyHash));
        output.AppendLine("goto " + Label(entry) + ";");
        foreach (string id in order)
        {
            var node = nodes[id];
            var available = new HashSet<string>(dominators[id], StringComparer.Ordinal);
            available.Remove(id);
            Need(node.Arguments.Count == node.Signature.Args.Count(p=>!p.IsOut) && node.Signature.Args.Where(p=>!p.IsOut).All(p => node.Arguments.ContainsKey(p.Name)), "GRAPH_ARGUMENTS", id);
            output.AppendLine(Label(id) + ": {");
            if(node.Kind=="property-ref"){
                output.AppendLine(Cell(id)+" = "+FieldCellAccess(node,Binding(node.Arguments["target"],"object",available,id+"/target"),(request["sourcePath"] is null?"calls.":"")+Import(PropertyRefAccessor).Alias)+";");
                manifestNodes.Single(n=>n!["id"]!.ToString()==id)!["includedInSource"]=true;
            }
            else if(node.Kind=="set"){
                string local=S(node.Definition,"local"),target=locals[local]["source"] is JsonObject source?Binding(source,S(locals[local],"type"),available,id+"/target"):LocalValue(local),value=Binding(node.Arguments["value"],S(locals[local],"type"),available,id+"/value");
                if(node.Definition["outputLocal"] is JsonValue stored){string temporary=Symbol(id)+"_set_value";output.AppendLine(S(locals[local],"type")+" "+temporary+" = "+value+";\n"+target+" = "+temporary+";\n"+LocalValue(stored.GetValue<string>())+" = "+temporary+";");}else output.AppendLine(target+" = "+value+";");
                manifestNodes.Single(n=>n!["id"]!.ToString()==id)!["includedInSource"]=true;
            }
            else if(node.Kind=="export"){
                string exported=S(node.Definition,"output"),outputType=FeatureOutputs(feature.Signature!).Single(p=>p.Name==exported).Type;
                output.AppendLine(FeatureValue(exported)+" = "+Binding(node.Arguments["value"],outputType,available,id+"/value")+";");
                if(externalRefs&&exported!="return")output.AppendLine(Assigned(exported)+" = true;");
                sourceMaps.Add(new JsonObject{["node"]=id,["definitionHash"]=node.DefinitionHash,["marker"]="graph:"+feature.Id+"@"+topologyHash});manifestNodes.Single(n=>n!["id"]!.ToString()==id)!["includedInSource"]=true;
            }
            else output.AppendLine((ExecutionType(node) == "void" ? "" : ExecutionValue(id) + " = ") + (HasContext(node) ? "this.Invoke" : Symbol(id)) + "(" + string.Join(",", node.Signature.Args.Select(p => p.IsOut?"out "+(ForwardCaller(node)?CallerOut(node,p.Name):Value(id,p.Name)):ArgumentBinding(p,node.Arguments[p.Name],available,id+"/"+p.Name)).Concat(WrappedReturn(node) ? new[] { "out " + Value(id) } : Array.Empty<string>()).Concat(HasContext(node) ? Array.Empty<string>() : NodeImports(node).Select(f => (request["sourcePath"] is null ? "calls." : "") + Import(f).Alias))) + ");");
            if(ForwardCaller(node))foreach(var parameter in node.Signature.Args.Where(p=>p.IsOut))output.AppendLine(Value(id,parameter.Name)+" = "+CallerOut(node,parameter.Name)+";\n"+Assigned(CallerOut(node,parameter.Name))+" = true;");
            if(node.Control=="switch"){
                output.AppendLine("switch ("+ExecutionValue(id)+") {");
                foreach(var member in node.Definition["executionEnum"]!["members"]!.AsArray())if(edges.TryGetValue((id,"case:"+S(member,"id")),out string? target))output.AppendLine("case "+member!["value"]!.ToJsonString()+": goto "+Label(target)+";");
                output.AppendLine("default: goto "+Label(edges.TryGetValue((id,"default"),out string? fallback)?fallback:continuations[id])+";\n}");
            }
            else if (node.Control == "branch")
                output.AppendLine("if (" + Value(id) + ") goto " + Label(edges[(id, "true")]) + "; else goto " + Label(edges[(id, "false")]) + ";");
            else
                output.AppendLine("goto " + Label(edges[(id, "next")]) + ";");
            output.AppendLine("}");
        }

        string CompleteOuts()=>externalRefs?string.Join(" ",feature.Signature!.Args.Where(p=>p.IsOut).Select(p=>"if (!"+Assigned(p.Name)+") "+p.Name+" = default("+p.Type+")!; ")):"";
        foreach (var exit in exits.OrderBy(e => e.Key, StringComparer.Ordinal))
        {
            string target = "exit:" + exit.Key;
            var incoming = edges.Where(e => e.Value == target && reachable.Contains(e.Key.Item1)).Select(e => e.Key.Item1).ToArray();
            if (incoming.Length == 0 && entry != target)
                continue;
            var available = incoming.Length == 0 ? new HashSet<string>(StringComparer.Ordinal) : new HashSet<string>(dominators[incoming[0]], StringComparer.Ordinal);
            foreach (string p in incoming.Skip(1))
                available.IntersectWith(dominators[p]);
            output.AppendLine(Label(target) + ": { "+CompleteOuts()+"return" + (feature.Signature!.Return == "void" ? "" : " " + (implicitEnd&&exit.Value is null?FeatureValue("return"):Binding(exit.Value, feature.Signature.Return, available, target))) + "; }");
        }

        if(implicitEnd)foreach(string target in edges.Where(edge=>reachable.Contains(edge.Key.Item1)).Select(edge=>edge.Value).Append(entry).Where(Terminal).Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal))output.AppendLine(Label(target)+": { "+CompleteOuts()+"return"+(feature.Signature!.Return=="void"?"":" "+FeatureValue("return"))+"; }");
        output.AppendLine("#line default");
        reply["state"] = "source-assembled";
        reply["body"] = output.ToString().Replace("\r\n", "\n");
        reply["members"] = membersOutput.ToString();
        reply["explicitEntry"] = multiOutput || nodes.Values.Any(HasContext);
        reply["entrySignature"] = contract.DeepClone();
        reply["bodyHash"] = Hash(reply["body"]!.ToString()+membersOutput);
        reply["sourceMap"] = sourceMaps;
        reply["graphMap"] = new JsonObject { ["marker"] = "graph:" + feature.Id + "@" + topologyHash, ["jsonPointer"] = "/edges", ["topologyHash"] = topologyHash };
        reply["nodeSources"] = new JsonArray(bodies.Where(p => nodes[p.Key].Kind == "code").OrderBy(p => p.Key, StringComparer.Ordinal).Select(p => (JsonNode)new JsonObject { ["id"] = p.Key, ["source"] = p.Value, ["helpers"] = helpers[p.Key], ["preserveImplementationContext"] = HasContext(nodes[p.Key]), ["marker"] = sourceMaps.Single(n => n!["node"]!.ToString() == p.Key)!["marker"]!.DeepClone() }).ToArray());
        reply["imports"] = new JsonArray(imports.OrderBy(i => i.Key, StringComparer.Ordinal).Select(i => (JsonNode)new JsonObject { ["feature"] = i.Key, ["alias"] = i.Value.Alias, ["contractHash"] = i.Value.Hash, ["binding"] = canonicalImports.Contains(i.Key) ? "canonical" : "implementation-context", ["signature"] = SignatureNode(i.Value.Element.Signature!) }).ToArray());
        return reply;
    }
}
