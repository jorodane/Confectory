"""Information own inline definitions in the real v536 renderer. Isolated sources only."""
import json,re,time
from playwright.sync_api import sync_playwright,expect
import v536_field_definitions_ui as d
f=d.f;owner=d.owner;info=f.project/'FreeInfo.celem'
info.write_text(info.read_text().replace('FreeInfo {','FreeInfo {contain function '+f.n+'Slot;',1));f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file()}

def schema():
 state=f.state();return next(row['schema'] for row in state['editorViews'] if row['view']=='1' and row['id']==owner) if d.is_view else state['schema']
def methods():return f.owner().locator('[data-inline-method]')
def pending():return [v for _,v in d.pending() if v['kind'] in ['function-add','function-edit']]
def detail(row):
 row.locator('.function-node-heading').press('Enter');p=f.page.locator('.function-detail-popover');expect(p).to_be_visible();return p
def pick(row,native):
 row.locator('[data-signature-type]').click();f.page.get_by_role('dialog',name='속성 타입 선택',exact=True).locator('[data-type="'+native+'"]').click()
def saved(name):
 f.owner().locator('[data-element-action=save]').click()
 deadline=time.monotonic()+60
 while time.monotonic()<deadline:
  if not pending() and any(v['name']==name for v in schema().get('ownFunctions',[])):f.idle();return
  f.page.wait_for_timeout(30)
 raise AssertionError((f.owner().locator('[data-element-error]').all_text_contents(),f.pending()))
def restart(index):
 held=f.pending();f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(index);f.page=f.setup();f.page.set_viewport_size({'width':1700,'height':1300});expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo');f.idle();return held
def compare_original(row):
 f.invoke('schema',{'id':owner})
 import zipfile
 with zipfile.ZipFile(f.repo/'reference/site-ui/Confectory-Editor-Prototype-v536.zip') as archive:
  app=next(n for n in archive.namelist() if n.endswith('/dist/app.js'));source=archive.read(app).decode();css=re.sub(r'@import\s+url\([^)]*\)\s*;','',archive.read(app.removesuffix('app.js')+'style.css').decode())
 names=['functionGearIcon','functionIconMarkup','receivedFunctionName','functionPinContourMarkup','functionPinsMarkup','functionFlowMarkup','functionWritingActionsMarkup','functionCollapseToggleMarkup','functionNodeMarkup','functionPinColor','setupFunctionNodeDescriptions']
 def extract(name):
  start=source.index('function '+name+'(');end=source.find('\nfunction ',start+1);return source[start:end if end>=0 else None]
 value=next(v for v in schema()['ownFunctions'] if v['id']==row.get_attribute('data-inline-method'));contract=value['signature'];primitive={'int':'정수','long':'정수','double':'실수','float':'실수','string':'글자','bool':'조건'}
 def field(a):return {'name':a['Name'],'type':primitive.get(a['Type'],a['Type'])}
 model={'name':row.locator('[data-inline-name]').input_value(),'description':row.locator('[data-inline-description]').input_value(),'inputs':[field(a) for a in contract['Args'] if a.get('Mode')!='out'],'outputs':[field(a) for a in contract['Args'] if a.get('Mode') in ['out','ref']]+([] if contract['return']=='void' else [{'name':'결과','type':primitive.get(contract['return'],contract['return'])}])}
 selectors=[':scope','.function-node-heading','[data-inline-name]','.function-node-flow','[data-inline-description]','.function-node-writing-actions','[data-pin-side=inputs]','[data-pin-side=outputs]','[data-function-icon]','[data-function-toggle]','[data-function-delete]','[data-function-write-direct]']
 measure="""(el,selectors)=>{const base=el.getBoundingClientRect();return selectors.map(selector=>{const e=selector===':scope'?el:el.querySelector(selector),r=e.getBoundingClientRect(),c=getComputedStyle(e);return {selector,x:r.x-base.x,y:r.y-base.y,width:r.width,height:r.height,font:c.font,padding:c.padding};});}"""
 actual=row.evaluate(measure,selectors);html=f.owner().evaluate('e=>e.outerHTML');oracle=f.browser.new_page(viewport=f.page.viewport_size);oracle.route('**/*',lambda route:route.abort());oracle.set_content('<!doctype html><html lang="ko"><head><style>'+css+'</style></head><body><div id="workspace">'+html+'</div></body></html>')
 oracle.add_script_tag(content="const esc=s=>String(s??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('\\\"','&quot;');const functionSignatureFields=(m,side)=>m[side]||[],propertyTypeSummary=f=>f.type+(f.multi?' 여러 개':''),blueprintIsAsync=()=>false,blueprintIsComplete=()=>false;"+'\n'.join(extract(name) for name in names)+"\nconst row=document.querySelector('[data-inline-method]');row.innerHTML=functionNodeMarkup("+json.dumps(model,ensure_ascii=False)+");setupFunctionNodeDescriptions({},row);")
 oracle.wait_for_function('()=>[...document.querySelectorAll(".function-node-description")].every(e=>e.style.height)');expected=oracle.locator('[data-inline-method]').evaluate(measure,selectors);oracle.screenshot(path=str(f.case/'own-function-original.png'));f.page.screenshot(path=str(f.case/'own-function-engine.png'));oracle.close();(f.case/'own-function-geometry.json').write_text(json.dumps({'expected':expected,'actual':actual},ensure_ascii=False,indent=2));assert actual==expected,{'expected':expected,'actual':actual};f.checked('원본 v536 함수 카드 12영역의 치수·배치·폰트·padding을 실제 DOM 대조했다')

try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{})
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1700,'height':1300});d.open_info();shared=f.owner().locator('[data-method-id=\"'+f.n+'Slot\"]');expect(shared).to_be_visible();expect(shared.locator('[data-inline-name],[data-function-delete]')).to_have_count(0);f.owner().locator('[data-function-add]').click();row=methods().last;row.locator('[data-inline-name]').fill('정보 계산 😀');row.locator('[data-inline-description]').fill('한글 설명과 줄바꿈\n원문');held=pending()[0];method=held['id'];assert held['kind']=='function-add';row.locator('[data-function-delete]').click();expect(methods()).to_have_count(0);f.owner().locator('[data-own-functions-toggle]').focus();f.page.keyboard.press('Control+z');expect(methods()).to_have_count(1);assert pending()[0]==held;f.page.keyboard.press('Control+y');expect(methods()).to_have_count(0);f.page.keyboard.press('Control+z');expect(methods()).to_have_count(1);f.originals();f.checked('원본 inline 기능 추가·한글 이름/설명·생성 전 삭제와 영역 Undo/Redo는 원문을 보존한다')
  p=detail(methods().last);p.locator('[data-signature-add=inputs]').click();arg=p.locator('[data-signature-kind=inputs] .feature-io-row').last;arg.locator('[data-signature-name]').fill('amount');pick(arg,'long');p.locator('[data-signature-add=outputs]').click();pick(p.locator('[data-signature-kind=outputs] .feature-io-row').last,'long');p.locator('[data-signature-add=outputs]').click();out=p.locator('[data-signature-kind=outputs] .feature-io-row:has([data-signature-name]:not([readonly]))').last;out.locator('[data-signature-name]').fill('ready');pick(out,'bool');p.locator('button[type=submit]').click();expect(p).to_have_count(0);signature=pending()[0]['signature'];assert signature=={'args':[{'name':'amount','type':'long'},{'name':'ready','type':'bool','mode':'out'}],'return':'long'},signature
  p=detail(methods().last);p.locator('[data-signature-add=inputs]').click();p.locator('[data-detail-cancel]').click();assert pending()[0]['signature']==signature;captured=restart(1);assert f.pending()==captured;expect(methods().last.locator('[data-inline-name]')).to_have_value('정보 계산 😀');f.originals();f.checked('기존 상세 popover의 입력·out/return 타입 편집·취소와 미저장 cold 복원은 native 함수 identity를 유지한다')
  saved('정보 계산 😀');s=schema();fn=next(v for v in s['ownFunctions'] if v['id']==method);assert fn['writable'] and fn['signature']['return']=='long';assert '9223372036854775806' in f.state()['draft']['text'];f.originals();expect(methods().last.locator('[data-function-delete]')).to_be_disabled();f.checked('정보·함수·등록을 같은 후보/CAS로 Save하며 정확한 기본값과 기존 원본을 보존한다')
  methods().last.locator('[data-inline-name]').fill('저장된 기능 이름');p=detail(methods().last);p.locator('[data-signature-kind=inputs] [data-signature-name]').fill('renamed');p.locator('button[type=submit]').click();saved('저장된 기능 이름');captured=restart(2);assert not pending();expect(methods().last.locator('[data-inline-name]')).to_have_value('저장된 기능 이름');fn=next(v for v in schema()['ownFunctions'] if v['id']==method);assert fn['signature']['Args'][0]['Name']=='renamed';f.originals();f.checked('저장된 자체 함수의 이름·미연결 핀 계약 재편집은 소스 proof를 확인하고 Save/cold로 보존한다')
  review=d.review();review.locator('[data-reject]').click();expect(review).to_be_hidden();f.originals();review=d.review()
  if review.locator('[data-review-advanced]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  review.locator('#confirm').click();expect(review).to_have_count(0,timeout=120000);f.idle();source=f.project/('elements/'+method.split('::')[1]+'.celem');assert json.loads(re.search(r'value editorName\s*=\s*("[^;]+");',source.read_text()).group(1))=='저장된 기능 이름' and 'long renamed' in source.read_text();assert {k for k,v in f.original.items() if (f.project/k).read_bytes()!=v}=={'FreeInfo.celem','project.cproj'};f.checked('Review 취소 후 새 명시적 compiler Confirm만 정보/등록/함수 파일을 반영하며 실행·계정 권한을 추가하지 않는다');methods().last.locator('[data-inline-name]').fill('확정 후 재편집');saved('확정 후 재편집');expect(f.owner().locator('[data-element-action=confirm]')).to_be_enabled();review=d.review();review.locator('[data-reject]').click();expect(review).to_be_hidden();assert '저장된 기능 이름'==json.loads(re.search(r'value editorName\s*=\s*("[^;]+");',source.read_text()).group(1));f.checked('확정 후 같은 창의 함수 metadata 재편집도 새 Review 대상으로 유지하며 취소 시 마지막 확정본을 쓰지 않는다');compare_original(methods().last);f.page.screenshot(path=str(f.case/'information-own-functions.png'));assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except Exception:
 try:(f.case/'own-functions-ui-failure.json').write_text(json.dumps({'state':f.state(),'traffic':f.traffic[-90:],'errors':f.errors},ensure_ascii=False,indent=2))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
