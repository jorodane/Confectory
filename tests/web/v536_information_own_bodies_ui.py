"""Primary information own body UI over real fixture engine; no accounts or project execution."""
import json,re,time,shutil,subprocess
from playwright.sync_api import sync_playwright,expect
import v536_field_definitions_ui as d
f=d.f;owner=d.owner

def method():return f.owner().locator('[data-inline-method]').last
def graph():return f.author().locator('[data-bp-node=body]')
def open_body():
 f.idle();method().locator('[data-function-write-direct],[data-function-edit]').click();expect(graph()).to_be_visible();expect(f.author().locator('[data-bp-name]')).to_have_value('자체 실행 😀');expect(f.owner().locator('.object-title-description')).to_be_editable();assert f.state()['draft']['id']==owner

def script(text,save=True):
 f.author().locator(':scope > .window-title .caption').click(position={'x':4,'y':5});f.author().locator('[data-bp-overview-node=body]').click();graph().locator('[data-internal-code]').click();dialog=f.page.locator('.bp-script-dialog');value=dialog.locator('[data-code-source]');expect(value).to_be_visible();value.evaluate(r'''el=>{el.focus();const a=el.value.indexOf('\n{\n')+3,b=el.value.lastIndexOf('\n}');if(a<3||b<a)throw Error('protected body range');el.setSelectionRange(a,b);}''');f.page.keyboard.insert_text(text);dialog.locator('[data-code-save]' if save else '[data-code-cancel]').click();expect(dialog).to_have_count(0)

def restart(i):
 held=f.pending();f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1850,'height':1450});expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo');f.idle();return held

def save_body():
 f.author().locator('[data-bp-save]').click();expect(f.author().locator('.bp-status')).not_to_have_text('저장 중…');deadline=time.monotonic()+60
 while time.monotonic()<deadline:
  if not [v for key,v in f.pending()['blueprint'] if '|v508-author|' in key]:f.idle();return
  f.page.wait_for_timeout(30)
 raise AssertionError((f.author().locator('.bp-status').all_text_contents(),f.pending()))
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{})
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1850,'height':1450});d.open_info();f.owner().locator('[data-function-add]').click();method().locator('[data-inline-name]').fill('자체 실행 😀');method().locator('[data-inline-description]').fill('실제 정보 함수의 본문');fn=next(v['id'] for _,v in d.pending() if v['kind']=='function-add');open_body();checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();members={v['id'] for v in json.loads(before)['changes']};assert {owner,fn,f.n+'ProjectManifest',fn+'BlueprintBody',fn+'BlueprintBody/body:common',fn+'BlueprintBody/body:common/node:body'}==members;f.originals();f.checked('원본 직접 작성은 미저장 정의부터 같은 정보 소유의 첫 구현·등록·graph/node를 완전한 checkpoint로 보관하고 정보 선택과 표시명을 유지한다')
  f.close_author();restart(1);open_body();assert checkpoint.read_bytes()==before;script('return; // 취소',False);assert not [v for key,v in f.pending()['blueprint'] if '|v508-author|' in key];f.originals();f.checked('아직 본문이 없는 저장 구현도 실제 cold/편집으로 열리고 C# 취소는 원래 source·초안을 쓰지 않는다')
  script('return;');save_body();f.originals();f.close_author();restart(2);open_body();graph().locator('[data-internal-code]').click();dialog=f.page.locator('.bp-script-dialog');expect(dialog.locator('[data-code-source]')).to_have_value(re.compile(r'return;'));dialog.locator('[data-code-cancel]').click();f.checked('정보 자체 C# 본문은 기존 bound slot의 실제 Save/cold로 복원하며 전역 함수 기본 구현과 원본을 바꾸지 않는다')
  script('return; // 미저장 한글 😀');held=f.pending();f.close_author();restart(3);assert f.pending()==held;open_body();graph().locator('[data-internal-code]').click();dialog=f.page.locator('.bp-script-dialog');expect(dialog.locator('[data-code-source]')).to_have_value(re.compile('미저장 한글'));dialog.locator('[data-code-cancel]').click();save_body();f.close_author();f.originals();f.checked('창 닫기와 재시작 후에도 함수의 private 본문 입력을 소스 identity/hash에 결부해 보존하고 같은 표시명으로 다시 편집한다')
  review=d.review();review.locator('[data-reject]').click();expect(review).to_be_hidden();f.originals();review=d.review()
  if review.locator('[data-review-advanced]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  review.locator('#confirm').click();expect(review).to_have_count(0,timeout=120000);f.idle();assert {name for name,value in f.original.items() if (f.project/name).read_bytes()!=value}=={'FreeInfo.celem','project.cproj'};source=f.project/('elements/'+fn.split('::')[1]+'.celem');assert 'provide' not in source.read_text();assert 'provide '+fn+' with '+fn+'BlueprintBody' in (f.project/'FreeInfo.celem').read_text();f.checked('Review 취소 뒤 새 compiler Confirm만 완전한 정보/함수/본문 그룹을 반영하며 다른 원본과 함수의 전역 default는 유지한다')
  open_body();script('return; // 확정 후 다시');save_body();f.close_author();expect(f.owner().locator('[data-element-action=confirm]')).to_be_enabled();f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts};review=d.review();review.locator('[data-reject]').click();f.originals();f.checked('확정 후 같은 함수의 본문 재편집도 새로운 Review를 요구하며 취소 시 마지막 확정본을 쓰지 않는다');f.page.screenshot(path=str(f.case/'information-own-body.png'));assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except Exception:
 try:(f.case/'own-body-ui-failure.json').write_text(json.dumps({'state':f.state(),'traffic':f.traffic[-100:],'errors':f.errors,'checks':f.checks},ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'own-body-ui-failure.png'))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
