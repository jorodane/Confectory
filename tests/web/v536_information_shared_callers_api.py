"""One actual checkpoint transaction for two contracts and a shared caller."""
import copy
import json
import os
if os.environ.get('CONFECTORY_SHARED_OUT_REF') == '1':
    import v536_information_shared_out_ref_fixture as x
elif os.environ.get('CONFECTORY_SHARED_REF_OUT') == '1':
    import v536_information_shared_ref_out_fixture as x
elif os.environ.get('CONFECTORY_SHARED_REF_ROLES') == '1':
    import v536_information_shared_ref_roles_fixture as x
elif os.environ.get('CONFECTORY_SHARED_REF_NAMES') == '1':
    import v536_information_shared_ref_names_fixture as x
else:
    import v536_information_shared_callers_fixture as x

f=x.f
def rpc(action,ok=True,**body):return f.invoke('blueprint',{'action':action,**body},ok)['result'].get('result')
def schema():f.invoke('schema',{'id':x.owner});return f.state()['schema']
def prepare():
    s=schema();basis=rpc('readOwnerEdits',id=x.owner,hash=s['textHash'])
    return {'id':x.owner,'rows':[],'basis':basis['basis'],
            'declaration':{'id':x.owner,'hash':s['textHash'],'changes':x.request()['changes']}}

try:
    f.start(0);f.invoke('select',{'id':x.owner});f.invoke('saveDraft',{})
    checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    baseline=checkpoint.read_bytes();request=prepare()
    bad=copy.deepcopy(request);bad['declaration']['changes'][1]['mapping']['args']['amount']='count'
    rpc('applySlots',False,**bad)
    assert checkpoint.read_bytes()==baseline;x.unchanged()
    f.checked('실제 서버는 두 번째 계약 오류에서 첫 함수와 공유 caller도 checkpoint에 남기지 않는다')
    if x.mode=='conflict':
        s=schema();f.invoke('editDescription',{'id':x.owner,'hash':s['textHash'],'revision':s['revision'],'value':'다른 편집자의 입력'})
        text=f.state()['draft']['text'];rpc('applySlots',False,**request)
        assert f.state()['draft']['text']==text and checkpoint.read_bytes()==baseline;x.unchanged()
        f.checked('실제 동시 수정은 두 계약 전체 미적용이며 다른 편집자의 입력을 유지한다')
    elif x.mode=='source':
        target=f.project/'caller.graph.json';g=json.loads(target.read_text());g['nodes'][0]['intent']='외부 편집 원문';target.write_text(json.dumps(g));peer=target.read_bytes()
        rpc('applySlots',False,**request)
        assert target.read_bytes()==peer and checkpoint.read_bytes()==baseline
        assert all((f.project/path).read_bytes()==raw for path,raw in x.snapshot.items() if path!='caller.graph.json')
        f.checked('공유 caller 물리 파일 경합은 기존 checkpoint와 peer 원문을 보존하고 전부 거절한다')
    else:
        if x.mode=='storage':
            checkpoint.chmod(0o400)
            try:
                rpc('applySlots',False,**request);assert checkpoint.read_bytes()==baseline;x.unchanged()
            finally:checkpoint.chmod(0o600)
            f.checked('한 checkpoint 쓰기 실패는 어느 함수·호출자도 부분 반영하지 않는다')
        reply=rpc('applySlots',**request);assert reply['atomic'] and reply['checkpointSaved']
        ids=x.verify(checkpoint);held=checkpoint.read_bytes()
        f.stop();f.start(1);f.invoke('select',{'id':x.owner})
        assert x.verify(checkpoint)==ids and checkpoint.read_bytes()==held
        f.checked('두 callee·공유 caller는 단일 거래로 저장되고 cold 복원에서도 연결과 원문을 유지한다')
        f.invoke('reviewGroup',{'ids':ids,'target':'portable'});review=f.state()['review'];assert review['status']=='ready',review
        f.invoke('confirmGroup',{'ids':ids,'token':review['token']})
        f.stop();f.start(2);f.invoke('select',{'id':x.owner})
        sc=schema()
        for fn,sig in zip(x.functions,x.nexts):assert x.n.canonical(next(row for row in sc['ownFunctions'] if row['id']==fn)['signature'])==sig
        call=json.loads((f.project/'caller.graph.json').read_text())
        if hasattr(x,'caller_arguments'):
            assert all(node['arguments']==x.caller_arguments(index) for index,node in enumerate(call['nodes']))
        else:
            assert call['nodes'][0]['arguments']['leftAmount']=={'input':'first'}
            assert call['nodes'][1]['arguments']['rightAmount']=={'node':'invoke'}
        if hasattr(x,'verify_live'):x.verify_live()
        for path,raw in x.snapshot.items():
            if path=='CallerBody.celem' and hasattr(x,'verify_caller_header'):
                x.verify_caller_header((f.project/path).read_text());continue
            if path not in {'FreeInfo.celem','caller.graph.json','function.graph.json','function.node.json','second.graph.json','second.node.json',
                           *['elements/'+fn.split('::')[1]+'.celem' for fn in x.functions],
                           *[fn.split('::')[1]+'Body.celem' for fn in x.functions]}:
                assert (f.project/path).read_bytes()==raw,path
        f.checked('실제 compiler Review/Confirm는 두 계약을 함께 확정하고 code/다른 함수·부모 원문을 보존한다')
finally:
    print(json.dumps({'checks':f.checks,'evidence':str(f.case),'mode':x.mode,'actualEngine':True,'actualWindows':False},ensure_ascii=False))
    f.stop()
