"""Actual explicit profile/whole-body conversion, cold restore and compiler Confirm."""
import json,time,uuid
from playwright.sync_api import expect

def verify_external_ref(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':1600,'height':1100});graph='Example.ButtonGame::NodeValueBody/body:common';legacy='Example.ButtonGame::LiftValueBody';calls=[]
 before={p:p.read_bytes() for p in project.iterdir() if p.is_file()}
 def record(request):
  if request.url.endswith('/api/request'):
   try:
    payload=json.loads(request.post_data or '{}')
    if payload.get('op')=='invoke':calls.append((payload.get('endpoint'),payload.get('input')))
   except ValueError:pass
 page.on('request',record)
 def ready():
  expect(page.locator('#nav')).to_be_enabled(timeout=180000)
  expect(page.locator('#workspace-save-state')).not_to_contain_text('편집창 복원 중',timeout=180000)
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
 def front(w):w.locator('.window-title').click(position={'x':100,'y':12})
 def apply(el):el.locator('..').locator('[data-apply]').click();ready()
 def confirm():
  panel().locator('[data-bp-review]').click();review=page.locator('.window[data-key="review"]');expect(review.locator('[data-review-advanced]')).to_be_visible(timeout=180000);ready();review.locator('[data-review-advanced]').click();review.locator('[data-advanced-reviewed]').check();expect(page.locator('#confirm')).to_be_enabled();page.locator('#confirm').click();ready();front(panel())
 page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name='기능 Blueprint',exact=True).click();ready();expect(panel().locator('[data-bp-node]')).to_have_count(2)
 first=invoke('blueprint',{'action':'read','id':graph});assert first['profile']=='sync-acyclic-v1';assert all(p.read_bytes()==b for p,b in before.items())
 panel().locator('[data-bp-external-ref-upgrade]').click();expect(panel().locator('[data-bp-external-ref-preview]')).to_contain_text('중복 저장소');assert invoke('blueprint',{'action':'read','id':graph})['profile']=='sync-acyclic-v1'
 panel().locator('[data-bp-external-ref-apply]').click();ready();panel().locator('[data-bp-select="condition"]').click();route=panel().locator('[data-bp-route="false"]');route.select_option('');apply(route)
 expect(panel().locator('[data-bp-node-end="condition/false"]')).to_contain_text('return : long');assert len(invoke('blueprint',{'action':'read','id':graph})['diagnostics']['warnings'])==1
 panel().locator('[data-bp-output-create]').click();ready();created=invoke('blueprint',{'action':'read','id':graph});output=next(n for n in created['nodes'] if n['kind']=='export');assert not output.get('sourceId');expect(panel().locator('[data-bp-task]')).to_have_count(0);expect(panel().locator('[data-bp-reference="'+output['id']+'"]')).to_have_count(0)
 arg=panel().locator('[data-bp-argument="value"]');arg.fill('{"node":"calculate"}');apply(arg);panel().locator('[data-bp-select="calculate"]').click();route=panel().locator('[data-bp-route="next"]');route.select_option(output['id']);apply(route)
 inspected=invoke('blueprint',{'action':'read','id':graph});assert len(inspected['diagnostics']['warnings'])==1;assert next(e for e in inspected['diagnostics']['terminations'] if e['from']==output['id'])['definitelyAssigned'];expect(panel().locator('[data-bp-termination="condition/false"]')).to_contain_text('미할당 반환값')
 page.screenshot(path='/tmp/confectory-v480-external-ref-ends.png',full_page=True);confirm();assert json.loads((project/'node-value.graph.json').read_text())['profile']=='sync-acyclic-ref-v1'
 # Conversion preview keeps source byte exact and creates no draft membership.
 front(panel());panel().locator('[data-bp-convert-open]').click();converter=page.locator('.window[data-key="blueprint-code:$conversion/$convert"]');converter.locator('[data-bp-convert-id]').fill(legacy);converter.locator('[data-bp-convert-target]').fill('common');converter.locator('[data-bp-convert-read]').click();ready();expect(converter.locator('[data-bp-convert-source]')).to_have_text((project/'lift.csbody').read_text());assert (project/'LiftValueBody.celem').read_bytes()==before[project/'LiftValueBody.celem']
 converter.locator('[data-bp-convert-ack]').check();converter.locator('[data-bp-convert-apply]').click();ready();expect(panel().locator('[data-bp-node]')).to_have_count(2);data=invoke('blueprint',{'action':'read','id':legacy+'/body:common'});assert data['profile']=='sync-acyclic-ref-v1' and data['nodes'][0]['forwardCallerStorage'];assert [a.get('mode') for a in data['nodes'][0]['signature']['args']]==['ref','ref','out'];assert len(data['reviewIds'])==3 and len([n for n in data['nodes'] if n['kind']=='code'])==1;assert data['nodes'][0]['source']==(project/'lift.csbody').read_bytes().decode();assert (project/'lift.csbody').read_bytes()==before[project/'lift.csbody']
 # Opening and applying an unchanged C# textarea retains literal CRLF rather than normalizing source.
 panel().locator('[data-bp-code-open="body"]').click();code=page.locator('.window[data-key="blueprint-code:'+legacy+'/body:common/body"]');expect(code).to_contain_text('ref long a, ref long b, out long copied');expect(code).to_contain_text('호출자 저장소에 직접 전달');code.locator('[data-apply]').click();ready();assert invoke('blueprint',{'action':'read','id':legacy+'/body:common'})['nodes'][0]['source']==data['nodes'][0]['source'];code.locator('[data-close]').click();front(panel())
 # No conversion is replayed during a real host restart; only the draft group is restored.
 panel().locator('[data-bp-save]').click();ready();page.evaluate('()=>globalThis.confectoryFlushPresentation()');restart();ready();front(panel());panel().locator('[data-bp-read]').click();ready();restored=invoke('blueprint',{'action':'read','id':legacy+'/body:common'});assert len(restored['reviewIds'])==3;assert restored['nodes'][0]['source']==data['nodes'][0]['source'];assert (project/'LiftValueBody.celem').read_bytes()==before[project/'LiftValueBody.celem']
 page.screenshot(path='/tmp/confectory-v480-external-ref-conversion.png',full_page=True);confirm();assert 'blueprint common' in (project/'LiftValueBody.celem').read_text();assert (project/'lift.csbody').read_bytes()==before[project/'lift.csbody'];assert all(p.read_bytes()==b for p,b in before.items() if p.name not in ['node-value.graph.json','LiftValueBody.celem'])
 assert not state()['aiOwnerAvailable'] and not state()['planningOwnerAvailable'];assert not any(endpoint in ['runProject','startAI','prepareAI','permission','startBuild','nodeTask'] for endpoint,args in calls)
 print('PASS actual external ref graph and whole body conversion: per-port warnings, explicit profile, structural output, byte exact body, three-source compiler Confirm and true cold restore',flush=True)
