"""Original property type/choice controls, typed defaults and real owner CAS/Confirm."""
import ast,base64,copy,io,json,pathlib,shutil,sys
from PIL import Image
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3] if len(sys.argv)>3 else 'normal';detached='view' in sys.argv[4:];with_peer=False;kind='object' if 'object' in sys.argv[4:] else 'schema';leaf='Target2' if kind=='object' else 'Details';owner=f.n+leaf
helper=pathlib.Path(__file__).with_name('v536_element_icon_ui.py');names={'surface','pending','own_schema','open_card','saved','restart','review'};exec(compile(ast.Module(body=[node for node in ast.parse(helper.read_text()).body if isinstance(node,ast.FunctionDef) and node.name in names],type_ignores=[]),str(helper),'exec'));f.owner=surface
buf=io.BytesIO();Image.new('RGBA',(128,128),(31,117,92,170)).save(buf,format='WEBP');image='data:image/webp;base64,'+base64.b64encode(buf.getvalue()).decode()
members=[dict(id='stable-ready',name='준비 됨',icon='★'),dict(id='stable-done',name='완료 😀',icon=image)]
enum_file=f.project/'Mood.celem';enum_file.write_text('enum '+f.n+'Mood {value editorEnumProfile="nominal-members-v1";value editorEnumValues='+json.dumps(json.dumps(members,ensure_ascii=False,separators=(',',':')))+';}')
f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element Mood enum "Mood.celem";registry Confectory.Build.DotNet'))
info=f.project/'Details.celem';info.write_text(info.read_text().replace('{','{ // preserve information source 😀\nfield Mood single enum '+f.n+'Mood;field Moods multiple enum '+f.n+'Mood;field Unused single general string;value editorInformationDefaults="typed-json-v1";value editorFieldDefault_Mood="\\"stable-ready\\"";value editorFieldDefault_Moods="[\\"stable-ready\\"]";',1))
file=f.project/(leaf+'.celem')
if kind=='object':file.write_text(file.read_text().replace('{','{data Mood="stable-ready";data Moods=["stable-ready"];',1))
f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file()}
def original():assert all((f.project/p).read_bytes()==data for p,data in f.original.items())
def row(name):return surface().locator('[data-property-path='+json.dumps(json.dumps([name],separators=(',',':')))+']')
def value(name):return next(r for r in own_schema()['rows'] if r['path']==[name])['valueJson']
def choose(button,id,wait=True):
 button.click();box=f.page.get_by_role('listbox',name=button.get_attribute('aria-label').removesuffix(' 기본값 선택')+' 종류 선택',exact=True);expect(box).to_be_visible();box.locator('[data-enum-choice="'+id+'"]').click()
 if wait:f.idle()
def save():surface().locator('[data-element-action=save]').click();saved()
try:
 f.start(0);f.invoke('select',dict(id=owner));f.invoke('saveDraft',{})
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size(dict(width=1900,height=1400));open_card();button=row('Mood').locator('.enum-dropdown');expect(button).to_contain_text('준비 됨');button.press('ArrowDown');expect(f.page.get_by_role('listbox',name='Mood 종류 선택')).to_be_visible();f.page.keyboard.press('Escape');assert not pending();original()
  choose(button,'stable-done');expect(row('Mood').locator('.enum-dropdown img')).to_be_visible();row('Mood').locator('[data-property-icon]').focus();f.page.keyboard.press('Control+z');expect(row('Mood').locator('.enum-dropdown')).to_contain_text('준비 됨');f.page.keyboard.press('Control+y');expect(row('Mood').locator('.enum-dropdown')).to_contain_text('완료');f.checked('종류 드롭다운의 키보드/취소·기호/이미지·명시 선택과 Undo/Redo는 같은 항목 ID를 유지한다')
  # Original array Add initializes the first item, then the user chooses an id.
  row('Moods').locator('.property-add-value').click();choose(row('Moods').locator('.enum-dropdown').last,'stable-done');assert len(row('Moods').locator('.property-multi-item').all())==2
  surface().locator('[data-schema-add]').click();new=surface().locator('[data-definition-key]').last;new.locator('[data-property-name]').fill('FreshChoice');new.locator('[data-property-type]').click();f.page.get_by_role('dialog',name='속성 타입 선택').locator('[data-field-kind=enum][data-field-type="'+f.n+'Mood"]').click();new=surface().locator('[data-definition-key]').last;expect(new.locator('.enum-dropdown')).to_contain_text('준비 됨');choose(new.locator('.enum-dropdown'),'stable-done');fresh=next(v for _,v in pending() if v['kind']=='definition');fresh_key=fresh.get('nativeKey') or fresh['name'];assert json.loads(fresh['text'])=='stable-done';f.checked('새 정보 속성의 타입 선택은 종류 owner와 기본값 항목 ID를 한 private 정의에 저장한다')
  if kind=='schema':
   row('Unused').locator('[data-property-type]').click();f.page.get_by_role('dialog',name='속성 타입 선택').locator('[data-field-kind=enum][data-field-type="'+f.n+'Mood"]').click();choose(row('Unused').locator('.enum-dropdown'),'stable-done')
  held=copy.deepcopy(pending());checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes();original();restart(1);expect(row('Mood').locator('.enum-dropdown')).to_contain_text('완료');assert pending()==held;f.checked('저장 전 cold는 선택 ID·배열·새 타입 정의와 창 문맥을 보존한다')
  if mode=='cancel':
   surface().locator('[data-element-action=discard]').click();f.idle();assert not pending();original();restart(2);expect(row('Mood').locator('.enum-dropdown')).to_contain_text('준비 됨');f.checked('변경 취소와 재시작은 원래 선택 ID·정의·원문을 복원한다');f.browser.close();raise SystemExit(0)
  if mode=='conflict':
   file.write_bytes(file.read_bytes()+b'\n// actual owner race\n');f.original[file.name]=file.read_bytes();surface().locator('[data-element-action=save]').click();expect(surface().locator('[data-element-error]')).not_to_have_text('');assert pending()==held and checkpoint.read_bytes()==baseline;original();restart(2);assert pending()==held;f.checked('실제 owner 충돌은 전체 미적용이며 종류 선택/새 정의 입력을 보존한다');f.browser.close();raise SystemExit(0)
  if mode=='project':
   other=f.case/'other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory'));f.pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(other/'project.cproj');f.start(10);f.page=f.setup();open_card();assert not pending();choose(row('Mood').locator('.enum-dropdown'),'stable-done');f.pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.project/'project.cproj');f.start(11);f.page=f.setup();open_card();assert pending()==held;original();f.checked('동일 namespace/항목 ID의 실제 프로젝트 왕복은 선택값과 창 입력을 섞지 않는다')
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:surface().locator('[data-element-action=save]').click();expect(surface().locator('[data-element-error]')).not_to_have_text('');assert pending()==held and checkpoint.read_bytes()==baseline;original()
   finally:checkpoint.chmod(0o600)
   restart(2);assert pending()==held;f.checked('checkpoint 실패는 타입/값을 부분 저장하지 않고 cold까지 입력을 보존한다')
  if mode in ['late','loss']:
   ids=set();queries=set();paused={};lost=[]
   def intercept(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
     action=body.get('input',{}).get('action')
     if action=='applySlots':ids.add(body['requestId'])
     if action=='settledSlots':queries.add(body['requestId'])
    response=route.fetch();payload=response.json()
    if mode=='late' and not paused and any(r.get('ok') and r['requestId'] in ids for r in payload.get('results',[])):paused.update(route=route,response=response);return
    if mode=='loss':
     for result in payload.get('results',[]):
      if result['requestId'] in ids|queries:rid=result['requestId'];lost.append(rid);result.clear();result.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',intercept);surface().locator('[data-element-action=save]').click()
   for _ in range(600):
    if paused or any(i in queries for i in lost):break
    f.page.wait_for_timeout(50)
   assert len(ids)==1
   if mode=='late':
    assert paused;choose(row('Mood').locator('.enum-dropdown'),'stable-ready',wait=False);paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',intercept);f.idle();restart(3);expect(row('Mood').locator('.enum-dropdown')).to_contain_text('준비 됨');save();f.checked('수락 응답 중 새 선택은 receipt로만 재기준하며 cold와 다음 명시 Save까지 보존한다')
   else:
    assert any(i in queries for i in lost) and pending()==held;f.page.unroute_all(behavior='wait');mark=len(f.traffic);restart(3);save();assert not any(v.get('invoke',{}).get('input',{}).get('action')=='applySlots' for v in f.traffic[mark:]);f.checked('적용/조회 응답 유실은 cold receipt로 회수하며 정의나 값을 중복 저장하지 않는다')
  else:save()
  assert json.loads(value('Mood'))==('stable-ready' if mode=='late' else 'stable-done');assert json.loads(value('Moods'))==['stable-ready','stable-done'];assert json.loads(value(fresh_key))=='stable-done';assert next(r for r in own_schema()['rows'] if r['path']==[fresh_key])['kind']=='enum';original();restart(4);assert json.loads(value(fresh_key))=='stable-done';assert json.loads(value('Mood'))==('stable-ready' if mode=='late' else 'stable-done');f.checked('정의·기본값/객체 값은 원자 후보·최종 CAS로 저장하고 재시작하며 원본은 Confirm 전 보존한다')
  r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();original();r=review()
  if r.locator('[data-review-advanced]').count():
   r.locator('[data-review-advanced]').click()
   if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
  expect(r.locator('#confirm')).to_be_enabled(timeout=120000);r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();assert {p for p,data in f.original.items() if (f.project/p).read_bytes()!=data}==({file.name} if kind=='schema' else {file.name,'project.cproj'});assert enum_file.read_bytes()==f.original['Mood.celem'];assert not f.errors and not f.external;f.checked('Review 취소·명시 compiler Confirm은 선택한 소유 값/기본값만 반영하고 종류·부모·외부·C# 원문을 보존한다');surface().screenshot(path=str(f.case/'information-enum-values.png'));f.browser.close()
except Exception:
 try:(f.case/'enum-values-failure.json').write_text(json.dumps(dict(state=f.state(),traffic=f.traffic[-100:],errors=f.errors),ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'enum-values-failure.png'),timeout=5000)
 except Exception:pass
 raise
finally:
 f.stop();(f.case/'information-enum-values-evidence.json').write_text(json.dumps(dict(checks=f.checks,mode=mode,detached=detached,kind=kind,actualWindows=False,actualMobile=False),ensure_ascii=False,indent=2)+'\n')
