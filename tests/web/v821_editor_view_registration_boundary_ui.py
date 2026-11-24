"""Exercise the current EditorHome boundary with the in-tree ElementView pack."""

import json

from playwright.sync_api import expect, sync_playwright

import v821_object_fallback_roundtrip_ui as fallback
from v821_project_browser_search_labels import browser_window, choose_tree_location, search


fixture = fallback.fixture
PACK = "Confectory.ElementView"
OBJECT = f"{fallback.NS}::{fallback.TARGET}"


def register_local_sample():
    manifest = fixture.projects[0]
    packs = {
        PACK: "element-view",
        "Confectory.EditWorkspace": "edit-workspace",
        "Confectory.SchemaEditing": "schema-editing",
        "Confectory.FileStream": "file-stream",
    }
    declarations = []
    for namespace, name in packs.items():
        path = fixture.repo / "packs" / name / "pack.cpack"
        assert path.is_file()
        declarations.append(f"registry {namespace} {json.dumps(str(path))};")
    declarations.append(f'dependency {PACK} version "0.1.0";')
    manifest.write_text(manifest.read_text().rstrip()[:-1] + "\n" + "\n".join(declarations) + "\n}\n",
                        encoding="utf-8")
    fixture.before[str(manifest)] = manifest.read_bytes()


def assert_default_view(page, title, value, *, registered):
    editor, _ = fallback.open_from_search(page, title, fallback.TARGET, value)
    state = fixture.state()
    assert state["draft"]["id"] == OBJECT
    inventory = state["inventory"]
    assert inventory["status"] == "available"
    assert any(row["namespace"] == PACK for row in inventory["packs"]) is registered
    editor.get_by_role("button", name="창 닫기", exact=True).click()
    return state["projectId"]


def reject_provider_as_mode():
    before = fixture.state()
    assert before["draft"]["id"] == OBJECT
    assert all(row["view"] != "3" for row in before["editorViews"])
    for mode in ("card", PACK + "::Create"):
        reply = fixture.call("openEditorView", {"view": "3", "id": OBJECT, "viewMode": mode}, ok=False)
        assert reply["error"]["code"] == "consumer_error", reply
    after = fixture.state()
    for key in ("projectId", "editorViews", "draft"):
        assert after[key] == before[key], key
    fixture.original()


def check_ordinary_detached_view(page, title):
    window = browser_window(page)
    choose_tree_location(window, f'[data-tree-id="{fallback.NS}::PeerFolder"]')
    search(window, fallback.LABEL, fallback.PEER)
    window.locator(f'[data-object="{fallback.NS}::{fallback.PEER}"]').click(button="right")
    page.locator(".context-menu").get_by_role("button", name="새 창으로 열기", exact=True).click()
    editor = page.locator('.window[data-key^="editor-"]:visible')
    expect(editor.get_by_role("heading", name=fallback.LABEL, exact=True)).to_be_visible()
    expect(fallback.field(editor, "Note").get_by_label("Note 기본값", exact=True)).to_have_value(f"{title} {fallback.PEER}")
    expect(page.locator("#project-menu")).to_be_enabled()
    bound, = fixture.state()["editorViews"]
    assert bound["id"] == f"{fallback.NS}::{fallback.PEER}" and bound["mode"] == "properties"
    editor.get_by_role("button", name="창 닫기", exact=True).click()
    return bound["authorBinding"]


def run():
    fallback.seed()
    register_local_sample()
    with sync_playwright() as playwright:
        expect.set_options(timeout=20000)
        for index in (0, 1):
            fixture.start(index)
            try:
                # Keep Chromium's mappings in the Linux fixture's shared memory.
                with playwright.chromium.launch(executable_path="/usr/bin/chromium",
                                                args=["--no-sandbox", "--disable-gpu"],
                                                ignore_default_args=["--disable-dev-shm-usage"]) as browser:
                    page = fixture.setup(browser)
                    if index == 1:
                        fallback.enter_from_home(page, fallback.FIRST)
                    project = assert_default_view(page, fallback.FIRST, fallback.BEFORE, registered=True)
                    reject_provider_as_mode()
                    binding = check_ordinary_detached_view(page, fallback.FIRST)
                    if index == 0:
                        fixture.checked("Trusted local registration leaves search on the default editor; a pack mode cannot claim an editor slot")
                    else:
                        fallback.enter_from_home(page, fallback.SECOND)
                        assert assert_default_view(page, fallback.SECOND, "19", registered=False) != project
                        assert check_ordinary_detached_view(page, fallback.SECOND) != binding
                        fixture.checked("After host restart, both same-ID projects still use their own built-in editor data")
                    fixture.original()
                    assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
                    fallback.leave_to_home(page)
            finally:
                fixture.stop()


if __name__ == "__main__":
    run()
