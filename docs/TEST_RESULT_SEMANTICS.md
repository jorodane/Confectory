# Test outcome semantics

Every selected test has one outcome: PASS after normal completion, FAIL after an assertion/exception, or SKIP after `TestCase.Skip(reason)` throws `SkippedException`. Missing DISPLAY/workload/platform support and formerly silent platform returns use SKIP. Mixed semantic/native tests that run only headless checks are SKIP for the whole test; those completed assertions do not prove native execution. No UI or platform implementation changes are involved.

The summary counts passed, failed and skipped independently. Exit0 requires at least one PASS and no FAIL. `--require-runtime` additionally requires zero SKIP. Flags are excluded from name filters; unknown flags exit2. Zero selected tests and selections with only skipped tests exit1. A regular mixed PASS/SKIP selection can exit0, so acceptance gates must use `--require-runtime` and inspect the summary. Existing fake-reply protocol-negative fixture returns its exact saved bytes before argument parsing, unchanged.

Commands run in the consumer-local worktree with SDK10.0.401, `DOTNET_CLI_HOME=/tmp/confectory-dotnet10`, `CONFECTORY_DOTNET=/workspace/toolchains/dotnet-10.0.401/dotnet`:

```
dotnet build tests/Confectory.Tests -c Release --nologo
env -u DISPLAY dotnet tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll EntryHomeTests.test_entry_home_actual_linux_startup_navigation_create_folder_cards_resize_and_lifetime ProjectShellTests.test_project_shell_actual_linux_menu_tabs_run_logs_resize_context_and_lifetime EditorTests.test_editor_native_designed_create_open_edit_save_review_confirm_run_stop_and_lifetime
dotnet tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll --require-runtime RunnerTests CoreTests
```

Build zero warnings/errors. Actual audit replay: three SKIP lines, **0 passed, 0 failed, 3 skipped**, exit1. Strict runner/Core regression: **42 passed, 0 failed, 0 skipped**, exit0, 1.081s. Runner regression launches those actual three GUI methods with DISPLAY removed, checks absence of PASS, normal mixed Core+SKIP success, strict mixed failure, no selected tests failure and unknown option rejection. No native runtime was exercised by this correction; native gates remain separate required checks.
