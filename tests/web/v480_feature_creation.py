"""Actual new function contract -> owned graph -> explicit source group compiler publication."""
import json,uuid,time
from playwright.sync_api import expect

def verify_feature_creation(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':1440,'height':1000});feature='Example.ButtonGame::FreshFeature';before={p:p.read_bytes() for p in project.iterdir() if p.is_file()}
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
 def nav(name):
  ready();page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name=name,exact=True).click();ready()
  if page.locator('.nav-menu').count():page.locator('#nav').click()
 def declaration():return page.locator('.window[data-key="declaration"]')
 def graph_panel():return page.locator('.window[data-key="blueprint"]')
 def read_graph():return invoke('blueprint',{'action':'read','id':graph})
 nav('기능');browser=page.locator('.window[data-key="browser"]');browser.locator('[data-new]').click();page.get_by_role('button',name='기능 생성',exact=True).click();page.locator('#new-declaration-name').fill('FreshFeature');page.locator('#new-declaration').click();ready();expect(declaration().locator('[data-declaration-id]')).to_have_text(feature)
 # Close the actual browser, so the real declaration controls are unobstructed.
 if browser.count():nav('기능');browser.locator('[data-close]').click()
 panel=declaration();panel.locator('[data-add-argument]').click();panel.locator('[data-arg-name]').fill('count');panel.locator('[data-arg-type]').select_option('long');panel.locator('[data-return]').select_option('long');panel.locator('[data-signature-apply]').click();ready();panel.locator('[data-decl-property="description"]').fill('Fresh feature adds nine');panel.locator('[data-properties-apply]').click();ready()
 panel.locator('[data-feature-read]').click();ready();expect(panel.locator('[data-feature-contract]')).to_contain_text('(long count) → long');assert not (project/'elements/FreshFeature.celem').exists()
 unit=state()['draft'];invoke('editDraft',{'id':feature,'revision':unit['revision'],'text':unit['text']+' '});panel.locator('[data-feature-create]').click();ready();expect(page.locator('#status')).to_contain_text('입력은 유지됩니다');assert not any('FreshFeatureBlueprintBody' in row['id'] for row in state()['units'])
 panel.locator('[data-declaration-current]').click();ready();panel.locator('[data-feature-read]').click();ready();page.screenshot(path='/tmp/confectory-v480-feature-contract.png',full_page=True);panel.locator('[data-feature-create]').click();ready();expect(panel.locator('[data-feature-open]')).to_be_visible();panel.locator('[data-feature-open]').click();ready()
 graph='Example.ButtonGame::FreshFeatureBlueprintBody/body:common';data=read_graph();assert data['signature']=={'args':[{'type':'long','name':'count'}],'return':'long'} and data['diagnostics']['state']=='needs-implementation';assert len(data['reviewIds'])==5 and len(data['sources'])==5
 paths=[project/s['path'] for s in data['sources'] if s['id']!='Example.ButtonGame::ProjectManifest'];assert all(not p.exists() for p in paths);expect(graph_panel().locator('[data-bp-node]')).to_have_count(1);expect(graph_panel().locator('.bp-node-state')).to_have_text('새 노드 · 본문 작성 전')
 graph_panel().locator('[data-bp-code-open="body"]').click();code=page.locator('.window').filter(has=page.locator('[data-bp-code]'));code.locator('[data-bp-code]').fill('return count + 9;');invoke('saveDraft',{});page.evaluate('()=>globalThis.confectoryFlushPresentation()');restart();ready()
 nav('기능 Blueprint');expect(graph_panel().locator('[data-bp-node]')).to_have_count(1);graph_panel().locator('[data-bp-code-open="body"]').click();expect(code.locator('[data-bp-code]')).to_have_value('return count + 9;');code.locator('[data-apply]').click();ready();expect(page.locator('#status')).to_contain_text('기준 재검토');assert read_graph()['nodes'][0]['source']=='';code.locator('[data-rebase]').click();code.locator('[data-apply]').click();ready();code.locator('[data-close]').click();nav('기능 Blueprint')
 graph_panel().locator('[data-bp-review]').click();ready();review=page.locator('.window[data-key="review"]');expect(review.locator('[data-review-advanced]')).to_be_visible(timeout=180000);actual=state()['review'];assert {r['id'] for r in actual['units']}==set(data['reviewIds']);assert all(not p.exists() for p in paths);review.locator('[data-review-advanced]').click();review.locator('[data-advanced-reviewed]').check();expect(page.locator('#confirm')).to_be_enabled();page.locator('#confirm').click();ready();assert all(p.exists() for p in paths),state().get('status');nav('기능 Blueprint');graph_panel().locator('[data-bp-fit]').click();page.screenshot(path='/tmp/confectory-v480-feature-creation.png',full_page=True)
 node=next(p for p in paths if p.name.endswith('.node.json'));assert json.loads(node.read_text())['source']=='return count + 9;';assert 'provide '+feature+' with Example.ButtonGame::FreshFeatureBlueprintBody' in (project/'elements/FreshFeature.celem').read_text();assert all(p.read_bytes()==b for p,b in before.items() if p.name!='project.cpack')
 invoke('saveDraft',{});restart();ready();nav('기능 Blueprint');assert read_graph()['nodes'][0]['source']=='return count + 9;' and not state()['aiOwnerAvailable'];assert all(p.exists() for p in paths)
 print('PASS actual v480 feature creation: typed contract, peer CAS, five-source registration, unimplemented state, cold input rebase, explicit compiler group Confirm and preserved existing sources',flush=True)
