"""Real transport admission race during an ordinary detached property drop.

Run with REPO BUILD_REPORT and the standard web fixture environment. The
first actual request is held while another host view changes the revision.
No response is fabricated. The UI must retry and open exactly its own ID.
"""
import time
import v821_property_window_reopen_ui as r
from playwright.sync_api import sync_playwright,expect
f=r.fixture;d=r.fallback;r.seed();expect.set_options(timeout=60000)
try:
 with sync_playwright() as p,p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu']) as b:
  f.start(0);page=f.setup(b);page.set_viewport_size({'width':2000,'height':1200});browser=r.browser_window(page);r.choose_tree_location(browser,f'[data-tree-id="{d.NS}::StockFolder"]');r.search(browser,d.LABEL,d.TARGET);item=browser.locator(f'[data-object="{r.owner}"]');expect(page.locator('#project-menu')).to_be_enabled()
  held=[];seen=[]
  def intercept(route):
   payload=route.request.post_data_json if route.request.method=='POST' else {}
   if payload.get('op')=='invoke' and payload.get('endpoint')=='openEditorView':
    seen.append(payload.get('expectedRevision'))
    if len(seen)==1:held.append(route);return
   route.fallback()
  page.route('**/api/request',intercept)
  canvas=page.locator('#workspace').bounding_box();item.drag_to(page.locator('#workspace'),target_position={'x':canvas['width']*.82,'y':canvas['height']*.62})
  deadline=time.monotonic()+10
  while not held and time.monotonic()<deadline:page.wait_for_timeout(20)
  assert len(held)==1,seen
  # A real independent host command moves the shared cursor revision while
  # the actual UI invoke waits; no fake stale reply is injected.
  try:f.call('select',{'id':r.peer})
  finally:held[0].continue_()
  target=page.locator('.window[data-key="editor-1"]');expect(r.floating.property_value(target,'Note')).to_be_editable();expect(page.locator('#project-menu')).to_be_enabled();assert len(seen)>=2 and seen[0]!=seen[-1],seen
  rows=f.state()['editorViews'];assert len(rows)==1 and rows[0]['id']==r.owner,rows;f.original();print('PASS actual stale transport admission retried once with new revision, one correct view',seen,flush=True)
finally:f.stop();print('evidence',f.root,flush=True)
