# Checkpoint 11 SDK/Roslyn compatibility fix

Status: the user explicitly chose to keep .NET8 after reviewing the historical rationale and alternatives. The scoped fix restores repository-local SDK8 selection, validates SDK/Roslyn compatibility and adds meaningful clean/incremental regression. It changes no machine-global SDK setting, framework or pack API and adopts no new package.

Base checkpoint remains immutable: a0f77a4d08dd6ddaa087de77697269a7b7cb7371 on integration/checkpoint-11. The scoped follow-up is fix/checkpoint-11-sdk8. Prior checkpoint markers, explicit core/window/Stage/Physics increments and all preserved prior local branch tips are ancestors of CP11. Main and CP11 are not rewritten or merged. CP12 work remains preserved separately and is not included in this fix.

The official Library Windows log libfile_244d65ea12fc8191a6ffb3ec036a316b was read at lines1..180 and540..589. It shows SDK10.0.401 building net8.0 projects, 27 MSB3277 warnings and two CS1705 errors in ElementAuthoring: SDK10 Roslyn Microsoft.CodeAnalysis/CSharp5.9 depends on System.Runtime10 while net8.0 references Runtime8. Core.dll appears in the conflict reference chain; that is not evidence that Core itself directly references Roslyn. The source has direct SDK-derived Roslyn HintPaths only in ElementAuthoring. This failure is distinct from compiler long-command handling.

Root cause: without repository SDK selection, solution builds use the selected/latest SDK; direct Roslyn library references consequently track that SDK, even though the authoring executable targets net8.0. The generated ProjectPack compiler already selects only installed8.* SDK directories and net8 reference/runtime packs; it is not changed here.

Fix: root global.json requests SDK8.0.100 with latestFeature and allowPrerelease=false. It accepts later installed stable8.0 feature/patch releases, including tested8.0.425, but does not roll to9/10. ElementAuthoring validates before ResolveAssemblyReferences/ResolveReferences: selected NETCoreSdkVersion must be8.0, both Roslyn DLLs must exist, and assembly identities must have SDK8 Roslyn major4. Bypassed/overridden selection or a wrong-major library produces a useful diagnostic before CS1705. ConfectoryRoslynDirectory defaults to the selected SDK folder; its explicit override allows diagnostic fixture validation, not automatic installation. Product frameworks stay net8.0; no new NuGet dependencies, tools, downloads, installs or license acceptance. SDK10 can stay installed beside SDK8.

Prerequisite/workaround: from the updated repository run dotnet --list-sdks and dotnet --version. There must be an installed8.0 SDK; the selected version should read8.0.*. A Runtime8 or Microsoft.NETCore.App.Ref8 pack alone is insufficient. Both Windows scripts already enter the repository before building, so they honor global.json. If only SDK10 is installed, an approved/pre-existing SDK8 installation is required; scripts do not silently install it. For the unchanged CP11 checkout, the same repository-local global.json is a verified SDK8 selection workaround when a stable8.0 SDK is already installed. Do not delete other SDKs or retarget the product to10.

Official SDK selection semantics: https://learn.microsoft.com/en-us/dotnet/core/tools/global-json (SDK selection is independent of targeted runtime; latestFeature stays within specified major/minor). Actual installed matrix here is only SDK8.0.425. SDK9/10 guard checks override the MSBuild NETCoreSdkVersion for the real validation target; they are targeted validation, not builds under actual installed9/10 SDKs. Native Windows execution remains unrun and needs the user's asynchronous recheck.

Final source evidence: SDK8.0.425 full solution clean/build passed, 0 warnings/0 errors (5.20s), /tmp/sdk8-fix-clean-build.log; incremental solution build passed0/0 (1.22s), /tmp/sdk8-fix-incremental-build.log. ToolchainSelectionTests passed2/0 (5.798s), /tmp/sdk8-fix-selection-tests.log. Private clean/incremental authoring copies keep identical output hashes, inspect actual DLL metadata for System.Runtime major<=8, and execute the real syntax projection. A synthetic major5 assembly tests wrong-major rejection; it is not actual Roslyn5/SDK10 execution. Explicit NETCoreSdkVersion10.0.401 guard returned exit1 with the expected prerequisite diagnostic and no CS1705, /tmp/checkpoint11-sdk10-guard.log. Focused SchemaEditing1/0 (18.836s), ProjectionDelivery2/0 (99.850s), CompilerTransport1/0 (2.942s), Win32Contract1/0 (9.388s) passed, all subprocesses exit0. Actual Linux X11 engine run returned exit0 with two-window isolation/reopen PASS and engine stopped; fixedTicks75/droppedSeconds0. These earlier candidate results validate installed SDK8 behavior; final related regression results are recorded below. Historical rationale remains unknown; the user has now independently chosen8. Previous CP11 full113/0 (2120.559s) is baseline evidence, not a claim of a new115-test full run.

Exact commands:

```sh
export CONFECTORY_DOTNET=/workspace/toolchains/dotnet-8.0.425/dotnet
export DOTNET_CLI_HOME=/tmp/confectory-dotnet
$CONFECTORY_DOTNET --version
$CONFECTORY_DOTNET build Confectory.sln -c Release --nologo
$CONFECTORY_DOTNET build tests/Confectory.Tests -c Release -o .confectory/verification-sdk8-fix
$CONFECTORY_DOTNET .confectory/verification-sdk8-fix/Confectory.Tests.dll ToolchainSelectionTests
$CONFECTORY_DOTNET msbuild targets/element-authoring/Confectory.ElementAuthoring.csproj -target:ValidateAuthoringSdk -property:NETCoreSdkVersion=10.0.401 -nologo
```

The last command intentionally fails to validate early rejection. Additional test filters: SchemaEditingTests, ProjectionDeliveryTests, CompilerTransportTests, Win32ContractTests. Linux native smoke uses DISPLAY=:97 CONFECTORY_BASEUI_SCRIPTED=1 CONFECTORY_BASEUI_CLOSE_AFTER_MS=1500 with CLI run examples/engine/project.cpack linux. No binaries/images/raw user log are in Git.


Outside implementation scope: build configuration/SDK-derived authoring references and test registration only; no Core or pack implementation/contract change. Public provider bindings and generated ProjectPack compiler already requireSDK8. No newly downloaded DLL/package or binary is committed. RigMotion/RenderAuthoring draft files remain outside this fix.

Windows recheck from the corrected checkout:

```bat
dotnet --list-sdks
dotnet --version
build-windows.bat
run-engine-windows.bat
```

Run these from the repository. The version should report8.0.* when an8.0 SDK is installed, even if10 is also installed. If the list has only10, the current source build prerequisite is an installed8.0 SDK; a runtime/reference pack alone is insufficient. Installation is not performed here. Native Windows and a real side-by-side SDK8/10 matrix remain asynchronous user checks, not claimed passes.


Final related regressions after the source fix: SchemaEditing1/0 (18.439s), ProjectionDelivery2/0 (89.528s), CompilerTransport1/0 (3.724s), Win32Contract1/0 (8.526s), all exit0. Together with ToolchainSelection2/0 (5.798s), seven focused tests pass. Logs /tmp/sdk8-fix-final-<test group>.log and /tmp/sdk8-fix-selection-tests.log. Final product/test source commit4db9279109d3629d35e2708146203e653e8617aa; only documentation follows. Existing full CP11 remains113/0 baseline; no new full115 run claimed for this scoped configuration-only fix. Normal publication is limited to fix/checkpoint-11-sdk8 and must be verified against its final local SHA; CP11 and main stay unchanged. Local receipt is retained under ignored .confectory after a successful push.
