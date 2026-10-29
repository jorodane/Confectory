"""Original unsaved information function glyph, actual owner creation and receipt lifecycle."""
import ast,json,pathlib,re,sys,time,zipfile
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3] if len(sys.argv)>3 else 'normal';detached='view' in sys.argv[4:];with_peer='peer' in sys.argv[4:];owner=f.n+'Details';leaf='Details';function_name='OwnGlyph';function_id=None;function_file=None;is_function=True;is_property=is_new=False;new_label='';file=f.project/'Details.celem'
file.write_text(file.read_text().replace('{','{ // preserve information owner comment\nvalue editorIcon="📦";value editorInformationDefaults="typed-json-v1";value editorFieldDefault_Power="9223372036854775805";',1));f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file()}
p=pathlib.Path(__file__).with_name('v536_element_icon_ui.py');node=next(v for v in ast.parse(p.read_text()).body if isinstance(v,ast.FunctionDef) and v.name=='compare');exec(compile(ast.Module(body=[node],type_ignores=[]),str(p),'exec'))
def surface():return f.page.locator('.window[data-key="'+('editor-1' if detached else 'schema')+'"]')
f.owner=surface
def schema():
 s=f.state();return next(row['schema'] for row in s['editorViews'] if row['view']=='1') if detached else s['schema']
def row():return surface().locator('[data-inline-method="'+function_id+'"]')
def icon():return row().locator('[data-function-icon]')
def pending():return [(k,v) for k,v in f.pending()['schema'] if '|'+owner+('|view:1|element|' if detached else '|element|') in k]
def popup():
 icon().click();p=f.page.get_by_role('dialog',name=function_name+' 아이콘 편집',exact=True);expect(p).to_be_visible();return p
def open_card(target=owner,view=detached):
 f.page.locator('#workspace').click(button='right',position={'x':80,'y':100});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab="'+('info' if target==owner else 'concept')+'"]').click();b.locator('[data-browser-control=object-query]').fill(target.split('::')[-1]);b.locator('[data-browser-control=object-search]').click();item=b.locator('[data-object="'+target+'"]');expect(item).to_be_visible();item.click(button='right');f.page.locator('.context-menu').get_by_role('button',name='새 창으로 열기' if view else '상세 편집',exact=True).click();expect(f.page.locator('.window[data-key="'+('editor-1' if view else 'schema')+'"] .object-title-name')).to_have_text(target.split('::')[-1]);b.locator('[data-close]').first.click();f.idle()
def saved():
 for _ in range(600):
  if not pending() and not [v for _,v in f.pending()['blueprint'] if v.get('kind') in ['owner-attempt','view-owner-attempt'] and v.get('owner')==owner]:f.idle();return
  if surface().locator('[data-element-error]').inner_text():raise AssertionError(surface().locator('[data-element-error]').inner_text())
  f.page.wait_for_timeout(100)
 raise AssertionError((pending(),f.pending()))
def save(ok=True):
 surface().locator('[data-element-action=save]').click()
 if ok:saved()
 else:expect(surface().locator('[data-element-error]')).not_to_have_text('',timeout=60000);f.idle();assert pending()
def restart(i):
 f.pending();f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(i);f.page=f.setup();expect(surface().locator('.object-title-name')).to_have_text(leaf,timeout=60000);f.idle()
 if with_peer:expect(f.page.locator('.window[data-key=schema]').get_by_label('Power 기본값',exact=True)).to_have_value('9223372036854775804')
def review():
 surface().locator('[data-element-action=confirm]').click();f.page.wait_for_function('()=>document.querySelector("#review-creation")||[...document.querySelectorAll(".window[data-key=review]")].some(e=>!e.hidden&&e.getClientRects().length)')
 if f.page.locator('#review-creation').count():f.page.locator('#review-creation').click()
 r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=120000);return r
def original():
 f.originals();assert not function_file or not function_file.exists();assert not (f.project/'elements').exists() or not list((f.project/'elements').glob('Details_Function_*.celem'))
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup()
  if with_peer:open_card(f.n+'Target1',False);f.page.locator('.window[data-key=schema]').get_by_label('Power 기본값',exact=True).fill('9223372036854775804')
  open_card();surface().locator('[data-function-add]').click();created=next(v for _,v in pending() if v['kind']=='function-add');function_id=created['id'];assert re.fullmatch(re.escape(owner+'_Function_')+'[0-9a-f]{32}',function_id);function_file=f.project/'elements'/(function_id.split('::')[-1]+'.celem');row().locator('[data-inline-name]').fill(function_name);row().locator('[data-inline-description]').fill('생성 함수 설명');base=pending();default=icon().inner_text();p=popup();compare(p);p.locator('[data-icon-choice="🔥"]').click();p.locator('[data-cancel]').click();assert pending()==base;expect(icon()).to_have_text(default);p=popup();p.get_by_label('기호나 이모지',exact=True).fill('ab');p.get_by_role('button',name='적용',exact=True).click();expect(p).to_be_visible();p.get_by_label('기호나 이모지',exact=True).press('Escape');assert pending()==base;original();f.checked('새 함수 카드의 원래 팝오버 취소·Escape·부적합 glyph는 생성 ID·이름·설명·원문을 보존한다')
  p=popup();p.locator('[data-icon-choice="★"]').click();p.get_by_role('button',name='적용',exact=True).click();icon().focus();f.page.keyboard.press('Control+z');expect(icon()).to_have_text(default);assert pending()==base;f.page.keyboard.press('Control+y');expect(icon()).to_have_text('★');p=popup();p.locator('[data-icon-choice="🛡️"]').click();p.get_by_role('button',name='적용',exact=True).click();row().locator('[data-inline-name]').fill('임시 이름');row().locator('[data-inline-name]').fill(function_name);assert next(v for _,v in pending() if v['kind']=='function-add')['icon']=='🛡️';surface().locator('.object-title-description').fill('새 함수와 아이콘 원자 저장');held=pending();assert len(held)==2;assert checkpoint.read_bytes()==before;original();restart(1);assert pending()==held;expect(icon()).to_have_text('🛡️');f.checked('생성 전 glyph Undo/Redo·이름 재편집·설명·cold는 같은 미확정 함수 ID와 64비트 기본값·원본을 보존한다')
  if mode=='cancel':
   surface().locator('[data-element-action=discard]').click();saved();expect(row()).to_have_count(0);restart(2);assert not pending() and checkpoint.read_bytes()==before;original();f.checked('새 함수 생성 취소와 cold는 미확정 아이콘/정보 설명만 취소하며 등록·함수 파일·부모·다른 입력을 생성/삭제하지 않는다')
  elif mode=='conflict':
   peer=file.read_bytes()+b'\n// fixture source race\n';file.write_bytes(peer);f.original[file.name]=peer;save(False);assert pending()==held and checkpoint.read_bytes()==before;original();restart(2);save(False);assert pending()==held and checkpoint.read_bytes()==before;original();f.checked('실제 소유 정보 변경은 새 함수·등록·glyph 모두 미적용이며 cold 재시도에도 원래 기준과 입력을 보존한다')
  else:
   if mode=='storage':
    checkpoint.chmod(0o400)
    try:save(False);assert pending()==held and checkpoint.read_bytes()==before;original()
    finally:checkpoint.chmod(0o600)
    restart(2);assert pending()==held;f.checked('checkpoint 쓰기 실패는 새 함수·등록·glyph의 부분 생성 없이 원문·입력·저장 기록을 cold까지 보존한다')
   if mode=='loss':
    applies=set();queries=set();lost=[]
    def intercept(route):
     body=route.request.post_data_json
     if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
      action=body.get('input',{}).get('action')
      if action=='applySlots':applies.add(body['requestId'])
      elif applies and action=='settledSlots':queries.add(body['requestId'])
     response=route.fetch();payload=response.json()
     for value in payload.get('results',[]):
      if value['requestId'] in applies|queries:rid=value['requestId'];lost.append(rid);value.clear();value.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
     route.fulfill(response=response,json=payload)
    f.page.route('**/api/request',intercept);surface().locator('[data-element-action=save]').click()
    for _ in range(600):
     if applies and any(v in queries for v in lost):break
     f.page.wait_for_timeout(50)
    assert len(applies)==1 and any(v in queries for v in lost) and pending()==held;f.page.unroute_all(behavior='wait');mark=len(f.traffic);restart(2);save();assert not any(v.get('invoke',{}).get('input',{}).get('action')=='applySlots' for v in f.traffic[mark:]);f.checked('생성 적용·조회 응답 유실은 cold 뒤 원래 receipt 조회로 회수하고 새 함수/등록을 중복 생성하지 않는다')
   elif mode=='late':
    ids=set();paused={}
    def hold(route):
     body=route.request.post_data_json
     if body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and body.get('input',{}).get('action')=='applySlots':ids.add(body['requestId'])
     response=route.fetch();payload=response.json()
     if not paused and any(value.get('ok') and value.get('requestId') in ids for value in payload.get('results',[])):paused.update(route=route,response=response);return
     route.fulfill(response=response)
    f.page.route('**/api/request',hold);surface().locator('[data-element-action=save]').click()
    for _ in range(600):
     if paused:break
     f.page.wait_for_timeout(50)
    assert paused and len(ids)==1;p=popup();p.locator('[data-icon-choice="👑"]').click();p.get_by_role('button',name='적용',exact=True).click();paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',hold);f.idle()
    for _ in range(600):
     current=pending()
     if len(current)==1 and current[0][1].get('copySavedBasis'):break
     f.page.wait_for_timeout(50)
    current=pending()[0][1];assert current['kind']=='function-edit' and current['id']==function_id and current['icon']=='👑' and current['copySavedBasis']['acceptedIcon']=='🛡️';original();restart(2);expect(icon()).to_have_text('👑');save();f.checked('생성 응답 대기의 늦은 glyph는 생성 intent를 같은 소유 함수의 edit로 receipt 재결합하고 cold 뒤 명시적 Save만 반영한다')
   else:save()
   expected='👑' if mode=='late' else '🛡️';function=next(v for v in schema()['ownFunctions'] if v['id']==function_id);assert function['writable'] and function['icon']==expected and function['name']==function_name and function['description']=='생성 함수 설명';assert function['signature']['Args']==[] and function['signature']['return']=='void';assert len([v for v in schema()['ownFunctions'] if v['id']==function_id])==1;assert next(v for v in schema()['rows'] if v['path']==['Power'])['valueJson']=='9223372036854775805';original();restart(3);assert not pending();expect(icon()).to_have_text(expected);f.checked('한 후보/CAS Save와 cold는 정보·등록·단 하나의 함수 ID·glyph·원계약·정확한 기본값을 함께 보존한다')
   if with_peer:
    surface().locator('[data-element-action=confirm]').click();group=f.page.get_by_role('dialog',name='관련 변경 검토',exact=True);expect(group).to_be_visible();group.locator('#review-creation').click();f.idle();expect(f.page.locator('#status')).to_contain_text('미적용 입력');assert any('|'+f.n+'Target1|' in k and v.get('text')=='9223372036854775804' for k,v in f.pending()['schema']);original();group.get_by_role('button',name='닫기',exact=True).click();peer=f.page.locator('.window[data-key=schema]');peer.locator(':scope>.window-title').click(position={'x':30,'y':25});peer.locator('[data-element-action=discard]').click();f.idle();expect(peer.get_by_label('Power 기본값',exact=True)).to_have_value('1');f.checked('독립 창의 새 함수 Review는 다른 창 exact64 입력을 보존해 거절하고 그 창의 명시 취소 뒤에만 진행한다')
   r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();original();r=review()
   if r.locator('[data-review-advanced]').count():
    r.locator('[data-review-advanced]').click()
    if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
   r.locator('#confirm').click();expect(r).to_have_count(0,timeout=120000);f.idle();assert function_file.is_file();assert {k for k,v in f.original.items() if (f.project/k).read_bytes()!=v}=={file.name,f.manifest.name};assert {str(p.relative_to(f.project)) for p in f.project.rglob('*.celem') if str(p.relative_to(f.project)) not in f.original}=={str(function_file.relative_to(f.project))};parsed=f.metadata('inspect',text=function_file.read_text());assert parsed['values']['editorIcon']==expected and parsed['description']=='생성 함수 설명';assert '9223372036854775805' in file.read_text() and 'preserve information owner comment' in file.read_text();f.checked('Review 취소 후 명시적 compiler Confirm만 정보·등록·새 함수 glyph를 전체 반영하며 원본·본문·부모·정확한 값을 보존한다')
   if with_peer:expect(f.page.locator('.window[data-key=schema] .object-title-name')).to_have_text('Target1');f.checked('독립 창 생성 Confirm은 기본 창의 다른 문서·선택·원문 문맥을 유지한다')
  assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except Exception:
 try:(f.case/'new-function-glyph-failure.json').write_text(json.dumps({'state':f.state(),'traffic':f.traffic[-80:],'errors':f.errors},ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'new-function-glyph-failure.png'))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'newFunction':function_id,'detached':detached,'peer':with_peer,'nativeWindows':False,'actualMobile':False,'projectRun':False,'accountOrInference':False},ensure_ascii=False))
