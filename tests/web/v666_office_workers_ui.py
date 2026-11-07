"""Actual native Worker records and owned loopback provider; no live AI or credentials."""
import hashlib,json,pathlib,shutil,time,uuid,sys,traceback,threading,io
from playwright.sync_api import sync_playwright,expect
from owned_responses import OwnedResponses
import v536_wide_mixed as f
mode=sys.argv[3];live=mode in ['live','io','phase-ui'];checkIO=mode in ['io','io-cold'];ioGates=[threading.Event(),threading.Event()];ioEntered=[threading.Event(),threading.Event()];node=f.n+'SlotBody/body:common/node:body';graph=f.n+'SlotBody/body:common';allowed={};owned=None;gate=threading.Event();entered=threading.Event()
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

def physical():
 for relative,content in f.original.items():assert(f.project/relative).read_bytes()==allowed.get(relative,content),relative
 assert not f.errors and not f.external,(f.errors,f.external)
def office():return f.page.locator('.voxel-office')
def switch(view):f.page.get_by_role('button',name='아이소메트릭 Workspace'if view=='office'else'패널 Workspace',exact=True).click()
def ready():
 expect(f.page.locator('#workspace')).to_have_attribute('data-office-renderer','ready');expect(office()).to_be_visible()
def projected(count):
 expect(office().locator('.office-worker-label[data-native-task]')).to_have_count(count)
 return f.state()['assignmentWorkers']
def status(id,value):
 label=office().locator('.office-worker-label[data-native-task="'+id+'"]');expect(label).to_have_attribute('data-native-status',value);return label
def inspect_current(id):
 f.idle();expect(status(id,'interrupted')).to_contain_text('SlotBody');expect(office().locator('.office-helper-label')).to_contain_text('실제 배정 도우미')
 # The authored menu follows moving actors, so a pointer stability wait is
 # inappropriate. Use its real keyboard controls; no forced click/DOM handler.
 label=status(id,'interrupted');expect(label).to_be_visible();label.focus();label.press('Enter')
 name=office().locator('[data-office-radial-name]');name.focus();name.press('Enter')
 expect(name).to_have_attribute('aria-expanded','true');expect(office().locator('.office-inspector')).to_be_visible();expect(office().locator('.office-inspector')).to_contain_text('실행 확인 필요')
def assign():
 before={row['id']for row in f.state()['assignmentWorkers']};plan=invoke('nodeTask',action='inspect',node=node)
 task=invoke('nodeTask',action='assign',node=node,assignmentHash=plan['assignmentHash'],commandID=uuid.uuid4().hex,rationale='owned 3D observation fixture')
 deadline=time.monotonic()+10
 while time.monotonic()<deadline:
  rows=[r for r in f.state()['assignmentWorkers']if r['id']not in before]
  if rows:return task,rows[0]['id']
  f.page.wait_for_timeout(50)
 raise AssertionError('public native task observation deadline')
def setup_agent(endpoint):
 f.page.locator('#add-agent').click();c=f.page.get_by_role('dialog',name='Agent 추가',exact=True);c.get_by_role('button',name='OpenAI Responses',exact=True).click()
 for key,value in [('model','owned-office-no-live-model'),('endpoint',endpoint),('credentialReference','')]:c.locator('[data-connection-field="'+key+'"]').fill(value)
 c.locator('[data-agent-register]').click();expect(c.locator('[data-agent-registration-state]')).to_contain_text('Agent 등록됨');c.locator('[data-connection-cancel]').click()
 h=invoke('helperGlobal',action='create',creationId=uuid.uuid4().hex,name='실제 배정 도우미',personality='owned fixture',speciality='fixture',agent='Confectory.Agent.Responses::Connection')['helper']
 invoke('projectHelpers',helpers=[h]);f.page.reload();f.idle();return h
def restart(index,project=None):
 f.pending();f.page.close();f.stop()
 if project:f.env['CONFECTORY_WEB_PROJECT']=str(project/'project.cproj')
 f.start(index);f.page=f.setup();f.idle()
def unchanged_journal(path,value):assert path.read_bytes()==value
try:
 if live:
  owned=OwnedResponses(node,'slotCount=amount+2;slotReady=true;return amount+4;');Base=owned.server.RequestHandlerClass
  class Gated(Base):
   def do_POST(self):
    raw=self.rfile.read(int(self.headers['Content-Length']));self.rfile=io.BytesIO(raw);body=json.loads(raw);outputs=[row for row in body['input']if row.get('type')=='function_call_output']
    if checkIO and outputs:
     index=min(len(outputs)-1,1);ioEntered[index].set();assert ioGates[index].wait(timeout=60),'owned IO provider release deadline'
    else:entered.set();assert gate.wait(timeout=60),'owned provider release deadline'
    super().do_POST()
  owned.server.RequestHandlerClass=Gated
 f.start(0)
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']);f.page=f.setup();f.idle()
  try:
   switch('office');ready();projected(0);assert not(f.project/'.confectory/ai-development').exists();physical();f.checked('3D empty read creates no Task owner/journal or demo Helper/Worker')
   switch('editor');chief=setup_agent(owned.endpoint if owned else'http://127.0.0.1:9');switch('office');ready()
   if live:
    invoke('bindHelperAgent',helper=chief);invoke('select',id=graph);u=f.state()['draft'];doc=json.loads(u['text']);doc['nodes'][0]['intent']+=' (owned separately reviewed support input)';invoke('editDraft',id=graph,revision=u['revision'],text=json.dumps(doc));invoke('saveDraft')
   task,id=assign();projected(1);expect(status(id,'ready')).to_contain_text('배정 대기');physical();f.checked('existing explicit native assignment appears with its stable public Worker identity and current project Helper, without dispatch or IO inference')
   f.page.evaluate("()=>window.dispatchEvent(new CustomEvent('confectory:worker-activity',{detail:{projectId:'foreign',helperId:'fake',workerId:'fake',state:'writing'}}))");projected(1);status(id,'ready');physical()
   if live:
    invoke('prepareWorker',task=task['task']);preview=f.state()['aiPreview'];f.invoke('startAI',dict(token=preview['token']),False);assert not entered.is_set()and not owned.requests;invoke('cancelPreview');status(id,'ready');physical();f.checked('3D display grants no execution approval; denied start and explicit preview cancellation preserve assignment/source')
    invoke('prepareWorker',task=task['task']);preview=f.state()['aiPreview']
    for requirement in preview['requirements']:invoke('permission',token=preview['token'],id=requirement['id'],approved=True)
    invoke('startAI',token=preview['token']);assert entered.wait(timeout=10);expect(status(id,'running')).to_contain_text('작업 중');assert not owned.requests
    f.page.evaluate("args=>window.dispatchEvent(new CustomEvent('confectory:worker-activity',{detail:{...args,state:'writing',access:'write'}}))",dict(projectId=f.state()['projectId'],helperId=chief,workerId=id));expect(status(id,'running')).to_contain_text('작업 중');physical();f.checked('actual approved Worker is running while owned HTTP is held; movement/arrival and forged visual events cannot start, finish or relabel it as a write')
    if mode=='phase-ui':
     # UI receipt injection is separate from the native gated-reader test. The
     # actual approved Worker exists, but its owned provider is still held.
     f.page.locator('#chat-input').fill('진행 표시 중 새 입력 보존')
     f.page.evaluate("""args=>{globalThis.__phaseFixture={projectId:args.project,receipt:'c'.repeat(64),ordinal:1,targetId:args.node,kind:'read',phase:'in-progress'};const base=fetch;fetch=async(...a)=>{const response=await base(...a);let p;try{p=await response.clone().json()}catch{return response}let found=false;for(const row of p.state?.assignmentWorkers||[])if(row.id===args.id){row.activeToolIO=__phaseFixture;found=true}return found?new Response(JSON.stringify(p),{status:200,headers:{'Content-Type':'application/json'}}):response;};}""",dict(project=f.state()['projectId'],id=id,node=node))
     expect(status(id,'running')).to_contain_text('읽는 중');assert not owned.requests;physical()
     f.page.evaluate("()=>__phaseFixture={...__phaseFixture,kind:'draft-stage'}");expect(status(id,'running')).to_contain_text('초안 처리 중');physical()
     for bad in [dict(targetId='External::Hidden'),dict(projectId='foreign'),dict(receipt='bad')]:
      f.page.evaluate('bad=>__phaseFixture={...__phaseFixture,...bad}',bad);expect(status(id,'running')).not_to_contain_text('초안 처리 중');f.page.evaluate("args=>__phaseFixture={projectId:args.project,receipt:'c'.repeat(64),ordinal:1,targetId:args.node,kind:'draft-stage',phase:'in-progress'}",dict(project=f.state()['projectId'],node=node));expect(status(id,'running')).to_contain_text('초안 처리 중')
     f.page.evaluate('()=>__phaseFixture=null');expect(status(id,'running')).not_to_contain_text('초안 처리 중');expect(status(id,'running')).not_to_contain_text('읽는 중');expect(f.page.locator('#chat-input')).to_have_value('진행 표시 중 새 입력 보존');assert not owned.requests
     f.checked('UI-only receipt injection on a real approved held Worker verifies read/draft labels, foreign/hidden/malformed rejection, removal and late input; it is not evidence of native I/O timing or completion')
    switch('editor');gate.set()
    if checkIO:
     for index,label in enumerate(['읽기 완료','초안 변경 확인']):
      assert ioEntered[index].wait(timeout=20),'actual tool completion deadline'
      switch('office');ready();expect(status(id,'running')).to_contain_text('최근 '+label)
      row=next(row for row in f.state()['assignmentWorkers']if row['id']==id);receipt=row['lastToolIO'];assert receipt['targetId']==node and receipt['projectId']==f.state()['projectId'];assert receipt['ordinal']==index+1
      assert receipt['kind']==['read','draft-stage'][index] and receipt['outcome']==['completed','applied'][index];assert set(receipt)=={'projectId','receipt','ordinal','targetId','kind','outcome'}
      assert len(receipt['receipt'])==64 and 'originHash'not in receipt
      f.page.evaluate("()=>window.dispatchEvent(new CustomEvent('confectory:worker-activity',{detail:{state:'writing',access:'write'}}))");expect(status(id,'running')).to_contain_text('최근 '+label);physical()
      path=f.project/'.confectory/ai-development/helpers'/hashlib.sha256(chief.encode()).hexdigest()[:16]/'tasks.json';assert 'lastToolIO'not in path.read_text()
      f.checked('actual authorized '+['read','draft-stage'][index]+' completed receipt reaches matching public Worker and authored status text; no active phase, source write, raw capability, visual inference or journal persistence')
      switch('editor');ioGates[index].set()
    deadline=time.monotonic()+45
    while time.monotonic()<deadline:
     s=f.state()
     if next(w for w in s['workers']if w['id']==task['task'])['status']=='awaiting-verification':break
     f.page.wait_for_timeout(50)
    assert next(w for w in s['workers']if w['id']==task['task'])['status']=='awaiting-verification';assert len(owned.requests)>=3 and not owned.errors
    count=len(owned.requests);switch('office');ready();expect(status(id,'awaiting-verification')).to_contain_text('완료 검증 대기');physical();f.checked('Worker continues with 3D disabled; actual tool completion becomes verification-pending rather than animation completion or automatic source adoption')
    invoke('reviewWorker',task=task['task'],ids=[node,graph],target='portable');review=f.state()['review'];assert review['status']=='ready',review
    invoke('adoptWorker',task=task['task'],token=review['token'],ids=[node,graph],goalEvidence='Owned loopback fixture only. Compiler validation and exact node/source adoption are verified; no live AI, project execution or device outcome claimed.')
    expect(status(id,'completed')).to_contain_text('완료');assert json.loads((f.project/'Slot.node.json').read_text())['source']==owned.node_source
    allowed.update({p:(f.project/p).read_bytes()for p in ['Slot.node.json','Slot.graph.json']});physical();assert len(owned.requests)==count;f.checked('only existing explicit Review/compiler Confirm/adoption changes owned fixture sources and publishes completed status; observing never approves or replays work')
    second,secondid=assign();projected(2);invoke('selectWorker',task=second['task']);invoke('cancelReadyWorker',task=second['task'],commandID=uuid.uuid4().hex,reason='owned fixture explicit cancellation');expect(status(secondid,'cancelled')).to_contain_text('취소됨');status(id,'completed');physical();assert len(owned.requests)==count;f.checked('explicit ready cancellation is shown alongside the distinct completed Worker; original journal retention and other tasks are unchanged')
   else:
    path=f.project/'.confectory/ai-development/helpers'/hashlib.sha256(chief.encode()).hexdigest()[:16]/'tasks.json';f.pending();f.page.close();f.stop();document=json.loads(path.read_bytes());first=next(iter(document['tasks']));document['tasks'][first]['status']='running';
    if checkIO:document['tasks'][first]['lastToolIO']={'projectId':document['project'],'receipt':'b'*64,'ordinal':1,'targetId':node,'kind':'draft-stage','outcome':'applied'}
    if mode=='phase-cold':document['tasks'][first]['activeToolIO']={'projectId':document['project'],'receipt':'c'*64,'ordinal':1,'targetId':node,'kind':'read','phase':'in-progress'}
    crash=json.dumps(document,ensure_ascii=False).encode();path.write_bytes(crash);f.start(1);f.page=f.setup();ready();f.idle();projected(1);expect(status(id,'interrupted')).to_contain_text('실행 확인 필요');assert not f.state()['planningOwnerAvailable'];unchanged_journal(path,crash);physical();
    if mode=='phase-cold':assert next(row for row in f.state()['assignmentWorkers']if row['id']==id)['activeToolIO']is None;assert '읽는 중'not in office().inner_text();f.checked('cold journal cannot recreate a volatile active I/O signal or resume tool execution')
    if checkIO:assert next(row for row in f.state()['assignmentWorkers']if row['id']==id)['lastToolIO']is None;assert '최근 초안 변경 확인'not in office().inner_text();f.checked('cold journal cannot forge or restore a volatile completed IO receipt; no owner recovery or replay')
    f.checked('owned crash fixture cold-running record is read as check-required interruption; camera/source observation never opens an owner, recovers, dispatches or rewrites the journal')
    # Original distant LOD exposes Worker labels. Also inspect the actual native
    # object-form Helper workers, rather than the prototype array-form alone.
    f.page.locator('[data-workspace-zoom]').click();zoom=f.page.get_by_role('dialog',name='복셀 작업실 배율',exact=True);zoom.locator('input[type=number]').fill('50');zoom.locator('input[type=number]').press('Tab');zoom.press('Escape')
    label=office().locator('.office-helper-label');label.focus();label.press('Enter');name=office().locator('[data-office-radial-name]');name.focus();name.press('Enter');expect(office().locator('.office-inspector')).to_contain_text('확인된 작업 1건');expect(office().locator('.office-helper-worker-state')).to_have_attribute('aria-label','Worker '+id[:12]+' · 실행 확인 필요');name.press('Escape');physical();f.checked('actual native Helper/Worker keyboard details accept object observations and preserve full task identity behind a bounded display label while the actor moves')
    for variant in ['owner','project','helper','invalid']:
     bad=json.loads(crash)
     if variant=='owner':bad['owner']='foreign-user'
     elif variant=='project':bad['project']='foreign-project'
     elif variant=='helper':bad['tasks'][first]['ownerHelper']='PRIVATE-HELPER-CANARY'
     inspect_current(id)
     payload=b'{'if variant=='invalid'else json.dumps(bad).encode();path.write_bytes(payload);projected(0);availability='available'if variant=='helper'else'partial';assert f.state()['assignmentWorkersStatus']==availability;expect(f.page.locator('#workspace')).to_have_attribute('data-office-workers-status',availability);expect(office().locator('.office-radial-menu')).to_be_hidden();expect(office().locator('.office-inspector')).to_be_empty();assert 'PRIVATE-HELPER-CANARY'not in office().inner_text();unchanged_journal(path,payload);path.write_bytes(crash);projected(1);status(id,'interrupted')
    physical();f.checked('native foreign owner/project/private Helper and malformed journals disappear from the live 3D projection without repair writes or hidden identity disclosure')
    other=f.case/'other same-ID project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory','.build'));restart(2,other);switch('office');ready();projected(0);physical();restart(3,f.project);ready();projected(1);status(id,'interrupted');unchanged_journal(path,crash);physical();f.checked('same namespace/IDs in another actual project never adopt A Worker records; returning A restores public observation, not execution authority')
   f.page.screenshot(path=str(f.case/('office-workers-'+mode+'-active.png')))
   # Leaving the active context retires all projected identities.
   f.pending();f.page.locator('.brand').click();expect(f.page.locator('.home-grid')).to_be_visible();assert f.state()['assignmentWorkers']==[];expect(f.page.locator('.office-worker-label')).to_have_count(0);physical();f.checked('no-project state disposes 3D Helper/Worker identities while retaining the actual task/source data')
   f.page.screenshot(path=str(f.case/('office-workers-'+mode+'.png')));f.browser.close()
  except Exception as e:
   try:f.page.screenshot(path=str(f.case/'failure.png'));(f.case/'failure.html').write_text(f.page.content())
   except Exception:pass
   (f.case/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 [event.set()for event in ioGates];gate.set();f.stop()
 if owned:owned.close()
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2));(f.case/'office-workers.json').write_text(json.dumps(dict(mode=mode,checks=f.checks,ownedHttpRequests=owned.requests if owned else[],ownedHttpErrors=owned.errors if owned else[],actualManagedEngine=True,actualWindows=False,actualMobile=False,liveAI=False),ensure_ascii=False,indent=2))
print('OFFICE_WORKERS_FIXTURE',f.case,flush=True)
