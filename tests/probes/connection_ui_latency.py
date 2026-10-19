"""Linux-only actual-click timing and exec-count probe; see docs/EDITOR_CONNECTION_LATENCY.md.

Arguments: repository, ordinary EditorHome build-report JSON, owned output directory.
Requires existing Chromium, Playwright and strace. Never installs or configures a provider.
"""
import json, os, pathlib, signal, subprocess, sys, tempfile, time
from playwright.sync_api import sync_playwright, expect

repo=pathlib.Path(sys.argv[1]); report=json.loads(pathlib.Path(sys.argv[2]).read_text()); out=pathlib.Path(sys.argv[3]); out.mkdir(parents=True,exist_ok=True)
if os.environ.get('PROBE_PARTIAL')=='1':
 import hashlib
 settings=out/'storage'/'ai-settings'/hashlib.sha256(b'Confectory.Agent.Codex::Connection').hexdigest()[:16];settings.mkdir(parents=True,exist_ok=True)
 (settings/'Settings.celem').write_text('object Confectory.AISettings::Settings extends Confectory.Agent.Codex::Connection {data model = \"preserved-user-input\";}\n')
env=os.environ.copy(); env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_ENTRY_STORAGE=str(out/'storage'),CONFECTORY_HOME_STORAGE=str(out/'storage'),CONFECTORY_MCP_DIRECTORY=str(out/'instances'),CONFECTORY_UI_TRACE='1'); env.pop('CONFECTORY_WEB_PROJECT',None)
log=(out/'host.log').open('w'); host=subprocess.Popen(['strace','-f','-ttt','-e','trace=execve','-s','256','-o',str(out/'exec.log'),*report['run']],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
try:
 for _ in range(600):
  lines=(out/'host.log').read_text().splitlines(); urls=[x.split(' ',1)[1] for x in lines if x.startswith('CONFECTORY_WEB_UI ')]
  if urls: url=urls[-1];break
  assert host.poll() is None, lines[-10:]; time.sleep(.1)
 else: raise AssertionError('startup timeout')
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu']); page=browser.new_page(viewport={'width':1360,'height':900}); errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script('''(()=>{globalThis.confectoryWebUITrace=[];const records=globalThis.__perf=[];const record=(kind,data={})=>records.push({kind,t:performance.now(),wall:Date.now(),...data});document.addEventListener('click',e=>record('click',{target:e.target.closest('button')?.getAttribute('aria-label')||e.target.closest('button')?.textContent}),true);const fetch0=globalThis.fetch;globalThis.fetch=async(...args)=>{let req;try{req=JSON.parse(args[1]?.body||'{}')}catch{}const id=crypto.randomUUID();record('request',{id,op:req?.op,endpoint:req?.endpoint});const r=await fetch0(...args);r.clone().json().then(reply=>record('response',{id,op:req?.op,endpoint:req?.endpoint,code:reply.error?.code,busy:reply.busy,revision:reply.revision,results:reply.results?.filter(x=>x.status!=='pending').map(x=>({id:x.requestId,code:x.error?.code}))}));return r;};let prev='';new MutationObserver(()=>{const d=document.querySelector('[data-connection-dialog]');const stamp=JSON.stringify({dialog:!!d,enabled:!!d?.querySelector('[data-connection-choice]:not(:disabled)'),form:!!d?.querySelector('[data-mcp-panel]'),toast:document.querySelector('#toast')?.textContent});if(stamp!==prev){prev=stamp;record('dom',JSON.parse(stamp));}}).observe(document,{subtree:true,childList:true,attributes:true,attributeFilter:['disabled']});})();''')
  page.goto(url);expect(page.locator('.home-grid')).to_be_visible(); page.wait_for_timeout(1000)
  phases=[]
  for n in range(3):
   start=time.time(); offset=page.evaluate('__perf.length'); page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='사용할 AI',exact=True);expect(dialog).to_be_visible(); button=dialog.get_by_role('button',name='Codex',exact=True);expect(button).to_be_enabled(); button.click()
   # Baseline may fail: wait until either settings or the generic toast becomes visible.
   deadline=time.monotonic()+25
   while time.monotonic()<deadline and not dialog.locator('[data-mcp-panel]').count() and '소스 작업' not in page.locator('#toast').inner_text(): page.wait_for_timeout(20)
   result='form' if dialog.locator('[data-mcp-panel]').count() else 'error';expect(dialog.locator('[data-connection-cancel]')).to_be_enabled();dialog.locator('[data-connection-cancel]').click();expect(dialog).to_have_count(0);page.wait_for_timeout(200)
   phases.append({'iteration':n,'start':start,'end':time.time(),'result':result,'toast':page.locator('#toast').inner_text(),'records':page.evaluate('__perf').copy()[offset:]})
  client=page.evaluate('globalThis.confectoryWebUITrace||[]');browser.close()
 (out/'browser.json').write_text(json.dumps({'phases':phases,'errors':errors,'clientTimings':client},indent=2,ensure_ascii=False)); print(out)
finally:
 if host.poll() is None: os.killpg(host.pid,signal.SIGTERM)
 host.wait(timeout=15);log.close()
