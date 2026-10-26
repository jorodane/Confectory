"""Existing whole C# out -> ref, explicit existing storage and one shared caller."""
import copy
import hashlib
import json
import v536_information_shared_ref_names_fixture as base

f,d,n,owner,mode=base.f,base.d,base.n,base.owner,base.mode
functions=base.functions
olds=copy.deepcopy(base.olds)
for sig in olds:sig['args'][1]['mode']='out'
nexts=copy.deepcopy(olds)
for sig in nexts:sig['args'][1]['mode']='ref'
old=olds[0];new=nexts[0];removed=[];added=[];retry_field='arg0';undo_steps=2
native={'args':[{'name':'nativeAmount','type':'long'},{'name':'nativeTotal','type':'long','mode':'out'}],'return':'long'}
selected=copy.deepcopy(native);selected['args'][1]['mode']='ref'
graphs={};records={}
source='nativeTotal=checked(nativeAmount+1);return nativeTotal; // 원문 · 9223372036854775806 😀\n'
for index,fn in enumerate(functions):
    prefix='function' if index==0 else 'second'
    declaration=f.project/('elements/'+fn.split('::')[1]+'.celem')
    declaration.write_text(declaration.read_text().replace('ref long count','out long count'))
    cpp='implementation '+fn+'Body for '+fn+' (long nativeAmount,out long nativeTotal) -> long {body common "'+prefix+'-original.csbody";}'
    (f.project/(fn.split('::')[1]+'Body.celem')).write_text(cpp)
    (f.project/(prefix+'-original.csbody')).write_text(source)
    prepared=f.metadata('blueprintConversion',project=str(f.manifest),id=fn+'Body',text=cpp,target='common',graphPath=prefix+'.graph.json',nodePath=prefix+'.node.json')
    (f.project/(fn.split('::')[1]+'Body.celem')).write_text(prepared['implementation'])
    graphs[fn]=copy.deepcopy(prepared['graph']);records[fn]=copy.deepcopy(prepared['node'])
    assert records[fn]['source']==source
    (f.project/(prefix+'.graph.json')).write_text(json.dumps(graphs[fn]));(f.project/(prefix+'.node.json')).write_text(json.dumps(records[fn]))
graph=copy.deepcopy(base.graph)
for index,node in enumerate(graph['nodes']):
    node['signature']=copy.deepcopy(olds[index]);node['arguments'].pop('count')
graph['nodes'][1]['arguments']['amount']={'node':'invoke','output':'count'}
graph['exits']['return']={'node':'invoke_second','output':'count'}
header=(f.project/'CallerBody.celem').read_text()
(f.project/'CallerBody.celem').write_text('\n'.join(line.replace('ref long','out long') if line.startswith('import ') else line for line in header.split('\n')))
(f.project/'caller.graph.json').write_text(json.dumps(graph))
snapshot={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}

def unchanged():assert all((f.project/path).read_bytes()==raw for path,raw in snapshot.items())
def request():
    r=n.request(nexts[0],{'amount':'amount','count':'count'});fn=functions[1]
    r['changes'].append({'type':'function-edit','id':fn,'hash':hashlib.sha256(r['units'][fn]['draft'].encode()).hexdigest(),'name':'둘째 공유 참조','description':'원문/원래 저장소와 명시 해제','signature':copy.deepcopy(nexts[1]),'mapping':{'before':copy.deepcopy(olds[1]),'args':{'amount':'amount','count':'count'}}})
    for index,row in enumerate(r['changes']):
        args={k:r[k] for k in ['project','manifest','id','units']}
        bodies=f.metadata('informationFunctionBodies',**args,function=row['id'],includeBlueprintTargets=True)
        rows={key:body for key,body in bodies.items() if not body['caller']}
        assert len(rows)==1 and all(body['sourceKind']=='whole-csharp' for body in rows.values()),rows
        row['mapping']['bodies']={key:{k:body[k] for k in ['hash','path','whole']}|{'beforeSignature':copy.deepcopy(native),'signature':copy.deepcopy(selected),'contract':copy.deepcopy(nexts[index]),'text':body['text']} for key,body in rows.items()}
        callers=f.metadata('informationFunctionInputs',**args,function=row['id'])
        row['mapping']['callers']={key:{k:body[k] for k in ['graph','node','hash']}|{'inputs':{'amount':{'valueJson':'5'},'count':'amount'},'disconnect':{},'outputs':{'return':'return','count':'return'}} for key,body in callers.items()}
    return r

def caller_arguments(index):return {'amount':{'constant':5},'count':{'input':'first'} if index==0 else {'node':'invoke'}}
def caller_exits():return {'return':{'node':'invoke_second'}}
def verify_caller_header(text):
    expected=snapshot['CallerBody.celem'].decode()
    for fn in functions:expected='\n'.join(line.replace('out long','ref long') if fn+' ' in line else line for line in expected.split('\n'))
    assert text==expected

def verify_rows(rows):
    merged={row['id']:{'draft':(f.project/row['path']).read_text()} for row in f.metadata('describe',project=str(f.manifest))['units']}|rows
    actual=json.loads(merged[n.caller+'Body/body:common']['draft']);expected=copy.deepcopy(graph)
    for index,node in enumerate(expected['nodes']):node.update(signature=nexts[index],arguments=caller_arguments(index))
    expected['exits']=caller_exits()
    assert actual==expected;verify_caller_header(merged[n.caller+'Body']['draft'])
    assert n.canonical(f.metadata('inspect',text=merged[n.caller+'Body']['draft'])['signature'])==base.caller_sig
    for index,fn in enumerate(functions):
        assert n.canonical(f.metadata('inspect',text=merged[fn]['draft'])['signature'])==nexts[index]
        assert n.canonical(f.metadata('inspect',text=merged[fn+'Body']['draft'])['signature'])==selected
        actual=json.loads(merged[fn+'Body/body:common']['draft']);expected=copy.deepcopy(graphs[fn]);code=next(node for node in expected['nodes'] if node['kind']=='code')
        code['signature']=copy.deepcopy(selected);code['implementationContext']['signature']=copy.deepcopy(selected);code['arguments']={'nativeAmount':{'input':'amount'},'nativeTotal':{'input':'count'}}
        expected['exits']={'return':None}
        definitions=f.metadata('featureBlueprintNodes',featureSource=merged[fn]['draft'],implementationContext=code['implementationContext'],bodyTarget='common',graph=actual)
        assert definitions['state']=='node-definitions',definitions
        expected['contractHash']=definitions['contractHash'];assert actual==expected
        assert json.loads(merged[fn+'Body/body:common/node:body']['draft'])['source']==source
        assert f.metadata('blueprintOutputSnapshot',functionText=merged[fn]['draft'])['fields']==[]

def verify(checkpoint):
    rows={row['id']:row for row in json.loads(checkpoint.read_text())['changes']};verify_rows(rows);unchanged()
    group=rows[owner]['atomicEditGroup'];assert set(functions+[fn+'Body/body:common' for fn in functions]+[n.caller+'Body/body:common',owner])<=set(group)
    return group

def verify_live():verify_rows({})
def has_mapping_dialog(index):return False
def edit_contract(popover,index):pass

def verify_pins(panel,index):
    from playwright.sync_api import expect
    method=panel.locator('[data-inline-method="'+functions[index]+'"]')
    expect(method.locator('[data-pin-side=inputs] [data-function-pin-name=amount]')).to_have_attribute('data-function-pin-type','정수')
    expect(method.locator('[data-pin-side=inputs] [data-function-pin-name=count]')).to_have_attribute('data-function-pin-type','정수')
    expect(method.locator('[data-pin-side=outputs] [data-function-pin-name=count]')).to_have_attribute('data-function-pin-type','정수')

def after_contract(index):
    from playwright.sync_api import expect
    selector='[data-inline-method="'+functions[index]+'"] [data-function-edit], [data-inline-method="'+functions[index]+'"] [data-function-write-direct]'
    held=d.pending();f.owner().locator(selector).click()
    dialog=f.page.locator('[role=dialog]:has([data-code-source])');expect(dialog).to_be_visible();assert source in dialog.locator('[data-code-source]').input_value()
    def fill():
        field=dialog.locator('[data-code-source]');field.evaluate("el=>{el.focus();el.setSelectionRange(el.value.indexOf('(')+1,el.value.indexOf(')'));}")
        f.page.keyboard.insert_text('long nativeAmount, ref long nativeTotal');f.idle()
    fill();dialog.locator('[data-code-cancel]').click();assert d.pending()==held
    f.owner().locator(selector).click();expect(dialog).to_be_visible();fill();dialog.locator('[data-code-save]').click()
    remap=f.page.get_by_role('dialog',name='호출 계약 갱신',exact=True);expect(remap).to_be_visible()
    for field in remap.locator('[data-abi-input=amount]').all():field.select_option('value')
    for field in remap.locator('[data-abi-value=amount]').all():field.fill('5')
    for field in remap.locator('[data-abi-input=count]').all():field.select_option('pin:amount')
    for field in remap.locator('[data-abi-output=count]').all():field.select_option('return')
    for field in remap.locator('[data-abi-output=return]').all():field.select_option('return')
    f.page.screenshot(path=str(f.case/('out-ref-review-'+str(index)+'.png')))
    remap.locator('[data-abi-remap-accept]').click();expect(remap).to_have_count(0);f.idle();saved=d.pending()
    for _ in range(2):f.owner().locator('[data-own-functions-toggle]').press('Control+z')
    assert d.pending()==held
    for _ in range(2):f.owner().locator('[data-own-functions-toggle]').press('Control+y')
    assert d.pending()==saved
