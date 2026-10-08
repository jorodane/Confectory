using Confectory.Core;

namespace Confectory.Tests;

public sealed class RealTimeUpdateTests : TestCase
{
    public void test_lifecycle_and_provider_locality()
    {
        string sample = Path.Combine(f.Root, "realtime-sample");
        string pack = Path.Combine(f.Root, "packs", "realtime-update");
        Fixture.CopyTree(Path.Combine(Fixture.Repo, "examples", "realtime-update"), sample);
        Fixture.CopyTree(Path.Combine(Fixture.Repo, "packs", "realtime-update"), pack);
        string project = Path.Combine(sample, "project.cpack");
        File.WriteAllText(project, File.ReadAllText(project)
            .Replace("../../packs/realtime-update/pack.cpack", "../packs/realtime-update/pack.cpack", StringComparison.Ordinal)
            .Replace("../../targets/dotnet/pack.cpack", "../target/pack.cpack", StringComparison.Ordinal));
        var first = new Builder(project, "portable").Build();
        Output(first, "RealTimeUpdate cadence and camera PASS");
        Sequence(["Confectory.RealTimeUpdate", "Example.RealTimeUpdate"], Strings(first, "includedPacks"));
        var cached = new Builder(project, "portable").Build();
        Equal(0, Strings(cached, "statistics", "compiledImplementations").Length);
        File.AppendAllText(Path.Combine(pack, "Advance.csbody"), "\n// local provider edit\n");
        var changed = new Builder(project, "portable").Build();
        PackRebuilt(changed, ["Confectory.RealTimeUpdate::AdvanceBody"]);
        Equal(0, Strings(changed, "statistics", "compiledContracts").Length);
        Output(changed, "RealTimeUpdate cadence and camera PASS");
    }
}
