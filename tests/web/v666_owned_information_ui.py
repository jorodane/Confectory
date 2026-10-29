"""Original owned compound controls over an isolated actual engine and compiler."""
import ast,json,pathlib,sys,time,shutil
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3] if len(sys.argv)>3 else 'normal';detached='view' in sys.argv[4:];with_peer=False;kind='object' if 'object' in sys.argv[4:] else 'schema';leaf='Target2' if kind=='object' else 'Details';owner=f.n+leaf
helper=pathlib.Path(__file__).with_name('v536_element_icon_ui.py');names={'surface','pending','own_schema','open_card','saved','restart','review'};functions=[node for node in ast.parse(helper.read_text()).body if isinstance(node,ast.FunctionDef) and node.name in names];exec(compile(ast.Module(body=functions,type_ignores=[]),str(helper),'exec'));f.owner=surface
file=f.project/(leaf+'.celem');file.write_text(file.read_text().replace('{','{ // nested definition keeps this comment\n',1))
if kind=='schema':
 for name,body in [('NestedAncestor','field Inherited single general string;'),('NamedInformation','field Existing single general long;')]:
  (f.project/(name+'.celem')).write_text('schema '+f.n+name+' {'+body+'}')
  f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element '+name+' schema "'+name+'.celem";registry Confectory.Build.DotNet'))
 file.write_text(file.read_text().replace(' {',' extends '+f.n+'NestedAncestor {',1).replace('{','{field Named single compound '+f.n+'NamedInformation;',1))
f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file()}
def setup():
 from editor_navigation import goto_editor
 page=f.browser.new_page(viewport={'width':1800,'height':1400});f.page=page
 cdp=page.context.new_cdp_session(page);cdp.send('Debugger.enable');cdp.on('Debugger.scriptFailedToParse',lambda e:(f.case/'script-parse-error.json').write_text(json.dumps(e,ensure_ascii=False,indent=2)))
 page.on('pageerror',lambda e:((f.case/'page-error.txt').write_text(str(e)+'\n'+e.stack),f.errors.append(str(e))));page.on('response',f.observe);page.route('**/*',f.route);goto_editor(page,f.url);return page
f.setup=setup
def own():return surface().locator('[data-owned-definition]').first
def direct(row,attr):return row.locator(':scope>.property-content-box>['+attr+']')
def tree_rows(row):return row.locator(':scope>.property-content-box>.property-expanded-content>.property-complex-body>.property-fields>.object-property-row')
def add(row):row.locator(':scope>.property-content-box>.object-property-default>[data-owned-add]').click();return tree_rows(row).last
def choose(row,kind):
 direct(row,'data-property-type').click();p=f.page.get_by_role('dialog',name='속성 타입 선택');p.locator('[data-type="'+kind+'"]' if kind in ['string','long','double','bool'] else '[data-field-kind="'+kind+'"]').click()
def name(row,value):direct(row,'data-property-name').fill(value)
def value(row,text):row.locator(':scope>.property-content-box>.object-property-default>[data-property-value]').fill(text)
def save():surface().locator('[data-element-action=save]').click();saved()
def files_same():f.originals();assert not list((f.project/'elements').glob(leaf+'_Properties_*.celem'))
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));checkpoint_before=checkpoint.read_bytes()
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_card()
  if kind=='schema':
   expect(surface().locator('[data-property-path=\'["Named","Existing"]\'] [data-property-type]')).to_have_count(0);expect(surface().locator('[data-property-path=\'["Inherited"]\'] [data-property-name]')).to_have_count(0)
  surface().locator('[data-schema-add]').click();new=surface().locator('[data-definition-key]').last;name(new,'자체 복합');choose(new,'owned');expect(own()).to_be_visible();native=own().get_attribute('data-owned-definition')
  first=add(own());name(first,'힘');choose(first,'long');first=tree_rows(own()).first;value(first,'9223372036854775806')
  nested=add(own());name(nested,'내부');choose(nested,'owned');nested=tree_rows(own()).nth(1);title=add(nested);name(title,'제목');value(title,'한글 😀')
  first=tree_rows(own()).first;direct(first,'data-property-icon').click();p=f.page.get_by_role('dialog',name='힘 아이콘 편집');p.locator('[data-icon-choice="★"]').click();p.get_by_role('button',name='적용',exact=True).click();expect(direct(tree_rows(own()).first,'data-property-icon')).to_contain_text('★')
  direct(tree_rows(own()).first,'data-property-icon').focus();f.page.keyboard.press('Control+z');expect(direct(tree_rows(own()).first,'data-property-icon')).not_to_contain_text('★');f.page.keyboard.press('Control+y');expect(direct(tree_rows(own()).first,'data-property-icon')).to_contain_text('★');files_same();f.checked('원본 추가/타입/이름/아이콘과 중첩 기본값은 하나의 private cell이며 정확한 수치·Undo/Redo·원문을 보존한다')
  if mode=='normal':
   import io
   from PIL import Image
   out=io.BytesIO();Image.new('RGBA',(24,16),(30,80,150,160)).save(out,format='PNG');direct(tree_rows(own()).first,'data-property-icon').click();p=f.page.get_by_role('dialog',name='힘 아이콘 편집');p.locator('[type=file]').set_input_files(dict(name='synthetic-nested.png',mimeType='image/png',buffer=out.getvalue()));expect(p.locator('.object-icon-preview img')).to_be_visible();uri=p.locator('.object-icon-preview img').get_attribute('src');assert uri.startswith('data:image/webp;base64,');p.get_by_role('button',name='적용',exact=True).click();expect(direct(tree_rows(own()).first,'data-property-icon').locator('img')).to_have_attribute('src',uri);direct(tree_rows(own()).first,'data-property-icon').press('Control+z');expect(direct(tree_rows(own()).first,'data-property-icon')).to_contain_text('★');direct(tree_rows(own()).first,'data-property-icon').press('Control+y');expect(direct(tree_rows(own()).first,'data-property-icon').locator('img')).to_have_attribute('src',uri);f.checked('생성한 로컬 테스트 이미지는 기존 팝오버의 128px WebP로만 저장하며 자체 자식 Undo/Redo와 입력을 보존한다')
  if mode=='late':name(tree_rows(own()).first,'힘  ')
  staged=next(v for _,v in pending() if v['kind']=='owned-definition');assert '9223372036854775806' in staged['text'];assert len(staged['tree']['fields'])==2
  held=pending()
  if mode=='project':
   b_project=f.case/'other project';shutil.copytree(f.project,b_project,ignore=shutil.ignore_patterns('.confectory'));f.pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(b_project/'project.cproj');f.start(10);f.page=f.setup();open_card();assert not pending();expect(surface().locator('[data-owned-definition]')).to_have_count(0);surface().locator('[data-schema-add]').click();name(surface().locator('[data-definition-key]').last,'다른 프로젝트 입력');f.pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.project/'project.cproj');f.start(11);f.page=f.setup();open_card();assert pending()==held;expect(own()).to_be_visible();files_same();f.checked('동일 namespace/ID의 다른 실제 프로젝트를 거쳐도 소유 정의·입력은 섞이지 않고 원래 프로젝트에 복원된다')
  if mode=='conflict':
   file.write_bytes(file.read_bytes()+b'\n// synthetic owner race\n');f.original[file.name]=file.read_bytes();surface().locator('[data-element-action=save]').click();expect(surface().locator('[data-element-error]')).not_to_have_text('');assert pending()==held and checkpoint.read_bytes()==checkpoint_before;files_same();restart(1);surface().locator('[data-element-action=save]').click();expect(surface().locator('[data-element-error]')).not_to_have_text('');assert pending()==held and checkpoint.read_bytes()==checkpoint_before;files_same();f.checked('실제 owner source 경합은 전체 미적용·원래 입력/기준 보존이며 cold 재시도도 자동 재기준하지 않는다')
  elif mode=='cancel':
   surface().locator('[data-element-action=discard]').click();expect(surface().locator('[data-owned-definition]')).to_have_count(0);assert not pending();files_same();f.checked('명시 취소는 새 자체 정의와 자식만 제거하고 원본/등록/다른 값을 보존한다')
  else:
   if mode=='storage':
    checkpoint.chmod(0o400)
    try:surface().locator('[data-element-action=save]').click();expect(surface().locator('[data-element-error]')).not_to_have_text('');assert pending()==held and checkpoint.read_bytes()==checkpoint_before;files_same()
    finally:checkpoint.chmod(0o600)
    restart(1);assert pending()==held;f.checked('checkpoint 쓰기 실패는 생성/등록/정의/값을 부분 적용하지 않고 입력을 cold까지 보존한다')
   if mode=='loss':
    applies=set();queries=set();lost=[]
    def interrupt(route):
     body=route.request.post_data_json
     if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
      action=body.get('input',{}).get('action')
      if action=='applySlots':applies.add(body['requestId'])
      elif applies and action=='settledSlots':queries.add(body['requestId'])
     response=route.fetch();payload=response.json()
     for v in payload.get('results',[]):
      if v['requestId'] in applies|queries:rid=v['requestId'];lost.append(rid);v.clear();v.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
     route.fulfill(response=response,json=payload)
    f.page.route('**/api/request',interrupt);surface().locator('[data-element-action=save]').click()
    for _ in range(600):
     if applies and any(r in queries for r in lost):break
     f.page.wait_for_timeout(50)
    assert len(applies)==1 and any(r in queries for r in lost) and pending()==held;f.page.unroute_all(behavior='wait');mark=len(f.traffic);restart(2);save();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='applySlots' for r in f.traffic[mark:]);f.checked('적용/조회 응답 유실은 cold 뒤 기존 receipt로 회수하며 자식 schema나 등록을 중복 생성하지 않는다')
   elif mode=='late':
    ids=set();paused={}
    def hold(route):
     body=route.request.post_data_json
     if body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and body.get('input',{}).get('action')=='applySlots':ids.add(body['requestId'])
     response=route.fetch();payload=response.json()
     if not paused and any(v.get('ok') and v.get('requestId') in ids for v in payload.get('results',[])):paused.update(route=route,response=response);return
     route.fulfill(response=response)
    f.page.route('**/api/request',hold);surface().locator('[data-element-action=save]').click()
    for _ in range(600):
     if paused:break
     f.page.wait_for_timeout(50)
    assert paused and len(ids)==1;name(tree_rows(own()).first,'저장 중 새 이름');paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',hold)
    for _ in range(600):
     if pending() and pending()[0][1].get('copySavedBasis'):break
     f.page.wait_for_timeout(50)
    late=next(v for _,v in pending() if v['kind']=='owned-definition');assert pending()[0][1]['tree']['fields'][0]['name']=='저장 중 새 이름' and pending()[0][1]['copySavedBasis']['accepted']['tree']['fields'][0]['name']=='힘';restart(2);expect(direct(tree_rows(own()).first,'data-property-name')).to_have_value('저장 중 새 이름');save();staged=late;f.checked('저장 응답 대기의 새 자식 입력은 새 source 증거로 재기준해 cold 뒤 명시적 재저장하며 이전 응답에 유실되지 않는다')
   else:save()
   assert not pending();s=own_schema();assert native in s['ownedDefinitions'];assert len(s['ownedDefinitions'][native]['sources'])==2;files_same();f.checked('실제 Save는 정보·등록·두 소유 자식 schema를 한 draft/CAS에 저장하며 파일은 Confirm 전 보존한다')
   restart(3);expect(own()).to_be_visible();assert own_schema()['ownedDefinitions'][native]['tree']==staged['tree'];files_same();f.checked('엔진 cold는 같은 소유 ID·정의·아이콘·정확한 기본값과 창 문맥을 복원한다')
   first=tree_rows(own()).first;name(first,'힘 재편집');choose(first,'bool');first=tree_rows(own()).first;save_button=surface().locator('[data-element-action=save]');save_button.click();expect(surface().locator('[data-element-error]')).not_to_have_text('');assert pending();files_same();value(first,'true');save();assert not pending();files_same();f.checked('호환 불가 타입 변경은 전체 미적용·입력 보존이며 사용자가 고친 기본값만 정의와 원자 저장한다')
   if mode=='normal':
    direct(tree_rows(own()).first,'data-schema-remove').click();expect(tree_rows(own())).to_have_count(1);direct(own(),'data-property-icon').focus();f.page.keyboard.press('Control+z');expect(tree_rows(own())).to_have_count(2);f.page.keyboard.press('Control+y');expect(tree_rows(own())).to_have_count(1);save();restart(4);expect(tree_rows(own())).to_have_count(1);files_same();f.checked('명시 자식 삭제·Undo/Redo·Save/cold는 삭제한 값만 제거하고 내부 자식 ID와 보관 소스를 보존한다')
   if mode=='normal':
    choose(own(),'string');surface().locator('[data-element-action=save]').click();expect(surface().locator('[data-element-error]')).not_to_have_text('');assert pending();files_same();value(own(),'사용자가 고른 새 기본값');save();expect(surface().locator('[data-owned-definition]')).to_have_count(0);restart(5);expect(surface().locator('[data-owned-definition]')).to_have_count(0);files_same();f.checked('소유 복합의 일반 타입 전환은 기존 값을 자동 변환하지 않고 명시 기본값만 원자 저장하며 이전 자식 소스를 보관한다')
   r=review();expect(r.locator('#confirm')).to_be_enabled();r.locator('[data-reject]').click();expect(r).to_be_hidden();files_same();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();assert file.read_text().startswith('schema') or '// nested definition keeps this comment' in file.read_text();assert len(list((f.project/'elements').glob(leaf+'_Properties_*.celem')))==(2 if kind=='schema' else 3);assert 'owned-nested-v1' in ''.join(p.read_text() for p in (f.project/'elements').glob(leaf+'_Properties_*.celem'));f.checked('Review 취소와 명시적 compiler Confirm을 구분하고 최종 정보·등록·소유 자식만 반영한다')
  assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'owned-information.png'));f.browser.close()
except Exception:
 try:f.page.screenshot(path=str(f.case/'owned-information-failure.png'),timeout=5000)
 except Exception:pass
 raise
finally:
 f.stop();(f.case/'owned-information-evidence.json').write_text(json.dumps({'checks':f.checks,'errors':f.errors,'actualEngine':True,'actualWindows':False,'actualMobile':False,'detached':detached,'mode':mode},ensure_ascii=False,indent=2)+'\n')
print('EVIDENCE',f.case,flush=True)
