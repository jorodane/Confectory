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
assert mode in {"normal", "readonly", "shared", "value", "branch"}
helper = Path(__file__).with_name("v821_function_document_ui.py")
functions = [node for node in ast.parse(helper.read_text()).body if isinstance(node, ast.FunctionDef)]
exec(compile(ast.Module(body=functions, type_ignores=[]), str(helper), "exec"), globals())

graph = f.project / t.graph_file
leaf = f.project / "Pair.after.node.json"
initial = graph.read_bytes()
if mode == "normal":
    # Exercise preservation of physical CRLF in the retained source record.
    record = json.loads(leaf.read_bytes())
    leaf.write_bytes((json.dumps(record, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n").encode())
    x.physical[leaf] = leaf.read_bytes()
leaf_bytes = leaf.read_bytes()
removed = copy.deepcopy(t.definition)
removed["nodes"] = [node for node in removed["nodes"] if node["id"] != "after"]
removed["edges"] = [{"from": "body", "port": "next", "to": "exit:return"}]


def order():
    return doc().locator("[data-document-cell]").evaluate_all("(rows)=>rows.map(row=>row.dataset.documentCell)")


def real_files_unchanged():
    for path, content in x.physical.items():
        if path != graph:
            assert path.read_bytes() == content, path


def undo_or_redo(direction, expected):
    history = f.invoke("draftHistory", {"action": "inspect"})["result"]["result"][direction]
    assert history["available"] and history["kind"] == "cell-removal"
    doc().locator(".fd-document-title").click()
    doc().press("Control+z" if direction == "undo" else "Control+y")
    expect(doc().locator("[data-document-cell=after]")).to_have_count(int(direction == "undo"))
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
    definition = copy.deepcopy(t.definition)
    after = next(node for node in definition["nodes"] if node["id"] == "after")
    after["signature"]["args"] = [{"name": "value", "type": "int"}]
    after["arguments"] = {"value": {"node": "body"}}
    definitions = f.metadata("featureBlueprintNodes", featureSource=t.base.function, graph=definition)
    record = json.loads(leaf_bytes)
    record["definitionHash"] = next(node["definitionHash"] for node in definitions["nodes"] if node["id"] == "after")
    leaf.write_text(json.dumps(record, ensure_ascii=False))
    graph.write_text(json.dumps(definition, ensure_ascii=False))
    initial = graph.read_bytes()
    x.physical[leaf] = leaf.read_bytes()
elif mode == "branch":
    def load_functions(file, names):
        path = Path(__file__).with_name(file)
        methods = [n for n in ast.parse(path.read_text()).body if isinstance(n, ast.FunctionDef) and n.name in names]
        exec(compile(ast.Module(body=methods, type_ignores=[]), str(path), "exec"), globals())

    load_functions("v821_case_transfer_ui.py", {"code", "edge"})
    load_functions("v821_scope_transfer_ui.py", {"prepare_project"})
    graph_path, body_path = graph, f.project / "Pair.move.node.json"
    prepare_project()
    initial = graph.read_bytes()
    x.physical = {path: path.read_bytes() for path in f.project.iterdir() if path.is_file()}

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
        remove = doc().locator("[data-document-remove=after]")
        if mode != "branch":
            assert order() == ["$entry", "body", "after", "$exit:return"]
        assert doc().locator("[data-document-remove=body]").count() == 0
        if mode != "normal":
            expect(remove).to_have_count(0)
            if mode == "branch":
                expect(doc().locator("[data-document-cell=left]")).to_be_visible()
                expect(doc().locator("[data-document-remove]")).to_have_count(0)
            assert checkpoint.read_bytes() == baseline_checkpoint
            assert graph.read_bytes() == initial
            real_files_unchanged()
            f.checked(mode + " prevents document deletion, without changing the isolated original")
        else:
            expect(remove).to_be_enabled()
            remove.click()
            expect(doc().locator("[data-document-cell=after]")).to_have_count(0)
            doc().locator(".fd-document-title").click()
            doc().press("Control+z")
            expect(remove).to_be_visible()
            assert checkpoint.read_bytes() == baseline_checkpoint
            real_files_unchanged()

            x.build("original", 10, "body\nafter\n10")
            remove.click()
            save()
            assert not pending(), panel().locator(".bp-status").inner_text()
            saved = json.loads(checkpoint.read_bytes())
            assert saved["version"] == 3 and saved["cellHistoryProfile"] == "retained-blueprint-cell-v1"
            assert saved["history"]["undo"][-1]["cellRemoval"]["node"] == "after"
            assert [row["id"] for row in saved["changes"]] == [t.graph]
            assert graph.read_bytes() == initial
            real_files_unchanged()
            restart(1)
            assert order() == ["$entry", "body", "$exit:return"]
            undo_or_redo("undo", t.definition)
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
            x.build("confirmed-removed", 10, "body\n10")
            restart(2)
            undo_or_redo("undo", t.definition)
            assert json.loads(graph.read_bytes()) == removed, "Undo silently wrote the committed graph"
            real_files_unchanged()
            panel().locator("[data-bp-save]").click()
            f.idle()
            restart(5)
            assert order() == ["$entry", "body", "after", "$exit:return"]
            assert t.read()["diagnostics"]["state"] in {"source-ready", "source-assembled"}
            confirm()
            assert graph.read_bytes() == initial
            real_files_unchanged()
            x.build("confirmed-restored", 10, "body\nafter\n10")
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
            expect(doc().locator("[data-document-cell=after]")).to_have_count(0)
            f.idle()
            assert leaf.read_bytes() == peer_bytes and json.loads(graph.read_bytes()) == removed
            assert t.read()["edges"] == removed["edges"]
            f.checked("an independent C# source edit prevents cold Undo and is never overwritten")
finally:
    f.stop()
