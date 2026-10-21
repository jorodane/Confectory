"""Actual floating Helper chat geometry with an owned loopback provider.
No real account, credentials or external inference. Baseline mode measures only.
"""
from editor_navigation import goto_editor
import hashlib,json,os,pathlib,signal,subprocess,sys,tempfile,time,urllib.request
from playwright.sync_api import sync_playwright,expect
expect.set_options(timeout=30000)
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());baseline=pathlib.Path(sys.argv[3]).resolve() if len(sys.argv)>3 else None
root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-chat-space-'));storage=root/'profile';print('FIXTURE '+str(root),flush=True)
fixture=subprocess.Popen(['python3',str(repo/'tests/protocol/global_helper_http.py'),str(root)],stdout=subprocess.PIPE,text=True);endpoint=fixture.stdout.readline().strip();assert endpoint.startswith('http://127.0.0.1:')
env=os.environ.copy();env.pop('CONFECTORY_WEB_PROJECT',None);env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(root/'instances'))
if env.get('CONFECTORY_DOTNET'):env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH']
log_path=root/'host.log';log=log_path.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);errors=[];external=[];measured={}
try:
 for _ in range(600):
  urls=[l.split(' ',1)[1] for l in log_path.read_text().splitlines() if l.startswith('CONFECTORY_WEB_UI ')]
  if urls:url=urls[-1];break
  assert host.poll() is None,log_path.read_text();time.sleep(.05)
 else:raise AssertionError('engine startup timeout')
 origin,token=url.split('/#')
 def state():
  def call(body):return json.load(urllib.request.urlopen(urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token}),timeout=20))
  for _ in range(400):
   m=call({'op':'mount'})
   if m.get('error',{}).get('code')=='busy':time.sleep(.01);continue
   assert m['ok'],m;break
  else:raise AssertionError('mount busy')
  try:return m['state']
  finally:assert call({'op':'dispose','view':m['view']})['ok']
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu']);page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
  def route(r):
   if r.request.url.startswith(origin) or r.request.url.startswith('data:'):r.continue_()
   else:external.append(r.request.url);r.abort()
  page.route('**/*',route);goto_editor(page,url);expect(page.locator('#add-agent')).to_be_enabled();page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);dialog.get_by_role('button',name='OpenAI Responses',exact=True).click()
  for name,value in [('model','owned-space-fixture'),('endpoint',endpoint),('credentialReference','')]:dialog.locator('[data-connection-field="'+name+'"]').fill(value)
  dialog.locator('[data-agent-register]').click();expect(dialog.locator('[data-agent-registration-state]')).to_contain_text('Agent 등록됨');dialog.locator('[data-connection-cancel]').click();page.locator('#add-helper').click();creator=page.locator('[data-v508-helper]');creator.locator('#participant-name').fill('Owned Helper');creator.locator('#participant-description').fill('Owned chat layout fixture');creator.locator('button[type=submit]').click();expect(creator).to_have_count(0);helper=page.locator('.home-side [data-helper]').first.get_attribute('data-helper')
  def open_chat():
   page.locator('.home-side [data-helper="'+helper+'"]').first.click();c=page.locator('.participant-expanded-card:not(.coworker-hover-card)');expect(c.locator('form')).to_be_visible();return c
  def measure(c):return c.evaluate('''e=>{const r=e.getBoundingClientRect(),q=s=>e.querySelector(s),b=q('[data-global-send]'),t=q('textarea'),m=q('.messages'),status=q('[data-helper-ai-status]'),box=x=>{const r=x?.getBoundingClientRect();return r?{x:r.x,y:r.y,width:r.width,height:r.height}:null;};return {card:box(e),messages:box(m),send:box(b),input:box(t),font:getComputedStyle(t).fontSize,buttonFont:getComputedStyle(b).fontSize,status:box(status),statusVisible:!!status&&!!status.getClientRects().length,bodyGap:q('.expanded-card-body').getBoundingClientRect().top-q('.helper-profile-status').getBoundingClientRect().bottom,viewport:{width:innerWidth,height:innerHeight}};}''')
  card=open_chat();measured['empty']=measure(card);page.screenshot(path=str(root/'empty.png'))
  card.locator('textarea').fill('hello-global');card.locator('textarea').press('Enter');expect(card.locator('.messages')).to_contain_text('OWNED GLOBAL HTTP FIXTURE');expect(card.locator('[data-global-send]')).to_have_text('보내기');page.wait_for_function("()=>!document.querySelector('#toast').classList.contains('show')");measured['success']=measure(card);page.screenshot(path=str(root/'success.png'))
  if baseline:
   before=json.loads(baseline.read_text())['measured'];actual=measured['success'];old=before['success']
   assert abs(actual['card']['width']-old['card']['width']*1.25)<1,(actual,old)
   assert abs(actual['card']['height']-old['card']['height']*1.25)<1,(actual,old)
   assert actual['messages']['height']>old['messages']['height']*1.25,(actual,old)
   assert not actual['statusVisible'] and card.locator('[data-helper-ai-status]').count()==0
   assert actual['send']['width']==old['send']['width'] and actual['send']['height']==old['send']['height']
   assert actual['font']==old['font'] and actual['buttonFont']==old['buttonFont']
   assert actual['bodyGap']<old['bodyGap'],(actual,old)
   # Responsive clamping includes the opened card and controls, without scaling them.
   for width,height in [(900,760),(600,800),(375,667),(667,375),(320,240)]:
    page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(100);m=measure(card);r=m['card'];assert r['x']>=8 and r['y']>=8 and r['x']+r['width']<=width-8+.5 and r['y']+r['height']<=height-8+.5,m
    assert m['send']['y']>=r['y'] and m['send']['y']+m['send']['height']<=height-8+.5,m
    assert m['send']['height']==old['send']['height'] and m['font']==old['font'] and m['buttonFont']==old['buttonFont'];assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),m
    measured[str(width)+'x'+str(height)]=m;page.screenshot(path=str(root/f'{width}x{height}.png'))
   page.set_viewport_size({'width':1440,'height':1000});card.locator('textarea').fill('fail-global');card.locator('textarea').press('Enter');expect(card.locator('[data-global-send]')).to_have_text('재시도');expect(card.locator('.messages')).to_contain_text('provider-http-error');measured['error']=measure(card);page.screenshot(path=str(root/'error.png'));assert not measured['error']['statusVisible']
   (root/'allow-retry').write_text('owned');card.locator('[data-global-send]').click();expect(card.locator('[data-global-send]')).to_have_text('보내기');expect(card.locator('.messages')).to_contain_text('OWNED GLOBAL HTTP FIXTURE');card.locator('textarea').fill('새 입력 보존');card.locator('[data-close]').click();card=open_chat();expect(card.locator('textarea')).to_have_value('새 입력 보존');expect(card.locator('.messages')).to_contain_text('OWNED GLOBAL HTTP FIXTURE')
  assert not errors and not external,(errors,external);(root/'evidence.json').write_text(json.dumps({'measured':measured,'baseline':str(baseline) if baseline else None,'errors':errors,'external':external,'actualAccountOrInference':False},ensure_ascii=False,indent=2));browser.close();print(('PASS focused Helper chat space / responsive / errors / retry / reopen' if baseline else 'MEASURE baseline Helper chat')+' '+str(root),flush=True)
except BaseException:
 print('FAILED '+str(root),flush=True)
 try:page.screenshot(path=str(root/'failure.png'));print(page.locator('body').inner_text()[-1500:],flush=True)
 except Exception:pass
 raise
finally:
 if host.poll() is None:os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=15)
 if fixture.poll() is None:fixture.terminate();fixture.wait(timeout=10)
 log.close()
