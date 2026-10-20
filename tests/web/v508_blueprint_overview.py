from editor_navigation import open_project_tools
"""v508 overview through the ordinary Home host; source and pending edit bases stay owned."""
import copy,json,shutil,time,uuid
from playwright.sync_api import expect

def prepare_overview(project,root):
 second=root/'second-project';shutil.copytree(project,second,ignore=shutil.ignore_patterns('.confectory'));storage=root/'storage';storage.mkdir(exist_ok=True)
 (storage/'projects.json').write_text(json.dumps([dict(path=str(p/'project.cpack'),title=t,description='Owned overview fixture') for p,t in [(project,'Overview A'),(second,'Overview B')]]))

def verify_overview(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':2200,'height':1400});graph='Example.ButtonGame::NodeValueBody/body:common';other='Example.ButtonGame::OtherValueBody/body:common';original={p:p.read_bytes() for d in [project,project.parent/'second-project'] for p in d.iterdir() if p.is_file()};calls=[]
 def record(request):
  if request.url.endswith('/api/request'):
   try:
    p=json.loads(request.post_data or '{}')
    if p.get('op')=='invoke':calls.append((p.get('endpoint'),p.get('input')))
   except ValueError:pass
 page.on('request',record)
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=180000)
 def window(key):return page.locator('.window[data-key="'+key+'"]')
 def state():
  v=mount();s=v['state'];assert send(envelope(v,'dispose'))['ok'];return s
 def saved():page.evaluate('()=>globalThis.confectoryFlushPresentation()');return state()['presentation']
 def invoke(endpoint,args):
  v=mount();rid=uuid.uuid4().hex;assert send(envelope(v,'invoke',endpoint=endpoint,input=args,requestId=rid,expectedRevision=v['revision']))['ok'];result,_=settle(v,rid);assert result['ok'],result;assert send(envelope(v,'dispose'))['ok'];return result.get('result')
 def panel():return window('blueprint')
 def front():
  title=panel().locator('.window-title');point=title.evaluate("e=>{const r=e.getBoundingClientRect();for(const f of [.8,.6,.3,.95]){const x=Math.floor(r.width*f),y=18,hit=document.elementFromPoint(r.left+x,r.top+y);if(hit&&e.contains(hit)&&!hit.closest('button'))return {x,y}}return null}");assert point;title.click(position=point)
 def overview():return panel().locator('[data-bp-overview]')
 def meta():return next(r for r in saved()['layout']+saved().get('windowDocuments',[]) if r['key']=='blueprint')['meta']
 def camera():return meta()['blueprintCamera']
 def nav(label):
  ready();open_project_tools(page);page.locator('.nav-menu').get_by_role('button',name=label,exact=True).click();ready()
  if page.locator('.nav-menu').count():open_project_tools(page)
 def position(key,x,y):
  title=window(key).locator('.window-title');b=title.bounding_box();assert b;page.mouse.move(b['x']+120,b['y']+18);page.mouse.down();page.mouse.move(x+120,y+18,steps=10);page.mouse.up();ready()
 def source_inputs(dom=True):
  expect(page.locator('#source')).to_have_value(source_pending);expect(window('editor-1').locator('[data-description]')).to_have_value(property_pending)
  if dom:
   assert page.locator('#source').evaluate('e=>e===globalThis.__overviewSource');assert window('editor-1').locator('[data-description]').evaluate('e=>e===globalThis.__overviewProperty')
  assert saved()['inputs']['source']['draft']==source_basis
 def intact(dom=True):
  source_inputs(dom);assert all(p.read_bytes()==raw for p,raw in original.items())
 def drag_cancel(kind):
  before=camera();b=overview().bounding_box();page.mouse.move(b['x']+25,b['y']+15);page.mouse.down();page.mouse.move(b['x']+b['width']*.85,b['y']+b['height']*.7,steps=5)
  if kind=='Escape':page.keyboard.press('Escape')
  elif kind=='pointercancel':overview().evaluate("e=>e.dispatchEvent(new PointerEvent('pointercancel',{pointerId:1,bubbles:true}))")
  else:overview().evaluate('e=>e.releasePointerCapture(1)');page.wait_for_timeout(80)
  page.mouse.up();assert camera()==before,kind
 nav('개념');page.locator('[data-id="Example.ButtonGame::Score"]').click();expect(window('schema').locator('[data-description]')).to_be_visible(timeout=120000);window('schema').locator('[data-close]').click();page.locator('#browser-actions').click();page.locator('#keep-properties').click();ready();position('editor-1',1450,180);page.locator('#browser-actions').click();page.locator('#advanced-source').click();ready();position('source',600,800)
 source_pending=page.locator('#source').input_value()+'\n// OVERVIEW_PENDING_SOURCE';property_pending='OVERVIEW_PROPERTY_PENDING';page.locator('#source').fill(source_pending);window('editor-1').locator('[data-description]').fill(property_pending);page.locator('#source').evaluate('e=>globalThis.__overviewSource=e');window('editor-1').locator('[data-description]').evaluate('e=>globalThis.__overviewProperty=e');source_basis=copy.deepcopy(saved()['inputs']['source']['draft'])
 nav('기능 Blueprint');expect(overview().locator('[data-bp-overview-node]')).to_have_count(2);initial=invoke('blueprint',dict(action='read',id=graph));outer=copy.deepcopy(saved()['workspaceView']);positions=copy.deepcopy(meta()['blueprintPositions']);signature=copy.deepcopy(initial['signature']);routes=copy.deepcopy(initial['edges']);profile=initial['profile'];assert profile=='sync-acyclic-v1'
 panel().locator('[data-bp-select="calculate"]').click();panel().locator('[data-bp-intent]').fill('OVERVIEW_PENDING_INTENT');panel().locator('[data-bp-argument="value"]').fill('{"constant":9223372036854775806}');panel().locator('[data-bp-code-open="calculate"]').click();code=window('blueprint-code:'+graph+'/calculate');code.locator('[data-bp-code]').fill('return value + 77; // OVERVIEW_PENDING_CODE');code.locator('[data-close]').click()
 panel().locator('[data-bp-zoom]').fill('137.125');before=camera();b=overview().bounding_box();overview().click(position={'x':b['width']*.8,'y':b['height']*.6});assert camera()!=before;assert meta()['blueprintZoom']==137.125 and meta()['blueprintPositions']==positions;overview().focus();overview().press('Home');home=camera();overview().press('ArrowRight');right=camera();overview().press('Shift+ArrowRight');shift=camera();assert right['x']<home['x'] and abs(shift['x']-right['x'])>abs(right['x']-home['x']);overview().press('ArrowDown');overview().press('PageDown');assert camera()['y']<home['y'];overview().press('End')
 for kind in ['Escape','pointercancel','lostpointercapture']:drag_cancel(kind)
 intact();expect(panel().locator('[data-bp-intent]')).to_have_value('OVERVIEW_PENDING_INTENT');expect(panel().locator('[data-bp-argument="value"]')).to_have_value('{"constant":9223372036854775806}');assert saved()['workspaceView']==outer
 # Moving the existing header updates private placement and the map, not ABI or source.
 panel().locator('[data-bp-fit]').click();before=copy.deepcopy(meta()['blueprintPositions']);header=panel().locator('[data-bp-drag="calculate"] span').first;h=header.bounding_box();page.mouse.move(h['x']+h['width']/2,h['y']+h['height']/2);page.mouse.down();page.mouse.move(h['x']+h['width']/2+35,h['y']+h['height']/2+12,steps=6);page.mouse.up();assert meta()['blueprintPositions']['calculate']!=before['calculate'];expect(overview().locator('[data-bp-overview-node="calculate"]')).to_have_count(1)
 # Switching graphs during capture cancels the provisional camera on the old graph.
 expected=copy.deepcopy(camera());b=overview().bounding_box();page.mouse.move(b['x']+20,b['y']+12);page.mouse.down();page.mouse.move(b['x']+b['width']*.85,b['y']+30);panel().locator('[data-bp-tab="'+other+'"]').focus();page.keyboard.press('Enter');ready();page.mouse.up();assert meta()['blueprintGraph']==other and meta()['blueprintViews'][graph]['camera']==expected;overview().focus();overview().press('End');second_camera=copy.deepcopy(camera());panel().locator('[data-bp-tab="'+graph+'"]').click();ready();assert camera()==expected;intact()
 # A project with the same graph/node IDs has an independent camera and input scope.
 expected_positions=copy.deepcopy(meta()['blueprintPositions']);page.locator('.brand').click();page.locator('[data-project]').filter(has_text='Overview B').locator('[data-enter]').click();ready();nav('기능 Blueprint');expect(overview().locator('[data-bp-overview-node]')).to_have_count(2);assert meta()['blueprintZoom']==100;overview().focus();overview().press('End');b_camera=copy.deepcopy(camera());page.locator('.brand').click();page.locator('[data-project]').filter(has_text='Overview A').locator('[data-enter]').click();ready();panel().locator('[data-bp-read]').click();ready();assert camera()==expected and meta()['blueprintPositions']==expected_positions;intact(False)
 # No ordering, new execution profile, source write, or hidden Apply occurred.
 after=invoke('blueprint',dict(action='read',id=graph));assert after['sources']==initial['sources'] and after['signature']==signature and after['edges']==routes and after['profile']==profile
 expected=copy.deepcopy(camera());page.screenshot(path='/tmp/confectory-v508-overview.png',full_page=True);invoke('saveDraft',{});restart();ready();expect(panel().locator('[data-bp-node]')).to_have_count(0);front();panel().locator('[data-bp-read]').click();ready();expect(overview().locator('[data-bp-overview-node]')).to_have_count(2);assert camera()==expected and meta()['blueprintPositions']==expected_positions;intact(False);panel().locator('[data-bp-select="calculate"]').click();expect(panel().locator('[data-bp-intent]')).to_have_value('OVERVIEW_PENDING_INTENT');expect(panel().locator('[data-bp-argument="value"]')).to_have_value('{"constant":9223372036854775806}')
 panel().locator('[data-bp-code-open="calculate"]').click();expect(code.locator('[data-bp-code]')).to_have_value('return value + 77; // OVERVIEW_PENDING_CODE');code.locator('[data-apply]').click();ready();expect(page.locator('#status')).to_contain_text('기준 재검토');expect(code.locator('[data-bp-code]')).to_have_value('return value + 77; // OVERVIEW_PENDING_CODE');assert invoke('blueprint',dict(action='read',id=graph))['sources']==initial['sources'];intact(False)
 forbidden={'editDraft','editField','editMetadata','editDeclaration','reviewDraft','confirmDraft','reviewGroup','confirmGroup','runProject','startAI','prepareAI','nodeTask','startBuild'};assert not forbidden.intersection(e for e,_ in calls),calls;assert all(a.get('action') in {'list','read'} for e,a in calls if e=='blueprint'),calls
 assert panel().locator('.bp-scroll').evaluate('e=>[e.scrollLeft,e.scrollTop]')==[0,0]
 evidence=dict(initialNodes=2,graphIds=[graph,other],sameNodeIds=True,projects=2,zoom=137.125,worldCamera=expected,otherGraphCamera=second_camera,otherProjectCamera=b_camera,pendingSourcePropertyIntentArgumentsCode=True,originalInputBasisPreserved=True,coldApplyRefused=True,sourceSignatureEdgesProfileUnchanged=True,originalFiles=len(original),cancellation=['Escape','pointercancel','lostpointercapture','graph-switch'],actualBrowser='Chromium ordinary EditorHome host')
 from pathlib import Path
 Path('/workspace/scratch/confectory-v508-overview-ui.json').write_text(json.dumps(evidence,indent=2)+'\n');print('PASS actual v508 Blueprint overview '+json.dumps(evidence),flush=True)
