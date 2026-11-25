"""Trusted mouse press and drag must survive ordinary state publication."""
import time
from playwright.sync_api import expect, sync_playwright
import v821_property_window_reopen_ui as r
import v821_project_property_model_ui as m
import v821_direct_property_save_ui as d

f=r.fixture;b=r.fallback;source=r.seed()
view_id=b.NS+'::PointerDesk'
for manifest in f.projects:
 view=manifest.parent/'PointerDesk.celem'
 view.write_text(f'view {view_id} {{ use object {b.NS}::{b.TARGET}; value editorName = "Pointer test"; }}\n')
 manifest.write_text(manifest.read_text().rstrip()[:-1]+'\nelement PointerDesk view "PointerDesk.celem";\n}\n')
 for path in (view,manifest):f.before[str(path)]=path.read_bytes()
expect.set_options(timeout=60000)

def state_publication(page,predicate=lambda state:True):
 # Wait for the actual browser poll, not an independent fixture mount.
 # Parse responses outside the event callback (avoids Playwright reentrancy).
 deadline=time.monotonic()+15
 while time.monotonic()<deadline:
  with page.expect_response(lambda response: response.url.endswith('/api/request')
    and (response.request.post_data_json or {}).get('op')=='update',timeout=15000) as result:
   pass
  response=result.value.json()
  if response.get('ok') and isinstance(response.get('state'),dict) and predicate(response['state']):
   page.evaluate('()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
   return
 raise AssertionError('actual changed state was not published to page')

def begin(page,item):
 expect(item).to_be_visible()
 item.scroll_into_view_if_needed()
 box=item.bounding_box();assert box
 x,y=box['x']+box['width']/2,box['y']+box['height']/2
 assert item.evaluate('(el,[x,y])=>el.contains(document.elementFromPoint(x,y))',[x,y]),('pointer hit mismatch',box)
 item.evaluate('el=>globalThis.pressedNode=el')
 page.mouse.move(x,y);page.mouse.down()
 return x,y

def intact(page):
 return page.evaluate('()=>pressedNode.isConnected')

def pack_open(page):
 page.locator('#project-menu').click()
 page.locator('.context-menu').get_by_role('button',name='팩 관리',exact=True).click()
 packs=page.locator('[data-key="packs"]')
 summary=packs.get_by_text('프로젝트 창 선언',exact=True)
 expect(summary).to_be_visible()
 return packs,summary

try:
 with sync_playwright() as p,p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) as browser:
  f.start(0);page=f.setup(browser);page.set_viewport_size({'width':2000,'height':1200})
  expect(page.locator('#project-menu')).to_be_enabled()
  packs,summary=pack_open(page)
  held=[]
  def hold(route):
   if (route.request.post_data_json or {}).get('op')=='update':held.append(route)
   else:route.fallback()
  page.route('**/api/request',hold)
  summary.click();item=packs.get_by_role('button',name=view_id,exact=True)
  begin(page,item)
  try:
   # Independently select another owned declaration through the real host.
   # This guarantees a changed snapshot while the pointer remains pressed.
   f.call('select',{'id':b.NS+'::Extra2'})
   with page.expect_response(lambda response:response.url.endswith('/api/request') and (response.request.post_data_json or {}).get('op')=='update',timeout=15000) as seen:
    page.unroute('**/api/request',hold)
    for route in held:route.fallback()
   assert seen.value.json().get('ok')
   state_publication(page,lambda state:(state.get('draft') or {}).get('id')==b.NS+'::Extra2')
   assert intact(page),'pack declaration node was replaced during real mouse press'
  finally:page.mouse.up()
  expect(page.locator('#selection')).to_have_text(view_id)
  print('PASS registered View click survives actual state publication',flush=True)
  r.close(packs)
  expect(page.locator('#project-menu')).to_be_enabled()
  page.locator('#workspace-pack-tab').click()
  manager=page.locator('#pack-manager-view')
  row=manager.locator('#home-pack-list [data-pack]').last
  begin(page,row)
  try:
   f.call('select',{'id':b.NS+'::Extra1'})
   state_publication(page,lambda state:(state.get('draft') or {}).get('id')==b.NS+'::Extra1');assert intact(page),'Pack Manager row replaced during press'
  finally:page.mouse.up()
  expect(row).to_have_attribute('aria-pressed','true')
  page.locator('#workspace-home-tab').click()
  print('PASS Pack Manager row selection survives a changed snapshot',flush=True)
  expect(page.locator('#project-menu')).to_be_enabled()
  m.wait_model(page,open_browser=True)
  w=r.browser_window(page);r.choose_tree_location(w,f'[data-tree-id="{b.NS}::StockFolder"]');r.search(w,b.LABEL,b.TARGET)
  item=w.locator(f'[data-object="{b.NS}::{b.TARGET}"]')
  page.evaluate('''()=>{globalThis.trustedGestures=[];for(const type of ['dragstart','drop'])document.addEventListener(type,e=>{if(e.isTrusted)trustedGestures.push(type)},true)}''')
  x,y=begin(page,item)
  try:
   state_publication(page);assert intact(page),'browser row replaced before native dragstart'
   page.mouse.move(x+14,y+3,steps=4)
   canvas=page.locator('#workspace').bounding_box();tx=canvas['x']+canvas['width']*.82;ty=canvas['y']+canvas['height']*.62
   page.mouse.move(tx,ty,steps=12)
   state_publication(page);assert intact(page),'browser row replaced during native drag'
   page.mouse.move(tx+1,ty)
  finally:page.mouse.up()
  target=page.locator(f'.window[data-element-owner="{b.NS}::{b.TARGET}"][data-element-mode="properties"]:visible')
  expect(target).to_have_count(1);expect(d.value(target,'Note')).to_be_editable()
  assert page.evaluate('trustedGestures')==['dragstart','drop']
  d.value(target,'Note').fill('pointer retained input')
  d.commit(page,target);assert 'data Note = "pointer retained input"' in source.read_text()
  print('PASS trusted native drag, exact owner, real field input and Save',flush=True)
  # A second pointer press spans an actual shared draft/relationship change.
  # Only the retained row's rendering is delayed; the host sees the new revision.
  w=r.browser_window(page);r.choose_tree_location(w,f'[data-tree-id="{b.NS}::PeerFolder"]');r.search(w,b.LABEL,b.PEER)
  peer_id=b.NS+'::'+b.PEER;peer=w.locator(f'[data-object="{peer_id}"]')
  x,y=begin(page,peer)
  try:
   f.call('select',{'id':peer_id});basis=f.state()['draft']
   changed=basis['text'].replace(b.FIRST+' '+b.PEER,'shared revision during pointer press').replace(b.LABEL,b.LABEL+' revised')
   f.call('editDraft',{'id':peer_id,'revision':basis['revision'],'text':changed})
   f.call('relationsMap',{})
   state_publication(page,lambda state:any(row.get('id')==peer_id and row.get('title')==b.LABEL+' revised' for row in (state.get('relationsMap') or {}).get('nodes',[])));assert intact(page),'browser row replaced during changed projection'
   assert peer_id not in {model['id'] for model in f.state()['preparedPropertyModels']}
   page.mouse.move(x+14,y+3,steps=4)
   canvas=page.locator('#workspace').bounding_box();tx=canvas['x']+canvas['width']*.82;ty=canvas['y']+canvas['height']*.40
   page.mouse.move(tx,ty,steps=12);state_publication(page);assert intact(page)
   page.mouse.move(tx+1,ty)
  finally:page.mouse.up()
  peer_window=page.locator(f'.window[data-element-owner="{peer_id}"][data-element-mode="properties"]:visible')
  expect(peer_window).to_have_count(1)
  expect(d.value(peer_window,'Note')).to_have_value('shared revision during pointer press')
  assert page.evaluate('trustedGestures')==['dragstart','drop','dragstart','drop']
  assert (source.parent/'private-source-PeerRecord.celem').read_bytes()==f.before[str(source.parent/'private-source-PeerRecord.celem')]
  f.call('saveDraft',{})
  print('PASS changed shared projection during trusted press/drag uses latest owner and preserves confirmed file',flush=True)
  b.enter_from_home(page,b.SECOND);m.wait_model(page,open_browser=True)
  w=r.browser_window(page);r.choose_tree_location(w,f'[data-tree-id="{b.NS}::StockFolder"]');r.search(w,b.LABEL,b.TARGET)
  target_item=w.locator(f'[data-object="{b.NS}::{b.TARGET}"]')
  x,y=begin(page,target_item)
  try:
   state_publication(page);assert intact(page)
   page.mouse.move(x+14,y+3,steps=4);canvas=page.locator('#workspace').bounding_box()
   tx=canvas['x']+canvas['width']*.82;ty=canvas['y']+canvas['height']*.62
   page.mouse.move(tx,ty,steps=12);page.mouse.move(tx+1,ty)
  finally:page.mouse.up()
  second=page.locator(f'.window[data-element-owner="{b.NS}::{b.TARGET}"][data-element-mode="properties"]:visible')
  expect(d.value(second,'Note')).to_have_value(b.SECOND+' '+b.TARGET)
  print('PASS same-ID second project opens its own value after pointer refresh',flush=True)
  # A real rapid-click sequence on the already-open owner may focus it but
  # must not allocate a second independent slot.
  w=r.browser_window(page);item=w.locator(f'[data-object="{b.NS}::{b.TARGET}"]')
  item.scroll_into_view_if_needed();box=item.bounding_box();x=box['x']+box['width']/2;y=box['y']+box['height']/2
  assert item.evaluate('(el,[x,y])=>el.contains(document.elementFromPoint(x,y))',[x,y])
  page.mouse.click(x,y,click_count=3)
  expect(page.locator('#project-menu')).to_be_enabled()
  expect(page.locator(f'.window[data-element-owner="{b.NS}::{b.TARGET}"][data-element-mode="properties"]:visible')).to_have_count(1)
  expect(d.value(second,'Note')).to_have_value(b.SECOND+' '+b.TARGET)
  print('PASS rapid trusted clicks focus the same object without duplicate slots',flush=True)
  assert not f.errors and not f.external,(f.errors,f.external)
finally:f.stop();print('evidence',f.root,flush=True)
