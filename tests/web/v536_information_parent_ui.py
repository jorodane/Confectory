"""Original v536 information parent = category/Root; isolated real engine, no login/model."""
import hashlib,json,re,sys,time,zipfile
from playwright.sync_api import sync_playwright,expect
import v536_field_definitions_ui as d
f=d.f
owner=f.n+'FreeInfo'
info=f.project/'FreeInfo.celem'
info.write_text(info.read_text().replace('FreeInfo {','FreeInfo extends '+f.n+'Leaf {',1))
for name,group in [('InfoA','info'),('InfoB','info'),('ConceptCategory','concept')]:
 (f.project/(name+'.celem')).write_text('category '+f.n+name+' {value editorBrowserGroup="'+group+'";}')
 f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element '+name+' category "'+name+'.celem";registry Confectory.Build.DotNet',1))
f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file()}

def wait(endpoint,after,action=None):
 deadline=time.monotonic()+60
 while time.monotonic()<deadline:
  ids={r['invoke']['requestId'] for r in f.traffic[after:] if r.get('invoke',{}).get('endpoint')==endpoint and (action is None or r['invoke']['input'].get('action')==action)}
  results=[r['result'] for r in f.traffic[after:] if r.get('result',{}).get('requestId') in ids and r['result'].get('error',{}).get('code')!='stale_revision']
  if results:
   assert all(r.get('ok') for r in results),results
   f.idle();return results[-1]
  f.page.wait_for_timeout(20)
 raise AssertionError('no completed '+endpoint)
def picker():
 f.idle();f.owner().locator('.object-parent-change').click();p=f.page.get_by_role('dialog',name='부모 변경',exact=True);expect(p).to_be_visible();return p

def compare_source(popup):
 with zipfile.ZipFile(f.repo/'reference/site-ui/Confectory-Editor-Prototype-v536.zip') as z:
  app=next(n for n in z.namelist() if n.endswith('/dist/app.js'));source=z.read(app).decode();css=re.sub(r'@import\s+url\([^)]*\)\s*;','',z.read(app.removesuffix('app.js')+'style.css').decode())
 def function(name):
  start=source.index('function '+name+'(');end=source.find('\nfunction ',start+1);return source[start:end]
 selectors=[':scope','input','.object-parent-options','[data-parent-choice=""]','[data-parent-choice="'+f.n+'InfoA"]','[data-parent-choice="'+f.n+'InfoB"]']
 measure="""(el,selectors)=>{const base=el.getBoundingClientRect();return selectors.map(s=>{const e=s===':scope'?el:el.querySelector(s),r=e.getBoundingClientRect(),c=getComputedStyle(e);return {selector:s,x:r.x-base.x,y:r.y-base.y,width:r.width,height:r.height,color:c.color,background:c.backgroundColor,font:c.font,padding:c.padding};});}"""
 actual=popup.evaluate(measure,selectors);anchor=f.owner().locator('.object-parent-change').bounding_box();original=f.browser.new_page(viewport={'width':1600,'height':1100});original.route('**/*',lambda route:route.abort());original.set_content('<!doctype html><html lang="ko"><head><style>'+css+'</style></head><body><button id="anchor" style="position:fixed;box-sizing:border-box;left:'+str(anchor['x'])+'px;top:'+str(anchor['y'])+'px;width:'+str(anchor['width'])+'px;height:'+str(anchor['height'])+'px">↔</button></body></html>')
 original.add_script_tag(content="""const esc=s=>String(s??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;'),profileIconMarkup=esc,project={objects:[{id:'Owned.Elements::FreeInfo',group:'info',kind:'Info',name:'FreeInfo'},...['InfoA','InfoB'].map(name=>({id:'Owned.Elements::'+name,group:'info',kind:'Category',name,icon:'▤'}))]};"""+'\n'.join(function(n) for n in ['browserHierarchyParent','canMoveBrowserObject','openObjectParentPicker'])+"\nopenObjectParentPicker({},project.objects[0],document.querySelector('#anchor'));")
 expected=original.locator('.object-parent-picker').evaluate(measure,selectors);original.screenshot(path=str(f.case/'information-parent-original.png'));original.close();(f.case/'information-parent-geometry.json').write_text(json.dumps({'original':expected,'actual':actual},ensure_ascii=False,indent=2));assert expected==actual,{'evidence':str(f.case),'original':expected,'actual':actual}

def choose(name):
 p=picker();after=len(f.traffic);p.locator('[data-parent-choice="'+(f.n+name if name else '')+'"]').click();wait('moveBrowserFolders',after);expect(f.owner().locator('[data-parent] strong') if name else f.owner().locator('[data-parent]')).to_have_text(name or 'Root');return f.state()

def restart(index):
 f.pending();f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(index);f.page=f.setup();f.page.set_viewport_size({'width':1600,'height':1100});expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo',timeout=60000);f.idle()

def held():return [(k,v) for k,v in f.pending()['schema'] if '|'+f.n+'RefTarget|element|' in k]
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{})
 with sync_playwright() as pw:
  f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1600,'height':1100});expect.set_options(timeout=60000);d.open_info()
  expect(f.owner().locator('[data-parent]')).to_have_text('Root');expect(d.field(['Count']).locator('[data-property-value]')).to_have_value('0');p=picker();assert set(p.locator('[data-parent-choice]').evaluate_all('(els)=>els.map(e=>e.dataset.parentChoice)'))=={'',f.n+'InfoA',f.n+'InfoB'};f.page.screenshot(path=str(f.case/'information-parent-picker.png'));compare_source(p);f.page.keyboard.press('Escape');expect(p).to_be_hidden();f.originals();assert not f.state()['folderMove'];f.checked('원본 정보 부모 선택은 같은 info 카테고리·Root만 제공하고 native extends/상속 Count는 그대로 유지한다; Escape는 미적용이다')
  d.field(['Power']).locator('[data-property-value]').fill('9223372036854775801');captured=d.pending();p=picker();after=len(f.traffic);p.locator('[data-parent-choice="'+f.n+'InfoA"]').click();expect(f.page.locator('#status')).to_contain_text('입력을 먼저');assert not f.state()['folderMove'] and d.pending()==captured;assert not any(r.get('invoke',{}).get('endpoint')=='moveBrowserFolders' for r in f.traffic[after:]);f.owner().locator('[data-element-action=discard]').click();expect(d.field(['Power']).locator('[data-property-value]')).to_have_value('9223372036854775806');f.checked('같은 정보의 미저장 타입/값은 자동 저장·폐기하지 않고 분류 변경을 거절해 입력을 보존한다')
  f.page.locator('#workspace').click(button='right',position={'x':80,'y':100});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=concept]').click();b.locator('[data-browser-control="object-query"]').fill('RefTarget');b.locator('[data-browser-control="object-search"]').click();row=b.locator('[data-object="'+f.n+'RefTarget"]');expect(row).to_have_attribute('aria-disabled','false');f.idle();row.press('Enter');expect(f.owner().locator('.object-title-name')).to_have_text('RefTarget');b.locator('[data-close]').first.click();f.idle();f.owner().get_by_label('Count 기본값',exact=True).fill('9223372036854775802');peer=held();assert peer;d.open_info();checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();s=choose('InfoA');assert set(s['folderMove']['ids'])=={owner,f.n+'InfoA'};assert 'extends '+f.n+'Leaf' in s['draft']['text'];assert checkpoint.read_bytes()==before and held()==peer;f.originals();f.checked('선택은 정보+카테고리의 검토 그룹에만 적용하고 원본·상속·다른 객체의 exact64 private 입력을 보존한다')
  after=len(f.traffic);f.owner().locator('[data-element-action=discard]').click();wait('browserDrafts',after,'discard');expect(f.owner().locator('[data-parent]')).to_have_text('Root');assert not f.state()['folderMove'] and held()==peer;f.originals();choose('InfoA');after=len(f.traffic);f.owner().locator('[data-element-action=save]').click();wait('saveDraft',after);restart(1);expect(f.owner().locator('[data-parent] strong')).to_have_text('InfoA');assert held()==peer;f.originals();f.checked('원본 변경 취소는 분류 전체를 복원하고 임시 저장/cold는 분류와 별도 private 입력을 각각 복원한다')
  # Folder review permits unrelated unapplied values but still checks this group's ownership/proofs.
  review=d.review();assert {r['id'] for r in f.state()['review']['units']}=={owner,f.n+'InfoA'};review.locator('[data-reject]').click();expect(review).to_be_hidden();f.originals();review=d.review()
  if review.locator('[data-additional-changes]').count():
   review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
   if ack.count():ack.check()
  after=len(f.traffic);review.locator('#confirm').click();result=wait('confirmGroup',after);assert result['result']['sourceConfirmed'];expect(review).to_be_hidden();assert not f.state()['folderMove'];assert held()==peer;assert 'editorFolder = "'+f.n+'InfoA"' in info.read_text();assert 'extends '+f.n+'Leaf' in info.read_text();assert all((f.project/k).read_bytes()==v for k,v in f.original.items() if k!='FreeInfo.celem');f.checked('검토 취소와 새 명시적 compiler Confirm은 분류 메타데이터만 확정하고 부모/카테고리/등록팩/다른 원본을 바꾸지 않는다')
  choose(None);after=len(f.traffic);f.owner().locator('[data-element-action=discard]').click();wait('browserDrafts',after,'discard');expect(f.owner().locator('[data-parent] strong')).to_have_text('InfoA');assert held()==peer;f.page.screenshot(path=str(f.case/'information-parent-final.png'));assert not f.errors and not f.external,(f.errors,f.external);f.checked('확정 후 같은 창 Root 재편집·취소는 저장된 카테고리로 돌아가며 다른 입력과 상속 원본을 유지한다')
  print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False));f.page.close();f.stop();f.browser.close()
except Exception:
 try:(f.case/'information-parent-failure.json').write_text(json.dumps({'state':f.state(),'traffic':f.traffic,'errors':f.errors},ensure_ascii=False))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
