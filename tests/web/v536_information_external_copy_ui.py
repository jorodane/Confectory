"""Existing module slot: edit a local copy of a registered function, not its ABI."""
import json
import sys
import time
import shutil
from playwright.sync_api import sync_playwright, expect
import v536_field_definitions_ui as d

f, owner = d.f, d.owner
mode = sys.argv[3]
foreign = 'Source.Module::'
fn = foreign + 'Feature'
target = 'windows' if 'windows' in sys.argv[4:] else 'common'
confirmed = 'confirmed' in sys.argv[4:]
source = f.case / 'registered module source'
source.mkdir()
(source / 'pack.cpack').write_text('pack Source.Module version "1" {element Rules module "Rules.celem";element Feature function "Feature.celem";element Body implementation "Body.celem";}')
(source / 'Rules.celem').write_text('module ' + foreign + 'Rules {require ' + fn + ' (long,out long,out bool) -> long;default ' + fn + ' with ' + foreign + 'Body;}')
(source / 'Feature.celem').write_text('function ' + fn + ' (long amount,out long slotCount,out bool slotReady) -> long {description "등록된 기능";provide ' + fn + ' with ' + foreign + 'Body;}')
(source / 'Body.celem').write_text('implementation ' + foreign + 'Body for ' + fn + ' (long amount,out long slotCount,out bool slotReady) -> long {body common "Body.csbody";body windows "Windows.csbody";}')
original_body = 'slotCount=amount+12;slotReady=true;return amount+13; // 원문 · 9223372036854775806\r\n'
(source / 'Body.csbody').write_bytes(original_body.encode())
(source / 'Windows.csbody').write_bytes(original_body.replace('+12', '+100').replace('+13', '+200').encode())
if target == 'windows':
    original_body = (source / 'Windows.csbody').read_bytes().decode()
info = f.project / 'FreeInfo.celem'
info.write_text(info.read_text().replace('FreeInfo {', 'FreeInfo {module ' + foreign + 'Rules;', 1))
f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet', 'registry Source.Module "../registered module source/pack.cpack";dependency Source.Module version "1";registry Confectory.Build.DotNet', 1))
nested_source='nested-source' in sys.argv[4:]
nested_values='nested-values' in sys.argv[4:]
nested_pins='nested-pins' in sys.argv[4:]
branch_source=next((v.removesuffix('-source') for v in sys.argv[4:] if v in ['branch-source','switch-source']),None)
if 'blueprint-source' in sys.argv[4:] or branch_source or nested_source:
    feature_text = (source / 'Feature.celem').read_text()
    prepared = f.metadata('blueprintPrepareFeature', id=fn, text=feature_text.replace('provide ' + fn + ' with ' + foreign + 'Body;', ''), implementation=foreign + 'Body', graphPath='Body.graph.json', nodePath='Body.node.json')
    if branch_source:
        graph=prepared['graph'];graph['profile']='sync-acyclic-switch-v1'
        decision={'id':'decision','kind':'code','control':branch_source,'intent':'기존 분기 원문 보존','signature':{'args':[{'name':'amount','type':'long'}],'return':'bool' if branch_source=='branch' else 'void'},'arguments':{'amount':{'input':'amount'}},'implementation':'Decision.node.json'}
        if branch_source=='switch':decision['executionEnum']={'primary':'next','members':[{'id':'next','name':'NoBranch','value':0},{'id':'positive','name':'Positive','value':7}]}
        graph['nodes'].insert(0,decision);graph['entry']='decision'
        if branch_source=='branch':graph['edges'] += [{'from':'decision','port':port,'to':'body'} for port in ['true','false']]
        else:
            graph['nodes'].append({'id':'positive','kind':'code','control':'next','branchOwner':'decision','intent':'원래 enum 실행 줄','signature':{'args':[],'return':'void'},'arguments':{},'implementation':'Positive.node.json'})
            graph['edges'] += [{'from':'decision','port':'case:positive','to':'positive'},{'from':'positive','port':'next','to':'return:decision'},{'from':'decision','port':'next','to':'body'}]
    if nested_source:
        import copy
        graph=prepared['graph'];graph['profile']='sync-acyclic-nested-v1';private_sig={'args':[{'name':'amount','type':'long'}],'return':'long'}
        def leaf(name):return {'schema':1,'profile':'sync-acyclic-methods-v1','entry':'body','nodes':[{'id':'body','kind':'code','control':'next','intent':'원래 '+name,'signature':copy.deepcopy(private_sig),'arguments':{'amount':{'input':'amount'}},'implementation':name+'.node.json'}],'edges':[{'from':'body','port':'next','to':'exit:return'}],'exits':{'return':{'node':'body'}},'locals':[{'id':'kept','name':'정확한 값','type':'long','initial':{'constant':9223372036854775806}}]}
        def box(name,child):return {'id':name,'kind':'graph','control':'next','intent':'내부 '+name,'signature':copy.deepcopy(private_sig),'arguments':{'amount':{'input':'amount'}},'graph':child}
        right={'schema':1,'profile':'sync-acyclic-nested-v1','entry':'deep','nodes':[box('deep',leaf('Right'))],'edges':[{'from':'deep','port':'next','to':'exit:return'}],'exits':{'return':{'node':'deep'}},'locals':[]}
        graph['nodes'][:0]=[box('left',leaf('Left')),box('right',right)];graph['entry']='left';graph['edges'] += [{'from':'left','port':'next','to':'right'},{'from':'right','port':'next','to':'body'}]
        source_graph=copy.deepcopy(graph);native_context={'implementation':foreign+'Body','feature':fn,'signature':graph['nodes'][-1]['signature'],'imports':{}}
    definitions = f.metadata('featureBlueprintNodes', featureSource=feature_text, graph=prepared['graph'],**({'implementationContext':native_context,'bodyTarget':'common'} if nested_source else {}))
    if nested_source:
        nested_original={};nested_changed={}
        for row in definitions['nestedNodes']:
            if row['definition']['kind']!='code':continue
            key=row['id'];name='Left' if key=='left/body' else 'Right';body='return Keep(amount)+'+('1' if name=='Left' else '7')+'; // '+name+' 原文 😀\r\n';nested_original[key]=body;nested_changed[key]=body.replace('原文','복사본 본문').replace('\r\n','\n')
            (source/(name+'.node.json')).write_text(json.dumps({'schema':1,'node':'body','definitionHash':row['definitionHash'],'source':body,'helpers':'private static long Keep(long value){return value;} // '+name+' 보조 원문\r\n'}))

    if branch_source:
        decision_definition=next(v for v in definitions['nodes'] if v['id']=='decision')
        decision_source='return amount>0;' if branch_source=='branch' else 'return amount>0?Result.Positive:Result.NoBranch;'
        (source/'Decision.node.json').write_text(json.dumps({'schema':1,'node':'decision','definitionHash':decision_definition['definitionHash'],'source':decision_source+' // 분기 원문 😀 9223372036854775806\r\n','helpers':'private static long Keep(long value){return value;} // 보조 원문\r\n'}))
        if branch_source=='switch':
            positive=next(v for v in definitions['nodes'] if v['id']=='positive');(source/'Positive.node.json').write_text(json.dumps({'schema':1,'node':'positive','definitionHash':positive['definitionHash'],'source':'// 원래 enum 실행 줄 😀\r\n'}))
        source_graph=__import__('copy').deepcopy(prepared['graph'])
        copied_decision_source=decision_source.replace('amount>0','Keep(amount)>1')+' // 분기 원문 😀 9223372036854775806\n'
    node = next(n for n in definitions['nodes'] if n['id'] == 'body')
    (source / 'Body.graph.json').write_text(json.dumps(prepared['graph']))
    (source / 'Body.node.json').write_text(json.dumps({'schema': 1, 'node': 'body', 'definitionHash': node['definitionHash'], 'source': original_body}))
    (source / 'Body.celem').write_text((source / 'Body.celem').read_text().replace('body common "Body.csbody"', 'blueprint common "Body.graph.json"'))
registered = {p: p.read_bytes() for p in source.iterdir()}
f.original = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file()}
copied = None
checkpoint = None

def originals():
    f.originals()
    assert all(p.read_bytes() == value for p, value in registered.items())

def slot():
    return f.owner().locator('[data-module-method="' + fn + '"]')

def expand():
    if not slot().locator('[data-function-edit],[data-function-write-direct]').first.is_visible():
        f.owner().locator('[data-behavior-toggle="' + foreign + 'Rules"]').click()

def copy_choices():
    return [v['copy'] for _, v in f.pending()['blueprint'] if v.get('kind') == 'copy-selection' and v['copy']['owner'] == owner]

def wait_result(start, action, ok=True):
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        ids = {r['invoke']['requestId'] for r in f.traffic[start:] if r.get('invoke', {}).get('endpoint') == 'blueprint' and r['invoke']['input'].get('action') == action}
        rows = [r['result'] for r in f.traffic[start:] if r.get('result', {}).get('requestId') in ids and r['result'].get('error', {}).get('code') != 'stale_revision']
        if rows:
            assert bool(rows[-1]['ok']) == ok, rows[-1]
            f.idle()
            return rows[-1]
        f.page.wait_for_timeout(20)
    raise AssertionError({'action': action, 'evidence': str(f.case)})

def restart(i):
    held = f.pending()
    f.page.unroute_all(behavior='wait')
    f.page.close()
    f.stop()
    f.start(i)
    f.page = f.setup()
    f.page.set_viewport_size({'width': 2300, 'height': 1700})
    if d.is_view:
        f.owner = lambda: f.page.locator('.window[data-key=editor-1]')
    expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo')
    f.idle()
    assert f.pending() == held

def edit(before, after):
    # HTML textarea normalizes newlines; immutable donor bytes remain CRLF.
    f.edit_region(f.author().locator('[data-bp-node=body] [data-internal-code]'), before.replace('\r\n', '\n'), after)

def cancel_and_undo(before):
    button = f.author().locator('[data-bp-node=body] [data-internal-code]')
    f.author().locator(':scope > .window-title .caption').click(position={'x': 5, 'y': 8})
    f.author().locator('[data-bp-overview-node=body]').click()
    button.click()
    dialog = f.page.locator('.bp-script-dialog')
    code = dialog.locator('[data-code-source]')
    assert before in code.input_value()
    held = f.pending()
    code.evaluate("el=>{el.focus();const i=el.value.indexOf('소유 복사본');el.setSelectionRange(i,i+6)}")
    f.page.keyboard.insert_text('취소할 본문')
    f.page.keyboard.press('Control+z')
    assert before in code.input_value()
    f.page.keyboard.press('Control+y')
    assert '취소할 본문' in code.input_value()
    dialog.locator('[data-code-cancel]').click()
    expect(dialog).to_be_hidden()
    assert f.pending() == held

def reopen():
    f.close_author()
    expand()
    start = len(f.traffic)
    slot().locator('[data-function-edit]').click()
    expect(f.author().locator('[data-bp-node=body]')).to_be_visible()
    assert not f.page.locator('.feature-import-dialog').count(), 're-edit the selected owned copy, not a second clone'
    row = wait_result(start, 'read')['result']
    assert row['feature'] == fn and row['slotContext']['implementation'] == copied
    assert row['slotContext']['writable'] is True
    assert row['slotContext']['copySource']['implementation'] == foreign + 'Body'
    assert row['slotContext']['copySource']['target'] == target
    if branch_source:
        assert row['entry']==source_graph['entry'] and row['edges']==source_graph['edges']
        assert {v['name']:json.loads(v['valueJson']) for v in row['exits']}==source_graph['exits']
        decision=next(v for v in row['nodes'] if v['id']=='decision')
        original=json.loads((source/'Decision.node.json').read_text())
        assert decision['control']==branch_source and decision['source']==copied_decision_source and decision['helpers']==original['helpers']
        assert decision['signature']==next(v for v in source_graph['nodes'] if v['id']=='decision')['signature']
        if branch_source=='switch':assert decision['executionEnum']==next(v for v in source_graph['nodes'] if v['id']=='decision')['executionEnum']
    return row

def nested_enter(parts):
    f.idle()
    for part in parts:
        f.author().locator('[data-bp-overview-node="'+part+'"]').click()
        f.author().locator('[data-bp-node="'+part+'"] [data-function-write-direct]').click()
        expect(f.author().locator('.bp-breadcrumbs')).to_be_visible()
        expect(f.author().locator('[data-bp-node="'+('deep' if part=='right' else 'body')+'"]').first).to_be_visible()
        f.idle()

def nested_parent():
    f.author().locator('.bp-breadcrumbs button').first.click()
    expect(f.author().locator('[data-bp-node=left]')).to_be_visible()
    f.idle()

def nested_edit_initial():
    for path in ['left','right/deep']:
        nested_enter(path.split('/'));f.author().locator('[data-bp-overview-node=body]').click()
        if nested_pins and path=='left':
            nested_pin_initial();nested_changed[path+'/body']=nested_changed[path+'/body'].replace('Keep(amount)','Keep(received)')
        f.edit_region(f.author().locator('[data-bp-node=body] [data-internal-code]'),nested_original[path+'/body'].replace('\r\n','\n'),nested_changed[path+'/body']);nested_parent()
    f.checked('원래 내부 편집/빵부스러기로 깊이1/2 copy를 오가며 동명 leaf의 서로 다른 본문·qualified 입력을 보존한다')

def nested_value(raw=None,option=None):
    f.author().locator('[data-bp-overview-node=body]').click();pin=f.author().get_by_role('combobox',name='입력값 · amount',exact=True);pin.click();menu=f.page.get_by_role('dialog',name='핀 값 선택',exact=True)
    if option:menu.get_by_role('button',name=option,exact=True).click()
    else:
        menu.get_by_role('searchbox',name='값 검색').fill(raw);menu.locator('[data-value-new]').click()
    expect(menu).to_have_count(0);f.idle()

def nested_values_initial():
    nested_enter(['left']);f.author().locator('[data-bp-overview-node=body]').click();before=f.pending()['blueprint'];f.author().get_by_role('combobox',name='입력값 · amount',exact=True).click();menu=f.page.get_by_role('dialog',name='핀 값 선택',exact=True);search=menu.get_by_role('searchbox',name='값 검색');search.fill('9223372036854775808');search.press('Enter');expect(search).to_have_attribute('aria-invalid','true');assert any(v.get('type')=='value-draft:amount' and v['text']=='9223372036854775808' for _,v in f.pending()['blueprint']);search.press('Escape');expect(menu).to_have_count(0);assert f.pending()['blueprint']==before
    nested_value(raw='9223372036854775804');nested_parent();nested_enter(['right','deep']);before=f.pending()['blueprint'];nested_value(option='지역변수 · 정확한 값')
    if 'value-undo' in sys.argv[4:]:
        after=f.pending()['blueprint'];f.author().locator('.bp-viewport').focus();f.page.keyboard.press('Control+z');assert dict(f.pending()['blueprint'])==dict(before),'value selection Undo must restore every original keyed cell';f.author().locator('.bp-viewport').focus();f.page.keyboard.press('Control+Shift+z');assert dict(f.pending()['blueprint'])==dict(after);f.checked('하위 값 선택 Undo/Redo는 그 프레임의 값만 되돌리고 다른 깊이의 입력과 본문을 보존한다')
    nested_parent()
    f.checked('원래 핀 값 선택의 overflow 원문/취소, 정확한64비트 상수와 프레임별 기존 local 연결은 다른 leaf·본문·공개 계약을 보존한다')

def nested_value_guards():
    current=f.state();schema=next(v for v in current['editorViews'] if v['view']=='1')['schema'] if d.is_view else current['schema'];surface={'view':'1','viewBinding':next(v for v in current['editorViews'] if v['view']=='1')['authorBinding']} if d.is_view else {}
    graph=copied+'/body:'+target+'/graph:left';base={'owner':owner,'ownerHash':schema['textHash'],'ownerRevision':schema['revision']};row=f.invoke('blueprint',{'action':'read','id':graph,**base,**surface})['result']['result'];held=f.pending();before=checkpoint.read_bytes();proof=json.dumps(sorted([[v['id'],v['revision'],v['hash']] for v in row['sources']]))
    for value in ['{"constant":"wrong"}','{"node":"right/deep/body"}']:
        request={'action':'authorBatch','id':graph,**base,**surface,'attempt':__import__('uuid').uuid4().hex,'sourceProof':proof,'checkpointHash':row['checkpointHash'],'edits':[{'action':'source','node':'body','text':'return 100; // 첫 편집도 적용되면 안 됨'},{'action':'argument','node':'body','name':'amount','valueJson':value}]}
        f.invoke('blueprint',request,False)
        if 'retry-values' in sys.argv[4:]:
            query={**request,'action':'settledAuthorBatch'};settled=f.invoke('blueprint',query)['result']['result'];assert settled['settled'] is False and settled['baselineUnchanged'] is True
            raw=info.read_bytes()
            try:
                info.write_bytes(raw+'\n// fixture 실제 외부 변경\n'.encode());changed=f.invoke('blueprint',query)['result']['result'];assert changed['settled'] is False and changed['baselineUnchanged'] is False
            finally:info.write_bytes(raw)
            settled=f.invoke('blueprint',query)['result']['result'];assert settled['settled'] is False and settled['baselineUnchanged'] is True
        assert checkpoint.read_bytes()==before and f.pending()==held
        again=f.invoke('blueprint',{'action':'read','id':graph,**base,**surface})['result']['result'];assert next(n for n in again['nodes'] if n['id']=='body')['source']==next(n for n in row['nodes'] if n['id']=='body')['source']
    f.checked('실제 bound 하위 authorBatch에서 마지막 값의 타입/프레임 오류는 먼저 편집한 본문도 저장하지 않고 checkpoint·입력을 보존한다')
    if 'retry-values' in sys.argv[4:]:f.checked('이전 거절의 전체 미적용/원래 기준은 조회로 확인하고 실제 물리 source 변경이 있으면 재시도 증거를 주지 않는다')

def nested_pin_name(before,after):
    unit=f.author().locator('[data-bp-node=body] [data-action-side=inputs][data-action-field="'+before+'"]');name=unit.locator('[data-action-field-name]');name.fill(after);name.press('Enter');f.idle();expect(f.author().locator('[data-bp-node=body] [data-action-side=inputs][data-action-field="'+after+'"]')).to_be_visible()

def nested_pin_value(name,raw=None,option=None):
    f.author().get_by_role('combobox',name='입력값 · '+name,exact=True).click();menu=f.page.get_by_role('dialog',name='핀 값 선택',exact=True)
    if option:menu.get_by_role('button',name=option,exact=True).click()
    else:menu.get_by_role('searchbox',name='값 검색').fill(raw);menu.locator('[data-value-new]').click()
    expect(menu).to_have_count(0);f.idle()

def nested_pin_initial():
    name=f.author().locator('[data-bp-node=body] [data-action-side=inputs][data-action-field=amount] [data-action-field-name]');held=f.pending()['blueprint'];name.fill('잘못된 이름');assert any(v.get('type')=='contract-draft:amount' and v['text']=='잘못된 이름' for _,v in f.pending()['blueprint']);name.press('Escape');assert dict(f.pending()['blueprint'])==dict(held)
    nested_pin_name('amount','received');after=f.pending()['blueprint'];f.author().locator('.bp-viewport').focus();f.page.keyboard.press('Control+z');assert dict(f.pending()['blueprint'])==dict(held);f.author().locator('.bp-viewport').focus();f.page.keyboard.press('Control+Shift+z');assert dict(f.pending()['blueprint'])==dict(after)
    f.author().locator('[data-bp-node=body] [data-action-field-add=inputs]').click();f.idle();nested_pin_name('input1','note');nested_pin_value('note',raw='"처음 😀"')
    box=f.author().bounding_box();assert round(box['width'])==850 and round(box['height'])==600;assert round(f.author().locator('[data-bp-node=body]').bounding_box()['width'])==360;f.page.screenshot(path=str(f.case/'pin-copy-prepared.png'))
    f.checked('원래 내부 핀 이름/추가 조작과 불완전 이름 취소·Undo/Redo는 기존 값 연결과 다른 프레임 입력을 보존한다')

def nested_pins_saved():
    global mode
    nested_enter(['left']);f.author().locator('[data-bp-overview-node=body]').click();before=checkpoint.read_bytes()
    nested_pin_value('note',option='연결 해제');f.author().get_by_role('button',name='note 삭제',exact=True).click();f.idle();nested_pin_name('received','saved');f.author().locator('[data-bp-node=body] [data-action-field-add=inputs]').click();f.idle()
    after=f.pending()['blueprint'];f.author().locator('.bp-viewport').focus();f.page.keyboard.press('Control+z');assert not any(v.get('type')=='parameters' and any(a['name']=='input1' for a in json.loads(v['text'])['args']) for _,v in f.pending()['blueprint']);f.author().locator('.bp-viewport').focus();f.page.keyboard.press('Control+Shift+z');assert dict(f.pending()['blueprint'])==dict(after)
    button=f.author().locator('[data-bp-node=body] [data-internal-code]');pending=f.pending();button.click();dialog=f.page.locator('.bp-script-dialog');code=dialog.locator('[data-code-source]');text=code.input_value();at=text.index(nested_changed['left/body']);code.evaluate('(el,i)=>{el.focus();el.setSelectionRange(i,i)}',at);f.page.keyboard.insert_text('// 취소할 편집\n');dialog.locator('[data-code-cancel]').click();expect(dialog).to_be_hidden();assert f.pending()==pending
    f.checked('저장된 copy의 핀 추가 Undo/Redo와 C# 편집 취소는 명시 해제·이름/매핑·원문을 보존한다')
    previous=nested_changed['left/body'];wanted=previous.replace('Keep(received)','Keep(saved)').replace('복사본 본문','저장된 핀 본문');f.edit_region(f.author().locator('[data-bp-node=body] [data-internal-code]'),previous,wanted)
    mark=len(f.traffic);f.author().locator('[data-bp-save]').click();wait_result(mark,'authorBatch',False);f.idle();rejected=f.pending();assert checkpoint.read_bytes()==before and any(v.get('kind')=='author-attempt' for _,v in rejected['blueprint']);originals()
    nested_pin_value('input1',raw='"저장 😀"');held=f.pending();assert all(dict(held['blueprint']).get(k)==v for k,v in rejected['blueprint'] if v.get('kind')=='author-attempt')
    restart(10);expect(f.author().locator('.bp-breadcrumbs')).to_be_visible();expect(f.author().locator('[data-action-field=saved]')).to_be_visible();expect(f.author().locator('[data-action-field=input1]')).to_be_visible()
    reads=[v['result']['result'] for v in f.traffic if isinstance(v.get('result',{}).get('result'),dict) and v['result']['result'].get('privatePath')=='left' and 'slotContext' in v['result']['result']];assert reads[-1]['slotContext']['copySource']['implementation']==foreign+'Body'
    f.checked('핀 삭제/추가·수동 C# 결합의 미완성 후보는 전체 거절하고 새 값 선택·cold 뒤에도 원래 실패 기록과 모든 입력을 보존한다')
    if mode=='context':
        f.close_author();d.open_peer();peer=f.page.locator('.window[data-key=editor-2]');title=peer.locator('.object-title-name').bounding_box();box=peer.bounding_box();f.page.mouse.move(title['x']+5,title['y']+5);f.page.mouse.down();f.page.mouse.move(1100+title['x']-box['x']+5,800+title['y']-box['y']+5,steps=10);f.page.mouse.up();reopen();nested_enter(['left']);d.verify_peer();assert all(dict(f.pending()['blueprint']).get(k)==v for k,v in held['blueprint']);f.checked('독립 창의 서로 다른 입력은 private 핀 계획 재진입에서도 분리된다')
    other_checkpoint=None
    if mode=='projects':
        listing=f.state()['listingId'];f.page.close();f.stop();other=f.case/'pin other root'/'owned project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory'));shutil.copytree(source,other.parent/source.name);f.env['CONFECTORY_WEB_PROJECT']=str(other/'project.cproj');f.start(11);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});second=f.state()['listingId'];other_checkpoint=next(other.glob('.confectory/edit-workspaces/*/draft.json'));other_before=other_checkpoint.read_bytes();f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700})
        def enter(id):
            f.page.locator('.brand').click();expect(f.page.locator('.home-grid')).to_be_visible();f.page.locator('[data-enter="'+id+'"]').click();expect(f.page.locator('.work-body')).to_be_visible();f.idle()
        enter(listing);assert all(dict(f.pending()['blueprint']).get(k)==v for k,v in held['blueprint']);enter(second);assert not any(v.get('type')=='parameters' for _,v in f.pending()['blueprint']);enter(listing);reopen();nested_enter(['left']);assert other_checkpoint.read_bytes()==other_before;f.env['CONFECTORY_WEB_PROJECT']=str(f.manifest);f.checked('실제 프로젝트 전환은 private 핀·본문 계획을 다른 프로젝트에 적용하지 않고 보존한다')
    if mode=='conflict':
        f.invoke('schema',{'id':owner});state=f.state()['schema'];f.invoke('editDescription',{'id':owner,'hash':state['textHash'],'revision':state['revision'],'value':'핀 계획 경합의 다른 저장'});f.invoke('saveDraft',{});peer=checkpoint.read_bytes();assert peer!=before;f.idle();mark=len(f.traffic);f.author().locator('[data-bp-save]').click();observed=wait_result(mark,'settledAuthorBatch')['result'];assert observed['settled'] is False and observed.get('baselineUnchanged') is not True;f.page.wait_for_function('()=>/유지|보존|다시 확인/.test(document.querySelector(".window[data-key=blueprint] .bp-status")?.textContent||"")');f.idle();assert checkpoint.read_bytes()==peer and all(dict(f.pending()['blueprint']).get(k)==v for k,v in held['blueprint']);restart(12);assert checkpoint.read_bytes()==peer and all(dict(f.pending()['blueprint']).get(k)==v for k,v in held['blueprint']);originals();f.checked('실제 다른 창 경합은 핀·값·본문 전부 미적용이며 peer 초안과 원래 입력/실패 기록을 보존한다');f.browser.close();print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'nativeWindows':False},ensure_ascii=False));sys.exit(0)
    applies=set();queries=set();lost=set()
    if mode=='loss':
        def intercept(route):
            request=route.request.post_data_json
            if request.get('op')=='invoke' and request.get('endpoint')=='blueprint':
                action=request.get('input',{}).get('action')
                if action=='authorBatch':applies.add(request['requestId'])
                elif applies and action=='settledAuthorBatch':queries.add(request['requestId'])
            response=route.fetch();payload=response.json()
            for row in payload.get('results',[]):
                if row['requestId'] in applies|queries:
                    rid=row['requestId'];lost.add(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport_lost'})
            route.fulfill(response=response,json=payload)
        f.page.route('**/api/request',intercept)
    if mode=='storage':checkpoint.chmod(0o400)
    mark=len(f.traffic);f.author().locator('[data-bp-save]').click()
    if mode=='storage':
        wait_result(mark,'authorBatch',False);f.idle();assert checkpoint.read_bytes()==before
        now=dict(f.pending()['blueprint'])
        for key,value in held['blueprint']:
            if value.get('kind')=='author-attempt':assert {k:v for k,v in value.items() if k not in ['previousAttempts','basis']} in [{k:v for k,v in old.items() if k!='basis'} for old in now[key].get('previousAttempts',[])]
            else:assert now.get(key)==value
        read=next(v['invoke']['input'] for v in reversed(f.traffic) if v.get('invoke',{}).get('endpoint')=='blueprint' and v['invoke']['input'].get('action')=='read' and v['invoke']['input']['id'].endswith('/graph:left'));live=f.invoke('blueprint',read)['result']['result'];node=next(n for n in live['nodes'] if n['id']=='body');assert [a['name'] for a in node['signature']['args']]==['received','note'] and node['source']==previous
        originals();checkpoint.chmod(0o600);f.checked('실제 쓰기 실패는 핀 정의/바인딩/C# 어느 것도 부분 저장하지 않고 입력·이전 실패를 보존한다');f.author().locator('[data-bp-save]').click()
    if mode=='loss':
        deadline=time.monotonic()+90
        while time.monotonic()<deadline and not queries&lost:f.page.wait_for_timeout(20)
        assert len(applies)==1 and queries&lost;f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(13);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});f.idle();expect(f.author().locator('.bp-breadcrumbs')).to_be_visible();expect(f.author().locator('[data-action-field=saved]')).to_be_visible();mark=len(f.traffic);f.author().locator('[data-bp-save]').click();wait_result(mark,'settledAuthorBatch');assert not any(v.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for v in f.traffic[mark:]);f.checked('핀 결합 저장/조회 응답 유실 뒤 cold에서 receipt를 조회해 새 계약을 중복 적용하지 않는다')
    f.page.wait_for_function('()=>document.querySelector(".window[data-key=blueprint] .bp-status")?.textContent.startsWith("복사본 ·")',timeout=120000);f.idle();assert not any(v.get('type') in ['source','parameters'] for _,v in f.pending()['blueprint']);nested_changed['left/body']=wanted;originals()
    if mode=='context':
        d.verify_peer();peer=f.page.locator('.window[data-key=editor-2]');peer.locator('[data-element-action=discard]').click();expect(peer.get_by_label('Count 기본값',exact=True)).to_have_value('8');d.peer_inputs=None
    if other_checkpoint:assert other_checkpoint.read_bytes()==other_before
    nested_parent();f.checked('동일 후보/CAS의 핀·바인딩·수동 C#은 거절 후 명시 보완으로 함께 저장되고 원본/부모/다른 프레임을 보존한다');mode='normal'

def nested_saved_edit():
    if nested_pins:return nested_pins_saved()
    nested_enter(['left']);f.author().locator('[data-bp-overview-node=body]').click()
    if nested_values:nested_value_guards()
    previous=nested_changed['left/body'];value=previous.replace('복사본 본문','저장된 내부 재편집')
    f.edit_region(f.author().locator('[data-bp-node=body] [data-internal-code]'),previous,value)
    if nested_values:
        if 'retry-values' in sys.argv[4:]:
            nested_value(option='연결 해제');old_checkpoint=checkpoint.read_bytes();mark=len(f.traffic);f.author().locator('[data-bp-save]').click();wait_result(mark,'authorBatch',False);f.idle();rejected=f.pending();assert checkpoint.read_bytes()==old_checkpoint and any(v.get('kind')=='author-attempt' for _,v in rejected['blueprint']);originals()
        nested_value(option='입력 · amount')
    if 'cold-private' in sys.argv[4:]:
        restart(8);expect(f.author().locator('.bp-breadcrumbs')).to_be_visible();expect(f.author().locator('[data-bp-node=body]')).to_be_visible();f.checked('저장된 copy의 하위 창과 미저장 leaf 입력도 실제 cold 재시작에서 소유/프로젝트 문맥을 유지한다')
    f.author().locator('[data-bp-save]').click();f.page.wait_for_function('()=>{const s=document.querySelector(".window[data-key=blueprint] .bp-status");return s&&s.textContent.startsWith("복사본 ·")}',timeout=120000);f.idle();assert not any(v.get('type')=='source' for _,v in f.pending()['blueprint']);nested_changed['left/body']=value
    if 'retry-values' in sys.argv[4:]:f.checked('미완성 값 저장 거절 뒤 원래 기준 미적용을 확인하고 새 명시 값으로 재시도하며 이전 실패/입력/CAS를 보존한다')
    nested_parent();nested_enter(['right','deep']);button=f.author().locator('[data-bp-node=body] [data-internal-code]');button.click();dialog=f.page.locator('.bp-script-dialog');assert nested_changed['right/deep/body'] in dialog.locator('[data-code-source]').input_value();dialog.locator('[data-code-cancel]').click();nested_parent()
    f.checked(('저장된 copy 내부 본문/값' if nested_values else '저장된 copy 내부 source-only')+' 후보/CAS는 선택 leaf만 바꾸며 다른 깊이 동명 leaf·원본·공개 계약을 보존한다')

def accept():
    f.close_author()
    review = d.review()
    review.locator('[data-reject]').click()
    originals()
    review = d.review()
    if review.locator('[data-review-advanced]').count():
        review.locator('[data-review-advanced]').click()
        if review.locator('[data-advanced-reviewed]').count():
            review.locator('[data-advanced-reviewed]').check()
    start = len(f.traffic)
    saved = checkpoint.read_bytes()
    review.locator('#confirm').click()
    if target == 'windows':
        # Review checks the draft first. The compiler-backed Confirm then
        # enforces Build.cs's requested-target/common body rule.
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            ids = {r['invoke']['requestId'] for r in f.traffic[start:] if r.get('invoke', {}).get('endpoint') == 'confirmGroup'}
            results = [r['result'] for r in f.traffic[start:] if r.get('result', {}).get('requestId') in ids and r['result'].get('error', {}).get('code') != 'stale_revision']
            if results: break
            f.page.wait_for_timeout(20)
        assert results and results[-1]['ok'] and results[-1]['result']['sourceConfirmed'] is False
        state = f.state()['review']
        assert state['status'] == 'invalid' and state['target'] == 'linux' and not state['token']
        assert checkpoint.read_bytes() == saved
        review.locator('[data-reject]').click()
        originals()
        f.checked('windows-only 복사본의 Linux compiler Confirm은 거절하며 선택한 target·저장 초안·원본을 보존한다')
        return False
    expect(review).to_have_count(0, timeout=120000)
    f.idle()
    assert all(p.read_bytes() == value for p, value in registered.items())
    return True

def snapshot():
    return {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}

try:
    f.start(0)
    f.invoke('select', {'id': owner})
    f.invoke('saveDraft', {})
    f.invoke('select', {'id': f.id})
    with sync_playwright() as pw:
        expect.set_options(timeout=60000)
        f.browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        f.page = f.setup()
        f.page.set_viewport_size({'width': 2300, 'height': 1700})
        d.open_info()
        # Move the original 460px card, without altering product layout.
        title = f.owner().locator('.object-title-name').bounding_box()
        box = f.owner().bounding_box()
        f.page.mouse.move(title['x'] + 5, title['y'] + 5)
        f.page.mouse.down()
        f.page.mouse.move(1780 + title['x'] - box['x'] + 5, 80 + title['y'] - box['y'] + 5, steps=10)
        f.page.mouse.up()
        expand()
        slot().locator('[data-function-write-direct]').click()
        picker = f.page.get_by_role('dialog', name='구현 선택', exact=True)
        expect(picker.locator('[data-copy-source="' + foreign + 'Body"]')).to_have_count(2)
        mark=len(f.traffic)
        picker.locator('[data-copy-source="' + foreign + 'Body"][data-copy-target="' + target + '"]').click()
        if mode=='diagnostic':
            result=wait_result(mark,'readImplementationCopy',False)
            f.page.screenshot(path=str(f.case/'branch-copy-before.png'));originals()
            f.checked('원래 구현 선택에 표시된 code '+branch_source+' Blueprint를 선택하면 기존 copy whitelist에서 실제 UI 준비가 거절되고 원본은 유지된다')
            f.browser.close();print(json.dumps({'evidence':str(f.case),'checks':f.checks,'renderer':True,'refused':result},ensure_ascii=False));sys.exit(0)
        expect(f.author().locator('[data-bp-node=body]')).to_be_visible()
        if branch_source=='switch':
            expect(f.author().locator('[data-bp-node=decision] [data-branch-name=positive]')).to_have_attribute('readonly','')
            expect(f.author().locator('[data-bp-node=decision] [data-branch-remove=positive]')).to_be_disabled()
            f.author().locator('[data-bp-overview-node=decision]').click()
            button=f.author().locator('[data-bp-node=decision] [data-internal-code]');button.click();dialog=f.page.locator('.bp-script-dialog');code=dialog.locator('[data-code-source]')
            value=code.input_value();assert 'public enum Result' in value and 'Positive = 7' in value and 'public static Result Execute(long amount)' in value
            code.evaluate("el=>{el.focus();const i=el.value.indexOf('Positive = 7');el.setSelectionRange(i,i+8)}");f.page.keyboard.insert_text('Changed');assert code.input_value()==value
            dialog.locator('[data-code-cancel]').click()
            original_decision=json.loads((source/'Decision.node.json').read_text())['source']
            f.edit_region(button,original_decision.replace('\r\n','\n'),copied_decision_source)
            f.author().locator('[data-bp-overview-node=body]').click()
            box=f.author().bounding_box();assert round(box['width'])==850 and round(box['height'])==600
            f.page.screenshot(path=str(f.case/'enum-copy-prepared.png'))
        if nested_source:
            nested_edit_initial()
            if nested_values:nested_values_initial()
            if 'cold-private' in sys.argv[4:]:
                nested_enter(['right','deep']);f.page.screenshot(path=str(f.case/'nested-private-before-cold.png'));restart(7)
                expect(f.author().locator('.bp-breadcrumbs')).to_be_visible();button=f.author().locator('[data-bp-node=body] [data-internal-code]');button.click();dialog=f.page.locator('.bp-script-dialog');assert nested_changed['right/deep/body'] in dialog.locator('[data-code-source]').input_value();dialog.locator('[data-code-cancel]').click();nested_parent()
                f.checked('저장 전 private copy의 깊이2 화면과 서로 다른 leaf 입력은 실제 cold 재시작에서 snapshot/선택/경로와 함께 복원한다')
        edited = original_body.replace('\r\n', '\n').replace('원문', '소유 복사본 😀')
        edit(original_body, edited)
        f.close_author()
        copied = copy_choices()[0]['implementation']
        d.field(['Power']).locator('[data-property-value]').fill('9223372036854775804')
        f.owner().locator('[data-element-action=save]').click()
        deadline = time.monotonic() + 90
        while copy_choices() and time.monotonic() < deadline:
            f.page.wait_for_timeout(30)
        assert not copy_choices(), f.pending()
        f.idle()
        checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
        originals()
        f.checked('외부 함수의 선택 target만 로컬 소유 copy로 저장하며 정확한64비트 값·등록 원본·다른 target을 보존한다')
        if confirmed:
            accept()
            f.original = snapshot()
        before = checkpoint.read_bytes()
        current = reopen()
        assert current['slotContext']['checkpointPlain'] is True
        provenance = current['slotContext']['copySource']
        if nested_source:
            nested_saved_edit();before=checkpoint.read_bytes();current=reopen()
        cancel_and_undo(edited)
        final = edited.replace('소유 복사본 😀', '재편집 · 한글 😀')
        edit(edited, final)
        held = f.pending()
        assert any(v.get('type') == 'source' and final in v.get('text', '') for _, v in held['blueprint'])
        f.close_author()
        restart(1)
        current = reopen()
        assert current['slotContext']['copySource'] == provenance
        originals()
        f.checked('기본/독립 정보 창의 재편집·Undo/Redo·팝업 취소·cold 복원은 같은 copy ID/외부 함수/출처/선택 target과 입력 원문을 유지한다')
        if mode == 'context':
            f.close_author()
            d.open_peer()
            # Place both floating cards through the original title drag. The
            # common helper overlaps the owner; a low row also keeps the
            # restored Blueprint title/close button clear of resize handles.
            peer = f.page.locator('.window[data-key=editor-2]')
            title = peer.locator('.object-title-name').bounding_box()
            box = peer.bounding_box()
            f.page.mouse.move(title['x'] + 5, title['y'] + 5)
            f.page.mouse.down()
            f.page.mouse.move(1100 + title['x'] - box['x'] + 5, 800 + title['y'] - box['y'] + 5, steps=10)
            f.page.mouse.up()
            current = reopen()
            d.verify_peer()
        if mode == 'projects':
            listing = f.state()['listingId']
            f.page.close()
            f.stop()
            other = f.case / 'other root' / 'owned project'
            shutil.copytree(f.project, other, ignore=shutil.ignore_patterns('.confectory'))
            shutil.copytree(source, other.parent / source.name)
            f.env['CONFECTORY_WEB_PROJECT'] = str(other / 'project.cproj')
            f.start(3)
            f.invoke('select', {'id': owner})
            f.invoke('saveDraft', {})
            second = f.state()['listingId']
            other_checkpoint = next(other.glob('.confectory/edit-workspaces/*/draft.json'))
            other_before = other_checkpoint.read_bytes()
            f.page = f.setup()
            f.page.set_viewport_size({'width': 2300, 'height': 1700})
            def enter(id):
                f.page.locator('.brand').click()
                expect(f.page.locator('.home-grid')).to_be_visible()
                f.page.locator('[data-enter="' + id + '"]').click()
                expect(f.page.locator('.work-body')).to_be_visible()
                f.idle()
            enter(listing)
            assert all(dict(f.pending()['blueprint']).get(k) == v for k, v in held['blueprint'])
            enter(second)
            assert not any(v.get('type') == 'source' for _, v in f.pending()['blueprint'])
            enter(listing)
            current = reopen()
            assert other_checkpoint.read_bytes() == other_before
            f.env['CONFECTORY_WEB_PROJECT'] = str(f.manifest)
            f.checked('같은 namespace의 다른 프로젝트로 전환해도 copy 입력을 잘못 적용하지 않고 문서/초안 문맥을 보존한다')
        if mode == 'conflict':
            # A real independent saved writer, not just an in-memory revision.
            f.invoke('schema', {'id': owner})
            state = f.state()['schema']
            f.invoke('editDescription', {'id': owner, 'hash': state['textHash'], 'revision': state['revision'], 'value': '다른 창의 저장'})
            f.invoke('saveDraft', {})
            peer_checkpoint = checkpoint.read_bytes()
            assert peer_checkpoint != before
            f.author().locator('[data-bp-save]').click()
            f.page.wait_for_function('()=>{const s=document.querySelector(".window[data-key=blueprint] .bp-status");return s&&/유지|보존|다시 확인/.test(s.textContent)}')
            f.idle()
            assert checkpoint.read_bytes() == peer_checkpoint
            assert all(dict(f.pending()['blueprint']).get(k) == v for k, v in held['blueprint'])
            restart(4)
            assert checkpoint.read_bytes() == peer_checkpoint
            assert all(dict(f.pending()['blueprint']).get(k) == v for k, v in held['blueprint'])
            originals()
            f.checked('실제 다른 창 저장 경합은 전체 미적용이며 cold 뒤에도 새 peer 초안과 copy 입력 원문을 보존한다')
        else:
            applies, queries, lost = set(), set(), set()
            if mode == 'loss':
                def intercept(route):
                    request = route.request.post_data_json
                    if request.get('op') == 'invoke' and request.get('endpoint') == 'blueprint':
                        action = request.get('input', {}).get('action')
                        if action == 'authorBatch': applies.add(request['requestId'])
                        elif applies and action == 'settledAuthorBatch': queries.add(request['requestId'])
                    response = route.fetch()
                    payload = response.json()
                    for row in payload.get('results', []):
                        if row['requestId'] in applies | queries:
                            rid = row['requestId']
                            lost.add(rid)
                            row.clear()
                            row.update(requestId=rid, ok=False, error={'code': 'transport_lost'})
                    route.fulfill(response=response, json=payload)
                f.page.route('**/api/request', intercept)
            if mode == 'storage':
                checkpoint.chmod(0o400)
            start = len(f.traffic)
            f.author().locator('[data-bp-save]').click()
            if mode == 'loss':
                deadline = time.monotonic() + 90
                while time.monotonic() < deadline and not queries & lost:
                    f.page.wait_for_timeout(20)
                assert len(applies) == 1 and queries & lost
                assert all(dict(f.pending()['blueprint']).get(k) == v for k, v in held['blueprint'])
                mark = len(f.traffic)
                # The server already committed. Restart without comparing the
                # stale before-write journal to the reconciled result.
                f.page.unroute_all(behavior='wait')
                f.page.close(); f.stop(); f.start(5)
                f.page = f.setup()
                f.page.set_viewport_size({'width': 2300, 'height': 1700})
                expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo')
                reopen()
                f.author().locator('[data-bp-save]').click()
                wait_result(mark, 'settledAuthorBatch')
                assert not any(r.get('invoke', {}).get('input', {}).get('action') == 'authorBatch' for r in f.traffic[mark:])
                f.checked('저장/결과 조회 응답 유실 뒤 cold에서 기존 receipt를 조회하고 같은 copy를 중복 저장하지 않는다')
            if mode == 'storage':
                # Inspect the rendered failure and the actual saved/live draft.
                f.page.wait_for_function('()=>{const s=document.querySelector(".window[data-key=blueprint] .bp-status");return s&&/consumer_error|실패|유지|마치지|저장 상태/.test(s.textContent)}', timeout=60000)
                f.idle()
                assert checkpoint.read_bytes() == before
                now = f.pending()
                assert all(dict(now['blueprint']).get(k) == v for k, v in held['blueprint']), {'before': held, 'after': now}
                read = next(r['invoke']['input'] for r in reversed(f.traffic) if r.get('invoke', {}).get('endpoint') == 'blueprint' and r['invoke']['input'].get('action') == 'read')
                live = f.invoke('blueprint', read)['result']['result']
                assert next(n['source'] for n in live['nodes'] if n['id'] == 'body') == edited
                rows = json.loads(checkpoint.read_text())['changes']
                assert final not in json.dumps(rows, ensure_ascii=False)
                checkpoint.chmod(0o600)
                f.checked('저장 실패는 checkpoint·live 본문·입력 원문·기존 copy를 보존하고 부분 적용하지 않는다')
                start = len(f.traffic)
                f.author().locator('[data-bp-save]').click()
            # Confirmed enum copies observe more source records. Wait for the
            # complete receipt/read/receipt reconciliation, keeping every assertion below.
            f.page.wait_for_function('()=>{const s=document.querySelector(".window[data-key=blueprint] .bp-status");return s&&s.textContent.startsWith("복사본 ·")}',timeout=120000)
            f.idle()
            assert not any(v.get('type') == 'source' for _, v in f.pending()['blueprint'])
            rows = {r['id']: r for r in json.loads(checkpoint.read_text())['changes']}
            assert json.loads(rows[copied + '/body:' + target + '/node:body']['draft'])['source'] == final
            if mode == 'context': d.verify_peer()
            if mode == 'projects': assert other_checkpoint.read_bytes() == other_before
            originals()
            f.checked('명시 Save/재시도는 기존 copy 본문만 저장하며 원본 함수 계약·출처·다른 target은 불변이다')
            restart(2)
            if mode == 'context': d.verify_peer()
            if mode == 'context':
                # Existing global Review policy blocks unapplied inputs. Do
                # not discard another window implicitly or loosen that guard.
                f.close_author()
                saved = checkpoint.read_bytes()
                f.owner().locator('[data-element-action=confirm]').click()
                dialog = f.page.get_by_role('dialog', name='관련 변경 검토', exact=True)
                expect(dialog).to_be_visible()
                dialog.locator('#review-creation').click()
                expect(f.page.locator('#status')).to_contain_text('미적용 입력을 먼저 적용')
                expect(dialog).to_be_visible()
                d.verify_peer()
                assert checkpoint.read_bytes() == saved
                originals()
                dialog.get_by_role('button', name='닫기', exact=True).click()
                peer = f.page.locator('.window[data-key=editor-2]')
                peer.locator('[data-element-action=discard]').click()
                expect(peer.get_by_label('Count 기본값', exact=True)).to_have_value('8')
                expect(peer.locator('.object-title-description')).to_have_value('')
                assert not [(k, v) for k, v in f.pending()['schema'] if '|' + f.n + 'RefTarget|view:2|element|' in k]
                d.peer_inputs = None
                originals()
                f.checked('copy Save/cold는 다른 창 입력을 보존하며 전역 Review는 미적용 입력을 차단하고 그 창의 명시 취소만 입력을 해제한다')
            accepted = accept()
            if mode == 'context': d.verify_peer()
            if mode == 'projects': assert other_checkpoint.read_bytes() == other_before
            if accepted:
                located = next(r for r in f.metadata('describe', project=str(f.manifest))['units'] if r['id'] == copied + '/body:' + target + '/node:body')
                assert json.loads((f.project / located['path']).read_text())['source'] == final
            else:
                rows = {r['id']: r for r in json.loads(checkpoint.read_text())['changes']}
                assert json.loads(rows[copied + '/body:' + target + '/node:body']['draft'])['source'] == final
            assert all(p.read_bytes() == value for p, value in registered.items())
            if accepted:
                if nested_source:
                    units=f.metadata('describe',project=str(f.manifest))['units'];body_key=copied+'/body:'+target
                    for key,value in nested_changed.items():
                        unit=next(v for v in units if v['id']==body_key+'/node:'+key.replace('/','/node:'));record=json.loads((f.project/unit['path']).read_text());assert record['source']==value and record['node']=='body';original_record=json.loads((source/('Left.node.json' if key=='left/body' else 'Right.node.json')).read_text());assert record['helpers']==original_record['helpers']
                    if nested_pins:
                        graph_unit=next(v for v in units if v['id']==body_key);stored=json.loads((f.project/graph_unit['path']).read_text());left=stored['nodes'][0]['graph']['nodes'][0];right=stored['nodes'][1]['graph']['nodes'][0]['graph']['nodes'][0];assert left['signature']=={'args':[{'name':'saved','type':'long'},{'name':'input1','type':'string'}],'return':'long'} and left['arguments']=={'saved':{'input':'amount'},'input1':{'constant':'저장 😀'}};assert right['signature']=={'args':[{'name':'amount','type':'long'}],'return':'long'} and stored['edges']==source_graph['edges'] and stored['exits']==source_graph['exits'];f.checked('실제 compiler Confirm 뒤 private 핀/값/본문만 변경되고 공개 계약·형제·실행선·원본은 보존된다')
                    if nested_values:
                        graph_unit=next(v for v in units if v['id']==body_key);stored=json.loads((f.project/graph_unit['path']).read_text());left=stored['nodes'][0]['graph']['nodes'][0];right=stored['nodes'][1]['graph']['nodes'][0]['graph']['nodes'][0];assert left['arguments']['amount']=={'input':'amount'} and right['arguments']['amount']=={'local':'kept'};assert stored['edges']==source_graph['edges'] and stored['exits']==source_graph['exits'];f.checked('내부 값/본문을 한 후보로 저장·Confirm하고 입력 재연결·다른 프레임 local·실행선/반환·원계약과 원본을 보존한다')
                    f.checked('중첩 copy의 실제 compiler Confirm은 qualified 각 leaf 본문만 반영하고 동명/공개 계약·부모/외부 원문을 보존한다')
                if branch_source:
                    units=f.metadata('describe',project=str(f.manifest))['units'];graph_unit=next(v for v in units if v['id']==copied+'/body:'+target)
                    stored=json.loads((f.project/graph_unit['path']).read_text());assert stored['entry']==source_graph['entry'] and stored['edges']==source_graph['edges'] and stored['exits']==source_graph['exits']
                    decision_unit=next(v for v in units if v['id']==copied+'/body:'+target+'/node:decision')
                    decision_record=json.loads((f.project/decision_unit['path']).read_text());origin_record=json.loads((source/'Decision.node.json').read_text())
                    assert decision_record['source']==copied_decision_source and decision_record['helpers']==origin_record['helpers']
                    f.checked('copied code '+branch_source+'의 분기/enum ID·값·순서·모든 route·반환과 C#·보조 원문은 실제 compiler Confirm 뒤에도 유지된다')
                f.checked('재시작·실제 compiler Review 취소와 명시 Confirm은 같은 copy만 반영하고 외부 팩을 쓰지 않는다')
        f.page.screenshot(path=str(f.case / 'external-copy-final.png'))
        assert not f.errors and not f.external, (f.errors, f.external)
        f.browser.close()
    print(json.dumps({'checks': f.checks, 'evidence': str(f.case), 'actualEngine': True, 'renderer': True, 'target': target, 'confirmedAtReedit': confirmed, 'nativeWindows': False, 'accountOrInference': False}, ensure_ascii=False))
except Exception:
    try:
        (f.case / 'external-copy-failure.json').write_text(json.dumps({'state': f.state(), 'traffic': f.traffic[-70:], 'checks': f.checks, 'errors': f.errors}, ensure_ascii=False, indent=2))
    except Exception:
        pass
    print('EVIDENCE ' + str(f.case), flush=True)
    raise
finally:
    if checkpoint is not None:
        checkpoint.chmod(0o600)
    f.stop()
