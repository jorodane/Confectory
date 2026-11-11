"""Owned standalone fixed-return labels: actual owner CAS and compiler workflow."""
import ast,copy,json,pathlib,re,sys,traceback
from playwright.sync_api import sync_playwright,expect
import v666_root_input_name_recovery_fixture as t
x=t.x;f=t.f;mode=sys.argv[3];text='계산 결과 😀';late='새 계산 결과 β';description='같은 소유 함수의 설명 😀'
helper=pathlib.Path(__file__).with_name('v666_signature_ime_ui.py')
names={'declaration','pop','show','review','restart'}
exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),str(helper),'exec'))
def has(value):return value in json.dumps(f.pending(),ensure_ascii=False)
def info():return f.invoke('inspectDeclaration',{'id':t.feature})['state']['declaration']
def stored():return info()['values'].get('editorReturnName','결과')
def edit(value,desc=None):
 show();declaration().locator('.object-info-button').click();field=pop().locator('[data-signature-id=return] [data-signature-name]');expect(field).to_be_editable();field.fill(value)
 if desc is not None:pop().locator('[data-detail-description]').fill(desc)
 pop().get_by_role('button',name='저장',exact=True).click();expect(pop()).to_have_count(0);assert has(value)
def save():show();declaration().locator('[data-feature-action=save]').click();f.idle()
def history(direction):
 state=f.invoke('draftHistory',{'action':'inspect'})['result']['result'];assert state[direction]['available'];assert f.invoke('draftHistory',{'action':direction,'token':state[direction]['token']})['result']['result']['accepted'];x.original()
def signature_guard():
 before=checkpoint.read_bytes();show();declaration().locator('.object-info-button').click();field=pop().locator('[data-signature-kind=inputs] [data-signature-name]').first;field.fill('units');ret=pop().locator('[data-signature-id=return] [data-signature-name]');ret.fill(late);pop().get_by_role('button',name='저장',exact=True).click();expect(pop()).to_be_visible();expect(field).to_have_value('units');expect(ret).to_have_value(late);pop().locator('[data-detail-cancel]').click();assert checkpoint.read_bytes()==before and stored()==text;x.original();f.checked('mixing a native signature change with a new return label refuses and retains the popup without contract or C# rewriting')
def main():
 if mode=='baseline':
  show();declaration().locator('.object-info-button').click();expect(pop().locator('[data-signature-id=return] [data-signature-name]')).to_have_attribute('readonly','');pop().locator('[data-detail-cancel]').click();x.original();f.checked('published baseline fixed return label is read-only in standalone details; pending/checkpoint/source remain unchanged');return
 show();declaration().locator('.object-info-button').click();field=pop().locator('[data-signature-id=return] [data-signature-name]');field.fill('');pop().get_by_role('button',name='저장',exact=True).click();expect(pop()).to_be_visible();expect(field).to_have_value('');pop().locator('[data-detail-cancel]').click();assert checkpoint.read_bytes()==before;x.original()
 edit(text,description);assert checkpoint.read_bytes()==before;x.original();expect(f.page.get_by_role('img',name=re.compile(re.escape(text)+r' ·'))).to_be_visible()
 declaration().locator('.object-title-name').click();f.page.keyboard.press('Control+z');assert not has(text);f.page.keyboard.press('Control+Shift+z');assert has(text);restart(1);assert has(text)and has(description);x.original();f.checked('explicit display mode, invalid/explicit cancel, local Undo/Redo and cold preserve the same native contract and pending return-label/description')
 if mode=='cancel':
  declaration().locator('[data-feature-action=discard]').click();f.idle();assert not has(text)and checkpoint.read_bytes()==before;x.original();restart(2);assert not has(text)and stored()=='결과';f.checked('explicit cancellation after cold removes only captured owner inputs and keeps original function/body/caller bytes');return
 if mode=='conflict':
  current=info();f.invoke('editFunctionContract',{'id':t.feature,'revision':current['revision'],'hash':current['textHash'],'edit':{'description':'同僚の説明'}});f.invoke('saveDraft',{});peer=checkpoint.read_bytes();save();assert checkpoint.read_bytes()==peer and has(text);restart(2);assert has(text)and checkpoint.read_bytes()==peer;x.original();f.checked('peer checkpoint cannot be overwritten or silently rebased by stale return-label/description input, including cold');return
 if mode=='storage':
  checkpoint.chmod(0o400)
  try:save();assert checkpoint.read_bytes()==before and has(text);x.original()
  finally:checkpoint.chmod(0o600)
  restart(2);assert has(text)and has(description)and checkpoint.read_bytes()==before;x.original();f.checked('real checkpoint write failure and cold retain return-label/description and original checkpoint before explicit retry')
 if mode in ['loss','late']:
  writes=set();queries=set();paused={};lost=[]
  def interrupt(route):
   body=route.request.post_data_json
   if body.get('op')=='invoke'and body.get('endpoint')=='blueprint':
    action=body.get('input',{}).get('action')
    if action=='applySlots':writes.add(body['requestId'])
    elif writes and action=='settledSlots':queries.add(body['requestId'])
   response=route.fetch();payload=response.json()
   if mode=='late'and not paused and any(row.get('ok')and row.get('requestId')in writes for row in payload.get('results',[])):paused.update(route=route,response=response);return
   if mode=='loss':
    for row in payload.get('results',[]):
     if row['requestId']in writes|queries:rid=row['requestId'];lost.append(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
   route.fulfill(response=response,json=payload)
  f.page.route('**/api/request',interrupt);declaration().locator('[data-feature-action=save]').click()
  for _ in range(1000):
   if paused or writes and any(r in queries for r in lost):break
   f.page.wait_for_timeout(30)
  assert len(writes)==1
  if mode=='late':
   assert paused;declaration().locator('.object-info-button').click();field=pop().locator('[data-signature-id=return] [data-signature-name]');field.fill(late);pop().get_by_role('button',name='저장',exact=True).click();expect(pop()).to_have_count(0);paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',interrupt);f.idle();assert has(late)
  else:
   assert any(r in queries for r in lost);f.page.unroute_all(behavior='wait');f.idle();assert has(text)
  wanted=late if mode=='late'else text;restart(3);assert has(wanted);mark=len(f.traffic);save()
  if has(wanted):save()
  assert not has(wanted)and stored()==wanted;x.original();actual=[row['invoke']for row in f.traffic[mark:]if row.get('invoke',{}).get('endpoint')=='blueprint'and row['invoke']['input'].get('action')=='applySlots'];assert len(actual)==(1 if mode=='late'else 0),actual
  f.checked('accepted '+mode+' and cold distinguish the existing receipt from new label input; previous apply is not replayed and native source/contract remains original');return
 save();assert not has(text)and stored()==text;assert [(a['Name'],a['Type'],a.get('Mode'))for a in info()['signature']['Args']]==[('amount','int',None)];x.original();f.checked('one existing owner transaction durably saves labels and description without changing native names/types/IDs or source C#')
 history('undo');assert stored()=='결과';history('redo');assert stored()==text;restart(3);assert stored()==text and not has(text);signature_guard()
 edit('결과');save();assert stored()=='결과'and 'editorReturnName'not in info()['values'];edit(text);save();assert stored()==text;x.original();f.checked('explicit default reset removes only optional return metadata; same-contract relabeling preserves source and fixed return identity')
 r=review();r.locator('[data-reject]').click();x.original();r=review();target=f.project/'Pair.celem';original=target.read_bytes();held=checkpoint.read_bytes();target.write_bytes(original+b' ')
 try:
  r.locator('#confirm').click();f.idle();assert target.read_bytes()==original+b' 'and checkpoint.read_bytes()==held;assert all(p.read_bytes()==raw for p,raw in physical.items()if p!=target)
 finally:target.write_bytes(original)
 if r.is_visible():r.locator('[data-reject]').click()
 f.checked('a physical peer change after Review is refused at final CAS with checkpoint and every other source unchanged')
 r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();assert all(p.read_bytes()==raw for p,raw in physical.items()if p!=f.project/'Pair.celem');assert (f.project/'Pair.celem').read_bytes()!=physical[f.project/'Pair.celem'];x.build('standalone-return-original-execution',10,'body\n10');restart(4);assert stored()==text and not has(text);assert not f.errors and not f.external;f.checked('Review cancellation and explicit compiler Confirm execute original result10 and preserve every C# body/caller/graph across cold')
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();physical=x.physical.copy()
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"');f.page.set_viewport_size({'width':1800,'height':1400})
  try:main()
  except Exception as error:
   (f.case/'failure-exception.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc(),errors=f.errors),ensure_ascii=False));print(traceback.format_exc(),flush=True)
   try:f.page.screenshot(path=str(f.case/'failure.png'),timeout=5000)
   except Exception:pass
   raise
  f.page.screenshot(path=str(f.case/('standalone-'+mode+'.png')),timeout=5000);f.browser.close()
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));f.stop()
