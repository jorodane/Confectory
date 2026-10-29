"""Original nominal information choices, real owner candidate and compiler Confirm."""
import base64,copy,json,pathlib,shutil,sys,time
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3] if len(sys.argv)>3 else 'normal';detached='view' in sys.argv[4:];owner=f.n+'Mood';leaf='Mood';panel_key='editor-1' if detached else 'declaration'
initial=[dict(id='stable-ready',name='준비 됨',icon='★'),dict(id='stable-done',name='완료')]
text='enum '+owner+' { // 保持する種類原文 😀\r\nvalue Exact=9223372036854775805; value editorEnumProfile="nominal-members-v1";value editorEnumValues='+json.dumps(json.dumps(initial,ensure_ascii=False,separators=(',',':')))+';}'
file=f.project/'Mood.celem';file.write_text(text);f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element Mood enum "Mood.celem";registry Confectory.Build.DotNet'))
snapshot={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file()}
def original():assert all(p.read_bytes()==v for p,v in snapshot.items())
def panel():return f.page.locator('.window[data-key="'+panel_key+'"]')
def pending():return [(k,v) for k,v in f.pending()['schema'] if '|'+owner+'|' in k and v.get('kind')=='enum-values']
def items():return json.loads(pending()[0][1]['text']) if pending() else saved()['enumValues']
def row(id):return panel().locator('[data-enum-value="'+id+'"]')
def saved():
 f.invoke('openEditorView',dict(view='1',id=owner,viewMode='declaration')) if detached else f.invoke('inspectDeclaration',dict(id=owner));s=f.state();return next(r for r in s['editorViews'] if r['view']=='1')['declaration'] if detached else s['declaration']
def open_card():
 f.idle()
 if panel().locator('[data-enum-definition]').is_visible():return
 f.invoke('select',{'id':owner});f.invoke('inspectDeclaration',{'id':owner});f.page.reload();f.idle()
 # Restore the same existing declaration document, or open it through Browser.
 if not f.page.locator('.window[data-key=declaration] [data-enum-definition]').is_visible():
  f.page.locator('#workspace').click(button='right',position={'x':1300,'y':200});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=info]').click();b.locator('[data-browser-control=object-query]').fill(leaf);b.locator('[data-browser-control=object-search]').click();b.locator('[data-object="'+owner+'"]').press('F2');b.locator('[data-close]').first.click()
 if detached:
  f.page.locator('.window[data-key=declaration] [data-declaration-keep]').click();f.idle();f.invoke('select',dict(id=f.n+'Unit'));f.idle()
 expect(panel().locator('[data-enum-definition]')).to_be_visible()
def restart(i):
 f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size(dict(width=1900,height=1400));open_card()
def save():
 panel().locator('[data-declaration-header-action=save]').click();f.idle();assert not pending(),(pending(),f.page.locator('#status').inner_text())
def pick(id,glyph=None,image=False,clear=False):
 row(id).locator('[data-enum-icon]').click();p=f.page.get_by_role('dialog',name=next(i['name'] for i in items() if i['id']==id)+' 종류 아이콘 편집',exact=True);expect(p).to_be_visible()
 if image:
  uri=f.page.evaluate("()=>{const c=document.createElement('canvas');c.width=48;c.height=24;const x=c.getContext('2d');x.fillStyle='#296';x.fillRect(0,0,48,24);return c.toDataURL('image/png')}");p.locator('[type=file]').set_input_files(dict(name='generated-enum.png',mimeType='image/png',buffer=base64.b64decode(uri.split(',')[1])));expect(p.locator('.object-icon-preview img')).to_be_visible()
 elif clear:p.get_by_role('button',name='아이콘 없음',exact=True).click();return
 else:p.locator('[data-icon-choice="'+glyph+'"]').click()
 p.get_by_role('button',name='적용',exact=True).click()
try:
 f.start(0);f.invoke('select',dict(id=owner));f.invoke('saveDraft',{})
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size(dict(width=1900,height=1400));open_card();expect(row('stable-ready').locator('[data-enum-name]')).to_have_value('준비 됨');original()
  panel().locator('[data-enum-add]').click();new_id=next(i['id'] for i in items() if i['id'] not in {i['id'] for i in initial});assert new_id;panel().locator('.object-title-name').click();panel().press('Control+z');assert len(items())==2;panel().press('Control+y');assert any(i['id']==new_id for i in items());f.checked('원본 종류 항목 추가와 private Undo/Redo는 같은 항목 ID를 유지하며 숫자 실행 값을 생성하지 않는다')
  row(new_id).locator('[data-enum-name]').fill('새 항목 😀');restart(1);expect(row(new_id).locator('[data-enum-name]')).to_have_value('새 항목 😀');row(new_id).locator('[data-enum-name]').fill('선택한 종류');row(new_id).locator('[data-enum-name]').press('Tab');pick(new_id,image=True);expect(row(new_id).locator('img')).to_be_visible();pick('stable-ready',clear=True);expect(row('stable-ready').locator('[data-enum-icon]')).to_have_text('◇');original();f.checked('타이핑 중 종류 이름도 cold까지 보존하고 생성 이미지·아이콘 해제는 해당 항목 표시만 바꾼다')
  row(new_id).locator('.enum-value-index').drag_to(row('stable-ready').locator('.enum-value-index'));assert items()[0]['id']==new_id;row('stable-done').locator('[data-enum-remove]').click();assert all(i['id']!='stable-done' for i in items());panel().locator('.object-title-name').click();panel().press('Control+z');assert any(i['id']=='stable-done' for i in items());panel().press('Control+y');assert all(i['id']!='stable-done' for i in items());expected=copy.deepcopy(items());assert all('value' not in item for item in expected);original();f.checked('원본 행 드래그 순서와 미참조 항목 삭제·복원은 생존 ID와 참조 의미를 바꾸지 않는다')
  checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes();held=copy.deepcopy(pending())
  if mode=='invalid':
   row(new_id).locator('[data-enum-name]').fill('준비 됨');row(new_id).locator('[data-enum-name]').press('Tab');invalid=copy.deepcopy(pending());mark=len(f.traffic);panel().locator('[data-declaration-header-action=save]').click();f.idle();assert pending()==invalid and checkpoint.read_bytes()==baseline;assert not any(v.get('invoke',{}).get('input',{}).get('action')=='applySlots' for v in f.traffic[mark:]);original();restart(6);expect(row(new_id).locator('[data-enum-name]')).to_have_value('준비 됨');expect(row(new_id).locator('[data-enum-name]')).to_have_attribute('aria-invalid','true');row(new_id).locator('[data-enum-name]').fill('올바른 종류');row(new_id).locator('[data-enum-name]').press('Tab');expected=copy.deepcopy(items());f.checked('중복 이름은 실제 UI에서 저장 전 거절하고 원문·입력·cold를 보존하며 명시 수정 뒤 저장할 수 있다')
  if mode=='guard':
   assert detached
   current=saved();binding=next(r for r in f.state()['editorViews'] if r['view']=='1')['authorBinding'];base=dict(id=owner,view='1',viewBinding=binding,owner=owner)
   f.invoke('blueprint',dict(base,action='readOwnerEdits',hash=current['textHash'],viewBinding='0'*32),False)
   observed=f.invoke('blueprint',dict(base,action='readOwnerEdits',hash=current['textHash']))['result']['result']
   declaration=dict(id=owner,hash=current['textHash'],changes=[dict(type='enum-values',text=held[0][1]['text']),dict(type='parent',text=f.n+'Unit')])
   f.invoke('blueprint',dict(base,action='applySlots',rows=[],basis=observed['basis'],declaration=declaration),False)
   f.invoke('blueprint',dict(base,action='readOwnerEdits',id=f.n+'Unit',hash=current['textHash']),False)
   assert pending()==held and checkpoint.read_bytes()==baseline;original();f.checked('독립 종류 창의 잘못된 binding·다른 owner·부모/계약 혼입은 전체 거절하며 모든 항목 입력과 원문을 보존한다')
  if mode=='conflict':
   current=saved();f.invoke('editViewDeclaration' if detached else 'editDeclaration',dict(**({'view':'1'} if detached else {}),id=owner,revision=current['revision'],hash=current['textHash'],edit={'action':'properties','values':{'description':'실제 동료 편집'}}));f.invoke('saveEditorView' if detached else 'saveDraft',dict(view='1',id=owner) if detached else {});peer=checkpoint.read_bytes();panel().locator('[data-declaration-header-action=save]').click();f.idle();assert pending()==held and checkpoint.read_bytes()==peer;original();restart(4);assert pending()==held;f.checked('실제 peer source/CAS 충돌은 종류 정의를 부분 적용하지 않고 동료 초안·새 이름/아이콘·cold를 보존한다');f.browser.close();raise SystemExit(0)
  if mode=='project':
   other=f.case/'other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory'));other_bytes=(other/file.name).read_bytes();f.pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(other/'project.cproj');f.start(10);f.page=f.setup();f.page.set_viewport_size(dict(width=1900,height=1400));open_card();assert not pending();pick('stable-ready','🔥');f.pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.project/'project.cproj');f.start(11);f.page=f.setup();f.page.set_viewport_size(dict(width=1900,height=1400));open_card();assert pending()==held and (other/file.name).read_bytes()==other_bytes;f.checked('같은 namespace/종류/항목 ID의 실제 다른 프로젝트 왕복은 항목 목록·이미지·창 입력을 섞지 않는다')
  if mode in ['late','loss']:
   applies=set();queries=set();lost=[];paused={}
   def intercept(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
     action=body.get('input',{}).get('action')
     if action=='applySlots':applies.add(body['requestId'])
     if action=='settledSlots':queries.add(body['requestId'])
    response=route.fetch();payload=response.json()
    if mode=='late' and not paused and any(v.get('ok') and v.get('requestId') in applies for v in payload.get('results',[])):paused.update(route=route,response=response);return
    if mode=='loss':
     for value in payload.get('results',[]):
      if value['requestId'] in applies|queries:rid=value['requestId'];lost.append(rid);value.clear();value.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',intercept);panel().locator('[data-declaration-header-action=save]').click()
   for _ in range(600):
    if paused or any(v in queries for v in lost):break
    f.page.wait_for_timeout(50)
   assert len(applies)==1
   if mode=='late':
    assert paused;row(new_id).locator('[data-enum-name]').fill('응답 중 새 이름');row(new_id).locator('[data-enum-name]').press('Tab');paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',intercept);f.idle();assert next(i for i in items() if i['id']==new_id)['name']=='응답 중 새 이름';expected=copy.deepcopy(items());restart(5);save();f.checked('수락 응답 중 새 종류 이름은 수락한 목록 receipt로만 재기준하며 ID·이미지와 함께 cold·다음 명시 Save까지 보존한다')
   else:
    assert any(v in queries for v in lost) and pending()==held;f.page.unroute_all(behavior='wait');mark=len(f.traffic);restart(5);save();assert not any(v.get('invoke',{}).get('input',{}).get('action')=='applySlots' for v in f.traffic[mark:]);f.checked('종류 수락/조회 응답 유실은 cold receipt로 복구하고 같은 목록을 중복 적용하지 않는다')
  if mode=='cancel':
   panel().locator('[data-declaration-header-action=discard]').click();f.idle();assert not pending() and checkpoint.read_bytes()==baseline;original();restart(2);assert saved()['enumValues']==initial;f.checked('종류 변경 취소·cold는 원래 ID·이름·아이콘과 원본을 유지한다');f.browser.close();raise SystemExit(0)
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:panel().locator('[data-declaration-header-action=save]').click();f.idle();assert pending()==held and checkpoint.read_bytes()==baseline;original()
   finally:checkpoint.chmod(0o600)
   restart(2);assert pending()==held;f.checked('종류 checkpoint 실패는 정의 일부를 저장하지 않고 새 이름·아이콘 입력을 cold까지 보존한다')
  if mode not in ['late','loss']:save()
  current=saved();assert current['enumValues']==expected and current['values']['Exact']==9223372036854775805;original();restart(3);assert saved()['enumValues']==expected;f.checked('종류 전체 정의는 한 owner 후보·최종 CAS로 저장·복구되며 원본·등록·함수·실행 분기는 유지된다')
  panel().locator('[data-declaration-header-action=confirm]').click();r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=120000);r.locator('[data-reject]').click();expect(r).to_be_hidden();original();panel().locator('[data-declaration-header-action=confirm]').click();expect(r).to_be_visible(timeout=120000)
  if r.locator('[data-review-advanced]').count():
   r.locator('[data-review-advanced]').click()
   if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
  expect(r.locator('#confirm')).to_be_enabled(timeout=120000);r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();assert {p.name for p,v in snapshot.items() if p.read_bytes()!=v}=={file.name};assert '// 保持する種類原文 😀\r\n'.encode() in file.read_bytes();assert not f.errors and not f.external;f.checked('Review 취소와 명시 compiler Confirm은 선택한 종류 정의만 반영하고 다른 원문·C#·계약을 보존한다');panel().locator('[data-enum-definition]').screenshot(path=str(f.case/'information-enum.png'));f.browser.close()
except Exception:
 try:(f.case/'enum-failure.json').write_text(json.dumps(dict(state=f.state(),traffic=f.traffic[-80:],errors=f.errors),ensure_ascii=False,indent=2)+'\n')
 except Exception:pass
 try:f.page.screenshot(path=str(f.case/'enum-failure.png'),timeout=5000)
 except Exception:pass
 raise
finally:
 f.stop();(f.case/'information-enum-evidence.json').write_text(json.dumps(dict(checks=f.checks,mode=mode,detached=detached,actualWindows=False,actualMobile=False),ensure_ascii=False,indent=2)+'\n')
print('EVIDENCE',f.case,flush=True)
