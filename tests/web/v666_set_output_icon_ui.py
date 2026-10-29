"""Original Set owned output picker, actual engine candidate/receipt/Confirm; synthetic assets only."""
import copy,json,pathlib,shutil,sys,time
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3] if len(sys.argv)>3 else 'normal';private=False;feature_label='IconPrivate' if private else 'Slot';feature_id=f.n+feature_label;graph_id=f.n+'SlotBody/body:common'
graph_file=f.project/'Slot.graph.json';record_file=f.project/'Slot.node.json'
if private:
 implementation=feature_id+'Body';text='function '+feature_id+' (long amount) -> long {}';prepared=f.metadata('blueprintPrepareFeature',id=feature_id,text=text,implementation=implementation,graphPath='IconPrivate.graph.json',nodePath='IconPrivate.node.json');signature={'args':[{'name':'amount','type':'long'}],'return':'long'}
 child={'schema':1,'profile':'sync-acyclic-methods-v1','entry':'body','nodes':[{'id':'body','kind':'code','control':'next','intent':'직접 소유한 내부 본문','signature':copy.deepcopy(signature),'arguments':{'amount':{'input':'amount'}},'implementation':'IconPrivate.node.json'}],'edges':[{'from':'body','port':'next','to':'exit:return'}],'exits':{'return':{'node':'body'}},'locals':[]}
 graph=prepared['graph'];graph.update(profile='sync-acyclic-nested-v1',entry='frame',nodes=[{'id':'frame','kind':'graph','control':'next','intent':'직접 소유한 내부 frame','signature':copy.deepcopy(signature),'arguments':{'amount':{'input':'amount'}},'graph':child}],edges=[{'from':'frame','port':'next','to':'exit:return'}],exits={'return':{'node':'frame'}})
 context={'implementation':implementation,'feature':feature_id,'signature':signature,'imports':{}};definitions=f.metadata('featureBlueprintNodes',featureSource=text,implementationContext=context,bodyTarget='common',graph=graph);definition=next(n for n in definitions['nestedNodes'] if n['id']=='frame/body');record={'schema':1,'node':'body','definitionHash':definition['definitionHash'],'source':'return amount+1; // 그대로 보존할 직접 소유 본문 😀\r\n'}
 graph_file=f.project/'IconPrivate.graph.json';record_file=f.project/'IconPrivate.node.json';graph_file.write_text(json.dumps(graph));record_file.write_text(json.dumps(record));(f.project/'IconPrivate.celem').write_text(text.replace('{}','{provide '+feature_id+' with '+implementation+';}'));(f.project/'IconPrivateBody.celem').write_text(prepared['implementation']);f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element IconPrivate function "IconPrivate.celem";element IconPrivateBody implementation "IconPrivateBody.celem";registry Confectory.Build.DotNet'));graph_id=implementation+'/body:common/graph:frame'
graph=json.loads(graph_file.read_text());graph.setdefault('locals',[]).extend([{'id':'ownStored','name':'저장한 값','type':'long','initial':{'constant':0}},{'id':'counter','name':'기존 변수','type':'long','initial':{'constant':0}},{'id':'sharedOut','name':'공유 출력','type':'long','initial':{'constant':0}}])
for id,local,output in [('store','ownStored','ownStored'),('shared','counter','sharedOut')]:graph['nodes'].append({'id':id,'kind':'set','control':'next','intent':'중간저장','local':local,'outputLocal':output,'signature':{'args':[{'name':'value','type':'long'}],'return':'void'},'arguments':{'value':{'input':'amount'}}})
graph['edges'] += [{'from':'shared','port':'next','to':'store'},{'from':'store','port':'next','to':graph['entry']}];graph['entry']='shared';
if mode in ['reset','reset-late']:next(n for n in graph['nodes'] if n['id']=='store')['icon']='★'
next(n for n in graph['nodes'] if n['id']=='body')['arguments']['amount']={'node':'store','output':'stored'}
defs=f.metadata('featureBlueprintNodes',featureSource=f.fn,graph=graph,featureContracts={f.n+'Native':f.native,f.n+'Donor':f.items['Donor'][1]});record=json.loads(record_file.read_text());record['definitionHash']=next(n for n in defs['nodes'] if n['id']=='body')['definitionHash'];record_file.write_text(json.dumps(record));graph_file.write_text(json.dumps(graph))
snapshot={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file()};checks=[]
def original():assert all(p.read_bytes()==v for p,v in snapshot.items())
def call(action,**kw):return f.invoke('blueprint',dict(action=action,id=graph_id,**kw))['result']['result']
def data():return call('read')
def node(d):return next(n for n in d['nodes'] if n['id']=='store')
def pending():return [(k,v) for k,v in f.pending()['blueprint'] if v.get('type')=='icon']
def button():return f.author().locator('[data-bp-node=store] [data-signature-icon]')
def open_graph():
 f.idle()
 if f.author().locator('[data-bp-node=store]').is_visible():return
 f.page.locator('#workspace').click(button='right',position={'x':1300,'y':300});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.get_by_role('button',name='기능',exact=True).click();b.locator('[data-browser-control=object-query]').fill(feature_label);b.locator('[data-browser-control=object-search]').click();b.locator('[data-object="'+feature_id+'"]').press('Enter');b.locator('[data-close]').first.click();f.idle();f.page.locator('[data-operation=feature-author-open]').first.click()
 if private and not button().is_visible():
  f.author().locator('[data-bp-overview-node=frame]').click();f.author().locator('[data-bp-node=frame] [data-function-write-direct]').click()
 expect(button()).to_be_visible()
def popup():
 f.author().locator('[data-bp-percent]').click();zoom=f.page.get_by_role('dialog',name='노드 화면 배율',exact=True);zoom.get_by_role('button',name='전체 보기',exact=True).click();zoom.locator('[data-zoom-value]').press('Escape');f.page.screenshot(path=str(f.case/'set-output-before-popup.png'));button().click();p=f.page.get_by_role('dialog',name='저장한 값 아이콘 편집',exact=True);expect(p).to_be_visible();return p
def position():return f.author().locator('[data-bp-node=store]').evaluate('e=>({x:e.offsetLeft,y:e.offsetTop})')
def pick(value):
 p=popup();p.locator('[data-icon-choice="'+value+'"]').click();p.get_by_role('button',name='적용',exact=True).click();expect(button()).to_have_text(value)
def save():
 f.author().locator('[data-bp-save]').click();expect(f.author().locator('.bp-status')).to_have_text('저장됨',timeout=90000);f.idle();assert not pending()
def restart(i):
 f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph();f.idle()
def review():
 f.author().locator('[data-bp-complete]').click();f.page.locator('.window[data-key=review]:visible,.window[data-key=targets]:visible').first.wait_for(state='visible',timeout=60000)
 target=f.page.locator('.window[data-key=targets]')
 if target.is_visible():target.locator('[data-target-choice]').select_option('portable');target.locator('[data-close]').click();f.author().locator('[data-bp-complete]').click()
 r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible();return r
try:
 f.start(0);f.invoke('select',{'id':feature_id});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before_checkpoint=checkpoint.read_bytes();baseline=data()
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph()
  expect(button()).to_have_text('★' if mode in ['reset','reset-late'] else '◇');expect(f.author().locator('[data-bp-node=shared] [data-signature-icon]')).to_be_disabled()
  expect(f.author().locator('[data-bp-node=native] [data-function-icon]')).to_have_count(0);p=popup();p.locator('[data-icon-choice="🔥"]').click();p.locator('[data-cancel]').click();assert not pending();p=popup();p.get_by_label('기호나 이모지',exact=True).fill('ab');p.get_by_role('button',name='적용',exact=True).click();expect(p).to_be_visible();f.page.keyboard.press('Escape');assert not pending();original();f.checked('원본 소유 Set 출력만 아이콘을 편집하고 호출/wrapper는 거절하며 취소·Escape·잘못된 glyph는 입력과 원본을 유지한다')
  start_position=position();pick('★');assert position()==start_position;button().press('Control+z');assert not pending();button().press('Control+y');expect(button()).to_have_text('★');original();restart(1);expect(button()).to_have_text('★');assert position()==start_position;f.checked('기존 private Undo/Redo와 cold는 해당 Set 출력 아이콘만 보존하고 공유 함수·부모·다른 target 원본을 쓰지 않는다')
  p=popup();asset=f.page.evaluate("()=>{const c=document.createElement('canvas');c.width=c.height=32;const x=c.getContext('2d');x.fillStyle='#2c9';x.fillRect(0,0,32,32);return c.toDataURL('image/png')}");import base64
  p.locator('[type=file]').set_input_files({'name':'synthetic-action.png','mimeType':'image/png','buffer':base64.b64decode(asset.split(',')[1])});expect(p.locator('.object-icon-preview img')).to_be_visible();p.get_by_role('button',name='적용',exact=True).click();expect(button().locator('img')).to_be_visible();wanted=pending()[0][1]['text'];assert wanted.startswith('data:image/webp;base64,');held=pending();original();f.checked('사용자가 선택한 생성 PNG를 기존 로컬 128×128 WebP 경로로 정규화하며 외부 업로드 없이 카드에 표시한다')
  if mode in ['reset','reset-late']:p=popup();p.get_by_role('button',name='아이콘 없음',exact=True).click();wanted='';held=pending();expect(button()).to_have_text('◇')
  if mode=='project':
   other=f.case/'other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory'));other_bytes=(other/graph_file.name).read_bytes();f.pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(other/'project.cproj');f.start(10);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph();assert not pending();pick('🔥');f.pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.project/'project.cproj');f.start(11);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph();assert pending()==held;expect(button().locator('img')).to_be_visible();assert (other/graph_file.name).read_bytes()==other_bytes;original();f.checked('같은 namespace/Set 출력 ID의 다른 실제 프로젝트를 왕복해도 이미지·private 입력·원문은 섞이지 않는다')
  if mode=='cancel':
   p=popup();p.locator('[data-icon-choice="🔥"]').click();p.locator('[data-cancel]').click();assert pending()==held and checkpoint.read_bytes()==before_checkpoint;original();restart(2);assert pending()==held;f.checked('새 팝오버 입력 취소·cold는 앞서 보존한 이미지 입력과 공유 초안·원본을 유지한다')
  else:
   if mode=='conflict':
    peer=data();call('argument',node='body',name='amount',valueJson='{"constant":9223372036854775804}',basis=peer['basis']);f.invoke('saveDraft',{});peer_checkpoint=checkpoint.read_bytes();assert peer_checkpoint!=before_checkpoint;f.author().locator('[data-bp-save]').click();f.idle();assert pending()==held and checkpoint.read_bytes()==peer_checkpoint;original();restart(2);f.author().locator('[data-bp-save]').click();f.idle();assert pending()==held and checkpoint.read_bytes()==peer_checkpoint;f.checked('다른 실제 편집의 graph/checkpoint CAS 충돌은 아이콘 후보를 전체 미적용하고 peer 저장·원본·cold 입력을 보존한다')
    assert not f.errors and not f.external,(f.errors,f.external);f.browser.close();raise SystemExit(0)
   if mode=='guard':
    def forged(route):
     body=route.request.post_data_json
     if body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and body.get('input',{}).get('action')=='authorBatch':body['input']['edits'][0]['node']='shared';route.continue_(post_data=json.dumps(body))
     else:route.continue_()
    f.page.route('**/api/request',forged);f.author().locator('[data-bp-save]').click();f.idle();assert pending()==held and checkpoint.read_bytes()==before_checkpoint;f.page.unroute('**/api/request',forged);original();f.checked('동일 관측 거래를 호출/wrapper 대상으로 변조해도 서버는 전체 미적용하며 원본 함수·caller·이미지 입력을 보존한다')
   if mode=='storage':
    checkpoint.chmod(0o400)
    try:f.author().locator('[data-bp-save]').click();f.idle();assert pending()==held and checkpoint.read_bytes()==before_checkpoint;original()
    finally:checkpoint.chmod(0o600)
    restart(2);assert pending()==held;f.checked('checkpoint 실패는 후보를 부분 저장하지 않고 이미지 입력을 cold 복구한다')
   if mode=='loss':
    applies=set();queries=set();lost=[]
    def lose(route):
     body=route.request.post_data_json
     if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
      action=body.get('input',{}).get('action')
      if action=='authorBatch':applies.add(body['requestId'])
      elif applies and action=='settledAuthorBatch':queries.add(body['requestId'])
     response=route.fetch();payload=response.json()
     for v in payload.get('results',[]):
      if v['requestId'] in applies|queries:rid=v['requestId'];lost.append(rid);v.clear();v.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
     route.fulfill(response=response,json=payload)
    f.page.route('**/api/request',lose);f.author().locator('[data-bp-save]').click()
    for _ in range(600):
     if applies and any(r in queries for r in lost):break
     f.page.wait_for_timeout(50)
    assert len(applies)==1 and any(r in queries for r in lost) and pending()==held;f.page.unroute_all(behavior='wait');mark=len(f.traffic);restart(2);save();assert not any(v.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for v in f.traffic[mark:]);f.checked('수락·조회 응답 유실은 cold receipt로 복구하며 아이콘 후보와 checkpoint를 중복 적용하지 않는다')
   elif mode in ['late','reset-late']:
    ids=set();paused={}
    def hold(route):
     body=route.request.post_data_json
     if body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and body.get('input',{}).get('action')=='authorBatch':ids.add(body['requestId'])
     response=route.fetch();payload=response.json()
     if not paused and any(v.get('ok') and v.get('requestId') in ids for v in payload.get('results',[])):paused.update(route=route,response=response);return
     route.fulfill(response=response)
    f.page.route('**/api/request',hold);f.author().locator('[data-bp-save]').click()
    for _ in range(600):
     if paused:break
     f.page.wait_for_timeout(50)
    assert paused and len(ids)==1;pick('🛡️');paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',hold);f.idle();assert pending() and pending()[0][1]['text']=='🛡️';wanted='🛡️';restart(3);expect(button()).to_have_text(wanted);save();f.checked('수락 응답을 기다리는 중 새 아이콘은 receipt로 재기준하고 cold·다음 명시 Save로만 저장한다')
   else:save()
   if mode=='plan-preserve':
    f.author().locator('[data-bp-node=store] [data-set-target]').select_option('');save();assert (node(data()).get('icon') or '')==wanted;f.checked('기존 Set 계획을 명시 재적용해도 저장된 출력 아이콘·ID·타입·값을 지우지 않는다')
   final=data();assert (node(final).get('icon') or '')==wanted;assert node(final)['definitionHash']==node(baseline)['definitionHash'];assert final['diagnostics']==baseline['diagnostics'];original();restart(4);assert (node(data()).get('icon') or '')==wanted;f.checked('한 후보/CAS Save와 cold는 표시만 저장하며 원래 C#·본문 stamp·핀·실행 연결·다른 target은 유지한다')
   r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();original();r=review();r.locator('[data-review-advanced]').click();r.locator('[data-advanced-reviewed]').check();r.screenshot(path=str(f.case/'set-output-review.png'));(f.case/'review-state.json').write_text(json.dumps(f.state().get('review'),ensure_ascii=False,indent=2));expect(r.locator('#confirm')).to_be_enabled(timeout=10000)
   if mode=='source-conflict':
    saved_checkpoint=checkpoint.read_bytes();graph_file.write_bytes(graph_file.read_bytes()+b'\n ');snapshot[graph_file]=graph_file.read_bytes();r.locator('#confirm').click();f.idle();expect(r.locator('#confirm')).to_be_disabled(timeout=120000);assert checkpoint.read_bytes()==saved_checkpoint;original();assert not pending() and not f.errors and not f.external;f.checked('최종 Review 뒤 실제 파일 경합은 Confirm CAS에서 전체 거절하고 저장된 이미지 초안·원문·본문을 보존한다');f.browser.close();raise SystemExit(0)
   r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();changed={str(p.relative_to(f.project)) for p,v in snapshot.items() if p.read_bytes()!=v};assert changed=={graph_file.name},changed;assert record_file.read_bytes()==snapshot[record_file];g=json.loads(graph_file.read_text());saved_nodes=g['nodes'][0]['graph']['nodes'] if private else g['nodes'];assert (next(n for n in saved_nodes if n['id']=='store').get('icon') or '')==wanted;f.checked('Review 취소와 명시 compiler Confirm은 선택된 graph metadata 파일만 바꾸며 함수 정의·C#·원본 본문 record·부모·외부를 보존한다')
  assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'set-output-icon.png'));f.browser.close()
except Exception:
 try:(f.case/'set-output-failure.json').write_text(json.dumps(dict(state=f.state(),traffic=f.traffic[-80:],errors=f.errors),ensure_ascii=False,indent=2)+'\n')
 except Exception:pass
 try:f.page.screenshot(path=str(f.case/'set-output-icon-failure.png'),timeout=5000)
 except Exception:pass
 raise
finally:
 f.stop();(f.case/'set-output-icon-evidence.json').write_text(json.dumps(dict(checks=f.checks,errors=f.errors,mode=mode,actualWindows=False,actualMobile=False),ensure_ascii=False,indent=2)+'\n')
print('EVIDENCE',f.case,flush=True)
