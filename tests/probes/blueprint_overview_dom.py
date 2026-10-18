"""Actual Chromium component stress probe; does not claim an ordinary EditorHome run."""
from pathlib import Path
import base64,hashlib,json,sys
from playwright.sync_api import sync_playwright
repo=Path(__file__).resolve().parents[2];raw=(repo/'examples/editor-home/ui/blueprint-viewport.js').read_bytes();url='data:text/javascript;base64,'+base64.b64encode(raw).decode()
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-gpu']);page=browser.new_page(viewport={'width':1200,'height':800})
 page.set_content('''<style>#host{width:1000px}.bp-body{display:flex}.bp-scroll{position:relative;width:700px;height:400px;overflow:hidden}.bp-canvas{position:relative;transform-origin:0 0}.bp-node{position:absolute;width:250px;height:180px}.bp-overview{width:700px;height:64px;touch-action:none}.bp-overview svg{width:100%;height:100%;pointer-events:none}</style><section id="host"><input data-bp-zoom><button data-bp-percent></button><button data-bp-fit></button><div data-bp-overview class="bp-overview" role="group" tabindex="0"><svg></svg></div><output data-bp-overview-status></output><div class="bp-body"><div class="bp-scroll"><div class="bp-canvas"><svg class="bp-wires"></svg></div></div><aside class="bp-output"><button data-bp-output-toggle></button><div data-bp-output-resize></div></aside></div></section>''')
 page.evaluate('''async url=>{const module=await import(url),host=document.querySelector('#host'),$=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)],nodes=[],saved=Object.create(null),edges=[];
 for(let i=0;i<256;i++){const id=i===0?'__proto__':'n'+i;nodes.push({id,control:'next'});saved[id]={x:i===254?1e7:i*300,y:(i%8)*280};if(i===255)continue;const el=document.createElement('article');el.className='bp-node';el.dataset.bpNode=id;const header=document.createElement('header');header.dataset.bpDrag=id;header.textContent=id;el.append(header);$('.bp-canvas').append(el);}
 saved.n1={x:Infinity,y:NaN};saved.n2={x:'999',y:-1e20};saved.forgotten={x:1e7,y:1e7};edges.push({from:'__proto__',port:'bad\"]port',to:'n2'},{from:'n1',port:'missing',to:'n2'},{from:'n254',port:'next',to:'missing'},{from:'missing',port:'next',to:'n1'});
 const data={id:'stress',nodes,edges,diagnostics:{branchReturns:[{from:'n254',owner:'missing',port:'next'}]}},w={body:host,el:host,meta:{blueprintPositions:saved,blueprintCamera:{x:Infinity,y:NaN}}};let current=true,persisted=0;const before=JSON.stringify(data),view=module.mountBlueprintViewport({w,data,$,$$,persist(){persisted++},isCurrent:()=>current,hasWire:()=>false,cancelWire(){}});globalThis.probe={w,data,view,before,get persisted(){return persisted},retire(){current=false}};}''',url)
 page.wait_for_function("document.querySelectorAll('[data-bp-overview-node]').length===255")
 baseline=page.evaluate('''()=>({glyphs:document.querySelectorAll('[data-bp-overview-node]').length,positions:Object.keys(probe.w.meta.blueprintPositions).length,prototypeOwn:Object.hasOwn(probe.w.meta.blueprintPositions,'__proto__'),finite:[...document.querySelector('svg:not(.bp-wires)').querySelectorAll('*')].every(el=>['x','y','width','height','x1','x2','y1','y2'].every(k=>!el.hasAttribute(k)||Number.isFinite(Number(el.getAttribute(k))))),noWire:document.querySelectorAll('.bp-wires path').length===0})''');assert baseline==dict(glyphs=255,positions=256,prototypeOwn=True,finite=True,noWire=True),baseline
 page.evaluate("document.querySelector('.bp-scroll').scrollTop=120");page.wait_for_function("document.querySelector('.bp-scroll').scrollTop===0")
 ov=page.locator('[data-bp-overview]');ov.focus();ov.press('End');end=page.evaluate('probe.w.meta.blueprintCamera');assert end['x'] < -9e6 and all(abs(v)<4e7 for v in end.values()),end
 ov.press('Home');home=page.evaluate('probe.w.meta.blueprintCamera');assert home['x']>0 and home['y']>0,home
 ov.press('ArrowRight');right=page.evaluate('probe.w.meta.blueprintCamera');assert right['x']<home['x'];ov.press('Shift+ArrowRight');shift=page.evaluate('probe.w.meta.blueprintCamera');assert abs(shift['x']-right['x'])>abs(right['x']-home['x']);ov.press('PageDown');assert page.evaluate('probe.w.meta.blueprintCamera.y')<home['y']
 page.locator('[data-bp-zoom]').fill('300');ov.press('End');large_camera=page.evaluate('probe.w.meta.blueprintCamera');assert large_camera['x'] < -2.9e7 and abs(large_camera['x']) < 4e7;page.locator('[data-bp-zoom]').fill('100');ov.press('Home')
 # Real pointer capture: Escape, pointercancel and lostpointercapture all restore.
 def drag_cancel(kind):
  before=page.evaluate('JSON.stringify(probe.w.meta.blueprintCamera)');b=ov.bounding_box();page.mouse.move(b['x']+30,b['y']+20);page.mouse.down();page.mouse.move(b['x']+200,b['y']+40)
  if kind=='Escape':page.keyboard.press('Escape')
  elif kind=='pointercancel':ov.evaluate("el=>el.dispatchEvent(new PointerEvent('pointercancel',{pointerId:1,bubbles:true}))")
  else:ov.evaluate('el=>el.releasePointerCapture(1)');page.wait_for_timeout(60)
  page.mouse.up();assert page.evaluate('JSON.stringify(probe.w.meta.blueprintCamera)')==before,kind
 for kind in ['Escape','pointercancel','lostpointercapture']:drag_cancel(kind)
 # A missing current DOM node disappears without touching the model or old basis.
 page.locator('[data-bp-node="n254"]').evaluate('el=>el.remove()');page.wait_for_function("document.querySelectorAll('[data-bp-overview-node]').length===254");page.evaluate("probe.view.focusNode('missing');probe.view.focusNode('n254')")
 assert page.evaluate('JSON.stringify(probe.data)===probe.before')
 # An empty visible scene has no map or navigation side effects.
 page.evaluate("document.querySelectorAll('.bp-node').forEach(el=>el.remove())");page.wait_for_function("document.querySelector('[data-bp-overview]').getAttribute('aria-disabled')==='true'");assert ov.locator('[data-bp-overview-node]').count()==0
 before=page.evaluate('JSON.stringify(probe.w.meta.blueprintCamera)');ov.press('End');assert page.evaluate('JSON.stringify(probe.w.meta.blueprintCamera)')==before
 page.evaluate('probe.retire();probe.view.dispose()');before=page.evaluate('JSON.stringify(probe.w.meta)');writes=page.evaluate('probe.persisted');ov.press('Home');b=ov.bounding_box();page.mouse.click(b['x']+20,b['y']+20);assert page.evaluate('JSON.stringify(probe.w.meta)')==before and page.evaluate('probe.persisted')==writes
 result=dict(kind='actual Chromium mounted production viewport component',sourceSha256=hashlib.sha256(raw).hexdigest(),metadataNodes=256,initialMountedGlyphs=255,missingDomNodesIgnored=True,oldSavedIdsIgnored=True,prototypeIdSafe=True,invalidPositionsFinite=True,worldExtent=10000000,endCamera=end,homeCamera=home,maxZoomCamera=large_camera,cancel=['Escape','pointercancel','lostpointercapture'],modelUnchanged=True,emptySceneDisabled=True,retiredHandlersIgnored=True)
 Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n');print('PASS overview actual DOM '+json.dumps(result),flush=True);browser.close()
