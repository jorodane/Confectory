"""Owned ordinary Home consumer: persisted custom plans without a configured AI."""
import uuid,time
from playwright.sync_api import expect

def verify_local_augment(page,project,mount,send,envelope,settle,restart):
 initial=(project/'Score.celem').read_bytes();manifest=(project/'project.cpack').read_bytes()
 def state():
  v=mount();s=v['state'];assert send(envelope(v,'dispose'))['ok'];return s
 def invoke(endpoint,args,ok=True):
  v=mount();request='local-augment-'+uuid.uuid4().hex
  assert send(envelope(v,'invoke',endpoint=endpoint,requestId=request,expectedRevision=v['revision'],input=args))['ok']
  if endpoint=='helperCommon':
   for _ in range(200):
    reply=send(envelope(v,'update'))
    if not reply['ok']:
     assert reply['error']['code']=='scope_changed',reply;result=reply;break
    time.sleep(.01)
   else:raise AssertionError('Helper scope did not change')
  else:result,_=settle(v,request)
  assert result['ok']==ok,result;assert send(envelope(v,'dispose'))['ok'];return result
 def select_score():
  page.locator('#nav').click();page.locator('.nav-menu button').filter(has_text='개념').first.click();expect(page.locator('#nav')).to_be_enabled();page.locator('#nav').click();page.locator('[data-id="Example.ButtonGame::Score"]').click();expect(page.locator('[data-schema-field="initial"]')).to_be_visible(timeout=30000)
  page.locator('.window[data-key="schema"] [data-close]').click()
 select_score()
 invoke('customProposal',{'target':'Example.ButtonGame::Score','commandID':'no-chief','text':'must refuse'},False)
 assert not list(project.glob('.confectory/ai-development/augment.json'))
 page.locator('#add-helper').click();page.locator('[data-recruit="global"]').click();expect(page.locator('#helper-list')).to_contain_text('main-helper');page.locator('#helper-list button').click();expect(page.locator('#helper-summary')).to_contain_text('main-helper',timeout=30000);page.locator('.modal [data-close]').click()
 page.locator('#augment').click();expect(page.locator('.augment-overlay')).to_be_visible();assert state()['planningOwnerAvailable'];assert not state()['aiOwnerAvailable'];assert state()['connection'] is None
 page.locator('[data-custom-propose]').click();page.locator('[data-custom-text]').fill('Explain score feedback before implementation');page.locator('.modal button[type="submit"]').click();expect(page.locator('[data-custom-proposals]')).to_contain_text('Explain score feedback before implementation',timeout=30000)
 expect(page.locator('[data-custom-propose]')).to_be_in_viewport();page.screenshot(path='/tmp/confectory-v424-custom-card.png',full_page=True)
 first=state();assert first['aiPreview'] is None;assert first['augment']['cards']==[];assert len(first['augment']['customCards'])==1;assert first['workers']==[];assert first['augment']['customCards'][0]['targets']==['Example.ButtonGame::Score']
 persisted=project/'.confectory/ai-development/augment.json';assert persisted.is_file();assert (project/'Score.celem').read_bytes()==initial
 # Domain idempotency holds even across independent public invocation envelopes.
 args={'target':'Example.ButtonGame::Score','commandID':'owned-repeat','text':'Second explicit local direction'}
 invoke('customProposal',args);saved=persisted.read_bytes();invoke('customProposal',args);assert persisted.read_bytes()==saved
 invoke('customProposal',dict(args,text='conflicting identity'),False);assert persisted.read_bytes()==saved
 invoke('customProposal',dict(args,commandID='foreign-target',target='Other.Project::Foreign'),False);assert persisted.read_bytes()==saved
 invoke('skipProposals',{'commandID':'no-generated-batch','batch':'old-batch','text':'stale UI'},False);assert persisted.read_bytes()==saved
 page.locator('.augment-overlay [data-close]').click();page.locator('#augment').click();expect(page.locator('[data-custom-proposals] article')).to_have_count(2)
 card=first['augment']['customCards'][0]['id'];page.locator('[data-card="'+card+'"]').click();expect(page.locator('#worker-summary button')).to_have_count(1,timeout=30000)
 selected=state();assert selected['workers'][0]['status']=='ready';assert not selected['aiOwnerAvailable'];worker=selected['workers'][0]['id'];invoke('selectCard',{'card':card});assert len(state()['workers'])==1
 # Archive is durable and leaves the selected ordinary task intact.
 page.locator('[data-custom-discard="'+card+'"]').click();expect(page.locator('[data-custom-proposals] article')).to_have_count(1,timeout=30000);assert state()['workers'][0]['id']==worker
 invoke('selectCard',{'card':card},False);assert state()['workers'][0]['status']=='ready';assert (project/'Score.celem').read_bytes()==initial
 page.locator('.augment-overlay [data-close]').click();restart();select_score();page.locator('#augment').click();expect(page.locator('[data-custom-proposals] article')).to_have_count(1,timeout=30000)
 restored=state();assert restored['planningOwnerAvailable'] and not restored['aiOwnerAvailable'];assert len(restored['workers'])==1;assert restored['workers'][0]['id']==worker;assert restored['workers'][0]['status']=='ready';assert restored['augment']['customCards'][0]['summary']=='Second explicit local direction';assert restored['aiPreview'] is None;assert restored['aiState']!='running'
 # Explicitly binding the retained local task opens a fresh, unchecked review; it dispatches nothing.
 from owned_responses import OwnedResponses
 owned=OwnedResponses(None)
 try:
  page.locator('.augment-overlay [data-close]').click();page.locator('.home-side [data-helper]').filter(has_text='main-helper').click();page.locator('.participant-expanded-card [data-worker]').click();expect(page.locator('#worker-prepare')).to_be_disabled()
  page.locator('#add-agent').click();setup=page.get_by_role('dialog',name='사용할 AI',exact=True);setup.get_by_role('button',name='OpenAI Responses',exact=True).click()
  for name,value in [('model','owned-local-plan-fixture'),('endpoint',owned.endpoint),('credentialReference','')]:setup.locator('[data-connection-field="'+name+'"]').fill(value)
  setup.locator('[data-connection-save]').click();expect(setup.locator('[data-connection-result]')).to_contain_text('설정 초안을 저장',timeout=30000);setup.locator('[data-connection-use]').click();expect(page.locator('#status')).to_contain_text('설정 선택됨',timeout=30000);setup.locator('[data-connection-cancel]').click()
  expect(page.locator('#worker-prepare')).to_be_enabled(timeout=30000);page.locator('#worker-prepare').click();expect(page.locator('#ai-start')).to_be_disabled(timeout=30000)
  pending=state();assert pending['aiPreview']['kind']=='worker' and pending['aiPreview']['approvals']=={};assert pending['aiOwnerAvailable'];assert pending['workers'][0]['id']==worker;assert owned.requests==[]
  invoke('startAI',{'token':pending['aiPreview']['token']},False);assert owned.requests==[]
  page.locator('#cancel-preview').click();assert owned.requests==[] and not owned.errors;assert state()['workers'][0]['status']=='ready';page.locator('.window[data-key="worker"] [data-close]').click();page.locator('#augment').click()
  # A later draft revision invalidates selection; restoring equal text does not restore its revision.
  page.locator('.augment-overlay [data-close]').click();invoke('schema',{'id':'Example.ButtonGame::Score'});fresh=state();invoke('editDescription',{'id':'Example.ButtonGame::Score','revision':fresh['draft']['revision'],'value':'changed after custom capture'});page.locator('#augment').click();expect(page.locator('[data-custom-proposals]')).to_contain_text('stale-proposal',timeout=30000)
  stale=state()['augment']['customCards'][0];invoke('selectCard',{'card':stale['id']},False);assert len(state()['workers'])==1
  # A changed Helper/common-memory scope cannot select or append through the retained chief owner.
  invoke('customProposal',{'target':'Example.ButtonGame::Score','commandID':'fresh-before-scope-change','text':'Fresh revision, old Helper scope'})
  candidate=state()['augment']['customCards'][-1]['id'];saved=persisted.read_bytes();invoke('helperCommon',{'enabled':True},False)
  assert state()['allowCommon'] is True and state()['augment']['canCustom'] is False
  invoke('selectCard',{'card':candidate},False);invoke('customProposal',{'target':'Example.ButtonGame::Score','commandID':'changed-helper','text':'must refuse'},False);assert persisted.read_bytes()==saved
  # A fresh real provider owner pins the new policy; only explicit approvals reach our owned HTTP fixture.
  invoke('prepareAI',{'kind':'proposals','target':'Example.ButtonGame::Score','message':'Owned fixture proposals after explicit policy renewal'})
  preview=state()['aiPreview'];assert preview and preview['approvals']=={};assert owned.requests==[]
  for permission in ['contentApproved','usageApproved']:invoke('permission',{'token':preview['token'],'id':permission,'approved':True})
  invoke('startAI',{'token':preview['token']})
  deadline=time.monotonic()+15
  while time.monotonic()<deadline:
   generated=state()
   if len(generated['augment']['cards'])==3:break
   time.sleep(.05)
  assert len(generated['augment']['cards'])==3 and len(owned.requests)==1 and not owned.errors
  invoke('selectCard',{'card':generated['augment']['cards'][0]['id']});assert len(state()['workers'])==2;assert all(w['status']=='ready' for w in state()['workers']);assert (project/'Score.celem').read_bytes()==initial and (project/'project.cpack').read_bytes()==manifest
  selected=state();new_task=selected['selectedWorkerId'];assert new_task!=worker
  overlay=page.locator('.augment-overlay [data-close]')
  if overlay.count():overlay.click()
  if not page.locator('.participant-expanded-card[data-helper-id="main-helper"]').count():page.locator('.home-side [data-helper="main-helper"]').first.click()
  page.locator('.participant-expanded-card [data-worker="'+new_task+'"]').click();expect(page.locator('#worker-cancel-ready')).to_be_enabled(timeout=30000)
  import json
  before_commands=set(json.loads(persisted.read_text())['commands']);page.locator('#worker-cancel-ready').click();expect(page.locator('.window[data-key="worker"]')).to_contain_text('cancelled',timeout=30000)
  assert {w['id']:w['status'] for w in state()['workers']}=={worker:'ready',new_task:'cancelled'};assert len(owned.requests)==1
  command=(set(json.loads(persisted.read_text())['commands'])-before_commands).pop();task_journal=project/'.confectory/ai-development/tasks.json';saved_cancel=(persisted.read_bytes(),task_journal.read_bytes());invoke('cancelReadyWorker',{'task':new_task,'commandID':command,'reason':'Explicitly cancelled before execution'});assert (persisted.read_bytes(),task_journal.read_bytes())==saved_cancel
  page.locator('.window[data-key="worker"] [data-close]').click()
  # The public projection stays bounded while all persisted proposals remain pageable.
  for index in range(33):invoke('customProposal',{'target':'Example.ButtonGame::Score','commandID':'owned-page-'+str(index),'text':'Preserved page proposal '+str(index)})
  latest=state()['augment'];assert latest['customCount']==35 and latest['customPage']==0 and len(latest['customCards'])==32;assert latest['customCards'][-1]['summary']=='Preserved page proposal 32'
  saved_page=persisted.read_bytes();invoke('customProposalPage',{'page':1});older=state()['augment'];assert older['customPage']==1 and len(older['customCards'])==3 and any(card['summary']=='Second explicit local direction' for card in older['customCards']);assert persisted.read_bytes()==saved_page;invoke('customProposalPage',{'page':8},False);assert persisted.read_bytes()==saved_page
  restart();select_score();page.locator('#augment').click();expect(page.locator('[data-custom-proposals]')).to_contain_text('35',timeout=30000);restored=state();assert {w['id']:w['status'] for w in restored['workers']}=={worker:'ready',new_task:'cancelled'};assert not restored['aiOwnerAvailable'];assert len(owned.requests)==1;assert (project/'Score.celem').read_bytes()==initial and (project/'project.cpack').read_bytes()==manifest
  page.screenshot(path='/tmp/confectory-v424-local-augment.png',full_page=True)
  print('PASS v424 local custom proposal: actual chief/scope/idempotency/CAS journal; archive/task/restart/stale fences; no real account/model or source writes; explicit fresh-policy owned provider fixture',flush=True)
 finally:owned.close()
