"""Actual Blueprint presentation and pin gestures through the ordinary Home host."""
import json,time,uuid
from playwright.sync_api import expect

def verify_blueprint_camera(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':1440,'height':1000});graph='Example.ButtonGame::NodeValueBody/body:common';other='Example.ButtonGame::OtherValueBody/body:common';before={p:p.read_bytes() for p in project.iterdir() if p.is_file()};calls=[]
 def record(request):
  if request.url.endswith('/api/request'):
   try:
    payload=json.loads(request.post_data or '{}')
    if payload.get('op')=='invoke':calls.append((payload.get('endpoint'),payload.get('input')))
   except ValueError:pass
 page.on('request',record)
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=180000)
 def state():
  v=mount();result=v['state'];assert send(envelope(v,'dispose'))['ok'];return result
 def invoke(endpoint,args):
  v=mount();request=uuid.uuid4().hex;assert send(envelope(v,'invoke',endpoint=endpoint,requestId=request,expectedRevision=v['revision'],input=args))['ok'];deadline=time.monotonic()+180;result=None
  while time.monotonic()<deadline:
   reply=send(envelope(v,'update'));assert reply['ok'];result=next((x for x in reply.get('results',[]) if x['requestId']==request),None)
   if result:break
   time.sleep(.02)
  assert result and result['ok'],result;assert send(envelope(v,'dispose'))['ok'];return result['result']
 def panel():return page.locator('.window[data-key="blueprint"]')
 def saved():page.evaluate('()=>globalThis.confectoryFlushPresentation()');return state()['presentation']
 def meta():
  data=saved();return next(row for row in data['layout']+data.get('windowDocuments',[]) if row['key']=='blueprint')['meta']
 def zoom(value):panel().locator('[data-bp-zoom]').fill(str(value))
 def drag(locator,dx,dy,button='left',cancel=False):
  box=locator.bounding_box();assert box;page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2);page.mouse.down(button=button);page.mouse.move(box['x']+box['width']/2+dx,box['y']+box['height']/2+dy,steps=6)
  if cancel:page.keyboard.press('Escape')
  page.mouse.up(button=button)
 ready();root_before=saved()['workspaceView'];area=page.locator('#workspace').bounding_box();point=None
 for fx in [.96,.8,.5,.2]:
  for fy in [.2,.65,.8]:
   candidate={'x':round(area['x']+area['width']*fx),'y':round(area['y']+area['height']*fy)}
   if page.evaluate("p=>{const el=document.elementFromPoint(p.x,p.y);return el?.closest('#workspace')&&!el.closest('.window,.workspace-decoration,.bubble-dock,.workspace-tabs')}",candidate):point=candidate;break
  if point:break
 assert point,'no actual blank Workspace point';page.mouse.move(point['x'],point['y']);page.mouse.wheel(0,200);deadline=time.monotonic()+5
 while saved()['workspaceView']['scale']>=root_before['scale'] and time.monotonic()<deadline:time.sleep(.02)
 assert saved()['workspaceView']['scale']<root_before['scale'],'native outer Workspace zoom was not applied'
 page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name='기능 Blueprint',exact=True).click();ready();expect(panel().locator('[data-bp-node]')).to_have_count(2);initial=invoke('blueprint',{'action':'read','id':graph});workspace=saved()['workspaceView']
 # Free precision, bounds, presets and uncommitted zoom-text Escape.
 panel().locator('[data-bp-percent]').click();menu=page.get_by_role('dialog',name='노드 화면 배율',exact=True);value=menu.locator('[data-zoom-value]');value.fill('137.125');value.press('Enter');expect(panel().locator('[data-bp-zoom]')).to_have_value('137.125');value.fill('44');value.press('Escape');expect(menu).to_have_count(0);expect(panel().locator('[data-bp-zoom]')).to_have_value('137.125')
 panel().locator('[data-bp-percent]').click();menu.locator('[data-zoom-preset="3.125"]').click();expect(panel().locator('[data-bp-zoom]')).to_have_value('3.125');menu.locator('[data-zoom-value]').fill('999');menu.locator('[data-zoom-value]').press('Enter');expect(panel().locator('[data-bp-zoom]')).to_have_value('300');menu.locator('[data-zoom-value]').press('Escape');zoom(100)
 # A real wheel keeps the world point under the pointer, including the outer Workspace scale.
 viewport=panel().locator('.bp-scroll');area=viewport.bounding_box();point={'x':round(area['x']+area['width']*.62),'y':round(area['y']+area['height']*.2)};local=viewport.evaluate('(el,p)=>({x:(p.x-el.getBoundingClientRect().left)/(el.getBoundingClientRect().width/el.offsetWidth),y:(p.y-el.getBoundingClientRect().top)/(el.getBoundingClientRect().height/el.offsetHeight)})',point);prior=meta();world={k:(local[k]-prior['blueprintCamera'][k])/(prior['blueprintZoom']/100) for k in ['x','y']};page.mouse.move(point['x'],point['y']);page.mouse.wheel(0,100);expect(panel().locator('[data-bp-zoom]')).to_have_value('87.5');after=meta();assert all(abs((local[k]-after['blueprintCamera'][k])/(after['blueprintZoom']/100)-world[k])<.05 for k in world),{'local':local,'world':world,'prior':prior,'after':after,'area':area};assert saved()['workspaceView']==workspace,{'workspaceBefore':workspace,'workspaceAfter':saved()['workspaceView']}
 page.mouse.wheel(0,-100);expect(panel().locator('[data-bp-zoom]')).to_have_value('100');panel().locator('[data-bp-fit]').click();fitted=meta();assert .03125<=fitted['blueprintZoom']/100<=1
 for card in panel().locator('[data-bp-node]').all():
  box=card.bounding_box();area=viewport.bounding_box();assert box['x']>=area['x']-1 and box['y']>=area['y']-1 and box['x']+box['width']<=area['x']+area['width']+1 and box['y']+box['height']<=area['y']+area['height']+1,(box,area)
 # Header moves are presentation only; Escape restores the original position.
 header=panel().locator('[data-bp-drag="calculate"]');prior=meta()['blueprintPositions'];internal=meta()['blueprintZoom']/100;outer=viewport.evaluate('el=>el.getBoundingClientRect().width/el.offsetWidth');drag(header,30,12);moved=meta()['blueprintPositions'];assert abs(moved['calculate']['x']-prior['calculate']['x']-30/(internal*outer))<1,(prior,moved,internal,outer);drag(header,25,8,cancel=True);assert meta()['blueprintPositions']==moved
 prior=meta()['blueprintCamera'];drag(viewport,35,18,button='middle');assert meta()['blueprintCamera']!=prior;prior=meta()['blueprintCamera'];drag(viewport,20,10,button='right',cancel=True);assert meta()['blueprintCamera']==prior;assert saved()['workspaceView']==workspace
 # Graph-local cameras/layout and selected inspector survive tab switches with identical node IDs.
 panel().locator('[data-bp-select="calculate"]').click();intent=panel().locator('[data-bp-intent]');intent.fill('CAMERA_PENDING_INTENT');zoom(93.75);first=meta();panel().locator('[data-bp-tab="'+other+'"]').click();ready();expect(panel().locator('[data-bp-zoom]')).to_have_value('100');zoom(125);panel().locator('[data-bp-tab="'+graph+'"]').click();ready();expect(panel().locator('[data-bp-zoom]')).to_have_value('93.75');expect(panel().locator('[data-bp-intent]')).to_have_value('CAMERA_PENDING_INTENT');assert meta()['blueprintCamera']==first['blueprintCamera'] and meta()['blueprintPositions']==first['blueprintPositions']
 panel().locator('[data-bp-fit]').click();panel().locator('[data-bp-code-open="calculate"]').click();code=page.locator('.window[data-key="blueprint-code:'+graph+'/calculate"]');code.locator('[data-bp-code]').fill('return value + 77; // CAMERA_PENDING_CODE');code.locator('[data-close]').click()
 # Execution output -> header drag stages a route, and Escape clears a pending wire.
 start=panel().locator('[data-bp-exec-out="condition"][data-exec-port="false"]');target=panel().locator('[data-bp-exec-target="calculate"]');start.drag_to(target);expect(panel().locator('[data-bp-route="false"]')).to_have_value('calculate');panel().locator('[data-bp-exec-out="condition"][data-exec-port="true"]').click();page.keyboard.press('Escape');expect(panel().locator('.bp-wire-preview')).to_have_count(0)
 panel().locator('[data-bp-select="calculate"]').click();expect(panel().locator('[data-bp-intent]')).to_have_value('CAMERA_PENDING_INTENT');arg=panel().locator('[data-bp-argument="value"]');arg.fill('{"constant":9223372036854775806}');panel().locator('[data-bp-input-pin="calculate"]').click();picker=page.get_by_role('dialog',name='value 입력 값',exact=True);picker.get_by_role('button',name='취소',exact=True).click();expect(arg).to_have_value('{"constant":9223372036854775806}');panel().locator('[data-bp-input-pin="calculate"]').click();picker.get_by_role('button',name='입력 n · long',exact=True).click();expect(arg).to_have_value('{"input":"n"}');expect(panel().locator('[data-bp-exit="fallback"]')).to_have_value('{"constant":9223372036854775807}')
 panel().locator('[data-bp-exec-out="calculate"]').click();panel().locator('[data-bp-exec-exit="fallback"]').click();expect(panel().locator('[data-bp-route="next"]')).to_have_value('exit:fallback');assert invoke('blueprint',{'action':'read','id':graph})['sources']==initial['sources'];assert all(p.read_bytes()==raw for p,raw in before.items())
 # Zoom/headers/pickers preserve unsent code and ordinary cold basis rules.
 zoom(112.125);expected=meta();panel().evaluate('el=>globalThis.__cameraDomainWindow=el');panel().locator('.window-title').click(button='right',position={'x':100,'y':18});page.locator('.context-menu').get_by_role('button',name='탭으로 열기',exact=True).click();expect(panel()).to_have_class('window window-document tab-document');assert panel().evaluate('el=>el===globalThis.__cameraDomainWindow');assert meta()['blueprintCamera']==expected['blueprintCamera'];panel().locator('[data-bp-input-pin="calculate"]').click();expect(page.get_by_role('dialog',name='value 입력 값',exact=True)).to_be_visible();page.locator('#workspace-home-tab').click();expect(page.locator('.bp-pin-menu,.bp-zoom-menu')).to_have_count(0);page.locator('[data-window-tab="blueprint"]').click();expect(panel().locator('[data-bp-intent]')).to_have_value('CAMERA_PENDING_INTENT');assert meta()['blueprintCamera']==expected['blueprintCamera'];page.screenshot(path='/tmp/confectory-v480-blueprint-camera.png',full_page=True);invoke('saveDraft',{});restart();ready();expect(panel().locator('[data-bp-node]')).to_have_count(0);panel().locator('[data-bp-read]').click();ready();expect(panel().locator('[data-bp-zoom]')).to_have_value('112.125');expect(panel().locator('[data-bp-intent]')).to_have_value('CAMERA_PENDING_INTENT');expect(panel().locator('[data-bp-route="next"]')).to_have_value('exit:fallback');assert meta()['blueprintCamera']==expected['blueprintCamera'] and meta()['blueprintPositions']==expected['blueprintPositions'];panel().locator('[data-bp-code-open="calculate"]').click();expect(code.locator('[data-bp-code]')).to_have_value('return value + 77; // CAMERA_PENDING_CODE');code.locator('[data-apply]').click();ready();expect(page.locator('#status')).to_contain_text('기준 재검토');code.locator('[data-close]').click();page.locator('[data-window-tab="blueprint"]').click()
 page.locator('.brand').click();page.locator('#home-projects').wait_for();expect(page.locator('.bp-pin-menu,.bp-zoom-menu')).to_have_count(0);page.locator('[data-enter]').click();ready();panel().locator('[data-bp-read]').click();ready();expect(panel().locator('[data-bp-intent]')).to_have_value('CAMERA_PENDING_INTENT');expect(panel().locator('[data-bp-zoom]')).to_have_value('112.125');assert meta()['blueprintCamera']==expected['blueprintCamera'];assert all(p.read_bytes()==raw for p,raw in before.items())
 assert viewport.evaluate('el=>[el.scrollLeft,el.scrollTop]')==[0,0],'camera view contains an unrecorded DOM scroll'
 assert not state()['aiOwnerAvailable'] and not state()['planningOwnerAvailable'];forbidden={'editDraft','editField','editMetadata','editDeclaration','reviewDraft','confirmDraft','reviewGroup','confirmGroup','runProject','startAI','prepareAI','nodeTask','startBuild'};assert not forbidden.intersection(endpoint for endpoint,_ in calls),calls
 assert all(not isinstance(payload,dict) or payload.get('action') in {'list','read'} for endpoint,payload in calls if endpoint=='blueprint'),calls
 page.screenshot(path='/tmp/confectory-v480-blueprint-camera-cold.png',full_page=True)
 print('PASS actual v480 Blueprint camera: precise zoom/wheel anchor, pan and header cancellation, graph-local tabs/layout, typed pin and header route staging only, exact pending values, cold/Home and source preservation',flush=True)
