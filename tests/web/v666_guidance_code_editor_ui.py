"""Formal guidance in the real C# editor with rejection, cold and compiler CAS."""
import ast,copy,json,pathlib,sys
from playwright.sync_api import sync_playwright,expect
import v666_root_execution_fixture as x
f=x.f;mode=sys.argv[3]if len(sys.argv)>3 else'normal'
helper=pathlib.Path(__file__).with_name('v666_async_transition_ui.py');names={'panel','pending','open_graph','save','restart','review'}
exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),str(helper),'exec'))
def editor():
 panel().locator('[data-bp-overview-node=choose]').click();panel().locator('[data-bp-node=choose] [data-internal-code]').click();d=f.page.locator('.bp-script-dialog');expect(d).to_be_visible();return d
def replace(d,old,new):
 field=d.locator('[data-code-source]');field.evaluate('(el,text)=>{const i=el.value.indexOf(text);if(i<0)throw Error("Editable region missing");el.focus();el.setSelectionRange(i,i+text.length)}',old);f.page.keyboard.insert_text(new)if new else f.page.keyboard.press('Backspace')
def body(d,text):replace(d,d.locator('[data-code-region=body]').text_content(),text)
def unchanged(held):
 now=dict(pending());return all(k in now and all(now[k].get(p)==v.get(p)for p in ['type','node','text'])for k,v in held)
def review_guidance(r):
 if '--review-guidance'not in sys.argv:return
 expect(r).to_contain_text('확정할 변경을 선택하십시오. 같은 객체의 변경은 함께 선택됩니다. 최종 소스는 Confirm에서만 반영됩니다.')
 expect(r.locator('[data-review-source]')).to_contain_text('변경 전 소스');expect(r.locator('[data-review-source]')).to_contain_text('변경 후 소스')
 checks=r.locator('[data-review-group]');confirm=r.locator('#confirm');ack=r.locator('[data-advanced-reviewed]');assert checks.count()
 for i in range(checks.count()):checks.nth(i).uncheck()
 expect(confirm).to_be_disabled();expect(r.locator('[data-review-selection-status]')).to_have_text('선택한 변경이 없습니다. 취소하거나 다시 선택하십시오.')
 for i in range(checks.count()):checks.nth(i).check()
 if ack.count():expect(confirm).to_be_disabled();expect(ack).not_to_be_checked();ack.check()
 expect(confirm).to_be_enabled();x.original();f.checked('검토 안내·실제 전후 소스·빈 선택 거절과 재선택 뒤 고급 확인 초기화를 원본 미변경 상태에서 확인한다')
try:
 f.start(0);f.invoke('select',dict(id=x.feature));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph()
  d=editor();expect(d.locator('.bp-script-guide')).to_contain_text('enum·본문·보조 함수를 편집하십시오.');field=d.locator('[data-code-source]');old=field.input_value();field.evaluate('el=>{el.focus();el.setSelectionRange(0,0)}');f.page.keyboard.insert_text('RejectedHeader');assert field.input_value()==old;expect(d.locator('[data-code-status]')).to_have_text('고정된 선언은 수정할 수 없습니다. enum·매개변수·본문·보조 함수 영역 안에서 편집해 주십시오.');assert not pending()and checkpoint.read_bytes()==before;x.original()
  replace(d,'Positive = 1','Positive = invalid_value');bad=field.input_value();d.locator('[data-code-save]').click();expect(d.locator('[data-code-error]')).to_have_text('enum 항목은 이름 또는 이름 = 정수 형식으로 작성해 주십시오.');assert field.input_value()==bad and not pending()and checkpoint.read_bytes()==before;x.original();d.locator('[data-code-cancel]').click();assert not pending();f.checked('v666 고정 영역/enum 형식 안내를 표시하고 거절 뒤 입력·원문·checkpoint와 취소 동작을 보존한다')
  d=editor();original=d.locator('[data-code-region=body]').text_content();text=original+'\n// 명시적으로 편집한 본문 😀';body(d,text);d.locator('[data-code-source]').press('Control+z');assert text not in d.locator('[data-code-source]').input_value();d.locator('[data-code-source]').press('Control+y');assert text in d.locator('[data-code-source]').input_value();d.locator('[data-code-cancel]').click();assert not pending();x.original()
  d=editor();body(d,'UnknownV666GuidanceSymbol();\n'+original);d.locator('[data-code-save]').click();held=copy.deepcopy(pending());assert len(held)==1;restart(1);assert unchanged(held);x.original();f.checked('코드 Undo/Redo·취소와 명시 편집의 cold 복원은 안내 문체와 무관하게 기존 C# 입력을 보존한다')
  if mode=='storage':
   prior=checkpoint.read_bytes();checkpoint.chmod(0o400)
   try:panel().locator('[data-bp-save]').click();f.idle();assert unchanged(held)and checkpoint.read_bytes()==prior
   finally:checkpoint.chmod(0o600)
   x.original();restart(2);assert unchanged(held);f.checked('checkpoint 쓰기 실패 뒤 cold와 명시 재시도는 개인 C# 입력과 기존 checkpoint를 보존한다')
  save();r=review();review_guidance(r);invalid=checkpoint.read_bytes();mark=len(f.traffic);r.locator('#confirm').click();f.idle();raw=[f.state(),f.traffic[mark:]];(f.case/'compiler-failure.json').write_text(json.dumps(raw,ensure_ascii=False));assert 'CS0103'in json.dumps(raw)and'UnknownV666GuidanceSymbol'in json.dumps(raw),'Compiler diagnostic must remain verbatim';assert checkpoint.read_bytes()==invalid;x.original();expect(r).to_be_visible();r.locator('[data-reject]').click();expect(r).to_be_hidden();f.checked('실제 compiler Confirm의 CS0103 원문 응답과 미확정 상태를 유지하며 원본·초안을 보존한다')
  d=editor();replace(d,'UnknownV666GuidanceSymbol();\n','');body(d,text);d.locator('[data-code-save]').click();save();r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();x.original();r=review();held=checkpoint.read_bytes();p=f.project/'Flow.node.json';old=p.read_bytes();p.write_bytes(old+b' ')
  try:
   r.locator('#confirm').click();f.idle();assert checkpoint.read_bytes()==held;assert p.read_bytes()==old+b' ';assert all(p.read_bytes()==value for p,value in x.physical.items()if p.name!='Flow.node.json')
  finally:p.write_bytes(old)
  x.original();f.idle();
  if r.is_visible():r.locator('[data-reject]').click()
  r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();actual=json.loads((f.project/'Flow.node.json').read_text())['source'];assert actual==x.original_source+'\n// 명시적으로 편집한 본문 😀';assert all(p.read_bytes()==old for p,old in x.physical.items()if p.name not in ['Flow.graph.json','Flow.node.json']);assert json.loads((f.project/'After.node.json').read_text())['source']==json.loads(x.physical[f.project/'After.node.json'])['source'];x.build('guidance-code-execution',10,'callee:1\nafter:10');restart(3);assert x.read()['diagnostics']['state']=='source-ready';d=editor();assert text in d.locator('[data-code-source]').input_value();d.locator('[data-code-cancel]').click();assert not pending();assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'code-guidance-final.png'),full_page=True);f.checked('명시 수정·반복 저장·Review 취소/최종 CAS 거절/Confirm·실제 실행·확정 cold는 원래 계약/분기/출력을 유지한다');f.browser.close()
except Exception:
 try:f.page.screenshot(path=str(f.case/'failure.png'));(f.case/'failure.html').write_text(f.page.content())
 except Exception:pass
 raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));f.stop()
print('CODE_GUIDANCE_FIXTURE',f.case,flush=True)
