---
name: setup
description: Connect this development plugin to the exact project or Blueprint node the user prepared in their local Confectory desktop app.
---

Use the packaged `confectory_instances` tool to find prepared local engines. This plugin uses the existing Confectory workspace tools; do not create another editing, proposal or batch system.

This onboarding runs after the plugin has been installed from a configured local development marketplace. ZIP is a transport archive, not a direct desktop install action. Do not invent a ZIP import or personal Git-URL input screen. The repository source omits server binaries, so registering its Git URL alone is not a runnable installation. Refer to the built marketplace root's README for reviewed source registration; never execute registration or change existing configuration without authorization.

Explain that this development package requires a supported local desktop plugin surface, .NET 10 runtime, and Confectory running under the same OS user. Actual ChatGPT app installation must be verified by the user. Browser/cloud sessions cannot reach a user's local IPC directly. If the MCP server cannot start, ask the user to confirm the existing .NET runtime and package location. Do not install a runtime, change Codex settings or register a marketplace without explicit authorization.

For a launch failure, `dotnet --list-runtimes` must be available in the desktop host environment and list `Microsoft.NETCore.App 10.x.x`. Command not found indicates missing PATH/runtime discovery; a missing 10.x line indicates the required runtime is unavailable. A newer major runtime alone does not meet this package's default policy. Do not report those prerequisite failures as account authentication or engine-project connection failures.

If no engine is available, guide the user to open their project in Confectory, choose **메뉴 → ChatGPT 플러그인 연결**, select the scope, leave **읽기 전용으로 연결** checked, then click **연결 준비**. For a Blueprint node scope, select a C# node in Blueprint before reopening the connection panel. Do not launch an engine or open a project automatically.

If several instances appear, show their project title, node scope and instanceId; ask the user to choose. Never silently pick the first engine or another project. Use `confectory_connect` with the exact displayed instanceId, then `confectory_status` to confirm the actual projectId, node scope and read-only state. Refresh the tool list after its list-changed notification.

Start with `workspace_list` or `workspace_read` within that exact scope. These schemas and operations come from Confectory's existing DevelopmentTools. Echo its projectId. Do not infer filesystem paths or request other source files. Do not treat a connected transport as completion of the user's engineering task.

If edits are requested and the connection is read-only, explain how the user can close that connection in Confectory and prepare an explicitly editable scope. Do not change permissions on their behalf. Existing `workspace_stage` uses the exact displayed revision (and the displayed hash for a node); `workspace_create` stages existing declaration/registration drafts. Their success never changes final source. Show `workspace_changes`, then direct the user to the existing Confectory **변경 검토 → Review/Confirm** flow. There is no plugin Confirm, build, runtime or shell tool.

On a CAS refusal, keep the proposed text and report the conflict. Read the current approved source again or have the user prepare a fresh node scope. Never reset, force, silently rebase or replay a mutation. On an uncertain write outcome, inspect the existing draft changes before any new request; cancellation is not rollback.

On project switch, scope change, disconnect or engine restart, reconnect explicitly to a newly prepared instance. No connection grant survives app restart. `confectory_disconnect` only clears this adapter's selection; it does not kill Confectory or discard drafts.
