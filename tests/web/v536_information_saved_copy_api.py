"""Actual copy-only checkpoint updates, CRLF donor retention and explicit Confirm."""
import copy,json
if 'inherited-copy' in __import__('sys').argv[4:]:
    import v536_information_inherited_contract_fixture as x
elif 'caller-copy' in __import__('sys').argv[4:]:
    import v536_information_caller_copy_fixture as x
else:
    import v536_information_saved_copy_fixture as x
f,owner,fn=x.f,x.owner,x.fn
def rpc(action,ok=True,**body):return f.invoke('blueprint',{'action':action,**body},ok)['result'].get('result')
def request():
    f.invoke('schema',{'id':owner});schema=f.state()['schema'];method=next(row for row in schema['ownFunctions'] if row['id']==fn)
    preview=rpc('readOwnerEdits',id=owner,hash=schema['textHash'],includeFunctionInputs=fn,includeFunctionBodies=True)
    assert preview['functionBodies'][x.body_id]['copyOwner']==x.copy_owner
    assert '소유 복사본' in preview['functionBodies'][x.body_id]['name']
    return {'id':owner,'rows':[],'basis':preview['basis'],'declaration':{'id':owner,'hash':schema['textHash'],'changes':[{'type':'function-edit','id':fn,'hash':method['hash'],'name':method['name'],'description':method['description'],'signature':x.new,'mapping':x.selections(preview)}]}}
try:
    f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes()
    for fault in ['missing','provenance','owner']:
        r=request();mapping=r['declaration']['changes'][0]['mapping']
        if fault=='missing':mapping.pop('copies')
        elif fault=='provenance':mapping['copies'][x.graph_id]['provenance']['bodyOrigin']='Other.Project::Body'
        else:mapping['copies'][x.graph_id]['ownerHash']='0'*64
        rpc('applySlots',False,**r);assert checkpoint.read_bytes()==baseline;x.unchanged()
    f.checked('복사 소유·배정·원래 출처의 누락/위조는 실제 서버에서 전체 미적용으로 거절한다')
    r=request();checkpoint.chmod(0o400)
    try:rpc('applySlots',False,**r);assert checkpoint.read_bytes()==baseline;x.unchanged()
    finally:checkpoint.chmod(0o600)
    result=rpc('applySlots',**request());assert result['atomic'] and result['checkpointSaved'];ids=x.verify(checkpoint)
    assert x.donor_impl not in ids and x.donor_id not in ids
    f.stop();f.start(1);f.invoke('select',{'id':owner});assert x.verify(checkpoint)==ids
    f.checked('저장 실패/재시도·cold는 소유 copy만 원자 반영하고 원래 출처와 donor CRLF 바이트를 보존한다')
    f.invoke('reviewGroup',{'ids':ids,'target':'portable'});review=f.state()['review'];assert review['status']=='ready',review
    f.invoke('confirmGroup',{'ids':ids,'token':review['token']});f.stop();f.start(2);f.invoke('select',{'id':owner})
    assert json.loads((f.project/x.body_path).read_text())['source']==x.edited
    assert (f.project/x.donor_path).read_bytes()==x.snapshot[x.donor_path]
    assert (f.project/x.donor_body_path).read_bytes()==x.snapshot[x.donor_body_path]
    assert json.loads((f.project/x.graph_path).read_text())['copySource']==x.prepared['graph']['copySource']
    f.checked('실제 compiler Review/Confirm과 재시작 후에도 donor·소유 copy ID·원래 출처를 혼동하지 않는다')
finally:
    f.stop();print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'projectRun':False,'nativeWindows':False},ensure_ascii=False))
