using Confectory.Core;
namespace Confectory.Tests;

public sealed class EditorLifetimeTests : TestCase
{
    // Auxiliary fault/provider checks use exact repository bodies. Actual product UI
    // acceptance is separately required; this harness does not substitute a target shell.
    public void test_editor_product_owned_startup_and_close_fault_retry()
    {
        var result=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests","probes","editor_lifetime_retry.py"),Path.Combine(f.Root,"lifetime-probe")},timeoutSeconds:120);
        True(result.ExitCode==0,result.Stdout+result.Stderr);
        True(result.Stdout.Contains("R1 retry: disposeAttempts=2; managerState=disposed; registryRetained=False",StringComparison.Ordinal));
        True(result.Stdout.Contains("Editor lifetime exact-body fault/retry gate PASS; not platform UI acceptance",StringComparison.Ordinal));
    }
}
