"""Exact data preparation and final graph validation over the scoped read-only stream."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

host = [os.environ["CONFECTORY_DOTNET"], sys.argv[1]]
with tempfile.TemporaryDirectory(prefix="cf-reference-prepare-") as tmp:
    root = Path(tmp)
    project = root / "first"
    project.mkdir()
    manifest = project / "project.cpack"
    contents = {
        "Link": ("object", 'object Alpha::Link { use schema Alpha::LinkInfo; data Target = Alpha::One; }'),
        "LinkInfo": ("schema", 'schema Alpha::LinkInfo { field Target single reference Alpha::TargetInfo; }'),
        "TargetInfo": ("schema", 'schema Alpha::TargetInfo { field Count single general long; }'),
        "One": ("object", 'object Alpha::One { use schema Alpha::TargetInfo; data Count = 0; }'),
        "Two": ("object", 'object Alpha::Two { use schema Alpha::TargetInfo; data Count = 7; value editorName = "Two"; }'),
        "Wrong": ("object", 'object Alpha::Wrong {}'),
        "TextInfo": ("schema", 'schema Alpha::TextInfo { field Note single general string; }'),
        "Text": ("object", 'object Alpha::Text { use schema Alpha::TextInfo; data Note = "old"; }'),
    }
    manifest.write_text('project Alpha version "1" { ' + " ".join(
        f'element {key} {kind} "{key}.celem";' for key, (kind, _) in contents.items()) + " }")
    for name, (_, text) in contents.items():
        (project / (name + ".celem")).write_text(text)
    peer = root / "second"
    shutil.copytree(project, peer)

    def unit(path, kind):
        text = path.read_text()
        return dict(kind=kind, path=path.name, draft=text, original=text,
                    baseline=hashlib.sha256(text.encode()).hexdigest(), revision=1)

    def requests(target="Two", folder=project):
        path = folder / "project.cpack"
        units = {"Alpha::ProjectManifest": unit(path, "project")}
        units.update({"Alpha::" + name: unit(folder / (name + ".celem"), kind)
                      for name, (kind, _) in contents.items()})
        change = dict(type="data", path=["Target"],
                      contract=dict(kind="reference", cardinality="single", type="Alpha::TargetInfo"),
                      valueJson=json.dumps({"$ref": "Alpha::" + target}))
        declaration = dict(id="Alpha::Link", hash=units["Alpha::Link"]["baseline"], changes=[change])
        yield dict(operation="mixedOwnerCopyEdits", project=str(path), manifest=path.read_text(),
                   id="Alpha::Link", text=units["Alpha::Link"]["draft"], changes=[change],
                   drafts=[], units=units, reuseLongPreparation=True)
        for operation in ("informationBodyGroupGuards", "informationPropertyGroupGuards", "informationTypeGuards"):
            yield dict(operation=operation, action="prepare", project=str(path), namespace="Alpha",
                       units=units, declaration=declaration)

    def string_requests(value,folder=project):
        path=folder/"project.cpack"
        units={"Alpha::ProjectManifest":unit(path,"project")}
        units.update({"Alpha::"+name:unit(folder/(name+".celem"),kind)
                      for name,(kind,_) in contents.items()})
        change=dict(type="data",path=["Note"],contract=dict(kind="general",cardinality="single",type="string"),valueJson=json.dumps(value))
        declaration=dict(id="Alpha::Text",hash=units["Alpha::Text"]["baseline"],changes=[change])
        yield dict(operation="mixedOwnerCopyEdits",project=str(path),manifest=path.read_text(),
                   id="Alpha::Text",text=units["Alpha::Text"]["draft"],changes=[change],drafts=[],units=units,reuseLongPreparation=True)
        for operation in ("informationBodyGroupGuards","informationPropertyGroupGuards","informationTypeGuards"):
            yield dict(operation=operation,action="prepare",project=str(path),namespace="Alpha",units=units,declaration=declaration)

    def ordinary(request):
        return json.loads(subprocess.run(host, input=json.dumps(request), text=True,
                                         capture_output=True, timeout=20, check=True).stdout)

    def start():
        process = subprocess.Popen(host + ["--inspect-stream"], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert process.stdout.readline().strip() == "CONFECTORY_INSPECT_STREAM_14"
        return process

    def send(process, request):
        process.stdin.write(json.dumps(request) + "\n")
        process.stdin.flush()
        line = process.stdout.readline()
        return None if not line else json.loads(line)

    def final_graph(process, target="Two", overlay=False):
        # The final SlotBatch query uses the same full graph/schema/reference
        # validation flags and the same current draft bytes as one-shot effective.
        after = contents["Link"][1].replace("Alpha::One", "Alpha::" + target)
        drafts = [{"id": "Alpha::" + name, "text": (project / (name + ".celem")).read_text()}
                  for name in contents if name != "Link"] if overlay else []
        payload = dict(operation="effective", project=str(manifest), manifest=manifest.read_text(),
                       id="Alpha::Link", text=after, drafts=drafts, schemaView=True,
                       validateObjects=True, observeSources=True)
        expected = ordinary(payload)
        actual = send(process, dict(payload, operation="inspectEffective", kind="object"))
        assert expected["ok"] and actual["ok"] and actual["result"]["effective"] == expected["result"], (expected, actual)
        return expected["result"]

    # Long and string use the same final full graph/schema validation as a
    # standalone effective request. A warm process is not a cached decision.
    def scalar_final(process, name, after, overlay=False):
        drafts=[{"id":"Alpha::"+n,"text":(project/(n+".celem")).read_text()} for n in contents if n!=name] if overlay else []
        payload=dict(operation="effective",project=str(manifest),manifest=manifest.read_text(),
                     id="Alpha::"+name,text=after,drafts=drafts,schemaView=True,validateObjects=True,observeSources=True)
        expected=ordinary(payload)
        actual=send(process,dict(payload,operation="inspectEffective",kind="object"))
        assert expected["ok"] and actual["ok"] and actual["result"]["effective"]==expected["result"],(expected,actual)
        return expected["result"]
    def scalar_valid(result):
        return result["status"]=="available" and result["schemaModel"]["validation"]["status"]=="valid"

    proc=start()
    try:
        for overlay in (False,True):
            assert scalar_valid(scalar_final(proc,"One",contents["One"][1].replace("= 0","= 123"),overlay))
            assert scalar_valid(scalar_final(proc,"Text",contents["Text"][1].replace('"old"','"한글 · café"'),overlay))
            assert not scalar_valid(scalar_final(proc,"One",contents["One"][1].replace("= 0",'= "bad"'),overlay))
            assert not scalar_valid(scalar_final(proc,"Text",contents["Text"][1].replace('"old"','12'),overlay))
        schema=project/"TargetInfo.celem";raw=schema.read_bytes()
        schema.write_text(raw.decode().replace("general long","general bool"))
        assert not scalar_valid(scalar_final(proc,"One",contents["One"][1].replace("= 0","= 123")))
        schema.write_bytes(raw)
        unrelated=project/"Wrong.celem";raw=unrelated.read_bytes()
        unrelated.write_text('object Alpha::Wrong { use schema Alpha::TargetInfo; data Count = "invalid"; }')
        assert not scalar_valid(scalar_final(proc,"One",contents["One"][1].replace("= 0","= 123")))
        unrelated.write_bytes(raw)
        assert scalar_valid(scalar_final(proc,"One",contents["One"][1].replace("= 0","= 123")))
    finally:
        if proc.poll() is None:proc.kill()
        proc.wait()

    # Coalescing is transport only: compare all original per-operation results
    # and error paths over the exact same source and draft snapshot.
    proc=start()
    try:
        for generator in (requests(), string_requests("batch")):
            individual=list(generator)[1:]
            prepare=dict(individual[0],operation="informationGuardBatch")
            old=[ordinary(request)["result"] for request in individual]
            expected=dict(complete=True,body=old[0],property=old[1],types=old[2])
            result=send(proc,prepare)
            assert result==ordinary(prepare) and result["result"]==expected,result
            validation={k:v for k,v in prepare.items() if k not in ("declaration","action")}
            validation["selected"]=[prepare["declaration"]["id"]]
            for mode in ("selection","observations","final"):
                combined=dict(validation,action=mode)
                result=send(proc,combined)
                assert result==ordinary(combined),result
                if mode=="final":
                    reads=[]
                    for op in ("informationTypeGuards","informationPropertyGroupGuards","informationBodyGroupGuards"):
                        reads+=ordinary(dict(validation,operation=op,action="validate"))["result"]["reads"]
                    assert result["result"]==dict(reads=reads)
                else:assert result["result"]==dict(complete=True)
            broken=dict(validation,action="observations",units=dict(validation["units"]))
            broken["units"]["Alpha::Broken/body:common"]={"kind":"blueprint","draft":"{}","propertyObservations":{}}
            old_error=ordinary(dict(broken,operation="blueprintPropertyObservations"))
            assert not old_error["ok"] and send(proc,broken)==old_error
        # An observation with actual required host file checks must not be
        # collapsed into a no-intermediate-read result.
        function="Alpha::Observed"
        function_text=f"function {function} () -> long {{}}"
        implementation=function+"Body";graph=implementation+"/body:common"
        authored=ordinary(dict(operation="blueprintPrepareFeature",id=function,text=function_text,
                               implementation=implementation,graphPath="Observed.graph.json",nodePath="Observed.node.json"))
        assert authored["ok"],authored
        def snapshot(kind,path,text):
            return dict(kind=kind,path=path,draft=text,original=text,revision=1,baseline=hashlib.sha256(text.encode()).hexdigest())
        observed_units=dict(validation["units"])
        observed_units[function]=snapshot("function","Observed.celem",function_text)
        observed_units[implementation]=snapshot("implementation","ObservedBody.celem",authored["result"]["implementation"])
        observed_units[graph]=snapshot("blueprint","Observed.graph.json",json.dumps(dict(nodes=[])))
        selected=["Alpha::ProjectManifest",function,implementation,graph]
        observed_units[graph]["propertyObservations"]=dict(version=1,graph=graph,sources={
            name:dict(path=observed_units[name]["path"],kind=observed_units[name]["kind"],hash=observed_units[name]["baseline"]) for name in selected})
        observed=dict(validation,units=observed_units,selected=selected,action="observations")
        old=ordinary(dict(observed,operation="blueprintPropertyObservations"))
        assert old["ok"] and len(old["result"]["checks"])==4,old
        assert send(proc,observed)==dict(ok=True,result=dict(complete=False))
        foreign=list(requests(folder=peer))[1]
        assert send(proc,dict(foreign,operation="informationGuardBatch")) is None and proc.wait(timeout=5)==2
    finally:
        if proc.poll() is None:proc.kill()
        proc.wait()

    for edit in ({"raw":"not a root data edit"}, {"changes":[list(requests())[1]["declaration"]["changes"][0],dict(type="description",text="mixed")]}):
        proc=start()
        try:
            request=list(requests())[1];request["operation"]="informationGuardBatch";request["declaration"].update(edit)
            assert send(proc,request) is None and proc.wait(timeout=5)==2
        finally:
            if proc.poll() is None:proc.kill()
            proc.wait()

    proc = start()
    try:
        initial = list(requests())
        for request in initial:
            expected = ordinary(request)
            assert expected["ok"], expected
            assert send(proc, request) == expected
        for overlay in (False, True):
            valid = final_graph(proc, overlay=overlay)
            assert valid["status"] == "available" and valid["schemaModel"]["validation"]["status"] == "valid", valid
            invalid = final_graph(proc, "Wrong", overlay=overlay)
            assert invalid["status"] != "available" or invalid["schemaModel"]["validation"]["status"] != "valid", invalid
        target = project / "Two.celem"
        raw = target.read_bytes()
        stamp = target.stat()
        target.write_text(raw.decode().replace('"Two"', '"Renamed"'))
        os.utime(target, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        for request in requests():
            assert send(proc, request) == ordinary(request)
        renamed = final_graph(proc)
        assert renamed["status"] == "available"
        target.write_text('object Alpha::Two { use schema Alpha::LinkInfo; }')
        invalid = final_graph(proc)
        assert invalid["status"] != "available" or invalid["schemaModel"]["validation"]["status"] != "valid", invalid
        for request in requests():
            assert send(proc, request) == ordinary(request)
        target.write_bytes(raw)
        for bad in ("Wrong", "Missing"):
            request = next(requests(bad))
            expected = ordinary(request)
            assert not expected["ok"] and send(proc, request) == expected
        for request in requests():
            assert send(proc, request) == ordinary(request)
        assert send(proc, next(requests(folder=peer))) is None
        assert proc.wait(timeout=5) == 2
    finally:
        if proc.poll() is None:
            proc.kill()
        proc.wait()

    proc = start()
    try:
        assert final_graph(proc)["status"] == "available"
        foreign_query = dict(operation="inspectEffective", project=str(peer / "project.cpack"),
                             manifest=(peer / "project.cpack").read_text(), id="Alpha::Link",
                             kind="object", text=contents["Link"][1], drafts=[],
                             schemaView=True, validateObjects=True, observeSources=True)
        assert send(proc, foreign_query) is None and proc.wait(timeout=5) == 2
    finally:
        if proc.poll() is None:
            proc.kill()
        proc.wait()

    # String preparation uses the full ordinary dispatch, never a repeat proof.
    proc=start()
    try:
        for value in ("", "한글 · café", "line\nquote\""):
            for request in string_requests(value):
                expected=ordinary(request)
                assert expected["ok"] and send(proc,request)==expected
                assert not expected.get("result",{}).get("repeatProof")
        # New caller can request the exact repeat proof only for its clean
        # existing root string. The same full before/after graph is verified.
        for value in ("","한글 · café"):
            request=dict(next(string_requests(value)),reuseStringPreparation=True)
            expected=ordinary(request)
            assert expected["ok"] and send(proc,request)==expected
            proof=expected["result"]["repeatProof"]
            assert proof["observations"] and proof["ownershipPaths"]
        schema=project/"TextInfo.celem";raw=schema.read_bytes()
        schema.write_bytes(raw.replace(b"general string",b"general long"))
        for request in string_requests("invalid"):
            expected=ordinary(request)
            assert send(proc,request)==expected
        schema.write_bytes(raw)
        request=next(string_requests(123))
        expected=ordinary(request)
        assert not expected["ok"] and send(proc,request)==expected
        assert send(proc,next(string_requests("peer",peer))) is None and proc.wait(timeout=5)==2
    finally:
        if proc.poll() is None:proc.kill()
        proc.wait()
    exact_string=next(string_requests("valid"))
    for edit in ({"rawText":contents["Text"][1]},
                 {"changes":[exact_string["changes"][0],dict(type="description",text="mixed")]}):
        proc=start()
        try:
            assert send(proc,dict(exact_string,**edit)) is None and proc.wait(timeout=5)==2
        finally:
            if proc.poll() is None:proc.kill()
            proc.wait()
    assert (project/"Text.celem").read_text()==contents["Text"][1]
    assert (peer/"Text.celem").read_text()==contents["Text"][1]

    # A multi-field or raw edit retains ordinary one-shot handling. The
    # read-only reference stream must not expand its accepted shape.
    for extra in ({"rawText": contents["Link"][1]},
                  {"changes": [initial[0]["changes"][0], dict(type="description", text="mixed")]}):
        proc = start()
        try:
            assert send(proc, dict(initial[0], **extra)) is None
            assert proc.wait(timeout=5) == 2
        finally:
            if proc.poll() is None:
                proc.kill()
            proc.wait()
    assert (project / "Link.celem").read_text() == contents["Link"][1]
    assert (peer / "Link.celem").read_text() == contents["Link"][1]
print("PASS scalar/string/reference final graph, preparation/guard batch one-shot equivalence, nonempty host-read fallback, fresh retype/rename, invalid targets, project scope and unsupported-shape refusal")
