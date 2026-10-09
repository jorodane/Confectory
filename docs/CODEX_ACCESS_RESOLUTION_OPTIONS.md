# Codex access resolution options (2026-10-09, research only)

There are official candidate paths. Current unsupported status means they are not
yet implemented and runtime-verified here, not that Codex cannot support this product.
No security configuration, account storage, authentication, permissions or model
requests were changed during this investigation. No app-server session was started.

The product promise is model access through DevelopmentTools only: one explicitly
chosen project ID and owned namespace, approved Helper context, bounded public
list/read/inspect and CAS stage/create drafts. No arbitrary filesystem path, other
projects, private Helper templates, native command, Confirm, build or task completion
capability is granted. Native file tools could bypass namespace/path validation and
read excluded files; native write tools could bypass draft revision/review semantics.
The app-server's necessary executable/runtime and separately approved authentication
storage are trusted transport resources, distinct from model tool read permission.
The objective is not literally zero process file reads; it is no unapproved
model-visible reads/actions and no access to unrelated host data through execution.

## Preferred minimal candidate: no environment access

The installed `0.159.0-alpha.3` generated schemas document `environments: []` on both
ThreadStartParams and TurnStartParams as disabling environment access. Omission
selects/inherits an environment; it is materially different from an empty list.
This is independent of cwd or read-only. The matching official version source
requires an environment before adding shell, apply_patch or view_image; dynamic tools
are appended separately. `features.shell_tool=false` removes shell registration but
alone does not remove apply_patch. No single public all-builtins allowlist was
established by the inspected CLI/config/protocol schemas. Some utility/extension
surfaces are independent of environments, so do not claim all native tools disappear.
Evidence: [version-pinned tool planning source](https://github.com/openai/codex/blob/rust-v0.159.0-alpha.3/codex-rs/core/src/tools/spec_plan.rs),
[version-pinned configuration schema](https://github.com/openai/codex/blob/rust-v0.159.0-alpha.3/codex-rs/core/config.schema.json).

Minimum implementation proposal (not applied): explicitly send empty environments
at thread and turn start; keep ephemeral/no-escalation policies and current public
dynamic tools. In an approved separate managed configuration, disable command,
browser/apps, hooks, subagent and other unnecessary extension surfaces, disable web
search and avoid inheriting MCP servers/plugins. Pin and verify effective configuration;
do not assume `{}` clears higher-priority managed layers. Inspect startup instruction
loading and all registered model tools, not just notifications after a tool has run.
Existing unsupported metadata stays false until installed behavior proves the promise.

Next local gate: disposable empty, unauthenticated home with synthetic allowed and
denied sentinel files; no production repository/account files. Verify effective no-
environment selection, absence/refusal of filesystem/command tools, continued public
dynamic-tool draft staging, startup context, repeated close and actual EditorHome
scope/approval path. This needs separate approval to start installed app-server and
apply isolated session configuration; it does not authorize login or inference.
Catalog/startup traffic must be blocked or explicitly approved before that experiment.
Schema validation alone cannot establish runtime behavior or all startup side effects.

## Additional official boundaries

Named permission profiles express read/write/deny rules, including default deny with
runtime exceptions. Thread/turn `permissions` cannot be combined with their legacy
sandbox fields. Profiles principally govern sandboxed local commands, not the entire
app-server or every connector/service surface. Platform enforcement differs, and
restricted container hosts can prevent Linux sandbox setup. Therefore a configured
profile plus synthetic allowed/denied tests is useful defense but is not a blanket
claim about parent-server credential reads. [Official permission profile scope](https://learn.chatgpt.com/docs/permissions).

Official documentation also supports Dev Containers as an outer isolation boundary.
For this product, a dedicated container/VM can omit host repositories/home/SSH/cloud
credentials/Docker socket, carry only reviewed content through stdio dynamic tools,
and use separately approved identity/storage. Anything mounted inside remains exposed
to that boundary: mounting a credential is not protecting it from model-accessible
tools. Keep inner controls where possible. The documented broad inner bypass mode
is not required or authorized here. [Official container guidance](https://learn.chatgpt.com/docs/agent-approvals-security).

Here `bwrap 0.12.0` and Docker CLI `28.4.0` are installed. Presence is not proof of
usable namespaces, daemon authorization, container isolation or firewall behavior;
none was activated/tested. No new tool installation was performed.

## User scope choices and exact approval boundaries

Moving to the user's computer resolves neither tool exposure nor read boundaries
automatically. It can provide an owned account, writable approved storage and usable
OS sandbox/container prerequisites, which this environment does not establish.

1. Preserve the current namespace/tool-only promise: approve disposable no-account
   runtime tests above, then implement and verify no-environment configuration.
   If effective startup/tool isolation cannot satisfy the promise, approve dedicated
   container/VM provisioning and the exact mounts/network destinations separately.
2. Explicitly approve a broader project-read mode: a named profile may allow the
   whole selected project plus disclosed runtime exceptions, with exact credential,
   unrelated-project and private-data denies. This includes non-element files and is
   a new product permission mode, not permission implied by today's approval preview.
   Native writes must remain denied so draft/review semantics still hold. Do not offer
   broad host read as the default. Verify direct-file and shell coverage per platform.
3. Use the existing Responses provider with scoped function tools to avoid CLI-native
   filesystem/command surfaces. API credential binding and usage-based billing need
   their own approval; this is not a Codex-subscription authentication shortcut.

All eventual live paths additionally require confirmed account ownership, exact
executable/model/service, managed credential/config/storage access, reviewed content
and tool scope, and usage/cost approval. No existing environment account may be used
just because `login status` succeeds. Source-only research changes no public contract,
pack selection or rebuild scope; current actual EditorHome live refusal remains tested
by the preceding c711799 regression, not a new runtime test in this investigation.
