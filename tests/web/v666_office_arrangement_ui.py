"""Actual private presentation + original 3D controls; no source or account writes."""
import json,sys,time,traceback,pathlib
from playwright.sync_api import sync_playwright,expect
import v666_finder_content_fixture as f
mode=sys.argv[3];page=None
def office():return page.locator('.voxel-office')
def ready():expect(page.locator('#workspace')).to_have_attribute('data-office-renderer','ready');expect(office()).to_be_visible();expect(page.locator('#office-arrange-bubble')).to_have_count(1)
def switch(view):page.get_by_role('button',name='아이소메트릭 Workspace'if view=='office'else'패널 Workspace',exact=True).click()
def private():page.evaluate('()=>confectoryFlushPresentation()');return f.state()['presentation']
def guards():
 f.original();assert not f.errors and not f.external,(f.errors,f.external)
 assert not {'editDraft','saveDraft','reviewDraft','confirmDraft','startAI','prepareWorker','runProject','editDefinition','editDeclaration','editFunctionContract'}.intersection(row.get('endpoint')for row in f.requests)
def zoom(value):
 page.locator('[data-workspace-zoom]').click();m=page.get_by_role('dialog',name='복셀 작업실 배율',exact=True);m.locator('input[type=number]').fill(str(value));m.locator('input[type=number]').press('Tab');m.press('Escape')
def begin():page.locator('#office-arrange-bubble').click();expect(office().locator('.office-build-catalog')).to_be_visible();expect(office().locator('[data-office-undo]')).to_be_disabled()
def place():
 # Original room labels are intentionally hidden above 90%; use the real zoom
 # control to choose a visible ground anchor, without forcing hidden elements.
 zoom(90)
 button=office().locator('[data-office-build-kind=plant]');button.focus();button.press('Enter');box=office().locator('.office-room-label[data-office-id="__lobby"]').bounding_box();assert box;cx=box['x']+box['width']/2;cy=box['y']+box['height']/2
 for dx,dy in [(-70,35),(70,35),(-110,30),(110,30),(0,85),(-60,-40),(60,-40),(-120,0),(120,0)]:
  page.mouse.move(cx+dx,cy+dy);page.mouse.click(cx+dx,cy+dy)
  if button.get_attribute('aria-pressed')!='true':break
 assert button.get_attribute('aria-pressed')!='true','owned fixture found no free lobby tile';expect(office().locator('[data-office-undo]')).to_be_enabled()
def confirm():office().locator('[data-office-build-confirm]').click();expect(office().locator('.office-build-catalog')).to_be_hidden()
def cancel():office().locator('[data-office-build-cancel]').click();expect(office().locator('.office-build-catalog')).to_be_hidden()
def retire():office().locator('[data-office-build-confirm]').evaluate('el=>globalThis.__retiredOfficeConfirm=el.onclick')
def late_callback():page.evaluate('()=>__retiredOfficeConfirm()')
try:
 f.env['CONFECTORY_WEB_PROJECT']=str(f.projects[1]);f.start(0);second=f.state()['listingId'];f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.projects[0]);f.start(1)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']);page=f.setup(browser)
  try:
   first=f.state()['listingId'];switch('office');ready();baseline=private();assert baseline['officeLayout']['props']==[];guards()
   begin();button=office().locator('[data-office-build-kind=plant]');button.focus();button.press('Enter');box=office().locator('.office-scene>canvas').bounding_box();page.mouse.click(box['x']+box['width']/2,box['y']+8);expect(office().locator('[data-office-undo]')).to_be_disabled();assert private()['officeLayout']['props']==[];guards();f.checked('real private arrangement controls open; invalid floor placement changes no committed geometry or source')
   place();zoom(150);assert private()['officeLayout']['props']==[];assert private()['officeLayout']['camera']['scale']==1.5;page.screenshot(path=str(f.root/'arrangement-provisional.png'))
   office().locator('[data-office-undo]').click();expect(office().locator('[data-office-redo]')).to_be_enabled();office().locator('[data-office-redo]').click();expect(office().locator('[data-office-redo]')).to_be_disabled();assert private()['officeLayout']['props']==[]
   retire();switch('editor');late_callback();assert private()['officeLayout']['props']==[];switch('office');ready();expect(office().locator('.office-build-catalog')).to_be_visible();cancel();assert private()['officeLayout']['props']==[];guards();f.checked('unconfirmed furniture survives panel pause but stays outside all checkpoints; current camera persists; Undo/Redo, stale hidden Confirm and explicit cancel preserve the committed arrangement')
   begin();place();confirm();saved=private();assert len(saved['officeLayout']['props'])==1;original=saved['officeLayout']['props'];guards();f.checked('explicit original arrangement Confirm persists one private furniture identity without source/contract/permission/Task operations')
   if mode=='late':
    files=[x for x in(f.root/'profile').rglob('*.json')if x.parent.name=='presentations'];assert len(files)==1,files;path=files[0];old_mode=path.stat().st_mode&0o777;before=path.read_bytes();path.chmod(0o400)
    try:
     begin();place();confirm();error=page.evaluate('()=>confectoryFlushPresentation().then(()=>null).catch(e=>e.message)');assert error;assert path.read_bytes()==before;assert len(f.state()['presentation']['officeLayout']['props'])==1
    finally:path.chmod(old_mode)
    saved=private();assert len(saved['officeLayout']['props'])==2;guards();f.checked('actual owned read-only presentation write rejects atomically; confirmed in-memory placement survives and explicit retry saves both identities after restoring only fixture permissions')
    zoom(200);held={};ids=set()
    def pause(route):
     body=route.request.post_data_json
     if body.get('op')=='invoke'and body.get('endpoint')=='savePresentation':ids.add(body['requestId'])
     response=route.fetch();data=response.json()
     if not held and any(row.get('requestId')in ids and row.get('ok')for row in data.get('results',[])):held.update(route=route,response=response,data=data);return
     route.fulfill(response=response,json=data)
    page.route('**/api/request',pause);page.evaluate("()=>{globalThis.__saveResult=null;confectoryFlushPresentation().then(()=>__saveResult='done').catch(e=>__saveResult=e.message)}")
    end=time.monotonic()+30
    while not held and time.monotonic()<end:page.wait_for_timeout(30)
    assert held;begin();place();zoom(300)
    for row in held['data']['results']:
     if row.get('requestId')in ids:row['ok']=False;row['error']={'code':'transport-interrupted'};row.pop('result',None)
    held['route'].fulfill(response=held['response'],json=held['data']);page.unroute('**/api/request',pause);page.wait_for_function('()=>__saveResult!==null');assert page.evaluate('__saveResult')!='done';assert len(f.state()['presentation']['officeLayout']['props'])==2
    assert private()['officeLayout']['camera']['scale']==3;assert len(private()['officeLayout']['props'])==2;cancel();guards();f.checked('post-commit lost reply keeps newer camera and pending furniture separate; retry retains two committed props, never publishes the newer unconfirmed third prop')
   else:
    begin();place();assert private()['officeLayout']['props']==original;page.close();f.stop();f.start(2);page=f.setup(browser);ready();assert private()['officeLayout']['props']==original;guards();f.checked('new engine cold restore retains exact confirmed furniture IDs/geometry while explicitly checkpointed provisional furniture never becomes durable')
   # Existing child Workspace creation is fixture input, not a new shared policy.
   value=private();root_props=value['officeLayout']['props'];child='owned-office-child';value['workspaces'].append(dict(id=child,name='Private office child',parentId='root',layout=[],view=dict(x=0,y=0,scale=1),items=[]));value['visitedWorkspaceTabs'].append(child);f.call('savePresentation',{'presentation':value});page.reload();page.wait_for_selector('.work-body');ready();page.locator('#workspace-tab-'+child).click();switch('office');ready();begin();place();confirm();child_value=private();assert child_value['activeWorkspaceId']==child;assert child_value['officeLayout']['props']==root_props;assert len(next(x for x in child_value['workspaces']if x['id']==child)['officeLayout']['props'])==1
   begin();place();retire();page.get_by_role('tab',name='Workspace',exact=True).click();ready();late_callback();root_value=private();assert root_value['officeLayout']['props']==root_props;assert len(next(x for x in root_value['workspaces']if x['id']==child)['officeLayout']['props'])==1;guards();f.checked('actual child/root navigation isolates private arrangement owners; leaving an unconfirmed child restores its committed geometry and retired child Confirm cannot mutate root')
   begin();place();retire();f.call('leaveProject',{});page.wait_for_selector('.home-grid');f.call('openProject',{'id':second});page.wait_for_selector('.work-body');switch('office');ready();late_callback();assert private()['officeLayout']['props']==[];f.call('leaveProject',{});page.wait_for_selector('.home-grid');f.call('openProject',{'id':first});page.wait_for_selector('.work-body');ready();assert private()['officeLayout']['props']==root_props;guards();f.checked('home/other same-namespace project/A return never applies stale arrangement or source changes; current private owner and confirmed layout are preserved')
   page.screenshot(path=str(f.root/'arrangement-final.png'));browser.close()
  except Exception as e:
   try:page.screenshot(path=str(f.root/'failure.png'));(f.root/'failure.html').write_text(page.content())
   except Exception:pass
   (f.root/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();f.save_evidence();(f.root/'arrangement.json').write_text(json.dumps(dict(mode=mode,checks=f.checks,actualManagedEngine=True,actualWindows=False,actualMobile=False,wholeUI=False),ensure_ascii=False,indent=2))
