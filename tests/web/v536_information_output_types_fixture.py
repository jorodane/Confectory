"""One typed output assignment and its real consumer, isolated local files."""
import copy
import json
import re
import v536_information_out_fixture as x

n, f, d, owner, fn, caller = x.n, x.f, x.d, x.owner, x.fn, x.caller
mode = x.mode
name = 'return' if mode.startswith('return') else 'count'
old = {'args': [{'name': 'amount', 'type': 'long'}, {'name': 'real', 'type': 'double'}, {'name': 'count', 'type': 'long', 'mode': 'out'}], 'return': 'long'}
new = copy.deepcopy(old)
if name == 'return':
    new['return'] = 'double'
else:
    new['args'][2]['type'] = 'double'
remap = {a['name']: a['name'] for a in old['args']}
source = 'function ' + fn + ' (long amount,double real,out long count) -> long {value blueprintPublishedOutputs="[\\"count\\",\\"return\\"]";}'
base = f.metadata('blueprintPrepareFeature', id=fn, text=source, implementation=fn + 'Body', graphPath='function.graph.json', nodePath='function.node.json')
function_file = f.project / ('elements/' + fn.split('::')[1] + '.celem')
function_file.write_text(base['function'].replace('provide ' + fn + ' with ' + fn + 'Body;', ''))
(f.project / (fn.split('::')[1] + 'Body.celem')).write_text(base['implementation'])
defs = f.metadata('featureBlueprintNodes', featureSource=base['function'], graph=base['graph'])
record = {**base['node'], 'definitionHash': next(r['definitionHash'] for r in defs['nodes'] if r['id'] == 'body'), 'source': 'count=amount+1;return amount+2; // C# 원문 9223372036854775806'}
(f.project / 'function.graph.json').write_text(json.dumps(base['graph']))
(f.project / 'function.node.json').write_text(json.dumps(record))
cp = f.metadata('blueprintPrepareFeature', id=caller, text=n.caller_source, implementation=caller + 'Body', graphPath='caller.graph.json', nodePath='unused.node.json')
g = cp['graph']
g.update(profile='sync-acyclic-implicit-out-v1', nodes=[], entry='', edges=[], exits={'return': None})
cp2 = f.metadata('blueprintPrepareCall', id=caller + 'Body', text=cp['implementation'], targetText=function_file.read_text(), graph=g, definition={'id': 'invoke', 'feature': fn, 'intent': '출력 명시 대응', 'control': 'next'})
g = cp2['graph']
g.update(entry='invoke', edges=[{'from': 'invoke', 'port': 'next', 'to': 'exit:return'}], exits={'return': {'node': 'invoke', **({'output': name} if name != 'return' else {})}})
g['nodes'][0]['arguments'] = {'amount': {'input': 'first'}, 'real': {'constant': 1.25}}
(f.project / 'Caller.celem').write_text(cp['function'])
(f.project / 'CallerBody.celem').write_text(re.sub(r'(import [^;]+)(;)', r'\1 in ' + owner + r'\2', cp2['implementation']))
(f.project / 'caller.graph.json').write_text(json.dumps(g))
snapshot = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}


def selections(preview):
    caller_plans = {key: {k: t[k] for k in ['graph', 'node', 'hash']} | {'inputs': {'amount': 'amount', 'real': 'real'}, 'disconnect': {}, 'outputs': {'return': 'count' if name == 'return' else 'return', 'count': 'count' if name == 'return' else 'return'}} for key, t in preview['functionInputs'].items()}
    outputs = {key: {k: t[k] for k in ['graph', 'node', 'name', 'hash', 'before']} | {'type': 'double', 'source': {'input': 'real'}} for key, t in preview['functionOutputs'].items() if t['name'] == name}
    return {'before': old, 'args': remap, 'callers': caller_plans, 'outputs': outputs}


def verify(checkpoint):
    rows = {r['id']: r for r in json.loads(checkpoint.read_text())['changes']}
    producer = json.loads(rows[fn + 'Body/body:common']['draft'])
    consumer = json.loads(rows[caller + 'Body/body:common']['draft'])
    writer = next(r for r in producer['nodes'] if r['kind'] == 'export' and r['output'] == name)
    assert writer['arguments']['value'] == {'input': 'real'} and writer['signature']['args'][0]['type'] == 'double'
    assert next(r for r in producer['nodes'] if r['kind'] == 'code')['signature'] == old
    assert consumer['nodes'][0]['signature'] == new
    assert consumer['nodes'][0]['arguments'] == g['nodes'][0]['arguments']
    assert consumer['exits']['return'] == {'node': 'invoke', **({'output': 'count'} if name == 'return' else {})}
    assert json.loads(rows[fn + 'Body/body:common/node:body']['draft'])['source'] == record['source']
    assert {owner, fn, fn + 'Body', fn + 'Body/body:common', caller + 'Body', caller + 'Body/body:common'} <= set(rows[owner]['atomicEditGroup'])
    fields = f.metadata('blueprintOutputSnapshot', functionText=rows[fn]['draft'])['fields']
    assert next(r for r in fields if r['name'] == name)['type'] == 'double'
    return rows[owner]['atomicEditGroup']
