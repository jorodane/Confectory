"""Read-only, cell-scoped contract diagnostics after a real declaration draft edit."""
import json
import subprocess

from playwright.sync_api import expect, sync_playwright

import v666_workspace_finder_fixture as f
from v821_browser_compound_roundtrip_ui import open_browser

NS = "Example.FrameLoop::"
A = "ImpactCaller"
B = "UnrelatedCaller"
TARGET = "ImpactTarget"
OTHER = "UnrelatedTarget"
CALL = "invoke"
LABEL = "계약 확인 필요"


def metadata(operation, **body):
    command = [f.env["CONFECTORY_DOTNET"],
               str(f.repo / "targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll")]
    answer = json.loads(subprocess.run(command, input=json.dumps({"operation": operation, **body}),
                                     text=True, capture_output=True, env=f.env, check=True).stdout)
    assert answer["ok"], answer
    return answer["result"]


def seed_one(name, target):
    feature, implementation = NS + name, NS + name + "Body"
    native, native_body = NS + target, NS + target + "Body"
    declaration = f"function {feature} (long seed) -> long {{provide {feature} with {implementation};}}"
    target_text = f"function {native} (long amount) -> long {{provide {native} with {native_body};}}"
    feature_graph = metadata("blueprintPrepareFeature", id=feature, text=f"function {feature} (long seed) -> long {{}}",
                             implementation=implementation, graphPath=f"{name}.graph.json",
                             nodePath=f"{name}.node.json")
    defs = metadata("featureBlueprintNodes", featureSource=declaration, graph=feature_graph["graph"])
    record = {"schema": 1, "node": "body", "source": "return seed;",
              "definitionHash": next(row["definitionHash"] for row in defs["nodes"] if row["id"] == "body")}
    with_call = metadata("blueprintPrepareCall", id=implementation, text=feature_graph["implementation"],
                         targetText=target_text, graph=feature_graph["graph"],
                         definition={"id": CALL, "feature": native, "intent": "Existing call", "control": "next"})
    graph = with_call["graph"]
    node = next(row for row in graph["nodes"] if row["id"] == CALL)
    enum = {"primary": "next", "members": [{"id": "next", "name": "NoBranch", "value": 0}]}
    wrapper = metadata("blueprintCallWrapper", functionText=target_text, executionEnum=enum,
                       returnMapping="native-return-out-v1", source="return Result.NoBranch;")
    node.update(control="switch", executionEnum=enum, arguments={"amount": {"input": "seed"}},
                postCall={"mode": "execution-enum", "returnMapping": "native-return-out-v1",
                          "contractHash": wrapper["contractHash"], "source": wrapper["source"],
                          "helpers": "private static long Retained(long value) { return value; }"})
    graph["profile"] = "sync-acyclic-switch-v1"
    graph["entry"] = CALL
    graph["edges"].append({"from": CALL, "port": "next", "to": "body"})
    next(row for row in graph["nodes"] if row["id"] == "body")["arguments"] = {"seed": {"node": CALL}}
    return {
        f"{name}.celem": ("function", declaration),
        f"{name}Body.celem": ("implementation", with_call["implementation"]),
        f"{name}.graph.json": (None, json.dumps(graph)),
        f"{name}.node.json": (None, json.dumps(record)),
        f"{target}.celem": ("function", target_text),
        f"{target}Body.celem": ("implementation", f'implementation {native_body} for {native} (long amount) -> long {{body common "{target}.csbody";}}'),
        f"{target}.csbody": (None, "return 9L;"),
    }


def seed():
    manifest = f.projects[0]
    files = {**seed_one(A, TARGET), **seed_one(B, OTHER)}
    registrations = []
    for filename, (kind, text) in files.items():
        path = manifest.parent / filename
        path.write_text(text + "\n")
        f.before[str(path)] = path.read_bytes()
        if kind:
            registrations.append(f'element {path.stem} {kind} "{filename}";')
    manifest.write_text(manifest.read_text().rstrip()[:-1] + "\n" + "\n".join(registrations) + "\n}\n")
    f.before[str(manifest)] = manifest.read_bytes()


def idle(page):
    expect(page.locator("#title")).to_be_enabled(timeout=60000)


def browse(page, name):
    for key in ("blueprint", "declaration"):
        panel = page.locator(f'.window[data-key="{key}"]')
        if panel.is_visible():
            panel.locator("[data-close]").first.click()
            idle(page)
    browser = page.locator('.window[data-key="browser"]')
    if not browser.is_visible():
        browser = open_browser(page)
    feature = browser.locator('[data-tab="feature"]')
    if "selected" not in (feature.get_attribute("class") or ""):
        feature.click()
    search = browser.get_by_role("button", name="검색 확정")
    expect(search).to_be_enabled()
    query = browser.locator('[data-browser-control="object-query"]')
    query.fill(name)
    query.press("Enter")
    card = browser.locator(f'[data-object="{NS}{name}"]')
    expect(card).to_be_visible()
    expect(search).to_be_enabled()
    return browser, card


def open_document(page, name):
    browser, card = browse(page, name)
    card.press("F2")
    declaration = page.locator('.window[data-key="declaration"]')
    expect(declaration.locator(".object-title-name")).to_have_text(name)
    if browser.is_visible():
        browser.locator("[data-close]").click()
    declaration.locator("[data-function-write-direct]").click()
    author = page.locator('.window[data-key="blueprint"]')
    expect(author.locator(f'[data-document-cell="{CALL}"]')).to_be_visible(timeout=60000)
    return author


def rename_draft(page, old_name, new_name):
    browser, card = browse(page, TARGET)
    card.press("F2")
    declaration = page.locator('.window[data-key="declaration"]')
    expect(declaration.locator(".object-title-name")).to_have_text(TARGET)
    if browser.is_visible():
        browser.locator("[data-close]").click()
    declaration.locator(".object-info-button").click()
    editor = page.get_by_role("dialog", name=TARGET + " 상세보기")
    field = editor.locator("[data-signature-kind=inputs] [data-signature-name]")
    expect(field).to_have_value(old_name)
    field.fill(new_name)
    editor.get_by_role("button", name="저장", exact=True).click()
    expect(editor).to_have_count(0)
    declaration.locator('[data-feature-action="save"]').click()
    idle(page)
    expect(declaration.locator("[data-feature-error]")).to_have_text("")
    expect(declaration.locator("[data-function-pin-name]").first).to_have_text(new_name)


def graph(name):
    graph_id = NS + name + "Body/body:common"
    try:
        result = f.call("blueprint", {"action": "read", "id": graph_id})
    except AssertionError as error:
        raise AssertionError((error.args, f.state().get("logs", [])[-8:])) from error
    assert "nodes" in result, (result.keys(), result.get("error"), result.get("status"), result.get("detail"))
    return result, next(row for row in result["nodes"] if row["id"] == CALL)


def assert_state(author, label):
    cell = author.locator(f'[data-document-cell="{CALL}"]')
    expect(cell.locator(".fd-cell-state")).to_have_text(label)
    expect(author.locator('[data-document-cell="body"] .fd-cell-state')).to_have_text("동작")


def refresh_publication(page, checkpoint, old):
    feature = NS + TARGET
    f.call("select", {"id": feature})
    f.call("inspectDeclaration", {"id": feature})
    declaration = f.state()["declaration"]
    f.call("editMetadata", {"id": feature, "revision": declaration["revision"], "hash": declaration["textHash"],
                            "field": "blueprintPublishedOutputs", "value": '["return"]'})
    f.call("saveDraft", {})
    stored = checkpoint.read_bytes()
    _, stale = graph(A)
    assert stale["postCallStale"] and stale["postCallSignatureMatches"], stale
    receipt = stale["postCallEditor"]["contractHash"]
    assert receipt != old["postCall"]["contractHash"]

    author = open_document(page, A)
    cell = author.locator(f'[data-document-cell="{CALL}"]')
    if not cell.locator(".fd-cell-content").is_visible():
        cell.locator("[data-document-fold]").click()
    assert_state(author, LABEL)
    button = cell.locator("[data-document-call-refresh]")
    expect(button).to_be_enabled()
    button.click()
    expect(button).to_have_count(0)
    assert_state(author, "참조")
    assert graph(A)[1]["postCall"] == old["postCall"] and checkpoint.read_bytes() == stored
    f.original()
    document = author.locator(".function-document")
    document.press("Control+z")
    assert_state(author, LABEL)
    expect(button).to_be_enabled()
    document.press("Control+y")
    assert_state(author, "참조")
    author.locator("[data-bp-save]").click()
    expect(author.locator(".bp-status")).to_have_text("저장됨", timeout=120000)
    saved, call = graph(A)
    assert not call["postCallStale"]
    assert saved["edges"] == old["edges"] and call["arguments"] == old["arguments"]
    assert call["postCall"] == {**old["postCall"], "contractHash": receipt}
    assert graph(B)[1]["postCallStale"] is False
    f.original()
    f.checked("Logic Code explicitly renews a same-signature publication receipt, preserving source, helpers and wiring through Undo/Redo and Save")


def run():
    seed()
    try:
        f.start(0)
        with sync_playwright() as driver:
            with driver.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox", "--disable-gpu"]) as browser:
                expect.set_options(timeout=20000)
                page = f.setup(browser)
                page.set_viewport_size({"width": 1500, "height": 1050})
                assert_state(open_document(page, A), "참조")
                before, original_call = graph(A)
                assert original_call["postCallSignatureMatches"] is True and original_call["postCallStale"] is False
                rename_draft(page, "amount", "renamed")
                checkpoint, = f.projects[0].parent.glob(".confectory/edit-workspaces/*/draft.json")
                saved = checkpoint.read_bytes()
                drafts = json.loads(saved)["changes"]
                assert [row["id"] for row in drafts] == [NS + TARGET], drafts
                assert "long renamed" in drafts[0]["draft"]

                updated, call = graph(A)
                _, unrelated = graph(B)
                assert call["postCallSignatureMatches"] is False and call["postCallStale"] is True, call
                assert unrelated["postCallSignatureMatches"] is True and unrelated["postCallStale"] is False
                assert call["calledFeature"] == NS + TARGET and unrelated["calledFeature"] == NS + OTHER
                assert updated["edges"] == before["edges"] and call["arguments"] == original_call["arguments"]
                args = call["currentCallSignature"]["args"]
                assert args[0]["name"] == "renamed"
                (f.root / "observed-calls.json").write_text(json.dumps(
                    {"changed": call, "unrelated": unrelated}, ensure_ascii=False, indent=2))
                f.original()
                f.checked("Existing declaration Save changes only the draft; engine detects the specific stale call and preserves its links")
                author = open_document(page, A)
                assert_state(author, LABEL)
                cell = author.locator(f'[data-document-cell="{CALL}"]')
                compare = cell.get_by_role('button', name='계약 차이 보기')
                expect(cell.locator('[data-document-call-refresh]')).to_have_count(0)
                compare.click()
                preview = page.get_by_role('dialog', name='원본 계약 비교')
                expect(preview.locator('[data-call-contract-before]')).to_have_text('(long amount) → long')
                expect(preview.locator('[data-call-contract-after]')).to_have_text('(long renamed) → long')
                expect(preview.locator('[data-call-contract-bound]')).to_have_text('확인이 필요한 기존 입력 연결 · amount')
                page.keyboard.press('Escape')
                expect(compare).to_be_focused()

                author.get_by_role('tab', name='블루프린트 보기', exact=True).click()
                author.locator(f'[data-bp-overview-node="{CALL}"]').click()
                author.locator(f'[data-bp-node="{CALL}"] [data-wrapper-refresh]').click()
                remap = page.get_by_role('dialog', name='호출 계약 갱신')
                expect(remap.locator('[data-abi-input="renamed"]')).to_have_value('')
                remap.locator('[data-abi-remap-accept]').click()
                expect(remap.locator('[data-abi-error]')).to_be_visible()
                assert graph(A)[1]['arguments'] == original_call['arguments']
                assert graph(A)[0]['edges'] == before['edges'] and checkpoint.read_bytes() == saved
                remap.locator('[data-abi-remap-cancel]').click()
                author.get_by_role('tab', name='논리 코드', exact=True).click()
                f.checked('The comparison exposes the bound old input; the existing remap refuses an unselected new input without changing wiring or checkpoint')
                cell.locator("[data-document-fold]").click()
                assert_state(author, LABEL)
                f.checked("Document view surfaces the verified diagnostic on exactly the affected cell even while folded")
                other = open_document(page, B)
                assert_state(other, "참조")
                expect(other.locator('[data-document-call-compare]')).to_have_count(0)
                assert_state(open_document(page, A), LABEL)
                assert checkpoint.read_bytes() == saved
                rename_draft(page, "renamed", "amount")
                restored_graph, restored = graph(A)
                assert restored["postCallSignatureMatches"] is True and restored["postCallStale"] is False
                assert_state(open_document(page, A), "참조")
                f.original()
                assert not f.errors and not f.external, (f.errors, f.external)
                f.checked("The same local cell ID in another function stays unaffected; restoring the declaration clears the indicator")
                refresh_publication(page, checkpoint, {**restored, "edges": restored_graph["edges"]})
    finally:
        f.save_evidence()
        f.stop()
        print("CALL_IMPACT_FIXTURE", f.root)


if __name__ == "__main__":
    run()
