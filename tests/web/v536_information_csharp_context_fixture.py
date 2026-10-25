"""The same real transaction with two C# targets and an explicitly edited caller."""
import copy
import json
import re
import v536_information_csharp_fixture as base
from v536_information_csharp_fixture import *

implementation.write_text(implementation.read_text().replace('}', 'body windows "manual-windows.csbody";}'))
(f.project / 'manual-windows.csbody').write_text('return amount + count; // 원래 Windows 본문')
caller_path = f.project / 'CallerBody.celem'
caller_path.write_text(re.sub(r'(import [^;]+ as )\w+( \()', r'\1Target\2', caller_path.read_text().replace('blueprint common "caller.graph.json";', 'body common "manual-caller.csbody";')))
(f.project / 'manual-caller.csbody').write_text('return calls.Target.Invoke(first,second); // 원래 호출자')
snapshot = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}
edited_files = {body_path: edited, 'manual-windows.csbody': 'return checked(text.Length+count+7); // 직접 쓴 Windows 본문\r\n', 'manual-caller.csbody': 'return calls.Target.Invoke("직접 고친 호출",second); // 직접 쓴 호출자\r\n'}


def selections(preview):
    bodies = {}
    for id, row in preview['functionBodies'].items():
        bodies[id] = {k: row[k] for k in ['hash', 'path']} | {'beforeSignature': row['signature'], 'signature': row['signature'] if row['caller'] else new, 'contract': new, 'text': edited_files[row['path']]}
    return {'before': old, 'args': remap, 'callers': {}, 'bodies': bodies}


def verify(checkpoint):
    rows = {r['id']: r for r in json.loads(checkpoint.read_text())['changes']}
    expected = {body_id: body_path, fn + 'Body/body:windows': 'manual-windows.csbody', caller + 'Body/body:common': 'manual-caller.csbody'}
    for id, path in expected.items():
        assert rows[id]['draft'] == edited_files[path]
    assert n.canonical(f.metadata('inspect', text=rows[fn + 'Body']['draft'])['signature']) == new
    assert n.canonical(f.metadata('inspect', text=rows[caller + 'Body']['draft'])['signature']) == {'args': [{'name': 'first', 'type': 'long'}, {'name': 'second', 'type': 'long'}], 'return': 'long'}
    ids = rows[owner]['atomicEditGroup']
    assert {owner, fn, fn + 'Body', caller + 'Body', *expected} <= set(ids)
    assert all((f.project / p).read_bytes() == b for p, b in snapshot.items())
    return ids
