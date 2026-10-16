"""Ordinary Home node assignments: no account, provider activation or generated response."""
import json,uuid,time,re
from playwright.sync_api import expect

def verify_node_tasks(page,project,mount,send,envelope,settle,restart):
 files={p:p.read_bytes() for p in project.iterdir() if p.is_file()};node='Example.ButtonGame::NodeValueBody/body:common/node:calculate';graph='Example.ButtonGame::NodeValueBody/body:common'
 def state():
  v=mount();s=v['state'];assert send(envelope(v,'dispose'))['ok'];return s
 def invoke(endpoint,args,ok=True):
  v=mount();request=uuid.uuid4().hex;assert send(envelope(v,'invoke',endpoint=endpoint,requestId=request,expectedRevision=v['revision'],input=args))['ok'];result,_=settle(v,request);assert result['ok']==ok,result;assert send(envelope(v,'dispose'))['ok'];return result.get('result')
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=120000)
 def nav():
  if not page.locator('.nav-menu').count():page.locator('#nav').click()
  page.locator('.nav-menu').get_by_role('button',name='Blueprint 노드 Task',exact=True).click();ready()
 def panel():return page.locator('.window[data-key="node-tasks"]')
 nav();expect(panel().locator('[data-node-task-id]')).to_have_count(1);panel().locator('[data-node-task-id]').click();expect(panel().locator('[data-node-task-assign]')).to_be_disabled();assert not state()['planningOwnerAvailable']
 panel().locator('[data-node-task-reason]').fill('Inspect retained node semantics before implementation');panel().locator('[data-node-task-inspect]').click();ready();expect(page.locator('#status')).to_contain_text('작업 사본과 입력은 유지');expect(panel().locator('[data-node-task-reason]')).to_have_value('Inspect retained node semantics before implementation');assert not state()['planningOwnerAvailable']
 page.locator('#add-helper').click();page.locator('[data-recruit="global"]').click();expect(page.locator('#helper-list')).to_contain_text('main-helper');page.locator('#helper-list button').click();expect(page.locator('#helper-summary')).to_contain_text('main-helper',timeout=30000);page.locator('.modal [data-close]').click()
 panel().locator('[data-node-task-inspect]').click();ready();expect(panel().locator('[data-node-task-plan]')).to_contain_text('Add four to the input');expect(panel().locator('[data-node-task-assign]')).to_be_enabled();assert state()['planningOwnerAvailable'] and not state()['aiOwnerAvailable'] and state()['connection'] is None
 # A peer draft definition changes after inspection. The displayed plan must not assign it.
 invoke('select',{'id':graph});unit=state()['draft'];doc=json.loads(unit['text']);doc['nodes'][0]['intent']='Add four with explicit scoped verification';invoke('editDraft',{'id':graph,'text':json.dumps(doc),'revision':unit['revision']})
 panel().locator('[data-node-task-assign]').click();ready();expect(page.locator('#status')).to_contain_text('작업 사본과 입력은 유지');assert not state()['workers'];expect(panel().locator('[data-node-task-reason]')).to_have_value('Inspect retained node semantics before implementation')
 panel().locator('[data-node-task-inspect]').click();ready();expect(panel().locator('[data-node-task-plan]')).to_contain_text('Add four with explicit scoped verification')
 # Unsent raw input is a separate intent and cannot be silently included in a node assignment.
 invoke('select',{'id':node});original_node=state()['draft']['text']
 if not page.locator('.nav-menu').count():page.locator('#nav').click()
 page.locator('.nav-menu').get_by_role('button',name='개념',exact=True).click();ready()
 if page.locator('.nav-menu').count():page.locator('#nav').click()
 page.locator('#browser-actions').click();page.locator('#advanced-source').click();ready();expect(page.locator('#source')).to_be_visible();page.locator('#source').fill(original_node+'\n')
 source_browser=page.locator('.window[data-key="browser"]');source_browser.locator('.caption').click(position={'x':100,'y':12});source_browser.locator('[data-close]').click()
 panel().locator('[data-node-task-assign]').click();ready();expect(page.locator('#status')).to_contain_text('미적용 입력');expect(page.locator('#source')).to_have_value(original_node+'\n');assert not state()['workers'] and state()['draft']['text']==original_node
 raw=page.locator('.window[data-key="source"]');raw.locator('.window-title').click(position={'x':400,'y':12});page.locator('#source').fill(original_node);page.locator('#apply').click();ready();raw.locator('[data-close]').click();panel().locator('[data-node-task-assign]').click();ready()
 worker=page.locator('.window[data-key="worker"]');expect(worker).to_be_visible();expect(worker.locator('pre').first).to_contain_text(node);expect(worker.locator('#worker-prepare')).to_be_disabled();expect(worker.locator('#worker-cancel-ready')).to_be_enabled();first=state();assert len(first['workers'])==1 and first['workers'][0]['status']=='ready' and first['workers'][0]['taskKind']=='blueprint-node' and first['workers'][0]['assignedNode']==node and first['aiPreview'] is None and not first['aiOwnerAvailable'];task=first['workers'][0]['id']
 worker.locator('[data-close]').click();panel().locator('[data-node-task-inspect]').click();ready();page.screenshot(path='/tmp/confectory-v424-node-tasks.png',full_page=True)
 for button in panel().locator('[data-node-task-read],[data-node-task-inspect],[data-node-task-assign]').all():
  box=button.bounding_box();dock=page.locator('#dock').bounding_box();assert box and (box['x']+box['width']<=dock['x'] or box['y']+box['height']<=dock['y']),(box,dock)
 invoke('saveDraft',{});page.evaluate('()=>globalThis.confectoryFlushPresentation()');restart();expect(panel()).to_be_visible(timeout=30000);expect(panel().locator('[data-node-task-plan]')).not_to_contain_text('assignmentHash');expect(panel().locator('[data-node-task-assign]')).to_be_disabled();expect(panel().locator('[data-node-task-reason]')).to_have_value('Inspect retained node semantics before implementation')
 panel().locator('[data-node-task-read]').click();ready();expect(panel().locator('[data-node-task-id]')).to_have_count(1);panel().locator('[data-node-task-inspect]').click();ready();restored=state();assert len(restored['workers'])==1 and restored['workers'][0]['id']==task and restored['workers'][0]['status']=='ready' and restored['aiPreview'] is None and not restored['aiOwnerAvailable']
 # Existing ready-only cancellation retains the immutable node specification and starts no Agent.
 page.locator('.home-side [data-helper]').filter(has_text='main-helper').click();page.locator('.participant-expanded-card [data-worker]').click();expect(page.locator('#worker-cancel-ready')).to_be_enabled();page.locator('#worker-cancel-ready').click();ready();assert state()['workers'][0]['status']=='cancelled' and not state()['aiOwnerAvailable']
 # Exercise the production Responses provider over an owned loopback server after exact UI approval.
 from owned_responses import OwnedResponses
 owned=OwnedResponses(node)
 try:
  worker=page.locator('.window[data-key="worker"]');expect(worker.locator('#worker-recover')).to_be_enabled();worker.locator('#worker-recover').click();ready();expect(panel().locator('[data-node-task-assign]')).to_be_disabled();assert len(state()['workers'])==1;panel().locator('[data-node-task-inspect]').click();ready();panel().locator('[data-node-task-assign]').click();ready();second=state()['selectedWorkerId'];assert second!=task;expect(worker).to_have_class(re.compile(r'.*\bactive\b.*'));panel().locator('[data-close]').click()
  page.locator('#add-agent').click();setup=page.get_by_role('dialog',name='사용할 AI',exact=True);setup.get_by_role('button',name='OpenAI Responses',exact=True).click()
  for name,value in [('model','owned-node-fixture'),('endpoint',owned.endpoint),('credentialReference','')]:setup.locator('[data-connection-field="'+name+'"]').fill(value)
  setup.locator('[data-connection-save]').click();expect(setup.locator('[data-connection-result]')).to_contain_text('설정 초안을 저장',timeout=30000);setup.locator('[data-connection-use]').click();expect(page.locator('#status')).to_contain_text('설정 선택됨',timeout=30000);setup.locator('[data-connection-cancel]').click()
  worker.locator('#worker-prepare').click();preview=page.locator('.window[data-key="ai-preview"]');expect(preview.locator('[data-node-approval]')).to_contain_text(node);expect(preview.locator('[data-node-approval]')).to_contain_text('Add four with explicit scoped verification');expect(preview.locator('#ai-start')).to_be_disabled();assert not owned.requests
  invoke('startAI',{'token':state()['aiPreview']['token']},False);assert not owned.requests
  for checkbox in preview.locator('[data-permission]').all():checkbox.check();ready()
  expect(preview.locator('#ai-start')).to_be_enabled();preview.locator('#ai-start').click();ready()
  deadline=time.monotonic()+45
  while time.monotonic()<deadline:
   current=state();row=next(w for w in current['workers'] if w['id']==second)
   if row['status'] not in ['ready','running','dispatching']:break
   time.sleep(.1)
  assert row['status']=='awaiting-verification' and not owned.errors and len(owned.requests)>=3,row
  assert row['changedIds']==[node] and graph in row['supportingDraftIds'];assert (project/'calculate.node.json').read_bytes()==files[project/'calculate.node.json']
  expect(worker.locator('[data-worker-source="'+node+'"]')).to_be_visible(timeout=30000);worker.locator('[data-worker-source="'+node+'"]').check();worker.locator('[data-worker-source="'+graph+'"]').check();worker.locator('#worker-review').click();review=page.locator('.window[data-key="worker-review"]');expect(review.locator('#worker-adopt')).to_be_enabled(timeout=180000);ready();expect(review).to_contain_text('사용자가 별도로 검토')
  review.locator('#worker-goal-evidence').fill('Owned HTTP fixture implemented the assigned node. The supporting graph intent is separately reviewed here. Runtime behavior is covered by the separate public engine consumer; this UI gate does not launch the project.')
  page.screenshot(path='/tmp/confectory-v480-node-task-review.png',full_page=True);review.locator('#worker-adopt').click();ready();assert next(w for w in state()['workers'] if w['id']==second)['status']=='completed'
  assert json.loads((project/'calculate.node.json').read_text())['source']=='return value + 5;';assert json.loads((project/'node-value.graph.json').read_text())['nodes'][0]['intent']=='Add four with explicit scoped verification'
  receipt=list((project/'.confectory/ai-development/adoption-records').glob('*.json'));assert len(receipt)==1;record=json.loads(receipt[0].read_text())['records'][-1];assert record['taskSourceIDs']==[node] and record['supportingSourceIDs']==[graph]
  count=len(owned.requests);page.evaluate('()=>globalThis.confectoryFlushPresentation()');restart();assert len(owned.requests)==count and not owned.errors
 finally:owned.close()
 for path,content in files.items():
  if path.name not in ['calculate.node.json','node-value.graph.json']:assert path.read_bytes()==content,path.name
 print('PASS actual node Task plan: owned list, explicit chief, stale definition refusal, local assignment, distinct scoped Worker, pending reason/cold presentation, durable ready history/cancellation, exact approval, real loopback scoped tools, separate supporting graph review, compiler adoption and cold no replay',flush=True)
