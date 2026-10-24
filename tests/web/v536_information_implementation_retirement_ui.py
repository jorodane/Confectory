"""Original implementation-only delete/recovery UI; actual isolated engine/compiler/renderer."""
import json,time,sys,re,shutil
from playwright.sync_api import sync_playwright,expect
import v536_field_definitions_ui as d
f=d.f;owner=d.owner;fn=owner+'_Function_'+'c'*32;mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
def rpc(action,**args):return f.invoke('blueprint',{'action':action,**args})['result']['result']
def schema():f.invoke('schema',{'id':owner});return f.state()['schema']
def method():return f.owner().locator('[data-inline-method="'+fn+'"]')
def mark():return len(f.traffic)
def wait_result(endpoint,after,ok=True):
 deadline=time.monotonic()+90
 while time.monotonic()<deadline:
  ids={r['invoke']['requestId'] for r in f.traffic[after:] if r.get('invoke',{}).get('endpoint')==endpoint};rows=[r['result'] for r in f.traffic[after:] if r.get('result',{}).get('requestId') in ids and r.get('result',{}).get('error',{}).get('code')!='stale_revision']
  if rows:assert bool(rows[-1].get('ok'))==ok,rows;return rows[-1]
  f.page.wait_for_timeout(20)
 raise AssertionError({'endpoint':endpoint,'status':f.page.locator('#status').inner_text(),'evidence':str(f.case)})
def check(present):
 expect(method()).to_be_visible();expect(method().locator('[data-inline-name]')).to_have_value('화면 구현만 삭제');expect(method().locator('[data-function-edit]' if present else '[data-function-write-direct]')).to_be_visible();f.idle();assert not f.page.locator('#app').evaluate('e=>e.inert');assert fnpath.read_bytes()==fn_original;f.originals();expect(f.owner().get_by_label('Power 기본값',exact=True)).to_have_value('9223372036854775806')
def delete(cancel=False):
 f.idle();after=mark();method().locator('[data-function-delete-implementation]').click();dialog=f.page.get_by_role('dialog',name='구현 삭제',exact=True);expect(dialog).to_be_visible();expect(dialog).to_contain_text('이름과 입출력 정의는 유지됩니다');f.page.screenshot(path=str(f.case/'implementation-only-modal.png'));wait_result('planBrowserRemoval',after);f.originals()
 if cancel:dialog.locator('[data-implementation-cancel]').click();expect(dialog).to_have_count(0);check(True);return
 after=mark();dialog.locator('[data-implementation-confirm]').click();wait_result('browserRetirement',after);expect(dialog).to_have_count(0);check(False)
def recover():
 f.idle();f.page.locator('#workspace').click(button='right',position={'x':80,'y':100});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-browser-control="browser-actions"]').click();f.page.get_by_role('button',name='삭제 항목 복구',exact=True).click();after=mark();f.page.get_by_role('button',name='화면 구현만 삭제',exact=True).click();wait_result('browserRetirement',after);f.idle();b.locator('[data-close]').first.click();check(True)
def restart(i):
 f.pending();f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':2100,'height':1450});expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo');f.idle()
def review():return d.review()
def accept(r):
 if r.locator('[data-review-advanced]').count():
  r.locator('[data-review-advanced]').click()
  if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
 after=mark();r.locator('#confirm').click();wait_result('confirmGroup',after);expect(r).to_have_count(0,timeout=120000);f.idle();assert any(row.get('result',{}).get('result',{}).get('sourceConfirmed') is True for row in f.traffic[after:])
try:
 f.start(0);f.invoke('select',{'id':owner});s=schema();b=rpc('readOwnerEdits',id=owner,hash=s['textHash']);rpc('applySlots',id=owner,rows=[],basis=b['basis'],declaration={'id':owner,'hash':s['textHash'],'changes':[{'type':'function-add','id':fn,'name':'화면 구현만 삭제','description':'선언/핀/원문 보존'}]});s=schema();m=next(v for v in s['ownFunctions'] if v['id']==fn);p=rpc('readFeature',id=fn,hash=m['hash'],revision=m['revision'],owner=owner,ownerHash=s['textHash'],ownerRevision=s['revision']);created=rpc('createFeature',id=fn,basis=p['basis']);s=schema();g=rpc('read',id=created['id'],owner=owner,ownerHash=s['textHash'],ownerRevision=s['revision']);rpc('source',id=created['id'],basis=g['basis'],node='body',text='return; // retained UI implementation');f.invoke('saveDraft',{});schema();ids=f.state()['draft']['creationReviewIds'];f.invoke('reviewGroup',{'ids':ids,'target':'portable'});r=f.state()['review'];assert f.invoke('confirmGroup',{'ids':ids,'token':r['token']})['result']['result']['sourceConfirmed'];fnpath=f.project/('elements/'+fn.split('::')[1]+'.celem');fn_original=fnpath.read_bytes();f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts};initial=dict(f.original);checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
 f.invoke('select',{'id':f.id})
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2100,'height':1450});d.open_info();check(True);assert abs(f.owner().bounding_box()['width']-460)<1
  if mode=='normal':
   delete(True);f.checked('원본 구현삭제 버튼/취소와 modal 정리는 460px 정보 카드·함수 선언·정확한 값·본문 파일을 보존한다')
   delete();f.owner().locator('[data-own-functions-toggle]').focus();after=mark();f.page.keyboard.press('Control+z');wait_result('browserRetirement',after);check(True);assert not f.state()['retirements'];f.owner().locator('[data-own-functions-toggle]').focus();after=mark();f.page.keyboard.press('Control+y');dialog=f.page.get_by_role('dialog',name='구현 삭제',exact=True);expect(dialog).to_be_visible();wait_result('planBrowserRemoval',after);dialog.locator('[data-implementation-confirm]').click();wait_result('browserRetirement',after);expect(dialog).to_have_count(0);check(False);assert f.state()['retirements'][0]['mode']=='implementation-only-v1';f.checked('실제 Undo/Redo는 구현만 복구·새 명시삭제하며 함수 전체 삭제로 전환되지 않는다')
   restart(1);check(False);recover();restart(2);check(True);f.checked('기존 Browser 복구 메뉴와 cold는 Fn 행/이름/핀을 유지하고 provider와 원래 본문만 복원한다')
   delete();r=review();r.locator('[data-reject]').click();f.originals();r=review();accept(r);assert fnpath.read_bytes()==fn_original;assert {name for name,value in f.original.items() if (f.project/name).read_bytes()!=value}=={'FreeInfo.celem','project.cproj'};f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts};restart(3);check(False);recover();f.owner().locator('[data-element-action=discard]').click();f.idle();check(False);recover();r=review();accept(r);assert all((f.project/name).read_bytes()==value for name,value in initial.items());f.original=dict(initial);check(True);f.checked('삭제/복구 Review취소·Confirm·cold·복구취소후재복구는 선언/원문/다른 target을 그대로 보존한다')
  elif mode=='storage':
   before=checkpoint.read_bytes();after=mark();method().locator('[data-function-delete-implementation]').click();dialog=f.page.get_by_role('dialog',name='구현 삭제',exact=True);expect(dialog).to_be_visible();f.page.screenshot(path=str(f.case/'implementation-only-modal.png'));wait_result('planBrowserRemoval',after);checkpoint.chmod(0o400)
   try:
    after=mark();dialog.locator('[data-implementation-confirm]').click();wait_result('browserRetirement',after,False);f.idle();expect(f.page.locator('#status')).to_contain_text('[archive-unapplied]');assert checkpoint.read_bytes()==before and not f.state()['retirements'];assert fnpath.read_bytes()==fn_original;expect(dialog.locator('[data-implementation-confirm]')).to_be_enabled()
   finally:checkpoint.chmod(0o600)
   after=mark();dialog.locator('[data-implementation-confirm]').click();wait_result('browserRetirement',after);expect(dialog).to_have_count(0);check(False);f.checked('화면의 실제 쓰기 실패는 선언/구현/checkpoint를 보존하고 결과 조회 뒤 같은 명시 요청으로만 재시도한다')
  elif mode=='conflict':
   before=checkpoint.read_bytes();after=mark();method().locator('[data-function-delete-implementation]').click();dialog=f.page.get_by_role('dialog',name='구현 삭제',exact=True);expect(dialog).to_be_visible();wait_result('planBrowserRemoval',after);state=f.state();source=next(v['schema'] for v in state['editorViews'] if v['view']=='1') if d.is_view else state['schema'];f.invoke('editViewDescription' if d.is_view else 'editDescription',{'id':owner,'revision':source['revision'],'hash':source['textHash'],'value':'계획 뒤 peer 원문 보존',**({'view':'1'} if d.is_view else {})});after=mark();dialog.locator('[data-implementation-confirm]').click();wait_result('browserRetirement',after,False);expect(f.page.locator('#status')).to_contain_text('[archive-outcome]');f.idle();assert checkpoint.read_bytes()==before and not f.state()['retirements'];assert fnpath.read_bytes()==fn_original;dialog.locator('[data-implementation-cancel]').click();expect(dialog).to_have_count(0);check(True);state=f.state();source=next(v['schema'] for v in state['editorViews'] if v['view']=='1') if d.is_view else state['schema'];assert source['description']=='계획 뒤 peer 원문 보존';f.checked('실제 계획 뒤 source 경합은 선언·구현·checkpoint를 부분 적용하지 않고 peer 원문과 실패 근거를 보존한다')
  elif mode in ['loss','loss-cold']:
   mutations={};lost=[];queries=[]
   def intercept(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke':
     if body.get('endpoint')=='browserRetirement':mutations[body['requestId']]=body['input']['action']
     if body.get('endpoint')=='browserArchiveOutcome':queries.append(body['requestId'])
    if body.get('op')=='update':
     response=route.fetch();payload=response.json()
     for row in payload.get('results',[]):
      rid=row['requestId']
      if row.get('ok') and (rid in mutations and rid not in lost or mode=='loss-cold' and rid in queries):lost.append(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport_lost'})
     route.fulfill(response=response,json=payload);return
    route.fallback()
   f.page.route('**/api/request',intercept);after=mark();method().locator('[data-function-delete-implementation]').click();dialog=f.page.get_by_role('dialog',name='구현 삭제',exact=True);expect(dialog).to_be_visible();wait_result('planBrowserRemoval',after);dialog.locator('[data-implementation-confirm]').click()
   if mode=='loss':wait_result('browserArchiveOutcome',after);expect(dialog).to_have_count(0);check(False)
   else:
    expect(f.page.locator('#status')).to_contain_text('[archive-outcome]',timeout=60000);f.idle();assert queries and any(r in queries for r in lost);held=[(k,v) for k,v in f.pending()['blueprint'] if v.get('kind')=='information-retirement'];assert held;dialog.locator('[data-implementation-cancel]').click();expect(dialog).to_have_count(0);f.page.unroute_all(behavior='wait');restart(1);check(False);assert [(k,v) for k,v in f.pending()['blueprint'] if v.get('kind')=='information-retirement']==held;recover();assert not [(k,v) for k,v in f.pending()['blueprint'] if v.get('kind')=='information-retirement']
   assert list(mutations.values()).count('apply')==1;f.checked('실제 성공 응답'+('·결과 조회 유실/cold' if mode=='loss-cold' else ' 유실')+'은 source/입력을 보존하고 readonly 완료 조회로 복구하며 apply를 중복하지 않는다')
  elif mode=='guards':
   f.page.locator('#workspace').click(button='right',position={'x':80,'y':100});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=info]').click();b.locator('[data-browser-control="object-query"]').fill('FreeInfo');b.locator('[data-browser-control="object-search"]').click();b.locator('[data-object="'+owner+'"]').click(button='right');f.page.locator('.context-menu').get_by_role('button',name='새 창으로 열기',exact=True).click();peer=f.page.locator('.window[data-key=editor-'+('2' if d.is_view else '1')+']');expect(peer.locator('.object-title-name')).to_have_text('FreeInfo');b.locator('[data-close]').first.click();head=peer.locator('.object-title-name').bounding_box();box=peer.bounding_box();f.page.mouse.move(head['x']+5,head['y']+5);f.page.mouse.down();f.page.mouse.move(1650+head['x']-box['x']+5,100+head['y']-box['y']+5,steps=10);f.page.mouse.up();peer.locator('.object-title-description').fill('다른 창 원문 보존');peer.get_by_label('Power 기본값',exact=True).fill('9223372036854775804');held=f.pending();before=checkpoint.read_bytes();after=mark();method().locator('[data-function-delete-implementation]').click();f.idle();expect(f.page.locator('#status')).to_contain_text('입력을 먼저');assert not f.page.get_by_role('dialog',name='구현 삭제',exact=True).count();assert checkpoint.read_bytes()==before and f.pending()==held;expect(peer.get_by_label('Power 기본값',exact=True)).to_have_value('9223372036854775804');assert not any(r.get('invoke',{}).get('endpoint')=='planBrowserRemoval' for r in f.traffic[after:]);check(True);restart(1);assert f.pending()==held;f.checked('같은 정보의 다른 창 원문/exact64 입력은 삭제 계획 전에 거절·보존하며 cold 후에도 유지된다')
  elif mode=='projects':
   a=f.state();alist=a['listingId'];saved_a=checkpoint.read_bytes();broot=f.case/'other root'/'owned project';shutil.copytree(f.project,broot,ignore=shutil.ignore_patterns('.confectory'));original_b={str(p.relative_to(broot)):p.read_bytes() for p in broot.rglob('*') if p.is_file()};f.pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(broot/'project.cproj');f.start(1);f.invoke('select',{'id':f.id});f.invoke('saveDraft',{});bstate=f.state();blist=bstate['listingId'];assert a['projectId']!=bstate['projectId'];bcheckpoint=next(broot.glob('.confectory/edit-workspaces/*/draft.json'));saved_b=bcheckpoint.read_bytes();f.page=f.setup();f.page.set_viewport_size({'width':2100,'height':1450})
   def enter(listing):
    f.page.locator('.brand').click();expect(f.page.locator('.home-grid')).to_be_visible();f.page.locator('[data-enter="'+listing+'"]').click();expect(f.page.locator('.work-body')).to_be_visible();f.idle()
   enter(alist);check(True);method().locator('[data-function-delete-implementation]').evaluate('el=>globalThis.retiredImplementationDelete=el.onclick');enter(blist);d.open_info();after=mark();f.page.evaluate('async()=>await retiredImplementationDelete()');f.idle();assert not f.page.get_by_role('dialog',name='구현 삭제',exact=True).count();assert checkpoint.read_bytes()==saved_a and bcheckpoint.read_bytes()==saved_b;assert not any(r.get('invoke',{}).get('endpoint') in ['planBrowserRemoval','browserRetirement'] for r in f.traffic[after:]);check(True);delete();assert checkpoint.read_bytes()==saved_a;assert all((broot/path).read_bytes()==value for path,value in original_b.items());enter(alist);check(True);enter(blist);check(False);f.checked('실제 A/B 같은 namespace와 Fn ID의 전환은 은퇴 callback을 거절하고 B 명시 삭제만 B checkpoint에 보관한다')
  else:raise AssertionError(mode)
  f.page.screenshot(path=str(f.case/'implementation-retirement-ui.png'));assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
 print(json.dumps({'checks':f.checks,'mode':mode,'view':d.is_view,'evidence':str(f.case),'actualEngineRenderer':True,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
except Exception:
 try:(f.case/'implementation-retirement-ui-failure.json').write_text(json.dumps({'state':f.state(),'traffic':f.traffic[-100:],'checks':f.checks,'errors':f.errors},ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'implementation-retirement-ui-failure.png'))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
