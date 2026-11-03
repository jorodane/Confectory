"""Authored wrapper controls with explicit public result and durable private input."""
import copy,json,sys
from playwright.sync_api import sync_playwright,expect
import v666_root_execution_wrapper_fixture as x
f=x.f;mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
def panel():return f.author()
def pending():return f.pending()['blueprint']
def held():return json.loads(next(v['text'] for _,v in pending() if v['type']=='wrapper'))
def card():return panel().locator('[data-bp-node=invoke]')
def focus():panel().locator('[data-bp-overview-node=invoke]').click()
def open_graph(feature):
 f.idle();f.page.locator('#workspace').click(button='right',position={'x':1300,'y':300});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.get_by_role('button',name='기능',exact=True).click();b.locator('[data-browser-control=object-query]').fill(feature.split('::')[-1]);b.locator('[data-browser-control=object-search]').click();b.locator('[data-object="'+feature+'"]').press('Enter');b.locator('[data-close]').first.click();f.idle();f.page.locator('[data-operation=feature-author-open]').first.click();expect(panel().locator('[data-bp-node]')).not_to_have_count(0)
def restart(i):
 f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});f.idle();expect(panel()).to_be_visible()
def modal():focus();card().locator('[data-wrapper-edit]').click();return f.page.get_by_role('dialog',name='분기 기능 편집 · Flow',exact=True)
def edit(d,text,region='body'):
 el=d.locator('[data-code-source]');el.evaluate('(el,key)=>{const spans=[...el.closest(".bp-script-editor").querySelectorAll("[data-code-highlight]>span")],p=spans.find(p=>p.dataset.codeRegion===key);if(!p)throw Error("missing source region");const start=spans.slice(0,spans.indexOf(p)).reduce((n,p)=>n+p.textContent.length,0);el.setSelectionRange(start,start+p.textContent.length)}',region);f.page.keyboard.insert_text(text)
def save():panel().locator('[data-bp-save]').click();expect(panel().locator('.bp-status')).to_have_text('저장됨',timeout=90000);f.idle()
def review():
 panel().locator('[data-bp-complete]').click();f.page.locator('.window[data-key=review]:visible,.window[data-key=targets]:visible').first.wait_for(state='visible',timeout=90000);t=f.page.locator('.window[data-key=targets]')
 if t.is_visible():t.locator('[data-target-choice]').select_option('portable');t.locator('[data-close]').click();panel().locator('[data-bp-complete]').click()
 r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=90000)
 if r.locator('[data-review-advanced]').is_visible():r.locator('[data-review-advanced]').click();r.locator('[data-advanced-reviewed]').check()
 return r
try:
 f.start(0);f.invoke('select',{'id':f.n+'Main'});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph(f.n+'Main');focus();expect(card().locator('[data-bp-wrap-call]')).to_be_enabled();card().locator('[data-bp-wrap-call]').click();v=held();assert v['originalExecution'] and {m['id'] for m in v['executionEnum']['members']}>= {'none','success','failure'};assert v['executionEnum']['primary']=='none';assert len({m['value'] for m in v['executionEnum']['members']})==len(v['executionEnum']['members']);x.original();assert checkpoint.read_bytes()==before
  panel().locator('.bp-viewport').press('Control+z');assert not pending();panel().locator('.bp-viewport').press('Control+y');assert held()==v;f.checked('원본 wrapper 버튼은 공개 ID·분기를 자체 enum에 유지하고 private Undo/Redo는 원문과 checkpoint를 쓰지 않는다')
  d=modal();assert 'InvokeExecution' in d.locator('[data-code-source]').input_value();edit(d,'None = 0, Duplicate = 0,','enum');d.locator('[data-code-save]').click();expect(d.locator('[data-code-error]')).to_be_visible();d.locator('[data-code-cancel]').click();assert held()==v
  body='global::System.Console.WriteLine("wrapper:"+(int)originalBranch+":"+context.result);\n'+v['source'];d=modal();edit(d,body);d.locator('[data-code-save]').click();held_before=copy.deepcopy(pending());restart(1);assert pending()==held_before and held()['source']==body;d=modal();assert body in d.locator('[data-code-source]').input_value();d.locator('[data-code-cancel]').click();x.original();f.checked('고정 OriginalResult/출력과 편집 enum·C#을 구별하고 잘못된 enum·취소·강제 cold에서도 원본과 새 입력을 보존한다')
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:panel().locator('[data-bp-save]').click();f.idle();assert pending() and checkpoint.read_bytes()==before;x.original()
   finally:checkpoint.chmod(0o600)
   restart(2);f.checked('실제 checkpoint 권한 실패는 전체 미적용하며 재시작 입력을 보존한다')
  if mode=='conflict':
   path=f.project/'Flow.celem';path.write_bytes(x.physical[path]+b' ')
   try:panel().locator('[data-bp-save]').click();f.idle();assert pending() and checkpoint.read_bytes()==before
   finally:path.write_bytes(x.physical[path])
   x.original();f.checked('원본 함수의 Save 전 경합은 전체 미적용하고 wrapper C# 입력을 보존한다')
  if mode in ['loss','late']:
   requests=set();queries=set();paused={};lost=[]
   def interrupt(route):
    q=route.request.post_data_json
    if q.get('op')=='invoke' and q.get('endpoint')=='blueprint':
     action=q.get('input',{}).get('action')
     if action=='authorBatch':requests.add(q['requestId'])
     elif requests and action=='settledAuthorBatch':queries.add(q['requestId'])
    response=route.fetch();data=response.json()
    if mode=='late' and not paused and any(r.get('ok') and r.get('requestId') in requests for r in data.get('results',[])):paused.update(route=route,response=response);return
    if mode=='loss':
     for r in data.get('results',[]):
      if r['requestId'] in requests|queries:key=r['requestId'];lost.append(key);r.clear();r.update(requestId=key,ok=False,error={'code':'transport-interrupted'})
    route.fulfill(response=response,json=data)
   f.page.route('**/api/request',interrupt);panel().locator('[data-bp-save]').click()
   for _ in range(1000):
    if paused or requests and any(key in queries for key in lost):break
    f.page.wait_for_timeout(30)
   assert len(requests)==1
   if mode=='late':
    assert paused;d=modal();edit(d,body+'\r\n// 늦게 입력한 C#');d.locator('[data-code-save]').click();paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',interrupt);f.idle();restart(3);assert held()['source'].endswith('// 늦게 입력한 C#');mark=len(f.traffic);panel().locator('[data-bp-save]').click();f.idle();assert pending() and not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for r in f.traffic[mark:]);save();f.checked('늦은 C#은 cold 뒤 기존 receipt만 먼저 확인하고 별도 명시 Save로 보존한다')
   else:
    assert any(key in queries for key in lost) and pending();f.page.unroute_all(behavior='wait');restart(3);mark=len(f.traffic);save();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for r in f.traffic[mark:]);f.checked('저장 응답 유실과 cold receipt 조회는 wrapper 후보를 중복 적용하지 않는다')
  else:save()
  assert not pending();x.original();n=next(n for n in x.read(x.caller)['nodes'] if n['id']=='invoke');assert n['postCall']['originalExecution'] and n['postCall']['source'].startswith(body);f.checked('Save는 명시 실행/출력 receipt와 C#·자체 분기·기존 연결을 한 후보/checkpoint에 저장한다')
  r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();x.original();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();x.build('ui-public-wrapper');x.preserved();f.checked('Review 취소와 최종 Confirm을 구분하며 원본 한번→출력 snapshot→자체 분기→기존 반환을 실제 실행한다')
  restart(4);assert x.read(x.caller)['diagnostics']['state']=='source-ready';assert next(n for n in x.read(x.caller)['nodes'] if n['id']=='invoke')['postCall']['originalExecution'];f.checked('확정 후 cold는 공개 OriginalResult·데이터·연결과 원래 C#을 보존한다');
  if mode=='normal':
   before_row=next(n for n in x.read(x.caller)['nodes'] if n['id']=='invoke');open_graph(x.feature);source_checkpoint=checkpoint.read_bytes();name=panel().locator('[data-root-branch="success"] [data-root-branch-name]');name.fill('직접 확인한 성공 계약');name.press('Tab');panel().locator('[data-bp-save]').click();f.idle();assert pending() and checkpoint.read_bytes()==source_checkpoint
   option=x.caller+'|node:invoke';panel().locator('[data-root-wrappers]').select_option(option);selection=copy.deepcopy(pending());restart(5);assert pending()==selection;save();n=next(n for n in x.read(x.caller)['nodes'] if n['id']=='invoke');assert n['postCall']['source']==before_row['postCall']['source'] and n['executionEnum']==before_row['executionEnum'] and n['postCall']['originalExecution']!=before_row['postCall']['originalExecution'];r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();x.build('ui-public-wrapper-root-update');assert (f.project/'Flow.node.json').read_bytes()==x.physical[f.project/'Flow.node.json'];assert (f.project/'After.node.json').read_bytes()==x.physical[f.project/'After.node.json'];f.checked('원본 계약 화면은 모든 공개 결과 wrapper의 명시 선택을 요구하며 cold·Save·전체 Review/CAS 뒤 자체 enum·C#·연결·실행을 보존한다')
  f.page.screenshot(path=str(f.case/'public-wrapper-final.png'),full_page=True);assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except Exception:
 try:(f.case/'failure-state.json').write_text(json.dumps(f.state(),ensure_ascii=False));f.page.screenshot(path=str(f.case/'public-wrapper-failure.png'),timeout=5000)
 except Exception:pass
 raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2));f.stop()
print('M12_PUBLIC_WRAPPER_FIXTURE '+str(f.case),flush=True)
