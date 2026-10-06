# SDK/Roslyn diagnosis and unpublished SDK8 candidate

Status: the SDK8-only policy below is a tested, unpublished candidate, not a chosen product baseline. Later user clarification says the previous engine was .NET10 and no downgrade was requested. No candidate implementation is committed or published; a private ignored backup is retained in .confectory/sdk8-proposal. See SDK_BASELINE_DECISION.md.

Base checkpoint remains immutable: a0f77a4d08dd6ddaa087de77697269a7b7cb7371 on integration/checkpoint-11. The scoped follow-up is fix/checkpoint-11-sdk8. Prior checkpoint markers, explicit core/window/Stage/Physics increments and all preserved prior local branch tips are ancestors of CP11. Main and CP11 are not rewritten or merged. CP12 work remains preserved separately and is not included in this fix.

The official Library Windows log libfile_244d65ea12fc8191a6ffb3ec036a316b was read at lines1..180 and540..589. It shows SDK10.0.401 building net8.0 projects, 27 MSB3277 warnings and two CS1705 errors in ElementAuthoring: SDK10 Roslyn Microsoft.CodeAnalysis/CSharp5.9 depends on System.Runtime10 while net8.0 references Runtime8. Core.dll appears in the conflict reference chain; that is not evidence that Core itself directly references Roslyn. The source has direct SDK-derived Roslyn HintPaths only in ElementAuthoring. This failure is distinct from compiler long-command handling.

Root cause: without repository SDK selection, solution builds use the selected/latest SDK; direct Roslyn library references consequently track that SDK, even though the authoring executable targets net8.0. The generated ProjectPack compiler already selects only installed8.* SDK directories and net8 reference/runtime packs; it is not changed here.

Fix: root global.json requests SDK8.0.100 with latestFeature and allowPrerelease=false. It accepts later installed stable8.0 feature/patch releases, including tested8.0.425, but does not roll to9/10. ElementAuthoring adds an early ResolveReferences guard against non8.0 NETCoreSdkVersion, so bypassed/overridden selection produces a useful diagnostic before CS1705. Product frameworks stay net8.0; no new NuGet dependencies, tools, downloads, installs or license acceptance. SDK10 can stay installed beside SDK8.

Prerequisite/workaround: from the updated repository run dotnet --list-sdks and dotnet --version. There must be an installed8.0 SDK; the selected version should read8.0.*. A Runtime8 or Microsoft.NETCore.App.Ref8 pack alone is insufficient. Both Windows scripts already enter the repository before building, so they honor global.json. If only SDK10 is installed, an approved/pre-existing SDK8 installation is required; scripts do not silently install it. For the unchanged CP11 checkout, the same repository-local global.json is a verified SDK8 selection workaround when a stable8.0 SDK is already installed. Do not delete other SDKs or retarget the product to10.

Official SDK selection semantics: https://learn.microsoft.com/en-us/dotnet/core/tools/global-json (SDK selection is independent of targeted runtime; latestFeature stays within specified major/minor). Actual installed matrix here is only SDK8.0.425. SDK9/10 guard checks override the MSBuild NETCoreSdkVersion for the real validation target; they are targeted validation, not builds under actual installed9/10 SDKs. Native Windows execution remains unrun and needs the user's asynchronous recheck.

Evidence: SDK8.0.425 solution Release build passed, 0 warnings/0 errors (5.38s), /tmp/checkpoint11-sdk-fix-build.log. New ToolchainSelectionTests passed1/0 (1.544s), /tmp/checkpoint11-sdk-fix-selection-tests.log. Explicit NETCoreSdkVersion10.0.401 guard returned exit1 with the expected prerequisite diagnostic and no CS1705, /tmp/checkpoint11-sdk10-guard.log. Focused SchemaEditing1/0 (18.836s), ProjectionDelivery2/0 (99.850s), CompilerTransport1/0 (2.942s), Win32Contract1/0 (9.388s) passed, all subprocesses exit0. Actual Linux X11 engine run returned exit0 with two-window isolation/reopen PASS and engine stopped; fixedTicks75/droppedSeconds0. These validate the candidate on installed SDK8; they do not justify selecting8 as the product baseline. Previous CP11 full113/0 (2120.559s) is baseline evidence, not a claim of a new114-test full run.

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
