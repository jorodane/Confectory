"""Original detail popovers, one Save and a shared real caller, no new UI."""
import json
import time
import shutil
import os
from playwright.sync_api import sync_playwright,expect
if os.environ.get('CONFECTORY_SHARED_INPUT_DEFINITION_RETURN_MIX') == '1':
    import v536_information_shared_input_definition_return_mix_fixture as x
elif os.environ.get('CONFECTORY_SHARED_INPUT_OUTPUT_DEFINITION_MIX') == '1':
    import v536_information_shared_input_output_definition_mix_fixture as x
elif os.environ.get('CONFECTORY_SHARED_INPUT_RETURN_MIX') == '1':
    import v536_information_shared_input_return_mix_fixture as x
elif os.environ.get('CONFECTORY_SHARED_INPUT_NAME_OUTPUT_DEFINITIONS') == '1':
    import v536_information_shared_input_name_output_definitions_fixture as x
elif os.environ.get('CONFECTORY_SHARED_INPUT_NAME_OUTPUT_MIX') == '1':
    import v536_information_shared_input_name_output_mix_fixture as x
elif os.environ.get('CONFECTORY_SHARED_OUTPUT_DEFINITION_MIX') == '1':
    import v536_information_shared_output_definition_mix_fixture as x
elif os.environ.get('CONFECTORY_SHARED_OUTPUT_RETURN_MIX') == '1':
    import v536_information_shared_output_return_mix_fixture as x
elif os.environ.get('CONFECTORY_SHARED_INPUT_MIX') == '1':
    import v536_information_shared_input_mix_fixture as x
elif os.environ.get('CONFECTORY_SHARED_INPUT_DEFINITIONS') == '1':
    import v536_information_shared_input_definitions_fixture as x
elif os.environ.get('CONFECTORY_SHARED_INPUTS_WITH_OUT') == '1':
    import v536_information_shared_inputs_with_out_fixture as x
elif os.environ.get('CONFECTORY_SHARED_MIXED_TYPES') == '1':
    import v536_information_shared_mixed_types_fixture as x
elif os.environ.get('CONFECTORY_SHARED_IO') == '1':
    import v536_information_shared_io_fixture as x
elif os.environ.get('CONFECTORY_SHARED_LOCAL_IMPORTS') == '1':
    import v536_information_shared_local_imports_fixture as x
else:
    import v536_information_shared_return_types_fixture as x

f,d=x.f,x.d
combined_io=hasattr(x,'caller_arguments')
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
def reject_conflict():
    # A peer edit may have rendered the boundary warning before Save. Observe
    # the current text as well as later mutations; checkpoint/input assertions
    # below still prove that the attempted Save applied nothing.
    f.page.evaluate('''()=>{globalThis.boundaryMessages=[];const collect=()=>{for(const el of document.querySelectorAll('[data-element-error],#status')){const text=el.textContent;if(text&&!boundaryMessages.includes(text))boundaryMessages.push(text)}};collect();globalThis.boundaryObserver=new MutationObserver(collect);boundaryObserver.observe(document.body,{subtree:true,childList:true,characterData:true})}''')
    mark=len(f.traffic)
    try:
        f.owner().locator('[data-element-action=save]').click()
        f.page.wait_for_function('()=>boundaryMessages.some(text=>/바뀌|입력.*유지|실패|완료하지|consumer_error|stale|changed/i.test(text))',timeout=30000)
        f.idle()
        ids={r['invoke']['requestId'] for r in f.traffic[mark:] if r.get('invoke',{}).get('endpoint')=='blueprint' and r['invoke']['input'].get('action')=='applySlots'}
        assert not any(r.get('result',{}).get('requestId') in ids and r['result'].get('ok') for r in f.traffic[mark:])
    finally:f.page.evaluate('()=>boundaryObserver.disconnect()')
def finish_early():
    # Let owned intercepted requests finish before exiting Playwright's context.
    # All product/checkpoint/input assertions run before this test-only cleanup.
    f.page.unroute_all(behavior='wait')
    f.browser.close()
    raise SystemExit(0)

try:
    f.start(0);f.invoke('select',{'id':x.owner});f.invoke('saveDraft',{})
    checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes()
    with sync_playwright() as pw:
        expect.set_options(timeout=60000)
        f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});d.open_info()
        p=popup(x.functions[0]);p.locator('[data-signature-id=arg0] [data-signature-name]').fill('취소한 이름');p.locator('[data-detail-cancel]').click()
        assert not pending()
        for index,fn in enumerate(x.functions):
            p=popup(fn)
            input_changed=not hasattr(x,'edit_contract') and combined_io and x.nexts[index]['args'][0]['type']!=x.old['args'][0]['type']
            output_changed=not hasattr(x,'edit_contract') and (not combined_io or x.nexts[index]['args'][2]['type']!=x.old['args'][2]['type'])
            if hasattr(x,'edit_contract'):x.edit_contract(p,index)
            if input_changed:
                p.locator('[data-signature-id=arg0] [data-signature-type]').click()
                f.page.get_by_role('dialog',name='속성 타입 선택',exact=True).locator('[data-type=string]').click()
            if output_changed:
                p.locator('[data-signature-id='+('arg2' if combined_io else 'return')+'] [data-signature-type]').click()
                f.page.get_by_role('dialog',name='속성 타입 선택',exact=True).locator('[data-type=double]').click()
            f.page.screenshot(path=str(f.case/('shared-return-'+str(index)+'.png')))
            p.get_by_role('button',name='저장',exact=True).click()
            if hasattr(x,'has_mapping_dialog') and not x.has_mapping_dialog(index):
                f.idle();expect(f.page.locator('[data-abi-remap-accept]')).to_have_count(0)
                continue
            has_uses=input_changed and (not hasattr(x,'usage_replacement_required') or x.usage_replacement_required(index))
            m=f.page.get_by_role('dialog',name=x.remap_title(index) if hasattr(x,'remap_title') else '입력 연결 갱신' if has_uses else '호출 계약 갱신',exact=True);expect(m).to_be_visible()
            if hasattr(x,'select_contract'):x.select_contract(m,index)
            if output_changed:m.locator('[data-abi-target^="output:"] [data-abi-input=value]').select_option('pin:real')
            if input_changed:
                for target in m.locator('section[data-abi-target]').all():
                    key=target.get_attribute('data-abi-target')
                    if key.startswith('output:'):continue
                    target.locator('[data-abi-input=amount]').select_option('value')
                    target.locator('[data-abi-value=amount]').fill(x.replacement if key.startswith('use:') else x.text_value)
                m.locator('[data-abi-disconnect=amount]').select_option('disconnect')
            if output_changed:m.locator('[data-abi-output='+('count' if combined_io else 'return')+']').select_option('return' if combined_io else 'count')
            f.page.screenshot(path=str(f.case/('shared-return-mapping-'+str(index)+'.png')))
            m.locator('[data-abi-remap-accept]').click();expect(m).to_have_count(0);f.idle()
        held=pending();assert len(held)==2
        for _ in range(2):f.owner().locator('[data-own-functions-toggle]').press('Control+z')
        assert len(pending())==1
        for _ in range(2):f.owner().locator('[data-own-functions-toggle]').press('Control+y')
        assert pending()==held
        preserved();restart(1);assert pending()==held;preserved()
        f.checked('두 원본 상세창의 취소·명시 대응·Undo/Redo·미저장 cold는 두 함수 입력과 exact64 값을 보존한다')
        if x.mode=='cancel':
            f.owner().locator('[data-element-action=discard]').click();f.idle();assert not pending() and checkpoint.read_bytes()==baseline
            restart(2);assert not pending() and checkpoint.read_bytes()==baseline;preserved()
            f.checked('한 변경 취소와 cold는 두 함수 입력만 취소하고 공유 caller·원래 checkpoint를 유지한다')
            finish_early()
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
            f.checked('동일 namespace 프로젝트 전환은 두 함수 계약 입력을 A에 보관하고 오래된 상세창의 B 적용을 막는다')
            finish_early()
        if x.mode=='conflict':
            sc=schema();f.invoke('editDescription',{'id':x.owner,'hash':sc['textHash'],'revision':sc['revision'],'value':'peer 설명 보존'})
            try:reject_conflict()
            except Exception:
                (f.case/'conflict-boundary.json').write_text(json.dumps({'pending':pending(),'traffic':f.traffic[-45:],
                    'boundaryMessages':f.page.evaluate('()=>globalThis.boundaryMessages'),
                    'visibleErrors':f.page.locator('[data-element-error]').all_text_contents()},ensure_ascii=False,indent=2))
                f.page.screenshot(path=str(f.case/'conflict-boundary.png'))
                raise
            assert pending()==held and checkpoint.read_bytes()==baseline
            assert f.metadata('inspect',text=f.state()['draft']['text'])['description']=='peer 설명 보존';preserved()
            f.checked('다른 창의 실제 source 경합은 두 함수 전체 미적용이며 peer 입력과 사용자 입력을 유지한다')
            finish_early()
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
            f.checked('저장/결과조회 응답 유실 뒤 cold는 결합 receipt를 확인하고 두 함수 계약을 중복 적용하지 않는다')
            finish_early()
        if x.mode=='storage':
            checkpoint.chmod(0o400)
            try:
                mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();wait('blueprint',mark,'applySlots',False)
                assert pending()==held and checkpoint.read_bytes()==baseline;preserved()
            finally:checkpoint.chmod(0o600)
            f.checked('화면 checkpoint 실패는 양쪽 계약·공유 caller 전체 미적용과 입력 보존 후 재시도를 허용한다')
        if x.mode=='retry':
            p=popup(x.functions[1]);p.locator('[data-signature-id='+('arg1' if combined_io else 'arg0')+'] [data-signature-type]').click()
            types=f.page.get_by_role('dialog',name='속성 타입 선택',exact=True);types.locator('[data-type=string]').click()
            p.get_by_role('button',name='저장',exact=True).click()
            remap_cancel=f.page.locator('[data-abi-remap-cancel]');expect(remap_cancel).to_be_visible()
            remap_cancel.click();expect(remap_cancel).to_have_count(0);f.idle()
            mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();wait('blueprint',mark,'applySlots',False)
            assert len(pending())==2 and checkpoint.read_bytes()==baseline;preserved()
            f.owner().locator('[data-own-functions-toggle]').press('Control+z');assert pending()==held
            f.checked('마지막 함수의 미완성 대응 거절은 양쪽 입력을 보존하고 Undo 후 원래 기준으로 명시 재시도한다')
        mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();wait('blueprint',mark,'applySlots');saved()
        x.verify(checkpoint);preserved();restart(2);assert not pending();x.verify(checkpoint)
        review=d.review();review.locator('[data-reject]').click();preserved();review=d.review()
        if review.locator('[data-review-advanced]').count():
            review.locator('[data-review-advanced]').click()
            if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
        mark=len(f.traffic);review.locator('#confirm').click();wait('confirmGroup',mark);expect(review).to_have_count(0)
        restart(3)
        for fn,sig in zip(x.functions,x.nexts):assert x.n.canonical(next(row for row in schema()['ownFunctions'] if row['id']==fn)['signature'])==sig
        x.verify_live()
        calls=json.loads((f.project/'caller.graph.json').read_text())['nodes']
        assert calls[1]['arguments']==(x.caller_arguments(1) if combined_io else {'amount':x.binding('invoke',x.destination),'real':{'constant':2.5}})
        assert json.loads((f.project/'caller.graph.json').read_text())['exits']==(x.caller_exits() if combined_io else {'return':x.binding('invoke_second',x.destination)})
        for index,fn in enumerate(x.functions):
            if hasattr(x,'verify_pins'):
                x.verify_pins(f.owner(),index)
                continue
            expect(f.owner().locator('[data-inline-method="'+fn+'"] [data-pin-side=outputs] [data-function-pin-name="'+('count' if combined_io else '결과')+'"]')).to_have_attribute('data-function-pin-type','실수' if not combined_io or x.nexts[index]['args'][2]['type']=='double' else '정수')
            if combined_io:expect(f.owner().locator('[data-inline-method="'+fn+'"] [data-pin-side=inputs] [data-function-pin-name=amount]')).to_have_attribute('data-function-pin-type','글자' if x.nexts[index]['args'][0]['type']=='string' else '정수')
            for name in x.removed:
                label='결과' if name=='return' else name
                expect(f.owner().locator('[data-inline-method="'+fn+'"] [data-pin-side=outputs] [data-function-pin-name="'+label+'"]')).to_have_count(0)
            for name in x.added:
                label='결과' if name=='return' else name
                expect(f.owner().locator('[data-inline-method="'+fn+'"] [data-pin-side=outputs] [data-function-pin-name="'+label+'"]')).to_have_count(1)
        for path in ['function.node.json','second.node.json']:
            assert json.loads((f.project/path).read_text())['source']==json.loads(x.snapshot[path])['source']
        f.checked('원본 460px 기본/독립 화면의 한 Save·cold·Review 취소/Confirm은 두 함수 계약과 공유 caller를 함께 확정한다')
        f.page.screenshot(path=str(f.case/'shared-return-types.png'))
        assert not f.errors and not f.external,(f.errors,f.external)
        f.browser.close()
except Exception:
    failure={'traffic':f.traffic[-80:],'checks':f.checks}
    try:failure['pending']=f.pending()
    except Exception:failure['pendingUnavailableAfterContextClose']=True
    (f.case/'shared-return-types-failure.json').write_text(json.dumps(failure,ensure_ascii=False,indent=2))
    try:
        f.page.screenshot(path=str(f.case/'failure.png'))
    except Exception:pass
    raise
finally:
    print(json.dumps({'checks':f.checks,'view':d.is_view,'mode':x.mode,'evidence':str(f.case),'actualEngineRenderer':True,'actualWindows':False},ensure_ascii=False))
    f.stop()
