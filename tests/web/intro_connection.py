"""Actual startup connection flow with owned CLI/accounts, no live OAuth/inference."""
import json,os,signal,subprocess,time,urllib.request
from playwright.sync_api import expect

def run(c):
 page=c['page'];case=c['case'];name=c['scenario'];requests=c['requests'];control=c['control'];checks=[]
 trace='''globalThis.__introTrace={homes:0,flights:0};new MutationObserver(rows=>{for(const r of rows)for(const n of r.addedNodes)if(n.nodeType===1){if(n.matches('.startup-flight-layer'))__introTrace.flights++;__introTrace.homes+=(n.matches('.home-grid')?1:n.querySelectorAll('.home-grid').length);}}).observe(document,{subtree:true,childList:true});'''
 page.add_init_script(trace)
 def raw(path,body):
  req=urllib.request.Request(c['origin']+path,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':c['token']});return json.load(urllib.request.urlopen(req,timeout=30))
 def state():
  for _ in range(500):
   v=raw('/api/request',{'op':'mount'})
   if v.get('error',{}).get('code')=='busy':page.wait_for_timeout(10);continue
   assert v['ok'],v;break
  else:raise AssertionError('owned state busy')
  try:return v['state']
  finally:assert raw('/api/request',{'op':'dispose','view':v['view']})['ok']
 def home():
  expect(page.locator('.home-grid')).to_be_visible();page.wait_for_function("() => !document.querySelector('.startup-flight-layer')");expect(page.locator('[data-connection-dialog]')).to_have_count(0);assert not page.locator('#app').evaluate('e=>e.inert');expect(page.locator('#new-project')).to_be_enabled();page.locator('#new-project').hover();assert page.evaluate('__introTrace')=={'homes':1,'flights':1}
 page.goto(c['url']);expect(page.locator('.welcome #connect')).to_be_enabled();assert not requests();assert not page.locator('.home-grid').count()
 if name=='intro-settings':page.locator('#later').click();home();page.locator('#add-agent').click()
 else:page.locator('#connect').evaluate('e=>{e.click();e.click();}')
 dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);expect(dialog).to_have_count(1);dialog.get_by_role('button',name='Codex',exact=True).click();expect(dialog.locator('[data-cli-login]')).to_be_enabled();assert not requests();dialog.locator('[data-cli-login]').click()
 if name=='intro-policy-block':
  expect(dialog.locator('[data-codex-onboarding]')).to_have_attribute('data-step','preparation-blocked');assert not page.locator('.home-grid').count();assert state()['helperAgents']['agents']==[];page.screenshot(path=str(case/'intro-policy-blocked.png'));dialog.locator('[data-close]').click();expect(dialog).to_have_count(0);expect(page.locator('.welcome #later')).to_be_enabled();page.locator('#later').click();home();checks+=['policy failure stays intro','cancel then Later remains usable']
 else:
  if name=='intro-install':
   expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 설치');assert not page.locator('.home-grid').count();dialog.locator('[data-cli-consent]').click();expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 로그인');assert state()['codexOnboarding']['installation']['state']=='prepared';assert not page.locator('.home-grid').count();checks.append('installation alone stays intro')
  logged_out=name in ('intro-new-login','intro-install','intro-close-race','intro-stop-race')
  held=[]
  if name in ('intro-close-race','intro-stop-race'):
   def hold_ready(route):
    if route.request.post_data_json.get('op')!='update':route.continue_();return
    response=route.fetch();reply=response.json();agents=reply.get('state',{}).get('helperAgents',{}).get('agents',[])
    if not held and any(a.get('readiness',{}).get('state')=='ready' for a in agents):held.append((route,response))
    else:route.fulfill(response=response)
   page.route('**/api/request',hold_ready)
  if logged_out:
   expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 로그인');dialog.locator('[data-cli-consent]').click();expect(dialog.locator('[data-cli-official-login]')).to_be_visible();assert not page.locator('.home-grid').count();checks.append('waiting for login stays intro')
   if name=='intro-new-login':
    control(failLogin=True);(case/'complete-login').write_text('failed');expect(dialog.locator('[data-cli-retry]')).to_be_enabled();assert not page.locator('.home-grid').count();assert state()['helperAgents']['agents']==[];(case/'complete-login').unlink();control(failLogin=False);dialog.locator('[data-cli-retry]').click();expect(dialog.locator('[data-cli-consent]')).to_be_enabled();dialog.locator('[data-cli-consent]').click();expect(dialog.locator('[data-cli-official-login]')).to_be_visible();checks.append('explicit login failure stays intro, retry works')
    dialog.locator('[data-cli-stop]').click();expect(dialog.locator('[data-cli-login]')).to_be_enabled();assert not page.locator('.home-grid').count();dialog.locator('[data-cli-login]').click();expect(dialog.locator('[data-cli-consent]')).to_be_enabled();dialog.locator('[data-cli-consent]').click();expect(dialog.locator('[data-cli-official-login]')).to_be_visible();checks.append('explicit Stop stays intro; explicit retry restores transition intent')
   (case/'complete-login').write_text('owned')
  else:
   expect(dialog.locator('[data-cli-account]')).to_have_count(1)
   if name!='intro-settings':assert not page.locator('.home-grid').count()
   dialog.locator('[data-cli-account]').first.click()
  if name in ('intro-close-race','intro-stop-race'):
   for _ in range(1000):
    if held:break
    page.wait_for_timeout(10)
   else:raise AssertionError('ready response was not captured')
   assert state()['helperAgents']['agents'][0]['readiness']['state']=='ready';dialog.locator('[data-cli-stop]' if name=='intro-stop-race' else '[data-close]').click();held[0][0].fulfill(response=held[0][1]);page.unroute('**/api/request',hold_ready)
   if name=='intro-stop-race':
    expect(dialog.locator('[data-cli-done]')).to_be_enabled();expect(dialog).to_be_visible();assert not page.locator('.home-grid').count();dialog.locator('[data-close]').click();checks.append('explicit Stop beats an already registered ready reply')
   expect(dialog).to_have_count(0);expect(page.locator('.welcome #connect')).to_be_enabled();assert not page.locator('.home-grid').count();assert page.evaluate('__introTrace')=={'homes':0,'flights':0};assert not page.locator('#app').evaluate('e=>e.inert');page.screenshot(path=str(case/'closed-before-ready-delivery.png'));page.locator('#later').click();home();checks.append('user close before ready delivery cancels auto navigation despite registered ready')
  elif name=='intro-settings':
   expect(dialog.locator('[data-cli-done]')).to_be_enabled();assert page.evaluate('__introTrace')=={'homes':1,'flights':1};expect(dialog).to_be_visible();dialog.locator('[data-cli-done]').click();expect(dialog).to_have_count(0);assert not page.locator('#app').evaluate('e=>e.inert');checks.append('Home settings success does not auto-retire or navigate')
   created=raw('/fixture/native-create',{'title':'Owned Intro Settings','description':'Isolated context','bucket':'one'});assert created['ok'],created;expect(page.locator('.work-body')).to_be_visible();project=state()['projectId'];assert project;page.locator('.home-side [data-agent]').first.click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);expect(dialog.locator('[data-cli-done]')).to_be_enabled();assert state()['projectId']==project;expect(page.locator('.work-body')).to_be_visible();assert page.evaluate('__introTrace')['homes']==1;dialog.locator('[data-cli-done]').click();expect(dialog).to_have_count(0);assert not page.locator('#app').evaluate('e=>e.inert');page.screenshot(path=str(case/'project-settings-stays-project.png'));checks.append('project settings preserve ProjectContext and remain explicit')
  else:
   home();assert state()['helperAgents']['agents'][0]['readiness']['state']=='ready';page.screenshot(path=str(case/'new-connection-home.png'));checks.append('new verified registered connection automatically enters project list once')
   if name=='intro-existing':
    before=sum(r['method']=='account/read' for r in requests());logins=sum(r['method']=='account/login/start' for r in requests());control(holdAccount=True);page.close();os.killpg(c['host'].pid,signal.SIGTERM);c['host'].wait(timeout=15);c['log'].close();c['log']=c['log_path'].open('w');c['host']=subprocess.Popen(c['report']['run'],cwd=c['repo'],env=c['run_env'],stdout=c['log'],stderr=subprocess.STDOUT,start_new_session=True)
    for _ in range(600):
     urls=[line.split(' ',1)[1] for line in c['log_path'].read_text().splitlines() if line.startswith('CONFECTORY_WEB_UI ')]
     if urls:c['url']=urls[-1];break
     assert c['host'].poll() is None;time.sleep(.03)
    else:raise AssertionError('restart startup timeout')
    c['origin'],c['token']=c['url'].split('/#');page=c['browser'].new_page(viewport={'width':1440,'height':1000});c['page']=page;page.add_init_script(trace);page.on('pageerror',lambda e:c['errors'].append(str(e)));page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(c['origin']+'/') or r.request.url.startswith('data:') else (c['external'].append(r.request.url),r.abort()));page.goto(c['url']);expect(page.locator('.welcome #later')).to_be_enabled()
    for _ in range(600):
     if sum(r['method']=='account/read' for r in requests())>before:break
     page.wait_for_timeout(10)
    else:raise AssertionError('startup verification did not begin')
    assert state()['helperAgents']['agents'][0]['readiness']['state']=='checking';assert not page.locator('.home-grid').count();control(holdAccount=False);home();assert sum(r['method']=='account/login/start' for r in requests())==logins;checks.append('registered startup waits for usable readiness then transitions without opening settings/login');page.screenshot(path=str(case/'restored-connection-home.png'))
 assert not [r for r in requests() if r['method']=='turn/start'];assert not c['errors'] and not c['external'];record={'checks':checks,'noRealAccountOrInference':True,'modelTurns':0,'windowsExecuted':False};(case/'intro-evidence.json').write_text(json.dumps(record,indent=2));print('PASS actual intro '+name+' '+str(case),flush=True)
