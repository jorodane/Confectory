"""Explicit child body: readonly public contract and parent, editable return cards."""
import ast,copy,json,pathlib,shutil,sys,time
from playwright.sync_api import sync_playwright,expect
import v666_root_execution_override_fixture as c
f=c.f;mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
def panel():return f.author()
helper=pathlib.Path(__file__).with_name('v666_root_execution_ui.py');exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='review'],type_ignores=[]),str(helper),'exec'))
def pending():return f.pending()['blueprint']
def selected():return json.loads(next(v['text'] for _,v in pending() if v['type']=='branch-exits'))
def choose(branch):
 panel().locator('[data-bp-node="$exit:yes"] [data-bp-branch-select]').click();f.page.get_by_role('listbox',name='기존 분기 선택',exact=True).locator('[data-branch-option="'+branch+'"]').click()
def save():
 expected=copy.deepcopy(selected());panel().locator('[data-bp-save]').click();deadline=time.monotonic()+90
 while time.monotonic()<deadline:
  f.page.wait_for_timeout(60)
  if not pending() and '저장 중' not in panel().locator('.bp-status').inner_text():break
 assert not pending(),panel().locator('.bp-status').inner_text();f.idle();rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']};stored=json.loads(rows[c.graph]['draft']);assert {k:stored[k] for k in ['entry','edges','exits']}==expected and rows[c.graph]['publicBodyOrigin']['version']==1 and rows[c.graph]['authorSaveReceipt']['dependencyHash']==c.read()['nodeFlowDependencyHash'];assert c.read()['diagnostics']['state']=='source-ready'
def restart(i):
 held=copy.deepcopy(pending());f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});f.idle();expect(panel()).to_be_visible();assert pending()==held
def open_copy():
 f.idle();f.page.locator('#workspace').click(button='right',position={'x':1300,'y':300});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.get_by_role('button',name='기능',exact=True).click();b.locator('[data-browser-control=object-query]').fill('Flow');b.locator('[data-browser-control=object-search]').click();b.locator('[data-object="'+c.feature+'"]').press('Enter');b.locator('[data-close]').first.click();f.idle();f.page.locator('[data-operation=feature-author-open]').first.click();expect(panel().locator('[data-bp-node=choose]')).to_be_visible()
try:
 f.start(0);f.invoke('select',{'id':c.owner});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_copy();expect(panel().locator('[data-root-branch-add]')).to_be_disabled();expect(panel().locator('[data-root-branch]')).to_have_count(2)
  for row in panel().locator('[data-root-branch]').all():assert row.locator('input').get_attribute('readonly') is not None;expect(row.locator('[data-root-branch-remove]')).to_be_disabled()
  panel().locator('[data-bp-percent]').click();zoom=f.page.get_by_role('dialog',name='노드 화면 배율',exact=True);zoom.locator('[data-zoom-preset="25"]').click();zoom.locator('[data-zoom-value]').press('Escape');panel().locator('[data-bp-node="$exit:yes"] [data-bp-branch-select]').click();f.page.keyboard.press('Escape');assert not pending();choose('failure');held=copy.deepcopy(pending());panel().locator('.bp-viewport').press('Control+z');assert not pending();panel().locator('.bp-viewport').press('Control+y');assert pending()==held
  panel().locator('[data-root-branch="success"] [data-root-branch-place]').click();assert len(selected()['exits'])==4;panel().locator('.bp-viewport').press('Control+z');assert pending()==held;c.original();assert checkpoint.read_bytes()==before;f.checked('자식 본문의 공개 분기 이름/정의는 readonly이며 기존 ID 반환 선택·배치·Undo/Redo·선택 취소는 원본과 계약을 보존한다')
  restart(1);assert pending()==held;c.original()
  if mode=='project':
   other=f.case/'same IDs other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory'));f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(other/'project.cproj');f.start(10);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});f.idle();assert not pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(c.x.manifest);f.start(11);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});f.idle();assert pending()==held;f.checked('같은 namespace/자식/분기 ID의 다른 프로젝트와 왕복해도 반환 입력과 소유 배정을 섞지 않는다')
  if mode=='cancel':panel().locator('.bp-viewport').press('Control+z');panel().locator('.bp-viewport').press('Control+y');assert pending()==held
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:panel().locator('[data-bp-save]').click();f.idle();assert pending() and checkpoint.read_bytes()==before;c.original()
   finally:checkpoint.chmod(0o600)
   restart(2);f.checked('저장 실패와 재시작에서 자식 본문 반환 입력·배정·원문을 보존한다')
  if mode=='conflict':
   file=c.parent_file;c.mutate_parent();c.physical[file]=file.read_bytes();panel().locator('[data-bp-save]').click();f.idle();assert pending() and checkpoint.read_bytes()==before;c.original();restart(6);assert pending() and checkpoint.read_bytes()==before;panel().locator('[data-bp-save]').click();f.idle();assert pending() and checkpoint.read_bytes()==before;c.original();f.checked('부모 원문 경합과 cold 뒤에도 최초 관측/반환 입력을 유지하며 새 부모 관측으로 묵시 재배정하지 않는다')
  else:
   if mode in ['loss','late']:
    applies=set();queries=set();lost=[];paused={}
    def intercept(route):
     request=route.request.post_data_json
     if request.get('op')=='invoke' and request.get('endpoint')=='blueprint':
      if request.get('input',{}).get('action')=='authorBatch':applies.add(request['requestId'])
      elif applies and request.get('input',{}).get('action')=='settledAuthorBatch':queries.add(request['requestId'])
     response=route.fetch();payload=response.json()
     if mode=='late' and not paused and any(v.get('ok') and v.get('requestId') in applies for v in payload.get('results',[])):paused.update(route=route,response=response);return
     for row in payload.get('results',[]):
      if mode=='loss' and row['requestId'] in applies|queries:rid=row['requestId'];lost.append(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
     route.fulfill(response=response,json=payload)
    f.page.route('**/api/request',intercept);panel().locator('[data-bp-save]').click()
    for _ in range(1000):
     if paused or applies and any(v in queries for v in lost):break
     f.page.wait_for_timeout(30)
    assert len(applies)==1
    if mode=='late':
     assert paused;choose('none');paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',intercept);f.idle();assert pending() and selected()['exits']['yes']['executionBranch']=='none';restart(3);mark=len(f.traffic);panel().locator('[data-bp-save]').click();f.idle();assert pending();assert not any(v.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for v in f.traffic[mark:]);save();f.checked('늦은 반환 선택은 cold에서 이전 receipt만 확인하고 두 번째 명시 Save로 별도 반영한다')
    else:
     assert any(v in queries for v in lost);f.page.unroute_all(behavior='wait');f.idle();restart(3);mark=len(f.traffic);save();assert not any(v.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for v in f.traffic[mark:]);f.checked('응답 유실 뒤 cold receipt 조회는 소유 자식 본문 반환을 중복 저장하지 않는다')
   else:save()
   c.original();assert c.read()['diagnostics']['state']=='source-ready';r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();c.original();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();c.originals_retained();stored=json.loads((f.project/c.graph_path).read_text());assert stored['exits']['yes']['executionBranch']==('none' if mode=='late' else 'failure');c.build('copy-ui-after',True,'none' if mode=='late' else 'failure');restart(4);assert c.read()['diagnostics']['state']=='source-ready';c.originals_retained();f.checked('Review 취소/Confirm·확정 후 cold·실제 호출은 부모/C#·공개 계약·ID/출처를 보존하며 out→분기→다음 줄을 실행한다')
  assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'m12-copy-final.png'),full_page=True);f.browser.close()
except Exception:
 try:f.page.screenshot(path=str(f.case/'m12-copy-failure.png'),timeout=5000);(f.case/'failure-dom.html').write_text(f.page.content())
 except Exception:pass
 raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2));f.stop()
print('M12_OVERRIDE_UI '+str(f.case),flush=True)
