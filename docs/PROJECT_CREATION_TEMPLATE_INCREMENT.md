# Owned source project creation

ProjectManager::CreationTemplate(namespace,targetPack) is a new public role contract returning owned relative path/content pairs. CreateProject invokes it before atomic staging, rejects unsafe, duplicate, or entry-overwriting paths, commits a new directory only, and rolls back if public Open fails. Desktop preserves the existing explicit target pack requirement. Android/browser choose the same offline source template through ordinary target body selection.

The offline template contains standalone project.cproj, common Main source and an owned Confectory.Build.DotNet target pack. Portable/windows/linux are declared; compiler is explicitly absent at build/tools/Confectory.Build.DotNet.dll. BUILDING.txt tells the caller to provision the complete installed compatible .NET10 compiler directory on desktop or explicitly replace its registry. Source creation is not an APK/browser compilation or native execution claim. There is no hardcoded engine/editor namespace, consumer path lookup, alias, or platform core change. The template's namespace is caller-selected and validated.

Outside implementation reads: EditorHome Model Command/CreateSession inspected because they supplied the repository target path. Only Command edited to allow explicit targetPack input, with its desktop fallback retained; Android/browser template does not read that path. EditorHome public binding inspected to verify provider resolution. ProjectExecution DescribeProject inspected because creation commits only after public metadata Open succeeds. Existing target tool metadata inspected to preserve the supported DotNet mode contract. Baseline design text sections on ProjectPack/target providers read. No exporter resource edits needed: ordinary role linking carries the selected template body.

Rebuild scope: new CreationTemplate contract/provider, CreateProjectBody import and body, Model CommandBody. Existing core/renderer/input/window contracts unchanged. Functional gates and body-locality gates are separate; actual product UI coverage remains integration-owned. Auxiliary template tests do not replace actual EditorHome interaction.

Validation commands (SDK10.0.401, DOTNET_CLI_HOME=/tmp/confectory-dotnet10, CONFECTORY_DOTNET selects the same SDK):

- `dotnet build Confectory.sln -c Release`: 0 warnings/errors.
- `dotnet tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll --require-runtime ProjectManagerTests`: existing lifecycle/locality 1 PASS, 0 FAIL/SKIP, 86.285s (before new method registration).
- `dotnet tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll --require-runtime offline_creation`: 1 PASS, 0 FAIL/SKIP, 13.126s. Android/browser-selected template auxiliary test; exact arbitrary namespace, nonexistent repository hint, explicit absent-tool failure, provisioned real compiler build/run and body-only locality. This is managed template validation, not Android/browser native UI.
- `dotnet src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll build examples/editor-home/project.cpack android`: actual product compile gate running at increment commit; native API36 export and UI gate remain integration-owned.
