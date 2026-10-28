"""Original property/function card images, isolated engine/renderer and synthetic files."""
import ast,io,json,pathlib,re,sys,time,zipfile
from PIL import Image
from playwright.sync_api import sync_playwright,expect

new_function='new-function' in sys.argv[5:]
helper=pathlib.Path(__file__).with_name('v536_new_function_icon_ui.py' if new_function else 'v536_element_icon_ui.py')
tree=ast.parse(helper.read_text());prefix=tree.body[:next(i for i,node in enumerate(tree.body) if isinstance(node,ast.Try))]
exec(compile(ast.Module(body=prefix,type_ignores=[]),str(helper),'exec'))
if new_function:
    function_row=row
    own_schema=schema
else:
    # Keep the fixture's declaration, inherited field and typed caller intact.
    if kind=='schema':
        file.write_text(file.read_text().replace('{','{value editorInformationDefaults="typed-json-v1";value editorFieldDefault_Power="9223372036854775805";',1))
    file.write_text(file.read_text().replace('{','{ // preserve card image owner\n',1))
    f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file()}


def image_bytes(fmt,color=(40,90,150,130)):
    b=io.BytesIO();im=Image.new('RGBA',(32,16),color)
    if fmt=='JPEG':im=im.convert('RGB')
    im.save(b,format=fmt);return b.getvalue()
def upload(p,fmt='PNG',color=(40,90,150,130)):
    p.locator('[type=file]').set_input_files(dict(name='synthetic-card.'+fmt.lower(),mimeType={'PNG':'image/png','JPEG':'image/jpeg','WEBP':'image/webp'}[fmt],buffer=image_bytes(fmt,color)))
    im=p.locator('.object-icon-preview img');expect(im).to_be_visible();expect(p.locator('[type=submit]')).to_be_enabled()
    assert im.evaluate('e=>e.complete&&e.naturalWidth===128&&e.naturalHeight===128')
    uri=im.get_attribute('src');assert uri.startswith('data:image/webp;base64,');return uri
def rendered(uri):
    im=icon().locator('img');expect(im).to_have_attribute('src',uri);assert im.evaluate('e=>e.complete&&e.naturalWidth===128&&e.naturalHeight===128')
def input_icon():
    for _,value in pending():
        if is_function and value['kind'] in ['function-add','function-edit']:return value.get('icon','')
        if is_new and value['kind']=='definition':return value.get('icon','')
        if is_property and value['kind']=='schema-icon':return value['text']
    return ''

def keypress(key):icon().focus();f.page.keyboard.press('Control+'+key)
def save(ok=True):
    surface().locator('[data-element-action=save]').click()
    if ok:saved()
    else:expect(surface().locator('[data-element-error]')).not_to_have_text('',timeout=60000);f.idle();assert pending()
def check_stored(uri):
    s=own_schema()
    if is_function:
        method=next(v for v in s['ownFunctions'] if v['id']==function_id);assert method['icon']==uri and method['name']==function_name
    else:
        property=next(v for v in s['rows'] if v['path']==[new_native if is_new else 'Power']);assert property['icon']==uri
        assert property['valueJson']==('9223372036854775804' if is_object_property else '9223372036854775805')
def confirmed():
    if new_function:
        changed={k for k,v in f.original.items() if (f.project/k).read_bytes()!=v};assert changed=={file.name,f.manifest.name},changed
        assert function_file.is_file() and len(list((f.project/'elements').glob('Details_Function_*.celem')))==1
    else:assert_confirmed_sources()
    assert not [p for p in f.project.rglob('*') if p.is_file() and p.suffix.lower() in ['.png','.jpg','.webp']]

try:
    f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
    with sync_playwright() as pw:
        expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup()
        if with_peer:open_card(f.n+'Target1',False);f.page.locator('.window[data-key=schema]').get_by_label('Power 기본값',exact=True).fill('9223372036854775804')
        open_card()
        if new_function:
            surface().locator('[data-function-add]').click();created=next(v for _,v in pending() if v['kind']=='function-add');function_id=created['id'];function_file=f.project/'elements'/(function_id.split('::')[-1]+'.celem');row().locator('[data-inline-name]').fill(function_name);row().locator('[data-inline-description]').fill('생성 함수 설명')
        elif is_new:
            surface().locator('[data-schema-add]').click();draft=surface().locator('[data-definition-key]').last;new_draft_key=draft.get_attribute('data-definition-key');new_native=next(v.get('nativeKey',new_label) for _,v in pending() if v['kind']=='definition');draft.locator('[data-property-name]').fill(new_label);draft.locator('[data-property-type]').click();f.page.get_by_role('dialog',name='속성 타입 선택',exact=True).locator('[data-type=long]').click();new_row().get_by_label(new_label+' 기본값',exact=True).fill('9223372036854775804' if is_object_property else '9223372036854775805')
        baseline=pending();default=icon().inner_text();p=popup();compare(p);expect(p.locator('.object-icon-upload')).to_be_enabled();uri=upload(p);p.locator('[data-cancel]').click();assert pending()==baseline;expect(icon()).to_have_text(default)
        p=popup()
        for name,mime,data in [('bad.svg','image/svg+xml',b'<svg/>'),('large.png','image/png',b'x'*5_000_001),('bad.webp','image/webp',b'broken')]:
            p.locator('[type=file]').set_input_files(dict(name=name,mimeType=mime,buffer=data));expect(p.locator('.icon-upload-error')).not_to_have_text('');assert pending()==baseline
        p.get_by_label('기호나 이모지',exact=True).press('Escape');assert pending()==baseline;f.originals();f.checked('원본 팝오버·취소/Escape·종류/5MB/읽기 오류는 선택 카드·다른 입력·원문을 보존한다')
        f.page.evaluate('()=>{window.originalDecode=Image.prototype.decode;Image.prototype.decode=function(){return new Promise(resolve=>{window.finishIconDecode=()=>window.originalDecode.call(this).then(resolve);});};}')
        p=popup();p.locator('[type=file]').set_input_files(dict(name='slow.png',mimeType='image/png',buffer=image_bytes('PNG')));expect(p.locator('[type=submit]')).to_be_disabled();p.locator('[data-icon-choice="★"]').click();p.get_by_role('button',name='적용',exact=True).click();f.page.evaluate('()=>{Image.prototype.decode=window.originalDecode;window.finishIconDecode();}');f.idle();expect(icon()).to_have_text('★');assert input_icon()=='★';keypress('z');expect(icon()).to_have_text(default);assert pending()==baseline
        for fmt in ['PNG','JPEG','WEBP']:
            p=popup();uri=upload(p,fmt);p.get_by_role('button',name='적용',exact=True).click();rendered(uri);assert input_icon()==uri;keypress('z');expect(icon()).to_have_text(default);assert pending()==baseline;keypress('y');rendered(uri)
            if fmt!='WEBP':keypress('z');assert pending()==baseline
        if is_property:
            p=popup();p.get_by_role('button',name='아이콘 없음',exact=True).click();assert input_icon()=='' if is_new else not any(v['kind']=='schema-icon' and v.get('text') for _,v in pending());keypress('z');rendered(uri)
            assert surface().locator('[data-property-id="Inherited"] [data-property-icon]').count()==0
        p=popup();expect(p.get_by_label('기호나 이모지',exact=True)).to_have_value('');expect(p.locator('.object-icon-preview img')).to_have_attribute('src',uri);p.locator('[data-cancel]').click();surface().locator('.object-title-description').fill('카드 이미지와 설명 원자 저장');held=pending();assert len(held)==2;assert checkpoint.read_bytes()==before;f.originals();restart(1);assert pending()==held;rendered(uri);f.checked('PNG/JPG/WebP·해제·Undo/Redo·늦은 decode·설명·cold는 같은 속성/함수 ID와 정확한 값·참조·부모를 보존한다')
        if mode=='cancel':
            surface().locator('[data-element-action=discard]').click();saved();restart(2);assert not pending() and checkpoint.read_bytes()==before;f.originals();f.checked('명시적 변경 취소와 재시작은 새 생성/이미지/설명만 취소하며 원본과 기존 참조를 지키고 파일을 만들지 않는다')
        elif mode=='conflict':
            target=function_file if is_function and not new_function else icon_file if not new_function else file
            raw=target.read_bytes()+b'\n// fixture card source race\n';target.write_bytes(raw);f.original[str(target.relative_to(f.project))]=raw;save(False);assert pending()==held and checkpoint.read_bytes()==before;f.originals();restart(2);save(False);assert pending()==held and checkpoint.read_bytes()==before;f.originals();f.checked('실제 카드 정의/함수 source 충돌은 설명/이미지 전부 미적용·원래 입력/기준 보존이며 cold에도 자동 재기준하지 않는다')
        else:
            if mode=='storage':
                checkpoint.chmod(0o400)
                try:save(False);assert pending()==held and checkpoint.read_bytes()==before;f.originals()
                finally:checkpoint.chmod(0o600)
                restart(2);assert pending()==held;f.checked('checkpoint 저장 실패는 카드 이미지/설명을 부분 적용하지 않고 입력과 원문을 cold까지 보존한다')
            if mode=='loss':
                applies=set();queries=set();lost=[]
                def interrupt(route):
                    body=route.request.post_data_json
                    if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
                        action=body.get('input',{}).get('action')
                        if action=='applySlots':applies.add(body['requestId'])
                        elif applies and action=='settledSlots':queries.add(body['requestId'])
                    response=route.fetch();payload=response.json()
                    for value in payload.get('results',[]):
                        if value['requestId'] in applies|queries:rid=value['requestId'];lost.append(rid);value.clear();value.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
                    route.fulfill(response=response,json=payload)
                f.page.route('**/api/request',interrupt);surface().locator('[data-element-action=save]').click()
                for _ in range(600):
                    if applies and any(r in queries for r in lost):break
                    f.page.wait_for_timeout(50)
                assert len(applies)==1 and any(r in queries for r in lost) and pending()==held;f.page.unroute_all(behavior='wait');mark=len(f.traffic);restart(2);save();assert not any(v.get('invoke',{}).get('input',{}).get('action')=='applySlots' for v in f.traffic[mark:]);f.checked('적용/조회 응답 유실은 cold 뒤 기존 receipt 조회로 회수하며 함수·속성·이미지를 중복 생성/적용하지 않는다')
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
                assert len(pending())==1 and input_icon()==late_uri and pending()[0][1]['copySavedBasis'];uri=late_uri;restart(2);rendered(uri);save();f.checked('저장 중 새 카드 이미지는 정확한 수락 receipt와 별도 입력으로 남고 cold 뒤 새 명시적 Save만 반영한다')
            else:save()
            check_stored(uri);f.originals();restart(3);assert not pending();rendered(uri);f.checked('한 후보/최종 CAS Save와 재시작은 이미지·값/함수 계약·설명을 함께 보존하고 실제 source는 Confirm 전 그대로다')
            if with_peer:
                surface().locator('[data-element-action=confirm]').click();group=f.page.get_by_role('dialog',name='관련 변경 검토',exact=True);expect(group).to_be_visible();group.locator('#review-creation').click();f.idle();expect(f.page.locator('#status')).to_contain_text('미적용 입력');assert any('|'+f.n+'Target1|' in k and v.get('text')=='9223372036854775804' for k,v in f.pending()['schema']);f.originals();group.get_by_role('button',name='닫기',exact=True).click();peer=f.page.locator('.window[data-key=schema]');peer.locator(':scope>.window-title').click(position={'x':30,'y':25});peer.locator('[data-element-action=discard]').click();f.idle();f.checked('독립 카드 창의 Save/Review 거절은 다른 창·문서의 정확64비트 입력과 원본을 보존한다')
            r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();f.originals();r=review()
            for cb in r.locator('[data-review-id]').all():cb.check()
            if r.locator('[data-review-advanced]').count():
                r.locator('[data-review-advanced]').click()
                if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
            r.locator('#confirm').click();expect(r).to_have_count(0,timeout=120000);f.idle();confirmed();f.checked('명시적 compiler Confirm만 선택 카드의 소유 정의/함수·필요한 새 등록을 반영하고 부모·외부·본문·다른 source를 보존한다')
        assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except Exception:
    try:(f.case/'card-image-failure.json').write_text(json.dumps(dict(state=f.state(),traffic=f.traffic[-80:],errors=f.errors),ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'card-image-failure.png'))
    except Exception:pass
    print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps(dict(checks=f.checks,evidence=str(f.case),newFunction=new_function,property=is_property,detached=detached,peer=with_peer,actualEngine=True,renderer=True,syntheticFiles=True,uploaded=False,actualWindows=False,actualMobile=False),ensure_ascii=False))
