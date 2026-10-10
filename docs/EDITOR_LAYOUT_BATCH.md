# Editor layout: bounded work area and responsive panels

This batch continues from `work/current` 7bca287. It applies the confirmed layout intent from the previously read v180 text: project header, Agent/Helper participant rail, central floating workspace, bottom project chat/logs and Dock. PDF pixels remain unavailable; this is not a claim of exact visual fidelity. No new document-download or proxy workaround was attempted.

## Visible changes

- Project chat has a stable reserved height independent of whether an object workspace is open. Its background and action row are visually grouped below the working area. Floating panels use that same working-area geometry, so Helper, direction, connection/permission and augmentation panels no longer extend over the chat/Dock at the checked sizes.
- The participant rail places the selected Helper identity and its actual local/AI state below the existing Agent control. The existing explicit Helper chooser and project scope remain the source of truth; no new Agent hierarchy or global conversation was invented.
- The Helper panel puts memory actions and scope at the top, owned Worker status/output in the middle, and its message plus Review/Close at the bottom. At short heights, redundant memory-count text is omitted while the actual controls and separate input remain available.
- Augmentation shows the existing three cards in columns when the panel is wide enough. Titles and summaries/tags wrap using existing public text metrics. At narrower widths, Previous/Next pages through the same three card identities; paging does not request, reroll or dispatch anything. At short heights, Worker actions are grouped into compact rows to keep the proposal readable. Existing selection, direction review, permissions, recovery and final-source confirmation semantics are unchanged.
- Panel dimensions respond to available width/height through the existing UIOrder/WindowPlacement contracts. Native field bounds, drawing and hit tests continue using their composed regions. The additional proposal page is presentation state scoped to the current live project and target and retired at complete project close.

Production changes are confined to `examples/editor-home/Main.csbody`. Model, shared UI contracts, platform adapters, native input providers, build acceptance gates, main and Android version settings are unchanged. The existing extra control surface now contains 18 controls (two proposal paging controls added); the shared control limit is unchanged. The retained three compact source/field views remain compact borrowed-draft presentations, not three independent full editors.

## Validation

The new native and browser probes use a normal build report for the same `examples/editor-home/project.cpack`, create ordinary projects through real controls, and compare field values/bindings and rendered geometry at 960×700, 1200×900 and 640×520. They verify that Helper controls stay inside their owner, the bottom chat remains editable, and proposal paging does not mutate/request AI work. The existing owned simulated-provider regression supplies actual proposal data and Worker behavior; no real AI account/model is used.

Final reports and results are recorded in the dated entry in [AI_DEVELOPMENT_STATUS.md](AI_DEVELOPMENT_STATUS.md). The final browser build passed with ordinary tool parallelism limited to two workers; four-worker attempts exceeded the unchanged outer timeout. This does not change compiler/native-build/compression/integrity gates.

Reproduce with the installed .NET 10 SDK in `CONFECTORY_DOTNET`, wasm-tools and the existing native prerequisites:

```sh
$CONFECTORY_DOTNET src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll build examples/editor-home/project.cpack linux > /tmp/layout-linux.json
DISPLAY=:96 python3 tests/gui/editor_home_layout_x11.py /tmp/layout-linux.json
DOTNET_PROCESSOR_COUNT=2 EMCC_CORES=2 $CONFECTORY_DOTNET src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll build examples/editor-home/project.cpack browser > /tmp/layout-browser.json
python3 tests/web/editor_home_layout.py /tmp/layout-browser.json
python3 tests/web/editor_home_connections.py /tmp/layout-browser.json
python3 tests/web/editor_home_windows.py /tmp/layout-browser.json
```


## Windows check at home

Use `run-home-windows.bat` for this layout batch. `run-editor-windows.bat` launches the separate older `examples/editor/project.cpack` consumer (Agent Manager / Offline local mode / Source, Properties and Elements); that screen cannot validate these EditorHome changes. The earlier launcher/log recommendation was incorrect; the implementation and recorded validation target remain `examples/editor-home/project.cpack`.

1. In a clean checkout, fetch `origin` and fast-forward `work/current` to the commit reported with this batch. Preserve any local edits; do not reset them. Double-click the existing `run-home-windows.bat` (which runs `examples/editor-home/project.cpack`) with the repository's required .NET 10 SDK available. This batch does not change the launcher or install anything on your PC.
2. Create/open a disposable project, open a source, and choose/create a Helper through the left participant rail. Type different text into project chat and the Helper message. Resize between approximately 1200×900, 960×700 and 640×520; both drafts and the Helper Close button should remain usable without overlap.
3. Open Augment. Without an AI connection, the three empty slots are explicitly placeholders. Wide layout shows three columns; narrow layout pages through Proposal 1/2/3 without a request. Real generation still requires the existing separate review/approval; it is not necessary for this layout check.
4. Move/fold/reopen a working window, use Source/Properties and the existing object/schema navigation, and hide/reopen the project. Verify retained input and the separate Save draft → Review → Confirm boundary. Do not Confirm test changes into a project you want to preserve.

If launch or native behavior differs, retain `.confectory/home-launch.log` and the viewport size/action sequence. Managed compilation here does not substitute for Windows runtime acceptance.

## Remaining limits

Exact PDF-derived colors, artwork and pixel placement remain unverified. Complete YogiBox/notification/tool delivery semantics, full Agent/Helper grouping and arbitrary independent editors are not introduced. Very short viewports, long compact button captions and large object/schema forms still need further responsive/scrolling work; bounded panels do not imply every document fits without truncation. Browser responsiveness is not established by functional UI tests. Native Windows/Android device execution and live model/account use remain deferred. Sites and the previous stopped Work are untouched.
