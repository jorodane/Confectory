"""Actual local Task assignment badges; no inference, accounts or project execution."""
import hashlib,json,pathlib,shutil,time,uuid
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
agent='Confectory.Agent.Responses::Connection';node=f.n+'SlotBody/body:common/node:body'
source={p:p.read_bytes() for p in f.project.iterdir() if p.is_file()}
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
     raise AssertionError((endpoint,'scope changed without evidence'))
    time.sleep(.01)
   assert rows,(endpoint,'bounded response deadline')
   if rows[0].get('error',{}).get('code')=='stale_revision':continue
   assert rows[0]['ok'],rows;return rows[0]['result']
  finally:f.raw(dict(op='dispose',view=v['view']))
 raise AssertionError('stale admission attempts')

def wait_badges(count):
 for _ in range(150):
  s=f.state()
  if len(s.get('assignmentWorkers',[]))==count:return s
  time.sleep(.05)
 raise AssertionError(('badge projection deadline',s.get('assignmentWorkersStatus'),s.get('assignmentWorkers')))
def original():assert all(p.read_bytes()==v for p,v in source.items())
def browser():
 f.idle();b=f.page.locator('.window[data-key^="browser:project:"]')
 if not b.is_visible():
  f.page.locator('#workspace').click(button='right',position=dict(x=1300,y=200));f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click()
 b.locator('[data-tab=feature]').click();f.idle();return b

def restart(i,project=None):
 f.pending();f.page.close();f.stop()
 if project:f.env['CONFECTORY_WEB_PROJECT']=str(project/'project.cproj')
 f.start(i);f.page=f.setup();f.page.set_viewport_size(dict(width=1900,height=1400));f.idle()

try:
 f.start(0)
 with sync_playwright() as pw:
  expect.set_options(timeout=30000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size(dict(width=1900,height=1400));s=wait_badges(0);assert not (f.project/'.confectory/ai-development').exists();original();f.checked('빈 프로젝트 조회는 Task 저널·실행 owner·가짜 배지를 만들지 않는다')
  f.page.locator('#add-agent').click();c=f.page.get_by_role('dialog',name='Agent 추가',exact=True);c.get_by_role('button',name='OpenAI Responses',exact=True).click()
  for key,value in [('model','owned-badge-no-inference'),('endpoint','http://127.0.0.1:9'),('credentialReference','')]:c.locator('[data-connection-field="'+key+'"]').fill(value)
  c.locator('[data-agent-register]').click();expect(c.locator('[data-agent-registration-state]')).to_contain_text('Agent 등록됨');c.locator('[data-connection-cancel]').click()
  def recruit(name):return invoke('helperGlobal',action='create',creationId=uuid.uuid4().hex,name=name,personality='fixture local profile',speciality='fixture',agent=agent)['helper']
  chief=recruit('배정 도우미');other=recruit('두 번째 도우미');invoke('projectHelpers',helpers=[chief]);f.page.reload();f.idle()
  plan=invoke('nodeTask',action='inspect',node=node);task=invoke('nodeTask',action='assign',node=node,assignmentHash=plan['assignmentHash'],commandID=uuid.uuid4().hex,rationale='배지 검증용 명시적 노드 배정');s=wait_badges(1);assert not s['aiOwnerAvailable'] and s['aiPreview'] is None;assert s['assignmentWorkers'][0]['ownerHelper']==chief;original();f.checked('기존 실제 노드 배정 API의 ready Task를 표시하며 추론·실행·권한 승인을 시작하지 않는다')
  b=browser();(f.case/'state-before-card.json').write_text(json.dumps(f.state(),ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'before-card.png'),full_page=True);card=b.locator('[data-object="'+f.n+'Slot'+'"]');expect(card.locator('[data-assigned-helper="'+chief+'"]')).to_be_visible();expect(b.locator('[data-browser-workers] [data-assigned-helper="'+chief+'"]')).to_be_visible()
  card.press('F2');f.idle();header=f.page.locator('.window[data-key=declaration] [data-object-workers]');expect(header.locator('[data-assigned-helper="'+chief+'"]')).to_be_visible();f.page.screenshot(path=str(f.case/'badge-card-header.png'),full_page=True);f.checked('실제 provide 연결로 구현 노드 배정을 함수 카드·브라우저 헤더·함수 헤더에 표시한다')
  # Cold display must read the record without recovery writes or opening an execution owner.
  task_path=f.project/'.confectory/ai-development/helpers'/hashlib.sha256(chief.encode()).hexdigest()[:16]/'tasks.json';assert task_path.is_file();saved=task_path.read_bytes();restart(1);s=wait_badges(1);assert not s['planningOwnerAvailable'] and task_path.read_bytes()==saved;expect(browser().locator('[data-object="'+f.n+'Slot'+'"] [data-assigned-helper="'+chief+'"]')).to_be_visible();f.checked('재시작 후 배지는 저장 기록을 읽되 Task 세션/중단 상태 쓰기·실행 재생 없이 나타난다')
  # An ordinary task uses its captured semantic target IDs, independent of node syntax.
  invoke('nodeTask',action='inspect',node=node)
  invoke('customProposal',target=f.n+'SlotBody',commandID=uuid.uuid4().hex,text='동일 도우미의 추가 명시적 작업')
  card_id=f.state()['augment']['customCards'][-1]['id'];invoke('selectCard',card=card_id);s=wait_badges(2);assert s['assignmentWorkers'][1]['assignedSourceIds'] or s['assignmentWorkers'][0]['assignedSourceIds'];b=browser()
  expect(b.locator('[data-tree-key=root] [data-assigned-helper="'+chief+'"]')).to_have_count(1);expect(b.locator('[data-tree-key=root] .worker-count')).to_have_count(0);f.checked('실제 일반 Task의 semantic target과 노드 Task를 결합하되 폴더 수는 Task 수가 아닌 고유 도우미 수다')
  f.pending();invoke('projectHelpers',helpers=[other,chief]);f.page.reload();f.idle();restart(11);plan=invoke('nodeTask',action='inspect',node=node);other_task=invoke('nodeTask',action='assign',node=node,assignmentHash=plan['assignmentHash'],commandID=uuid.uuid4().hex,rationale='두 번째 도우미의 명시적 배정');wait_badges(3);b=browser()
  count=b.locator('[data-tree-key=root] .worker-count');expect(count).to_have_text('2');count.click();popup=f.page.get_by_role('dialog',name='2명의 작업자',exact=True);expect(popup.locator('[data-assigned-helper]')).to_have_count(2);count.press('Escape');expect(popup).to_have_count(0);expect(count).to_be_focused();count.click();f.page.locator('#chat-input').click();expect(popup).to_have_count(0)
  for density in [0,100,40]:
   b.locator('[data-density="'+str(density)+'"]').click();f.idle();expect(b.locator('[data-object="'+f.n+'Slot'+'"] .worker-count')).to_have_text('2')
  f.page.screenshot(path=str(f.case/'two-helpers-folders.png'),full_page=True);f.checked('도우미별 저장 경로와 현재 owner를 결합하고 원본 폴더 count/팝오버·Escape/바깥 클릭 및 Preview/Compact/Data를 검증한다')
  # Source editing remains private; badges do not save or erase input.
  invoke('openEditorView',view='1',id=f.n+'Slot',viewMode='declaration');f.idle();panel=f.page.locator('.window[data-key=editor-1]');expect(panel.locator('[data-object-workers] [data-assigned-helper]')).to_have_count(2)
  description=panel.locator('[data-decl-property=description]');description.fill('배지 갱신 중 보존할 설명 😀');description.press('Tab');f.pending();held=f.pending();time.sleep(1.1);f.state();expect(description).to_have_value('배지 갱신 중 보존할 설명 😀');assert f.pending()==held;original();f.checked('독립 함수 헤더의 두 배지와 늦은 private 설명 입력을 함께 유지하며 조회가 저장/CAS/확정을 실행하지 않는다')
  invoke('selectWorker',task=other_task['task']);invoke('cancelReadyWorker',task=other_task['task'],commandID=uuid.uuid4().hex,reason='명시 배정 취소');
  deadline=time.monotonic()+5
  while time.monotonic()<deadline:
   s=f.state()
   if next(r for r in s['assignmentWorkers'] if r['ownerHelper']==other)['status']=='cancelled':break
   time.sleep(.05)
  assert next(r for r in s['assignmentWorkers'] if r['ownerHelper']==other)['status']=='cancelled';b=browser();expect(b.locator('[data-tree-key=root] .worker-count')).to_have_count(0);expect(b.locator('[data-tree-key=root] [data-assigned-helper]')).to_have_count(1);expect(description).to_have_value('배지 갱신 중 보존할 설명 😀');original();f.checked('기존 명시 취소는 해당 도우미 배지만 제거하며 다른 Task·본문·독립 창 입력을 보존한다')
  # Read failure / unknown owners are never substituted with demo participants.
  restart(2);saved=task_path.read_bytes();document=json.loads(saved);records=document['tasks'];first=next(iter(records));records[first]['status']='running';uncertain=json.dumps(document,ensure_ascii=False).encode();task_path.write_bytes(uncertain)
  for _ in range(100):
   s=f.state()
   if any(r['ownerHelper']==chief and r.get('needsCheck') for r in s['assignmentWorkers']):break
   time.sleep(.05)
  assert any(r['ownerHelper']==chief and r['status']=='interrupted' and r['needsCheck'] for r in s['assignmentWorkers']);assert task_path.read_bytes()==uncertain and not s['planningOwnerAvailable'];b=browser();expect(b.locator('[data-browser-workers] [data-assigned-helper="'+chief+'"]')).to_have_attribute('title',__import__('re').compile('.*확인 필요.*'));f.checked('cold running 기록은 확인 필요로만 표시하며 저널 상태·실행 owner를 바꾸지 않는다')
  for variant in ['project','owner','chief','helper','invalid','link']:
   altered=json.loads(saved)
   if variant=='project':altered['project']='foreign-project'
   elif variant=='owner':altered['owner']='another-user'
   elif variant=='chief':altered['chief']=other
   elif variant=='helper':
    for row in altered['tasks'].values():row['ownerHelper']='PRIVATE-HELPER-CANARY'
   if variant=='link':
    outside=f.case/'outside-tasks.json';outside.write_bytes(saved);task_path.unlink();task_path.symlink_to(outside)
   else:task_path.write_bytes(b'{' if variant=='invalid' else json.dumps(altered).encode())
   deadline=time.monotonic()+5
   while time.monotonic()<deadline:
    s=f.state()
    if not any(row['ownerHelper']==chief for row in s['assignmentWorkers']):break
    time.sleep(.05)
   assert not any(row['ownerHelper']==chief for row in s['assignmentWorkers']),(variant,s['assignmentWorkers']);assert 'PRIVATE-HELPER-CANARY' not in json.dumps(s.get('assignmentWorkers'))
   if variant=='link':assert outside.read_bytes()==saved;task_path.unlink()
   task_path.write_bytes(saved)
   # Observe restoration before trying the next independently rejected journal.
   wait_badges(3)
  f.checked('다른 프로젝트/소유자/chief/비공개 Helper·손상 저널·링크는 실제 조회에서 제외하고 정상 저장 원본과 입력을 보존한다')
  f.page.locator('.brand').click();f.page.wait_for_selector('.home-grid');s=f.state();assert not s['projectId'] and s['assignmentWorkers']==[];assert not f.page.locator('[data-assigned-helper]').count();f.page.locator('[data-enter]').first.click();f.idle();wait_badges(3);f.checked('프로젝트 없음에서는 배지를 비우고 명시 재진입 때 해당 프로젝트의 기록만 복원한다')
  other_project=f.case/'same-name project';shutil.copytree(f.project,other_project,ignore=shutil.ignore_patterns('.confectory','.build'));restart(3,other_project);s=wait_badges(0);assert s['projectId']!=document['project'];assert not f.page.locator('[data-assigned-helper]').count();restart(4,f.project);wait_badges(3);assert task_path.read_bytes()==saved;original();f.checked('같은 이름·같은 선언 ID의 다른 프로젝트 왕복은 배정과 독립 입력을 섞지 않는다')
  assert not f.errors and not f.external,(f.errors,f.external)
  print('B2_FIXTURE '+str(f.case),flush=True)
  f.browser.close()
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2));(f.case/'errors.json').write_text(json.dumps(f.errors));f.stop()
