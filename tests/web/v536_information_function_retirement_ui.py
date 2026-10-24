"""Existing v536 own-function delete/recovery controls, isolated engine/Chromium/compiler."""
import json,time,sys,re,shutil
from playwright.sync_api import sync_playwright,expect
import v536_field_definitions_ui as d
f=d.f;owner=d.owner;mode=sys.argv[3] if len(sys.argv)>3 else 'normal';fn=owner+'_Function_'+'c'*32

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
 raise AssertionError({'endpoint':endpoint,'status':f.page.locator('#status').inner_text(),'elementError':f.owner().locator('[data-element-error]').all_text_contents(),'evidence':str(f.case)})
def deleted():expect(method()).to_have_count(0);f.idle();assert not f.page.locator('#app').evaluate('e=>e.inert');f.originals()
def present():expect(method()).to_be_visible();f.idle();f.originals();expect(f.owner().get_by_label('Power 기본값',exact=True)).to_have_value('9223372036854775806')
def delete(cancel=False):
 f.idle();after=mark();method().locator('[data-function-delete]').click();dialog=f.page.get_by_role('dialog',name='의미 객체 삭제',exact=True);expect(dialog).to_be_visible();wait_result('planBrowserRemoval',after);assert not f.state()['retirements'];f.originals()
 if cancel:dialog.get_by_role('button',name='닫기',exact=True).click();present();return
 after=mark();dialog.locator('#delete-object').click();wait_result('browserArchiveOutcome' if mode=='loss' else 'browserRetirement',after);expect(dialog).to_have_count(0);deleted()
def recover_menu():
 f.idle();f.page.locator('#workspace').click(button='right',position={'x':80,'y':100});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-browser-control="browser-actions"]').click();f.page.get_by_role('button',name='삭제 항목 복구',exact=True).click();after=mark();f.page.get_by_role('button',name='화면에서 복구할 함수',exact=True).click();wait_result('browserArchiveOutcome' if mode=='loss' else 'browserRetirement',after);f.idle();b.locator('[data-close]').first.click();present()
def restart(i):
 f.pending();f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1850,'height':1450});expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo');f.idle()
def enter(listing):
 f.page.locator('.brand').click();expect(f.page.locator('.home-grid')).to_be_visible();f.page.locator('[data-enter="'+listing+'"]').click();expect(f.page.locator('.work-body')).to_be_visible();expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo');f.idle()
def review():return d.review()
def accept(r):
 if r.locator('[data-review-advanced]').count():
  r.locator('[data-review-advanced]').click()
  if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
 after=mark();r.locator('#confirm').click();assert wait_result('confirmGroup',after)['result']['sourceConfirmed'];expect(r).to_have_count(0);f.idle()
try:
 f.start(0);f.invoke('select',{'id':owner});s=schema();p=rpc('readOwnerEdits',id=owner,hash=s['textHash']);rpc('applySlots',id=owner,rows=[],basis=p['basis'],declaration={'id':owner,'hash':s['textHash'],'changes':[{'type':'function-add','id':fn,'name':'화면에서 복구할 함수','description':'원문 보존'}]});s=schema();method_data=next(row for row in s['ownFunctions'] if row['id']==fn);p=rpc('readFeature',id=fn,hash=method_data['hash'],revision=method_data['revision'],owner=owner,ownerHash=s['textHash'],ownerRevision=s['revision']);created=rpc('createFeature',id=fn,basis=p['basis']);s=schema();g=rpc('read',id=created['id'],owner=owner,ownerHash=s['textHash'],ownerRevision=s['revision']);rpc('source',id=created['id'],basis=g['basis'],node='body',text='return; // UI fixture valid body');f.invoke('saveDraft',{});schema()
 if mode!='pending':
  ids=f.state()['draft']['creationReviewIds'];f.invoke('reviewGroup',{'ids':ids,'target':'portable'});r=f.state()['review'];assert r['status']=='ready';assert f.invoke('confirmGroup',{'ids':ids,'token':r['token']})['result']['result']['sourceConfirmed']
 f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts};initial_sources=dict(f.original);checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1850,'height':1450});d.open_info();present();assert abs(f.owner().bounding_box()['width']-460)<1;before=method().locator('[data-function-delete]').bounding_box();f.page.screenshot(path=str(f.case/'function-before-delete.png'))
  if mode in ['normal','pending']:
   delete(True);f.checked('기존 460px 정보 카드의 삭제 X는 기존 확인창을 열며 닫기/취소는 함수·본문·정확한 값을 보존하고 inert를 정리한다')
   delete();saved=checkpoint.read_bytes();f.owner().locator('[data-own-functions-toggle]').focus();after=mark();f.page.keyboard.press('Control+z');wait_result('browserRetirement',after);present();assert not f.state()['retirements'];f.owner().locator('[data-own-functions-toggle]').focus();after=mark();f.page.keyboard.press('Control+y');dialog=f.page.get_by_role('dialog',name='의미 객체 삭제',exact=True);expect(dialog).to_be_visible();wait_result('planBrowserRemoval',after);dialog.locator('#delete-object').click();wait_result('browserRetirement',after);expect(dialog).to_have_count(0);deleted();f.checked('삭제 Undo는 archive 복구를 쓰며 Redo는 새 계획/명시적 삭제를 요구하고 함수 전체를 함께 저장한다')
   expect(f.owner().locator('[data-element-action=discard]')).to_be_enabled();after=mark();f.owner().locator('[data-element-action=discard]').click();wait_result('browserRetirement',after);present();assert not f.state()['retirements'];f.checked('정보 변경 취소는 저장된 pending 삭제도 원자적으로 복구하고 별도 함수·본문 파일을 쓰지 않는다')
   delete();restart(1);deleted();recover_menu();restart(2);present();assert not f.state()['retirements'];f.checked('기존 Browser 복구 메뉴는 이름을 표시하며 삭제/복구 cold와 재진입에 원문·입력·상태를 복원한다')
   if mode=='pending':
    r=review();r.locator('[data-reject]').click();f.originals();r=review();accept(r);assert (f.project/('elements/'+fn.split('::')[1]+'.celem')).exists();f.checked('미확정 생성 함수도 UI 삭제·복구·Review 취소 뒤 새 명시적 Confirm으로만 함수/본문을 생성한다')
   else:
    delete();r=review();r.locator('[data-reject]').click();f.originals();r=review();accept(r);assert f.state()['retirements'][0]['state']=='confirmed';assert {name for name,value in f.original.items() if (f.project/name).read_bytes()!=value}=={'FreeInfo.celem','project.cproj'};f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts};restart(3);recover_menu();assert f.state()['retirements'][0]['state']=='restoring';after=mark();f.owner().locator('[data-element-action=discard]').click();wait_result('browserRetirement',after);deleted();recover_menu();r=review();accept(r);assert all((f.project/name).read_bytes()==value for name,value in initial_sources.items());f.original=dict(initial_sources);present();assert not f.state()['retirements'];f.checked('확정 삭제는 원본 파일을 보관하며 cold 복구·복구취소·재복구 뒤 별도 전체 Review/Confirm으로만 등록을 복원한다')
  elif mode=='storage':
   before_checkpoint=checkpoint.read_bytes();after=mark();method().locator('[data-function-delete]').click();dialog=f.page.get_by_role('dialog',name='의미 객체 삭제',exact=True);expect(dialog).to_be_visible();wait_result('planBrowserRemoval',after);checkpoint.chmod(0o400)
   try:
    after=mark();dialog.locator('#delete-object').click();wait_result('browserRetirement',after,False);f.idle();expect(f.page.locator('#status')).to_contain_text('[archive-unapplied]');assert checkpoint.read_bytes()==before_checkpoint;assert not f.state()['retirements'];present();expect(dialog.locator('#delete-object')).to_be_enabled()
   finally:checkpoint.chmod(0o600)
   after=mark();dialog.locator('#delete-object').click();wait_result('browserRetirement',after);expect(dialog).to_have_count(0);deleted();f.checked('실제 쓰기 거절은 live/disk 모두 미적용하고 읽기 결과조회 후 같은 창의 명시적 재시도만 허용한다')
  elif mode=='projects':
   a=f.state();alist=a['listingId'];saved_a=checkpoint.read_bytes();b_root=f.case/'other root'/'owned project';shutil.copytree(f.project,b_root,ignore=shutil.ignore_patterns('.confectory'));original_b={str(p.relative_to(b_root)):p.read_bytes() for p in b_root.rglob('*') if p.is_file()};f.pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(b_root/'project.cproj');f.start(1);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});f.page=f.setup();f.page.set_viewport_size({'width':1850,'height':1450});d.open_info();bstate=f.state();blist=bstate['listingId'];assert a['projectId']!=bstate['projectId'];checkpoint_b=next(b_root.glob('.confectory/edit-workspaces/*/draft.json'));saved_b=checkpoint_b.read_bytes();enter(alist);method().locator('[data-function-delete]').evaluate('el=>globalThis.retiredInformationDelete=el.onclick');enter(blist);after=mark();f.page.evaluate('async()=>await retiredInformationDelete()');f.idle();assert not f.page.get_by_role('dialog',name='의미 객체 삭제',exact=True).count();assert checkpoint.read_bytes()==saved_a and checkpoint_b.read_bytes()==saved_b;assert not any(r.get('invoke',{}).get('endpoint') in ['planBrowserRemoval','browserRetirement'] for r in f.traffic[after:]);present();f.checked('같은 native 정보/함수 ID를 가진 A→B 전환 뒤 은퇴한 삭제 callback은 현재 프로젝트의 삭제 계획이나 거래를 만들지 않는다')
   delete();assert checkpoint.read_bytes()==saved_a;assert all((b_root/name).read_bytes()==value for name,value in original_b.items());enter(alist);present();assert not f.state()['retirements'];enter(blist);deleted();assert f.state()['retirements'][0]['owner']==owner;f.originals();f.checked('실제 Home 프로젝트 전환 후 B의 명시 삭제는 B checkpoint에만 보관되며 A 함수·등록·입력과 두 프로젝트 최종 소스를 보존한다')
  elif mode=='guards':
   f.page.locator('#workspace').click(button='right',position={'x':80,'y':100});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=info]').click();b.locator('[data-browser-control="object-query"]').fill('FreeInfo');b.locator('[data-browser-control="object-search"]').click();b.locator('[data-object="'+owner+'"]').click(button='right');f.page.locator('.context-menu').get_by_role('button',name='새 창으로 열기',exact=True).click();peer=f.page.locator('.window[data-key=editor-1]');expect(peer.locator('.object-title-name')).to_have_text('FreeInfo');b.locator('[data-close]').first.click();head=peer.locator('.object-title-name').bounding_box();box=peer.bounding_box();f.page.mouse.move(head['x']+5,head['y']+5);f.page.mouse.down();f.page.mouse.move(1300+head['x']-box['x']+5,120+head['y']-box['y']+5,steps=10);f.page.mouse.up();peer.locator('.object-title-description').fill('같은 정보 다른 창 입력');peer.get_by_label('Power 기본값',exact=True).fill('9223372036854775804');held=f.pending();saved=checkpoint.read_bytes();after=mark();method().locator('[data-function-delete]').click();f.idle();expect(f.page.locator('#status')).to_contain_text('입력을 먼저');assert not f.page.get_by_role('dialog',name='의미 객체 삭제',exact=True).count();assert checkpoint.read_bytes()==saved and f.pending()==held;expect(peer.get_by_label('Power 기본값',exact=True)).to_have_value('9223372036854775804');assert not any(r.get('invoke',{}).get('endpoint') in ['planBrowserRemoval','browserRetirement'] for r in f.traffic[after:]);present();restart(1);assert f.pending()==held;f.checked('같은 정보의 독립 창 미적용 설명·exact64 입력은 삭제 전에 차단·보존하고 cold 후에도 복원한다')
  elif mode in ['loss','loss-cold']:

   targets={};lost=[];queries=[]
   def intercept(route):
    body=route.request.post_data_json if route.request.method=='POST' else None
    if isinstance(body,dict) and body.get('op')=='invoke':
     if body.get('endpoint')=='browserRetirement':targets[body['requestId']]=body['input']['action']
     if body.get('endpoint')=='browserArchiveOutcome':queries.append(body['input']['action'])
    if isinstance(body,dict) and body.get('op')=='update':
     response=route.fetch();data=response.json();changed=False
     for row in data.get('results',[]):
      if mode=='loss-cold' and row.get('ok') and isinstance(row.get('result'),dict) and 'settled' in row['result'] and 'unapplied' not in row['result']:row.pop('result');row['ok']=False;row['error']={'code':'transport_lost'};changed=True;continue
      if row.get('ok') and row.get('requestId') in targets and row['requestId'] not in lost:lost.append(row['requestId']);row.clear();row.update({'requestId':lost[-1],'ok':False,'error':{'code':'transport_lost'}});changed=True
     if changed:route.fulfill(response=response,json=data);return
     route.fulfill(response=response);return
    route.fallback()
   f.page.route('**/api/request',intercept)
   if mode=='loss-cold':
    after=mark();method().locator('[data-function-delete]').click();dialog=f.page.get_by_role('dialog',name='의미 객체 삭제',exact=True);expect(dialog).to_be_visible();wait_result('planBrowserRemoval',after);after=mark();dialog.locator('#delete-object').click();wait_result('browserArchiveOutcome',after,False);f.idle();expect(f.page.locator('#status')).to_contain_text('[archive-outcome]');held=f.pending();assert len([v for _,v in held['blueprint'] if v.get('kind')=='information-retirement'])==1;dialog.get_by_role('button',name='닫기',exact=True).click();assert len(targets)==1 and len(lost)==1;restart(1);deleted();assert f.pending()==held;after=mark();recover_menu();assert any(r.get('invoke',{}).get('endpoint')=='browserArchiveOutcome' for r in f.traffic[after:]);assert not [v for _,v in f.pending()['blueprint'] if v.get('kind')=='information-retirement'];present();f.checked('응답과 결과 조회가 함께 유실되면 journal을 cold까지 보관하고 기존 Browser 복구 때 이전 결과를 읽어 확인한 후 다음 명시적 거래만 적용한다')
   else:
    delete();saved=checkpoint.read_bytes();recover_menu();present();assert not f.state()['retirements'];assert len(targets)==2 and len(lost)==2 and queries==['apply','recover'];f.pending();assert not [v for _,v in f.pending()['blueprint'] if v.get('kind')=='information-retirement'];restart(1);present();f.checked('실제 renderer의 apply/recover 응답 유실은 durable 읽기 조회로 확인하고 mutation 재전송 없이 cold에서도 한 번만 복구한다')
  f.page.screenshot(path=str(f.case/'function-after-recovery.png'));assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
 print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
except Exception:
 try:(f.case/'information-retirement-ui-failure.json').write_text(json.dumps({'state':f.state(),'traffic':f.traffic[-100:],'errors':f.errors,'checks':f.checks},ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'information-retirement-ui-failure.png'))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
