"""Input definitions and type edits preserve explicit old value identities."""
import copy
import json
import v536_information_shared_input_definitions_fixture as base

f, d, n, owner, mode = base.f, base.d, base.n, base.owner, base.mode
functions, old = base.functions, base.old
graphs, records, graph, snapshot = base.graphs, base.records, base.graph, base.snapshot
removed, added = [], []
unchanged = base.unchanged
extra_value, replacement = base.extra_value, base.replacement
text_value = '명시한 새 입력 😀'
joint = mode.startswith('joint')
nexts = copy.deepcopy(base.nexts)
if joint:
    nexts[0]['args'][0]['type'] = 'string'
else:
    nexts[1] = copy.deepcopy(old)
    nexts[1]['args'][0]['type'] = 'string'
new = nexts[0]


def request():
    result = base.request()
    typed = base.base.request()
    if joint:
        row = result['changes'][0]
        row['signature'] = copy.deepcopy(nexts[0])
        row['mapping']['args']['amount'] = None
        row['mapping']['implementations'] = copy.deepcopy(typed['changes'][0]['mapping']['implementations'])
        for use in row['mapping']['implementations'].values():
            use['value'] = {'input': 'extra'}
        for plan in row['mapping']['callers'].values():
            plan['inputs']['amount'] = {'valueJson': json.dumps(text_value, ensure_ascii=False)}
            plan['inputs']['extra'] = 'amount'
    else:
        result['changes'][1] = copy.deepcopy(typed['changes'][1])
    return result


def caller_arguments(index):
    original = copy.deepcopy(graph['nodes'][index]['arguments'])
    if index == 0:
        return ({'amount': {'constant': text_value}, 'real': original['real'], 'extra': original['amount']}
                if joint else original | {'extra': {'constant': int(extra_value)}})
    return ({'real': original['real'], 'fresh': original['amount']} if joint
            else {'amount': {'constant': text_value}, 'real': original['real']})


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
        value = {'input': 'extra' if index == 0 else 'fresh'} if joint else {'input': 'amount'} if index == 0 else {'constant': int(replacement)}
        assert code['signature'] == old and code['arguments'] == {'amount': value, 'real': {'input': 'real'}}
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
    if joint or index == 1:
        if index == 0 or not joint:
            popover.locator('[data-signature-id=arg0] [data-signature-type]').click()
            f.page.get_by_role('dialog', name='속성 타입 선택', exact=True).locator('[data-type=string]').click()
    if joint or index == 0:
        base.edit_contract(popover, index)


def remap_title(index):
    return '입력 연결 갱신' if joint or index == 1 else '호출 계약 갱신'


def select_contract(dialog, index):
    if not joint and index == 0 or joint and index == 1:
        return base.select_contract(dialog, index)
    for target in dialog.locator('section[data-abi-target]').all():
        use = target.get_attribute('data-abi-target').startswith('use:')
        target.locator('[data-abi-input=amount]').select_option('pin:extra' if use and joint else 'value')
        if not (use and joint):
            target.locator('[data-abi-value=amount]').fill(replacement if use else text_value)
        if not use and joint:
            target.locator('[data-abi-input=extra]').select_option('pin:amount')
    dialog.locator('[data-abi-disconnect=amount]').select_option('disconnect')
    if joint:
        from playwright.sync_api import expect
        dialog.locator('[data-abi-remap-accept]').click()
        expect(dialog).to_be_visible()
        expect(dialog.locator('[data-abi-error]')).to_contain_text('사용하는 기존 연결')
        dialog.locator('[data-abi-disconnect=amount]').select_option('')


def verify_pins(window, index):
    from playwright.sync_api import expect
    method = window.locator('[data-inline-method="'+functions[index]+'"]')
    expect(method.locator('[data-pin-side=outputs] [data-function-pin-name=count]')).to_have_attribute('data-function-pin-type', '정수')
    for arg in nexts[index]['args']:
        if arg.get('mode') == 'out':continue
        expect(method.locator('[data-pin-side=inputs] [data-function-pin-name="'+arg['name']+'"]')).to_have_attribute('data-function-pin-type', {'long':'정수','double':'실수','string':'글자'}[arg['type']])
    if joint and index == 1:
        expect(method.locator('[data-pin-side=inputs] [data-function-pin-name=amount]')).to_have_count(0)
