# Minimal Codex connection and Windows exe package

The Codex connection UI now exposes a login action, the installation/login consent that is actually needed, progress/cancel, failure/retry and automatic Agent registration. Candidate installations, account directories, path/platform/version chores, advanced/manual settings, model fields, save/check/manual registration and refresh menus are absent from the rendered Codex screen. Internal compatibility and discovery APIs remain. Original v508 styling/reference and existing account/project/settings data are preserved.

Existing distinct accounts lead to official login rather than a local directory list. The same identity across multiple homes has one identified confirmation. Existing confirmed identity and saved/configured/default models are reused; absent these, the first model returned by the official visible catalogue is selected. Every actual Helper turn still needs its reviewed request approval. Selecting the card loads settings declarations but starts no runtime discovery, installation, authentication, model RPC or external relay. Local settings loading may invoke the authoring host.

## Exact policy failure investigation

The previous `policy-check` has deliberate `PlatformNotSupportedException` guards; the user's diagnostic does not establish an unsupported Windows .NET API. The pinned official `0.159.0-alpha.3` CLI, started with a fresh empty owned account home and all existing disabled features, reports the default `unified-computer-use@openai-bundled` plugin enabled even when `--disable plugins` is present. This causes the old extension guard to refuse readiness. An owned account/provider fixture reproduced the original stage/code/type/processStarted/version combination before the fix.

Provider and login processes now receive the raw argument `plugins.unified-computer-use@openai-bundled.enabled=false` through `ArgumentList`. This affects only those child processes. Quoting the plugin key inside that raw argument creates a separate entry and does not disable the original bundle. No user configuration, plugin installation, credentials or accounts are edited. Other enabled plugins/MCP entries and enabled web search are still rejected. Failure detail includes only fixed labels (`enabled-plugin-entry`, `enabled-mcp-entry`, `startup-web-search`); names, paths and config contents are not returned.

The real CLI probe used a cleared environment, ephemeral credentials and a child seccomp guard denying socket/connect/send/io_uring. It only initialized, read the null account with `refreshToken:false`, and read effective configuration. The bundle was confirmed disabled, search remained disabled and no auth file was created. This proves a shared default-configuration defect and its correction on the pinned Linux CLI. It does not uniquely identify the user's private Windows configuration or prove their connection succeeds.

`installation.state = not-installed-by-this-flow` means this onboarding transaction did not install a runtime. It does not mean the CLI is absent. To retry on Windows, use the updated build, open Codex and choose Login. If failure remains, open the failure-only error information and send that JSON (stage/code/detail and available numeric codes). No auth.json, tokens, complete config or private logs are needed.

## Windows output and execution

The existing Windows developer build action and `scripts/windows/internal/build-windows.bat` now create `Builds/Windows-x64/Confectory.exe`. A source checkout first needs a Release solution build. The explicit package command is:

```text
dotnet build Confectory.sln -c Release
dotnet targets/editor-desktop/bin/Release/net10.0/Confectory.dll package . Builds/Windows-x64
```

Keep the entire result folder with the exe. It includes the x64 GUI apphost, precompiled engine, pack/project metadata, UI resources, authoring/execution/compiler tools, generic Windows host and x64 WebView2 loader. Paths resolve from the executable folder. Existing explicit storage configuration is honored; otherwise editor data/logs use `%LOCALAPPDATA%/Confectory/EditorHome`. A valid existing result is retained as a `.previous-<timestamp>` folder during replacement. Unknown folders are not overwritten.

Microsoft .NET Desktop Runtime **10.0 x64** and Microsoft Edge WebView2 Runtime must already be installed. No system runtime is automatically installed. The .NET 10 SDK is additionally needed for package/project builds, not to open the precompiled editor. Framework-dependent apphost and WebView2 deployment requirements follow [Microsoft's .NET publishing documentation](https://learn.microsoft.com/en-us/dotnet/core/deploying/) and [WebView2 distribution documentation](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/distribution).

## Executed validation

- Actual Chromium coordinator/UI: **27 distinct scenarios passed** in one complete run, with no page errors or external browser requests. Fresh/existing runtime, logged-out/authenticated/empty home, defaults/configured/no models, install/login interruptions, repeated consent, retry without redownload, close/reopen, identity change, offline/reconnect, automatic registration and owned Helper response were exercised. Forbidden development controls and fields were asserted absent across initial, consent, pending, failure and ready states.
- Four policy-focused scenarios: bundled default, unchanged original enabled-bundle settings, unknown enabled extension rejection and web-search rejection. Rejected policies did not reach model/login/turn calls; retry after fixing the fixture proceeded. A seven-scenario focused run also passed account/model/identity cases.
- Actual Agent presentation/partial settings/missing authoring/retry/retained Responses input/late-close regression passed; actual owned global Helper scope/approval/cancel/history/restart and owned stdio protocol regressions passed.
- Latest Release solution build passed with zero warnings/errors. The package publisher compiled the Windows engine and published win-x64 launcher/native host. Manifest inventory, x64 PE GUI apphost/native loader, altered resource and missing dependency rejection passed.
- The final package has **2,221 files**. Its actual engine served all **50** pinned resources and rendered minimal Codex login from an unrelated working directory. This also passed using an owned runtime-only copy with no installed SDK/reference packs (`--list-sdks` empty).
- Original v508 stylesheet/reference hashes and current 50 resource identities matched. Git checkout startup and the internal installation/login consent regression are recorded in the final validation update below.

The initial regression batch failed two fixture argv assumptions after the new restrictive argument was added. The fake CLIs were updated to require the argument; global Helper and owned stdio passed. An installer test then revealed its own stale expectation of `approval-required` at the distinct `catalogue-approval-required` stage. The corrected test additionally asserts zero process/RPC changes before valid consent. Failed attempts are not counted as passing runs.

Actual Windows apphost double-click, CMD/PowerShell/WebView2 execution, the user's account/OAuth and paid inference remain unverified. UI account/model/service replies use owned fixtures; a passing schema or fixture is not live account success. No external Site deployment or relay prerequisite was introduced.

## Rendered evidence

These are actual runtime screenshots. All accounts, codes and models shown are synthetic fixtures.

- [Initial login](codex-minimal-connection/01-Codex-Login.png)
- [Installation consent](codex-minimal-connection/02-Codex-Install-Consent.png)
- [Device login](codex-minimal-connection/03-Codex-Device-Login.png)
- [Automatic Agent registration complete](codex-minimal-connection/04-Codex-Ready-Fixture.png)
- [Policy rejection and retry](codex-minimal-connection/05-Codex-Policy-Failure.png)
- [Final packaged engine login](codex-minimal-connection/06-Windows-Package-Login.png)
- [Installation completed, account query failed](codex-minimal-connection/07-Codex-Post-Install-Failure.png)

[Structured evidence](codex-minimal-connection-windows-package.json) includes method counts, public default-bundle observations, package checks, protected hashes and test limits.

A package built into an existing checkout’s `Builds/Windows-x64` reuses its existing `.confectory/editor-home` profile when present and no explicit storage override is set. Standalone distributions use the LocalAppData default. The profile stays outside the package; no user settings are copied into the ZIP. An owned checkout/profile fixture verifies reuse and unchanged sentinel bytes.

## Final validation update

The internal installer/login regression passed (1 passed / 0 failed / 0 skipped, 176.385s). It retains nine archive/digest/size/link/traversal rejection cases, lock/foreign-root preservation, cancellation before process start, stale consent, device URL/version gating, close/late completion and separate account/installation storage. `catalogue-approval-required` and model-bound `preflight-required` are distinct intended states. Both are now checked with zero new process starts or RPCs before their required approvals; the model-bound check does not inherit catalogue consent.

Library delivery was attempted for the ZIP and six synthetic runtime screenshots. The supported prepared-upload helper failed to discover Library tools because of a network error, before any upload was confirmed. No Library file ID is claimed. Local deliverables and reproducible Git build instructions remain available.
