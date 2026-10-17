"""Real ref node authoring: same storage bindings, cold fencing and explicit compiler publication."""
import json,uuid,time
from playwright.sync_api import expect

def verify_ref_nodes(page,project,mount,send,envelope,settle,restart):
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
 def nav(name='기능 Blueprint'):
  ready();page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name=name,exact=True).click();ready()
  if page.locator('.nav-menu').count():page.locator('#nav').click()
 def panel():return page.locator('.window[data-key="blueprint"]')
 def read():return invoke('blueprint',{'action':'read','id':graph})
 def apply(el):el.locator('..').locator('[data-apply]').click();ready()
 nav();assert read()['profile']=='sync-acyclic-v1';panel().locator('[data-bp-ref-upgrade]').click();expect(panel().locator('[data-bp-ref-preview]')).to_contain_text('같은 슬롯');panel().locator('[data-bp-ref-apply]').click();ready();assert read()['profile']=='sync-acyclic-ref-nodes-v1';assert (project/'node-value.graph.json').read_bytes()==before[project/'node-value.graph.json']
 panel().locator('[data-bp-locals-open]').click();local_window=page.locator('.window[data-key="blueprint-code:'+graph+'/$locals"]');card=local_window.locator('[data-bp-local="$new"]');card.locator('[data-local-id]').fill('shared');card.locator('[data-local-name]').fill('공유 저장소');card.locator('[data-local-type]').select_option('long');card.locator('[data-local-initial]').fill('5');card.locator('[data-local-apply]').click();ready();local_window.locator('[data-close]').click();nav()
 panel().locator('[data-bp-new-open]').click();creator=page.locator('.window[data-key="blueprint-code:'+graph+'/$create"]');creator.locator('[data-bp-new-id]').fill('alias');creator.locator('[data-bp-new-intent]').fill('실제 ref 별칭 공유');creator.locator('[data-bp-new-args]').fill('ref long a\nref long b\nout long audit');creator.locator('[data-bp-new-return]').select_option('long');creator.locator('[data-bp-new-submit]').click();ready();creator.locator('[data-close]').click();nav();node=next(n for n in read()['nodes'] if n['id']=='alias');assert [p.get('mode') for p in node['signature']['args']]==['ref','ref','out'] and len(node['arguments'])==2
 panel().locator('[data-bp-code-open="alias"]').click();code=page.locator('.window[data-key="blueprint-code:'+graph+'/alias"]');expect(code).to_contain_text('ref long a, ref long b, out long audit');source='a = 10; b += a; audit = a + b; return a + b + audit;';code.locator('[data-bp-code]').fill(source);code.locator('[data-apply]').click();ready();code.locator('[data-close]').click();nav();panel().locator('[data-bp-select="alias"]').click();panel().locator('[data-bp-fit]').click()
 for name in ['a','b']:
  panel().locator('[data-bp-input-pin="alias"][data-pin-name="'+name+'"]').click();picker=page.locator('.bp-pin-menu');expect(picker).to_have_attribute('aria-label',name+' ref 저장 슬롯');picker.get_by_role('button',name='로컬 공유 저장소 · long',exact=True).click();apply(panel().locator('[data-bp-argument="'+name+'"]'))
 route=panel().locator('[data-bp-route="next"]');route.select_option('calculate');apply(route);panel().locator('[data-bp-select="condition"]').click();route=panel().locator('[data-bp-route="true"]');route.select_option('alias');apply(route);exit=panel().locator('[data-bp-exit="done"]');exit.fill('{"node":"alias","output":"return"}');apply(exit);panel().locator('[data-bp-select="alias"]').click();pending=panel().locator('[data-bp-argument="b"]');pending.fill('{"constant":5}');invoke('saveDraft',{});page.evaluate('()=>globalThis.confectoryFlushPresentation()');restart();ready();nav();panel().locator('[data-bp-read]').click();ready();panel().locator('[data-bp-select="alias"]').click();expect(panel().locator('[data-bp-argument="b"]')).to_have_value('{"constant":5}');apply(panel().locator('[data-bp-argument="b"]'));expect(page.locator('#status')).to_contain_text('기준 재검토');panel().locator('[data-bp-argument="b"]').locator('..').locator('[data-rebase]').click();apply(panel().locator('[data-bp-argument="b"]'));assert read()['diagnostics']['diagnostics'][0]['code']=='GRAPH_REF_STORAGE';assert (project/'node-value.graph.json').read_bytes()==before[project/'node-value.graph.json']
 panel().locator('[data-bp-fit]').click();panel().locator('[data-bp-input-pin="alias"][data-pin-name="b"]').click();page.locator('.bp-pin-menu').get_by_role('button',name='로컬 공유 저장소 · long',exact=True).click();apply(panel().locator('[data-bp-argument="b"]'));data=read();assert data['diagnostics']['state']=='source-ready';assert next(n for n in data['nodes'] if n['id']=='alias')['arguments'][0]['valueJson']==next(n for n in data['nodes'] if n['id']=='alias')['arguments'][1]['valueJson'];page.screenshot(path='/tmp/confectory-v480-ref-node-bindings.png',full_page=True)
 panel().locator('[data-bp-review]').click();ready();review=page.locator('.window[data-key="review"]');expect(review.locator('[data-review-advanced]')).to_be_visible(timeout=180000);review.locator('[data-review-advanced]').click();review.locator('[data-advanced-reviewed]').check();page.locator('#confirm').click();ready();saved=json.loads((project/'node-value.graph.json').read_text());assert saved['profile']=='sync-acyclic-ref-nodes-v1';alias=next(n for n in saved['nodes'] if n['id']=='alias');assert alias['arguments']['a']==alias['arguments']['b']=={'local':'shared'};assert json.loads((project/alias['implementation']).read_text())['source']==source;assert all(p.read_bytes()==b for p,b in before.items() if p.name!='node-value.graph.json')
 # Ordinary ref contracts remain editable; their unsupported graph conversion is stated before creation.
 nav('기능');browser=page.locator('.window[data-key="browser"]');browser.locator('[data-new]').click();page.get_by_role('button',name='기능 생성',exact=True).click();page.locator('#new-declaration-name').fill('RefContract');page.locator('#new-declaration').click();ready();nav('기능');browser.locator('[data-close]').click();decl=page.locator('.window[data-key="declaration"]')
 for name in ['left','right']:
  decl.locator('[data-add-argument]').click();row=decl.locator('[data-argument]').last;row.locator('[data-arg-name]').fill(name);row.locator('[data-arg-type]').select_option('long');row.locator('[data-arg-mode]').select_option('ref')
 decl.locator('[data-return]').select_option('long');decl.locator('[data-signature-apply]').click();ready();expect(decl.locator('[data-feature-ref-unsupported]')).to_contain_text('아직 지원하지 않습니다');expect(decl.locator('[data-feature-read]')).to_be_disabled();decl.locator('[data-declaration-review]').click();ready();page.locator('#review-creation').click();expect(page.locator('#confirm')).to_be_enabled();page.locator('#confirm').click();ready();assert '(ref long left, ref long right) -> long' in (project/'elements/RefContract.celem').read_text();assert not any(p.name.startswith('RefContractBlueprintBody') for p in (project/'elements').iterdir())
 invoke('saveDraft',{});restart();ready();nav();panel().locator('[data-bp-read]').click();ready();assert next(n for n in read()['nodes'] if n['id']=='alias')['source']==source;assert not any(x in ['runProject','startAI','prepareAI','permission','startBuild','nodeTask'] for x in calls);page.screenshot(path='/tmp/confectory-v480-ref-node-published.png',full_page=True)
 print('PASS actual v480 ref node profile, same storage inputs, constant rejection, cold basis, C# contract form and explicit compiler Confirm',flush=True)
