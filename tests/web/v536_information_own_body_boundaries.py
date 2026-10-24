"""Atomic first implementation, source/CAS and close/lost-response boundaries in isolated fixtures."""
import json,sys,time
from playwright.sync_api import sync_playwright,expect
import v536_field_definitions_ui as d
f=d.f;owner=d.owner;fn=owner+'_Function_'+'6'*32;mode=sys.argv[3]
def schema():f.invoke('schema',{'id':owner});return f.state()['schema']
def method():return f.owner().locator('[data-inline-method="'+fn+'"]')
def direct():f.idle();method().locator('[data-function-write-direct],[data-function-edit]').click()
def no_provider():assert not any(row['function']==fn for row in schema().get('providers',[]))
def ready():expect(f.author().locator('[data-bp-node=body]')).to_be_visible();expect(f.author().locator('[data-bp-name]')).to_have_value('자체 보존');expect(f.owner().get_by_label('Power 기본값',exact=True)).to_be_editable();f.idle()
def restart(i):f.pending();f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1850,'height':1450});expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo');f.idle()
try:
 f.start(0);f.invoke('select',{'id':owner});s=schema();p=f.invoke('blueprint',{'action':'readOwnerEdits','id':owner,'hash':s['textHash']})['result']['result'];f.invoke('blueprint',{'action':'applySlots','id':owner,'rows':[],'basis':p['basis'],'declaration':{'id':owner,'hash':s['textHash'],'changes':[{'type':'function-add','id':fn,'name':'자체 보존','description':'보존할 함수'}]}})
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1850,'height':1450});d.open_info();checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();no_provider()
  if mode in ['body-storage','body-conflict','body-loss','body-close']:
   direct();ready();f.author().locator(':scope>.window-title .caption').click(position={'x':5,'y':5});f.author().locator('[data-bp-overview-node=body]').click();f.author().locator('[data-bp-node=body] [data-internal-code]').click();dialog=f.page.locator('.bp-script-dialog');value=dialog.locator('[data-code-source]');value.evaluate(r"""el=>{el.focus();el.setSelectionRange(el.value.indexOf('\n{\n')+3,el.value.lastIndexOf('\n}'));}""");f.page.keyboard.insert_text('return; // 보존할 본문');dialog.locator('[data-code-save]').click();held_inputs=f.pending();before_body=checkpoint.read_bytes()
   def body_read():
    current=schema();return f.invoke('blueprint',{'action':'read','id':fn+'BlueprintBody/body:common','owner':owner,'ownerHash':current['textHash'],'ownerRevision':current['revision']})['result']['result']
   original_body=body_read()['nodes'][0]['source']
   def retained():
    now=f.pending();assert all(dict(now['blueprint']).get(key)==value for key,value in held_inputs['blueprint']),{'expected':held_inputs,'actual':now}
   def saved():
    f.idle();now=f.pending();assert not [v for k,v in now['blueprint'] if '|v508-author' in k],{'status':f.author().locator('.bp-status').all_text_contents(),'inputs':now}
   if mode in ['body-storage','body-conflict']:
    if mode=='body-storage':checkpoint.chmod(0o400)
    else:
     source=f.project/'FreeInfo.celem';source.write_bytes(source.read_bytes()+b'\n// concurrent body fixture source\n');f.original['FreeInfo.celem']=source.read_bytes()
    try:
     f.author().locator('[data-bp-save]').click();expect(f.author().locator('.bp-status')).to_contain_text(__import__('re').compile('못|실패|failed|consumer|바뀌'));f.idle();assert checkpoint.read_bytes()==before_body;retained();assert body_read()['nodes'][0]['source']==original_body;f.originals();f.checked('본문 checkpoint 쓰기 거절/실제 source 변경은 live 본문과 저장본을 모두 미적용하고 C# private 입력을 보존한다')
    finally:
     if mode=='body-storage':checkpoint.chmod(0o600)
    restart(1);retained();assert checkpoint.read_bytes()==before_body;f.originals()
    if mode=='body-storage':
     direct();ready();f.author().locator('[data-bp-save]').click();saved();assert '보존할 본문' in body_read()['nodes'][0]['source'];f.originals();f.checked('쓰기 거절 뒤 실제 cold와 명시적 재시도는 같은 입력·기준으로 한 번만 전체 본문을 저장한다')
    else:f.checked('실제 source 변경 거절 뒤 cold도 원래 입력과 동료 원본을 보존하고 자동 적용하지 않는다')
   else:
    ids=set();held={}
    def intercept_body(route):
     request=route.request.post_data_json
     if request.get('op')=='invoke' and request.get('endpoint')=='blueprint' and request.get('input',{}).get('action')=='authorBatch':ids.add(request['requestId'])
     response=route.fetch();payload=response.json()
     if not held and any(row.get('requestId') in ids and row.get('ok') for row in payload.get('results',[])):held.update(route=route,response=response,payload=payload);return
     route.fulfill(response=response,json=payload)
    f.page.route('**/api/request',intercept_body);f.author().locator('[data-bp-save]').click();deadline=time.monotonic()+60
    while time.monotonic()<deadline and not held:f.page.wait_for_timeout(30)
    assert held and len(ids)==1;assert checkpoint.read_bytes()!=before_body
    if mode=='body-loss':
     f.author().locator('[data-bp-description]').fill('응답 대기 중 늦은 설명')
     for row in held['payload']['results']:
      if row.get('requestId') in ids:rid=row['requestId'];row.clear();row.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
    else:f.close_author()
    held['route'].fulfill(response=held['response'],json=held['payload']);f.idle();f.page.unroute_all(behavior='wait');assert len(ids)==1
    if mode=='body-loss':
     now=f.pending()['blueprint'];assert len(now)==1 and now[0][1]['type']=='implementation-description' and now[0][1]['text']=='응답 대기 중 늦은 설명',now;assert '보존할 본문' in body_read()['nodes'][0]['source'];f.originals();f.checked('실제 본문 성공 응답 유실은 저장 receipt를 조회해 한 번만 복구하며 응답 대기 중 생긴 새 설명을 유지한다')
    else:
     assert not f.author().is_visible();assert '보존할 본문' in body_read()['nodes'][0]['source'];retained();f.originals();f.checked('본문 저장 성공 응답 직전 창 닫기는 새 창을 열지 않고 이미 저장한 checkpoint와 원래 입력·저장 시도 기록을 유지한다')
    restart(1);direct();ready();f.author().locator('[data-bp-save]').click();saved();current=body_read();assert '보존할 본문' in current['nodes'][0]['source']
    if mode=='body-loss':assert current['implementationDescription']=='응답 대기 중 늦은 설명'
    f.originals();f.checked('성공 결과와 원래 receipt의 cold 복원·명시적 저장은 중복 본문 적용 없이 보관 입력만 정리한다')
  elif mode in ['storage','source']:
   if mode=='storage':checkpoint.chmod(0o400)
   else:
    source=f.project/'FreeInfo.celem';source.write_bytes(source.read_bytes()+b'\n// concurrent fixture source\n');f.original['FreeInfo.celem']=source.read_bytes()
   try:direct();expect(f.owner().locator('[data-element-error]')).not_to_be_empty();f.idle();expect(f.owner().get_by_label('Power 기본값',exact=True)).to_be_editable();assert not f.author().is_visible();assert checkpoint.read_bytes()==before;no_provider();f.originals();f.checked('첫 구현의 저장 거절/실제 원본 변경은 정보 provide·구현·등록·graph/node를 모두 미적용하고 입력 보호를 해제한다')
   finally:
    if mode=='storage':checkpoint.chmod(0o600)
   restart(1)
   if mode=='storage':direct();ready();assert len([v for v in json.loads(checkpoint.read_text())['changes'] if v['kind']=='implementation' and v.get('creationOwner')==owner])==1;f.originals();f.checked('cold 뒤 새 명시적 재시도는 첫 구현을 한 번만 checkpoint에 보관하고 본문 편집을 연다')
   else:direct();expect(f.owner().locator('[data-element-error]')).not_to_be_empty();f.idle();assert checkpoint.read_bytes()==before;no_provider();f.originals();f.checked('cold 뒤에도 실제 달라진 원본은 자동 덮어쓰지 않고 전체 거절한다')
  elif mode in ['loss','close']:
   ids=set();held={}
   def intercept(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and body.get('input',{}).get('action')=='createFeature':ids.add(body['requestId'])
    response=route.fetch();payload=response.json()
    if not held and any(row.get('requestId') in ids and row.get('ok') for row in payload.get('results',[])):held.update(route=route,response=response,payload=payload);return
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',intercept);direct();deadline=time.monotonic()+60
   while time.monotonic()<deadline and not held:f.page.wait_for_timeout(30)
   assert held and len(ids)==1;assert checkpoint.read_bytes()!=before;expect(f.owner().get_by_label('Power 기본값',exact=True)).not_to_be_editable();assert not f.page.locator('#app').evaluate('e=>e.inert')
   if mode=='close':f.owner().locator('[data-close]').first.click();expect(f.owner()).to_be_hidden()
   else:
    for row in held['payload']['results']:
     if row.get('requestId') in ids:rid=row['requestId'];row.clear();row.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
   held['route'].fulfill(response=held['response'],json=held['payload']);f.idle();f.page.unroute_all(behavior='wait')
   if mode=='loss':ready();assert len(ids)==1;f.originals();f.checked('실제 첫 구현 성공 응답 유실은 보관된 같은 정보의 provide/graph를 읽어 복구하며 생성 요청을 중복하지 않는다')
   else:assert not f.author().is_visible();d.open_info();expect(f.owner().get_by_label('Power 기본값',exact=True)).to_be_editable();direct();ready();f.originals();f.checked('성공 응답 직전 정보 창 닫기는 본문 창을 뒤늦게 열지 않고 잠금을 정리하며 보관된 구현의 재진입을 허용한다')
   f.close_author();restart(1);direct();ready();assert len([v for v in json.loads(checkpoint.read_text())['changes'] if v['kind']=='implementation' and v.get('creationOwner')==owner])==1;f.originals();f.checked('실제 cold는 같은 구현과 전체 검토 그룹을 복원하며 중복 구현/부분 등록을 남기지 않는다')
  else:raise AssertionError(mode)
  assert not f.errors and not f.external,(f.errors,f.external);f.page.unroute_all(behavior='wait');f.browser.close()
except Exception:
 try:(f.case/'own-body-boundary-failure.json').write_text(json.dumps({'mode':mode,'state':f.state(),'traffic':f.traffic[-100:],'checks':f.checks,'errors':f.errors},ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'own-body-boundary-failure.png'))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
