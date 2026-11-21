"""Real Linux UI for saved and confirmed cell removal and checked shared Undo."""

import ast
import copy
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
                "case-shared", "case-implicit", "case-readonly", "case-value"}
case = mode.startswith("case")
positive_modes = {"normal", "case", "case-empty", "case-exit"}
helper = Path(__file__).with_name("v821_function_document_ui.py")
functions = [node for node in ast.parse(helper.read_text()).body if isinstance(node, ast.FunctionDef)]
exec(compile(ast.Module(body=functions, type_ignores=[]), str(helper), "exec"), globals())

graph = f.project / t.graph_file
cell_id = {"case": "move", "case-exit": "right"}.get(mode, "left" if case else "after")
leaf = f.project / f"Pair.{cell_id}.node.json"
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


def expect_cell(present):
    expect(doc().locator(f"[data-document-cell={cell_id}]")).to_have_count(int(present))
    if case:
        cells = original_case if present else [cell for cell in original_case if cell != cell_id]
        expect_case_order(case_port, cells)
    else:
        assert order() == (["$entry", "body", "after", "$exit:return"] if present else ["$entry", "body", "$exit:return"])


def real_files_unchanged():
    for path, content in x.physical.items():
        if path != graph:
            assert path.read_bytes() == content, path


def undo_or_redo(direction, expected):
    history = f.invoke("draftHistory", {"action": "inspect"})["result"]["result"][direction]
    assert history["available"] and history["kind"] == "cell-removal"
    doc().locator(".fd-document-title").click()
    doc().press("Control+z" if direction == "undo" else "Control+y")
    expect_cell(direction == "undo")
    f.idle()
    current = t.read()
    assert current["edges"] == expected["edges"]
    assert current["diagnostics"]["state"] in {"source-ready", "source-assembled"}


def confirm():
    window = review()
    window.locator("#confirm").click()
    expect(window).to_be_hidden(timeout=120000)
    f.idle()

def rejected_confirm(window):
    mark = len(f.traffic)
    window.locator("#confirm").click()
    f.idle()
    requests = {row["invoke"]["requestId"] for row in f.traffic[mark:]
                if row.get("invoke", {}).get("endpoint") == "confirmGroup"}
    results = [row["result"] for row in f.traffic[mark:]
               if row.get("result", {}).get("requestId") in requests]
    assert any(result.get("ok") and result.get("result", {}).get("sourceConfirmed") is False
               for result in results), results
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


definition = copy.deepcopy(t.definition)
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

if mode == "readonly":
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
    removed["nodes"] = [node for node in removed["nodes"] if node["id"] != cell_id]
    outgoing = next(edge for edge in removed["edges"] if edge["from"] == cell_id)
    next(edge for edge in removed["edges"] if edge["to"] == cell_id)["to"] = outgoing["to"]
    removed["edges"].remove(outgoing)
    if case:
        positive = ["pre", "moved", "left", "body", "after", "result:10"]
        negative = ["pre", "right", "result:41"] if mode == "case" else ["pre", "moved", "right", "result:41"]
        output_after = positive + negative
        output_before = output_after.copy()
        output_after.remove({"case": "moved", "case-empty": "left", "case-exit": "right"}[mode])
        exit_code = 51
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
        remove = doc().locator(f"[data-document-remove={cell_id}]")
        expect_cell(True)
        assert doc().locator("[data-document-remove=body]").count() == 0
        if case:
            expect(doc().locator("[data-document-remove=choose],[data-document-remove=after]")).to_have_count(0)
        if mode not in positive_modes:
            expect(remove).to_have_count(0)
            if mode in {"case-shared", "case-implicit"}:
                expect(doc().locator("[data-document-remove]")).to_have_count(0)
            assert checkpoint.read_bytes() == baseline_checkpoint
            assert graph.read_bytes() == initial
            real_files_unchanged()
            f.checked(mode + " prevents document deletion, without changing the isolated original")
        else:
            expect(remove).to_be_enabled()
            remove.click()
            expect_cell(False)
            doc().locator(".fd-document-title").click()
            doc().press("Control+z")
            expect(remove).to_be_visible()
            assert checkpoint.read_bytes() == baseline_checkpoint
            real_files_unchanged()

            x.build("original", exit_code, "\n".join(output_before))
            remove.click()
            save()
            assert not pending(), panel().locator(".bp-status").inner_text()
            saved = json.loads(checkpoint.read_bytes())
            assert saved["version"] == 3 and saved["cellHistoryProfile"] == "retained-blueprint-cell-v1"
            assert saved["history"]["undo"][-1]["cellRemoval"]["node"] == cell_id
            assert [row["id"] for row in saved["changes"]] == [t.graph]
            assert graph.read_bytes() == initial
            real_files_unchanged()
            restart(1)
            expect_cell(False)
            if case:
                expect_case_order(other_port, other_case)
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
            assert json.loads(graph.read_bytes()) == removed, "Undo silently wrote the committed graph"
            real_files_unchanged()
            panel().locator("[data-bp-save]").click()
            f.idle()
            restart(5)
            expect_cell(True)
            assert t.read()["diagnostics"]["state"] in {"source-ready", "source-assembled"}
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
            changed = json.loads(leaf_bytes)
            changed["source"] += '\r\n// independently edited C# source'
            leaf.write_text(json.dumps(changed, ensure_ascii=False))
            peer_bytes = leaf.read_bytes()
            restart(4)
            history = f.invoke("draftHistory", {"action": "inspect"})["result"]["result"]["undo"]
            assert history["kind"] == "cell-removal" and history["code"] == "SOURCE_CHANGED" and not history["available"]
            doc().locator(".fd-document-title").click()
            doc().press("Control+z")
            expect_cell(False)
            f.idle()
            assert leaf.read_bytes() == peer_bytes and json.loads(graph.read_bytes()) == removed
            assert t.read()["edges"] == removed["edges"]
            f.checked("an independent C# source edit prevents cold Undo and is never overwritten")
finally:
    f.stop()
