"""Explicit producer output remapping crosses a second selected call's input."""
import copy,hashlib,json
import v536_information_shared_outputs_fixture as base
f,d,n,owner,mode=base.f,base.d,base.n,base.owner,base.mode
functions=base.functions
old={'args':[{'name':'amount','type':'long'},{'name':'real','type':'double'},{'name':'count','type':'long','mode':'out'}],'return':'long'}
nexts=[copy.deepcopy(old),copy.deepcopy(old)]
for signature in nexts:signature['args'][2]['type']='double'
graphs={};records={}
for index,fn in enumerate(functions):
    prefix='function' if index==0 else 'second'
    source='function '+fn+' (long amount,double real,out long count) -> long {value editorName="'+('첫째' if index==0 else '둘째')+' 공유 출력";value blueprintPublishedOutputs="[\\"count\\"]";}'
    prepared=f.metadata('blueprintPrepareFeature',id=fn,text=source,implementation=fn+'Body',graphPath=prefix+'.graph.json',nodePath=prefix+'.node.json')
    (f.project/('elements/'+fn.split('::')[1]+'.celem')).write_text(prepared['function']);(f.project/(fn.split('::')[1]+'Body.celem')).write_text(prepared['implementation'])
    graphs[fn]=prepared['graph'];defs=f.metadata('featureBlueprintNodes',featureSource=prepared['function'],graph=prepared['graph'])
    records[fn]=prepared['node']|{'definitionHash':next(r['definitionHash'] for r in defs['nodes'] if r['id']=='body'),'source':'count=checked(amount+'+str(index+1)+');return amount; // real/count 원문 · 9223372036854775806'}
    (f.project/(prefix+'.graph.json')).write_text(json.dumps(prepared['graph']));(f.project/(prefix+'.node.json')).write_text(json.dumps(records[fn]))
prepared=f.metadata('blueprintPrepareFeature',id=n.caller,text=n.caller_source,implementation=n.caller+'Body',graphPath='caller.graph.json',nodePath='unused.node.json')
graph=prepared['graph'];graph.update(profile='sync-acyclic-implicit-out-v1',nodes=[],entry='',edges=[],exits={'return':None});header=prepared['implementation']
for fn,node in zip(functions,['invoke','invoke_second']):
    result=f.metadata('blueprintPrepareCall',id=n.caller+'Body',text=header,targetText=(f.project/('elements/'+fn.split('::')[1]+'.celem')).read_text(),graph=graph,definition={'id':node,'feature':fn,'intent':'count/return 문자열 보존 · '+node,'control':'next'});header,graph=result['implementation'],result['graph']
graph['nodes'][0]['arguments']={'amount':{'input':'first'},'real':{'constant':1.25}}
graph['nodes'][1]['arguments']={'amount':{'node':'invoke','output':'count'},'real':{'constant':2.5}}
graph.update(entry='invoke',edges=[{'from':'invoke','port':'next','to':'invoke_second'},{'from':'invoke_second','port':'next','to':'exit:return'}],exits={'return':{'node':'invoke_second','output':'count'}})
(f.project/'Caller.celem').write_text(prepared['function']);(f.project/'CallerBody.celem').write_text(header);(f.project/'caller.graph.json').write_text(json.dumps(graph))
snapshot={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}
def unchanged():assert all((f.project/path).read_bytes()==raw for path,raw in snapshot.items())
def selections(preview):
    callers={key:{k:row[k] for k in ['graph','node','hash']}|{'inputs':{'amount':'amount','real':'real'},'disconnect':{},'outputs':{'count':'return','return':'return'}} for key,row in preview['functionInputs'].items()}
    outputs={key:{k:row[k] for k in ['graph','node','name','hash','before']}|{'type':'double','source':{'input':'real'}} for key,row in preview['functionOutputs'].items() if row['name']=='count'}
    return {'before':copy.deepcopy(old),'args':{a['name']:a['name'] for a in old['args']},'callers':callers,'outputs':outputs}
def request():
    result=n.request(nexts[0],{'amount':'amount','real':'real','count':'count'});text=result['units'][functions[1]]['draft']
    result['changes'].append({'type':'function-edit','id':functions[1],'hash':hashlib.sha256(text.encode()).hexdigest(),'name':'둘째 공유 출력','description':'선택한 대응과 본문 보존','signature':copy.deepcopy(nexts[1])})
    for row in result['changes']:
        args={k:result[k] for k in ['project','manifest','id','units']}
        inputs=f.metadata('informationFunctionInputs',**args,function=row['id']);outputs=f.metadata('informationFunctionOutputs',**args,function=row['id'])
        row['mapping']=selections({'functionInputs':inputs,'functionOutputs':outputs})
    return result
def verify_rows(rows):
    caller=json.loads(rows[n.caller+'Body/body:common']['draft']);assert caller['edges']==graph['edges'] and caller['entry']==graph['entry']
    assert caller['nodes'][0]['arguments']==graph['nodes'][0]['arguments']
    assert caller['nodes'][1]['arguments']=={'amount':{'node':'invoke'},'real':{'constant':2.5}}
    assert caller['exits']=={'return':{'node':'invoke_second'}}
    for index,(fn,sig) in enumerate(zip(functions,nexts)):
        assert n.canonical(f.metadata('inspect',text=rows[fn]['draft'])['signature'])==sig
        assert caller['nodes'][index]['signature']==sig and caller['nodes'][index]['intent']==graph['nodes'][index]['intent']
        leaf=json.loads(rows[fn+'Body/body:common']['draft']);assert leaf['edges']==graphs[fn]['edges']
        code=next(r for r in leaf['nodes'] if r['kind']=='code');assert code['signature']==old and code['arguments']=={'amount':{'input':'amount'},'real':{'input':'real'}}
        writer=next(r for r in leaf['nodes'] if r['kind']=='export' and r['output']=='count');assert writer['arguments']=={'value':{'input':'real'}} and writer['signature']['args'][0]['type']=='double'
        assert {r['id'] for r in leaf['nodes']}=={r['id'] for r in graphs[fn]['nodes']}
        assert json.loads(rows[fn+'Body/body:common/node:body']['draft'])['source']==records[fn]['source']
        assert f.metadata('blueprintOutputSnapshot',functionText=rows[fn]['draft'])['fields'][0]['type']=='double'
def verify(checkpoint):
    rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']};verify_rows(rows);unchanged();group=rows[owner]['atomicEditGroup']
    assert set(functions+[fn+'Body/body:common' for fn in functions]+[n.caller+'Body',n.caller+'Body/body:common',owner])<=set(group)
    return group
