using Confectory.Core;
using System.Globalization;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

namespace Confectory.Core;
// Pure compiler input processing: no source-file writes, activation, AI request or runtime invocation.
public static class FeatureBlueprint
{
    public const string Profile = "sync-acyclic-v1", Generator = "feature-blueprint-source-v1";
    public static string ContractHash(Element feature) => Hash(CanonicalText(new JsonObject { ["feature"] = feature.Id, ["signature"] = SignatureNode(feature.Signature!) }));
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
    static JsonObject SignatureNode(FunctionSignature signature) => new()
    {
        ["args"] = new JsonArray(signature.Args.Select(p => (JsonNode)new JsonObject { ["type"] = p.Type, ["name"] = p.Name }).ToArray()),
        ["return"] = signature.Return
    };
    static string SignatureText(FunctionSignature signature, bool names) => "(" + string.Join(", ", signature.Args.Select(p => p.Type + (names ? " " + p.Name : ""))) + ") -> " + signature.Return;
    static FunctionSignature Signature(JsonNode value)
    {
        var args = value["args"]!.AsArray();
        var signature = new FunctionSignature(args.Select(p => new Parameter(S(p, "type"), S(p, "name"))).ToList(), S(value, "return"));
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
        Need(operation is "featureBlueprintDescribe" or "featureBlueprintAssemble" or "featureBlueprintNodes", "GRAPH_OPERATION", operation);
        var feature = new Parser(S(request, "featureSource"), "<feature-contract>").ParseElement();
        Need(feature.Kind == "function" && feature.Signature is not null, "GRAPH_FEATURE_CONTRACT", feature.Id);
        var contract = SignatureNode(feature.Signature!);
        string contractHash = Hash(CanonicalText(new JsonObject { ["feature"] = feature.Id, ["signature"] = contract.DeepClone() }));
        var graph = request["graph"]!.AsObject();
        Need(graph["schema"]?.GetValue<int>() == 1, "GRAPH_SCHEMA", "schema");
        Need(S(graph, "profile") == Profile, "GRAPH_PROFILE_UNSUPPORTED", S(graph, "profile"));
        Need(S(graph, "feature") == feature.Id, "GRAPH_FEATURE_MISMATCH", "feature");
        Need(S(graph, "contractHash") == contractHash, "GRAPH_CONTRACT_STALE", feature.Id);
        var imports = new Dictionary<string, (Element Element, string Alias, string Hash)>(StringComparer.Ordinal);
        (Element Element, string Alias, string Hash) Import(string id)
        {
            if (imports.TryGetValue(id, out var known))
                return known;
            string source = id == feature.Id ? S(request, "featureSource") : request["featureContracts"]?[id]?.GetValue<string>() ?? throw new Refusal("GRAPH_CALLEE_MISSING", id);
            var element = new Parser(source, "<called-feature>").ParseElement();
            Need(element.Id == id && element.Kind == "function" && element.Signature is not null, "GRAPH_CALLEE_CONTRACT", id);
            string hash = Hash(CanonicalText(new JsonObject { ["feature"] = id, ["signature"] = SignatureNode(element.Signature!) }));
            var result = (element, "fg_call_" + Hash(id)[..24], hash);
            imports.Add(id, result);
            return result;
        }

        var nodes = new Dictionary<string, Node>(StringComparer.Ordinal);
        foreach (var item in graph["nodes"]!.AsArray())
        {
            var value = item!.AsObject();
            string id = Id(value, "id"), kind = S(value, "kind"), control = S(value, "control"), intent = S(value, "intent");
            Need(!nodes.ContainsKey(id), "GRAPH_DUPLICATE_NODE", id);
            Need(kind is "code" or "call", "GRAPH_NODE_KIND", id);
            Need(control is "next" or "branch", "GRAPH_CONTROL", id);
            Need(!string.IsNullOrWhiteSpace(intent), "NODE_INTENT", id);
            var signature = Signature(value["signature"]!);
            Need(!signature.Args.Any(p => (p.Name.StartsWith("__fg_", StringComparison.Ordinal) || p.Name.StartsWith("fg_call_", StringComparison.Ordinal))), "NODE_RESERVED_NAME", id);
            Need(control != "branch" || signature.Return == "bool", "GRAPH_BRANCH_TYPE", id);
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
            nodes.Add(id, new(id, kind, control, signature, definition, value["arguments"]?.AsObject() ?? new JsonObject(), Hash(CanonicalText(definition)), called));
        }

        if (operation == "featureBlueprintNodes")
        {
            var versions = new JsonObject(imports.OrderBy(p => p.Key, StringComparer.Ordinal).Select(p => new KeyValuePair<string, JsonNode?>(p.Key, JsonValue.Create(p.Value.Hash))));
            versions[feature.Id] = contractHash;
            return new JsonObject
            {
                ["state"] = "node-definitions", ["feature"] = feature.Id, ["profile"] = Profile, ["contractHash"] = contractHash, ["signature"] = contract.DeepClone(),
                ["nodes"] = new JsonArray(nodes.OrderBy(p => p.Key, StringComparer.Ordinal).Select(p => (JsonNode)new JsonObject { ["id"] = p.Key, ["definitionHash"] = p.Value.DefinitionHash, ["definition"] = p.Value.Definition.DeepClone() }).ToArray()),
                ["contractVersions"] = versions,
                ["imports"] = new JsonArray(imports.OrderBy(i => i.Key, StringComparer.Ordinal).Select(i => (JsonNode)new JsonObject { ["feature"] = i.Key, ["alias"] = i.Value.Alias, ["contractHash"] = i.Value.Hash, ["signature"] = SignatureNode(i.Value.Element.Signature!) }).ToArray()),
                ["sourceWritten"] = false, ["compiled"] = false, ["executed"] = false
            };
        }

        string entry = S(graph, "entry");
        var exits = graph["exits"]!.AsObject();
        var edges = new Dictionary<(string, string), string>();
        bool Exit(string target) => target.StartsWith("exit:", StringComparison.Ordinal) && exits.ContainsKey(target[5..]);
        void Target(string target) => Need(nodes.ContainsKey(target) || Exit(target), "GRAPH_TARGET", target);
        Target(entry);
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
            if (Exit(id) || reachable.Contains(id))
                return;
            Need(stack.Add(id), "GRAPH_CYCLE_PROFILE_UNSUPPORTED", id);
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
        foreach (string id in order)
        {
            var node = nodes[id];
            JsonNode? record = request["implementations"]?[id];
            string? body = node.Kind == "call" ? null : record?["source"]?.GetValue<string>();
            string? codeHash = body is null ? null : Hash(body.Replace("\r\n", "\n"));
            string status = node.Kind == "call" ? "feature-reference" : body is null ? "missing" : record?["definitionHash"]?.ToString() != node.DefinitionHash ? "stale" : "available";
            manifestNodes.Add(new JsonObject { ["id"] = id, ["definitionHash"] = node.DefinitionHash, ["definition"] = node.Definition.DeepClone(), ["implementationHash"] = codeHash, ["status"] = status });
            if (status is "missing" or "stale")
                missing.Add(id);
            else if (body is not null)
            {
                bodies[id] = body.Replace("\r\n", "\n");
            }
        }

        var sortedEdges = new JsonArray(edges.OrderBy(e => e.Key.Item1, StringComparer.Ordinal).ThenBy(e => e.Key.Item2, StringComparer.Ordinal).Select(e => (JsonNode)new JsonObject { ["from"] = e.Key.Item1, ["port"] = e.Key.Item2, ["to"] = e.Value }).ToArray());
        string topologyHash = Hash(CanonicalText(new JsonObject { ["entry"] = entry, ["edges"] = sortedEdges, ["exits"] = exits.DeepClone(), ["arguments"] = new JsonObject(nodes.OrderBy(n => n.Key, StringComparer.Ordinal).Select(n => new KeyValuePair<string, JsonNode?>(n.Key, n.Value.Arguments.DeepClone()))) }));
        var reply = new JsonObject
        {
            ["state"] = missing.Count > 0 ? "needs-implementation" : "source-ready",
            ["feature"] = feature.Id,
            ["signature"] = contract.DeepClone(),
            ["profile"] = Profile,
            ["generator"] = Generator,
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
        string Symbol(string id) => "__fg_" + Hash(id)[..32];
        string Value(string id) => Symbol(id) + "_value";
        string Label(string target) => Exit(target) ? "__fg_exit_" + Hash(target)[..32] : Symbol(target) + "_run";
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
            Need(binding.Count == 1, "GRAPH_VALUE", subject);
            if (binding.ContainsKey("input"))
            {
                string name = S(binding, "input");
                var parameter = feature.Signature!.Args.SingleOrDefault(p => p.Name == name);
                Need(parameter is not null && parameter.Type == type, "GRAPH_INPUT_TYPE", subject);
                return name;
            }

            if (binding.ContainsKey("node"))
            {
                string source = S(binding, "node");
                Need(available.Contains(source) && nodes[source].Signature.Return == type, "GRAPH_VALUE_UNAVAILABLE", subject);
                return Value(source);
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
            Need(node.Arguments.Count == node.Signature.Args.Count && node.Signature.Args.All(p => node.Arguments.ContainsKey(p.Name)), "GRAPH_ARGUMENTS", id);
            foreach (var p in node.Signature.Args)
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
            if (feature.Signature!.Return != "void")
                Binding(exit.Value, feature.Signature.Return, available, target);
        }

        reply["contractVersions"] = new JsonObject(imports.OrderBy(p => p.Key, StringComparer.Ordinal).Select(p => new KeyValuePair<string, JsonNode?>(p.Key, JsonValue.Create(p.Value.Hash))));
        reply["contractVersions"]![feature.Id] = contractHash;
        reply["imports"] = new JsonArray(imports.OrderBy(i => i.Key, StringComparer.Ordinal).Select(i => (JsonNode)new JsonObject { ["feature"] = i.Key, ["alias"] = i.Value.Alias, ["contractHash"] = i.Value.Hash, ["signature"] = SignatureNode(i.Value.Element.Signature!) }).ToArray());
        if (operation == "featureBlueprintDescribe" || missing.Count > 0)
            return reply;
        var output = new StringBuilder();
        foreach (string id in order.Where(id => nodes[id].Signature.Return != "void"))
            output.AppendLine(nodes[id].Signature.Return + " " + Value(id) + ";");
        foreach (string id in order)
        {
            var node = nodes[id];
            output.AppendLine("static " + node.Signature.Return + " " + Symbol(id) + "(" + string.Join(",", node.Signature.Args.Select(p => p.Type + " " + p.Name).Concat(NodeImports(node).Select(f => Generation.Interface(f) + " " + ImportParameter(f)))) + ") {");
            string marker = "node:" + feature.Id + "/" + id + "@" + manifestNodes.Single(n => n!["id"]!.ToString() == id)![node.Kind == "call" ? "definitionHash" : "implementationHash"]!.ToString();
            output.AppendLine("#line 1 " + JsonSerializer.Serialize(marker));
            if (node.Kind == "call")
                output.AppendLine((node.Signature.Return == "void" ? "" : "return ") + ImportParameter(node.Feature!) + ".Invoke(" + string.Join(",", node.Signature.Args.Select(p => p.Name)) + ");");
            else
                output.AppendLine(bodies[id]);
            output.AppendLine("#line default\n}");
            sourceMaps.Add(new JsonObject { ["node"] = id, ["definitionHash"] = node.DefinitionHash, ["marker"] = marker });
        }

        output.AppendLine("#line 1 " + JsonSerializer.Serialize("graph:" + feature.Id + "@" + topologyHash));
        output.AppendLine("goto " + Label(entry) + ";");
        foreach (string id in order)
        {
            var node = nodes[id];
            var available = new HashSet<string>(dominators[id], StringComparer.Ordinal);
            available.Remove(id);
            Need(node.Arguments.Count == node.Signature.Args.Count && node.Signature.Args.All(p => node.Arguments.ContainsKey(p.Name)), "GRAPH_ARGUMENTS", id);
            output.AppendLine(Label(id) + ": {");
            output.AppendLine((node.Signature.Return == "void" ? "" : Value(id) + " = ") + Symbol(id) + "(" + string.Join(",", node.Signature.Args.Select(p => Binding(node.Arguments[p.Name], p.Type, available, id + "/" + p.Name)).Concat(NodeImports(node).Select(f => "calls." + Import(f).Alias))) + ");");
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
            output.AppendLine(Label(target) + ": { return" + (feature.Signature!.Return == "void" ? "" : " " + Binding(exit.Value, feature.Signature.Return, available, target)) + "; }");
        }

        output.AppendLine("#line default");
        reply["state"] = "source-assembled";
        reply["body"] = output.ToString().Replace("\r\n", "\n");
        reply["bodyHash"] = Hash(reply["body"]!.ToString());
        reply["sourceMap"] = sourceMaps;
        reply["graphMap"] = new JsonObject { ["marker"] = "graph:" + feature.Id + "@" + topologyHash, ["jsonPointer"] = "/edges", ["topologyHash"] = topologyHash };
        reply["nodeSources"] = new JsonArray(bodies.OrderBy(p => p.Key, StringComparer.Ordinal).Select(p => (JsonNode)new JsonObject { ["id"] = p.Key, ["source"] = p.Value, ["marker"] = sourceMaps.Single(n => n!["node"]!.ToString() == p.Key)!["marker"]!.DeepClone() }).ToArray());
        reply["imports"] = new JsonArray(imports.OrderBy(i => i.Key, StringComparer.Ordinal).Select(i => (JsonNode)new JsonObject { ["feature"] = i.Key, ["alias"] = i.Value.Alias, ["contractHash"] = i.Value.Hash, ["signature"] = SignatureNode(i.Value.Element.Signature!) }).ToArray());
        return reply;
    }
}
