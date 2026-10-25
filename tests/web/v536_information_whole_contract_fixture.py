"""Explicit whole-body shape changes, isolated owned fixture and ordinary caller."""
import copy
import json
import sys
import v536_information_whole_body_fixture as base
f,d,n,owner,fn,caller,mode=base.f,base.d,base.n,base.owner,base.fn,base.caller,base.mode
old=copy.deepcopy(base.old);before_native=copy.deepcopy(base.native);remap={'amount':None,'count':'total'}
chain='chain' in sys.argv[4:]
scenario=next((s for s in ['out-value','value-out','out-ref','ref-out','void','add-return'] if s in sys.argv[4:]),'types')
new={'args':[{'name':'text','type':'string'},{'name':'total','type':'long','mode':'out'},{'name':'increment','type':'long'}],'return':'bool'}
selected={'args':[{'name':'message','type':'string'},{'name':'nativeTotal','type':'long','mode':'out'},{'name':'delta','type':'long'}],'return':'bool'}
edited='nativeTotal=checked(message.Length+delta);return nativeTotal>0; // 직접 편집 😀\r\n'
inputs={'text':{'valueJson':'"명시한 문자열"'},'increment':'amount'};outputs={'return':'total','count':'total'}
if scenario!='types':
    remap=copy.deepcopy(base.remap);new=copy.deepcopy(old);selected=copy.deepcopy(before_native);inputs={'amount':'amount'};outputs={'return':'return','count':'count'}
if scenario=='out-value':
    new['args'][1].pop('mode');selected['args'][1].pop('mode');edited='return checked(nativeAmount+nativeTotal); // out→값, 원문 보존\r\n';inputs['count']={'valueJson':'9223372036854775805'};outputs['count']='return'
elif scenario=='value-out':
    new['args'][0]['mode']='out';selected['args'][0]['mode']='out';edited='nativeAmount=9223372036854775805;nativeTotal=checked(nativeAmount+1);return nativeTotal; // 값→out\r\n';inputs={}
elif scenario=='out-ref':
    new['args'][1]['mode']='ref';selected['args'][1]['mode']='ref';edited='nativeTotal=checked(nativeTotal+nativeAmount);return nativeTotal; // out→ref, 명시 저장소\r\n';inputs={'amount':{'valueJson':'5'},'count':'amount'};outputs['count']='return'
elif scenario=='ref-out':
    old['args'][1]['mode']='ref';before_native['args'][1]['mode']='ref'
    base.function_file.write_text(base.function_file.read_text().replace('out long count','ref long count'))
    original='nativeTotal=checked(nativeTotal+nativeAmount);return nativeTotal; // 원래 ref 본문\r\n'
    cpp='implementation '+fn+'Body for '+fn+' (long nativeAmount,ref long nativeTotal) -> long {body common "whole-original.csbody";}'
    base.implementation_file.write_text(cpp);(f.project/'whole-original.csbody').write_bytes(original.encode())
    converted=f.metadata('blueprintConversion',project=str(f.manifest),id=fn+'Body',text=cpp,target='common',graphPath='function.graph.json',nodePath='function.node.json')
    base.implementation_file.write_text(converted['implementation']);(f.project/'function.graph.json').write_text(json.dumps(converted['graph']));(f.project/'function.node.json').write_text(json.dumps(converted['node']))
    base.consumer_file.write_text(base.consumer_file.read_text().replace('out long','ref long'))
    g=json.loads((f.project/'caller.graph.json').read_text());g['nodes'][0]['signature']=old;g['nodes'][0]['arguments']['count']={'input':'second'};g['profile']='sync-acyclic-ref-v1';(f.project/'caller.graph.json').write_text(json.dumps(g))
    edited='nativeTotal=checked(nativeAmount+1);return nativeTotal; // ref→out, 이전 저장소 명시 해제\r\n';outputs={'return':'return'}
elif scenario=='void':
    new['return']='void';selected['return']='void';edited='nativeTotal=checked(nativeAmount+1);return; // 명시 void\r\n';outputs['return']='count'
elif scenario=='add-return':
    old['return']='void';before_native['return']='void'
    base.function_file.write_text(base.function_file.read_text().replace('-> long','-> void'))
    original='nativeTotal=nativeAmount;return; // 원래 void 본문\r\n'
    cpp='implementation '+fn+'Body for '+fn+' (long nativeAmount,out long nativeTotal) -> void {body common "whole-original.csbody";}'
    (f.project/'whole-original.csbody').write_bytes(original.encode())
    base.implementation_file.write_text(cpp)
    converted=f.metadata('blueprintConversion',project=str(f.manifest),id=fn+'Body',text=cpp,target='common',graphPath='function.graph.json',nodePath='function.node.json')
    base.implementation_file.write_text(converted['implementation'])
    (f.project/'function.graph.json').write_text(json.dumps(converted['graph']))
    (f.project/'function.node.json').write_text(json.dumps(converted['node']))
    base.consumer_file.write_text(base.consumer_file.read_text().replace('-> long in '+owner,'-> void in '+owner))
    g=json.loads((f.project/'caller.graph.json').read_text());g['nodes'][0]['signature']=old;g['exits']['return']={'node':'invoke','output':'count'};(f.project/'caller.graph.json').write_text(json.dumps(g))
    edited='nativeTotal=checked(nativeAmount+1);return checked(nativeTotal+1); // void→반환\r\n';outputs={'count':'count'}
if chain:
    assert scenario=='value-out'
    new['return']='bool';selected['return']='bool';edited='nativeAmount=1;nativeTotal=2;return true; // 두 호출의 명시 계약'
    outputs={'return':'count','count':'count'}
    p=f.project/'caller.graph.json';g=json.loads(p.read_text());second=copy.deepcopy(g['nodes'][0]);second['id']='invoke2';second['arguments']['amount']={'node':'invoke'};g['nodes'].append(second);g['edges']=[{'from':'invoke','port':'next','to':'invoke2'},{'from':'invoke2','port':'next','to':'exit:return'}];g['exits']['return']={'node':'invoke2'};p.write_text(json.dumps(g))
if scenario=='types':
    g=json.loads((f.project/'function.graph.json').read_text());g['outputOrder']=['count','return'];(f.project/'function.graph.json').write_text(json.dumps(g))
body_id,body_path=base.body_id,base.body_path
snapshot={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}
original_graph=json.loads((f.project/'function.graph.json').read_text());original_record=json.loads((f.project/body_path).read_text())
caller_graph=json.loads((f.project/'caller.graph.json').read_text())

def selections(preview):
    row=preview['functionBodies'][body_id]
    flow=copy.deepcopy(row['whole']);flow['returnNode']=None if new['return']=='void' else flow['returnNode'] or 'explicit_return'
    body={k:row[k] for k in ['hash','path']}|{'beforeSignature':before_native,'signature':selected,'contract':new,'text':edited,'whole':flow}
    callers={key:{k:r[k] for k in ['graph','node','hash']}|{'inputs':copy.deepcopy(inputs),'outputs':copy.deepcopy(outputs),'disconnect':{name:r['bindings'][name] for name in (['amount'] if scenario=='value-out' else ['count'] if scenario=='ref-out' else [])}} for key,r in preview['functionInputs'].items()}
    return {'before':old,'args':copy.deepcopy(remap),'bodies':{body_id:body},'callers':callers}

def request():
    r=n.request(new,remap)
    p={key:f.metadata(op,id=owner,function=fn,includeBlueprintTargets=True,units=r['units']) for key,op in [('functionInputs','informationFunctionInputs'),('functionBodies','informationFunctionBodies')]}
    r['changes'][0]['mapping']=selections(p);return r

def verify(checkpoint):
    rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']}
    assert json.loads(rows[body_id]['draft'])['source']==edited
    assert n.canonical(f.metadata('inspect',text=rows[fn+'Body']['draft'])['signature'])==selected
    graph=json.loads(rows[fn+'Body/body:common']['draft']);node=next(r for r in graph['nodes'] if r['id']=='body')
    assert node['signature']==selected and node['implementationContext']['signature']==selected
    assert node['arguments']=={a['name']:{'input':new['args'][i]['name']} for i,a in enumerate(selected['args']) if a.get('mode')!='out'}
    writers=[r for r in graph['nodes'] if r['kind']=='export'];assert len(writers)==(0 if new['return']=='void' else 1)
    if writers:assert writers[0]['signature']['args'][0]['type']==new['return'] and writers[0]['arguments']=={'value':{'node':'body'}}
    consumer=json.loads(rows[caller+'Body/body:common']['draft']);call=consumer['nodes'][0];assert call['signature']==new
    expected={name:copy.deepcopy(caller_graph['nodes'][0]['arguments'][v]) if isinstance(v,str) else {'constant':json.loads(v['valueJson'])} for name,v in inputs.items()};assert call['arguments']==expected
    old_output=caller_graph['exits']['return'].get('output','return');to=outputs[old_output];assert consumer['exits']['return']==({'node':caller_graph['exits']['return']['node']} if to=='return' else {'node':caller_graph['exits']['return']['node'],'output':to})
    if chain:assert len(consumer['nodes'])==2 and all(row['signature']==new and not row['arguments'] for row in consumer['nodes'])
    ids=rows[owner]['atomicEditGroup'];assert {owner,fn,fn+'Body',fn+'Body/body:common',body_id,caller+'Body',caller+'Body/body:common'}<=set(ids)
    assert all((f.project/p).read_bytes()==v for p,v in snapshot.items())
    return ids
