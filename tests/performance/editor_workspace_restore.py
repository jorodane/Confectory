"""Measure project card activation with 0, 1 or 3 restored property windows.

Run: python tests/run_isolated_browser_test.py -- python tests/performance/editor_workspace_restore.py REPO BUILD_REPORT 3
The fixture creates an isolated profile, hides the project, reopens it, then
restarts the editor and compares the real window and control milestones.
"""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'web'))
import v821_property_window_reopen_ui as r
from playwright.sync_api import sync_playwright,expect
f=r.fixture;d=r.fallback;r.seed();count=int(sys.argv[3]);assert count in (0,1,3);expect.set_options(timeout=90000)
f.env['CONFECTORY_UI_TRACE']='1'
def capture(page):
 page.locator('.project-card').filter(has=page.get_by_role('heading',name=d.FIRST,exact=True)).locator('[data-enter]').evaluate("""el=>{globalThis.marks=[];globalThis.confectoryWebUITrace=[];el.addEventListener('click',()=>{const start=performance.now();let names=new Set();function loop(){const check=(name,ok)=>{if(ok&&!names.has(name)){names.add(name);marks.push([name,performance.now()-start]);}};check('workspace',!!document.querySelector('.work-body'));check('chat-editable',!!document.querySelector('#chat-input')&&!document.querySelector('#chat-input').disabled&&!document.querySelector('#chat-input').closest('[inert]'));check('commands',!!document.querySelector('#project-menu')&&!document.querySelector('#project-menu').disabled);for(const w of document.querySelectorAll('.window[data-key^=editor-]')){const input=w.querySelector('[data-property-value]');check(w.dataset.key+'-visible',!w.hidden&&w.getClientRects().length&&!!input);check(w.dataset.key+'-editable',!w.hidden&&w.getClientRects().length&&!!input&&!input.disabled&&!input.closest('[inert]'));}if(performance.now()-start<60000)requestAnimationFrame(loop);}requestAnimationFrame(loop)},{once:true,capture:true})}""")
def open_and_measure(page,kind):
 capture(page)
 page.locator('.project-card').filter(has=page.get_by_role('heading',name=d.FIRST,exact=True)).locator('[data-enter]').click()
 expect(page.locator('.work-body')).to_be_visible()
 expect(page.locator('.window[data-key^="editor-"]:visible')).to_have_count(count)
 expect(page.locator('#project-menu')).to_be_enabled()
 for w in page.locator('.window[data-key^="editor-"]:visible').all():expect(w.locator('[data-property-value]').first).to_be_editable()
 page.wait_for_timeout(120)
 print(kind,count,json.dumps(page.evaluate('marks')),flush=True);print('trace',json.dumps(page.evaluate('confectoryWebUITrace')),flush=True)
 f.original()
try:
 with sync_playwright() as p,p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) as b:
  f.start(0);page=f.setup(b);page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"');page.set_viewport_size({'width':2000,'height':1200})
  for name,folder in [(d.TARGET,'StockFolder'),(d.PEER,'PeerFolder'),('Extra1','ExtraFolder1')][:count]:
   w,_=r.floating.open_properties(page,name,folder);expect(w.locator('[data-property-value]').first).to_be_editable()
  page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"');page.evaluate('()=>confectoryFlushPresentation()')
  page.locator('.brand').click();expect(page.locator('.home-grid')).to_be_visible();open_and_measure(page,'warm')
  page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"');page.evaluate('()=>confectoryFlushPresentation()');page.close();f.stop()
  f.env.pop('CONFECTORY_WEB_PROJECT',None);f.start(1);page=b.new_page();page.route('**/*',lambda route:route.continue_() if route.request.url.startswith(f.origin+'/') else route.abort());from editor_navigation import goto_editor;goto_editor(page,f.url);page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"');page.set_viewport_size({'width':2000,'height':1200});expect(page.locator('.home-grid')).to_be_visible();open_and_measure(page,'cold')
finally:f.stop();print('evidence',f.root,flush=True)
