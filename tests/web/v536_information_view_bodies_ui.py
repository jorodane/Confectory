"""Detached own-function body UI over actual engine; fixtures only, no provider/run."""
import json,re,time,sys,shutil
from playwright.sync_api import sync_playwright,expect
import v536_field_definitions_ui as d
f=d.f;owner=d.owner;fn=owner+'_Function_'+'e'*32;mode=sys.argv[3] if len(sys.argv)>3 else 'normal'

def rpc(action,**args):return f.invoke('blueprint',{'action':action,**args})['result']['result']
def method():return f.owner().locator('[data-inline-method="'+fn+'"]')
def primary():
 s=f.state();assert s['draft']['id']==f.id and s['draft']['text']==primary_text;f.originals()
 if f.page and not f.page.is_closed():expect(f.page.locator('.window[data-key=schema] .object-title-description')).to_have_value('primary 입력 보존')
def open_body():
 f.idle();method().locator('[data-function-write-direct],[data-function-edit]').click();expect(f.author().locator('[data-bp-node=body]')).to_be_visible();expect(f.author()).to_have_attribute('data-blueprint-view','1');expect(f.author().locator('[data-bp-name]')).to_have_value('독립 창 자체 본문');f.idle();primary()
def script(text=None,accept=True,undo=False):
 f.author().locator(':scope>.window-title .caption').click(position={'x':5,'y':5});f.author().locator('[data-bp-overview-node=body]').click();f.author().locator('[data-bp-node=body] [data-internal-code]').click();dialog=f.page.locator('.bp-script-dialog');value=dialog.locator('[data-code-source]');expect(value).to_be_visible();before=value.input_value()
 if text is not None:value.evaluate(r'''el=>{el.focus();const a=el.value.indexOf('\n{\n')+3,b=el.value.lastIndexOf('\n}');if(a<3||b<a)throw Error('protected body range');el.setSelectionRange(a,b);}''');f.page.keyboard.insert_text(text)
 if undo:
  f.page.keyboard.press('Control+z');expect(value).to_have_value(before);f.page.keyboard.press('Control+y');assert text in value.input_value()
 dialog.locator('[data-code-save]' if accept else '[data-code-cancel]').click();expect(dialog).to_have_count(0);return before
def author_inputs():return [(k,v) for k,v in f.pending()['blueprint'] if '|v508-author|view:1|'+fn+'|' in k]
def save():
 f.author().locator('[data-bp-save]').click();expect(f.author().locator('.bp-status')).to_have_text('저장됨',timeout=60000);f.idle();assert not author_inputs();assert not [v for k,v in f.pending()['blueprint'] if '|v508-author-attempt|view:1|' in k];primary()

def restart(i):
 held=f.pending();f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':2100,'height':1450});f.owner=lambda:f.page.locator('.window[data-key=editor-1]');expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo');f.idle();return held
def review():
 f.author().locator('[data-bp-complete]').click();r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible();return r
def accept(r):
 if r.locator('[data-review-advanced]').count():
  r.locator('[data-review-advanced]').click()
  if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
 mark=len(f.traffic);r.locator('#confirm').click();expect(r).to_have_count(0,timeout=120000);f.idle();assert any(row.get('result',{}).get('result',{}).get('sourceConfirmed') is True for row in f.traffic[mark:])
def boundary(checkpoint):
 held=author_inputs();before=checkpoint.read_bytes();mark=len(f.traffic)
 if mode=='context':
  a=f.state();alist=a['listingId'];broot=f.case/'other root'/'owned project';shutil.copytree(f.project,broot,ignore=shutil.ignore_patterns('.confectory'));bfiles={str(p.relative_to(broot)):p.read_bytes() for p in broot.rglob('*') if p.is_file()};f.pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(broot/'project.cproj');f.start(3);f.invoke('select',{'id':f.id});f.invoke('saveDraft',{});b=f.state();blist=b['listingId'];assert a['projectId']!=b['projectId'];bcheckpoint=next(broot.glob('.confectory/edit-workspaces/*/draft.json'));bsaved=bcheckpoint.read_bytes();f.page=f.setup();f.page.set_viewport_size({'width':2100,'height':1450})
  def enter(listing):
   f.page.locator('.brand').click();expect(f.page.locator('.home-grid')).to_be_visible();f.page.locator('[data-enter="'+listing+'"]').click();expect(f.page.locator('.work-body')).to_be_visible();f.idle()
  enter(alist);expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo');open_body();assert author_inputs()==held;f.author().locator('[data-bp-save]').evaluate('el=>globalThis.retiredViewBodySave=el.onclick');enter(blist);mark=len(f.traffic);f.page.evaluate('async()=>await retiredViewBodySave()');f.idle();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for r in f.traffic[mark:]);assert checkpoint.read_bytes()==before and bcheckpoint.read_bytes()==bsaved;assert all((broot/path).read_bytes()==value for path,value in bfiles.items());enter(alist);open_body();assert author_inputs()==held;assert '독립 창 미저장 한글' in script(None,False);save();assert checkpoint.read_bytes()!=before and bcheckpoint.read_bytes()==bsaved;primary();f.checked('실제 Home A→B→A 전환은 독립 본문/primary 입력을 복원하고 은퇴한 A 저장 callback은 B에 후보·checkpoint를 만들지 않는다')
 elif mode=='storage':
  checkpoint.chmod(0o400)
  try:
   f.author().locator('[data-bp-save]').click();expect(f.author().locator('.bp-status')).to_contain_text('입력',timeout=60000);f.idle();assert checkpoint.read_bytes()==before and author_inputs()==held;primary()
  finally:checkpoint.chmod(0o600)
  restart(3);open_body();assert author_inputs()==held;save();assert checkpoint.read_bytes()!=before;primary();f.checked('실제 checkpoint 쓰기 거절/cold 뒤 명시 재시도는 본문 입력·primary 입력을 보존하고 전체 저장만 허용한다')
 elif mode=='loss':
  applies=set();queries=set();lost=[]
  def intercept(route):
   body=route.request.post_data_json
   if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
    action=body.get('input',{}).get('action')
    if action=='authorBatch':applies.add(body['requestId'])
    if applies and action=='settledAuthorBatch':queries.add(body['requestId'])
   response=route.fetch();payload=response.json()
   for row in payload.get('results',[]):
    if row['requestId'] in applies|queries:rid=row['requestId'];lost.append(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
   route.fulfill(response=response,json=payload)
  f.page.route('**/api/request',intercept);f.author().locator('[data-bp-save]').click();expect(f.author().locator('.bp-status')).to_have_text('transport-interrupted',timeout=60000);f.idle();assert len(applies)==1 and queries.intersection(lost);assert checkpoint.read_bytes()!=before;assert author_inputs()==held;primary();f.page.unroute_all(behavior='wait');restart(3);open_body();mark=len(f.traffic);save();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for r in f.traffic[mark:]);primary();f.checked('저장 응답·결과 조회 유실/cold는 surface receipt 재조회로만 복구하고 중복 저장이나 입력 유실이 없다')
 elif mode=='conflict':
  row=next(v for v in f.state()['editorViews'] if v['view']=='1');s=row['schema'];args={'owner':owner,'ownerHash':s['textHash'],'ownerRevision':s['revision']};graph=fn+'BlueprintBody/body:common';peer=rpc('read',id=graph,**args);rpc('source',id=graph,basis=peer['basis'],node='body',text='return; // peer body conflict',**args);f.invoke('saveDraft',{});before=checkpoint.read_bytes();f.author().locator('[data-bp-save]').click();expect(f.author().locator('.bp-status')).to_contain_text('입력',timeout=60000);f.idle();assert checkpoint.read_bytes()==before and author_inputs()==held;primary();restart(3);open_body();assert author_inputs()==held;f.author().locator('[data-bp-save]').click();expect(f.author().locator('.bp-status')).to_contain_text('입력',timeout=60000);f.idle();assert checkpoint.read_bytes()==before and author_inputs()==held;primary();f.checked('실제 peer 본문 변경은 전체 Save를 거절하고 cold 재시도에서도 원래 근거·입력·checkpoint를 보존한다')
 else:raise AssertionError(mode)
 assert not f.errors and not f.external,(f.errors,f.external)
 f.page.screenshot(path=str(f.case/('information-view-body-'+mode+'.png')))
try:
 assert d.is_view,'pass view after the scenario argument';f.start(0);f.invoke('select',{'id':owner});f.invoke('schema',{'id':owner});s=f.state()['schema'];b=rpc('readOwnerEdits',id=owner,hash=s['textHash']);rpc('applySlots',id=owner,rows=[],basis=b['basis'],declaration={'id':owner,'hash':s['textHash'],'changes':[{'type':'function-add','id':fn,'name':'독립 창 자체 본문','description':'동일 함수의 창별 입력'}]});f.invoke('saveDraft',{});f.invoke('select',{'id':f.id});f.invoke('schema',{'id':f.id});primary_text=f.state()['draft']['text']
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2100,'height':1450});f.open_owner(f.id);d.open_info();head=f.owner().locator('.object-title-name').bounding_box();box=f.owner().bounding_box();f.page.mouse.move(head['x']+5,head['y']+5);f.page.mouse.down();f.page.mouse.move(1300+head['x']-box['x']+5,130+head['y']-box['y']+5,steps=10);f.page.mouse.up();main=f.page.locator('.window[data-key=schema]');main.locator('.object-title-description').fill('primary 입력 보존');held_primary=[(k,v) for k,v in f.pending()['schema'] if '|'+f.id+'|element|' in k];assert held_primary;open_body();checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();assert f.state()['draft']['id']==f.id;assert abs(f.owner().bounding_box()['width']-460)<1;f.checked('기존 독립 정보 카드의 직접 작성은 bound view에서 첫 구현/graph/node를 저장하고 다른 primary 선택·미저장 설명을 유지한다')
  script('return; // 취소할 내용',False);assert not author_inputs();assert checkpoint.read_bytes()==before;primary();script('return; // 독립 창 미저장 한글 😀');held=author_inputs();assert held;assert all('|view:1|' in k for k,_ in held);f.close_author();restart(1);assert author_inputs()==held;assert [(k,v) for k,v in f.pending()['schema'] if '|'+f.id+'|element|' in k]==held_primary;open_body();assert '독립 창 미저장 한글' in script();f.checked('C# 취소와 독립 창 닫기/cold는 view별 본문 입력·원래 source proof·다른 창 설명을 보존한다')
  if mode!='normal':
   boundary(checkpoint);f.browser.close();print(json.dumps({'checks':f.checks,'mode':mode,'evidence':str(f.case),'actualEngine':True,'renderer':True,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False));sys.exit(0)
  save();saved=checkpoint.read_bytes();f.close_author();restart(2);open_body();assert '독립 창 미저장 한글' in script();assert checkpoint.read_bytes()==saved;f.checked('독립 창 source/설명 Save는 해당 surface receipt와 한 checkpoint CAS를 쓰며 cold 재진입과 primary 입력을 보존한다')
  r=review();r.locator('[data-reject]').click();primary();r=review();accept(r);assert (f.project/('elements/'+fn.split('::')[1]+'.celem')).exists();assert all((f.project/name).read_bytes()==value for name,value in f.original.items() if name not in ['FreeInfo.celem','project.cproj']);assert f.state()['draft']['id']==f.id;expect(f.page.locator('.window[data-key=schema] .object-title-description')).to_have_value('primary 입력 보존');f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts};f.checked('독립 본문의 기능 완성은 명시적 전체 Review/Confirm을 요구하며 unrelated primary 입력과 최종 소스를 변경하지 않는다')
  script('return; // 같은 창 확정 후',undo=True);save();primary();f.page.screenshot(path=str(f.case/'information-view-body.png'));assert not f.errors and not f.external,(f.errors,f.external);f.checked('같은 독립 본문 창에서 확정 후 재편집도 새 checkpoint로 저장하고 최종 source는 새 Confirm 전까지 유지한다');f.browser.close()
 print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
except Exception:
 try:(f.case/'information-view-body-ui-failure.json').write_text(json.dumps({'state':f.state(),'traffic':f.traffic[-100:],'errors':f.errors,'checks':f.checks},ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'information-view-body-ui-failure.png'))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
