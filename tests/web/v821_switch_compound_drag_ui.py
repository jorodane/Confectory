"""Move an existing branch-containing call using the Linux editor's mouse and real engine."""
import ast
import copy
import json
import stat
import sys
import time
import uuid
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

import v666_node_names_recovery_fixture as t

f, x = t.f, t.x
mode = sys.argv[3] if len(sys.argv) > 3 else "normal"
assert mode in {"normal", "shared", "implicit", "readonly", "aliased"}


def load_helpers(name):
    path = Path(__file__).with_name(name)
    methods = [node for node in ast.parse(path.read_text()).body if isinstance(node, ast.FunctionDef)]
    exec(compile(ast.Module(body=methods, type_ignores=[]), str(path), "exec"), globals())


load_helpers("v821_function_document_ui.py")
load_helpers("v821_cell_drag_ui.py")


def edge(start, end, port="next"):
    return {"from": start, "port": port, "to": end}


def code(name, args=(), result="void", owner=None):
    node = {
        "id": name, "kind": "code", "control": "next", "intent": name,
        "signature": {"args": [dict(name=name, type="int") for name in args], "return": result},
        "arguments": {name: {"input": name} for name in args},
        "implementation": f"Pair.{name}.node.json",
    }
    if owner:
        node["branchOwner"] = owner
    return node


def prepare_project():
    graph = copy.deepcopy(t.definition)
    graph["profile"] = "sync-acyclic-nested-v1"
    invocation = graph["nodes"][0]
    invocation.pop("implementation")
    invocation["kind"] = "graph"
    choose = code("choose", ("amount",))
    choose["control"] = "switch"
    choose["executionEnum"] = {
        "primary": "next",
        "members": [
            {"id": "next", "name": "None", "value": 0},
            {"id": "positive", "name": "Positive", "value": 1},
            {"id": "negative", "name": "Negative", "value": 2},
        ],
    }
    nodes = [choose, code("positive", ("amount",), owner="choose"), code("finish", ("amount",), "int")]
    edges = [
        edge("choose", "finish"), edge("choose", "positive", "case:positive"),
        edge("positive", "return:choose"), edge("finish", "exit:return"),
    ]
    if mode == "shared":
        edges.append(edge("choose", "positive", "case:negative"))
    elif mode != "implicit":
        nodes.append(code("negative", ("amount",), owner="choose"))
        edges.extend([edge("choose", "negative", "case:negative"), edge("negative", "return:choose")])
    invocation["graph"] = dict(
        schema=1, profile="sync-acyclic-switch-v1", entry="choose",
        nodes=nodes, edges=edges, exits={"return": {"node": "finish"}},
    )
    graph_path.write_text(json.dumps(graph, ensure_ascii=False))
    definitions = f.metadata(
        "blueprintDescribeOwned", project=str(f.manifest), id=f.n + "PairBody",
        text=(f.project / "PairBody.celem").read_text(), bodyTarget="common",
        graph=graph, definitionsOnly=True,
    )
    assert definitions["state"] == "node-definitions", definitions
    bodies = {
        "choose": "return amount > 0 ? Result.Positive : Result.Negative;",
        "positive": 'global::System.Console.WriteLine("positive:"+amount);',
        "negative": 'global::System.Console.WriteLine("negative:"+amount);',
        "finish": '// 원문 보존\r\nglobal::System.Console.WriteLine("finish:"+amount);\r\nreturn checked(amount+3);',
    }
    hashes = {node["id"]: node["definitionHash"] for node in definitions["nestedNodes"]}
    for node in nodes:
        name = node["id"]
        record = dict(schema=1, node=name, definitionHash=hashes["body/" + name], source=bodies[name])
        (f.project / node["implementation"]).write_text(json.dumps(record, ensure_ascii=False))
    after = f.project / "Pair.after.node.json"
    record = json.loads(after.read_text())
    record["definitionHash"] = next(row["definitionHash"] for row in definitions["nodes"] if row["id"] == "after")
    after.write_text(json.dumps(record, ensure_ascii=False))
    (f.project / "Main.csbody").write_text(
        "int sum=0;foreach(int value in new[]{7,-2}){int result=calls.Pair.Invoke(value);"
        'global::System.Console.WriteLine("result:"+result);sum+=result;}return sum;'
    )
    if mode == "readonly":
        graph_path.chmod(0o444)
    if mode == "aliased":
        header = f.project / "PairBody.celem"
        source = header.read_text()
        marker = f'blueprint common "{t.graph_file}";'
        assert marker in source
        header.write_text(source.replace(marker, marker + f' blueprint windows "{t.graph_file}";', 1))
    return graph


def stdout(moved=False):
    lines = []
    for value, label in [(7, "positive"), (-2, {"shared": "positive", "implicit": None}.get(mode, "negative"))]:
        if moved:
            lines.append("after")
        if label:
            lines.append(f"{label}:{value}")
        lines.append(f"finish:{value}")
        if not moved:
            lines.append("after")
        lines.append(f"result:{value + 3}")
    return "\n".join(lines)


def source_modes():
    return {path: stat.S_IMODE(path.stat().st_mode) for path in x.physical}


def draft_request(data):
    return dict(
        action="authorBatch", documentCompound=True, id=t.graph, attempt=uuid.uuid4().hex,
        checkpointHash=data["checkpointHash"], sourceProof=x.proof(data),
        edits=[dict(action="entry", node="$entry", to="after"),
               dict(action="route", node="after", port="next", to="body"),
               dict(action="route", node="body", port="next", to="exit:return")],
    )


def assert_confirmed():
    expected = copy.deepcopy(original_graph)
    expected["entry"] = "after"
    expected["edges"] = [edge("after", "body"), edge("body", "exit:return")]
    actual = json.loads(graph_path.read_text())
    assert sorted(actual.pop("edges"), key=lambda route: route["from"]) == sorted(expected.pop("edges"), key=lambda route: route["from"])
    assert actual == expected
    assert all(path.read_bytes() == raw for path, raw in x.physical.items() if path != graph_path)
    assert source_modes() == modes


def open_child():
    cell("body").locator("[data-document-fold][aria-expanded=false]").click()
    doc().locator("[data-document-internal=body]").click()
    f.idle()
    expect(cell("choose")).to_be_visible()
    for branch in ("positive", "negative"):
        doc().locator(f'[data-document-branch="case:{branch}"]').click()
        expect(cell(branch)).to_be_visible()
        expect(grip(branch)).to_be_disabled()
    panel().locator(".bp-breadcrumbs button").first.click()
    f.idle()


graph_path = f.project / t.graph_file
original_graph = prepare_project()
x.physical = {p: p.read_bytes() for p in f.project.rglob("*") if p.is_file() and ".confectory" not in p.parts}
modes = source_modes()
initial_order, moved_order = ["body", "after"], ["after", "body"]
try:
    x.build("before-drag", 11, stdout())
    f.start(0)
    f.invoke("select", dict(id=t.feature))
    f.invoke("saveDraft", {})
    checkpoint = next(f.project.glob(".confectory/edit-workspaces/*/draft.json"))
    before = checkpoint.read_bytes()
    with sync_playwright() as pw:
        try:
            expect.set_options(timeout=45000)
            f.browser = pw.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
            f.page = f.setup()
            f.page.set_viewport_size(dict(width=1800, height=1400))
            open_document()
            enlarge()
            baseline = t.read()
            folded()
            assert baseline["documentCompoundOrderAvailable"] == (mode in {"normal", "readonly", "aliased"}), baseline["diagnostics"]
            assert baseline["documentCompoundOrderWritable"] == (mode not in {"readonly", "aliased"})
            if mode != "normal":
                expect(grip("body")).to_be_disabled()
                move("body", "after", after=True, valid=False, disabled=True)
                assert logical_ids() == initial_order and not pending()
                f.invoke("blueprint", draft_request(baseline), False)
                assert checkpoint.read_bytes() == before and t.read()["entry"] == "body"
                x.original()
                assert source_modes() == modes
                f.checked(f"{mode} child keeps its existing execution, disabled drag and original source/checkpoint")
            else:
                move("body", "after", after=True, capture=True)
                wait_order(moved_order)
                held = pending()
                assert len(held) == 3 and t.read()["nodes"] == baseline["nodes"]
                assert checkpoint.read_bytes() == before
                x.original()
                local_undo()
                wait_order(initial_order)
                assert not pending()
                local_undo(True)
                wait_order(moved_order)
                assert pending() == held
                move("body", "after")
                wait_order(initial_order)
                local_undo()
                wait_order(moved_order)
                assert pending() == held
                start_drag("body")
                hover("after")
                expect(f.page.locator(".fd-cell-drop-marker")).to_have_count(1)
                f.page.keyboard.press("Escape")
                f.page.mouse.up()
                expect(f.page.locator(".fd-cell-drop-marker")).to_have_count(0)
                assert logical_ids() == moved_order and pending() == held
                open_child()
                wait_order(moved_order)
                assert pending() == held
                restart_drag(1)
                wait_order(moved_order)
                assert pending() == held and checkpoint.read_bytes() == before
                x.original()
                f.checked("real mouse reorders both ways, Escape keeps staged input, qualified child branches and local history survive reopen")

                graph_path.chmod(0o444)
                try:
                    restart_drag(2)
                    expect(grip("body")).to_be_disabled()
                    assert pending() == held
                    traffic = save()
                    assert not any(row.get("invoke", {}).get("input", {}).get("action") in {"entry", "route", "serialRoutes"} for row in traffic)
                    assert retained(held) and checkpoint.read_bytes() == before
                    assert not t.read()["documentCompoundOrderWritable"]
                    x.original()
                finally:
                    graph_path.chmod(modes[graph_path])
                save()
                assert not pending() and t.read()["entry"] == "after"
                for direction, entry in [("undo", "body"), ("redo", "after")]:
                    history = f.invoke("draftHistory", dict(action="inspect"))["result"]["result"]
                    assert history[direction]["available"]
                    assert f.invoke("draftHistory", dict(action=direction, token=history[direction]["token"]))["result"]["result"]["accepted"]
                    current = t.read()
                    assert current["entry"] == entry and current["nodes"] == baseline["nodes"]
                f.invoke("saveDraft", {})
                restart_drag(3)
                wait_order(moved_order)
                assert not pending()
                x.original()
                r = review()
                r.locator("[data-reject]").click()
                x.original()
                r = review()
                raw, saved = graph_path.read_bytes(), checkpoint.read_bytes()
                graph_path.write_bytes(raw + b" ")
                try:
                    r.locator("#confirm").click()
                    f.idle()
                    assert graph_path.read_bytes() == raw + b" " and checkpoint.read_bytes() == saved
                finally:
                    graph_path.write_bytes(raw)
                if r.is_visible():
                    r.locator("[data-reject]").click()
                r = review()
                r.locator("#confirm").click()
                expect(r).to_be_hidden(timeout=120000)
                f.idle()
                assert_confirmed()
                x.build("after-drag", 11, stdout(moved=True))
                restart_drag(4)
                wait_order(moved_order)
                assert not pending()
                assert_confirmed()
                f.checked("read-only Save and final CAS reject safely, shared history and reopen keep branches, both compiled outcomes preserve child bindings after Confirm")
            f.page.screenshot(path=str(f.case / f"switch-compound-drag-{mode}.png"), full_page=True)
            assert not f.errors and not f.external, (f.errors, f.external)
        except Exception:
            if f.page and not f.page.is_closed():
                (f.case / "failure.html").write_text(f.page.content())
                f.page.screenshot(path=str(f.case / "failure.png"), timeout=10000)
            raise
        finally:
            f.browser.close()
finally:
    (f.case / "drag-traffic.json").write_text(json.dumps(f.traffic, ensure_ascii=False))
    (f.case / "drag-checks.json").write_text(json.dumps(f.checks, ensure_ascii=False))
    f.stop()
print("V821_SWITCH_COMPOUND_DRAG", mode, f.case, flush=True)
