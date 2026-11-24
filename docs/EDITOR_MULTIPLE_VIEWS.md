# Multiple owned editor views

The later [layout batch](EDITOR_LAYOUT_BATCH.md) bounds working panels above chat and adds responsive proposal columns/paging; older overlap/layout limitations below describe the earlier increment.

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

## Object-specific Editor View selection

EditorHome opens objects in its schema editor. **새 창으로 열기** uses the same renderer with an independently bound properties window. The server accepts three built-in window modes (`source`, `properties`, `declaration`). A project's pack registry describes dependencies and the inventory exposes declaration metadata. A durable object-to-editor binding and a resolver for a trusted renderer remain unimplemented. [EditorHome command](../packs/editor-home-model/Command.csbody) · [Separate properties renderer](../examples/editor-home/ui/element-instances.js)

The in-tree `ElementView` sample implements borrowed card and table projections. Its `Labels` output includes a raw declaration excerpt and test-consumer action captions. A read-only EditorHome connection would need a projection of approved typed fields for the current project and exact owned object, plus an explicitly selected renderer bundled with the host. [ElementView labels](../packs/element-view/Labels.csbody)

The remaining storage choice is who owns the selection.

- A private EditorHome preference would apply to that profile, project and object. The existing presentation data stores window and layout state, so a durable renderer choice would need its own validated meaning.
- A project-owned declaration would share the selection with readers of that project. The host would still have to resolve trust locally and check that the current project and object match. A copied declaration can carry a preference without carrying permission to run its renderer.

The Linux EditorHome boundary test registers the in-tree pack as a local dependency, verifies the default editor and separate properties window, and checks that the existing `viewMode` rejects a card mode and pack function identifier. It repeats the check after restart and opens the same qualified ID in a second project with independent data. The stand-alone ElementView test covers card and table lifetime. [EditorHome boundary test](../tests/web/v821_editor_view_registration_boundary_ui.py) · [ElementView test](../tests/Confectory.Tests/ElementViewTests.cs)

## Project-owned windows in the project menu

A project manifest can register a qualified `view` ID. An entry function can reach it with `use view`, and the build records the declaration and its metadata in the public linkage catalog. EditorHome's project-tools menu adds shortcuts for objects. Its independent editor windows accept the built-in `source`, `properties` and `declaration` modes. ElementView's stand-alone runner supplies its own workspace, selected element, render calls and input loop. [Linkage catalog](../src/Confectory.Core/Generation.cs) · [Project-tools menu](../examples/editor-home/ui/v508-runtime.js) · [EditorHome view modes](../packs/editor-home-model/Command.csbody) · [ElementView sample](../examples/element-view/main.csbody)

The browser project's ≡ menu lists directly owned, confirmed View declarations whose `editorWindow` value is `"element-view-card"` or `"element-view-table"`. Edit a registered view through **팩 관리 → 프로젝트 창 선언**, then use the existing source **Review** and **Confirm**. The view's `editorName` labels the menu entry. The initial read-only card and one-row table support one direct `use object` target with a directly owned schema declaring a single string field. The existing `value` declaration syntax carries the option.

On Linux GTK, choose **≡ → Project windows** to open the same confirmed card or table. A registered View can be edited in **Edit sources** by selecting its exact ID with **Prev** or **Next**, then using the existing **Review** and **Confirm**. There is no separate View authoring surface.

The host resolves the active project again for each menu listing and click and reads only confirmed files in that project. Browser responses are tied to the current project activation. The first projection sends the field label and literal string to the built-in presentation, with no declaration file paths, provider execution or object editing.

The installed Linux regression uses Alpha and Bravo with the same namespace and View source bytes. Only Alpha registers the View. It exercises a linked-only declaration, canceled Review, explicit Confirm for each renderer, unsupported renderers, project and Home isolation, ordinary concept and function editors and the existing ▶ action.

```sh
python tests/web/project_owned_window_boundary.py Builds/Linux-x64
python tests/gui/editor_project_windows_x11.py Builds/Linux-x64
```

The focused card-and-Run regression can reuse a Linux EditorHome build report from
the current checkout. With Chromium, Playwright and the .NET 10 tools available,
run from the checkout root:

```sh
python tests/web/project_owned_window_boundary.py "$LINUX_EDITOR_HOME_REPORT" --card-run
```

This mode confirms the read-only card after canceling one Review, opens it through
≡ and checks that it stays visible while Alpha's real entry runs exactly once.
Use `--card-refresh` with the same build report for two separate local editor
processes in one Chromium. The reader keeps its card open after the writer
cancels Review. After the writer Confirms, opening ≡ in the reader withdraws
both the menu entry and the open card.


## Read-only Recipe View

In **팩 관리 → 프로젝트 창 선언**, select a registered View that directly
uses an owned Recipe object. Its **≡ 메뉴에 표시** setting offers **읽기 전용
레시피** when the confirmed object follows the existing [Recipe contract](../packs/recipe/README.md)
and all ingredient and output IDs identify directly owned registered objects.
After Review and Confirm, open the View from ≡ to see the ingredient and
result IDs and quantities from confirmed declarations. Crafting and inventory
continue through their runtime controls. The opening Workspace uses its own
card and table settings. On Linux GTK, select the owned declaration under
**Edit sources**, then choose **View menu visibility → Read-only recipe**.
After Review and Confirm, open it through **≡ → Project windows**.
In the browser, **레시피 편집기 열기** selects the same registered recipe in
the existing editor. The host rechecks the current project and View when that
button is used. Existing draft and Confirm controls remain in the editor.

```sh
python tests/web/project_owned_window_boundary.py "$LINUX_EDITOR_HOME_REPORT" --recipe-view
python tests/web/project_owned_window_boundary.py "$LINUX_EDITOR_HOME_REPORT" --recipe-editor
python tests/gui/editor_project_windows_x11.py "$LINUX_EDITOR_HOME_REPORT" --recipe-view
```

## Confirmed workspace opening View

The browser and Linux GTK editors can open the root Workspace with one directly owned and
registered View. Go to **팩 관리 → 프로젝트 창 선언**, select the View,
and open **프로젝트 시작 화면 설정**. Choose the standard workspace, a read-only
card, or a read-only table. **초안에 적용** stages the selection with the existing
source input. Review and Confirm publish it for the next project open.
To change the designated View, first clear the current View's assignment and
Confirm that change. The independent **≡ 메뉴에 표시** setting stays intact.
On Linux GTK, use **Edit sources**, select the registered View with **Prev** or
**Next**, and choose **Project opening view**. Use the ordinary Review and
Confirm, then reopen the project. Both surfaces use the same read-only
object and string-field projection.
Absent, invalid, or ambiguous assignments use the standard workspace.

Run the focused check with a Linux EditorHome build report from the checkout:

```sh
python tests/web/project_owned_window_boundary.py "$LINUX_EDITOR_HOME_REPORT" --main-view
python tests/gui/editor_project_windows_x11.py "$LINUX_EDITOR_HOME_REPORT" --opening-view
```

The browser and Linux GTK Review show the opening screen before and after the proposal.
When a local Worker contribution matches the exact reviewed View text, the
Review also shows the recorded Worker and task. To check that path without
dispatching a Worker, build `tests/Confectory.Tests` in Release and run:

```sh
python tests/web/project_owned_window_boundary.py "$LINUX_EDITOR_HOME_REPORT" --worker-opening-review
python tests/gui/editor_project_windows_x11.py "$LINUX_EDITOR_HOME_REPORT" --worker-opening-review
```

## Reproduce the affected gates

Use the ordinary .NET 10 SDK, wasm-tools and existing native prerequisites. `CONFECTORY_DOTNET` names the installed SDK executable; private XDG/entry paths are useful when the host home is read-only. This environment's four-CPU quota required ordinary browser tool parallelism to be bounded with `DOTNET_PROCESSOR_COUNT=4 EMCC_CORES=4`.

```sh
$CONFECTORY_DOTNET build tests/Confectory.Tests -c Release
$CONFECTORY_DOTNET run --project tests/Confectory.Tests -c Release --no-build -- test_project_shell_domain_isolated_execution_no_null_chat_open_and_context_cleanup test_editor_home_semantic_presentation_rebuilds_only_own_provider
DISPLAY=:96 $CONFECTORY_DOTNET run --project tests/Confectory.Tests -c Release --no-build -- test_actual_editor_home_multiple_object_views_share_drafts
$CONFECTORY_DOTNET src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll build examples/editor-home/project.cpack linux > /tmp/editor-linux.json
python3 tests/web/v821_editor_view_registration_boundary_ui.py "$PWD" /tmp/editor-linux.json
DISPLAY=:96 python3 tests/gui/editor_home_multiview_x11.py /tmp/editor-linux.json
DOTNET_PROCESSOR_COUNT=4 EMCC_CORES=4 $CONFECTORY_DOTNET src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll build examples/editor-home/project.cpack browser > /tmp/editor-browser.json
python3 tests/web/editor_home_multiview.py /tmp/editor-browser.json
python3 tests/web/editor_home_connections.py /tmp/editor-browser.json
python3 tests/web/editor_home_windows.py /tmp/editor-browser.json
```

## Reference access restriction

The previously confirmed official Library consumer-local materialization attempts resolved the named PDF and Word original, then failed with `download failed`. The transfer endpoint probe was refused by the environment proxy with HTTP 403. The reference Sites request likewise failed with proxy 403 / Chromium ERR_TUNNEL_CONNECTION_FAILED. These observations establish an access restriction in the execution environment; they do not establish a broken document, an account permission problem or a user-PC setting to change. Library text access succeeded, but PDF pixels were not inspected.

No alternate route, proxy bypass, guessed transfer URL or Sites mutation was attempted. A supported next attempt is the same official Library materialization flow after the environment/service access issue is resolved, obtaining a fresh transfer response. Another supported source is a user-provided local copy through the normal attachment workflow. No specific allowlist or account setting change is prescribed because the responsible configuration and impact have not been verified. Report the confirmed proxy error through environment/service support if access remains blocked. External visual comparison remains incomplete and is not counted as acceptance of this increment.
