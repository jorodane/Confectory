# .NET 10 migration

The repository selects stable SDK 10 (`global.json`: 10.0.100, latestFeature), and all solution hosts/tests use `net10.0`. Generated DotNet pack contracts, implementations and linked applications use .NET 10 reference assemblies and runtimeconfig 10.0.0 with LatestPatch. Authoring requires SDK10 Roslyn5; SDK8/9 and Roslyn4 fail with an explicit guard. C#12 language semantics remain unchanged.

Public pack element IDs, signatures and target protocol1 are unchanged. Tool executable locators, Windows/POSIX launch scripts, fixtures and metadata are updated together. Editor bodies receive only host output-path substitutions; their View, command, capability and loop behavior is unchanged. Android exporter changes are integrated separately by its owner. Historical SDK8 evidence is retained as history.

Compiler/reference/runtime hashes and target-tool bytes change the fingerprint, invalidating .NET8 generated caches. First rebuild covers every reached contract/provider/application; subsequent owning-provider changes retain existing locality rules. Outside-target edits are host consumers and their locators because the public target contract supplies compilation services, not installation paths. Core only changes its missing-host diagnostic; no engine or platform policy moves into Core.

Verified on Linux using `/workspace/toolchains/dotnet-10.0.401/dotnet`, `DOTNET_CLI_HOME=/tmp/confectory-dotnet`, `CONFECTORY_DOTNET` pointing at that executable:

```
dotnet build Confectory.sln -c Release --nologo
dotnet tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll CoreTests ToolchainSelectionTests CompilerTransportTests RuntimeBaseTests RealTimeUpdateTests
```

Release build: zero warnings/errors, 18.18s. Official `wasm-tools` workload 10.0.112 installed alongside Android36.1.2, preserving SDK8. Repository NuGet.Config clears feeds; workload installation explicitly used `--source https://api.nuget.org/v3/index.json --skip-manifest-update`. No signing credentials or external deployment involved.

Migration build/test evidence is not proof that a separate browser/Android shell runs the desktop editor ProjectPack. Same-pack platform execution, actual Windows GUI and Android device/signing are separate gates.
