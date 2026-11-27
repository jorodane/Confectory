"""Real delayed prepared-model publication at an ordinary property click.

Run with REPO BUILD_REPORT and optional external mode. A separate mounted
view prepares the real model; held browser requests exercise the actual
refreshed state and must not resurrect a closed window.
"""
import sys
import v821_partial_property_model_ui as m
from playwright.sync_api import sync_playwright,expect
f=m.fixture;b=m.fallback;r=m.reopen;m.seed()
identifier=b.NS+'::Extra1'
external_mode=len(sys.argv)>3 and sys.argv[3]=='external'
expect.set_options(timeout=60000)
try:
 with sync_playwright() as p,p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) as browser:
  f.start(0);page=f.setup(browser);page.set_viewport_size({'width':2000,'height':1200})
  prepares=[];updates=[];gate=False;seen=[]
  def intercept(route):
   x=route.request.post_data_json if route.request.method=='POST' else {}
   if x.get('op')=='invoke' and x.get('endpoint')=='preparePropertyModels' and identifier in x.get('input',{}).get('ids',[]):
    prepares.append(route);return
   if gate and x.get('op')=='update':
    updates.append(route);return
   if x.get('op')=='invoke' and x.get('endpoint')=='openEditorView' and x.get('input',{}).get('id')==identifier:seen.append(x)
   route.fallback()
  page.route('**/api/request',intercept)
  window=r.browser_window(page)
  r.choose_tree_location(window,f'[data-tree-id="{b.NS}::ExtraFolder1"]')
  r.search(window,b.LABEL,'Extra1')
  item=window.locator(f'[data-object="{identifier}"]')
  expect(page.locator('#project-menu')).to_be_enabled()
  item.click(button='right')
  button=page.locator('.context-menu').get_by_role('button',name='새 창으로 열기',exact=True)
  expect(button).to_be_enabled()
  assert identifier not in {row['id'] for row in f.state()['preparedPropertyModels']}
  gate=True
  # Real owner-scoped preparation on an independent mounted view. The page
  # cannot receive it until its required update reaches the host.
  f.call('preparePropertyModels',{'ids':[identifier]})
  assert identifier in {row['id'] for row in f.state()['preparedPropertyModels']}
  if external_mode:
   schema=f.projects[0].parent/'private-source-StockInfo.celem'
   schema.write_text(schema.read_text()+'\n// external schema revision\n')
   assert identifier not in {row['id'] for row in f.state()['preparedPropertyModels']}
  page.evaluate('''owner=>{globalThis.lateModelEditable=null;document.addEventListener('click',event=>{if(!event.isTrusted)return;const start=performance.now();const observe=()=>{const w=[...document.querySelectorAll('.window[data-element-owner]')].find(row=>row.dataset.elementOwner===owner&&!row.hidden);if(w&&[...w.querySelectorAll('[data-property-value]')].some(field=>field.getClientRects().length&&!field.disabled&&!field.readOnly&&!field.closest('[inert]'))){lateModelEditable=performance.now()-start;return;}if(performance.now()-start<30000)requestAnimationFrame(observe);};requestAnimationFrame(observe);},{capture:true,once:true})}''',identifier)
  button.click()
  gate=False
  for route in updates:route.fallback()
  target=page.locator(f'.window[data-element-owner="{identifier}"]:visible')
  note=m.direct.value(target,'Note')
  expect(note).to_have_value(b.FIRST+' Extra1');expect(note).to_be_editable()
  page.wait_for_function('()=>lateModelEditable!==null')
  print('click-to-editable ms',page.evaluate('lateModelEditable'),flush=True)
  # Release the real delayed requests even if an assertion fails.
  try:
   if external_mode:
    assert seen, 'invalidated external dependency must use the ordinary host path'
   else:
    assert not seen, 'host binding unexpectedly issued before actual edit'
   note.click();note.press('End');note.press('x');expect(note).to_have_value(b.FIRST+' Extra1x')
   key=target.get_attribute('data-key')
   target=page.locator(f'.window[data-key="{key}"]')
   expect(page.locator('#project-menu')).to_be_enabled()
   r.close(target)
  finally:
   for route in prepares:route.fallback()
   page.unroute('**/api/request',intercept)
  expect(page.locator('#project-menu')).to_be_enabled()
  expect(target).to_be_hidden()
  window=r.browser_window(page)
  r.choose_tree_location(window,f'[data-tree-id="{b.NS}::ExtraFolder1"]')
  r.search(window,b.LABEL,'Extra1')
  # Enter reopens the existing owner; "open in a new window" intentionally
  # permits a separate instance when the hidden one owns unapplied input.
  window.locator(f'[data-object="{identifier}"]').press('Enter')
  expect(target).to_be_visible()
  expect(m.direct.value(target,'Note')).to_have_value(b.FIRST+' Extra1x')
  source=f.projects[0].parent/'private-source-Extra1.celem'
  if external_mode:
   # The stale proof never binds a local model. The ordinary path remains
   # available without modifying the externally changed schema or source.
   assert source.read_bytes()==f.before[str(source)]
   assert schema.read_text().endswith('// external schema revision\n')
   print('PASS external schema invalidates late model; ordinary open and retained input',flush=True)
  else:
   m.direct.commit(page,target)
   assert 'data Note = "Fallback First Extra1x"' in source.read_text()
   print('PASS verified model arrived during click refresh; close/reopen and direct save exact owner',flush=True)
  # The second same-ID project did not participate in the write.
  other=f.projects[1].parent/'private-source-Extra1.celem'
  assert other.read_bytes()==f.before[str(other)]
finally:f.stop();print('evidence',f.root,flush=True)
