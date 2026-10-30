"""M11 원본 내부 흐름 진입: private 미리보기/Undo/cold/Save/Review/Confirm."""
import json,sys,time,copy,shutil
from playwright.sync_api import sync_playwright,expect
import v666_node_internal_api as x
f=x.f;mode=sys.argv[3] if len(sys.argv)>3 else 'normal';feature=x.feature;graph=x.graph;child=x.child

def original():x.original()
def data(id=graph):return x.read(id)
def panel():return f.author()
def pending():return f.pending()['blueprint']
def open_graph():
 f.idle()
 if panel().is_visible():return
 f.page.locator('#workspace').click(button='right',position={'x':1300,'y':300});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.get_by_role('button',name='기능',exact=True).click();b.locator('[data-browser-control=object-query]').fill('Flow');b.locator('[data-browser-control=object-search]').click();b.locator('[data-object="'+feature+'"]').press('Enter');b.locator('[data-close]').first.click();f.idle();f.page.locator('[data-operation=feature-author-open]').first.click();expect(panel().locator('[data-bp-node=calculate]')).to_be_visible()
def enter():
 panel().locator('[data-bp-node=calculate] [data-internal-flow]').click();expect(panel().locator('[data-bp-node=body]')).to_be_visible();expect(panel().locator('.bp-status')).to_contain_text('미리보기')
def code(text=None,cancel=False):
 panel().locator('[data-bp-node=body] [data-internal-code]').click();p=f.page.get_by_role('dialog',name='C# Script · body',exact=True);editor=p.locator('[data-code-source]');
 raw=editor.input_value();source=p.locator('[data-code-region=body]').text_content();assert source in raw
 if text is not None:
  editor.evaluate('(el,text)=>{const at=el.value.indexOf(text);if(at<0)throw Error("body not found");el.focus();el.setSelectionRange(at,at+text.length)}',source);f.page.keyboard.insert_text(text);assert text in editor.input_value()
 p.locator('[data-code-cancel]' if cancel else '[data-code-save]').click();return p

def restart(i):
 f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});f.idle();expect(panel()).to_be_visible()
def save():
 panel().locator('[data-bp-save]').click();expect(panel().locator('.bp-status')).to_have_text('저장됨',timeout=90000);f.idle()
def review():
 panel().locator('[data-bp-complete]').click();f.page.locator('.window[data-key=review]:visible,.window[data-key=targets]:visible').first.wait_for(state='visible',timeout=90000);t=f.page.locator('.window[data-key=targets]')
 if t.is_visible():t.locator('[data-target-choice]').select_option('portable');t.locator('[data-close]').click();panel().locator('[data-bp-complete]').click()
 r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=90000);advanced=r.locator('[data-review-advanced]')
 if advanced.is_visible():advanced.click();r.locator('[data-advanced-reviewed]').check()
 return r
try:
 f.start(0);f.invoke('select',{'id':feature});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph();enter();original();assert checkpoint.read_bytes()==before;panel().locator('.bp-viewport').press('Control+z');expect(panel().locator('[data-bp-node=calculate]')).to_be_visible();panel().locator('.bp-viewport').press('Control+y');expect(panel().locator('[data-bp-node=body]')).to_be_visible();original();f.checked('원본 내부 흐름 버튼과 미저장 단일 코드 래핑·Undo/Redo는 원문과 바깥 실행선을 보존한다')
  code('return amount+8;',True);assert not pending();code('return amount+8;');assert len(pending())==1;original();assert checkpoint.read_bytes()==before;f.checked('C# 대화상자 취소/적용은 단일 내부 노드 입력만 보관하고 활성 구현·원문 파일을 쓰지 않는다')
  restart(1);expect(panel().locator('[data-bp-node=body]')).to_be_visible();assert pending();held=copy.deepcopy(pending());panel().locator('.bp-viewport').press('Control+z');expect(panel().locator('[data-bp-node=calculate]')).to_be_visible();assert not pending();panel().locator('.bp-viewport').press('Control+y');expect(panel().locator('[data-bp-node=body]')).to_be_visible();assert pending()==held;original();f.checked('cold 복원과 취소/재실행은 같은 프로젝트·원본 증거로 미리보기를 다시 준비하며 입력을 보존한다')
  if mode=='project':
   held=copy.deepcopy(pending());other=f.case/'same IDs other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory'));f.pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(other/'project.cproj');f.start(10);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph();assert not pending();expect(panel().locator('[data-bp-node=calculate]')).to_be_visible();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(x.manifest);f.start(11);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});f.idle();expect(panel().locator('[data-bp-node=body]')).to_be_visible();assert pending()==held;original();f.checked('같은 namespace/ID의 프로젝트 왕복은 원래 전환 의도와 미저장 C#을 섞지 않는다')
  # Returning to Root is the same original breadcrumb path; Save captures the child.
  if mode!='late':panel().locator('.bp-breadcrumbs button').first.click();expect(panel().locator('[data-bp-node=calculate]' if mode!='late' else '[data-bp-node=body]')).to_be_visible();assert pending();original();f.checked('Root 왕복은 아직 생성되지 않은 내부 소스를 공유 초안으로 조기 적용하지 않는다')
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:
    panel().locator('[data-bp-save]').click();expect(panel().locator('.bp-status')).not_to_have_text('저장됨');f.idle();assert checkpoint.read_bytes()==before;original();assert pending()
   finally:checkpoint.chmod(0o600)
   restart(2);f.checked('쓰기 실패와 재시작은 모든 입력·원문·checkpoint를 보존한다')
  if mode=='conflict':
   file=f.project/'Flow.node.json';file.write_bytes(x.physical[file]+b' ');x.physical[file]=file.read_bytes();panel().locator('[data-bp-save]').click();f.idle();assert checkpoint.read_bytes()==before and pending();original();f.checked('물리 원문 충돌은 미적용 상태로 입력을 유지한다')
  else:
   if mode=='late':
    ids=set();paused={}
    def hold(route):
     body=route.request.post_data_json
     if body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and body.get('input',{}).get('action')=='authorBatch':ids.add(body['requestId'])
     response=route.fetch();payload=response.json()
     if not paused and any(v.get('ok') and v.get('requestId') in ids for v in payload.get('results',[])):paused.update(route=route,response=response);return
     route.fulfill(response=response)
    f.page.route('**/api/request',hold);panel().locator('[data-bp-save]').click()
    for _ in range(1000):
     if paused:break
     f.page.wait_for_timeout(30)
    assert paused and len(ids)==1;code('return amount+9;');paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',hold);f.idle();assert pending() and pending()[0][1]['text']=='return amount+9;';original();restart(3);save();f.checked('저장 중 늦은 C# 입력은 수락한 후보 기준으로 보존하고 cold 뒤 별도 Save로 반영한다')
   elif mode=='loss':
    applies=set();queries=set();lost=[]
    def interrupt(route):
     body=route.request.post_data_json
     if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
      action=body.get('input',{}).get('action')
      if action=='authorBatch':applies.add(body['requestId'])
      elif applies and action=='settledAuthorBatch':queries.add(body['requestId'])
     response=route.fetch();payload=response.json()
     for v in payload.get('results',[]):
      if v['requestId'] in applies|queries:rid=v['requestId'];lost.append(rid);v.clear();v.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
     route.fulfill(response=response,json=payload)
    f.page.route('**/api/request',interrupt);panel().locator('[data-bp-save]').click()
    for _ in range(1000):
     if applies and any(r in queries for r in lost):break
     f.page.wait_for_timeout(30)
    assert len(applies)==1 and any(r in queries for r in lost) and pending();f.page.unroute_all(behavior='wait');restart(3);mark=len(f.traffic);save();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for r in f.traffic[mark:]);f.checked('저장/조회 응답 유실 후 cold receipt 조회로 중복 래핑 없이 복구한다')
   else:save()
   assert not pending();assert data(child)['diagnostics']['state']=='source-ready';assert next(n for n in data(child)['nodes'] if n['id']=='body')['source']==('return amount+9;' if mode=='late' else 'return amount+8;');original();f.checked('Root Save는 부모 graph와 내부 C#을 하나의 후보로 저장하고 원본 보존 guard와 묶는다')
   r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();original();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();assert (f.project/'Flow.node.json').read_bytes()==x.physical[f.project/'Flow.node.json'];x.build('ui-after',12 if mode=='late' else 11);f.checked('Review 취소와 컴파일 Confirm을 구분하며 원문을 그대로 보존한 새 활성 내부 C#을 실행한다')
   restart(4);assert data(child)['diagnostics']['state']=='source-ready';f.checked('최종 반영 뒤 재시작도 내부 동작과 원문 보관을 유지한다')
  assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'node-internal-final.png'),full_page=True);f.browser.close()
except Exception:
 try:f.page.screenshot(path=str(f.case/'node-internal-failure.png'),timeout=5000)
 except Exception:pass
 raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2));f.stop()
print('M11_FIXTURE '+str(f.case),flush=True)
