"""Implementation-only archive through the actual isolated engine save/CAS/Confirm gate."""
import json,sys
import v536_field_definitions_ui as d
f=d.f;owner=d.owner;fn=owner+'_Function_'+'c'*32;mode=sys.argv[3] if len(sys.argv)>3 else 'normal';manifest=f.n+'ProjectManifest'
def rpc(action,**args):return f.invoke('blueprint',{'action':action,**args})['result']['result']
def schema():f.invoke('schema',{'id':owner});return f.state()['schema']
def plan(ok=True):
 s=schema();method=next(v for v in s['ownFunctions'] if v['id']==fn);return f.invoke('planBrowserRemoval',{'ids':[fn],'information':{'owner':owner,'hash':s['textHash'],'functionHash':method['hash'],'mode':'implementation-only-v1'}},ok)['result'].get('result')
def action(name,token,ok=True):return f.invoke('browserRetirement',{'action':name,'token':token},ok)['result'].get('result')
def query(name,token):return f.invoke('browserArchiveOutcome',{'action':name,'token':token})['result']['result']
def check(present):
 s=schema();assert next(v for v in s['ownFunctions'] if v['id']==fn)['name']=='선언 유지 자체 함수';assert any(v['function']==fn for v in s['providers']) is present;assert fnpath.read_bytes()==function_original;f.originals()
def confirm(ids):
 f.invoke('reviewGroup',{'ids':ids,'target':'portable'});review=f.state()['review'];assert review['status']=='ready',review;assert f.invoke('confirmGroup',{'ids':ids,'token':review['token']})['result']['result']['sourceConfirmed']
def restart(i):f.stop();f.start(i);f.invoke('select',{'id':owner});schema()
try:
 f.start(0);f.invoke('select',{'id':owner});s=schema();b=rpc('readOwnerEdits',id=owner,hash=s['textHash']);rpc('applySlots',id=owner,rows=[],basis=b['basis'],declaration={'id':owner,'hash':s['textHash'],'changes':[{'type':'function-add','id':fn,'name':'선언 유지 자체 함수','description':'함수 선언 원문 보존'}]});s=schema();method=next(v for v in s['ownFunctions'] if v['id']==fn);preview=rpc('readFeature',id=fn,hash=method['hash'],revision=method['revision'],owner=owner,ownerHash=s['textHash'],ownerRevision=s['revision']);created=rpc('createFeature',id=fn,basis=preview['basis']);s=schema();body=rpc('read',id=created['id'],owner=owner,ownerHash=s['textHash'],ownerRevision=s['revision']);rpc('source',id=created['id'],basis=body['basis'],node='body',text='return; // body kept while declaration remains');f.invoke('saveDraft',{});schema();confirm(f.state()['draft']['creationReviewIds']);fnpath=f.project/('elements/'+fn.split('::')[1]+'.celem');function_original=fnpath.read_bytes();f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts};checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();p=plan();token=p['token'];assert p['state']=='planned' and fn not in p['ids'];check(True);assert checkpoint.read_bytes()==before;f.checked('실제 계획은 함수 선언·핀·등록을 보존하고 구현 closure만 선택하며 원본이나 checkpoint를 쓰지 않는다')
 if mode in ['bindings','function-bindings']:
  f.invoke('select',{'id':f.id});primary=f.state()['draft'];f.invoke('openEditorView',{'view':'1','id':owner,'viewMode':'properties'});row=next(v for v in f.state()['editorViews'] if v['view']=='1');surface={'view':'1','id':owner,'viewBinding':row['authorBinding']};s=row['schema'];method=next(v for v in s['ownFunctions'] if v['id']==fn);request={'ids':[fn],'information':{'owner':owner,'hash':s['textHash'],'functionHash':method['hash'],'mode':'implementation-only-v1'},**surface}
  if mode=='function-bindings':request['information'].pop('mode')
  for bad in [{k:v for k,v in request.items() if k!='viewBinding'},{**request,'viewBinding':'0'*32},{**request,'id':f.n+'Leaf'},{**request,'information':{**request['information'],'mode':'unknown-lifetime'}}]:f.invoke('planBrowserRemoval',bad,False);assert checkpoint.read_bytes()==before
  p=f.invoke('planBrowserRemoval',request)['result']['result'];token=p['token'];f.invoke('openEditorView',{'view':'2','id':f.n+'Leaf','viewMode':'properties'});other=next(v for v in f.state()['editorViews'] if v['view']=='2');f.invoke('browserRetirement',{'action':'apply','token':token,'view':'2','id':other['id'],'viewBinding':other['authorBinding']},False);assert checkpoint.read_bytes()==before;f.checked('독립 구현 계획은 정확한 정보/프로젝트/mode/nonce를 요구하고 위조·다른 창 token을 거절한다')
  f.invoke('browserRetirement',{'action':'apply','token':token,**surface});assert f.state()['draft']==primary;row=next(v for v in f.state()['editorViews'] if v['view']=='1');assert any(v['id']==fn for v in row['schema']['ownFunctions'])==(mode=='bindings') and not any(v['function']==fn for v in row['schema']['providers']);saved=checkpoint.read_bytes();f.invoke('closeEditorView',{'view':'1','id':owner});f.invoke('openEditorView',{'view':'1','id':owner,'viewMode':'properties'});fresh=next(v for v in f.state()['editorViews'] if v['view']=='1');assert fresh['authorBinding']!=surface['viewBinding'];f.invoke('browserRetirement',{'action':'recover','token':token,**surface},False);assert checkpoint.read_bytes()==saved;surface['viewBinding']=fresh['authorBinding'];assert f.invoke('browserArchiveOutcome',{'action':'apply','token':token,**surface})['result']['result']['settled'];f.invoke('browserRetirement',{'action':'recover','token':token,**surface});assert f.state()['draft']==primary and not f.state()['retirements'];f.originals();assert fnpath.read_bytes()==function_original;f.checked('독립 삭제·닫기/reopen·복구는 새 nonce에서만 처리하고 primary 선택/입력과 Fn source를 보존한다')
  f.stop();f.start(10);f.invoke('select',{'id':f.id});f.invoke('openEditorView',{'view':'1','id':owner,'viewMode':'properties'});row=next(v for v in f.state()['editorViews'] if v['view']=='1');surface['viewBinding']=row['authorBinding'];current=checkpoint.read_bytes();assert f.invoke('browserArchiveOutcome',{'action':'recover','token':token,**surface})['result']['result']['settled'];assert checkpoint.read_bytes()==current;f.originals();f.checked('archive 제거 뒤 cold 완료조회도 해당 bound 정보의 저장된 proof만 읽고 재적용하지 않는다')
 elif mode=='conflict':
  s=schema();f.invoke('editDescription',{'id':owner,'revision':s['revision'],'hash':s['textHash'],'value':'계획 뒤 동료의 정보 변경'});peer=f.state()['draft']['text'];action('apply',token,False);assert checkpoint.read_bytes()==before and f.state()['draft']['text']==peer;check(True);f.checked('계획 뒤 동료 변경은 전체 미적용이며 새 정보 원문·함수·구현을 보존한다')
 else:
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:action('apply',token,False);assert checkpoint.read_bytes()==before;assert not f.state()['retirements'];check(True)
   finally:checkpoint.chmod(0o600)
   assert query('apply',token)['unapplied'];f.checked('실제 쓰기 거절은 live/disk 모두 미적용이며 읽기 결과 조회 뒤 같은 원래 후보만 재시도한다')
  applied=action('apply',token);assert applied['retainedFunction']==fn;check(False);saved=checkpoint.read_bytes();assert query('apply',token)['settled'];assert checkpoint.read_bytes()==saved;restart(1);check(False);assert query('apply',token)['settled'];assert checkpoint.read_bytes()==saved;f.checked('구현만 원자 저장·cold·응답 유실 재조회는 선언/최종 파일을 유지하고 중복 거래가 없다')
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:action('recover',token,False);assert checkpoint.read_bytes()==saved;check(False)
   finally:checkpoint.chmod(0o600)
   assert query('recover',token)['unapplied'];f.checked('복구 쓰기 거절도 선언과 삭제 checkpoint를 보존하고 부분 live 복원하지 않는다')
  action('recover',token);check(True);assert not f.state()['retirements'];saved=checkpoint.read_bytes();assert query('recover',token)['settled'];assert action('recover',token)['settled'];assert checkpoint.read_bytes()==saved;restart(2);check(True);assert query('recover',token)['settled'];f.checked('pending 복구·재전송·cold는 원래 provider/본문을 한 번 복원하고 남긴 선언을 재작성하지 않는다')
  p=plan();token=p['token'];action('apply',token);confirm([owner,manifest]);assert {k for k,v in f.original.items() if (f.project/k).read_bytes()!=v}=={'FreeInfo.celem','project.cproj'};f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts};restart(3);check(False);assert f.state()['retirements'][0]['state']=='confirmed';f.checked('명시 compiler Confirm은 구현 등록/연결만 제외하고 함수 선언과 모든 원본 본문 파일을 보관한다')
  action('recover',token);check(True);action('cancel',token);check(False);saved=checkpoint.read_bytes();assert query('cancel',token)['settled'];restart(4);check(False);action('recover',token);check(True);confirm(f.state()['draft']['creationReviewIds']);assert fnpath.read_bytes()==function_original;assert not f.state()['retirements'];f.checked('확정 복구·취소·cold·새 명시 Review/Confirm은 함수 선언을 유지하고 provider·전체 본문 등록만 복원한다')
 print(json.dumps({'checks':f.checks,'mode':mode,'evidence':str(f.case),'actualEngine':True,'renderer':False,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
except Exception:
 try:(f.case/'implementation-retirement-api-failure.json').write_text(json.dumps({'state':f.state(),'checks':f.checks},ensure_ascii=False,indent=2))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
