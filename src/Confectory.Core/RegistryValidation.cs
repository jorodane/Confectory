namespace Confectory.Core;

// Shared declaration and structural graph validation, independent of target-tool execution.
public static class RegistryValidation
{
    public static void Validate(Registry registry, string target)
    {
        var planner = new Planner(registry, target);
        foreach (var (ns, manifest) in registry.Packs)
        foreach (string local in manifest.Elements.Keys)
        {
            string id = ns + "::" + local; var e = registry.Effective(id); planner.Structural(id);
            SchemaContracts.Validate(registry, id);
            if (e.Kind == "implementation") registry.Implementation(e.Function!, id, id, e.Loc);
            else if (e.Kind == "module") planner.Module(id);
            foreach (var reference in e.Uses.Concat(e.Contains)) registry.Get(reference.Id, reference.Kind, reference.Origin ?? id, reference.Loc);
            foreach (var (fn, provider) in e.Provides) registry.Implementation(fn, provider.Id, provider.Origin ?? id, provider.Loc);
        }
    }
}
