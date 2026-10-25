"""Two existing owned contracts and one real shared Blueprint caller."""
import copy
import hashlib
import json
import v536_information_function_contracts_native as n

f, d, owner, mode = n.f, n.a.d, n.owner, n.a.mode
functions = [n.fn, n.a.functions[1]]
old = {'args': [{'name': 'amount', 'type': 'long'}, {'name': 'count', 'type': 'long'}], 'return': 'long'}
nexts = [copy.deepcopy(old), copy.deepcopy(old)]
nexts[0]['args'][0]['name'] = 'leftAmount'
nexts[1]['args'][0]['name'] = 'rightAmount'
second = functions[1]
source = 'function ' + second + ' (long amount,long count) -> long {value editorName="둘째 공유 함수";}'
prepared = f.metadata('blueprintPrepareFeature', id=second, text=source, implementation=second+'Body',
                      graphPath='second.graph.json', nodePath='second.node.json')
(f.project / ('elements/' + second.split('::')[1] + '.celem')).write_text(prepared['function'])
(f.project / (second.split('::')[1] + 'Body.celem')).write_text(prepared['implementation'])
(f.project / 'second.graph.json').write_text(json.dumps(prepared['graph']))
definitions = f.metadata('featureBlueprintNodes', featureSource=prepared['function'], graph=prepared['graph'])
(f.project / 'second.node.json').write_text(json.dumps(prepared['node'] | {
    'definitionHash':next(row['definitionHash'] for row in definitions['nodes'] if row['id']=='body'),
    'source':'return amount-count; // 둘째 원문 · 9223372036854775806'}))
caller_path = f.project / 'CallerBody.celem'
graph = json.loads((f.project / 'caller.graph.json').read_text())
linked = f.metadata('blueprintPrepareCall', id=n.caller+'Body', text=caller_path.read_text(),
                    targetText=prepared['function'], graph=graph,
                    definition={'id':'invoke_second','feature':second,'intent':'같은 호출자의 두 번째 계약','control':'next'})
caller_path.write_text(linked['implementation'])
graph = linked['graph']
graph['nodes'][-1]['arguments'] = {'amount': {'node':'invoke'}, 'count': {'input':'second'}}
graph['edges'] = [{'from':'invoke','port':'next','to':'invoke_second'},
                  {'from':'invoke_second','port':'next','to':'exit:return'}]
graph['exits'] = {'return': {'node':'invoke_second'}}
(f.project / 'caller.graph.json').write_text(json.dumps(graph))
snapshot = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*')
            if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}

def unchanged():
    assert all((f.project/path).read_bytes()==raw for path,raw in snapshot.items())

def request():
    result = n.request(nexts[0], {'amount':'leftAmount','count':'count'})
    text = result['units'][second]['draft']
    result['changes'].append({'type':'function-edit','id':second,
        'hash':hashlib.sha256(text.encode()).hexdigest(),'name':'둘째 공유 함수','description':'원문 보존',
        'signature':copy.deepcopy(nexts[1]),'mapping':{'before':copy.deepcopy(old),
            'args':{'amount':'rightAmount','count':'count'}}})
    return result

def verify_rows(rows):
    for fn,next_sig in zip(functions,nexts):
        assert n.canonical(f.metadata('inspect',text=rows[fn]['draft'])['signature'])==next_sig
    caller=json.loads(rows[n.caller+'Body/body:common']['draft'])
    calls={row['id']:row for row in caller['nodes']}
    assert calls['invoke']['arguments']=={'leftAmount':{'input':'first'},'count':{'input':'second'}}
    assert calls['invoke_second']['arguments']=={'rightAmount':{'node':'invoke'},'count':{'input':'second'}}
    assert calls['invoke']['signature']==nexts[0] and calls['invoke_second']['signature']==nexts[1]
    assert caller['edges']==graph['edges'] and caller['exits']==graph['exits']
    for path,id in [('function.node.json',functions[0]+'Body/body:common/node:body'),
                    ('second.node.json',functions[1]+'Body/body:common/node:body')]:
        if id in rows:assert json.loads(rows[id]['draft'])['source']==json.loads(snapshot[path])['source']

def verify(checkpoint):
    rows={row['id']:row for row in json.loads(checkpoint.read_text())['changes']}
    verify_rows(rows)
    group=rows[owner]['atomicEditGroup']
    assert set(functions+[fn+'Body/body:common' for fn in functions]+[n.caller+'Body/body:common',owner])<=set(group)
    unchanged()
    return group
