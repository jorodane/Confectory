# Multiple owned editor views

This continuation starts from verified `work/current` 3d741de, with main a4418ec preserved. It implements behavior through existing public PackWorkspace, UIOrder/WindowPlacement, BaseUI controls and native text roles. No v180 artwork or unobserved geometry is invented.

## Consumer connections

The ordinary workspace has **Keep view** in Source and Properties. It retains up to three additional source or selected-field views beside the primary workspace. Header **View 1–3** buttons raise an obscured/folded view; **Reopen** restores a closed presentation. The existing eight-pixel top handle drags and double-clicks to fold. Common UIOrder composition owns z-order, visible regions, native clipping and hit testing; WindowPlacement owns movement/recovery. The current compact view is not a duplicate full explorer or an unbounded window manager.

Each additional Model workspace owner is bound to the live context, durable project ID, object ID and view mode. PackWorkspace::Open uses the same existing participant/context draft identity as the primary workspace; no separate editing session or private draft access is introduced. Selected-field views additionally retain a schema row ID and explicit path. Changing the primary selection or opening an actual schema does not retarget another window. Different objects and live projects have independent source/form buffers. Helper inputs retain their separate existing scope.

A source view reuses the object's actual text buffer. A selected-field view stages the existing data-path command, including compound/list paths, against its captured source revision. Clean field inputs follow updated authoritative values; locally changed input remains for explicit conflict resolution. Schema refresh describes the actual current shared draft and reports an unavailable field/schema rather than substituting a mock object. Inspect returns the bound object/field to the ordinary full workspace.

**Save draft** persists the working copy. **Set value** stages a revisioned draft edit. Neither commits final sources. Additional views cannot invoke Confirm directly: the primary workspace retains explicit source Review/Confirm and compiler validation. A peer edit after Review still invalidates the reviewed revision. No automatic merge, conflict resolution, new transmission/charge rule, Worker chat or model invocation is added.

Closing an additional view releases its PackWorkspace owner and hides its native fields. It retains presentation/buffer identity for reopening within the same live project. Other owners and the shared draft remain alive. Project hide keeps all view owners and placement. Complete project close retires every additional owner and its UI resources using the existing close-confirmation boundary. Cross-process layout persistence is not introduced.

The primary shell keeps its 128-control surface; additional controls have a separate ordinary 16-control surface. Input routes to the owning surface, and keyboard groups contain only screen-relevant IDs. Common control/navigation budgets and platform build paths are unchanged.

## Boundaries and verification

Production changes are limited to EditorHome MainBody and EditorHome.Model CommandBody. Existing public function signatures, Core, platform adapters, Android settings and main are unchanged. Model Command adds optional bounded `view` slots and `open-view`/`close-view` actions using existing PackWorkspace operations. Detached mutations require the explicit matching object ID, and inherit the ordinary settings-secret guard, CAS and selected-project guard.

New actual acceptance scripts are `tests/gui/editor_home_multiview_x11.py` and `tests/web/editor_home_multiview.py`; both consume a normal build report for `examples/editor-home/project.cpack` and create ordinary projects through actual controls. The existing VerifyShell adds independent owner/selection/CAS, wrong-object rejection, peer-edit Review fencing and close/reopen checks. Build and acceptance results are recorded in [AI_DEVELOPMENT_STATUS.md](AI_DEVELOPMENT_STATUS.md).

The three retained compact views do not each reproduce every primary toolbar or arbitrary independent explorer. Schema definition editing remains available through Source or Inspect in the primary editor; selected schema fields in a retained Properties view are descriptive. Existing full responsive scrolling, long-label sizing and v180 visual fidelity remain separate unfinished work.

## Reproduce the affected gates

Use the ordinary .NET 10 SDK, wasm-tools and existing native prerequisites. `CONFECTORY_DOTNET` names the installed SDK executable; private XDG/entry paths are useful when the host home is read-only. This environment's four-CPU quota required ordinary browser tool parallelism to be bounded with `DOTNET_PROCESSOR_COUNT=4 EMCC_CORES=4`.

```sh
$CONFECTORY_DOTNET build tests/Confectory.Tests -c Release
$CONFECTORY_DOTNET run --project tests/Confectory.Tests -c Release --no-build -- test_project_shell_domain_isolated_execution_no_null_chat_open_and_context_cleanup test_editor_home_semantic_presentation_rebuilds_only_own_provider
DISPLAY=:96 $CONFECTORY_DOTNET run --project tests/Confectory.Tests -c Release --no-build -- test_actual_editor_home_multiple_object_views_share_drafts
$CONFECTORY_DOTNET src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll build examples/editor-home/project.cpack linux > /tmp/editor-linux.json
DISPLAY=:96 python3 tests/gui/editor_home_multiview_x11.py /tmp/editor-linux.json
DOTNET_PROCESSOR_COUNT=4 EMCC_CORES=4 $CONFECTORY_DOTNET src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll build examples/editor-home/project.cpack browser > /tmp/editor-browser.json
python3 tests/web/editor_home_multiview.py /tmp/editor-browser.json
python3 tests/web/editor_home_connections.py /tmp/editor-browser.json
python3 tests/web/editor_home_windows.py /tmp/editor-browser.json
```

## Reference access restriction

The previously confirmed official Library consumer-local materialization attempts resolved the named PDF and Word original, then failed with `download failed`. The transfer endpoint probe was refused by the environment proxy with HTTP 403. The reference Sites request likewise failed with proxy 403 / Chromium ERR_TUNNEL_CONNECTION_FAILED. These observations establish an access restriction in the execution environment; they do not establish a broken document, an account permission problem or a user-PC setting to change. Library text access succeeded, but PDF pixels were not inspected.

No alternate route, proxy bypass, guessed transfer URL or Sites mutation was attempted. A supported next attempt is the same official Library materialization flow after the environment/service access issue is resolved, obtaining a fresh transfer response. Another supported source is a user-provided local copy through the normal attachment workflow. No specific allowlist or account setting change is prescribed because the responsible configuration and impact have not been verified. Report the confirmed proxy error through environment/service support if access remains blocked. External visual comparison remains incomplete and is not counted as acceptance of this increment.
