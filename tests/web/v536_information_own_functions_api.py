"""Contained information function creation/body/review on the real isolated engine.
No renderer, account, provider, automatic grant or project execution.
"""
import json,shutil,subprocess,sys
import v536_field_definitions_ui as d
f=d.f;owner=d.owner;fn=owner+'_Function_'+'3'*32
published=len(sys.argv)>3 and sys.argv[3]=='published'
f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file()}
def rpc(action,ok=True,**args):return f.invoke('blueprint',{'action':action,**args},ok)['result'].get('result')
def schema():f.invoke('schema',{'id':owner});return f.state()['schema']
def prepare(changes):
 s=schema();basis=rpc('readOwnerEdits',id=owner,hash=s['textHash']);return {'id':owner,'rows':[],'basis':basis['basis'],'declaration':{'id':owner,'hash':s['textHash'],'changes':changes}}
def definition():
 row=next(v for v in schema()['ownFunctions'] if v['id']==fn);return {'id':fn,'revision':row['revision'],'hash':row['hash']}
def owner_proof():
 s=schema();return {'owner':owner,'ownerRevision':s['revision'],'ownerHash':s['textHash']}
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));original_checkpoint=checkpoint.read_bytes();changes=[{'type':'function-add','id':fn,'name':'정보 자체 기능','description':'원래 정보의 기능 😀'},{'type':'data','path':['Power'],'contract':{'kind':'general','cardinality':'single','type':'long'},'valueJson':'9223372036854775805'}];request=prepare(changes);wrong={**request,'id':f.n+'RefTarget'};rpc('applySlots',False,**wrong);assert checkpoint.read_bytes()==original_checkpoint;applied=rpc('applySlots',**request);assert applied['checkpointSaved'] and not applied['sourceWritten'];s=schema();method=next(v for v in s['ownFunctions'] if v['id']==fn);assert method['name']=='정보 자체 기능' and method['origin']==owner and method['writable'];assert '9223372036854775805' in f.state()['draft']['text'];f.originals();f.checked('정보·새 native 함수·등록·exact64 기본값은 같은 후보/CAS로 저장되고 잘못된 owner 요청은 전체 미적용이다')
 saved=checkpoint.read_bytes();duplicate=prepare([changes[0]]);rpc('applySlots',False,**duplicate);assert checkpoint.read_bytes()==saved;f.originals();f.checked('같은 함수 id의 재생성은 원래 함수/정보/등록을 덮거나 일부 저장하지 않는다')
 f.stop();f.start(1);f.invoke('select',{'id':owner});s=schema();group=set(f.state()['draft']['creationReviewIds']);assert group=={owner,fn,f.n+'ProjectManifest'};assert next(v for v in s['ownFunctions'] if v['id']==fn)['description']=='원래 정보의 기능 😀';f.originals();f.checked('실제 cold는 함수의 정보 owner·contain·등록과 생성 검토 그룹을 복원하고 원래 source를 쓰지 않는다')
 if published:
  f.invoke('reviewGroup',{'ids':list(group),'target':'portable'});review=f.state()['review'];f.invoke('confirmGroup',{'ids':list(group),'token':review['token']});f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts};f.checked('본문 없는 정보 함수 정의의 별도 명시적 Confirm도 가능하며 이후 첫 구현은 새로운 owner proof를 요구한다')
 feature=definition();p=owner_proof();rpc('readFeature',False,**feature);rpc('readFeature',False,**feature,owner=f.n+'RefTarget',ownerRevision=p['ownerRevision'],ownerHash=p['ownerHash']);preview=rpc('readFeature',**feature,**p);s=schema();f.invoke('editDescription',{'id':owner,'revision':s['revision'],'hash':s['textHash'],'value':'동료 정보 변경 보존'});before=f.state()['draft']['text'];rpc('createFeature',False,id=fn,basis=preview['basis']);assert f.state()['draft']['text']==before;f.originals();f.checked('새 함수 본문 생성의 다른 owner 및 원래 정보 proof 변경은 전체 거절하고 동료 입력/함수를 보존한다')
 p=owner_proof();preview=rpc('readFeature',**feature,**p);created=rpc('createFeature',id=fn,basis=preview['basis']);assert f.state()['draft']['id']==owner and created['owner']['id']==owner;graph=rpc('read',id=created['id'],**owner_proof());assert graph['slotContext']['writable'];rpc('source',id=created['id'],basis=graph['basis'],node='body',text='return;');f.invoke('saveDraft',{});f.originals();f.stop();f.start(2);f.invoke('select',{'id':owner});s=schema();graph=rpc('read',id=created['id'],**owner_proof());assert next(v for v in graph['nodes'] if v['id']=='body')['source']=='return;';assert f.state()['draft']['id']==owner;f.checked('명시적 정보 소유 생성은 primary 선택을 유지하고 새 함수/구현/graph/본문을 같은 검토 그룹으로 Save/cold 복원한다')
 f.invoke('select',{'id':owner});group=f.state()['draft']['creationReviewIds'];assert {owner,fn,created['id'],created['node'],created['id'].split('/body:')[0],f.n+'ProjectManifest'}==set(group);f.invoke('reviewGroup',{'ids':group,'target':'portable'});review=f.state()['review'];assert {v['id'] for v in review['units']}==set(group);f.invoke('confirmGroup',{'ids':group,'token':'not-the-reviewed-token'},False);assert checkpoint.read_bytes();result=f.invoke('confirmGroup',{'ids':group,'token':review['token']})['result']['result'];assert result['sourceConfirmed'];expected={'FreeInfo.celem','project.cproj'};assert {name for name,value in f.original.items() if (f.project/name).read_bytes()!=value}==expected;assert (f.project/('elements/'+fn.split('::')[1]+'.celem')).is_file();f.checked('실제 compiler Review/명시적 Confirm은 전체 생성 그룹만 반영하며 틀린 token과 원본/부모/다른 target 변경을 차단한다')
 invoked=f.case/'compile contained invocation';shutil.copytree(f.project,invoked,ignore=shutil.ignore_patterns('.confectory'));source=invoked/'MainBody.celem';source.write_text(source.read_text().replace('{','{import '+fn+' as NewOwn () -> void in '+owner+';',1));(invoked/'Main.csbody').write_text('calls.NewOwn.Invoke();return 0;');compiled=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(invoked/'project.cproj'),'portable'],capture_output=True,text=True,env=f.env);(f.case/'contained-invocation-build.json').write_text(compiled.stdout);assert compiled.returncode==0,compiled.stderr;assert not json.loads(compiled.stdout)['warnings'];f.checked('확정한 함수의 실제 정보 scope 호출은 별도 격리 사본에서 경고 없이 컴파일하며 프로젝트를 실행하지 않는다')
 print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':False,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
except Exception:
 try:(f.case/'own-functions-api-failure.json').write_text(json.dumps({'state':f.state()},ensure_ascii=False,indent=2))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
