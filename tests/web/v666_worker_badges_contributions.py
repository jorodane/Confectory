"""Badge provenance from the real scoped HTTP/tool flow, using an owned loopback fixture."""
import hashlib,json,time,uuid
from playwright.sync_api import sync_playwright,expect
from owned_responses import OwnedResponses
import v536_wide_mixed as f
node=f.n+'SlotBody/body:common/node:body';graph=f.n+'SlotBody/body:common'
owned=OwnedResponses(node,'slotCount=amount+2;slotReady=true;return amount+4;')
def invoke(endpoint,**body):
 for _ in range(4):
  v=f.mount();rid=uuid.uuid4().hex
  try:
   assert f.raw(dict(op='invoke',view=v['view'],scope=v['scope'],expectedRevision=v['revision'],requestId=rid,endpoint=endpoint,input=body))['ok']
   deadline=time.monotonic()+60
   while time.monotonic()<deadline:
    u=f.raw(dict(op='update',view=v['view'],scope=v['scope']));rows=[r for r in u.get('results',[]) if r['requestId']==rid]
    if rows:break
    if u.get('error',{}).get('code')=='scope_changed':
     if endpoint=='projectHelpers' and f.state()['projectHelperIds']==body['helpers']:return {}
     raise AssertionError((endpoint,'scope changed without outcome'))
    time.sleep(.01)
   assert rows,(endpoint,'result deadline')
   if rows[0].get('error',{}).get('code')=='stale_revision':continue
   assert rows[0]['ok'],rows;return rows[0]['result']
  finally:f.raw(dict(op='dispose',view=v['view']))
 raise AssertionError('stale revision admission')
try:
 f.start(0)
 with sync_playwright() as pw:
  expect.set_options(timeout=30000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size(dict(width=1900,height=1400))
  f.page.locator('#add-agent').click();c=f.page.get_by_role('dialog',name='Agent 추가',exact=True);c.get_by_role('button',name='OpenAI Responses',exact=True).click()
  for key,value in [('model','owned-badge-provenance'),('endpoint',owned.endpoint),('credentialReference','')]:c.locator('[data-connection-field="'+key+'"]').fill(value)
  c.locator('[data-agent-register]').click();expect(c.locator('[data-agent-registration-state]')).to_contain_text('Agent 등록됨');c.locator('[data-connection-cancel]').click()
  chief=invoke('helperGlobal',action='create',creationId=uuid.uuid4().hex,name='변경 검증 도우미',personality='owned protocol fixture',speciality='fixture',agent='Confectory.Agent.Responses::Connection')['helper'];invoke('projectHelpers',helpers=[chief]);f.page.reload();f.idle();invoke('bindHelperAgent',helper=chief)
  invoke('select',id=graph);u=f.state()['draft'];doc=json.loads(u['text']);doc['nodes'][0]['intent']+=' (사용자가 별도로 편집한 지원 초안)';invoke('editDraft',id=graph,revision=u['revision'],text=json.dumps(doc));invoke('saveDraft')
  plan=invoke('nodeTask',action='inspect',node=node);task=invoke('nodeTask',action='assign',node=node,assignmentHash=plan['assignmentHash'],commandID=uuid.uuid4().hex,rationale='실제 출처 배지 검증');invoke('prepareWorker',task=task['task']);preview=f.state()['aiPreview'];assert preview and preview['approvals']=={} and not owned.requests;invoke('cancelPreview');assert not owned.requests;f.checked('실제 배정·권한 검토 취소와 배지 조회는 소스나 Agent 요청을 실행하지 않는다')
  invoke('prepareWorker',task=task['task']);preview=f.state()['aiPreview'];f.invoke('startAI',dict(token=preview['token']),False);assert not owned.requests
  for requirement in preview['requirements']:invoke('permission',token=preview['token'],id=requirement['id'],approved=True)
  invoke('startAI',token=preview['token']);deadline=time.monotonic()+40
  while time.monotonic()<deadline:
   s=f.state();worker=next(row for row in s['workers'] if row['id']==task['task'])
   if worker['status']=='awaiting-verification' and any(node in row['changedIds'] for row in s['assignmentWorkers']):break
   time.sleep(.05)
  assert not owned.errors and len(owned.requests)>=3,(owned.errors,owned.requests)
  assert worker['status']=='awaiting-verification',worker
  badge=next(row for row in s['assignmentWorkers'] if row['ownerHelper']==chief);assert badge['changedIds']==[node] and graph in badge['supportingDraftIds'],badge
  f.checked('명시 권한 승인 후 실제 생산 provider/tools가 만든 노드 변경과 사용자 지원 초안의 출처를 별도로 읽는다')
  f.page.locator('#workspace').click(button='right',position=dict(x=1300,y=200));f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=feature]').click();card=b.locator('[data-object="'+f.n+'Slot'+'"] [data-assigned-helper="'+chief+'"]');expect(card).to_be_visible();expect(card).to_have_attribute('title',__import__('re').compile('.*미반영 변경.*지원 초안.*'));f.page.screenshot(path=str(f.case/'real-contribution-badges.png'),full_page=True)
  for relative,content in f.original.items():assert (f.project/relative).read_bytes()==content,relative
  assert s['review'] is None and not list(f.project.glob('.confectory/ai-development/**/adoption-records/*.json'))
  count=len(owned.requests);f.page.wait_for_timeout(1200);f.state();assert len(owned.requests)==count;assert not f.errors and not f.external,(f.errors,f.external);f.checked('실제 카드 배지는 미반영 변경/지원 초안을 구분하고 자동 Review·Confirm·채택·추가 모델 요청을 수행하지 않는다')
  invoke('reviewWorker',task=task['task'],ids=[node,graph],target='portable');review=f.state()['review'];assert review['status']=='ready',review
  invoke('adoptWorker',task=task['task'],token=review['token'],ids=[node,graph],goalEvidence='Owned loopback fixture changed only the assigned node. This source adoption explicitly includes the separately edited supporting graph. Compiler validation is verified; project execution and domain outcome are not claimed.')
  deadline=time.monotonic()+5
  while time.monotonic()<deadline:
   s=f.state();badge=next(row for row in s['assignmentWorkers'] if row['ownerHelper']==chief)
   if badge['status']=='completed' and badge['changedIds']==[]:break
   time.sleep(.05)
  assert badge['status']=='completed' and badge['changedIds']==[] and badge['supportingDraftIds']==[],badge;expect(b.locator('[data-object="'+f.n+'Slot'+'"] [data-assigned-helper]')).to_have_count(0)
  assert json.loads((f.project/'Slot.node.json').read_text())['source']==owned.node_source
  for relative,content in f.original.items():
   if relative not in ['Slot.node.json','Slot.graph.json']:assert (f.project/relative).read_bytes()==content,relative
  assert len(list(f.project.glob('.confectory/ai-development/**/adoption-records/*.json')))==1 and len(owned.requests)==count
  f.checked('명시 source Review/컴파일 Confirm·채택 후 완료/clean 상태로 배지를 제거하고 원계약·부모·다른 본문 및 모델 요청 수를 보존한다')
  f.browser.close()
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2));(f.case/'owned-http-errors.json').write_text(json.dumps(owned.errors));f.stop();owned.close()
