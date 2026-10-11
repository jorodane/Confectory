# Generic web UI foundation — 2026-10-11

This change separates presentation resources and a bounded web transport from
consumer-owned functionality. It is not the v180 Sites visual port or the paused
native editor redesign. The latter's 18 dirty files remain unchanged in the
original checkout, with a binary patch, working-file archive and SHA-256 manifest
in `/workspace/confectory-paused-ui-backup`. Work here uses the separate
`/workspace/Confectory-web-ui` checkout on work/current, starting at f182ea3.
No paused redesign files are copied into this implementation.

## Ownership

- New `Confectory.WebUI`: declared resources/entry, view lifetime, revision
  subscriptions, explicit consumer endpoint requests, results/errors, cancellation,
  scope validation and bounded deduplication. Reuses RuntimeBase ownership.
- `Confectory.BrowserHost`: generic loopback transport and HostLoop cleanup.
- `Confectory.BrowserRuntime`: generic WASM bridge adapter; no editor dependencies.
- Existing import-only demos own their former editor-specific adapters and assets.
  Web/WASM target packaging points to those legacy consumer resources.
- Actual EditorHome owns its public projection and permitted Model commands;
  ButtonGame owns Score and a shared native/web ChangeScore function.
- Core grammar/compiler contracts, domain Model, Save/Review/Confirm, AI permission
  policy, main branch, Android version settings and Sites are unchanged.

The compiled consumer supplies the context and exported endpoint list. Browser
input cannot choose a function ID, local path, project owner or Helper authority.
The current editor host selects a ProjectPack explicitly before listening. Its
projection excludes full model/configuration, capabilities, filesystem paths and
approval records. Selected source/draft text is the explicit editing payload. Account environment,
provider configuration and credential values are not read by the web adapter.
No real AI provider, account, credentials or external content transfer is used.

See [the pack contract](../packs/web-ui/README.md) for exact schemas, budgets,
non-rollback cancellation, packaging and future transport boundaries.

## Validation

| Check | Result / evidence |
| --- | --- |
| Actual ordinary EditorHome + ButtonGame in Chromium | Passed. Objects, host/Helper scope denial, undeclared endpoints/resources, request dedup, stale transport revision, real draft edit/Save, unchanged final source, reconnect/reload, domain draft CAS and unowned object denial. Final product rerun: 1/0/0, 38.967s; `/tmp/confectory-web-ui-final-product.log`. |
| Common contract and ownership locality | Passed. Cooperative cancellation, nonblocking update while work runs, current Helper scope checks including replay, revision subscription, idempotent view/owner disposal and no late result. Shared batch: 2/0/0, 171.383s; `/tmp/confectory-web-ui-final-common.log`. |
| Existing local browser demonstration + consumer ownership locality | Passed, 1/0/0, 190.074s; `/tmp/confectory-web-ui-legacy-final.log`. Current Model dependency/provide registrations were incomplete before this work and are reconciled. Current Model links AI/Helper contracts, so the test verifies native UI exclusion and actual rejection of AI/Confirm/arbitrary commands instead of an obsolete no-AI-assembly assertion. |
| Actual existing Linux EditorHome GUI | Passed: menus, tabs, execution/logs, resize, project context/lifetime and owning presentation locality; `/tmp/confectory-web-ui-final-gates.log`. Native presentation itself is unchanged apart from the opt-in web entry branch. |
| Windows / Android managed EditorHome | Passed for the ordinary EditorHome ProjectPack; combined platform gate in `/tmp/confectory-web-ui-final-gates.log`. Managed compilation only, not native Windows or Android device execution. |
| Generic BrowserRuntime browser-target contract compilation | Passed, `contract-only`; `/tmp/confectory-web-ui-runtime-check.json`. This is not WASM runtime or new HTML startup evidence. |
| Existing actual EditorHome WASM target | Failed at the unchanged outer 120-second target-tool deadline; `/tmp/confectory-web-ui-home-wasm.log`. No timeout, compiler/compression option, artificial success or per-editor exception was added. |
| Existing ButtonGame native GUI | Failed at hidden-button activation. Reproduced with unmodified f182ea3 ButtonGame sources using the same normal build/tool/provider and GUI script; `/tmp/confectory-web-ui-button-baseline-gui.log`. No input/native-navigation fix is included here. The test's later Windows/Android ButtonGame checks did not execute. |
| SDK / source hygiene | Solution/test projects build with zero warnings/errors; Python test scripts compile; `git diff --check` passes. |

Intermediate failure history is retained in `final-gates.log`: the new editor's
selection click was ignored during an outstanding list update; final consumer
controls now expose busy state and do not reconstruct unchanged DOM revisions.
The corrected product rerun passes. The earlier legacy dependency failure is fixed
and its full rerun passes. Do not interpret that earlier mixed batch as all green.

Actual browser screenshots are `/tmp/confectory-web-ui-editor.png` and
`/tmp/confectory-web-ui-button.png`. The product test uses a regular copied
ButtonGame ProjectPack for editing through actual EditorHome; it does not replace
the editor entry or domain functions. Separate deterministic contract fixtures
exercise cancellation only, not product feature success.

The paused native redesign's earlier browser-build timeouts, home-card test failure
and old harness storage-path error are not repaired or hidden by this separate work.

Independent new WASM HTML startup, remote hosting/authentication, OS WebViews,
native Windows execution, Android device execution, full editor feature parity and
v180 visual fidelity remain outside this first common-boundary implementation.
