"""Validate captured real adapter requests against locally generated CLI schemas.

No CLI/server/auth/network invocation here. The caller supplies an owned schema
directory generated with an empty CODEX_HOME and the owned stdio fixture capture.
This checks protocol shape, never filesystem containment or model entitlement.
"""
import json
import pathlib
import sys

import jsonschema

root, capture = map(pathlib.Path, sys.argv[1:])
types = {
    "initialize": "InitializeParams",
    "thread/start": "ThreadStartParams",
    "turn/start": "TurnStartParams",
    "turn/interrupt": "TurnInterruptParams",
}
seen = set()
for line in capture.read_text().splitlines():
    request = json.loads(line)
    method = request.get("method")
    if method not in types:
        continue
    files = list(root.rglob(types[method] + ".json"))
    assert len(files) == 1, (method, files)
    schema = json.loads(files[0].read_text())
    params = request["params"]
    # Serde schemas can allow unknown fields. Do not let that hide drift.
    assert not (params.keys() - schema["properties"].keys()), method
    jsonschema.validators.validator_for(schema)(schema).validate(params)
    if method == "thread/start":
        assert params["sandbox"] == "read-only" and params["ephemeral"]
        assert params["approvalPolicy"] == "never"
    if method == "turn/start":
        assert params["sandboxPolicy"] == {"type": "readOnly", "networkAccess": False}
        # Negative checks catch the exact previous compatibility mistakes.
        invalid = json.loads(json.dumps(params))
        invalid["sandboxPolicy"]["type"] = "read-only"
        assert not jsonschema.validators.validator_for(schema)(schema).is_valid(invalid)
    seen.add(method)
assert seen == set(types), seen
thread_schema = json.loads(next(root.rglob("ThreadStartParams.json")).read_text())
assert "readOnly" not in thread_schema["definitions"]["SandboxMode"]["enum"]
print("Installed schema actual request capture PASS: initialize/thread/start/turn/start/turn/interrupt; no read isolation claim")
