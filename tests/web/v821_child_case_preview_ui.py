"""Desktop preview for a direct switch child using the Linux editor and emitter."""
import ast
import hashlib
import sys
from pathlib import Path

scenario = sys.argv[3] if len(sys.argv) > 3 else "normal"
assert scenario in {"normal", "shared", "alias"}
fixture = Path(__file__).with_name("v821_child_case_order_ui.py")
nodes = ast.parse(fixture.read_text()).body
argv = sys.argv
sys.argv = [*argv[:3], "shared" if scenario == "shared" else "normal"]
try:
    start = next(i for i, node in enumerate(nodes) if isinstance(node, ast.Try))
    exec(compile(ast.Module(body=nodes[:start], type_ignores=[]), str(fixture), "exec"), globals())
finally:
    sys.argv = argv

source_path = f.project / "Pair.tail.node.json"
record = json.loads(source_path.read_text())
record.update(helpers='private static string TailLabel(int n) => "tail:" + n;',
              source="global::System.Console.WriteLine(TailLabel(amount));")
source_path.write_text(json.dumps(record))
if scenario == "alias":
    header = f.project / "PairBody.celem"
    declaration = header.read_text()
    common = f'blueprint common "{t.graph_file}";'
    assert common in declaration
    header.write_text(declaration.replace(common, common + f' blueprint windows "{t.graph_file}";', 1))
x.physical = {path: path.read_bytes() for path in f.project.iterdir() if path.is_file()}


def native():
    panel().get_by_role("tab", name="네이티브 미리보기", exact=True).click()
    return panel().locator(".function-native-preview")


def logic():
    panel().get_by_role("tab", name="논리 코드", exact=True).click()
    expect(doc()).to_be_visible()


def shown(view, expected):
    expect(view.locator("[role=status]")).to_contain_text("생성됨", timeout=90000)
    for key in ("body", "members"):
        field = view.locator(f"[data-native-{key}]")
        expect(field).to_have_text(expected[key], use_inner_text=False)
        assert field.text_content() == expected[key]
    assert not view.locator("textarea,input,[contenteditable=true]").count()


def empty(view, status):
    expect(view.locator("[role=status]")).to_contain_text(status)
    assert not view.locator("[data-native-body]").text_content()
    assert not view.locator("[data-native-members]").text_content()


def preserved():
    assert all(path.read_bytes() == raw for path, raw in x.physical.items())
    assert checkpoint.read_bytes() == before
    assert history == f.invoke("draftHistory", dict(action="inspect"))["result"]["result"]


def enter_peer():
    panel().locator(".bp-breadcrumbs button").first.click()
    f.idle()
    button = doc().locator('[data-document-internal="peer"]')
    if not button.is_visible():
        doc().locator('[data-document-fold="peer"][aria-expanded=false]').click()
    button.click()
    f.idle()
    expect(doc().locator('[data-document-cell="positive"]')).to_be_visible()


try:
    x.build("switch-preview-baseline", 14, output())
    f.start(0)
    f.invoke("select", dict(id=t.feature))
    f.invoke("saveDraft", {})
    checkpoint = next(f.project.glob(".confectory/edit-workspaces/*/draft.json"))
    before = checkpoint.read_bytes()
    history = f.invoke("draftHistory", dict(action="inspect"))["result"]["result"]
    selection = read()
    binding = selection.get("documentFramePreviewBinding")
    with sync_playwright() as pw:
        expect.set_options(timeout=45000)
        f.browser = pw.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
        f.page = f.setup()
        f.page.set_viewport_size(dict(width=1800, height=1400))
        open_document()
        enter_body()
        expect(select_case("positive").locator('[data-document-cell="positive"]')).to_be_visible()
        if scenario != "shared":
            expect(select_case("negative").locator('[data-document-cell="negative"]')).to_be_visible()
        if scenario != "normal":
            assert binding is None
            empty(native(), "지원하지")
            preserved()
            f.checked(f"{scenario} scope has no native preview in the actual editor and preserves all original input")
        else:
            assert (binding["root"], binding["graph"], binding["path"]) == (t.graph, frame, "body")
            assert selection["documentFrameOrderBinding"] is None
            query = dict(action="nativePreview", id=frame, documentFrame=binding, sourceProof=x.proof(selection),
                         checkpointHash=selection["checkpointHash"])
            preview = f.invoke("blueprint", query)["result"]["result"]
            result = preview["diagnostics"]
            assert preview["documentFramePreviewBinding"] == binding and not preview["sourceWritten"]
            assert set(result) == {"state", "body", "members", "bodyHash", "assembledPath"}
            assert result["state"] == "source-assembled" and result["assembledPath"] == "body"
            assert hashlib.sha256((result["body"] + result["members"]).encode()).hexdigest() == result["bodyHash"]
            assert all(text in result["body"] for text in ("case 1:", "case 2:", "default:"))
            assert all(text in result["members"] for text in ('"positive:"', '"negative:"', '"finish:"', "TailLabel"))
            assert result["members"].count("private static class __fg_methods_") == len(child["nodes"])
            assert all(text not in json.dumps(preview) for text in ('WriteLine(\\"peer', 'WriteLine(\\"after'))
            whole = f.invoke("blueprint", dict(action="nativePreview", id=t.graph))["result"]["result"]["diagnostics"]
            assert result["body"] in whole["body"] and result["members"] in whole["members"]
            assert 'WriteLine("peer")' in whole["body"] and 'WriteLine("after")' in whole["body"]
            for wrong in (dict(id=other), dict(sourceProof="[]"), dict(checkpointHash="0" * 64),
                          dict(documentFrame=dict(binding, path="peer")), dict(uiSurface="view:1")):
                refusal = f.invoke("blueprint", dict(query, **wrong), False)["result"]
                assert not refusal.get("result")
            shown(native(), result)
            preserved()
            f.checked("selected branch body and helper members match the actual root assembly; wrong scope and observation are refused")

            view = panel().locator(".function-native-preview")
            peer_file = f.project / peer["implementation"]
            raw = peer_file.read_bytes()
            peer_file.write_bytes(raw + b" ")
            try:
                view.locator("[data-native-refresh]").click()
                empty(view, "생성에 실패")
                assert peer_file.read_bytes() == raw + b" " and checkpoint.read_bytes() == before
            finally:
                peer_file.write_bytes(raw)
            view.locator("[data-native-refresh]").click()
            shown(view, result)
            logic()
            enter_peer()
            assert read(other)["nodes"][0]["id"] == "positive"
            empty(native(), "지원하지")
            logic()
            panel().locator(".bp-breadcrumbs button").first.click()
            f.idle()
            enter_body()
            order(initial)
            shown(native(), result)
            preserved()
            f.checked("a same-ID sibling does not receive the selected branch output; source drift clears both preview panes")

            requests, paused = set(), {}

            def hold(route):
                message = route.request.post_data_json
                if (message.get("op") == "invoke" and message.get("endpoint") == "blueprint"
                        and message.get("input", {}).get("action") == "nativePreview"):
                    requests.add(message["requestId"])
                response = route.fetch()
                payload = response.json()
                if (not paused and message.get("op") == "update"
                        and any(row.get("requestId") in requests for row in payload.get("results", []))):
                    paused.update(route=route, response=response, payload=payload)
                    return
                route.fulfill(response=response)

            f.page.route("**/api/request", hold)
            view.locator("[data-native-refresh]").click()
            deadline = time.monotonic() + 90
            while not paused and time.monotonic() < deadline:
                f.page.wait_for_timeout(30)
            assert paused
            logic()
            doc().locator('[data-document-name="tail"]').fill("늦은 응답 중 입력 α")
            doc().locator(".fd-document-title").click()
            empty(native(), "저장하지 않은 입력")
            paused["route"].fulfill(response=paused["response"], json=paused["payload"])
            f.page.unroute_all(behavior="wait")
            f.idle()
            held = pending()
            assert "늦은 응답 중 입력 α" in json.dumps(held, ensure_ascii=False)
            empty(view, "저장하지 않은 입력")
            preserved()
            f.pending()
            f.page.close()
            f.stop()
            f.start(1)
            f.page = f.setup()
            f.page.set_viewport_size(dict(width=1800, height=1400))
            f.idle()
            assert pending() == held
            empty(panel().locator(".function-native-preview"), "저장하지 않은 입력")
            preserved()
            x.build("switch-preview-unchanged", 14, output())
            f.checked("late real emitter response cannot replace unsaved input; cold input and all three execution paths are intact")
        assert not f.errors and not f.external, (f.errors, f.external)
        f.browser.close()
finally:
    (f.case / "switch-preview-traffic.json").write_text(json.dumps(f.traffic, ensure_ascii=False))
    print("V821_CHILD_CASE_PREVIEW", scenario, f.case, flush=True)
    f.stop()
