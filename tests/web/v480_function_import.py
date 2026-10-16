"""Actual whole implementation import; donor C# and slot contract stay in their original sources."""
import uuid,time,hashlib,re
from playwright.sync_api import expect

def verify_function_import(page,project,registered,counter,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':1440,'height':1000});prefix='Example.ButtonGame::';owner=prefix+'Consumer';fn='ReferenceApi::Value';donor=prefix+'ImportedDouble';implementation=prefix+'ConsumerImportedBody';before={p:p.read_bytes() for folder in [project,registered] for p in folder.iterdir() if p.is_file()}
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
 nav();browser=page.locator('.window[data-key="browser"]');browser.locator('[data-id="'+owner+'"]').press('F2');ready();nav();browser.locator('[data-close]').click();modules();field().fill(implementation);row().locator('[data-object-implementation-mode]').select_option('reference');row().locator('[data-object-import-query]').fill('ImportedDouble');row().locator('[data-object-import-list]').click();ready();row().locator('[data-object-import-reference]').select_option(donor);invoke('saveDraft',{});page.evaluate('()=>globalThis.confectoryFlushPresentation()')
 current=state();saved=current['presentation'];sections=next(sections for key,sections in saved['inputs']['declarations'] if key.endswith('|'+owner));record=sections['object-implementation:'+fn];record['revision']=current['draft']['revision'];record['hash']=hashlib.sha256(current['draft']['text'].encode()).hexdigest();record['basis']='forged-import-authority';record['contract']={'target':'forged','reference':donor};invoke('savePresentation',{'presentation':saved});restart();ready();panel().locator('.caption strong').click();modules();expect(field()).to_have_value(implementation);expect(row().locator('[data-object-implementation-mode]')).to_have_value('reference');expect(row().locator('[data-object-import-reference]')).to_have_value(donor);expect(row().locator('[data-object-import-query]')).to_have_value('ImportedDouble');expect(row().locator('[data-object-implementation-create]')).to_have_count(0);assert all(p.read_bytes()==b for p,b in before.items()) and not counter.exists()
 read();expect(row().locator('[data-object-implementation-contract]')).to_contain_text('(long value) → long');expect(row().locator('[data-object-import-contract]')).to_contain_text('(long input) → long');expect(row().locator('[data-object-implementation-origin]')).to_contain_text('읽기 전용');page.screenshot(path='/tmp/confectory-v480-function-import-contract.png',full_page=True)
 path=registered/'Value.celem';original=path.read_text();path.write_text(original+' ');row().locator('[data-object-implementation-create]').click();ready();expect(page.locator('#status')).to_contain_text(re.compile('현재|다시|유지|바뀌'));expect(field()).to_have_value(implementation);assert not (project/'elements/ConsumerImportedBody.celem').exists();path.write_text(original);read();row().locator('[data-object-implementation-create]').click();ready();panel().locator('[data-object-implementation-open]').click();ready()
 graph=page.locator('.window[data-key="blueprint"]');expect(graph.locator('[data-bp-node]')).to_have_count(1);expect(graph.locator('[data-bp-code-open]')).to_have_count(0);expect(graph.locator('[data-bp-task]')).to_have_count(0);invoke('saveDraft',{});page.evaluate('()=>globalThis.confectoryFlushPresentation()');restart();ready();page.evaluate('()=>globalThis.confectoryFlushPresentation()');assert not (state()['presentation'] or {}).get('recoveryFailed') and not state().get('sourceError');panel().locator('[data-close]').click();page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name='기능 Blueprint',exact=True).click();ready()
 if page.locator('.nav-menu').count():page.locator('#nav').click()
 graph.locator('[data-bp-read]').click();ready();expect(graph.locator('[data-bp-node]')).to_have_count(1);graph.locator('[data-bp-review]').click();ready();review=page.locator('.window[data-key="review"]');expect(review.locator('[data-review-group]')).to_have_count(1,timeout=180000);units={unit['id'] for unit in state()['review']['units']};assert owner in units and implementation in units and fn not in units and donor not in units and len(units)==4;assert set(state()['review']['requiredIds'])==units;review.locator('[data-review-group]').uncheck();expect(page.locator('#confirm')).to_be_disabled();review.locator('[data-review-group]').check();review.locator('[data-review-advanced]').click();review.locator('[data-advanced-reviewed]').check();page.screenshot(path='/tmp/confectory-v480-function-import-review.png',full_page=True);page.locator('#confirm').click();expect(page.locator('#status')).to_have_text('Source confirmed',timeout=180000);assert not counter.exists()
 assert 'provide '+fn+' with '+implementation in (project/'Consumer.celem').read_text();assert 'import '+donor+' as fg_call_' in (project/'elements/ConsumerImportedBody.celem').read_text();assert not list(project.glob('blueprints/nodes/*.node.json'));assert all(p.read_bytes()==b for p,b in before.items() if p.name not in ['Consumer.celem','project.cpack']);graph.locator('[data-bp-reference="imported"]').click();ready();assert state()['draft']['id']==donor
 print('PASS actual v480 module function import: value-only mode/donor restore and no forged authority, exact target/donor typed positional contract, raw required function CAS, one reference/no C# or Task source, clean cold, four-source mandatory Review and compiler Confirm, no donor execution and unchanged original C# with source navigation',flush=True)
