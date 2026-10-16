"""Owned Home node creation/removal; no supplied reference runtime is executed."""
import json,uuid,time
from playwright.sync_api import expect

def verify_node_creation(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':1440,'height':1000})
 graph='Example.ButtonGame::NodeValueBody/body:common';before={p:p.read_bytes() for p in project.iterdir() if p.is_file()}
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
 def read():return invoke('blueprint',{'action':'read','id':graph})
 def panel():return page.locator('.window[data-key="blueprint"]')
 def creator():return page.locator('.window').filter(has=page.locator('[data-bp-new-submit]'))
 def front(w):
  key=w.get_attribute('data-key')
  ready();page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name='기능 Blueprint',exact=True).click();ready()
  if key.endswith('/$create'):panel().locator('[data-bp-new-open]').click()
  elif key.startswith('blueprint-code:'):panel().locator('[data-bp-code-open="'+key.rsplit('/',1)[-1]+'"]').click()

 def fill_new(id):
  front(panel());panel().locator('[data-bp-new-open]').click();creator().locator('[data-bp-new-id]').fill(id);creator().locator('[data-bp-new-intent]').fill('Owned independent '+id);creator().locator('[data-bp-new-args]').fill('long value');creator().locator('[data-bp-new-return]').select_option('long')
 def apply_new():creator().locator('[data-bp-new-submit]').click();ready()
 def remove():
  panel().locator('.bp-remove summary').click();panel().locator('[data-bp-remove-ack]').check();panel().locator('[data-bp-remove]').click();ready()
 def confirm():
  panel().locator('[data-bp-review]').click();review=page.locator('.window[data-key="review"]');expect(review.locator('[data-review-advanced]')).to_be_visible(timeout=180000);ready();review.locator('[data-review-advanced]').click();review.locator('[data-advanced-reviewed]').check();expect(page.locator('#confirm')).to_be_enabled();page.locator('#confirm').click();ready()
 page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name='기능 Blueprint',exact=True).click();ready();expect(panel().locator('[data-bp-node]')).to_have_count(2)
 fill_new('ui_pending');old=read();invoke('select',{'id':graph+'/node:calculate'});unit=state()['draft'];record=json.loads(unit['text']);record['source']+=' // peer source pin';invoke('editDraft',{'id':graph+'/node:calculate','text':json.dumps(record),'revision':unit['revision']})
 apply_new();expect(page.locator('#status')).to_contain_text('입력');expect(creator().locator('[data-bp-new-id]')).to_have_value('ui_pending');assert len(read()['nodes'])==2
 invoke('saveDraft',{});page.evaluate('()=>globalThis.confectoryFlushPresentation()');restart();ready();expect(panel().locator('[data-bp-node]')).to_have_count(0)
 front(panel());panel().locator('[data-bp-read]').click();ready();expect(creator().locator('[data-bp-new-id]')).to_have_value('ui_pending');front(creator());apply_new();expect(page.locator('#status')).to_contain_text('기준 재검토');creator().locator('[data-bp-new-rebase]').click();body_box=creator().locator('.window-body').bounding_box();dock=page.locator('#dock').bounding_box()
 for selector in ['[data-bp-new-id]','[data-bp-new-intent]','[data-bp-new-args]','[data-bp-new-control]','[data-bp-new-return]','[data-bp-new-submit]']:
  box=creator().locator(selector).bounding_box();assert box and box['y']>=body_box['y'] and box['y']+box['height']<=body_box['y']+body_box['height']+1,(selector,box,body_box);assert box['x']+box['width']<=dock['x'] or box['y']+box['height']<=dock['y'],(selector,box,dock)
 page.screenshot(path='/tmp/confectory-v480-node-create-form.png',full_page=True);apply_new();expect(panel().locator('[data-bp-node]')).to_have_count(3);creator().locator('[data-close]').click()
 created=read();source=next(s for s in created['sources'] if s['id']==graph+'/node:ui_pending');pending_path=project/source['path'];assert not pending_path.exists();assert next(n for n in created['nodes'] if n['id']=='ui_pending')['pendingSource']
 front(panel());panel().locator('[data-bp-fit]').click();panel().locator('[data-bp-select="ui_pending"]').click();panel().locator('[data-bp-code-open="ui_pending"]').click();code=page.locator('.window').filter(has=page.locator('[data-bp-code]'));code.locator('[data-bp-code]').fill('return value; // unsent input');front(panel());remove();expect(page.locator('#status')).to_contain_text('미적용 입력');assert len(read()['nodes'])==3
 front(code);code.locator('[data-reset]').click();code.locator('[data-close]').click();front(panel());remove();expect(panel().locator('[data-bp-node]')).to_have_count(2);assert not pending_path.exists()
 fill_new('ui_live');apply_new();creator().locator('[data-close]').click();front(panel());panel().locator('[data-bp-fit]').click();panel().locator('[data-bp-code-open="ui_live"]').click();code=page.locator('.window').filter(has=page.locator('[data-bp-code]'));code.locator('[data-bp-code]').fill('throw new System.Exception("Independent body must not execute");');code.locator('[data-apply]').click();ready();code.locator('[data-close]').click();front(panel());confirm()
 created=read();source=next(s for s in created['sources'] if s['id']==graph+'/node:ui_live');path=project/source['path'];assert path.exists();retained=path.read_bytes();assert json.loads(retained)['source'].startswith('throw new System.Exception');assert len(json.loads((project/'node-value.graph.json').read_text())['nodes'])==3
 front(panel());panel().locator('[data-bp-read]').click();ready();panel().locator('[data-bp-select="ui_live"]').click();panel().locator('[data-bp-fit]').click();page.screenshot(path='/tmp/confectory-v480-node-creation.png',full_page=True)
 viewport=panel().locator('.bp-scroll').bounding_box()
 for card in panel().locator('[data-bp-node]').all():
  box=card.bounding_box();assert box and box['x']>=viewport['x'] and box['y']>=viewport['y'] and box['x']+box['width']<=viewport['x']+viewport['width']+1 and box['y']+box['height']<=viewport['y']+viewport['height']+1,(box,viewport)
 expect(panel().locator('[data-bp-remove]')).to_be_disabled();panel().locator('.bp-remove summary').click();panel().locator('[data-bp-remove-ack]').check();panel().locator('[data-bp-remove]').scroll_into_view_if_needed();page.screenshot(path='/tmp/confectory-v480-node-remove-review.png',full_page=True);panel().locator('[data-bp-remove]').click();ready();expect(panel().locator('[data-bp-node]')).to_have_count(2);assert path.read_bytes()==retained and len(json.loads((project/'node-value.graph.json').read_text())['nodes'])==3
 confirm();assert len(json.loads((project/'node-value.graph.json').read_text())['nodes'])==2 and path.read_bytes()==retained
 invoke('saveDraft',{});restart();ready();front(panel());panel().locator('[data-bp-read]').click();ready();expect(panel().locator('[data-bp-node]')).to_have_count(2);assert path.read_bytes()==retained and not pending_path.exists()
 assert all(p.read_bytes()==b for p,b in before.items() if p.name not in ['calculate.node.json','node-value.graph.json']);assert not state()['aiOwnerAvailable'] and not state()['planningOwnerAvailable']
 print('PASS actual v480 node creation/removal: retained cold creation input, peer CAS, explicit source rebase, pending input protection, graph/body group compiler Confirm, existing body preservation and cold no replay',flush=True)
