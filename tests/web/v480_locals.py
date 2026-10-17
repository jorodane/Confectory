"""Actual local declaration/set editing with exact JSON, cold input fencing and compiler Confirm."""
import json,uuid,time
from playwright.sync_api import expect

def verify_locals(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':1700,'height':1150});graph='Example.ButtonGame::NodeValueBody/body:common';before={p:p.read_bytes() for p in project.iterdir() if p.is_file()};calls=[]
 def record(request):
  if request.url.endswith('/api/request'):
   try:
    p=json.loads(request.post_data or '{}')
    if p.get('op')=='invoke':calls.append(p.get('endpoint'))
   except ValueError:pass
 page.on('request',record)
 def ready():
  expect(page.locator('#nav')).to_be_enabled(timeout=180000);expect(page.locator('#workspace-save-state')).not_to_contain_text('편집창 복원 중',timeout=180000)
 def invoke(endpoint,args):
  v=mount();request=uuid.uuid4().hex;assert send(envelope(v,'invoke',endpoint=endpoint,requestId=request,expectedRevision=v['revision'],input=args))['ok'];deadline=time.monotonic()+180;result=None
  while time.monotonic()<deadline:
   reply=send(envelope(v,'update'));assert reply['ok'];result=next((x for x in reply.get('results',[]) if x['requestId']==request),None)
   if result:break
   time.sleep(.02)
  assert result and result['ok'],result;assert send(envelope(v,'dispose'))['ok'];return result['result']
 def nav():
  ready();page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name='기능 Blueprint',exact=True).click();ready()
  if page.locator('.nav-menu').count():page.locator('#nav').click()
 def panel():return page.locator('.window[data-key="blueprint"]')
 def local_window():return page.locator('.window[data-key="blueprint-code:'+graph+'/$locals"]')
 def read():return invoke('blueprint',{'action':'read','id':graph})
 def apply(el):el.locator('..').locator('[data-apply]').click();ready()
 nav();initial=read();assert initial['profile']=='sync-acyclic-v1' and not initial['locals'];panel().locator('[data-bp-locals-open]').click();expect(local_window()).to_contain_text('명시적 타입');local_window().locator('[data-bp-local-upgrade]').click();ready();assert read()['profile']=='sync-acyclic-locals-v1';assert (project/'node-value.graph.json').read_bytes()==before[project/'node-value.graph.json']
 def create(id,name,value):
  card=local_window().locator('[data-bp-local="$new"]');card.locator('[data-local-id]').fill(id);card.locator('[data-local-name]').fill(name);card.locator('[data-local-type]').select_option('long');card.locator('[data-local-initial]').fill(value);card.locator('[data-local-apply]').click();ready()
 create('counter','카운터','5');create('exact','정확한 큰 정수','9223372036854775807');assert next(x for x in read()['locals'] if x['id']=='exact')['initialJson']=='9223372036854775807'
 counter=local_window().locator('[data-bp-local="counter"]');counter.locator('[data-local-initial]').fill('7');invoke('saveDraft',{});page.evaluate('()=>globalThis.confectoryFlushPresentation()');restart();ready();expect(local_window().locator('.caption strong')).to_have_text('로컬 값 · 설정');nav();panel().locator('[data-bp-read]').click();ready();panel().locator('[data-bp-locals-open]').click();expect(counter.locator('[data-local-initial]')).to_have_value('7');assert next(x for x in read()['locals'] if x['id']=='counter')['initialJson']=='5';counter.locator('[data-local-apply]').click();ready();expect(page.locator('#status')).to_contain_text('기준 재검토');counter.locator('[data-local-rebase]').click();counter.locator('[data-local-apply]').click();ready();assert next(x for x in read()['locals'] if x['id']=='counter')['initialJson']=='7'
 counter.locator('[data-local-set]').click();ready();data=read();node=next(x for x in data['nodes'] if x['kind']=='set');assert node['sourceStatus']=='local-assignment' and not node.get('sourceId');counter.locator('[data-local-remove]').click();ready();assert any(x['id']=='counter' for x in read()['locals']);local_window().locator('[data-bp-local="exact"] [data-local-remove]').click();ready();assert len(read()['locals'])==1;page.screenshot(path='/tmp/confectory-v480-locals-form.png',full_page=True);local_window().locator('[data-close]').click();nav()
 panel().locator('[data-bp-select="'+node['id']+'"]').click();expect(panel().locator('[data-bp-task]')).to_have_count(0);panel().locator('[data-bp-fit]').click();panel().locator('[data-bp-input-pin="'+node['id']+'"]').click();picker=page.locator('.bp-pin-menu');picker.get_by_role('button',name='로컬 카운터 · long',exact=True).click();expect(panel().locator('[data-bp-argument="value"]')).to_have_value('{"local":"counter"}');assert next(x for x in read()['nodes'] if x['id']==node['id'])['arguments'][0]['valueJson']=='null';panel().locator('[data-bp-argument="value"]').fill('{"input":"n"}');apply(panel().locator('[data-bp-argument="value"]'))
 route=panel().locator('[data-bp-route="next"]');route.select_option('calculate');apply(route);panel().locator('[data-bp-select="condition"]').click();route=panel().locator('[data-bp-route="true"]');route.select_option(node['id']);apply(route);exit=panel().locator('[data-bp-exit="done"]');exit.fill('{"local":"counter"}');apply(exit);assert read()['diagnostics']['warnings']==[];assert all(p.read_bytes()==b for p,b in before.items())
 panel().locator('[data-bp-review]').click();ready();review=page.locator('.window[data-key="review"]');expect(review.locator('[data-review-advanced]')).to_be_visible(timeout=180000);review.locator('[data-review-advanced]').click();review.locator('[data-advanced-reviewed]').check();expect(page.locator('#confirm')).to_be_enabled();page.locator('#confirm').click();ready();published=json.loads((project/'node-value.graph.json').read_text());assert published['locals']==[{'id':'counter','name':'카운터','type':'long','initial':{'constant':7}}];assert any(x['kind']=='set' for x in published['nodes']);assert all(p.read_bytes()==b for p,b in before.items() if p.name!='node-value.graph.json')
 invoke('saveDraft',{});restart();ready();nav();panel().locator('[data-bp-read]').click();ready();assert read()['locals'][0]['initialJson']=='7' and read()['exits'][0]['valueJson']=='{"local":"counter"}';assert not any(x in ['runProject','startAI','prepareAI','permission','startBuild','nodeTask'] for x in calls);bounds=panel().evaluate('el=>{const box=s=>{const e=el.querySelector(s),r=e.getBoundingClientRect();return {left:r.left,right:r.right,width:r.width,scroll:e.scrollWidth,client:e.clientWidth}};return {window:box(".window-body"),editor:box(".bp-editor"),body:box(".bp-body"),plane:box(".bp-scroll"),outputs:box(".bp-output"),toolbar:box(".bp-toolbar")}}');print('Actual Blueprint output bounds',json.dumps(bounds),flush=True);assert bounds['outputs']['right']<=bounds['window']['right']+2,bounds;page.screenshot(path='/tmp/confectory-v480-locals-published.png',full_page=True)
 print('PASS actual v480 locals profile, exact initializer, typed picker, set order, cold input basis, delete guard and graph-only compiler Confirm',flush=True)
