"""Insert one void cell into an existing owned child case using the Linux editor."""
import ast
import subprocess
import sys
from pathlib import Path

scenario = sys.argv[3] if len(sys.argv) > 3 else "after"
assert scenario in {"start", "after", "shared"}
# Reuse the real editor fixture with the same local ID in a sibling. The
# after-anchor case also keeps a value dependency across the inserted cell.
fixture_file = Path(__file__).with_name("v821_child_case_order_ui.py")
setup = ast.parse(fixture_file.read_text()).body
original_argv = sys.argv
sys.argv = [*sys.argv[:3], {"start": "normal", "after": "dependency", "shared": "shared"}[scenario]]
try:
    exec(compile(ast.Module(body=setup[:next(i for i, node in enumerate(setup) if isinstance(node, ast.Try))],
                            type_ignores=[]), str(fixture_file), "exec"), globals())
finally:
    sys.argv = original_argv

key = "documentFrameCaseOrderBinding"
anchor = "choose" if scenario == "start" else "positive"
anchor_port = "case:positive" if scenario == "start" else "next"
successor = "positive" if scenario == "start" else "tail"
new_body = 'global::System.Console.WriteLine("inserted-case");\nreturn;'


def proposal(data):
    name = "cell_candidate"
    binding = data.get(key) or dict(root=t.graph, graph=frame, path="body", rootHash="0" * 64, frameHash="0" * 64)
    return dict(action="authorBatch", id=frame, documentFrame=copy.deepcopy(binding), attempt=uuid.uuid4().hex,
                sourceProof=x.proof(data), checkpointHash=data["checkpointHash"], edits=[
                    dict(action="createNode", node=name, definition=dict(kind="code", control="next",
                         branchOwner="choose", intent="new cell", signature={"args": [], "return": "void"})),
                    dict(action="rename", node=name, text="새 동작"),
                    dict(action="intent", node=name, text="새 동작"),
                    dict(action="source", node=name, text=new_body),
                    dict(action="route", node=anchor, port=anchor_port, to=name),
                    dict(action="route", node=name, port="next", to=successor),
                ])


def edit_source(created):
    doc().locator(f'[data-document-code="{created}"]').click()
    dialog = f.page.locator(".bp-script-dialog")
    body = dialog.locator("[data-code-region=body]").text_content()
    area = dialog.locator("[data-code-source]")
    area.evaluate('(el,text)=>{el.focus();const at=el.value.indexOf(text);if(at<0)throw Error("Missing body");el.setSelectionRange(at,at+text.length)}', body)
    f.page.keyboard.insert_text(new_body)
    dialog.locator("[data-code-save]").click()
    f.idle()


def new_files():
    return [p for p in f.project.rglob("*.node.json") if p not in x.physical and ".confectory" not in p.parts]


def pure_denied(graph, edits):
    try:
        f.metadata("blueprintCellRegion", action="frame-case-create", graph=graph, path="body", edits=edits)
    except (AssertionError, subprocess.CalledProcessError):
        return
    raise AssertionError("Unsupported insertion retained metadata authority")


try:
    x.build("case-before-insert", 14, output())
    f.start(0)
    f.invoke("select", dict(id=t.feature))
    f.invoke("saveDraft", {})
    checkpoint = next(f.project.glob(".confectory/edit-workspaces/*/draft.json"))
    before = checkpoint.read_bytes()
    baseline = read()
    peer_before = read(other)["nodes"]
    with sync_playwright() as pw:
        expect.set_options(timeout=45000)
        f.browser = pw.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
        f.page = f.setup()
        f.page.set_viewport_size(dict(width=1800, height=1400))
        open_document()
        enter_body()
        branch = order(initial)
        button = branch.locator("[data-document-branch-add]" if scenario == "start" else "[data-document-add=positive]")
        if scenario == "shared":
            expect(button).to_be_disabled()
            assert not baseline.get("documentFrameCaseCreationAvailable")
            pure_denied(root, proposal(baseline)["edits"])
            f.invoke("blueprint", proposal(baseline), False)
            assert checkpoint.read_bytes() == before and not pending() and not new_files()
            x.original()
            f.checked("shared entry refuses the insertion in the actual editor and the full-frame planner")
        else:
            expect(button).to_be_enabled()
            assert baseline["documentFrameCaseCreationAvailable"]
            q = proposal(baseline)
            f.metadata("blueprintCellRegion", action="frame-case-create", graph=root, path="body", edits=q["edits"])
            # An empty explicit case remains outside the existing child switch contract.
            empty = copy.deepcopy(root)
            empty_child = empty["nodes"][0]["graph"]
            empty_child["nodes"] = [node for node in empty_child["nodes"] if node["id"] not in initial]
            empty_child["edges"] = [route for route in empty_child["edges"] if route["from"] not in initial]
            next(route for route in empty_child["edges"] if route["port"] == "case:positive")["to"] = "return:choose"
            pure_denied(empty, q["edits"])
            button.click()
            f.idle()
            created = branch.locator("[data-document-cell^=cell_]").get_attribute("data-document-cell")
            assert created
            expected_order = [*initial]
            expected_order.insert(0 if scenario == "start" else 1, created)
            order(expected_order)
            assert len(pending()) == 6 and not new_files()
            local_undo()
            order(initial)
            assert not pending()
            local_undo(True)
            order(expected_order)
            edit_source(created)
            held = pending()
            assert len(held) == 6 and any(value["text"] == new_body for _, value in held)
            restart_child(1)
            order(expected_order)
            assert pending() == held and read(other)["nodes"] == peer_before
            assert checkpoint.read_bytes() == before and not new_files()
            x.original()
            f.checked("both UI and planner preserve the existing case; local Undo/Redo and cold restore retain the new body and all six edits")

            for fault in ("path", "args", "exit"):
                wrong = proposal(read())
                if fault == "path":
                    wrong["documentFrame"]["path"] = "peer"
                elif fault == "args":
                    wrong["edits"][0]["definition"]["signature"]["args"] = [dict(name="amount", type="int")]
                else:
                    wrong["edits"][-1]["to"] = "exit:return"
                f.invoke("blueprint", wrong, False)
                assert checkpoint.read_bytes() == before and pending() == held and not new_files()

            peer_file = f.project / peer["implementation"]
            raw = peer_file.read_bytes()
            peer_file.write_bytes(raw + b" ")
            try:
                save()
                assert retained(held) and checkpoint.read_bytes() == before and read()["edges"] == baseline["edges"]
                assert peer_file.read_bytes() == raw + b" " and not new_files()
            finally:
                peer_file.write_bytes(raw)
            save()
            assert not pending() and not new_files()
            owned_id = t.graph + "/node:body/node:" + created
            saved = json.loads(checkpoint.read_text())
            assert {row["id"] for row in saved["changes"]} == {t.graph, owned_id}
            node = next(row for row in read()["nodes"] if row["id"] == created)
            assert node["sourceId"] == owned_id and node["source"] == new_body
            history = f.invoke("draftHistory", dict(action="inspect"))["result"]["result"]
            assert history["boundary"] == "OWNERSHIP_CHANGED" and not history["undo"]["available"] and not history["redo"]["available"]
            restart_child(2)
            order(expected_order)
            assert read(other)["nodes"] == peer_before and not new_files()
            x.original()
            f.checked("stale sibling source refuses Save, then one checkpoint records only the graph and full-path new source with the existing shared history boundary")

            review_window = review()
            saved_bytes = checkpoint.read_bytes()
            peer_file.write_bytes(raw + b" ")
            try:
                review_window.locator("#confirm").click()
                f.idle()
                assert checkpoint.read_bytes() == saved_bytes and graph_path.read_bytes() == x.physical[graph_path]
                assert peer_file.read_bytes() == raw + b" " and not new_files()
            finally:
                peer_file.write_bytes(raw)
            if review_window.is_visible():
                review_window.locator("[data-reject]").click()
            review_window = review()
            review_window.locator("#confirm").click()
            expect(review_window).to_be_hidden(timeout=120000)
            f.idle()
            confirmed = json.loads(graph_path.read_text())
            expected = copy.deepcopy(root)
            selected = expected["nodes"][0]["graph"]
            added = confirmed["nodes"][0]["graph"]["nodes"][-1]
            assert added["id"] == created and added["branchOwner"] == "choose"
            assert added["signature"] == {"args": [], "return": "void"}
            selected["nodes"].append(added)
            next(route for route in selected["edges"] if (route["from"], route["port"]) == (anchor, anchor_port))["to"] = created
            selected["edges"].append(edge(created, successor))
            assert confirmed == expected and all(p.read_bytes() == raw for p, raw in x.physical.items() if p != graph_path)
            files = new_files()
            assert len(files) == 1 and json.loads(files[0].read_text())["source"] == new_body
            output_lines = output().splitlines()
            output_lines.insert(output_lines.index("positive:7") + (scenario == "after"), "inserted-case")
            x.build("confirmed-child-case-insert", 14, "\n".join(output_lines))
            restart_child(3)
            order(expected_order)
            assert not pending()
            f.checked("Confirm protects sibling originals, then writes only the new source and selected routes; both cases and the primary path rebuild and execute in order")

        f.page.screenshot(path=str(f.case / f"child-case-insert-{scenario}.png"), full_page=True)
        assert not f.errors and not f.external, (f.errors, f.external)
        f.browser.close()
finally:
    (f.case / "child-case-insert-traffic.json").write_text(json.dumps(f.traffic, ensure_ascii=False))
    print("V821_CHILD_CASE_INSERT", scenario, f.case, flush=True)
    f.stop()
