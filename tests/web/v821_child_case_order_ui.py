"""Actual Linux editor and engine for one case inside a directly owned compound."""
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
test_mode = sys.argv[3] if len(sys.argv) > 3 else "normal"
assert test_mode in {"normal", "dependency", "shared"}
mode = "shared" if test_mode == "shared" else "normal"
fixture = Path(__file__).with_name("v821_switch_compound_drag_ui.py")
methods = [node for node in ast.parse(fixture.read_text()).body if isinstance(node, ast.FunctionDef)]
exec(compile(ast.Module(body=methods, type_ignores=[]), str(fixture), "exec"), globals())
load_helpers("v821_function_document_ui.py")
load_helpers("v821_cell_drag_ui.py")

graph_path = f.project / t.graph_file
root = prepare_project()
child = root["nodes"][0]["graph"]
positive = next(node for node in child["nodes"] if node["id"] == "positive")
tail = code("tail", ("amount",), owner="choose")
child["nodes"].append(tail)
next(route for route in child["edges"] if route["from"] == "positive")["to"] = "tail"
child["edges"].append(edge("tail", "return:choose"))
if test_mode == "dependency":
    positive["signature"]["return"] = "int"
    tail["arguments"]["amount"] = {"node": "positive"}
if mode != "shared":
    child["nodes"].append(code("negativeTail", ("amount",), owner="choose"))
    next(route for route in child["edges"] if route["from"] == "negative")["to"] = "negativeTail"
    child["edges"].append(edge("negativeTail", "return:choose"))

peer = code("positive")
peer["implementation"] = "Pair.peer.positive.node.json"
root["nodes"].insert(1, {
    "id": "peer", "kind": "graph", "control": "next", "intent": "peer",
    "signature": {"args": [], "return": "void"}, "arguments": {},
    "graph": dict(schema=1, profile="sync-acyclic-nested-v1", entry="positive",
                  nodes=[peer], edges=[edge("positive", "exit:return")], exits={"return": None}),
})
root["edges"] = [edge("body", "peer"), edge("peer", "after"), edge("after", "exit:return")]

definitions = f.metadata(
    "blueprintDescribeOwned", project=str(f.manifest), id=f.n + "PairBody",
    text=(f.project / "PairBody.celem").read_text(), bodyTarget="common", graph=root, definitionsOnly=True,
)
assert definitions["state"] == "node-definitions", definitions
hashes = {node["id"]: node["definitionHash"] for node in definitions["nodes"] + definitions["nestedNodes"]}
updated_sources = {
    "body/choose": "return amount == 0 ? Result.None : amount > 0 ? Result.Positive : Result.Negative;",
    "body/tail": 'global::System.Console.WriteLine("tail:"+amount);',
    "body/negativeTail": 'global::System.Console.WriteLine("negativeTail:"+amount);',
    "peer/positive": 'global::System.Console.WriteLine("peer");',
}
for path, node in [("body/" + row["id"], row) for row in child["nodes"]] + [("peer/positive", peer), ("after", root["nodes"][-1])]:
    file = f.project / node["implementation"]
    source = updated_sources[path] if path in updated_sources else json.loads(file.read_text())["source"]
    if path == "body/positive" and test_mode == "dependency":
        source += "return amount;"
    file.write_text(json.dumps(dict(schema=1, node=node["id"], definitionHash=hashes[path], source=source), ensure_ascii=False))
graph_path.write_text(json.dumps(root, ensure_ascii=False))
main = f.project / "Main.csbody"
main.write_text(main.read_text().replace("new[]{7,-2}", "new[]{7,-2,0}"))
x.physical = {path: path.read_bytes() for path in f.project.iterdir() if path.is_file()}
frame = t.graph + "/graph:body"
other = t.graph + "/graph:peer"
key = "documentFrameCaseOrderBinding"
initial = ["positive", "tail"]
moved = ["tail", "positive"]


def read(id=frame):
    return f.invoke("blueprint", dict(action="read", id=id))["result"]["result"]


def enter_body():
    if doc().locator('[data-document-cell="choose"]').is_visible():
        return
    tab = doc().locator('[data-document-internal="body"]')
    if not tab.is_visible():
        doc().locator('[data-document-fold="body"][aria-expanded=false]').click()
    tab.click()
    f.idle()
    expect(doc().locator('[data-document-cell="choose"]')).to_be_visible()


def select_case(name="positive"):
    doc().locator(f'[data-document-branch="case:{name}"]').click()
    return doc().locator(f'[data-document-panel="case:{name}"]')


def order(expected):
    branch = select_case()
    expect(branch.locator("[data-document-cell]")).to_have_count(len(expected))
    assert branch.locator("[data-document-cell]").evaluate_all("(els)=>els.map(el=>el.dataset.documentCell)") == expected
    return branch


def restart_child(index):
    restart(index)
    enter_body()


def output(changed=False):
    result = []
    for value in (7, -2, 0):
        if value > 0 or value < 0 and mode == "shared":
            result.extend(f"{name}:{value}" for name in (moved if changed else initial))
        elif value < 0:
            result.extend([f"negative:{value}", f"negativeTail:{value}"])
        result.extend([f"finish:{value}", "peer", "after", f"result:{value + 3}"])
    return "\n".join(result)


def request(data, binding, port="case:positive", end="return:choose"):
    return dict(action="authorBatch", id=frame, documentFrame=copy.deepcopy(binding), attempt=uuid.uuid4().hex,
                sourceProof=x.proof(data), checkpointHash=data["checkpointHash"],
                edits=[dict(action="route", node="choose", port=port, to="tail"),
                       dict(action="route", node="tail", port="next", to="positive"),
                       dict(action="route", node="positive", port="next", to=end)])


try:
    x.build("original-child-cases", 14, output())
    f.start(0)
    f.invoke("select", dict(id=t.feature))
    f.invoke("saveDraft", {})
    checkpoint = next(f.project.glob(".confectory/edit-workspaces/*/draft.json"))
    before = checkpoint.read_bytes()
    baseline = read()
    peer_edges = read(other)["edges"]
    with sync_playwright() as pw:
        expect.set_options(timeout=45000)
        f.browser = pw.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
        f.page = f.setup()
        f.page.set_viewport_size(dict(width=1800, height=1400))
        open_document()
        enter_body()
        branch = order(initial)
        assert doc().locator("[data-document-branch]").all_text_contents() == ["Positive", "Negative"]
        for selector in ("[data-document-add=positive]", "[data-document-branch-add]"):
            button = expect(branch.locator(selector))
            if test_mode == "shared":
                button.to_be_disabled()
            else:
                button.to_be_enabled()
        move_up = branch.locator("[data-document-up=tail]")
        binding = baseline.get(key)
        if test_mode == "shared":
            assert binding is None
            expect(move_up).to_be_disabled()
            x.original()
            f.checked("shared case entry stays disabled in the actual editor; original switch still runs")
        elif test_mode == "dependency":
            assert binding
            move_up.click()
            f.idle()
            order(initial)
            assert not pending()
            f.invoke("blueprint", request(baseline, binding), False)
            assert read()["edges"] == baseline["edges"] and checkpoint.read_bytes() == before
            x.original()
            f.checked("value dependency refuses the move both in the editor and in the checked atomic plan")
        else:
            assert binding and (binding["root"], binding["graph"], binding["path"]) == (t.graph, frame, "body")
            assert baseline["documentFrameOrderBinding"] is None
            enlarge()
            folded()
            move("tail", "positive", capture=True)
            order(moved)
            local_undo()
            order(initial)
            assert not pending()
            doc().locator('[data-document-fold="tail"]').click()
            move_up.click()
            f.idle()
            order(moved)
            held = pending()
            assert len(held) == 3 and checkpoint.read_bytes() == before
            expect(select_case("negative").locator("[data-document-up=negativeTail]")).to_be_disabled()
            order(moved)
            doc().locator(".fd-document-title").click()
            doc().press("Control+z")
            order(initial)
            assert not pending()
            doc().press("Control+y")
            order(moved)
            assert pending() == held
            restart_child(1)
            order(moved)
            assert pending() == held and read(other)["edges"] == peer_edges
            x.original()
            f.checked("one case moves as a single local Undo/Redo record and survives cold with same-ID sibling unchanged")

            for port, end in [("case:negative", "return:choose"), ("case:positive", "exit:return")]:
                f.invoke("blueprint", request(read(), binding, port, end), False)
                assert checkpoint.read_bytes() == before and pending() == held
            wrong = request(read(), binding)
            wrong["documentFrame"]["path"] = "peer"
            f.invoke("blueprint", wrong, False)
            assert checkpoint.read_bytes() == before and pending() == held

            graph_mode = stat.S_IMODE(graph_path.stat().st_mode)
            graph_path.chmod(0o444)
            try:
                restart_child(10)
                order(moved)
                assert not read().get(key)
                expect(doc().locator('[data-document-down="tail"]')).to_be_disabled()
                mark = len(f.traffic)
                panel().locator("[data-bp-save]").click()
                f.idle()
                expect(panel().locator(".bp-status")).to_contain_text("자식 frame 저장 계획")
                assert not any(row.get("invoke", {}).get("input", {}).get("action") in
                               {"entry", "route", "serialRoutes", "authorBatch"} for row in f.traffic[mark:])
                assert retained(held) and checkpoint.read_bytes() == before
                x.original()
            finally:
                graph_path.chmod(graph_mode)
            restart_child(11)
            assert read()[key] == binding and retained(held)

            peer_file = f.project / peer["implementation"]
            original = peer_file.read_bytes()
            peer_file.write_bytes(original + b" ")
            try:
                save()
                assert retained(held) and checkpoint.read_bytes() == before
                assert peer_file.read_bytes() == original + b" " and read()["edges"] == baseline["edges"]
            finally:
                peer_file.write_bytes(original)
            save()
            assert not pending()
            saved = read()
            assert saved["edges"] != baseline["edges"] and read(other)["edges"] == peer_edges
            for direction, expected in [("undo", baseline["edges"]), ("redo", saved["edges"])]:
                history = f.invoke("draftHistory", dict(action="inspect"))["result"]["result"][direction]
                assert history["available"]
                assert f.invoke("draftHistory", dict(action=direction, token=history["token"]))["result"]["result"]["accepted"]
                assert read()["edges"] == expected and read(other)["edges"] == peer_edges
            f.invoke("saveDraft", {})
            restart_child(2)
            order(moved)
            x.original()
            f.checked("invalid paths and routes or a changed sibling source preserve drafts; shared Undo/Redo and cold retain the exact selected case")

            r = review()
            saved_checkpoint = checkpoint.read_bytes()
            peer_file.write_bytes(original + b" ")
            try:
                r.locator("#confirm").click()
                f.idle()
                assert peer_file.read_bytes() == original + b" " and checkpoint.read_bytes() == saved_checkpoint
                assert graph_path.read_bytes() == x.physical[graph_path]
            finally:
                peer_file.write_bytes(original)
            if r.is_visible():
                r.locator("[data-reject]").click()
            r = review()
            r.locator("#confirm").click()
            expect(r).to_be_hidden(timeout=120000)
            f.idle()
            expected = copy.deepcopy(root)
            changed_routes = {("choose", "case:positive"): "tail", ("tail", "next"): "positive",
                              ("positive", "next"): "return:choose"}
            for route in expected["nodes"][0]["graph"]["edges"]:
                route["to"] = changed_routes.get((route["from"], route["port"]), route["to"])
            assert json.loads(graph_path.read_text()) == expected
            assert all(path.read_bytes() == raw for path, raw in x.physical.items() if path != graph_path)
            x.build("confirmed-child-cases", 14, output(changed=True))
            restart_child(3)
            order(moved)
            assert not pending()
            f.checked("Confirm rechecks source observation, then changes only the case routes; both cases and the primary path execute with original continuation")

        f.page.screenshot(path=str(f.case / f"child-case-order-{test_mode}.png"), full_page=True)
        assert not f.errors and not f.external, (f.errors, f.external)
        f.browser.close()
except BaseException:
    if getattr(f, "page", None):
        try:
            f.page.screenshot(path=str(f.case / "child-case-order-failure.png"), timeout=10000)
        except Exception:
            pass
    raise
finally:
    (f.case / "child-case-order-traffic.json").write_text(json.dumps(f.traffic, ensure_ascii=False))
    print("V821_CHILD_CASE_ORDER", test_mode, f.case, flush=True)
    f.stop()
