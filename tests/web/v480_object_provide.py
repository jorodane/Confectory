"""Actual owned object module provider rows, pure contract read and compiler source publication."""
import uuid,time,re,hashlib
from playwright.sync_api import expect

def verify_object_provide(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':1440,'height':1000});prefix='Example.ButtonGame::';id=prefix+'Consumer';fn=prefix+'ModuleValue';second=prefix+'ModuleSecondBody';before={p:p.read_bytes() for p in project.iterdir() if p.is_file()}
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
  page.locator('.nav-menu').get_by_role('button',name='개념',exact=True).click();ready()
  if page.locator('.nav-menu').count():page.locator('#nav').click()
 def restore_guard_fixture():
  current=state();saved=current['presentation'];info=current['draft'];sections=next(sections for key,sections in saved['inputs']['declarations'] if key.endswith('|'+id));record=sections['object-provider:'+fn];record['revision']=info['revision'];record['hash']=hashlib.sha256(info['text'].encode('utf-8')).hexdigest();invoke('savePresentation',{'presentation':saved})
 def panel():return page.locator('.window[data-key="declaration"]')
 def row(root=None):return (root if root is not None else panel()).locator('[data-object-provider="'+fn+'"]')
 def open_object():
  nav();browser=page.locator('.window[data-key="browser"]');browser.locator('[data-id="'+id+'"]').press('F2');ready();expect(panel().locator('[data-declaration-id]')).to_have_text(id);nav();browser.locator('[data-close]').click()
 def read():panel().locator('[data-object-modules-read]').click();ready()
 def apply():row().locator('[data-object-provider-apply]').click();ready()
 def confirm(valid=True):
  panel().locator('[data-declaration-review]').click();ready();review=page.locator('.window[data-key="review"]');expect(review.locator('[data-review-advanced]')).to_be_visible(timeout=180000);assert {unit['id'] for unit in state()['review']['units']}=={id};review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
  if ack.count():ack.check()
  expect(page.locator('#confirm')).to_be_enabled();page.locator('#confirm').click();ready()
  if valid:expect(page.locator('#status')).to_have_text('Source confirmed')
 open_object();read();expect(row().locator('[data-object-provider-origin]')).to_contain_text(prefix+'ParentConsumer');expect(row().locator('[data-object-provider-origin]')).to_contain_text('선언 계약 확인');expect(row().locator('[data-object-provider-value]')).to_have_value('');meta=state()['declaration']['appliedModules'];assert meta['providerSelection']=='not-performed' and meta['bodyReads']==0
 row().locator('[data-object-provider-value]').fill(second);invoke('saveDraft',{});page.evaluate('()=>globalThis.confectoryFlushPresentation()');restore_guard_fixture();restart();ready();expect(panel().locator('[data-declaration-id]')).to_have_text(id);panel().locator('.caption strong').click();expect(row().locator('[data-object-provider-value]')).to_have_value(second);apply();expect(page.locator('#status')).to_contain_text(re.compile('기준 정보|현재 모듈 구성'));read();apply();expect(page.locator('#status')).to_contain_text('입력의 기준 정보가 없습니다');row().locator('[data-object-provider-rebase]').click();apply();expect(row().locator('[data-object-provider-origin]')).to_contain_text(second+' ← '+id);assert (project/'Consumer.celem').read_bytes()==before[project/'Consumer.celem'];panel().locator('.window-body').evaluate('el=>el.scrollTop=0');expect(row().locator('[data-object-provider-contract]')).to_be_visible();page.screenshot(path='/tmp/confectory-v480-object-provider-contract.png',full_page=True);confirm();assert 'provide '+fn+' with '+second in (project/'Consumer.celem').read_text()
 open_object();read();row().locator('[data-object-provider-value]').fill(prefix+'ModuleValueBody');unit=state()['draft'];invoke('editDraft',{'id':id,'revision':unit['revision'],'text':unit['text']+' '});apply();expect(page.locator('#status')).to_contain_text('입력은 유지됩니다');expect(row().locator('[data-object-provider-value]')).to_have_value(prefix+'ModuleValueBody');assert 'provide '+fn+' with '+second in state()['draft']['text'];read();row().locator('[data-object-provider-rebase]').click();apply()
 row().locator('[data-object-provider-value]').fill(prefix+'MainBody');apply();expect(row().locator('[data-object-provider-origin]')).to_contain_text('IMPLEMENTATION_ID');confirmed=(project/'Consumer.celem').read_text();confirm(False);assert (project/'Consumer.celem').read_text()==confirmed;review=page.locator('.window[data-key="review"]')
 if review.count():review.locator('[data-close]').click()
 open_object();read();row().locator('[data-object-provider-remove]').click();ready();expect(row().locator('[data-object-provider-origin]')).to_contain_text(prefix+'ParentConsumer');expect(row().locator('[data-object-provider-value]')).to_have_value('');confirm();assert 'provide '+fn not in (project/'Consumer.celem').read_text();open_object();read();panel().locator('.window-body').evaluate('el=>el.scrollTop=0');page.screenshot(path='/tmp/confectory-v480-object-provider.png',full_page=True)
 panel().locator('[data-declaration-keep]').click();ready();bound=page.locator('.window[data-key="editor-1"]');expect(bound.locator('[data-declaration-id]')).to_have_text(id);invoke('select',{'id':fn});bound.locator('[data-object-modules-read]').click();ready();row(bound).locator('[data-object-provider-value]').fill(second);row(bound).locator('[data-object-provider-apply]').click();ready();expect(row(bound).locator('[data-object-provider-origin]')).to_contain_text(second+' ← '+id);assert state()['draft']['id']==fn and 'provide '+fn not in (project/'Consumer.celem').read_text();row(bound).locator('[data-object-provider-remove]').click();ready();expect(row(bound).locator('[data-object-provider-value]')).to_have_value('');assert all(p.read_bytes()==value for p,value in before.items() if p.name!='Consumer.celem')
 print('PASS actual v480 object module provider: inherited origins/current declaration contract, no chosen/compiled state, cold private input/current read/rebase, peer CAS, incompatible provider actual compiler refusal, explicit one-source Confirm/removal, detached own view and unchanged module/parent/provider/function/Main sources',flush=True)
