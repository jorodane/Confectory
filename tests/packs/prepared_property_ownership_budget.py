"""Oversized optional model proof is unavailable without changing ordinary schema reads."""
import json, os, subprocess, tempfile, sys
from pathlib import Path

host = [os.environ["CONFECTORY_DOTNET"], sys.argv[1]]
with tempfile.TemporaryDirectory(prefix="cf-property-proof-") as tmp:
    for count in (40, 126, 127, 400):
        folder = Path(tmp) / str(count); folder.mkdir()
        project = folder / "project.cpack"
        schema = folder / "Info.celem"
        schema.write_text("schema Synthetic::Info { field Count single general long; }")
        rows = ['element Info schema "Info.celem";']
        for i in range(count):
            name = f"Item{i}"
            (folder / (name+".celem")).write_text(f"object Synthetic::{name} {{ use schema Synthetic::Info; data Count = {i}; }}")
            rows.append(f'element {name} object "{name}.celem";')
        project.write_text('project Synthetic version "1" { standalone false; ' + " ".join(rows) + " }")
        source = folder / "Item0.celem"
        request = dict(project=str(project), manifest=project.read_text(), id="Synthetic::Item0",
                       kind="object", text=source.read_text(), schemaView=True, schemaReuseProof=True)
        with subprocess.Popen(host+["--inspect-stream"], text=True, stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            assert proc.stdout.readline().strip()=="CONFECTORY_INSPECT_STREAM_12"
            def send(**values):
                proc.stdin.write(json.dumps(request|values)+"\n");proc.stdin.flush()
                return json.loads(proc.stdout.readline())
            prepared=send(operation="preparePropertyModels",ids=["Synthetic::Item0"])
            if count<=126:
                assert prepared["ok"], prepared
                assert len(prepared["result"]["effective"]["ownershipPaths"])==count+2
                assert prepared["result"]["effective"]["rows"][0]["id"]=="Synthetic::Item0"
            else:
                assert not prepared["ok"], prepared
            # No change to the ordinary fresh opening or project-bound stream:
            # it may return a larger proof, but no reusable optional model.
            opened=send(operation="inspectEffective")
            assert opened["ok"] and opened["result"]["effective"]["schemaModel"]["validation"]["status"]=="valid", opened
            source.write_text(source.read_text().replace("Count = 0", "Count = 9"))
            updated=send(operation="inspectEffective",text=source.read_text())
            assert updated["ok"] and updated["result"]["inspection"]["id"]=="Synthetic::Item0"
            assert updated["result"]["effective"]!=opened["result"]["effective"]
            proc.stdin.close();assert proc.wait(timeout=10)==0
    print("PASS exact 128-path boundary, oversized optional proof rejection, ordinary fresh reads and resident stream")
