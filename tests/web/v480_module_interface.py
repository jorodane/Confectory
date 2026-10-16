"""Owned module contract/default source, inherited origins and private cold input fencing."""
import uuid,time
from playwright.sync_api import expect

def verify_module_interface(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':1440,'height':1000});prefix='Example.ButtonGame::';fn=prefix+'ModuleValue';module=prefix+'Rules';second=prefix+'ModuleSecondBody';before={p:p.read_bytes() for p in project.iterdir() if p.is_file()}
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=180000)
 def state():
  v=mount();s=v['state'];assert send(envelope(v,'dispose'))['ok'];return s
 def invoke(endpoint,args):
  v=mount();request=uuid.uuid4().hex;assert send(envelope(v,'invoke',endpoint=endpoint,requestId=request,expectedRevision=v['revision'],input=args))['ok'];deadline=time.monotonic()+180;result=None
  while time.monotonic()<deadline:
   reply=send(envelope(v,'update'));assert reply['ok'],reply;result=next((r for r in reply.get('results',[]) if r['requestId']==request),None)
   if result:break
   time.sleep(.02)
  assert result and result['ok'],result;assert send(envelope(v,'dispose'))['ok'];return result['result']
 def nav():
  ready()
  if not page.locator('.nav-menu:visible').count():page.locator('#nav').click()
  page.locator('.nav-menu').get_by_role('button',name='모듈',exact=True).click();ready()
  if page.locator('.nav-menu').count():page.locator('#nav').click()
 def panel():return page.locator('.window[data-key="declaration"]')
 def row():return panel().locator('section[data-module-function="'+fn+'"]')
 def open_module():
  nav();browser=page.locator('.window[data-key="browser"]');browser.locator('[data-id="'+module+'"]').click();ready();expect(panel().locator('[data-declaration-id]')).to_have_text(module)
  nav();browser.locator('[data-close]').click();ready()
 def apply():row().locator('[data-module-apply]').click();ready()
 def confirm():
  panel().locator('[data-declaration-review]').click();ready();review=page.locator('.window[data-key="review"]');expect(review.locator('[data-review-advanced]')).to_be_visible(timeout=180000);assert {u['id'] for u in state()['review']['units']}=={module};review.locator('[data-review-advanced]').click()
  ack=review.locator('[data-advanced-reviewed]')
  if ack.count():ack.check()
  expect(page.locator('#confirm')).to_be_enabled();page.locator('#confirm').click();ready()
 open_module();expect(panel().locator('.caption strong')).to_have_text('Rules · 인터페이스');expect(row().locator('.module-contract-flow')).to_contain_text('long');expect(row()).to_contain_text(prefix+'ParentRules');expect(row().locator('[data-module-required]')).not_to_be_checked();expect(row().locator('[data-module-args]')).to_be_disabled();expect(row().locator('[data-module-default]')).to_have_value('')
 checkbox=row().locator('[data-module-required]');label=checkbox.locator('..');assert label.evaluate('n=>getComputedStyle(n).display')=='flex';assert checkbox.bounding_box()['width']<=24
 metadata=state()['declaration']['moduleInterface'];assert metadata['bodyReads']==0 and metadata['providerSelection']=='not-performed' and metadata['status']=='available'
 row().locator('[data-module-default]').fill(second);invoke('saveDraft',{});page.evaluate('()=>globalThis.confectoryFlushPresentation()');restart();ready();expect(panel().locator('.caption strong')).to_have_text('Rules · 인터페이스');panel().locator('.caption strong').click();expect(row().locator('[data-module-default]')).to_have_value(second);apply();expect(page.locator('#status')).to_contain_text('입력의 기준 정보가 없습니다');assert (project/'Rules.celem').read_bytes()==before[project/'Rules.celem']
 panel().locator('[data-module-read]').click();ready();expect(row().locator('[data-module-default]')).to_have_value(second);row().locator('[data-module-rebase]').click();apply();expect(panel().locator('[data-module-status]')).to_contain_text('실행 및 구현 선택 미수행');assert 'require '+fn not in state()['draft']['text'];assert state()['declaration']['moduleInterface']['requirements'][0]['origin']==prefix+'ParentRules';assert (project/'Rules.celem').read_bytes()==before[project/'Rules.celem'];panel().locator('.window-body').evaluate('n=>n.scrollTop=0');expect(row().locator('.module-contract-flow')).to_be_visible();page.screenshot(path='/tmp/confectory-v480-module-contract.png',full_page=True);confirm();assert 'default '+fn+' with '+second in (project/'Rules.celem').read_text()
 # Refuse a stale row after another mounted consumer changes the same owned source.
 open_module();row().locator('[data-module-default]').fill(prefix+'ModuleValueBody');unit=state()['draft'];invoke('editDraft',{'id':module,'revision':unit['revision'],'text':unit['text']+' '});apply();expect(page.locator('#status')).to_contain_text('입력은 유지됩니다');expect(row().locator('[data-module-default]')).to_have_value(prefix+'ModuleValueBody');assert 'default '+fn+' with '+second in state()['draft']['text'];panel().locator('[data-module-read]').click();ready();row().locator('[data-module-rebase]').click();apply()
 # An unfinished local signature is visible as unavailable; corrections remain one source.
 row().locator('[data-module-required]').check();row().locator('[data-module-args]').fill('int');apply();expect(panel().locator('[data-module-status]')).to_contain_text('CONTRACT_MISMATCH');assert 'default '+fn+' with '+second in (project/'Rules.celem').read_text();row().locator('[data-module-args]').fill('long');apply();expect(panel().locator('[data-module-status]')).to_contain_text('실행 및 구현 선택 미수행');row().locator('[data-module-remove]').click();ready();expect(row().locator('[data-module-required]')).not_to_be_checked();expect(row()).to_contain_text(prefix+'ParentRules');expect(row().locator('[data-module-default]')).to_have_value('');confirm();open_module();panel().locator('.window-body').evaluate('n=>n.scrollTop=0');expect(row().locator('.module-contract-flow')).to_be_visible();page.screenshot(path='/tmp/confectory-v480-module-interface.png',full_page=True);assert 'require '+fn not in (project/'Rules.celem').read_text() and 'default '+fn not in (project/'Rules.celem').read_text();assert all(p.read_bytes()==b for p,b in before.items() if p.name!='Rules.celem')
 # Detached module view keeps its own source while the primary selection changes.
 panel().locator('[data-declaration-keep]').click();ready();bound=page.locator('.window[data-key="editor-1"]');expect(bound.locator('[data-declaration-id]')).to_have_text(module);invoke('select',{'id':fn});bound.locator('[data-module-read]').click();ready();expect(bound.locator('[data-module-status]')).to_contain_text('실행 및 구현 선택 미수행');bound.locator('section[data-module-function="'+fn+'"] [data-module-default]').fill(second);bound.locator('section[data-module-function="'+fn+'"] [data-module-apply]').click();ready();expect(bound.locator('section[data-module-function="'+fn+'"] [data-module-default]')).to_have_value(second);assert state()['draft']['id']==fn and 'default '+fn not in (project/'Rules.celem').read_text();bound.locator('section[data-module-function="'+fn+'"] [data-module-remove]').click();ready();expect(bound.locator('section[data-module-function="'+fn+'"] [data-module-default]')).to_have_value('');assert all(p.read_bytes()==b for p,b in before.items() if p.name!='Rules.celem')
 print('PASS actual v480 module interface: inherited contract origins, cold private input rebase, peer CAS, typed contract/default source edits, mismatch status, explicit compiler Confirm and preserved parent/provider/consumer sources',flush=True)
