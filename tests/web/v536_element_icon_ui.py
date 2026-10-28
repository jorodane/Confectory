"""Original element glyph popover and actual atomic owner save; isolated fixture only."""
import json,pathlib,re,sys,time,zipfile
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f

mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
kind=sys.argv[4] if len(sys.argv)>4 else 'schema'
detached='view' in sys.argv[5:]
with_peer='peer' in sys.argv[5:]
is_function='function' in sys.argv[5:]
function_name='OwnGlyph'
function_id=f.n+'Details_Function_'+'1'*32
is_new_object='new-object-property' in sys.argv[5:]
is_object_property='object-property' in sys.argv[5:] or is_new_object
is_new='new-property' in sys.argv[5:] or is_new_object
is_property='property' in sys.argv[5:] or is_new or is_object_property
new_native=None
new_draft_key=None
new_label='IconPower' if is_new_object else '아이콘 새 속성'
owner=f.n+('Details' if kind=='schema' else 'Target2' if is_object_property else 'Slime')
leaf=owner.split('::')[-1];file=f.project/(leaf+'.celem')
if is_property:
 assert kind==('object' if is_object_property else 'schema')
 (f.project/'IconBase.celem').write_text('schema '+f.n+'IconBase {field Inherited single general long;value editorFieldIcon_Inherited="🌿";}')
 f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element IconBase schema "IconBase.celem";registry Confectory.Build.DotNet'))
 if is_object_property:
  (f.project/'IconParent.celem').write_text('object '+f.n+'IconParent {use schema '+f.n+'IconBase;data Inherited=7;}')
  f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element IconParent object "IconParent.celem";registry Confectory.Build.DotNet'))
  file.write_text(file.read_text().replace(' {',' extends '+f.n+'IconParent {',1).replace('{','{ // object property icon fixture preserve\nvalue editorIcon="📦";\n',1).replace('data Power=2;','data Power=9223372036854775804;'))
 else:file.write_text(file.read_text().replace(' {',' extends '+f.n+'IconBase {',1).replace('{','{ // property icon fixture preserve\nvalue editorIcon="📦";\n',1))
 f.original={str(path.relative_to(f.project)):path.read_bytes() for path in f.project.rglob('*') if path.is_file()}
icon_file=f.project/'Details.celem' if is_object_property and not is_new_object else file
if is_function:
 (f.project/'elements').mkdir(exist_ok=True)
 function_file=f.project/'elements'/(function_id.split('::')[-1]+'.celem')
 function_file.write_text('function '+function_id+' (long amount,out bool active) -> long { // preserved function comment\nvalue editorName="OwnGlyph";description "함수 원래 설명";provide '+function_id+' with '+f.n+'GlyphBody;}')
 (f.project/'GlyphBody.celem').write_text('implementation '+f.n+'GlyphBody for '+function_id+' (long amount,out bool active) -> long {body common "Glyph.csbody";}')
 (f.project/'Glyph.csbody').write_text('active=true;return amount+1;')
 file.write_text(file.read_text().replace('{','{contain function '+function_id+';value editorIcon="📦";',1))
 caller=f.project/'MainBody.celem';caller.write_text(caller.read_text().replace('{','{import '+function_id+' as GlyphCall (long,out bool) -> long;',1))
 f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element '+function_id.split('::')[-1]+' function "elements/'+function_file.name+'";element GlyphBody implementation "GlyphBody.celem";registry Confectory.Build.DotNet'))
 f.original={str(path.relative_to(f.project)):path.read_bytes() for path in f.project.rglob('*') if path.is_file()};icon_file=function_file
f.original[file.name]=file.read_bytes()
def surface():return f.page.locator('.window[data-key="'+('editor-1' if detached else 'schema')+'"]')
f.owner=surface
def pending():return [(k,v) for k,v in f.pending()['schema'] if '|'+owner+('|view:1|element|' if detached else '|element|') in k]
def own_schema():
 s=f.state();return next(r['schema'] for r in s['editorViews'] if r['view']=='1') if detached else s['schema']
def open_card(target=owner,view=detached):
 f.page.locator('#workspace').click(button='right',position={'x':80,'y':100});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab="'+('info' if target==f.n+'Details' else 'concept')+'"]').click();b.locator('[data-browser-control="object-query"]').fill(target.split('::')[-1]);b.locator('[data-browser-control="object-search"]').click();row=b.locator('[data-object="'+target+'"]');expect(row).to_be_visible();row.click(button='right');f.page.locator('.context-menu').get_by_role('button',name='새 창으로 열기' if view else '상세 편집',exact=True).click();expect(f.page.locator('.window[data-key="'+('editor-1' if view else 'schema')+'"] .object-title-name')).to_have_text(target.split('::')[-1]);b.locator('[data-close]').first.click();f.idle()
def assert_confirmed_sources():
 changed={k for k,v in f.original.items() if (f.project/k).read_bytes()!=v}
 if is_new_object:
  assert changed=={file.name,f.manifest.name},changed
  added={str(p.relative_to(f.project)) for p in f.project.rglob('*.celem') if str(p.relative_to(f.project)) not in f.original};assert added=={str(icon_file.relative_to(f.project))},added
  assert icon_file.is_file() and 'field '+new_native+' single general long;' in icon_file.read_text() and re.search(r'\bdata\s+'+re.escape(new_native)+r'\s*=\s*9223372036854775804;',file.read_text())
  assert str(icon_file.relative_to(f.project)) in f.manifest.read_text();assert len(list((f.project/'elements').glob(leaf+'_Properties_*.celem')))==1
  f.checked('최종 Confirm만 객체·등록·단 하나의 새 소유 속성 스키마를 함께 반영하고 재시도에서 중복 생성하지 않는다')
 elif is_function:assert changed=={file.name,str(icon_file.relative_to(f.project))},changed
 else:assert (file.name in changed and changed<={file.name,icon_file.name}) if is_object_property and mode=='clear' else changed==({file.name,icon_file.name} if is_object_property else {file.name})
def new_row():
 selector='[data-property-path='+json.dumps(json.dumps([new_native],separators=(',',':')))+']';draft=surface().locator('[data-definition-key='+json.dumps(new_draft_key)+']') if new_draft_key else surface().locator('[data-definition-key]'+selector);return draft if draft.count() else surface().locator(selector)
def function_row():return surface().locator('[data-inline-method='+json.dumps(function_id)+']')
def icon():return function_row().locator('[data-function-icon]') if is_function else new_row().locator('[data-property-icon]') if is_new else surface().get_by_label('Power 속성 아이콘 편집',exact=True) if is_property else surface().locator('.object-icon-control>.obj-icon')
def popup():
 (icon() if is_property or is_function else surface().locator('.object-icon-edit')).click();p=f.page.get_by_role('dialog',name=(function_name if is_function else new_label if is_new else 'Power' if is_property else leaf)+' 아이콘 편집',exact=True);expect(p).to_be_visible();return p
def saved():
 for _ in range(300):
  if not pending() and not [v for _,v in f.pending()['blueprint'] if v.get('kind') in ['owner-attempt','view-owner-attempt'] and v.get('owner')==owner]:f.idle();return
  f.page.wait_for_timeout(100)
 raise AssertionError((surface().locator('[data-element-error]').all_text_contents(),f.pending()))
def restart(i):
 f.pending();f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(i);f.page=f.setup();expect(surface().locator('.object-title-name')).to_have_text(leaf,timeout=60000);f.idle()
 if with_peer:expect(f.page.locator('.window[data-key=schema]').get_by_label('Power 기본값',exact=True)).to_have_value('9223372036854775804')
def review():
 surface().locator('[data-element-action=confirm]').click();r=f.page.locator('.window[data-key=review]');f.page.wait_for_function('()=>document.querySelector("#review-creation")||[...document.querySelectorAll(".window[data-key=review]")].some(e=>!e.hidden&&e.getClientRects().length)')
 if f.page.locator('#review-creation').count():f.page.locator('#review-creation').click()
 expect(r).to_be_visible();return r
def compare(p):
 with zipfile.ZipFile(pathlib.Path(__file__).resolve().parents[2]/'reference/site-ui/Confectory-Editor-Prototype-v536.zip') as z:
  app='Confectory-v536/dist/app.js';source=z.read(app).decode();css=re.sub(r'@import\s+url\([^)]*\)\s*;','',z.read('Confectory-v536/dist/style.css').decode())
 a=source.index('function editIconValue(');b=source.index('\nfunction ',a+1);function=source[a:b]
 selectors=[':scope','form','.object-icon-preview','.object-icon-options','[data-icon-choice="🛡️"]','#object-icon-input','.object-icon-upload','small','.actions','[type=submit]']
 measure="""(el,selectors)=>{const b=el.getBoundingClientRect();return selectors.map(s=>{const e=s===':scope'?el:el.querySelector(s),r=e.getBoundingClientRect(),c=getComputedStyle(e);return {selector:s,x:r.x-b.x,y:r.y-b.y,width:r.width,height:r.height,font:c.font,padding:c.padding,background:c.backgroundColor};});}"""
 actual=p.evaluate(measure,selectors);anchor=(icon() if is_property or is_function else surface().locator('.object-icon-edit')).bounding_box();original=f.browser.new_page(viewport=f.page.viewport_size);original.route('**/*',lambda r:r.abort());original.set_content('<!doctype html><html lang="ko"><head><style>'+css+'</style></head><body><button id="anchor" style="position:fixed;box-sizing:border-box;left:'+str(anchor['x'])+'px;top:'+str(anchor['y'])+'px;width:'+str(anchor['width'])+'px;height:'+str(anchor['height'])+'px">편집</button></body></html>')
 original.add_script_tag(content="const esc=s=>String(s??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('\"','&quot;');let closeObjectIconPopover=null;const profileIconMarkup=esc;"+function+"\neditIconValue({name:'"+(function_name if is_function else new_label if is_new else 'Power' if is_property else leaf)+"',icon:'"+('⚙' if is_function else '' if is_property else '▤')+"'},document.querySelector('#anchor'),()=>{throw Error('visual oracle cannot write')},"+('true' if is_property else 'false')+");")
 expected=original.locator('.object-icon-popover').evaluate(measure,selectors);assert p.bounding_box()==original.locator('.object-icon-popover').bounding_box();original.screenshot(path=str(f.case/'icon-original.png'));f.page.screenshot(path=str(f.case/'icon-engine.png'));original.close();(f.case/'icon-geometry.json').write_text(json.dumps({'original':expected,'actual':actual},ensure_ascii=False,indent=2));assert expected==actual,{'expected':expected,'actual':actual}
 f.checked('원본 ZIP의 실제 팝오버 10영역과 같은 치수·위치·글꼴·패딩·배경을 사용한다(이미지 지원 범위는 별도 수용 기록)')
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{})
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup()
  if with_peer:open_card(f.n+'Target1',False);f.page.locator('.window[data-key=schema]').get_by_label('Power 기본값',exact=True).fill('9223372036854775804')
  open_card()
  if is_new:
   surface().locator('[data-schema-add]').click();draft=surface().locator('[data-definition-key]').last;new_draft_key=draft.get_attribute('data-definition-key');new_native=next(v.get('nativeKey',new_label) for _,v in pending() if v['kind']=='definition');draft.locator('[data-property-icon]').click();p=f.page.get_by_role('dialog',name='Property 아이콘 편집',exact=True);p.locator('[data-icon-choice="★"]').click();p.get_by_role('button',name='적용',exact=True).click();draft.locator('[data-property-name]').fill(new_label);draft.get_by_label('새 속성 기본값',exact=True).fill('문자 초안');assert next(v for _,v in pending() if v['kind']=='definition')['icon']=='★';draft.get_by_label('새 속성 기본값',exact=True).fill('');p=popup();p.get_by_role('button',name='아이콘 없음',exact=True).click();draft.locator('[data-property-type]').click();f.page.get_by_role('dialog',name='속성 타입 선택',exact=True).locator('[data-type=long]').click();new_row().get_by_label(new_label+' 기본값',exact=True).fill('9223372036854775804');f.checked('새 미저장 속성의 이름·기본값·타입 편집은 선택한 glyph와 nativeKey를 보존하고 명시 해제는 그 초안 안에 남긴다')
  checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();default=icon().inner_text();expected_glyph='🛡️';base_pending=pending()
  p=popup();compare(p)
  if with_peer:
   button=f.page.locator('.window[data-key=schema] .object-icon-edit');button.focus();button.press('Enter');expect(f.page.locator('.object-icon-popover')).to_have_count(1);peer_popup=f.page.get_by_role('dialog',name='Target1 아이콘 편집',exact=True);expect(peer_popup).to_be_visible();peer_popup.locator('[data-cancel]').click();p=popup();f.checked('다른 창의 키보드 아이콘 진입은 원본처럼 이전 팝오버 하나만 닫고 각 창의 입력을 보존한다')
  (expect(p.locator('.object-icon-upload')).to_be_enabled() if kind=='schema' and not is_property and not is_function else expect(p.locator('.object-icon-upload')).to_be_disabled());p.locator('[data-icon-choice="🔥"]').click();p.locator('[data-cancel]').click();assert pending()==base_pending;expect(icon()).to_have_text(default);expect(icon() if is_property or is_function else surface().locator('.object-icon-edit')).to_be_focused();p=popup();p.get_by_label('기호나 이모지',exact=True).fill('ab');p.get_by_role('button',name='적용',exact=True).click();expect(p).to_be_visible();assert pending()==base_pending;control=p.get_by_label('기호나 이모지',exact=True);control.fill('★');control.press('End');f.page.keyboard.insert_text('x');control.press('Control+z');expect(control).to_have_value('★');control.press('Escape');expect(p).to_have_count(0);f.originals();f.checked('선택 후 닫기·Escape·문자 입력 Undo·잘못된 복수 문자 적용은 원본·초안·입력을 바꾸지 않으며 초점을 복원한다')
  if is_function:
   p=popup();p.locator('[data-icon-choice="★"]').click();p.get_by_role('button',name='적용',exact=True).click();icon().focus();f.page.keyboard.press('Control+z');expect(icon()).to_have_text(default);assert pending()==base_pending;f.checked('함수 카드의 기존 Undo는 glyph 초안만 되돌리고 원래 서명·함수 identity·다른 입력을 보존한다')
  if is_property:
   assert surface().locator('[data-property-id="Inherited"] [data-property-icon]').count()==0;expect(surface().locator('[data-property-id="Inherited"] .property-label-icon')).to_have_text('🌿')
   p=popup();p.locator('[data-icon-choice="★"]').click();p.get_by_role('button',name='적용',exact=True).click();icon().focus();f.page.keyboard.press('Control+z');expect(icon()).to_have_text('◇');assert pending()==base_pending;p=popup();p.locator('[data-icon-choice="★"]').click();p.get_by_role('button',name='적용',exact=True).click();p=popup();p.get_by_role('button',name='아이콘 없음',exact=True).click();expect(icon()).to_have_text('◇');icon().focus();f.page.keyboard.press('Control+z');expect(icon()).to_have_text('★');f.checked('기존 직접 정보 속성의 기호 적용/아이콘 없음/Undo는 stable field와 다른 입력을 유지하며 상속 아이콘은 읽기 전용으로 표시한다')
  p=popup();p.locator('[data-icon-choice="🛡️"]').click();p.get_by_role('button',name='적용',exact=True).click();expect(icon()).to_have_text('🛡️')
  if is_new:
   new_row().get_by_label(new_label+' 기본값',exact=True).fill('9223372036854775805');new_row().get_by_label(new_label+' 기본값',exact=True).fill('9223372036854775804');assert next(v for _,v in pending() if v['kind']=='definition')['icon']=='🛡️'
  if is_function:
   function_row().locator('[data-inline-name]').fill('다른 이름');function_row().locator('[data-inline-name]').fill(function_name);assert next(v for _,v in pending() if v['kind']=='function-edit')['icon']=='🛡️'
  surface().locator('.object-title-description').fill('아이콘과 설명 원자 저장');held=pending();assert len(held)==2;glyph=next(v for _,v in held if v['kind']==('function-edit' if is_function else 'definition' if is_new else 'schema-icon' if is_property else 'icon'));assert glyph['icon' if is_new or is_function else 'text']=='🛡️';assert checkpoint.read_bytes()==before;f.originals();restart(1);assert pending()==held;expect(icon()).to_have_text('🛡️');f.checked('한 grapheme 이모지 적용과 설명은 저장 전 같은 owner 입력으로 보관되고 프로세스 재시작에 원래 기준과 함께 복원한다')
  if mode=='cancel':
   surface().locator('[data-element-action=discard]').click();saved();expect(new_row()).to_have_count(0) if is_new else expect(icon()).to_have_text(default);restart(2);assert not pending() and checkpoint.read_bytes()==before;f.originals();f.checked('명시적 변경 취소/cold는 아이콘·설명만 취소하고 부모·참조·정확한 기존 값과 원본을 보존한다')
  elif mode=='conflict':
   peer=icon_file.read_bytes()+b'\n// fixture concurrent source\n';icon_file.write_bytes(peer);f.original[str(icon_file.relative_to(f.project))]=peer;f.rejected_save();assert pending()==held and checkpoint.read_bytes()==before;f.originals();restart(2);assert pending()==held;f.rejected_save();assert pending()==held and checkpoint.read_bytes()==before;f.originals();f.checked('실제 source 변경은 후보 전부 미적용·입력 보존이고 재시작 재시도에도 원래 기준을 자동 교체하지 않는다')
  else:
   if mode=='storage':
    checkpoint.chmod(0o400)
    try:f.rejected_save();assert pending()==held and checkpoint.read_bytes()==before;f.originals()
    finally:checkpoint.chmod(0o600)
    restart(2);assert pending()==held;f.checked('실제 checkpoint 쓰기 실패는 아이콘만/설명만 부분 적용하지 않고 cold 입력을 보존한다')
   if mode=='loss':
    applies=set();queries=set();lost=[]
    def intercept(route):
     body=route.request.post_data_json
     if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
      action=body.get('input',{}).get('action')
      if action=='applySlots':applies.add(body['requestId'])
      elif applies and action=='settledSlots':queries.add(body['requestId'])
     response=route.fetch();payload=response.json()
     for row in payload.get('results',[]):
      if row['requestId'] in applies|queries:rid=row['requestId'];lost.append(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
     route.fulfill(response=response,json=payload)
    f.page.route('**/api/request',intercept);surface().locator('[data-element-action=save]').click()
    for _ in range(300):
     if applies and any(r in queries for r in lost):break
     f.page.wait_for_timeout(100)
    assert len(applies)==1 and any(r in queries for r in lost) and pending()==held;f.page.unroute_all(behavior='wait');mark=len(f.traffic);restart(2);surface().locator('[data-element-action=save]').click();saved();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='applySlots' for r in f.traffic[mark:]);f.checked('적용·조회 응답 유실은 재시작 뒤 receipt 조회로만 회수하고 동일 아이콘/설명을 중복 적용하지 않는다')
   elif mode=='late':
    ids=set();paused={}
    def hold(route):
     body=route.request.post_data_json
     if body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and body.get('input',{}).get('action')=='applySlots':ids.add(body['requestId'])
     response=route.fetch();payload=response.json()
     if not paused and any(row.get('ok') and row.get('requestId') in ids for row in payload.get('results',[])):paused.update(route=route,response=response);return
     route.fulfill(response=response)
    f.page.route('**/api/request',hold);surface().locator('[data-element-action=save]').click()
    for _ in range(300):
     if paused:break
     f.page.wait_for_timeout(100)
    assert paused and len(ids)==1;p=popup();p.locator('[data-icon-choice="👑"]').click();p.get_by_role('button',name='적용',exact=True).click();paused['route'].fulfill(response=paused['response']);f.idle();f.page.unroute('**/api/request',hold)
    for _ in range(300):
     if len(pending())==1 and pending()[0][1].get('copySavedBasis'):break
     f.page.wait_for_timeout(100)
    assert len(pending())==1 and pending()[0][1]['icon' if is_function else 'text']=='👑' and pending()[0][1]['copySavedBasis']['acceptedIcon' if is_function else 'accepted']=='🛡️';restart(2);expect(icon()).to_have_text('👑');surface().locator('[data-element-action=save]').click();saved();expected_glyph='👑';f.checked('성공 응답 대기 중 새 glyph는 채택/폐기하지 않고 receipt 기준으로 보존하며 cold 뒤 새 명시 저장만 반영한다')
   else:surface().locator('[data-element-action=save]').click();saved()
   assert (next(row for row in own_schema()['ownFunctions'] if row['id']==function_id).get('icon') if is_function else next(row for row in own_schema()['rows'] if row['path']==([new_native] if is_new else ['Power'])).get('icon') if is_property else own_schema()['values']['editorIcon'])==expected_glyph and own_schema()['description']=='아이콘과 설명 원자 저장';f.originals();restart(3);expect(icon()).to_have_text(expected_glyph);assert not pending();f.checked('단일 owner 후보/CAS 임시 저장과 cold는 glyph·설명을 함께 저장하며 원본 파일과 실행 권한은 유지한다')
   if is_function:
    current=next(row for row in own_schema()['ownFunctions'] if row['id']==function_id);assert current['signature']['Args'][0]['Name']=='amount' and current['signature']['Args'][1]['Mode']=='out' and current['signature'].get('return',current['signature'].get('Return'))=='long';assert own_schema()['values']['editorIcon']=='📦';f.checked('연결된 함수 glyph와 정보 설명의 Save/cold는 서명·typed import·구현 C#·부모·기존 값을 보존한다')
   if is_new_object:
    row=next(row for row in own_schema()['rows'] if row['path']==[new_native]);assert row['schemaOrigin'].startswith(owner+'_Properties_') and row['fieldSource']==owner;icon_file=f.project/'elements'/(row['schemaOrigin'].split('::')[-1]+'.celem');assert not icon_file.exists();f.checked('새 객체 속성의 등록·소유 스키마·값·glyph는 확정 전 하나의 생성 후보이며 원본 파일은 생성하지 않는다')
   if is_new:
    row=next(row for row in own_schema()['rows'] if row['path']==[new_native]);assert row['type']=='long' and row['displayName']==new_label and row['valueJson']=='9223372036854775804';f.checked('새 필드 선언·정확한 long 기본값·glyph는 같은 후보로 저장되고 stable nativeKey로 재시작 복원한다')
   if is_property:
    assert own_schema()['values']['editorIcon']=='📦'
    if is_object_property:
     assert next(row for row in own_schema()['rows'] if row['path']==['Power'])['valueJson']=='9223372036854775804';assert 'data Power=9223372036854775804;' in file.read_text();f.checked('객체의 직접 소유 스키마 glyph와 설명을 같은 후보로 저장하고 정확한 값·부모 glyph·참조·원본을 보존한다')
    if mode=='clear':
     p=popup();p.get_by_role('button',name='아이콘 없음',exact=True).click();assert len(pending())==1 and pending()[0][1]['text']=='';surface().locator('[data-element-action=save]').click();saved();restart(4);expect(icon()).to_have_text('◇');assert next(row for row in own_schema()['rows'] if row['path']==([new_native] if is_new else ['Power'])).get('icon') in [None,''] if is_object_property else ('editorFieldIcon_'+new_native if is_new else 'editorFieldIcon_Power') not in own_schema()['values'];f.checked('저장된 속성 아이콘 해제는 metadata만 원자 제거하고 재시작에도 원래 필드/값/다른 아이콘을 유지한다')
   if with_peer:
    surface().locator('[data-element-action=confirm]').click();group=f.page.get_by_role('dialog',name='관련 변경 검토',exact=True);expect(group).to_be_visible();group.locator('#review-creation').click();f.idle();expect(f.page.locator('#status')).to_contain_text('미적용 입력');assert any('|'+f.n+'Target1|' in k and v.get('text')=='9223372036854775804' for k,v in f.pending()['schema']);f.originals();group.get_by_role('button',name='닫기',exact=True).click();peer=f.page.locator('.window[data-key=schema]');peer.locator(':scope>.window-title').click(position={'x':30,'y':25});peer.locator('[data-element-action=discard]').click();f.idle();expect(peer.get_by_label('Power 기본값',exact=True)).to_have_value('1');f.checked('다른 창의 exact64 입력은 Save/cold/Review 거절에 보존되고 그 창에서 명시 취소한 뒤에만 최종 검토를 진행한다')
   r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();f.originals();r=review()
   if r.locator('[data-review-advanced]').count():
    r.locator('[data-review-advanced]').click()
    if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
   r.locator('#confirm').click();expect(r).to_have_count(0,timeout=120000);f.idle();assert_confirmed_sources();assert (('editorFieldIcon_'+new_native if is_new else 'editorFieldIcon_Power') not in icon_file.read_text() if is_property and mode=='clear' else ('editorFieldIcon_'+new_native if is_new else 'editorFieldIcon_Power' if is_property else 'editorIcon') in icon_file.read_text());f.checked('실제 compiler Review 취소 후 새 명시적 Confirm만 해당 선언의 glyph·설명을 반영하고 부모/외부/다른 본문·exact 값을 보존한다')
   if with_peer:expect(f.page.locator('.window[data-key=schema] .object-title-name')).to_have_text('Target1');expect(f.page.locator('.window[data-key=schema]').get_by_label('Power 기본값',exact=True)).to_have_value('1');f.checked('독립 창 최종 Confirm은 다른 기본 창의 문서 문맥과 원본을 바꾸지 않는다')
  assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except Exception:
 try:f.case.joinpath('icon-failure.json').write_text(json.dumps({'traffic':f.traffic[-50:],'errors':f.errors,'state':f.state()},ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'icon-failure.png'))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'nativeWindows':False,'actualMobile':False,'projectRun':False,'accountOrInference':False},ensure_ascii=False,indent=2))
