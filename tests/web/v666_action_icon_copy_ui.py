"""Same-contract owned copy icons, including a saved private frame; registered source is read only."""
import json,pathlib,sys,copy
from playwright.sync_api import sync_playwright,expect
helper=pathlib.Path(__file__).with_name('v536_information_external_copy_ui.py')
if len(sys.argv)<4:sys.argv.append('normal')
sys.argv.append('nested-source')
g={'__file__':str(helper),'__name__':'action_icon_copy_fixture'}
exec(compile(helper.read_text().split('\ntry:\n',1)[0],str(helper),'exec'),g)
f,owner,source=g['f'],g['owner'],g['source'];donor={p:p.read_bytes() for p in source.iterdir() if p.is_file()}
def unchanged():g['originals']();assert all(p.read_bytes()==v for p,v in donor.items())
def icon(node):return f.author().locator('[data-bp-node="'+node+'"] [data-function-icon]')
def choose(node,value):
 f.author().locator('[data-bp-overview-node="'+node+'"]').click();icon(node).click();p=f.page.get_by_role('dialog',name=node+' 아이콘 편집',exact=True);expect(p).to_be_visible();p.locator('[data-icon-choice="'+value+'"]').click();p.get_by_role('button',name='적용',exact=True).click();expect(icon(node)).to_have_text(value)
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});f.invoke('select',{'id':f.id})
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});g['d'].open_info();title=f.owner().locator('.object-title-name').bounding_box();box=f.owner().bounding_box();f.page.mouse.move(title['x']+5,title['y']+5);f.page.mouse.down();f.page.mouse.move(1780+title['x']-box['x']+5,80+title['y']-box['y']+5,steps=10);f.page.mouse.up();g['expand']();g['slot']().locator('[data-function-write-direct]').click();picker=f.page.get_by_role('dialog',name='구현 선택',exact=True);picker.locator('[data-copy-source="Source.Module::Body"][data-copy-target=common]').click();expect(icon('left')).to_be_visible();copied=g['copy_choices']()[0]['implementation'];g['copied']=copied
  choose('left','★');g['nested_enter'](['left']);choose('body','🛡️');unchanged();f.close_author();mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();g['wait_result'](mark,'applySlots');expect(f.owner().locator('[data-element-error]')).to_have_text('');f.idle();checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']};root=copied+'/body:common';graph=json.loads(rows[root]['draft']);assert graph['nodes'][0]['icon']=='★' and graph['nodes'][0]['graph']['nodes'][0]['icon']=='🛡️';provenance=graph['copySource'];right_branch=copy.deepcopy(graph['nodes'][1]);bodies={k:r['draft'] for k,r in rows.items() if '/node:' in k};unchanged();f.checked('원래 명시적 common copy 선택과 첫 owner Save는 소유 graph/내부 동작 아이콘만 복제 대상에 저장하며 등록 함수 계약·외부 원문·다른 target은 보존한다')
  g['reopen']();expect(icon('left')).to_have_text('★');g['nested_enter'](['left']);choose('body','🔥');mark=len(f.traffic);f.author().locator('[data-bp-save]').click();g['wait_result'](mark,'authorBatch');expect(f.author().locator('.bp-status')).not_to_contain_text('미저장');assert not [(k,v) for k,v in f.pending()['blueprint'] if v.get('type')=='icon'];rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']};graph=json.loads(rows[root]['draft']);assert graph['copySource']==provenance and graph['nodes'][1]==right_branch;assert f.n+'ProjectManifest' in rows[owner]['atomicEditGroup'];assert graph['nodes'][0]['graph']['nodes'][0]['icon']=='🔥';assert all(rows[k]['draft']==v for k,v in bodies.items());unchanged();f.checked('저장된 copy의 private frame 아이콘 Save는 원자 후보/CAS를 사용하고 공개 ABI·원래 copy 출처·본문 record를 유지한다')
  f.close_author();g['restart'](2);g['reopen']();expect(icon('left')).to_have_text('★');g['nested_enter'](['left']);expect(icon('body')).to_have_text('🔥');f.close_author();r=g['d'].review();r.locator('[data-reject]').click();expect(r).to_be_hidden();unchanged();r=g['d'].review()
  if r.locator('[data-additional-changes]').count():r.locator('[data-review-advanced]').click();r.locator('[data-advanced-reviewed]').check()
  expect(r.locator('#confirm')).to_be_enabled();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();assert all(p.read_bytes()==v for p,v in donor.items());f.checked(('독립' if g['d'].is_view else '기본')+' 정보 창의 copy 재진입·cold·Review 취소·명시 Confirm은 두 아이콘을 복원하고 외부/부모 원본을 쓰지 않는다');assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'action-copy-icons.png'));f.browser.close()
finally:
 f.stop();(f.case/'action-copy-icon-evidence.json').write_text(json.dumps(dict(checks=f.checks,errors=f.errors,detached=g['d'].is_view,actualWindows=False,actualMobile=False),ensure_ascii=False,indent=2)+'\n')
print('EVIDENCE',f.case,flush=True)
