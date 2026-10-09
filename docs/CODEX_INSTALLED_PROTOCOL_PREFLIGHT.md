# Installed Codex protocol preflight (2026-10-09)

Subsequent implementation and installed unauthenticated startup evidence:
[no-environment offline gate](CODEX_NO_ENVIRONMENT_OFFLINE_GATE.md). This document
records the earlier investigation stage; it is not the latest runtime outcome.

The executable `/opt/codex/bin/codex` reports `0.159.0-alpha.3`.
Public app-server help supports stdio and local experimental JSON-schema generation.
`codex login status` returned exit 0 / ChatGPT mode; raw output was suppressed.
This establishes neither account ownership, entitlement, nor usable managed authentication.
No authentication/configuration file was manually read, copied or modified; no model
request, project transmission, new login or persistent account setup was performed.

Schemas were generated locally into an owned temporary directory using an empty
`CODEX_HOME`, with `app-server generate-json-schema --experimental --out <owned-dir>`.
No app-server session was started. The actual qualified provider's owned stdio fixture
captures outgoing initialize/thread/start/turn/start/turn/interrupt requests. The optional
installed-schema gate validates these captures with the installed CLI's generated schemas,
including negative checks for the previous enum mismatch. It does not replace the
actual EditorHome consumer gate with a direct live provider call.

Thread `SandboxMode` uses `read-only`; turn `SandboxPolicy.type` uses `readOnly`.
The turn requests `networkAccess=false`. The previous invented
`sandboxPolicy.access.readableRoots` field was removed: it is absent from this version's
schema. These are protocol-shape checks, not proof of kernel sandbox enforcement.
Read-only does not imply a read allowlist. Empty cwd, environment clearing, ephemeral
thread storage and aborting native protocol items do not constrain all file reads.
Native protocol detection may happen after a native operation; it is not isolation.
Sandbox network denial does not mean denial of the server's model-service traffic.

**Live execution remains unsupported.** Desktop/browser/Android/functionTools capability
flags stay false. The actual EditorHome settings -> binding -> ai-prepare path is tested
to refuse Codex before any provider dispatch. Direct Provider is an explicitly trusted
low-level transport contract, not a substitute permission boundary; caller-provided
`protocolVerified` and other booleans cannot establish read isolation or account ownership.
The installed turn schema also accepts a named `permissions` profile id, mutually
exclusive with `sandboxPolicy`; a profile name alone is not a verified configured OS
boundary. No permission profile or security configuration was changed in this task.
An independently enforced and tested read boundary, approved usable managed storage,
confirmed account, model/service and reviewed exact content/usage scope are still required.
Existing environment account storage is read-only and ownership is unverified; do not use it.

Pack increment ledger: own Confectory.Agent.Codex::Provider/AdapterBody and compatibility
ProviderBody request serialization changed; Connection's unsupported reason clarified.
Public signatures and role composition unchanged. Outside implementation reads:
EditorHomeModel::Command's capability gate to verify that unsupported metadata is checked
before AIOpen, because transport contracts alone cannot establish product authorization.
Outside edits: owned provider fixture/schema regression and actual EditorHome consumer
test, to verify request shape and refusal through the existing product path. No core,
platform, Agent, Helper, Worker, Augment or EditorHome implementation changes.
Rebuild expectation: AdapterBody physical owner only, zero public contracts for a body
probe; Connection metadata additionally affects consumers of its declared capabilities.
Functional transport and product refusal gates are separate from locality/structure gates.

Commands (SDK path is this environment's existing installation):

```sh
DOTNET_CLI_HOME=/tmp/confectory-dotnet10 /workspace/toolchains/dotnet-10.0.401/dotnet build tests/Confectory.Tests -c Release --no-restore
CONFECTORY_CODEX_SCHEMA_DIRECTORY=<owned-generated-schema-dir> CONFECTORY_DOTNET=/workspace/toolchains/dotnet-10.0.401/dotnet DOTNET_CLI_HOME=/tmp/confectory-dotnet10 /workspace/toolchains/dotnet-10.0.401/dotnet run --project tests/Confectory.Tests -c Release --no-build -- test_codex_owned_stdio test_declared_connection_settings test_actual_editor_home_ai_scope
```

The schema gate requires existing Python `jsonschema`; no tools were installed.
Schema bundles, captures and diagnostics remain outside Git. Windows/Android checks are
managed target builds, not native Windows or Android-device execution. Existing SDK
and user version settings are preserved. No live, filesystem-isolation or account test
is implied by owned simulated provider success.

Verification outcome: tests build passed with 0 warnings/errors (6.25s). The three
filtered regressions passed, 0 failed, 0 skipped (116.524s), including the optional
installed-schema capture gate, provider-owned body locality with zero compiled
contracts, Windows/Android managed builds, API approval guards, and actual EditorHome
Codex refusal before provider dispatch. Private logs:
`/tmp/confectory-codex-schema-build.log` and
`/tmp/confectory-codex-schema-regression.log`.
No new GUI/visual, WASM build, native Windows, Android-device or live account coverage
was claimed for this serialization/metadata change.
