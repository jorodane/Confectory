"""Owned whole-body/native aliases plus an ordinary caller, temporary fixtures."""
import copy
import json
import re
import v536_information_function_contracts_native as n

f, d, owner, fn, caller, mode = n.f, n.a.d, n.owner, n.fn, n.caller, n.a.mode
old = {'args': [{'name': 'amount', 'type': 'long'}, {'name': 'count', 'type': 'long', 'mode': 'out'}], 'return': 'long'}
new = copy.deepcopy(old)
new['args'][0]['mode'] = 'ref'
native = {'args': [{'name': 'nativeAmount', 'type': 'long'}, {'name': 'nativeTotal', 'type': 'long', 'mode': 'out'}], 'return': 'long'}
selected = copy.deepcopy(native)
selected['args'][0]['mode'] = 'ref'
remap = {'amount': 'amount', 'count': 'count'}
original = 'nativeTotal=checked(nativeAmount+1);return nativeTotal; // 원래 별칭 · 9223372036854775806\r\n'
edited = 'nativeAmount=checked(nativeAmount+2);nativeTotal=nativeAmount;return nativeTotal; // 명시 본문 😀\r\n'
function_path = 'elements/' + fn.split('::')[1] + '.celem'
function_file = f.project / function_path
function_file.write_text(function_file.read_text().replace('(long amount, long count)', '(long amount, out long count)').replace('(long amount,long count)', '(long amount,out long count)'))
implementation_path = fn.split('::')[1] + 'Body.celem'
implementation_file = f.project / implementation_path
cpp = 'implementation ' + fn + 'Body for ' + fn + ' (long nativeAmount,out long nativeTotal) -> long {body common "whole-original.csbody";}'
implementation_file.write_text(cpp)
(f.project / 'whole-original.csbody').write_bytes(original.encode())
converted = f.metadata('blueprintConversion', project=str(f.manifest), id=fn+'Body', text=cpp, target='common', graphPath='function.graph.json', nodePath='function.node.json')
implementation_file.write_text(converted['implementation'])
(f.project / 'function.graph.json').write_text(json.dumps(converted['graph']))
(f.project / 'function.node.json').write_text(json.dumps(converted['node']))
# An owned information function is provided by that information, not globally.
function_file.write_text(function_file.read_text().replace('provide '+fn+' with '+fn+'Body;', ''))
info = f.project / 'FreeInfo.celem'
info.write_text(info.read_text().replace('{', '{provide '+fn+' with '+fn+'Body;', 1))
consumer_file = f.project / 'CallerBody.celem'
consumer_file.write_text(re.sub(r'(import [^;]+ -> long)(;)', lambda m:m[1].replace('(long, long)', '(long, out long)').replace('long count','out long count')+' in '+owner+m[2],consumer_file.read_text()))
graph = json.loads((f.project / 'caller.graph.json').read_text())
graph['profile'] = 'sync-acyclic-implicit-out-v1'
graph['nodes'][0]['signature'] = old
graph['nodes'][0]['arguments'] = {'amount': {'input': 'first'}}
(f.project / 'caller.graph.json').write_text(json.dumps(graph))
body_id = fn+'Body/body:common/node:body'
body_path = 'function.node.json'
snapshot = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}


def selections(preview):
    row = preview['functionBodies'][body_id]
    assert row['sourceKind'] == 'whole-csharp' and row['signature'] == native
    body = {k:row[k] for k in ['hash','path']} | {'beforeSignature':native,'signature':selected,'contract':new,'text':edited}
    callers = {key:{k:row[k] for k in ['graph','node','hash']} | {'inputs':{'amount':'amount'},'disconnect':{}} for key,row in preview['functionInputs'].items()}
    return {'before':old,'args':remap,'bodies':{body_id:body},'callers':callers}


def request():
    r = n.request(new,remap)
    preview = {key:f.metadata(op,id=owner,function=fn,includeBlueprintTargets=True,units=r['units']) for key,op in [('functionInputs','informationFunctionInputs'),('functionBodies','informationFunctionBodies')]}
    r['changes'][0]['mapping'] = selections(preview)
    return r


def verify(checkpoint):
    rows = {r['id']:r for r in json.loads(checkpoint.read_text())['changes']}
    record=json.loads(rows[body_id]['draft']);assert record['source']==edited
    assert n.canonical(f.metadata('inspect',text=rows[fn+'Body']['draft'])['signature'])==selected
    g=json.loads(rows[fn+'Body/body:common']['draft']);node=next(r for r in g['nodes'] if r['id']=='body')
    assert node['signature']==selected and node['implementationContext']['signature']==selected
    assert node['arguments']=={'nativeAmount':{'input':'amount'}}
    consumer=json.loads(rows[caller+'Body/body:common']['draft'])
    assert consumer['nodes'][0]['signature']==new and consumer['nodes'][0]['arguments']==graph['nodes'][0]['arguments']
    assert consumer['exits']==graph['exits']
    ids=rows[owner]['atomicEditGroup']
    assert {owner,fn,fn+'Body',fn+'Body/body:common',body_id,caller+'Body',caller+'Body/body:common'}<=set(ids)
    assert all((f.project/path).read_bytes()==b for path,b in snapshot.items())
    return ids
