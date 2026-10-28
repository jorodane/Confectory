"""Explicit value input definitions and retained out/nonvoid return writers."""
import copy
import json
import v536_information_shared_output_return_mix_fixture as base

f, d, n, owner, mode = base.f, base.d, base.n, base.owner, base.mode
functions, old = base.functions, base.old
graphs, records, graph = base.graphs, base.records, base.graph
binding = base.binding
removed, added = [], []
extra_value, replacement = '9223372036854775806', '9223372036854775800'
joint, delete_only = mode.startswith('joint'), mode.startswith('delete')
nexts = [copy.deepcopy(old), copy.deepcopy(old)]
nexts[0]['args'].append({'name': 'extra', 'type': 'long'})
if joint or delete_only:
    nexts[0]['return'] = 'double'
    nexts[1]['args'] = nexts[1]['args'][1:] + ([] if delete_only else [{'name': 'fresh', 'type': 'long'}])
next(a for a in nexts[1]['args'] if a['name'] == 'count')['type'] = 'double'
if not delete_only: nexts[1]['return'] = 'double'
if joint: next(a for a in nexts[0]['args'] if a['name'] == 'count')['type'] = 'double'
new = nexts[0]

# Two actual writers must both be selected; no C# signature/body is rewritten.
for index, fn in enumerate(functions):
    leaf = graphs[fn]
    writer = next(row for row in leaf['nodes'] if row['kind'] == 'export' and row['output'] == 'count')
    duplicate = copy.deepcopy(writer) | {'id': 'count_second'}
    leaf['nodes'].append(duplicate)
    edge = next(row for row in leaf['edges'] if row['from'] == writer['id'])
    following = edge['to']; edge['to'] = duplicate['id']
    leaf['edges'].append({'from': duplicate['id'], 'port': 'next', 'to': following})
    prefix = 'function' if index == 0 else 'second'
    (f.project/(prefix+'.graph.json')).write_text(json.dumps(leaf))
    defs = f.metadata('featureBlueprintNodes', featureSource=(f.project/('elements/'+fn.split('::')[1]+'.celem')).read_text(), graph=leaf)
    records[fn]['definitionHash'] = next(row['definitionHash'] for row in defs['nodes'] if row['id'] == 'body')
    (f.project/(prefix+'.node.json')).write_text(json.dumps(records[fn]))
snapshot = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}

def unchanged():
    assert all((f.project/path).read_bytes() == raw for path, raw in snapshot.items())

def changed_outputs(index):
    sig = nexts[index]
    return {a['name']: a['type'] for a in sig['args'] if a.get('mode') == 'out' and a['type'] != 'long'} | ({'return': sig['return']} if sig['return'] != old['return'] else {})

def removed_input(index): return index == 1 and (joint or delete_only)

def request():
    result = base.request()
    for index, (row, sig) in enumerate(zip(result['changes'], nexts)):
        row['signature'] = copy.deepcopy(sig)
        args = {k: result[k] for k in ['project', 'manifest', 'id', 'units']}
        inputs = f.metadata('informationFunctionInputs', **args, function=row['id'])
        mapping = base.selections(result, row['id'], sig)
        mapping['args']['amount'] = None if removed_input(index) else 'amount'
        if not changed_outputs(index):
            mapping.pop('outputs')
            for plan in mapping['callers'].values(): plan.pop('outputs')
        for key, plan in mapping['callers'].items():
            if index == 0: plan['inputs']['extra'] = {'valueJson': extra_value}
            elif removed_input(index):
                plan['inputs'].pop('amount')
                if delete_only: plan['disconnect'] = {'amount': inputs[key]['bindings']['amount']}
                else: plan['inputs']['fresh'] = 'amount'
        if removed_input(index):
            uses = f.metadata('informationFunctionInputUses', **args, function=row['id'])
            mapping['implementations'] = {key: {k: plan[k] for k in ['graph', 'node', 'argument', 'hash', 'before']} |
                {'value': {'valueJson': replacement} if delete_only else {'input': 'fresh'}} for key, plan in uses.items() if plan['input'] == 'amount'}
        row['mapping'] = mapping
    return result

def caller_arguments(index):
    if index == 0: return copy.deepcopy(graph['nodes'][0]['arguments']) | {'extra': {'constant': int(extra_value)}}
    args = {'real': copy.deepcopy(graph['nodes'][1]['arguments']['real'])}
    if not (removed_input(index) and delete_only):
        args['fresh' if removed_input(index) else 'amount'] = binding('invoke', 'stable' if 'return' in changed_outputs(0) else 'return')
    return args

def caller_exits(): return {'return': binding('invoke_second', 'stable')}

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
        amount = {'constant': int(replacement)} if removed_input(index) and delete_only else {'input': 'fresh' if removed_input(index) else 'amount'}
        assert code['signature'] == old and code['arguments'] == {'amount': amount, 'real': {'input': 'real'}}
        assert json.loads(merged[fn+'Body/body:common/node:body']['draft'])['source'] == records[fn]['source']
        for writer in [row for row in leaf['nodes'] if row['kind'] == 'export']:
            if writer['output'] in changed_outputs(index):
                assert writer['arguments'] == {'value': {'input': 'real'}} and writer['signature']['args'][0]['type'] == 'double'
            else: assert writer == next(row for row in graphs[fn]['nodes'] if row['id'] == writer['id'])
        fields = f.metadata('blueprintOutputSnapshot', functionText=merged[fn]['draft'])['fields']
        assert [(row['name'], row['type']) for row in fields] == [(a['name'], a['type']) for a in sig['args'] if a.get('mode') == 'out'] + [('return', sig['return'])]

def verify(checkpoint):
    rows = {row['id']: row for row in json.loads(checkpoint.read_text())['changes']}; verify_rows(rows); unchanged()
    group = rows[owner]['atomicEditGroup']
    assert set(functions+[fn+'Body/body:common' for fn in functions]+[n.caller+'Body', n.caller+'Body/body:common', owner]) <= set(group)
    return group

def verify_live(): verify_rows({})

def edit_contract(popover, index):
    # Edit original output IDs before the input deletion changes their order.
    for field, typ in [('arg2', changed_outputs(index).get('count')), ('return', changed_outputs(index).get('return'))]:
        if typ:
            popover.locator('[data-signature-id='+field+'] [data-signature-type]').click()
            f.page.get_by_role('dialog', name='속성 타입 선택', exact=True).locator('[data-type='+typ+']').click()
    if removed_input(index): popover.locator('[data-signature-id=arg0] [data-signature-remove]').click()
    if index == 0 or removed_input(index) and not delete_only:
        popover.locator('[data-signature-add=inputs]').click()
        row = popover.locator('[data-signature-kind=inputs] [data-signature-id]').last
        row.locator('[data-signature-name]').fill('extra' if index == 0 else 'fresh')
        row.locator('[data-signature-type]').click()
        f.page.get_by_role('dialog', name='속성 타입 선택', exact=True).locator('[data-type=long]').click()

def remap_title(index): return '입력 연결 갱신' if removed_input(index) else '호출 계약 갱신'

def select_contract(dialog, index):
    for target in dialog.locator('section[data-abi-target]').all():
        key = target.get_attribute('data-abi-target')
        if key.startswith('output:'): target.locator('[data-abi-input=value]').select_option('pin:real')
        elif key.startswith('use:'):
            target.locator('[data-abi-input=amount]').select_option('value' if delete_only else 'pin:fresh')
            if delete_only: target.locator('[data-abi-value=amount]').fill(replacement)
        elif index == 0:
            target.locator('[data-abi-input=extra]').select_option('value'); target.locator('[data-abi-value=extra]').fill(extra_value)
        elif removed_input(index) and not delete_only: target.locator('[data-abi-input=fresh]').select_option('pin:amount')
    if removed_input(index) and delete_only: dialog.locator('[data-abi-disconnect=amount]').select_option('disconnect')
    for name in changed_outputs(index): dialog.locator('[data-abi-output='+name+']').select_option('stable')

def verify_pins(panel, index):
    from playwright.sync_api import expect
    method = panel.locator('[data-inline-method="'+functions[index]+'"]')
    expect(method.locator('[data-pin-side=inputs] [data-function-pin-name=amount]')).to_have_count(0 if removed_input(index) else 1)
    name = 'extra' if index == 0 else 'fresh'
    pin = method.locator('[data-pin-side=inputs] [data-function-pin-name='+name+']')
    if index == 0 or removed_input(index) and not delete_only: expect(pin).to_have_attribute('data-function-pin-type', '정수')
    else: expect(pin).to_have_count(0)
    for name in ['count', 'stable', 'return']:
        label = '결과' if name == 'return' else name
        expect(method.locator('[data-pin-side=outputs] [data-function-pin-name="'+label+'"]')).to_have_attribute('data-function-pin-type', '실수' if name in changed_outputs(index) else '정수')
