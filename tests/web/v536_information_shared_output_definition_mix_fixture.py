"""Explicit output graph and retained writer plans in one original candidate."""
import copy
import hashlib
import json
import v536_information_shared_outputs_fixture as base

f, d, n, owner, mode = base.f, base.d, base.n, base.owner, base.mode
functions = base.functions
joint, to_void, from_void = mode.startswith('joint'), mode.startswith('void'), mode.startswith('fromvoid')
old = {'args': [{'name': 'amount', 'type': 'long'}, {'name': 'real', 'type': 'double'},
                {'name': 'count', 'type': 'long', 'mode': 'out'},
                {'name': 'stable', 'type': 'long', 'mode': 'out'}], 'return': 'void' if from_void else 'long'}
nexts = [copy.deepcopy(old), copy.deepcopy(old)]
nexts[0]['args'] = [a for a in nexts[0]['args'] if a['name'] != 'count'] + [{'name': 'fresh', 'type': 'long', 'mode': 'out'}]
if joint:
    nexts[1]['args'] = [a for a in nexts[1]['args'] if a['name'] != 'count'] + [{'name': 'fresh', 'type': 'long', 'mode': 'out'}]
    for sig in nexts:
        next(a for a in sig['args'] if a['name'] == 'stable')['type'] = 'double'
        sig['return'] = 'double'
else:
    nexts[1]['args'][2]['type'] = 'double'
    nexts[1]['return'] = 'string' if from_void else 'double'
    if to_void: nexts[0]['return'] = 'void'
    if from_void: nexts[0]['return'] = 'string'
new, removed, added = nexts[0], [], []
outs = lambda sig: {a['name']: a['type'] for a in sig['args'] if a.get('mode') == 'out'} | ({} if sig['return'] == 'void' else {'return': sig['return']})
removed_for = lambda sig: [name for name in outs(old) if name not in outs(sig)]
added_for = lambda sig: [name for name in outs(sig) if name not in outs(old)]
changed_for = lambda sig: {name: typ for name, typ in outs(sig).items() if name in outs(old) and typ != outs(old)[name]}
binding = lambda node, output: {'node': node} | ({'output': output} if output != 'return' else {})
literal = lambda name, index: json.dumps('한글 반환 '+str(index)+' 😀', ensure_ascii=False) if name == 'return' else '23' if index == 0 else '9223372036854775806'
published = list(outs(old))
graphs, records = {}, {}
for index, fn in enumerate(functions):
    prefix = 'function' if index == 0 else 'second'
    source = ('function '+fn+' (long amount,double real,out long count,out long stable) -> '+old['return']+
              ' {value editorName='+json.dumps(('첫째' if index == 0 else '둘째')+' 공유 출력')+
              ';value blueprintPublishedOutputs='+json.dumps(json.dumps(published))+';}')
    prepared = f.metadata('blueprintPrepareFeature', id=fn, text=source, implementation=fn+'Body', graphPath=prefix+'.graph.json', nodePath=prefix+'.node.json')
    (f.project/('elements/'+fn.split('::')[1]+'.celem')).write_text(prepared['function'])
    (f.project/(fn.split('::')[1]+'Body.celem')).write_text(prepared['implementation'])
    leaf = prepared['graph']
    writer = next(row for row in leaf['nodes'] if row['kind'] == 'export' and row['output'] == 'count')
    duplicate = copy.deepcopy(writer) | {'id': 'count_second'}
    leaf['nodes'].append(duplicate)
    edge = next((row for row in leaf['edges'] if row['from'] == writer['id']), None)
    following = edge['to'] if edge else ''
    if edge: edge['to'] = duplicate['id']
    else: leaf['edges'].append({'from': writer['id'], 'port': 'next', 'to': duplicate['id']})
    if following: leaf['edges'].append({'from': duplicate['id'], 'port': 'next', 'to': following})
    graphs[fn] = leaf
    defs = f.metadata('featureBlueprintNodes', featureSource=prepared['function'], graph=leaf)
    records[fn] = prepared['node'] | {'definitionHash': next(row['definitionHash'] for row in defs['nodes'] if row['id'] == 'body'),
        'source': 'count=checked(amount+'+str(index+1)+');stable=amount;'+('return;' if from_void else 'return amount;')+' // 원문 · 9223372036854775806'}
    (f.project/(prefix+'.graph.json')).write_text(json.dumps(leaf))
    (f.project/(prefix+'.node.json')).write_text(json.dumps(records[fn]))
prepared = f.metadata('blueprintPrepareFeature', id=n.caller, text=n.caller_source, implementation=n.caller+'Body', graphPath='caller.graph.json', nodePath='unused.node.json')
graph = prepared['graph']; graph.update(profile='sync-acyclic-implicit-out-v1', nodes=[], entry='', edges=[], exits={'return': None})
header = prepared['implementation']
for fn, node in zip(functions, ['invoke', 'invoke_second']):
    linked = f.metadata('blueprintPrepareCall', id=n.caller+'Body', text=header,
        targetText=(f.project/('elements/'+fn.split('::')[1]+'.celem')).read_text(), graph=graph,
        definition={'id': node, 'feature': fn, 'intent': '원래 count/return 설명 · '+node, 'control': 'next'})
    header, graph = linked['implementation'], linked['graph']
graph['nodes'][0]['arguments'] = {'amount': {'input': 'first'}, 'real': {'constant': 1.25}}
graph['nodes'][1]['arguments'] = {'amount': binding('invoke', 'count'), 'real': {'constant': 2.5}}
graph.update(entry='invoke', edges=[{'from': 'invoke', 'port': 'next', 'to': 'invoke_second'}, {'from': 'invoke_second', 'port': 'next', 'to': 'exit:return'}], exits={'return': binding('invoke_second', 'count')})
(f.project/'Caller.celem').write_text(prepared['function']); (f.project/'CallerBody.celem').write_text(header); (f.project/'caller.graph.json').write_text(json.dumps(graph))
snapshot = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}


def unchanged():
    assert all((f.project/path).read_bytes() == raw for path, raw in snapshot.items())


def destination(index):
    return 'fresh' if 'fresh' in outs(nexts[index]) else 'stable'


def selections(result, fn, signature, index):
    args = {k: result[k] for k in ['project', 'manifest', 'id', 'units']}
    inputs = f.metadata('informationFunctionInputs', **args, function=fn)
    writers = f.metadata('informationFunctionOutputs', **args, function=fn)
    previews = f.metadata('informationFunctionOutputGraphs', **args, function=fn)
    removed, added, changed = removed_for(signature), added_for(signature), changed_for(signature)
    result = {'before': copy.deepcopy(old), 'args': {a['name']: None if a['name'] in removed else a['name'] for a in old['args']},
        'callers': {key: {k: row[k] for k in ['graph', 'node', 'hash']} | {'inputs': {'amount': 'amount', 'real': 'real'}, 'disconnect': {},
            'outputs': {name: destination(index) if name in removed or name in changed else name for name in outs(old)}} for key, row in inputs.items()}}
    if changed:
        result['outputs'] = {key: {k: row[k] for k in ['graph', 'node', 'name', 'hash', 'before']} | {'type': changed[row['name']], 'source': {'input': 'real'}} for key, row in writers.items() if row['name'] in changed}
    if removed or added:
        plans = {}
        for key, row in previews.items():
            removals = [{'name': name, 'writers': row['writers'][name], 'before': row['exits'].get(name, 'null')} for name in removed]
            deleted = {node for removal in removals for node in removal['writers']}
            def resolve(target):
                while target in deleted: target = next((e['to'] for e in row['edges'] if e['from'] == target and e['port'] == 'next'), '')
                return '' if target.startswith('exit:') and target[5:] in removed else target
            following = resolve(next((e['to'] for e in row['edges'] if e['from'] == 'body' and e['port'] == 'next'), ''))
            creates = []
            for name in added:
                creates.append({'node': 'created_'+name, 'name': name, 'type': outs(signature)[name], 'source': {'valueJson': literal(name, index)}, 'after': creates[-1]['node'] if creates else 'body', 'next': following})
            plans[key] = {'graph': key, 'hash': row['hash'], 'removes': removals, 'creates': creates, 'publicOutputs': [name for name in published if name not in removed]}
        result['outputGraphs'] = plans
    return result


def request():
    remap = {a['name']: None if a['name'] in removed_for(nexts[0]) else a['name'] for a in old['args']}
    result = n.request(nexts[0], remap)
    fn = functions[1]
    result['changes'].append({'type': 'function-edit', 'id': fn, 'hash': hashlib.sha256(result['units'][fn]['draft'].encode()).hexdigest(), 'name': '둘째 공유 출력', 'description': '정의와 writer/소비의 원래 대응 보존', 'signature': copy.deepcopy(nexts[1])})
    for index, row in enumerate(result['changes']): row['mapping'] = selections(result, row['id'], nexts[index], index)
    return result


def caller_arguments(index):
    return copy.deepcopy(graph['nodes'][0]['arguments']) if index == 0 else {'amount': binding('invoke', destination(0)), 'real': {'constant': 2.5}}


def caller_exits():
    return {'return': binding('invoke_second', destination(1))}


def verify_rows(rows):
    merged = {row['id']: {'draft': (f.project/row['path']).read_text()} for row in f.metadata('describe', project=str(f.manifest))['units']} | rows
    shared = json.loads(merged[n.caller+'Body/body:common']['draft'])
    assert shared['entry'] == graph['entry'] and shared['edges'] == graph['edges'] and shared['exits'] == caller_exits()
    for index, (fn, sig) in enumerate(zip(functions, nexts)):
        assert n.canonical(f.metadata('inspect', text=merged[fn]['draft'])['signature']) == sig
        assert shared['nodes'][index]['signature'] == sig and shared['nodes'][index]['arguments'] == caller_arguments(index) and shared['nodes'][index]['intent'] == graph['nodes'][index]['intent']
        leaf = json.loads(merged[fn+'Body/body:common']['draft'])
        code = next(row for row in leaf['nodes'] if row['kind'] == 'code')
        assert code['signature'] == old and code['arguments'] == {'amount': {'input': 'amount'}, 'real': {'input': 'real'}}
        assert json.loads(merged[fn+'Body/body:common/node:body']['draft'])['source'] == records[fn]['source']
        removed, added, changed = removed_for(sig), added_for(sig), changed_for(sig)
        for name in removed:
            assert not any(row['kind'] == 'export' and row['output'] == name for row in leaf['nodes']) and leaf['exits'].get(name) is None
        for name in added:
            writer = next(row for row in leaf['nodes'] if row['kind'] == 'export' and row['output'] == name)
            assert writer['arguments']['value'] == {'constant': json.loads(literal(name, index))}
        for name in outs(old):
            if name in removed: continue
            originals = [row for row in graphs[fn]['nodes'] if row['kind'] == 'export' and row['output'] == name]
            writers = [row for row in leaf['nodes'] if row['kind'] == 'export' and row['output'] == name]
            assert [row['id'] for row in writers] == [row['id'] for row in originals]
            if name in changed:
                for writer in writers: assert writer['arguments'] == {'value': {'input': 'real'}} and writer['signature']['args'][0]['type'] == 'double'
            else: assert writers == originals
        path = []; at = leaf['entry']; routes = {row['from']: row['to'] for row in leaf['edges']}
        while at in {row['id'] for row in leaf['nodes']}:
            assert at not in path; path.append(at); at = routes.get(at, '')
        assert set(path) == {row['id'] for row in leaf['nodes']}
        fields = f.metadata('blueprintOutputSnapshot', functionText=merged[fn]['draft'])['fields']
        assert [(row['name'], row['type']) for row in fields] == [(name, outs(sig)[name]) for name in published if name not in removed]


def verify(checkpoint):
    rows = {row['id']: row for row in json.loads(checkpoint.read_text())['changes']}; verify_rows(rows); unchanged()
    group = rows[owner]['atomicEditGroup']
    assert set(functions+[fn+'Body/body:common' for fn in functions]+[n.caller+'Body', n.caller+'Body/body:common', owner]) <= set(group)
    return group


def verify_live():
    verify_rows({row['id']: {'draft': (f.project/row['path']).read_text()} for row in f.metadata('describe', project=str(f.manifest))['units']})


def edit_contract(popover, index):
    from playwright.sync_api import expect
    sig = nexts[index]
    if 'count' in removed_for(sig): popover.locator('[data-signature-id=arg2] [data-signature-remove]').click()
    if from_void:
        popover.locator('[data-signature-add=outputs]').click()
        expect(popover.locator('[data-signature-id=return]')).to_have_count(1)
    if 'fresh' in added_for(sig):
        popover.locator('[data-signature-add=outputs]').click()
        field = popover.locator('[data-signature-kind=outputs] .feature-io-row:has(input:not([readonly]))').last
        field.locator('[data-signature-name]').fill('fresh'); field.locator('[data-signature-type]').click()
        f.page.get_by_role('dialog', name='속성 타입 선택', exact=True).locator('[data-type=long]').click()
    for name, typ in changed_for(sig).items():
        field = 'return' if name == 'return' else 'arg3' if name == 'stable' else 'arg2'
        popover.locator('[data-signature-id='+field+'] [data-signature-type]').click()
        f.page.get_by_role('dialog', name='속성 타입 선택', exact=True).locator('[data-type='+typ+']').click()
    if sig['return'] == 'void' and old['return'] != 'void': popover.locator('[data-signature-id=return] [data-signature-remove]').click()


def remap_title(index):
    return '호출 계약 갱신'


def select_contract(dialog, index):
    sig = nexts[index]
    for name in outs(old):
        if name in removed_for(sig) or name in changed_for(sig): dialog.locator('[data-abi-output='+name+']').select_option(destination(index))
    for control in dialog.locator('[data-abi-remove-output]').all(): control.select_option('remove')
    for target in dialog.locator('[data-abi-target^="output:"]').all(): target.locator('[data-abi-input=value]').select_option('pin:real')
    previous = None
    for name in added_for(sig):
        create = dialog.locator('[data-abi-target^="create:"][data-abi-target$="#'+name+'"]')
        create.locator('[data-abi-input=value]').select_option('value')
        raw = literal(name, index)
        create.locator('[data-abi-value=value]').fill(json.loads(raw) if outs(sig)[name] == 'string' else raw)
        if previous: create.locator('[data-abi-placement]').select_option(label='새 출력 '+previous+' 다음')
        else: create.locator('[data-abi-placement]').select_option('body')
        previous = name


def verify_pins(panel, index):
    from playwright.sync_api import expect
    expected = outs(nexts[index])
    for name in set(outs(old)) | set(expected):
        label = '결과' if name == 'return' else name
        pin = panel.locator('[data-inline-method="'+functions[index]+'"] [data-pin-side=outputs] [data-function-pin-name="'+label+'"]')
        if name not in expected: expect(pin).to_have_count(0)
        else: expect(pin).to_have_attribute('data-function-pin-type', {'long': '정수', 'double': '실수', 'string': '글자'}[expected[name]])
