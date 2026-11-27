"""Bounded grouped relation projections must exactly equal legacy independent batches."""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

host = [os.environ["CONFECTORY_DOTNET"], sys.argv[1]]
with tempfile.TemporaryDirectory(prefix="cf-relation-group-") as temp:
    project = Path(temp) / "project.cpack"
    def unit(name, text, kind="object", dirty=False):
        return dict(id="Synthetic::"+name, kind=kind, text=text, revision=2,
                    textHash=hashlib.sha256(text.encode()).hexdigest(), dirty=dirty)
    def query(**args):
        request = dict(operation="relationsMap", project=str(project), **args)
        return json.loads(subprocess.run(host, input=json.dumps(request), text=True,
                                        capture_output=True, check=True, timeout=30).stdout)
    batches = [
        [unit("Info", "schema Synthetic::Info { field Note single general string; }", "schema"),
         unit("Record", 'object Synthetic::Record { use schema Synthetic::Info; data Note = "Draft"; value editorName = "Draft label"; }', dirty=True)],
        [unit("Malformed", "object Synthetic::Malformed { !"),
         unit("Wrong", "object Synthetic::Other {}")],
    ]
    independent = [query(units=b)["result"] for b in batches]
    grouped = query(units=[], batches=batches)
    assert grouped["ok"] and grouped["result"]["grouped"] is True, grouped
    for key in ("nodes", "edges"):
        assert grouped["result"][key] == [row for result in independent for row in result[key]]
    assert grouped["result"]["sourceWritten"] is False and grouped["result"]["executed"] is False
    assert grouped["result"]["nodes"][1]["title"] == "Draft label"
    assert all(not n["valid"] for n in grouped["result"]["nodes"][2:])
    for args in (dict(units=[], batches=[batches[0]]),
                 dict(units=[], batches=[batches[0]]*17),
                 dict(units=[], batches=[batches[0]*17, batches[1]]),
                 dict(units=batches[0], batches=batches),
                 dict(units=[], batches={"invalid": True}),
                 dict(units=[], batches=[[unit("Huge", "x"*1048576)], batches[1]])):
        assert not query(**args)["ok"], args
    assert not project.exists()
    print("PASS exact grouped map, draft/identity/malformed diagnostics, bounded input and no writes")
