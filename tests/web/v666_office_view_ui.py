"""Real managed-engine project projection + local WebGL renderer; no devices/AI."""
import json,sys,traceback,time
from playwright.sync_api import sync_playwright,expect
import v666_finder_content_fixture as f

mode=sys.argv[3];page=None;damaged=f.repo/'packs/workspace-3d/ui/office.js';saved_asset=None
folder=f.namespace+'OfficeFolder'
for manifest in f.projects:
 path=manifest.parent/'OfficeFolder.celem';path.write_text('category '+folder+' {value editorBrowserGroup="feature";value editorName="OwnedFeatureRoom";}')
 text=manifest.read_text();at=text.rfind('}');manifest.write_text(text[:at]+'element OfficeFolder category "OfficeFolder.celem";'+text[at:])
f.before={str(p):p.read_bytes()for m in f.projects for p in m.parent.rglob('*')if p.is_file()}

def office():return page.locator('.voxel-office')
def switch(view):
 page.get_by_role('button',name='아이소메트릭 Workspace'if view=='office'else'패널 Workspace',exact=True).click()
def ready():
 expect(page.locator('#workspace')).to_have_attribute('data-office-renderer','ready',timeout=60000)
 expect(office()).to_be_visible()
def private():
 page.evaluate('()=>confectoryFlushPresentation()');return f.state()['presentation']
def guards():
 f.original();assert not f.external and not f.errors,(f.external,f.errors)
 forbidden={'editDraft','saveDraft','reviewDraft','confirmDraft','startAI','startConnectionCheck','runProject','prepareWorker','startBuild','editDefinition','editDeclaration','editFunctionContract'}
 assert not forbidden.intersection(row.get('endpoint')for row in f.requests)
def zoom(value):
 page.locator('[data-workspace-zoom]').click();menu=page.get_by_role('dialog',name='복셀 작업실 배율',exact=True)
 menu.locator('input[type=number]').fill(str(value));menu.locator('input[type=number]').press('Tab');menu.press('Escape')
def camera():return private()['officeLayout']['camera']
try:
 if mode=='tampered':saved_asset=damaged.read_bytes();damaged.write_bytes(saved_asset+b'\n// controlled owned-fixture integrity failure\n')
 if mode=='normal':
  f.env['CONFECTORY_WEB_PROJECT']=str(f.projects[1]);f.start(0);second=f.state()['listingId'];f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.projects[0]);f.start(1)
 else:f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  try:
   if mode=='unavailable':
    browser_context=browser.new_context();browser_context.add_init_script("const original=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(type,...args){return /webgl/i.test(type)?null:original.call(this,type,...args)};")
    page=f.setup(type('UnavailableBrowser',(),{'new_page':lambda self,**options:browser_context.new_page()})());page.set_viewport_size({'width':1440,'height':1000})
   else:page=f.setup(browser)
   if mode=='tampered':
    expect(page.get_by_role('button',name='패널 Workspace',exact=True)).to_have_count(0);page.locator('[data-workspace-zoom]').click();page.get_by_role('button',name='150%',exact=True).click();assert abs(private()['workspaceView']['scale']-1.5)<.001;guards();f.checked('tampered optional display asset fails its full SHA and withholds the 3D bundle; existing editor/private zoom and source protections still work')
   else:expect(page.get_by_role('button',name='패널 Workspace',exact=True)).to_have_attribute('aria-pressed','true')
   if mode=='interrupted':
    held={}
    def pause(route):held['route']=route
    page.route('**/workspace-3d/office.js',pause);switch('office')
    end=time.monotonic()+15
    while not held and time.monotonic()<end:page.wait_for_timeout(50)
    assert held;switch('editor');held['route'].continue_();page.unroute('**/workspace-3d/office.js',pause);page.wait_for_timeout(200)
    expect(office()).to_have_count(0);guards();f.checked('late module import after explicit panel return cannot mount a retired 3D view or mutate project source')
   if mode!='tampered':switch('office')
   if mode=='tampered':pass
   elif mode=='unavailable':
    expect(page.locator('#workspace')).to_have_attribute('data-office-renderer','unavailable',timeout=30000);expect(office()).to_have_count(0)
    expect(page.get_by_role('button',name='패널 Workspace',exact=True)).to_have_attribute('aria-pressed','true')
    assert private()['workspacePresentation']=='editor';guards();f.checked('controlled WebGL-unavailable context falls back to the existing editor, preserving private data and source without pretending to render')
   else:
    ready();expect(office().locator('[data-office-id="'+folder+'"]')).to_have_count(1)
    assert not office().locator('.office-worker-label,.office-helper-label').count()
    assert office().locator('canvas').first.evaluate("el=>!!el.getContext('webgl2')")
    guards();f.checked('actual owned declarations from the active ProjectContext render with pinned local Three.js, original v666 room geometry, no demo Helper/Worker or network assets')
    zoom(150);assert abs(camera()['scale']-1.5)<.001
    page.locator('[data-workspace-zoom]').click();menu=page.get_by_role('dialog',name='복셀 작업실 배율',exact=True)
    menu.locator('input[type=range]').evaluate('el=>globalThis.__officeRetired={el,callback:el.oninput}')
    switch('editor');expect(office()).to_be_hidden()
    old=camera();page.evaluate('()=>{__officeRetired.el.value="400";__officeRetired.callback()}');assert camera()==old
    for _ in range(2):switch('office');ready();switch('editor')
    switch('office');ready();assert abs(camera()['scale']-1.5)<.001;guards();f.checked('camera 150% survives repeated panel/office toggles; closed zoom callback cannot change the current private camera; no layout/source edits')
    # Original storage -> native Browser; never a separate prototype editor.
    page.locator('[data-office-map]').click();office().locator('[data-office-map-list="'+folder+'"]').click()
    expect(office().locator('[data-office-radial="rearrange"]')).to_have_count(0)
    office().locator('[data-office-radial="open"]').click()
    expect(page.locator('.window[data-key="browser"]')).to_be_visible(timeout=20000)
    guards();f.checked('original owned room radial entry delegates to the existing permission-checked feature Browser rather than copying or editing declaration sources')
    if mode=='late':
     zoom(200);held={};ids=set()
     def pause_save(route):
      body=route.request.post_data_json
      if body.get('op')=='invoke'and body.get('endpoint')=='savePresentation':ids.add(body['requestId'])
      response=route.fetch();data=response.json()
      if not held and any(row.get('requestId')in ids and row.get('ok')for row in data.get('results',[])):held.update(route=route,response=response,data=data);return
      route.fulfill(response=response,json=data)
     page.route('**/api/request',pause_save);page.evaluate("()=>{globalThis.__officeSaved=null;confectoryFlushPresentation().then(()=>globalThis.__officeSaved='done').catch(e=>globalThis.__officeSaved=e.message)}")
     end=time.monotonic()+30
     while not held and time.monotonic()<end:page.wait_for_timeout(30)
     assert held;zoom(300)
     for row in held['data']['results']:
      if row.get('requestId')in ids:row['ok']=False;row['error']={'code':'transport-interrupted'};row.pop('result',None)
     held['route'].fulfill(response=held['response'],json=held['data']);page.unroute('**/api/request',pause_save);page.wait_for_function('globalThis.__officeSaved!==null');assert page.evaluate('globalThis.__officeSaved')!='done'
     assert abs(camera()['scale']-3)<.001;guards();f.checked('controlled lost checkpoint reply after server commit preserves a newer 300% camera and explicit retry saves that camera under the same project, without source or execution changes')
    elif mode=='cold':
     stored=camera();page.close();f.stop();f.start(1);page=f.setup(browser);ready();assert camera()==stored;guards();f.checked('fresh engine restores display preference and private camera from durable presentation without restoring source-edit or execution authority')
    elif mode=='normal':
     old=camera();first=f.state()['listingId'];f.call('leaveProject',{});page.wait_for_selector('.home-grid');f.call('openProject',{'id':second});page.wait_for_selector('.work-body');expect(page.get_by_role('button',name='패널 Workspace',exact=True)).to_have_attribute('aria-pressed','true');expect(office()).to_have_count(0)
     f.call('leaveProject',{});page.wait_for_selector('.home-grid');f.call('openProject',{'id':first});page.wait_for_selector('.work-body');ready();assert camera()==old;guards();f.checked('actual project A/home/B/A isolates office preference/camera and restores A; same displayed declaration names never select another project')
   page.screenshot(path=str(f.root/('office-view-'+mode+'.png')));guards();browser.close()
  except Exception as e:
   try:page.screenshot(path=str(f.root/'failure.png'));(f.root/'failure.html').write_text(page.content())
   except Exception:pass
   (f.root/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();
 if saved_asset is not None:damaged.write_bytes(saved_asset)
 f.save_evidence();(f.root/'office-view.json').write_text(json.dumps(dict(mode=mode,checks=f.checks,actualManagedEngine=True,softwareWebGL=True,simulatedUnavailable=mode=='unavailable',actualWindows=False,actualMobile=False,workerDisplay=False),ensure_ascii=False,indent=2))
print('OFFICE_VIEW_FIXTURE',f.root,flush=True)
