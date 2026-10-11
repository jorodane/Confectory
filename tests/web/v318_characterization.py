"""Frozen ZIP vs refactored workbench: reference-only behavior, never engine acceptance."""
import contextlib,datetime,functools,http.server,json,pathlib,sys,threading
from playwright.sync_api import sync_playwright,expect
from PIL import Image,ImageChops
repo=pathlib.Path(sys.argv[1]).resolve();original=pathlib.Path(sys.argv[2]).resolve();out=pathlib.Path(sys.argv[3]).resolve();out.mkdir(parents=True,exist_ok=True)
assert (repo/'workbench/v318/style.css').read_bytes()==(original/'style.css').read_bytes(), 'frozen stylesheet changed'
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
@contextlib.contextmanager
def server(root):
 service=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(root)));thread=threading.Thread(target=service.serve_forever,daemon=True);thread.start()
 try:yield 'http://127.0.0.1:'+str(service.server_port)
 finally:service.shutdown();service.server_close();thread.join()
def snapshot(page):
 return page.evaluate('''()=>({text:document.querySelector('#app').innerText,windows:[...document.querySelectorAll('.window')].map(e=>({title:e.querySelector('.caption')?.textContent,rect:{x:e.getBoundingClientRect().x,y:e.getBoundingClientRect().y,width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height},folded:e.classList.contains('folded'),left:e.style.left,top:e.style.top,width:e.style.width,height:e.style.height,selected:e.classList.contains('multi-selected')})),items:[...document.querySelectorAll('.workspace-decoration')].map(e=>({kind:[...e.classList].find(c=>['workspace-note','workspace-group','workspace-portal'].includes(c)),name:e.querySelector('.workspace-item-name')?.textContent,text:e.querySelector('textarea')?.value,left:e.style.left,top:e.style.top,width:e.style.width,height:e.style.height,selected:e.classList.contains('multi-selected')})),tabs:[...document.querySelectorAll('#workspace-tabs button')].map(e=>({label:e.textContent,selected:e.getAttribute('aria-selected')}))})''')
def run(browser,url,label):
 context=browser.new_context(viewport={'width':1440,'height':900});page=context.new_page();page.clock.set_fixed_time(datetime.datetime(2026,10,11,tzinfo=datetime.timezone.utc));page.set_default_timeout(12000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.route('https://fonts.googleapis.com/**',lambda route:route.abort());page.route('https://fonts.gstatic.com/**',lambda route:route.abort())
 def settle_visuals():page.add_style_tag(content='*,*::before,*::after{animation:none!important;transition:none!important;caret-color:transparent!important}')
 page.goto(url,wait_until='domcontentloaded');settle_visuals();page.locator('#later').click();shots=[];states=[]
 def capture(name):
  page.wait_for_timeout(350);page.evaluate('async()=>{await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))}');file=out/(label+'-'+name+'.png');page.screenshot(path=str(file),full_page=True);shots.append(file);states.append(snapshot(page))
 capture('home');page.locator('[data-favorite="demo"]').click();expect(page.locator('[data-favorite="demo"]')).to_have_attribute('aria-pressed','true')
 page.locator('#home-project-search').fill('not-found');expect(page.locator('[data-enter="demo"]')).to_have_count(0);page.locator('#home-project-search').fill('')
 page.locator('#home-tab-packs').click();capture('packs');page.locator('#home-tab-projects').click();page.locator('[data-enter="demo"]').click();capture('workspace')
 page.locator('#nav').click();expect(page.locator('.window[data-key="browser"]')).to_be_visible();capture('browser')
 def add(name,x,y):
  page.mouse.click(x,y,button='right');page.get_by_role('button',name=name,exact=True).click()
 add('메모 만들기',1280,230);note=page.locator('.workspace-note');note.locator('textarea').fill('보존하는 메모 <literal>');expect(note.locator('textarea')).to_have_value('보존하는 메모 <literal>')
 add('그룹 만들기',1260,540);group=page.locator('.workspace-group');add('하위 Workspace 만들기',1280,130);portal=page.locator('.workspace-portal');capture('nodes')
 # One common gesture must select and move both a note and a group.
 def handlepoint(locator):
  return locator.locator('.workspace-item-handle').evaluate('(e)=>{const r=e.getBoundingClientRect();for(let x=8;x<r.width-8;x++){const px=r.x+x,py=r.y+r.height/2;if(document.elementFromPoint(px,py)===e)return [px,py]}throw Error("No handle background")}')
 x,y=handlepoint(note);page.mouse.click(x,y);page.keyboard.down('Control');gx,gy=handlepoint(group);page.mouse.click(gx,gy);page.keyboard.up('Control');expect(page.locator('.workspace-decoration.multi-selected')).to_have_count(2)
 before=snapshot(page);page.mouse.move(x,y);page.mouse.down();page.mouse.move(x+24,y+22,steps=5);page.evaluate('()=>{const handle=[...document.querySelectorAll("*")].find(e=>e.hasPointerCapture?.(1));if(!handle)throw Error("No pointer capture");handle.dispatchEvent(new PointerEvent("pointercancel",{pointerId:1,bubbles:true}))}');page.mouse.up();assert snapshot(page)==before,'pointer cancellation changed geometry/selection'
 page.mouse.move(x,y);page.mouse.down();page.mouse.move(x+24,y+22,steps=5);page.mouse.up();after=snapshot(page);assert after!=before;assert [i['selected'] for i in after['items']].count(True)==2;capture('multi-drag')
 # Child navigation and destructive confirmation cancel preserve parent notes/windows.
 portal.dblclick(position={'x':8,'y':12});expect(page.locator('#workspace-tabs button[aria-selected="true"]')).to_have_text('Workspace 1');expect(page.locator('.workspace-note')).to_have_count(0)
 page.locator('.workspace-parent-node').dblclick();expect(note.locator('textarea')).to_have_value('보존하는 메모 <literal>');expect(page.locator('.window[data-key="browser"]')).to_be_visible()
 portal.locator('[data-remove]').click();page.locator('.modal [data-cancel]').click();expect(portal).to_have_count(1);capture('returned')
 # Folding/reopening and a fresh page preserve the original reference's saved presentation.
 window=page.locator('.window[data-key="browser"]');window.locator('[data-fold]').click();expect(window).to_have_class(__import__('re').compile('.*folded.*'));window.locator('[data-fold]').click()
 window.locator('[data-close]').click();expect(window).to_have_count(0);page.locator('#nav').click();expect(window).to_be_visible()
 page.reload(wait_until='domcontentloaded');settle_visuals();page.locator('#later').click();page.locator('[data-enter="demo"]').click();expect(note.locator('textarea')).to_have_value('보존하는 메모 <literal>');capture('reload')
 assert not errors,errors;context.close();return shots,states
with server(original) as source,server(repo) as workbench,sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-gpu','--disable-lcd-text','--disable-font-subpixel-positioning','--font-render-hinting=none']);baseline,old=run(browser,source+'/','original');changed,new=run(browser,workbench+'/workbench/v318/','refactor');assert old==new,'behavior snapshots diverged'
 comparisons=[]
 for a,b in zip(baseline,changed):
  with Image.open(a) as first,Image.open(b) as second:
   assert first.size==second.size;diff=ImageChops.difference(first.convert('RGB'),second.convert('RGB'));box=diff.getbbox();hist=diff.histogram();nonzero_channels=sum(hist)-sum(hist[0::256]);maximum=max(i%256 for i,v in enumerate(hist) if v);comparisons.append({'original':a.name,'refactor':b.name,'differentPixelsBoundingBox':box,'nonzeroChannels':nonzero_channels,'maximumChannelDelta':maximum});assert maximum<=8 and nonzero_channels<=768,(a.name,box,nonzero_channels,maximum)
 browser.close();(out/'characterization.json').write_text(json.dumps({'scope':'prototype reference behavior only; not an engine test','pageErrors':[],'states':new,'comparisons':comparisons},ensure_ascii=False,indent=2)+'\n')
 print('PASS frozen v318 vs refactor: 8 matching captures (bounded renderer noise recorded); shared note/group selection and drag/cancel; child navigation/delete cancel; fold/close/reopen/reload; no page errors')
