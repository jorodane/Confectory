"""Original Browser deletion, retained enum sources and scoped recovery transactions.

The fixture owns all files; no personal images, account, model or project run.
"""
import base64, copy, io, json, pathlib, shutil, sys
from PIL import Image
from playwright.sync_api import sync_playwright, expect
import v536_wide_mixed as f

mode = sys.argv[3] if len(sys.argv) > 3 else 'normal'
detached = 'view' in sys.argv[4:]
owner = f.n+'Mood'; used = f.n+'UsedMood'; manifest = f.n+'ProjectManifest'
buf=io.BytesIO();Image.new('RGBA',(128,128),(31,117,92,170)).save(buf,format='WEBP');image='data:image/webp;base64,'+base64.b64encode(buf.getvalue()).decode()
initial = [dict(id='stable-ready', name='준비 됨', icon='★'), dict(id='stable-done', name='완료 😀',icon=image)]
def declaration(id):
 return 'enum '+id+' { // 保持する種類原文 😀\r\nvalue Exact=9223372036854775805;value editorEnumProfile="nominal-members-v1";value editorEnumValues='+json.dumps(json.dumps(initial,ensure_ascii=False,separators=(',',':')))+';}'
file=f.project/'Mood.celem';file.write_bytes(b"\xef\xbb\xbf"+declaration(owner).encode())
(f.project/'UsedMood.celem').write_bytes(declaration(used).encode())
f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element Mood enum "Mood.celem";element UsedMood enum "UsedMood.celem";registry Confectory.Build.DotNet'))
vitals=f.project/'Vitals.celem';vitals.write_text(vitals.read_text().replace('}', 'field Choice single enum '+used+';value editorInformationDefaults="typed-json-v1";value editorFieldDefault_Choice='+json.dumps(json.dumps('stable-done'))+';}'))
unit=f.project/'Unit.celem';unit.write_text(unit.read_text().replace('{', '{data Choice="stable-ready";',1))
snapshot={p:p.read_bytes() for p in f.project.iterdir() if p.is_file()}
expected=copy.deepcopy(initial);expected[1]['name']='보관할 편집 😀'
panel_key='editor-1' if detached else 'declaration'
def panel():return f.page.locator('.window[data-key="'+panel_key+'"]')
def focus_surface():
 point=panel().evaluate("""el=>{const r=el.getBoundingClientRect();for(let y=r.top+5;y<Math.min(innerHeight-5,r.bottom-5);y+=16)for(let x=r.left+5;x<Math.min(innerWidth-5,r.right-5);x+=16){const at=document.elementFromPoint(x,y);if(at?.closest('.window')===el&&!at.closest('button,input,textarea,select,[data-resize]'))return {x,y};}return null;}""");assert point;f.page.mouse.click(point['x'],point['y'])
def originals(except_names=()):assert all(p.read_bytes()==v for p,v in snapshot.items() if p.name not in except_names)
def invoke(endpoint, **args):return f.invoke(endpoint,args)['result']['result']
def archive():return next((r for r in f.state().get('retirements',[]) if owner in r['ids']),None)
def state_items():
 invoke('select',id=owner);invoke('inspectDeclaration',id=owner);return f.state()['declaration']['enumValues']
def open_browser():
 f.idle();b=f.page.locator('.window[data-key^="browser:project:"]')
 if not b.is_visible():
  f.page.locator('#workspace').click(button='right',position=dict(x=1300,y=200));f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click()
 b.locator('[data-tab=info]').click();b.locator('[data-browser-control=object-query]').fill('Mood');b.locator('[data-browser-control=object-search]').click();f.idle();return b
def open_enum():
 b=open_browser();b.locator('[data-object="'+owner+'"]').press('F2');f.idle()
 if detached:
  rejected=[]
  def reject_admission(route):
   body=route.request.post_data_json
   if not rejected and body.get('op')=='invoke' and body.get('endpoint')=='openEditorView':
    rejected.append(body['requestId']);body['expectedRevision']-=1;route.continue_(post_data=json.dumps(body));return
   route.continue_()
  f.page.route('**/api/request',reject_admission);f.page.locator('.window[data-key=declaration] [data-declaration-keep]').click();f.idle();f.page.unroute('**/api/request',reject_admission);assert rejected

 expect(panel().locator('[data-enum-definition]')).to_be_visible()
def restart(i):
 f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size(dict(width=1900,height=1400));f.idle()
def remove(confirm=True):
 b=open_browser();b.locator('[data-object="'+owner+'"]').click(button='right');f.page.get_by_role('button',name='삭제',exact=True).click();f.idle()
 if confirm:
  expect(f.page.locator('#delete-object')).to_be_visible();f.page.locator('#delete-object').click();f.idle()
  if mode=='loss' and f.page.locator('#delete-object').is_visible():f.page.get_by_role('dialog',name='의미 객체 삭제',exact=True).locator('[data-close]').click()
 return b
def recover():
 b=open_browser();b.locator('[data-browser-control=browser-actions]').click();f.page.get_by_role('button',name='삭제 항목 복구',exact=True).click();f.page.get_by_role('button',name='Mood',exact=True).click();f.idle()
def discard():
 b=open_browser();expect(b.locator('[data-browser-discard]')).to_be_enabled();b.locator('[data-browser-discard]').click();f.idle()
def confirm_api(ids):
 if mode=='normal':
  b=open_browser();expect(b.locator('[data-browser-confirm]')).to_be_enabled();b.locator('[data-browser-confirm]').click();r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=120000)
  assert set(row['id'] for row in f.state()['review']['units'])==set(ids)
  r.locator('[data-reject]').click();expect(r).to_be_hidden();originals(['project.cproj'])
  b=open_browser();b.locator('[data-browser-confirm]').click();expect(r).to_be_visible(timeout=120000)
  if r.locator('[data-review-advanced]').count():
   r.locator('[data-review-advanced]').click()
   if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
  expect(r.locator('#confirm')).to_be_enabled(timeout=120000);r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();return
 invoke('select',id=manifest);invoke('reviewGroup',ids=ids,target='portable');review=f.state()['review'];assert set(r['id'] for r in review['units'])==set(ids)
 result=invoke('confirmGroup',ids=ids,token=review['token']);assert result['sourceConfirmed']
try:
 f.start(0);invoke('select',id=owner);invoke('inspectDeclaration',id=owner);invoke('saveDraft')
 # A real schema field/default and inherited object value retain their IDs.
 blocked=invoke('planBrowserRemoval',ids=[used]);assert blocked['state']=='blocked' and any(r['source']==f.n+'Vitals' and r['target']==used for r in blocked['references']);originals()
 inspect=f.metadata('inspect',text=vitals.read_text());assert any(r['kind']=='enum' and r['target']==used for r in inspect['relations']['edges'])
 for ids in [[f.n+'ProjectManifest'],['External::Mood'],[owner,owner]]:f.invoke('planBrowserRemoval',dict(ids=ids),False)
 f.checked('실제 종류 타입·기본값·상속 값의 참조는 보관을 차단하며 소비자 ID/값·부모·외부 및 모든 원문을 그대로 보존한다')
 plan=invoke('planBrowserRemoval',ids=[f.n+'Wrong']);assert plan.get('mode') is None;invoke('browserRetirement',action='apply',token=plan['token']);invoke('browserRetirement',action='recover',token=plan['token']);invoke('saveDraft');originals();assert not f.state()['retirements'];f.checked('기존 일반 함수 선언의 보관·복구 거래는 기존 경계를 그대로 유지한다')
 if mode=='unedited':
  plan=invoke('planBrowserRemoval',ids=[owner]);invoke('browserRetirement',action='apply',token=plan['token']);confirm_api([manifest]);assert archive()['state']=='confirmed';originals(['project.cproj']);invoke('browserRetirement',action='recover',token=plan['token']);confirm_api([manifest,owner]);assert archive() is None;originals(['project.cproj']);assert file.read_bytes().startswith(b'\xef\xbb\xbf');f.checked('미편집 정의의 확정 보관·복구는 동일 항목/이미지 ID와 BOM/CRLF 원문을 바이트 단위로 유지한다');raise SystemExit(0)
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size(dict(width=1900,height=1400));open_enum()
  panel().locator('[data-enum-value=stable-done] [data-enum-name]').fill(expected[1]['name']);panel().locator('[data-enum-value=stable-done] [data-enum-name]').press('Tab');held=copy.deepcopy(f.pending());before=next(f.project.glob('.confectory/edit-workspaces/*/draft.json')).read_bytes()
  remove(False);assert not f.page.locator('#delete-object').is_visible();assert f.pending()['schema']==held['schema'];originals();f.checked('기본/독립 종류 창의 미적용 항목 이름이 있으면 Browser 삭제를 거절하고 입력을 유지한다')
  # Real private Undo/Redo remains scoped; save the chosen list before archive.
  panel().locator('.object-title-name').click();panel().press('Control+z');assert panel().locator('[data-enum-value=stable-done] [data-enum-name]').input_value()==initial[1]['name'];panel().press('Control+y');assert panel().locator('[data-enum-value=stable-done] [data-enum-name]').input_value()==expected[1]['name']
  panel().locator('[data-declaration-header-action=save]').click();f.idle();assert state_items()==expected;originals()
  checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));saved=checkpoint.read_bytes()
  if mode=='conflict':
   plan=invoke('planBrowserRemoval',ids=[owner]);file.write_bytes(file.read_bytes()+b'\n// actual source race\n');f.invoke('browserRetirement',dict(action='apply',token=plan['token']),False);assert archive() is None and checkpoint.read_bytes()==saved and state_items()==expected;file.write_bytes(snapshot[file]);f.checked('원문 경쟁은 보관 전체를 거절하며 등록·종류 항목 초안·체크포인트를 유지한다');f.browser.close();raise SystemExit(0)
  if mode=='checkpoint-peer':
   plan=invoke('planBrowserRemoval',ids=[owner]);checkpoint.write_bytes(saved+b'\n');peer=checkpoint.read_bytes();f.invoke('browserRetirement',dict(action='apply',token=plan['token']),False);assert archive() is None and checkpoint.read_bytes()==peer and state_items()==expected;originals();f.checked('동료 checkpoint CAS 변경은 보관을 전체 거절하고 동료 바이트와 종류 초안을 보존한다');f.browser.close();raise SystemExit(0)
  if mode=='storage':
   plan=invoke('planBrowserRemoval',ids=[owner]);checkpoint.chmod(0o400)
   try:f.invoke('browserRetirement',dict(action='apply',token=plan['token']),False);assert archive() is None and checkpoint.read_bytes()==saved and state_items()==expected
   finally:checkpoint.chmod(0o600)
   assert state_items()==expected;originals();f.checked('보관 checkpoint 실패는 등록·메모리·초안 전체를 미적용으로 유지한다')
  if mode=='project':
   other=f.case/'other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory'));f.pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(other/'project.cproj');f.start(10);f.page=f.setup();f.page.set_viewport_size(dict(width=1900,height=1400));assert not archive();assert state_items()==initial;f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.project/'project.cproj');f.start(11);f.page=f.setup();f.page.set_viewport_size(dict(width=1900,height=1400));assert state_items()==expected;f.checked('실제 동일 ID 프로젝트 왕복은 종류 목록·보관 대상·창 입력을 섞지 않는다')
  lost=[];calls={};paused={}
  if mode in ['loss','late']:
   def intercept(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke' and body.get('endpoint') in ['browserRetirement','browserArchiveOutcome']:calls[body['requestId']]=(body['endpoint'],body.get('input',{}).get('action'))
    response=route.fetch();payload=response.json()
    if mode=='late' and not paused and any(v.get('ok') and calls.get(v['requestId'])==('browserRetirement','apply') for v in payload.get('results',[])):paused.update(route=route,response=response);return
    if mode=='loss':
     for v in payload.get('results',[]):
      if v['requestId'] in calls:rid=v['requestId'];lost.append(rid);v.clear();v.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',intercept)
  if mode=='late':
   remove(False);f.page.locator('#delete-object').click()
   for _ in range(600):
    if paused:break
    f.page.wait_for_timeout(50)
   assert paused;f.page.get_by_role('dialog',name='의미 객체 삭제',exact=True).locator('[data-close]').click();panel().locator('[data-enum-value=stable-done] [data-enum-name]').fill('보관 응답 중 새 입력');paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',intercept);f.idle();assert any(v.get('kind')=='enum-values' and '보관 응답 중 새 입력' in v['text'] for k,v in f.pending()['schema']);assert archive()['state']=='pending';originals();restart(50);assert any('보관 응답 중 새 입력' in v.get('text','') for k,v in f.pending()['schema']);recover();assert archive() is None and state_items()==expected;f.page.reload();f.idle();expect(panel().locator('[data-enum-value=stable-done] [data-enum-name]')).to_have_value('보관 응답 중 새 입력');focus_surface();panel().locator('[data-declaration-header-action=save]').click();f.idle();assert state_items()[1]['name']=='보관 응답 중 새 입력';originals();f.checked('보관 수락 응답 중 새 종류 입력은 cold와 복구를 통과해 보존되며 다음 명시 Save로 적용한다');f.browser.close();raise SystemExit(0)
  else:remove()
  assert archive()['state']=='pending';token=archive()['token'];f.invoke('select',dict(id=owner),False);originals();assert not open_browser().locator('[data-object="'+owner+'"]').count()
  if mode=='loss':
   assert lost;f.page.unroute_all(behavior='wait');restart(20);assert archive()['state']=='pending';recover();assert archive() is None and state_items()==expected;assert sum(v==('browserRetirement','apply') for v in calls.values())==1;f.checked('보관 응답·조회 유실 후 cold 복구는 저장된 receipt를 확인하고 삭제를 중복 적용하지 않는다');remove();token=archive()['token']
  discard();assert archive() is None and state_items()==expected;originals();f.checked('변경 취소는 보관 전 동일 종류 ID·항목·저장 초안과 등록을 원자적으로 복구한다')
  remove();token=archive()['token'];restart(1);assert archive()['state']=='pending';originals()
  confirm_api([manifest]);assert archive()['state']=='confirmed' and 'Mood enum "Mood.celem"' not in f.manifest.read_text();originals(['project.cproj']);f.checked('명시 compiler Review/Confirm은 등록만 해제하고 BOM/CRLF·정확한 정수·종류 원문과 소비자를 보존한다')
  restart(2);assert archive()['state']=='confirmed'
  if mode=='storage':
   saved=checkpoint.read_bytes();checkpoint.chmod(0o400)
   try:f.invoke('browserRetirement',dict(action='recover',token=token),False);assert archive()['state']=='confirmed' and checkpoint.read_bytes()==saved and owner not in [r['id'] for r in f.state()['units']]
   finally:checkpoint.chmod(0o600)
   f.checked('복구 checkpoint 실패도 보관 기록·등록·원문·기존 초안을 바꾸지 않는다')
  if mode=='retained-conflict':
   saved=checkpoint.read_bytes();peer=file.read_bytes()+b'\n// peer retained source\n';file.write_bytes(peer);f.invoke('browserRetirement',dict(action='recover',token=token),False);assert archive()['state']=='confirmed' and checkpoint.read_bytes()==saved and file.read_bytes()==peer;originals(['project.cproj','Mood.celem']);f.checked('확정 후 보관 원문이 바뀌면 복구를 거절하고 동료 원문·보관 기록·소비자를 보존한다');f.browser.close();raise SystemExit(0)
  if mode=='recover-loss':
   def lose_recover(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke' and body.get('endpoint') in ['browserRetirement','browserArchiveOutcome']:calls[body['requestId']]=(body['endpoint'],body.get('input',{}).get('action'))
    response=route.fetch();payload=response.json()
    for value in payload.get('results',[]):
     if value['requestId'] in calls:rid=value['requestId'];lost.append(rid);value.clear();value.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',lose_recover)
  recover();assert archive()['state']=='restoring' and state_items()==expected
  if mode=='recover-loss':
   assert lost;f.page.unroute_all(behavior='wait');restart(25);assert archive()['state']=='restoring' and state_items()==expected;assert sum(v==('browserRetirement','recover') for v in calls.values())==1;f.checked('복구 수락·조회 응답 유실 후 cold는 동일 복구를 재실행하지 않고 취소·다음 복구로 이어진다')
  f.invoke('reviewGroup',dict(ids=[owner],target='portable'),False);discard();assert archive()['state']=='confirmed';recover();assert archive()['state']=='restoring' and state_items()==expected
  restart(3);assert archive()['state']=='restoring' and state_items()==expected;confirm_api([manifest,owner]);assert archive() is None and state_items()==expected and 'Mood enum "Mood.celem"' in f.manifest.read_text();originals(['Mood.celem','project.cproj']);assert '// 保持する種類原文 😀\r\n'.encode() in file.read_bytes()
  f.checked('확정 보관·복구 취소·재복구·cold는 같은 항목 ID를 보존하며 부분 Review를 거절하고 등록+편집 정의를 함께 Confirm한다')
  assert not f.errors and not f.external,(f.errors,f.external);panel().screenshot(path=str(f.case/'enum-retirement.png')) if panel().is_visible() else open_browser().screenshot(path=str(f.case/'enum-retirement.png'));f.browser.close()
except Exception:
 try:
  (f.case/'enum-retirement-failure.json').write_text(json.dumps(dict(state=f.state(),traffic=f.traffic,errors=f.errors),ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'enum-retirement-failure.png'))
 except Exception:pass
 print('FAILURE EVIDENCE '+str(f.case),flush=True);raise
finally:
 f.stop();(f.case/'enum-retirement-evidence.json').write_text(json.dumps(dict(checks=f.checks,mode=mode,detached=detached,actualWindows=False,actualMobile=False),ensure_ascii=False,indent=2)+'\n')
