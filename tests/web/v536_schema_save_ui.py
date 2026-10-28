"""Actual owner/schema + separate Save and optional copy, using isolated wide fixture helpers."""
import copy,hashlib,json,pathlib,sys,time
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
local='schema '+f.n+'Local {field Mana single general long;}'
(f.project/'Local.celem').write_text(local);f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element Local schema "Local.celem";registry Confectory.Build.DotNet'));p=f.project/'Slime.celem';p.write_text(p.read_text().replace('{','{use schema '+f.n+'Local;data Mana=9223372036854775806;',1));f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file()};shape={'kind':'general','cardinality':'single','type':'long'}
contract={'type':'schema-field','path':['Mana'],'contract':shape,'schema':f.n+'Local','schemaHash':hashlib.sha256(local.encode()).hexdigest(),'nativeType':'string'}
changes=[{'type':'description','text':'분리 저장도 원자적'},contract,{'type':'data','path':['Mana'],'contract':shape,'valueJson':'"명시적 한글"'}]
def request():
 f.invoke('schema',{'id':f.id});d=f.state()['schema'];prepared=f.invoke('blueprint',{'action':'readOwnerEdits','id':f.id,'hash':d['textHash']})['result']['result'];return {'action':'applySlots','id':f.id,'rows':[],'basis':prepared['basis'],'declaration':{'id':f.id,'hash':d['textHash'],'changes':copy.deepcopy(changes)}},prepared

def graph_boundary():
 import v536_property_plan as p
 try:
  p.start(0);prior=p.current();assert prior['diagnostics']['state'] in ['source-ready','source-assembled'];owner=p.n+'Monster';p.call('select',{'id':owner});p.call('saveDraft',{});p.call('schema',{'id':owner});view=p.mount()
  try:schema=view['state']['schema']
  finally:p.raw({'op':'dispose','view':view['view']})
  source=(p.project/'Vitals.celem').read_text();change={'type':'schema-field','path':['health'],'contract':{'kind':'general','cardinality':'single','type':'long'},'schema':p.n+'Vitals','schemaHash':hashlib.sha256(source.encode()).hexdigest(),'nativeType':'double'};prepared=p.call('blueprint',{'action':'readOwnerEdits','id':owner,'hash':schema['textHash']});checkpoint=next(p.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();p.call('blueprint',{'action':'applySlots','id':owner,'rows':[],'basis':prepared['basis'],'declaration':{'id':owner,'hash':schema['textHash'],'changes':[change,{'type':'description','text':'연결은 보존'}]}},ok=False);assert checkpoint.read_bytes()==before;p.unchanged();assert p.current()['sources']==prior['sources'];f.checked('기존 long 속성 읽기/쓰기·소비 연결은 값 타입이 유효해도 staged schema 변경을 거절하며 연결·원문·checkpoint를 보존한다');f.case.joinpath('graph-fixture.txt').write_text(str(p.case));print('GRAPH_EVIDENCE '+str(p.case),flush=True)
 finally:p.stop()

def backend():
 f.start(0);f.invoke('select',{'id':f.id});f.invoke('saveDraft',{});req,basis=request();checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();bad=copy.deepcopy(req);bad['declaration']['changes'].pop();f.invoke('blueprint',bad,False);assert checkpoint.read_bytes()==before;f.originals();f.invoke('schema',{'id':f.id});assert f.state()['schema']['description']!='분리 저장도 원자적';f.checked('독립 Save의 마지막 타입/값 오류가 앞 설명/schema를 부분 반영하지 않는다')
 result=f.invoke('blueprint',req)['result']['result'];assert result['checkpointSaved'];query={'action':'settledSlots','id':f.id,'rows':[],'declaration':req['declaration'],'fingerprint':basis['fingerprint']};assert f.invoke('blueprint',query)['result']['result']['settled'];f.invoke('schema',{'id':f.id});assert f.state()['schema']['description']=='분리 저장도 원자적';f.originals();f.checked('기존 schema+선언+명시 값은 한 후보/CAS와 정확한 receipt로 저장되고 원본은 미확정이다');saved=checkpoint.read_bytes();f.invoke('reviewGroup',{'ids':[f.id],'target':'portable'},False);assert checkpoint.read_bytes()==saved;f.originals();f.checked('schema와 선언 중 일부만 Review하는 요청은 거절하며 원자 그룹의 명시 확정 경계를 유지한다')

def type_choice(value):
 row=f.field(['Mana']);row.locator('[data-property-type]').click();picker=f.page.get_by_role('dialog',name='속성 타입 선택',exact=True);expect(picker).to_be_visible();
 if mode=='capture':f.page.screenshot(path=str(f.case/'schema-type-controls.png'))
 picker.locator('[data-type="'+value+'"]').click();f.idle()
def own_inputs():return [(k,v) for k,v in f.pending()['schema'] if '|'+f.id+'|element|' in k]
def preserve_inputs(captured):
 now=f.pending()
 for group in ['schema','blueprint']:
  for key,value in captured[group]:
   if value.get('kind') in ['owner-attempt','copy-attempt']:
    current=dict(now[group]).get(key);assert current==value or value in (current or {}).get('previousAttempts',[]),(key,current);continue
   assert dict(now[group]).get(key)==value,(key,now[group])
 return now
def wait_save():
 for _ in range(240):
  now=f.pending();attempts=[v for k,v in now['blueprint'] if v.get('kind') in ['owner-attempt','copy-attempt']];cells=[v for k,v in now['schema'] if '|'+f.id+'|element|' in k]
  if not cells and not attempts:f.idle();return
  f.page.wait_for_timeout(100)
 raise AssertionError((f.owner().locator('[data-element-error]').all_text_contents(),f.pending()))
def ui():
 f.start(0);f.invoke('select',{'id':f.id});f.invoke('saveDraft',{})
 with sync_playwright() as playwright:
  f.browser=playwright.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();expect.set_options(timeout=60000);f.open_owner();f.owner().locator('.object-title-description').fill('분리 저장도 원자적');
  if mode=='copy':f.select_copy('Slot','AliasBody','slotCount=amount+5;slotReady=true;return amount+70;',True)
  type_choice('string');expect(f.field(['Mana']).locator('[data-property-value]')).to_have_value('9223372036854775806');held=f.pending();checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();f.rejected_save();preserve_inputs(held);assert checkpoint.read_bytes()==before;f.originals();f.checked('실제 타입 버튼은 원래 숫자를 보존하고 불일치 Save는 설명/schema/값 모두 미적용한다')
  # Use the original control and keyboard Undo, never edit product input maps.
  f.field(['Mana']).locator('[data-property-type]').focus();f.page.keyboard.press('Control+z');assert not any(v.get('kind')=='schema-field' for k,v in own_inputs());
  if mode=='undo-empty':
   f.owner().locator('.object-title-description').fill('');assert not own_inputs();held=f.pending();mark=len(f.traffic);f.rejected_save();preserve_inputs(held);assert checkpoint.read_bytes()==before and not any(v.get('invoke',{}).get('endpoint')=='saveDraft' or v.get('invoke',{}).get('input',{}).get('action')=='applySlots' for v in f.traffic[mark:]);f.originals();f.owner().locator('[data-element-action=discard]').click();expect(f.owner().locator('[data-element-action=discard]')).to_be_disabled();assert not f.pending()['blueprint'];f.checked('전체 입력 Undo 뒤 남은 미적용 시도는 빈 Save로 덮지 않고 결과 조회·명시 취소로만 정리한다');return
  type_choice('string');f.field(['Mana']).locator('[data-property-value]').fill('명시적 한글');
  if mode.startswith('copy-after'):f.select_copy('Slot','AliasBody','slotCount=amount+5;slotReady=true;return amount+70;',True)
  held=f.pending()
  if mode=='cancel':
   f.owner().locator('[data-element-action=discard]').click();expect(f.owner().locator('[data-element-action=discard]')).to_be_disabled();assert not own_inputs();assert checkpoint.read_bytes()==before;f.originals();f.restart(1);assert not own_inputs();f.checked('조회로 미적용을 확인한 뒤 명시 취소는 원본·저장본을 유지하며 cold에도 취소 입력을 되살리지 않는다');return
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:f.rejected_save();preserve_inputs(held);assert checkpoint.read_bytes()==before;f.originals();f.checked('실제 checkpoint 쓰기 거절은 전체 미적용 및 입력 보존이다')
   finally:checkpoint.chmod(0o600)
   f.restart(1);preserve_inputs(held)
  if mode in ['conflict','copy-after-source']:
   if mode=='copy-after-source':
    source=f.project/'Slot2.csbody';source.write_text('slotCount=amount+8;slotReady=true;return amount+80;');f.original['Slot2.csbody']=source.read_bytes()
   else:
    f.invoke('schema',{'id':f.id});d=f.state()['schema'];f.invoke('editDescription',{'id':f.id,'revision':d['revision'],'hash':d['textHash'],'value':'동료의 저장'});f.invoke('saveDraft',{})
   peer=checkpoint.read_bytes();f.rejected_save();preserve_inputs(held);assert checkpoint.read_bytes()==peer;f.originals()
   if mode=='copy-after-source':f.checked('새 copy 선택 뒤 실제 source 파일이 바뀌면 old owner 요청을 새 기준으로 재적용하지 않고 전체 입력·기록·checkpoint를 보존한다');return
   f.restart(1);preserve_inputs(held);f.checked('실제 동시 저장은 새 기준으로 덮어쓰지 않고 전체 입력·동료 checkpoint를 cold에도 보존한다');return
  if mode=='copy-after-race':
   before=checkpoint.read_bytes();raced=[]
   def race(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and body.get('input',{}).get('action')=='applySlots':
     assert body['input'].get('priorOwner');source=f.project/'Slot2.csbody';source.write_text('slotCount=amount+8;slotReady=true;return amount+80;');f.original['Slot2.csbody']=source.read_bytes();raced.append(body['requestId'])
    route.continue_()
   f.page.route('**/api/request',race);f.rejected_save();f.page.unroute('**/api/request',race);assert len(raced)==1;preserve_inputs(held);assert checkpoint.read_bytes()==before;f.originals();f.checked('UI 재검증 뒤 전송 직전 실제 source 변경도 서버 prior-owner 검사가 전체 거절하며 앞 schema/copy나 기록을 부분 정리하지 않는다');return
  if mode in ['response-loss','copy-after-loss']:
   ids=set();lookups=set();lost=[]
   def intercept(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
     if body.get('input',{}).get('action')=='applySlots':
      if mode=='copy-after-loss':assert body['input'].get('priorOwner')
      ids.add(body['requestId'])
     elif ids and body.get('input',{}).get('action')=='settledSlots':lookups.add(body['requestId'])
    response=route.fetch();payload=response.json()
    for row in payload.get('results',[]):
     if row['requestId'] in ids|lookups:
      rid=row['requestId'];lost.append(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',intercept);f.owner().locator('[data-element-action=save]').click()
   for _ in range(1800):
    if ids and any(rid in lookups for rid in lost):break
    f.page.wait_for_timeout(20)
   assert ids and any(rid in lookups for rid in lost);f.idle();preserve_inputs(held);assert len(ids)==1 and lost;mark=len(f.traffic);f.page.unroute('**/api/request',intercept);f.restart(1)
   if [v for _,v in f.pending()['blueprint'] if v.get('kind') in ['owner-attempt','copy-attempt']]:f.owner().locator('[data-element-action=save]').click()
   wait_save();assert not any(v.get('invoke',{}).get('endpoint')=='blueprint' and v.get('invoke',{}).get('input',{}).get('action')=='applySlots' for v in f.traffic[mark:]);f.checked('성공 응답과 결과 조회 유실은 입력을 보관하고 cold 조회로만 복구하며 중복 저장하지 않는다')
  else:
   mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click()
   if mode=='copy-after-rejection':
    for _ in range(1800):
     ids={row['invoke']['requestId'] for row in f.traffic[mark:] if row.get('invoke',{}).get('endpoint')=='blueprint' and row['invoke'].get('input',{}).get('action')=='applySlots'}
     if any(row.get('result',{}).get('requestId') in ids and row['result'].get('ok') for row in f.traffic[mark:]):break
     f.page.wait_for_timeout(20)
    assert ids;f.idle();now=f.pending();f.case.joinpath('cross-save-journals.json').write_text(json.dumps(now,ensure_ascii=False,indent=2));assert not [value for _,value in now['blueprint'] if value.get('kind') in ['owner-attempt','copy-attempt']],now['blueprint']
   wait_save()
  f.originals();f.invoke('schema',{'id':f.id});d=f.state()['schema'];mana=next(row for row in d['rows'] if row['path']==['Mana']);assert mana['type']=='string' and '명시적 한글' in str(mana);f.checked('거절→원래 Undo→새 타입/명시 값의 재시도는 한 후보로 성공하고 입력·원본을 보존한다')
  if mode=='capture':f.page.screenshot(path=str(f.case/'schema-atomic-saved.png'));return
  f.restart(2);expect(f.field(['Mana']).locator('[data-property-value]')).to_have_value('명시적 한글');f.owner().locator('[data-element-action=confirm]').click();review=f.page.locator('.window[data-key=review]');
  f.page.wait_for_function('()=>document.querySelector("#review-creation")||[...document.querySelectorAll(".window[data-key=review]")].some(el=>!el.hidden&&el.getClientRects().length)')
  if f.page.locator('#review-creation').count():f.page.locator('#review-creation').click()
  expect(review).to_be_visible();ids=f.state()['review']['units'];assert {f.id,f.n+'Local'}<={row['id'] for row in ids};review.locator('[data-reject]').click();expect(review).to_be_hidden();f.originals();f.owner().locator('[data-element-action=confirm]').click();
  f.page.wait_for_function('()=>document.querySelector("#review-creation")||[...document.querySelectorAll(".window[data-key=review]")].some(el=>!el.hidden&&el.getClientRects().length)')
  if f.page.locator('#review-creation').count():f.page.locator('#review-creation').click()
  expect(review).to_be_visible()
  if review.locator('[data-review-advanced]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  review.locator('#confirm').click();expect(review).to_have_count(0,timeout=120000);f.idle();changed={key for key,value in f.original.items() if (f.project/key).read_bytes()!=value};assert changed==({'Slime.celem','Local.celem','project.cproj'} if mode=='copy' or mode.startswith('copy-after') else {'Slime.celem','Local.celem'}),changed;f.checked('cold·Review취소·명시 compiler Confirm은 schema/선언/선택copy 전체만 반영하고 부모·원본·다른 target은 불변이다');assert not f.errors and not f.external,(f.errors,f.external)
try:
 if mode=='graph':graph_boundary()
 elif mode=='backend':backend()
 else:ui()
except Exception:
 try:f.page.screenshot(path=str(f.case/'schema-failure.png'));f.case.joinpath('schema-failure.json').write_text(json.dumps({'traffic':f.traffic[-40:],'state':f.pending(),'messages':f.owner().locator('[data-element-error]').all_text_contents()},ensure_ascii=False,indent=2))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':mode not in ['backend','graph'],'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
