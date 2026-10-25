"""Existing v536 function/C# dialogs distinguish an owned copy from its donor."""
import json,time,shutil
from playwright.sync_api import sync_playwright,expect
import v536_information_saved_copy_fixture as x
f,d,owner,fn,mode=x.f,x.d,x.owner,x.fn,x.mode
x.edited=x.edited.replace('\r\n','\n')
def pending():return [(k,v) for k,v in d.pending() if v['kind']=='function-edit']
def preserved():
    x.unchanged();expect(f.owner().get_by_label('Power 기본값',exact=True)).to_have_value('9223372036854775806')
    assert not f.page.locator('#app').evaluate('el=>el.inert')
def restart(i):
    held=f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700})
    if d.is_view:f.owner=lambda:f.page.locator('.window[data-key=editor-1]')
    expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo');f.idle();return held
def cpp(body):
    f.owner().locator('[data-inline-method="'+fn+'"] [data-function-edit], [data-inline-method="'+fn+'"] [data-function-write-direct]').click()
    p=f.page.get_by_role('dialog',name='구현 선택',exact=True);expect(p).to_be_visible()
    expect(p.locator('[data-information-body="'+x.body_id+'"]')).to_contain_text('소유 복사본')
    p.locator('[data-information-body="'+body+'"]').click()
    dialog=f.page.locator('[role=dialog]:has([data-code-source])');expect(dialog).to_be_visible()
    assert 'public long Invoke(long nativeAmount, out long nativeTotal)' in dialog.locator('[data-code-source]').input_value()
    return dialog
def fill(dialog,partial=False):
    dialog.locator('[data-code-source]').evaluate(r"el=>{el.focus();el.setSelectionRange(el.value.indexOf('\n{\n')+3,el.value.lastIndexOf('\n}'));}")
    f.page.keyboard.insert_text(x.edited+('unfinished' if partial else ''));f.idle()
def accept_mapping(required=False):
    modal=f.page.locator('[role=dialog]:has([data-abi-remap-accept])')
    if required:expect(modal).to_be_visible()
    if modal.count():
        if required:
            native=modal.locator('[data-abi-target^="native:"]');expect(native).to_have_count(1)
            expect(native.locator('[data-abi-output=return]')).to_have_value('return')
            expect(native.locator('[data-abi-output=nativeTotal]')).to_have_value('nativeTotal')
        modal.locator('[data-abi-remap-accept]').click();f.idle();expect(modal).to_have_count(0)
def wait(endpoint,start,ok=True,action=None):
    deadline=time.monotonic()+120
    while time.monotonic()<deadline:
        ids={r['invoke']['requestId'] for r in f.traffic[start:] if r.get('invoke',{}).get('endpoint')==endpoint and (action is None or r['invoke']['input'].get('action')==action)}
        rows=[r['result'] for r in f.traffic[start:] if r.get('result',{}).get('requestId') in ids and r['result'].get('error',{}).get('code')!='stale_revision']
        if rows:assert bool(rows[-1]['ok'])==ok,rows[-1];f.idle();return
        f.page.wait_for_timeout(20)
    raise AssertionError({'waiting':endpoint,'action':action,'evidence':str(f.case)})
try:
    f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes()
    with sync_playwright() as pw:
        expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});d.open_info()
        f.owner().locator('[data-inline-method="'+fn+'"] > .function-node-heading').dblclick(position={'x':190,'y':3});popover=f.page.locator('.function-detail-popover');expect(popover).to_be_visible();popover.locator('[data-signature-id=arg0] [data-signature-name]').fill('renamed');popover.get_by_role('button',name='저장',exact=True).click();f.idle();accept_mapping()
        dialog=cpp(x.donor_id);dialog.locator('[data-code-save]').click();f.idle()
        assert pending()[0][1]['mapping']['bodies'][x.donor_id]['text']==x.original
        initial=pending();dialog=cpp(x.body_id);fill(dialog);dialog.locator('[data-code-cancel]').click();assert pending()==initial;preserved()
        dialog=cpp(x.body_id);fill(dialog,True);held=restart(1);assert f.pending()==held
        dialog=cpp(x.body_id);assert x.edited+'unfinished' in dialog.locator('[data-code-source]').input_value();fill(dialog);f.page.screenshot(path=str(f.case/'copy-csharp.png'));dialog.locator('[data-code-save]').click();f.idle();accept_mapping(True)
        value=pending()[0][1];assert value['mapping']['copies'][x.graph_id]['provenance']==x.prepared['graph']['copySource'];assert value['mapping']['bodies'][x.body_id]['text']==x.edited
        f.owner().locator('[data-own-functions-toggle]').press('Control+z');f.owner().locator('[data-own-functions-toggle]').press('Control+y');assert pending()[0][1]==value
        held=restart(2);assert f.pending()==held and pending()[0][1]==value;preserved()
        f.checked('원본 UI에서 donor/소유 copy를 명시 선택하고 CRLF 원문·취소·불완전 입력·Undo/Redo·cold를 보존한다')
        if mode.endswith('conflict'):
            s=f.state()['schema'];f.invoke('editDescription',{'id':owner,'hash':s['textHash'],'revision':s['revision'],'value':'다른 창의 새 입력'})
            f.rejected_save();assert pending()[0][1]==value and checkpoint.read_bytes()==baseline;preserved();f.checked('실제 경합은 copy·선언·caller 전체 미적용이며 새 입력과 donor를 보존한다')
        elif mode.endswith('cancel'):
            f.owner().locator('[data-element-action=discard]').click();f.idle();assert not pending() and checkpoint.read_bytes()==baseline;preserved();restart(3);assert not pending();f.checked('전체 취소와 재시작은 소유 copy·선언·caller를 반영하지 않고 donor/출처를 보존한다')
        elif mode.endswith('projects'):
            listing=f.state()['listingId'];f.page.close();f.stop();other=f.case/'other root'/'owned project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory'));f.env['CONFECTORY_WEB_PROJECT']=str(other/'project.cproj');f.start(3);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});second=f.state()['listingId'];other_checkpoint=next(other.glob('.confectory/edit-workspaces/*/draft.json'));other_before=other_checkpoint.read_bytes();f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700})
            def enter(id):
                f.page.locator('.brand').click();expect(f.page.locator('.home-grid')).to_be_visible();f.page.locator('[data-enter="'+id+'"]').click();expect(f.page.locator('.work-body')).to_be_visible();f.idle()
            enter(listing);assert pending()[0][1]==value;dialog=cpp(x.body_id);dialog.locator('[data-code-save]').evaluate('el=>globalThis.staleCopySave=el');dialog.locator('[data-code-cancel]').click();enter(second);d.open_info();assert not pending();f.page.evaluate('()=>staleCopySave.click()');assert not pending() and other_checkpoint.read_bytes()==other_before and checkpoint.read_bytes()==baseline;enter(listing);assert pending()[0][1]==value;preserved();f.checked('두 프로젝트/독립 창에서 copy ID가 같아도 입력과 닫힌 저장 동작은 원래 문맥에 묶인다')
        else:
            if mode.endswith('simple'):
                mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();wait('blueprint',mark,True,'applySlots')
            else:
                checkpoint.chmod(0o400)
                try:mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();wait('blueprint',mark,False,'applySlots');assert pending()[0][1]==value and checkpoint.read_bytes()==baseline;preserved()
                finally:checkpoint.chmod(0o600)
                f.checked('화면 저장 실패는 선언이나 copy만 남기지 않고 전체 입력과 donor 바이트를 보존한다')
                applies,queries,masked=set(),set(),set()
                def intercept(route):
                    body=route.request.post_data_json
                    if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
                        action=body.get('input',{}).get('action')
                        if action=='applySlots':applies.add(body['requestId'])
                        elif applies and action=='settledSlots':queries.add(body['requestId'])
                    response=route.fetch();payload=response.json()
                    for row in payload.get('results',[]):
                        if row['requestId'] in applies|queries:rid=row['requestId'];masked.add(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport_lost'})
                    route.fulfill(response=response,json=payload)
                f.page.route('**/api/request',intercept);f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+90
                while time.monotonic()<deadline and not queries&masked:f.page.wait_for_timeout(20)
                assert len(applies)==1 and queries&masked and pending();f.page.unroute_all(behavior='wait');held=restart(3);assert f.pending()==held;mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();wait('blueprint',mark,True,'settledSlots');assert not any(r.get('invoke',{}).get('input',{}).get('action')=='applySlots' for r in f.traffic[mark:]);f.checked('응답/receipt 유실 후 cold 재시도는 결과 조회로 저장을 확인하며 copy를 중복 적용하지 않는다')
            deadline=time.monotonic()+60
            while pending() and time.monotonic()<deadline:f.page.wait_for_timeout(20)
            assert not pending();x.verify(checkpoint);preserved();restart(4);x.verify(checkpoint)
            review=d.review();review.locator('[data-reject]').click();preserved();review=d.review()
            if review.locator('[data-review-advanced]').count():
                review.locator('[data-review-advanced]').click()
                if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
            mark=len(f.traffic);review.locator('#confirm').click();wait('confirmGroup',mark);expect(review).to_have_count(0)
            assert json.loads((f.project/x.body_path).read_text())['source']==x.edited
            assert (f.project/'whole-original.csbody').read_bytes()==x.snapshot['whole-original.csbody']
            f.checked('화면 저장·Review 취소/재검토·명시 Confirm·cold는 copy만 갱신하고 donor와 원래 출처를 보존한다')
        assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'copy-final.png'));f.browser.close()
except Exception:
    try:(f.case/'failure.json').write_text(json.dumps({'checks':f.checks,'traffic':f.traffic[-40:],'state':f.state()},ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'failure.png'))
    except Exception:pass
    raise
finally:
    f.stop();print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'mode':mode,'nativeWindows':False,'deviceTouch':False},ensure_ascii=False))
