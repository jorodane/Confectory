"""Real Linux UI for saved and confirmed cell removal and checked shared Undo."""

import ast
import copy
import hashlib
import json
import stat
import sys
import time
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

import v666_node_names_recovery_fixture as t

f, x = t.f, t.x
mode = sys.argv[3] if len(sys.argv) > 3 else "normal"
assert mode in {"normal", "readonly", "shared", "value", "case", "case-empty", "case-exit",
                "case-shared", "case-implicit", "case-readonly", "case-value", "child-first", "child-last", "child-readonly",
                "compound", "compound-readonly", "compound-views", "compound-deep-guard"}
case = mode.startswith("case")
child_case = mode.startswith("child")
compound_case = mode.startswith("compound")
frame_path = "other" if mode == "child-first" else "body"
sibling_path = "body" if frame_path == "other" else "other"
positive_modes = {"normal", "case", "case-empty", "case-exit", "child-first", "child-last", "compound", "compound-views"}
helper = Path(__file__).with_name("v821_function_document_ui.py")
functions = [node for node in ast.parse(helper.read_text()).body if isinstance(node, ast.FunctionDef)]
exec(compile(ast.Module(body=functions, type_ignores=[]), str(helper), "exec"), globals())

graph = f.project / t.graph_file
cell_id = "other" if compound_case else {"case": "move", "case-exit": "right", "child-first": "inner",
           "child-last": "tail", "child-readonly": "tail"}.get(mode, "left" if case else "after")
source_name = "Pair.other.inner.node.json" if compound_case else (
    f"Pair.{frame_path}.{cell_id}.node.json" if child_case else f"Pair.{cell_id}.node.json")
retained_sources = {f"{t.graph}/node:other/node:{name}": f"Pair.other.{name}.node.json"
                    for name in ("inner", "tail")} if compound_case else {}
sibling_sources = {f"{t.graph}/node:body/node:{name}": f"Pair.body.{name}.node.json"
                   for name in ("inner", "tail")} if compound_case else {}
if mode == "compound-views":
    sibling_sources = {f"{t.graph}/node:body/node:nest/node:{name}": f"Pair.body.{name}.node.json"
                       for name in ("inner", "tail")}
leaf = f.project / source_name
case_port = "case:negative" if mode == "case-exit" else "case:positive"


def order():
    return doc().locator("[data-document-cell]").evaluate_all("(rows)=>rows.map(row=>row.dataset.documentCell)")


def expect_case_order(port, cells):
    tab = doc().locator(f'[data-document-branch="{port}"][data-document-owner=choose]')
    if tab.get_attribute("aria-pressed") != "true":
        tab.click()
    branch = doc().locator(f'[data-document-panel="{port}"]')
    expect(branch).to_be_visible()
    expect(branch.locator("[data-document-branch-add]")).to_be_visible()
    actions = branch.locator(':scope > [data-document-cell]:not([data-document-cell^="$"])')
    expect(actions).to_have_count(len(cells))
    assert actions.evaluate_all("(rows)=>rows.map(row=>row.dataset.documentCell)") == cells


def read_graph(frame=frame_path):
    if not child_case:
        return t.read()
    return f.invoke("blueprint", {"action": "read", "id": f"{t.graph}/graph:{frame}"})["result"]["result"]


def select_frame(frame):
    if panel().locator(".bp-breadcrumbs").count():
        panel().locator(".bp-breadcrumbs button").first.click()
        f.idle()
    doc().locator(f"[data-document-internal={frame}]").click()
    f.idle()
    expect(panel().locator(".bp-breadcrumbs")).to_be_visible()


def press_history_shortcut(direction):
    doc().locator(".fd-document-title").click()
    doc().press("Control+z" if direction == "undo" else "Control+y")
    f.idle()


def expect_cell(present):
    expect(doc().locator(f"[data-document-cell={cell_id}]")).to_have_count(int(present))
    if case:
        cells = original_case if present else [cell for cell in original_case if cell != cell_id]
        expect_case_order(case_port, cells)
    elif compound_case:
        cells = ["$entry", "body", *(["other"] if present else []), "after", "$exit:return"]
        assert order() == cells, order()
    elif child_case:
        selected_nodes = ["inner", "tail"] if present else [node for node in ["inner", "tail"] if node != cell_id]
        exit_cell = ["$exit:return"] if frame_path == "body" else []
        assert order() == ["$entry", *selected_nodes, *exit_cell], order()
        if not present:
            expect(doc().locator("[data-document-remove]")).to_have_count(0)
    else:
        assert order() == (["$entry", "body", "after", "$exit:return"] if present else ["$entry", "body", "$exit:return"])


def assert_compound_sources(present):
    if not compound_case:
        return
    sources = {source["id"]: source["path"] for source in read_graph()["sources"]}
    for identities, visible in [(retained_sources, present), (sibling_sources, True)]:
        for node, path in identities.items():
            assert sources.get(node) == (path if visible else None), sources


def click_remove(remove, cancel=False):
    remove.click()
    if compound_case:
        confirm = f.page.locator("[data-compound-delete-confirm]")
        expect(confirm).to_be_visible()
        f.page.locator("[data-compound-delete-cancel]" if cancel else "[data-compound-delete-confirm]").click()


def real_files_unchanged():
    for path, content in x.physical.items():
        if path != graph:
            assert path.read_bytes() == content, path


def graph_view(blueprint):
    tab = panel().get_by_role("tab", name="블루프린트 보기" if blueprint else "논리 코드", exact=True)
    if tab.get_attribute("aria-selected") != "true":
        tab.click()
    expect(tab).to_have_attribute("aria-selected", "true")
    expect(panel().locator(".bp-viewport") if blueprint else doc()).to_be_visible()


def expect_canvas_cell(present):
    viewport = panel().locator(".bp-viewport")
    expect(viewport.locator("[data-bp-node=other]")).to_have_count(int(present))
    expect(viewport.locator("[data-bp-node=body]")).to_be_visible()
    expect(viewport.locator("[data-bp-node=after]")).to_be_visible()
    expect(viewport.locator('[data-bp-link="route:body"]')).to_have_count(1)
    expect(viewport.locator('[data-bp-link="route:other"]')).to_have_count(int(present))
    expect(viewport.locator('.bp-exec-header-in[data-node=after].is-connected')).to_have_count(1)


def compound_view_roundtrip(remove, checkpoint, baseline_checkpoint):
    click_remove(remove)
    expect_cell(False)
    graph_view(True)
    expect_canvas_cell(False)
    assert checkpoint.read_bytes() == baseline_checkpoint and graph.read_bytes() == initial
    real_files_unchanged()
    viewport = panel().locator(".bp-viewport")
    viewport.press("Control+z")
    expect_canvas_cell(True)
    f.page.keyboard.press("Control+y")
    expect_canvas_cell(False)
    graph_view(False)
    expect_cell(False)
    save()
    assert_compound_sources(False)
    history = json.loads(checkpoint.read_bytes())["history"]
    assert len(history["undo"]) == 1 and not history["redo"]
    receipt = history["undo"][0]["cellRemoval"]
    assert {row["id"]: row["path"] for row in receipt["sources"]} == retained_sources
    assert graph.read_bytes() == initial
    confirm()
    assert json.loads(graph.read_bytes()) == removed
    real_files_unchanged()
    x.build("views-removed", exit_code, "\n".join(output_after))
    f.checked("Both views reflect the same one-step private compound deletion and Confirm removes exactly its execution")

    restart(1)
    graph_view(True)
    expect_canvas_cell(False)
    viewport = panel().locator(".bp-viewport")
    viewport.press("Control+z")
    expect_canvas_cell(True)
    expect(viewport).to_be_focused()
    f.page.keyboard.press("Control+y")
    expect_canvas_cell(False)
    f.page.keyboard.press("Control+z")
    expect_canvas_cell(True)
    assert json.loads(graph.read_bytes()) == removed
    graph_view(False)
    expect_cell(True)
    assert_compound_sources(True)
    panel().locator("[data-bp-save]").click()
    f.idle()
    window = review()
    window.locator("[data-reject]").click()
    real_files_unchanged()
    assert json.loads(graph.read_bytes()) == removed
    restart(2)
    expect_cell(True)
    confirm()
    assert graph.read_bytes() == initial
    real_files_unchanged()
    x.build("views-restored", exit_code, "\n".join(output_before))
    f.checked("Canvas cold Undo and Redo have one group; Review cancel leaves the original removed until explicit Confirm")

    graph_view(True)
    panel().locator("[data-bp-node=body] [data-internal-flow]").click()
    f.idle()
    graph_view(False)
    doc().locator("[data-document-internal=nest]").click()
    f.idle()
    doc().locator("[data-document-up=tail]").click()
    expect(doc().locator("[data-document-cell]").nth(1)).to_have_attribute("data-document-cell", "tail")
    save()
    confirm()
    written = json.loads(graph.read_bytes())
    assert select_graph(written, "other") == select_graph(definition, "other")
    assert select_graph(select_graph(written, "body"), "nest")["entry"] == "tail"
    real_files_unchanged()
    x.build("views-edit-sibling", exit_code, "\n".join(["inside", "body", "peer-inner", "peer-tail", "after", "10"]))
    assert not f.errors and not f.external, (f.errors, f.external)
    f.checked("Entering a nested sibling from Blueprint and reordering its same-ID children leaves the restored compound and all C# unchanged")


def undo_or_redo(direction, expected):
    history = f.invoke("draftHistory", {"action": "inspect"})["result"]["result"][direction]
    assert history["available"] and history["kind"] == "cell-removal"
    assert history.get("frame") == (frame_path if child_case else None)
    press_history_shortcut(direction)
    expect_cell(direction == "undo")
    current = read_graph()
    expected = select_graph(expected, frame_path) if child_case else expected
    assert current["entry"] == expected["entry"] and current["edges"] == expected["edges"]
    assert current["diagnostics"]["state"] in {"source-ready", "source-assembled"}
    assert_compound_sources(direction == "undo")


def confirm():
    window = review()
    window.locator("#confirm").click()
    expect(window).to_be_hidden(timeout=120000)
    f.idle()

def rejected_confirm(window):
    mark = len(f.traffic)
    window.locator("#confirm").click()
    # The UI can become idle before Playwright delivers the matching result event.
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        requests = {row["invoke"]["requestId"] for row in f.traffic[mark:]
                    if row.get("invoke", {}).get("endpoint") == "confirmGroup"}
        result = next((row["result"]["result"] for row in f.traffic[mark:]
                       if row.get("result", {}).get("requestId") in requests
                       and row["result"].get("ok")
                       and "sourceConfirmed" in row["result"].get("result", {})), None)
        if result is not None:
            assert result["sourceConfirmed"] is False, result
            break
        f.page.wait_for_timeout(25)
    else:
        raise AssertionError("Expected an engine confirmation refusal")
    f.idle()
    if window.is_visible():
        window.locator("[data-reject]").click()


def load_functions(file, names):
    path = Path(__file__).with_name(file)
    methods = [n for n in ast.parse(path.read_text()).body if isinstance(n, ast.FunctionDef) and n.name in names]
    exec(compile(ast.Module(body=methods, type_ignores=[]), str(path), "exec"), globals())


def change_definition(definition, changed_node):
    definitions = f.metadata("featureBlueprintNodes", featureSource=t.base.function, graph=definition)
    assert definitions["state"] == "node-definitions", definitions
    path = f.project / changed_node["implementation"]
    record = json.loads(path.read_bytes())
    record["definitionHash"] = next(node["definitionHash"] for node in definitions["nodes"]
                                    if node["id"] == changed_node["id"])
    path.write_bytes((json.dumps(record, indent=2, ensure_ascii=False).replace("\n", "\r\n") + "\r\n").encode())
    graph.write_text(json.dumps(definition, ensure_ascii=False))


def select_graph(root, path):
    return next(node["graph"] for node in root["nodes"] if node["id"] == path)


def prepare_child(root):
    load_functions("v821_frame_structure_ui.py", {"edge", "signature", "code", "child", "compound"})
    amount = [{"name": "amount", "type": "int"}]
    owned = child([
        code("inner", "Pair.body.inner.node.json", signature(amount, "int"), {"amount": {"input": "amount"}}),
        code("tail", "Pair.body.tail.node.json"),
    ], {"return": {"node": "inner"}})
    peer = child([code("inner", "Pair.other.inner.node.json"), code("tail", "Pair.other.tail.node.json")],
                 {"return": None})
    if mode == "compound-views":
        owned = child([compound("nest", owned, signature(amount, "int"), {"amount": {"input": "amount"}})],
                      {"return": {"node": "nest"}})
    if mode == "compound-deep-guard":
        peer = child([compound("nest", peer)], {"return": None})
    root["profile"] = "sync-acyclic-nested-v1"
    root["nodes"][0].pop("implementation")
    root["nodes"][0].update(kind="graph", graph=owned)
    root["nodes"].insert(1, compound("other", peer))
    root["edges"] = [edge("body", "other"), edge("other", "after"), edge("after", "exit:return")]
    graph.write_text(json.dumps(root, ensure_ascii=False))
    definitions = f.metadata("blueprintDescribeOwned", project=str(f.manifest), id=f.n + "PairBody",
                             text=(f.project / "PairBody.celem").read_text(), bodyTarget="common",
                             graph=root, definitionsOnly=True)
    assert definitions["state"] == "node-definitions", definitions
    bodies = {
        "body/inner": 'global::System.Console.WriteLine("body");\r\nreturn checked(amount+3);',
        "body/tail": 'global::System.Console.WriteLine("inside");',
        "other/inner": 'global::System.Console.WriteLine("peer-inner");',
        "other/tail": 'global::System.Console.WriteLine("peer-tail");',
        "after": 'global::System.Console.WriteLine("after");',
    }
    for node, source in bodies.items():
        path = node
        if mode == "compound-views" and node.startswith("body/"):
            node = node.replace("body/", "body/nest/")
        if mode == "compound-deep-guard" and node.startswith("other/"):
            node = node.replace("other/", "other/nest/")
        row = next(row for row in definitions["nodes"] + definitions["nestedNodes"] if row["id"] == node)
        file = f.project / f"Pair.{path.replace('/', '.')}.node.json"
        record = dict(schema=1, node=node.split("/")[-1], definitionHash=row["definitionHash"], source=source)
        file.write_bytes((json.dumps(record, indent=2, ensure_ascii=False).replace("\n", "\r\n") + "\r\n").encode())
    x.physical = {path: path.read_bytes() for path in f.project.iterdir() if path.is_file()}


definition = copy.deepcopy(t.definition)
if child_case or compound_case:
    prepare_child(definition)
if case:
    load_functions("v821_case_transfer_ui.py", {"code", "edge"})
    load_functions("v821_scope_transfer_ui.py", {"prepare_project"})
    graph_path, body_path = graph, f.project / "Pair.move.node.json"
    test_mode = mode
    mode = mode.removeprefix("case-") if mode in {"case-shared", "case-implicit"} else "normal"
    definition = prepare_project()
    mode = test_mode
    if mode == "case":
        moved = next(node for node in definition["nodes"] if node["id"] == "move")
        moved["branchOwner"] = "choose"
        for route in definition["edges"]:
            if route["from"] == "pre":
                route["to"] = "choose"
            elif route["from"] == "move":
                route["to"] = "left"
            elif route["port"] == "case:positive":
                route["to"] = "move"
        change_definition(definition, moved)
    if mode == "case-value":
        selected = next(node for node in definition["nodes"] if node["id"] == cell_id)
        selected["signature"]["args"] = [{"name": "amount", "type": "int"}]
        selected["arguments"] = {"amount": {"input": "amount"}}
        change_definition(definition, selected)
    if mode == "case-readonly":
        leaf.chmod(stat.S_IMODE(leaf.stat().st_mode) & ~0o222)
    original_case = ["right"] if mode == "case-exit" else ["move", "left"] if mode == "case" else ["left"]
    other_port = "case:positive" if mode == "case-exit" else "case:negative"
    other_case = ["left"] if mode == "case-exit" else ["right"]
    x.physical = {path: path.read_bytes() for path in f.project.iterdir() if path.is_file()}

if mode in {"readonly", "child-readonly", "compound-readonly"}:
    leaf.chmod(stat.S_IMODE(leaf.stat().st_mode) & ~0o222)
elif mode == "shared":
    manifest = f.project / "project.cproj"
    manifest.write_text(manifest.read_text().replace(
        'element PairBody implementation "PairBody.celem";',
        'element PairBody implementation "PairBody.celem";element SeparateBody implementation "SeparateBody.celem";'))
    (f.project / "SeparateBody.celem").write_text((f.project / "PairBody.celem").read_text().replace(
        f.n + "PairBody", f.n + "SeparateBody"))
    x.physical.update({path: path.read_bytes() for path in [manifest, f.project / "SeparateBody.celem"]})
elif mode == "value":
    after = next(node for node in definition["nodes"] if node["id"] == "after")
    after["signature"]["args"] = [{"name": "value", "type": "int"}]
    after["arguments"] = {"value": {"node": "body"}}
    change_definition(definition, after)
    x.physical[leaf] = leaf.read_bytes()
elif mode == "normal":
    # Exercise preservation of physical CRLF in the retained source record.
    record = json.loads(leaf.read_bytes())
    leaf.write_bytes((json.dumps(record, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n").encode())
    x.physical[leaf] = leaf.read_bytes()

initial = graph.read_bytes()
leaf_bytes = leaf.read_bytes()
if mode in positive_modes:
    removed = copy.deepcopy(definition)
    selected = select_graph(removed, frame_path) if child_case else removed
    selected["nodes"] = [node for node in selected["nodes"] if node["id"] != cell_id]
    outgoing = next(edge for edge in selected["edges"] if edge["from"] == cell_id)
    if selected["entry"] == cell_id:
        selected["entry"] = outgoing["to"]
    else:
        next(edge for edge in selected["edges"] if edge["to"] == cell_id)["to"] = outgoing["to"]
    selected["edges"].remove(outgoing)
    if case:
        positive = ["pre", "moved", "left", "body", "after", "result:10"]
        negative = ["pre", "right", "result:41"] if mode == "case" else ["pre", "moved", "right", "result:41"]
        output_after = positive + negative
        output_before = output_after.copy()
        output_after.remove({"case": "moved", "case-empty": "left", "case-exit": "right"}[mode])
        exit_code = 51
    elif child_case or compound_case:
        output_before, exit_code = ["body", "inside", "peer-inner", "peer-tail", "after", "10"], 10
        if compound_case:
            output_after = ["body", "inside", "after", "10"]
        else:
            output_after = output_before.copy()
            output_after.remove("peer-inner" if mode == "child-first" else "inside")
    else:
        output_before, output_after, exit_code = ["body", "after", "10"], ["body", "10"], 10

try:
    f.start(0)
    f.invoke("select", {"id": t.feature})
    f.invoke("saveDraft", {})
    checkpoint = next(f.project.glob(".confectory/edit-workspaces/*/draft.json"))
    baseline_checkpoint = checkpoint.read_bytes()
    with sync_playwright() as playwright:
        expect.set_options(timeout=45000)
        f.browser = playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
        f.page = f.setup()
        f.page.set_viewport_size({"width": 1800, "height": 1400})
        open_document()
        if child_case:
            expect(doc().locator("[data-document-remove=body],[data-document-remove=after]")).to_have_count(0)
            select_frame(frame_path)
            if frame_path == "body":
                expect(doc().locator("[data-document-remove=inner]")).to_have_count(0)
        remove = doc().locator(f"[data-document-remove={cell_id}]")
        expect_cell(True)
        assert doc().locator("[data-document-remove=body]").count() == 0
        if case:
            expect(doc().locator("[data-document-remove=choose],[data-document-remove=after]")).to_have_count(0)
        if mode not in positive_modes:
            expect(remove).to_have_count(0)
            if mode in {"case-shared", "case-implicit"}:
                expect(doc().locator("[data-document-remove]")).to_have_count(0)
            if mode == "compound-deep-guard":
                select_frame("other")
                doc().locator("[data-document-internal=nest]").click()
                f.idle()
                expect(doc().locator("[data-document-cell=inner]")).to_be_visible()
                expect(doc().locator("[data-document-cell=tail]")).to_be_visible()
                x.build("protected-deep-compound", 10, "body\ninside\npeer-inner\npeer-tail\nafter\n10")
                assert not pending()
            assert checkpoint.read_bytes() == baseline_checkpoint
            assert graph.read_bytes() == initial
            real_files_unchanged()
            f.checked(mode + " prevents document deletion, without changing the isolated original")
        elif mode == "compound-views":
            compound_view_roundtrip(remove, checkpoint, baseline_checkpoint)
        else:
            expect(remove).to_be_enabled()
            if compound_case:
                click_remove(remove, cancel=True)
                expect_cell(True)
                assert not pending() and checkpoint.read_bytes() == baseline_checkpoint
                assert_compound_sources(True)
                f.checked("compound deletion confirmation can be cancelled without staging an edit")
            click_remove(remove)
            expect_cell(False)
            f.page.keyboard.press("Control+z")
            expect(remove).to_be_visible(timeout=5000)
            if compound_case:
                f.page.keyboard.press("Control+y")
                expect_cell(False)
                f.page.keyboard.press("Control+z")
                expect_cell(True)
                assert_compound_sources(True)
                f.checked("direct keyboard Undo/Redo after compound deletion restores or removes the whole group")
            assert checkpoint.read_bytes() == baseline_checkpoint
            real_files_unchanged()

            x.build("original", exit_code, "\n".join(output_before))
            click_remove(remove)
            save()
            assert not pending(), panel().locator(".bp-status").inner_text()
            saved = json.loads(checkpoint.read_bytes())
            want_profile = "retained-blueprint-cell-group-v1" if compound_case else "retained-blueprint-cell-v1"
            assert saved["version"] == 3 and saved["cellHistoryProfile"] == want_profile
            receipt = saved["history"]["undo"][-1]["cellRemoval"]
            assert receipt["node"] == (f"{frame_path}/{cell_id}" if child_case else cell_id)
            if compound_case:
                assert len(saved["history"]["undo"]) == 1 and receipt["version"] == 2
                assert {row["id"]: row["path"] for row in receipt["sources"]} == retained_sources
                assert all(receipt["proof"][path] == hashlib.sha256((f.project / path).read_bytes()).hexdigest()
                           for path in retained_sources.values())
                (f.case / "compound-checkpoint.json").write_bytes(checkpoint.read_bytes())
                assert_compound_sources(False)
            assert [row["id"] for row in saved["changes"]] == [t.graph]
            assert graph.read_bytes() == initial
            real_files_unchanged()
            restart(1)
            expect_cell(False)
            assert_compound_sources(False)
            if case:
                expect_case_order(other_port, other_case)
            if child_case:
                selected_before = read_graph()
                sibling_before = read_graph(sibling_path)
                select_frame(sibling_path)
                expect(doc().locator(f"[data-document-cell={cell_id}]")).to_be_visible()
                press_history_shortcut("undo")
                assert read_graph()["edges"] == selected_before["edges"]
                assert read_graph(sibling_path)["edges"] == sibling_before["edges"]
                select_frame(frame_path)
                f.checked("keyboard Undo in a sibling with the same local ID leaves the saved edit and sibling intact")
            undo_or_redo("undo", definition)
            assert graph.read_bytes() == initial
            undo_or_redo("redo", removed)
            assert graph.read_bytes() == initial
            real_files_unchanged()
            f.checked("local cancellation and cold saved Undo/Redo preserve precise cell, ordering, exit and C# bytes")

            panel().locator("[data-bp-save]").click()
            f.idle()
            confirm()
            assert json.loads(graph.read_bytes()) == removed
            real_files_unchanged()
            x.build("confirmed-removed", exit_code, "\n".join(output_after))
            restart(2)
            undo_or_redo("undo", definition)
            if compound_case:
                history = f.invoke("draftHistory", {"action": "inspect"})["result"]["result"]
                assert history["undoCount"] == 0 and history["redoCount"] == 1
            assert json.loads(graph.read_bytes()) == removed, "Undo silently wrote the committed graph"
            real_files_unchanged()
            panel().locator("[data-bp-save]").click()
            f.idle()
            restart(5)
            expect_cell(True)
            assert_compound_sources(True)
            if compound_case:
                assert json.loads(graph.read_bytes()) == removed
            assert read_graph()["diagnostics"]["state"] in {"source-ready", "source-assembled"}
            confirm()
            assert graph.read_bytes() == initial
            real_files_unchanged()
            x.build("confirmed-restored", exit_code, "\n".join(output_before))
            f.checked("after Confirm and a new process Undo creates a draft; only a separate Save/Confirm restores active execution")

            restart(3)
            undo_or_redo("redo", removed)
            panel().locator("[data-bp-save]").click()
            f.idle()
            saved = checkpoint.read_bytes()
            window = review()
            leaf.write_bytes(leaf_bytes + b" ")
            rejected_confirm(window)
            assert graph.read_bytes() == initial and checkpoint.read_bytes() == saved
            assert leaf.read_bytes() == leaf_bytes + b" "
            leaf.write_bytes(leaf_bytes)
            f.checked("Confirm refuses a source change made after Review without discarding either input")

            window = review()
            changed_checkpoint = checkpoint.read_bytes() + b"\n"
            checkpoint.write_bytes(changed_checkpoint)
            rejected_confirm(window)
            assert graph.read_bytes() == initial and checkpoint.read_bytes() == changed_checkpoint
            checkpoint.write_bytes(saved)
            real_files_unchanged()
            f.checked("Confirm refuses a checkpoint change made after Review without publishing the graph")
            confirm()
            paths = [f.project / path for path in retained_sources.values()] if compound_case else [leaf]
            for index, source in enumerate(paths):
                source_bytes = source.read_bytes()
                changed = json.loads(source_bytes)
                changed["source"] += '\r\n// independently edited C# source'
                source.write_text(json.dumps(changed, ensure_ascii=False))
                peer_bytes = source.read_bytes()
                restart(10 + index)
                snapshot = checkpoint.read_bytes()
                history = f.invoke("draftHistory", {"action": "inspect"})["result"]["result"]
                step = history["undo"]
                assert step["kind"] == "cell-removal" and step["code"] == "SOURCE_CHANGED" and not step["available"]
                press_history_shortcut("undo")
                expect_cell(False)
                assert source.read_bytes() == peer_bytes and json.loads(graph.read_bytes()) == removed
                assert checkpoint.read_bytes() == snapshot
                assert read_graph()["edges"] == (select_graph(removed, frame_path) if child_case else removed)["edges"]
                after = f.invoke("draftHistory", {"action": "inspect"})["result"]["result"]
                assert all(after[key] == history[key] for key in ["revision", "undoCount", "redoCount"])
                assert not pending()
                assert_compound_sources(False)
                if compound_case:
                    source.write_bytes(source_bytes)
                    real_files_unchanged()
                f.checked(f"changing only {source.name} prevents cold Undo with no draft, history move or overwrite")

            if compound_case:
                available = f.invoke("draftHistory", {"action": "inspect"})["result"]["result"]["undo"]
                assert available["available"]
                source = paths[-1]
                hidden = source.with_suffix(".fixture-held")
                source.rename(hidden)
                try:
                    snapshot = checkpoint.read_bytes()
                    press_history_shortcut("undo")
                    expect_cell(False)
                    assert_compound_sources(False)
                    blocked = f.invoke("draftHistory", {"action": "inspect"})["result"]["result"]["undo"]
                    assert not blocked["available"] and blocked["id"] == available["id"]
                    assert not source.exists() and checkpoint.read_bytes() == snapshot and not pending()
                finally:
                    hidden.rename(source)
                real_files_unchanged()
                f.checked("a missing retained child refuses the entire Undo without creating a file")

                select_frame("body")
                doc().locator("[data-document-up=tail]").click()
                save()
                confirm()
                edited = copy.deepcopy(removed)
                sibling = select_graph(edited, "body")
                sibling["entry"] = "tail"
                sibling["edges"] = [{"from": "tail", "port": "next", "to": "inner"},
                                    {"from": "inner", "port": "next", "to": "exit:return"}]
                expect_written = json.loads(graph.read_bytes())
                written_sibling = select_graph(expect_written, "body")
                assert written_sibling["entry"] == sibling["entry"]
                assert {row["from"]: row for row in written_sibling["edges"]} == {row["from"]: row for row in sibling["edges"]}
                written_sibling["edges"] = sibling["edges"]
                assert expect_written == edited
                panel().locator(".bp-breadcrumbs button").first.click()
                f.idle()
                snapshot = checkpoint.read_bytes()
                history = f.invoke("draftHistory", {"action": "undo", "token": available["token"]})["result"]["result"]
                assert not history["accepted"] and not history["changed"]
                expect_cell(False)
                assert_compound_sources(False)
                assert checkpoint.read_bytes() == snapshot
                assert select_graph(json.loads(graph.read_bytes()), "body")["entry"] == "tail"
                real_files_unchanged()
                x.build("edited-sibling", exit_code, "\n".join(["inside", "body", "after", "10"]))
                f.checked("a normal sibling order edit survives an attempt using the previous compound Undo observation")
finally:
    f.stop()
