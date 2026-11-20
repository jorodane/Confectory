"""Linux Chromium and engine verification of main/case placement and paired Save."""
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
assert mode in {"normal", "empty", "value", "readonly", "shared", "implicit"}
graph_path = f.project / t.graph_file
body_path = f.project / "Pair.move.node.json"


def load_helpers(filename, names=None):
    path = Path(__file__).with_name(filename)
    methods = [
        node for node in ast.parse(path.read_text()).body
        if isinstance(node, ast.FunctionDef) and (names is None or node.name in names)
    ]
    exec(compile(ast.Module(body=methods, type_ignores=[]), str(path), "exec"), globals())


load_helpers("v821_function_document_ui.py")
load_helpers("v821_cell_drag_ui.py", {"cell", "grip", "flow", "ids", "logical_ids", "folded", "enlarge", "start_drag", "local_undo", "restart_drag"})
load_helpers("v821_case_transfer_ui.py", {"edge", "code", "case_tab", "case_order", "sources_unchanged"})


def prepare_project():
    graph = copy.deepcopy(t.definition)
    graph.update(profile="sync-acyclic-switch-v1", entry="pre")
    choose = code("choose", ("amount",))
    choose.update(control="switch", executionEnum={
        "primary": "next", "members": [
            {"id": "next", "name": "None", "value": 0},
            {"id": "positive", "name": "Positive", "value": 1},
            {"id": "negative", "name": "Negative", "value": 2},
        ],
    })
    nodes = [code("pre"), code("move", ("amount",) if mode == "value" else ()), choose]
    if mode != "empty":
        nodes.append(code("left", owner="choose"))
    if mode not in {"shared", "implicit"}:
        nodes.append(code("right", owner="choose"))
    graph["nodes"] += nodes
    positive = "return:choose" if mode == "empty" else "left"
    graph["edges"] += [edge("pre", "move"), edge("move", "choose"), edge("choose", "body"),
                       edge("choose", positive, "case:positive")]
    if mode != "empty":
        graph["edges"].append(edge("left", "return:choose"))
    if mode == "shared":
        graph["edges"].append(edge("choose", "left", "case:negative"))
    elif mode != "implicit":
        graph["edges"] += [edge("choose", "right", "case:negative"), edge("right", "exit:early")]
        graph["exits"]["early"] = {"constant": 41}
    defs = f.metadata("featureBlueprintNodes", featureSource=t.base.function, graph=graph)
    assert defs["state"] == "node-definitions", defs
    hashes = {row["id"]: row["definitionHash"] for row in defs["nodes"]}
    bodies = {
        "pre": 'global::System.Console.WriteLine("pre");',
        "choose": "return amount > 0 ? Result.Positive : Result.Negative;",
        "move": '// 원문 😀\r\nglobal::System.Console.WriteLine("moved");\r\n',
        "left": 'global::System.Console.WriteLine("left");',
        "right": 'global::System.Console.WriteLine("right");',
    }
    for node in graph["nodes"]:
        name = node["id"]
        path = f.project / node["implementation"]
        record = json.loads(path.read_text()) if path.exists() else dict(schema=1, node=name, source=bodies[name])
        record["definitionHash"] = hashes[name]
        path.write_bytes((json.dumps(record, indent=2, ensure_ascii=False).replace("\n", "\r\n") + "\r\n").encode())
    graph_path.write_text(json.dumps(graph, ensure_ascii=False))
    (f.project / "Main.csbody").write_text(
        'int sum=0;foreach(int value in new[]{7,-2}){int result=calls.Pair.Invoke(value);'
        'global::System.Console.WriteLine("result:"+result);sum+=result;}return sum;'
    )
    if mode == "readonly":
        body_path.chmod(0o444)
    return graph


def output(region):
    def before():
        if region == "entry":
            return ["moved", "pre"]
        return ["pre"] + (["moved"] if region == "before" else [])

    left = [] if mode == "empty" else ["left"]
    positive = before() + left + (["moved"] if region == "case" else []) + ["body", "after", "result:10"]
    if mode == "shared":
        return 11, "\n".join(positive + before() + ["left", "body", "after", "result:1"])
    if mode == "implicit":
        return 11, "\n".join(positive + before() + ["body", "after", "result:1"])
    return 51, "\n".join(positive + before() + ["right", "result:41"])


def drag_placement(target, side, scope, *, cancel=False, picture=False):
    start_drag("move")
    bounds = target.bounding_box()
    assert bounds
    x_pos = bounds["x"] + bounds["width"] / 2
    y_pos = bounds["y"] + bounds["height"] * (0.24 if side == "before" else 0.76)
    f.page.mouse.move(x_pos + 3, y_pos, steps=15)
    f.page.mouse.move(x_pos, y_pos, steps=3)
    marker = f.page.locator('.fd-cell-drop-marker[data-scope-transfer]')
    expect(marker).to_have_count(1 if scope else 0)
    if scope:
        expect(marker).to_have_attribute("data-scope-transfer", scope)
        expect(marker).to_have_text("분기 안에 놓기" if scope == "case" else "주 흐름에 놓기")
    if cancel:
        f.page.keyboard.press("Escape")
    if picture:
        f.page.screenshot(path=str(f.case / ("scope-transfer-" + scope + "-placement.png")))
    f.page.mouse.up()
    f.idle()
    expect(marker).to_have_count(0)


def assert_view(root, branch):
    assert logical_ids() == root, logical_ids()
    assert case_order("positive") == branch


def expected_case():
    expected = copy.deepcopy(original)
    node = next(node for node in expected["nodes"] if node["id"] == "move")
    node["branchOwner"] = "choose"
    routes = {(row["from"], row["port"]): row for row in expected["edges"]}
    routes["pre", "next"]["to"] = "choose"
    routes["move", "next"]["to"] = "return:choose"
    if mode == "empty":
        routes["choose", "case:positive"]["to"] = "move"
    else:
        routes["left", "next"]["to"] = "move"
    return expected


def expected_root_entry():
    expected = copy.deepcopy(original)
    expected["entry"] = "move"
    routes = {(row["from"], row["port"]): row for row in expected["edges"]}
    routes["pre", "next"]["to"] = "choose"
    routes["move", "next"]["to"] = "pre"
    return expected


def original_except_pair(expected):
    for path, data in x.physical.items():
        if path not in {graph_path, body_path}:
            assert path.read_bytes() == data
        assert stat.S_IMODE(path.stat().st_mode) == modes[path]
    assert json.loads(graph_path.read_text()) == expected
    definitions = f.metadata("featureBlueprintNodes", featureSource=t.base.function, graph=expected)
    assert definitions["state"] == "node-definitions", definitions
    digest = next(row["definitionHash"] for row in definitions["nodes"] if row["id"] == "move")
    assert body_path.read_bytes() == before_body.replace(old_stamp.encode(), digest.encode())


def shared_history(direction, want):
    history = f.invoke("draftHistory", {"action": "inspect"})["result"]["result"][direction]
    assert history["available"] and {row["kind"] for row in history["units"]} == {"blueprint", "blueprint-node"}
    assert f.invoke("draftHistory", {"action": direction, "token": history["token"]})["result"]["result"]["accepted"]
    result = t.read()
    assert result["edges"] == want["edges"]
    assert result["diagnostics"]["state"] == "source-ready"


def confirm(r):
    r.locator("#confirm").click()
    expect(r).to_be_hidden(timeout=120000)
    f.idle()


original = prepare_project()
x.physical = {p: p.read_bytes() for p in f.project.rglob("*") if p.is_file() and ".confectory" not in p.parts}
modes = {path: stat.S_IMODE(path.stat().st_mode) for path in x.physical}
before_body = x.physical[body_path]
old_stamp = json.loads(before_body)["definitionHash"]
root_old = ["pre", "move", "choose", "body", "after"]
root_moved = ["pre", "choose", "body", "after"]
branch_old = [] if mode == "empty" else ["left"]
supported = mode in {"normal", "empty"}
try:
    x.build("scope-before", *output("before"))
    f.start(0)
    f.invoke("select", {"id": t.feature})
    f.invoke("saveDraft", {})
    checkpoint = next(f.project.glob(".confectory/edit-workspaces/*/draft.json"))
    initial = checkpoint.read_bytes()
    with sync_playwright() as pw:
        expect.set_options(timeout=45000)
        f.browser = pw.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
        f.page = f.setup()
        f.page.set_viewport_size({"width": 1800, "height": 1400})
        try:
            open_document()
            enlarge()
            folded()
            assert_view(root_old, branch_old)
            before = t.read()
            capability = before["documentScopeTransfer"]
            if not supported:
                assert capability is None or "move" not in capability["movable"]
                expect(grip("move")).to_be_disabled()
                assert not pending() and t.read()["edges"] == before["edges"]
                assert checkpoint.read_bytes() == initial
                sources_unchanged()
                f.checked(mode + " scope transfer is disabled with original sources and inputs intact")
            else:
                assert capability["owner"] == "choose" and "move" in capability["movable"]
                target = doc().locator('[data-document-branch-add="case:positive"]') if mode == "empty" else cell("left")
                drag_placement(target, "before", "case", cancel=True)
                assert_view(root_old, branch_old)
                assert not pending()
                if mode == "normal":
                    drag_placement(target, "before", "case")
                    assert_view(root_moved, ["move", "left"])
                    local_undo()
                    assert_view(root_old, branch_old)
                    assert not pending()
                drag_placement(target, "before" if mode == "empty" else "after", "case", picture=True)
                assert_view(root_moved, branch_old + ["move"])
                held = pending()
                assert len(held) == 1 and checkpoint.read_bytes() == initial
                sources_unchanged()
                local_undo()
                assert_view(root_old, branch_old)
                local_undo(True)
                assert_view(root_moved, branch_old + ["move"])
                restart_drag(1)
                assert_view(root_moved, branch_old + ["move"])
                assert pending() == held
                f.checked("draft marker, cancel, placement before/after, Undo/Redo and reopening")

                if mode == "normal":
                    checkpoint.chmod(0o400)
                    try:
                        save()
                        assert retained(held) and checkpoint.read_bytes() == initial
                        sources_unchanged()
                    finally:
                        checkpoint.chmod(0o600)
                save()
                assert not pending()
                assert t.read()["edges"] == expected_case()["edges"]
                sources_unchanged()
                shared_history("undo", original)
                shared_history("redo", expected_case())
                f.invoke("saveDraft", {})
                restart_drag(2)
                assert_view(root_moved, branch_old + ["move"])

                if mode == "normal":
                    saved = checkpoint.read_bytes()
                    for member in [t.graph, t.graph + "/node:move"]:
                        f.invoke("reviewGroup", {"ids": [member], "target": "portable"}, False)
                    assert checkpoint.read_bytes() == saved
                    sources_unchanged()
                r = review()
                if mode == "normal":
                    r.locator("[data-reject]").click()
                    sources_unchanged()
                    r = review()
                    saved = checkpoint.read_bytes()
                    body_path.write_bytes(before_body + b" ")
                    try:
                        r.locator("#confirm").click()
                        f.idle()
                        assert body_path.read_bytes() == before_body + b" "
                        assert graph_path.read_bytes() == x.physical[graph_path] and checkpoint.read_bytes() == saved
                    finally:
                        body_path.write_bytes(before_body)
                    if r.is_visible():
                        r.locator("[data-reject]").click()
                    r = review()
                confirm(r)
                original_except_pair(expected_case())
                x.build("scope-in-case", *output("case"))
                restart_drag(3)
                folded()
                assert_view(root_moved, branch_old + ["move"])
                f.checked("graph and original node digest move together through Save, history, Review and execution")

                if mode == "normal":
                    drag_placement(cell("pre"), "before", "root", cancel=True)
                    assert_view(root_moved, branch_old + ["move"])
                    drag_placement(cell("pre"), "before", "root")
                    assert_view(["move", "pre", "choose", "body", "after"], branch_old)
                    local_undo()
                    assert_view(root_moved, branch_old + ["move"])
                    drag_placement(cell("body"), "after", "root", picture=True)
                    assert_view(["pre", "choose", "body", "move", "after"], branch_old)
                    local_undo()
                    assert_view(root_moved, branch_old + ["move"])
                    drag_placement(cell("pre"), "before", "root")
                    assert_view(["move", "pre", "choose", "body", "after"], branch_old)
                    save()
                    assert not pending()
                    confirm(review())
                    original_except_pair(expected_root_entry())
                    assert body_path.read_bytes() == before_body
                    x.build("scope-before-switch", *output("entry"))
                    restart_drag(4)
                    assert_view(["move", "pre", "choose", "body", "after"], branch_old)
                    f.checked("reverse placement before a root cell and after the fixed continuation; the confirmed prefix executes the moved cell on both paths")
            f.page.screenshot(path=str(f.case / f"scope-transfer-{mode}.png"))
            assert not f.errors and not f.external, (f.errors, f.external)
        except BaseException:
            if not f.page.is_closed():
                (f.case / "scope-failure.html").write_text(f.page.content())
                (f.case / "scope-errors.json").write_text(json.dumps(f.errors, ensure_ascii=False))
                f.page.screenshot(path=str(f.case / "scope-failure.png"), timeout=10000)
            raise
        finally:
            f.browser.close()
finally:
    (f.case / "scope-traffic.json").write_text(json.dumps(f.traffic, ensure_ascii=False))
    (f.case / "scope-checks.json").write_text(json.dumps(f.checks, ensure_ascii=False))
    f.stop()
print("V821_SCOPE_TRANSFER", mode, f.case, flush=True)
