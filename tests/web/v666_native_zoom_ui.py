"""Real native viewport module/DOM, controlled presentation only; no engine write claims."""
from pathlib import Path
import http.server,threading,tempfile,sys,json
from playwright.sync_api import sync_playwright,expect

repo=Path(sys.argv[1]).resolve();root=Path(tempfile.mkdtemp(prefix='confectory-native-zoom-'))
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(repo),**kw)
    def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();errors=[]
try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1200,'height':900});page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto('http://127.0.0.1:'+str(server.server_port)+'/')
        page.evaluate('''async()=>{
         const el=document.createElement('section');el.innerHTML='<button data-bp-percent></button><input data-bp-zoom type="range" min="3.125" max="500" step="any"><button data-bp-fit>전체 보기</button><div data-bp-overview style="width:300px;height:80px"><svg></svg></div><output data-bp-overview-status></output><div style="display:flex;width:900px"><div class="bp-scroll" style="width:700px;height:400px;overflow:hidden;position:relative"><div class="bp-canvas" style="position:absolute;transform-origin:0 0"><svg class="bp-wires"></svg><article class="bp-node" data-bp-node="node" style="position:absolute;width:200px;height:100px"><header data-bp-drag="node">동작</header></article></div></div><aside class="bp-output"><button data-bp-output-toggle></button><span data-bp-output-resize tabindex="0"></span></aside></div>';document.body.replaceChildren(el);
         const w={el,body:el,meta:{blueprintZoom:500,blueprintCamera:{x:-50000000,y:0},blueprintPositions:{node:{x:10000000,y:0}}}},data={id:'Owned::Body/body:common',profile:'sync-acyclic-v1',nodes:[{id:'node'}],edges:[],sources:[{id:'owned',hash:'unchanged',revision:1}],diagnostics:{}};
         const {mountBlueprintViewport}=await import('/examples/editor-home/ui/blueprint-viewport.js');let current=true,persists=0,view;
         const open=()=>view=mountBlueprintViewport({w,data,$:(s,r)=>r.querySelector(s),$$:(s,r)=>[...r.querySelectorAll(s)],persist:()=>persists++,isCurrent:()=>current,hasWire:()=>false,cancelWire:()=>{}});
         globalThis.fixture={w,data,original:JSON.stringify(data),open,close:()=>view.dispose(),stale:()=>current=false,count:()=>persists};open();
        }''')
        expect(page.locator('[data-bp-zoom]')).to_have_value('500');assert page.evaluate('fixture.w.meta.blueprintCamera.x')==-50000000
        page.locator('[data-bp-percent]').click();menu=page.get_by_role('dialog',name='노드 화면 배율');menu.locator('[data-zoom-preset="400"]').click();expect(page.locator('[data-bp-zoom]')).to_have_value('400');menu.locator('[data-zoom-preset="500"]').click();expect(page.locator('[data-bp-zoom]')).to_have_value('500');menu.locator('[data-zoom-value]').press('Escape')
        before=page.evaluate('structuredClone(fixture.w.meta)');area=page.locator('.bp-scroll').bounding_box();point={'x':area['x']+area['width']*.6,'y':area['y']+area['height']*.4};local={'x':area['width']*.6,'y':area['height']*.4};world={k:(local[k]-before['blueprintCamera'][k])/(before['blueprintZoom']/100) for k in local};page.mouse.move(**point);page.mouse.wheel(0,100);expect(page.locator('[data-bp-zoom]')).to_have_value('475');after=page.evaluate('structuredClone(fixture.w.meta)');assert all(abs((local[k]-after['blueprintCamera'][k])/(after['blueprintZoom']/100)-world[k])<.01 for k in world)
        page.locator('[data-bp-zoom]').fill('500');saved=page.evaluate('structuredClone(fixture.w.meta)');page.evaluate('fixture.close();fixture.open()');expect(page.locator('[data-bp-zoom]')).to_have_value('500');assert page.evaluate('fixture.w.meta.blueprintCamera')==saved['blueprintCamera'];assert page.evaluate('JSON.stringify(fixture.data)===fixture.original')
        page.locator('[data-bp-percent]').click();menu.locator('[data-zoom-value]').fill('200');menu.locator('[data-zoom-value]').press('Escape');expect(page.locator('[data-bp-zoom]')).to_have_value('500');page.screenshot(path=str(root/'native-zoom.png'))
        page.evaluate('''async()=>{const {bindCanvasZoomMenu}=await import('/examples/editor-home/ui/canvas-zoom.js');const button=document.createElement('button');button.id='zoom-owner';button.textContent='500%';document.body.append(button);const events=new AbortController();let scale=5,calls=0;const control=bindCanvasZoomMenu({button,signal:events.signal,isCurrent:()=>true,getScale:()=>scale,setScale:value=>{scale=value;calls++;},fit:()=>{}});globalThis.zoomFixture={control,events,value:()=>scale,calls:()=>calls};}''')
        page.locator('#zoom-owner').click();page.evaluate("zoomFixture.retired=document.querySelector('.workspace-zoom-menu [data-zoom-slider]');zoomFixture.control.close(false)")
        page.locator('#zoom-owner').click();page.evaluate("zoomFixture.retired.value='200';zoomFixture.retired.dispatchEvent(new Event('input',{bubbles:true}))")
        assert page.evaluate('zoomFixture.value()')==5 and page.evaluate('zoomFixture.calls()')==0
        page.evaluate('zoomFixture.events.abort()');expect(page.locator('.workspace-zoom-menu')).to_have_count(0)
        assert not errors,errors;browser.close()
finally:server.shutdown();server.server_close()
(root/'evidence.json').write_text(json.dumps({'errors':errors,'actualEngine':False,'actualViewportModule':True,'actualWindows':False,'actualMobile':False,'sourceUnchanged':True},indent=2)+'\n')
print('PASS native 500% range/presets, wheel world anchor, large camera cold remount, Escape and source-byte identity; evidence',root)
