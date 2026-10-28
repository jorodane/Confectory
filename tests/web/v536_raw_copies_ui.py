"""Existing v536 properties/copy/source controls, actual isolated engine and renderer."""
import json,sys
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
import v536_wide_mixed as f
mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
def source():return f.page.locator('.window[data-key="editor-1"] [data-editor-source]')
def source_window():return f.page.locator('.window[data-key="editor-1"]')
def views():return [(k,v) for k,v in f.pending()['views'] if k.endswith('|1|'+f.id)]
def setup():
 page=f.browser.new_page(viewport={'width':2300,'height':1400});page.on('pageerror',lambda e:f.errors.append(str(e)));page.on('response',f.observe);page.route('**/*',f.route);goto_editor(page,f.url);return page
f.setup=setup

def restart(i):
 f.pending();f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(i);f.page=f.setup();expect(source()).to_be_visible(timeout=60000);expect(f.owner().locator('[aria-label="MP 기본값"]')).to_be_visible(timeout=60000);f.idle()
def saved():
 for _ in range(400):
  now=f.pending()
  if not any('|'+f.id+'|element|' in k for k,_ in now['schema']) and not now['blueprint'] and not now['views']:f.idle();return
  error=f.owner().locator('[data-element-error]').inner_text()
  if error:raise AssertionError(error)
  f.page.wait_for_timeout(100)
 raise AssertionError('raw+copy Save did not settle')
def retained(before):
 now=f.pending()
 for group in ['schema','blueprint','views']:
  assert all(dict(now[group]).get(k)==v for k,v in before[group]),group
 f.originals()
def reject():f.rejected_save()
def open_raw():
 f.invoke('openEditorView',{'view':'1','id':f.id,'viewMode':'source'});expect(source()).to_be_visible();w=source_window();h=w.locator('.caption').bounding_box();box=w.bounding_box();f.page.mouse.move(h['x']+5,h['y']+8);f.page.mouse.down();f.page.mouse.move(1500+h['x']-box['x']+5,180+h['y']-box['y']+8,steps=12);f.page.mouse.up();f.idle();base=source().input_value();raw=base.replace('{','{\n// raw 원문 한글 😀\n',1).replace('data MP=4;','data MP= // MP 정확한 값 주석\n4;')+'\n// raw 끝\n';source().fill(raw);return base,raw
try:
 f.start(0);f.invoke('select',{'id':f.id});f.invoke('saveDraft',{})
 with sync_playwright() as pw:
  f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();expect.set_options(timeout=60000);
  f.open_owner()
  if mode=='peer':
   f.invoke('openEditorView',{'view':'2','id':f.n+'Target1','viewMode':'properties'});other=f.page.locator('.window[data-key="editor-2"]');expect(other.locator('.object-title-description')).to_be_visible();head=other.locator('.object-title-name').bounding_box();box=other.bounding_box();f.page.mouse.move(head['x']+5,head['y']+8);f.page.mouse.down();f.page.mouse.move(1000+head['x']-box['x']+5,800+head['y']-box['y']+8,steps=12);f.page.mouse.up();other.locator('.object-title-description').fill('다른 창의 보관 입력');peer=[(k,v) for k,v in f.pending()['schema'] if '|'+f.n+'Target1|view:2|element|' in k];assert len(peer)==1
  f.edit_owner()
  if mode=='prior':
   base,raw=open_raw();original_checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json')).read_bytes();source().evaluate("el=>{el.focus();const i=el.value.lastIndexOf('}');el.setSelectionRange(i,i)}");f.page.keyboard.insert_text('description "raw 충돌 설명";\n');reject();assert next(f.project.glob('.confectory/edit-workspaces/*/draft.json')).read_bytes()==original_checkpoint and any(v.get('kind')=='raw-owner-attempt' for _,v in f.pending()['blueprint']);source().focus();f.page.keyboard.press('Control+z');expect(source()).to_have_value(raw);f.checked('raw/typed description conflict remains unapplied with its original journal; real Undo precedes explicit copy selection')
  f.select_copy('Slot','AliasBody','slotCount=amount+5;slotReady=true;return amount+70;',True);f.select_copy('Slot2','SlotBody2','slotCount=amount+9;slotReady=true;return amount+90;')
  if mode!='prior':base,raw=open_raw()
  held=f.pending();checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();assert len(views())==1 and len([v for _,v in held['blueprint'] if v.get('kind')=='copy-selection'])==2;f.originals();f.checked('original properties/structure/typed values and two actual edited copy bodies/wrapper coexist with separate raw annotations without applying any source')
  restart(1);expect(source()).to_have_value(raw);retained(held);f.checked('cold before Save preserves exact raw source basis, every typed input, both immutable copy choices and original sources')
  if mode=='late':
   applies=set();inserted=[];late=raw+'\n// 저장 대기 중 추가한 원문 😀\n'
   def inject(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and body.get('input',{}).get('action')=='applySlots':applies.add(body['requestId'])
    response=route.fetch();payload=response.json()
    if not inserted and any(r['requestId'] in applies and r.get('ok') for r in payload.get('results',[])):
     source().evaluate("(el,text)=>{el.value=text;el.dispatchEvent(new Event('input',{bubbles:true}))}",late);f.owner().locator('[aria-label="MP 기본값"]').evaluate("el=>{el.value='9007199254740997';el.dispatchEvent(new Event('input',{bubbles:true}))}");inserted.append(True)
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',inject);f.owner().locator('[data-element-action=save]').click()
   for _ in range(300):
    if inserted and not f.pending()['blueprint']:break
    f.page.wait_for_timeout(100)
   assert inserted and not f.pending()['blueprint'];f.page.unroute_all(behavior='wait');expect(source()).to_have_value(late);expect(f.owner().locator('[aria-label="MP 기본값"]')).to_have_value('9007199254740997');assert views();f.originals();restart(2);expect(source()).to_have_value(late);expect(f.owner().locator('[aria-label="MP 기본값"]')).to_have_value('9007199254740997');assert len([r for r in json.loads(checkpoint.read_text())['changes'] if r.get('creationOwner')==f.id and r['kind']=='implementation'])==2;f.originals();f.checked('late raw/typed input is not deleted or applied by the saved copy receipt; cold keeps exact new text and both existing copies without duplicates')
  elif mode=='cancel':
   f.owner().locator('[data-element-action=discard]').click();f.idle();assert not f.pending()['blueprint'] and not f.pending()['schema'] and views();expect(source()).to_have_value(raw);f.originals();source_window().locator('[data-editor-reset]').click();f.idle();assert not views();restart(2);expect(source()).to_have_value(base);assert not any(r.get('creationOwner')==f.id for r in json.loads(checkpoint.read_text())['changes']);f.originals();f.checked('owner Cancel removes only its typed/copy plans while the independent raw input remains until its own Reset; cold has no partial creations')
  elif mode=='conflict':
   p=f.project/'Slime.celem';p.write_bytes(p.read_bytes()+b'\n// isolated peer source\n');f.original['Slime.celem']=p.read_bytes();reject();assert checkpoint.read_bytes()==before;retained(held);restart(2);reject();retained(held);assert checkpoint.read_bytes()==before;f.checked('actual source conflict rejects raw/typed/schema/registration/all copies and preserves peer bytes and original input through cold retry')
  else:
   if mode=='undo':
    source().evaluate("el=>{el.focus();const i=el.value.lastIndexOf('}');el.setSelectionRange(i,i)}");f.page.keyboard.insert_text('provide '+f.n+'Slot with '+f.n+'SlotBody;\n');bad=f.pending();reject();assert checkpoint.read_bytes()==before;retained(bad);source().focus();f.page.keyboard.press('Control+z');expect(source()).to_have_value(raw);f.checked('overlapping raw provider versus copy selection is entirely rejected; real textarea Undo restores the original input for an explicit retry')
   if mode=='last-copy':
    injected=[]
    def corrupt(route):
     body=route.request.post_data_json
     if body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and body.get('input',{}).get('action')=='applySlots':assert len(body['input']['rows'])==2;body['input']['rows'][-1]['edits'][0]['node']='not-owned';injected.append(True);route.continue_(post_data=json.dumps(body));return
     route.continue_()
    f.page.route('**/api/request',corrupt);reject();f.page.unroute('**/api/request',corrupt);assert injected and checkpoint.read_bytes()==before;retained(held);restart(2);retained(held);f.checked('last copy invalidates the entire raw/owner/schema/registration candidate with no first-copy residue; cold preserves all inputs')
   if mode=='storage':
    checkpoint.chmod(0o400)
    try:reject();assert checkpoint.read_bytes()==before;retained(held);assert next(r for r in f.state()['editorViews'] if r['view']=='1')['draft']['text']==base;f.checked('real checkpoint write failure leaves every raw/typed/copy candidate unapplied and retains all input')
    finally:checkpoint.chmod(0o600)
    restart(2);retained(held)
   if mode=='loss':
    applies=set();queries=set();lost=[]
    def lose(route):
     body=route.request.post_data_json
     if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
      action=body.get('input',{}).get('action')
      if action=='applySlots':applies.add(body['requestId'])
      elif applies and action=='settledSlots':queries.add(body['requestId'])
     response=route.fetch();payload=response.json()
     for r in payload.get('results',[]):
      if r['requestId'] in applies|queries:rid=r['requestId'];lost.append(rid);r.clear();r.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
     route.fulfill(response=response,json=payload)
    f.page.route('**/api/request',lose);f.owner().locator('[data-element-action=save]').click()
    for _ in range(300):
     if applies and any(r in queries for r in lost):break
     f.page.wait_for_timeout(100)
    assert len(applies)==1 and any(r in queries for r in lost);assert f.pending()['blueprint'] and views();f.page.unroute_all(behavior='wait');mark=len(f.traffic);restart(2)
    if f.pending()['blueprint']:f.owner().locator('[data-element-action=save]').click()
    saved();assert not any(v.get('invoke',{}).get('input',{}).get('action')=='applySlots' for v in f.traffic[mark:]);f.checked('lost Apply/receipt responses recover the entire original raw+copy receipt after cold without another apply or duplicate copy')
   else:
    if mode=='source-save':source_window().locator('[data-editor-save]').click()
    else:f.owner().locator('[data-element-action=save]').click()
    saved()
   final=source().input_value();assert '// raw 원문 한글 😀' in final and '// raw 끝' in final and 'data MP= // MP 정확한 값 주석\n9007199254740995;' in final;assert len([r for r in json.loads(checkpoint.read_text())['changes'] if r.get('creationOwner')==f.id and r['kind']=='implementation'])==2;f.originals();restart(3);expect(source()).to_have_value(final);f.checked('one Save/cold retains exact annotation fragments/64-bit values/references and both copy sources, with a single atomic review group')
   if mode=='peer':
    assert [(k,v) for k,v in f.pending()['schema'] if '|'+f.n+'Target1|view:2|element|' in k]==peer;other=f.page.locator('.window[data-key="editor-2"]');expect(other.locator('.object-title-description')).to_have_value('다른 창의 보관 입력');other.locator('[data-element-action=discard]').click();f.idle();assert not [(k,v) for k,v in f.pending()['schema'] if '|'+f.n+'Target1|view:2|element|' in k];assert f.state()['draft']['id']==f.id;f.originals();f.checked('unrelated owner input survives combined Save/cold and only its own explicit Cancel clears it without changing the saved copy group')
   r=f.complete_ui();r.locator('[data-reject]').click();expect(r).to_be_hidden();f.originals();r=f.complete_ui()
   if r.locator('[data-review-advanced]').count():
    r.locator('[data-review-advanced]').click()
    if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
   r.locator('#confirm').click();expect(r).to_have_count(0,timeout=120000);f.idle();assert {k for k,v in f.original.items() if (f.project/k).read_bytes()!=v}=={'Slime.celem','project.cproj'};assert (f.project/'Slime.celem').read_text()==final;restart(4);expect(source()).to_have_value(final);f.checked('explicit Review Cancel/compiler Confirm/cold applies the whole owner/schema/copy/registration group while donor/parent/other targets remain unchanged')
  f.page.screenshot(path=str(f.case/'raw-copies-final.png'));assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except Exception:
 try:f.case.joinpath('raw-copies-failure.json').write_text(json.dumps({'state':f.state(),'traffic':f.traffic[-80:],'errors':f.errors},ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'raw-copies-failure.png'))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'nativeWindows':False,'accountOrInference':False,'projectRun':False},ensure_ascii=False))
