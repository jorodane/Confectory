"""Actual registered read-only contract + owned body atomic checkpoint/Confirm."""
import copy,json
import v536_information_registered_fixture as x
f,owner,fn=x.f,x.owner,x.fn

def rpc(action,ok=True,**body):return f.invoke('blueprint',{'action':action,**body},ok)['result'].get('result')
def request():
    f.invoke('schema',{'id':owner});s=f.state()['schema'];method=next(r for r in s['ownFunctions'] if r['id']==fn)
    p=rpc('readOwnerEdits',id=owner,hash=s['textHash'],includeFunctionInputs=fn,includeFunctionBodies=True)
    mapping=x.selections(p)
    assert mapping['dependencies'][x.caller+'Body']['contracts'][x.foreign]['textHash']==x.n.h(x.foreign_source)
    return {'id':owner,'rows':[],'basis':p['basis'],'declaration':{'id':owner,'hash':s['textHash'],'changes':[{'type':'function-edit','id':fn,'hash':method['hash'],'name':method['name'],'description':method['description'],'signature':x.new,'mapping':mapping}]}}
try:
    f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes()
    r=request()
    for fault in ['missing','forged']:
        bad=copy.deepcopy(r);mapping=bad['declaration']['changes'][0]['mapping']
        if fault=='missing':mapping.pop('dependencies')
        else:mapping['dependencies'][x.caller+'Body']['contracts'][x.foreign]['textHash']='0'*64
        rpc('applySlots',False,**bad);assert checkpoint.read_bytes()==baseline;x.unchanged()
    text=x.pack.read_bytes()
    try:
        x.pack.write_bytes(text+b' ');rpc('applySlots',False,**r);assert checkpoint.read_bytes()==baseline
    finally:x.pack.write_bytes(text)
    x.unchanged();f.checked('실제 서버는 누락·위조·바뀐 등록 계약을 저장 전에 거절하고 checkpoint·외부 팩을 보존한다')
    result=rpc('applySlots',**r);assert result['atomic'] and result['checkpointSaved'];ids=x.verify(checkpoint)
    f.stop();f.start(1);f.invoke('select',{'id':owner});assert x.verify(checkpoint)==ids
    f.checked('명시 계약·C#·import/context를 한 후보/CAS로 저장하고 재시작에서 원문과 외부 출처를 보존한다')
    f.invoke('reviewGroup',{'ids':ids,'target':'portable'});review=f.state()['review'];assert review['status']=='ready',review
    f.invoke('confirmGroup',{'ids':ids,'token':review['token']});f.stop();f.start(2);f.invoke('select',{'id':owner})
    assert json.loads((f.project/'caller-context.node.json').read_text())['source']==x.caller_text
    assert all((f.project/p).read_bytes()==v for p,v in x.snapshot.items() if p.startswith('registered/'))
    f.checked('실제 컴파일 Review/Confirm과 재시작 후에도 외부 선언·provider·등록 manifest는 불변이다')
finally:
    print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'projectRun':False,'nativeWindows':False},ensure_ascii=False));f.stop()
