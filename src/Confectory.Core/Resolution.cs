namespace Confectory.Core;

public sealed class Registry
{
    public Documents Documents { get; }
    public BuildStatistics Statistics { get; }
    public string ProjectPath { get; }
    public Manifest Project { get; }
    public Dictionary<string, Manifest> Packs { get; } = new(StringComparer.Ordinal);
    public Dictionary<string, string> Paths { get; } = new(StringComparer.Ordinal);
    public Dictionary<string, Element> Elements { get; } = new(StringComparer.Ordinal);
    private readonly Dictionary<string, Element> effectiveCache = new(StringComparer.Ordinal);
    public List<Diagnostic> Warnings { get; } = [];

    public Registry(string projectPath, Documents documents, BuildStatistics statistics)
    {
        Documents = documents; Statistics = statistics; ProjectPath = PackPaths.Resolve(projectPath);
        Project = documents.Manifest(ProjectPath);
        if (Project.Kind != "project") throw new BuildError("PROJECT_INPUT", "Build input must be a ProjectPack", Project.Loc);
        Register(ProjectPath, Project, Project.Namespace);
        foreach (var (ns, locator) in Project.Registry)
        {
            if (Packs.ContainsKey(ns)) throw new BuildError("DUPLICATE_NAMESPACE", $"Namespace {ns} is registered more than once", locator.Loc);
            string path = PackPaths.Resolve(Path.Combine(Path.GetDirectoryName(ProjectPath)!, locator.Path));
            Register(path, documents.Manifest(path), ns);
        }
        foreach (var (ns, pack) in Packs)
        foreach (var (dep, expectation) in pack.Dependencies)
        {
            if (dep == ns) throw new BuildError("DEPENDENCY", "A pack must not depend on itself", expectation.Loc);
            if (!Packs.TryGetValue(dep, out var selected)) throw new BuildError("MISSING_NAMESPACE", $"Dependency {dep} is not registered", expectation.Loc);
            if (expectation.Version != "*" && expectation.Version != selected.Version)
                Warnings.Add(new("warning", "VERSION_MISMATCH", $"{ns} expects {dep} {expectation.Version}; selected {selected.Version}", expectation.Loc));
        }
    }
    private void Register(string path, Manifest manifest, string expected)
    {
        string ns = manifest.Namespace;
        if (Packs.ContainsKey(ns)) throw new BuildError("DUPLICATE_NAMESPACE", $"Duplicate namespace {ns}", manifest.Loc);
        if (ns != expected) throw new BuildError("REGISTRY_ID", $"Registry {expected} points to namespace {ns}", manifest.Loc);
        if (manifest.Kind == "project" && Packs.Count > 0) throw new BuildError("PROJECT_INPUT", "Nested ProjectPacks are not pack registry entries", manifest.Loc);
        Packs.Add(ns, manifest); Paths.Add(ns, path);
        foreach (var locator in manifest.Elements.Values) PackPaths.Owned(Path.GetDirectoryName(path)!, locator.Path, locator.Loc);
    }
    public Element Get(string id, string? expected = null, string? source = null, SourceLocation? loc = null)
    {
        string[] parts = id.Split("::", StringSplitOptions.None);
        if (parts.Length != 2) throw new BuildError("IDENTIFIER", "Expected a namespace-qualified element ID", loc);
        string ns = parts[0], local = parts[1];
        if (source is not null)
        {
            string owner = PackPaths.Namespace(source);
            if (ns != owner && !Packs[owner].Dependencies.ContainsKey(ns)) throw new BuildError("UNDECLARED_DEPENDENCY", $"{source} refers to {ns} without a direct dependency", loc);
        }
        if (!Packs.TryGetValue(ns, out var pack)) throw new BuildError("MISSING_NAMESPACE", $"Namespace {ns} is not registered", loc);
        if (!pack.Elements.TryGetValue(local, out var locator)) throw new BuildError("MISSING_ELEMENT", $"No declaration for {id}", loc);
        if (expected is not null && locator.Kind != expected) throw new BuildError("ELEMENT_KIND", $"{id} is {locator.Kind}, expected {expected}", loc ?? locator.Loc);
        if (!Elements.TryGetValue(id, out var element))
        {
            string path = PackPaths.Owned(Path.GetDirectoryName(Paths[ns])!, locator.Path, locator.Loc);
            element = Documents.Element(path);
            if (element.Id != id || element.Kind != locator.Kind) throw new BuildError("LOCATOR_MISMATCH", $"Locator {id} {locator.Kind} points to {element.Id} {element.Kind}", element.Loc);
            Elements.Add(id, element);
        }
        return element;
    }
    private static Dictionary<string, T> Merge<T>(Dictionary<string, T> parent, Dictionary<string, T> child)
    {
        var result = new Dictionary<string, T>(parent, StringComparer.Ordinal);
        foreach (var (key, value) in child) result[key] = value;
        return result;
    }
    public Element Effective(string id, IReadOnlyList<string>? stack = null)
    {
        stack ??= [];
        if (stack.Contains(id)) throw new BuildError("INHERITANCE_CYCLE", "Inheritance cycle: " + string.Join(" -> ", stack.Append(id)), Get(id).Loc);
        if (effectiveCache.TryGetValue(id, out var cached)) return cached;
        var e = JsonData.Clone(Get(id));
        if (e.Parent is not null)
        {
            var parent = Get(e.Parent, e.Kind, id, e.Loc);
            var p = Effective(parent.Id, [..stack, id]);
            if (e.Signature is not null && !e.Signature.Matches(p.Signature)) throw new BuildError("CONTRACT_MISMATCH", "Inherited function/implementation signature changed", e.Loc);
            if (e.Kind == "implementation" && e.Function != p.Function) throw new BuildError("IMPLEMENTATION_ID", "Implementation inheritance cannot change function identity", e.Loc);
            e.Values = Merge(p.Values, e.Values); e.Provides = Merge(p.Provides, e.Provides); e.Requires = Merge(p.Requires, e.Requires);
            e.Defaults = Merge(p.Defaults, e.Defaults); e.Imports = Merge(p.Imports, e.Imports); e.Bodies = Merge(p.Bodies, e.Bodies); e.Options = Merge(p.Options, e.Options);
            e.Modules = [..p.Modules, ..e.Modules]; e.Includes = [..p.Includes, ..e.Includes]; e.Uses = [..p.Uses, ..e.Uses]; e.Contains = [..p.Contains, ..e.Contains];
            if (!e.DescriptionPresent) e.Description = p.Description;
            if (e.Tool is null && p.Tool is not null) { e.Tool = p.Tool; e.ToolOrigin = p.ToolOrigin ?? p.Id; }
        }
        effectiveCache[id] = e;
        return e;
    }
    public Element Signature(string id, FunctionSignature expected, string source, SourceLocation loc)
    {
        var fn = Get(id, "function", source, loc);
        if (!expected.Matches(fn.Signature)) throw new BuildError("CONTRACT_MISMATCH", $"Incompatible signature for {id}", loc);
        if (!Statistics.CheckedContracts.Contains(id)) Statistics.CheckedContracts.Add(id);
        return fn;
    }
    public Element Implementation(string function, string implementation, string source, SourceLocation loc)
    {
        Get(function, "function", source, loc);
        var i = Effective(Get(implementation, "implementation", source, loc).Id);
        if (i.Function != function) throw new BuildError("IMPLEMENTATION_ID", $"{implementation} implements {i.Function}, not {function}", loc);
        Signature(function, i.Signature!, i.Id, i.Loc);
        foreach (var imported in i.Imports.Values)
        {
            Signature(imported.Id, imported.Signature, imported.Origin, imported.Loc);
            if (imported.Scope is not null)
            {
                var scope = Get(imported.Scope, source: imported.Origin, loc: imported.Loc);
                if (scope.Kind is "implementation" or "module" or "buildtarget") throw new BuildError("SCOPE_KIND", "Function import scope must be a consumer element", imported.Loc);
            }
        }
        return i;
    }
}

public sealed record BindingKey(string Owner, string Function);
public sealed class Binding(string owner, string function, string implementation)
{
    public string Owner { get; } = owner;
    public string Function { get; } = function;
    public string Implementation { get; } = implementation;
    public Dictionary<string, string[]> Imports { get; } = new(StringComparer.Ordinal);
}
public sealed record ModuleContract(Dictionary<string, RequiredFunction> Required, Dictionary<string, Dictionary<string, ElementReference>> Defaults);

public sealed class Planner(Registry registry, string target)
{
    public Registry Registry { get; } = registry;
    public string Target { get; } = target;
    public HashSet<string> Reached { get; } = new(StringComparer.Ordinal);
    public Dictionary<BindingKey, Binding> Bindings { get; } = [];
    public Dictionary<string, Element> Implementations { get; } = new(StringComparer.Ordinal);
    private readonly Dictionary<string, ModuleContract> moduleCache = new(StringComparer.Ordinal);
    private readonly HashSet<string> structuralDone = new(StringComparer.Ordinal);
    private readonly HashSet<(string Id, bool Active, string? Consumer)> visited = [];

    public void Structural(string id, IReadOnlyList<string>? stack = null)
    {
        stack ??= [];
        if (stack.Contains(id)) throw new BuildError("STRUCTURAL_CYCLE", "Structural cycle: " + string.Join(" -> ", stack.Append(id)), Registry.Get(id).Loc);
        if (structuralDone.Contains(id)) return;
        var e = Registry.Get(id);
        List<ElementReference> edges = [..e.Contains, ..e.Includes.Select(x => x with { Kind = "module" }), ..e.Modules.Select(x => x with { Kind = "module" })];
        if (e.Parent is not null) edges.Insert(0, new(e.Parent, e.Loc, id, e.Kind));
        foreach (var edge in edges) { Registry.Get(edge.Id, edge.Kind, id, edge.Loc); Structural(edge.Id, [..stack, id]); }
        structuralDone.Add(id);
    }
    private static void CombineDefaults(Dictionary<string, Dictionary<string, ElementReference>> destination, Dictionary<string, Dictionary<string, ElementReference>> source)
    {
        foreach (var (fn, choices) in source)
        {
            if (!destination.TryGetValue(fn, out var values)) destination[fn] = values = new(StringComparer.Ordinal);
            foreach (var (id, provider) in choices) values[id] = provider;
        }
    }
    public ModuleContract Module(string id, IReadOnlyList<string>? stack = null)
    {
        stack ??= [];
        if (stack.Contains(id)) throw new BuildError("MODULE_CYCLE", "Module inclusion cycle: " + string.Join(" -> ", stack.Append(id)), Registry.Get(id).Loc);
        if (moduleCache.TryGetValue(id, out var cached)) return cached;
        var e = Registry.Effective(Registry.Get(id, "module").Id); Structural(id);
        var result = new ModuleContract(new(StringComparer.Ordinal), new(StringComparer.Ordinal));
        foreach (var child in e.Includes)
        {
            Registry.Get(child.Id, "module", child.Origin ?? id, child.Loc);
            var contract = Module(child.Id, [..stack, id]);
            foreach (var (fn, req) in contract.Required) result.Required[fn] = req;
            CombineDefaults(result.Defaults, contract.Defaults);
        }
        foreach (var (fn, contract) in e.Requires)
        {
            Registry.Signature(fn, contract.Signature, contract.Origin, contract.Loc); result.Required[fn] = contract;
        }
        foreach (var (fn, provider) in e.Defaults)
        {
            if (!result.Required.ContainsKey(fn)) throw new BuildError("MODULE_CONTRACT", $"Default {fn} is not required by module {id}", provider.Loc);
            Registry.Implementation(fn, provider.Id, provider.Origin ?? id, provider.Loc);
            if (!result.Defaults.TryGetValue(fn, out var choices)) result.Defaults[fn] = choices = new(StringComparer.Ordinal);
            choices[provider.Id] = provider;
        }
        moduleCache[id] = result; return result;
    }
    public ModuleContract ModulesFor(string owner)
    {
        var result = new ModuleContract(new(StringComparer.Ordinal), new(StringComparer.Ordinal));
        foreach (var reference in Registry.Effective(owner).Modules)
        {
            Registry.Get(reference.Id, "module", reference.Origin ?? owner, reference.Loc);
            var contract = Module(reference.Id);
            foreach (var (fn, req) in contract.Required) result.Required[fn] = req;
            CombineDefaults(result.Defaults, contract.Defaults);
        }
        return result;
    }
    public void Visit(string id, string? expected = null, string? source = null, SourceLocation? loc = null, bool active = true, string? consumer = null)
    {
        var e = Registry.Get(id, expected, source, loc);
        if (!visited.Add((id, active, e.Kind is "implementation" or "module" ? consumer : null))) return;
        Reached.Add(id); Structural(id); var effective = Registry.Effective(id);
        string? scope = e.Kind is "implementation" or "module" or "buildtarget" ? consumer : id;
        if (active && e.Kind == "implementation")
        {
            effective = Registry.Implementation(effective.Function!, id, id, effective.Loc);
            if (!effective.Bodies.ContainsKey(Target) && !effective.Bodies.ContainsKey("common"))
                throw new BuildError("MISSING_TARGET_IMPLEMENTATION", $"{id} has neither {Target} nor common body", effective.Loc);
            Implementations[id] = effective;
            Visit(effective.Function!, "function", id, effective.Loc, false);
            foreach (var imported in effective.Imports.Values)
            {
                string importScope = imported.Scope ?? scope ?? throw new BuildError("IMPLEMENTATION_SCOPE",
                    $"Directly included implementation {id} has no consumer scope for {imported.Id}; declare 'in Namespace::Consumer' on the import", imported.Loc);
                Visit(imported.Id, "function", imported.Origin, imported.Loc, false);
                if (imported.Scope is not null) Visit(importScope, source: imported.Origin, loc: imported.Loc);
                Bind(importScope, imported.Id);
            }
        }
        if (e.Parent is not null) Visit(e.Parent, e.Kind, id, e.Loc, false);
        foreach (var reference in effective.Uses.Concat(effective.Contains))
        {
            // Direct implementation edges select executable code even when the
            // containing declaration was reached as module/contract metadata.
            Visit(reference.Id, reference.Kind, reference.Origin ?? id, reference.Loc,
                reference.Kind == "implementation" || (active && reference.Kind != "function"), scope);
            if (active && reference.Kind == "function")
                Bind(scope ?? throw new BuildError("IMPLEMENTATION_SCOPE", $"No consumer scope for function use in {id}", reference.Loc), reference.Id);
        }
        foreach (var reference in effective.Modules.Concat(effective.Includes)) Visit(reference.Id, "module", reference.Origin ?? id, reference.Loc, false, scope);
        foreach (var (fn, provider) in effective.Provides) Registry.Implementation(fn, provider.Id, provider.Origin ?? id, provider.Loc);
        if (e.Kind == "module") Module(id);
        else if (active && e.Kind is not ("implementation" or "buildtarget")) foreach (string fn in ModulesFor(id).Required.Keys) Bind(id, fn);
    }
    public void Bind(string owner, string function)
    {
        var key = new BindingKey(owner, function);
        if (Bindings.ContainsKey(key)) return;
        var ownerElement = Registry.Effective(owner); var fn = Registry.Get(function, "function"); var functionElement = Registry.Effective(function);
        ElementReference provider; string source;
        if (ownerElement.Provides.TryGetValue(function, out var declared) || functionElement.Provides.TryGetValue(function, out declared))
        {
            provider = declared; source = declared.Origin ?? (ownerElement.Provides.ContainsKey(function) ? owner : function);
        }
        else
        {
            var choices = new Dictionary<string, ElementReference>(StringComparer.Ordinal);
            if (ModulesFor(owner).Defaults.TryGetValue(function, out var defaults)) foreach (var item in defaults) choices[item.Key] = item.Value;
            if (owner != function && ModulesFor(function).Defaults.TryGetValue(function, out defaults)) foreach (var item in defaults) choices[item.Key] = item.Value;
            if (choices.Count == 0) throw new BuildError("MISSING_IMPLEMENTATION", $"No implementation for {function} in scope {owner}", fn.Loc);
            if (choices.Count > 1) throw new BuildError("DEFAULT_CONFLICT", $"Conflicting defaults for {function} in {owner}: {string.Join(", ", choices.Keys.Order(StringComparer.Ordinal))}", ownerElement.Loc);
            provider = choices.Values.Single(); source = provider.Id;
        }
        var impl = Registry.Implementation(function, provider.Id, source, provider.Loc);
        if (!impl.Bodies.ContainsKey(Target) && !impl.Bodies.ContainsKey("common")) throw new BuildError("MISSING_TARGET_IMPLEMENTATION", $"{impl.Id} has neither {Target} nor common body", impl.Loc);
        var node = new Binding(owner, function, impl.Id);
        Bindings[key] = node;
        Visit(owner); Visit(function, "function", active: false); Visit(impl.Id, "implementation", consumer: owner);
        foreach (var (alias, imported) in impl.Imports)
        {
            string scope = imported.Scope ?? owner;
            Visit(imported.Id, "function", imported.Origin, imported.Loc, false);
            if (imported.Scope is not null) Visit(scope, source: imported.Origin, loc: imported.Loc);
            Bind(scope, imported.Id); node.Imports[alias] = [scope, imported.Id];
        }
    }
    public Planner Plan()
    {
        var p = Registry.Project;
        if (p.Entry is null) throw new BuildError("MISSING_ENTRY", "ProjectPack must declare an entry function", p.Loc);
        var entry = Registry.Get(p.Entry, "function", p.Namespace + "::<project>", p.Loc);
        if (entry.Signature!.Args.Count != 0 || entry.Signature.Return is not ("int" or "void")) throw new BuildError("ENTRY_CONTRACT", "Entry contract must be () -> int or () -> void", entry.Loc);
        Bind(p.Entry, p.Entry);
        foreach (var reference in p.Always)
        {
            Visit(reference.Id, source: p.Namespace + "::<project>", loc: reference.Loc);
            if (Registry.Get(reference.Id).Kind == "function") Bind(reference.Id, reference.Id);
        }
        return this;
    }
}
