"""Actual whole-body candidate/cold/compiler, no project Run or real account."""
import copy
import json
import v536_information_whole_body_fixture as x
f, owner, fn=x.f,x.owner,x.fn

def rpc(action,ok=True,**input):return f.invoke('blueprint',{'action':action,**input},ok)['result'].get('result')
def request():
    f.invoke('schema',{'id':owner});s=f.state()['schema'];method=next(r for r in s['ownFunctions'] if r['id']==fn)
    p=rpc('readOwnerEdits',id=owner,hash=s['textHash'],includeFunctionInputs=fn,includeFunctionBodies=True)
    return {'id':owner,'rows':[],'basis':p['basis'],'declaration':{'id':owner,'hash':s['textHash'],'changes':[{'type':'function-edit','id':fn,'hash':method['hash'],'name':method['name'],'description':method['description'],'signature':x.new,'mapping':x.selections(p)}]}}
try:
    f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{})
    checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes()
    for fault in ['missing','hash','syntax','type','storage','caller']:
        r=request();m=r['declaration']['changes'][0]['mapping'];b=m['bodies'][x.body_id]
        if fault=='missing':m.pop('bodies')
        elif fault=='hash':b['hash']='0'*64
        elif fault=='syntax':b['text']='return ; }'
        elif fault=='type':b['text']='nativeTotal="wrong";return nativeAmount;'
        elif fault=='storage':next(iter(m['callers'].values()))['inputs']['amount']={'valueJson':'1'}
        else:m['callers'].clear()
        rpc('applySlots',False,**r);assert checkpoint.read_bytes()==baseline
        assert all((f.project/path).read_bytes()==v for path,v in x.snapshot.items())
    f.checked('whole-body 본문/원래 증거/컴파일/명시 ref 저장소/호출자 오류는 전체 미적용이다')
    r=rpc('applySlots',**request());assert r['atomic'] and r['checkpointSaved'];ids=x.verify(checkpoint)
    f.stop();f.start(1);f.invoke('select',{'id':owner});assert x.verify(checkpoint)==ids
    f.checked('명시 본문·native/ref/out·호출자 저장소는 한 후보/CAS로 저장하고 cold에서 정확히 복원한다')
    f.invoke('reviewGroup',{'ids':ids,'target':'portable'});review=f.state()['review'];assert review['status']=='ready',review
    f.invoke('confirmGroup',{'ids':ids,'token':review['token']});f.stop();f.start(2);f.invoke('select',{'id':owner})
    assert json.loads((f.project/x.body_path).read_text())['source']==x.edited
    f.invoke('schema',{'id':owner});assert x.n.canonical(next(r for r in f.state()['schema']['ownFunctions'] if r['id']==fn)['signature'])==x.new
    for path,v in x.snapshot.items():
        if path not in {'FreeInfo.celem',x.function_path,x.implementation_path,'function.graph.json','function.node.json','CallerBody.celem','caller.graph.json'}:assert (f.project/path).read_bytes()==v,path
    f.checked('실제 compiler Review/Confirm 이후에만 source/native/context/caller를 함께 반영하며 부모·타 함수·정확한 원문을 보존한다')
    s=f.state()['schema'];method=next(r for r in s['ownFunctions'] if r['id']==fn)
    preview=rpc('readOwnerEdits',id=owner,hash=s['textHash'],includeFunctionInputs=fn,includeFunctionBodies=True)
    row=preview['functionBodies'][x.body_id];assert row['signature']==x.selected
    mapping={'before':x.new,'args':x.remap,'bodies':{x.body_id:{k:row[k] for k in ['hash','path']}|{'beforeSignature':x.selected,'signature':x.native,'contract':x.old,'text':x.edited}},'callers':{key:{k:r[k] for k in ['graph','node','hash']}|{'inputs':{'amount':'amount'},'disconnect':{}} for key,r in preview['functionInputs'].items()}}
    applied=rpc('applySlots',id=owner,rows=[],basis=preview['basis'],declaration={'id':owner,'hash':s['textHash'],'changes':[{'type':'function-edit','id':fn,'hash':method['hash'],'name':method['name'],'description':method['description'],'signature':x.old,'mapping':mapping}]})
    assert applied['atomic'] and applied['checkpointSaved']
    reverse={r['id']:r for r in json.loads(checkpoint.read_text())['changes']}
    assert x.n.canonical(f.metadata('inspect',text=reverse[fn+'Body']['draft'])['signature'])==x.native
    g=json.loads(reverse[fn+'Body/body:common']['draft']);assert g['nodes'][0]['arguments']=={'nativeAmount':{'input':'amount'}} and g['nodes'][0]['signature']==x.native
    assert json.loads(reverse[x.body_id]['draft'])['source']==x.edited
    assert json.loads((f.project/x.body_path).read_text())['source']==x.edited
    f.checked('자기 Confirm 뒤 최신 증거로 다시 편집하여 ref→값을 되돌려도 native/out/source와 저장소를 보존하며 허위 충돌로 차단하지 않는다')
finally:
    print(json.dumps({'checks':f.checks,'actualEngine':True,'evidence':str(f.case),'nativeWindows':False,'projectRun':False},ensure_ascii=False));f.stop()
