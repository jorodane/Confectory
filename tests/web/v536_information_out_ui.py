"""Original out row editing with a scoped producer and real output consumer."""
import json
import time
import shutil
from playwright.sync_api import sync_playwright, expect
import v536_information_out_fixture as x
n=x.n

f, d, owner, fn = x.f, x.d, x.owner, x.fn
mode=x.mode
snapshot = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}


def pending():
    return [(key, value) for key, value in d.pending() if value['kind'] == 'function-edit']


def heading():
    return f.owner().locator('[data-inline-method="' + fn + '"] > .function-node-heading')


def schema():
    s = f.state()
    return next(row['schema'] for row in s['editorViews'] if row['view'] == '1') if d.is_view else s['schema']


def preserved():
    expect(f.owner().get_by_label('Power 기본값', exact=True)).to_have_value('9223372036854775806')
    assert not f.page.locator('#app').evaluate('el=>el.inert')
    assert all((f.project / p).read_bytes() == b for p, b in snapshot.items())


def popup():
    heading().dblclick(position={'x': 190, 'y': 3})
    p = f.page.locator('.function-detail-popover')
    expect(p).to_be_visible()
    return p


def restart(i):
    held = f.pending()
    f.page.close()
    f.stop()
    f.start(i)
    f.page = f.setup()
    f.page.set_viewport_size({'width': 2300, 'height': 1700})
    if d.is_view:
        f.owner = lambda: f.page.locator('.window[data-key=editor-1]')
    expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo')
    f.idle()
    return held


def wait(endpoint, start, ok=True, action=None):
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        ids = {row['invoke']['requestId'] for row in f.traffic[start:] if row.get('invoke', {}).get('endpoint') == endpoint and (action is None or row['invoke']['input'].get('action') == action)}
        rows = [row['result'] for row in f.traffic[start:] if row.get('result', {}).get('requestId') in ids and row['result'].get('error', {}).get('code') != 'stale_revision']
        if rows:
            assert bool(rows[-1]['ok']) == ok, rows[-1]
            f.idle()
            return
        f.page.wait_for_timeout(20)
    raise AssertionError({'endpoint': endpoint, 'evidence': str(f.case)})


try:
    f.start(0)
    f.invoke('select', {'id': owner})
    f.invoke('saveDraft', {})
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    baseline = checkpoint.read_bytes()
    with sync_playwright() as pw:
        expect.set_options(timeout=60000)
        f.browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        f.page = f.setup()
        f.page.set_viewport_size({'width': 2300, 'height': 1700})
        d.open_info()
        p = popup()
        p.locator('[data-signature-id=arg1] [data-signature-name]').fill('취소 입력')
        p.locator('[data-detail-cancel]').click()
        assert not pending() and checkpoint.read_bytes() == baseline
        p = popup()
        p.locator('[data-signature-id=arg1] [data-signature-name]').fill('count2')
        p.locator('[data-detail-description]').fill('출력 이름과 설명 함께')
        if mode=='both':p.locator('[data-signature-id=arg0] [data-signature-name]').fill('amount2')
        p.get_by_role('button', name='저장', exact=True).click()
        expect(p).to_have_count(0)
        value = pending()[0][1]
        assert value['mapping'] == x.mapping and value['signature']==x.signature
        f.owner().locator('[data-own-functions-toggle]').press('Control+z')
        assert not pending()
        f.owner().locator('[data-own-functions-toggle]').press('Control+y')
        assert pending()[0][1] == value
        preserved()
        held = restart(1)
        assert f.pending() == held and pending()[0][1]['mapping'] == value['mapping']
        preserved()
        f.checked('원본 상세창 취소·out 이름 편집·Undo/Redo·미저장 cold는 명시적 pin ID와 입력/기존 원문을 보존한다')
        if mode == 'cancel':
            f.owner().locator('[data-element-action=discard]').click()
            f.idle()
            assert not pending() and checkpoint.read_bytes()==baseline
            preserved()
            restart(2)
            assert not pending() and checkpoint.read_bytes()==baseline
            assert n.canonical(next(row for row in schema()['ownFunctions'] if row['id']==fn)['signature'])==x.original_signature
            preserved()
            f.checked('실제 변경 취소와 cold는 함수 계약 입력만 취소하고 원래 caller·checkpoint·본문을 보존한다')
            raise SystemExit(0)
        if mode == 'conflict':
            sc=schema()
            f.invoke('editDescription',{'id':owner,'hash':sc['textHash'],'revision':sc['revision'],'value':'다른 편집자 입력 보존'})
            start=len(f.traffic)
            f.rejected_save()
            messages=f.page.evaluate('()=>boundaryMessages')
            assert any('편집 기준이나 입력 형식' in message for message in messages), messages
            assert not any(row.get('invoke',{}).get('input',{}).get('action')=='applySlots' for row in f.traffic[start:])
            assert pending()[0][1]['mapping']==value['mapping'] and checkpoint.read_bytes()==baseline
            assert f.metadata('inspect',text=f.state()['draft']['text'])['description']=='다른 편집자 입력 보존'
            preserved()
            f.checked('실제 source 충돌은 전체 미적용이며 새 설명과 모든 계약 입력을 보존한다')
            raise SystemExit(0)
        if mode == 'projects':
            alist=f.state()['listingId'];held=f.pending()
            f.page.close();f.stop()
            other=f.case/'other root'/'owned project'
            shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory'))
            f.env['CONFECTORY_WEB_PROJECT']=str(other/'project.cproj')
            f.start(2);f.invoke('select',{'id':owner});f.invoke('saveDraft',{})
            blist=f.state()['listingId'];bcheckpoint=next(other.glob('.confectory/edit-workspaces/*/draft.json'));bsaved=bcheckpoint.read_bytes()
            f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700})
            def enter(listing):
                f.page.locator('.brand').click();expect(f.page.locator('.home-grid')).to_be_visible()
                f.page.locator('[data-enter="'+listing+'"]').click();expect(f.page.locator('.work-body')).to_be_visible();f.idle()
            enter(alist)
            assert pending()[0][1]['mapping']==value['mapping']
            p=popup();p.locator('form').evaluate('el=>globalThis.staleContractForm=el')
            enter(blist);d.open_info()
            assert not pending()
            f.page.evaluate("()=>staleContractForm.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}))")
            assert not pending() and checkpoint.read_bytes()==baseline and bcheckpoint.read_bytes()==bsaved
            enter(alist)
            assert pending()[0][1]['mapping']==value['mapping']
            preserved()
            f.checked('동일 namespace 프로젝트 전환은 A 입력을 보존하고 닫힌 상세창 submit이 B를 바꾸지 못한다')
            raise SystemExit(0)
        if mode == 'loss':
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
            f.page.route('**/api/request',intercept)
            f.owner().locator('[data-element-action=save]').click()
            deadline=time.monotonic()+90
            while time.monotonic()<deadline and not queries&masked:f.page.wait_for_timeout(20)
            assert len(applies)==1 and queries&masked and pending()
            f.page.unroute_all(behavior='wait')
            held=f.pending();mark=len(f.traffic)
            restart(2);assert f.pending()==held
            f.owner().locator('[data-element-action=save]').click()
            wait('blueprint',mark,True,'settledSlots')
            deadline=time.monotonic()+60
            while pending() and time.monotonic()<deadline:f.page.wait_for_timeout(20)
            assert not pending()
            assert not any(row.get('invoke',{}).get('input',{}).get('action')=='applySlots' for row in f.traffic[mark:])
            rows={row['id']:row for row in json.loads(checkpoint.read_text())['changes']}
            x.assert_graphs(rows)
            preserved()
            f.checked('apply와 결과 조회 응답 유실 뒤 cold는 전체 closure receipt만 확인하며 중복 적용하지 않는다')
            raise SystemExit(0)
        if mode == 'retry':
            p=popup();p.locator('[data-signature-id=arg1] [data-signature-type]').click()
            types=f.page.get_by_role('dialog',name='속성 타입 선택',exact=True)
            types.locator('[data-type=string]').click();p.get_by_role('button',name='저장',exact=True).click()
            start=len(f.traffic);f.owner().locator('[data-element-action=save]').click();wait('blueprint',start,False,'applySlots')
            assert pending()[0][1]['signature']['args'][1]['type']=='string' and checkpoint.read_bytes()==baseline
            preserved()
            f.owner().locator('[data-own-functions-toggle]').press('Control+z')
            assert pending()[0][1]['signature']['args'][1]['type']=='long'
            f.checked('호환 불가 타입 저장 거절은 입력을 유지하고 명시적 Undo 뒤 같은 원래 기준으로 재시도한다')
        if mode == 'storage':
            checkpoint.chmod(0o400)
            try:
                start=len(f.traffic);f.owner().locator('[data-element-action=save]').click();wait('blueprint',start,False,'applySlots')
                assert pending()[0][1]['mapping']==value['mapping'] and checkpoint.read_bytes()==baseline
                preserved()
            finally:checkpoint.chmod(0o600)
            f.checked('화면 쓰기 실패는 callee/caller 전체 미적용 및 계약 입력·원문·기존 checkpoint를 보존한다')
        start = len(f.traffic)
        f.owner().locator('[data-element-action=save]').click()
        wait('blueprint', start,True,'applySlots')
        deadline = time.monotonic() + 60
        while pending() and time.monotonic() < deadline:
            f.page.wait_for_timeout(20)
        assert not pending(), f.owner().locator('[data-element-error]').all_text_contents()
        assert n.canonical(next(row for row in schema()['ownFunctions'] if row['id'] == fn)['signature']) == x.signature
        rows = {row['id']: row for row in json.loads(checkpoint.read_text())['changes']}
        x.assert_graphs(rows)
        published=f.metadata('blueprintOutputSnapshot',functionText=rows[fn]['draft'])
        assert [row['name'] for row in published['fields']]==['count2']
        assert published['snapshot']=='read-only-properties; shallow-array-copy-on-return-and-read'
        assert json.loads(rows[fn + 'Body/body:common/node:body']['draft'])['source'] == x.record['source']
        preserved()
        restart(2)
        assert not pending()
        preserved()
        review = d.review()
        review.locator('[data-reject]').click()
        preserved()
        review = d.review()
        if review.locator('[data-review-advanced]').count():
            review.locator('[data-review-advanced]').click()
            if review.locator('[data-advanced-reviewed]').count():
                review.locator('[data-advanced-reviewed]').check()
        start = len(f.traffic)
        review.locator('#confirm').click()
        wait('confirmGroup', start)
        expect(review).to_have_count(0)
        restart(3)
        assert n.canonical(next(row for row in schema()['ownFunctions'] if row['id'] == fn)['signature']) == x.signature
        assert json.loads((f.project / 'function.node.json').read_text())['source'] == x.record['source']
        for path, text in snapshot.items():
            if path not in {'FreeInfo.celem', 'elements/' + fn.split('::')[1] + '.celem', fn.split('::')[1] + 'Body.celem', 'function.graph.json', 'function.node.json', 'caller.graph.json'}:
                assert (f.project / path).read_bytes() == text, path
        f.checked('실제 화면 Save·cold·Review 취소/명시 Confirm은 out 내보내기와 consumer 전체 후보만 반영하고 code/다른 소스를 유지한다')
        f.page.screenshot(path=str(f.case / 'out-contract-ui.png'))
        assert not f.errors and not f.external, (f.errors, f.external)
        f.browser.close()
except Exception:
    try:
        (f.case / 'out-ui-failure.json').write_text(json.dumps({'state': f.state(), 'checks': f.checks, 'traffic': f.traffic[-50:]}, ensure_ascii=False, indent=2))
    except Exception:
        pass
    raise
finally:
    print(json.dumps({'checks': f.checks, 'view': d.is_view, 'evidence': str(f.case), 'actualEngineRenderer': True, 'nativeWindows': False}, ensure_ascii=False))
    f.stop()
