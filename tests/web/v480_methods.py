"""Actual node-owned static methods and reviewed typed parameter edits."""
import json,time,uuid
from playwright.sync_api import expect

def verify_methods(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':1700,'height':1150});graph='Example.ButtonGame::NodeValueBody/body:common';before={p:p.read_bytes() for p in project.iterdir() if p.is_file()};calls=[]
 def record(request):
  if request.url.endswith('/api/request'):
   try:
    data=json.loads(request.post_data or '{}')
    if data.get('op')=='invoke':calls.append(data.get('endpoint'))
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
 def read():return invoke('blueprint',{'action':'read','id':graph})
 def node():return next(n for n in read()['nodes'] if n['id']=='calculate')
 def body():return code().locator('[data-bp-code]')
 def helpers():return code().locator('[data-bp-helpers]')
 def area():return code().locator('[data-bp-code-full]')
 def apply():code().locator('[data-apply]').click();ready()
 nav();panel().locator('[data-bp-code-open="calculate"]').click();code().locator('[data-bp-methods-upgrade]').click();ready();assert read()['profile']=='sync-acyclic-methods-v1';assert node()['sourceStatus']=='available'
 source='return Double(value);';helper='private static long Double(long candidate) => candidate*2;';body().fill(source);helpers().fill(helper);apply();assert node()['helpers']==helper and node()['source']==source;assert all(p.read_bytes()==raw for p,raw in before.items())
 code().locator('[data-bp-code-mode="protected"]').click();initial=area().input_value();assert initial.startswith('public static class Node\n{\npublic static long Execute(long value)\n{\n');assert '\n}\n\n'+helper in initial
 def position(at,end=None):area().evaluate('(el,p)=>{el.focus();el.setSelectionRange(p[0],p[1])}',[at,at if end is None else end])
 position(initial.index('Execute'),initial.index('Execute')+7);page.keyboard.insert_text('Injected');expect(area()).to_have_value(initial)
 position(initial.index('\n}\n\n'),initial.index(helper)+7);page.keyboard.insert_text('escape');expect(area()).to_have_value(initial)
 end=initial.rfind('\n}');position(end);page.keyboard.insert_text('\n');assert helpers().input_value()==helper+'\n';page.keyboard.press('Control+z');expect(area()).to_have_value(initial);page.keyboard.press('Control+Shift+z');assert helpers().input_value()==helper+'\n';page.keyboard.press('Control+z');expect(area()).to_have_value(initial)
 retained=helper+'\n// retained static helper';code().locator('[data-bp-code-mode="body"]').click();helpers().fill(retained);invoke('saveDraft',{});page.evaluate('()=>globalThis.confectoryFlushPresentation()');restart();ready();nav();panel().locator('[data-bp-read]').click();ready();panel().locator('[data-bp-code-open="calculate"]').click();expect(helpers()).to_have_value(retained);apply();expect(page.locator('#status')).to_contain_text('기준');assert node()['helpers']==helper;code().locator('[data-rebase]').click();apply();assert node()['helpers']==retained
 contract=code().locator('.bp-parameters');contract.locator('summary').click();row=contract.locator('[data-bp-parameter-row="0"]');row.locator('[data-bp-parameter-name]').fill('renamed');contract.locator('[data-bp-parameters-preview]').click();expect(page.locator('#status')).to_contain_text('대응');contract.locator('[data-bp-remap="0"]').select_option('renamed');contract.locator('[data-bp-parameter-add]').click();row=contract.locator('[data-bp-parameter-row="1"]');row.locator('[data-bp-parameter-name]').fill('audit');row.locator('[data-bp-parameter-type]').select_option('long');row.locator('[data-bp-parameter-mode]').select_option('out');contract.locator('[data-bp-parameters-preview]').click();contract.locator('[data-bp-parameters-ack]').check();invoke('saveDraft',{});page.evaluate('()=>globalThis.confectoryFlushPresentation()');restart();ready();nav();panel().locator('[data-bp-read]').click();ready();panel().locator('[data-bp-code-open="calculate"]').click();contract=code().locator('.bp-parameters');contract.locator('summary').click();expect(contract.locator('[data-bp-parameter-row="0"] [data-bp-parameter-name]')).to_have_value('renamed');contract.locator('[data-bp-parameters-preview]').click();contract.locator('[data-bp-parameters-ack]').check();contract.locator('[data-bp-parameters-apply]').click();ready();expect(page.locator('#status')).to_contain_text('기준 재검토');assert node()['signature']['args'][0]['name']=='value';contract.locator('[data-bp-parameters-rebase]').click();page.screenshot(path='/tmp/confectory-v480-methods-parameters.png',full_page=True);contract.locator('[data-bp-parameters-apply]').click();ready();assert node()['signature']['args']==[{'type':'long','name':'renamed'},{'type':'long','name':'audit','mode':'out'}];assert node()['sourceStatus']=='stale' and node()['source']==source and node()['helpers']==retained
 body().fill('audit=Double(renamed);return audit;');apply();assert node()['sourceStatus']=='available';code().locator('[data-bp-code-mode="protected"]').click();assert 'Execute(long renamed, out long audit)' in area().input_value();assert retained in area().input_value();page.screenshot(path='/tmp/confectory-v480-methods-code.png',full_page=True)
 code().locator('[data-close]').click();panel().locator('[data-bp-review]').click();ready();review=page.locator('.window[data-key="review"]');expect(review.locator('[data-review-advanced]')).to_be_visible(timeout=180000);review.locator('[data-review-advanced]').click();review.locator('[data-advanced-reviewed]').check();page.locator('#confirm').click();ready();saved=json.loads((project/'calculate.node.json').read_text());assert saved['source']=='audit=Double(renamed);return audit;' and saved['helpers']==retained;assert json.loads((project/'node-value.graph.json').read_text())['profile']=='sync-acyclic-methods-v1';assert all(p.read_bytes()==raw for p,raw in before.items() if p.name not in ['calculate.node.json','node-value.graph.json'])
 invoke('saveDraft',{});restart();ready();nav();panel().locator('[data-bp-read]').click();ready();panel().locator('[data-bp-code-open="calculate"]').click();code().locator('[data-bp-code-mode="protected"]').click();expect(area()).to_be_visible();assert 'Execute(long renamed, out long audit)' in area().input_value() and node()['helpers']==retained;assert not any(x in ['runProject','startAI','prepareAI','permission','startBuild','nodeTask'] for x in calls)
 print('PASS actual v480 static methods protected regions/history, typed explicit remap, body stale/reapply, cold basis fence and compiler Confirm',flush=True)
