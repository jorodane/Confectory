"""Actual protected function view; edits remain ordinary body drafts with existing CAS and Confirm."""
import json,time,uuid
from playwright.sync_api import expect

def verify_code_regions(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':1700,'height':1150});graph='Example.ButtonGame::NodeValueBody/body:common';node=graph+'/node:calculate';before={p:p.read_bytes() for p in project.iterdir() if p.is_file()};calls=[]
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
 def source():return next(n for n in read()['nodes'] if n['id']=='calculate')['source']
 def area():return code().locator('[data-bp-code-full]')
 def position(start,end=None):area().evaluate('(el,p)=>{el.focus();el.setSelectionRange(p[0],p[1])}',[start,start if end is None else end])
 def replace_body(text):
  old=area().input_value();begin=old.index('\n{\n')+3;position(begin,len(old)-3);page.keyboard.insert_text(text)
 def apply():code().locator('[data-apply]').click();ready()
 nav();panel().locator('[data-bp-code-open="calculate"]').click();expect(code().locator('[data-bp-code]')).to_have_value('return value + 4;');code().locator('[data-bp-code-mode="protected"]').click();full=area();initial=full.input_value();assert initial.startswith('public static long Execute(long value)\n{\n');expect(code().locator('[data-bp-code]')).to_be_hidden();basis=read()['sources'];begin=initial.index('\n{\n')+3
 # Native insertion, cross-region delete and boundary keys cannot rewrite the fixed signature/braces.
 position(0,6);page.keyboard.insert_text('private');expect(full).to_have_value(initial);expect(code().locator('[data-bp-code-status]')).to_contain_text('보호');position(begin);page.keyboard.press('Backspace');expect(full).to_have_value(initial);position(len(initial)-3);page.keyboard.press('Delete');expect(full).to_have_value(initial)
 full.evaluate("el=>{el.value=el.value.replace('public static','private static');el.dispatchEvent(new Event('input',{bubbles:true}))}");expect(full).to_have_value(initial);assert read()['sources']==basis
 # Tab and protected-region undo/redo update only the pre-existing private body input.
 position(begin);page.keyboard.press('Tab');expect(code().locator('[data-bp-code]')).to_have_value('    return value + 4;');page.keyboard.press('Control+z');expect(full).to_have_value(initial);page.keyboard.press('Control+Shift+z');expect(code().locator('[data-bp-code]')).to_have_value('    return value + 4;');page.keyboard.press('Control+z');expect(full).to_have_value(initial)
 # Synthetic composition exercises one grouped undo; actual platform IME installation is outside this test.
 position(begin);full.evaluate("el=>{el.dispatchEvent(new CompositionEvent('compositionstart'));el.setRangeText('// 조합\\n',el.selectionStart,el.selectionEnd,'end');el.dispatchEvent(new InputEvent('input',{bubbles:true,inputType:'insertCompositionText',data:'조합'}));el.dispatchEvent(new CompositionEvent('compositionend',{data:'조합'}))}");assert '// 조합' in code().locator('[data-bp-code]').input_value();page.keyboard.press('Control+z');expect(full).to_have_value(initial)
 code().locator('[data-bp-code-helper]').click();assert full.evaluate('el=>el.selectionStart')==len(initial)-3
 helper='return Twice(value);\nstatic long Twice(long candidate)\n{\n    return candidate * 2;\n}'
 replace_body(helper);assert source()=='return value + 4;';code().locator('[data-reset]').click();expect(full).to_have_value(initial);replace_body(helper);full.press('Control+s');ready();assert source()==helper;assert all(p.read_bytes()==raw for p,raw in before.items());page.screenshot(path='/tmp/confectory-v480-code-protected.png',full_page=True)
 # A peer raw revision invalidates Apply; body and local helpers are retained until explicit rebase.
 retained=helper+'\n// cold retained helpers';replace_body(retained);invoke('saveDraft',{});page.evaluate('()=>globalThis.confectoryFlushPresentation()');restart();ready();nav();panel().locator('[data-bp-read]').click();ready();panel().locator('[data-bp-code-open="calculate"]').click();expect(area()).to_be_visible();expect(code().locator('[data-bp-code]')).to_have_value(retained);apply();expect(page.locator('#status')).to_contain_text('기준 재검토');assert source()==helper;code().locator('[data-rebase]').click();apply();assert source()==retained
 code().locator('[data-bp-code-mode="body"]').click();expect(code().locator('[data-bp-code]')).to_be_visible();expect(code().locator('[data-bp-code]')).to_have_value(retained);code().locator('[data-bp-code-mode="protected"]').click();assert retained in area().input_value()
 code().locator('[data-close]').click();panel().locator('[data-bp-review]').click();ready();review=page.locator('.window[data-key="review"]');expect(review.locator('[data-review-advanced]')).to_be_visible(timeout=180000);review.locator('[data-review-advanced]').click();review.locator('[data-advanced-reviewed]').check();page.locator('#confirm').click();ready();saved=json.loads((project/'calculate.node.json').read_text());assert saved['source']==retained and 'public static long Execute' not in saved['source'] and set(saved)=={'schema','node','definitionHash','source'};assert all(p.read_bytes()==raw for p,raw in before.items() if p.name!='calculate.node.json')
 invoke('saveDraft',{});restart();ready();nav();panel().locator('[data-bp-read]').click();ready();panel().locator('[data-bp-code-open="calculate"]').click();expect(area()).to_be_visible();assert 'static long Twice' in area().input_value() and source()==retained;assert not any(x in ['runProject','startAI','prepareAI','permission','startBuild','nodeTask'] for x in calls);page.screenshot(path='/tmp/confectory-v480-code-published.png',full_page=True)
 print('PASS actual v480 protected CSharp scaffold, body/local helpers, native editing and undo, synthetic composition, cold fence, unchanged source format and compiler Confirm',flush=True)
