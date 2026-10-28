"""Original value-pin identity maps combined with explicit output graph plans."""
import copy
import json
import v536_information_shared_output_definition_mix_fixture as base

f, d, n, owner, mode = base.f, base.d, base.n, base.owner, base.mode
functions, old, nexts = base.functions, base.old, base.nexts
graphs, records, graph, snapshot = base.graphs, base.records, base.graph, base.snapshot
unchanged, binding = base.unchanged, base.binding
if mode.startswith('cross'):
    nexts[0].clear(); nexts[0].update(copy.deepcopy(old))
    nexts[1].clear(); nexts[1].update(copy.deepcopy(old))
    nexts[1]['args'] = [a for a in nexts[1]['args'] if a['name'] != 'count'] + [{'name': 'fresh', 'type': 'long', 'mode': 'out'}]
nexts[0]['args'][0]['name'] = 'leftAmount'
if mode.startswith('joint'): nexts[1]['args'][0]['name'] = 'rightAmount'
new, removed, added = nexts[0], [], []
outs, removed_for, added_for, changed_for = base.outs, base.removed_for, base.added_for, base.changed_for
destination, literal, published = base.destination, base.literal, base.published

def request():
    result = base.request()
    for index, (row, sig) in enumerate(zip(result['changes'], nexts)):
        mapping = row['mapping']
        mapping['args']['amount'] = sig['args'][0]['name']
        if not removed_for(sig) and not added_for(sig) and not changed_for(sig):
            row['mapping'] = {key: mapping[key] for key in ['before', 'args']}
        else:
            for plan in mapping['callers'].values():
                plan['inputs'] = {sig['args'][0]['name']: 'amount', 'real': 'real'}
    return result

def caller_arguments(index):
    original = copy.deepcopy(graph['nodes'][0]['arguments']) if index == 0 else {
        'amount': binding('invoke', destination(0) if removed_for(nexts[0]) or changed_for(nexts[0]) else 'count'),
        'real': {'constant': 2.5}}
    return {nexts[index]['args'][0]['name']: original['amount'], 'real': original['real']}

caller_exits = base.caller_exits

def verify_rows(rows):
    merged = {row['id']: {'draft': (f.project/row['path']).read_text()} for row in f.metadata('describe', project=str(f.manifest))['units']} | rows
    shared = json.loads(merged[n.caller+'Body/body:common']['draft'])
    assert shared['entry'] == graph['entry'] and shared['edges'] == graph['edges'] and shared['exits'] == caller_exits()
    for index, (fn, sig) in enumerate(zip(functions, nexts)):
        assert n.canonical(f.metadata('inspect', text=merged[fn]['draft'])['signature']) == sig
        assert shared['nodes'][index]['signature'] == sig and shared['nodes'][index]['arguments'] == caller_arguments(index)
        assert shared['nodes'][index]['intent'] == graph['nodes'][index]['intent']
        leaf = json.loads(merged[fn+'Body/body:common']['draft'])
        code = next(row for row in leaf['nodes'] if row['kind'] == 'code')
        assert code['signature'] == old and code['arguments'] == {'amount': {'input': sig['args'][0]['name']}, 'real': {'input': 'real'}}
        assert json.loads(merged[fn+'Body/body:common/node:body']['draft'])['source'] == records[fn]['source']
        missing, created, changed = removed_for(sig), added_for(sig), changed_for(sig)
        for name in missing:
            assert not any(row['kind'] == 'export' and row['output'] == name for row in leaf['nodes']) and leaf['exits'].get(name) is None
        for name in created:
            writer = next(row for row in leaf['nodes'] if row['kind'] == 'export' and row['output'] == name)
            assert writer['arguments']['value'] == {'constant': json.loads(literal(name, index))}
        for name in outs(old):
            if name in missing: continue
            originals = [row for row in graphs[fn]['nodes'] if row['kind'] == 'export' and row['output'] == name]
            writers = [row for row in leaf['nodes'] if row['kind'] == 'export' and row['output'] == name]
            assert [row['id'] for row in writers] == [row['id'] for row in originals]
            if name in changed:
                for writer in writers: assert writer['arguments'] == {'value': {'input': 'real'}} and writer['signature']['args'][0]['type'] == 'double'
            else: assert writers == originals
        at = leaf['entry']; route = {row['from']: row['to'] for row in leaf['edges']}; path = []
        while at in {row['id'] for row in leaf['nodes']}:
            assert at not in path; path.append(at); at = route.get(at, '')
        assert set(path) == {row['id'] for row in leaf['nodes']}
        fields = f.metadata('blueprintOutputSnapshot', functionText=merged[fn]['draft'])['fields']
        assert [(row['name'], row['type']) for row in fields] == [(name, outs(sig)[name]) for name in published if name not in missing]

def verify(checkpoint):
    rows = {row['id']: row for row in json.loads(checkpoint.read_text())['changes']}; verify_rows(rows); unchanged()
    group = rows[owner]['atomicEditGroup']
    assert set(functions+[fn+'Body/body:common' for fn in functions]+[n.caller+'Body', n.caller+'Body/body:common', owner]) <= set(group)
    return group

def verify_live():
    verify_rows({})

def edit_contract(popover, index):
    if nexts[index]['args'][0]['name'] != 'amount': popover.locator('[data-signature-id=arg0] [data-signature-name]').fill(nexts[index]['args'][0]['name'])
    base.edit_contract(popover, index)

def has_mapping_dialog(index):
    return bool(removed_for(nexts[index]) or added_for(nexts[index]) or changed_for(nexts[index]))

remap_title, select_contract = base.remap_title, base.select_contract

def verify_pins(panel, index):
    from playwright.sync_api import expect
    base.verify_pins(panel, index)
    method = panel.locator('[data-inline-method="'+functions[index]+'"]')
    expect(method.locator('[data-pin-side=inputs] [data-function-pin-name="'+nexts[index]['args'][0]['name']+'"]')).to_have_attribute('data-function-pin-type', '정수')
    if nexts[index]['args'][0]['name'] != 'amount': expect(method.locator('[data-pin-side=inputs] [data-function-pin-name=amount]')).to_have_count(0)
