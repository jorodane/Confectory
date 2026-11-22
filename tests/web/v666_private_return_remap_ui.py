"""Explicit private return retarget through the real Linux Blueprint editor."""
import copy
import json
import os
from pathlib import Path
import subprocess
import uuid

from playwright.sync_api import expect, sync_playwright

import v666_private_node_out_double_fixture as fixture

f = fixture.f
frame = fixture.whole_graph + "/graph:inner"
sink_path = f.project / "private-out-void-sink.node.json"
sink_record = json.loads(sink_path.read_text())
sink_record["source"] = 'global::System.Console.WriteLine("consumer:"+value);'
sink_path.write_text(json.dumps(sink_record))
originals = {
    path: path.read_bytes() for path in f.project.rglob("*")
    if path.is_file() and ".confectory" not in path.relative_to(f.project).parts
}
source = fixture.sources[fixture.whole_function]
authored = source.replace("return Keep(firstNative+secondNative);", "return Keep(firstNative+secondNative)+0D;")


def untouched():
    assert all(path.read_bytes() == data for path, data in originals.items())


def read():
    return f.invoke("blueprint", {"action": "read", "id": frame})["result"]["result"]


def build(name, expected_consumer, expected_return):
    compilation = subprocess.run(
        [f.env["CONFECTORY_DOTNET"], str(f.repo / "src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll"),
         "build", str(f.manifest), "portable"],
        env=f.env, text=True, capture_output=True, check=True,
    )
    result = subprocess.run(json.loads(compilation.stdout)["run"], env=f.env, text=True, capture_output=True)
    (f.case / (name + ".json")).write_text(json.dumps({"stdout": result.stdout, "stderr": result.stderr}))
    assert result.returncode == 104, result
    assert result.stdout.splitlines() == [f"consumer:{expected_consumer}", "104"], result.stdout
    assert result.stderr.strip() == f"private-out-return:{expected_return}", result.stderr


def open_graph():
    f.idle()
    if not f.author().is_visible():
        f.page.locator("#workspace").click(button="right", position={"x": 1300, "y": 300})
        f.page.get_by_role("button", name="프로젝트 브라우저", exact=True).click()
        browser = f.page.locator('.window[data-key^="browser:project:"]')
        browser.get_by_role("button", name="기능", exact=True).click()
        browser.locator("[data-browser-control=object-query]").fill(fixture.whole_function.split("::")[-1])
        browser.locator("[data-browser-control=object-search]").click()
        browser.locator(f'[data-object="{fixture.whole_function}"]').press("Enter")
        browser.locator("[data-close]").first.click()
        f.idle()
        f.page.locator("[data-operation=feature-author-open]").first.click()
    panel = f.author()
    blueprint_tab = panel.get_by_role("tab", name="블루프린트 보기", exact=True)
    expect(blueprint_tab).to_be_visible()
    if not panel.locator(".bp-breadcrumbs").count():
        panel.get_by_role("tab", name="논리 코드", exact=True).click()
        document = panel.locator(".function-document")
        expect(document.locator('[data-document-cell="inner"]')).to_be_visible()
        button = document.locator('[data-document-internal="inner"]')
        if not button.is_visible():
            document.locator('[data-document-fold="inner"][aria-expanded=false]').click()
        button.click()
        f.idle()
    blueprint_tab.click()
    expect(panel.locator('[data-bp-node="body"]')).to_be_visible()
    return panel


def map_output(panel):
    panel.locator('[data-bp-node="body"] .bp-pin-plug[data-side=out][data-port="field:return"]')         .locator(".bp-pin-value").click(button="right")
    f.page.get_by_role("dialog", name="속성 타입 선택", exact=True).locator("[data-type=double]").click()
    dialog = f.page.get_by_role("dialog", name="반환 연결 갱신", exact=True)
    expect(dialog).to_be_visible()
    expect(dialog.locator('[data-abi-output="return"]')).to_have_value("")
    return dialog


def review_in_editor(panel):
    panel.locator("[data-bp-complete]").click()
    f.idle()
    f.page.locator('.window[data-key="review"]:visible,.window[data-key="targets"]:visible').first.wait_for(timeout=90000)
    targets = f.page.locator('.window[data-key="targets"]')
    if targets.is_visible():
        targets.locator("[data-target-choice]").select_option("portable")
        targets.locator("[data-close]").click()
        panel.locator("[data-bp-complete]").click()
        f.idle()
    review = f.page.locator('.window[data-key="review"]')
    expect(review).to_be_visible()
    if review.locator("[data-review-advanced]").is_visible():
        review.locator("[data-review-advanced]").click()
    if review.locator("[data-advanced-reviewed]").count():
        review.locator("[data-advanced-reviewed]").check()
    expect(review.locator("#confirm")).to_be_enabled()
    return review


try:
    build("before", 129, "long")
    f.start(0)
    f.invoke("select", {"id": fixture.whole_function})
    f.invoke("saveDraft", {})
    checkpoint = next(f.project.glob(".confectory/edit-workspaces/*/draft.json"))
    baseline = checkpoint.read_bytes()
    initial = read()
    expected_choice = {"consumer": "sink", "argument": "value", "output": "secondNative"}
    assert initial["privateReturnChoices"] == {"body": expected_choice}
    parameter_plan = {"args": fixture.code_signature["args"], "returnType": "double",
                      "remap": {arg["name"]: arg["name"] for arg in fixture.code_signature["args"]}}
    edits = [
        {"action": "argument", "node": "sink", "name": "value", "valueJson": '{"node":"body","output":"return"}'},
        {"action": "parameters", "node": "body", "definition": parameter_plan},
        {"action": "source", "node": "body", "text": authored},
    ]
    proof = json.dumps([[row["id"], row["revision"], row["hash"]] for row in initial["sources"]])
    for rejected in (edits, edits[1:]):
        f.invoke("blueprint", {"action": "authorBatch", "id": frame, "attempt": uuid.uuid4().hex,
                 "checkpointHash": initial["checkpointHash"], "sourceProof": proof, "edits": rejected}, False)
        assert checkpoint.read_bytes() == baseline
        untouched()
    with_another_use = copy.deepcopy(json.loads(originals[f.project / fixture.graph_path]))
    child = next(node["graph"] for node in with_another_use["nodes"] if node["id"] == "inner")
    child["exits"]["return"] = {"node": "body"}
    assert not f.metadata("blueprintPrivateReturnChoices", graph=with_another_use, path="inner")
    f.checked("Wrong and missing selections fail closed; a second return use prevents eligibility.")

    with sync_playwright() as playwright:
        expect.set_options(timeout=60000)
        f.browser = playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
        f.page = f.setup()
        f.page.set_viewport_size({"width": 2200, "height": 1500})
        panel = open_graph()
        dialog = map_output(panel)
        dialog.locator("[data-abi-remap-accept]").click()
        expect(dialog.locator("[data-abi-error]")).to_be_visible()
        dialog.locator('[data-abi-output="return"]').select_option("secondNative")
        dialog.locator("[data-abi-remap-cancel]").click()
        assert not f.pending()["blueprint"] and checkpoint.read_bytes() == baseline
        untouched()
        f.checked("Unmapped return is blocked and Cancel retains the original candidate and sources.")

        dialog = map_output(panel)
        dialog.locator('[data-abi-output="return"]').select_option("secondNative")
        dialog.locator("[data-abi-remap-accept]").click()
        expect(dialog).to_have_count(0)
        panel.locator('[data-bp-node="body"] [data-internal-code]').click()
        editor = f.page.locator('[role=dialog]:has([data-code-source])')
        field = editor.locator("[data-code-source]")
        assert field.input_value().startswith("public static double Execute(")
        field.evaluate("(element, text)=>{const start=element.value.indexOf(text);if(start<0)throw Error('missing original source');element.focus();element.setSelectionRange(start,start+text.length);}", source.rstrip())
        f.page.keyboard.insert_text(authored.rstrip())
        editor.locator("[data-code-save]").click()

        inputs = f.pending()["blueprint"]
        mark = len(f.traffic)
        panel.locator("[data-bp-save]").click()
        f.idle()
        assert not [row for row in f.pending()["blueprint"] if row[1].get("type") in ("argument:value", "parameters", "source")]
        actions = [row["invoke"]["input"] for row in f.traffic[mark:] if row.get("invoke", {}).get("endpoint") == "blueprint"]
        save = [row for row in actions if row["action"] == "authorBatch"]
        assert len(save) == 1 and [edit["action"] for edit in save[0]["edits"]] == ["argument", "parameters", "source"]
        assert not any(row["action"] in ("argument", "parameters", "source") for row in actions)
        assert inputs
        untouched()
        f.page.unroute_all(behavior="wait")
        f.page.close()
        f.browser.close()
    f.stop()

    text = json.loads(checkpoint.read_text())
    assert text["version"] == 1
    graph_unit = next(row for row in text["changes"] if row["id"] == fixture.whole_graph)
    candidate = json.loads(graph_unit["draft"])
    expected = json.loads(originals[f.project / fixture.graph_path])
    child = next(node["graph"] for node in expected["nodes"] if node["id"] == "inner")
    child["nodes"][0]["signature"]["return"] = "double"
    child["nodes"][1]["arguments"]["value"]["output"] = "secondNative"
    assert candidate == expected
    assert graph_unit["propertyObservations"]["version"] == 1
    assert set(graph_unit["propertyObservations"]["sources"]) == set(initial["privateReturnSources"])
    f.checked("One ordinary version-1 checkpoint records exactly the ABI, qualified consumer and C# source change.")

    f.start(1)
    restored = read()
    assert json.loads(restored["nodes"][1]["arguments"][0]["valueJson"]) == {"node": "body", "output": "secondNative"}
    assert restored["nodes"][0]["signature"]["return"] == "double"
    assert restored["nodes"][0]["source"] == authored
    ids = restored["reviewIds"]
    assert {fixture.whole_graph, fixture.whole_node} <= set(ids)
    f.invoke("reviewGroup", {"ids": ids, "target": "portable"})
    review = f.state()["review"]
    assert review["status"] == "ready", review
    peer = f.project / fixture.extra_path
    saved = checkpoint.read_bytes()
    assert peer.read_bytes() == originals[peer]
    stamp = peer.stat()
    peer.write_bytes(originals[peer] + b"\n")
    try:
        refusal = f.invoke("confirmGroup", {"ids": ids, "token": review["token"]})["result"]["result"]
        assert refusal["sourceConfirmed"] is False
        assert checkpoint.read_bytes() == saved
        assert peer.read_bytes() == originals[peer] + b"\n"
        assert all(path == peer or path.read_bytes() == data for path, data in originals.items())
    finally:
        peer.write_bytes(originals[peer])
        os.utime(peer, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    f.stop()
    f.checked("A sibling source change after Review blocks Confirm and preserves the whole checkpoint and source bytes.")

    previous = os.environ.get("REMAP_PREVIOUS")
    if previous:
        previous = Path(previous)
        current_repo, current_report = f.repo, f.report
        editor_repo = f.env["CONFECTORY_EDITOR_REPO"]
        try:
            f.repo = previous / "checkout"
            f.report = json.loads((previous / "report.json").read_text())
            f.env["CONFECTORY_EDITOR_REPO"] = str(f.repo)
            f.start(2)
            backward = read()
            assert "privateReturnChoices" not in backward
            assert backward["nodes"][0]["signature"]["return"] == "double"
            assert backward["nodes"][1]["arguments"] == restored["nodes"][1]["arguments"]
            f.invoke("reviewGroup", {"ids": backward["reviewIds"], "target": "portable"})
            assert f.state()["review"]["status"] == "ready"
            untouched()
        finally:
            f.stop()
            f.repo, f.report = current_repo, current_report
            f.env["CONFECTORY_EDITOR_REPO"] = editor_repo
        f.checked("The unmodified baseline engine cold-restores and reviews the current pending checkpoint.")

    f.start(3)
    with sync_playwright() as playwright:
        f.browser = playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
        f.page = f.setup()
        f.page.set_viewport_size({"width": 2200, "height": 1500})
        panel = open_graph()
        review = review_in_editor(panel)
        reviewed = checkpoint.read_bytes()
        def pending_sources(raw):
            changes = json.loads(raw)["changes"]
            return {row["id"]: (row["path"], row["baseline"], row["draft"]) for row in changes}
        assert pending_sources(reviewed) == pending_sources(saved)
        review.locator("[data-reject]").click()
        expect(review).to_be_hidden()
        untouched()
        assert checkpoint.read_bytes() == reviewed
        review = review_in_editor(panel)
        review.locator("#confirm").click()
        expect(review).to_be_hidden(timeout=120000)
        f.idle()
        assert read()["nodes"][0]["signature"]["return"] == "double"
        f.page.unroute_all(behavior="wait")
        f.page.close()
        f.browser.close()
    f.stop()
    assert json.loads((f.project / fixture.graph_path).read_text()) == expected
    record = json.loads((f.project / fixture.node_path).read_text())
    assert record["source"] == authored
    assert record["helpers"] == json.loads(originals[f.project / fixture.node_path])["helpers"]
    for path, data in originals.items():
        if path.name not in (fixture.graph_path, fixture.node_path):
            assert path.read_bytes() == data, path
    build("after", 99, "double")
    assert not f.errors and not f.external, (f.errors, f.external)
    f.checked("Cold Review and Confirm preserve siblings and old out. Actual execution routes the consumer from 129 to out=99.")
finally:
    print("Evidence:", f.case)
    f.stop()
