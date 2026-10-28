"""Original whole C# editor + explicit caller storage, real engine and renderer."""
import json
import shutil
import time
from playwright.sync_api import sync_playwright,expect
import v536_information_nested_fixture as x
f,d,owner,fn,mode=x.f,x.d,x.owner,x.fn,x.mode
if mode.startswith('view-'):d.is_view=True
x.edited=x.edited.replace('\r\n','\n');x.edited_records={k:v.replace('\r\n','\n') for k,v in x.edited_records.items()};x.post_source=x.post_source.replace('\r\n','\n');x.post_helpers=x.post_helpers.replace('\r\n','\n');x.code_helpers=x.code_helpers.replace('\r\n','\n')

def pending():return [(k,v) for k,v in d.pending() if v['kind']=='function-edit']
def preserved():
    expect(f.owner().get_by_label('Power 기본값',exact=True)).to_have_value('9223372036854775806')
    assert all((f.project/p).read_bytes()==v for p,v in x.snapshot.items())
    assert not f.page.locator('#app').evaluate('el=>el.inert')
def restart(i):
    held=f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700})
    if d.is_view:f.owner=lambda:f.page.locator('.window[data-key=editor-1]')
    expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo');f.idle();return held
def cpp(body=x.body_id):
    f.owner().locator('[data-inline-method="'+fn+'"] [data-function-edit], [data-inline-method="'+fn+'"] [data-function-write-direct]').click()
    picker=f.page.get_by_role('dialog',name='구현 선택',exact=True);expect(picker).to_be_visible();picker.locator('[data-information-body=\"'+body+'\"]').click()
    dialog=f.page.locator('[role=dialog]:has([data-code-source])');expect(dialog).to_be_visible();return dialog
def define():
    if x.scenario in ['out-value','value-out','out-ref','ref-out'] and not x.chain:return
    f.owner().locator('[data-inline-method="'+fn+'"] > .function-node-heading').dblclick(position={'x':190,'y':3})
    p=f.page.locator('.function-detail-popover');expect(p).to_be_visible()
    def kind(button,type):
        button.click();f.page.get_by_role('dialog',name='속성 타입 선택',exact=True).locator('[data-type='+type+']').click()
    if x.chain:kind(p.locator('[data-signature-id=return] [data-signature-type]'),'bool')
    elif x.scenario=='types':
        p.locator('[data-signature-id=arg0] [data-signature-name]').fill('text')
        kind(p.locator('[data-signature-id=arg0] [data-signature-type]'),'string')
        p.locator('[data-signature-id=arg1] [data-signature-name]').fill('total')
        p.locator('[data-signature-add=inputs]').click()
        added=p.locator('[data-signature-kind=inputs] .feature-io-row').last;added.locator('[data-signature-name]').fill('increment');kind(added.locator('[data-signature-type]'),'long')
        kind(p.locator('[data-signature-id=return] [data-signature-type]'),'bool')
    elif x.scenario=='void':p.locator('[data-signature-id=return] [data-signature-remove]').click()
    else:
        p.locator('[data-signature-add=outputs]').click();kind(p.locator('[data-signature-id=return] [data-signature-type]'),'long')
    p.get_by_role('button',name='저장',exact=True).click()
    m=f.page.get_by_role('dialog',name='호출 계약 갱신',exact=True);expect(m).to_be_visible();m.get_by_role('button',name='취소',exact=True).click();f.idle()

def fill(dialog,partial=False):
    field=dialog.locator('[data-code-source]');field.evaluate("el=>{el.focus();el.setSelectionRange(el.value.indexOf('(')+1,el.value.indexOf(')'));}")
    parameters=', '.join((a.get('mode','')+' ' if a.get('mode') else '')+a['type']+' '+a['name'] for a in x.selected['args'])
    f.page.keyboard.insert_text(parameters)
    field.evaluate(r"el=>{el.focus();el.setSelectionRange(el.value.indexOf('\n{\n')+3,el.value.lastIndexOf('\n}'));}")
    f.page.keyboard.insert_text(x.edited+('native' if partial else ''));f.idle()
def choose():
    m=f.page.get_by_role('dialog',name='호출 계약 갱신',exact=True);expect(m).to_be_visible()
    for section in m.locator('[data-abi-target]').all():
        key=section.get_attribute('data-abi-target');path='left' if '#left/' in key else 'right'
        section.locator('[data-abi-input=text]').select_option('value');section.locator('[data-abi-value=text]').fill('왼쪽' if path=='left' else '오른쪽');section.locator('[data-abi-input=increment]').select_option('pin:amount')
        for field in section.locator('[data-abi-output]').all():field.select_option('total')
    m.locator('[data-abi-remap-accept]').click();expect(m).to_have_count(0);f.idle()
    for name in ['left','right']:
        if x.cpp:scoped_code(name)
    if x.post_mode:
        for path in ['left','right/deep']:post_code(path)
def replace_body(dialog,text):
    field=dialog.locator('[data-code-source]');field.evaluate(r"el=>{const p=el.value.indexOf(' Invoke('),a=el.value.indexOf('\n{\n',p)+3,b=el.value.indexOf('\n}\n',a);el.focus();el.setSelectionRange(a,b);}");f.page.keyboard.insert_text(text);f.idle()
def scoped_code(name):
    id=x.record_ids[name];text=x.edited_records[name];dialog=cpp(id);assert ('public '+('Result' if x.code_control=='switch' else x.code_native['return'])+' Invoke('+('ref ' if x.forward else '')+'long item)') in dialog.locator('[data-code-source]').input_value();replace_body(dialog,text);dialog.locator('[data-code-cancel]').click();assert id not in pending()[0][1]['mapping']['bodies']
    dialog=cpp(id);replace_body(dialog,text+'partial');held=restart(6 if name=='left' else 7);assert f.pending()==held;dialog=cpp(id);assert text+'partial' in dialog.locator('[data-code-source]').input_value();replace_body(dialog,text);
    if x.code_control:
        field=dialog.locator('[data-code-source]');field.evaluate(r"el=>{const p=el.value.indexOf(' Invoke('),a=el.value.indexOf('\n{\n',p)+3,b=el.value.indexOf('\n}\n',a)+3;el.focus();el.setSelectionRange(b,el.value.length);}");f.page.keyboard.insert_text(x.code_helpers)
    f.page.screenshot(path=str(f.case/(name+'-scoped-code.png')));dialog.locator('[data-code-save]').click();f.idle();assert pending()[0][1]['mapping']['bodies'][id]['text']==text
def post_code(path):
    id=x.caller_id+'/postCall:'+path+'/'+x.leaf_id;dialog=cpp(id);field=dialog.locator('[data-code-source]');assert '@total' in field.input_value()
    field.evaluate("el=>{const p=el.value.indexOf(' After('),a=el.value.indexOf('\\n{\\n',p)+3,b=el.value.indexOf('\\n}\\n',a);el.focus();el.setSelectionRange(a,b);}");f.page.keyboard.insert_text(x.post_source)
    field.evaluate("el=>{const p=el.value.indexOf(' After('),a=el.value.indexOf('\\n{\\n',p)+3,b=el.value.indexOf('\\n}\\n',a)+3,c=el.value.lastIndexOf('\\n}\\n');el.focus();el.setSelectionRange(b,c);}");f.page.keyboard.insert_text(x.post_helpers);dialog.locator('[data-code-save]').click();f.idle();assert pending()[0][1]['mapping']['bodies'][id]['helpers']==x.post_helpers

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
        expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});d.open_info();define()
        initial=pending()
        dialog=cpp();fill(dialog);assert pending()[0][1]['bodyDrafts'][x.body_id]['parameters']
        dialog.locator('[data-code-cancel]').click();assert pending()==initial;preserved()
        dialog=cpp();fill(dialog,True);held=restart(1);assert f.pending()==held
        dialog=cpp()
        text=dialog.locator('[data-code-source]').input_value();assert x.edited+'native' in text and x.selected['args'][0]['name'] in text
        fill(dialog);f.page.screenshot(path=str(f.case/'whole-body-code.png'));dialog.locator('[data-code-save]').click();choose()
        value=pending()[0][1];assert value['signature']==x.new and value['mapping']['bodies'][x.body_id]['signature']==x.selected and value['mapping']['bodies'][x.body_id]['text']==x.edited
        f.owner().locator('[data-own-functions-toggle]').press('Control+z');f.owner().locator('[data-own-functions-toggle]').press('Control+y');assert pending()[0][1]==value
        held=restart(2);assert f.pending()==held and pending()[0][1]==value;preserved()
        f.checked('원본 전체 본문 편집창의 본문·형식 매개변수/입출력은 취소·불완전 cold·코드 저장·명시 caller 선택·Undo/Redo에서 보존된다')
        if mode.endswith('projects'):
            alist=f.state()['listingId'];held=f.pending();f.page.close();f.stop()
            other=f.case/'other root'/'owned project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory'))
            f.env['CONFECTORY_WEB_PROJECT']=str(other/'project.cproj');f.start(5);f.invoke('select',{'id':owner});f.invoke('saveDraft',{})
            blist=f.state()['listingId'];other_checkpoint=next(other.glob('.confectory/edit-workspaces/*/draft.json'));other_baseline=other_checkpoint.read_bytes()
            f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700})
            def enter(listing):
                f.page.locator('.brand').click();expect(f.page.locator('.home-grid')).to_be_visible();f.page.locator('[data-enter="'+listing+'"]').click();expect(f.page.locator('.work-body')).to_be_visible();f.idle()
            enter(alist);assert pending()[0][1]==value
            dialog=cpp();dialog.locator('[data-code-save]').evaluate('el=>globalThis.staleWholeSave=el');dialog.locator('[data-code-cancel]').click()
            enter(blist);d.open_info();assert not pending();f.page.evaluate('()=>staleWholeSave.click()')
            assert not pending() and checkpoint.read_bytes()==baseline and other_checkpoint.read_bytes()==other_baseline
            enter(alist);assert pending()[0][1]==value;preserved()
            f.checked('동일 namespace 두 프로젝트는 전체 본문/입출력 입력을 분리하고 닫힌 편집창 저장을 차단한다')
        elif mode.endswith('conflict'):
            s=f.state()['schema'];f.invoke('editDescription',{'id':owner,'hash':s['textHash'],'revision':s['revision'],'value':'다른 편집자 입력 보존'})
            f.rejected_save();assert pending()[0][1]==value and checkpoint.read_bytes()==baseline;preserved()
            f.checked('동시 source 변경은 본문·저장소·호출자 전체를 거절하고 새 입력과 다른 편집자를 보존한다')
        elif mode.endswith('cancel'):
            f.owner().locator('[data-element-action=discard]').click();f.idle();assert not pending() and checkpoint.read_bytes()==baseline;preserved();restart(3);assert not pending()
            f.checked('변경 취소는 본문·native 입출력·호출자와 cold 기록을 함께 미적용으로 유지한다')
        else:
            if mode.endswith('simple'):
                mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();wait('blueprint',mark,True,'applySlots')
            else:
                checkpoint.chmod(0o400)
                try:
                    mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();wait('blueprint',mark,False,'applySlots');assert pending()[0][1]==value and checkpoint.read_bytes()==baseline;preserved()
                finally:checkpoint.chmod(0o600)
                f.checked('화면 저장 장치 오류는 source·호출자·checkpoint 부분 적용 없이 명시 입력을 보존한다')
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
                f.page.route('**/api/request',intercept);f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+90
                while time.monotonic()<deadline and not queries&masked:f.page.wait_for_timeout(20)
                assert len(applies)==1 and queries&masked and pending()
                f.page.unroute_all(behavior='wait');held=restart(3);assert f.pending()==held
                mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();wait('blueprint',mark,True,'settledSlots')
                assert not any(r.get('invoke',{}).get('input',{}).get('action')=='applySlots' for r in f.traffic[mark:])
            deadline=time.monotonic()+60
            while pending() and time.monotonic()<deadline:f.page.wait_for_timeout(20)
            assert not pending();x.verify(checkpoint);preserved();restart(4);x.verify(checkpoint)
            f.checked('화면 정상 저장·cold는 전체 후보와 C# 원문·호출자를 정확히 복원한다' if mode.endswith('simple') else '응답과 receipt 유실 뒤 cold/재시도는 결과 조회로 전체 저장을 확인하며 중복 적용하지 않는다')
            review=d.review();review.locator('[data-reject]').click();preserved();review=d.review()
            if review.locator('[data-review-advanced]').count():
                review.locator('[data-review-advanced]').click()
                if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
            mark=len(f.traffic);review.locator('#confirm').click();wait('confirmGroup',mark);expect(review).to_have_count(0)
            assert json.loads((f.project/x.body_path).read_text())['source']==x.edited
            f.checked('실제 화면 compiler Review 취소·재검토·명시 Confirm은 입출력 저장소와 C# 원문을 함께 반영한다')
        assert not f.errors and not f.external,(f.errors,f.external)
        f.page.screenshot(path=str(f.case/'whole-final.png'));f.browser.close()
except Exception:
    try:(f.case/'failure.json').write_text(json.dumps({'checks':f.checks,'traffic':f.traffic[-50:],'state':f.state()},ensure_ascii=False,indent=2))
    except Exception:pass
    raise
finally:
    f.stop();print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'scenario':x.scenario,'chain':x.chain,'mode':mode,'nested':True,'independent':d.is_view,'forward':x.forward,'cpp':x.cpp,'postMode':x.post_mode,'nativeWindows':False,'deviceTouch':False},ensure_ascii=False))
