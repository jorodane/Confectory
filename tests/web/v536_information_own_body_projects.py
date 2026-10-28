"""Same native IDs in distinct real projects keep independent own-function body intent and storage."""
import json,shutil,time
from playwright.sync_api import sync_playwright,expect
import v536_field_definitions_ui as d
f=d.f;owner=d.owner;fn=owner+'_Function_'+'8'*32
b_root=f.case/'other root'/'owned project'
def method():return f.owner().locator('[data-inline-method="'+fn+'"]')
def script(text=None):
 f.author().locator(':scope>.window-title .caption').click(position={'x':5,'y':5});f.author().locator('[data-bp-overview-node=body]').click();f.author().locator('[data-bp-node=body] [data-internal-code]').click();dialog=f.page.locator('.bp-script-dialog');value=dialog.locator('[data-code-source]');actual=value.input_value()
 if text is not None:value.evaluate(r'''el=>{el.focus();el.setSelectionRange(el.value.indexOf('\n{\n')+3,el.value.lastIndexOf('\n}'));}''');f.page.keyboard.insert_text(text)
 dialog.locator('[data-code-save]' if text is not None else '[data-code-cancel]').click();return actual

def open_body():f.idle();method().locator('[data-function-write-direct],[data-function-edit]').click();expect(f.author().locator('[data-bp-node=body]')).to_be_visible();expect(f.author().locator('[data-bp-name]')).to_have_value('두 프로젝트');f.idle()
def save_body():
 f.author().locator('[data-bp-save]').click();f.idle();now=f.pending();assert not [v for k,v in now['blueprint'] if '|v508-author|' in k],{'status':f.author().locator('.bp-status').all_text_contents(),'inputs':now}

def enter(listing):
 f.page.locator('.brand').click();expect(f.page.locator('.home-grid')).to_be_visible();f.page.locator('[data-enter="'+listing+'"]').click();expect(f.page.locator('.work-body')).to_be_visible();expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo');f.idle()
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('schema',{'id':owner});s=f.state()['schema'];basis=f.invoke('blueprint',{'action':'readOwnerEdits','id':owner,'hash':s['textHash']})['result']['result']['basis'];f.invoke('blueprint',{'action':'applySlots','id':owner,'rows':[],'basis':basis,'declaration':{'id':owner,'hash':s['textHash'],'changes':[{'type':'function-add','id':fn,'name':'두 프로젝트','description':'문맥 보존'}]}});group=f.state()['draft']['creationReviewIds'];f.invoke('reviewGroup',{'ids':group,'target':'portable'});f.invoke('confirmGroup',{'ids':group,'token':f.state()['review']['token']});f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts};shutil.copytree(f.project,b_root,ignore=shutil.ignore_patterns('.confectory'));original_b={str(p.relative_to(b_root)):p.read_bytes() for p in b_root.rglob('*') if p.is_file()}
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1850,'height':1450});d.open_info();open_body();script('return; // project A private');f.close_author();a=f.state();alist=a['listingId'];held_a=f.pending();checkpoint_a=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before_a=checkpoint_a.read_bytes();method().locator('[data-function-edit]').evaluate('el=>globalThis.retiredOwnBody=el.onclick');f.originals()
  f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(b_root/'project.cproj');f.start(1);f.invoke('select',{'id':owner});f.page=f.setup();f.page.set_viewport_size({'width':1850,'height':1450});d.open_info();b=f.state();blist=b['listingId'];assert a['projectId']!=b['projectId'];open_body();assert 'project A private' not in script();script('return; // project B saved');save_body();f.close_author();checkpoint_b=next(b_root.glob('.confectory/edit-workspaces/*/draft.json'));saved_b=checkpoint_b.read_bytes();assert checkpoint_a.read_bytes()==before_a;f.checked('같은 native 함수/정보 ID의 다른 실제 프로젝트는 본문 private 입력과 전체 저장 checkpoint를 분리한다')
  enter(alist);assert f.pending()==held_a;method().locator('[data-function-edit]').evaluate('el=>globalThis.retiredOwnBody=el.onclick');enter(blist);mark=len(f.traffic);f.page.evaluate('async()=>await retiredOwnBody()');f.idle();assert checkpoint_a.read_bytes()==before_a and checkpoint_b.read_bytes()==saved_b;assert not any(r.get('invoke',{}).get('endpoint')=='blueprint' for r in f.traffic[mark:]);f.checked('A의 은퇴한 본문 열기 callback은 B 전환 후 구현/본문/저장이나 문맥을 바꾸지 않는다')
  enter(alist);open_body();assert 'project A private' in script() and 'project B saved' not in script();save_body();f.close_author();assert checkpoint_b.read_bytes()==saved_b;enter(blist);open_body();assert 'project B saved' in script() and 'project A private' not in script();f.close_author();f.originals();assert all((b_root/name).read_bytes()==value for name,value in original_b.items());f.checked('실제 Home A↔B 재진입과 A 저장은 각 본문/소유/입력을 보존하고 상대 checkpoint나 두 프로젝트의 최종 원본을 쓰지 않는다');assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except Exception:
 try:(f.case/'own-body-projects-failure.json').write_text(json.dumps({'state':f.state(),'traffic':f.traffic[-100:],'checks':f.checks,'errors':f.errors},ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'own-body-projects-failure.png'))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
