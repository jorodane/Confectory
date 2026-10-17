"""Actual Home graph/node consumer; reference demo stamps never supply success."""
import json,uuid,time
from playwright.sync_api import expect

def verify_blueprint(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':1440,'height':900})
 graph='Example.ButtonGame::NodeValueBody/body:common';node=graph+'/node:calculate';before={p:p.read_bytes() for p in project.iterdir() if p.is_file()}
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=180000)
 def state():
  v=mount();s=v['state'];assert send(envelope(v,'dispose'))['ok'];return s
 def invoke(endpoint,args,ok=True):
  v=mount();request=uuid.uuid4().hex;assert send(envelope(v,'invoke',endpoint=endpoint,requestId=request,expectedRevision=v['revision'],input=args))['ok'];deadline=time.monotonic()+180
  while time.monotonic()<deadline:
   reply=send(envelope(v,'update'));assert reply['ok'],reply;result=next((r for r in reply.get('results',[]) if r['requestId']==request),None)
   if result:break
   time.sleep(.02)
  assert result and result['ok']==ok,result;assert send(envelope(v,'dispose'))['ok'];return result.get('result')
 def panel():return page.locator('.window[data-key="blueprint"]')
 def front(w):
  title=w.locator('.window-title');point=title.evaluate("el=>{const r=el.getBoundingClientRect();for(const fraction of [.75,.5,.25,.9]){const x=Math.floor(r.width*fraction),y=Math.floor(r.height*.6),hit=document.elementFromPoint(r.left+x,r.top+y);if(hit&&el.contains(hit)&&!hit.closest('button,[data-resize]'))return {x,y}}return null}");assert point,'No actually exposed title area';title.click(position=point)
 page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name='기능 Blueprint',exact=True).click();ready()
 expect(panel().locator('[data-bp-node]')).to_have_count(2);expect(panel().locator('.bp-start')).to_contain_text('n');expect(panel().locator('.bp-start')).to_contain_text('long');expect(panel().locator('[data-bp-exit="fallback"]')).to_have_value('{"constant":9223372036854775807}')
 assert not state()['aiOwnerAvailable'] and not state()['planningOwnerAvailable'];assert all(p.read_bytes()==b for p,b in before.items())
 expect(panel().locator('.bp-wires path')).to_have_count(1)
 # Presentation moves and zoom cannot change a source revision or graph hash.
 first=invoke('blueprint',{'action':'read','id':graph});handle=panel().locator('[data-bp-drag="calculate"]');box=handle.bounding_box();page.mouse.move(box['x']+40,box['y']+12);page.mouse.down();page.mouse.move(box['x']+85,box['y']+38,steps=5);page.mouse.up();panel().locator('[data-bp-zoom]').fill('90');page.evaluate('()=>globalThis.confectoryFlushPresentation()');again=invoke('blueprint',{'action':'read','id':graph});assert first['sources']==again['sources']
 panel().locator('[data-bp-select="calculate"]').click();intent=panel().locator('[data-bp-intent]');intent.fill('Human revised intent, retained until explicitly applied');panel().locator('[data-bp-task]').click();expect(page.locator('#status')).to_contain_text('미적용 입력');assert page.locator('.window[data-key="node-tasks"]').count()==0
 # Standalone node inspection sees the same unsent node intent, even without a chief.
 page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name='Blueprint 노드 Task',exact=True).click();ready();tasks=page.locator('.window[data-key="node-tasks"]');tasks.locator('[data-node-task-id="'+node+'"]').click();tasks.locator('[data-node-task-inspect]').click();ready();expect(page.locator('#status')).to_contain_text('미적용 입력');tasks.locator('[data-close]').click();front(panel());expect(intent).to_have_value('Human revised intent, retained until explicitly applied')
 # The opaque basis also fences another source, even when graph itself is unchanged.
 invoke('select',{'id':node});unit=state()['draft'];record=json.loads(unit['text']);record['source']='return value + 6;';invoke('editDraft',{'id':node,'text':json.dumps(record),'revision':unit['revision']})
 intent.locator('..').locator('[data-apply]').click();ready();expect(page.locator('#status')).to_contain_text('입력은 유지');expect(intent).to_have_value('Human revised intent, retained until explicitly applied')
 after=invoke('blueprint',{'action':'read','id':graph});assert next(n for n in after['nodes'] if n['id']=='calculate')['intent']=='Add four to the input';assert next(n for n in after['nodes'] if n['id']=='calculate')['source']=='return value + 6;'
 panel().locator('[data-bp-read]').click();ready();expect(panel().locator('[data-bp-intent]')).to_have_value('Human revised intent, retained until explicitly applied');intent=panel().locator('[data-bp-intent]');intent.locator('..').locator('[data-rebase]').click();intent.locator('..').locator('[data-apply]').click();ready();expect(panel().locator('[data-bp-node="calculate"]')).to_contain_text('계약 변경');assert (project/'node-value.graph.json').read_bytes()==before[project/'node-value.graph.json']
 # Exact argument JSON and a targeted route change preserve an untouched long constant.
 arg=panel().locator('[data-bp-argument="value"]');arg.fill('{"constant":9223372036854775806}');arg.locator('..').locator('[data-apply]').click();ready();expect(panel().locator('[data-bp-argument="value"]')).to_have_value('{"constant":9223372036854775806}');expect(panel().locator('[data-bp-exit="fallback"]')).to_have_value('{"constant":9223372036854775807}')
 route=panel().locator('[data-bp-route="next"]');route.select_option('exit:fallback');route.locator('..').locator('[data-apply]').click();ready();result=invoke('blueprint',{'action':'read','id':graph});assert next(e for e in result['edges'] if e['from']=='calculate')['to']=='exit:fallback';assert result['exits'][1]['valueJson']=='{"constant":9223372036854775807}'
 # Independent C# body, no JSON wrapper input or generated source write.
 panel().locator('[data-bp-code-open="calculate"]').click();code=page.locator('.window[data-key^="blueprint-code:"]');expect(code.locator('[data-bp-code]')).to_have_value('return value + 6;');code.locator('[data-bp-code]').fill('return value + 5;');code.locator('[data-bp-code]').locator('..').locator('[data-apply]').click();ready();expect(code.locator('p').first).to_contain_text('available');assert json.loads(state()['draft']['text'])['source']=='return value + 5;', 'shared primary source projection must refresh after node body apply';assert (project/'calculate.node.json').read_bytes()==before[project/'calculate.node.json']
 # Cold restore retains unsent code, never a usable server basis. The user rereads and rebinds.
 code.locator('[data-bp-code]').fill('return value + 7; // retained cold input');page.evaluate('()=>globalThis.confectoryFlushPresentation()');invoke('saveDraft',{});restart();ready();expect(panel()).to_be_visible(timeout=30000);expect(panel().locator('[data-bp-node]')).to_have_count(0);expect(code.locator('[data-bp-open]')).to_be_visible()
 code.locator('[data-bp-open]').click();ready();front(panel());panel().locator('[data-bp-read]').click();ready();panel().locator('[data-bp-code-open="calculate"]').click();expect(code.locator('[data-bp-code]')).to_have_value('return value + 7; // retained cold input');code.locator('[data-apply]').click();ready();expect(page.locator('#status')).to_contain_text('기준 재검토');expect(code.locator('[data-bp-code]')).to_have_value('return value + 7; // retained cold input')
 code.locator('[data-rebase]').click();code.locator('[data-apply]').click();ready();assert next(n for n in invoke('blueprint',{'action':'read','id':graph})['nodes'] if n['id']=='calculate')['source']=='return value + 7; // retained cold input'
 code.locator('[data-close]').click();front(panel());panel().locator('[data-bp-select="condition"]').click();expect(panel().locator('[data-bp-route]')).to_have_count(2);panel().locator('[data-bp-select="calculate"]').click();panel().locator('[data-bp-task]').click();ready();task_panel=page.locator('.window[data-key="node-tasks"]');expect(task_panel.locator('.node-task-list .selected')).to_contain_text(node);task_panel.locator('[data-close]').click();front(panel());expect(panel().locator('[data-bp-tab]')).to_have_count(1);expect(panel().locator('[data-bp-tab]')).to_contain_text('NodeValue');prior_fit=invoke('blueprint',{'action':'read','id':graph});panel().locator('[data-bp-fit]').click();assert invoke('blueprint',{'action':'read','id':graph})['sources']==prior_fit['sources'];viewport=panel().locator('.bp-scroll').bounding_box()
 for card in panel().locator('[data-bp-node]').all():
  box=card.bounding_box();assert box and box['x']>=viewport['x'] and box['y']>=viewport['y'] and box['x']+box['width']<=viewport['x']+viewport['width']+1 and box['y']+box['height']<=viewport['y']+viewport['height']+1,(box,viewport)
 page.screenshot(path='/tmp/confectory-v480-blueprint.png',full_page=True)
 toolbar=panel().locator('.bp-toolbar').bounding_box();tabs=panel().locator('.bp-doc-tabs').bounding_box();body=panel().locator('.bp-body').bounding_box();assert tabs['y']<toolbar['y']<body['y'];assert tabs['y']>=panel().bounding_box()['y']
 for button in panel().locator('[data-bp-read],[data-bp-review]').all():
  box=button.bounding_box();dock=page.locator('#dock').bounding_box();assert box and (box['x']+box['width']<=dock['x'] or box['y']+box['height']<=dock['y']),(box,dock)
 # A no-op node operation preserves an unrelated primary schema view and source versions.
 invoke('select',{'id':'Example.ButtonGame::Score'});invoke('schema',{'id':'Example.ButtonGame::Score'});snapshot=invoke('blueprint',{'action':'read','id':graph});body=next(n for n in snapshot['nodes'] if n['id']=='calculate')['source'];invoke('blueprint',{'action':'source','id':graph,'basis':snapshot['basis'],'node':'calculate','text':body});assert state()['schema']['id']=='Example.ButtonGame::Score';assert invoke('blueprint',{'action':'read','id':graph})['sources']==snapshot['sources']
 # UI review obtains a fresh real compiler result; Confirm is a distinct user action.
 panel().locator('[data-bp-review]').click();review=page.locator('.window[data-key="review"]');expect(review.locator('[data-review-advanced]')).to_be_visible(timeout=180000);ready();review.locator('[data-review-advanced]').click();review.locator('[data-advanced-reviewed]').check();expect(page.locator('#confirm')).to_be_enabled();page.locator('#confirm').click();ready()
 assert json.loads((project/'calculate.node.json').read_text())['source']=='return value + 7; // retained cold input'
 saved=json.loads((project/'node-value.graph.json').read_text());assert saved['nodes'][1]['arguments']['value']['constant']==9223372036854775806 and saved['exits']['fallback']['constant']==9223372036854775807 and saved['nodes'][1]['intent']=='Human revised intent, retained until explicitly applied'
 assert all(p.read_bytes()==b for p,b in before.items() if p.name not in ['calculate.node.json','node-value.graph.json'])
 assert not state()['aiOwnerAvailable'] and not state()['planningOwnerAvailable']
 print('PASS actual v480 Blueprint: owned contract rails/output, private layout, exact JSON, atomic observed-source refusal, retained intent and cold code, explicit source basis rebind, compiler Review/Confirm and no AI activation',flush=True)
