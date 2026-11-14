"""A real late header input survives a delayed successful mixed Save response."""
import json,time
from playwright.sync_api import sync_playwright,expect
import v666_native_return_chain_fixture as x
f,d=x.f,x.d;late='응답을 기다리는 동안의 새 정보 설명';observed=[]
original_setup=f.setup
def setup():
 page=original_setup()
 def trace(source,payload):
  with(f.case/'save-clicks.jsonl').open('a')as out:out.write(json.dumps(payload,ensure_ascii=False)+'\n')
 page.expose_binding('recordRetainedSaveClick',trace)
 page.evaluate("""()=>{for(const type of ['pointerdown','pointerup','click'])document.addEventListener(type,e=>{const b=e.target.closest?.('[data-element-action=save]');if(b)window.recordRetainedSaveClick({type,trusted:e.isTrusted,disabled:b.disabled,connected:b.isConnected,status:document.querySelector('#status')?.textContent})},true)}""")
 return page
f.setup=setup
def saved():
 deadline=time.monotonic()+100
 while time.monotonic()<deadline:
  if not any(v['kind']=='function-edit'for _,v in d.pending()):f.idle();return
  f.page.wait_for_timeout(300)
 raise AssertionError('Mixed save did not settle')
def restart(index):
 f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(index);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});d.open_info();f.idle()
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});d.open_info()
  for index in range(2):
   if True:
    f.owner().locator('[data-inline-method="'+x.functions[index]+'"] > .function-node-heading').dblclick(position={'x':190,'y':3});popup=f.page.locator('.function-detail-popover');expect(popup).to_be_visible();x.edit_contract(popup,index);popup.get_by_role('button',name='저장',exact=True).click();expect(popup).to_have_count(0)
   x.after_contract(index)
  assert len(d.pending())==2
  def intercept(route):
   body=route.request.post_data_json
   if body.get('op')=='invoke'and body.get('endpoint')=='blueprint'and body.get('input',{}).get('action')=='applySlots'and not observed:
    response=route.fetch();assert response.status==200;accepted=response.json()
    field=f.owner().locator('.object-title-description');assert field.is_enabled()and not field.evaluate('el=>el.readOnly');assert f.owner().locator('[data-element-action=save]').is_disabled();field.fill(late);observed.append(dict(request=body['requestId'],acknowledgement=accepted,pending=d.pending(),saveDisabled=True,editableHeader=True));route.fulfill(response=response);return
   route.continue_()
  f.page.route('**/api/request',intercept);f.owner().locator('[data-element-action=save]').click();saved();f.page.unroute_all(behavior='wait');assert len(observed)==1;x.verify(checkpoint);pending=d.pending();assert len(pending)==1 and pending[0][1]['kind']=='description'and pending[0][1]['text']==late;x.unchanged();expect(f.owner().locator('.object-title-description')).to_have_value(late);f.checked('delayed successful Save stores the captured return contracts and two bodies once while retaining the later real header input; repeated Save stays disabled')
  (f.case/'late-save-observation.json').write_text(json.dumps(observed,ensure_ascii=False,indent=2));first_guards=next(r for r in json.loads(checkpoint.read_text())['changes']if r['id']==x.owner)['slotSaveReceipt']['readGuards'];assert set([x.retained_header,x.retained_file,x.retained_graph])<=set(first_guards);assert set([*x.functions,*[fn+'Body/body:common'for fn in x.functions],x.n.caller+'Body/body:common'])<=set(next(r for r in json.loads(checkpoint.read_text())['changes']if r['id']==x.owner)['slotSaveReceipt']['sources']);restart(1);assert len(d.pending())==1 and d.pending()[0][1]['text']==late;expect(f.owner().locator('.object-title-description')).to_have_value(late);x.verify(checkpoint);f.checked('cold restart restores the late header with the saved mixed candidate and its original dependencies')
  if x.mode=='late-peer':
   before=d.pending();saved_checkpoint=checkpoint.read_bytes();sc=f.state()['schema'];f.invoke('editDescription',dict(id=x.owner,hash=sc['textHash'],revision=sc['revision'],value='peer가 바꾼 소유 선언'))
   f.idle();button=f.owner().locator('[data-element-action=save]')
   if not button.is_disabled():button.click()
   f.page.wait_for_function("()=>document.querySelector('[data-element-action=save]')?.disabled||[...document.querySelectorAll('[data-element-error],#status')].some(el=>/바뀌|입력.*유지|확인.*주세요|실패/.test(el.textContent))",timeout=30000);f.idle();assert d.pending()==before and checkpoint.read_bytes()==saved_checkpoint;assert f.metadata('inspect',text=f.state()['draft']['text'])['description']=='peer가 바꾼 소유 선언';x.unchanged();f.checked('new description cannot advance its basis when the owner source changes; peer, late input and saved body group remain intact');f.browser.close();raise SystemExit(0)
  f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+90
  while d.pending()and time.monotonic()<deadline:f.page.wait_for_timeout(300)
  assert not d.pending();x.accepted_description=late;ids=x.verify(checkpoint);second_guards=next(r for r in json.loads(checkpoint.read_text())['changes']if r['id']==x.owner)['slotSaveReceipt']['readGuards'];assert second_guards==first_guards,(first_guards,second_guards);review=d.review();review.locator('[data-reject]').click();x.unchanged();review=d.review()
  if review.locator('[data-review-advanced]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  review.locator('#confirm').click();expect(review).to_have_count(0);restart(2);assert not d.pending();x.verify_live();f.checked('a second explicit header Save retains the body group; cancelled Review and fresh Confirm publish the later description, explicit return contracts and both native bodies together');assert not f.errors and not f.external;f.browser.close()
except Exception:
 try:f.page.screenshot(path=str(f.case/'late-failure.png'))
 except Exception:pass
 (f.case/'late-failure.json').write_text(json.dumps(dict(traffic=f.traffic[-60:],checks=f.checks),ensure_ascii=False,indent=2));raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
