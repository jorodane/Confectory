"""A real late header input survives a delayed successful mixed Save response."""
import json,time
from playwright.sync_api import sync_playwright,expect
import v666_retained_body_group_fixture as x
f,d=x.f,x.d;late='whole 원본 증명을 유지하는 늦은 설명 · 😀';observed=[]
def saved():
 deadline=time.monotonic()+100
 while time.monotonic()<deadline:
  if not any(v['kind']=='function-edit'for _,v in d.pending()):f.idle();return
  f.page.wait_for_timeout(20)
 raise AssertionError('Mixed save did not settle')
def restart(index):
 f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(index);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});d.open_info();f.idle()
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});d.open_info()
  for index in range(2):x.after_contract(index)
  assert len(d.pending())==2
  def intercept(route):
   body=route.request.post_data_json
   if body.get('op')=='invoke'and body.get('endpoint')=='blueprint'and body.get('input',{}).get('action')=='applySlots'and not observed:
    response=route.fetch();assert response.status==200;accepted=response.json()
    field=f.owner().locator('.object-title-description');assert field.is_enabled()and not field.evaluate('el=>el.readOnly');assert f.owner().locator('[data-element-action=save]').is_disabled();field.fill(late);observed.append(dict(request=body['requestId'],acknowledgement=accepted,pending=d.pending(),saveDisabled=True,editableHeader=True));route.fulfill(response=response);return
   route.continue_()
  f.page.route('**/api/request',intercept);f.owner().locator('[data-element-action=save]').click();saved();f.page.unroute_all(behavior='wait');assert len(observed)==1;x.verify(checkpoint);pending=d.pending();assert len(pending)==1 and pending[0][1]['kind']=='description'and pending[0][1]['text']==late;x.unchanged();expect(f.owner().locator('.object-title-description')).to_have_value(late);f.checked('delayed successful Save stores the two captured body inputs once while retaining the later real header input; repeated Save stays disabled')
  (f.case/'late-save-observation.json').write_text(json.dumps(observed,ensure_ascii=False,indent=2));first_receipt=next(r for r in json.loads(checkpoint.read_text())['changes']if r['id']==x.owner)['slotSaveReceipt'];first_guards=first_receipt['readGuards'];assert x.retained_file in first_guards;restart(1);assert len(d.pending())==1 and d.pending()[0][1]['text']==late;expect(f.owner().locator('.object-title-description')).to_have_value(late);x.verify(checkpoint);f.checked('cold restart restores the late header with the saved mixed candidate and its original dependencies')
  f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+90
  while d.pending()and time.monotonic()<deadline:f.page.wait_for_timeout(20)
  assert not d.pending();x.accepted_description=late;ids=x.verify(checkpoint);second_receipt=next(r for r in json.loads(checkpoint.read_text())['changes']if r['id']==x.owner)['slotSaveReceipt'];assert all(first_receipt[k]==second_receipt[k]for k in ['nativeBodyContexts']);second_guards=second_receipt['readGuards'];assert second_guards==first_guards,(first_guards,second_guards);review=d.review();review.locator('[data-reject]').click();x.unchanged();review=d.review()
  if review.locator('[data-review-advanced]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  review.locator('#confirm').click();expect(review).to_have_count(0);restart(2);assert not d.pending();x.verify_live();f.checked('a second explicit header Save retains the body group; cancelled Review and fresh Confirm publish the later description, both explicit bodies together');assert not f.errors and not f.external;f.browser.close()
except Exception:
 try:f.page.screenshot(path=str(f.case/'late-failure.png'))
 except Exception:pass
 (f.case/'late-failure.json').write_text(json.dumps(dict(traffic=f.traffic[-60:],checks=f.checks),ensure_ascii=False,indent=2));raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
