"""Original detached module pickers, registered sources and two-copy atomic Save."""
import json,re,time,sys,subprocess
from playwright.sync_api import sync_playwright,expect
import v536_field_definitions_ui as d
f=d.f;owner=d.owner;foreign='Source.Module::';source=f.case/'registered module source';source.mkdir()
(source/'pack.cpack').write_text('pack Source.Module version "1" {element Rules module "Rules.celem";element Feature function "Feature.celem";element Body implementation "Body.celem";}')
(source/'Rules.celem').write_text('module '+foreign+'Rules {require '+foreign+'Feature (long,out long,out bool) -> long;default '+foreign+'Feature with '+foreign+'Body;}')
(source/'Feature.celem').write_text('function '+foreign+'Feature (long amount,out long slotCount,out bool slotReady) -> long {description "등록된 기능";provide '+foreign+'Feature with '+foreign+'Body;}')
(source/'Body.celem').write_text('implementation '+foreign+'Body for '+foreign+'Feature (long amount,out long slotCount,out bool slotReady) -> long {body common "Body.csbody";body windows "Windows.csbody";}')
foreign_body='slotCount=amount+12;slotReady=true;return amount+13;'
(source/'Body.csbody').write_text(foreign_body);(source/'Windows.csbody').write_text('slotCount=amount+100;slotReady=false;return amount+200;')
foreign_original={p:p.read_bytes() for p in source.iterdir() if p.is_file()}
info=f.project/'FreeInfo.celem';info.write_text(info.read_text().replace('FreeInfo {','FreeInfo {module '+f.n+'Rules;module '+foreign+'Rules;provide '+f.n+'Slot with '+f.n+'AliasBody;',1))
f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','registry Source.Module "../registered module source/pack.cpack";dependency Source.Module version "1";registry Confectory.Build.DotNet',1))
if sys.argv[3]=='blueprint':
 def metadata(operation,**args):
  result=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':operation,**args}),text=True,capture_output=True,timeout=60);assert result.returncode==0,result.stderr;value=json.loads(result.stdout);assert value['ok'],value;return value['result']
 feature_text=(f.project/'Slot.celem').read_text();prepared=metadata('blueprintPrepareFeature',id=f.n+'Slot',text=re.sub(r'provide[^;]+;','',feature_text),implementation=f.n+'SlotBody',graphPath='Slot.graph.json',nodePath='slot-body.node.json');graph=prepared['graph'];definitions=metadata('featureBlueprintNodes',featureSource=feature_text,graph=graph);node=next(n for n in definitions['nodes'] if n['id']=='body');(f.project/'Slot.graph.json').write_text(json.dumps(graph));(f.project/'slot-body.node.json').write_text(json.dumps({'schema':1,'node':'body','definitionHash':node['definitionHash'],'source':f.body}));path=f.project/'SlotBody.celem';path.write_text(path.read_text().replace('body common "Slot.csbody"','blueprint common "Slot.graph.json"'))
f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file()}
def slot(fn):return f.owner().locator('[data-module-method="'+fn+'"]')
def schema():return next(r['schema'] for r in f.state()['editorViews'] if r['view']=='1')
def choices():return [v['copy'] for _,v in f.pending()['blueprint'] if v.get('kind')=='copy-selection' and v['copy']['owner']==owner]
def originals():f.originals();assert all(p.read_bytes()==value for p,value in foreign_original.items())
def pending():return [(k,v) for k,v in f.pending()['schema'] if '|'+owner+'|view:1|element|' in k]+[(k,v) for k,v in f.pending()['blueprint'] if v.get('copy',{}).get('owner')==owner or v.get('owner')==owner or '|slot:'+owner+':' in k]
def copy(fn,body,before,after,edit=False):
 slot(fn).locator('[data-function-edit]' if edit else '[data-function-write-direct]').click();picker=f.page.locator('.feature-import-dialog');expect(picker).to_be_visible();picker.locator('[data-copy-source="'+body+'"][data-copy-target=common]').click();expect(f.author().locator('[data-bp-node=body]')).to_be_visible();f.edit_region(f.author().locator('[data-bp-node=body] [data-internal-code]'),before,after);f.close_author();return next(c['implementation'] for c in choices() if c['function']==fn)
def saved():
 deadline=time.monotonic()+90
 while time.monotonic()<deadline:
  if not pending():f.idle();return
  f.page.wait_for_timeout(30)
 raise AssertionError((f.owner().locator('[data-element-error]').all_text_contents(),pending()))
def accept():
 review=d.review();review.locator('[data-reject]').click();originals();review=d.review()
 if review.locator('[data-review-advanced]').count():
  review.locator('[data-review-advanced]').click()
  if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
 review.locator('#confirm').click();expect(review).to_have_count(0,timeout=120000);f.idle()
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});f.invoke('select',{'id':f.id})
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1600});d.open_info();w=f.owner();head=w.locator('.object-title-name').bounding_box();box=w.bounding_box();f.page.mouse.move(head['x']+5,head['y']+5);f.page.mouse.down();f.page.mouse.move(1780+head['x']-box['x']+5,80+head['y']-box['y']+5,steps=10);f.page.mouse.up()
  first=copy(f.n+'Slot',f.n+'AliasBody',f.body,'slotCount=amount+31;slotReady=false;return amount+32;',True);f.owner().locator('[data-behavior-toggle=\"'+f.n+'Rules\"]').click();second=copy(foreign+'Feature',foreign+'Body',foreign_body,'slotCount=amount+41;slotReady=true;return amount+42;');f.owner().locator('[data-behavior-toggle=\"'+foreign+'Rules\"]').click();d.field(['Power']).locator('[data-property-value]').fill('9223372036854775804');assert len(choices())==2;held=pending();checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();originals();f.checked('원본 선택창은 상속/등록 구현의 common 실행 대상을 각각 private copy로 열며 두 슬롯·exact64 입력과 모든 원본/다른 target을 보존한다')
  target=source/'Feature.celem';target.write_text(target.read_text().replace('-> long','-> bool'));f.rejected_save();assert pending()==held and checkpoint.read_bytes()==before;current_info=next(r['draft']['text'] for r in f.state()['editorViews'] if r['view']=='1');assert first not in current_info and second not in current_info;target.write_bytes(foreign_original[target]);originals();f.checked('마지막 등록 계약이 바뀌면 두 copy·선언 후보 전체를 거절하며 앞선 슬롯이나 값의 부분 저장과 입력 삭제가 없다')
  f.owner().locator('[data-element-action=save]').click();saved();originals();assert {r['implementation'] for r in schema()['providers']} >= {first,second};accept();assert all(p.read_bytes()==value for p,value in foreign_original.items());assert '9223372036854775804' in info.read_text();f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts};f.checked('새 명시적 Save와 Review 취소/Confirm은 두 copy·정확한 정보 값을 같은 후보로 반영하며 부모/등록 소스/다른 target은 불변이다')
  f.owner().locator('[data-behavior-toggle=\"'+f.n+'Rules\"]').click();slot(f.n+'Slot2').locator('[data-function-import]').click();picker=f.page.locator('.feature-import-dialog');expect(picker).to_be_visible();picker.locator('[data-feature-import-search]').fill('Feature');picker.locator('[data-feature-import="'+foreign+'Feature"]').click();f.owner().locator('[data-element-action=save]').click();saved();originals();expect(slot(f.n+'Slot2').locator('[data-imported-feature-open]')).to_contain_text('Feature');accept();assert all(p.read_bytes()==value for p,value in foreign_original.items());f.checked('명시적 등록 callable 가져오기는 해당 정보 슬롯의 wrapper/import만 생성하고 등록 팩과 함수 계약을 바꾸지 않는다')
  f.page.screenshot(path=str(f.case/'registered-module-final.png'));assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
 print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'sourceVariant':sys.argv[3],'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
except Exception:
 try:(f.case/'registered-module-failure.json').write_text(json.dumps({'state':f.state(),'traffic':f.traffic[-70:],'checks':f.checks,'errors':f.errors},ensure_ascii=False,indent=2))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
