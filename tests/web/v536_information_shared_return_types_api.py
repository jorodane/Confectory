"""One actual checkpoint transaction for two contracts and a shared caller."""
import copy
import json
import os
if os.environ.get('CONFECTORY_SHARED_INPUT_DEFINITION_RETURN_MIX') == '1':
    import v536_information_shared_input_definition_return_mix_fixture as x
elif os.environ.get('CONFECTORY_SHARED_INPUT_OUTPUT_DEFINITION_MIX') == '1':
    import v536_information_shared_input_output_definition_mix_fixture as x
elif os.environ.get('CONFECTORY_SHARED_INPUT_RETURN_MIX') == '1':
    import v536_information_shared_input_return_mix_fixture as x
elif os.environ.get('CONFECTORY_SHARED_INPUT_NAME_OUTPUT_DEFINITIONS') == '1':
    import v536_information_shared_input_name_output_definitions_fixture as x
elif os.environ.get('CONFECTORY_SHARED_INPUT_NAME_OUTPUT_MIX') == '1':
    import v536_information_shared_input_name_output_mix_fixture as x
elif os.environ.get('CONFECTORY_SHARED_OUTPUT_DEFINITION_MIX') == '1':
    import v536_information_shared_output_definition_mix_fixture as x
elif os.environ.get('CONFECTORY_SHARED_OUTPUT_RETURN_MIX') == '1':
    import v536_information_shared_output_return_mix_fixture as x
elif os.environ.get('CONFECTORY_SHARED_INPUT_MIX') == '1':
    import v536_information_shared_input_mix_fixture as x
elif os.environ.get('CONFECTORY_SHARED_INPUT_DEFINITIONS') == '1':
    import v536_information_shared_input_definitions_fixture as x
elif os.environ.get('CONFECTORY_SHARED_INPUTS_WITH_OUT') == '1':
    import v536_information_shared_inputs_with_out_fixture as x
elif os.environ.get('CONFECTORY_SHARED_MIXED_TYPES') == '1':
    import v536_information_shared_mixed_types_fixture as x
elif os.environ.get('CONFECTORY_SHARED_IO') == '1':
    import v536_information_shared_io_fixture as x
elif os.environ.get('CONFECTORY_SHARED_LOCAL_IMPORTS') == '1':
    import v536_information_shared_local_imports_fixture as x
else:
    import v536_information_shared_return_types_fixture as x

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
    bad=copy.deepcopy(request);last=bad['declaration']['changes'][1]['mapping']
    if 'outputs' in last:next(iter(last['outputs'].values()))['source']={'input':'amount'}
    else:next(iter(last['implementations'].values()))['value']={'valueJson':'"long 아닌 값"'}
    rpc('applySlots',False,**bad)
    assert checkpoint.read_bytes()==baseline;x.unchanged()
    f.checked('실제 서버는 두 번째 계약 오류에서 첫 함수와 공유 caller도 checkpoint에 남기지 않는다')
    if x.mode=='conflict':
        s=schema();f.invoke('editDescription',{'id':x.owner,'hash':s['textHash'],'revision':s['revision'],'value':'다른 편집자의 입력'})
        text=f.state()['draft']['text'];rpc('applySlots',False,**request)
        assert f.state()['draft']['text']==text and checkpoint.read_bytes()==baseline;x.unchanged()
        f.checked('실제 동시 수정은 두 계약 전체 미적용이며 다른 편집자의 입력을 유지한다')
    elif x.mode=='source':
        source='StableHelper.celem' if hasattr(x,'stable') else 'caller.graph.json'
        target=f.project/source
        if source.endswith('.json'):
            g=json.loads(target.read_text());g['nodes'][0]['intent']='외부 편집 원문';target.write_text(json.dumps(g))
        else:target.write_text(target.read_text().replace('long value','string value'))
        peer=target.read_bytes()
        rpc('applySlots',False,**request)
        assert target.read_bytes()==peer and checkpoint.read_bytes()==baseline
        assert all((f.project/path).read_bytes()==raw for path,raw in x.snapshot.items() if path!=source)
        f.checked('참조 중인 물리 파일 경합은 기존 checkpoint와 peer 원문을 보존하고 전부 거절한다')
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
        x.verify_live()
        call=json.loads((f.project/'caller.graph.json').read_text())
        assert call['nodes'][1]['arguments']==(x.caller_arguments(1) if hasattr(x,'caller_arguments') else {'amount':x.binding('invoke',x.destination),'real':{'constant':2.5}})
        assert call['exits']==(x.caller_exits() if hasattr(x,'caller_exits') else {'return':x.binding('invoke_second',x.destination)})
        header=(f.project/'CallerBody.celem').read_text()
        # Native imports serialize type/mode/return, while graph signatures
        # retain public pin names. Count equal native contracts accordingly.
        native_signatures=['('+', '.join((a.get('mode','')+' '+a['type']).strip() for a in selected['args'])+') -> '+selected['return']+';' for selected in x.nexts]
        for signature in set(native_signatures):
            assert header.count(signature)==native_signatures.count(signature),header
        for path,raw in x.snapshot.items():
            if path not in {'FreeInfo.celem','CallerBody.celem','caller.graph.json','function.graph.json','function.node.json','second.graph.json','second.node.json',
                           *['elements/'+fn.split('::')[1]+'.celem' for fn in x.functions],
                           *[fn.split('::')[1]+'Body.celem' for fn in x.functions]}:
                assert (f.project/path).read_bytes()==raw,path
        f.checked('실제 compiler Review/Confirm는 두 계약을 함께 확정하고 code/다른 함수·부모 원문을 보존한다')
finally:
    print(json.dumps({'checks':f.checks,'evidence':str(f.case),'mode':x.mode,'actualEngine':True,'actualWindows':False},ensure_ascii=False))
    f.stop()
