"""Explicit value pin renames retain values while output types are selected."""
import copy
import json
import v536_information_shared_output_return_mix_fixture as base

f, d, n, owner, mode = base.f, base.d, base.n, base.owner, base.mode
functions, old = base.functions, base.old
graphs, records, graph, snapshot = base.graphs, base.records, base.graph, base.snapshot
unchanged, binding = base.unchanged, base.binding
joint = mode.startswith('joint')
nexts = [copy.deepcopy(old), copy.deepcopy(old)]
nexts[0]['args'][0]['name'] = 'leftAmount'
nexts[1]['args'][2]['type'] = 'double'; nexts[1]['return'] = 'double'
if joint:
    nexts[0]['args'][2]['type'] = 'double'; nexts[0]['return'] = 'double'
    nexts[1]['args'][0]['name'] = 'rightAmount'
new, removed, added = nexts[0], [], []


def request():
    result = base.request()
    for row, sig in zip(result['changes'], nexts):
        row['signature'] = copy.deepcopy(sig)
        remap = {a['name']: sig['args'][i]['name'] for i, a in enumerate(old['args'])}
        changed = sig['return'] != old['return'] or sig['args'][2]['type'] != old['args'][2]['type']
        if not changed:
            row['mapping'] = {'before': copy.deepcopy(old), 'args': remap}
        else:
            row['mapping'] = base.selections(result, row['id'], sig)
            row['mapping']['args'] = remap
            for caller in row['mapping']['callers'].values():
                caller['inputs'] = {sig['args'][0]['name']: 'amount', 'real': 'real'}
    return result


def caller_arguments(index):
    return {nexts[index]['args'][0]['name']: {'input': 'first'} if index == 0 else binding('invoke', 'stable' if joint else 'return'),
            'real': {'constant': 1.25 if index == 0 else 2.5}}


def caller_exits():
    return {'return': binding('invoke_second', 'stable')}


def verify_rows(rows):
    merged = {row['id']: {'draft': (f.project/row['path']).read_text()} for row in f.metadata('describe', project=str(f.manifest))['units']} | rows
    caller = json.loads(merged[n.caller+'Body/body:common']['draft'])
    assert caller['entry'] == graph['entry'] and caller['edges'] == graph['edges'] and caller['exits'] == caller_exits()
    for index, (fn, sig) in enumerate(zip(functions, nexts)):
        assert n.canonical(f.metadata('inspect', text=merged[fn]['draft'])['signature']) == sig
        assert caller['nodes'][index]['signature'] == sig and caller['nodes'][index]['arguments'] == caller_arguments(index)
        assert caller['nodes'][index]['intent'] == graph['nodes'][index]['intent']
        leaf = json.loads(merged[fn+'Body/body:common']['draft'])
        assert leaf['edges'] == graphs[fn]['edges'] and leaf['entry'] == graphs[fn]['entry']
        assert {row['id'] for row in leaf['nodes']} == {row['id'] for row in graphs[fn]['nodes']}
        code = next(row for row in leaf['nodes'] if row['kind'] == 'code')
        assert code['signature'] == old and code['arguments'] == {'amount': {'input': sig['args'][0]['name']}, 'real': {'input': 'real'}}
        assert json.loads(merged[fn+'Body/body:common/node:body']['draft'])['source'] == records[fn]['source']
        for name, typ in [('count', sig['args'][2]['type']), ('stable', 'long'), ('return', sig['return'])]:
            writer = next(row for row in leaf['nodes'] if row['kind'] == 'export' and row['output'] == name)
            original = next(row for row in graphs[fn]['nodes'] if row['kind'] == 'export' and row['output'] == name)
            if typ == 'long': assert writer == original
            else: assert writer['arguments'] == {'value': {'input': 'real'}} and writer['signature']['args'][0]['type'] == 'double'
        fields = f.metadata('blueprintOutputSnapshot', functionText=merged[fn]['draft'])['fields']
        assert [(row['name'], row['type']) for row in fields] == [('count', sig['args'][2]['type']), ('stable', 'long'), ('return', sig['return'])]


def verify(checkpoint):
    rows = {row['id']: row for row in json.loads(checkpoint.read_text())['changes']}; verify_rows(rows); unchanged()
    group = rows[owner]['atomicEditGroup']
    assert set(functions+[fn+'Body/body:common' for fn in functions]+[n.caller+'Body', n.caller+'Body/body:common', owner]) <= set(group)
    return group


def verify_live():
    verify_rows({})


def edit_contract(popover, index):
    sig = nexts[index]
    if sig['args'][0]['name'] != 'amount': popover.locator('[data-signature-id=arg0] [data-signature-name]').fill(sig['args'][0]['name'])
    for field, before, after in [('arg2', 'long', sig['args'][2]['type']), ('return', 'long', sig['return'])]:
        if before != after:
            popover.locator('[data-signature-id='+field+'] [data-signature-type]').click()
            f.page.get_by_role('dialog', name='속성 타입 선택', exact=True).locator('[data-type='+after+']').click()


def has_mapping_dialog(index):
    return joint or index == 1


remap_title = base.remap_title


def select_contract(dialog, index):
    for target in dialog.locator('[data-abi-target^="output:"]').all():
        target.locator('[data-abi-input=value]').select_option('pin:real')
    for name, typ in [('count', nexts[index]['args'][2]['type']), ('return', nexts[index]['return'])]:
        if typ != 'long': dialog.locator('[data-abi-output='+name+']').select_option('stable')


def verify_pins(panel, index):
    from playwright.sync_api import expect
    method = panel.locator('[data-inline-method="'+functions[index]+'"]')
    for name, typ in [('count', nexts[index]['args'][2]['type']), ('stable', 'long'), ('return', nexts[index]['return'])]:
        label = '결과' if name == 'return' else name
        expect(method.locator('[data-pin-side=outputs] [data-function-pin-name="'+label+'"]')).to_have_attribute('data-function-pin-type', '실수' if typ == 'double' else '정수')
    expect(method.locator('[data-pin-side=inputs] [data-function-pin-name="'+nexts[index]['args'][0]['name']+'"]')).to_have_attribute('data-function-pin-type', '정수')
    if nexts[index]['args'][0]['name'] != 'amount': expect(method.locator('[data-pin-side=inputs] [data-function-pin-name=amount]')).to_have_count(0)
