"""Actual independent windows from the shared project model; no host slot until edit."""
import v821_project_property_model_ui as m
import v821_property_window_reopen_ui as r
import v821_direct_property_save_ui as d
from playwright.sync_api import sync_playwright,expect
f=r.fixture;b=r.fallback;source=r.seed();expect.set_options(timeout=60000)
# Extra1 deliberately uses a different schema while the other three share StockInfo.
for project in f.projects:
 schema=project.parent/'private-source-IndependentInfo.celem'
 schema.write_text((project.parent/'private-source-StockInfo.celem').read_text().replace('::StockInfo','::IndependentInfo'))
 extra=project.parent/'private-source-Extra1.celem'
 extra.write_text(extra.read_text().replace('::StockInfo','::IndependentInfo'))
 project.write_text(project.read_text().rstrip()[:-1]+'\nelement IndependentInfo schema "private-source-IndependentInfo.celem";\n}\n')
 for path in (schema,extra,project):f.before[str(path)]=path.read_bytes()
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
  ids=lambda:{row['id'] for row in f.state()['preparedPropertyModels']}
  assert {b.NS+'::'+b.TARGET,b.NS+'::Extra1',b.NS+'::'+b.PEER}<=ids()
  assert b.NS+'::Extra2' not in ids() or 'second local committed' in f.state()['preparedPropertyDrafts'][b.NS+'::Extra2']['text']
  third,note3=open_local(page,'Extra1','ExtraFolder1',3,'menu')
  expect(note3).to_be_editable()
  print('PASS first opening of unaffected owner after independent direct save',flush=True)
  d.commit(page,first);assert 'data Note = "retained first local"' in source.read_text()
  print('PASS first detached owner saved',flush=True)
  note3.fill('staged independent local draft')
  third.locator('[data-element-action="save"]').click()
  expect(third.locator('[data-element-action="save"]')).to_be_disabled()
  expect(page.locator("#project-menu")).to_be_enabled(timeout=120000)
  print("after staged",ids(),flush=True)
  assert b.NS+'::Extra1' not in ids() and b.NS+'::'+b.PEER in ids()
  assert 'staged independent local draft' not in (source.parent/'private-source-Extra1.celem').read_text()
  # A clean-only preparation attempted during a shared draft cannot discard
  # previously proven unrelated rows.
  f.call('relationsMap',{'prepareProperties':True})
  assert b.NS+'::'+b.PEER in ids()
  primary,peer_note=m.open_local(page,b.PEER,'PeerFolder',b.FIRST+' '+b.PEER)
  expect(peer_note).to_be_editable()
  print('PASS unrelated prepared owner survives staged draft and opens for real input',flush=True)
  b.enter_from_home(page,b.SECOND);m.wait_model(page,open_browser=True)
  first,note=open_local(page,b.TARGET,'StockFolder',1,title=b.SECOND);note.fill('second project local input')
  expect(page.locator('#project-menu')).to_be_enabled()
  second,note2=open_local(page,b.PEER,'PeerFolder',2,'menu',title=b.SECOND);note2.fill('second peer local input')
  page.evaluate("()=>confectoryFlushPresentation()");page.close();f.stop()
  restore_mark=len(f.requests)
  f.env['CONFECTORY_WEB_PROJECT']=str(f.projects[1]);f.start(1);page=f.setup(browser);page.set_viewport_size({'width':2000,'height':1200})
  expect(page.locator('#title')).to_contain_text(b.SECOND);first=page.locator('.window[data-key="editor-1"]');second=page.locator('.window[data-key="editor-2"]')
  expect(d.value(first,'Note')).to_have_value('second project local input');expect(d.value(second,'Note')).to_have_value('second peer local input')
  expect(d.value(first,'Note')).to_be_editable();assert not f.state()['editorViews']
  expect(page.locator('#project-menu')).to_be_enabled(timeout=120000)
  restored=f.requests[restore_mark:]
  preparations=[row for row in restored if row['endpoint']=='preparePropertyModels' and row['input'].get('restoreStatuses') is True]
  assert len(preparations)==1 and set(preparations[0]['input']['ids'])=={b.NS+'::'+b.TARGET,b.NS+'::'+b.PEER},restored
  # The property windows use status proof in the restore response, not separate
  # detached status RPCs before the inventory/relations projection.
  prior_projection=[]
  for request in restored:
   if request['endpoint'] in ('localInventory','relationsMap'):break
   prior_projection.append(request)
  assert not any(row['endpoint']=='browserDrafts' for row in prior_projection),prior_projection
  print('PASS clean cold restore creates both real input surfaces and checkpoint statuses from one model request without host slots',flush=True)
  d.commit(page,first)
  second_source=f.projects[1].parent/source.name
  assert 'data Note = "second project local input"' in second_source.read_text()
  expect(d.value(second,'Note')).to_have_value('second peer local input')
  print('PASS direct Save after cold restore retains other input',flush=True)
  # Restore prepares only saved owners. Explicitly prepare the same batch of four
  # using the real host reader before testing a shared schema dependency.
  f.call('preparePropertyModels',{'ids':sorted(m.identifiers)})
  assert ids()==m.identifiers
  peer=f.projects[1].parent/'private-source-PeerRecord.celem';external=peer.read_text().replace(b.SECOND+' '+b.PEER,'external peer value');peer.write_text(external)
  after=ids()
  assert b.NS+'::'+b.PEER not in after and b.NS+'::'+b.TARGET in after
  dependency=peer.with_name('private-source-StockInfo.celem')
  dependency.write_text(dependency.read_text()+'\n// external shared schema change\n')
  assert ids()=={b.NS+"::Extra1"}
  print("PASS external owner and shared schema invalidate only dependent rows",flush=True)
  expect(page.locator('#project-menu')).to_be_enabled(timeout=120000)
  confirm=second.locator('[data-element-action="confirm"]');expect(confirm).to_be_enabled()
  mark=len(f.requests);confirm.click()
  expect(page.locator('#project-menu')).to_be_enabled(timeout=120000)
  attempted=[x['endpoint'] for x in f.requests[mark:]]
  print('external attempted endpoints',attempted,'status',page.locator('#status').text_content(),flush=True)
  # A stale owner may reach the read-only admission check after its local
  # prepared view is refreshed. It must never reach a source-writing action.
  assert 'openEditorView' in attempted and not any(x in attempted for x in ('editViewField','saveEditorView','reviewGroup','confirmGroup'))
  assert all(req.get('input',{}).get('action')=='readOwnerEdits' for req in f.requests[mark:] if req['endpoint']=='blueprint')
  expect(second.locator('[data-element-error]')).not_to_have_text('')
  expect(d.value(second,'Note')).to_have_value('second peer local input');expect(d.value(first,'Note')).to_have_value('second project local input');assert peer.read_text()==external
  print('PASS external conflict, same-ID project isolation and retained independent input',flush=True)
  page.close();f.stop()
  f.env['CONFECTORY_WEB_PROJECT']=str(f.projects[0]);f.start(2);page=f.setup(browser);page.set_viewport_size({'width':2000,'height':1200})
  expect(page.locator('#title')).to_contain_text(b.FIRST)
  staged=page.locator('.window[data-element-owner="'+b.NS+'::Extra1"]')
  expect(d.value(staged,'Note')).to_have_value('staged independent local draft',timeout=120000)
  assert 'staged independent local draft' not in (source.parent/'private-source-Extra1.celem').read_text()
  assert b.NS+'::Extra1' not in ids()
  print('PASS restarted dirty checkpoint uses ordinary verified restore without publishing the draft',flush=True)
  assert not f.errors and not f.external,(f.errors,f.external)
finally:f.stop();print('evidence',f.root,flush=True)
