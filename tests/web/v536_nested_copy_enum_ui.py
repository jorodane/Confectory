"""Existing private execution enum editor; shared external-copy UI fixture adapter."""
import copy,json,time,sys,shutil
from playwright.sync_api import expect

def saved(g):
 f=g['f'];mode=g['mode'];checkpoint=g['checkpoint'];g['nested_enter'](['left']);before=checkpoint.read_bytes()
 rows={v['id']:v for v in json.loads(before)['changes']};root_id=g['copied']+'/body:'+g['target']
 if root_id in rows:g['enum_graph_before']=json.loads(rows[root_id]['draft'])
 else:
  unit=next(v for v in f.metadata('describe',project=str(f.manifest))['units'] if v['id']==root_id);g['enum_graph_before']=json.loads((f.project/unit['path']).read_text())
 previous=g['nested_changed']['left/body'];wanted=previous.replace('Result.Positive','Result.Renamed').replace('복사본 본문','enum 저장 본문');helpers='private static long Keep(long value){return checked(value+1);} // 새 보조 원문 😀\n'
 execution=copy.deepcopy(g['enum_expected']);execution['members'].reverse();execution['members'][0]['name']='Renamed';execution['members'][0]['value']=11
 def dialog():return f.page.locator('.bp-script-dialog')
 def open_code():
  if 'mobile-enum' in sys.argv[4:]:
   g['nested_mobile_flow']();f.author().locator('[data-flow-node=body]').click();f.page.locator('.bp-flow-inspector:visible [data-flow-code]').click()
  else:
   g['nested_desktop_window']();f.author().locator('[data-bp-overview-node=body]').click();f.author().locator('[data-bp-node=body] [data-internal-code]').click()
  expect(dialog()).to_be_visible();return dialog().locator('[data-code-source]')
 def desktop():
  inspector=f.page.locator('.bp-flow-inspector:visible')
  if inspector.count():inspector.locator('[data-flow-done]').click()
  g['nested_desktop_window']()
 def replace(field,section,text):
  field.evaluate(r"(el,part)=>{let a,b;if(part==='enum'){a=el.value.indexOf('\n{\n')+3;b=el.value.indexOf('\n}\n',a);}else{const p=el.value.indexOf(' Execute(');a=el.value.indexOf('\n{\n',p)+3;b=el.value.indexOf('\n}\n',a);if(part==='helpers'){a=b+3;b=el.value.length;}}el.focus();el.setSelectionRange(a,b);}",section);f.page.keyboard.insert_text(text)
 def edit(cancel=False,invalid=False):
  field=open_code();assert 'public static Result Execute(long amount)' in field.input_value()
  replace(field,'body',wanted);replace(field,'helpers',helpers);replace(field,'enum','    Renamed = 7,\n    NoBranch = 0,' if not invalid else '    NoBranch = 0,')
  if invalid:
   dialog().locator('[data-code-save]').click();expect(dialog().locator('[data-code-error]')).to_be_visible();assert checkpoint.read_bytes()==before;dialog().locator('[data-code-cancel]').click()
  else:
   if not cancel:
    geometry={'viewport':f.page.viewport_size,'dialog':dialog().bounding_box(),'editor':dialog().locator('.bp-script-editor').bounding_box(),'save':dialog().locator('[data-code-save]').bounding_box()};(f.case/'enum-script-geometry.json').write_text(json.dumps(geometry,indent=2));f.page.screenshot(path=str(f.case/'private-copy-enum-script.png'))
    if 'mobile-enum' in sys.argv[4:]:
     viewport=geometry['viewport'];box=geometry['dialog'];assert abs(box['x']-6)<1 and abs(box['y']-6)<1 and abs(box['width']-(viewport['width']-12))<1 and abs(box['height']-(viewport['height']-12))<1;assert geometry['save']['y']+geometry['save']['height']<=viewport['height']-6
   dialog().locator('[data-code-cancel]' if cancel else '[data-code-save]').click()
  expect(dialog()).to_be_hidden();f.idle();desktop()
 held=f.pending();edit(cancel=True);assert f.pending()==held;edit(invalid=True);assert f.pending()==held
 # Original branch addition uses the existing structural Undo/Redo, without adding UI.
 f.author().locator('[data-bp-node=body] [data-bp-add-branch]').click();added=f.pending();assert any(v.get('type')=='enum-code' for _,v in added['blueprint']);f.author().locator('.bp-viewport').focus();f.page.keyboard.press('Control+z');assert f.pending()==held;f.page.keyboard.press('Control+Shift+z');assert f.pending()==added;f.page.keyboard.press('Control+z');assert f.pending()==held
 edit();field=open_code();replace(field,'enum','    Renamed = 11,\n    NoBranch = 0,');dialog().locator('[data-code-save]').click();expect(dialog()).to_be_hidden();f.idle();desktop();held=f.pending();f.page.screenshot(path=str(f.case/'private-copy-enum-editor.png'));g['restart'](20);expect(f.author().locator('.bp-breadcrumbs')).to_be_visible();assert f.pending()==held;g['originals']()
 f.checked('내부 enum 취소·연결 포트 삭제 거절·분기 추가 Undo/Redo·이름/순서·수동 C#/helpers와 cold 입력을 보존한다')
 if 'retry-enum' in sys.argv[4:]:
  g['nested_desktop_window']();f.author().locator('[data-bp-overview-node=body]').click();label=f.author().locator('[data-bp-node=body] [data-branch-name=positive]');label.fill('class');label.press('Tab');f.idle();mark=len(f.traffic);f.author().locator('[data-bp-save]').click();g['wait_result'](mark,'authorBatch',False);f.idle();assert checkpoint.read_bytes()==before;rejected=f.pending();assert any(v.get('kind')=='author-attempt' for _,v in rejected['blueprint']);f.author().locator('.bp-viewport').focus();f.page.keyboard.press('Control+z');held=f.pending();assert all(dict(held['blueprint']).get(k)==v for k,v in rejected['blueprint'] if v.get('kind')=='author-attempt');g['restart'](24);assert f.pending()==held;g['originals']();f.checked('유효하지 않은 C# enum 이름 저장은 전체 거절하고 Undo·cold 뒤 원래 기준의 명시 재시도와 실패 기록을 보존한다')
 if mode=='context':
  f.close_author();g['d'].open_peer();peer=f.page.locator('.window[data-key=editor-2]');title=peer.locator('.object-title-name').bounding_box();box=peer.bounding_box();f.page.mouse.move(title['x']+5,title['y']+5);f.page.mouse.down();f.page.mouse.move(1100+title['x']-box['x']+5,800+title['y']-box['y']+5,steps=10);f.page.mouse.up();g['reopen']();g['nested_enter'](['left']);g['d'].verify_peer();assert f.pending()['blueprint']==held['blueprint'];f.checked('독립 소유 창 재진입과 다른 창 미저장 입력은 enum 원문과 분리된다')
 if mode=='projects':
  listing=f.state()['listingId'];f.page.close();f.stop();other=f.case/'enum other root'/'owned project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory'));shutil.copytree(g['source'],other.parent/g['source'].name);f.env['CONFECTORY_WEB_PROJECT']=str(other/'project.cproj');f.start(23);f.invoke('select',{'id':g['owner']});f.invoke('saveDraft',{});second=f.state()['listingId'];other_checkpoint=next(other.glob('.confectory/edit-workspaces/*/draft.json'));other_before=other_checkpoint.read_bytes();g['enum_other_checkpoint']=(other_checkpoint,other_before);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700})
  def enter(id):
   f.page.locator('.brand').click();expect(f.page.locator('.home-grid')).to_be_visible();f.page.locator('[data-enter="'+id+'"]').click();expect(f.page.locator('.work-body')).to_be_visible();f.idle()
  enter(listing);assert all(dict(f.pending()['blueprint']).get(k)==v for k,v in held['blueprint']);enter(second);assert not any(v.get('type')=='enum-code' for _,v in f.pending()['blueprint']);enter(listing);g['reopen']();g['nested_enter'](['left']);assert other_checkpoint.read_bytes()==other_before;f.env['CONFECTORY_WEB_PROJECT']=str(f.manifest);f.checked('실제 프로젝트 전환은 enum 계획과 입력을 다른 프로젝트에 적용하지 않고 문맥별로 복원한다')
 if mode=='conflict':
  f.invoke('schema',{'id':g['owner']});state=f.state()['schema'];f.invoke('editDescription',{'id':g['owner'],'hash':state['textHash'],'revision':state['revision'],'value':'enum 계획 경합의 다른 저장'});f.invoke('saveDraft',{});peer=checkpoint.read_bytes();assert peer!=before;mark=len(f.traffic);f.author().locator('[data-bp-save]').click();g['wait_result'](mark,'authorBatch',False);f.idle();assert checkpoint.read_bytes()==peer and all(dict(f.pending()['blueprint']).get(k)==v for k,v in held['blueprint']);g['restart'](21);assert checkpoint.read_bytes()==peer;g['originals']();f.checked('실제 owner/checkpoint 경합은 enum·본문·helpers 전체 미적용·입력 보존이며 자동 재적용하지 않는다');f.browser.close();print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'nativeWindows':False},ensure_ascii=False));sys.exit(0)
 applied=set();queried=set();masked=set()
 if mode=='loss':
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
  f.page.route('**/api/request',intercept)
 if mode=='storage':checkpoint.chmod(0o400)
 mark=len(f.traffic);f.author().locator('[data-bp-save]').click()
 if mode=='storage':
  g['wait_result'](mark,'authorBatch',False);f.idle();assert checkpoint.read_bytes()==before and all(dict(f.pending()['blueprint']).get(k)==v for k,v in held['blueprint']);g['originals']();checkpoint.chmod(0o600);f.checked('실제 checkpoint 쓰기 실패는 enum·본문·helpers를 전부 미적용하고 원문/입력을 보존한다');f.author().locator('[data-bp-save]').click()
 if mode=='loss':
  deadline=time.monotonic()+90
  while time.monotonic()<deadline and not queried&masked:f.page.wait_for_timeout(30)
  assert len(applied)==1 and queried&masked;f.page.unroute_all(behavior='wait');g['restart'](22);mark=len(f.traffic);f.author().locator('[data-bp-save]').click();f.page.wait_for_function('()=>document.querySelector(".window[data-key=blueprint] .bp-status")?.textContent.startsWith("복사본 ·")',timeout=120000);assert not any(t.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for t in f.traffic[mark:]);f.checked('응답 유실·cold 뒤 원래 enum source binding receipt를 조회하여 중복 적용을 막는다')
 f.page.wait_for_function('()=>document.querySelector(".window[data-key=blueprint] .bp-status")?.textContent.startsWith("복사본 ·")',timeout=120000);f.idle();assert not any(v.get('type')=='enum-code' for _,v in f.pending()['blueprint']);g['originals']();g['nested_changed']['left/body']=wanted
 if mode=='projects':assert other_checkpoint.read_bytes()==other_before
 g['nested_parent']();g['nested_enter'](['right','deep']);button=f.author().locator('[data-bp-node=body] [data-internal-code]');button.click();assert g['nested_changed']['right/deep/body'] in dialog().locator('[data-code-source]').input_value();dialog().locator('[data-code-cancel]').click();g['nested_parent']()
 f.checked('저장된 copy 내부 enum/수동 C#/helpers는 한 후보/CAS이며 공개 계약·형제 동명 leaf·부모·외부를 보존한다')
 return execution,helpers
