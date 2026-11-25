"""Actual independent windows from the shared project model; no host slot until edit."""
import v821_project_property_model_ui as m
import v821_property_window_reopen_ui as r
import v821_direct_property_save_ui as d
from playwright.sync_api import sync_playwright,expect
f=r.fixture;b=r.fallback;source=r.seed();expect.set_options(timeout=60000)
def open_local(page,name,folder,slot,gesture='drag',held=True,title=None):
 w=r.browser_window(page);r.choose_tree_location(w,f'[data-tree-id="{b.NS}::{folder}"]');r.search(w,b.LABEL,name)
 item=w.locator(f'[data-object="{b.NS}::{name}"]');key='editor-'+str(slot);window=page.locator(f'.window[data-key="{key}"]')
 expect(page.locator('#project-menu')).to_be_enabled()
 if gesture=='menu':item.click(button='right')
 page.evaluate('''([key,gesture])=>{globalThis.localStart=null;document.addEventListener(gesture==='drag'?'drop':'click',e=>{if(!e.isTrusted)return;const start=performance.now();const watch=()=>{const w=document.querySelector('.window[data-key="'+key+'"]');if(w&&!w.hidden&&[...w.querySelectorAll('[data-property-value]')].some(f=>!f.disabled&&!f.readOnly&&!f.closest('[inert]')&&f.getClientRects().length)){globalThis.localStart=performance.now()-start;return;}if(performance.now()-start<10000)requestAnimationFrame(watch);};requestAnimationFrame(watch);},{capture:true,once:true})}''',[key,gesture])
 routes=[]
 def hold(route):
  body=route.request.post_data_json
  if isinstance(body,dict) and body.get('op')=='update':routes.append(route)
  else:route.fallback()
 if held:page.route('**/api/request',hold)
 mark=len(f.requests)
 try:
  if gesture=='menu':page.locator('.context-menu').get_by_role('button',name='새 창으로 열기',exact=True).click()
  else:
   box=item.bounding_box();start=(box['x']+12,box['y']+12);canvas=page.locator('#workspace').bounding_box();xy=(canvas['x']+canvas['width']*.82,canvas['y']+canvas['height']*.62);page.mouse.move(*start);page.mouse.down();page.mouse.move(start[0]+12,start[1]+2,steps=3);page.mouse.move(*xy,steps=12);page.mouse.move(xy[0]+1,xy[1]);page.mouse.up()
  expect(window).to_be_visible(timeout=3000)
  note=d.value(window,'Note');expect(note).to_be_editable(timeout=3000);expect(note).to_have_value((title or b.FIRST)+' '+name)
  page.wait_for_function('()=>localStart!==null',timeout=3000);print('local editable ms',name,page.evaluate('localStart'),flush=True)
  if held:assert not any(x['endpoint'] in ('openEditorView','select','schema') for x in f.requests[mark:])
 finally:
  if held:
   page.unroute('**/api/request',hold)
   for route in routes:route.fallback()
 return window,note
try:
 with sync_playwright() as p,p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) as browser:
  f.start(0);page=f.setup(browser);page.set_viewport_size({'width':2000,'height':1200});m.wait_model(page,open_browser=True)
  print('prepared drafts',list(f.state().get('preparedPropertyDrafts',{})),flush=True)
  first,note=open_local(page,b.TARGET,'StockFolder',1);note.fill('retained first local')
  expect(page.locator('#project-menu')).to_be_enabled()
  second,note2=open_local(page,'Extra2','ExtraFolder2',2,'menu');note2.fill('second local committed')
  assert not f.state()['editorViews'],'local windows must not allocate host slots on click'
  d.commit(page,second)
  extra=source.parent/'private-source-Extra2.celem';assert 'data Note = "second local committed"' in extra.read_text()
  assert source.read_bytes()==f.before[str(source)];expect(note).to_have_value('retained first local')
  print('PASS second detached owner saved without touching first',flush=True)
  d.commit(page,first);assert 'data Note = "retained first local"' in source.read_text()
  print('PASS first detached owner saved',flush=True)
  b.enter_from_home(page,b.SECOND);m.wait_model(page,open_browser=True)
  first,note=open_local(page,b.TARGET,'StockFolder',1,title=b.SECOND);note.fill('second project local input')
  expect(page.locator('#project-menu')).to_be_enabled()
  second,note2=open_local(page,b.PEER,'PeerFolder',2,'menu',title=b.SECOND);note2.fill('second peer local input')
  page.evaluate("()=>confectoryFlushPresentation()");page.close();f.stop()
  f.env['CONFECTORY_WEB_PROJECT']=str(f.projects[1]);f.start(1);page=f.setup(browser)
  expect(page.locator('#title')).to_contain_text(b.SECOND);first=page.locator('.window[data-key="editor-1"]');second=page.locator('.window[data-key="editor-2"]')
  expect(d.value(first,'Note')).to_have_value('second project local input');expect(d.value(second,'Note')).to_have_value('second peer local input')
  expect(d.value(first,'Note')).to_be_editable();assert not f.state()['editorViews']
  print('PASS clean cold restore creates both real input surfaces from one model without host slots',flush=True)
  peer=f.projects[1].parent/'private-source-PeerRecord.celem';external=peer.read_text().replace(b.SECOND+' '+b.PEER,'external peer value');peer.write_text(external)
  assert not f.state()['preparedPropertyModels']
  expect(page.locator('#project-menu')).to_be_enabled(timeout=120000)
  confirm=second.locator('[data-element-action="confirm"]');expect(confirm).to_be_enabled()
  mark=len(f.requests);confirm.click()
  expect(page.locator('#project-menu')).to_be_enabled(timeout=120000)
  attempted=[x['endpoint'] for x in f.requests[mark:]]
  print('external attempted endpoints',attempted,'status',page.locator('#status').text_content(),flush=True)
  assert 'openEditorView' in attempted and not any(x in attempted for x in ('blueprint','editViewField','saveEditorView','reviewGroup','confirmGroup'))
  expect(second.locator('[data-element-error]')).not_to_have_text('')
  expect(d.value(second,'Note')).to_have_value('second peer local input');expect(d.value(first,'Note')).to_have_value('second project local input');assert peer.read_text()==external
  print('PASS external conflict, same-ID project isolation and retained independent input',flush=True)
  assert not f.errors and not f.external,(f.errors,f.external)
finally:f.stop();print('evidence',f.root,flush=True)
