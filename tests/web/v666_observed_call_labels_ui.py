"""Existing observed call labels, authored navigation, explicit binding and actual execution."""
import ast,json,pathlib,sys,traceback,copy,uuid
from playwright.sync_api import sync_playwright,expect
import v666_observed_call_labels_fixture as t
x=t.x;f=t.f;mode=sys.argv[3]
p=pathlib.Path(__file__).with_name('v666_signature_ime_ui.py');exec(compile(ast.Module(body=[n for n in ast.parse(p.read_text()).body if isinstance(n,ast.FunctionDef)and n.name in {'declaration','show'}],type_ignores=[]),str(p),'exec'))
helper=pathlib.Path(__file__).with_name('v666_call_pin_labels_ui.py');exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef)and n.name in {'edit_value','save_value','review'}],type_ignores=[]),str(helper),'exec'))
def panel():return f.page.locator('.window[data-key=blueprint]')
def card():return panel().locator('[data-bp-node="'+t.node+'"]')
def open_frame():
 show();declaration().locator('[data-function-write-direct]').click();f.idle()
 if t.context!='after':
  parent=panel().locator('[data-bp-node=inside]');expect(parent).to_be_visible();parent.locator('[data-internal-flow]').click();f.idle()
 expect(card()).to_be_visible()
def verify():
 current=t.row();assert current['signature']==initial['signature']and current['arguments']==initial['arguments']and current['definitionHash']==initial['definitionHash'];assert (f.project/'Call.graph.json').read_bytes()==original_graph;x.original();actual=card().locator('[data-function-pin-unit]').evaluate_all('(els)=>els.map(e=>e.dataset.functionPinName)')
 if mode=='baseline':assert actual==[t.parameter,'결과']and 'pinPresentation'not in current
 else:assert actual==[t.input_label,t.return_label]and current['pinPresentation']['status']=='available'
 expect(card().locator('button.bp-port[data-side=in][data-port="field:'+t.parameter+'"]')).to_be_visible();expect(card().locator('button.bp-port[data-side=out][data-port="field:return"]')).to_be_visible()
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();initial=t.row();original_graph=(f.project/'Call.graph.json').read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2100,'height':1500});f.page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"')
  try:
   open_frame();verify();assert checkpoint.read_bytes()==before;f.checked('published saved private call remains native despite observed aliases'if mode=='baseline'else'exact observed function labels appear in the existing '+t.context+' view without changing pin IDs, graph/native signatures, definitions or C#')
   if t.context=='after':
    panel().locator('[data-close]').first.click();open_frame()
   else:
    panel().locator('.bp-breadcrumbs button').first.click();f.idle();expect(panel().locator('[data-bp-node=inside]')).to_be_visible();panel().locator('[data-bp-node=inside] [data-internal-flow]').click();f.idle()
   verify();assert checkpoint.read_bytes()==before
   f.pending();f.page.close();f.stop();f.start(1);f.page=f.setup();f.page.set_viewport_size({'width':2100,'height':1500});f.idle();expect(card()).to_be_visible();verify();assert checkpoint.read_bytes()==before;f.checked('existing '+t.context+' navigation and cold retain the same sources, bindings, checkpoint and display provenance')
   if mode!='baseline':x.build('observed-private-original-execution',10,'body');verify();f.checked('original saved '+t.context+' call actually executes result10 with unchanged C# and native bindings')
   if mode=='binding':
    edit_value();save_value();assert not any(v.get('type')=='argument:'+t.parameter for _,v in f.pending()['blueprint']);current=t.row();assert current['signature']==initial['signature']and current['definitionHash']==initial['definitionHash'];assert json.loads(next(a['valueJson']for a in current['arguments']if a['name']==t.parameter))=={'constant':8};x.original()
    r=review();r.locator('[data-reject]').click();x.original();r=review();target=f.project/'Call.graph.json';raw=target.read_bytes();held=checkpoint.read_bytes();target.write_bytes(raw+b' ')
    try:r.locator('#confirm').click();f.idle();assert target.read_bytes()==raw+b' 'and checkpoint.read_bytes()==held and all(p.read_bytes()==v for p,v in x.physical.items()if p!=target)
    finally:target.write_bytes(raw)
    if r.is_visible():r.locator('[data-reject]').click()
    r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();assert all(p.read_bytes()==v for p,v in x.physical.items()if p!=target);g=json.loads(target.read_text());inside=g['nodes'][0]['graph']['nodes'][0];assert inside['id']==t.node and inside['arguments']=={t.parameter:{'constant':8}};x.build('observed-private-authored-value',11,'body');f.checked('displayed private input edits native supplied only, saves explicit binding, retains Review cancel/edited-graph final CAS and unchanged C#, executes result11')
   f.page.screenshot(path=str(f.case/('observed-call-'+mode+'.png')),timeout=5000)
  except Exception:
   (f.case/'failure.txt').write_text(traceback.format_exc());
   try:f.page.screenshot(path=str(f.case/'failure.png'),timeout=5000)
   except Exception:pass
   raise
  f.browser.close()
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));f.stop()
