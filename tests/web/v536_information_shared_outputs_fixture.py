"""Identity-preserving output names across two owned leaves and one shared caller."""
import copy
import hashlib
import json
import v536_information_shared_callers_fixture as base

f,d,n,owner,mode=base.f,base.d,base.n,base.owner,base.mode
functions=base.functions
old={'args':[{'name':'amount','type':'long'},{'name':'count','type':'long','mode':'out'}],'return':'long'}
nexts=[copy.deepcopy(old),copy.deepcopy(old)]
for signature,name in zip(nexts,['leftCount','rightCount']):signature['args'][1]['name']=name
graphs={};records={}
for index,fn in enumerate(functions):
    prefix='function' if index==0 else 'second'
    source='function '+fn+' (long amount,out long count) -> long {value editorName="'+('첫째' if index==0 else '둘째')+' 공유 출력";value blueprintPublishedOutputs="[\\"count\\"]";}'
    prepared=f.metadata('blueprintPrepareFeature',id=fn,text=source,implementation=fn+'Body',graphPath=prefix+'.graph.json',nodePath=prefix+'.node.json')
    (f.project/('elements/'+fn.split('::')[1]+'.celem')).write_text(prepared['function'])
    (f.project/(fn.split('::')[1]+'Body.celem')).write_text(prepared['implementation'])
    graphs[fn]=prepared['graph']
    defs=f.metadata('featureBlueprintNodes',featureSource=prepared['function'],graph=prepared['graph'])
    records[fn]=prepared['node']|{'definitionHash':next(row['definitionHash'] for row in defs['nodes'] if row['id']=='body'),'source':'count=checked(amount+'+str(index+1)+');return amount; // count 원문 · 9223372036854775806'}
    (f.project/(prefix+'.graph.json')).write_text(json.dumps(prepared['graph']))
    (f.project/(prefix+'.node.json')).write_text(json.dumps(records[fn]))
prepared=f.metadata('blueprintPrepareFeature',id=n.caller,text=n.caller_source,implementation=n.caller+'Body',graphPath='caller.graph.json',nodePath='unused.node.json')
graph=prepared['graph'];graph.update(profile='sync-acyclic-implicit-out-v1',nodes=[],entry='',edges=[],exits={'return':None})
header=prepared['implementation']
for fn,node in zip(functions,['invoke','invoke_second']):
    linked=f.metadata('blueprintPrepareCall',id=n.caller+'Body',text=header,targetText=(f.project/('elements/'+fn.split('::')[1]+'.celem')).read_text(),graph=graph,definition={'id':node,'feature':fn,'intent':'count라는 설명 문자열은 보존 · '+node,'control':'next'})
    header,graph=linked['implementation'],linked['graph']
graph['nodes'][0]['arguments']={'amount':{'input':'first'}}
graph['nodes'][1]['arguments']={'amount':{'node':'invoke','output':'count'}}
graph.update(entry='invoke',edges=[{'from':'invoke','port':'next','to':'invoke_second'},{'from':'invoke_second','port':'next','to':'exit:return'}],exits={'return':{'node':'invoke_second','output':'count'}})
(f.project/'Caller.celem').write_text(prepared['function']);(f.project/'CallerBody.celem').write_text(header);(f.project/'caller.graph.json').write_text(json.dumps(graph))
snapshot={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}

def unchanged():assert all((f.project/path).read_bytes()==raw for path,raw in snapshot.items())
def request():
    result=n.request(nexts[0],{'amount':'amount','count':'leftCount'})
    fn=functions[1];text=result['units'][fn]['draft']
    result['changes'].append({'type':'function-edit','id':fn,'hash':hashlib.sha256(text.encode()).hexdigest(),'name':'둘째 공유 출력','description':'count 설명과 본문 보존','signature':copy.deepcopy(nexts[1]),'mapping':{'before':copy.deepcopy(old),'args':{'amount':'amount','count':'rightCount'}}})
    return result
def verify_rows(rows):
    shared=json.loads(rows[n.caller+'Body/body:common']['draft'])
    assert shared['edges']==graph['edges'] and shared['entry']==graph['entry']
    assert shared['nodes'][0]['arguments']=={'amount':{'input':'first'}}
    assert shared['nodes'][1]['arguments']=={'amount':{'node':'invoke','output':'leftCount'}}
    assert shared['exits']=={'return':{'node':'invoke_second','output':'rightCount'}}
    for index,(fn,signature) in enumerate(zip(functions,nexts)):
        assert n.canonical(f.metadata('inspect',text=rows[fn]['draft'])['signature'])==signature
        assert shared['nodes'][index]['signature']==signature and shared['nodes'][index]['intent']==graph['nodes'][index]['intent']
        leaf=json.loads(rows[fn+'Body/body:common']['draft']);code=next(r for r in leaf['nodes'] if r['kind']=='code')
        assert code['signature']==old and code['arguments']=={'amount':{'input':'amount'}}
        assert {r['id'] for r in leaf['nodes']}=={r['id'] for r in graphs[fn]['nodes']}
        out=next(r for r in leaf['nodes'] if r['kind']=='export' and r['output']==signature['args'][1]['name'])
        assert out['arguments']['value']=={'node':'body','output':'count'}
        assert json.loads(rows[fn+'Body/body:common/node:body']['draft'])['source']==records[fn]['source']
        assert [r['name'] for r in f.metadata('blueprintOutputSnapshot',functionText=rows[fn]['draft'])['fields']]==[signature['args'][1]['name']]
def verify(checkpoint):
    rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']};verify_rows(rows);unchanged()
    group=rows[owner]['atomicEditGroup'];assert set(functions+[fn+'Body/body:common' for fn in functions]+[n.caller+'Body/body:common',owner])<=set(group)
    return group
