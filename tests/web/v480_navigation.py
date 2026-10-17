"""Real local Home queries and retained browser/document inputs; no accounts or source mutation."""
import time,uuid
from playwright.sync_api import expect

def verify_navigation(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':1550,'height':1100});before={p:p.read_bytes() for p in project.iterdir() if p.is_file()};issues=[]
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=180000);expect(page.locator('#workspace-save-state')).not_to_contain_text('편집창 복원 중',timeout=180000)
 def invoke(endpoint,args):
  v=mount();request=uuid.uuid4().hex;assert send(envelope(v,'invoke',endpoint=endpoint,requestId=request,expectedRevision=v['revision'],input=args))['ok'];deadline=time.monotonic()+180;result=None
  while time.monotonic()<deadline:
   reply=send(envelope(v,'update'));assert reply['ok'];result=next((x for x in reply.get('results',[]) if x['requestId']==request),None)
   if result:break
   time.sleep(.02)
  assert result and result['ok'],result;assert send(envelope(v,'dispose'))['ok'];return result['result']
 def state():
  v=mount();s=v['state'];assert send(envelope(v,'dispose'))['ok'];return s
 def saved():page.evaluate('()=>globalThis.confectoryFlushPresentation()');return state()['presentation']
 def window(key):return page.locator('.window[data-key="'+key+'"]')
 def nav(name):
  ready();page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name=name,exact=True).click();ready()
  if page.locator('.nav-menu').count():page.locator('#nav').click()
 def query():return window('browser').locator('[data-browser-control="object-query"]')
 ready();page.locator('.brand').click();page.locator('#home-projects').wait_for();card=page.locator('[data-project]').first;card_id=card.get_attribute('data-project');title=card.locator('h2').inner_text();page.locator('#home-project-search').fill(title);expect(card).to_be_visible();card.locator('[data-manage]').click();page.get_by_role('button',name='프로젝트 정보',exact=True).click();expect(page.locator('.modal')).to_contain_text(title);page.locator('.modal [data-close]').click();card.locator('[data-manage]').click();page.get_by_role('button',name='목록에서 삭제',exact=True).click();page.locator('.modal [data-close]').click();expect(page.locator('[data-project="'+card_id+'"]')).to_have_count(1)
 page.locator('#home-tab-packs').click();expect(page.locator('#home-pack-list [data-pack]').first).to_be_visible(timeout=180000);rows=page.locator('#home-pack-list [data-pack]');assert rows.count()>1;chosen=rows.nth(1).get_attribute('data-pack');rows.nth(1).click();page.locator('[data-pack-group="local"]').click()
 if page.locator('#home-pack-list [aria-pressed="true"]').get_attribute('data-pack')!=chosen:issues.append('repeat active local-pack tab lost the selected pack')
 page.locator('#home-pack-search').fill('Confectory.BaseUI');page.locator('#home-pack-search').press('Enter');expect(page.locator('#home-pack-list [data-pack]').first).to_be_visible();assert all('confectory.baseui' in row.inner_text().lower() for row in page.locator('#home-pack-list [data-pack]').all());page.locator('#home-pack-search').fill('LOCAL_PACK_PENDING');page.locator('[data-pack-group="explore"]').click();page.locator('#home-pack-search').fill('REMOTE_PACK_PENDING');page.locator('[data-pack-group="local"]').click()
 if page.locator('#home-pack-search').input_value()!='LOCAL_PACK_PENDING':issues.append('pack group switch lost separate unsubmitted query input')
 page.locator('#home-pack-sort').click();page.locator('[data-pack-sort="name"]').click()
 if page.locator('#home-pack-sort').get_attribute('aria-expanded')!='false':issues.append('pack sort menu closed visually but retained expanded state')
 page.locator('#home-pack-sort').click();page.keyboard.press('Escape');expect(page.locator('#home-pack-sort-menu')).not_to_be_visible();expect(page.locator('#home-pack-sort')).to_have_attribute('aria-expanded','false');expect(page.locator('#home-pack-sort')).to_be_focused();page.locator('#home-pack-sort').click();page.locator('#home-pack-search').click();expect(page.locator('#home-pack-sort-menu')).not_to_be_visible();expect(page.locator('#home-pack-sort')).to_have_attribute('aria-expanded','false')
 page.locator('#home-tab-projects').click();page.locator('[data-enter="'+card_id+'"]').click();ready();page.locator('.brand').click();page.locator('#home-projects').wait_for();page.locator('#home-tab-packs').click();expect(page.locator('#home-pack-list [data-pack]').first).to_be_visible(timeout=180000)
 if page.locator('#home-pack-search').input_value()!='LOCAL_PACK_PENDING':issues.append('Home return showed a filtered pack list with missing retained query')
 page.locator('#home-tab-projects').click();page.locator('[data-enter="'+card_id+'"]').click();ready();nav('개념');browser=window('browser');query().fill('BROWSER_PENDING');browser.locator('[data-tab="concept"]').click()
 if query().input_value()!='BROWSER_PENDING':issues.append('repeat active browser group cleared unsubmitted query')
 query().fill('BROWSER_PENDING');query().evaluate('el=>globalThis.__navigationSearch=el');nav('개념')
 if not query().evaluate('el=>el===globalThis.__navigationSearch'):issues.append('repeat browser open rebuilt its live search DOM')
 if browser.locator('[data-load-inventory]').count():browser.locator('[data-load-inventory]').click();ready()
 browser.locator('[data-namespace="Example.ButtonGame"]').click();query().fill('Score');browser.locator('[data-browser-control="object-search"]').click();query().fill('CONCEPT_PENDING');browser.locator('[data-tab="feature"]').click();query().fill('FEATURE_PENDING');browser.locator('[data-tab="concept"]').click()
 if query().input_value()!='CONCEPT_PENDING':issues.append('browser group round trip lost query/location')
 assert all(p.read_bytes()==raw for p,raw in before.items())
 if issues:
  page.screenshot(path='/tmp/confectory-v480-navigation-before.png',full_page=True);raise AssertionError('; '.join(issues))
 # Docking and repeated navigation preserve the actual search DOM and native undo history.
 query().evaluate('el=>globalThis.__navigationSearch=el');browser.locator('.window-title').click(button='right',position={'x':110,'y':18});page.locator('.context-menu').get_by_role('button',name='탭으로 열기',exact=True).click();expect(browser).to_have_class('window window-document tab-document');expect(query()).to_have_value('CONCEPT_PENDING');query().press('End');query().press('x');nav('개념');assert query().evaluate('el=>el===globalThis.__navigationSearch');expect(query()).to_have_value('CONCEPT_PENDINGx');query().press('Control+z');expect(query()).to_have_value('CONCEPT_PENDING');query().press('Control+Shift+z');expect(query()).to_have_value('CONCEPT_PENDINGx')
 page.locator('[data-window-tab="browser"]').click();page.locator('[data-window-tab="browser"]').click();assert query().evaluate('el=>el===globalThis.__navigationSearch');browser.locator('[data-tab="feature"]').click();expect(query()).to_have_value('FEATURE_PENDING');browser.locator('[data-tab="concept"]').click();expect(query()).to_have_value('CONCEPT_PENDINGx');expect(browser.locator('[data-id="Example.ButtonGame::Score"]')).to_be_visible();page.screenshot(path='/tmp/confectory-v480-navigation.png',full_page=True);saved();invoke('saveDraft',{});restart();ready();expect(window('browser')).to_be_visible(timeout=60000);expect(query()).to_have_value('CONCEPT_PENDINGx');window('browser').locator('[data-tab="feature"]').click();expect(query()).to_have_value('FEATURE_PENDING');window('browser').locator('[data-tab="concept"]').click();expect(query()).to_have_value('CONCEPT_PENDINGx');expect(window('browser').locator('[data-id="Example.ButtonGame::Score"]')).to_be_visible();window('browser').locator('[data-document-return]').click();expect(page.locator('[data-window-tab="browser"]')).to_have_count(0);expect(query()).to_have_value('CONCEPT_PENDINGx');assert all(p.read_bytes()==raw for p,raw in before.items())
 # Source input blocks selection changes before browser metadata or applied query changes.
 browser=window('browser');browser.locator('[data-catalog-root]').click();ready();browser.locator('[data-browser-control="browser-actions"]').click();page.locator('#advanced-source').click();source=page.locator('#source');expect(source).to_be_visible();pending=source.input_value()+'\n// NAVIGATION_SOURCE_PENDING';source.fill(pending);source.evaluate('el=>globalThis.__navigationSource=el');query().fill('BLOCKED_QUERY');prior=saved()['layout'];prior=next(x['meta'] for x in prior if x['key']=='browser');browser.locator('[data-tab="feature"]').click();expect(browser.locator('[data-tab="concept"]')).to_have_class('selected');expect(query()).to_have_value('BLOCKED_QUERY');browser.locator('[data-browser-control="object-search"]').click();expect(page.locator('#status')).to_have_text('Apply local input before changing selection');after=saved()['layout'];after=next(x['meta'] for x in after if x['key']=='browser');assert after['group']==prior['group'] and after['query']==prior['query'] and not after['catalogue'];expect(source).to_have_value(pending);assert source.evaluate('el=>el===globalThis.__navigationSource')
 browser.locator('[data-namespace="Example.ButtonGame"]').click();browser.locator('[data-catalog-root]').click();after=next(x['meta'] for x in saved()['layout'] if x['key']=='browser');assert after['catalogue'] and after['namespace']=='Example.ButtonGame';expect(source).to_have_value(pending);assert all(p.read_bytes()==raw for p,raw in before.items())
 print('PASS actual v480 Home/browser/document navigation: cancel/repeat, applied/draft queries, group location, exact DOM/undo, dock and cold restore; source unchanged',flush=True)
