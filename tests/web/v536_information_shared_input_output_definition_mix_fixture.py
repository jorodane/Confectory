"""Explicit input type/use replacements and original output graph plans."""
import copy
import json
import v536_information_shared_output_definition_mix_fixture as base

f, d, n, owner, mode = base.f, base.d, base.n, base.owner, base.mode
functions, old, nexts = base.functions, base.old, base.nexts
graphs, records, graph, snapshot = base.graphs, base.records, base.graph, base.snapshot
unchanged, binding = base.unchanged, base.binding
joint = mode.startswith('joint')
if not joint and not mode.startswith(('void', 'fromvoid')):
    nexts[1].clear(); nexts[1].update(copy.deepcopy(old)); nexts[1]['args'][0]['type'] = 'string'
else:
    nexts[0]['args'][0]['type'] = 'string'
    if joint or mode.startswith('fromvoid'): nexts[1]['args'][0]['type'] = 'string'
new, removed, added = nexts[0], [], []
replacement, text_value = '41', '명시한 새 입력 😀'
outs, removed_for, added_for, changed_for = base.outs, base.removed_for, base.added_for, base.changed_for
destination, literal, published = base.destination, base.literal, base.published

def input_changed(index): return nexts[index]['args'][0]['type'] != old['args'][0]['type']
def output_changed(index): return bool(removed_for(nexts[index]) or added_for(nexts[index]) or changed_for(nexts[index]))

def request():
    result = base.request()
    for index, (row, sig) in enumerate(zip(result['changes'], nexts)):
        mapping = row['mapping']; mapping['args']['amount'] = None if input_changed(index) else 'amount'
        if input_changed(index):
            args = {k: result[k] for k in ['project', 'manifest', 'id', 'units']}
            inputs = f.metadata('informationFunctionInputs', **args, function=row['id'])
            uses = f.metadata('informationFunctionInputUses', **args, function=row['id'])
            mapping['implementations'] = {key: {k: plan[k] for k in ['graph', 'node', 'argument', 'hash', 'before']} |
                                          {'value': {'valueJson': replacement}} for key, plan in uses.items() if plan['input'] == 'amount'}
            for key, plan in mapping['callers'].items():
                plan['inputs']['amount'] = {'valueJson': json.dumps(text_value, ensure_ascii=False)}
                plan['disconnect'] = {'amount': inputs[key]['bindings']['amount']}
        if not output_changed(index):
            for plan in mapping['callers'].values(): plan.pop('outputs')
    return result

def caller_arguments(index):
    return {'amount': {'constant': text_value} if input_changed(index) else
            copy.deepcopy(graph['nodes'][index]['arguments']['amount']) if index == 0 else binding('invoke', destination(0)),
            'real': copy.deepcopy(graph['nodes'][index]['arguments']['real'])}

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
        assert code['signature'] == old and code['arguments'] == {'amount': {'constant': int(replacement)} if input_changed(index) else {'input': 'amount'}, 'real': {'input': 'real'}}
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
    if input_changed(index):
        popover.locator('[data-signature-id=arg0] [data-signature-type]').click()
        f.page.get_by_role('dialog', name='속성 타입 선택', exact=True).locator('[data-type=string]').click()
    base.edit_contract(popover, index)

def remap_title(index): return '입력 연결 갱신' if input_changed(index) else '호출 계약 갱신'

def select_contract(dialog, index):
    base.select_contract(dialog, index)
    if input_changed(index):
        for target in dialog.locator('section[data-abi-target]').all():
            key = target.get_attribute('data-abi-target')
            # Removal sections have no input fields; base already selects the
            # mandatory whole-writer removal for every such section.
            if key.startswith(('output:', 'create:', 'remove:')): continue
            target.locator('[data-abi-input=amount]').select_option('value')
            target.locator('[data-abi-value=amount]').fill(replacement if key.startswith('use:') else text_value)
        dialog.locator('[data-abi-disconnect=amount]').select_option('disconnect')

def verify_pins(panel, index):
    from playwright.sync_api import expect
    base.verify_pins(panel, index)
    expect(panel.locator('[data-inline-method="'+functions[index]+'"] [data-pin-side=inputs] [data-function-pin-name=amount]')).to_have_attribute('data-function-pin-type', '글자' if input_changed(index) else '정수')
