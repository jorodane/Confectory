"""Actual mouse transfer across two case tabs with real engine execution and Save."""
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
assert mode in {"normal", "empty", "value", "shared", "readonly", "start"}
graph_path = f.project / t.graph_file


def load_helpers(filename):
    path = Path(__file__).with_name(filename)
    methods = [node for node in ast.parse(path.read_text()).body if isinstance(node, ast.FunctionDef)]
    exec(compile(ast.Module(body=methods, type_ignores=[]), str(path), "exec"), globals())


load_helpers("v821_function_document_ui.py")
load_helpers("v821_cell_drag_ui.py")


def edge(start, end, port="next"):
    return {"from": start, "port": port, "to": end}


def code(name, args=(), owner=None):
    node = dict(
        id=name, kind="code", control="next", intent=name, implementation=f"Pair.{name}.node.json",
        signature={"args": [dict(name=arg, type="int") for arg in args], "return": "void"},
        arguments={arg: {"input": arg} for arg in args},
    )
    if owner:
        node["branchOwner"] = owner
    return node


def prepare_project():
    graph = copy.deepcopy(t.definition)
    graph.update(profile="sync-acyclic-switch-v1", entry="choose")
    choose = code("choose", ("amount",))
    choose.update(control="switch", executionEnum={
        "primary": "next",
        "members": [
            {"id": "next", "name": "None", "value": 0},
            {"id": "positive", "name": "Positive", "value": 1},
            {"id": "negative", "name": "Negative", "value": 2},
        ],
    })
    move_node = code("move", ("amount",) if mode == "value" else (), "choose")
    left = code("left", owner="choose")
    graph["nodes"] += [choose, move_node, left]
    right = code("right", owner="choose")
    if mode not in {"empty", "shared"}:
        graph["nodes"].append(right)
    negative = "exit:early" if mode == "empty" else "move" if mode == "shared" else "right"
    graph["edges"] += [
        edge("choose", "body"), edge("choose", "move", "case:positive"),
        edge("choose", negative, "case:negative"),
        edge("move", "left"), edge("left", "return:choose"),
    ]
    graph["exits"]["early"] = {"constant": 41}
    if negative == "right":
        graph["edges"].append(edge("right", "exit:early"))
    elif mode == "shared":
        # Keep the unused negative terminal out of the existing shared runtime.
        del graph["exits"]["early"]
    definitions = f.metadata("featureBlueprintNodes", featureSource=t.base.function, graph=graph)
    assert definitions["state"] == "node-definitions", definitions
    hashes = {row["id"]: row["definitionHash"] for row in definitions["nodes"]}
    bodies = {
        "choose": "return amount > 0 ? Result.Positive : Result.Negative;",
        "move": '// 보존될 원문 😀\r\nglobal::System.Console.WriteLine("moved");\r\n',
        "left": 'global::System.Console.WriteLine("left");',
        "right": 'global::System.Console.WriteLine("right");',
    }
    for node in graph["nodes"]:
        name = node["id"]
        path = f.project / node["implementation"]
        record = json.loads(path.read_text()) if path.exists() else dict(schema=1, node=name, source=bodies[name])
        record["definitionHash"] = hashes[name]
        path.write_text(json.dumps(record, ensure_ascii=False))
    graph_path.write_text(json.dumps(graph, ensure_ascii=False))
    (f.project / "Main.csbody").write_text(
        'int sum=0;foreach(int value in new[]{7,-2}){int result=calls.Pair.Invoke(value);'
        'global::System.Console.WriteLine("result:"+result);sum+=result;}return sum;'
    )
    if mode == "readonly":
        graph_path.chmod(0o444)
    return graph


def expected_output(transferred=False):
    positive = [] if transferred else ["moved"]
    positive += ["left", "body", "after", "result:10"]
    negative = [] if mode == "empty" else ["right"]
    if mode == "shared":
        return 11, "\n".join(positive + ["moved", "left", "body", "after", "result:1"])
    if transferred:
        negative.insert(0 if mode == "start" else len(negative), "moved")
    return 51, "\n".join(positive + negative + ["result:41"])


def case_tab(name):
    return doc().locator(f'[data-document-branch="case:{name}"][data-document-owner=choose]')


def case_order(name):
    case_tab(name).click()
    pane = doc().locator(f'[data-document-panel="case:{name}"]')
    return pane.locator(":scope>[data-document-cell]").evaluate_all(
        '(els)=>els.map(e=>e.dataset.documentCell).filter(id=>!id.startsWith("$"))'
    )


def assert_cases(positive, negative):
    expect(case_tab("positive")).to_be_visible()
    assert case_order("positive") == positive
    assert case_order("negative") == negative


def drag_to_case(destination, allowed, cancel=False, screenshot=False):
    start_drag("move")
    tab = case_tab(destination)
    bounds = tab.bounding_box()
    assert bounds
    x_pos = bounds["x"] + bounds["width"] / 2
    y_pos = bounds["y"] + bounds["height"] / 2
    f.page.mouse.move(x_pos + 3, y_pos, steps=15)
    f.page.mouse.move(x_pos, y_pos, steps=3)
    f.page.wait_for_timeout(350)
    marker = f.page.locator(".fd-cell-drop-marker[data-branch-transfer]")
    expect(marker).to_have_count(int(allowed), timeout=3000)
    if allowed:
        expect(marker).to_have_text("분기 끝에 놓기")
        if mode == "start" and destination == "negative":
            pane=doc().locator('[data-document-panel="case:negative"]')
            expect(pane).to_be_visible()
            target=pane.locator(':scope>[data-document-cell="right"]');box=target.bounding_box();assert box
            f.page.mouse.move(box['x']+box['width']/2,box['y']+box['height']*.25,steps=15)
            expect(marker).to_have_text("분기 안에 놓기")
        if screenshot:
            f.page.screenshot(path=str(f.case / "case-transfer-placement.png"))
    if cancel:
        f.page.keyboard.press("Escape")
    f.page.mouse.up()
    f.idle()
    expect(marker).to_have_count(0)


def sources_unchanged(allow_graph=False):
    for path, raw in x.physical.items():
        if not allow_graph or path != graph_path:
            assert path.read_bytes() == raw
        assert stat.S_IMODE(path.stat().st_mode) == modes[path]


def expected_edges(destination_has_right):
    edges = copy.deepcopy(original["edges"])
    routes = {(row["from"], row["port"]): row for row in edges}
    routes["choose", "case:positive"]["to"] = "left"
    routes["move", "next"]["to"] = "exit:early"
    if mode == "start":
        routes["choose", "case:negative"]["to"] = "move"
        routes["move", "next"]["to"] = "right"
    elif destination_has_right:
        routes["right", "next"]["to"] = "move"
    else:
        routes["choose", "case:negative"]["to"] = "move"
    return edges


original = prepare_project()
x.physical = {p: p.read_bytes() for p in f.project.rglob("*") if p.is_file() and ".confectory" not in p.parts}
modes = {path: stat.S_IMODE(path.stat().st_mode) for path in x.physical}
supported = mode in {"normal", "empty", "start"}
negative = [] if mode == "empty" else ["right"]
negative_after = ["move"] + negative if mode == "start" else negative + ["move"]
try:
    x.build("before-transfer", *expected_output())
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
            start = t.read()
            folded()
            assert case_order("positive") == ["move", "left"]
            capability = start["documentBranchTransfer"]
            if not supported:
                assert capability is None or "move" not in capability["movable"]
                if grip("move").is_enabled():
                    drag_to_case("negative", False)
                else:
                    expect(grip("move")).to_be_disabled()
                assert case_order("positive") == ["move", "left"]
                assert not pending() and t.read()["edges"] == start["edges"] and checkpoint.read_bytes() == before
                sources_unchanged()
                f.checked(f"{mode} condition cannot move the cell or change any input, routes or original source")
            else:
                assert capability["owner"] == "choose" and "move" in capability["movable"]
                drag_to_case("negative", True, cancel=True)
                assert_cases(["move", "left"], negative)
                assert not pending()
                case_tab("positive").click()
                drag_to_case("negative", True, screenshot=True)
                assert_cases(["left"], negative_after)
                held = pending()
                assert len(held) == len(negative) + 4
                assert checkpoint.read_bytes() == before
                sources_unchanged()
                local_undo()
                assert_cases(["move", "left"], negative)
                assert not pending()
                local_undo(True)
                assert_cases(["left"], negative_after)
                assert pending() == held
                restart_drag(1)
                assert_cases(["left"], negative_after)
                assert pending() == held
                f.checked("mouse transfer including target marker and Escape is one local Undo/Redo step and survives reopening")

                if mode == "normal":
                    checkpoint.chmod(0o400)
                    try:
                        save()
                        assert retained(held) and checkpoint.read_bytes() == before
                        sources_unchanged()
                    finally:
                        checkpoint.chmod(0o600)
                save()
                assert not pending()
                wanted = expected_edges(bool(negative))
                assert t.read()["nodes"] == start["nodes"] and t.read()["edges"] == wanted
                sources_unchanged()
                for direction, expected in [("undo", original["edges"]), ("redo", wanted)]:
                    history = f.invoke("draftHistory", dict(action="inspect"))["result"]["result"]
                    assert history[direction]["available"]
                    assert f.invoke("draftHistory", dict(action=direction, token=history[direction]["token"]))["result"]["result"]["accepted"]
                    assert t.read()["edges"] == expected
                f.invoke("saveDraft", {})
                restart_drag(2)
                folded()
                assert_cases(["left"], negative_after)
                assert not pending()
                drag_to_case("positive", True)
                assert_cases(["left", "move"], negative)
                local_undo()
                assert_cases(["left"], negative_after)
                assert not pending()
                f.checked("checkpoint Save and shared history are atomic; real reverse gesture is available and can be undone")

                if mode == "normal":
                    r = review()
                    r.locator("[data-reject]").click()
                    sources_unchanged()
                    r = review()
                    source = f.project / "Pair.move.node.json"
                    raw, saved = source.read_bytes(), checkpoint.read_bytes()
                    source.write_bytes(raw + b" ")
                    try:
                        r.locator("#confirm").click()
                        f.idle()
                        assert source.read_bytes() == raw + b" " and checkpoint.read_bytes() == saved
                        assert graph_path.read_bytes() == x.physical[graph_path]
                    finally:
                        source.write_bytes(raw)
                    if r.is_visible():
                        r.locator("[data-reject]").click()
                r = review()
                r.locator("#confirm").click()
                expect(r).to_be_hidden(timeout=120000)
                f.idle()
                confirmed = copy.deepcopy(original)
                confirmed["edges"] = wanted
                assert json.loads(graph_path.read_text()) == confirmed
                sources_unchanged(allow_graph=True)
                x.build("after-transfer", *expected_output(transferred=True))
                restart_drag(3)
                assert_cases(["left"], negative_after)
                assert not pending()
                f.checked("both case outcomes keep their original terminals and bindings; the moved source, ID and every other original stay intact")
            f.page.screenshot(path=str(f.case / f"case-transfer-{mode}.png"))
            assert not f.errors and not f.external, (f.errors, f.external)
        except Exception:
            if f.page and not f.page.is_closed():
                (f.case / "failure.html").write_text(f.page.content())
                f.page.screenshot(path=str(f.case / "failure.png"), timeout=10000)
            raise
        finally:
            f.browser.close()
finally:
    (f.case / "transfer-traffic.json").write_text(json.dumps(f.traffic, ensure_ascii=False))
    (f.case / "transfer-checks.json").write_text(json.dumps(f.checks, ensure_ascii=False))
    f.stop()
print("V821_CASE_TRANSFER", mode, f.case, flush=True)
