"""Actual renderer and shipped engine using only the owned fake CLI/account."""
import json,urllib.request,uuid
from playwright.sync_api import expect

def run(c):
 page=c['page'];case=c['case'];requests=c['requests'];checks=[];c['control'](projectChat=True)
 def raw(body):
  req=urllib.request.Request(c['origin']+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':c['token']});return json.load(urllib.request.urlopen(req,timeout=30))
 def state():
  for _ in range(500):
   v=raw({'op':'mount'})
   if v.get('error',{}).get('code')=='busy':page.wait_for_timeout(10);continue
   assert v['ok'],v;break
  else:raise AssertionError('owned state busy')
  try:return v['state']
  finally:raw({'op':'dispose','view':v['view']})
 def invoke(endpoint,body,deny=False):
  for attempt in range(4):
   v=raw({'op':'mount'});assert v['ok'],v;rid=uuid.uuid4().hex
   try:
    ack=raw({'op':'invoke','view':v['view'],'scope':v['scope'],'expectedRevision':v['revision'],'requestId':rid,'endpoint':endpoint,'input':body});assert ack['ok'],ack
    for _ in range(600):
     update=raw({'op':'update','view':v['view'],'scope':v['scope']});found=[r for r in update.get('results',[]) if r['requestId']==rid]
     if not update.get('ok'):result={'error':update['error']};break
     if found:result=found[0];break
     page.wait_for_timeout(10)
    else:raise AssertionError('owned invoke pending')
   finally:raw({'op':'dispose','view':v['view']})
   if result.get('error',{}).get('code')=='stale_revision' and attempt<3:continue
   assert bool(result.get('error'))==deny,result;return result
 def receipts():
  f=c['storage']/'chat-use-grants.json';return [r for r in json.loads(f.read_text())['grants'] if r['state']=='active'] if f.exists() else []
 def turns():return [r for r in requests() if r['method']=='turn/start']
 def settings():
  page.locator('#add-agent').click();d=page.get_by_role('dialog',name='Agent 추가',exact=True);d.get_by_role('button',name='Codex',exact=True).click();return d
 def create(name):
  before={h['id'] for h in state()['helpers']}
  page.locator('#add-helper').click();creator=page.locator('[data-v508-helper]');creator.locator('#participant-name').fill(name);creator.locator('#participant-description').fill('Owned fixture only');creator.locator('button[type=submit]').click();expect(creator).to_have_count(0);s=state();assert s['projectId']=='';return next(h['id'] for h in s['helpers'] if h['id'] not in before)
 def open_helper(helper,can_send=True):
  page.locator('.home-side [data-helper="'+helper+'"]').first.click();card=page.locator('.participant-expanded-card:not(.coworker-hover-card)');expect(card.locator('textarea')).to_be_visible();(expect(card.locator('button[type=submit]')).to_be_enabled() if can_send else expect(card.locator('button[type=submit]')).to_be_disabled());return card
 def send(card,text,count,project=''):
  card.locator('textarea').fill(text);expect(card.locator('button[type=submit]')).to_be_enabled();card.locator('textarea').press('Enter');expect(card.locator('textarea')).to_have_value('');expect(card.locator('.messages')).to_contain_text('OWNED CLI HELPER REPLY',timeout=40000)
  for _ in range(500):
   s=state()
   if len(turns())==count and (s.get('aiState')=='completed' if project else all(t.get('state')!='running' for t in s['helperAgents']['turns'].values())):break
   page.wait_for_timeout(20)
  assert len(turns())==count;expect(page.locator('[data-chat-use-consent],[data-global-approval]')).to_have_count(0);assert state()['projectId']==project
 page.add_init_script("globalThis.__projectBucket='one';")
 page.goto(c['url']);expect(page.locator('.welcome #connect')).to_be_enabled();page.locator('#connect').click();d=page.get_by_role('dialog',name='Agent 추가',exact=True);d.get_by_role('button',name='Codex',exact=True).click();d.locator('[data-cli-login]').click();expect(d.locator('[data-cli-account]')).to_be_visible();d.locator('[data-cli-account]').click();expect(d.locator('[data-agent-use-accept]')).to_be_enabled(timeout=40000)
 assert state()['helperAgents']['agents']==[] and not receipts() and not turns();expect(page.locator('.home-grid')).to_have_count(0);expect(d.locator('input[type=checkbox]')).to_have_count(0);page.screenshot(path=str(case/'agent-explicit-before-registration.png'));checks.append('technical readiness alone neither registers nor consents nor enters Home')
 d.locator('[data-close]').click();expect(d).to_have_count(0);assert state()['helperAgents']['agents']==[] and not receipts();checks.append('closing common consent does not register or grant')
 page.locator('#connect').click();d=page.get_by_role('dialog',name='Agent 추가',exact=True);d.get_by_role('button',name='Codex',exact=True).click();expect(d.locator('[data-agent-use-accept]')).to_be_enabled();d.locator('[data-agent-use-accept]').click();expect(page.locator('.home-grid')).to_be_visible(timeout=40000);page.wait_for_function("() => !document.querySelector('.startup-flight-layer')");expect(d).to_have_count(0);assert not page.locator('#app').evaluate('e=>e.inert');assert len(state()['helperAgents']['agents'])==1 and len(receipts())==1;assert receipts()[0]['basis']['policy']=='codex-agent-use-v2';assert not turns();checks.append('one explicit Agent completion registers, grants and finishes Intro')
 print('MILESTONE explicit Agent common registration passed',flush=True)
 first=create('fff');card=open_helper(first);send(card,'Owned fff first',1);page.screenshot(path=str(case/'fff-global-direct.png'));card.locator('[data-close]').click();second=create('Second Helper');card=open_helper(second);send(card,'Owned second first',2);send(card,'Owned second next',3);assert len(receipts())==1;checks.append('fff and second global Helper direct first/next send with no Helper grant or project context');page.screenshot(path=str(case/'second-helper-global-direct.png'));card.locator('[data-close]').click()
 print('MILESTONE fff and second Helper direct replies passed',flush=True)
 title='Owned Scope '+case.name[-8:]
 # The original new-project roster is the explicit project-scope action.
 page.locator('#new-project').click();d=page.get_by_role('dialog',name='새 프로젝트 만들기',exact=True);d.locator('#project-name').fill(title);d.locator('[data-project-helper="'+first+'"]').click();d.locator('[data-project-helper="'+second+'"]').click();expect(d.locator('.project-helper-heading')).to_contain_text('최종 반영·실행·다른 프로젝트');d.locator('button[type=submit]').click();expect(page.locator('.work-body')).to_be_visible(timeout=40000);expect(d).to_have_count(0);project=state()['projectId'];assert project and state()['projectHelperIds']==[first,second];assert len(receipts())==3;assert not page.locator('#app').evaluate('e=>e.inert');checks.append('original project creation/roster explicitly grants only exact selected Helper project scopes');print('MILESTONE project creation and two Helper placement passed',flush=True)
 card=open_helper(first);send(card,'Owned assigned project first',4,project);send(card,'Owned assigned project next',5,project);card.locator('[data-close]').click();card=open_helper(second);send(card,'Owned second project first',6,project);card.locator('[data-close]').click();checks.append('both assigned Helpers project first/next direct, no contract dialog');print('MILESTONE project first/next replies passed',flush=True);page.screenshot(path=str(case/'project-direct-placement.png'))
 before=len(turns());invoke('projectHelpers',{'action':'apply','token':'forged'},True);invoke('projectHelpers',{'action':'plan','helpers':[first],'confirmApproved':True},True);assert len(turns())==before and state()['projectId']==project
 # Reuse the original roster for edits; cancel never changes a receipt or roster.
 page.locator('#add-helper').click();d=page.get_by_role('dialog',name='프로젝트 도우미 배치',exact=True);expect(d.locator('#project-name')).to_be_disabled();d.locator('[data-remove-helper="'+second+'"]').click();d.locator('[data-project-cancel]').click();assert state()['projectHelperIds']==[first,second] and len(receipts())==3
 page.locator('#add-helper').click();d=page.get_by_role('dialog',name='프로젝트 도우미 배치',exact=True);
 while d.locator('[data-remove-helper]').count():d.locator('[data-remove-helper]').first.click()
 d.locator('button[type=submit]').click();expect(d).to_have_count(0);assert state()['projectId']==project and state()['projectHelperIds']==[] and len(receipts())==1;card=open_helper(first,False);expect(card.locator('textarea')).to_be_disabled();expect(card.locator('button[type=submit]')).to_be_disabled();invoke('prepareAI',{'kind':'chat','message':'Owned unassigned must not dispatch'},True);invoke('selectHelperConversation',{'helper':first},True);assert len(turns())==6 and state()['projectId']==project;card.locator('[data-close]').click();checks.append('cancel preserves old placement; explicit removal revokes all project receipts and blocks unassigned send without global fallback')
 stale_plan=invoke('projectHelpers',{'action':'plan','helpers':[first]})['result']['token']
 page.locator('.brand').click();expect(page.locator('.home-grid')).to_be_visible();card=open_helper(first);send(card,'Owned global after project removal',7);card.locator('[data-close]').click();assert len(receipts())==1;checks.append('project removal preserves Agent grant and global Helper conversation')
 req=urllib.request.Request(c['origin']+'/fixture/native-create',data=json.dumps({'title':title,'description':'Same name, another owned folder','bucket':'two'}).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':c['token']});native=json.load(urllib.request.urlopen(req,timeout=30));assert native['ok'],native;expect(page.locator('.work-body')).to_be_visible(timeout=30000);other=state()['projectId'];assert other and other!=project and state()['projectHelperIds']==[]
 invoke('projectHelpers',{'action':'apply','token':stale_plan},True);invoke('prepareAI',{'kind':'chat','message':'Owned other project must not dispatch'},True);assert len(turns())==7 and len(receipts())==1 and state()['projectId']==other;page.screenshot(path=str(case/'other-project-denied.png'));checks.append('same-name different-folder project cannot reuse old placement token or context and cannot dispatch unassigned chat');page.locator('.brand').click();expect(page.locator('.home-grid')).to_be_visible()
 d=settings();expect(d.locator('[data-agent-use-revoke]')).to_be_enabled();d.locator('[data-agent-use-revoke]').click();expect(d.locator('[data-agent-use-accept]')).to_be_enabled();assert not receipts();page.screenshot(path=str(case/'agent-revoked.png'));d.locator('[data-close]').click();card=open_helper(first);card.locator('textarea').fill('Owned after Agent revoke');card.locator('textarea').press('Enter');expect(page.locator('#toast')).to_contain_text('chat-use-agent-consent-required');expect(card.locator('textarea')).to_have_value('Owned after Agent revoke');expect(page.locator('[data-chat-use-consent]')).to_have_count(0);assert len(turns())==7;checks.append('Agent settings revocation blocks global use, preserves input and shows no Helper consent')
 for t in turns():
  body=json.loads(t['params']['input'][0]['text']);assert body['kind'] in ('helper-global-chat','project-chat');assert body['projectId']==('' if body['kind']=='helper-global-chat' else project)
 assert not c['errors'] and not c['external'],(c['errors'],c['external']);(case/'agent-common-evidence.json').write_text(json.dumps({'checks':checks,'turns':len(turns()),'fixtureAccountOnly':True,'actualOAuthOrInference':False,'windowsExecuted':False},indent=2));print('PASS actual Agent common consent renderer '+str(case),flush=True)
