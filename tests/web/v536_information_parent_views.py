"""Bound information classification in independent views, real isolated engine/renderer.
No real account, user project, grants, provider invocation or final source writes before explicit Confirm.
"""
import hashlib,json,shutil,sys,time
from playwright.sync_api import sync_playwright,expect
import v536_field_definitions_ui as d
from editor_navigation import open_project_tools
f=d.f
assert d.is_view,'append view to select the actual independent information window'
mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
owner=d.owner
expected_primary=f.n+'RefTarget'
info=f.project/'FreeInfo.celem';info.write_text(info.read_text().replace('FreeInfo {','FreeInfo extends '+f.n+'Leaf {',1))
for name,group in [('InfoA','info'),('InfoB','info'),('ConceptCategory','concept')]:
 (f.project/(name+'.celem')).write_text('category '+f.n+name+' {value editorBrowserGroup="'+group+'";}')
 f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element '+name+' category "'+name+'.celem";registry Confectory.Build.DotNet',1))
f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file()}
if mode=='projects':
 b_root=f.case/'another root'/'owned project';shutil.copytree(f.project,b_root);original_b={str(p.relative_to(b_root)):p.read_bytes() for p in b_root.rglob('*') if p.is_file()}

def wait(endpoint,after,action=None,ok=True):
 deadline=time.monotonic()+60
 while time.monotonic()<deadline:
  ids={r['invoke']['requestId'] for r in f.traffic[after:] if r.get('invoke',{}).get('endpoint')==endpoint and (action is None or r['invoke']['input'].get('action')==action)}
  results=[r['result'] for r in f.traffic[after:] if r.get('result',{}).get('requestId') in ids and r['result'].get('error',{}).get('code')!='stale_revision']
  if results:
   assert bool(results[-1].get('ok')) is ok,results;f.idle();return results[-1]
  f.page.wait_for_timeout(20)
 raise AssertionError('no completed '+endpoint)
def choose(category,success=True):
 f.idle();f.owner().locator('.object-title-name').click();f.owner().locator('.object-parent-change').click();p=f.page.get_by_role('dialog',name='부모 변경',exact=True);expect(p).to_be_visible();after=len(f.traffic);p.locator('[data-parent-choice="'+(f.n+category if category else '')+'"]').click();result=wait('moveBrowserFolders',after,ok=success)
 if success:expect(f.owner().locator('[data-parent] strong') if category else f.owner().locator('[data-parent]')).to_have_text(category or 'Root')
 return result

def reenter():
 global expected_primary
 f.idle()
 if f.owner().is_visible():f.owner().locator('[data-close]').first.click()
 expect(f.owner()).to_be_hidden();f.page.locator('#workspace').click(button='right',position={'x':80,'y':100});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=info]').click();b.locator('[data-browser-control="object-query"]').fill('FreeInfo');b.locator('[data-browser-control="object-search"]').click();row=b.locator('[data-object="'+owner+'"]');expect(row).to_have_attribute('aria-disabled','false');f.idle();row.click(button='right');f.page.locator('.context-menu').get_by_role('button',name='새 창으로 열기',exact=True).click();expect(f.owner()).to_be_visible();expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo');b.locator('[data-close]').first.click();f.idle();state=f.state();assert [(r['view'],r['id']) for r in state['editorViews']]==[('1',owner),('2',f.n+'RefTarget')];assert state['draft']['id'] in [expected_primary,owner];expected_primary=state['draft']['id']

def view():return next(row for row in f.state()['editorViews'] if row['view']=='1')
def proof(category='InfoA'):
 f.invoke('relationsMap',{});row=view()['schema'];nodes=f.state()['relationsMap']['nodes'];folder=next(v for v in nodes if v['id']==f.n+category)
 return {'view':'1','id':owner,'moves':[{'id':owner,'revision':row['revision'],'hash':row['textHash'],'folder':folder['id'],'folderRevision':folder['revision'],'folderHash':folder['textHash']}]}
def restart(i):
 f.pending();f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1500});expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo',timeout=60000);f.idle();d.verify_peer()
def original_peer():
 d.verify_peer();f.originals();assert f.state()['draft']['id']==expected_primary
def accept(review):
 if review.locator('[data-additional-changes]').count():
  review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
  if ack.count():ack.check()
 after=len(f.traffic);review.locator('#confirm').click();result=wait('confirmGroup',after);assert result['result']['sourceConfirmed'];expect(review).to_be_hidden()
def folder():return f.state()['folderMove']
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});f.invoke('select',{'id':f.n+'RefTarget'})
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1500});d.open_info();d.open_peer();checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();original_peer()
  if mode=='normal':
   choose('InfoA');assert set(folder()['ids'])=={owner,f.n+'InfoA'};assert view()['draft']['id']==owner and view()['schema']['revision']==view()['draft']['revision'];assert checkpoint.read_bytes()==before;original_peer();f.checked('실제 독립 정보 창의 카테고리 선택은 그 정보만 분류하고 primary RefTarget 선택·peer exact64 입력·schema extends를 보존한다')
   after=len(f.traffic);expect(f.owner().locator('[data-element-action=discard]')).to_be_enabled();f.owner().locator('[data-element-action=discard]').click();wait('browserDrafts',after,'discard');expect(f.owner().locator('[data-parent]')).to_have_text('Root');assert not folder();original_peer();f.checked('독립 창 변경 취소는 bound 정보의 완전한 분류 그룹만 복원하며 다른 창의 입력·원본·primary 선택을 건드리지 않는다')
   choose('InfoA');open_project_tools(f.page);after=len(f.traffic);f.page.get_by_role('button',name='의미 편집 이력',exact=True).click();history=f.page.locator('.window[data-key=history]');expect(history).to_be_visible();f.idle();h=wait('draftHistory',after,'inspect')['result'];assert set(row['id'] for row in h['undo']['units'])=={owner,f.n+'InfoA'}
   after=len(f.traffic);history.locator('[data-history-move=undo]').click();result=wait('draftHistory',after,'undo');assert result['result']['accepted'];assert not folder() and 'editorFolder' not in view()['draft']['text'];expect(f.owner().locator('[data-parent]')).to_have_text('Root');original_peer()
   after=len(f.traffic);history.locator('[data-history-move=redo]').click();result=wait('draftHistory',after,'redo');assert result['result']['accepted'];assert folder();expect(f.owner().locator('[data-parent] strong')).to_have_text('InfoA');original_peer();history.locator('[data-close]').first.click()
   f.owner().locator('[data-close]').first.click();expect(f.owner()).to_be_hidden();reenter();original_peer();f.checked('native Undo/Redo 뒤 늦은 분류 조회도 열린 독립 창의 부모 표시를 갱신하고 실제 창 닫기/재진입은 같은 view와 private 입력을 보존한다')
   after=len(f.traffic);f.owner().locator('[data-element-action=save]').click();wait('saveEditorView',after);restart(1);expect(f.owner().locator('[data-parent] strong')).to_have_text('InfoA');assert folder() and 'extends '+f.n+'Leaf' in view()['draft']['text'];original_peer();f.checked('독립 창 Save와 프로세스 cold는 분류·상속 원문과 view1/view2의 서로 다른 문맥·입력을 복원한다')
   review=d.review();assert {r['id'] for r in f.state()['review']['units']}=={owner,f.n+'InfoA'};review.locator('[data-reject]').click();expect(review).to_be_hidden();f.originals();d.verify_peer();review=d.review();accept(review);assert not folder();assert 'editorFolder = "'+f.n+'InfoA"' in info.read_text();assert 'extends '+f.n+'Leaf' in info.read_text();assert all((f.project/k).read_bytes()==v for k,v in f.original.items() if k!='FreeInfo.celem');d.verify_peer();f.checked('독립 창에서 Review 취소 후 새 명시적 compiler Confirm은 분류만 최종 반영하며 parent/category/등록팩/다른 창 입력을 보존한다')
   f.page.screenshot(path=str(f.case/'information-parent-view-final.png'))
  elif mode=='boundaries':
   original=proof();before_draft=view()['draft']['text'];wrong=json.loads(json.dumps(original));wrong['id']=f.n+'Leaf';wrong['moves'][0]['id']=f.n+'Leaf';f.invoke('moveBrowserFolders',wrong,False);assert not folder() and view()['draft']['text']==before_draft
   wrong=json.loads(json.dumps(original));wrong['moves'].append(json.loads(json.dumps(original['moves'][0])));f.invoke('moveBrowserFolders',wrong,False);assert not folder()
   wrong=json.loads(json.dumps(original));wrong['view']='3';f.invoke('moveBrowserFolders',wrong,False);assert not folder();original_peer();f.checked('잘못된 bound id·미개방 view·복수 source 위조는 서버에서 거절하고 아무 분류도 적용하지 않는다')
   basis=view()['schema'];f.invoke('editViewDescription',{'view':'1','id':owner,'revision':basis['revision'],'hash':basis['textHash'],'value':'보존할 동료 shared 변경'});f.invoke('moveBrowserFolders',original,False);assert not folder();f.invoke('openEditorView',{'view':'1','id':owner,'viewMode':'properties'});assert view()['schema']['description']=='보존할 동료 shared 변경';assert checkpoint.read_bytes()==before;original_peer();f.checked('실제 같은 정보의 newer shared revision은 오래된 분류 후보 전체를 거절해 동료 원문·checkpoint·private 입력을 보존한다')
   # Save that explicit peer source, then a new user choice is permitted with its new proof.
   f.invoke('saveEditorView',{'view':'1','id':owner});reenter();choose('InfoA');drafts=f.invoke('browserDrafts',{'view':'1','id':owner,'action':'status','ids':[owner]})['result']['result'];cancel={k:drafts[k] for k in ['ids','checkpointHash','ownerHash']};cancel.update(view='1',id=owner,action='discard',revisions=[r['revision'] for r in drafts['rows']],hashes=[r['hash'] for r in drafts['rows']]);wrong=json.loads(json.dumps(cancel));wrong['ids']=[owner];wrong['revisions']=wrong['revisions'][:1];wrong['hashes']=wrong['hashes'][:1];f.invoke('browserDrafts',wrong,False);assert folder();wrong=json.loads(json.dumps(cancel));wrong['id']=f.n+'RefTarget';f.invoke('browserDrafts',wrong,False);assert folder();f.invoke('browserDrafts',cancel);assert not folder();f.invoke('openEditorView',{'view':'1','id':owner,'viewMode':'properties'});assert view()['schema']['description']=='보존할 동료 shared 변경';original_peer();f.checked('부분 그룹 또는 다른 owner 취소는 거절하고 정확한 그룹/CAS 취소만 saved peer 원문으로 복원한다')
  elif mode=='atomic':
   f.owner().locator('.object-title-description').fill('보존할 원자 저장 그룹');f.owner().locator('[data-element-action=save]').click();d.saved();saved=checkpoint.read_bytes();assert set(next(row for row in json.loads(saved)['changes'] if row['id']==owner)['atomicEditGroup'])=={owner,f.n+'ProjectManifest'};candidate=proof();before_text=view()['draft']['text'];f.invoke('moveBrowserFolders',candidate,False);assert not folder() and view()['draft']['text']==before_text and checkpoint.read_bytes()==saved;original_peer();f.checked('미확정 atomic 저장 그룹이 있는 정보는 분류 그룹으로 덮지 않고 전체 거절하여 저장본/원문/다른 입력/기존 검토 경계를 보존한다')
  elif mode=='projects':
   choose('InfoA');mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();wait('saveEditorView',mark);a=f.state();aid,alist=a['projectId'],a['listingId'];peer_a=d.peer_inputs;cp_a=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));saved_a=cp_a.read_bytes();choose('InfoB');assert set(folder()['ids'])=={owner,f.n+'InfoA',f.n+'InfoB'};mark=len(f.traffic);f.owner().locator('[data-element-action=discard]').click();wait('browserDrafts',mark,'discard');expect(f.owner().locator('[data-parent] strong')).to_have_text('InfoA');assert set(folder()['ids'])=={owner,f.n+'InfoA'} and cp_a.read_bytes()==saved_a;f.invoke('relationsMap',{});leaf=next(r for r in f.state()['relationsMap']['nodes'] if r['id']==f.n+'Leaf');cat=next(r for r in f.state()['relationsMap']['nodes'] if r['id']==f.n+'InfoB');f.invoke('moveBrowserFolders',{'moves':[{'id':leaf['id'],'revision':leaf['revision'],'hash':leaf['textHash'],'folder':cat['id'],'folderRevision':cat['revision'],'folderHash':cat['textHash']}]},False);assert set(folder()['ids'])=={owner,f.n+'InfoA'} and cp_a.read_bytes()==saved_a;f.pending();f.page.close();f.stop()
   f.env['CONFECTORY_WEB_PROJECT']=str(b_root/'project.cproj');f.start(1);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});f.invoke('select',{'id':f.n+'RefTarget'});f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1500});d.open_info();d.open_peer();peer=f.page.locator('.window[data-key=editor-2]');peer.get_by_label('Count 기본값',exact=True).fill('9223372036854775803');peer_b=[(k,v) for k,v in f.pending()['schema'] if '|'+f.n+'RefTarget|view:2|element|' in k];choose('InfoB');mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();wait('saveEditorView',mark);b=f.state();bid,blist=b['projectId'],b['listingId'];assert aid!=bid;cp_b=next(b_root.glob('.confectory/edit-workspaces/*/draft.json'));saved_b=cp_b.read_bytes();f.checked('같은 정보 ID/카테고리를 가진 실제 A/B 프로젝트가 독립 창의 분류와 서로 다른 peer exact64 입력을 각각 보관한다')
   def enter(listing):
    f.page.locator('.brand').click();expect(f.page.locator('.home-grid')).to_be_visible();f.page.locator('[data-enter="'+listing+'"]').click();expect(f.page.locator('.work-body')).to_be_visible();f.idle();expect(f.owner()).to_be_visible()
   enter(alist);expect(f.owner().locator('[data-parent] strong')).to_have_text('InfoA');assert [(k,v) for k,v in f.pending()['schema'] if '|'+f.n+'RefTarget|view:2|element|' in k]==peer_a
   f.owner().locator('.object-parent-change').click();picker=f.page.get_by_role('dialog',name='부모 변경',exact=True);picker.locator('[data-parent-choice="'+f.n+'InfoB"]').evaluate('el=>globalThis.retiredInfoParent=el.onclick');f.page.keyboard.press('Escape');enter(blist);expect(f.owner().locator('[data-parent] strong')).to_have_text('InfoB');mark=len(f.traffic);f.page.evaluate('async()=>await retiredInfoParent(new Event("click"))');f.idle();assert not any(r.get('invoke',{}).get('endpoint')=='moveBrowserFolders' for r in f.traffic[mark:]);assert cp_a.read_bytes()==saved_a and cp_b.read_bytes()==saved_b;assert [(k,v) for k,v in f.pending()['schema'] if '|'+f.n+'RefTarget|view:2|element|' in k]==peer_b;f.checked('실제 Home A→B 전환 후 은퇴한 A 부모 선택 callback은 B에 요청/적용/입력 삭제를 하지 않는다')
   enter(alist);choose(None);mark=len(f.traffic);f.owner().locator('[data-element-action=discard]').click();wait('browserDrafts',mark,'discard');expect(f.owner().locator('[data-parent] strong')).to_have_text('InfoA');assert cp_a.read_bytes()==saved_a and cp_b.read_bytes()==saved_b;f.pending();f.page.close();f.stop();f.start(2);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1500});expect(f.owner().locator('[data-parent] strong')).to_have_text('InfoB');expect(f.page.locator('.window[data-key=editor-2]').get_by_label('Count 기본값',exact=True)).to_have_value('9223372036854775803');assert [(k,v) for k,v in f.pending()['schema'] if '|'+f.n+'RefTarget|view:2|element|' in k]==peer_b;enter(alist);expect(f.owner().locator('[data-parent] strong')).to_have_text('InfoA');expect(f.page.locator('.window[data-key=editor-2]').get_by_label('Count 기본값',exact=True)).to_have_value('9223372036854775802');assert [(k,v) for k,v in f.pending()['schema'] if '|'+f.n+'RefTarget|view:2|element|' in k]==peer_a;f.originals();assert all((b_root/k).read_bytes()==v for k,v in original_b.items());f.checked('A의 분류 취소와 프로세스 cold·양방향 재진입은 A/B 저장 그룹과 peer 원문을 분리 복원하며 양쪽 원본을 바꾸지 않는다')
  elif mode=='peers':
   choose('InfoA');before_text=view()['draft']['text'];before_group=folder();f.page.locator('#workspace').click(button='right',position={'x':80,'y':100});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=info]').click();b.locator('[data-browser-control="object-query"]').fill('FreeInfo');b.locator('[data-browser-control="object-search"]').click();row=b.locator('[data-object="'+owner+'"]');expect(row).to_have_attribute('aria-disabled','false');row.click(button='right');f.page.locator('.context-menu').get_by_role('button',name='새 창으로 열기',exact=True).click();peer=f.page.locator('.window[data-key=editor-3]');expect(peer.locator('.object-title-name')).to_have_text('FreeInfo');b.locator('[data-close]').first.click();f.idle();state=f.state();assert state['draft']['id'] in [expected_primary,owner];expected_primary=state['draft']['id']
   head=peer.locator('.object-title-name').bounding_box();box=peer.bounding_box();f.page.mouse.move(head['x']+5,head['y']+5);f.page.mouse.down();f.page.mouse.move(240+head['x']-box['x']+5,130+head['y']-box['y']+5,steps=10);f.page.mouse.up();power=peer.locator('[data-property-path=\'["Power"]\'] [data-property-value]');power.fill('9223372036854775801');held=[(k,v) for k,v in f.pending()['schema'] if '|'+owner+'|view:3|element|' in k];assert held
   f.owner().locator('.object-title-name').click();mark=len(f.traffic);f.owner().locator('[data-element-action=discard]').click();expect(f.owner().locator('[data-element-error]')).to_contain_text('다른 창');assert folder()==before_group and view()['draft']['text']==before_text;assert [(k,v) for k,v in f.pending()['schema'] if '|'+owner+'|view:3|element|' in k]==held;assert not any(r.get('invoke',{}).get('endpoint')=='browserDrafts' and r['invoke']['input'].get('action')=='discard' for r in f.traffic[mark:]);original_peer();f.checked('같은 정보의 세 번째 창에 새 exact64 입력이 있으면 다른 창의 분류 취소는 native 쓰기 없이 거절하고 모든 입력/그룹을 유지한다')
   power.fill('9223372036854775806');assert not [(k,v) for k,v in f.pending()['schema'] if '|'+owner+'|view:3|element|' in k];f.owner().locator('.object-title-name').click();mark=len(f.traffic);f.owner().locator('[data-element-action=discard]').click();wait('browserDrafts',mark,'discard');assert not folder();expect(f.owner().locator('[data-parent]')).to_have_text('Root');expect(peer.locator('[data-parent]')).to_have_text('Root');expect(power).to_have_value('9223372036854775806');original_peer();f.checked('사용자가 peer 입력을 명시적으로 원래 값으로 정리한 뒤 정확한 분류 그룹 취소가 두 정보 창을 함께 갱신한다')
  elif mode=='loss':
   requests=set();lost=[]
   def intercept(route):
    payload=route.request.post_data_json
    if payload.get('op')=='invoke' and payload.get('endpoint')=='moveBrowserFolders':requests.add(payload['requestId'])
    response=route.fetch();reply=response.json()
    if not lost and payload.get('op')=='update' and any(row.get('requestId') in requests and row.get('ok') for row in reply.get('results',[])):
     lost.append(True);reply['results']=[{**row,'ok':False,'error':{'code':'owned_fixture_response_lost'}} if row.get('requestId') in requests else row for row in reply['results']];route.fulfill(response=response,json=reply);return
    route.fulfill(response=response)
   f.page.route('**/api/request',intercept);choose('InfoA',False);assert lost and len(requests)==1 and folder();original_peer();f.checked('실제 적용 뒤 응답 유실은 실패로 안내하며 같은 move를 자동 중복 실행하지 않고 기존 입력/원본을 보존한다')
   f.page.unroute('**/api/request',intercept);f.invoke('openEditorView',{'view':'1','id':owner,'viewMode':'properties'});reenter();expect(f.owner().locator('[data-parent] strong')).to_have_text('InfoA');original_peer();after=len(f.traffic);f.owner().locator('[data-element-action=save]').click();wait('saveEditorView',after);restart(1);assert folder();expect(f.owner().locator('[data-parent] strong')).to_have_text('InfoA');original_peer();assert len(requests)==1;f.checked('결과 조회·명시 Save/cold는 이미 적용된 그룹을 복원하며 source move를 중복 적용하지 않는다')
  else:raise AssertionError('unknown mode')
  assert not f.errors and not f.external,(f.errors,f.external);print(json.dumps({'checks':f.checks,'evidence':str(f.case),'mode':mode,'actualEngine':True,'nativeWindows':False,'loginOrInference':False},ensure_ascii=False));f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.browser.close()
except Exception:
 try:(f.case/'information-parent-view-failure.json').write_text(json.dumps({'state':f.state(),'traffic':f.traffic,'errors':f.errors},ensure_ascii=False))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
