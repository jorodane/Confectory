"""Explicit value-input type replacement combined with scalar nonvoid returns."""
import copy
import json
import v536_information_shared_output_return_mix_fixture as base

f, d, n, owner, mode = base.f, base.d, base.n, base.owner, base.mode
functions, old = base.functions, base.old
graphs, records, graph, snapshot = base.graphs, base.records, base.graph, base.snapshot
unchanged, binding = base.unchanged, base.binding
joint = mode.startswith(('joint', 'triple'))
nexts = [copy.deepcopy(old), copy.deepcopy(old)]
nexts[0]['return'] = 'double'
nexts[1]['args'][0]['type'] = 'string'
if joint:
    nexts[0]['args'][0]['type'] = 'string'
    nexts[1]['return'] = 'double'
if mode.startswith('triple'):
    for sig in nexts: sig['args'][2]['type'] = 'double'
new, removed, added = nexts[0], [], []
replacement, text_value = '41', '명시한 새 입력 😀'

def input_changed(index): return nexts[index]['args'][0]['type'] != old['args'][0]['type']
def return_changed(index): return nexts[index]['return'] != old['return']
def changed_outputs(index):
    return ({'return': nexts[index]['return']} if return_changed(index) else {}) | ({'count': 'double'} if nexts[index]['args'][2]['type'] != 'long' else {})

def request():
    result = base.request()
    for index, (row, sig) in enumerate(zip(result['changes'], nexts)):
        row['signature'] = copy.deepcopy(sig)
        args = {k: result[k] for k in ['project', 'manifest', 'id', 'units']}
        inputs = f.metadata('informationFunctionInputs', **args, function=row['id'])
        mapping = {'before': copy.deepcopy(old), 'args': {a['name']: None if a['name'] == 'amount' and input_changed(index) else a['name'] for a in old['args']},
                   'callers': {key: {k: plan[k] for k in ['graph', 'node', 'hash']} | {
                       'inputs': {'amount': {'valueJson': json.dumps(text_value, ensure_ascii=False)} if input_changed(index) else 'amount', 'real': 'real'},
                       'disconnect': {'amount': plan['bindings']['amount']} if input_changed(index) else {}}
                       for key, plan in inputs.items()}}
        if input_changed(index):
            uses = f.metadata('informationFunctionInputUses', **args, function=row['id'])
            mapping['implementations'] = {key: {k: plan[k] for k in ['graph', 'node', 'argument', 'hash', 'before']} |
                                          {'value': {'valueJson': replacement}} for key, plan in uses.items() if plan['input'] == 'amount'}
        if return_changed(index):
            writers = f.metadata('informationFunctionOutputs', **args, function=row['id'])
            changed = changed_outputs(index)
            mapping['outputs'] = {key: {k: plan[k] for k in ['graph', 'node', 'name', 'hash', 'before']} |
                                  {'type': changed[plan['name']], 'source': {'input': 'real'}} for key, plan in writers.items() if plan['name'] in changed}
            for plan in mapping['callers'].values(): plan['outputs'] = {name: 'stable' if name in changed else name for name in ['count', 'stable', 'return']}
        row['mapping'] = mapping
    return result

def caller_arguments(index):
    return {'amount': {'constant': text_value} if input_changed(index) else copy.deepcopy(graph['nodes'][index]['arguments']['amount']),
            'real': copy.deepcopy(graph['nodes'][index]['arguments']['real'])}

def caller_exits(): return {'return': binding('invoke_second', 'stable')} if 'count' in changed_outputs(1) else copy.deepcopy(graph['exits'])

def verify_rows(rows):
    merged = {row['id']: {'draft': (f.project/row['path']).read_text()} for row in f.metadata('describe', project=str(f.manifest))['units']} | rows
    shared = json.loads(merged[n.caller+'Body/body:common']['draft'])
    assert shared['entry'] == graph['entry'] and shared['edges'] == graph['edges'] and shared['exits'] == caller_exits()
    for index, (fn, sig) in enumerate(zip(functions, nexts)):
        assert n.canonical(f.metadata('inspect', text=merged[fn]['draft'])['signature']) == sig
        assert shared['nodes'][index]['signature'] == sig and shared['nodes'][index]['arguments'] == caller_arguments(index)
        assert shared['nodes'][index]['intent'] == graph['nodes'][index]['intent']
        leaf = json.loads(merged[fn+'Body/body:common']['draft'])
        assert leaf['entry'] == graphs[fn]['entry'] and leaf['edges'] == graphs[fn]['edges']
        assert {row['id'] for row in leaf['nodes']} == {row['id'] for row in graphs[fn]['nodes']}
        code = next(row for row in leaf['nodes'] if row['kind'] == 'code')
        assert code['signature'] == old and code['arguments'] == {'amount': {'constant': int(replacement)} if input_changed(index) else {'input': 'amount'}, 'real': {'input': 'real'}}
        assert json.loads(merged[fn+'Body/body:common/node:body']['draft'])['source'] == records[fn]['source']
        for writer in [row for row in leaf['nodes'] if row['kind'] == 'export']:
            if writer['output'] in changed_outputs(index):
                assert writer['arguments'] == {'value': {'input': 'real'}} and writer['signature']['args'][0]['type'] == 'double'
            else: assert writer == next(row for row in graphs[fn]['nodes'] if row['id'] == writer['id'])
        fields = f.metadata('blueprintOutputSnapshot', functionText=merged[fn]['draft'])['fields']
        assert [(row['name'], row['type']) for row in fields] == [('count', sig['args'][2]['type']), ('stable', 'long'), ('return', sig['return'])]

def verify(checkpoint):
    rows = {row['id']: row for row in json.loads(checkpoint.read_text())['changes']}; verify_rows(rows); unchanged()
    group = rows[owner]['atomicEditGroup']
    assert set(functions+[fn+'Body/body:common' for fn in functions]+[n.caller+'Body', n.caller+'Body/body:common', owner]) <= set(group)
    return group

def verify_live(): verify_rows({})

def edit_contract(popover, index):
    for field, typ in [('arg0', 'string' if input_changed(index) else None), ('arg2', 'double' if 'count' in changed_outputs(index) else None), ('return', 'double' if return_changed(index) else None)]:
        if typ:
            popover.locator('[data-signature-id='+field+'] [data-signature-type]').click()
            f.page.get_by_role('dialog', name='속성 타입 선택', exact=True).locator('[data-type='+typ+']').click()

def remap_title(index): return '입력 연결 갱신' if input_changed(index) else '호출 계약 갱신'

def select_contract(dialog, index):
    for target in dialog.locator('section[data-abi-target]').all():
        key = target.get_attribute('data-abi-target')
        if key.startswith('output:'): target.locator('[data-abi-input=value]').select_option('pin:real')
        elif input_changed(index):
            target.locator('[data-abi-input=amount]').select_option('value')
            target.locator('[data-abi-value=amount]').fill(replacement if key.startswith('use:') else text_value)
    if input_changed(index): dialog.locator('[data-abi-disconnect=amount]').select_option('disconnect')
    for name in changed_outputs(index): dialog.locator('[data-abi-output='+name+']').select_option('stable')

def verify_pins(panel, index):
    from playwright.sync_api import expect
    method = panel.locator('[data-inline-method="'+functions[index]+'"]')
    expect(method.locator('[data-pin-side=inputs] [data-function-pin-name=amount]')).to_have_attribute('data-function-pin-type', '글자' if input_changed(index) else '정수')
    for name, typ in [('count', '실수' if 'count' in changed_outputs(index) else '정수'), ('stable', '정수'), ('결과', '실수' if return_changed(index) else '정수')]:
        expect(method.locator('[data-pin-side=outputs] [data-function-pin-name="'+name+'"]')).to_have_attribute('data-function-pin-type', typ)
