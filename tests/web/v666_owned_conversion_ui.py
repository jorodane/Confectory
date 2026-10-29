"""Original type popup acknowledgement and actual engine-owned conversion transaction."""
import pathlib,sys,json,copy,time
helper=pathlib.Path(__file__).with_name('v666_owned_information_ui.py');prefix=helper.read_text().split('\ntry:\n f.start(0);',1)[0];assert 'def files_same' in prefix;exec(compile(prefix,str(helper),'exec'))
scenario=sys.argv[4] if len(sys.argv)>4 else 'general';is_many=scenario in ['array','ref-array','collapse'];new_many=is_many and scenario!='collapse' or scenario=='expand';count=2 if is_many else 1;is_ref=scenario=='ref-array';foreign={}
def literal(v):return json.dumps(v,ensure_ascii=False)
def add_source(name,kind,text):
 p=f.project/(name+'.celem');p.write_text(text);f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element '+name+' '+kind+' "'+name+'.celem";registry Confectory.Build.DotNet'));return p
if scenario=='named':
 lib=f.case/'reference pack';lib.mkdir();(lib/'pack.cpack').write_text('pack External.Values version "1" {element Base schema "Base.celem";element Named schema "Named.celem";}');(lib/'Base.celem').write_text('schema External.Values::Base {field Exact single general long;}');(lib/'Named.celem').write_text('schema External.Values::Named extends External.Values::Base {field Text single general string;}');foreign={p:p.read_bytes() for p in lib.iterdir()};f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','registry External.Values '+literal(str(lib/'pack.cpack'))+';dependency External.Values version "1";registry Confectory.Build.DotNet'));definition='single compound External.Values::Named';old={'Exact':9223372036854775805,'Text':'참조 원래😀'}
elif is_ref:
 add_source('ReferenceShape','schema','schema '+f.n+'ReferenceShape {field Title single general string;}')
 for key in ['FirstRef','SecondRef']:add_source(key,'object','object '+f.n+key+' {use schema '+f.n+'ReferenceShape;data Title="'+key+'";}')
 definition='multiple reference '+f.n+'ReferenceShape';old=[{'$ref':f.n+'FirstRef'},{'$ref':f.n+'SecondRef'}]
elif scenario=='function':
 add_source('Callback','function','function '+f.n+'Callback () -> void {}');add_source('CallbackBody','implementation','implementation '+f.n+'CallbackBody for '+f.n+'Callback () -> void {body common "Callback.csbody";}');(f.project/'Callback.csbody').write_text('return; // original function body');definition='single function '+f.n+'Callback';old={'$ref':f.n+'CallbackBody'}
else:definition=('multiple' if is_many else 'single')+' general long';old=[9223372036854775805,9223372036854775806] if is_many else 9223372036854775805
private_source=None
if kind=='object':
 private_id=owner+'_Properties_'+'1'*12;private_source=f.project/'elements'/(private_id.split('::')[1]+'.celem');private_source.parent.mkdir(exist_ok=True);private_source.write_text('schema '+private_id+' {field Convert '+definition+';value editorFieldIcon_Convert="☆";}');f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element '+private_id.split('::')[1]+' schema "elements/'+private_source.name+'";registry Confectory.Build.DotNet'));file.write_text(file.read_text().replace('{','{use schema '+private_id+';data Convert='+literal(old)+';',1))
else:
 text=file.read_text();extra='field Convert '+definition+';value editorFieldIcon_Convert="☆";value editorFieldDefault_Convert='+literal(literal(old))+';'
 if 'value editorInformationDefaults' not in text:extra+='value editorInformationDefaults="typed-json-v1";'
 file.write_text(text.replace('{','{'+extra,1))
f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file()};initial_owned_paths=set((f.project/'elements').glob(leaf+'_Properties_*.celem'))

def original():f.originals();assert set((f.project/'elements').glob(leaf+'_Properties_*.celem'))==initial_owned_paths;assert all(p.read_bytes()==b for p,b in foreign.items())
def source_row():return surface().locator('[data-property-path=\'["Convert"]\']').first
def prompt():
 direct(source_row(),'data-property-type').click();p=f.page.get_by_role('dialog',name='속성 타입 선택')
 if scenario in ['collapse','expand']:p.get_by_label('여러 개 허용',exact=True).set_checked(new_many)
 p.locator('[data-field-kind=owned]').click();expect(p.locator('[data-owned-reset-apply]')).to_be_visible();return p
def staged():return next(v for _,v in pending() if v['kind']=='owned-definition')
def saved_value():return json.loads(next(r['valueJson'] for r in own_schema()['rows'] if r['path']==['Convert']))
def save_rejected():surface().locator('[data-element-action=save]').click();expect(surface().locator('[data-element-error]')).not_to_have_text('');f.idle()
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before_checkpoint=checkpoint.read_bytes()
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();open_card();name(source_row(),'전환 이름');surface().get_by_label('Label 기본값',exact=True).fill('다른 속성 입력')
  if scenario=='general':value(source_row(),'9223372036854775806')
  held=pending();p=prompt();assert pending()==held;original();f.page.keyboard.press('Escape');assert pending()==held;expect(surface().locator('[data-owned-definition]')).to_have_count(0);f.checked('원본 타입 팝오버의 경고를 취소하면 현재 값·이름·독립 입력과 원본/참조 파일을 그대로 보존한다')
  p=prompt();p.locator('[data-owned-reset-apply]').click();expect(surface().locator('[data-owned-definition]')).to_have_count(1);assert staged()['conversion']['originalValueJson'] and staged()['conversion']['mode']=='reset-empty-v1';assert json.loads(staged()['text'])==([{} for _ in range(count)] if new_many else {});assert staged()['displayName']=='전환 이름' and staged()['icon']=='☆';original()
  direct(own(),'data-property-icon').press('Control+z');assert pending()==held;expect(surface().locator('[data-owned-definition]')).to_have_count(0);direct(source_row(),'data-property-icon').press('Control+y');expect(own()).to_be_visible();assert json.loads(staged()['text'])==([{} for _ in range(count)] if new_many else {});original();f.checked('명시 적용만 선택한 속성을 빈 소유 복합으로 전환하며 배열 수·native key·이름/아이콘·다른 입력과 Undo/Redo를 유지한다')
  if new_many:own().locator(':scope>.property-content-box>.property-multi-values>.property-multi-item').first.locator('[data-owned-add]').first.click()
  else:child=add(own())
  if new_many:
   values=own().locator('.property-multi-item [data-property-value]');expect(values).to_have_count(count)
   for i in range(count):values.nth(i).fill('새 배열값 '+str(i)+' 😀')
  else:name(child,'자식');value(tree_rows(own()).first,'새 값 😀')
  if new_many and count>1:
   own().locator(':scope>.property-content-box>.property-multi-values>.property-multi-item').first.locator(':scope>.property-value-box>.property-multi-remove').click();expect(own().locator(':scope>.property-content-box>.property-multi-values>.property-multi-item')).to_have_count(count-1);direct(own(),'data-property-icon').press('Control+z');expect(own().locator(':scope>.property-content-box>.property-multi-values>.property-multi-item')).to_have_count(count);direct(own(),'data-property-icon').press('Control+y');expect(own().locator(':scope>.property-content-box>.property-multi-values>.property-multi-item')).to_have_count(count-1);direct(own(),'data-property-icon').press('Control+z');expect(own().locator(':scope>.property-content-box>.property-multi-values>.property-multi-item')).to_have_count(count);f.checked('원래 배열 항목의 추가/접기/삭제 버튼은 가려지지 않으며 값 삭제와 Undo/Redo가 각 항목의 새 값을 보존한다')
  held=pending();wanted=json.loads(staged()['text']);wanted_tree=copy.deepcopy(staged()['tree']);f.page.screenshot(path=str(f.case/'conversion-before-save.png'))
  if mode=='project':
   b_project=f.case/'other project';shutil.copytree(f.project,b_project,ignore=shutil.ignore_patterns('.confectory'));b_bytes=(b_project/file.name).read_bytes();f.pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(b_project/'project.cproj');f.start(10);f.page=f.setup();open_card();assert not pending();expect(surface().locator('[data-owned-definition]')).to_have_count(0);surface().get_by_label('Label 기본값',exact=True).fill('B 프로젝트 입력');f.pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.project/'project.cproj');f.start(11);f.page=f.setup();open_card();assert pending()==held;expect(own()).to_be_visible();assert (b_project/file.name).read_bytes()==b_bytes;original();f.checked('동일 namespace/ID의 다른 실제 프로젝트를 거쳐도 초기화 동의·원래 값 증거·새 정의와 입력을 섞지 않는다')
  if mode=='cancel':
   surface().locator('[data-element-action=discard]').click();assert not pending();expect(surface().locator('[data-owned-definition]')).to_have_count(0);assert checkpoint.read_bytes()==before_checkpoint;original();restart(1);assert not pending();f.checked('변경 취소와 cold는 전환/초기화/새 정의를 모두 취소하고 원래 값과 참조 계약으로 돌아간다')
  elif mode=='conflict':
   file.write_bytes(file.read_bytes()+b'\n// actual conversion source race\n');f.original[file.name]=file.read_bytes();save_rejected();assert pending()==held and checkpoint.read_bytes()==before_checkpoint;original();restart(1);save_rejected();assert pending()==held;original();f.checked('실제 원본 경합은 전환·등록·기본값 전체를 미적용하고 cold 재시도에도 입력과 원래 기준을 보존한다')
  else:
   if mode=='storage':
    checkpoint.chmod(0o400)
    try:save_rejected();assert pending()==held and checkpoint.read_bytes()==before_checkpoint;original()
    finally:checkpoint.chmod(0o600)
    restart(1);assert pending()==held;f.checked('checkpoint 쓰기 실패는 전환·값 초기화·새 소유 schema를 부분 저장하지 않고 재시작 후 재시도한다')
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
    assert len(applies)==1 and any(r in queries for r in lost) and pending()==held;f.page.unroute_all(behavior='wait');mark=len(f.traffic);restart(2);save();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='applySlots' for r in f.traffic[mark:]);f.checked('적용/조회 응답 유실은 cold receipt로만 복구하고 초기화·등록·자식 생성은 중복 적용하지 않는다')
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
    assert paused and len(ids)==1;name(tree_rows(own()).first,'늦은 자식 이름');paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',hold);f.idle();now=staged();assert now['conversion'] is None and now.get('copySavedBasis') and now['tree']['fields'][0]['name']=='늦은 자식 이름';wanted_tree=copy.deepcopy(now['tree']);restart(2);assert staged()['conversion'] is None;save();f.checked('저장 중 새 입력은 수락한 소유 계약으로 재기준하며 초기화 의도는 한 번만 소비하고 cold 뒤 새 Save로 반영한다')
   else:save()
   assert not pending() and saved_value()==wanted;assert own_schema()['ownedDefinitions']['Convert']['tree']==wanted_tree;original();restart(3);expect(own()).to_be_visible();assert saved_value()==wanted;assert json.loads(next(r['valueJson'] for r in own_schema()['rows'] if r['path']==['Label']))=='다른 속성 입력';original();f.checked('정의·값·등록의 한 Save와 cold는 정확한 새 값·배열 연결·다른 입력을 보존하고 Confirm 전 원본을 쓰지 않는다')
   if scenario=='inner':
    inner=tree_rows(own()).first;choose(inner,'owned');p=f.page.get_by_role('dialog',name='속성 타입 선택');expect(p.locator('[data-owned-reset-apply]')).to_be_visible();p.locator('[data-owned-reset-apply]').click();assert json.loads(staged()['text'])!=wanted;direct(tree_rows(own()).first,'data-property-icon').press('Control+z');assert not pending() and saved_value()==wanted;expect(tree_rows(own()).first.locator('[data-property-value]')).to_have_value('새 값 😀');direct(tree_rows(own()).first,'data-property-icon').press('Control+y');inner=tree_rows(own()).first;child=add(inner);name(child,'깊은 자식');value(tree_rows(inner).first,'깊은 새 값 😀');wanted=json.loads(staged()['text']);save();restart(4);assert saved_value()==wanted;assert len(own_schema()['ownedDefinitions']['Convert']['sources'])==2;original();f.checked('저장된 소유 복합 내부의 일반 자식도 명시 초기화·Undo/Redo·새 하위 정의·Save/cold로 원자 전환한다')
   r=review();expect(r.locator('#confirm')).to_be_enabled();r.locator('[data-reject]').click();expect(r).to_be_hidden();original();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();changed={k for k,v in f.original.items() if (f.project/k).read_bytes()!=v};assert changed==({file.name,f.manifest.name}|({str(private_source.relative_to(f.project))} if private_source else set())),changed;assert all(p.read_bytes()==b for p,b in foreign.items());added=list(set((f.project/'elements').glob(leaf+'_Properties_*.celem'))-initial_owned_paths);assert len(added)==(2 if scenario=='inner' else 1) and 'owned-nested-v1' in added[0].read_text();f.checked('Review 취소와 명시 Confirm을 구분하며 선택된 속성/등록/소유 자식만 바꾸고 부모·외부·참조·함수 본문 원본을 유지한다')
  if mode=='project':assert (b_project/file.name).read_bytes()==b_bytes
  assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'owned-conversion.png'));f.browser.close()
except Exception:
 try:f.page.screenshot(path=str(f.case/'owned-conversion-failure.png'),timeout=5000)
 except Exception:pass
 raise
finally:
 f.stop();(f.case/'owned-conversion-evidence.json').write_text(json.dumps(dict(checks=f.checks,errors=f.errors,scenario=scenario,mode=mode,detached=detached,actualEngine=True,actualWindows=False,actualMobile=False),ensure_ascii=False,indent=2)+'\n')
print('EVIDENCE',f.case,flush=True)
