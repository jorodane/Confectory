"""Actual manual caller import/source candidate, cold and compiler boundary."""
import json
import v536_information_context_fixture as x
f,owner,fn=x.f,x.owner,x.fn

def rpc(action,ok=True,**body):return f.invoke('blueprint',{'action':action,**body},ok)['result'].get('result')
def request():
    f.invoke('schema',{'id':owner});s=f.state()['schema'];method=next(r for r in s['ownFunctions'] if r['id']==fn)
    p=rpc('readOwnerEdits',id=owner,hash=s['textHash'],includeFunctionInputs=fn,includeFunctionBodies=True)
    return {'id':owner,'rows':[],'basis':p['basis'],'declaration':{'id':owner,'hash':s['textHash'],'changes':[{'type':'function-edit','id':fn,'hash':method['hash'],'name':method['name'],'description':method['description'],'signature':x.new,'mapping':x.selections(p)}]}}
try:
    f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes()
    for fault in ['missing','old-source','stale','own-abi']:
        r=request();plans=r['declaration']['changes'][0]['mapping']['bodies'];body=plans[x.caller_id]
        if fault=='missing':plans.pop(x.caller_id)
        elif fault=='old-source':body['text']=x.original_caller
        elif fault=='stale':body['whole']['hash']='0'*64
        else:body['signature']=x.new
        rpc('applySlots',False,**r);assert checkpoint.read_bytes()==baseline
    f.checked('caller own ABI·원래 context/source/import 증거와 명시 C# 오류는 전체 미적용이다')
    result=rpc('applySlots',**request());assert result['atomic'] and result['checkpointSaved'];ids=x.verify(checkpoint)
    f.stop();f.start(1);f.invoke('select',{'id':owner});assert x.verify(checkpoint)==ids
    f.checked('callee와 수동 caller C#·import를 한 후보/CAS에 저장하고 own ABI·원문·cold를 보존한다')
    f.invoke('reviewGroup',{'ids':ids,'target':'portable'});r=f.state()['review'];assert r['status']=='ready',r
    f.invoke('confirmGroup',{'ids':ids,'token':r['token']});f.stop();f.start(2);f.invoke('select',{'id':owner})
    assert json.loads((f.project/'caller-context.node.json').read_text())['source']==x.caller_text
    assert json.loads((f.project/x.body_path).read_text())['source']==x.edited
    assert x.n.canonical(f.metadata('inspect',text=(f.project/'CallerBody.celem').read_text())['signature'])==x.caller_signature
    f.checked('실제 Review/Confirm 뒤 재시작에서도 source/context/import와 caller ABI를 함께 보존한다')
finally:
    print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'projectRun':False,'nativeWindows':False},ensure_ascii=False));f.stop()
