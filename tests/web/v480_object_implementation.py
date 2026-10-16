"""Actual object-specific graph creation: current contract, no copied function and explicit group publication."""
import uuid,time,hashlib,json,re
from playwright.sync_api import expect

def verify_object_implementation(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':1440,'height':1000});prefix='Example.ButtonGame::';owner=prefix+'Consumer';fn=prefix+'ModuleValue';implementation=prefix+'ConsumerFreshBody';before={p:p.read_bytes() for p in project.iterdir() if p.is_file()}
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
 def panel():return page.locator('.window[data-key="declaration"]')
 def row():return panel().locator('[data-object-provider="'+fn+'"]')
 def field():return row().locator('[data-object-implementation-value]')
 def read():row().locator('[data-object-implementation-read]').click();ready()
 def modules():panel().locator('[data-object-modules-read]').click();ready()
 def nav():
  ready()
  if not page.locator('.nav-menu:visible').count():page.locator('#nav').click()
  page.locator('.nav-menu').get_by_role('button',name='개념',exact=True).click();ready()
  if page.locator('.nav-menu').count():page.locator('#nav').click()
 nav();browser=page.locator('.window[data-key="browser"]');browser.locator('[data-id="'+owner+'"]').press('F2');ready();expect(panel().locator('[data-declaration-id]')).to_have_text(owner);nav();browser.locator('[data-close]').click();modules();expect(row().locator('[data-object-provider-origin]')).to_contain_text(prefix+'ParentConsumer');field().fill(implementation);invoke('saveDraft',{});page.evaluate('()=>globalThis.confectoryFlushPresentation()')
 # Deliberately add saved current source preconditions and a fake authority token: restore keeps only the value.
 current=state();saved=current['presentation'];sections=next(sections for key,sections in saved['inputs']['declarations'] if key.endswith('|'+owner));record=sections['object-implementation:'+fn];record['revision']=current['draft']['revision'];record['hash']=hashlib.sha256(current['draft']['text'].encode()).hexdigest();record['basis']='forged-saved-authority';invoke('savePresentation',{'presentation':saved});restart();ready();expect(panel().locator('[data-declaration-id]')).to_have_text(owner);panel().locator('.caption strong').click();modules();expect(field()).to_have_value(implementation);expect(row().locator('[data-object-implementation-create]')).to_have_count(0);assert all(p.read_bytes()==value for p,value in before.items())
 read();expect(row().locator('[data-object-implementation-contract]')).to_contain_text('long value');expect(row().locator('[data-object-implementation-create]')).to_be_enabled();assert not (project/'elements/ConsumerFreshBody.celem').exists();page.screenshot(path='/tmp/confectory-v480-object-implementation-contract.png',full_page=True)
 unit=state()['draft'];invoke('editDraft',{'id':owner,'revision':unit['revision'],'text':unit['text']+' '});row().locator('[data-object-implementation-create]').click();ready();expect(page.locator('#status')).to_contain_text(re.compile('현재|다시|유지|바뀌'));expect(field()).to_have_value(implementation);assert not (project/'elements/ConsumerFreshBody.celem').exists();modules();read();row().locator('[data-object-implementation-create]').click();ready();expect(panel().locator('[data-object-implementation-open]')).to_be_visible();assert all(p.read_bytes()==value for p,value in before.items());panel().locator('[data-object-implementation-open]').click();ready()
 graph=page.locator('.window[data-key="blueprint"]');expect(graph.locator('[data-bp-code-open="body"]')).to_be_visible();graph.locator('[data-bp-code-open="body"]').click();code=page.locator('.window[data-key^="blueprint-code:"]');expect(code.locator('[data-bp-code]')).to_have_value('');code.locator('[data-bp-code]').fill('return value + 100;');code.locator('[data-apply]').click();ready();expect(code.locator('p').first).to_contain_text('available');invoke('saveDraft',{});page.evaluate('()=>globalThis.confectoryFlushPresentation()');restart();ready();expect(page.locator('#workspace-save-state')).not_to_contain_text('복원 중');page.evaluate('()=>globalThis.confectoryFlushPresentation()');assert not (state()['presentation'] or {}).get('recoveryFailed'),'cold graph/node selection must restore without the presentation recovery failure flag';assert not state().get('sourceError'),'restored declaration window must not inspect graph JSON as a CELEM declaration';panel().locator('[data-close]').click();code.locator('[data-close]').click();page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name='기능 Blueprint',exact=True).click();ready();
 if page.locator('.nav-menu').count():page.locator('#nav').click()
 graph.locator('[data-bp-read]').click();ready();expect(graph.locator('[data-bp-code-open="body"]')).to_be_visible();expect(graph.locator('[data-bp-review]')).to_be_enabled();graph.locator('[data-bp-review]').click();ready()
 review=page.locator('.window[data-key="review"]');expect(review.locator('[data-review-group]')).to_have_count(1,timeout=180000);units={unit['id'] for unit in state()['review']['units']};assert owner in units and implementation in units and fn not in units and len(units)==5;assert set(state()['review']['requiredIds'])==units;assert (project/'ModuleValue.celem').read_bytes()==before[project/'ModuleValue.celem'];review.locator('[data-review-group]').uncheck();expect(page.locator('#confirm')).to_be_disabled();review.locator('[data-review-group]').check();review.locator('[data-review-advanced]').click();review.locator('[data-advanced-reviewed]').check();expect(page.locator('#confirm')).to_be_enabled();page.screenshot(path='/tmp/confectory-v480-object-implementation-review.png',full_page=True);page.locator('#confirm').click();expect(page.locator('#status')).to_have_text('Source confirmed',timeout=180000)
 assert 'provide '+fn+' with '+implementation in (project/'Consumer.celem').read_text();assert (project/'elements/ConsumerFreshBody.celem').exists();assert all(p.read_bytes()==value for p,value in before.items() if p.name not in ['Consumer.celem','project.cpack']);assert 'return value + 100;' not in (project/'module-value.csbody').read_text()
 print('PASS actual v480 object implementation: explicit current owned function contract and ID, restored value without authority, peer owner CAS and input retention, no function/default/body copy, independent blank-to-written graph, cold five-source owner/implementation/graph/node/manifest group, mandatory object selection and explicit compiler Confirm with all other originals preserved',flush=True)
