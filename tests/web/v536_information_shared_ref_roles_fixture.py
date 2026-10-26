"""Explicit value/ref roles on existing retained storage; never invent a cell."""
import copy
import hashlib
import json
import v536_information_shared_ref_names_fixture as base

f,d,n,owner,mode=base.f,base.d,base.n,base.owner,base.mode
functions=base.functions
up=mode.startswith('up')
mixed=mode.startswith('mixed')
olds=copy.deepcopy(base.olds)
# Existing retained bodies can also have value parameters, for example after
# a previous explicit ref -> value edit. Their storage marker/profile persists.
for index,fn in enumerate(functions):
    value=up or mixed and index==0
    olds[index]['args'][1].pop('mode',None)
    if not value:olds[index]['args'][1]['mode']='ref'
    prefix='function' if index==0 else 'second'
    for path in ['elements/'+fn.split('::')[1]+'.celem',fn.split('::')[1]+'Body.celem']:
        p=f.project/path;p.write_text(p.read_text().replace('ref long count','long count').replace('long count',('' if value else 'ref ')+'long count'))
    g=base.graphs[fn];g['profile']='sync-acyclic-ref-v1';g['nodes'][0]['forwardCallerStorage']=True
    g['nodes'][0]['signature']['args'][1].pop('mode',None)
    if not value:g['nodes'][0]['signature']['args'][1]['mode']='ref'
    initial=f.metadata('blueprintPrepareFeature',id=fn,text='function '+fn+' (long amount,'+('' if value else 'ref ')+'long count) -> long {}',implementation=fn+'Body',graphPath=prefix+'.graph.json',nodePath=prefix+'.node.json')
    g['contractHash']=initial['graph']['contractHash']
    definition=f.metadata('featureBlueprintNodes',featureSource=(f.project/('elements/'+fn.split('::')[1]+'.celem')).read_text(),graph=g)
    (f.case/('original-storage-definition-'+str(index)+'.json')).write_text(json.dumps(definition,ensure_ascii=False,indent=2))
    assert definition.get('state')=='node-definitions',definition
    g['contractHash']=definition['contractHash']
    base.records[fn]['definitionHash']=next(row['definitionHash'] for row in definition['nodes'] if row['id']=='body')
    (f.project/(prefix+'.graph.json')).write_text(json.dumps(g));(f.project/(prefix+'.node.json')).write_text(json.dumps(base.records[fn]))
    p=f.project/'CallerBody.celem';p.write_text('\n'.join(line.replace('ref long','long').replace('(long, long)','(long, '+('' if value else 'ref ')+'long)') if fn+' ' in line else line for line in p.read_text().split('\n')))
    base.graph['nodes'][index]['signature']=copy.deepcopy(olds[index])
(f.project/'caller.graph.json').write_text(json.dumps(base.graph))
bare=mode.startswith('bare')
nexts=copy.deepcopy(olds if bare else base.nexts)
for index,sig in enumerate(nexts):
    if olds[index]['args'][1].get('mode')=='ref':sig['args'][1].pop('mode',None)
    else:sig['args'][1]['mode']='ref'
# Reuse the existing identity-preserving body/caller builder, with explicitly
# selected modes. Every before signature and graph comes from the real source.
base.olds=olds;base.nexts=nexts
old=olds[0];new=nexts[0];removed=[];added=[];retry_field='arg0';undo_steps=2 if bare else 3
snapshot={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}
base.snapshot=snapshot

def unchanged():base.unchanged()
def request():
    r=base.request()
    for index,row in enumerate(r['changes']):
        for plan in row['mapping']['bodies'].values():
            for before,after in zip(plan['signature']['args'],nexts[index]['args']):
                before.pop('mode',None)
                if after.get('mode'):before['mode']=after['mode']
    return r

def caller_arguments(index):return base.caller_arguments(index)
def caller_exits():return base.caller_exits()
def verify_caller_header(text):
    expected=snapshot['CallerBody.celem'].decode()
    for index,fn in enumerate(functions):
        expected='\n'.join(line.replace('ref long','long').replace('(long, long)','(long, '+('ref ' if nexts[index]['args'][1].get('mode') else '')+'long)') if fn+' ' in line else line for line in expected.split('\n'))
    assert text==expected
def verify_rows(rows):
    merged={row['id']:{'draft':(f.project/row['path']).read_text()} for row in f.metadata('describe',project=str(f.manifest))['units']}|rows
    shared=json.loads(merged[n.caller+'Body/body:common']['draft']);expected=copy.deepcopy(base.graph)
    for index,node in enumerate(expected['nodes']):node.update(signature=nexts[index],arguments=caller_arguments(index))
    assert shared==expected
    verify_caller_header(merged[n.caller+'Body']['draft'])
    assert n.canonical(f.metadata('inspect',text=merged[n.caller+'Body']['draft'])['signature'])==base.caller_sig
    for index,(fn,sig) in enumerate(zip(functions,nexts)):
        assert n.canonical(f.metadata('inspect',text=merged[fn]['draft'])['signature'])==sig
        selected=copy.deepcopy(olds[index]);selected['args'][1].pop('mode',None)
        if sig['args'][1].get('mode'):selected['args'][1]['mode']=sig['args'][1]['mode']
        # This retained graph's header uses public names; the independently
        # reviewed C# node below keeps the original native formal names.
        assert n.canonical(f.metadata('inspect',text=merged[fn+'Body']['draft'])['signature'])==sig
        leaf=json.loads(merged[fn+'Body/body:common']['draft']);expected=copy.deepcopy(base.graphs[fn]);code=expected['nodes'][0]
        code['signature']=selected;code['arguments']={a['name']:{'input':b['name']} for a,b in zip(selected['args'],sig['args'])}
        current=f.metadata('featureBlueprintNodes',featureSource=merged[fn]['draft'],graph=leaf);assert current['state']=='node-definitions'
        expected['contractHash']=current['contractHash'];assert leaf==expected
        assert json.loads(merged[fn+'Body/body:common/node:body']['draft'])['source']==base.records[fn]['source']

def verify(checkpoint):
    rows={row['id']:row for row in json.loads(checkpoint.read_text())['changes']};verify_rows(rows);unchanged()
    group=rows[owner]['atomicEditGroup'];assert set(functions+[fn+'Body/body:common' for fn in functions]+[n.caller+'Body/body:common',owner])<=set(group)
    return group

def verify_live():verify_rows({})
def has_mapping_dialog(index):return False
def edit_contract(popover,index):base.edit_contract(popover,index)
def verify_pins(panel,index):
    from playwright.sync_api import expect
    method=panel.locator('[data-inline-method="'+functions[index]+'"]')
    for arg in nexts[index]['args']:expect(method.locator('[data-pin-side=inputs] [data-function-pin-name='+arg['name']+']')).to_have_attribute('data-function-pin-type','정수')
    expect(method.locator('[data-pin-side=outputs] [data-function-pin-name='+nexts[index]['args'][1]['name']+']')).to_have_count(1 if nexts[index]['args'][1].get('mode')=='ref' else 0)

def after_contract(index):
    from playwright.sync_api import expect
    selector='[data-inline-method="'+functions[index]+'"] [data-function-edit], [data-inline-method="'+functions[index]+'"] [data-function-write-direct]'
    held=d.pending();f.owner().locator(selector).click()
    dialog=f.page.locator('[role=dialog]:has([data-code-source])');expect(dialog).to_be_visible()
    assert base.records[functions[index]]['source'] in dialog.locator('[data-code-source]').input_value()
    def fill():
        field=dialog.locator('[data-code-source]');field.evaluate("el=>{el.focus();el.setSelectionRange(el.value.indexOf('(')+1,el.value.indexOf(')'));}")
        f.page.keyboard.insert_text('long amount, '+('ref ' if nexts[index]['args'][1].get('mode') else '')+'long count');f.idle()
    fill();dialog.locator('[data-code-cancel]').click();assert d.pending()==held
    f.owner().locator(selector).click();expect(dialog).to_be_visible();fill();dialog.locator('[data-code-save]').click()
    remap=f.page.get_by_role('dialog',name='호출 계약 갱신',exact=True);expect(remap).to_be_visible()
    # Exact original caller bindings, including the already-owned ref cell.
    for arg,before in zip(nexts[index]['args'],olds[index]['args']):
        for select in remap.locator('[data-abi-input='+arg['name']+']').all():select.select_option('pin:'+before['name'])
    for select in remap.locator('[data-abi-output=return]').all():select.select_option('return')
    f.page.screenshot(path=str(f.case/('ref-role-review-'+str(index)+'.png')))
    remap.locator('[data-abi-remap-accept]').click();expect(remap).to_have_count(0);f.idle()
    saved=d.pending()
    for _ in range(2):f.owner().locator('[data-own-functions-toggle]').press('Control+z')
    assert d.pending()==held
    for _ in range(2):f.owner().locator('[data-own-functions-toggle]').press('Control+y')
    assert d.pending()==saved
