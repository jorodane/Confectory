"""Measure real mouse drag to editable property fields in one fresh profile.

Run: python tests/performance/editor_property_open.py REPO BUILD_REPORT
Set the same host/runtime environment as the ordinary web UI fixtures. Three
independent invocations per build report permit an alternating A/B comparison.
This measures, rather than asserts, latency on the actual test machine.
"""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'web'))
import v821_property_window_reopen_ui as r
from playwright.sync_api import sync_playwright,expect
f=r.fixture;d=r.fallback;r.seed();expect.set_options(timeout=60000);f.env['CONFECTORY_UI_TRACE']='1'
try:
 with sync_playwright() as p,p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu']) as b:
  f.start(0);page=f.setup(b);page.set_viewport_size({'width':2000,'height':1200});page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"')
  for n,name,folder,xyrel in [(1,d.TARGET,'StockFolder',(.82,.62)),(2,d.PEER,'PeerFolder',(.58,.82))]:
   browser=r.browser_window(page);r.choose_tree_location(browser,f'[data-tree-id="{d.NS}::{folder}"]');r.search(browser,d.LABEL,name);item=browser.locator(f'[data-object="{d.NS}::{name}"]');expect(page.locator('#project-menu')).to_be_enabled();key='editor-'+str(n)
   page.evaluate('''key=>{globalThis.marks=[];document.addEventListener('drop',e=>{if(!e.isTrusted)return;const start=performance.now();let seen=new Set();const loop=()=>{const w=document.querySelector('.window[data-key="'+key+'"]');const input=w?.querySelector('[data-property-value]');const ready=!!input&&w.getClientRects().length&&!w.hidden&&!input.disabled&&!input.readOnly&&!input.closest('[inert]');for(const [name,ok] of [['visible',w?.getClientRects().length&&!w.hidden],['editable',ready],['commands',ready&&!document.querySelector('#project-menu')?.disabled]])if(ok&&!seen.has(name)){seen.add(name);marks.push([name,performance.now()-start]);}if(!seen.has('commands')&&performance.now()-start<60000)requestAnimationFrame(loop);};requestAnimationFrame(loop);},{capture:true,once:true})}''',key)
   box=item.bounding_box();start=(box['x']+12,box['y']+12);canvas=page.locator('#workspace').bounding_box();xy=(canvas['x']+canvas['width']*xyrel[0],canvas['y']+canvas['height']*xyrel[1]);page.mouse.move(*start);page.mouse.down();page.mouse.move(start[0]+12,start[1]+2,steps=3);page.mouse.move(*xy,steps=12);page.mouse.move(xy[0]+1,xy[1]);page.mouse.up()
   window=page.locator(f'.window[data-key="{key}"]');note=r.floating.property_value(window,'Note');expect(note).to_be_editable();note.fill('actual local input '+str(n));expect(note).to_have_value('actual local input '+str(n));expect(page.locator('#project-menu')).to_be_enabled();print(n,name,json.dumps(page.evaluate('marks')),flush=True)
  expect(r.floating.property_value(page.locator('.window[data-key="editor-1"]'),'Note')).to_have_value('actual local input 1');f.original()
finally:f.stop();print('evidence',f.root,flush=True)
