"""Scoped out producer and actual output consumer, all isolated local sources."""
import json
import re
import v536_information_function_contracts_native as n

f, d, owner, fn, caller = n.f, n.a.d, n.owner, n.fn, n.caller
mode = n.a.mode
original_signature = {'args': [{'name': 'amount', 'type': 'long'}, {'name': 'count', 'type': 'long', 'mode': 'out'}], 'return': 'long'}
signature = {'args': [{'name': 'amount2' if mode == 'both' else 'amount', 'type': 'long'}, {'name': 'count2', 'type': 'long', 'mode': 'out'}], 'return': 'long'}
mapping = {'before': original_signature, 'args': {'amount': signature['args'][0]['name'], 'count': 'count2'}}
function_file = f.project / ('elements/' + fn.split('::')[1] + '.celem')
source = function_file.read_text().replace('provide ' + fn + ' with ' + fn + 'Body;', '').replace('long count', 'out long count')
source = source.replace('{', '{value blueprintPublishedOutputs=' + json.dumps(json.dumps(['count'])) + ';', 1)
base = f.metadata('blueprintPrepareFeature', id=fn, text=source, implementation=fn + 'Body', graphPath='function.graph.json', nodePath='function.node.json')
function_file.write_text(base['function'].replace('provide ' + fn + ' with ' + fn + 'Body;', ''))
n.a.info.write_text(n.a.info.read_text().replace('{', '{provide ' + fn + ' with ' + fn + 'Body;', 1))
(f.project / (fn.split('::')[1] + 'Body.celem')).write_text(base['implementation'])
definitions = f.metadata('featureBlueprintNodes', featureSource=base['function'], graph=base['graph'])
record = {**base['node'], 'definitionHash': next(row['definitionHash'] for row in definitions['nodes'] if row['id'] == 'body'), 'source': 'count=amount+1;return amount+2; // out 원문 그대로'}
(f.project / 'function.graph.json').write_text(json.dumps(base['graph']))
(f.project / 'function.node.json').write_text(json.dumps(record))
cp = f.metadata('blueprintPrepareFeature', id=caller, text=n.caller_source, implementation=caller + 'Body', graphPath='caller.graph.json', nodePath='unused.node.json')
g = cp['graph']
g.update(profile='sync-acyclic-implicit-out-v1', nodes=[], entry='', edges=[], exits={'return': None})
cp2 = f.metadata('blueprintPrepareCall', id=caller + 'Body', text=cp['implementation'], targetText=function_file.read_text(), graph=g, definition={'id': 'invoke', 'feature': fn, 'intent': 'out 실제 사용처', 'control': 'next'})
g = cp2['graph']
g.update(entry='invoke', edges=[{'from': 'invoke', 'port': 'next', 'to': 'exit:return'}], exits={'return': {'node': 'invoke', 'output': 'count'}})
g['nodes'][0]['arguments'] = {'amount': {'input': 'first'}}
(f.project / 'Caller.celem').write_text(cp['function'])
(f.project / 'CallerBody.celem').write_text(re.sub(r'(import [^;]+)(;)', r'\1 in ' + owner + r'\2', cp2['implementation']))
if mode == 'wrapper':
    g['profile'] = 'sync-acyclic-methods-v1'
    after = f.metadata('blueprintCallAfter', functionText=function_file.read_text(), source='return @context.@count; // 기존 공개 출력 읽기')
    g['nodes'][0]['postCall'] = {key: after[key] for key in ['contractHash', 'source', 'helpers']}
(f.project / 'caller.graph.json').write_text(json.dumps(g))
snapshot = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}


def change(method):
    return {'type': 'function-edit', 'id': fn, 'hash': method['hash'], 'name': method['name'], 'description': '출력 이름과 설명 함께', 'signature': signature, 'mapping': mapping}


def assert_graphs(rows):
    producer = json.loads(rows[fn + 'Body/body:common']['draft'])
    consumer = json.loads(rows[caller + 'Body/body:common']['draft'])
    code = next(row for row in producer['nodes'] if row['kind'] == 'code')
    assert code['signature'] == original_signature
    assert code['arguments'] == {'amount': {'input': signature['args'][0]['name']}}
    assert {row['id'] for row in producer['nodes']} == {row['id'] for row in base['graph']['nodes']}
    export = next(row for row in producer['nodes'] if row['kind'] == 'export' and row['output'] == 'count2')
    assert export['arguments']['value'] == {'node': 'body', 'output': 'count'}
    assert consumer['nodes'][0]['signature'] == signature
    assert consumer['nodes'][0]['arguments'] == {signature['args'][0]['name']: {'input': 'first'}}
    assert consumer['exits']['return'] == {'node': 'invoke', 'output': 'count2'}
    assert json.loads(rows[fn + 'Body/body:common/node:body']['draft'])['source'] == record['source']
