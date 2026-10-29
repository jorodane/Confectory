"""Original module requirement input/out/return icons, real receipt/CAS/Review; generated images only."""
import base64,copy,json,pathlib,shutil,sys,time
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3] if len(sys.argv)>3 else 'normal';kind='module';detached='view' in sys.argv[4:];leaf='HeaderModule';owner=f.n+leaf;target_pin=next((v for v in sys.argv[4:] if v in ['a0','a1','a2','return']),'a0')
for name,k in [('HeaderCategory','category'),('HeaderConcept','concept'),('HeaderModule','module')]:
 for suffix in ['Base','']:
  label=name+suffix;parent='' if suffix else ' extends '+f.n+name+'Base';text=k+' '+f.n+label+parent+' { // 그대로 보존할 헤더 원문 😀\r\nvalue Exact=9223372036854775805;value editorIcon="'+('🌿' if suffix else '📦')+'";'+('require '+f.n+'Slot (long,out long,out bool) -> long;' if k=='module' else '')+'}'
  (f.project/(label+'.celem')).write_text(text);f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element '+label+' '+k+' "'+label+'.celem";registry Confectory.Build.DotNet'))
if mode=='reset':
 key='editorModulePinIcon_f'+(f.n+'Slot').encode().hex()+'_'+target_pin;record=dict(function=f.n+'Slot',pin=target_pin,signature=dict(args=[dict(type='long',mode=''),dict(type='long',mode='out'),dict(type='bool',mode='out')],**{'return':'long'}),icon='★');p=f.project/(leaf+'.celem');p.write_text(p.read_bytes().decode().replace('value Exact=', 'value '+key+'='+json.dumps(json.dumps(record))+';value Exact='))
file=f.project/(leaf+'.celem');snapshot={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file()};panel_key='editor-1' if detached else 'declaration';wire=f.n+leaf+'|'+('view:1|' if detached else '')+'element|'
def original():assert all(p.read_bytes()==v for p,v in snapshot.items())
def panel():return f.page.locator('.window[data-key="'+panel_key+'"]')
def pin_button():return panel().locator('[data-module-function="'+f.n+'Slot"] [data-module-pin="'+target_pin+'"]')
def icon():return pin_button()
def shown(current):return json.loads(current['values'].get('editorModulePinIcon_f'+(f.n+'Slot').encode().hex()+'_'+target_pin,'{"icon":""}'))['icon']
def pending():return [(k,v) for k,v in f.pending()['schema'] if '|'+wire in k]
def open_card():
 f.idle()
 if panel().locator('.object-title-name').is_visible():
  layout();return
 f.page.locator('#workspace').click(button='right',position={'x':1550,'y':140});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab="'+('module' if kind=='module' else 'concept')+'"]').click();b.locator('[data-browser-control=object-query]').fill(leaf);b.locator('[data-browser-control=object-search]').click();b.locator('[data-object="'+owner+'"]').press('F2');f.idle();b.locator('[data-close]').first.click()
 if detached:
  primary=f.page.locator('.window[data-key=declaration]');primary.locator('[data-declaration-keep]').click();expect(panel().locator('.object-title-name')).to_have_text(leaf);f.invoke('select',{'id':f.n+'Unit'});f.idle()
 expect(panel().locator('.object-title-name')).to_have_text(leaf)
 layout()
def layout():
 for b in panel().locator('[data-module-pin]').all():
  rect=b.locator('xpath=following-sibling::code').bounding_box();assert rect and rect['width']>=64 and rect['height']<=44,rect
def popup():
 pin_button().click();p=f.page.get_by_role('dialog',name=pin_button().get_attribute('aria-label'),exact=True);expect(p).to_be_visible();return p
def pick(glyph):
 p=popup();p.locator('[data-icon-choice="'+glyph+'"]').click();p.get_by_role('button',name='적용',exact=True).click();expect(icon()).to_have_text(glyph)
def saved_value():
 result=f.invoke('openEditorView',dict(view='1',id=owner,viewMode='declaration')) if detached else f.invoke('inspectDeclaration',dict(id=owner))
 state=f.state();return next(r for r in state['editorViews'] if r['view']=='1')['declaration'] if detached else state['declaration']
def save():
 panel().locator('[data-declaration-header-action=save]').click();f.idle();assert not pending(),(pending(),f.page.locator('#status').inner_text())
def restart(i):
 f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':2100,'height':1500});open_card();f.idle()
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before_checkpoint=checkpoint.read_bytes()
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2100,'height':1500});open_card();expect(icon()).to_have_text('★' if mode=='reset' else '◇');p=popup();p.locator('[data-icon-choice="🔥"]').click();p.locator('[data-cancel]').click();assert not pending();p=popup();p.get_by_label('기호나 이모지',exact=True).fill('ab');p.get_by_role('button',name='적용',exact=True).click();expect(p).to_be_visible();f.page.keyboard.press('Escape');assert not pending();original();f.checked('원본 모듈 핀 팝오버 취소/Escape·잘못된 glyph는 공유 초안·원문·입력을 보존한다')
  pick('★');pin_button().press('Control+z');expect(icon()).to_have_text('★' if mode=='reset' else '◇');assert not pending();pin_button().press('Control+y');expect(icon()).to_have_text('★');restart(1);expect(icon()).to_have_text('★');f.checked('모듈 핀 private Undo/Redo·cold는 선택한 선언과 창의 아이콘만 복원한다')
  if mode=='mixed-preserve':panel().locator('[data-decl-property=displayName]').fill('보존할 기존 표시 이름 입력')
  p=popup();uri=f.page.evaluate("()=>{const c=document.createElement('canvas');c.width=64;c.height=32;const x=c.getContext('2d');x.fillStyle='#936';x.fillRect(0,0,64,32);return c.toDataURL('image/png')}");p.locator('[type=file]').set_input_files(dict(name='synthetic-header.png',mimeType='image/png',buffer=base64.b64decode(uri.split(',')[1])));expect(p.locator('.object-icon-preview img')).to_be_visible();p.get_by_role('button',name='적용',exact=True).click();expect(icon().locator('img')).to_be_visible();wanted=next(json.loads(v['text'])['icon'] for _,v in pending() if v['kind']=='module-pin-icon');panel().locator('[data-decl-property=description]').fill('이미지·설명 한 후보');held=pending();original();assert checkpoint.read_bytes()==before_checkpoint
  if mode=='reset':p=popup();p.get_by_role('button',name='아이콘 없음',exact=True).click();wanted='';held=pending();expect(icon()).to_have_text('◇')
  if mode=='multi':
   prior=target_pin;multi_icons={prior:wanted}
   for target_pin,glyph in [('a0','★'),('a1','🔥'),('return','🧪')]:
    if target_pin!=prior:pick(glyph);multi_icons[target_pin]=glyph
   target_pin=prior;held=pending();actual={json.loads(v['text'])['pin']:json.loads(v['text'])['icon'] for _,v in held if v['kind']=='module-pin-icon'};assert actual==multi_icons;original()
  if mode=='mixed-preserve':
   panel().locator('[data-declaration-header-action=save]').click();f.idle();assert pending()==held and checkpoint.read_bytes()==before_checkpoint;original();panel().locator('[data-declaration-header-action=discard]').click();f.idle();assert not pending();expect(panel().locator('[data-decl-property=displayName]')).to_have_value('보존할 기존 표시 이름 입력');restart(2);assert not pending();expect(panel().locator('[data-decl-property=displayName]')).to_have_value('보존할 기존 표시 이름 입력');original();f.checked('다른 기존 선언 입력과의 저장 경계는 이미지 선택을 유실하지 않으며 헤더 취소도 다른 표시 이름 입력을 지우지 않는다');f.browser.close();raise SystemExit(0)
  if mode=='project':
   other=f.case/'other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory'));other_bytes=(other/file.name).read_bytes();f.pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(other/'project.cproj');f.start(10);f.page=f.setup();f.page.set_viewport_size({'width':2100,'height':1500});open_card();assert not pending();pick('🔥');f.pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.project/'project.cproj');f.start(11);f.page=f.setup();f.page.set_viewport_size({'width':2100,'height':1500});open_card();assert pending()==held;assert (other/file.name).read_bytes()==other_bytes;f.checked('동일 namespace/ID의 실제 다른 프로젝트 왕복은 이미지·설명·창 입력을 섞지 않는다')
  if mode=='cancel-late':
   ids=set();paused={}
   def pause_cancel(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke' and body.get('endpoint')=='browserDrafts' and body.get('input',{}).get('action')=='status':ids.add(body['requestId'])
    response=route.fetch();payload=response.json()
    if not paused and any(v.get('ok') and v.get('requestId') in ids for v in payload.get('results',[])):paused.update(route=route,response=response);return
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',pause_cancel);panel().locator('[data-declaration-header-action=discard]').click()
   for _ in range(600):
    if paused:break
    f.page.wait_for_timeout(50)
   assert paused;pick('🛡️');panel().locator('[data-decl-property=description]').fill('취소 응답 대기 중 새 설명');paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',pause_cancel);f.idle();assert {v['kind']:(json.loads(v['text'])['icon'] if v['kind']=='module-pin-icon' else v['text']) for _,v in pending()}=={'module-pin-icon':'🛡️','description':'취소 응답 대기 중 새 설명'};assert checkpoint.read_bytes()==before_checkpoint;original();restart(2);assert {v['kind']:(json.loads(v['text'])['icon'] if v['kind']=='module-pin-icon' else v['text']) for _,v in pending()}=={'module-pin-icon':'🛡️','description':'취소 응답 대기 중 새 설명'};f.checked('취소의 관측 응답 중 새 이미지/설명은 원래 취소 snapshot과 구분되어 cold까지 보존된다');f.browser.close();raise SystemExit(0)
  if mode=='cancel':
   panel().locator('[data-declaration-header-action=discard]').click();f.idle();assert not pending() and checkpoint.read_bytes()==before_checkpoint;original();restart(2);expect(icon()).to_have_text('★' if mode=='reset' else '◇');f.checked('명시 변경 취소·cold는 선택한 헤더의 private 입력만 취소하고 부모·모듈·원문을 보존한다')
  else:
   if mode=='guard':
    assert detached
    current=saved_value();binding=next(r for r in f.state()['editorViews'] if r['view']=='1')['authorBinding'];base=dict(id=owner,view='1',viewBinding=binding,owner=owner)
    f.invoke('blueprint',dict(base,action='readOwnerEdits',hash=current['textHash'],viewBinding='0'*32),False)
    observed=f.invoke('blueprint',dict(base,action='readOwnerEdits',hash=current['textHash']))['result']['result']
    edit=dict(id=owner,hash=current['textHash'],changes=[dict(type='module-pin-icon',text=next(v['text'] for _,v in pending() if v['kind']=='module-pin-icon')),dict(type='parent',text=f.n+'Unit')])
    f.invoke('blueprint',dict(base,action='applySlots',rows=[],basis=observed['basis'],declaration=edit),False)
    f.invoke('blueprint',dict(base,action='readOwnerEdits',id=f.n+'Unit',hash=current['textHash']),False)
    assert pending()==held and checkpoint.read_bytes()==before_checkpoint;original();f.checked('독립 선언창의 잘못된 binding·다른 owner·계약 변경 결합은 서버에서 전체 거절하며 이미지 입력·기존 원문을 보존한다')
   if mode=='conflict':
    current=saved_value();f.invoke('editViewDeclaration' if detached else 'editDeclaration',dict(**({'view':'1'} if detached else {}),id=owner,revision=current['revision'],hash=current['textHash'],edit={'action':'properties','values':{'description':'다른 실제 편집'}}));f.invoke('saveEditorView' if detached else 'saveDraft',dict(view='1',id=owner) if detached else {});peer_checkpoint=checkpoint.read_bytes();panel().locator('[data-declaration-header-action=save]').click();f.idle();assert pending()==held and checkpoint.read_bytes()==peer_checkpoint;original();restart(2);assert pending()==held;f.checked('실제 peer source/checkpoint CAS 충돌은 전체 거절하고 기존 저장·이미지 입력·cold를 보존한다');f.browser.close();raise SystemExit(0)
   if mode=='storage':
    checkpoint.chmod(0o400)
    try:panel().locator('[data-declaration-header-action=save]').click();f.idle();assert pending()==held and checkpoint.read_bytes()==before_checkpoint;original()
    finally:checkpoint.chmod(0o600)
    restart(2);assert pending()==held;f.checked('원자 checkpoint 실패는 이미지·설명을 부분 저장하지 않고 cold 입력을 보존한다')
   if mode in ['loss','late']:
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
     assert paused;pick('🛡️');paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',intercept);f.idle();assert next(json.loads(v['text'])['icon'] for _,v in pending() if v['kind']=='module-pin-icon')=='🛡️';wanted='🛡️';restart(3);save();f.checked('저장 응답 중 새 아이콘은 수락 receipt로 재기준하며 cold·다음 명시 Save까지 보존한다')
    else:
     assert any(v in queries for v in lost) and pending()==held;f.page.unroute_all(behavior='wait');mark=len(f.traffic);restart(3);save();assert not any(v.get('invoke',{}).get('input',{}).get('action')=='applySlots' for v in f.traffic[mark:]);f.checked('수락/조회 응답 유실은 cold receipt로 확인하며 metadata 후보를 중복 적용하지 않는다')
   else:save()
   current=saved_value();
   if mode=='multi':
    for pin,glyph in multi_icons.items():assert json.loads(current['values']['editorModulePinIcon_f'+(f.n+'Slot').encode().hex()+'_'+pin])['icon']==glyph
   assert shown(current)==wanted and current['values']['editorIcon']=='📦';assert current['values']['Exact']==9223372036854775805;assert current['parent']==f.n+leaf+'Base';original();restart(4);assert not pending();expect(icon().locator('img') if wanted.startswith('data:') else icon()).to_be_visible();f.checked('metadata 전용 한 후보/CAS Save·cold는 이미지/설명만 저장하고 Exact64·부모·모듈 계약·본문을 유지한다')
   panel().locator('[data-declaration-header-action=confirm]').click();r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=120000);r.locator('[data-reject]').click();expect(r).to_be_hidden();original();panel().locator('[data-declaration-header-action=confirm]').click();expect(r).to_be_visible(timeout=120000)
   if r.locator('[data-review-advanced]').count():
    r.locator('[data-review-advanced]').click()
    if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
   expect(r.locator('#confirm')).to_be_enabled(timeout=120000);r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();assert {p.name for p,v in snapshot.items() if p.read_bytes()!=v}=={file.name};assert '// 그대로 보존할 헤더 원문 😀\r\n'.encode() in file.read_bytes();f.checked('Review 취소와 명시 compiler Confirm은 선택한 선언 metadata 한 파일만 반영하며 부모/외부/등록/다른 원문을 보존한다')
  assert not f.errors and not f.external,(f.errors,f.external);panel().locator('[data-module-function="'+f.n+'Slot"] .module-contract-flow').screenshot(path=str(f.case/'module-pin-flow.png'));f.page.screenshot(path=str(f.case/'module-pin.png'));f.browser.close()
except Exception:
 try:(f.case/'header-failure.json').write_text(json.dumps(dict(state=f.state(),traffic=f.traffic[-60:],errors=f.errors),ensure_ascii=False,indent=2)+'\n')
 except Exception:pass
 try:f.page.screenshot(path=str(f.case/'module-pin-failure.png'),timeout=5000)
 except Exception:pass
 raise
finally:
 f.stop();(f.case/'module-pin-evidence.json').write_text(json.dumps(dict(checks=f.checks,errors=f.errors,kind=kind,mode=mode,detached=detached,actualWindows=False,actualMobile=False),ensure_ascii=False,indent=2)+'\n')
print('EVIDENCE',f.case,flush=True)
