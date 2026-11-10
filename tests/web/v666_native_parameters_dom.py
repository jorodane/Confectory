"""Actual parameter editor DOM: nominal identity survives names and explicit additions."""
import json,os,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
repo=Path(sys.argv[1]);target=Path(sys.argv[2]);target.mkdir(parents=True,exist_ok=True)
source=(repo/'examples/editor-home/ui/blueprint-parameters.js').read_text()
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1100,'height':900});page.set_content('<main><div class="bp-code"></div></main>')
 page.add_script_tag(type='module',content=source+'\nwindow.mountParameters=mountBlueprintParameters;')
 page.wait_for_function('window.mountParameters !== undefined')
 result=page.evaluate('''() => {
  const payload='Confectory.Information.E'+'1'.repeat(24)+'.E'+'2'.repeat(24),unknown='Confectory.Information.E'+'3'.repeat(24)+'.E'+'4'.repeat(24);
  const api={current:{projectId:'project'},inputs:new Map(),controls(){},persist(){},toast(text){throw Error(text);}},node={id:'transform',sourceId:'graph/node:transform',signature:{args:[{name:'data',type:payload}],return:payload}};
  const data={id:'graph',basis:'observed',profile:'sync-acyclic-methods-v1',signature:{args:[{name:'data',type:payload}],return:'int'},nodes:[node]},w={body:document.querySelector('main')};
  let held=null,applied=null;
  function bindInput(w,data,kind,id,field,initial,request){field.value=initial;field.oninput=()=>{held=field.value;};const host=field.closest('details');host.querySelector('[data-apply]').onclick=()=>{applied=request(field.value);};host.querySelector('[data-reset]').onclick=()=>{field.value=initial;held=null;};host.querySelector('[data-rebase]').onclick=()=>{};}
  window.mountParameters({api,w,data,node,bindInput,actions:'<button data-apply>Apply</button><button data-reset>Cancel</button><button data-rebase>Rebase</button>',esc:text=>String(text).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))});
  const editor=w.body.querySelector('details');editor.open=true;const initialType=editor.querySelector('[data-bp-parameter-type]').value;
  const name=editor.querySelector('[data-bp-parameter-name]');name.value='received';name.dispatchEvent(new Event('input'));
  const renamed=JSON.parse(held);editor.querySelector('[data-bp-remap]').value='received';editor.querySelector('[data-bp-remap]').dispatchEvent(new Event('change'));
  editor.querySelector('[data-bp-parameter-add]').click();const row=editor.querySelectorAll('[data-bp-parameter-row]')[1],type=row.querySelector('[data-bp-parameter-type]');type.value=payload;type.dispatchEvent(new Event('input'));
  const chosen=JSON.parse(held);editor.querySelector('[data-bp-parameters-preview]').click();editor.querySelector('[data-bp-parameters-ack]').checked=true;editor.querySelector('[data-bp-parameters-apply]').click();
  const result={payload,initialType,renamed,chosen,applied,unknownOffered:[...type.options].some(o=>o.value===unknown),arrayOffered:[...type.options].some(o=>o.value===payload+'[]')};
  editor.querySelector('[data-bp-parameters-reset]').click();result.cancelType=editor.querySelector('[data-bp-parameter-type]').value;result.cancelHeld=held;return result;
 }''')
 page.screenshot(path=str(target/'parameters.png'));(target/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));browser.close()
print(json.dumps(result,ensure_ascii=False))
if 'observe'not in sys.argv[3:]:
 assert result['initialType']==result['payload']==result['renamed']['args'][0]['type']
 assert result['chosen']['args'][1]['type']==result['payload'] and result['applied']['action']=='parameters'
 assert result['arrayOffered'] and not result['unknownOffered']
 assert result['cancelType']==result['payload'] and result['cancelHeld']is None
