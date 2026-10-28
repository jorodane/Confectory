"""Original private Script enum/body/helpers, real author batch and explicit Confirm."""
import json,time
from playwright.sync_api import sync_playwright,expect
import v536_information_nested_fixture as x
f=x.f
source=x.record_sources['left'].replace('\r\n','\n').replace('Result.Next','Result.Renamed');helpers=x.code_helpers.replace('\r\n','\n')
def author():return f.page.locator('.window[data-key=blueprint]')
def dialog():return f.page.locator('.bp-script-dialog')
def open_code():
 author().locator('[data-flow-node=body]').click();f.page.locator('.bp-flow-inspector:not([hidden]) [data-flow-code]').click();expect(dialog()).to_be_visible();return dialog().locator('[data-code-source]')
def fields(field):
 field.evaluate(r"el=>{const p=el.value.indexOf(' Execute('),a=el.value.indexOf('\n{\n',p)+3,b=el.value.indexOf('\n}\n',a);el.focus();el.setSelectionRange(a,b);}");f.page.keyboard.insert_text(source)
 field.evaluate(r"el=>{const p=el.value.indexOf(' Execute('),a=el.value.indexOf('\n{\n',p)+3,b=el.value.indexOf('\n}\n',a)+3;el.focus();el.setSelectionRange(b,el.value.length);}");f.page.keyboard.insert_text(helpers)
 field.evaluate(r"el=>{const a=el.value.indexOf('\n{\n')+3,b=el.value.indexOf('\n}\n',a);el.focus();el.setSelectionRange(a,b);}");f.page.keyboard.insert_text('    Renamed = 7,\n    Done = 0,')
try:
 f.start(0);f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes()
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});f.page.locator('#workspace').click(button='right',position={'x':900,'y':400});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=feature]').click();b.locator('[data-object="'+x.caller+'"]').press('Enter');f.idle();f.page.locator('.window[data-key=declaration] [data-function-write-direct]').click();expect(author().locator('[data-bp-node=left]')).to_be_visible();f.page.set_viewport_size({'width':390,'height':844});author().locator('[data-flow-node=left]').click();f.page.locator('.bp-flow-inspector:not([hidden]) [data-flow-internal]').click();expect(author().locator('[data-flow-node=body]')).to_be_visible();f.idle()
  field=open_code();fields(field);dialog().locator('[data-code-cancel]').click();assert not f.pending()['blueprint'];f.page.locator('.bp-flow-inspector:not([hidden]) [data-flow-done]').click();field=open_code();fields(field);dialog().locator('[data-code-save]').click();f.page.locator('.bp-flow-inspector:not([hidden]) [data-flow-done]').click();held=f.pending()['blueprint'];assert len(held)==1 and held[0][1]['type']=='enum-code';f.pending();f.page.close();f.stop();f.start(1);f.page=f.setup();f.page.set_viewport_size({'width':390,'height':844});f.idle();expect(author().locator('[data-flow-node=body]')).to_be_visible();assert f.pending()['blueprint']==held
  if x.mode=='loss':
   checkpoint.chmod(0o400)
   try:
    mark=len(f.traffic);author().locator('[data-bp-save]').click();f.page.wait_for_function("()=>{const t=document.querySelector('.window[data-key=blueprint] .bp-status')?.textContent;return t&&!['저장됨','저장 중…','미저장 초안'].includes(t)}");assert checkpoint.read_bytes()==baseline and any(v.get('type')=='enum-code' for k,v in f.pending()['blueprint']);assert all((f.project/p).read_bytes()==v for p,v in x.snapshot.items())
   finally:checkpoint.chmod(0o600)
   applied,queried,masked=set(),set(),set()
   def intercept(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
     action=body.get('input',{}).get('action')
     if action=='authorBatch':applied.add(body['requestId'])
     elif applied and action=='settledAuthorBatch':queried.add(body['requestId'])
    response=route.fetch();payload=response.json()
    for row in payload.get('results',[]):
     if row['requestId'] in applied|queried:
      rid=row['requestId'];masked.add(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport_lost'})
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',intercept);author().locator('[data-bp-save]').click();deadline=time.monotonic()+90
   while time.monotonic()<deadline and not queried&masked:f.page.wait_for_timeout(20)
   assert len(applied)==1 and queried&masked;f.page.unroute_all(behavior='wait');held=f.pending();f.page.close();f.stop();f.start(2);f.page=f.setup();f.page.set_viewport_size({'width':390,'height':844});f.idle();assert f.pending()==held
   mark=len(f.traffic);author().locator('[data-bp-save]').click();expect(author().locator('.bp-status')).to_have_text('저장됨',timeout=120000);assert not any(t.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for t in f.traffic[mark:]);f.checked('private enum 저장 실패는 전체 미적용·입력 보존이며 응답 유실·cold 뒤 원래 source binding의 receipt 조회로 중복 저장을 막는다')
  else:author().locator('[data-bp-save]').click();expect(author().locator('.bp-status')).to_have_text('저장됨',timeout=120000)
  assert not f.pending()['blueprint'];data=f.invoke('blueprint',{'action':'read','id':x.caller_id+'/graph:left'})['result']['result'];node=next(n for n in data['nodes'] if n['id']=='body');assert node['source']==source and node['helpers']==helpers and [(m['id'],m['name']) for m in node['executionEnum']['members']]==[('next','Renamed'),('done','Done')];assert all((f.project/p).read_bytes()==v for p,v in x.snapshot.items());f.checked('원본 private enum/본문/helper의 취소·순서/이름·cold·단일 root저장은 기존 포트 식별성과 원문을 보존한다')
  author().locator('[data-bp-complete]').click();review=f.page.locator('.window[data-key=review]');expect(review).to_be_visible();review.locator('[data-reject]').click();f.idle()
  if not author().is_visible():f.page.locator('[data-tab-order-key="window:blueprint"] [role=tab]').click()
  author().locator('[data-bp-complete]').click();expect(review).to_be_visible()
  for cb in review.locator('[data-review-id]').all():cb.check()
  if review.locator('[data-review-advanced]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  review.locator('#confirm').click();expect(review).to_have_count(0,timeout=120000);assert json.loads((f.project/'left.node.json').read_text())['source']==source;assert (f.project/'right.node.json').read_bytes()==x.snapshot['right.node.json'];f.checked('private enum의 실제 Review 취소·재검토·Confirm은 소유 leaf만 함께 반영하고 형제·부모를 보존한다');f.page.screenshot(path=str(f.case/'private-enum.png'));assert not f.errors and not f.external;f.browser.close()
except Exception:
 try:(f.case/'failure.json').write_text(json.dumps({'state':f.state(),'traffic':f.traffic[-40:]},ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'private-enum-failure.png'))
 except Exception:pass
 raise
finally:
 f.stop();print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngineRenderer':True,'nativeWindowsOrMobile':False},ensure_ascii=False))
