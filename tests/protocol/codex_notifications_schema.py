"""Validate captured owned CLI lifecycle/error replies against retained CLI schemas.

No executable, auth file, user account, network or inference is accessed. This
checks wire shape only; foreign-scope and malformed-event fixtures still fail
separately in the production adapter. Intentional non-JSON output is not captured
by the fixture's JSON send function and is not counted as a valid notification.
"""
import json
import pathlib
import sys

import jsonschema

schemas, captures = map(pathlib.Path, sys.argv[1:])
types = {
    "item/agentMessage/delta": "AgentMessageDeltaNotification",
    "item/completed": "ItemCompletedNotification",
    "turn/completed": "TurnCompletedNotification",
    "error": "ErrorNotification",
    "turn/start response": "TurnStartResponse",
}
validators = {}
for method, name in types.items():
    files = list(schemas.rglob(name + ".json"))
    assert len(files) == 1, (name, len(files))
    schema = json.loads(files[0].read_text())
    validators[method] = jsonschema.validators.validator_for(schema)(schema)

counts = dict.fromkeys(types, 0)
files = sorted(captures.glob("*/responses.jsonl"))
assert files, "No captured owned fixture responses"
for file in files:
    for line in file.read_text().splitlines():
        message = json.loads(line)
        method = message.get("method")
        params = message.get("params")
        if method not in validators:
            if not isinstance(message.get("result", {}).get("turn"), dict):
                continue
            method, params = "turn/start response", message["result"]
        errors = list(validators[method].iter_errors(params))
        assert not errors, (file.parent.name, method,
                            [(list(e.path), e.validator) for e in errors])
        counts[method] += 1

assert all(counts.values()), counts
print(json.dumps({"pass": True, "fixtureCases": len(files),
                  "validatedOwnedMessages": counts,
                  "actualAccountOrInference": False}))
print("PASS retained CLI lifecycle/error schema shapes; not live service compatibility")
