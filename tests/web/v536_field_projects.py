"""Actual typed-definition input across same-name project roots; no real grants."""
import json,shutil
from playwright.sync_api import sync_playwright,expect
import v536_field_definitions_ui as d

f=d.f
b_root=f.case/'different root'/'owned project'
shutil.copytree(f.project,b_root,ignore=shutil.ignore_patterns('.confectory','.build'))
original_b={str(p.relative_to(b_root)):p.read_bytes() for p in b_root.rglob('*') if p.is_file()}
def unchanged():
 f.originals();assert all((b_root/name).read_bytes()==data for name,data in original_b.items())
def enter(listing):
 f.page.locator('.brand').click();expect(f.page.locator('.home-grid')).to_be_visible();f.page.locator('[data-enter="'+listing+'"]').click();expect(f.page.locator('.work-body')).to_be_visible();f.idle()
def edit(label,raw):
 d.choose(d.field(['Power']).locator('[data-property-type]'),'general','long',True)
 d.field(['Power']).locator('[data-value-path=\'["Power",0]\']').fill(raw)
 d.target(d.add(label,'reference',f.n+'Leaf'),f.n+'RefTarget')
 return d.pending()
def power(raw):expect(d.field(['Power']).locator('[data-value-path=\'["Power",0]\']')).to_have_value(raw)
try:
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.start(0);f.invoke('select',{'id':d.owner});f.invoke('saveDraft',{});f.page=f.setup();f.page.set_viewport_size({'width':1600,'height':1100});d.open_info();a=f.state();aid,alist=a['projectId'],a['listingId'];held_a=edit('A 참조','9223372036854775805');f.page.unroute_all(behavior='wait');f.page.close();f.stop()
  f.env['CONFECTORY_WEB_PROJECT']=str(b_root/'project.cproj');f.start(1);f.invoke('select',{'id':d.owner});f.invoke('saveDraft',{});f.page=f.setup();f.page.set_viewport_size({'width':1600,'height':1100});d.open_info();b=f.state();bid,blist=b['projectId'],b['listingId'];assert aid!=bid;held_b=edit('B 참조','9223372036854775804');unchanged();f.checked('동일 namespace/정보 이름의 실제 두 프로젝트에 서로 다른 cardinality·exact64·새 참조 타입 후보를 보관한다')
  enter(alist);power('9223372036854775805');assert d.pending()==held_a;f.owner().locator('[data-element-action=save]').evaluate('e=>globalThis.retiredTypeSave=e.onclick');enter(blist);power('9223372036854775804');assert d.pending()==held_b;checkpoint=next(b_root.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();mark=len(f.traffic);f.page.evaluate('async()=>await retiredTypeSave(new Event("click"))');f.idle();assert not any(row.get('invoke',{}).get('input',{}).get('action')=='applySlots' for row in f.traffic[mark:]);assert checkpoint.read_bytes()==before and d.pending()==held_b;unchanged();f.checked('A→B 실제 전환 뒤 은퇴한 A 저장 콜백은 B에 요청·적용·입력 삭제를 하지 않는다')
  enter(alist);f.owner().locator('[data-element-action=save]').click();d.saved();assert not d.pending();enter(blist);power('9223372036854775804');assert d.pending()==held_b and checkpoint.read_bytes()==before;unchanged();f.checked('A의 typed 정의·값 저장은 A에만 적용되고 B의 미저장 후보·기존 checkpoint·양쪽 원본은 보존한다')
  f.pending();f.page.close();f.stop();f.start(2);f.page=f.setup();f.page.set_viewport_size({'width':1600,'height':1100});power('9223372036854775804');assert d.pending()==held_b;enter(alist);power('9223372036854775805');assert not d.pending();enter(blist);power('9223372036854775804');assert d.pending()==held_b;unchanged();assert not f.errors and not f.external,(f.errors,f.external);f.checked('cold와 양방향 재진입은 저장된 A 정의와 B의 미저장 타입·정확한 입력을 각 프로젝트에 복원한다');f.page.unroute_all(behavior='wait');f.browser.close()
finally:f.stop()
print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'nativeWindows':False,'liveProjectSwitch':True,'accountOrInference':False},ensure_ascii=False))
