---
name: setup
description: Connect to the local Confectory engine, discuss and propose new projects before one exists, then separately authorize any project or Blueprint node access.
---

Use the packaged `confectory_instances` tool to find prepared local engines. This plugin uses the existing Confectory workspace tools; do not create another editing, proposal or batch system.

This onboarding runs after the plugin has been installed from a configured local development marketplace. ZIP is a transport archive, not a direct desktop install action. Do not invent a ZIP import or personal Git-URL input screen. The repository source omits server binaries, so registering its Git URL alone is not a runnable installation. Refer to the built marketplace root's README for reviewed source registration; never execute registration or change existing configuration without authorization.

Explain that this development package requires a supported local desktop plugin surface, .NET 10 runtime, and Confectory running under the same OS user. Actual ChatGPT app installation must be verified by the user. Browser/cloud sessions cannot reach a user's local IPC directly. If the MCP server cannot start, ask the user to confirm the existing .NET runtime and package location. Do not install a runtime, change Codex settings or register a marketplace without explicit authorization.

For a launch failure, `dotnet --list-runtimes` must be available in the desktop host environment and list `Microsoft.NETCore.App 10.x.x`. Command not found indicates missing PATH/runtime discovery; a missing 10.x line indicates the required runtime is unavailable. A newer major runtime alone does not meet this package's default policy. Do not report those prerequisite failures as account authentication or engine-project connection failures.

If no engine is available, guide the user to the existing Confectory AI connection flow: **Agent 추가 → Codex → 엔진 연결 준비**. This works from the start/Home screen without a project. Do not tell the user to open a project just to connect, add an independent plugin button, launch an engine or open a project automatically.

If several instances appear, show each engine instanceId and its current scope or absence of project access; ask the user to choose. Never silently pick the first engine or a project. Use `confectory_connect` with the exact instanceId, then `confectory_status`. Engine state `ready` with `scope: null` is a valid connection and grants no project access. The four connection-management tools remain usable before a project is chosen.

Discuss the intended task before choosing a project. When project data is actually needed, have the user select the target through Confectory's existing Home/project UI, then use the same **Agent 추가 → Codex** form to choose an explicit project-owned-source or selected Blueprint-node range and click **선택한 범위 허용**, leaving **프로젝트 읽기 전용** checked. Opening a project alone does not authorize access. Do not open, pick, grant or broaden a target automatically.

For creating a new project, keep using the current conversation. With no project
selected, refresh tools and call `engine_project_options` for the actual supported
template and targets. Only when the user explicitly asks for a creation proposal,
call `engine_project_propose` with title, description, intent, templateId and
targetId. This leaves a proposal in the running engine and creates no files. Do not
invent unsupported templates or send a filesystem path, target-pack path, shell
command, Helper/Agent assignment or confirmation request. Have the user choose
**Home → 도우미의 새 프로젝트 제안 → 제안 검토**, review/edit the existing creation
form, pick the parent folder locally, then press **프로젝트 생성** themselves.
Use `engine_project_status` for that connection's proposal receipt. A created
project still has no MCP access until the separate explicit scope grant. A missing
engine creation tool means that engine/adapter needs the current build; selecting
an existing project does not add this capability. Pending proposals are retired
on connection close or engine restart and must not be automatically replayed.

After the user grants a range, call `confectory_status` and refresh the tool list. Echo the exact `scope.id` as `scopeId` and its `projectId` in every workspace tool call. The definitions reuse the existing DevelopmentTools and pin this scope ID. Start with `workspace_list` or `workspace_read` within it. Do not infer filesystem paths or request other source files. A connected transport does not complete the engineering task.

If edits are requested and the connection is read-only, explain how the user can release only the project scope with **프로젝트 접근 해제** and explicitly grant an editable scope, keeping the engine connected. Do not change permissions on their behalf. Existing `workspace_stage` uses the exact displayed revision (and the displayed hash for a node); `workspace_create` stages existing declaration/registration drafts. Their success never changes final source. Show `workspace_changes`, then direct the user to the existing Confectory **변경 검토 → Review/Confirm** flow. There is no plugin Confirm, build, runtime or shell tool.

On a CAS refusal, keep the proposed text and report the conflict. Read the current approved source again or have the user prepare a fresh node scope. Never reset, force, silently rebase or replay a mutation. On an uncertain write outcome, inspect the existing draft changes before any new request; cancellation is not rollback.

On project open, hide, close or switch, the engine connection stays available while the old project capability is retired. Observe `scope: null`, discuss the next target, and wait for a fresh explicit grant. Refresh status and tools after every grant or revocation. Never reuse an old scopeId, even when reopening the same project; do not replay cached or uncertain writes across scopes. Engine restart retires both the connection and all project access: prepare and select a new instance explicitly. `confectory_disconnect` only clears this adapter's selection; it does not kill Confectory or discard drafts.
