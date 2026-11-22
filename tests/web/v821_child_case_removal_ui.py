"""Real Linux editor for scoped, reversible removal in an owned child case."""
import ast
import hashlib
import sys
import uuid
from pathlib import Path

scenario = sys.argv[3] if len(sys.argv) > 3 else "normal"
assert scenario in {"normal", "shared", "mixed"}
fixture = Path(__file__).with_name("v821_child_case_order_ui.py")
nodes = ast.parse(fixture.read_text()).body
argv = sys.argv
sys.argv = [*argv[:3], "normal" if scenario == "mixed" else scenario]
try:
    exec(compile(ast.Module(body=nodes[:next(i for i, node in enumerate(nodes) if isinstance(node, ast.Try))],
                            type_ignores=[]), str(fixture), "exec"), globals())
finally:
    sys.argv = argv

selected_name = "tail"
leaf = f.project / "Pair.tail.node.json"
peer_file = f.project / peer["implementation"]
peer_frame = root["nodes"][1]["graph"]
peer["id"] = selected_name
peer_frame["entry"] = selected_name
peer_frame["edges"][0]["from"] = selected_name
tail["signature"]["args"] = []
tail["arguments"] = {}

definitions = f.metadata(
    "blueprintDescribeOwned", project=str(f.manifest), id=f.n + "PairBody",
    text=(f.project / "PairBody.celem").read_text(), bodyTarget="common", graph=root, definitionsOnly=True,
)
assert definitions["state"] == "node-definitions", definitions
hashes = {node["id"]: node["definitionHash"] for node in definitions["nestedNodes"]}
for path, filename, source in [
    ("body/tail", leaf, 'global::System.Console.WriteLine("tail:7");'),
    ("peer/tail", peer_file, 'global::System.Console.WriteLine("peer");'),
]:
    filename.write_text(json.dumps(dict(schema=1, node=selected_name, definitionHash=hashes[path], source=source)))
graph_path.write_text(json.dumps(root, ensure_ascii=False))


def legacy_example(name, compound):
    feature, impl = f.n + name, f.n + name + "Body"
    graph_name = name + ".graph.json"
    kept, dropped = code("kept"), code("dropped")
    for node in (kept, dropped):
        node["implementation"] = f'{name}.{node["id"]}.node.json'
    prepared = f.metadata("blueprintPrepareFeature", id=feature, text=f"function {feature} () -> void {{}}",
                          implementation=impl, graphPath=graph_name, nodePath=kept["implementation"])
    graph = prepared["graph"]
    initial_drop = dropped
    if compound:
        initial_drop = dict(id="group", kind="graph", control="next", intent="group",
                            signature={"args": [], "return": "void"}, arguments={},
                            graph=dict(schema=1, profile="sync-acyclic-nested-v1", entry="dropped",
                                       nodes=[dropped], edges=[edge("dropped", "exit:return")],
                                       exits={"return": None}))
        graph["profile"] = "sync-acyclic-nested-v1"
    removal = initial_drop["id"]
    graph.update(entry="kept", nodes=[kept, initial_drop],
                 edges=[edge("kept", removal), edge(removal, "exit:return")], exits={"return": None})
    (f.project / (name + ".celem")).write_text(prepared["function"])
    (f.project / (name + "Body.celem")).write_text(prepared["implementation"])
    (f.project / graph_name).write_text(json.dumps(graph))
    manifest = f.manifest.read_text()
    entries = f'element {name} function "{name}.celem";element {name}Body implementation "{name}Body.celem";'
    f.manifest.write_text(manifest.replace("{", "{" + entries, 1))
    definitions = f.metadata("blueprintDescribeOwned", project=str(f.manifest), id=impl,
                             text=prepared["implementation"], bodyTarget="common", graph=graph, definitionsOnly=True)
    hashes = {node["id"]: node["definitionHash"] for node in definitions["nodes"] + definitions.get("nestedNodes", [])}
    for node, path in ((kept, "kept"), (dropped, "group/dropped" if compound else "dropped")):
        (f.project / node["implementation"]).write_text(json.dumps(
            dict(schema=1, node=node["id"], definitionHash=hashes[path], source="return;")))
    return feature, impl + "/body:common", removal


legacy = [legacy_example("LegacyLeaf", False), legacy_example("LegacyGroup", True)] if scenario == "mixed" else []
if legacy:
    main_implementation = f.project / "MainBody.celem"
    imports = "".join(f'import {feature} as {feature.split("::")[-1]} () -> void;' for feature, _, _ in legacy)
    main_implementation.write_text(main_implementation.read_text().replace("{", "{" + imports, 1))
    calls_legacy = "".join(f'calls.{feature.split("::")[-1]}.Invoke();' for feature, _, _ in legacy)
    main.write_text(calls_legacy + main.read_text())
x.physical = {path: path.read_bytes() for path in f.project.iterdir() if path.is_file()}
original_graph = graph_path.read_bytes()
deleted = copy.deepcopy(root)
scope = deleted["nodes"][0]["graph"]
scope["nodes"] = [node for node in scope["nodes"] if node["id"] != selected_name]
scope["edges"] = [route for route in scope["edges"] if route["from"] != selected_name]
next(route for route in scope["edges"] if route["to"] == selected_name)["to"] = "return:choose"


def disk_unchanged(except_graph=False):
    assert all(path.read_bytes() == raw for path, raw in x.physical.items()
               if not except_graph or path != graph_path)


def history(direction="undo"):
    return f.invoke("draftHistory", dict(action="inspect"))["result"]["result"][direction]


def change_history(direction, present):
    step = history(direction)
    assert step["available"] and step["kind"] == "cell-removal"
    assert step["frame"] == "body" and [unit["id"] for unit in step["units"]] == [t.graph]
    local_undo(direction == "redo")
    f.idle()
    order(initial if present else ["positive"])
    assert read()["edges"] == (root if present else deleted)["nodes"][0]["graph"]["edges"]
    assert read(other)["nodes"] == sibling_before


def confirm():
    window = review()
    window.locator("#confirm").click()
    expect(window).to_be_hidden(timeout=120000)
    f.idle()


def reject_stale_restore():
    window = review()
    raw = peer_file.read_bytes()
    mark = len(f.traffic)
    peer_file.write_bytes(raw + b" ")
    try:
        snapshot = checkpoint.read_bytes()
        window.locator("#confirm").click()
        f.idle()
        requests = {row["invoke"]["requestId"] for row in f.traffic[mark:]
                    if row.get("invoke", {}).get("endpoint") == "confirmGroup"}
        replies = [row["result"] for row in f.traffic[mark:]
                   if row.get("result", {}).get("requestId") in requests]
        assert any(reply.get("ok") and reply.get("result", {}).get("sourceConfirmed") is False
                   for reply in replies), replies
        assert checkpoint.read_bytes() == snapshot
        assert json.loads(graph_path.read_bytes()) == deleted and peer_file.read_bytes() == raw + b" "
        order(initial)
    finally:
        peer_file.write_bytes(raw)
    if window.is_visible():
        window.locator("[data-reject]").click()


def refused_request(binding):
    datum = read()
    return dict(action="authorBatch", id=frame, attempt=uuid.uuid4().hex, documentFrame=binding,
                sourceProof=x.proof(datum), checkpointHash=datum["checkpointHash"],
                edits=[dict(action="removeDocumentCell", node=selected_name)])


def confirm_legacy(feature, graph, cell):
    f.invoke("select", dict(id=feature))
    datum = read(graph)
    assert cell in datum["documentRemovableCells"]
    f.invoke("blueprint", dict(action="authorBatch", id=graph, attempt=uuid.uuid4().hex,
                              sourceProof=x.proof(datum), checkpointHash=datum["checkpointHash"],
                              edits=[dict(action="removeDocumentCell", node=cell)]))
    ids = [graph]
    f.invoke("reviewGroup", dict(ids=ids, target="linux"))
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        state = f.state().get("review") or {}
        if state.get("status") == "ready" and state.get("token"):
            break
        time.sleep(0.1)
    else:
        raise AssertionError((feature, state.get("status"), state.get("issues")))
    confirmed = f.invoke("confirmGroup", dict(ids=ids, token=state["token"]))
    assert confirmed["result"]["result"]["sourceConfirmed"], (feature, confirmed["state"].get("status"))


try:
    original_output = "\n".join("tail:7" if line.startswith("tail:") else line for line in output().splitlines())
    x.build("before-case-removal", 14, original_output)
    f.start(0)
    for previous in legacy:
        confirm_legacy(*previous)
    if legacy:
        x.physical = {path: path.read_bytes() for path in x.physical}
    f.invoke("select", dict(id=t.feature))
    f.invoke("saveDraft", {})
    checkpoint = next(f.project.glob(".confectory/edit-workspaces/*/draft.json"))
    before = checkpoint.read_bytes()
    baseline = read()
    sibling_before = read(other)["nodes"]
    with sync_playwright() as pw:
        expect.set_options(timeout=45000)
        f.browser = pw.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
        f.page = f.setup()
        f.page.set_viewport_size(dict(width=1800, height=1400))
        open_document()
        enter_body()
        case_panel = order(initial)
        button = case_panel.locator(f'[data-document-remove="{selected_name}"]')
        if scenario == "shared":
            expect(button).to_have_count(0)
            assert not baseline.get("documentFrameCaseOrderBinding") and not baseline["documentRemovableCells"]
            assert checkpoint.read_bytes() == before
            disk_unchanged()
            f.checked("shared explicit case entry disables deletion in the actual editor")
        else:
            assert baseline["documentRemovableCells"] == [selected_name]
            expect(button).to_be_visible()
            remaining = copy.deepcopy(deleted)
            lone = next(node for node in remaining["nodes"][0]["graph"]["nodes"] if node["id"] == "positive")
            lone["signature"]["args"] = []
            lone["arguments"] = {}
            options = f.metadata("blueprintCellRemovalHistory", action="options", graph=remaining, path="body")
            assert "positive" not in options["nodes"]
            wrong = copy.deepcopy(baseline["documentFrameCaseOrderBinding"])
            wrong["path"] = "peer"
            f.invoke("blueprint", refused_request(wrong), False)
            assert checkpoint.read_bytes() == before
            button.click()
            order(["positive"])
            held = pending()
            assert len(held) == 1
            peer_bytes = peer_file.read_bytes()
            peer_file.write_bytes(peer_bytes + b" ")
            try:
                save()
                assert checkpoint.read_bytes() == before and retained(held)
                assert graph_path.read_bytes() == original_graph and peer_file.read_bytes() == peer_bytes + b" "
            finally:
                peer_file.write_bytes(peer_bytes)
            save()
            assert not pending()
            saved = json.loads(checkpoint.read_bytes())
            profile = "retained-blueprint-cell-group-v1" if legacy else "retained-blueprint-cell-v1"
            assert saved["version"] == 3 and saved["cellHistoryProfile"] == profile
            assert [entry["cellRemoval"]["version"] for entry in saved["history"]["undo"]] == (
                [1, 2, 3] if legacy else [3])
            item = saved["history"]["undo"][-1]
            receipt = item["cellRemoval"]
            assert receipt["version"] == 3 and receipt["node"] == "body/tail"
            assert receipt["source"] == leaf.name
            for original in (leaf, peer_file, f.project / "Pair.negativeTail.node.json"):
                assert receipt["proof"][original.name] == hashlib.sha256(original.read_bytes()).hexdigest()
            assert [unit["id"] for unit in saved["changes"]] == [t.graph]
            disk_unchanged()

            restart_child(1)
            order(["positive"])
            assert not read()["documentRemovableCells"]
            panel().locator(".bp-breadcrumbs button").first.click()
            f.idle()
            peer_tab = doc().locator('[data-document-internal="peer"]')
            if not peer_tab.is_visible():
                doc().locator('[data-document-fold="peer"][aria-expanded=false]').click()
            peer_tab.click()
            f.idle()
            local_undo()
            assert history()["id"] == item["id"] and read(other)["nodes"] == sibling_before
            panel().locator(".bp-breadcrumbs button").first.click()
            f.idle()
            enter_body()
            change_history("undo", True)
            change_history("redo", False)
            disk_unchanged()
            f.checked("Save and cold Undo/Redo change only the selected case; same-ID sibling cannot invoke its Undo or lose its original source")
            if legacy:
                reloaded = json.loads(checkpoint.read_bytes())
                for previous, current in zip(saved["history"]["undo"][:2], reloaded["history"]["undo"][:2], strict=True):
                    assert current == previous
                f.checked("the same cold checkpoint retains exact version 1 and 2 receipts beside the new version 3 receipt")

            panel().locator("[data-bp-save]").click()
            f.idle()
            confirm()
            assert json.loads(graph_path.read_bytes()) == deleted
            disk_unchanged(except_graph=True)
            lines = original_output.splitlines()
            lines.remove("tail:7")
            x.build("confirmed-case-removal", 14, "\n".join(lines))

            for i, changed_file in enumerate((peer_file, leaf)):
                raw = changed_file.read_bytes()
                changed = json.loads(raw)
                changed["source"] += "\n// actual sibling or retained source update"
                changed_file.write_text(json.dumps(changed))
                try:
                    restart_child(10 + i)
                    snapshot = checkpoint.read_bytes()
                    before_history = f.invoke("draftHistory", dict(action="inspect"))["result"]["result"]
                    assert before_history["undo"]["code"] == "SOURCE_CHANGED" and not before_history["undo"]["available"]
                    local_undo()
                    f.idle()
                    order(["positive"])
                    after_history = f.invoke("draftHistory", dict(action="inspect"))["result"]["result"]
                    assert all(after_history[key] == before_history[key] for key in ("revision", "undoCount", "redoCount"))
                    assert checkpoint.read_bytes() == snapshot and json.loads(graph_path.read_bytes()) == deleted
                    assert json.loads(changed_file.read_text()) == changed and not pending()
                finally:
                    changed_file.write_bytes(raw)
            f.checked("a changed sibling or retained C# source blocks cold Undo without advancing history or overwriting files")

            restart_child(2)
            change_history("undo", True)
            assert json.loads(graph_path.read_bytes()) == deleted
            assert all(path.read_bytes() == raw for path, raw in x.physical.items() if path != graph_path)
            panel().locator("[data-bp-save]").click()
            f.idle()
            restart_child(3)
            order(initial)
            assert json.loads(graph_path.read_bytes()) == deleted
            reject_stale_restore()
            confirm()
            assert graph_path.read_bytes() == original_graph
            disk_unchanged()
            x.build("confirmed-case-restoration", 14, original_output)
            f.checked("confirmed Undo is only a restoration draft; Confirm rejects a stale sibling after Review, then preserves original execution after separate confirmation")

        f.page.screenshot(path=str(f.case / f"child-case-removal-{scenario}.png"), full_page=True)
        assert not f.errors and not f.external, (f.errors, f.external)
        f.browser.close()
finally:
    (f.case / "child-case-removal-traffic.json").write_text(json.dumps(f.traffic, ensure_ascii=False))
    print("V821_CHILD_CASE_REMOVAL", scenario, f.case, flush=True)
    f.stop()
