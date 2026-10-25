"""Confirmed owned copy of an inherited body; original registration stays valid."""
import copy
import json
from pathlib import Path
import v536_information_inherited_copy_fixture as x

f, d, n, owner, fn, caller, mode = x.f, x.d, x.n, x.owner, x.fn, x.b.caller, x.mode
child, parent, parent_path = x.child, x.parent, x.parent_path
old = copy.deepcopy(x.b.old)
new = copy.deepcopy(old)
new['args'][0]['name'] = 'renamed'
remap = {'amount': 'renamed', 'count': 'count'}
if 'out-name' in __import__('sys').argv[4:]:
    new['args'][1]['name'] = 'result'
    remap['count'] = 'result'
original, selected = x.original, x.b.native
copy_id = f.n + 'SavedInheritedCopy'
prepared = f.metadata('implementationCopy', project=str(f.manifest), action='prepare',
                      feature=fn, source=x.child, target='common',
                      implementation=copy_id, owner=owner, ownerText=x.b.info.read_text())
assert prepared['bodyOrigin'] == x.parent
copy_path = 'SavedInheritedCopy.celem'
(f.project / copy_path).write_text(prepared['implementation'])
f.manifest.write_text(f.manifest.read_text().replace(
    'registry Confectory.Build.DotNet',
    'element SavedInheritedCopy implementation "' + copy_path +
    '";registry Confectory.Build.DotNet', 1))
graph_path = prepared['graphPath']
(f.project / graph_path).parent.mkdir(parents=True, exist_ok=True)
(f.project / graph_path).write_text(json.dumps(prepared['graph']))
for row in prepared['records']:
    path = f.project / Path(graph_path).parent / row['relative']
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row['record']))
x.b.info.write_text(prepared['owner'])
graph_id = copy_id + '/body:common'
body_id = graph_id + '/node:' + prepared['records'][0]['id']
body_path = str(Path(graph_path).parent / prepared['records'][0]['relative'])
donor_id, donor_impl, donor_path = x.parent + '/body:common', x.parent, x.parent_path
donor_body_path, copy_owner = 'whole-original.csbody', owner
edited = original.replace('원래 별칭', '상속 복사본 계약 편집')
snapshot = {str(p.relative_to(f.project)): p.read_bytes()
            for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}

def selections(preview):
    row, donor = preview['functionBodies'][body_id], preview['functionBodies'][donor_id]
    assert row['sourceKind'] == 'whole-graph-csharp' and donor['sourceKind'] == 'csharp'
    native = copy.deepcopy(selected)
    return {'before': old, 'args': remap, 'copies': copy.deepcopy(preview['functionCopies']),
            'bodies': {
                body_id: {k: row[k] for k in ['hash', 'path', 'whole']} |
                {'beforeSignature': native, 'signature': native, 'contract': new,
                 'text': edited, 'outputs': {'return': 'return', 'nativeTotal': 'nativeTotal'}},
                donor_id: {k: donor[k] for k in ['hash', 'path']} |
                {'beforeSignature': native, 'signature': native, 'contract': new, 'text': original}}}

def request():
    r = n.request(new, remap)
    preview = {key: f.metadata(op, project=str(f.manifest), manifest=f.manifest.read_text(),
                              id=owner, function=fn, includeBlueprintTargets=True, units=r['units'])
               for key, op in [('functionBodies', 'informationFunctionBodies'),
                               ('functionCopies', 'informationFunctionCopies')]}
    r['changes'][0]['mapping'] = selections(preview)
    return r

def unchanged():
    assert all((f.project / p).read_bytes() == value for p, value in snapshot.items())

def verify(checkpoint):
    rows = {r['id']: r for r in json.loads(checkpoint.read_text())['changes']}
    assert json.loads(rows[body_id]['draft'])['source'] == edited
    graph = json.loads(rows[graph_id]['draft'])
    assert graph['copySource'] == prepared['graph']['copySource']
    assert graph['nodes'][0]['arguments'] == {'nativeAmount': {'input': 'renamed'}}
    assert x.child not in rows and x.parent not in rows
    unchanged()
    return rows[owner]['atomicEditGroup']
