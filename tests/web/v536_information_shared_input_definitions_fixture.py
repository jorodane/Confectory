"""Explicit input addition and used-input replacement share one caller."""
import copy
import json
import v536_information_shared_inputs_with_out_fixture as base

f, d, n, owner, mode = base.f, base.d, base.n, base.owner, base.mode
functions, old = base.functions, base.old
graphs, records, graph, snapshot = base.graphs, base.records, base.graph, base.snapshot
removed, added = [], []
unchanged = base.unchanged
extra_value = '9223372036854775806'
replacement = '9223372036854775800'
delete_only = mode.startswith('delete')
nexts = [copy.deepcopy(old), copy.deepcopy(old)]
nexts[0]['args'].append({'name': 'extra', 'type': 'long'})
nexts[1]['args'] = nexts[1]['args'][1:]+([] if delete_only else [{'name': 'fresh', 'type': 'long'}])
new = nexts[0]


def request():
    result = base.base.base.request()
    for index, row in enumerate(result['changes']):
        row['signature'] = copy.deepcopy(nexts[index])
        args = {k: result[k] for k in ['project', 'manifest', 'id', 'units']}
        inputs = f.metadata('informationFunctionInputs', **args, function=row['id'])
        uses = f.metadata('informationFunctionInputUses', **args, function=row['id'])
        mapping = {'before': copy.deepcopy(old), 'args': {'amount': 'amount' if index == 0 else None, 'real': 'real', 'count': 'count'},
                   'callers': {key: {k: plan[k] for k in ['graph', 'node', 'hash']} | {
                       'inputs': {'amount': 'amount', 'real': 'real', 'extra': {'valueJson': extra_value}} if index == 0 else {'real': 'real'} | ({} if delete_only else {'fresh': 'amount'}),
                       'disconnect': {'amount': plan['bindings']['amount']} if index == 1 and delete_only else {}} for key, plan in inputs.items()}}
        if index == 1:
            mapping['implementations'] = {key: {k: plan[k] for k in ['graph', 'node', 'argument', 'hash', 'before']} | {'value': {'valueJson': replacement} if delete_only else {'input': 'fresh'}}
                                          for key, plan in uses.items() if plan['input'] == 'amount'}
        row['mapping'] = mapping
    return result


def caller_arguments(index):
    original = copy.deepcopy(graph['nodes'][index]['arguments'])
    if index == 0:
        return original | {'extra': {'constant': int(extra_value)}}
    return {'real': original['real']} | ({} if delete_only else {'fresh': original['amount']})


def caller_exits():
    return copy.deepcopy(graph['exits'])


def verify_rows(rows):
    units = f.metadata('describe', project=str(f.manifest))['units']
    rows = {row['id']: {'draft': (f.project/row['path']).read_text()} for row in units} | rows
    caller = json.loads(rows[n.caller+'Body/body:common']['draft'])
    assert caller['entry'] == graph['entry'] and caller['edges'] == graph['edges'] and caller['exits'] == graph['exits']
    for index, (fn, signature) in enumerate(zip(functions, nexts)):
        assert n.canonical(f.metadata('inspect', text=rows[fn]['draft'])['signature']) == signature
        assert caller['nodes'][index]['signature'] == signature and caller['nodes'][index]['arguments'] == caller_arguments(index)
        assert caller['nodes'][index]['intent'] == graph['nodes'][index]['intent']
        leaf = json.loads(rows[fn+'Body/body:common']['draft'])
        assert leaf['entry'] == graphs[fn]['entry'] and leaf['edges'] == graphs[fn]['edges']
        assert {row['id'] for row in leaf['nodes']} == {row['id'] for row in graphs[fn]['nodes']}
        code = next(row for row in leaf['nodes'] if row['kind'] == 'code')
        assert code['signature'] == old and code['arguments'] == {'amount': {'input': 'amount'} if index == 0 else {'constant': int(replacement)} if delete_only else {'input': 'fresh'}, 'real': {'input': 'real'}}
        assert [row for row in leaf['nodes'] if row['kind'] == 'export'] == [row for row in graphs[fn]['nodes'] if row['kind'] == 'export']
        assert json.loads(rows[fn+'Body/body:common/node:body']['draft'])['source'] == records[fn]['source']
        assert f.metadata('blueprintOutputSnapshot', functionText=rows[fn]['draft'])['fields'][0]['type'] == 'long'


def verify(checkpoint):
    rows = {row['id']: row for row in json.loads(checkpoint.read_text())['changes']}
    verify_rows(rows); unchanged()
    group = rows[owner]['atomicEditGroup']
    assert set(functions+[fn+'Body/body:common' for fn in functions]+[n.caller+'Body', n.caller+'Body/body:common', owner]) <= set(group)
    return group


def verify_live():
    verify_rows({})


def edit_contract(popover, index):
    if index == 1:
        popover.locator('[data-signature-id=arg0] [data-signature-remove]').click()
    if index == 0 or not delete_only:
        popover.locator('[data-signature-add=inputs]').click()
        row = popover.locator('[data-signature-kind=inputs] [data-signature-id]').last
        row.locator('[data-signature-name]').fill('extra' if index == 0 else 'fresh')
        row.locator('[data-signature-type]').click()
        f.page.get_by_role('dialog', name='속성 타입 선택', exact=True).locator('[data-type=long]').click()


def remap_title(index):
    return '호출 계약 갱신' if index == 0 else '입력 연결 갱신'


def select_contract(dialog, index):
    if index == 0:
        dialog.locator('[data-abi-input=extra]').select_option('value')
        dialog.locator('[data-abi-value=extra]').fill(extra_value)
    else:
        for target in dialog.locator('section[data-abi-target]').all():
            if target.get_attribute('data-abi-target').startswith('use:'):
                target.locator('[data-abi-input=amount]').select_option('value' if delete_only else 'pin:fresh')
                if delete_only:
                    target.locator('[data-abi-value=amount]').fill(replacement)
            elif not delete_only:
                target.locator('[data-abi-input=fresh]').select_option('pin:amount')
        dialog.locator('[data-abi-disconnect=amount]').select_option('disconnect')
        if not delete_only:
            from playwright.sync_api import expect
            dialog.locator('[data-abi-remap-accept]').click()
            expect(dialog).to_be_visible()
            expect(dialog.locator('[data-abi-error]')).to_contain_text('사용하는 기존 연결')
            dialog.locator('[data-abi-disconnect=amount]').select_option('')


def verify_pins(window, index):
    from playwright.sync_api import expect
    method = window.locator('[data-inline-method="'+functions[index]+'"]')
    expect(method.locator('[data-pin-side=outputs] [data-function-pin-name=count]')).to_have_attribute('data-function-pin-type', '정수')
    expect(method.locator('[data-pin-side=inputs] [data-function-pin-name=amount]')).to_have_count(1 if index == 0 else 0)
    name = 'extra' if index == 0 else 'fresh'
    pin = method.locator('[data-pin-side=inputs] [data-function-pin-name="'+name+'"]')
    if index == 0 or not delete_only:
        expect(pin).to_have_attribute('data-function-pin-type', '정수')
    else:
        expect(pin).to_have_count(0)
