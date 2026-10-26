"""Two explicit native C# bodies, with every ABI and caller unchanged."""
import copy
import hashlib
import json
import v536_information_shared_callers_fixture as base

f,d,n,owner,mode=base.f,base.d,base.n,base.owner,base.mode
functions=base.functions;old=copy.deepcopy(base.old);olds=[copy.deepcopy(old),copy.deepcopy(old)];nexts=copy.deepcopy(olds);new=old;removed=[];added=[]
native={'args':[{'name':'nativeAmount','type':'long'},{'name':'nativeCount','type':'long'}],'return':'long'}
labels=['본문 첫째','본문 둘째'];sources={};selected={};paths={};undo_steps=1;retry_field='arg0'
for index,fn in enumerate(functions):
    path=('function' if index==0 else 'second')+'-native.csbody';paths[fn]=path
    (f.project/('elements/'+fn.split('::')[1]+'.celem')).write_text('function '+fn+' (long amount,long count) -> long {value editorName='+json.dumps(labels[index],ensure_ascii=False)+';}')
    (f.project/(fn.split('::')[1]+'Body.celem')).write_text('implementation '+fn+'Body for '+fn+' (long nativeAmount,long nativeCount) -> long {body common "'+path+'";}')
    sources[fn]='return checked(nativeAmount+nativeCount); // '+labels[index]+' · 원문 9223372036854775806 😀\n'
    selected[fn]='return checked(nativeAmount-nativeCount); // '+labels[index]+' · 직접 편집 9223372036854775806 😀\n'
    (f.project/path).write_text(sources[fn])
changed_source_paths=set(paths.values())
graph=copy.deepcopy(base.graph)
if mode.startswith('raw'):
    graph['profile']='sync-acyclic-implicit-out-v1'
    graph['nodes'][1]['arguments']['amount']={'node':'invoke','output':'return'}
    (f.project/'caller.graph.json').write_text(json.dumps(graph))
snapshot={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}
def unchanged():assert all((f.project/path).read_bytes()==raw for path,raw in snapshot.items())
def request():
    r=n.request(copy.deepcopy(old),{'amount':'amount','count':'count'});fn=functions[1]
    r['changes'].append({'type':'function-edit','id':fn,'hash':hashlib.sha256(r['units'][fn]['draft'].encode()).hexdigest(),'name':labels[1],'description':'','signature':copy.deepcopy(old),'mapping':{'before':copy.deepcopy(old),'args':{'amount':'amount','count':'count'}}})
    for index,row in enumerate(r['changes']):
        row.update(name=labels[index],description='')
        args={k:r[k] for k in ['project','manifest','id','units']}
        bodies=f.metadata('informationFunctionBodies',**args,function=row['id'],includeBlueprintTargets=True)
        rows={key:body for key,body in bodies.items() if not body['caller']}
        assert len(rows)==1 and all(body['sourceKind']=='csharp' for body in rows.values()),rows
        row['mapping']['bodies']={key:{k:body[k] for k in ['hash','path']}|{'beforeSignature':copy.deepcopy(native),'signature':copy.deepcopy(native),'contract':copy.deepcopy(old),'text':selected[row['id']]} for key,body in rows.items()}
    return r

def caller_arguments(index):return copy.deepcopy(graph['nodes'][index]['arguments'])
def caller_exits():return copy.deepcopy(graph['exits'])
def verify_caller_header(text):assert text==snapshot['CallerBody.celem'].decode()
def verify_rows(rows):
    merged={row['id']:{'draft':(f.project/row['path']).read_text()} for row in f.metadata('describe',project=str(f.manifest))['units']}|rows
    assert json.loads(merged[n.caller+'Body/body:common']['draft'])==graph
    assert merged[n.caller+'Body/body:common']['draft']==snapshot['caller.graph.json'].decode()
    verify_caller_header(merged[n.caller+'Body']['draft'])
    for fn in functions:
        assert n.canonical(f.metadata('inspect',text=merged[fn]['draft'])['signature'])==old
        assert merged[fn+'Body']['draft']==snapshot[fn.split('::')[1]+'Body.celem'].decode()
        assert merged[fn+'Body/body:common']['draft']==selected[fn]
def verify(checkpoint):
    rows={row['id']:row for row in json.loads(checkpoint.read_text())['changes']};verify_rows(rows);unchanged()
    group=rows[owner]['atomicEditGroup'];assert set(functions+[fn+'Body/body:common' for fn in functions]+[owner])<=set(group)
    return group
def verify_live():verify_rows({})
def has_mapping_dialog(index):return False
def edit_contract(popover,index):pass
def verify_pins(panel,index):
    from playwright.sync_api import expect
    method=panel.locator('[data-inline-method="'+functions[index]+'"]')
    for arg in old['args']:expect(method.locator('[data-pin-side=inputs] [data-function-pin-name='+arg['name']+']')).to_have_count(1)
    expect(method.locator('[data-pin-side=outputs] [data-function-pin-name=결과]')).to_have_attribute('data-function-pin-type','정수')
    assert method.locator('[data-pin-side=inputs] [data-function-pin-name]').evaluate_all('(els)=>els.map(e=>e.dataset.functionPinName)')==['amount','count']
def after_contract(index):
    from playwright.sync_api import expect
    selector='[data-inline-method="'+functions[index]+'"] [data-function-edit], [data-inline-method="'+functions[index]+'"] [data-function-write-direct]'
    held=d.pending();f.owner().locator(selector).click();dialog=f.page.locator('[role=dialog]:has([data-code-source])');expect(dialog).to_be_visible()
    def fill():
        field=dialog.locator('[data-code-source]');assert sources[functions[index]] in field.input_value()
        field.evaluate('(el,text)=>{el.focus();const i=el.value.indexOf(text);if(i<0)throw Error("Original body absent");el.setSelectionRange(i,i+text.length);}',sources[functions[index]])
        f.page.keyboard.insert_text(selected[functions[index]]);f.idle()
    fill();dialog.locator('[data-code-cancel]').click();assert d.pending()==held
    f.owner().locator(selector).click();expect(dialog).to_be_visible();fill();f.page.screenshot(path=str(f.case/('native-body-'+str(index)+'.png')))
    dialog.locator('[data-code-save]').click();expect(dialog).to_have_count(0);f.idle();saved=d.pending()
    f.owner().locator('[data-own-functions-toggle]').press('Control+z');assert d.pending()==held
    f.owner().locator('[data-own-functions-toggle]').press('Control+y');assert d.pending()==saved
    if index==1 and mode=='reproduce-ui':
        checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes();mark=len(f.traffic)
        f.owner().locator('[data-element-action=save]').click()
        import time
        deadline=time.monotonic()+60
        while time.monotonic()<deadline:
            ids={row['invoke']['requestId'] for row in f.traffic[mark:] if row.get('invoke',{}).get('endpoint')=='blueprint' and row['invoke']['input'].get('action')=='applySlots'}
            replies=[row['result'] for row in f.traffic[mark:] if row.get('result',{}).get('requestId') in ids]
            if replies:assert replies[-1]['ok'] is False;break
            f.page.wait_for_timeout(20)
        else:raise AssertionError('No observed applySlots result')
        assert d.pending()==saved and checkpoint.read_bytes()==baseline;unchanged()
        f.checked('기존 화면에서 계약 그대로 두 본문을 편집해 Save하면 전부 거절하고 입력을 보존한다')
        f.browser.close();raise SystemExit(0)
