"""An actual child-name edit during a held Save response retains its own input."""
import copy,json,time
from playwright.sync_api import sync_playwright,expect
import v666_owned_creation_fixture as x
f,d=x.f,x.d;late='응답 중 새 힘 이름';late_value=9223372036854775803;applies=set();held=[]
def restart(index):
 f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(index);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});d.open_info();f.idle()
def receipt():return next(v for v in json.loads(checkpoint.read_text())['changes']if v['id']==x.owner)['slotSaveReceipt']
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();d.open_info()
  for index,fn in enumerate(x.functions):
   f.owner().locator('[data-inline-method="'+fn+'"] > .function-node-heading').dblclick(position={'x':190,'y':3});popup=f.page.locator('.function-detail-popover');expect(popup).to_be_visible();x.edit_contract(popup,index);popup.get_by_role('button',name='저장',exact=True).click();expect(popup).to_have_count(0);x.after_contract(index)
  assert len(d.pending())==5
  def intercept(route):
   body=route.request.post_data_json
   if body.get('op')=='invoke'and body.get('endpoint')=='blueprint'and body.get('input',{}).get('action')=='applySlots':applies.add(body['requestId'])
   response=route.fetch();payload=response.json()
   if not held and any(v.get('ok')and v.get('requestId')in applies for v in payload.get('results',[])):
    held.append(dict(requestIds=sorted(applies),response=payload));x.expanded(x.own());x.direct(x.tree_rows(x.own()).first,'data-property-name').fill(late);x.tree_rows(x.own()).first.locator(':scope>.property-content-box>.object-property-default>[data-property-value]').fill(str(late_value))
   route.fulfill(response=response)
  f.page.route('**/api/request',intercept);f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+120
  while time.monotonic()<deadline:
   cells=d.pending()
   if held and len(cells)==1 and cells[0][1].get('kind')=='owned-definition'and cells[0][1].get('copySavedBasis'):break
   f.page.wait_for_timeout(100)
  else:raise AssertionError('Late owned input did not settle with its saved basis')
  f.page.unroute_all(behavior='wait');assert len(applies)==1;x.verify(checkpoint);before=copy.deepcopy(receipt());cells=d.pending();assert cells[0][1]['tree']['fields'][0]['name']==late;x.unchanged();f.checked('a held successful mixed Save preserves the later real child name with its saved basis, while the captured group and exact values are stored once')
  (f.case/'late-owned-observation.json').write_text(json.dumps(dict(held=held,pending=cells,receipt=before),ensure_ascii=False,indent=2));restart(1);assert d.pending()==cells;x.verify(checkpoint);x.expanded(x.own());expect(x.direct(x.tree_rows(x.own()).first,'data-property-name')).to_have_value(late);saved_checkpoint=checkpoint.read_bytes()
  if x.mode=='owned-peer':
   sc=f.state()['schema'];f.invoke('editDescription',dict(id=x.owner,hash=sc['textHash'],revision=sc['revision'],value='peer owns this declaration'));f.idle();button=f.owner().locator('[data-element-action=save]')
   if not button.is_disabled():button.click()
   f.page.wait_for_function("()=>document.querySelector('[data-element-action=save]')?.disabled||[...document.querySelectorAll('[data-element-error],#status')].some(el=>/바뀌|입력.*유지|확인.*주세요|실패/.test(el.textContent))",timeout=30000);f.idle();assert d.pending()==cells and checkpoint.read_bytes()==saved_checkpoint and f.metadata('inspect',text=f.state()['draft']['text'])['description']=='peer owns this declaration';x.unchanged();f.checked('late child name/value cannot rebase a peer-changed owner; the checkpoint, original read scope, peer text and every input survive');f.browser.close();raise SystemExit(0)
  mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+120;reply=None
  while time.monotonic()<deadline:
   ids={r['invoke']['requestId']for r in f.traffic[mark:]if r.get('invoke',{}).get('endpoint')=='blueprint'and r['invoke']['input'].get('action')=='applySlots'};rows=[r['result']for r in f.traffic[mark:]if r.get('result',{}).get('requestId')in ids and r['result'].get('error',{}).get('code')!='stale_revision']
   if rows:reply=rows[-1];break
   f.page.wait_for_timeout(100)
  assert reply is not None;f.idle();(f.case/'owned-followup-reply.json').write_text(json.dumps(reply,ensure_ascii=False,indent=2))
  if x.mode.startswith('diagnose-late-owned'):
   assert reply['ok']is False and d.pending()==cells and checkpoint.read_bytes()==saved_checkpoint;x.unchanged();f.checked('the later child input survives cold and the current unsupported follow-up rejects without rebasing, erasing input or altering its saved native group');f.browser.close();raise SystemExit(0)
  assert reply['ok']is True and not d.pending();x.power_label=late;x.power_value=late_value;ids=x.verify(checkpoint);after=receipt();old_plan=next(v for v in before['nativeBodyOwnerEdits']if v['type']=='owned-definition');new_plan=next(v for v in after['nativeBodyOwnerEdits']if v['type']=='owned-definition');assert after['readGuards']==before['readGuards']and after['nativeBodyOwnerReads']==before['nativeBodyOwnerReads'];assert old_plan['sources']==new_plan['sources']and old_plan['schemaHash']==new_plan['schemaHash']and old_plan['contract']==new_plan['contract'] and new_plan['tree']['fields'][0]['name']==late and json.loads(new_plan['valueJson'])[x.power_key]==late_value;x.unchanged();f.checked('explicit child-name/value follow-up retains original read versions and owned source/contract proof while validating the exact64 value under the same field identities and types')
  review=d.review();review.locator('[data-reject]').click();x.unchanged();review=d.review()
  if review.locator('[data-review-advanced]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  review.locator('#confirm').click();expect(review).to_have_count(0);restart(2);assert not d.pending();x.verify_live();f.checked('fresh explicit Review/Confirm publishes the later child name with both native plans, preserving named definitions, exact values and original registration');assert not f.errors and not f.external;f.browser.close()
except Exception:
 try:f.page.screenshot(path=str(f.case/'owned-late-failure.png'))
 except Exception:pass
 (f.case/'owned-late-failure.json').write_text(json.dumps(dict(traffic=f.traffic[-60:],checks=f.checks),ensure_ascii=False,indent=2));raise
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
