using Confectory.Core;

namespace Confectory.Tests;

public sealed class RuntimeBaseTests : TestCase
{
    public void test_lifecycle_and_provider_locality()
    {
        string sample = Path.Combine(f.Root, "runtime-sample");
        string pack = Path.Combine(f.Root, "packs", "runtime-base");
        Fixture.CopyTree(Path.Combine(Fixture.Repo, "examples", "runtime-base"), sample);
        Fixture.CopyTree(Path.Combine(Fixture.Repo, "packs", "runtime-base"), pack);
        string project = Path.Combine(sample, "project.cpack");
        File.WriteAllText(project, File.ReadAllText(project)
            .Replace("../../packs/runtime-base/pack.cpack", "../packs/runtime-base/pack.cpack", StringComparison.Ordinal)
            .Replace("../../targets/dotnet/pack.cpack", "../target/pack.cpack", StringComparison.Ordinal));
        var first = new Builder(project, "portable").Build();
        Output(first, "RuntimeBase lifecycle PASS");
        Sequence(["Confectory.RuntimeBase", "Example.RuntimeBase"], Strings(first, "includedPacks"));
        var cached = new Builder(project, "portable").Build();
        Equal(0, Strings(cached, "statistics", "compiledImplementations").Length);
        File.AppendAllText(Path.Combine(pack, "Write.csbody"), "\n// local provider edit\n");
        var changed = new Builder(project, "portable").Build();
        Sequence(["Confectory.RuntimeBase::WriteBody"], Strings(changed, "statistics", "compiledImplementations"));
        Equal(0, Strings(changed, "statistics", "compiledContracts").Length);
        Output(changed, "RuntimeBase lifecycle PASS");
    }
}
