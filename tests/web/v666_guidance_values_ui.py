"""Value guidance on an owned real engine: refusal, exact input, cold and final CAS."""
import ast,copy,json,pathlib,sys
from playwright.sync_api import sync_playwright,expect
import v666_root_execution_fixture as x
f=x.f;mode=sys.argv[3]if len(sys.argv)>3 else'normal'
helper=pathlib.Path(__file__).with_name('v666_async_transition_ui.py');names={'panel','pending','open_graph','save','restart','review'}
exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),str(helper),'exec'))
def menu(name='amount',path='',operator=False):
 panel().locator('.window-title').click(position={'x':190,'y':16});panel().locator('[data-bp-overview-node=choose]').click();f.page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
 if panel().locator('[data-bp-percent]').inner_text()!='50%':
  panel().locator('[data-bp-percent]').click();zoom=f.page.get_by_role('dialog',name='노드 화면 배율',exact=True);zoom.locator('[data-zoom-preset="50"]').click();zoom.locator('[data-zoom-value]').press('Escape')
 plug=panel().locator('.bp-inline-pin[data-node=choose][data-side=in][data-port="field:'+name+'"]')
 button=plug.locator('[data-expression-group="'+path+'"] > .bp-expression-terminal > button.bp-expression-operator')if operator else plug.locator('input[data-expression-path="'+path+'"]').locator('..').locator('[aria-label="값 목록 열기"]')
 viewport=panel().locator('.bp-viewport');box=viewport.bounding_box();delta=button.evaluate('(el)=>{const a=el.getBoundingClientRect(),v=el.closest(".bp-viewport").getBoundingClientRect();return {x:a.x+a.width/2-v.x-v.width/2,y:a.y+a.height/2-v.y-v.height/2}}');f.page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2);f.page.mouse.wheel(delta['x'],delta['y']);f.page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');
 try:button.click(timeout=5000)
 except Exception:
  (f.case/'obscured-control.json').write_text(json.dumps(button.evaluate('(el)=>{const r=el.getBoundingClientRect(),v=el.closest(".bp-viewport").getBoundingClientRect(),hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return {button:r.toJSON(),viewport:v.toJSON(),hit:hit?.outerHTML.slice(0,500)}}')));f.page.screenshot(path=str(f.case/'obscured-control.png'),timeout=5000);(f.case/'obscured-control.html').write_text(f.page.content());raise
 d=f.page.get_by_role('dialog',name='핀 값 선택',exact=True);expect(d).to_be_visible();return d
def literal(path,value):
 d=menu(path=path);d.get_by_role('searchbox',name='값 검색').fill(value);f.page.keyboard.press('Enter');expect(d).to_have_count(0)
def held():return copy.deepcopy(pending())
def preserved(previous):
 now=dict(pending());return all(now.get(key)==value for key,value in previous)
def invariant(previous,checkpoint,before):
 (f.case/'last-invariant.json').write_text(json.dumps({'before':previous,'after':pending(),'sameCheckpoint':checkpoint.read_bytes()==before},ensure_ascii=False))
 assert preserved(previous)and checkpoint.read_bytes()==before;x.original()
try:
 f.start(0);f.invoke('select',dict(id=x.feature));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph()
  # Authored camera clamps positive pan; drag the node to leave space for its expression tree.
  panel().locator('[data-bp-overview-node=choose]').click();f.page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');header=panel().locator('[data-bp-node=choose] .function-node-heading').bounding_box();f.page.mouse.move(header['x']+70,header['y']+22);f.page.mouse.down();f.page.mouse.move(header['x']+370,header['y']+22,steps=10);f.page.mouse.up();f.page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
  d=menu();d.get_by_role('searchbox',name='값 검색').fill('9223372036854775808');f.page.keyboard.press('Enter');expect(d.get_by_role('status')).to_have_text('자료형에 맞는 범위의 값을 입력해 주십시오.');expect(d.get_by_role('searchbox')).to_have_value('9223372036854775808');invalid=held();assert invalid and checkpoint.read_bytes()==before;x.original();restart(1);assert pending()==invalid;d=menu();expect(d.get_by_role('searchbox')).to_have_value('9223372036854775808');f.page.keyboard.press('Escape');assert pending()==invalid
  # A reopened popup retains its pre-existing invalid draft on cancel; explicit correction clears it.
  d=menu();d.get_by_role('searchbox').fill('2');f.page.keyboard.press('Enter');assert all(v.get('type')!='value-draft:amount'for _,v in pending());x.original();f.checked('정수 범위 거절의 새 안내·원문/체크포인트·정확한 입력을 cold와 취소 뒤 보존하고 명시 수정한다')
  if x.data_mode:
   previous=held();d=menu('total');d.get_by_role('searchbox').fill('5');f.page.keyboard.press('Enter');expect(d.get_by_role('status')).to_have_text('참조 입력에는 기존 입력이나 앞선 노드의 저장소를 연결해 주십시오.');expect(d.get_by_role('searchbox')).to_have_value('5');f.page.keyboard.press('Escape');assert pending()==previous;x.original();f.checked('ref는 상수/연산식으로 대체하지 않고 저장소 연결 조건과 취소 입력을 유지한다')
  d=menu();d.get_by_role('button',name='연산자 /',exact=True).click();incomplete=held();panel().locator('[data-bp-save]').click();f.idle();expect(panel().locator('.bp-status')).to_have_text('연산에 사용할 두 값을 선택해 주십시오. 입력은 유지됩니다.');invariant(incomplete,checkpoint,before)
  viewport=panel().locator('.bp-viewport');viewport.focus();f.page.keyboard.press('Control+z');assert pending()!=incomplete;f.page.keyboard.press('Control+y');assert pending()==incomplete;x.original();f.checked('미완성 연산 저장 거절·새 안내·구조 Undo/Redo는 원본과 두 피연산자 입력을 유지한다')
  literal('0','2');literal('1','0');zero=held();panel().locator('[data-bp-save]').click();f.idle();expect(panel().locator('.bp-status')).to_have_text('0으로 나눌 수 없습니다. 입력은 유지됩니다.');invariant(zero,checkpoint,before);restart(2);assert pending()==zero;literal('1','1');correct=held();x.original()
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:panel().locator('[data-bp-save]').click();f.idle();invariant(correct,checkpoint,before)
   finally:checkpoint.chmod(0o600)
   restart(3);assert preserved(correct);f.checked('쓰기 실패·재시작 뒤 올바른 연산 입력과 이전 checkpoint를 보존한다')
  if mode in ['loss','late']:
   requests=set();queries=set();paused={};lost=[]
   def interrupt(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke'and body.get('endpoint')=='blueprint':
     action=body.get('input',{}).get('action')
     if action=='authorBatch':requests.add(body['requestId'])
     elif requests and action=='settledAuthorBatch':queries.add(body['requestId'])
    response=route.fetch();payload=response.json()
    if mode=='late'and not paused and any(r.get('ok')and r.get('requestId')in requests for r in payload.get('results',[])):paused.update(route=route,response=response);return
    if mode=='loss':
     for row in payload.get('results',[]):
      if row['requestId']in requests|queries:rid=row['requestId'];lost.append(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',interrupt);panel().locator('[data-bp-save]').click()
   for _ in range(1000):
    if paused or requests and any(r in queries for r in lost):break
    f.page.wait_for_timeout(30)
   assert len(requests)==1
   if mode=='late':
    assert paused;literal('1','2');paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',interrupt);f.idle();assert pending();restart(3);mark=len(f.traffic);panel().locator('[data-bp-save]').click();f.idle();assert pending()and not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch'for r in f.traffic[mark:]);save();value=next(a['valueJson']for row in x.read()['nodes']if row['id']=='choose'for a in row['arguments']if a['name']=='amount');assert json.loads(value)['binary']['operands'][1]=={'constant':2};literal('1','1');save();f.checked('늦은 새 값은 cold 뒤 이전 receipt만 조회하고 명시적 별도 Save로 보존하며 이전 저장을 중복하지 않는다')
   else:
    assert any(r in queries for r in lost)and pending();f.page.unroute_all(behavior='wait');restart(3);mark=len(f.traffic);save();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch'for r in f.traffic[mark:]);f.checked('저장 응답 유실 뒤 cold 재조회는 기존 receipt를 확인하고 값 저장을 중복하지 않는다')
  else:save()
  save();r=review();r.locator('[data-reject]').click();x.original();r=review();saved=checkpoint.read_bytes();p=f.project/'Flow.graph.json';old=p.read_bytes();p.write_bytes(old+b' ')
  try:r.locator('#confirm').click();f.idle();assert checkpoint.read_bytes()==saved and p.read_bytes()==old+b' ';assert all(p.read_bytes()==v for p,v in x.physical.items()if p.name!='Flow.graph.json')
  finally:p.write_bytes(old)
  f.idle()
  if r.is_visible():r.locator('[data-reject]').click()
  r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();g=json.loads(p.read_text());assert next(n for n in g['nodes']if n['id']=='choose')['arguments']['amount']=={'binary':{'operator':'/','operands':[{'constant':2},{'constant':1}]}};assert all(p.read_bytes()==v for p,v in x.physical.items()if p.name!='Flow.graph.json');assert g['edges']==x.root['edges'] and g['profile']==x.root['profile'];x.build('value-guidance-execution',43 if x.data_mode else 20,'callee:2\nafter:430:value:43:43'if x.data_mode else'callee:2\nafter:20');restart(4);assert x.read()['diagnostics']['state']=='source-ready';assert not pending();assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'value-guidance-final.png'),full_page=True);f.checked('0 나눗셈 거절·cold·명시 수정·반복 Save·Review 취소·최종 CAS 충돌·Confirm·실행·확정 재시작은 기존 C#/계약/분기/연결을 보존한다');f.browser.close()
except Exception:
 try:f.page.screenshot(path=str(f.case/'failure.png'),timeout=5000,animations='disabled')
 except Exception:pass
 try:(f.case/'failure.html').write_text(f.page.content())
 except Exception:pass
 raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));f.stop()
print('VALUE_GUIDANCE_FIXTURE',f.case,flush=True)
