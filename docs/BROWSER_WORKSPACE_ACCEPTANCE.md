# Actual browser workspace acceptance

`tests/web/editor_home_workspace.py <browser-build-report.json>` drives the generated actual EditorHome Canvas/UI through New, owned project creation, Edit sources, source textarea edits, Save draft, Leave, recent reopen, app reload/recent reopen and Export work copy.

The test passively observes actual Canvas labels while calling the original renderer. It does not issue model commands, replace entry bodies or modify generated output. A read-only target storage map additionally verifies that Save/export never change the final `main.csbody` source before Confirm. The downloaded ZIP must contain the edited body, the original ProjectPack and ProjectInfo declaration. Stable native textarea identity and acknowledged IndexedDB saving are distinct assertions. Static browser requests must remain GET-only with no backend API route.

Functional result is recorded only after the real product run. This test does not assert dynamic compilation, execution of exported gameplay, physical OS chooser cancel, Android/Windows device runtime, or durable runtime-only project chat.

Result: PASS against root frozen product commit `3c8f06f`, browser report `/tmp/confectory-workspace-browser-final-build.json`; actual gate log `/tmp/confectory-workspace-browser-actual.log`. This verifies the same public entry `Confectory.EditorHome::Main`, real common UI and selected browser providers with no generated output mutation.

```
python3 tests/web/editor_home_workspace.py /tmp/confectory-workspace-browser-final-build.json
python3 tests/web/editor_home_browser.py /tmp/confectory-workspace-browser-final-build.json
```

Both commands passed. The unchanged NativeUI regression also covers folder import, controls/input, repeated leave/reopen, original DOM owner release failure/retry/idempotence and static WASM use. Its console includes a missing favicon/resource HTTP404; no page exception or API/backend request occurred. Native source textarea identity after Save, final source byte preservation and exact downloaded ZIP overlay are functional assertions. Build locality is assessed independently by the root compiler report, not inferred from a UI pass.

## Responsive actual product replay and build defect

The first responsive product output failed before initial UI: Chromium rejected Core bytes against the SDK boot integrity catalogue. Original gate log `/tmp/confectory-workspace-browser-responsive-actual.log`, diagnostic replay `/tmp/confectory-workspace-browser-responsive-replay.log`. No assertion/time limit, original input or SRI policy was relaxed. The first immutable-reference layout then failed SDK compression and remains recorded separately. See `BROWSER_PUBLISH_INTEGRITY_FIX.md` for concrete same-byte inside/outside reference location evidence and the general build-target fix.

After immutable sibling reference captures, exact publish-bundle selection and compiled boot-resource integrity validation, the actual product rebuild reports tool.ok=true and zero warnings: `/tmp/confectory-workspace-browser-sibling-fixed-build.json`.

```
python3 tests/web/editor_home_workspace.py /tmp/confectory-workspace-browser-sibling-fixed-build.json
python3 tests/web/editor_home_browser.py /tmp/confectory-workspace-browser-sibling-fixed-build.json
```

Both PASS. In addition to the original full flow, the workspace gate resizes the actual source View to 480x850 after reopen: the same textarea DOM instance and edited text remain, its bounds stay visible inside the viewport, and the wrapped-row Save button produces the actual durable acknowledgement. Restoring 1200x850, reload/reopen, downloaded ZIP verification and final-source preservation all pass. Logs `/tmp/confectory-workspace-browser-sibling-fixed-actual.log` and `...-regression.log`. The original failures are not replaced by this later successful run.
