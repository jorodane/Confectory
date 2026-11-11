"""Read-only direct call labels with exact pins, existing value edits and cold restore."""
import ast,json,pathlib,sys,traceback,copy,uuid
from playwright.sync_api import sync_playwright,expect
import v666_call_pin_labels_fixture as t
x=t.x;f=t.f;mode=sys.argv[3]
helper=pathlib.Path(__file__).with_name('v666_signature_ime_ui.py');exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef)and n.name in {'declaration','show'}],type_ignores=[]),str(helper),'exec'))
def panel():return f.page.locator('.window[data-key=blueprint]')
def card():return panel().locator('[data-bp-node="'+t.node+'"]')
def open_graph():
 show();declaration().locator('[data-function-write-direct]').click();f.idle();expect(card()).to_be_visible();expect(card().locator('button.bp-port[data-side=in][data-port="field:'+t.parameter+'"]')).to_be_visible();expect(card().locator('button.bp-port[data-side=out][data-port="field:return"]')).to_be_visible()
def names():return card().locator('[data-function-pin-unit]').evaluate_all('(els)=>els.map(e=>e.dataset.functionPinName)')
def edit_value():
 control=card().locator('.bp-pin-plug[data-side=in][data-port="field:'+t.parameter+'"] input').first;control.click();menu=f.page.get_by_role('dialog',name='핀 값 선택',exact=True);expect(menu).to_be_visible();search=menu.get_by_role('searchbox',name='값 검색',exact=True);search.fill('8');search.press('Enter');expect(menu).to_have_count(0);assert any(v.get('type')=='argument:'+t.parameter and '8'in v.get('text','')for _,v in f.pending()['blueprint'])
def save_value():panel().locator('[data-bp-save]').click();f.idle()
def review():
 panel().locator('[data-bp-complete]').click();f.idle()
 if f.page.locator('#review-creation').is_visible():f.page.locator('#review-creation').click();f.idle()
 f.page.locator('.window[data-key=review]:visible,.window[data-key=targets]:visible').first.wait_for(state='visible',timeout=90000);targets=f.page.locator('.window[data-key=targets]')
 if targets.is_visible():targets.locator('[data-target-choice]').select_option('portable');targets.locator('[data-close]').click();panel().locator('[data-bp-complete]').click();f.idle()
 r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=90000)
 if r.locator('[data-review-advanced]').is_visible():r.locator('[data-review-advanced]').click()
 if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
 return r
def verify():
 current=t.row();assert current['signature']==initial['signature']and current['arguments']==initial['arguments']and current['definitionHash']==initial['definitionHash'];assert (f.project/'Call.graph.json').read_bytes()==graph_before;x.original()
 if mode=='baseline':assert names()==[t.parameter,'결과'];assert 'pinPresentation'not in current
 elif mode=='invalid':assert names()==[t.parameter,'결과']and current['pinPresentation']['status']=='invalid-labels';expect(card().locator('.function-node')).to_have_attribute('title','표시 이름을 현재 호출 계약에서 확인하지 못했어요. 실제 핀과 연결은 유지됩니다.')
 elif mode=='plain-prototype':assert names()==[t.parameter,'결과']and current['pinPresentation']['status']=='available'and current['pinPresentation']['argumentNames']=={}
 else:
  assert names()==[t.input_label,t.return_label],names();p=current['pinPresentation'];assert p['status']=='available'and p['argumentNames']=={t.parameter:t.input_label}and p['returnName']==t.return_label;expect(card().locator('.bp-pin-remove').first).to_be_disabled()
try:
 f.start(0);f.invoke('select',{'id':t.feature});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();initial=t.row();graph_before=(f.project/'Call.graph.json').read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2100,'height':1500});f.page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"')
  try:
   open_graph();verify();assert checkpoint.read_bytes()==before;f.checked('published call pin labels remain native'if mode=='baseline'else'existing caller IDs supplied/return and definition hash stay exact while observed callee aliases are displayed')
   panel().locator('[data-close]').first.click()
   if mode=='pending':
    old=t.feature;t.feature=t.callee
    try:show()
    finally:t.feature=old
    declaration().locator('.object-info-button').click();pop=f.page.locator('.function-detail-popover');pop.locator('[data-signature-id=return] [data-signature-name]').fill('아직 저장하지 않은 결과');pop.get_by_role('button',name='저장',exact=True).click();assert '아직 저장하지 않은 결과'in json.dumps(f.pending(),ensure_ascii=False);x.original()
   open_graph();verify();assert checkpoint.read_bytes()==before
   f.pending();f.page.close();f.stop();f.start(1);f.page=f.setup();f.page.set_viewport_size({'width':2100,'height':1500});f.idle();expect(card()).to_be_visible();verify();assert checkpoint.read_bytes()==before;f.checked('repeated open and cold restore preserve native call signature, bindings, original C# and checkpoint')
   if mode=='pending':assert '아직 저장하지 않은 결과'in json.dumps(f.pending(),ensure_ascii=False);f.checked('another function pending return label survives caller open/cold and never becomes an implicit save or observed alias')
   if mode=='conflict':
    edit_value();d=t.read();f.invoke('select',dict(id=t.callee));source=f.invoke('inspectDeclaration',dict(id=t.callee))['state']['declaration'];f.invoke('editFunctionContract',dict(id=t.callee,revision=source['revision'],hash=source['textHash'],edit=dict(description='동료의 관측 원문 변경')));f.invoke('select',dict(id=t.feature));held=checkpoint.read_bytes();mark=len(f.traffic);save_value();assert checkpoint.read_bytes()==held and any(v.get('type')=='argument:'+t.parameter for _,v in f.pending()['blueprint']);issued=[row['invoke']for row in f.traffic[mark:]if row.get('invoke',{}).get('endpoint')=='blueprint'and row['invoke']['input'].get('action')=='argument'];assert len(issued)==1 and issued[0]['input']['name']==t.parameter and json.loads(issued[0]['input']['valueJson'])=={'constant':8},issued;assert any(row.get('result',{}).get('requestId')==issued[0]['requestId']and row['result']['ok']is False for row in f.traffic[mark:]);verify();f.checked('actual caller value Save issues the existing native argument request and refuses an observed callee peer change without dropping the input or changing checkpoint, graph/C# or pin IDs')
   if mode!='baseline':x.build('call-labels-original-execution',10,'body');verify();f.checked('actual original positional call executes result10 without rewriting C# or graph bindings')
   if mode=='binding':
    edit_value();save_value();assert not any(v.get('type')=='argument:'+t.parameter for _,v in f.pending()['blueprint']);current=t.row();assert current['signature']==initial['signature']and current['definitionHash']==initial['definitionHash'];assert json.loads(next(a['valueJson']for a in current['arguments']if a['name']==t.parameter))=={'constant':8};x.original()
    r=review();r.locator('[data-reject]').click();x.original();r=review();target=f.project/'Call.graph.json';raw=target.read_bytes();held=checkpoint.read_bytes();target.write_bytes(raw+b' ')
    try:r.locator('#confirm').click();f.idle();assert target.read_bytes()==raw+b' 'and checkpoint.read_bytes()==held and all(p.read_bytes()==raw for p,raw in x.physical.items()if p!=target)
    finally:target.write_bytes(raw)
    if r.is_visible():r.locator('[data-reject]').click()
    r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();assert all(p.read_bytes()==raw for p,raw in x.physical.items()if p!=f.project/'Call.graph.json');g=json.loads((f.project/'Call.graph.json').read_text());assert g['nodes'][0]['id']==t.node and g['nodes'][0]['arguments']=={t.parameter:{'constant':8}};x.build('call-labels-authored-value-execution',11,'body');f.checked('editing the displayed input uses native supplied, saves only its explicit binding, and preserves Review cancellation/final edited-graph CAS and C# while executing result11')
   f.page.screenshot(path=str(f.case/('call-labels-'+mode+'.png')),timeout=5000)
  except Exception:
   (f.case/'failure.txt').write_text(traceback.format_exc());
   try:f.page.screenshot(path=str(f.case/'failure.png'),timeout=5000)
   except Exception:pass
   raise
  f.browser.close()
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));f.stop()
