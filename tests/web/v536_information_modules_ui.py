"""Information module attachment through original v536 UI, isolated real engine.
Bound module editing uses the same candidates; complete lifecycles have separate focused suites.
"""
import json,re,sys,time,zipfile
from playwright.sync_api import sync_playwright,expect
import v536_field_definitions_ui as d
from editor_navigation import open_project_tools
f=d.f;owner=d.owner;mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
info=f.project/'FreeInfo.celem';info.write_text(info.read_text().replace('FreeInfo {','FreeInfo extends '+f.n+'Leaf {provide '+f.n+'Slot with '+f.n+'AliasBody;',1))
(f.project/'Empty.celem').write_text('module '+f.n+'Empty {}')
leaf=f.project/'Leaf.celem';leaf.write_text(leaf.read_text().replace('{','{module '+f.n+'Empty;',1))
f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element Empty module "Empty.celem";registry Confectory.Build.DotNet',1))
f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file()}
compared=False
def compare_picker(popup):
 global compared
 if compared:return
 with zipfile.ZipFile(f.repo/'reference/site-ui/Confectory-Editor-Prototype-v536.zip') as z:
  app=next(n for n in z.namelist() if n.endswith('/dist/app.js'));source=z.read(app).decode();css=re.sub(r'@import\s+url\([^)]*\)\s*;','',z.read(app.removesuffix('app.js')+'style.css').decode())
 start=source.index('function linkObjectBehavior(');end=source.index('\nfunction ',start+1);function=source[start:end]
 choices=popup.locator('[data-link-id]').evaluate_all('(els)=>els.map(el=>({id:el.dataset.linkId,name:el.querySelector("strong").textContent,description:el.querySelector("small").textContent,group:"module",kind:"Module"}))');selectors=[':scope','input','.behavior-link-options']+['[data-link-id="'+row['id']+'"]' for row in choices]
 measure="""(el,selectors)=>{const b=el.getBoundingClientRect();return selectors.map(s=>{const e=s===':scope'?el:el.querySelector(s),r=e.getBoundingClientRect(),c=getComputedStyle(e);return {selector:s,x:r.x-b.x,y:r.y-b.y,width:r.width,height:r.height,color:c.color,background:c.backgroundColor,font:c.font,padding:c.padding};});}"""
 try:actual=popup.evaluate(measure,selectors)
 except Exception:
  print('MODULE_POPUP_STATE '+json.dumps(f.page.evaluate('''()=>({roots:[...document.querySelectorAll('.behavior-link-popover')].map(el=>({html:el.outerHTML,rect:el.getBoundingClientRect().toJSON(),ancestors:[...function*(e){while(e){yield {tag:e.tagName,classes:e.className,inert:e.inert,hidden:e.hidden,aria:e.getAttribute('aria-hidden')};e=e.parentElement}}(el)]})),removals:globalThis.modulePopupRemovals})'''),ensure_ascii=False),flush=True);raise
 anchor=f.owner().locator('[data-module-link]').bounding_box();original=f.browser.new_page(viewport=f.page.viewport_size);original.route('**/*',lambda route:route.abort());original.set_content('<!doctype html><html lang="ko"><head><style>'+css+'</style></head><body><button id="anchor" style="position:fixed;box-sizing:border-box;left:'+str(anchor['x'])+'px;top:'+str(anchor['y'])+'px;width:'+str(anchor['width'])+'px;height:'+str(anchor['height'])+'px">＋ 모듈</button></body></html>')
 original.add_script_tag(content="const esc=s=>String(s??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('\\\"','&quot;');let activeBehaviorLinkPopover=null;const project={objects:"+json.dumps(choices,ensure_ascii=False)+"};function objectBehaviorChanged(){throw Error('visual-only oracle cannot mutate');}"+function+"\nlinkObjectBehavior({id:'Owned.Elements::FreeInfo'},'module',document.querySelector('#anchor'));")
 expected=original.locator('.behavior-link-popover').evaluate(measure,selectors);original.screenshot(path=str(f.case/'information-module-picker-original.png'));f.page.screenshot(path=str(f.case/'information-module-picker-engine.png'));original.close();(f.case/'information-module-picker-geometry.json').write_text(json.dumps({'original':expected,'actual':actual},ensure_ascii=False,indent=2));assert expected==actual,{'original':expected,'actual':actual};compared=True
def schema():
 s=f.state();return next(r['schema'] for r in s['editorViews'] if r['view']=='1') if d.is_view else s['schema']
def card(name='Rules'):return f.owner().locator('[data-behavior-source="'+f.n+name+'"]')
def wait(endpoint,after,action=None,ok=True):
 deadline=time.monotonic()+90
 while time.monotonic()<deadline:
  ids={r['invoke']['requestId'] for r in f.traffic[after:] if r.get('invoke',{}).get('endpoint')==endpoint and (action is None or r['invoke']['input'].get('action')==action)}
  rows=[r['result'] for r in f.traffic[after:] if r.get('result',{}).get('requestId') in ids and r['result'].get('error',{}).get('code')!='stale_revision']
  if rows:assert bool(rows[-1].get('ok')) is ok,rows;f.idle();return rows[-1]
  f.page.wait_for_timeout(20)
 raise AssertionError('no completed '+endpoint)
def attach():
 f.idle();button=f.owner().locator('[data-module-link]');button.scroll_into_view_if_needed();f.page.evaluate('()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))');button.click();p=f.page.get_by_role('dialog',name='모듈 연결',exact=True);expect(p).to_be_visible();compare_picker(p);p.locator('[data-link-id="'+f.n+'Rules"]').click();expect(card()).to_be_visible()
def save():
 f.owner().locator('[data-element-action=save]').click();d.saved();expect(card().locator('[data-module-method]')).to_have_count(2)
def values():
 expect(f.owner().get_by_label('Power 기본값',exact=True)).to_have_value('9223372036854775806');expect(f.owner().locator('.property-reference-value')).to_contain_text('RefTarget');assert schema()['validation']['status']=='valid'
def restart(i):
 d.restart(i);d.verify_peer();expect(card('Empty')).to_be_visible();values()
def finish():
 r=d.review();r.locator('[data-reject]').click();expect(r).to_be_hidden();f.originals();r=d.review()
 if r.locator('[data-review-advanced]').count():
  r.locator('[data-review-advanced]').click()
  if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
 r.locator('#confirm').click();expect(r).to_have_count(0,timeout=120000);f.idle();assert {k for k,v in f.original.items() if (f.project/k).read_bytes()!=v}=={'FreeInfo.celem'}
 assert 'module '+f.n+'Rules;' in info.read_text() and 'provide '+f.n+'Slot with '+f.n+'AliasBody;' in info.read_text()
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{})
 if d.is_view:f.invoke('select',{'id':f.n+'RefTarget'})
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300 if d.is_view else 1600,'height':1500});d.open_info()
  if d.is_view:d.open_peer()
  expect(card('Empty')).to_be_visible();expect(card('Empty').locator('[data-behavior-unlink]')).to_have_count(0);assert abs(f.owner().bounding_box()['width']-460)<1;values();checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();attach();held=d.pending();assert held[0][1]['kind']=='modules';f.originals();assert checkpoint.read_bytes()==before
  if mode=='normal':
   f.owner().locator('[data-element-action=discard]').click();expect(card()).to_have_count(0);assert checkpoint.read_bytes()==before;values();attach();f.owner().locator('[data-own-functions-toggle]').focus();f.page.keyboard.press('Control+z');expect(card()).to_have_count(0);f.page.keyboard.press('Control+Shift+z');expect(card()).to_be_visible();f.checked('원본 정보 모듈 선택·취소·private Undo/Redo는 inherited 모듈·정확한 값·provide·원본과 다른 창 입력을 보존한다')
   held=d.pending();restart(1);assert d.pending()==held;expect(card()).to_be_visible();save();f.originals();values();d.verify_peer();assert not any(r.get('invoke',{}).get('endpoint') in ['run','runProject','startProject'] for r in f.traffic);assert {r['function'] for r in schema()['requirements']}=={f.n+'Slot',f.n+'Slot2'}

   for control in ['[data-function-import]','[data-function-edit]']:
    expect(card().locator(control).first).to_be_enabled()
   f.checked('원본 모듈 카드·핀은 실제 schema module/provide/default 계약을 표시하고 기본/독립 창 구현 진입을 연결하고 AI 작성 및 프로젝트 실행은 하지 않는다')
   f.page.screenshot(path=str(f.case/'information-modules-saved.png'));restart(2);assert not d.pending();expect(card().locator('[data-module-method]')).to_have_count(2);values();d.verify_peer();f.checked('Save와 실제 cold는 bound 정보의 모듈·계약·provider·typed defaults 및 독립 peer 입력을 복원한다')
   card().locator('[data-behavior-unlink]').click();expect(card()).to_have_count(0);f.owner().locator('[data-element-action=discard]').click();expect(card().locator('[data-module-method]')).to_have_count(2);values();d.verify_peer()
   if d.is_view:
    peer=f.page.locator('.window[data-key=editor-2]');peer.locator('[data-element-action=discard]').click();d.peer_inputs=None
   finish();restart(3);expect(card().locator('[data-module-method]')).to_have_count(2);values();f.checked('unlink 취소와 Review 취소/새 compiler Confirm/cold는 정보 파일의 모듈만 반영하고 부모·기능·구현·다른 소스를 보존한다')
  elif mode in ['storage','conflict']:
   if mode=='storage':checkpoint.chmod(0o400)
   else:
    source=info.read_bytes()+b'\n// isolated concurrent information source\n';info.write_bytes(source);f.original['FreeInfo.celem']=source
   try:
    f.rejected_save();assert d.pending()==held and checkpoint.read_bytes()==before;f.originals();values();d.verify_peer();f.checked('실제 저장 거절/동시 source 변경은 정보 module·선언·값 후보 전부 미적용이고 입력·peer·checkpoint를 보존한다')
   finally:
    if mode=='storage':checkpoint.chmod(0o600)
   restart(1);assert d.pending()==held;f.originals();values();d.verify_peer()
   if mode=='storage':save();f.originals();expect(card().locator('[data-module-method]')).to_have_count(2)
   else:f.rejected_save();assert checkpoint.read_bytes()==before and d.pending()==held
   f.checked('실패 cold 뒤 명시 재시도는 동일 source면 저장 가능하고 실제 바뀐 source면 재거절하며 자동 덮어쓰기하지 않는다')
  elif mode=='loss':
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
   f.page.route('**/api/request',intercept);f.owner().locator('[data-element-action=save]').click()
   for _ in range(300):
    if applies and any(r in queries for r in lost):break
    f.page.wait_for_timeout(100)
   assert len(applies)==1 and any(r in queries for r in lost) and d.pending()==held;f.page.unroute_all(behavior='wait');mark=len(f.traffic);restart(1);f.owner().locator('[data-element-action=save]').click();d.saved();expect(card().locator('[data-module-method]')).to_have_count(2)
   assert not any(r.get('invoke',{}).get('input',{}).get('action')=='applySlots' for r in f.traffic[mark:]);values();d.verify_peer();f.originals();f.checked('실제 적용/조회 응답 유실 뒤 cold receipt 확인은 모듈 Save를 중복하지 않고 private 입력·provider·peer를 보존한다')
  else:raise AssertionError(mode)
  assert not f.errors and not f.external,(f.errors,f.external);f.page.unroute_all(behavior='wait');f.browser.close()
except Exception:
 try:f.case.joinpath('information-modules-failure.json').write_text(json.dumps({'state':f.state(),'traffic':f.traffic[-60:],'errors':f.errors},ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'information-modules-failure.png'))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
