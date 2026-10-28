"""Real fixture workspace own-function retirement/recovery; no user data or execution."""
import hashlib,json,sys
import v536_field_definitions_ui as d
f=d.f;owner=d.owner;fn=owner+'_Function_'+'b'*32;mode=sys.argv[3] if len(sys.argv)>3 else 'normal';manifest_id=f.n+'ProjectManifest'
def rpc(action,**args):return f.invoke('blueprint',{'action':action,**args})['result']['result']
def schema():f.invoke('schema',{'id':owner});return f.state()['schema']
def plan(ok=True):
 s=schema();method=next(row for row in s['ownFunctions'] if row['id']==fn);return f.invoke('planBrowserRemoval',{'ids':[fn],'information':{'owner':owner,'hash':s['textHash'],'functionHash':method['hash']}},ok)['result'].get('result')
def action(name,token,ok=True):return f.invoke('browserRetirement',{'action':name,'token':token},ok)['result'].get('result')
def restart(index):f.stop();f.start(index);f.invoke('select',{'id':owner});return schema()
def absent():assert not any(row['id']==fn for row in schema()['ownFunctions']) and not any(row['function']==fn for row in f.state()['schema']['providers'])
def present():assert next(row for row in schema()['ownFunctions'] if row['id']==fn)['name']=='보관할 자체 함수'
def confirm(ids):
 f.invoke('reviewGroup',{'ids':ids,'target':'portable'});review=f.state()['review'];assert review['status']=='ready',review;result=f.invoke('confirmGroup',{'ids':ids,'token':review['token']})['result']['result'];assert result['sourceConfirmed'],result
try:
 f.start(0);f.invoke('select',{'id':owner});s=schema();p=rpc('readOwnerEdits',id=owner,hash=s['textHash']);rpc('applySlots',id=owner,rows=[],basis=p['basis'],declaration={'id':owner,'hash':s['textHash'],'changes':[{'type':'function-add','id':fn,'name':'보관할 자체 함수','description':'보존할 선언'}]})
 if mode!='pending-bare':
  s=schema();method=next(row for row in s['ownFunctions'] if row['id']==fn);p=rpc('readFeature',id=fn,hash=method['hash'],revision=method['revision'],owner=owner,ownerHash=s['textHash'],ownerRevision=s['revision']);created=rpc('createFeature',id=fn,basis=p['basis']);s=schema();g=rpc('read',id=created['id'],owner=owner,ownerHash=s['textHash'],ownerRevision=s['revision']);rpc('source',id=created['id'],basis=g['basis'],node='body',text='return; // retained body')
 f.invoke('saveDraft',{});schema()
 if not mode.startswith('pending-'):confirm(f.state()['draft']['creationReviewIds'])
 if mode=='normal':
  source=f.project/('elements/'+fn.split('::')[1]+'BlueprintBody.celem');source.write_text(source.read_text().replace('}', 'body linux \"retained-linux.csbody\";}',1));(f.project/'retained-linux.csbody').write_text('return; // 다른 target 원문');restart(99)
 f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts};checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();p=plan();assert p['state']=='planned' and not p['references'];token=p['token'];f.originals()
 if mode.startswith('pending-'):
  original_ids=set(p['ids']);assert json.loads(before)['changes'];action('apply',token);absent();f.originals();assert all(not (f.project/'elements'/name).exists() for name in [fn.split('::')[1]+'.celem',fn.split('::')[1]+'BlueprintBody.celem']);restart(1);absent();f.originals();f.checked('미확정 자체 함수의 삭제·cold는 생성 원문과 본문을 보관하며 빈 최종 파일이나 부분 생성을 남기지 않는다')
  action('recover',token);present();f.originals();restart(2);present();f.originals();assert set(f.state()['draft']['creationReviewIds'])==original_ids|{owner,manifest_id};confirm(f.state()['draft']['creationReviewIds']);present();assert (f.project/('elements/'+fn.split('::')[1]+'.celem')).exists();restart(3);present();assert not f.state()['retirements'];f.checked('미확정 삭제 복구는 원래 생성 후보 전체를 cold 뒤에도 복원하고 새 명시적 Review/Confirm에서만 최종 파일을 만든다')
 elif mode=='queries':
  def query(name,t=token):return f.invoke('browserArchiveOutcome',{'action':name,'token':t})['result']['result']
  assert query('apply')=={'settled':False,'unapplied':True};assert query('apply','0'*64)=={'settled':False,'unapplied':False};assert checkpoint.read_bytes()==before;present();f.checked('결과 조회는 원래 미실행 계획만 재시도 가능으로 읽고 다른 token은 채택하지 않으며 저장하지 않는다')
  action('apply',token);absent();saved=checkpoint.read_bytes();assert query('apply')['settled'];assert query('recover')=={'settled':False,'unapplied':True};assert checkpoint.read_bytes()==saved;action('recover',token);present();saved=checkpoint.read_bytes();assert query('recover')['settled'];restart(1);present();assert query('recover')['settled'];assert checkpoint.read_bytes()==saved;f.checked('실제 삭제·복구와 cold 후 읽기 조회로 완료를 확인하며 추가 mutation을 보내지 않는다')
  s=schema();f.invoke('editDescription',{'id':owner,'revision':s['revision'],'hash':s['textHash'],'value':'응답 뒤 보존할 새 입력'});assert query('recover')=={'settled':False,'unapplied':False};assert checkpoint.read_bytes()==saved;f.originals();f.checked('결과 뒤 새 입력이 생기면 완료나 미실행으로 추측하지 않고 양쪽 근거와 입력을 보존한다')
 elif mode=='discard-storage':
  action('apply',token);absent();saved=checkpoint.read_bytes();s=f.invoke('browserDrafts',{'action':'status','ids':[owner,manifest_id]})['result']['result'];request={'action':'discard','ids':s['ids'],'revisions':[r['revision'] for r in s['rows']],'hashes':[r['hash'] for r in s['rows']],'ownerHash':s['ownerHash'],'checkpointHash':s['checkpointHash']};checkpoint.chmod(0o400)
  try:
   f.invoke('browserDrafts',request,False);assert checkpoint.read_bytes()==saved;absent();assert f.state()['retirements'][0]['state']=='pending';f.originals();f.checked('변경 취소의 쓰기 실패도 보관된 삭제 상태와 전체 checkpoint를 유지하며 live 복구만 먼저 적용하지 않는다')
  finally:checkpoint.chmod(0o600)
  f.invoke('browserDrafts',request);present();assert not f.state()['retirements'];f.originals();restart(1);present();f.originals();f.checked('같은 원래 변경 취소의 명시적 재시도와 cold는 한 번만 전체 함수를 복구한다')
 elif mode=='outcomes':
  action('apply',token);action('recover',token);present();assert not f.state()['retirements'];saved=checkpoint.read_bytes();assert action('recover',token)['settled'];assert checkpoint.read_bytes()==saved;restart(1);present();assert action('recover',token)['settled'];assert checkpoint.read_bytes()==saved;f.originals();f.checked('pending 복구의 완료 proof는 archive 제거 후에도 저장되며 재전송·cold를 추가 쓰기 없이 확인한다')
  s=schema();f.invoke('editDescription',{'id':owner,'revision':s['revision'],'hash':s['textHash'],'value':'복구 응답 뒤 새 설명'});peer=f.state()['draft']['text'];action('recover',token,False);assert f.state()['draft']['text']==peer;assert checkpoint.read_bytes()==saved;f.invoke('saveDraft',{});restart(2);present();current=checkpoint.read_bytes();action('recover',token,False);assert checkpoint.read_bytes()==current;f.originals();f.checked('완료 후 달라진 새 입력은 이전 결과로 채택하거나 덮지 않으며 재시작 후에도 보존한다')
  p=plan();token=p['token'];action('apply',token);confirm([owner,manifest_id]);f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts};action('recover',token);present();saved=checkpoint.read_bytes();assert action('recover',token)['settled'];assert checkpoint.read_bytes()==saved;restart(3);present();assert action('recover',token)['settled'];assert checkpoint.read_bytes()==saved;action('cancel',token);absent();saved=checkpoint.read_bytes();assert action('cancel',token)['settled'];assert checkpoint.read_bytes()==saved;restart(4);absent();assert action('cancel',token)['settled'];assert checkpoint.read_bytes()==saved;f.originals();f.checked('확정 archive 복구와 복구 취소의 재전송·cold는 정확한 phase/source proof를 조회하고 거래를 중복 적용하지 않는다')
 elif mode in ['storage','conflict']:
  if mode=='storage':checkpoint.chmod(0o400)
  else:
   s=schema();f.invoke('editDescription',{'id':owner,'revision':s['revision'],'hash':s['textHash'],'value':'동료가 먼저 작성한 설명'});peer=f.state()['draft']['text']
  try:
   action('apply',token,False);present();assert not f.state()['retirements'];assert checkpoint.read_bytes()==before;f.originals();f.checked('쓰기가 거절되거나 계획 뒤 실제 정보 초안이 바뀌면 정보/함수/등록/전체 본문을 모두 미적용하고 원본을 보존한다')
  finally:
   if mode=='storage':checkpoint.chmod(0o600)
  if mode=='storage':action('apply',token);absent();f.originals();restart(1);absent();f.originals();f.checked('쓰기 실패 뒤 같은 원래 계획의 명시적 재시도와 cold는 한 번만 완전한 archive를 보관한다')
  else:assert f.state()['draft']['text']==peer;f.invoke('inspectDeclaration',{'id':owner});assert f.state()['declaration']['description']=='동료가 먼저 작성한 설명';f.invoke('saveDraft',{});saved=checkpoint.read_bytes();action('apply',token,False);assert checkpoint.read_bytes()==saved;present();f.originals();f.checked('새 checkpoint 이후 이전 삭제 계획 재시도는 덮어쓰지 않고 동료 입력·새 저장본을 유지한다')
 else:
  result=action('apply',token);assert result['checkpointSaved'];absent();assert f.state()['retirements'][0]['state']=='pending';f.originals();saved=checkpoint.read_bytes();repeat=action('apply',token);assert repeat['settled'] and checkpoint.read_bytes()==saved;f.checked('저장된 자체 함수와 독점 구현/graph/node 삭제는 하나의 checkpoint로 전체 적용하며 동일 요청 재전송도 중복 적용하지 않는다')
  f.invoke('reviewGroup',{'ids':[manifest_id],'target':'portable'},False);assert checkpoint.read_bytes()==saved;restart(1);absent();assert f.state()['retirements'][0]['state']=='pending';f.originals();action('recover',token);present();assert not f.state()['retirements'];f.originals();restart(2);present();f.originals();f.checked('정보/등록 일부만 Review하면 차단하고 pending archive의 cold·복구는 함수/본문/원래 값을 되살리며 최종 파일을 쓰지 않는다')
  p=plan();token=p['token'];action('apply',token);confirm([owner,manifest_id]);absent();assert f.state()['retirements'][0]['state']=='confirmed';assert {path for path,data in f.original.items() if (f.project/path).read_bytes()!=data}=={'FreeInfo.celem','project.cproj'};f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts};f.checked('새 명시적 compiler Confirm만 정보 연결/등록 제외를 반영하며 함수·구현·본문 원본 파일은 물리 삭제하지 않는다')
  restart(3);absent();action('recover',token);present();ids=f.state()['draft']['creationReviewIds'];assert set(ids)=={owner,manifest_id,fn,fn+'BlueprintBody',created['id'],created['node'],fn+'BlueprintBody/body:linux'};f.originals();action('cancel',token);absent();assert f.state()['retirements'][0]['state']=='confirmed';f.originals();restart(4);absent();action('recover',token);present();confirm(f.state()['draft']['creationReviewIds']);assert not f.state()['retirements'];present();restart(5);present();assert not f.state()['retirements'];assert all((f.project/path).read_bytes()==data for path,data in f.original.items() if path not in ['FreeInfo.celem','project.cproj']);f.checked('확정 archive의 cold·복구 취소·재복구는 전체 새 Review/Confirm 후에만 등록을 되살리고 기존 본문 원본을 보존한다')
 print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':False,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
except Exception:
 try:(f.case/'information-retirement-api-failure.json').write_text(json.dumps({'state':f.state(),'checks':f.checks},ensure_ascii=False,indent=2))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
