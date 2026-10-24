"""I1-I3 original type picker through a real isolated engine/renderer/compiler."""
import json, sys
from playwright.sync_api import sync_playwright, expect
import v536_wide_mixed as f

mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
is_object='object' in sys.argv[4:]
is_view='view' in sys.argv[4:]
peer_inputs=None
owner=f.id if is_object else f.n+'FreeInfo'
labels=('NewRef','NewFunction','Imported','NewNumber','NewCondition') if is_object else ('새 참조','새 함수','등록 정보','새 정수','새 조건')
new_paths={}
extra={
 'Leaf':('schema','schema '+f.n+'Leaf {field Count single general long;}'),
 'Leaf2':('schema','schema '+f.n+'Leaf2 {field Count single general long;field Note single general string;}'),
 'LeafChild':('schema','schema '+f.n+'LeafChild extends '+f.n+'Leaf {}'),
 'RefTarget':('object','object '+f.n+'RefTarget {use schema '+f.n+'LeafChild;data Count=8;}'),
 'FreeInfo':('schema','schema '+f.n+'FreeInfo'+' {field Power single general long;field Tree single compound '+f.n+'Leaf;field Peer single reference '+f.n+'LeafChild;value editorInformationDefaults="typed-json-v1";value editorFieldDefault_Power="9223372036854775806";value editorFieldDefault_Tree="{\\\"Count\\\":9223372036854775805}";value editorFieldDefault_Peer="{\\\"$ref\\\":\\\"'+f.n+'RefTarget\\\"}";}'),
}
if is_object:
 extra['LocalFields']=('schema','schema '+f.n+'LocalFields {field Power single general long;field Tree single compound '+f.n+'Leaf;field Peer single reference '+f.n+'LeafChild;}')
 path=f.project/'Slime.celem';path.write_text(path.read_text().replace('{','{use schema '+f.n+'LocalFields;data Power=9223372036854775806;data Tree={Count=9223372036854775805;};data Peer='+f.n+'RefTarget;',1))
for key,(kind,text) in extra.items():(f.project/(key+'.celem')).write_text(text)
registered=f.project/'registered';registered.mkdir()
(registered/'pack.cpack').write_text('pack External.Fields version "1" {element Leaf schema "Leaf.celem";}')
(registered/'Leaf.celem').write_text('schema External.Fields::Leaf {field HP single general long;}')
f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet',''.join('element '+key+' '+kind+' "'+key+'.celem";' for key,(kind,text) in extra.items())+'registry External.Fields "registered/pack.cpack";dependency External.Fields version "1";registry Confectory.Build.DotNet'))
f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file()}

def pending():return [(k,v) for k,v in f.pending()['schema'] if '|'+owner+('|view:1|element|' if is_view else '|element|') in k]
def field(path):return f.owner().locator('[data-property-path=\''+json.dumps(path,separators=(',',':'))+'\']')
def open_info():
 if is_object and not is_view:return f.open_owner(owner)
 f.page.locator('#workspace').click(button='right',position={'x':80,'y':100});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=info]').click();b.locator('[data-browser-control="object-query"]').fill('FreeInfo');b.locator('[data-browser-control="object-search"]').click();row=b.locator('[data-object="'+owner+'"]');expect(row).to_have_attribute('aria-disabled','false');
 if is_view:
  row.click(button='right');f.page.locator('.context-menu').get_by_role('button',name='새 창으로 열기',exact=True).click();f.owner=lambda:f.page.locator('.window[data-key=editor-1]')
 else:row.press('Enter')
 expect(f.owner().locator('.object-title-name')).to_have_text('Slime' if is_object else 'FreeInfo');b.locator('[data-close]').first.click();f.idle()
def picker(button):
 button.click();p=f.page.get_by_role('dialog',name='속성 타입 선택',exact=True);expect(p).to_be_visible();return p
def choose(button,kind,type,multi=False):
 p=picker(button);expect(p.get_by_label('여러 개 허용',exact=True)).to_be_enabled();p.get_by_label('여러 개 허용',exact=True).set_checked(multi);f.page.screenshot(path=str(f.case/'type-picker.png'));p.locator('[data-type="'+type+'"]' if kind=='general' else '[data-field-kind="'+kind+'"][data-field-type="'+type+'"]').click();f.idle()
def add(name,kind,type,multi=False):
 f.owner().locator('[data-schema-add]').click();row=f.owner().locator('[data-definition-key]').last;row.locator('[data-property-name]').fill(name);choose(row.locator('[data-property-type]'),kind,type,multi);return f.owner().locator('[data-definition-key]').last
def target(row,id):
 row.locator('.property-reference-value').click();p=f.page.get_by_role('dialog',name='기본값 선택',exact=True);expect(p).to_be_visible();p.locator('[data-reference-choice="'+id+'"]').click()
def verify_peer():
 if peer_inputs is None:return
 w=f.page.locator('.window[data-key=editor-2]');expect(w.locator('.object-title-description')).to_have_value('다른 창 입력 보존');expect(w.get_by_label('Count 기본값',exact=True)).to_have_value('9223372036854775802');assert [(k,v) for k,v in f.pending()['schema'] if '|'+f.n+'RefTarget|view:2|element|' in k]==peer_inputs
def open_peer():
 global peer_inputs
 f.page.locator('#workspace').click(button='right',position={'x':80,'y':100});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=concept]').click();b.locator('[data-browser-control="object-query"]').fill('RefTarget');b.locator('[data-browser-control="object-search"]').click();row=b.locator('[data-object="'+f.n+'RefTarget"]');expect(row).to_have_attribute('aria-disabled','false');row.click(button='right');f.page.locator('.context-menu').get_by_role('button',name='새 창으로 열기',exact=True).click();w=f.page.locator('.window[data-key=editor-2]');expect(w.locator('.object-title-name')).to_have_text('RefTarget');b.locator('[data-close]').first.click();head=w.locator('.object-title-name').bounding_box();box=w.bounding_box();f.page.mouse.move(head['x']+5,head['y']+5);f.page.mouse.down();f.page.mouse.move(1700+head['x']-box['x']+5,120+head['y']-box['y']+5,steps=10);f.page.mouse.up();w.locator('.object-title-description').fill('다른 창 입력 보존');w.get_by_label('Count 기본값',exact=True).fill('9223372036854775802');peer_inputs=[(k,v) for k,v in f.pending()['schema'] if '|'+f.n+'RefTarget|view:2|element|' in k];assert len(peer_inputs)==2;verify_peer()
def values():
 expect(field(['Power']).locator('[data-value-path=\'["Power",0]\']')).to_have_value('9223372036854775806')
 expect(field([new_paths[labels[2]]]).get_by_label('HP 기본값',exact=True)).to_have_value('9223372036854775804')
 expect(field([new_paths[labels[0]]]).locator('.property-reference-value')).to_have_text('RefTarget')
 expect(field([new_paths[labels[1]]]).locator('.property-reference-value')).to_have_text('NativeBody')
 expect(field([new_paths[labels[3]]]).locator('[data-property-value]')).to_have_value('9223372036854775803')
 expect(field([new_paths[labels[4]]]).locator('[data-property-value]')).to_be_checked()
def saved():
 for _ in range(240):
  if not pending() and not [v for _,v in f.pending()['blueprint'] if v.get('kind') in ['owner-attempt','view-owner-attempt'] and v.get('owner')==owner]:f.idle();return
  f.page.wait_for_timeout(100)
 raise AssertionError((f.owner().locator('[data-element-error]').all_text_contents(),f.pending()))
def restart(i):
 f.pending();f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':2300 if is_view else 1600,'height':1500 if is_object or is_view else 1100});expect(field(['Power']).locator('[data-property-type]')).to_be_visible(timeout=60000);f.idle()
def review():
 if is_view:f.owner().locator('.object-title-name').click(position={'x':4,'y':4})
 f.owner().locator('[data-element-action=confirm]').click();r=f.page.locator('.window[data-key=review]');f.page.wait_for_function('()=>document.querySelector("#review-creation")||[...document.querySelectorAll(".window[data-key=review]")].some(e=>!e.hidden&&e.getClientRects().length)')
 if f.page.locator('#review-creation').count():f.page.locator('#review-creation').click()
 expect(r).to_be_visible();return r

try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{})
 with sync_playwright() as pw:
  f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300 if is_view else 1600,'height':1500 if is_object or is_view else 1100});expect.set_options(timeout=60000);open_info();assert abs(f.owner().bounding_box()['width']-460)<1
  if is_object:
   for toggle in f.owner().locator('.inherited-property-source>.inherited-source-toggle').all():toggle.click()
  choose(field(['Power']).locator('[data-property-type]'),'general','long',True);expect(field(['Power']).locator('[data-value-path=\'["Power",0]\']')).to_have_value('9223372036854775806');f.owner().locator('[data-own-properties-toggle]').focus();f.page.keyboard.press('Control+z');expect(field(['Power']).locator('[data-property-value]')).to_have_value('9223372036854775806');assert not pending();choose(field(['Power']).locator('[data-property-type]'),'general','long',True)
  choose(field(['Tree']).locator('[data-property-type]'),'compound',f.n+'Leaf2');expect(field(['Tree','Count']).locator('[data-property-value]')).to_have_value('9223372036854775805');field(['Tree','Note']).locator('[data-property-value]').fill('새 형식 한글');choose(field(['Peer']).locator('[data-property-type]'),'reference',f.n+'Leaf');expect(field(['Peer']).locator('.property-reference-value')).to_have_text('RefTarget');field(['Power']).locator(':scope>.property-content-box>.object-property-default>.property-expand').click();field(['Tree']).locator(':scope>.property-content-box>.object-property-default>.property-expand').click();f.checked('460px 원본 정보 카드의 단일→다중/Undo와 복합·참조 타입 변경은 exact64·상속 참조·기존 값을 보존한다')
  target(add(labels[0],'reference',f.n+'Leaf'),f.n+'RefTarget');target(add(labels[1],'function',f.n+'Native'),f.n+'NativeBody');imported=add(labels[2],'compound','External.Fields::Leaf',True);imported.locator('[aria-label="HP 기본값"]').fill('9223372036854775804');imported.locator(':scope>.property-content-box>.object-property-default>.property-expand').click();add(labels[3],'general','long').locator('[data-property-value]').fill('9223372036854775803');add(labels[4],'general','bool').locator('[data-property-value]').check();new_paths.update({v['name']:v.get('nativeKey') or v['name'] for _,v in pending() if v.get('kind')=='definition'});values();f.owner().locator('.object-title-description').fill('I1 I2 I3 한 후보');held=pending();checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();f.originals();f.checked('기존 타입 선택창의 객체·기능·등록 정보와 다중 값은 명시적 대상 선택 후 한 private 후보에 보관된다')
  if mode=='context':open_peer()
  restart(1);assert pending()==held;values();verify_peer();
  if is_view:f.owner().locator('.object-title-name').click(position={'x':4,'y':4})
  f.originals();f.checked('저장 전 실제 재시작은 선택한 계약·출처 근거·한글·정확한 수치와 함수/객체 대상을 복원한다')
  if mode=='cancel':
   f.owner().locator('[data-element-action=discard]').click();expect(f.owner().locator('[data-definition-key]')).to_have_count(0);assert not pending() and checkpoint.read_bytes()==before;restart(2);assert not pending();f.originals();f.checked('명시 취소/cold는 원본·등록 팩·참조·checkpoint를 보존하며 새 필드를 만들지 않는다')
  else:
   if mode=='conflict':
    source=f.project/('LocalFields.celem' if is_object else 'FreeInfo.celem');peer=source.read_bytes()+b'\n// isolated peer definition change\n';source.write_bytes(peer);f.original[str(source.relative_to(f.project))]=peer;f.rejected_save();assert checkpoint.read_bytes()==before and pending()==held;f.originals();restart(2);assert pending()==held;f.rejected_save();assert checkpoint.read_bytes()==before and pending()==held;f.originals();f.checked('실제 source 변경은 후보 전체를 거절하고 cold 재시도에도 원문·타입 근거·peer source를 보존한다')
   else:
    if mode=='reject':
     choose(field(['Power']).locator('[data-property-type]'),'general','bool',True);wrong=pending();f.rejected_save();assert checkpoint.read_bytes()==before and pending()==wrong;f.originals();f.owner().locator('[data-own-properties-toggle]').focus();f.page.keyboard.press('Control+z');values();assert pending()==held;f.checked('호환 불가 타입 Save 거절→실제 Undo는 원문과 원래 후보를 복원하며 새 기준 덮어쓰기 없이 재시도한다')
    if mode=='storage':
     checkpoint.chmod(0o400)
     try:f.rejected_save();assert checkpoint.read_bytes()==before and pending()==held;values();f.originals();f.checked('실제 저장 파일 쓰기 거절은 선언/정의/기본값 전체 미적용과 입력 보존이다')
     finally:checkpoint.chmod(0o600)
     restart(2);assert pending()==held
    if mode=='loss':
     applies=set();queries=set();lost=[]
     def intercept(route):
      body=route.request.post_data_json
      if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
       action=body.get('input',{}).get('action')
       if action=='applySlots':applies.add(body['requestId'])
       elif applies and action=='settledSlots':queries.add(body['requestId'])
      response=route.fetch();payload=response.json()
      for row in payload.get('results',[]):
       if row['requestId'] in applies|queries:rid=row['requestId'];lost.append(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
      route.fulfill(response=response,json=payload)
     f.page.route('**/api/request',intercept);f.owner().locator('[data-element-action=save]').click()
     for _ in range(300):
      if applies and any(r in queries for r in lost):break
      f.page.wait_for_timeout(100)
     assert len(applies)==1 and any(r in queries for r in lost);assert pending()==held;f.page.unroute_all(behavior='wait');mark=len(f.traffic);restart(2);f.owner().locator('[data-element-action=save]').click();saved();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='applySlots' for r in f.traffic[mark:]);f.checked('응답과 결과 조회 유실 뒤 cold는 receipt 조회만으로 복구하며 새 필드·schema·배열을 중복 저장하지 않는다')
    else:f.owner().locator('[data-element-action=save]').click();saved();
    f.originals();restart(3);values();verify_peer();assert not pending();f.checked('한 후보 Save와 cold 복원은 정의·기본값을 함께 저장하고 원본/부모/등록 팩을 아직 확정하지 않는다')
    if mode=='context':
     accepted=checkpoint.read_bytes();f.owner().locator('[data-element-action=confirm]').click();dialog=f.page.get_by_role('dialog',name='관련 변경 검토',exact=True);expect(dialog).to_be_visible();dialog.locator('#review-creation').click();expect(f.page.locator('#status')).to_contain_text('미적용 입력을 먼저 적용');expect(dialog).to_be_visible();verify_peer();assert checkpoint.read_bytes()==accepted;f.originals();dialog.get_by_role('button',name='닫기',exact=True).click();peer=f.page.locator('.window[data-key=editor-2]');peer.locator('[data-element-action=discard]').click();expect(peer.get_by_label('Count 기본값',exact=True)).to_have_value('8');expect(peer.locator('.object-title-description')).to_have_value('');assert not [(k,v) for k,v in f.pending()['schema'] if '|'+f.n+'RefTarget|view:2|element|' in k];peer_inputs=None;f.originals();values();f.checked('독립 창 Save/cold는 peer 입력을 보존하고 전역 검토는 미적용 입력을 차단하며 peer의 명시 취소만 그 입력을 해제한다')
    r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();f.originals();r=review()
    if r.locator('[data-review-advanced]').count():
     r.locator('[data-review-advanced]').click()
     if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
    r.locator('#confirm').click();expect(r).to_have_count(0,timeout=120000);f.idle();changed={k for k,v in f.original.items() if (f.project/k).read_bytes()!=v};assert changed==({'Slime.celem','LocalFields.celem','project.cproj'} if is_object else {'FreeInfo.celem'}),changed;restart(4);values();verify_peer();f.checked('Review 취소/명시 compiler Confirm/재시작은 소유 정보만 반영하고 원본 타입·객체·부모·등록 팩·다른 target을 보존한다')
  f.page.screenshot(path=str(f.case/'field-definitions-final.png'));assert not f.errors and not f.external,(f.errors,f.external);f.page.unroute_all(behavior='wait');f.browser.close()
except Exception:
 try:f.case.joinpath('field-definitions-failure.json').write_text(json.dumps({'state':f.state(),'traffic':f.traffic[-50:],'errors':f.errors},ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'field-definitions-failure.png'))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
