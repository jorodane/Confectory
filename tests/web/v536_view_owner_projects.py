"""Live same-name project switches retain detached candidate input and reject retired callbacks."""
import json,os,pathlib,shutil,sys
from playwright.sync_api import sync_playwright,expect
import v536_view_owner_ui as u
f=u.f;root_b=f.case/'different root'/'owned project';shutil.copytree(f.project,root_b,ignore=shutil.ignore_patterns('.confectory'));original_b={str(p.relative_to(root_b)):p.read_bytes() for p in root_b.rglob('*') if p.is_file()}
def same_sources():f.originals();assert all((root_b/k).read_bytes()==v for k,v in original_b.items())
def goto(listing):
 f.page.locator('.brand').click();expect(f.page.locator('.home-grid')).to_be_visible();f.page.locator('[data-enter="'+listing+'"]').click();expect(f.page.locator('.work-body')).to_be_visible();f.idle()
try:
 with sync_playwright() as pw,u.cleanup():
  f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.start(0);f.invoke('select',{'id':f.id});f.invoke('saveDraft',{});f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1400});u.open_two();a=f.state();aid=a['projectId'];alist=a['listingId'];u.power('1').fill('9223372036854775805');u.description('1').fill('프로젝트 A 입력');u.pending();f.page.unroute_all(behavior='wait');f.page.close();f.stop()
  f.env['CONFECTORY_WEB_PROJECT']=str(root_b/'project.cproj');f.start(1);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1400});u.open_two();b=f.state();bid=b['projectId'];blist=b['listingId'];assert aid!=bid;u.power('1').fill('9223372036854775806');u.description('1').fill('프로젝트 B 입력');u.pending();same_sources();f.checked('같은 namespace/id/view 슬롯의 서로 다른 실제 프로젝트는 독립 한글/raw64 입력을 보관한다')
  goto(alist);expect(u.power('1')).to_have_value('9223372036854775805');expect(u.description('1')).to_have_value('프로젝트 A 입력');u.window('1').locator('[data-element-action=save]').evaluate('e=>globalThis.retiredSave=e.onclick');goto(blist);expect(u.power('1')).to_have_value('9223372036854775806');baseline=u.view('1')['draft']['text'];mark=len(f.traffic);f.page.evaluate('async()=>await globalThis.retiredSave(new Event("click"))');f.idle();assert not [r for r in f.traffic[mark:] if r.get('invoke',{}).get('input',{}).get('action')=='applySlots'];assert u.view('1')['draft']['text']==baseline and f.state()['projectId']==bid;expect(u.power('1')).to_have_value('9223372036854775806');same_sources();f.checked('실제 A→B 전환 뒤 은퇴한 A Save 콜백은 B 요청/적용 없이 두 창 문맥과 입력을 유지한다')
  goto(alist);u.window('1').locator('[data-element-action=save]').click();u.saved();assert u.view('1')['schema']['description']=='프로젝트 A 입력';goto(blist);expect(u.power('1')).to_have_value('9223372036854775806');expect(u.description('1')).to_have_value('프로젝트 B 입력');assert u.view('1')['draft']['text']==baseline;same_sources();f.checked('A의 실제 원자 Save는 A에만 보관되고 동일 이름 B의 저장본/미저장 입력/소스는 변경하지 않는다')
  u.restart(2);expect(u.power('1')).to_have_value('9223372036854775806');goto(alist);expect(u.power('1')).to_have_value('9223372036854775805');assert u.view('1')['schema']['description']=='프로젝트 A 입력';goto(blist);expect(u.description('1')).to_have_value('프로젝트 B 입력');same_sources();assert not f.errors and not f.external,(f.errors,f.external);f.checked('프로세스 재시작과 양방향 재진입에도 저장된 A 후보와 B의 미저장 입력을 각각 복원한다')
except Exception:
 try:f.case.joinpath('project-failure.json').write_text(json.dumps({'state':f.state(),'traffic':f.traffic[-50:]},ensure_ascii=False,indent=2))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'liveProjectSwitch':True,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
