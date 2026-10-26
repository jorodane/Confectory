"""Original input definitions and coordinated output graph plans, no new UI."""
import copy
import json
import v536_information_shared_output_definition_mix_fixture as base

f, d, n, owner, mode = base.f, base.d, base.n, base.owner, base.mode
functions, old, nexts = base.functions, base.old, base.nexts
graphs, records, graph, snapshot = base.graphs, base.records, base.graph, base.snapshot
unchanged, binding = base.unchanged, base.binding
outs, removed_for, added_for, changed_for = base.outs, base.removed_for, base.added_for, base.changed_for
destination, literal, published = base.destination, base.literal, base.published
joint, to_void, from_void = base.joint, base.to_void, base.from_void
extra_value, replacement = '9223372036854775806', '9223372036854775800'
if not (joint or to_void or from_void):
    nexts[1].clear(); nexts[1].update(copy.deepcopy(old)); nexts[1]['args'].append({'name': 'extra', 'type': 'long'})
else:
    nexts[0]['args'].append({'name': 'extra', 'type': 'long'})
    nexts[1]['args'] = nexts[1]['args'][1:] + ([] if to_void else [{'name': 'incoming', 'type': 'long'}])
new, removed, added = nexts[0], [], []

def input_removed(index): return index == 1 and (joint or to_void or from_void)
def extra_added(index): return index == (0 if joint or to_void or from_void else 1)
def output_changed(index): return bool(removed_for(nexts[index]) or added_for(nexts[index]) or changed_for(nexts[index]))

def request():
    result = base.request()
    for index, row in enumerate(result['changes']):
        mapping = row['mapping']
        if input_removed(index): mapping['args']['amount'] = None
        args = {k: result[k] for k in ['project', 'manifest', 'id', 'units']}
        inputs = f.metadata('informationFunctionInputs', **args, function=row['id'])
        if not output_changed(index):
            mapping.pop('outputs', None)
            for plan in mapping['callers'].values(): plan.pop('outputs')
        for key, plan in mapping['callers'].items():
            if extra_added(index): plan['inputs']['extra'] = {'valueJson': extra_value}
            if input_removed(index):
                plan['inputs'].pop('amount')
                if to_void: plan['disconnect'] = {'amount': inputs[key]['bindings']['amount']}
                else: plan['inputs']['incoming'] = 'amount'
        if input_removed(index):
            uses = f.metadata('informationFunctionInputUses', **args, function=row['id'])
            mapping['implementations'] = {key: {k: plan[k] for k in ['graph', 'node', 'argument', 'hash', 'before']} |
                {'value': {'valueJson': replacement} if to_void else {'input': 'incoming'}} for key, plan in uses.items() if plan['input'] == 'amount'}
    return result

def caller_arguments(index):
    args = {'real': copy.deepcopy(graph['nodes'][index]['arguments']['real'])}
    if not (input_removed(index) and to_void):
        args['incoming' if input_removed(index) else 'amount'] = copy.deepcopy(graph['nodes'][index]['arguments']['amount']) if index == 0 else binding('invoke', destination(0))
    if extra_added(index): args['extra'] = {'constant': int(extra_value)}
    return args

def caller_exits():
    return {'return': binding('invoke_second', destination(1))} if output_changed(1) else copy.deepcopy(graph['exits'])

def verify_rows(rows):
    merged = {row['id']: {'draft': (f.project/row['path']).read_text()} for row in f.metadata('describe', project=str(f.manifest))['units']} | rows
    shared = json.loads(merged[n.caller+'Body/body:common']['draft'])
    assert shared['entry'] == graph['entry'] and shared['edges'] == graph['edges'] and shared['exits'] == caller_exits()
    for index, (fn, sig) in enumerate(zip(functions, nexts)):
        assert n.canonical(f.metadata('inspect', text=merged[fn]['draft'])['signature']) == sig
        assert shared['nodes'][index]['signature'] == sig and shared['nodes'][index]['arguments'] == caller_arguments(index)
        assert shared['nodes'][index]['intent'] == graph['nodes'][index]['intent']
        leaf = json.loads(merged[fn+'Body/body:common']['draft']); code = next(row for row in leaf['nodes'] if row['kind'] == 'code')
        amount = {'constant': int(replacement)} if input_removed(index) and to_void else {'input': 'incoming' if input_removed(index) else 'amount'}
        assert code['signature'] == old and code['arguments'] == {'amount': amount, 'real': {'input': 'real'}}
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
        at = leaf['entry']; routes = {row['from']: row['to'] for row in leaf['edges']}; path = []
        while at in {row['id'] for row in leaf['nodes']}:
            assert at not in path; path.append(at); at = routes.get(at, '')
        assert set(path) == {row['id'] for row in leaf['nodes']}
        fields = f.metadata('blueprintOutputSnapshot', functionText=merged[fn]['draft'])['fields']
        assert [(row['name'], row['type']) for row in fields] == [(name, outs(sig)[name]) for name in published if name not in missing]

def verify(checkpoint):
    rows = {row['id']: row for row in json.loads(checkpoint.read_text())['changes']}; verify_rows(rows); unchanged()
    group = rows[owner]['atomicEditGroup']
    assert set(functions+[fn+'Body/body:common' for fn in functions]+[n.caller+'Body', n.caller+'Body/body:common', owner]) <= set(group)
    return group

def verify_live(): verify_rows({})

def edit_contract(popover, index):
    base.edit_contract(popover, index)
    if input_removed(index): popover.locator('[data-signature-id=arg0] [data-signature-remove]').click()
    if extra_added(index) or input_removed(index) and not to_void:
        popover.locator('[data-signature-add=inputs]').click()
        row = popover.locator('[data-signature-kind=inputs] [data-signature-id]').last
        row.locator('[data-signature-name]').fill('extra' if extra_added(index) else 'incoming')
        row.locator('[data-signature-type]').click()
        f.page.get_by_role('dialog', name='속성 타입 선택', exact=True).locator('[data-type=long]').click()

def remap_title(index): return '입력 연결 갱신' if input_removed(index) else '호출 계약 갱신'

def select_contract(dialog, index):
    base.select_contract(dialog, index)
    for target in dialog.locator('section[data-abi-target]').all():
        key = target.get_attribute('data-abi-target')
        if key.startswith(('output:', 'create:', 'remove:')): continue
        if key.startswith('use:'):
            target.locator('[data-abi-input=amount]').select_option('value' if to_void else 'pin:incoming')
            if to_void: target.locator('[data-abi-value=amount]').fill(replacement)
        elif extra_added(index):
            target.locator('[data-abi-input=extra]').select_option('value'); target.locator('[data-abi-value=extra]').fill(extra_value)
        elif input_removed(index) and not to_void: target.locator('[data-abi-input=incoming]').select_option('pin:amount')
    if input_removed(index) and to_void: dialog.locator('[data-abi-disconnect=amount]').select_option('disconnect')

def verify_pins(panel, index):
    from playwright.sync_api import expect
    base.verify_pins(panel, index)
    method = panel.locator('[data-inline-method="'+functions[index]+'"]')
    expect(method.locator('[data-pin-side=inputs] [data-function-pin-name=amount]')).to_have_count(0 if input_removed(index) else 1)
    for name, present in [('extra', extra_added(index)), ('incoming', input_removed(index) and not to_void)]:
        pin = method.locator('[data-pin-side=inputs] [data-function-pin-name='+name+']')
        if present: expect(pin).to_have_attribute('data-function-pin-type', '정수')
        else: expect(pin).to_have_count(0)
