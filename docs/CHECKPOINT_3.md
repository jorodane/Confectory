# Checkpoint 3: runnable local draft authoring

The ordinary `examples/engine/project.cpack` now composes SchemaEditing, EditWorkspace, Save, ChangeSet, FileStream and ElementView with the existing RuntimeBase, RealTimeUpdate, BaseUI, render/input/window and project manager/execution packs. The core remains unchanged. Authoring is a caller-selected slice (`CONFECTORY_ELEMENT_UI=1`), preserving the original A/B execution slice when unset.

Both native windows open the configured authoring project explicitly. A is a reusable card; B is a small paginated table aggregate. They borrow the same participant/project/work-context draft while retaining independent selection, focus/press, resize and native View lifetimes. J cycles the table's selected row/element; element data is never table-owned. A different participant gets a separate draft and Save identity. Updates retain the existing View instances, native windows and render buffers. Worker results are projected at a coherent UI completion boundary.

SchemaEditing supports category, concept, function, module, object and schema creation; K cycles the creation kind. Scalar metadata editing preserves existing public signature, inheritance, module/default/provide/import/body rules. N stages a new element and its manifest registration. E changes the actual Main implementation body to a runnable demonstration. V validates/builds/runs the isolated draft candidate, with bounded execution and captured output, while the peer UI remains responsive. This is a small authoring slice, not a full text/IME editor, schema migration tool or complete editor.

D saves only versioned local diffs and original baselines. W saves, explicitly closes the workspace owner and reopens/restores it; final source is unchanged. Closing/reopening a native View with R preserves the live workspace. F confirms only the selected unit; G confirms all current diffs. New declarations require their project registration. Compilation, stale-draft and actual baseline conflicts preserve both final sources and live drafts. Unrelated files do not conflict with an independent body edit. Selected source writes and participating execution builds share FileStream's public lease; arbitrary external editors and crash-proof multi-file transactions are not guaranteed.

## Run and user checkpoint

Windows: with .NET 8 installed, pull main and double-click `run-authoring-windows.bat`. It calls the same corrected build/launch flow and selects the built authoring strategy. Native Windows usability is still pending corrected user acceptance; this Linux environment has not exercised that OS.

Linux, from the checkout:

```sh
export PATH="/workspace/toolchains/dotnet-8.0.425:$PATH"
export DOTNET_CLI_HOME=/tmp/confectory-dotnet
export CONFECTORY_DOTNET=/workspace/toolchains/dotnet-8.0.425/dotnet
dotnet build Confectory.sln -c Release
export CONFECTORY_PROJECT_ROOT="$PWD"
export CONFECTORY_PROJECT_EXECUTION_HOST="$PWD/targets/project-execution-host/bin/Release/net8.0/Confectory.ProjectExecutionHost.dll"
export CONFECTORY_ELEMENT_AUTHORING_HOST="$PWD/targets/element-authoring/bin/Release/net8.0/Confectory.ElementAuthoring.dll"
export CONFECTORY_ELEMENT_UI=1
dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll run examples/engine/project.cpack linux
```

Use a separate disposable copy of `examples/projects/authoring` for Confirm checks; resolve its DotNet registry path to the checkout's `targets/dotnet/pack.cpack`, then set CONFECTORY_PROJECT_A and CONFECTORY_PROJECT_B to that same explicit copied project path. The automated native probe creates/cleans such a private copy; it never modifies the tracked demonstration source.

In each window press O, then A. Click Count +1 in A and observe the same draft in B; their basic counters/pressed states remain independent. N creates a draft, E changes the functional body, V runs it, D then W proves Save/restore without final changes. F on the body publishes only it, leaving creation pending; G then publishes valid creation/registration. Change a selected final file externally and F reports conflict, retaining the draft. Close one native View and R in the other reopens it. User checks are asynchronous and do not pause development.

## Gates and limits

Functional and provider-locality evidence is recorded separately in CHECKPOINT_3_WORK_LOG.md. Full regressions: 91 passed, zero failed (749.059 seconds). Expanded final workspace/Android capability test: 1 passed (195.014 seconds). Final actual X11 authoring and both legacy interaction/project-lifetime probes passed; Linux and Windows profiles compile. Exact commands and rebuild scope are recorded in the ledger. Windows compilation is a framework-dependent profile, not Windows runtime acceptance. Android target selection/storage capability and native bridge preparation remain distinct from SDK packaging/app authoring.

Android Call selects an explicit unavailable authoring-tool strategy; it does not launch a desktop process. FileStream/Save storage must be app-private or granted by the host. The established Android Activity/surface/input/lifecycle entry remains the equivalent two-logical-View surface preparation, not two native windows. Native schema-authoring integration, APK compilation and device UX remain blocked/unverified: SDK/full JDK absent, Google license acceptance pending. No SDK license was accepted and no tooling bypass was attempted.
