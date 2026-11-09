"""Shared function-detail IME Escape routing; synthetic events are not physical IME validation."""
import json,pathlib,sys,traceback,copy
from playwright.sync_api import sync_playwright,expect
import v666_root_input_name_recovery_fixture as t
x=t.x;f=t.f;mode=sys.argv[3]if len(sys.argv)>3 else'normal';raw='한글 조합 중 설명 α 😀';name='draft_units'
def declaration():return f.page.locator('.window[data-key=declaration]')
def pop():return f.page.locator('.function-detail-popover')
def picker():return f.page.locator('.property-type-popover')
def has(text):return text in json.dumps(f.pending(),ensure_ascii=False)
def show():
 f.idle();f.page.locator('#workspace').click(button='right',position={'x':1300,'y':300});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.get_by_role('button',name='기능',exact=True).click();b.locator('[data-browser-control=object-query]').fill(t.feature.split('::')[-1]);b.locator('[data-browser-control=object-search]').click();b.locator('[data-object="'+t.feature+'"]').press('Enter');b.locator('[data-close]').first.click();f.idle();expect(declaration().locator('.object-info-button')).to_be_visible()
def open_popup():
 declaration().locator('.object-info-button').click();expect(pop()).to_be_visible();pop().locator('[data-detail-description]').fill(raw);pop().locator('[data-signature-kind=inputs] [data-signature-name]').first.fill(name)
def ime(field,legacy=False):
 observed=field.evaluate("(el,legacy)=>{el.dispatchEvent(new CompositionEvent('compositionstart',{data:'한',bubbles:true}));const e=new KeyboardEvent('keydown',{key:'Escape',code:'Escape',bubbles:true,cancelable:true,isComposing:!legacy,keyCode:legacy?229:27});el.dispatchEvent(e);el.dispatchEvent(new CompositionEvent('compositionend',{data:'한',bubbles:true}));return {composing:e.isComposing,keyCode:e.keyCode,trusted:e.isTrusted};}",legacy);assert observed==dict(composing=not legacy,keyCode=229 if legacy else 27,trusted=False),observed
def preserved():
 expect(pop()).to_be_visible();expect(pop().locator('[data-detail-description]')).to_have_value(raw);expect(pop().locator('[data-signature-kind=inputs] [data-signature-name]').first).to_have_value(name)
def original():assert checkpoint.read_bytes()==before; x.original()
def exercise(target,legacy=False):
 open_popup()
 if target=='parent':field=pop().locator('[data-detail-description]')
 else:pop().locator('[data-signature-kind=inputs] [data-signature-type]').first.click();expect(picker()).to_be_visible();field=picker().locator('[type=search]');field.fill('정')
 ime(field,legacy)
 if mode=='baseline':
  expect(pop()if target=='parent'else picker()).to_have_count(0)
  if pop().count():pop().locator('[data-detail-cancel]').click()
  original();assert not has(raw)and not has(name);f.checked('published 833617c7 '+target+' '+('keyCode229'if legacy else'isComposing')+' Escape closes editor/search and loses uncommitted composition input; original/checkpoint unchanged');return
 preserved()
 if target=='picker':
  expect(picker()).to_be_visible();expect(picker().locator('[type=search]')).to_have_value('정');f.page.keyboard.press('Escape');expect(picker()).to_have_count(0);preserved()
 f.page.keyboard.press('Escape');expect(pop()).to_have_count(0);original();assert not has(raw)and not has(name);f.checked(target+' '+('keyCode229'if legacy else'isComposing')+' keeps composition text/contract draft; ordinary Escape still cancels picker then popup without source writes')
def review():
 declaration().locator('[data-feature-action=confirm]').click();f.idle()
 if f.page.locator('#review-creation').is_visible():f.page.locator('#review-creation').click();f.idle()
 f.page.locator('.window[data-key=review]:visible,.window[data-key=targets]:visible').first.wait_for(state='visible',timeout=90000);targets=f.page.locator('.window[data-key=targets]')
 if targets.is_visible():targets.locator('[data-target-choice]').select_option('portable');targets.locator('[data-close]').click();declaration().locator('[data-feature-action=confirm]').click();f.idle()
 r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=90000)
 if r.locator('[data-review-advanced]').is_visible():r.locator('[data-review-advanced]').click()
 if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
 return r
def restart(i):f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});show()
def main():
 show()
 for target in ['parent','picker']:
  for legacy in [False,True]:exercise(target,legacy)
 if mode=='baseline':return
 for _ in range(2):open_popup();pop().locator('[data-detail-cancel]').click();expect(pop()).to_have_count(0);original()
 f.checked('repeated explicit cancel releases shared editor/picker listeners and leaves draft/source/contracts unchanged')
 if mode!='normal':
  restart(1);original();assert not has(raw)and not has(name);open_popup();ime(pop().locator('[data-signature-kind=inputs] [data-signature-name]').first);preserved();pop().locator('[data-detail-close]').click();expect(pop()).to_have_count(0);original();f.page.screenshot(path=str(f.case/'signature-ime-cancel.png'),timeout=5000);f.checked('cold reopen uses a current owned editor; explicit close still discards only its private popup copy');return
 declaration().locator('.object-info-button').click();expect(pop()).to_be_visible();pop().locator('[data-detail-description]').fill(raw);ime(pop().locator('[data-detail-description]'));expect(pop()).to_be_visible();pop().get_by_role('button',name='저장',exact=True).click();expect(pop()).to_have_count(0);assert has(raw);original();declaration().locator('[data-feature-action=save]').click();f.idle();assert not has(raw);x.original();restart(2);assert not has(raw);expect(declaration().locator('[data-inline-description]')).to_have_value(raw);x.original();f.checked('explicit unchanged-contract Save after IME cancellation preserves description in the checkpoint across cold, original C# untouched')
 r=review();r.locator('[data-reject]').click();x.original();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();assert (f.project/'Pair.celem').read_bytes()!=physical[f.project/'Pair.celem'];assert all(p.read_bytes()==v for p,v in physical.items()if p!=f.project/'Pair.celem');x.build('signature-ime-original-execution',10,'body\n10');restart(3);expect(declaration().locator('[data-inline-description]')).to_have_value(raw);assert not has(raw)and not has(name)and not f.errors and not f.external;f.page.screenshot(path=str(f.case/'signature-ime-saved.png'),timeout=5000);f.checked('Review cancel/explicit Confirm/cold and actual result10 preserve function/parameter identities, original C# and caller contract')
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();physical=x.physical.copy()
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400})
  try:main()
  except Exception as error:
   (f.case/'failure-exception.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc(),errors=f.errors),ensure_ascii=False));print(traceback.format_exc(),flush=True)
   try:f.page.screenshot(path=str(f.case/'failure.png'),timeout=5000)
   except Exception:pass
   raise
  f.browser.close()
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));f.stop()
print('SIGNATURE_IME_UI',f.case,flush=True)
