"""Actual shared enum transition, scoped case routing, cold restoration and compiler Confirm."""
import json,time,uuid
from playwright.sync_api import expect

def verify_switch(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':1700,'height':1150});graph='Example.ButtonGame::NodeValueBody/body:common';before={p:p.read_bytes() for p in project.iterdir() if p.is_file()};actions=[]
 def record(request):
  if request.url.endswith('/api/request'):
   try:
    data=json.loads(request.post_data or '{}')
    if data.get('op')=='invoke':actions.append(data.get('endpoint'))
   except ValueError:pass
 page.on('request',record)
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=180000);expect(page.locator('#workspace-save-state')).not_to_contain_text('편집창 복원 중',timeout=180000)
 def invoke(endpoint,args):
  v=mount();request=uuid.uuid4().hex;assert send(envelope(v,'invoke',endpoint=endpoint,requestId=request,expectedRevision=v['revision'],input=args))['ok'];deadline=time.monotonic()+180;result=None
  while time.monotonic()<deadline:
   reply=send(envelope(v,'update'));assert reply['ok'];result=next((x for x in reply.get('results',[]) if x['requestId']==request),None)
   if result:break
   time.sleep(.02)
  assert result and result['ok'],result;assert send(envelope(v,'dispose'))['ok'];return result['result']
 def read():return invoke('blueprint',{'action':'read','id':graph})
 def node(name):return next(n for n in read()['nodes'] if n['id']==name)
 def nav():
  ready();page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name='기능 Blueprint',exact=True).click();ready()
  if page.locator('.nav-menu').count():page.locator('#nav').click()
 def panel():return page.locator('.window[data-key="blueprint"]')
 def code(name):return page.locator('.window[data-key="blueprint-code:'+graph+'/'+name+'"]')
 def plan(name):return code(name).locator('.bp-enum-plan')
 def open_code(name):panel().locator('[data-bp-code-open="'+name+'"]').click();return code(name)
 def close_code(name):code(name).locator('[data-close]').click()
 def source(name,text):
  open_code(name).locator('[data-bp-code-mode="body"]').click();code(name).locator('[data-bp-code]').fill(text);code(name).locator('[data-apply]').first.click();ready();assert node(name)['source']==text;close_code(name)
 def create(name,owner=''):
  panel().locator('[data-bp-new-open]').click();w=page.locator('.window[data-key="blueprint-code:'+graph+'/$create"]');w.locator('[data-bp-new-id]').fill(name);w.locator('[data-bp-new-intent]').fill(name+' explicit scope');w.locator('[data-bp-new-args]').fill('long value' if not owner else '');w.locator('[data-bp-new-return]').select_option('void');w.locator('[data-bp-new-owner]').select_option(owner);w.locator('[data-bp-new-submit]').click();ready();assert node(name).get('branchOwner')== (owner or None);w.locator('[data-close]').click()
 def route(name,port,to):
  panel().locator('[data-bp-select="'+name+'"]').click();select=panel().locator('[data-bp-route="'+port+'"]');select.select_option(to);select.locator('..').locator('[data-apply]').click();ready();assert any(e['from']==name and e['port']==port and e['to']==to for e in read()['edges']) if to else not any(e['from']==name and e['port']==port for e in read()['edges'])
 nav();open_code('calculate');plan('calculate').locator('summary').click();plan('calculate').locator('[data-bp-switch-upgrade]').click();ready();assert read()['profile']=='sync-acyclic-switch-v1';expect(plan('calculate').locator('[data-bp-enum-apply]')).to_be_disabled();assert node('calculate')['source']=='return value + 4;' and node('calculate')['signature']['return']=='long';close_code('calculate')
 create('selector');open_code('selector');plan('selector').locator('summary').click();
 for i in range(1,4):
  plan('selector').locator('[data-bp-enum-add]').click();plan('selector').locator('[data-bp-enum-row="'+str(i)+'"] [data-bp-enum-value]').fill(str(i))
 plan('selector').locator('[data-bp-enum-preview]').click();ready();expect(plan('selector').locator('[data-bp-enum-source]')).to_contain_text('Next = 0');plan('selector').locator('[data-bp-enum-apply]').click();ready();assert node('selector')['control']=='switch' and node('selector')['sourceStatus']=='stale';code('selector').locator('[data-bp-code-mode="protected"]').click();assert 'public enum Result : int' in code('selector').locator('[data-bp-code-full]').input_value();assert 'static Result Execute(long value)' in code('selector').locator('[data-bp-code-full]').input_value();close_code('selector')
 source('selector','return value > 0 ? Result.Next : (Result)99;');panel().locator('[data-bp-select="selector"]').click();arg=panel().locator('[data-bp-argument="value"]');arg.fill('{"input":"n"}');arg.locator('..').locator('[data-apply]').click();ready();create('case_work','selector');source('case_work','int count=1;_ = count;')
 route('selector','next','condition');route('selector','case:next','case_work');route('case_work','next','return:selector');panel().locator('[data-bp-select="selector"]').click();case_options=panel().locator('[data-bp-route="case:next"] option').evaluate_all('(els)=>els.map(e=>e.value)');assert 'condition' not in case_options and 'case_work' in case_options and 'return:selector' in case_options
 start=panel().locator('[data-bp-entry]');start.select_option('selector');start.locator('..').locator('[data-apply]').click();ready();current=read();assert not current['diagnostics']['warnings'];route('selector','next','');ended=read();assert all(e.get('from')=='selector' and e['port']=='next' for e in ended['diagnostics']['terminations']);expect(panel().locator('[data-bp-termination="selector/next"]')).to_contain_text('return');expect(panel().locator('[data-bp-node-end="case_work/next"]')).to_have_count(0);route('selector','next','condition');current=read();assert not current['diagnostics']['warnings'];assert not any(e.get('from')=='case_work' for e in current['diagnostics']['terminations']);panel().locator('[data-bp-select="case_work"]').click();expect(panel().locator('.bp-inspector')).to_contain_text('메인으로 복귀');expect(panel().locator('[data-bp-return-wire="case_work/next"]')).to_have_count(1);assert panel().locator('[data-bp-node="selector"]').evaluate('(node)=>{const n=node.getBoundingClientRect();return [...node.querySelectorAll(".bp-exec-ports button")].every(p=>p.getBoundingClientRect().right<=n.right+1)}');panel().locator('[data-bp-fit]').click();page.screenshot(path='/tmp/confectory-v480-switch-routes.png',full_page=True)
 from v480_pin_gestures import verify_pin_gestures
 verify_pin_gestures(page,panel,read)
 invoke('saveDraft',{});page.evaluate('()=>globalThis.confectoryFlushPresentation()');restart();ready();nav();panel().locator('[data-bp-read]').click();ready();assert node('selector')['executionEnum']['members'][0]=={'id':'next','name':'Next','value':0};assert node('case_work')['branchOwner']=='selector';open_code('selector');plan('selector').locator('summary').click();plan('selector').locator('[data-bp-enum-rebind]').click();plan('selector').locator('[data-bp-enum-preview]').click();ready();expect(plan('selector').locator('[data-bp-enum-source]')).to_contain_text('Next = 0');plan('selector').locator('[data-bp-enum-source]').scroll_into_view_if_needed();page.screenshot(path='/tmp/confectory-v480-switch-enum.png',full_page=True);close_code('selector')
 panel().locator('[data-bp-review]').click();ready();review=page.locator('.window[data-key="review"]');expect(review.locator('[data-review-advanced]')).to_be_visible(timeout=180000);review.locator('[data-review-advanced]').click();review.locator('[data-advanced-reviewed]').check();page.locator('#confirm').click();ready();saved=json.loads((project/'node-value.graph.json').read_text());assert saved['profile']=='sync-acyclic-switch-v1';assert next(n for n in saved['nodes'] if n['id']=='selector')['control']=='switch';assert all(p.read_bytes()==raw for p,raw in before.items() if p.name!='node-value.graph.json');assert not any(a in ['runProject','startAI','prepareAI','permission','startBuild','nodeTask'] for a in actions)
 print('PASS actual v480 switch enum explicit transition/Result source/scoped case/main return/cold/compiler Confirm',flush=True)
