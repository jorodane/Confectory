"""Both inputs change; every original out writer and consumer stays intact."""
import copy
import json
import v536_information_shared_mixed_types_fixture as base

f, d, n, owner, mode = base.f, base.d, base.n, base.owner, base.mode
functions, old = base.functions, base.old
graphs, records, graph = base.graphs, base.records, base.graph
text_value, replacement, binding = base.text_value, base.replacement, base.binding
removed, added, destination = [], [], 'count'
unused_first = mode.startswith('unused')
if unused_first:
    path = f.project/'function.graph.json'
    original_graph = json.loads(path.read_text())
    next(row for row in original_graph['nodes'] if row['kind'] == 'code')['arguments']['amount'] = {'constant': int(replacement)}
    path.write_text(json.dumps(original_graph))
    definitions = f.metadata('featureBlueprintNodes', featureSource=(f.project/('elements/'+functions[0].split('::')[1]+'.celem')).read_text(), graph=original_graph)
    record_path = f.project/'function.node.json'
    record = json.loads(record_path.read_text())
    record['definitionHash'] = next(row['definitionHash'] for row in definitions['nodes'] if row['id'] == 'body')
    record_path.write_text(json.dumps(record))
snapshot = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*')
            if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}
nexts = [copy.deepcopy(old), copy.deepcopy(old)]
for signature in nexts:
    signature['args'][0]['type'] = 'string'
new = nexts[0]


def request():
    result = base.base.request()
    for index, row in enumerate(result['changes']):
        row['signature'] = copy.deepcopy(nexts[index])
        row['mapping'].pop('outputs')
        for plan in row['mapping']['callers'].values():
            plan.pop('outputs')
        if not row['mapping']['implementations']:
            row['mapping'].pop('implementations')
    return result


def unchanged():
    assert all((f.project/path).read_bytes() == raw for path, raw in snapshot.items())


def usage_replacement_required(index):
    return not (unused_first and index == 0)


def caller_arguments(index):
    return base.caller_arguments(index, nexts)


def caller_exits():
    return base.caller_exits(nexts)


def verify_rows(rows):
    units = f.metadata('describe', project=str(f.manifest))['units']
    original = {row['id']: {'draft': (f.project/row['path']).read_text()} for row in units}
    return base.verify_rows(original | rows, nexts)


def verify(checkpoint):
    rows = {row['id']: row for row in json.loads(checkpoint.read_text())['changes']}
    verify_rows(rows)
    unchanged()
    group = rows[owner]['atomicEditGroup']
    assert set(functions+[fn+'Body/body:common' for fn in functions]+[n.caller+'Body', n.caller+'Body/body:common', owner]) <= set(group)
    return group


def verify_live():
    return base.verify_live(nexts)
