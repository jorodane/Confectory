"""A real later return-label input survives a queued successful Save and cold restart."""
import json,time
from playwright.sync_api import sync_playwright,expect
import v666_return_label_fixture as x
f,d=x.f,x.d;late='응답 후에도 남길 결과';observed=[]
def popup(fn):
 f.owner().locator('[data-inline-method="'+fn+'"] > .function-node-heading').dblclick(position={'x':190,'y':3});p=f.page.locator('.function-detail-popover');expect(p).to_be_visible();return p
def edit(index,label):
 p=popup(x.functions[index]);p.locator('[data-signature-id=return] [data-signature-name]').fill(label);p.get_by_role('button',name='저장',exact=True).click();expect(p).to_have_count(0);f.idle()
def saved(count):
 deadline=time.monotonic()+100
 while time.monotonic()<deadline:
  if len(d.pending())==count:f.idle();return
  f.page.wait_for_timeout(20)
 raise AssertionError(('Pending did not settle',d.pending()))
def restart(index):
 f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(index);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});d.open_info();f.idle()
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});d.open_info()
  for index,label in enumerate(x.labels):edit(index,label)
  assert len(d.pending())==2
  def intercept(route):
   body=route.request.post_data_json
   if body.get('op')=='invoke'and body.get('endpoint')=='blueprint'and body.get('input',{}).get('action')=='applySlots'and not observed:
    response=route.fetch();assert response.status==200;assert f.owner().locator('[data-element-action=save]').is_disabled();edit(0,late);observed.append(dict(request=body['requestId'],pending=d.pending(),saveDisabled=True));route.fulfill(response=response);return
   route.continue_()
  f.page.route('**/api/request',intercept);f.owner().locator('[data-element-action=save]').click();saved(1);f.page.unroute_all(behavior='wait');assert len(observed)==1;x.verify(checkpoint);pending=d.pending();assert len(pending)==1 and pending[0][1]['id']==x.functions[0]and pending[0][1]['returnName']==late;x.unchanged();f.checked('delayed queued Save stores both captured labels once and retains a later real label; repeated Save is disabled')
  (f.case/'late-save-observation.json').write_text(json.dumps(observed,ensure_ascii=False,indent=2));restart(1);assert len(d.pending())==1 and d.pending()[0][1]['returnName']==late;x.verify(checkpoint);p=popup(x.functions[0]);expect(p.locator('[data-signature-id=return] [data-signature-name]')).to_have_value(late);p.locator('[data-detail-cancel]').click();f.checked('cold restores the later return label against the saved function hash without clearing or replacing its text')
  f.owner().locator('[data-element-action=save]').click();saved(0);x.labels[0]=late;x.verify(checkpoint);review=d.review();review.locator('[data-reject]').click();x.unchanged();review=d.review()
  if review.locator('[data-review-advanced]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  review.locator('#confirm').click();expect(review).to_have_count(0);restart(2);assert not d.pending();x.verify_live();x.verify_pins(f.owner(),0);f.checked('second explicit Save and new Review/Confirm publish the later label only; original native program still executes46');assert not f.errors and not f.external;f.browser.close()
except Exception:
 try:f.page.screenshot(path=str(f.case/'late-failure.png'))
 except Exception:pass
 (f.case/'late-failure.json').write_text(json.dumps(dict(traffic=f.traffic[-60:],checks=f.checks),ensure_ascii=False,indent=2));raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
