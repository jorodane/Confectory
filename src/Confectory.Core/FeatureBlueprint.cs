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
        ["args"] = new JsonArray(signature.Args.Select(p => { var row=new JsonObject { ["type"] = p.Type, ["name"] = p.Name }; if(p.IsOut)row["mode"]="out"; return (JsonNode)row; }).ToArray()),
        ["return"] = signature.Return
    };
    static JsonObject SignatureNode(FunctionSignature signature) => SignatureDocument(signature);
    static string SignatureText(FunctionSignature signature, bool names) => signature.Format(names);
    static FunctionSignature Signature(JsonNode value)
    {
        var args = value["args"]!.AsArray();
        var signature = new FunctionSignature(args.Select(p => new Parameter(S(p, "type"), S(p, "name"), p?["mode"]?.GetValue<string>())).ToList(), S(value, "return"));
        Need(signature.Args.All(p => p.Mode is null or "out"), "GRAPH_PARAMETER_MODE", "signature");
        var parsed = new Parser("function Blueprint.Validation::Node " + SignatureText(signature, true) + " {}", "<node-contract>").ParseElement();
        Need(parsed.Signature is not null, "NODE_CONTRACT", "signature");
        return parsed.Signature!;
    }

    public static JsonObject Execute(JsonObject request)
    {
        try
        {
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
    static JsonObject Process(JsonObject request)
    {
        string operation = S(request, "operation");
        Need(operation is "featureBlueprintDescribe" or "featureBlueprintAssemble" or "featureBlueprintNodes" or "featureBlueprintNodeProbe", "GRAPH_OPERATION", operation);
        var feature = new Parser(S(request, "featureSource"), "<feature-contract>").ParseElement();
        Need(feature.Kind == "function" && feature.Signature is not null, "GRAPH_FEATURE_CONTRACT", feature.Id);
        var contract = SignatureNode(feature.Signature!);
        string contractHash = Hash(CanonicalText(new JsonObject { ["feature"] = feature.Id, ["signature"] = contract.DeepClone() }));
        var graph = request["graph"]!.AsObject();
        Need(graph["schema"]?.GetValue<int>() == 1, "GRAPH_SCHEMA", "schema");
        string profile=S(graph,"profile");bool multiOutput=profile==MultiOutputProfile, implicitEnd=profile==ImplicitProfile||multiOutput;string generator=multiOutput?MultiOutputGenerator:implicitEnd?ImplicitGenerator:Generator;
        Need(profile==Profile||implicitEnd,"GRAPH_PROFILE_UNSUPPORTED",profile);
        Need(multiOutput || !feature.Signature!.Args.Any(p=>p.IsOut), "GRAPH_PARAMETER_MODE_PROFILE", profile);
        Need(S(graph, "feature") == feature.Id, "GRAPH_FEATURE_MISMATCH", "feature");
        Need(S(graph, "contractHash") == contractHash, "GRAPH_CONTRACT_STALE", feature.Id);
        var canonicalImports = new HashSet<string>(StringComparer.Ordinal);
        var imports = new Dictionary<string, (Element Element, string Alias, string Hash)>(StringComparer.Ordinal);
        (Element Element, string Alias, string Hash) Import(string id, bool canonical = true)
        {
            if (canonical) canonicalImports.Add(id);
            if (imports.TryGetValue(id, out var known))
                return known;
            string source = id == feature.Id ? S(request, "featureSource") : request["featureContracts"]?[id]?.GetValue<string>() ?? throw new Refusal("GRAPH_CALLEE_MISSING", id);
            var element = new Parser(source, "<called-feature>").ParseElement();
            Need(element.Id == id && element.Kind == "function" && element.Signature is not null, "GRAPH_CALLEE_CONTRACT", id);
            string hash = Hash(CanonicalText(new JsonObject { ["feature"] = id, ["signature"] = SignatureNode(element.Signature!) }));
            var result = (element, ImportAlias(id), hash);
            imports.Add(id, result);
            return result;
        }

        if(multiOutput)Need(feature.Signature!.Args.Count<=64&&graph["nodes"]!.AsArray().Count<=256,"GRAPH_MULTI_OUTPUT_BUDGET",feature.Id);
        var nodes = new Dictionary<string, Node>(StringComparer.Ordinal);
        foreach (var item in graph["nodes"]!.AsArray())
        {
            var value = item!.AsObject();
            string id = Id(value, "id"), kind = S(value, "kind"), control = S(value, "control"), intent = S(value, "intent");
            Need(!nodes.ContainsKey(id), "GRAPH_DUPLICATE_NODE", id);
            Need(kind is "code" or "call" || implicitEnd && kind=="export", "GRAPH_NODE_KIND", id);
            Need(control is "next" or "branch", "GRAPH_CONTROL", id);
            Need(!string.IsNullOrWhiteSpace(intent), "NODE_INTENT", id);
            var signature = Signature(value["signature"]!);
            Need(multiOutput || !signature.Args.Any(p=>p.IsOut), "GRAPH_PARAMETER_MODE_PROFILE", id);
            Need(value["implementationContext"] is JsonObject || !signature.Args.Any(p => (p.Name.StartsWith("__fg_", StringComparison.Ordinal) || p.Name.StartsWith("fg_call_", StringComparison.Ordinal))), "NODE_RESERVED_NAME", id);
            Need(control != "branch" || signature.Return == "bool", "GRAPH_BRANCH_TYPE", id);
            if(kind=="export")Need(signature.Args.Count==1&&!signature.Args[0].IsOut&&signature.Args[0].Name=="value"&&FeatureOutputs(feature.Signature!).Any(p=>p.Name==S(value,"output")&&p.Type==signature.Args[0].Type)&&control=="next"&&signature.Return=="void","GRAPH_OUTPUT_CONTRACT",id);
            var references = new JsonObject();
            string? called = null;
            if (kind == "call")
            {
                called = S(value, "feature");
                var imported = Import(called);
                Need(signature.Matches(imported.Element.Signature), "GRAPH_CALLEE_SIGNATURE", id);
                references[called] = imported.Hash;
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
            if(kind=="export")definition["output"]=S(value,"output");
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
            nodes.Add(id, new(id, kind, control, signature, definition, value["arguments"]?.AsObject() ?? new JsonObject(), Hash(CanonicalText(definition)), called));
        }

        if (operation == "featureBlueprintNodeProbe")
        {
            string id = S(request, "node");
            Need(nodes.TryGetValue(id, out var selected) && selected.Kind == "code", "NODE_CODE_REQUIRED", id);
            var node = selected!;
            var record = request["implementations"]?[id];
            Need(record?["schema"]?.GetValue<int>() == 1 && record["node"]?.ToString() == id && record["definitionHash"]?.ToString() == node.DefinitionHash, "NODE_IMPLEMENTATION_STALE", id);
            string source = HasContext(node) ? S(record,"source") : S(record, "source").Replace("\r\n", "\n"), marker = "node:" + feature.Id + "/" + id + "@" + Hash(source);
            var used = node.Definition["featureContracts"]!.AsObject().Select(p => p.Key).Order(StringComparer.Ordinal).ToArray();
            string code = "#pragma warning disable CS8321\nstatic " + node.Signature.Return + " __fg_probe_" + Hash(id)[..24] + "(" + string.Join(",", node.Signature.Args.Select(p => p.Declaration()).Concat(used.Select(f => Generation.Interface(f) + " " + Import(f).Alias))) + ") {\n#pragma warning restore CS8321\n#line 1 " + JsonSerializer.Serialize(marker) + "\n" + source + "\n#line default\n}\n";
            marker = ContextMarker(node,marker);
            string members = HasContext(node) ? ContextMember(node, source, marker) : "";
            if (HasContext(node)) code = "throw new global::System.InvalidOperationException(\"Independent context probe must never execute\");";
            string graphHash = Hash(CanonicalText(graph));
            return new JsonObject
            {
                ["state"] = "node-source-assembled", ["mode"] = "independent-node", ["profile"] = profile, ["generator"] = generator, ["feature"] = feature.Id,
                ["node"] = id, ["definitionHash"] = node.DefinitionHash, ["body"] = code, ["members"] = members, ["explicitEntry"] = HasContext(node), ["entrySignature"] = contract.DeepClone(), ["bodyHash"] = Hash(code+members),
                ["nodes"] = new JsonArray(new JsonObject { ["id"] = id, ["definitionHash"] = node.DefinitionHash, ["definition"] = node.Definition.DeepClone(), ["status"] = "available", ["compilationEligible"] = true, ["includedInSource"] = true, ["compilerValidated"] = false }),
                ["sourceMap"] = new JsonArray(new JsonObject { ["node"] = id, ["definitionHash"] = node.DefinitionHash, ["marker"] = marker }),
                ["nodeSources"] = new JsonArray(new JsonObject { ["id"] = id, ["source"] = source, ["marker"] = marker, ["preserveImplementationContext"] = HasContext(node) }),
                ["graphMap"] = new JsonObject { ["marker"] = "graph:" + feature.Id + "@" + graphHash, ["jsonPointer"] = "/nodes/" + graph["nodes"]!.AsArray().IndexOf(graph["nodes"]!.AsArray().Single(n => n!["id"]!.ToString() == id)), ["topologyHash"] = graphHash },
                ["imports"] = new JsonArray(used.Select(f => (JsonNode)new JsonObject { ["feature"] = f, ["alias"] = Import(f).Alias, ["contractHash"] = Import(f,false).Hash, ["binding"] = HasContext(node) ? "implementation-context" : "canonical" }).ToArray()),
                ["sourceWritten"] = false, ["compiled"] = false, ["executed"] = false
            };
        }

        if (operation == "featureBlueprintNodes")
        {
            var versions = new JsonObject(imports.OrderBy(p => p.Key, StringComparer.Ordinal).Select(p => new KeyValuePair<string, JsonNode?>(p.Key, JsonValue.Create(p.Value.Hash))));
            versions[feature.Id] = contractHash;
            return new JsonObject
            {
                ["state"] = "node-definitions", ["feature"] = feature.Id, ["profile"] = profile, ["contractHash"] = contractHash, ["signature"] = contract.DeepClone(),
                ["nodes"] = new JsonArray(nodes.OrderBy(p => p.Key, StringComparer.Ordinal).Select(p => (JsonNode)new JsonObject { ["id"] = p.Key, ["definitionHash"] = p.Value.DefinitionHash, ["definition"] = p.Value.Definition.DeepClone(), ["outputs"] = OutputDocument(p.Value.Signature) }).ToArray()),
                ["outputs"] = OutputDocument(feature.Signature!), ["contractVersions"] = versions,
                ["imports"] = new JsonArray(imports.OrderBy(i => i.Key, StringComparer.Ordinal).Select(i => (JsonNode)new JsonObject { ["feature"] = i.Key, ["alias"] = i.Value.Alias, ["contractHash"] = i.Value.Hash, ["binding"] = canonicalImports.Contains(i.Key) ? "canonical" : "implementation-context", ["signature"] = SignatureNode(i.Value.Element.Signature!) }).ToArray()),
                ["independentNodeCompilation"] = true, ["sourceWritten"] = false, ["compiled"] = false, ["executed"] = false
            };
        }

        string entry = S(graph, "entry");
        var exits = graph["exits"]!.AsObject();
        var edges = new Dictionary<(string, string), string>();
        bool Exit(string target) => target.StartsWith("exit:", StringComparison.Ordinal) && exits.ContainsKey(target[5..]);
        void Target(string target) => Need(nodes.ContainsKey(target) || Exit(target), "GRAPH_TARGET", target);
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

        var reachable = new HashSet<string>(StringComparer.Ordinal);
        var stack = new HashSet<string>(StringComparer.Ordinal);
        var order = new List<string>();
        void Visit(string id)
        {
            if (Exit(id) || Terminal(id) || reachable.Contains(id))
                return;
            Need(stack.Add(id), "GRAPH_CYCLE_PROFILE_UNSUPPORTED", id);
            if(implicitEnd){string[] expected=nodes[id].Control=="branch"?["true","false"]:["next"];Need(edges.Keys.Where(k=>k.Item1==id).All(k=>expected.Contains(k.Item2)),"GRAPH_PORTS",id);foreach(string port in expected)edges.TryAdd((id,port),"end:"+id+"/"+port);}
            foreach (var target in edges.Where(p => p.Key.Item1 == id).OrderBy(p => p.Key.Item2, StringComparer.Ordinal))
                Visit(target.Value);
            stack.Remove(id);
            reachable.Add(id);
            order.Add(id);
        }

        Visit(entry);
        foreach (var node in nodes.Values.Where(n => reachable.Contains(n.Id)))
        {
            string[] ports = node.Control == "branch" ? ["true", "false"] : ["next"];
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
        var missing = new List<string>();
        var definitionOrder = order.Concat(nodes.Keys.Where(id => !reachable.Contains(id)).Order(StringComparer.Ordinal)).ToArray();
        foreach (string id in definitionOrder)
        {
            var node = nodes[id];
            JsonNode? record = request["implementations"]?[id];
            string? body = node.Kind == "call" ? null : record?["source"]?.GetValue<string>();
            string? codeHash = body is null ? null : Hash(HasContext(node) ? body : body.Replace("\r\n", "\n"));
            string status = node.Kind == "export" ? "output-assignment" : node.Kind == "call" ? "feature-reference" : body is null ? "missing" : record?["definitionHash"]?.ToString() != node.DefinitionHash ? "stale" : "available";
            manifestNodes.Add(new JsonObject { ["id"] = id, ["definitionHash"] = node.DefinitionHash, ["definition"] = node.Definition.DeepClone(), ["implementationHash"] = codeHash, ["status"] = status, ["reachable"] = reachable.Contains(id), ["compilationEligible"] = status is "available" or "feature-reference" or "output-assignment", ["includedInSource"] = false, ["compilerValidated"] = false });
            if (status is "missing" or "stale")
            { if (reachable.Contains(id)) missing.Add(id); }
            else if (body is not null)
            {
                bodies[id] = HasContext(node) ? body : body.Replace("\r\n", "\n");
            }
        }

        var sortedEdges = new JsonArray(edges.OrderBy(e => e.Key.Item1, StringComparer.Ordinal).ThenBy(e => e.Key.Item2, StringComparer.Ordinal).Select(e => (JsonNode)new JsonObject { ["from"] = e.Key.Item1, ["port"] = e.Key.Item2, ["to"] = e.Value }).ToArray());
        string topologyHash = Hash(CanonicalText(new JsonObject { ["entry"] = entry, ["edges"] = sortedEdges, ["exits"] = exits.DeepClone(), ["arguments"] = new JsonObject(nodes.OrderBy(n => n.Key, StringComparer.Ordinal).Select(n => new KeyValuePair<string, JsonNode?>(n.Key, n.Value.Arguments.DeepClone()))) }));
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
            ["disconnected"] = new JsonArray(nodes.Keys.Where(id => !reachable.Contains(id)).Order(StringComparer.Ordinal).Select(id => (JsonNode)JsonValue.Create(id)!).ToArray()),
            ["sourceWritten"] = false,
            ["compiled"] = false,
            ["executed"] = false
        };
        IEnumerable<string> NodeImports(Node node) => ((JsonObject)node.Definition["featureContracts"]!).Select(p => p.Key).Order(StringComparer.Ordinal);
        string ImportParameter(string feature) => Import(feature).Alias;
        string prefix="__fg_";if(multiOutput)while(feature.Signature!.Args.Any(p=>p.Name.StartsWith(prefix,StringComparison.Ordinal)))prefix="_"+prefix;
        string Symbol(string id) => prefix + Hash(id)[..32];
        string Value(string id,string result="return") => Symbol(id) + (result=="return"?"_value":"_out_"+Hash(result)[..16]);
        string FeatureValue(string name)=>name=="return"?prefix+"output_return":name;
        string Label(string target) => Exit(target)||Terminal(target) ? "__fg_exit_" + Hash(target)[..32] : Symbol(target) + "_run";
        string Literal(JsonNode? value, string type)
        {
            if (type.EndsWith("[]", StringComparison.Ordinal))
            {
                Need(value is JsonArray, "GRAPH_CONSTANT_TYPE", type);
                return "new " + type[..^2] + "[]{" + string.Join(",", value!.AsArray().Select(v => Literal(v, type[..^2]))) + "}";
            }

            var datum = JsonSerializer.SerializeToElement(value);
            return type switch
            {
                "string" when datum.ValueKind == JsonValueKind.String => JsonSerializer.Serialize(datum.GetString()),
                "bool" when datum.ValueKind is JsonValueKind.True or JsonValueKind.False => datum.GetBoolean() ? "true" : "false",
                "int" when datum.ValueKind == JsonValueKind.Number && datum.TryGetInt32(out int n) => n.ToString(CultureInfo.InvariantCulture),
                "long" when datum.ValueKind == JsonValueKind.Number && datum.TryGetInt64(out long n) => n == long.MinValue ? "long.MinValue" : n.ToString(CultureInfo.InvariantCulture) + "L",
                "float" when datum.ValueKind == JsonValueKind.Number && datum.TryGetSingle(out float n) && float.IsFinite(n) => n.ToString("R", CultureInfo.InvariantCulture) + "F",
                "double" when datum.ValueKind == JsonValueKind.Number && datum.TryGetDouble(out double n) && double.IsFinite(n) => n.ToString("R", CultureInfo.InvariantCulture) + "D",
                _ => throw new Refusal("GRAPH_CONSTANT_TYPE", type)};
        }

        string Binding(JsonNode? data, string type, HashSet<string> available, string subject)
        {
            var binding = data?.AsObject() ?? throw new Refusal("GRAPH_VALUE", subject);
            Need(binding.Count == 1 || multiOutput && binding.Count == 2 && binding.ContainsKey("node") && binding.ContainsKey("output"), "GRAPH_VALUE", subject);
            if (binding.ContainsKey("input"))
            {
                string name = S(binding, "input");
                var parameter = feature.Signature!.Args.SingleOrDefault(p => p.Name == name && !p.IsOut);
                Need(parameter is not null && parameter.Type == type, "GRAPH_INPUT_TYPE", subject);
                return name;
            }

            if (binding.ContainsKey("node"))
            {
                string source = S(binding, "node");
                string result=multiOutput&&binding.ContainsKey("output")?S(binding,"output"):"return";
                Need(available.Contains(source) && FeatureOutputs(nodes[source].Signature).Any(p=>p.Name==result&&p.Type==type), "GRAPH_VALUE_UNAVAILABLE", subject);
                return Value(source,result);
            }

            if (binding.ContainsKey("constant"))
                return Literal(binding["constant"], type);
            throw new Refusal("GRAPH_VALUE", subject);
        }

        foreach (string id in order)
        {
            var node = nodes[id];
            var available = new HashSet<string>(dominators[id], StringComparer.Ordinal);
            available.Remove(id);
            Need(node.Arguments.Count == node.Signature.Args.Count(p=>!p.IsOut) && node.Signature.Args.Where(p=>!p.IsOut).All(p => node.Arguments.ContainsKey(p.Name)), "GRAPH_ARGUMENTS", id);
            foreach (var p in node.Signature.Args.Where(p=>!p.IsOut))
                Binding(node.Arguments[p.Name], p.Type, available, id + "/" + p.Name);
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

        if(implicitEnd){var flow=multiOutput?DescribeMultiTerminations(entry,feature,nodes,edges,order,predecessors,exits):DescribeImplicitTerminations(entry,feature,nodes,edges,order,predecessors,exits);reply["outputs"]=OutputDocument(feature.Signature!);reply["terminations"]=flow.Ends;reply["warnings"]=flow.Warnings;reply["unassignedReturnPolicy"]="csharp-type-default";}
        reply["contractVersions"] = new JsonObject(imports.OrderBy(p => p.Key, StringComparer.Ordinal).Select(p => new KeyValuePair<string, JsonNode?>(p.Key, JsonValue.Create(p.Value.Hash))));
        reply["contractVersions"]![feature.Id] = contractHash;
        reply["imports"] = new JsonArray(imports.OrderBy(i => i.Key, StringComparer.Ordinal).Select(i => (JsonNode)new JsonObject { ["feature"] = i.Key, ["alias"] = i.Value.Alias, ["contractHash"] = i.Value.Hash, ["binding"] = canonicalImports.Contains(i.Key) ? "canonical" : "implementation-context", ["signature"] = SignatureNode(i.Value.Element.Signature!) }).ToArray());
        if (operation == "featureBlueprintDescribe" || missing.Count > 0)
            return reply;
        var output = new StringBuilder();
        var membersOutput = new StringBuilder();
        if(implicitEnd&&feature.Signature!.Return!="void")output.AppendLine(feature.Signature.Return+" "+FeatureValue("return")+" = default("+feature.Signature.Return+")!;\n_ = "+FeatureValue("return")+";");
        if(multiOutput)foreach(var parameter in feature.Signature!.Args.Where(p=>p.IsOut))output.AppendLine(parameter.Name+" = default("+parameter.Type+")!;");
        foreach (string id in order)foreach(var result in FeatureOutputs(nodes[id].Signature))
            output.AppendLine(result.Type + " " + Value(id,result.Name) + ";");
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
            output.AppendLine("static " + node.Signature.Return + " " + Symbol(id) + "(" + string.Join(",", node.Signature.Args.Select(p => p.Declaration()).Concat(NodeImports(node).Select(f => Generation.Interface(f) + " " + ImportParameter(f)))) + ") {");
            if (!reachable.Contains(id)) output.AppendLine("#pragma warning restore CS8321");
            string marker = "node:" + feature.Id + "/" + id + "@" + manifestNodes.Single(n => n!["id"]!.ToString() == id)![node.Kind == "call" ? "definitionHash" : "implementationHash"]!.ToString();
            output.AppendLine("#line 1 " + JsonSerializer.Serialize(marker));
            if (node.Kind == "call")
                output.AppendLine((node.Signature.Return == "void" ? "" : "return ") + ImportParameter(node.Feature!) + ".Invoke(" + string.Join(",", node.Signature.Args.Select(p => (p.IsOut?"out ":"")+p.Name)) + ");");
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
            if(node.Kind=="export"){
                string exported=S(node.Definition,"output"),outputType=FeatureOutputs(feature.Signature!).Single(p=>p.Name==exported).Type;
                output.AppendLine(FeatureValue(exported)+" = "+Binding(node.Arguments["value"],outputType,available,id+"/value")+";");
                sourceMaps.Add(new JsonObject{["node"]=id,["definitionHash"]=node.DefinitionHash,["marker"]="graph:"+feature.Id+"@"+topologyHash});manifestNodes.Single(n=>n!["id"]!.ToString()==id)!["includedInSource"]=true;
            }
            else output.AppendLine((node.Signature.Return == "void" ? "" : Value(id) + " = ") + (HasContext(node) ? "this.Invoke" : Symbol(id)) + "(" + string.Join(",", node.Signature.Args.Select(p => p.IsOut?"out "+Value(id,p.Name):Binding(node.Arguments[p.Name], p.Type, available, id + "/" + p.Name)).Concat(HasContext(node) ? Array.Empty<string>() : NodeImports(node).Select(f => "calls." + Import(f).Alias))) + ");");
            if (node.Control == "branch")
                output.AppendLine("if (" + Value(id) + ") goto " + Label(edges[(id, "true")]) + "; else goto " + Label(edges[(id, "false")]) + ";");
            else
                output.AppendLine("goto " + Label(edges[(id, "next")]) + ";");
            output.AppendLine("}");
        }

        foreach (var exit in exits.OrderBy(e => e.Key, StringComparer.Ordinal))
        {
            string target = "exit:" + exit.Key;
            var incoming = edges.Where(e => e.Value == target && reachable.Contains(e.Key.Item1)).Select(e => e.Key.Item1).ToArray();
            if (incoming.Length == 0 && entry != target)
                continue;
            var available = incoming.Length == 0 ? new HashSet<string>(StringComparer.Ordinal) : new HashSet<string>(dominators[incoming[0]], StringComparer.Ordinal);
            foreach (string p in incoming.Skip(1))
                available.IntersectWith(dominators[p]);
            output.AppendLine(Label(target) + ": { return" + (feature.Signature!.Return == "void" ? "" : " " + (implicitEnd&&exit.Value is null?FeatureValue("return"):Binding(exit.Value, feature.Signature.Return, available, target))) + "; }");
        }

        if(implicitEnd)foreach(string target in edges.Values.Append(entry).Where(Terminal).Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal))output.AppendLine(Label(target)+": { return"+(feature.Signature!.Return=="void"?"":" "+FeatureValue("return"))+"; }");
        output.AppendLine("#line default");
        reply["state"] = "source-assembled";
        reply["body"] = output.ToString().Replace("\r\n", "\n");
        reply["members"] = membersOutput.ToString();
        reply["explicitEntry"] = multiOutput || nodes.Values.Any(HasContext);
        reply["entrySignature"] = contract.DeepClone();
        reply["bodyHash"] = Hash(reply["body"]!.ToString()+membersOutput);
        reply["sourceMap"] = sourceMaps;
        reply["graphMap"] = new JsonObject { ["marker"] = "graph:" + feature.Id + "@" + topologyHash, ["jsonPointer"] = "/edges", ["topologyHash"] = topologyHash };
        reply["nodeSources"] = new JsonArray(bodies.OrderBy(p => p.Key, StringComparer.Ordinal).Select(p => (JsonNode)new JsonObject { ["id"] = p.Key, ["source"] = p.Value, ["preserveImplementationContext"] = HasContext(nodes[p.Key]), ["marker"] = sourceMaps.Single(n => n!["node"]!.ToString() == p.Key)!["marker"]!.DeepClone() }).ToArray());
        reply["imports"] = new JsonArray(imports.OrderBy(i => i.Key, StringComparer.Ordinal).Select(i => (JsonNode)new JsonObject { ["feature"] = i.Key, ["alias"] = i.Value.Alias, ["contractHash"] = i.Value.Hash, ["binding"] = canonicalImports.Contains(i.Key) ? "canonical" : "implementation-context", ["signature"] = SignatureNode(i.Value.Element.Signature!) }).ToArray());
        return reply;
    }
}
