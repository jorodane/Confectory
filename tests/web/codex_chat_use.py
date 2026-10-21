"""Scoped use exercised through the actual engine UI and an owned CLI protocol.
Only fake account metadata and temporary projects; no live account/OAuth/inference.
"""
import json,os,pathlib,signal,subprocess,time,urllib.request,uuid
from playwright.sync_api import expect
from editor_navigation import goto_editor

def run(c):
 page=c['page'];case=c['case'];storage=c['storage'];requests=c['requests'];control=c['control'];checks=[]
 control(projectChat=True)
 def raw(path,body):
  req=urllib.request.Request(c['origin']+path,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':c['token']})
  return json.load(urllib.request.urlopen(req,timeout=30))
 def mount():
  for _ in range(500):
   result=raw('/api/request',{'op':'mount'})
   if result.get('error',{}).get('code')=='busy':page.wait_for_timeout(20);continue
   assert result['ok'],result;return result
  raise AssertionError('owned mount busy')
 def state():
  v=mount()
  try:return v['state']
  finally:raw('/api/request',{'op':'dispose','view':v['view']})
 def invoke(endpoint,body,allow_error=False):
  for attempt in range(3):
   v=mount();rid=uuid.uuid4().hex
   try:
    ack=raw('/api/request',{'op':'invoke','view':v['view'],'scope':v['scope'],'requestId':rid,'expectedRevision':v['revision'],'endpoint':endpoint,'input':body});assert ack['ok'],ack
    for _ in range(600):
     update=raw('/api/request',{'op':'update','view':v['view'],'scope':v['scope']})
     if not update.get('ok'):result={'error':update['error']};break
     found=[r for r in update.get('results',[]) if r['requestId']==rid]
     if found:result=found[0];break
     page.wait_for_timeout(10)
    else:raise AssertionError('owned action pending')
   finally:raw('/api/request',{'op':'dispose','view':v['view']})
   if result.get('error',{}).get('code')=='stale_revision' and attempt<2:continue
   if not allow_error:assert not result.get('error'),result
   return result
 def turns():return [r for r in requests() if r['method']=='turn/start']
 def active_receipts():return [r for r in json.loads((storage/'chat-use-grants.json').read_text())['grants'] if r['state']=='active'] if (storage/'chat-use-grants.json').exists() else []
 def helper_card():return page.locator('.participant-expanded-card:not(.coworker-hover-card)')
 def open_helper(helper):
  page.locator('.home-side [data-helper="'+helper+'"]').first.click();card=helper_card();expect(card.locator('textarea')).to_be_visible();return card
 def send(text,first=False):
  card=helper_card();before=len(turns());card.locator('textarea').fill(text);expect(card.locator('button[type=submit]')).to_be_enabled();card.locator('textarea').press('Enter')
  if first:
   expect(page.locator('[data-chat-use-consent]')).to_be_visible();assert len(turns())==before;expect(page.locator('[data-permission],[data-global-permission]')).to_have_count(0)
  else:
   expect(card.locator('textarea')).to_have_value('');expect(page.locator('[data-chat-use-consent]')).to_have_count(0)
  return before
 def allow():
  page.locator('[data-chat-use-allow]').click();expect(page.locator('[data-chat-use-consent]')).to_have_count(0);expect(helper_card().locator('textarea')).to_have_value('')
 def reply(count):
  for _ in range(900):
   s=state();done=s.get('aiState')=='completed' if s.get('projectId') else s['helperAgents']['turns'].get(helper,{}).get('state')=='completed'
   if done:break
   page.wait_for_timeout(20)
  else:raise AssertionError('owned response never completed')
  expect(helper_card().locator('.messages')).to_contain_text('OWNED CLI HELPER REPLY');assert len(turns())==count
 def create(bucket):
  reply=raw('/fixture/native-create',{'title':'Same Name '+case.name[-8:],'description':'Owned isolated chat scope','bucket':bucket});assert reply['ok'],reply
  result=invoke('projectHelpers',{'helpers':[helper]},True);assert not result.get('error') or result['error']['code']=='scope_changed',result
  s=state();assert s['projectHelperIds']==[helper];goto_editor(page,c['url']);expect(page.locator('#helper-summary')).to_contain_text(helper);open_helper(helper);return s['projectId'],next(row['id'] for row in s['cards'] if row['id'] not in cards_seen)
 def home():
  helper_card().locator('textarea').focus() if helper_card().count() else None;page.locator('.brand').click();expect(page.locator('.home-grid')).to_be_visible()
 page.locator('#add-helper').click();creator=page.locator('[data-v508-helper]');creator.locator('#participant-name').fill('Owned Scope Helper');creator.locator('#participant-description').fill('Owned fake CLI only');creator.locator('button[type=submit]').click();expect(creator).to_have_count(0)
 helper=state()['helpers'][0]['id'];held=[]
 def hold_history(route):
  body=route.request.post_data_json
  if body.get('op')=='invoke' and body.get('endpoint')=='helperGlobal' and body.get('input',{}).get('action')=='conversation' and not held:held.append(route)
  else:route.continue_()
 page.route('**/api/request',hold_history);open_helper(helper);assert not active_receipts()
 # Hold a real history request, then press Enter while the busy gate is active.
 for _ in range(1000):
  if held:break
  page.wait_for_timeout(10)
 else:raise AssertionError('real conversation request not intercepted')
 expect(helper_card().locator('button[type=submit]')).to_be_disabled()
 helper_card().locator('textarea').fill('owned global initial');helper_card().locator('textarea').press('Enter');helper_card().locator('textarea').press('Enter')
 helper_card().locator('textarea').fill('owned newer while history');expect(helper_card().locator('textarea')).to_have_value('owned newer while history');assert not turns() and not active_receipts();held[0].continue_();page.unroute('**/api/request',hold_history)
 expect(page.locator('[data-chat-use-consent]')).to_be_visible();checks.append('Enter during held history queues once, input preserved, no silent dropped send');print('MILESTONE initial consent after held history',flush=True);page.screenshot(path=str(case/'global-initial-use.png'));page.set_viewport_size({'width':640,'height':500});expect(page.locator('[data-chat-use-allow]')).to_be_visible();page.locator('[data-chat-use-allow]').scroll_into_view_if_needed();assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(case/'global-initial-small.png'));page.set_viewport_size({'width':1440,'height':1000});page.locator('[data-chat-use-cancel]').click();expect(page.locator('[data-chat-use-consent]')).to_have_count(0);expect(helper_card().locator('textarea')).to_have_value('owned newer while history');assert not turns() and not active_receipts()
 print('MILESTONE cancel preserves card/input',flush=True);send('owned global initial',True);allow();reply(1);print('MILESTONE first global reply',flush=True);assert len(active_receipts())==1;send('owned global second');reply(2);print('MILESTONE second global direct reply',flush=True);page.screenshot(path=str(case/'global-direct-second.png'));checks+=['legacy no continuing grant','cancel no grant/dispatch/input loss','explicit global use once','second global send direct']
 cards_seen={r['id'] for r in state()['cards']};project,card_a=create('one');cards_seen.add(card_a);assert project
 send('owned project initial',True);pending=state()['aiPreview'];assert pending['helperContext']['helper']==helper;before=len(turns())
 forged=invoke('startAI',{'token':pending['token'],**{r:True for r in ('contentApproved','usageApproved','processApproved','managedCredentialApproved','managedConfigurationApproved','managedStorageApproved')}},True);assert forged.get('error'),forged;assert len(turns())==before
 denied=invoke('chatUse',{'action':'authorize','kind':'project'},True);assert denied.get('error'),denied
 denied=invoke('chatUse',{'action':'accept','kind':'project','helper':helper,'challenge':'forged','approvals':{'contentApproved':True}},True);assert denied.get('error'),denied
 page.screenshot(path=str(case/'project-initial-use.png'));allow();reply(3);print('MILESTONE first project reply',flush=True);assert state()['projectId']==project and len(active_receipts())==2
 send('owned project second');reply(4);print('MILESTONE second project direct reply',flush=True);assert state()['projectId']==project;page.screenshot(path=str(case/'project-direct-second.png'));checks+=['global grant cannot cover project','forged six flags/internal action/client grant denied','explicit project use once','second project send direct, context intact']
 # A new selected-memory entry is content in an already disclosed category.
 invoke('helperRemember',{'helper':helper,'scope':'project','text':'OWNED project category content'});send('owned after memory');reply(5);assert 'OWNED project category content' in turns()[-1]['params']['input'][0]['text'];checks.append('new memory content within category no new consent')
 receipt_ids={r['id'] for r in active_receipts()};accounts=sum(r['method']=='account/read' for r in requests());assert raw('/fixture/expire',{})['ok'];send('owned after technical expiry');reply(6);assert receipt_ids=={r['id'] for r in active_receipts()} and sum(r['method']=='account/read' for r in requests())>=accounts+2;checks.append('technical expiry renews without new use consent');print('MILESTONE expiry renewed, receipts unchanged',flush=True)
 assert state()['chatDraft']=='';home();other,card_b=create('two');assert other!=project;send('owned other project',True);page.locator('[data-chat-use-cancel]').click();assert len(turns())==6;checks.append('same name different project/path does not reuse grant');print('MILESTONE same-name distinct project needs consent',flush=True);home()
 assert state()['chatDraft'] in ('',None)
 # Full engine restart reloads stored use consent, but must obtain fresh technical evidence.
 c['page'].close();os.killpg(c['host'].pid,signal.SIGTERM);c['host'].wait(timeout=15);c['log'].close();c['log']=c['log_path'].open('w');c['host']=subprocess.Popen(c['report']['run'],cwd=c['repo'],env=c['run_env'],stdout=c['log'],stderr=subprocess.STDOUT,start_new_session=True)
 for _ in range(700):
  urls=[line.split(' ',1)[1] for line in c['log_path'].read_text().splitlines() if line.startswith('CONFECTORY_WEB_UI ')]
  if urls:c['url']=urls[-1];break
  assert c['host'].poll() is None;time.sleep(.03)
 else:raise AssertionError('restart startup timeout')
 c['origin'],c['token']=c['url'].split('/#');page=c['browser'].new_page(viewport={'width':1440,'height':1000});c['page']=page;page.on('pageerror',lambda e:c['errors'].append(str(e)))
 def route(req):
  if req.request.url.startswith(c['origin']+'/') or req.request.url.startswith('data:'):req.continue_()
  else:c['external'].append(req.request.url);req.abort()
 page.route('**/*',route);goto_editor(page,c['url']);open_helper(helper);expect(helper_card().locator('.messages')).to_contain_text('owned global second');send('owned global after restart');reply(7);assert receipt_ids=={r['id'] for r in active_receipts()};helper_card().locator('[data-close]').click();page.locator('[data-enter="'+card_a+'"]').click();expect(page.locator('#helper-summary')).to_contain_text(helper);open_helper(helper);send('owned project after restart');reply(8);assert receipt_ids=={r['id'] for r in active_receipts()};checks+=['engine restart loads consent/history','global and original project direct after startup revalidation']
 # Original sent draft stays cleared; the other project's cancelled draft survives restart.
 expect(helper_card().locator('textarea')).to_have_value('');home();page.locator('[data-enter="'+card_b+'"]').click();expect(page.locator('#helper-summary')).to_contain_text(helper);open_helper(helper);expect(helper_card().locator('textarea')).to_have_value('owned other project');assert len(turns())==8;home();page.locator('[data-enter="'+card_a+'"]').click();expect(page.locator('#helper-summary')).to_contain_text(helper);open_helper(helper);expect(helper_card().locator('textarea')).to_have_value('');checks+=['sent project draft remains cleared','cancelled different-project draft restored without send']
 print('MILESTONE restart direct sends and separate draft restoration',flush=True)
 # Revoke while the owned provider is waiting in its fresh account check, before context dispatch.
 control(holdAccount=True);before=sum(r['method']=='account/read' for r in requests());send('owned pending revocation')
 for _ in range(500):
  if sum(r['method']=='account/read' for r in requests())>before:break
  page.wait_for_timeout(20)
 else:raise AssertionError('owned request did not reach pre-dispatch account check')
 helper_card().locator('.helper-window-settings').click();expect(page.locator('[data-chat-use-revoke]')).to_be_visible();page.locator('[data-chat-use-revoke]').click();expect(page.locator('#toast')).to_contain_text('대화 사용을 해제');assert not active_receipts();control(holdAccount=False);page.locator('.modal [data-close]').last.click();page.wait_for_timeout(500);assert len(turns())==8
 if not helper_card().count():open_helper(helper)
 send('owned requires re-optin',True);page.locator('[data-chat-use-cancel]').click();assert len(turns())==8;checks+=['settings revoke cancels before inference','revokes project/global receipts together','later send requires new optin, no silent revival']
 for row in turns():
  content=json.loads(row['params']['input'][0]['text']);assert 'authorization' not in content and 'chatUseToken' not in content
  if content['kind']=='helper-global-chat':assert content['projectId']==''
  else:assert content['kind']=='project-chat' and content['projectId']==project
 assert not c['errors'],c['errors'];(case/'chat-use-evidence.json').write_text(json.dumps({'checks':checks,'turns':len(turns()),'noRealAccountOrInference':True,'windowsExecuted':False,'projectIdsDistinct':project!=other},indent=2));page.screenshot(path=str(case/'after-revoke.png'));print('PASS actual Codex scoped-use UI/backend '+str(case),flush=True)
