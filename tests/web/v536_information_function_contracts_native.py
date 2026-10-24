"""Pure linked information-function closure; only temporary fixture files."""
import copy
import hashlib
import json
import v536_information_function_order_api as a

f, owner, fn = a.f, a.owner, a.functions[0]
checks = []
h = lambda s: hashlib.sha256(s.encode()).hexdigest()


def checked(label):
    checks.append(label)
    print('PASS ' + label, flush=True)


def canonical(sig):
    return {'args': [{'name': a['Name'], 'type': a['Type'], **({'mode': a['Mode']} if a.get('Mode') else {})} for a in sig['Args']], 'return': sig['return']}


def request(signature, remap):
    entries = f.metadata('describe', project=str(f.manifest))['units']
    units = {}
    for row in entries:
        text = (f.project / row['path']).read_text()
        units[row['id']] = {**row, 'draft': text, 'original': text, 'revision': 1, 'baseline': h(text)}
    text = units[fn]['draft']
    before = canonical(f.metadata('inspect', text=text)['signature'])
    change = {'type': 'function-edit', 'id': fn, 'hash': h(text), 'name': '연결 계약', 'description': '원문과 참조 보존', 'signature': signature, 'mapping': {'before': before, 'args': remap}}
    return {'project': str(f.manifest), 'manifest': f.manifest.read_text(), 'id': owner, 'text': a.info.read_text(), 'changes': [change], 'units': units, 'drafts': [{'id': id, 'text': row['draft']} for id, row in units.items() if row['kind'] in ['object', 'schema', 'function', 'implementation', 'module', 'category', 'concept'] and id != owner]}


def prepare(r, ok=True):
    return rpc(r, ok)


def rpc(r, ok):
    import subprocess
    p = subprocess.run([f.env['CONFECTORY_DOTNET'], str(f.repo / 'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')], input=json.dumps({'operation': 'informationDefinitions', **r}), text=True, capture_output=True, check=True, env=f.env)
    v = json.loads(p.stdout)
    assert bool(v['ok']) == ok, v
    return v.get('result')


def initial_tests():
    sig = {'args': [{'name': 'count', 'type': 'long', 'mode': 'ref'}, {'name': 'amount', 'type': 'long'}], 'return': 'long'}
    r = request(sig, {'amount': 'amount', 'count': 'count'})
    p = prepare(r)
    assert [row['id'] for row in p['linkedUpdates']] == [fn + 'Body']
    assert canonical(f.metadata('inspect', text=p['linkedUpdates'][0]['text'])['signature']) == sig
    assert len(p['updates']) == 1 and p['updates'][0]['id'] == fn
    assert all((f.project / path).read_bytes() == text for path, text in f.original.items())
    checked('C# 원문을 재작성하지 않는 정확한 이름/타입/모드 순열은 함수·직접 구현을 한 후보에 담고 원본 파일을 보존한다')
    bad = copy.deepcopy(r)
    bad['changes'][0]['signature']['args'][1]['name'] = 'renamed'
    bad['changes'][0]['mapping']['args']['amount'] = 'renamed'
    prepare(bad, False)
    for patch in [{'before': {'args': [], 'return': 'void'}, 'args': {}}, {'before': r['changes'][0]['mapping']['before'], 'args': {'amount': 'count', 'count': 'count'}}]:
        bad = copy.deepcopy(r)
        bad['changes'][0]['mapping'] = patch
        prepare(bad, False)
    checked('C# 이름 재작성 추측·오래된 원래 서명·중복 pin 대응은 전체 거절한다')
    implementation = f.project / (fn.split('::')[1] + 'Body.celem')
    source = f.project / (fn.split('::')[1] + '.csbody')
    before_implementation, before_source = implementation.read_bytes(), source.read_bytes()
    try:
        implementation.write_text(implementation.read_text().replace('long amount', 'long originalAmount').replace('long count', 'long originalCount'))
        source.write_text('originalCount=checked(originalCount+1);return originalAmount; // 그대로 유지')
        original_body = source.read_bytes()
        p = prepare(request(sig, {'amount': 'amount', 'count': 'count'}))
        own = canonical(f.metadata('inspect', text=p['linkedUpdates'][0]['text'])['signature'])
        assert [a['name'] for a in own['args']] == ['originalCount', 'originalAmount']
        assert source.read_bytes() == original_body
        bad = request(sig, {'amount': 'amount', 'count': 'count'})
        bad['units'][fn + 'Body']['draft'] = bad['units'][fn + 'Body']['draft'].replace('long originalAmount', 'string originalAmount')
        prepare(bad, False)
    finally:
        implementation.write_bytes(before_implementation)
        source.write_bytes(before_source)
    checked('공개 함수와 다른 C# 구현 매개변수 이름·본문을 보존하고 기존 구현 계약 불일치는 거절한다')
    module = f.project / 'ContractRules.celem'
    windows = f.project / 'contract-windows.csbody'
    manifest_before, implementation_before = f.manifest.read_bytes(), implementation.read_bytes()
    try:
        module.write_text('module ' + f.n + 'ContractRules {require ' + fn + ' (long,ref long) -> long;}')
        windows.write_text('count=checked(count+2);return amount; // target 원문')
        f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet', 'element ContractRules module "ContractRules.celem";registry Confectory.Build.DotNet', 1))
        implementation.write_text(implementation.read_text().replace('}', 'body windows "contract-windows.csbody";}'))
        body_before = windows.read_bytes()
        p = prepare(request(sig, {'amount': 'amount', 'count': 'count'}))
        rows = {row['id']: row for row in p['linkedUpdates']}
        assert {fn + 'Body', f.n + 'ContractRules'} == rows.keys()
        assert '(ref long, long) -> long' in rows[f.n + 'ContractRules']['text']
        assert windows.read_bytes() == body_before and 'body windows "contract-windows.csbody";' in rows[fn + 'Body']['text']
    finally:
        f.manifest.write_bytes(manifest_before)
        implementation.write_bytes(implementation_before)
        module.unlink()
        windows.unlink()
    checked('C# 다중 target과 소유 module require는 같은 명시 순열 후보로 갱신하며 모든 target 본문을 보존한다')


if __name__ == '__main__':
    initial_tests()

# The ordinary authored Blueprint keeps code-node parameters stable while its
# root and each call argument are explicitly renamed by the original pin ID.
native = f.project / ('elements/' + fn.split('::')[1] + '.celem')
native.write_text(native.read_text().replace('ref long count', 'long count'))
base = f.metadata('blueprintPrepareFeature', id=fn, text=native.read_text().replace('provide ' + fn + ' with ' + fn + 'Body;', ''), implementation=fn + 'Body', graphPath='function.graph.json', nodePath='function.node.json')
native.write_text(base['function'])
(f.project / (fn.split('::')[1] + 'Body.celem')).write_text(base['implementation'])
defs = f.metadata('featureBlueprintNodes', featureSource=base['function'], graph=base['graph'])
record = {**base['node'], 'definitionHash': next(row['definitionHash'] for row in defs['nodes'] if row['id'] == 'body'), 'source': 'return amount + count; // 그대로 보존'}
(f.project / 'function.graph.json').write_text(json.dumps(base['graph']))
(f.project / 'function.node.json').write_text(json.dumps(record))
caller = f.n + 'Caller'
caller_source = 'function ' + caller + ' (long first,long second) -> long {}'
c = f.metadata('blueprintPrepareFeature', id=caller, text=caller_source, implementation=caller + 'Body', graphPath='caller.graph.json', nodePath='caller.node.json')
g = c['graph']
g.update(nodes=[], entry='', edges=[], exits={'return': None})
c = f.metadata('blueprintPrepareCall', id=caller + 'Body', text=c['implementation'], targetText=base['function'], graph=g, definition={'id': 'invoke', 'feature': fn, 'intent': '실제 연결', 'control': 'next'}) | {'function': c['function']}
g = c['graph']
g.update(entry='invoke', edges=[{'from': 'invoke', 'port': 'next', 'to': 'exit:return'}], exits={'return': {'node': 'invoke'}})
g['nodes'][0]['arguments'] = {'amount': {'input': 'first'}, 'count': {'input': 'second'}}
for local, kind, text in [('Caller', 'function', c['function']), ('CallerBody', 'implementation', c['implementation'])]:
    (f.project / (local + '.celem')).write_text(text)
    f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet', 'element ' + local + ' ' + kind + ' "' + local + '.celem";registry Confectory.Build.DotNet', 1))
(f.project / 'caller.graph.json').write_text(json.dumps(g))
snapshot = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file()}


def add_targets_and_wrapper():
    implementation = f.project / (fn.split('::')[1] + 'Body.celem')
    implementation.write_text(implementation.read_text().replace('}', 'blueprint windows "function-windows.graph.json";}'))
    graph = copy.deepcopy(base['graph'])
    graph['nodes'][0]['implementation'] = 'function-windows.node.json'
    definitions = f.metadata('featureBlueprintNodes', featureSource=base['function'], graph=graph)
    code = {**record, 'definitionHash': next(row['definitionHash'] for row in definitions['nodes'] if row['id'] == 'body')}
    (f.project / 'function-windows.graph.json').write_text(json.dumps(graph))
    (f.project / 'function-windows.node.json').write_text(json.dumps(code))
    caller_graph = json.loads((f.project / 'caller.graph.json').read_text())
    caller_graph['profile'] = 'sync-acyclic-methods-v1'
    after = f.metadata('blueprintCallAfter', functionText=base['function'])
    caller_graph['nodes'][0]['postCall'] = {k: after[k] for k in ['contractHash', 'source', 'helpers']}
    (f.project / 'caller.graph.json').write_text(json.dumps(caller_graph))
def graph_tests():
    sig = {'args': [{'name': 'count', 'type': 'long'}, {'name': 'renamed', 'type': 'long'}], 'return': 'long'}
    r = request(sig, {'amount': 'renamed', 'count': 'count'})
    p = prepare(r)
    by_id = {row['id']: row for row in p['linkedUpdates']}
    assert {fn + 'Body', fn + 'Body/body:common', caller + 'Body/body:common'} <= by_id.keys(), sorted(by_id)
    # Both import argument types remain long; import syntax stores no pin names.
    # Keeping its exact source is required, while call-node names are updated below.
    assert caller + 'Body' not in by_id
    assert '(long, long) -> long;' in r['units'][caller + 'Body']['draft']
    root = json.loads(by_id[fn + 'Body/body:common']['text'])
    assert root['nodes'][0]['arguments']['amount'] == {'input': 'renamed'}
    assert root['nodes'][0]['signature'] == base['graph']['nodes'][0]['signature']
    call = json.loads(by_id[caller + 'Body/body:common']['text'])['nodes'][0]
    assert call['arguments'] == {'renamed': {'input': 'first'}, 'count': {'input': 'second'}} and call['signature'] == sig
    for row in p['linkedUpdates']:
        if row['kind'] == 'blueprint-node':
            assert json.loads(row['text'])['source'] == record['source']
    assert all((f.project / path).read_bytes() == text for path, text in snapshot.items())
    checked('명시적 pin ID 대응은 루트·typed import·실제 호출 입력을 함께 갱신하며 code 노드 서명/본문과 물리 원본은 보존한다')
    bad = copy.deepcopy(r)
    bad['changes'][0]['signature']['args'][1]['type'] = 'string'
    prepare(bad, False)
    bad = copy.deepcopy(r)
    del bad['units'][caller + 'Body/body:common']
    prepare(bad, False)
    checked('연결된 타입 불일치·호출자 snapshot 누락은 부분 후보 없이 거절한다')
    add_targets_and_wrapper()
    before_targets = {p: (f.project / p).read_bytes() for p in ['function.node.json', 'function-windows.node.json', 'caller.graph.json']}
    sig = {'args': [{'name': 'count', 'type': 'long'}, {'name': 'amount', 'type': 'long'}], 'return': 'long'}
    p = prepare(request(sig, {'amount': 'amount', 'count': 'count'}))
    rows = {row['id']: row for row in p['linkedUpdates']}
    assert {fn + 'Body/body:common', fn + 'Body/body:windows', caller + 'Body/body:common'} <= rows.keys()
    after_call = json.loads(rows[caller + 'Body/body:common']['text'])['nodes'][0]
    assert after_call['postCall']['source'] == json.loads(before_targets['caller.graph.json'])['nodes'][0]['postCall']['source']
    assert after_call['signature'] == sig and after_call['arguments'] == {'count': {'input': 'second'}, 'amount': {'input': 'first'}}
    assert all((f.project / path).read_bytes() == data for path, data in before_targets.items())
    checked('Blueprint 모든 target과 안전한 같은 이름 집합의 C# 후처리는 명시 순서 후보를 공유하고 원문을 재작성하지 않는다')
    print(json.dumps({'checks': checks, 'evidence': str(f.case), 'pure': True, 'engineIntegrated': False, 'windowsNative': False}, ensure_ascii=False))

if __name__ == '__main__':
    graph_tests()
