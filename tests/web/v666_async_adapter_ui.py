"""원본 메뉴·원문/선택기 두 영역·취소/반복/cold·원자 저장 UI."""
import copy,json,sys
from playwright.sync_api import sync_playwright,expect
import v666_async_adapter_fixture as x
f=x.f;mode=sys.argv[3]if len(sys.argv)>3 else 'normal'
def panel():return f.author()
def pending():return f.pending()['blueprint']
def retained(held):return all(dict(pending()).get(k)==v for k,v in held)
def open_graph():
 f.idle()
 if panel().is_visible()and panel().locator('[data-bp-node=choose]').count():return
 f.page.locator('#workspace').click(button='right',position={'x':1300,'y':300});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.get_by_role('button',name='기능',exact=True).click();b.locator('[data-browser-control=object-query]').fill('Flow');b.locator('[data-browser-control=object-search]').click();b.locator('[data-object="'+x.feature+'"]').press('Enter');b.locator('[data-close]').first.click();f.idle();f.page.locator('[data-operation=feature-author-open]').first.click();expect(panel().locator('[data-bp-node=choose]')).to_be_visible()
def toggle():
 panel().locator('[data-bp-node=choose] .function-node-heading').click(button='right');f.page.locator('[data-bp-async=choose]').click()
def save():
 panel().locator('[data-bp-save]').click();expect(panel().locator('.bp-status')).to_have_text('저장됨',timeout=90000);f.idle()
def restart(i):
 f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});f.idle();open_graph();expect(panel()).to_be_visible()
def review():
 panel().locator('[data-bp-complete]').click();f.page.locator('.window[data-key=review]:visible,.window[data-key=targets]:visible').first.wait_for(state='visible',timeout=90000);t=f.page.locator('.window[data-key=targets]')
 if t.is_visible():t.locator('[data-target-choice]').select_option('portable');t.locator('[data-close]').click();panel().locator('[data-bp-complete]').click()
 r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=90000);a=r.locator('[data-review-advanced]')
 if a.is_visible():a.click();r.locator('[data-advanced-reviewed]').check()
 return r
def confirm():
 r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle()
def editor():
 panel().locator('[data-bp-node=choose] [data-internal-code]').click();d=f.page.locator('.bp-script-dialog');expect(d).to_be_visible();return d
def replace(d,before,after):
 value=d.locator('[data-code-source]');assert before in value.input_value();value.evaluate('(el,text)=>{el.focus();const i=el.value.indexOf(text);el.setSelectionRange(i,i+text.length)}',before);f.page.keyboard.insert_text(after)
try:
 f.start(0);f.invoke('select',{'id':x.feature});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph();toggle();expect(panel().locator('[data-bp-node=choose] .function-async-clock')).to_have_count(0);expect(panel().locator('[data-bp-node=choose] [data-port=completion]')).to_be_visible();held=copy.deepcopy(pending());assert held;panel().locator('.bp-viewport').press('Control+z');assert not pending();panel().locator('.bp-viewport').press('Control+y');assert pending()==held;x.original();assert checkpoint.read_bytes()==before;restart(1);assert pending()==held;save();assert not pending();assert x.selected()['completionAdapter']['source']=='return Result.None;';r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();x.original();confirm();x.build('ui-none');x.code_unchanged();f.checked('메뉴/Undo/Redo/cold/Review 취소·확정은 출력·원문·완료 연결을 보존하고 None을 암묵 선택하지 않는다')
  d=editor();text=d.locator('[data-code-source]').input_value();assert 'public static long Execute(long amount, out int result)'in text and 'SourceContext'in text and 'public static int Result()'in text;replace(d,'return Result.None;',x.selection());d.locator('[data-code-cancel]').click();assert not pending();d=editor();assert 'return Result.None;'in d.locator('[data-code-source]').input_value();replace(d,'return Result.None;',x.selection());
  # Force the existing window-close event while its modal owns pointer focus.
  panel().locator('[data-close]').first.evaluate('(button)=>button.click()');expect(d).to_be_hidden();assert pending();held=copy.deepcopy(pending());restart(2);restored=pending();assert [v for _,v in restored]==[v for _,v in held] and all(k.endswith('|choose|completion-code')for k,_ in restored);open_graph();d=editor();assert x.selection()in d.locator('[data-code-source]').input_value();d.locator('[data-code-save]').click();held=copy.deepcopy(pending());before=checkpoint.read_bytes();x.code_unchanged();f.checked('두 코드 영역과 고정 서명/helper·readonly snapshot을 표시하고 취소/창 닫기/cold에서 선택기 입력을 보존한다')
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:panel().locator('[data-bp-save]').click();f.idle();assert retained(held)and checkpoint.read_bytes()==before;x.code_unchanged()
   finally:checkpoint.chmod(0o600)
   restart(3);f.checked('checkpoint 실패는 선택기 입력과 원래 C# bytes를 보존한다')
  if mode=='conflict':
   path=f.project/'After.node.json';old=path.read_bytes();path.write_bytes(old+b' ')
   try:panel().locator('[data-bp-save]').click();f.idle();assert retained(held)and checkpoint.read_bytes()==before
   finally:path.write_bytes(old)
   f.checked('다른 호출자 원문 경합은 후보와 늦지 않은 사용자 입력을 보존한다')
  if mode in ['loss','late']:
   requests=set();queries=set();paused={};lost=[]
   def interrupt(route):
    data=route.request.post_data_json
    if data.get('op')=='invoke'and data.get('endpoint')=='blueprint':
     action=data.get('input',{}).get('action')
     if action=='authorBatch':requests.add(data['requestId'])
     elif requests and action=='settledAuthorBatch':queries.add(data['requestId'])
    response=route.fetch();payload=response.json()
    if mode=='late'and not paused and any(r.get('ok')and r.get('requestId')in requests for r in payload.get('results',[])):paused.update(route=route,response=response);return
    if mode=='loss':
     for r in payload.get('results',[]):
      if r['requestId']in requests|queries:rid=r['requestId'];lost.append(rid);r.clear();r.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',interrupt);panel().locator('[data-bp-save]').click()
   for _ in range(1000):
    if paused or requests and any(r in queries for r in lost):break
    f.page.wait_for_timeout(30)
   assert len(requests)==1
   if mode=='late':
    assert paused;d=editor();replace(d,x.selection(),'return Result.None;');d.locator('[data-code-save]').click();paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',interrupt);f.idle();assert pending();restart(4);mark=len(f.traffic);panel().locator('[data-bp-save]').click();f.idle();assert pending();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch'for r in f.traffic[mark:]);save();assert x.selected()['completionAdapter']['source']=='return Result.None;';d=editor();replace(d,'return Result.None;',x.selection());d.locator('[data-code-save]').click();save();f.checked('늦은 새 선택기 입력은 이전 응답/cold 조회에 덮어쓰이지 않으며 별도 Save로 확정한다')
   else:
    assert any(r in queries for r in lost)and pending();f.page.unroute_all(behavior='wait');restart(4);mark=len(f.traffic);save();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch'for r in f.traffic[mark:]);f.checked('유실 응답은 cold에서 같은 배치를 조회해 중복 저장 없이 회복한다')
  else:save()
  assert not pending();x.code_unchanged();confirm();x.build('ui-explicit',True);x.code_unchanged();assert x.read()['edges']==x.initial_edges;f.checked('확정 후 선택기만 다시 원자 저장해 출력→명시 완료→다음 순서를 실행하고 원문 CRLF/helper를 보존한다');restart(5);assert x.selected()['completionAdapter']['source']==x.selection();assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'adapter-final.png'),full_page=True);f.browser.close()
except Exception:
 (f.case/'failure-details.json').write_text(json.dumps({'errors':f.errors,'checks':f.checks},ensure_ascii=False,indent=2))
 raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2));f.stop()
print('ASYNC_ADAPTER_FIXTURE',f.case,flush=True)
