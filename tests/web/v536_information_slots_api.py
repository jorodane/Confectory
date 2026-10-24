"""Atomic schema-owned module implementation/import/copy paths in an isolated real engine.
No account, model call, project execution, automatic Confirm or source/donor edits.
"""
import hashlib,json,sys
import v536_field_definitions_ui as d
f=d.f;owner=d.owner;info=f.project/'FreeInfo.celem'
info.write_text(info.read_text().replace('FreeInfo {','FreeInfo {module '+f.n+'Rules;provide '+f.n+'Slot with '+f.n+'AliasBody;',1))
main=f.project/'MainBody.celem';main.write_text(main.read_text().replace(' in '+f.n+'Slime;',' in '+owner+';'))
f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file()}
def rpc(action,ok=True,**args):return f.invoke('blueprint',{'action':action,**args},ok)['result'].get('result')
def schema():f.invoke('schema',{'id':owner});return f.state()['schema']
def require():
 s=schema();return {'id':owner,'revision':s['revision'],'hash':s['textHash']}
def state_snapshot():
 s=f.state();return json.dumps(s['draft'],sort_keys=True),next(f.project.glob('.confectory/edit-workspaces/*/draft.json')).read_bytes()
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});basis=require();before=state_snapshot()
 listing=rpc('implementationCallables',id=owner,function=f.n+'Slot2',scope='owned',query='Donor',page=0);assert [r['id'] for r in listing['rows']]==[f.n+'Donor'];f.originals()
 created=f.n+'InfoImported';prepared=rpc('readImplementation',**basis,function=f.n+'Slot2',implementation=created,reference=f.n+'Donor');assert not prepared['sourceWritten'] and not prepared['compiled'] and prepared['contractBodyReads']==0
 row={'function':f.n+'Slot2','implementation':created,'reference':f.n+'Donor','basis':prepared['basis']}
 rpc('applySlots',False,id=f.n+'RefTarget',rows=[row]);assert state_snapshot()==before
 applied=rpc('applySlots',id=owner,rows=[row]);assert applied['checkpointSaved'] and not applied['sourceWritten'];s=schema();assert next(r for r in s['providers'] if r['function']==f.n+'Slot2')['origin']==owner;assert '9223372036854775806' in f.state()['draft']['text'];f.originals()
 settled=rpc('settledSlots',id=owner,rows=[{'function':f.n+'Slot2','implementation':created,'reference':f.n+'Donor','fingerprint':prepared['contractFingerprint']}]);assert settled['settled'];f.checked('정보의 기존 module 슬롯은 명시적 함수 선택/import·manifest/graph/provider를 한 후보·CAS로 저장하고 다른 owner 토큰은 전체 거절한다')
 body=rpc('read',id=created+'/body:common',owner=owner,ownerRevision=s['revision'],ownerHash=s['textHash']);assert body['slotContext']['owner']==owner and body['slotContext']['writable'] is True and body['nodes'][0]['calledFeature']==f.n+'Donor';before=state_snapshot();rpc('read',False,id=created+'/body:common',owner=f.n+'RefTarget',ownerRevision=0,ownerHash=s['textHash']);assert state_snapshot()==before;f.originals();f.checked('실제 정보 provide에 묶인 본문 read만 성공하고 위조 owner/body는 입력·checkpoint·원본을 바꾸지 않는다')
 basis=require();catalog=rpc('implementationSources',**basis,function=f.n+'Slot');assert any(r['id']==f.n+'AliasBody' and r['target']=='common' for r in catalog['rows']);new=f.n+'InfoCopy';copy=rpc('readImplementationCopy',**basis,function=f.n+'Slot',source=f.n+'AliasBody',target='common',implementation=new);assert copy['preview']['slotContext']['owner']==owner;f.originals()
 f.stop();f.start(1);f.invoke('select',{'id':owner});copy=rpc('readImplementationCopy',**require(),function=f.n+'Slot',source=f.n+'AliasBody',target='common',implementation=new,expectedContentFingerprint=copy['contentFingerprint']);assert copy['seedHash'];f.checked('실제 cold는 정보 owner의 저장 import와 private copy snapshot/원래 출처 식별성을 복원한다');copyrow={'function':f.n+'Slot','implementation':new,'copySource':f.n+'AliasBody','copyTarget':'common','basis':copy['basis'],'edits':[{'type':'source','node':'body','text':'slotCount=amount+7;slotReady=true;return amount+9;'}]}
 result=rpc('applySlots',id=owner,rows=[copyrow]);assert result['checkpointSaved'];s=schema();provider=next(r for r in s['providers'] if r['function']==f.n+'Slot');assert provider['implementation']==new and provider['contract']['status']=='valid';body=rpc('read',id=new+'/body:common',owner=owner,ownerRevision=s['revision'],ownerHash=s['textHash']);assert next(r for r in body['nodes'] if r['id']=='body')['source']=='slotCount=amount+7;slotReady=true;return amount+9;';assert body['slotContext']['writable'] is True;f.originals();f.checked('기본/상속 Blueprint의 비공개 snapshot 복사는 정보의 원래 provide만 바꾸고 donor/부모/다른 target과 정확한 기본값을 보존한다')
 rpc('source',id=new+'/body:common',basis=body['basis'],node='body',text='slotCount=amount+11;slotReady=false;return amount+19;');f.invoke('saveDraft',{});f.originals();f.stop();f.start(2);f.invoke('select',{'id':owner});s=schema();body=rpc('read',id=new+'/body:common',owner=owner,ownerRevision=s['revision'],ownerHash=s['textHash']);assert next(r for r in body['nodes'] if r['id']=='body')['source']=='slotCount=amount+11;slotReady=false;return amount+19;';f.originals();f.checked('정보 소유 copy의 실제 본문 편집/Save/cold는 그 본문만 복원하며 원래 모듈/함수/부모/다른 target을 바꾸지 않는다')
 before=state_snapshot();s=schema();removal=rpc('readSlotRemoval',id=owner,function=f.n+'Slot2',implementation=created,revision=s['revision'],hash=s['textHash']);changed=f.invoke('editDescription',{'id':owner,'revision':s['revision'],'hash':s['textHash'],'value':'동시 편집 보존'})['state'];rpc('applySlots',False,id=owner,rows=[{'function':f.n+'Slot2','implementation':created,'basis':removal['basis']}]);assert f.state()['draft']['text']==changed['draft']['text'] and next(f.project.glob('.confectory/edit-workspaces/*/draft.json')).read_bytes()==before[1];f.originals();f.checked('실제 같은 정보의 후속 편집 뒤 오래된 구현 삭제 CAS는 전체 미적용이고 새 설명·저장 copy/import·checkpoint를 보존한다')
 print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':False,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
except Exception:
 try:(f.case/'information-slots-failure.json').write_text(json.dumps({'state':f.state()},ensure_ascii=False,indent=2))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
