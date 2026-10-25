"""Original detail popovers, one Save and a shared real caller, no new UI."""
import json
import time
import shutil
from playwright.sync_api import sync_playwright,expect
import v536_information_shared_outputs_fixture as x

f,d=x.f,x.d
def pending():return [(k,v) for k,v in d.pending() if v['kind']=='function-edit']
def schema():
    state=f.state()
    return next(row['schema'] for row in state['editorViews'] if row['view']=='1') if d.is_view else state['schema']
def popup(fn):
    f.owner().locator('[data-inline-method="'+fn+'"] > .function-node-heading').dblclick(position={'x':190,'y':3})
    p=f.page.locator('.function-detail-popover');expect(p).to_be_visible();return p
def preserved():
    expect(f.owner().get_by_label('Power 기본값',exact=True)).to_have_value('9223372036854775806')
    assert abs(f.owner().bounding_box()['width']-460)<1
    x.unchanged()
def restart(i):
    held=f.pending();f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(i);f.page=f.setup()
    f.page.set_viewport_size({'width':2300,'height':1700})
    if d.is_view:f.owner=lambda:f.page.locator('.window[data-key=editor-1]')
    expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo');f.idle();return held
def wait(endpoint,start,action=None,ok=True):
    deadline=time.monotonic()+120
    while time.monotonic()<deadline:
        ids={row['invoke']['requestId'] for row in f.traffic[start:] if row.get('invoke',{}).get('endpoint')==endpoint and (action is None or row['invoke']['input'].get('action')==action)}
        rows=[row['result'] for row in f.traffic[start:] if row.get('result',{}).get('requestId') in ids and row['result'].get('error',{}).get('code')!='stale_revision']
        if rows:assert bool(rows[-1]['ok'])==ok,rows[-1];f.idle();return
        f.page.wait_for_timeout(20)
    raise AssertionError((endpoint,action,str(f.case)))
def saved():
    deadline=time.monotonic()+90
    while pending() and time.monotonic()<deadline:f.page.wait_for_timeout(20)
    assert not pending(),f.owner().locator('[data-element-error]').all_text_contents()

try:
    f.start(0);f.invoke('select',{'id':x.owner});f.invoke('saveDraft',{})
    checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes()
    with sync_playwright() as pw:
        expect.set_options(timeout=60000)
        f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});d.open_info()
        p=popup(x.functions[0]);p.locator('[data-signature-id=arg0] [data-signature-name]').fill('취소한 이름');p.locator('[data-detail-cancel]').click()
        assert not pending()
        for fn,name in zip(x.functions,['leftCount','rightCount']):
            p=popup(fn);p.locator('[data-signature-id=arg1] [data-signature-name]').fill(name);p.get_by_role('button',name='저장',exact=True).click();expect(p).to_have_count(0)
        held=pending();assert len(held)==2
        f.owner().locator('[data-own-functions-toggle]').press('Control+z');assert len(pending())==1
        f.owner().locator('[data-own-functions-toggle]').press('Control+y');assert pending()==held
        preserved();restart(1);assert pending()==held;preserved()
        f.checked('두 원본 상세창의 취소·명시 입력·Undo/Redo·미저장 cold는 두 함수 입력과 exact64 값을 보존한다')
        if x.mode=='cancel':
            f.owner().locator('[data-element-action=discard]').click();f.idle();assert not pending() and checkpoint.read_bytes()==baseline
            restart(2);assert not pending() and checkpoint.read_bytes()==baseline;preserved()
            f.checked('한 변경 취소와 cold는 두 함수 입력만 취소하고 공유 caller·원래 checkpoint를 유지한다')
            raise SystemExit(0)
        if x.mode=='projects':
            first=f.state()['listingId'];f.page.close();f.stop()
            other=f.case/'other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory'))
            f.env['CONFECTORY_WEB_PROJECT']=str(other/'project.cproj')
            f.start(2);f.invoke('select',{'id':x.owner});f.invoke('saveDraft',{})
            second=f.state()['listingId'];peer_checkpoint=next(other.glob('.confectory/edit-workspaces/*/draft.json'));peer_saved=peer_checkpoint.read_bytes()
            f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700})
            def enter(listing):
                f.page.locator('.brand').click();expect(f.page.locator('.home-grid')).to_be_visible()
                f.page.locator('[data-enter="'+listing+'"]').click();expect(f.page.locator('.work-body')).to_be_visible();f.idle()
            enter(first);assert pending()==held
            p=popup(x.functions[1]);p.locator('form').evaluate('el=>globalThis.staleSharedContractForm=el')
            enter(second);d.open_info();assert not pending()
            f.page.evaluate("()=>staleSharedContractForm.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}))")
            assert not pending() and checkpoint.read_bytes()==baseline and peer_checkpoint.read_bytes()==peer_saved
            enter(first);assert pending()==held;preserved()
            f.checked('동일 namespace 프로젝트 전환은 두 계약 입력을 A에 보관하고 오래된 상세창의 B 적용을 막는다')
            raise SystemExit(0)
        if x.mode=='conflict':
            sc=schema();f.invoke('editDescription',{'id':x.owner,'hash':sc['textHash'],'revision':sc['revision'],'value':'peer 설명 보존'})
            f.rejected_save();assert pending()==held and checkpoint.read_bytes()==baseline
            assert f.metadata('inspect',text=f.state()['draft']['text'])['description']=='peer 설명 보존';preserved()
            f.checked('다른 창의 실제 source 경합은 두 함수 전체 미적용이며 peer 입력과 사용자 입력을 유지한다')
            raise SystemExit(0)
        if x.mode=='loss':
            applies,queries,masked=set(),set(),set()
            def intercept(route):
                body=route.request.post_data_json
                if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
                    action=body.get('input',{}).get('action')
                    if action=='applySlots':applies.add(body['requestId'])
                    elif applies and action=='settledSlots':queries.add(body['requestId'])
                response=route.fetch();payload=response.json()
                for row in payload.get('results',[]):
                    if row['requestId'] in applies|queries:
                        rid=row['requestId'];masked.add(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport_lost'})
                route.fulfill(response=response,json=payload)
            f.page.route('**/api/request',intercept);f.owner().locator('[data-element-action=save]').click()
            deadline=time.monotonic()+100
            while time.monotonic()<deadline and not queries&masked:f.page.wait_for_timeout(20)
            assert len(applies)==1 and queries&masked and pending()
            f.page.unroute_all(behavior='wait');restart(2);mark=len(f.traffic)
            f.owner().locator('[data-element-action=save]').click();wait('blueprint',mark,'settledSlots');saved()
            assert not any(row.get('invoke',{}).get('input',{}).get('action')=='applySlots' for row in f.traffic[mark:])
            x.verify(checkpoint);preserved()
            f.checked('저장/결과조회 응답 유실 뒤 cold는 결합 receipt를 확인하고 두 계약을 중복 적용하지 않는다')
            raise SystemExit(0)
        if x.mode=='storage':
            checkpoint.chmod(0o400)
            try:
                mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();wait('blueprint',mark,'applySlots',False)
                assert pending()==held and checkpoint.read_bytes()==baseline;preserved()
            finally:checkpoint.chmod(0o600)
            f.checked('화면 checkpoint 실패는 양쪽 계약·공유 caller 전체 미적용과 입력 보존 후 재시도를 허용한다')
        if x.mode=='retry':
            p=popup(x.functions[1]);p.locator('[data-signature-id=arg0] [data-signature-type]').click()
            types=f.page.get_by_role('dialog',name='속성 타입 선택',exact=True);types.locator('[data-type=string]').click()
            p.get_by_role('button',name='저장',exact=True).click()
            remap_cancel=f.page.locator('[data-abi-remap-cancel]');expect(remap_cancel).to_be_visible()
            remap_cancel.click();expect(remap_cancel).to_have_count(0);f.idle()
            mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();wait('blueprint',mark,'applySlots',False)
            assert len(pending())==2 and checkpoint.read_bytes()==baseline;preserved()
            f.owner().locator('[data-own-functions-toggle]').press('Control+z');assert pending()==held
            f.checked('마지막 함수 타입 변경 거절은 양쪽 입력을 보존하고 Undo 후 원래 기준으로 명시 재시도한다')
        mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();wait('blueprint',mark,'applySlots');saved()
        x.verify(checkpoint);preserved();restart(2);assert not pending();x.verify(checkpoint)
        review=d.review();review.locator('[data-reject]').click();preserved();review=d.review()
        if review.locator('[data-review-advanced]').count():
            review.locator('[data-review-advanced]').click()
            if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
        mark=len(f.traffic);review.locator('#confirm').click();wait('confirmGroup',mark);expect(review).to_have_count(0)
        restart(3)
        for fn,sig in zip(x.functions,x.nexts):assert x.n.canonical(next(row for row in schema()['ownFunctions'] if row['id']==fn)['signature'])==sig
        calls=json.loads((f.project/'caller.graph.json').read_text())['nodes']
        assert calls[1]['arguments']=={'amount':{'node':'invoke','output':'leftCount'}}
        assert json.loads((f.project/'caller.graph.json').read_text())['exits']['return']=={'node':'invoke_second','output':'rightCount'}
        for fn,name in zip(x.functions,['leftCount','rightCount']):
            expect(f.owner().locator('[data-inline-method="'+fn+'"] [data-pin-side=outputs] [data-function-pin-name="'+name+'"]')).to_have_attribute('data-function-pin-type','정수')
        for path in ['function.node.json','second.node.json']:
            assert json.loads((f.project/path).read_text())['source']==json.loads(x.snapshot[path])['source']
        f.checked('원본 460px 기본/독립 화면의 한 Save·cold·Review 취소/Confirm은 두 계약과 공유 caller를 함께 확정한다')
        f.page.screenshot(path=str(f.case/'shared-outputs.png'))
        assert not f.errors and not f.external,(f.errors,f.external)
        f.browser.close()
except Exception:
    try:
        (f.case/'shared-outputs-failure.json').write_text(json.dumps({'pending':f.pending(),'traffic':f.traffic[-35:]},ensure_ascii=False,indent=2))
        f.page.screenshot(path=str(f.case/'failure.png'))
    except Exception:pass
    raise
finally:
    print(json.dumps({'checks':f.checks,'view':d.is_view,'mode':x.mode,'evidence':str(f.case),'actualEngineRenderer':True,'actualWindows':False},ensure_ascii=False))
    f.stop()
