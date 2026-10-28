"""Real v536 display-name/removal controls, isolated engine; no account/provider run."""
import contextlib,hashlib,json,pathlib,sys,time
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3] if len(sys.argv)>3 else 'rename';local='schema '+f.n+'Local {field Mana single general long;field Other single general string;}'
(f.project/'Local.celem').write_text(local);f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element Local schema "Local.celem";registry Confectory.Build.DotNet'));p=f.project/'Slime.celem';p.write_text(p.read_text().replace('{','{use schema '+f.n+'Local;data Mana=9223372036854775806;data Other="남길 값";',1))
if mode=='delete-reference':
 (f.project/'Baby.celem').write_text('object '+f.n+'Baby extends '+f.id+' {data Mana=7;}');f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element Baby object "Baby.celem";registry Confectory.Build.DotNet'))
f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file()};key=lambda kind:f.state()['projectId']+'|'+f.id+'|element|'+kind+':["Mana"]'
def pending():return [(k,v) for k,v in f.pending()['schema'] if '|'+f.id+'|element|' in k]
def retained(captured):
 now=f.pending()
 def same(a,b):return {k:v for k,v in a.items() if k!='basis'}=={k:v for k,v in b.items() if k!='basis'}
 def journal_kept(current,prior):return isinstance(current,dict) and (same(current,prior) or any(journal_kept(p,prior) for p in current.get('previousAttempts',[])))
 for group in ['schema','blueprint']:
  for key,value in captured[group]:
   current=dict(now[group]).get(key)
   assert (journal_kept(current,value) if value.get('kind')=='owner-attempt' else current==value),(key,current)
 return now
def wait_saved():
 for _ in range(180):
  now=f.pending()
  if not [v for k,v in now['schema'] if '|'+f.id+'|element|' in k] and not [v for _,v in now['blueprint'] if v.get('kind') in ['owner-attempt','copy-attempt']]:f.idle();return
  f.page.wait_for_timeout(100)
 raise AssertionError((f.owner().locator('[data-element-error]').all_text_contents(),f.pending()))
def review():
 f.owner().locator('[data-element-action=confirm]').click();r=f.page.locator('.window[data-key=review]');f.page.wait_for_function('()=>document.querySelector("#review-creation")||[...document.querySelectorAll(".window[data-key=review]")].some(el=>!el.hidden&&el.getClientRects().length)')
 if f.page.locator('#review-creation').count():f.page.locator('#review-creation').click()
 expect(r).to_be_visible();return r

@contextlib.contextmanager
def clean_renderer():
 try:yield
 finally:
  if getattr(f,'page',None) and not f.page.is_closed():f.page.unroute_all(behavior='wait')
  if getattr(f,'browser',None):f.browser.close()

def run():
 f.start(0);f.invoke('select',{'id':f.id});f.invoke('saveDraft',{})
 with sync_playwright() as pw,clean_renderer():
  f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();expect.set_options(timeout=60000);f.open_owner();row=f.field(['Mana']);name=row.locator('[data-property-name]');expect(name).to_be_editable();checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
  if mode.startswith('delete'):
   row.locator('[data-schema-remove]').click();expect(f.field(['Mana'])).to_have_count(0);f.owner().locator('[data-own-properties-toggle]').focus();f.page.keyboard.press('Control+z');expect(f.field(['Mana'])).to_be_visible();expect(f.field(['Mana']).locator('[data-property-value]')).to_have_value('9223372036854775806');f.field(['Mana']).locator('[data-schema-remove]').click();f.checked('실제 삭제→원본 Ctrl+Z는 필드·정확한 raw64를 복원하며 디스크와 checkpoint를 바꾸지 않는다');assert checkpoint.read_bytes()==before;f.originals()
  else:
   name.fill(' ');held=f.pending();f.rejected_save();assert checkpoint.read_bytes()==before;retained(held);f.originals();expect(f.field(['Mana']).locator('[data-property-name]')).to_have_value(' ');f.field(['Mana']).locator('[data-property-name]').press('Escape');f.field(['Mana']).locator('[data-property-name]').fill('마나 한글');f.checked('불완전 이름의 실제 Save는 전체 거절·원문 보존이며 Escape 뒤 명시적 새 표시 이름으로 재시도한다')
  if mode=='copy':f.select_copy('Slot','AliasBody','slotCount=amount+5;slotReady=true;return amount+70;',True)
  held=f.pending()
  if mode=='delete-reference':
   f.rejected_save();assert checkpoint.read_bytes()==before;retained(held);f.originals();f.owner().locator('[data-element-action=discard]').click();expect(f.field(['Mana'])).to_be_visible();f.restart(1);assert not pending();f.originals();f.checked('자손이 쓰는 속성 삭제는 전체 거절하며 명시 취소·cold에 정의/값/자손/다른 입력을 보존한다');return
  if mode=='cancel':
   f.owner().locator('[data-element-action=discard]').click();expect(f.field(['Mana']).locator('[data-property-name]')).to_have_value('Mana');f.restart(1);assert not pending();assert checkpoint.read_bytes()==before;f.originals();f.checked('미적용 조회 뒤 변경 취소와 cold는 원래 표시 이름·원문·checkpoint를 유지한다');return
  if mode=='conflict':
   f.invoke('schema',{'id':f.id});d=f.state()['schema'];f.invoke('editDescription',{'id':f.id,'revision':d['revision'],'hash':d['textHash'],'value':'동료의 저장'});f.invoke('saveDraft',{});peer=checkpoint.read_bytes();f.rejected_save();retained(held);assert checkpoint.read_bytes()==peer;f.originals();f.restart(1);retained(held);f.checked('실제 동료 저장 뒤 CAS 충돌은 입력·상대 checkpoint를 cold에도 보존하고 새 기준으로 덮지 않는다');return
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:f.rejected_save();retained(held);assert checkpoint.read_bytes()==before;f.originals();f.checked('실제 checkpoint 쓰기 실패는 표시 이름·schema·선언 전체 미적용이며 입력을 보존한다')
   finally:checkpoint.chmod(0o600)
   f.restart(1);retained(held)
  if mode=='loss':
   applied=set();lookups=set();lost=[]
   def intercept(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
     action=body.get('input',{}).get('action')
     if action=='applySlots':applied.add(body['requestId'])
     elif applied and action=='settledSlots':lookups.add(body['requestId'])
    response=route.fetch();payload=response.json()
    for r in payload.get('results',[]):
     if r['requestId'] in applied|lookups:rid=r['requestId'];lost.append(rid);r.clear();r.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',intercept);f.owner().locator('[data-element-action=save]').click()
   f.page.wait_for_function('()=>!document.querySelector(".brand")?.disabled')
   for _ in range(300):
    if applied and any(r in lookups for r in lost):break
    f.page.wait_for_timeout(100)
   assert len(applied)==1 and any(r in lookups for r in lost);f.idle();retained(held);mark=len(f.traffic);f.page.unroute('**/api/request',intercept);f.restart(1)
   if pending() or [v for _,v in f.pending()['blueprint'] if v.get('kind')=='owner-attempt']:f.owner().locator('[data-element-action=save]').click()
   wait_saved();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='applySlots' for r in f.traffic[mark:]);f.checked('응답과 조회 유실 뒤 cold는 receipt 조회로만 복구하고 표시 이름 저장을 중복 실행하지 않는다')
  else:f.owner().locator('[data-element-action=save]').click();wait_saved()
  f.originals();expect(f.owner().locator('[data-element-action=confirm]')).to_be_enabled();f.restart(2)
  if mode.startswith('delete'):expect(f.field(['Mana'])).to_have_count(0)
  else:expect(f.field(['Mana']).locator('[data-property-name]')).to_have_value('마나 한글');expect(f.field(['Mana']).locator('[data-property-value]')).to_have_value('9223372036854775806')
  expect(f.field(['Other']).locator('[data-property-value]')).to_have_value('남길 값');f.checked('실제 저장/cold는 표시 이름과 안정된 데이터 키·raw64 또는 명시 삭제만 복원하고 다른 속성은 보존한다')
  r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();f.originals();r=review()
  if r.locator('[data-review-advanced]').count():
   r.locator('[data-review-advanced]').click()
   if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
  r.locator('#confirm').click();expect(r).to_have_count(0,timeout=120000);f.idle();changed={k for k,v in f.original.items() if (f.project/k).read_bytes()!=v};assert changed==({'Local.celem','Slime.celem'} if mode.startswith('delete') else {'Local.celem','Slime.celem','project.cproj'} if mode=='copy' else {'Local.celem'}),changed
  f.case.joinpath('final-schema.json').write_text(json.dumps(f.state()['schema'],ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'schema-mutations-final.png'));assert not f.errors and not f.external,(f.errors,f.external);f.checked('Review 취소는 원본 불변이고 명시 compiler Confirm만 해당 schema/삭제 owner를 반영하며 부모·다른 target은 보존한다')
  saved=json.loads(checkpoint.read_text());members={u['id']:u for u in saved['changes']};assert all(all(member in members for member in u['atomicEditGroup']) for u in members.values() if u.get('atomicEditGroup'));f.restart(3);assert not pending();
  if mode.startswith('delete'):expect(f.field(['Mana'])).to_have_count(0)
  else:expect(f.field(['Mana']).locator('[data-property-name]')).to_have_value('마나 한글');expect(f.field(['Mana']).locator('[data-property-value]')).to_have_value('9223372036854775806');f.field(['Mana']).scroll_into_view_if_needed()
  f.page.screenshot(path=str(f.case/'schema-post-confirm-cold.png'));f.checked('확정 후 cold도 정상 열리며 clean 지원 행을 포함한 원자 그룹 기록은 함께 정리하고 표시명/원문을 복원한다');assert not f.errors and not f.external,(f.errors,f.external)
def graph_boundary():
 import v536_property_plan as p
 try:
  p.start(0);prior=p.current();assert prior['diagnostics']['state'] in ['source-ready','source-assembled'];owner=p.n+'Monster';p.call('select',{'id':owner});p.call('saveDraft',{});p.call('schema',{'id':owner});view=p.mount()
  try:schema=view['state']['schema']
  finally:p.raw({'op':'dispose','view':view['view']})
  old=(p.project/'Vitals.celem').read_text();prepared=p.call('blueprint',{'action':'readOwnerEdits','id':owner,'hash':schema['textHash']});checkpoint=next(p.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();change={'type':'schema-remove','path':['health'],'contract':{'kind':'general','cardinality':'single','type':'long'},'schema':p.n+'Vitals','schemaHash':hashlib.sha256(old.encode()).hexdigest()};p.call('blueprint',{'action':'applySlots','id':owner,'rows':[],'basis':prepared['basis'],'declaration':{'id':owner,'hash':schema['textHash'],'changes':[change]}},ok=False);assert checkpoint.read_bytes()==before;p.unchanged();assert p.current()['sources']==prior['sources'];f.checked('데이터 값이 없는 속성도 기존 property 읽기/쓰기 graph가 사용하면 staged 검증에서 전체 삭제를 거절한다');print('GRAPH_EVIDENCE '+str(p.case),flush=True)
 finally:p.stop()
try:
 if mode=='graph':graph_boundary()
 else:run()
except Exception:
 try:f.page.screenshot(path=str(f.case/'failure.png'));f.case.joinpath('failure.json').write_text(json.dumps({'traffic':f.traffic[-50:],'inputs':f.pending(),'errors':f.owner().locator('[data-element-error]').all_text_contents()},ensure_ascii=False,indent=2))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':mode!='graph','nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
