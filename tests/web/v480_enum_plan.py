"""Private enum authoring and exact owned-source declaration previews; no runtime migration."""
import json,time,uuid
from playwright.sync_api import expect

def verify_enum_plan(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':1700,'height':1150});graph='Example.ButtonGame::NodeValueBody/body:common';before={p:p.read_bytes() for p in project.iterdir() if p.is_file()};actions=[]
 def record(request):
  if request.url.endswith('/api/request'):
   try:
    data=json.loads(request.post_data or '{}')
    if data.get('op')=='invoke':actions.append((data.get('endpoint'),data.get('input',{})))
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
 def code():return page.locator('.window[data-key="blueprint-code:'+graph+'/calculate"]')
 def plan():return code().locator('.bp-enum-plan')
 def read():return invoke('blueprint',{'action':'read','id':graph})
 def preview():plan().locator('[data-bp-enum-preview]').click();ready()
 def row(i):return plan().locator('[data-bp-enum-row="'+str(i)+'"]')
 nav();panel().locator('[data-bp-code-open="calculate"]').click();plan().locator('summary').click();expect(row(0).locator('[data-bp-enum-remove]')).to_be_disabled();plan().locator('[data-bp-enum-add]').click();stable=row(1).locator('[data-bp-enum-id]').inner_text();row(1).locator('[data-bp-enum-name]').fill('Succeeded');row(1).locator('[data-bp-enum-value]').fill('17');initial=read()['sources'];preview();expect(plan().locator('[data-bp-enum-source]')).to_contain_text('Succeeded = 17, // port: '+stable);assert read()['sources']==initial
 row(1).locator('[data-bp-enum-name]').fill('Completed');row(1).locator('[data-bp-enum-value]').fill('-2');row(1).locator('[data-bp-enum-up]').click();assert row(0).locator('[data-bp-enum-id]').inner_text()==stable;assert row(1).locator('[data-bp-enum-id]').inner_text()=='next';expect(row(1).locator('[data-bp-enum-remove]')).to_be_disabled();preview();expect(plan().locator('[data-bp-enum-source]')).to_contain_text('Completed = -2, // port: '+stable)
 row(0).locator('[data-bp-enum-value]').fill('0');preview();expect(plan().locator('[data-bp-enum-status]')).to_contain_text('값이 중복');row(0).locator('[data-bp-enum-value]').fill('2147483648');preview();expect(plan().locator('[data-bp-enum-status]')).to_contain_text('int32');row(0).locator('[data-bp-enum-value]').fill('-2');row(0).locator('[data-bp-enum-name]').fill('Next');preview();expect(plan().locator('[data-bp-enum-status]')).to_contain_text('이름이 중복');row(0).locator('[data-bp-enum-name]').fill('Completed');preview()
 assert all(p.read_bytes()==raw for p,raw in before.items());invoke('saveDraft',{});page.evaluate('()=>globalThis.confectoryFlushPresentation()');restart();ready();nav();panel().locator('[data-bp-read]').click();ready();panel().locator('[data-bp-code-open="calculate"]').click();plan().locator('summary').click();assert row(0).locator('[data-bp-enum-id]').inner_text()==stable;expect(row(0).locator('[data-bp-enum-name]')).to_have_value('Completed');expect(row(0).locator('[data-bp-enum-value]')).to_have_value('-2');preview();expect(plan().locator('[data-bp-enum-source]')).to_contain_text('Completed = -2')
 peer=read();invoke('blueprint',{'action':'intent','id':graph,'basis':peer['basis'],'node':'calculate','text':'Peer contract observation changed'});preview();expect(plan().locator('[data-bp-enum-status]')).to_contain_text('현재 원본·계약');code().locator('[data-close]').click();panel().locator('[data-bp-read]').click();ready();panel().locator('[data-bp-code-open="calculate"]').click();plan().locator('summary').click();preview();expect(plan().locator('[data-bp-enum-status]')).to_contain_text('연결이 오래');expect(row(0).locator('[data-bp-enum-name]')).to_have_value('Completed');plan().locator('[data-bp-enum-rebind]').click();preview();expect(plan().locator('[data-bp-enum-source]')).to_contain_text('Completed = -2, // port: '+stable);expect(plan().locator('[data-bp-enum-status]')).to_contain_text('분기 후 메인 계속');page.screenshot(path='/tmp/confectory-v480-enum-plan.png',full_page=True)
 current=next(n for n in read()['nodes'] if n['id']=='calculate');assert current['control']=='next' and current['signature']['return']=='long' and current['source']=='return value + 4;';assert all(p.read_bytes()==raw for p,raw in before.items());assert not any(endpoint in ['runProject','startAI','prepareAI','permission','startBuild','nodeTask'] for endpoint,_ in actions);assert not any(endpoint=='blueprint' and isinstance(args,dict) and args.get('action') in ['source','parameters','route','upgradeProfile'] for endpoint,args in actions)
 print('PASS actual v480 private enum stable IDs/int32/source binding/reorder/cold/rebind; legacy source and execution policy unchanged',flush=True)
