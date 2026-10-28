"""Keep existing ref storage and native parameters while naming owned pins."""
import copy
import hashlib
import json
import v536_information_shared_callers_fixture as base

f, d, n, owner, mode = base.f, base.d, base.n, base.owner, base.mode
functions = base.functions
olds = [{'args': [{'name': 'amount', 'type': 'long'}, {'name': 'count', 'type': 'long', **({'mode': 'ref'} if index == 0 or not mode.startswith('mixed') else {})}], 'return': 'long'} for index in range(2)]
old = olds[0]
nexts = copy.deepcopy(olds)
for index, sig in enumerate(nexts):
    sig['args'][0]['name'] = ['leftAmount', 'rightAmount'][index]
    sig['args'][1]['name'] = ['leftCount', 'rightCount'][index]
new, removed, added = nexts[0], [], []
retry_field = 'arg0'
undo_steps = 1 if mode.startswith('mixed') else 3
graphs, records = {}, {}
for index, fn in enumerate(functions):
    prefix = 'function' if index == 0 else 'second'
    ref = olds[index]['args'][1].get('mode') == 'ref'
    source = 'function '+fn+' (long amount,'+('ref ' if ref else '')+'long count) -> long {value editorName='+json.dumps(('첫째' if index == 0 else '둘째')+' 공유 참조')+';}'
    prepared = f.metadata('blueprintPrepareFeature', id=fn, text=source, implementation=fn+'Body', graphPath=prefix+'.graph.json', nodePath=prefix+'.node.json')
    (f.project/('elements/'+fn.split('::')[1]+'.celem')).write_text(prepared['function'])
    (f.project/(fn.split('::')[1]+'Body.celem')).write_text(prepared['implementation'])
    leaf = prepared['graph']; graphs[fn] = copy.deepcopy(leaf)
    definitions = f.metadata('featureBlueprintNodes', featureSource=prepared['function'], graph=leaf)
    records[fn] = prepared['node'] | {'definitionHash': next(row['definitionHash'] for row in definitions['nodes'] if row['id'] == 'body'),
        'source': ('count=checked(count+amount);return count;' if ref else 'return checked(amount+count);')+' // 원문 · 9223372036854775806 😀\n'}
    (f.project/(prefix+'.graph.json')).write_text(json.dumps(leaf))
    (f.project/(prefix+'.node.json')).write_text(json.dumps(records[fn]))
caller_sig = {'args': [{'name': 'first', 'type': 'long'}, {'name': 'second', 'type': 'long', 'mode': 'ref'}], 'return': 'long'}
prepared = f.metadata('blueprintPrepareFeature', id=n.caller, text='function '+n.caller+' (long first,ref long second) -> long {}', implementation=n.caller+'Body', graphPath='caller.graph.json', nodePath='unused.node.json')
graph = prepared['graph']; graph.update(profile='sync-acyclic-ref-v1', nodes=[], entry='', edges=[], exits={'return': None})
header = prepared['implementation']
for fn, node in zip(functions, ['invoke', 'invoke_second']):
    linked = f.metadata('blueprintPrepareCall', id=n.caller+'Body', text=header,
        targetText=(f.project/('elements/'+fn.split('::')[1]+'.celem')).read_text(), graph=graph,
        definition={'id': node, 'feature': fn, 'intent': '같은 ref 저장소 · '+node, 'control': 'next'})
    header, graph = linked['implementation'], linked['graph']
graph['nodes'][0]['arguments'] = {'amount': {'input': 'first'}, 'count': {'input': 'second'}}
graph['nodes'][1]['arguments'] = {'amount': {'node': 'invoke'}, 'count': {'input': 'second'}}
graph.update(entry='invoke', edges=[{'from': 'invoke', 'port': 'next', 'to': 'invoke_second'}, {'from': 'invoke_second', 'port': 'next', 'to': 'exit:return'}], exits={'return': {'node': 'invoke_second'}})
(f.project/'Caller.celem').write_text(prepared['function']); (f.project/'CallerBody.celem').write_text(header); (f.project/'caller.graph.json').write_text(json.dumps(graph))
snapshot = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}

def unchanged(): assert all((f.project/path).read_bytes() == raw for path, raw in snapshot.items())

def request():
    maps = [{a['name']: b['name'] for a, b in zip(old['args'], new['args'])} for old, new in zip(olds, nexts)]
    result = n.request(nexts[0], maps[0]); fn = functions[1]
    result['changes'].append({'type': 'function-edit', 'id': fn, 'hash': hashlib.sha256(result['units'][fn]['draft'].encode()).hexdigest(),
        'name': '둘째 공유 참조', 'description': '원래 ref 계약과 본문 보존', 'signature': copy.deepcopy(nexts[1]), 'mapping': {'before': copy.deepcopy(olds[1]), 'args': maps[1]}})
    for index, row in enumerate(result['changes']):
        args = {k: result[k] for k in ['project', 'manifest', 'id', 'units']}
        bodies = f.metadata('informationFunctionBodies', **args, function=row['id'], includeBlueprintTargets=True)
        selected = {key: {k: body[k] for k in ['hash', 'path', 'whole']} |
                    {'beforeSignature': copy.deepcopy(body['signature']), 'signature': copy.deepcopy(body['signature']),
                     'contract': copy.deepcopy(nexts[index]), 'text': body['text'], 'outputs': {'return': 'return'}}
                    for key, body in bodies.items() if not body['caller'] and body['sourceKind'] == 'whole-graph-csharp'}
        if selected:
            row['mapping']['bodies'] = selected
            callers = f.metadata('informationFunctionInputs', **args, function=row['id'])
            row['mapping']['callers'] = {key: {k: body[k] for k in ['graph', 'node', 'hash']} |
                {'inputs': {arg['name']: before['name'] for arg, before in zip(nexts[index]['args'], olds[index]['args'])}, 'disconnect': {}} for key, body in callers.items()}
    return result

def caller_arguments(index): return {a['name']: copy.deepcopy(graph['nodes'][index]['arguments'][b['name']]) for a, b in zip(nexts[index]['args'], olds[index]['args'])}
def caller_exits(): return copy.deepcopy(graph['exits'])

def verify_rows(rows):
    merged = {row['id']: {'draft': (f.project/row['path']).read_text()} for row in f.metadata('describe', project=str(f.manifest))['units']} | rows
    shared = json.loads(merged[n.caller+'Body/body:common']['draft'])
    expected = copy.deepcopy(graph)
    for index, node in enumerate(expected['nodes']): node.update(signature=nexts[index], arguments=caller_arguments(index))
    assert shared == expected
    assert n.canonical(f.metadata('inspect', text=merged[n.caller+'Body']['draft'])['signature']) == caller_sig
    for index, (fn, sig) in enumerate(zip(functions, nexts)):
        assert n.canonical(f.metadata('inspect', text=merged[fn]['draft'])['signature']) == sig
        assert n.canonical(f.metadata('inspect', text=merged[fn+'Body']['draft'])['signature']) == sig
        leaf = json.loads(merged[fn+'Body/body:common']['draft']); expected = copy.deepcopy(graphs[fn])
        code = next(row for row in expected['nodes'] if row['kind'] == 'code')
        code['arguments'] = {a['name']: {'input': b['name']} for a, b in zip(olds[index]['args'], sig['args'])}
        current = f.metadata('featureBlueprintNodes', featureSource=merged[fn]['draft'], graph=leaf)
        assert current['state'] == 'node-definitions', current
        expected['contractHash'] = current['contractHash']
        assert leaf == expected and code['signature'] == olds[index]
        assert json.loads(merged[fn+'Body/body:common/node:body']['draft'])['source'] == records[fn]['source']

def verify(checkpoint):
    rows = {row['id']: row for row in json.loads(checkpoint.read_text())['changes']}; verify_rows(rows); unchanged()
    group = rows[owner]['atomicEditGroup']; assert set(functions+[fn+'Body/body:common' for fn in functions]+[n.caller+'Body/body:common', owner]) <= set(group)
    return group

def verify_live(): verify_rows({})
def has_mapping_dialog(index): return False

def edit_contract(popover, index):
    for position, arg in enumerate(nexts[index]['args']): popover.locator('[data-signature-kind=inputs] [data-signature-id=arg'+str(position)+'] [data-signature-name]').fill(arg['name'])

def verify_pins(panel, index):
    from playwright.sync_api import expect
    method = panel.locator('[data-inline-method="'+functions[index]+'"]')
    for arg in nexts[index]['args']: expect(method.locator('[data-pin-side=inputs] [data-function-pin-name='+arg['name']+']')).to_have_attribute('data-function-pin-type', '정수')
    expect(method.locator('[data-pin-side=outputs] [data-function-pin-name='+nexts[index]['args'][1]['name']+']')).to_have_count(1 if olds[index]['args'][1].get('mode') == 'ref' else 0)


def after_contract(index):
    if not any(node.get('forwardCallerStorage') for node in graphs[functions[index]]['nodes']): return
    from playwright.sync_api import expect
    selector = '[data-inline-method="'+functions[index]+'"] [data-function-edit], [data-inline-method="'+functions[index]+'"] [data-function-write-direct]'
    held = d.pending()
    f.owner().locator(selector).click()
    dialog = f.page.locator('[role=dialog]:has([data-code-source])'); expect(dialog).to_be_visible()
    assert records[functions[index]]['source'] in dialog.locator('[data-code-source]').input_value()
    dialog.locator('[data-code-cancel]').click(); assert d.pending() == held
    f.owner().locator(selector).click(); expect(dialog).to_be_visible()
    # Accept the existing native parameter names and exact original text.
    dialog.locator('[data-code-save]').click()
    remap = f.page.get_by_role('dialog', name='호출 계약 갱신', exact=True); expect(remap).to_be_visible()
    for select in remap.locator('[data-abi-output=return]').all(): select.select_option('return')
    f.page.screenshot(path=str(f.case/('ref-body-review-'+str(index)+'.png')))
    remap.locator('[data-abi-remap-accept]').click(); expect(remap).to_have_count(0); f.idle()
