"""Original local-image header flow, synthetic files and isolated engine only."""
import ast, base64, io, json, pathlib, re, sys, time, zipfile
from PIL import Image
from playwright.sync_api import sync_playwright, expect
import v536_wide_mixed as f

mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
detached='view' in sys.argv[4:];with_peer='peer' in sys.argv[4:]
owner=f.n+'Details';leaf='Details';kind='schema';is_function=is_property=is_new=False;new_label=''
file=f.project/'Details.celem'
file.write_text(file.read_text().replace('{','{ // keep owner source\nvalue editorIcon="📦";value editorInformationDefaults="typed-json-v1";value editorFieldDefault_Power="9223372036854775805";',1))
f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file()}
helper=pathlib.Path(__file__).with_name('v536_element_icon_ui.py')
names={'surface','pending','own_schema','open_card','icon','popup','saved','restart','review','compare'}
functions=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef) and n.name in names]
assert len(functions)==len(names)
exec(compile(ast.Module(body=functions,type_ignores=[]),str(helper),'exec'))
f.owner=surface

def raster(fmt,color=(40,90,150,130)):
    output=io.BytesIO();image=Image.new('RGBA',(32,16),color)
    if fmt=='JPEG':image=image.convert('RGB')
    image.save(output,format=fmt);return output.getvalue()
def upload(p,fmt='PNG',color=(40,90,150,130)):
    p.locator('[type=file]').set_input_files(dict(name='synthetic-icon.'+fmt.lower(),mimeType={'PNG':'image/png','JPEG':'image/jpeg','WEBP':'image/webp'}[fmt],buffer=raster(fmt,color)))
    image=p.locator('.object-icon-preview img');expect(image).to_be_visible();expect(p.locator('[type=submit]')).to_be_enabled()
    assert image.evaluate('e=>e.naturalWidth===128&&e.naturalHeight===128&&e.complete')
    uri=image.get_attribute('src');assert uri.startswith('data:image/webp;base64,');return uri
def rendered(uri):
    image=icon().locator('img');expect(image).to_have_attribute('src',uri);assert image.evaluate('e=>e.complete&&e.naturalWidth===128&&e.naturalHeight===128')
def save(ok=True):
    surface().locator('[data-element-action=save]').click()
    if ok:saved()
    else:expect(surface().locator('[data-element-error]')).not_to_have_text('',timeout=60000);f.idle();assert pending()

try:
    f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
    with sync_playwright() as pw:
        expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup()
        if with_peer:open_card(f.n+'Target1',False);f.page.locator('.window[data-key=schema]').get_by_label('Power 기본값',exact=True).fill('9223372036854775804')
        open_card();baseline=pending();p=popup();compare(p);expect(p.locator('.object-icon-upload')).to_be_enabled();uri=upload(p);p.locator('[data-cancel]').click();assert pending()==baseline;expect(icon()).to_have_text('📦')
        p=popup()
        for name,mime,data in [('bad.svg','image/svg+xml',b'<svg/>'),('large.png','image/png',b'x'*5_000_001),('broken.png','image/png',b'not a PNG')]:
            p.locator('[type=file]').set_input_files(dict(name=name,mimeType=mime,buffer=data));expect(p.locator('.icon-upload-error')).not_to_have_text('');expect(p.locator('[type=submit]')).to_be_enabled();assert pending()==baseline
        p.get_by_label('기호나 이모지',exact=True).press('Escape');assert pending()==baseline;f.originals();f.checked('원본 팝오버/취소/Escape·종류/5MB/읽기 오류는 원본과 입력을 보존하며 파일을 업로드하지 않는다')

        f.page.evaluate('()=>{window.originalDecode=Image.prototype.decode;Image.prototype.decode=function(){return new Promise(resolve=>{window.finishIconDecode=()=>window.originalDecode.call(this).then(resolve);});};}')
        p=popup();p.locator('[type=file]').set_input_files(dict(name='slow.png',mimeType='image/png',buffer=raster('PNG')));expect(p.locator('[type=submit]')).to_be_disabled();p.locator('[data-icon-choice="★"]').click();p.get_by_role('button',name='적용',exact=True).click();f.page.evaluate('()=>{Image.prototype.decode=window.originalDecode;window.finishIconDecode();}');f.idle();expect(icon()).to_have_text('★');assert next(v for _,v in pending() if v['kind']=='icon')['text']=='★'
        surface().locator('.object-icon-edit').press('Control+z');expect(icon()).to_have_text('📦');assert pending()==baseline;f.checked('늦은 로컬 decode는 새 기호 선택을 덮어쓰지 않으며 헤더 Undo는 원래 입력만 복원한다')

        for fmt in ['PNG','JPEG','WEBP']:
            p=popup();uri=upload(p,fmt);p.get_by_role('button',name='적용',exact=True).click();rendered(uri);assert next(v for _,v in pending() if v['kind']=='icon')['text']==uri
            surface().locator('.object-icon-edit').press('Control+z');expect(icon()).to_have_text('📦');assert pending()==baseline
            surface().locator('.object-icon-edit').press('Control+y');rendered(uri)
            if fmt!='WEBP':surface().locator('.object-icon-edit').press('Control+z');assert pending()==baseline
        p=popup();expect(p.get_by_label('기호나 이모지',exact=True)).to_have_value('');expect(p.locator('.object-icon-preview img')).to_have_attribute('src',uri);p.locator('[data-cancel]').click();surface().locator('.object-title-description').fill('로컬 이미지와 설명 원자 저장');held=pending();assert len(held)==2;assert checkpoint.read_bytes()==before;f.originals();restart(1);assert pending()==held;rendered(uri);f.checked('PNG/JPG/WebP 선택은 원본처럼 128px WebP로만 보관하고 Undo/Redo·설명·cold에 정확한 값과 부모/본문을 보존한다')

        if mode=='cancel':
            surface().locator('[data-element-action=discard]').click();saved();restart(2);assert not pending() and checkpoint.read_bytes()==before;expect(icon()).to_have_text('📦');f.originals();f.checked('명시적 취소/cold는 이미지·설명 초안만 취소하며 프로젝트 자산 파일이나 원본을 생성/삭제하지 않는다')
        elif mode=='conflict':
            raw=file.read_bytes()+b'\n// fixture source race\n';file.write_bytes(raw);f.original[file.name]=raw;save(False);assert pending()==held and checkpoint.read_bytes()==before;f.originals();restart(2);save(False);assert pending()==held and checkpoint.read_bytes()==before;f.originals();f.checked('실제 소유 source 충돌은 이미지/설명 전부 미적용이며 cold 재시도에도 원래 기준·입력을 유지한다')
        else:
            if mode=='storage':
                checkpoint.chmod(0o400)
                try:save(False);assert pending()==held and checkpoint.read_bytes()==before;f.originals()
                finally:checkpoint.chmod(0o600)
                restart(2);assert pending()==held;f.checked('checkpoint 저장 실패는 이미지/설명 부분 적용 없이 원본과 입력을 cold까지 보존한다')
            if mode=='loss':
                applies=set();queries=set();lost=[]
                def intercept(route):
                    body=route.request.post_data_json
                    if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
                        action=body.get('input',{}).get('action')
                        if action=='applySlots':applies.add(body['requestId'])
                        elif applies and action=='settledSlots':queries.add(body['requestId'])
                    response=route.fetch();payload=response.json()
                    for value in payload.get('results',[]):
                        if value['requestId'] in applies|queries:rid=value['requestId'];lost.append(rid);value.clear();value.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
                    route.fulfill(response=response,json=payload)
                f.page.route('**/api/request',intercept);surface().locator('[data-element-action=save]').click()
                for _ in range(600):
                    if applies and any(v in queries for v in lost):break
                    f.page.wait_for_timeout(50)
                assert len(applies)==1 and any(v in queries for v in lost) and pending()==held;f.page.unroute_all(behavior='wait');mark=len(f.traffic);restart(2);save();assert not any(v.get('invoke',{}).get('input',{}).get('action')=='applySlots' for v in f.traffic[mark:]);f.checked('적용·조회 응답 유실은 cold 뒤 기존 receipt 조회로 회수하며 이미지를 중복 적용하지 않는다')
            elif mode=='late':
                ids=set();paused={}
                def hold(route):
                    body=route.request.post_data_json
                    if body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and body.get('input',{}).get('action')=='applySlots':ids.add(body['requestId'])
                    response=route.fetch();payload=response.json()
                    if not paused and any(v.get('ok') and v.get('requestId') in ids for v in payload.get('results',[])):paused.update(route=route,response=response);return
                    route.fulfill(response=response)
                f.page.route('**/api/request',hold);surface().locator('[data-element-action=save]').click()
                for _ in range(600):
                    if paused:break
                    f.page.wait_for_timeout(50)
                assert paused and len(ids)==1;p=popup();late_uri=upload(p,'PNG',(160,30,90,255));assert late_uri!=uri;p.get_by_role('button',name='적용',exact=True).click();paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',hold);f.idle()
                for _ in range(600):
                    if len(pending())==1 and pending()[0][1].get('copySavedBasis'):break
                    f.page.wait_for_timeout(50)
                assert pending()[0][1]['text']==late_uri and pending()[0][1]['copySavedBasis']['accepted']==uri;uri=late_uri;restart(2);rendered(uri);save();f.checked('저장 응답 대기의 새 이미지는 receipt 기준의 별도 입력으로 보존되고 cold 뒤 명시적 Save만 반영한다')
            else:save()
            assert own_schema()['values']['editorIcon']==uri and next(v for v in own_schema()['rows'] if v['path']==['Power'])['valueJson']=='9223372036854775805';f.originals();restart(3);assert not pending();rendered(uri);f.checked('한 후보/최종 CAS Save와 cold는 이미지·설명을 함께 저장하고 실제 source·정확64비트·본문·권한을 보존한다')
            if with_peer:
                surface().locator('[data-element-action=confirm]').click();group=f.page.get_by_role('dialog',name='관련 변경 검토',exact=True);expect(group).to_be_visible();group.locator('#review-creation').click();f.idle();expect(f.page.locator('#status')).to_contain_text('미적용 입력');assert any('|'+f.n+'Target1|' in k and v.get('text')=='9223372036854775804' for k,v in f.pending()['schema']);f.originals();group.get_by_role('button',name='닫기',exact=True).click();peer=f.page.locator('.window[data-key=schema]');peer.locator(':scope>.window-title').click(position={'x':30,'y':25});peer.locator('[data-element-action=discard]').click();f.idle();f.checked('독립 이미지 창의 Save/cold/Review 거절은 다른 창 문서와 정확64비트 입력을 보존한다')
            r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();f.originals();r=review()
            if r.locator('[data-review-advanced]').count():
                r.locator('[data-review-advanced]').click()
                if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
            r.locator('#confirm').click();expect(r).to_have_count(0,timeout=120000);f.idle();assert {k for k,v in f.original.items() if (f.project/k).read_bytes()!=v}=={file.name};assert 'keep owner source' in file.read_text() and '9223372036854775805' in file.read_text();assert not [p for p in f.project.rglob('*') if p.is_file() and p.suffix.lower() in ['.png','.jpg','.webp']];f.checked('명시적 compiler Confirm만 선택 정보의 inline 이미지/설명을 반영하며 다른 source/등록/부모와 개인 파일은 건드리지 않는다')
            if with_peer:expect(f.page.locator('.window[data-key=schema] .object-title-name')).to_have_text('Target1')
        assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except Exception:
    try:(f.case/'image-failure.json').write_text(json.dumps(dict(state=f.state(),traffic=f.traffic[-80:],errors=f.errors),ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'image-failure.png'))
    except Exception:pass
    print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps(dict(checks=f.checks,evidence=str(f.case),detached=detached,peer=with_peer,actualEngine=True,renderer=True,localSyntheticFiles=True,uploaded=False,nativeWindows=False,actualMobile=False)))
