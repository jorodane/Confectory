"""Named out contracts through real declaration forms, graph pins and compiler publication."""
import json,uuid,time
from playwright.sync_api import expect

def verify_multiout(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':1700,'height':1150});feature='Example.ButtonGame::OutFeature';calls=[];before={p:p.read_bytes() for p in project.iterdir() if p.is_file()}
 def record(request):
  if request.url.endswith('/api/request'):
   try:
    p=json.loads(request.post_data or '{}')
    if p.get('op')=='invoke':calls.append(p.get('endpoint'))
   except ValueError:pass
 page.on('request',record)
 def ready():
  expect(page.locator('#nav')).to_be_enabled(timeout=180000);expect(page.locator('#workspace-save-state')).not_to_contain_text('편집창 복원 중',timeout=180000)
 def state():
  v=mount();s=v['state'];assert send(envelope(v,'dispose'))['ok'];return s
 def invoke(endpoint,args):
  v=mount();request=uuid.uuid4().hex;assert send(envelope(v,'invoke',endpoint=endpoint,requestId=request,expectedRevision=v['revision'],input=args))['ok'];deadline=time.monotonic()+180;result=None
  while time.monotonic()<deadline:
   r=send(envelope(v,'update'));assert r['ok'];result=next((x for x in r.get('results',[]) if x['requestId']==request),None)
   if result:break
   time.sleep(.02)
  assert result and result['ok'],result;assert send(envelope(v,'dispose'))['ok'];return result['result']
 def nav(name):
  ready();page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name=name,exact=True).click();ready()
  if page.locator('.nav-menu').count():page.locator('#nav').click()
 def panel():return page.locator('.window[data-key="blueprint"]')
 def read():return invoke('blueprint',{'action':'read','id':graph})
 def apply(el):el.locator('..').locator('[data-apply]').click();ready()
 nav('기능');browser=page.locator('.window[data-key="browser"]');browser.locator('[data-new]').click();page.get_by_role('button',name='기능 생성',exact=True).click();page.locator('#new-declaration-name').fill('OutFeature');page.locator('#new-declaration').click();ready()
 declaration=page.locator('.window[data-key="declaration"]');expect(declaration.locator('[data-declaration-id]')).to_have_text(feature)
 if browser.count():nav('기능');browser.locator('[data-close]').click()
 declaration.locator('[data-add-argument]').click();declaration.locator('[data-arg-name]').fill('count');declaration.locator('[data-arg-type]').select_option('long');declaration.locator('[data-return]').select_option('long')
 declaration.locator('[data-add-output]').click();row=declaration.locator('[data-argument="1"]');expect(row.locator('[data-arg-mode]')).to_have_value('out');row.locator('[data-arg-name]').fill('amount');row.locator('[data-arg-type]').select_option('long')
 declaration.locator('[data-add-output]').click();row=declaration.locator('[data-argument="2"]');row.locator('[data-arg-name]').fill('text');row.locator('[data-arg-type]').select_option('string');declaration.locator('[data-signature-apply]').click();ready()
 assert '(long count, out long amount, out string text) -> long' in state()['draft']['text']
 declaration.locator('[data-feature-read]').click();ready();expect(declaration.locator('[data-feature-contract]')).to_contain_text('out long amount');declaration.locator('[data-feature-create]').click();ready();declaration.locator('[data-feature-open]').click();ready();graph='Example.ButtonGame::OutFeatureBlueprintBody/body:common';data=read()
 assert data['profile']=='sync-acyclic-implicit-out-v1' and len(data['reviewIds'])==5;assert data['outputs']==[{'name':'return','type':'long'},{'name':'amount','type':'long'},{'name':'text','type':'string'}];assert [a['name'] for a in data['nodes'][0]['arguments']]==['count']
 expect(panel().locator('[data-bp-feature-pin]')).to_have_count(1);expect(panel().locator('[data-bp-output-pin="body"]')).to_have_count(3);expect(panel().locator('[data-bp-output-name] option')).to_have_count(3);expect(panel().locator('[data-bp-node]')).to_have_count(4)
 paths=[project/s['path'] for s in data['sources'] if s['id']!='Example.ButtonGame::ProjectManifest'];assert all(not p.exists() for p in paths)
 panel().locator('[data-bp-code-open="body"]').click();code=page.locator('.window').filter(has=page.locator('[data-bp-code]'));expect(code).to_contain_text('out long amount');source='amount = count * 2; text = "ok"; return count + 9;';code.locator('[data-bp-code]').fill(source);invoke('saveDraft',{});page.evaluate('()=>globalThis.confectoryFlushPresentation()');restart();ready();nav('기능 Blueprint');panel().locator('[data-bp-code-open="body"]').click();expect(code.locator('[data-bp-code]')).to_have_value(source);assert read()['nodes'][0]['source']==''
 code.locator('[data-apply]').click();ready();expect(page.locator('#status')).to_contain_text('기준 재검토');code.locator('[data-rebase]').click();code.locator('[data-apply]').click();ready();code.locator('[data-close]').click();nav('기능 Blueprint');panel().locator('[data-bp-fit]').click()
 data=read();first=next(e['to'] for e in data['edges'] if e['from']=='body');panel().locator('[data-bp-select="body"]').click();route=panel().locator('[data-bp-route="next"]');route.select_option('');apply(route);expect(panel().locator('[data-bp-node-end="body/next"]')).to_contain_text('amount : long');expect(panel().locator('[data-bp-node-end="body/next"]')).to_contain_text('text : string');warning=read()['diagnostics']['warnings'][0];assert [o['name'] for o in warning['missingOutputs']]==['return','amount','text'] and set(warning['outputPaths'])=={'return','amount','text'}
 page.screenshot(path='/tmp/confectory-v480-multi-output-warnings.png',full_page=True);route=panel().locator('[data-bp-route="next"]');route.select_option(first);apply(route)
 data=read();amount=next(n for n in data['nodes'] if n['kind']=='export' and n['intent']=='Assign amount')['id'];panel().locator('[data-bp-select="'+amount+'"]').click();arg=panel().locator('[data-bp-argument="value"]');arg.fill('{"constant":6}');apply(arg)
 panel().locator('[data-bp-fit]').click();panel().locator('[data-bp-input-pin="'+amount+'"][data-pin-name="value"]').click();menu=page.locator('.bp-pin-menu');menu.get_by_role('button',name='body · amount · long',exact=True).click();expect(panel().locator('[data-bp-argument="value"]')).to_have_value('{"node":"body","output":"amount"}');assert next(n for n in read()['nodes'] if n['id']==amount)['arguments'][0]['valueJson']=='{"constant":6}'
 apply(panel().locator('[data-bp-argument="value"]'));assert read()['diagnostics']['warnings']==[]
 panel().locator('[data-bp-contract-read]').click();ready();expect(panel().locator('[data-bp-contract-preview]')).to_contain_text('out long amount');assert all(not p.exists() for p in paths);panel().locator('[data-bp-contract-ack]').check();panel().locator('[data-bp-contract-apply]').click();ready()
 panel().locator('[data-bp-review]').click();ready();review=page.locator('.window[data-key="review"]');expect(review.locator('[data-review-advanced]')).to_be_visible(timeout=180000);review.locator('[data-review-advanced]').click();review.locator('[data-advanced-reviewed]').check();expect(page.locator('#confirm')).to_be_enabled();page.locator('#confirm').click();ready();assert all(p.exists() for p in paths),state().get('status')
 assert '(long count, out long amount, out string text) -> long' in (project/'elements/OutFeature.celem').read_text();assert json.loads(next(p for p in paths if p.name.endswith('.node.json')).read_text())['source']==source;assert all(p.read_bytes()==b for p,b in before.items() if p.name!='project.cpack')
 # Create an independent node with out parameters through the real bounded node form.
 nav('기능 Blueprint');panel().locator('[data-bp-new-open]').click();creator=page.locator('.window[data-key="blueprint-code:'+graph+'/$create"]');creator.locator('[data-bp-new-id]').fill('aux');creator.locator('[data-bp-new-intent]').fill('Independent typed out results');creator.locator('[data-bp-new-args]').fill('long seed\nout long produced\nout bool flag');creator.locator('[data-bp-new-return]').select_option('void');creator.locator('[data-bp-new-submit]').click();ready();creator.locator('[data-close]').click();nav('기능 Blueprint');aux=next(n for n in read()['nodes'] if n['id']=='aux');assert len(aux['arguments'])==1 and aux['outputs']==[{'name':'produced','type':'long'},{'name':'flag','type':'bool'}]
 panel().locator('[data-bp-code-open="aux"]').click();aux_code=page.locator('.window[data-key="blueprint-code:'+graph+'/aux"]');expect(aux_code).to_contain_text('out long produced');aux_code.locator('[data-bp-code]').fill('produced = seed * 3; flag = true; return;');aux_code.locator('[data-apply]').click();ready();aux_code.locator('[data-close]').click();nav('기능 Blueprint');panel().locator('[data-bp-review]').click();ready();review=page.locator('.window[data-key="review"]');expect(review.locator('[data-review-advanced]')).to_be_visible(timeout=180000);review.locator('[data-review-advanced]').click();review.locator('[data-advanced-reviewed]').check();page.locator('#confirm').click();ready();assert any(n['id']=='aux' and n['sourceStatus']=='available' for n in read()['nodes'])
 # The module text editor round-trips modifiers, and displays outs on its output side.
 nav('모듈');browser=page.locator('.window[data-key="browser"]');browser.locator('[data-new]').click();page.get_by_role('button',name='모듈 생성',exact=True).click();page.locator('#new-declaration-name').fill('OutModule');page.locator('#new-declaration').click();ready();nav('모듈');browser.locator('[data-close]').click();declaration=page.locator('.window[data-key="declaration"]');declaration.locator('[data-module-new] summary').click();form=declaration.locator('[data-module-new-form]');form.locator('[data-module-function]').fill(feature);form.locator('[data-module-args]').fill('long, out long, out string');form.locator('[data-module-return]').select_option('long');form.locator('[data-module-apply]').click();ready();card=declaration.locator('section[data-module-function="'+feature+'"]');expect(card.locator('[data-module-args]')).to_have_value('long, out long, out string');expect(card.locator('.module-contract-flow > div').first).not_to_contain_text('out long');expect(card.locator('.module-contract-flow > div').nth(1)).to_contain_text('out long');expect(card.locator('.module-contract-flow > div').nth(1)).to_contain_text('out string')
 declaration.locator('[data-declaration-review]').click();ready();expect(page.locator('#review-creation')).to_be_visible(timeout=180000);page.locator('#review-creation').click();expect(page.locator('#confirm')).to_be_enabled();page.locator('#confirm').click();ready();assert 'require '+feature+' (long, out long, out string) -> long;' in (project/'elements/OutModule.celem').read_text()
 invoke('saveDraft',{});restart();ready();nav('기능 Blueprint');assert read()['outputs']==data['outputs'] and read()['nodes'][0]['source']==source;assert not state()['aiOwnerAvailable'];assert not any(x in ['runProject','startAI','prepareAI','permission','startBuild','nodeTask'] for x in calls)
 page.screenshot(path='/tmp/confectory-v480-multi-output-published.png',full_page=True)
 print('PASS actual v480 named out creation, typed pins, per-end missing outputs, no preview replay, cold source rebase and five-source compiler Confirm, new node out form and module modifier round-trip',flush=True)
