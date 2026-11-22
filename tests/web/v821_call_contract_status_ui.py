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
                          "contractHash": wrapper["contractHash"], "source": wrapper["source"], "helpers": ""})
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
                cell.locator("[data-document-fold]").click()
                assert_state(author, LABEL)
                f.checked("Document view surfaces the verified diagnostic on exactly the affected cell even while folded")
                assert_state(open_document(page, B), "참조")
                assert_state(open_document(page, A), LABEL)
                assert checkpoint.read_bytes() == saved
                rename_draft(page, "renamed", "amount")
                _, restored = graph(A)
                assert restored["postCallSignatureMatches"] is True and restored["postCallStale"] is False
                assert_state(open_document(page, A), "참조")
                f.original()
                assert not f.errors and not f.external, (f.errors, f.external)
                f.checked("The same local cell ID in another function stays unaffected; restoring the declaration clears the indicator")
    finally:
        f.save_evidence()
        f.stop()
        print("CALL_IMPACT_FIXTURE", f.root)


if __name__ == "__main__":
    run()
