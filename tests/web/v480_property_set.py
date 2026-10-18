"""Actual structural Set authoring with an explicit typed value, cold restoration and grouped Confirm."""
import json,uuid,time
from playwright.sync_api import expect

def verify_property_set(page,project,mount,send,envelope,settle,restart):
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
 def form():return page.locator('.window[data-key="blueprint-code:'+graph+'/$property"]')
 def read():return invoke('blueprint',{'action':'read','id':graph})
 def apply(el):el.locator('..').locator('[data-apply]').click();ready()
 def select(id):panel().locator('[data-bp-select="'+id+'"]').click()
 def route(id,to):
  select(id);field=panel().locator('[data-bp-route="next"]');field.select_option(to);apply(field)
 nav();assert read()['profile']=='sync-acyclic-v1';panel().locator('[data-bp-property-upgrade]').click();expect(panel().locator('[data-bp-property-upgrade-preview]')).to_contain_text('도달할 때');panel().locator('[data-bp-property-upgrade-apply]').click();ready();assert read()['profile']=='sync-acyclic-property-v1';expect(panel().locator('[data-bp-nested-upgrade]')).to_have_count(0)
 panel().locator('[data-bp-property-set-upgrade]').click();expect(panel().locator('[data-bp-property-set-preview]')).to_contain_text('value');panel().locator('[data-bp-property-set-upgrade-apply]').click();ready();assert read()['profile']=='sync-acyclic-property-set-v1'
 # Ordinary typed call returns the real receiver; no implicit self/declaration lookup.
 panel().locator('[data-bp-call-open]').click();call=page.locator('.window[data-key="blueprint-code:'+graph+'/$call"]');call.locator('[data-call-search]').click();ready();call.locator('[data-call-feature]').select_option('Example.ButtonGame::CreateMonster');call.locator('[data-call-id]').fill('spawn');call.locator('[data-call-intent]').fill('호출자가 사용할 실제 객체');call.locator('[data-call-read]').click();ready();expect(call.locator('[data-call-contract]')).to_contain_text('object');call.locator('[data-call-ack]').check();call.locator('[data-call-submit]').click();ready();select('spawn');field=panel().locator('[data-bp-argument="value"]');field.fill('{"node":"calculate"}');apply(field)
 panel().locator('[data-bp-property-set-open]').click();form().locator('[data-property-node]').fill('set_health');form().locator('[data-property-search]').click();ready();expect(form().locator('datalist option[value="Example.ButtonGame::Monster"]')).to_have_count(1);form().locator('[data-property-owner]').fill('Example.ButtonGame::Monster');form().locator('[data-property-fields]').click();ready();form().locator('[data-property-field]').select_option('health');form().locator('[data-property-target-choice]').select_option('{"node":"spawn","output":"return"}');expect(form().locator('[data-property-target]')).to_have_value('{"node":"spawn","output":"return"}');form().locator('[data-property-value]').fill('{"node":"calculate"}');form().locator('[data-property-read]').click();ready();expect(form().locator('[data-property-contract]')).to_contain_text('health → Set long');form().locator('[data-property-ack]').check();assert not any(n['id']=='set_health' for n in read()['nodes']);assert all(p.read_bytes()==b for p,b in before.items());page.screenshot(path='/tmp/confectory-v480-property-set-preview.png',full_page=True)
 invoke('saveDraft',{});page.evaluate('()=>globalThis.confectoryFlushPresentation()');restart();ready();nav();panel().locator('[data-bp-read]').click();ready();expect(form().locator('[data-property-node]')).to_have_value('set_health');expect(form().locator('[data-property-value]')).to_have_value('{"node":"calculate"}');expect(form().locator('[data-property-target]')).to_have_value('{"node":"spawn","output":"return"}');expect(form().locator('[data-property-apply]')).to_have_count(0);assert not any(n['id']=='set_health' for n in read()['nodes'])
 form().locator('[data-property-read]').click();ready();form().locator('[data-property-ack]').check();form().locator('[data-property-apply]').click();ready();data=read();node=next(n for n in data['nodes'] if n['id']=='set_health');assert node['kind']=='property-set' and node['signature']['return']=='void' and not node.get('sourceId') and node['property']['writeTiming']=='execution-node';select('set_health');expect(panel().locator('[data-bp-task]')).to_have_count(0);expect(panel().locator('[data-bp-code-open="set_health"]')).to_have_count(0)
 # A separate typed Read observes the field after Set when the actual graph runs.
 panel().locator('[data-bp-property-open]').click();form().locator('[data-property-node]').fill('health');form().locator('[data-property-owner]').fill('Example.ButtonGame::Monster');form().locator('[data-property-fields]').click();ready();form().locator('[data-property-field]').select_option('health');form().locator('[data-property-target-choice]').select_option('{"node":"spawn","output":"return"}');form().locator('[data-property-read]').click();ready();form().locator('[data-property-ack]').check();form().locator('[data-property-apply]').click();ready()
 route('calculate','spawn');route('spawn','set_health');route('set_health','health');route('health','exit:done');field=panel().locator('[data-bp-exit="done"]');field.fill('{"node":"health"}');apply(field);assert read()['diagnostics']['state']=='source-ready';assert all(p.read_bytes()==b for p,b in before.items())
 # Rebind is explicit and preserves node identity, routes and selected actual receiver.
 panel().locator('[data-bp-property-rebind="set_health"]').click();expect(form().locator('[data-property-node]')).to_have_attribute('readonly','');expect(form().locator('[data-property-value]')).to_have_value('{"node":"calculate"}');expect(form().locator('[data-property-target]')).to_have_value('{"node":"spawn","output":"return"}');form().locator('[data-property-read]').click();ready();form().locator('[data-property-ack]').check();form().locator('[data-property-apply]').click();ready();assert read()['diagnostics']['state']=='source-ready'
 panel().locator('[data-bp-review]').click();ready();review=page.locator('.window[data-key="review"]');expect(review.locator('[data-review-advanced]')).to_be_visible(timeout=180000);review.locator('[data-review-advanced]').click();review.locator('[data-advanced-reviewed]').check();expect(page.locator('#confirm')).to_be_enabled();page.locator('#confirm').click();ready();published=json.loads((project/'node-value.graph.json').read_text());assert published['profile']=='sync-acyclic-property-set-v1';assert next(n for n in published['nodes'] if n['id']=='set_health')['arguments']['value']=={'node':'calculate'};assert next(n for n in published['nodes'] if n['id']=='health')['arguments']['target']=={'node':'spawn','output':'return'};assert all(p.read_bytes()==b for p,b in before.items() if p.name not in ['node-value.graph.json','NodeValueBody.celem'])
 invoke('saveDraft',{});restart();ready();nav();panel().locator('[data-bp-read]').click();ready();assert read()['diagnostics']['state']=='source-ready';select('health');panel().locator('[data-bp-fit]').click();assert not any(x in ['runProject','startAI','prepareAI','permission','startBuild','nodeTask'] for x in calls);page.screenshot(path='/tmp/confectory-v480-property-set-published.png',full_page=True)
 print('PASS actual v480 property Set explicit receiver/value, typed field, cold preview, Set/Read order, rebind and grouped compiler Confirm',flush=True)
