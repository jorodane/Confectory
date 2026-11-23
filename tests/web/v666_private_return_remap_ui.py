"""Explicit private return retarget through the real Linux Blueprint editor."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

from playwright.sync_api import expect, sync_playwright

# The shared fixture needs its single direct return consumer in either direction.
mode = sys.argv[3] if len(sys.argv) > 3 else "return-argument-original"
nested = mode in ("nested", "nested-narrow")
narrow = mode in ("narrow", "nested-narrow")
sys.argv[3:4] = ["return-argument-original"]
import v666_private_node_out_double_fixture as fixture

original_type, selected_type = ("double", "long") if narrow else ("long", "double")
output_pin = "realOutput" if narrow else "secondNative"
before_value, after_value = (129.25, 99.5) if narrow else (129, 99)

f = fixture.f
frame_path = ("outer", "inner") if nested else ("inner",)
frame = fixture.whole_graph + "".join("/graph:" + cell for cell in frame_path)
producer_id = fixture.whole_graph + "".join("/node:" + cell for cell in (*frame_path, "body"))
peer_path = f.project / ("peer-sink.node.json" if nested else fixture.extra_path)
sink_path = f.project / "private-out-void-sink.node.json"
sink_record = json.loads(sink_path.read_text())
sink_record["source"] = 'global::System.Console.WriteLine("consumer:"+value.ToString(global::System.Globalization.CultureInfo.InvariantCulture));'
code_args = copy.deepcopy(fixture.code_signature["args"])
source = fixture.sources[fixture.whole_function]
authored = source.replace("return Keep(firstNative+secondNative);", "return Keep(firstNative+secondNative)+0D;")

if narrow:
    graph_path = f.project / fixture.graph_path
    graph = json.loads(graph_path.read_text())
    inner = next(node["graph"] for node in graph["nodes"] if node["id"] == "inner")
    code_args.append({"name": output_pin, "type": "double", "mode": "out"})
    inner["nodes"][0]["signature"] = {"args": code_args, "return": "double"}
    inner["nodes"][1]["signature"]["args"][0]["type"] = "double"
    graph_path.write_text(json.dumps(graph))
    definitions = f.metadata(
        "blueprintDescribeOwned", project=str(f.manifest), id=fixture.whole_implementation, text=fixture.whole_header.decode(),
        bodyTarget="common", graph=graph, definitionsOnly=True,
    )
    assert definitions["state"] == "node-definitions", definitions
    hashes = {node["id"]: node["definitionHash"] for node in definitions["nestedNodes"]}
    source = "secondNative=99; realOutput=99.5D; return Keep(firstNative+secondNative)+0.25D; // explicit narrowing fixture\n"
    authored = source.replace("return Keep(firstNative+secondNative)+0.25D;",
                              "return checked((long)(Keep(firstNative+secondNative)+0.25D));")
    path = f.project / fixture.node_path
    producer = json.loads(path.read_text())
    producer.update(definitionHash=hashes["inner/body"], source=source)
    path.write_text(json.dumps(producer))
    sink_record["definitionHash"] = hashes["inner/sink"]
    (f.project / "Main.csbody").write_text("""
long value=calls.SharedCaller.Invoke(30,5);
string? returnType=null;
var flags=global::System.Reflection.BindingFlags.Public|global::System.Reflection.BindingFlags.NonPublic
    |global::System.Reflection.BindingFlags.Static|global::System.Reflection.BindingFlags.DeclaredOnly;
foreach(var type in global::System.Reflection.Assembly.GetExecutingAssembly().GetTypes())
    foreach(var method in type.GetMethods(flags)){
        var pins=method.GetParameters();
        if(pins.Length!=3||pins[0].Name!="firstNative"||pins[2].Name!="realOutput")continue;
        if(!pins[2].IsOut||pins[2].ParameterType!=typeof(double).MakeByRefType())
            throw new global::System.InvalidOperationException("original double out changed");
        var kind=method.ReturnType==typeof(double)?"double":method.ReturnType==typeof(long)?"long":"unsupported";
        if(returnType is not null&&returnType!=kind)throw new global::System.InvalidOperationException("inconsistent private ABI");
        returnType=kind;
    }
if(returnType is null)throw new global::System.InvalidOperationException("private method missing");
global::System.Console.Error.WriteLine("private-out-return:"+returnType);
global::System.Console.WriteLine(value);
return checked((int)value);
""")

sink_path.write_text(json.dumps(sink_record))


def child_graph(graph, path=frame_path):
    for cell in path:
        graph = next(node["graph"] for node in graph["nodes"] if node["id"] == cell)
    return graph


def add_nested_frames():
    graph_file = f.project / fixture.graph_path
    graph = json.loads(graph_file.read_text())
    inner = graph["nodes"][1]
    outer = copy.deepcopy(inner)
    outer.update(id="outer", intent="Selected ancestor")
    inner["arguments"] = {arg["name"]: {"input": arg["name"]} for arg in outer["signature"]["args"]}
    outer["graph"] = {
        "schema": 1, "profile": "sync-acyclic-nested-v1", "nodes": [inner], "entry": "inner",
        "edges": [{"from": "inner", "port": "next", "to": "exit:return"}],
        "exits": {"return": {"node": "inner"}},
    }
    peer = copy.deepcopy(outer)
    peer.update(id="peer", intent="Sibling ancestor")
    body, sink = child_graph(peer["graph"], ("inner",))["nodes"]
    body["implementation"] = "peer-body.node.json"
    sink["implementation"] = peer_path.name
    body["signature"]["args"][0]["name"] = "peerNative"
    body["arguments"]["peerNative"] = body["arguments"].pop("firstNative")
    graph["nodes"][1:] = [outer, peer]
    graph["edges"][0]["to"] = "outer"
    graph["edges"][1].update({"from": "outer", "to": "peer"})
    graph["edges"].append({"from": "peer", "port": "next", "to": "exit:return"})
    graph["exits"]["return"]["node"] = "outer"
    graph_file.write_text(json.dumps(graph))
    definitions = f.metadata(
        "blueprintDescribeOwned", project=str(f.manifest), id=fixture.whole_implementation,
        text=fixture.whole_header.decode(), bodyTarget="common", graph=graph, definitionsOnly=True,
    )
    assert definitions["state"] == "node-definitions", definitions
    hashes = {node["id"]: node["definitionHash"] for node in definitions["nestedNodes"]}
    producer = json.loads((f.project / fixture.node_path).read_text())
    peer_producer = dict(producer, source=source.replace("firstNative", "peerNative"))
    peer_sink = dict(sink_record, source=f'if(value!={before_value})throw new System.InvalidOperationException("Sibling link changed");')
    for path, record, relative in (
        (f.project / fixture.node_path, producer, "outer/inner/body"),
        (sink_path, sink_record, "outer/inner/sink"),
        (f.project / body["implementation"], peer_producer, "peer/inner/body"),
        (peer_path, peer_sink, "peer/inner/sink"),
    ):
        path.write_text(json.dumps(dict(record, definitionHash=hashes[relative])))


if nested:
    add_nested_frames()
originals = {
    path: path.read_bytes() for path in f.project.rglob("*")
    if path.is_file() and ".confectory" not in path.relative_to(f.project).parts
}


def untouched():
    assert all(path.read_bytes() == data for path, data in originals.items())


def read(graph_id=frame):
    return f.invoke("blueprint", {"action": "read", "id": graph_id})["result"]["result"]


def source_proof(data):
    return json.dumps([[row["id"], row["revision"], row["hash"]] for row in data["sources"]])


def build(name, expected_consumer, expected_return):
    compilation = subprocess.run(
        [f.env["CONFECTORY_DOTNET"], str(f.repo / "src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll"),
         "build", str(f.manifest), "portable"],
        env=f.env, text=True, capture_output=True, check=True,
    )
    result = subprocess.run(json.loads(compilation.stdout)["run"], env=f.env, text=True, capture_output=True)
    (f.case / (name + ".json")).write_text(json.dumps({"stdout": result.stdout, "stderr": result.stderr}))
    assert result.returncode == 104, result
    assert result.stdout.splitlines() == [f"consumer:{expected_consumer}", "104"], result.stdout
    assert result.stderr.strip() == f"private-out-return:{expected_return}", result.stderr


def open_graph():
    f.idle()
    if not f.author().is_visible():
        f.page.locator("#workspace").click(button="right", position={"x": 1300, "y": 300})
        f.page.get_by_role("button", name="프로젝트 브라우저", exact=True).click()
        browser = f.page.locator('.window[data-key^="browser:project:"]')
        browser.get_by_role("button", name="기능", exact=True).click()
        browser.locator("[data-browser-control=object-query]").fill(fixture.whole_function.split("::")[-1])
        browser.locator("[data-browser-control=object-search]").click()
        browser.locator(f'[data-object="{fixture.whole_function}"]').press("Enter")
        browser.locator("[data-close]").first.click()
        f.idle()
        f.page.locator("[data-operation=feature-author-open]").first.click()
    panel = f.author()
    blueprint_tab = panel.get_by_role("tab", name="블루프린트 보기", exact=True)
    expect(blueprint_tab).to_be_visible()
    if not panel.locator(".bp-breadcrumbs").count():
        panel.get_by_role("tab", name="논리 코드", exact=True).click()
        document = panel.locator(".function-document")
        cell = frame_path[0]
        expect(document.locator(f'[data-document-cell="{cell}"]')).to_be_visible()
        button = document.locator(f'[data-document-internal="{cell}"]')
        if not button.is_visible():
            document.locator(f'[data-document-fold="{cell}"][aria-expanded=false]').click()
        button.click()
        f.idle()
    blueprint_tab.click()
    if nested and not panel.locator('[data-bp-node="body"]').count():
        panel.locator('[data-bp-node="inner"] [data-internal-flow]').click()
        f.idle()
        blueprint_tab.click()
    expect(panel.locator('[data-bp-node="body"]')).to_be_visible()
    return panel


def map_output(panel):
    panel.locator('[data-bp-node="body"] .bp-pin-plug[data-side=out][data-port="field:return"]')         .locator(".bp-pin-value").click(button="right")
    f.page.get_by_role("dialog", name="속성 타입 선택", exact=True).locator(f"[data-type={selected_type}]").click()
    dialog = f.page.get_by_role("dialog", name="반환 연결 갱신", exact=True)
    expect(dialog).to_be_visible()
    select = dialog.locator('[data-abi-output="return"]')
    expect(select).to_have_value("")
    assert select.locator("option").evaluate_all("(options)=>options.map(option=>option.value)") == ["", output_pin]
    return dialog


def review_in_editor(panel):
    panel.locator("[data-bp-complete]").click()
    f.idle()
    f.page.locator('.window[data-key="review"]:visible,.window[data-key="targets"]:visible').first.wait_for(timeout=90000)
    targets = f.page.locator('.window[data-key="targets"]')
    if targets.is_visible():
        targets.locator("[data-target-choice]").select_option("portable")
        targets.locator("[data-close]").click()
        panel.locator("[data-bp-complete]").click()
        f.idle()
    review = f.page.locator('.window[data-key="review"]')
    expect(review).to_be_visible()
    if review.locator("[data-review-advanced]").is_visible():
        review.locator("[data-review-advanced]").click()
    if review.locator("[data-advanced-reviewed]").count():
        review.locator("[data-advanced-reviewed]").check()
    expect(review.locator("#confirm")).to_be_enabled()
    return review


try:
    build("before", before_value, original_type)
    f.start(0)
    f.invoke("select", {"id": fixture.whole_function})
    f.invoke("saveDraft", {})
    checkpoint = next(f.project.glob(".confectory/edit-workspaces/*/draft.json"))
    baseline = checkpoint.read_bytes()
    initial = read()
    expected_choice = {"consumer": "sink", "argument": "value", "output": output_pin, "returnType": selected_type}
    assert initial["privateReturnChoices"] == {"body": expected_choice}, initial["diagnostics"]["state"]
    parameter_plan = {"args": code_args, "returnType": selected_type,
                      "remap": {arg["name"]: arg["name"] for arg in code_args}}
    wrong_output = "secondNative" if narrow else "return"
    edits = [
        {"action": "argument", "node": "sink", "name": "value",
         "valueJson": json.dumps({"node": "body", "output": wrong_output})},
        {"action": "parameters", "node": "body", "definition": parameter_plan},
        {"action": "source", "node": "body", "text": authored},
    ]
    request = {"action": "authorBatch", "id": frame, "checkpointHash": initial["checkpointHash"],
               "sourceProof": source_proof(initial)}
    if nested:
        producer = next(node for node in initial["nodes"] if node["id"] == "body")
        assert producer["sourceId"] == producer_id
        source_hash = next(row["hash"] for row in initial["sources"] if row["id"] == producer_id)
        request["privateBinding"] = {"graph": frame, "root": fixture.whole_graph, "node": "body",
                                     "source": producer_id, "definitionHash": producer["definitionHash"],
                                     "sourceHash": source_hash}
    wrong_type = copy.deepcopy(edits)
    wrong_type[0]["valueJson"] = json.dumps({"node": "body", "output": output_pin})
    wrong_type[1]["definition"]["returnType"] = "int"
    for rejected in (edits, edits[1:], wrong_type):
        f.invoke("blueprint", dict(request, attempt=uuid.uuid4().hex, edits=rejected), False)
        assert checkpoint.read_bytes() == baseline
        untouched()
    if nested:
        peer_frame = fixture.whole_graph + "/graph:peer/graph:inner"
        sibling = read(peer_frame)
        assert sibling["privateReturnChoices"] == {"body": expected_choice}
        peer_edits = copy.deepcopy(wrong_type)
        peer_edits[1]["definition"] = {"args": sibling["nodes"][0]["signature"]["args"],
                                       "returnType": selected_type,
                                       "remap": {arg["name"]: arg["name"] for arg in sibling["nodes"][0]["signature"]["args"]}}
        peer_edits[2]["text"] = authored.replace("firstNative", "peerNative")
        f.invoke("blueprint", dict(request, id=peer_frame, attempt=uuid.uuid4().hex,
                                   sourceProof=source_proof(sibling), edits=peer_edits,
                                   privateBinding=dict(request["privateBinding"], graph=peer_frame)), False)
        assert checkpoint.read_bytes() == baseline
        untouched()
        f.checked("An eligible sibling with identical local IDs rejects the selected frame's source binding.")
        valid_edits = copy.deepcopy(wrong_type)
        valid_edits[1]["definition"]["returnType"] = selected_type
        original_source = f.project / fixture.node_path
        stamp = original_source.stat()
        original_source.write_bytes(originals[original_source] + b"\n")
        try:
            f.invoke("blueprint", dict(request, attempt=uuid.uuid4().hex, edits=valid_edits), False)
            assert checkpoint.read_bytes() == baseline
            assert original_source.read_bytes() == originals[original_source] + b"\n"
            assert all(path == original_source or path.read_bytes() == data for path, data in originals.items())
        finally:
            original_source.write_bytes(originals[original_source])
            os.utime(original_source, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        f.checked("After the selected source changes on disk, a previously valid retarget cannot stage any of its three edits.")
    with_another_use = copy.deepcopy(json.loads(originals[f.project / fixture.graph_path]))
    child = child_graph(with_another_use)
    child["exits"]["return"] = {"node": "body"}
    assert not f.metadata("blueprintPrivateReturnChoices", graph=with_another_use, path="/".join(frame_path))
    f.checked("Wrong and missing selections and an unsupported return type fail closed; a second return use prevents eligibility.")

    with sync_playwright() as playwright:
        expect.set_options(timeout=60000)
        f.browser = playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
        f.page = f.setup()
        f.page.set_viewport_size({"width": 2200, "height": 1500})
        panel = open_graph()
        dialog = map_output(panel)
        dialog.locator("[data-abi-remap-accept]").click()
        expect(dialog.locator("[data-abi-error]")).to_be_visible()
        dialog.locator('[data-abi-output="return"]').select_option(output_pin)
        dialog.locator("[data-abi-remap-cancel]").click()
        assert not f.pending()["blueprint"] and checkpoint.read_bytes() == baseline
        untouched()
        f.checked("Unmapped return is blocked and Cancel retains the original candidate and sources.")

        dialog = map_output(panel)
        dialog.locator('[data-abi-output="return"]').select_option(output_pin)
        dialog.locator("[data-abi-remap-accept]").click()
        expect(dialog).to_have_count(0)
        panel.locator('[data-bp-node="body"] [data-internal-code]').click()
        editor = f.page.locator('[role=dialog]:has([data-code-source])')
        field = editor.locator("[data-code-source]")
        assert field.input_value().startswith(f"public static {selected_type} Execute(")
        field.evaluate("(element, text)=>{const start=element.value.indexOf(text);if(start<0)throw Error('missing original source');element.focus();element.setSelectionRange(start,start+text.length);}", source.rstrip())
        f.page.keyboard.insert_text(authored.rstrip())
        editor.locator("[data-code-save]").click()

        inputs = f.pending()["blueprint"]
        mark = len(f.traffic)
        panel.locator("[data-bp-save]").click()
        f.idle()
        assert not [row for row in f.pending()["blueprint"] if row[1].get("type") in ("argument:value", "parameters", "source")]
        actions = [row["invoke"]["input"] for row in f.traffic[mark:] if row.get("invoke", {}).get("endpoint") == "blueprint"]
        save = [row for row in actions if row["action"] == "authorBatch"]
        assert len(save) == 1 and [edit["action"] for edit in save[0]["edits"]] == ["argument", "parameters", "source"]
        if nested:
            assert save[0]["privateBinding"] == request["privateBinding"]
        assert not any(row["action"] in ("argument", "parameters", "source") for row in actions)
        assert inputs
        untouched()
        f.page.unroute_all(behavior="wait")
        f.page.close()
        f.browser.close()
    f.stop()

    text = json.loads(checkpoint.read_text())
    assert text["version"] == 1
    graph_unit = next(row for row in text["changes"] if row["id"] == fixture.whole_graph)
    candidate = json.loads(graph_unit["draft"])
    expected = json.loads(originals[f.project / fixture.graph_path])
    child = child_graph(expected)
    child["nodes"][0]["signature"]["return"] = selected_type
    child["nodes"][1]["arguments"]["value"]["output"] = output_pin
    assert candidate == expected
    assert graph_unit["propertyObservations"]["version"] == 1
    assert set(graph_unit["propertyObservations"]["sources"]) == set(initial["privateReturnSources"])
    f.checked("One ordinary version-1 checkpoint records exactly the ABI, qualified consumer and C# source change.")

    f.start(1)
    restored = read()
    assert json.loads(restored["nodes"][1]["arguments"][0]["valueJson"]) == {"node": "body", "output": output_pin}
    assert restored["nodes"][0]["signature"]["return"] == selected_type
    assert restored["nodes"][0]["source"] == authored
    ids = restored["reviewIds"]
    assert {fixture.whole_graph, producer_id} <= set(ids)
    f.invoke("reviewGroup", {"ids": ids, "target": "portable"})
    review = f.state()["review"]
    assert review["status"] == "ready", review
    peer = peer_path
    saved = checkpoint.read_bytes()
    assert peer.read_bytes() == originals[peer]
    stamp = peer.stat()
    peer.write_bytes(originals[peer] + b"\n")
    try:
        refusal = f.invoke("confirmGroup", {"ids": ids, "token": review["token"]})["result"]["result"]
        assert refusal["sourceConfirmed"] is False
        assert checkpoint.read_bytes() == saved
        assert peer.read_bytes() == originals[peer] + b"\n"
        assert all(path == peer or path.read_bytes() == data for path, data in originals.items())
    finally:
        peer.write_bytes(originals[peer])
        os.utime(peer, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    f.stop()
    f.checked("A sibling source change after Review blocks Confirm and preserves the whole checkpoint and source bytes.")

    previous = os.environ.get("REMAP_PREVIOUS")
    if previous:
        previous = Path(previous)
        current_repo, current_report = f.repo, f.report
        editor_repo = f.env["CONFECTORY_EDITOR_REPO"]
        try:
            f.repo = previous / "checkout"
            f.report = json.loads((previous / "report.json").read_text())
            f.env["CONFECTORY_EDITOR_REPO"] = str(f.repo)
            f.start(2)
            backward = read()
            assert not backward.get("privateReturnChoices")
            assert backward["nodes"][0]["signature"]["return"] == selected_type
            assert backward["nodes"][1]["arguments"] == restored["nodes"][1]["arguments"]
            f.invoke("reviewGroup", {"ids": backward["reviewIds"], "target": "portable"})
            assert f.state()["review"]["status"] == "ready"
            untouched()
        finally:
            f.stop()
            f.repo, f.report = current_repo, current_report
            f.env["CONFECTORY_EDITOR_REPO"] = editor_repo
        f.checked("The unmodified baseline engine cold-restores and reviews the current pending checkpoint.")

    f.start(3)
    with sync_playwright() as playwright:
        f.browser = playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
        f.page = f.setup()
        f.page.set_viewport_size({"width": 2200, "height": 1500})
        panel = open_graph()
        review = review_in_editor(panel)
        reviewed = checkpoint.read_bytes()
        def pending_sources(raw):
            changes = json.loads(raw)["changes"]
            return {row["id"]: (row["path"], row["baseline"], row["draft"]) for row in changes}
        assert pending_sources(reviewed) == pending_sources(saved)
        review.locator("[data-reject]").click()
        expect(review).to_be_hidden()
        untouched()
        assert checkpoint.read_bytes() == reviewed
        review = review_in_editor(panel)
        review.locator("#confirm").click()
        expect(review).to_be_hidden(timeout=120000)
        f.idle()
        assert read()["nodes"][0]["signature"]["return"] == selected_type
        f.page.unroute_all(behavior="wait")
        f.page.close()
        f.browser.close()
    f.stop()
    assert json.loads((f.project / fixture.graph_path).read_text()) == expected
    record = json.loads((f.project / fixture.node_path).read_text())
    assert record["source"] == authored
    assert record["helpers"] == json.loads(originals[f.project / fixture.node_path])["helpers"]
    for path, data in originals.items():
        if path.name not in (fixture.graph_path, fixture.node_path):
            assert path.read_bytes() == data, path
    build("after", after_value, selected_type)
    assert not f.errors and not f.external, (f.errors, f.external)
    f.checked(f"Cold Review and Confirm preserve siblings and old out. Actual execution changes the consumer from {before_value} to {after_value}.")
finally:
    print("Evidence:", f.case)
    f.stop()
