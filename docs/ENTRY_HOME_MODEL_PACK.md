# Entry/Home shared model extraction

The four domain operations now belong to library pack `Confectory.EditorHome.Model`: `CreateSession`, `Command`, `Snapshot`, `CloseSession`, with unchanged argument/return signatures. Their owned implementation IDs have the same suffix plus the new namespace. `CreateSessionBody` retains its Android body and its common desktop body. Existing session state/operation policy is unchanged.

`Confectory.EditorHome` remains the native engine ProjectPack namespace and entry ID. Its Main, Verify and VerifyShell import/provide the new public IDs. Android generated facade aliases (`CreateSession`, `Command`, `Snapshot`, `CloseSession`) remain unchanged because aliases belong to the consumer; the Android Activity does not need to own the domain. All three native Home manifests register the shared model pack. Android export settings remain ProjectPack-owned and are not part of this extraction.

Why the shared contract change was needed: a separate browser ProjectPack cannot register the existing native Home ProjectPack as a library. Core's existing ProjectPack boundary correctly disallows it. Creating a reusable role pack avoids copying/forking the model or introducing a special engine host in core. No core edits are needed. External consumers of old model element IDs must update imports to the model namespace; native Home Main ID stays stable.

Outside implementation reads/edits: moved exactly the four existing domain declarations/providers/common bodies and the Android CreateSession body from `examples/editor-home` into the new owner. Updated native function import/provide declarations and manifests to select these contracts. The former project-owned model implementations were removed, rather than duplicated. Session behavior source contents are preserved. Updated existing EntryHomeTests/ProjectShellTests consumer-locality fixture to copy the new model owner and append its locality probe in that copy. No Windows/Android host logic entered core. Native Main and Android Activity implementation bodies were not changed by this extraction.

Affected rebuild scope: new model contracts/provider assemblies and native/browser consumer bindings on first build, including Android generated facade references. Thereafter an edit to the owned model Command body must compile only `Confectory.EditorHome.Model::CommandBody`, with zero contracts. Native presentation providers remain independent. Existing native model, shell-domain and Android managed adapter gates are the functional consumer gates; locality assertions remain separate.

## Recorded verification

Commands used after extraction (with .NET SDK path selected and `/tmp` CLI home):

```sh
dotnet build tests/Confectory.Tests/Confectory.Tests.csproj -c Release
dotnet tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll test_fresh_entry_home_project_contracts_and_consumer_locality test_project_shell_domain_isolated_execution_no_null_chat_open_and_context_cleanup test_android_home_activity_dispatch_requires_adapter_and_preserves_public_domain
dotnet tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll test_project_shell_domain_isolated_execution_no_null_chat_open_and_context_cleanup
dotnet tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll BrowserTests test_project_shell_windows_and_android_managed_compile
```

The first grouped run recorded 2 passed, 1 failed: Android managed adapter and fresh Home/domain locality passed; shell functional execution completed but its post-run provider-locality assertion saw a full provider rebuild during concurrent build activity. The cause of that one invalidated baseline was not established. No locality assertion was relaxed. Tool path/identity equality assertions were added to the shell gate; the isolated rerun passed (1 passed, 0 failed; 85.877s), including exactly the Model CommandBody provider and zero contracts. Browser actual Chromium/locality and Windows+Android managed consumer compilation passed together (2 passed, 0 failed; 408.515s). Build warnings/errors were zero. Windows native execution, Android packaging/device behavior and actual Linux native GUI remain separate gates owned by root after integration.
