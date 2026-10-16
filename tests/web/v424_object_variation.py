"""New object inheritance is an ordinary owned draft creation, never a source copy."""
import json,uuid,hashlib
from playwright.sync_api import expect

def verify_object_variation(page,project,mount,send,envelope,settle,restart):
 prefix='Example.ButtonGame::';parent=prefix+'Score';child=prefix+'ScoreVariant';manifest=prefix+'ProjectManifest';originals={p:p.read_bytes() for p in project.glob('*') if p.is_file()}
 def state():
  v=mount();s=v['state'];assert send(envelope(v,'dispose'))['ok'];return s
 def invoke(endpoint,args,ok=True):
  v=mount();request='variation-'+uuid.uuid4().hex;assert send(envelope(v,'invoke',endpoint=endpoint,requestId=request,expectedRevision=v['revision'],input=args))['ok'];result,_=settle(v,request);assert result['ok']==ok,result;assert send(envelope(v,'dispose'))['ok'];return result
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=60000)
 def schema():return page.locator('.window[data-key="schema"]')
 def initial():return schema().locator('[data-schema-field="initial"]')
 def open_dialog():
  page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name='개념',exact=True).click();ready()
  if page.locator('.nav-menu').count():page.locator('#nav').click()
  page.locator('.window[data-key="browser"] [data-id="'+parent+'"]').first.click(button='right');page.get_by_role('button',name='바리에이션 생성',exact=True).click();ready();return page.locator('.modal').filter(has=page.locator('[data-variation-parent]'))
 invoke('select',{'id':manifest});before=state()['draft'];invoke('select',{'id':parent});invoke('schema',{'id':parent});baseline=state()['schema']
 invoke('createVariation',{'id':prefix+'NeverCreated','parent':parent,'revision':baseline['revision'],'hash':'0'*64},False)
 invoke('select',{'id':manifest});after=state()['draft'];assert before['text']==after['text'] and before['revision']==after['revision'];invoke('select',{'id':parent});invoke('schema',{'id':parent});assert not state()['draft']['creationReviewIds']
 modal=open_dialog();expect(modal.locator('[data-variation-parent]')).to_contain_text(parent);modal.locator('#new-declaration-name').fill('CancelledVariation');modal.locator('[data-close]').click();assert not (project/'elements/CancelledVariation.celem').exists() and not state()['draft']['creationReviewIds']
 modal=open_dialog();modal.locator('#new-declaration-name').fill('ScoreVariant');modal.locator('#new-declaration').click();ready();expect(schema().locator('[data-schema-id]')).to_have_text(child);expect(initial()).to_have_value('0');current=state();assert 'extends '+parent in current['draft']['text'] and 'value initial' not in current['draft']['text'];assert set(current['draft']['creationReviewIds'])=={child,manifest};assert current['schema']['metadata'][0]['origin']==parent
 initial().fill('2');initial().locator('..').get_by_role('button',name='Apply field',exact=True).click();ready();schema().locator('[data-override-remove]').click();ready();expect(initial()).to_have_value('0');initial().fill('3');initial().locator('..').get_by_role('button',name='Apply field',exact=True).click();ready();schema().locator('#semantic-save').click();ready();assert not (project/'elements/ScoreVariant.celem').exists()
 for p,original in originals.items():assert p.read_bytes()==original,p.name
 page.evaluate('()=>globalThis.confectoryFlushPresentation()');restart();ready();expect(schema().locator('[data-schema-id]')).to_have_text(child,timeout=30000);expect(initial()).to_have_value('3');assert 'extends '+parent in state()['draft']['text'];assert not (project/'elements/ScoreVariant.celem').exists()
 schema().locator('#semantic-review').click();ready();modal=page.locator('.modal').filter(has=page.locator('#review-creation'));expect(modal.locator('[data-creation-review-id]')).to_have_count(2);modal.locator('#review-creation').click();ready();review=page.locator('.window[data-key="review"]');expect(review.locator('[data-review-unit]')).to_have_count(2);review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
 if ack.count():ack.check()
 page.screenshot(path='/tmp/confectory-v424-object-variation.png',full_page=True);expect(review.locator('#confirm')).to_be_enabled();review.locator('#confirm').click();expect(page.locator('#status')).to_have_text('Source confirmed',timeout=180000);ready()
 text=(project/'elements/ScoreVariant.celem').read_text();assert 'extends '+parent in text and 'value initial = 3;' in text;assert 'element ScoreVariant object' in (project/'project.cpack').read_text()
 for p,original in originals.items():
  if p.name!='project.cpack':assert p.read_bytes()==original,p.name
 print('PASS actual owned object variation: stale parent all-or-refuse, cancellation, inherited values/local reset, creation group, Save/cold restart and ordinary compiler Confirm; parent source unchanged',flush=True)
