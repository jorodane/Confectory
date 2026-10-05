using Confectory.Core;

namespace Confectory.Tests;

public sealed class BaseUITests : TestCase
{
    public void test_lifecycle_and_provider_locality()
    {
        string sample = Path.Combine(f.Root, "baseui-sample");
        string pack = Path.Combine(f.Root, "packs", "base-ui");
        Fixture.CopyTree(Path.Combine(Fixture.Repo, "examples", "base-ui"), sample);
        Fixture.CopyTree(Path.Combine(Fixture.Repo, "packs", "base-ui"), pack);
        Fixture.CopyTree(Path.Combine(Fixture.Repo, "packs", "runtime-base"), Path.Combine(f.Root, "packs", "runtime-base"));
        string project = Path.Combine(sample, "project.cpack");
        File.WriteAllText(project, File.ReadAllText(project)
            .Replace("../../packs/runtime-base/pack.cpack", "../packs/runtime-base/pack.cpack", StringComparison.Ordinal)
            .Replace("../../packs/base-ui/pack.cpack", "../packs/base-ui/pack.cpack", StringComparison.Ordinal)
            .Replace("../../targets/dotnet/pack.cpack", "../target/pack.cpack", StringComparison.Ordinal));
        var first = new Builder(project, "portable").Build();
        Output(first, "BaseUI controls and lifetime PASS");
        Sequence(["Confectory.BaseUI", "Confectory.RuntimeBase", "Example.BaseUI"], Strings(first, "includedPacks"));
        var cached = new Builder(project, "portable").Build();
        Equal(0, Strings(cached, "statistics", "compiledImplementations").Length);
        File.AppendAllText(Path.Combine(pack, "UpdateView.csbody"), "\n// local provider edit\n");
        var changed = new Builder(project, "portable").Build();
        Sequence(["Confectory.BaseUI::UpdateViewBody"], Strings(changed, "statistics", "compiledImplementations"));
        Equal(0, Strings(changed, "statistics", "compiledContracts").Length);
        Output(changed, "BaseUI controls and lifetime PASS");
    }
}
