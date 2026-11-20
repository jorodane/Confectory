"""Document presentation over the existing author adapter; controlled provider, not engine execution."""
import ast,http.server,json,pathlib,re,sys,tempfile,threading
from playwright.sync_api import sync_playwright,expect

repo=pathlib.Path(sys.argv[1]).resolve();case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-v821-document-'));checks=[];errors=[]
tree=ast.parse((repo/'tests/web/v508_feature_serial_canvas.py').read_text())
setup=next(n.args[0].value for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='evaluate' and n.args and isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str) and 'const {createFeatureAuthoring}' in n.args[0].value)
setup=setup.replace(",functionDocumentViews:{'owned|function-document|primary||Owned::SerialBody/body:common|':{mode:'blueprint'}}",'')
setup=setup.replace('await author.openInWork(info);','fixture.api=api;graph.nodes.reverse();await author.openInWork(info);')
setup=setup.replace('fixture.api=api;', '''api.modal=(title,html,setup)=>{const el=document.createElement('section');el.setAttribute('role','dialog');el.setAttribute('aria-label',title);el.style.cssText='position:fixed;inset:20px;z-index:100;background:#222;padding:20px;overflow:auto';el.innerHTML=html;document.body.append(el);setup(el,()=>el.remove());};fixture.api=api;''')
# The historical renderer fixture only implements the disconnected-node batch.
# Add this test's single checked argument batch; actual engine/CAS coverage is
# separate and must not be inferred from this controlled provider.
setup=setup.replace("if(invalid||!durable||input.id!==graph.id", """if(input.edits.length===1&&input.edits[0].action==='argument'){
      const edit=input.edits[0],row=graph.nodes.find(n=>n.id===edit.node),argument=row?.arguments.find(a=>a.name===edit.name);
      if(invalid||!durable||input.id!==graph.id||input.sourceProof!==JSON.stringify(graph.sources.map(s=>[s.id,s.revision,s.hash]))||!argument)throw Error('Fixture checked argument batch rejected');
      argument.valueJson=edit.valueJson;graph.sources[0].revision++;graph.basis='b'+graph.sources[0].revision;(fixture.batchReceipts??=new Map()).set(input.attempt,structuredClone(input));return {checkpointSaved:true};
     }
     if(invalid||!durable||input.id!==graph.id""")
setup=setup.replace("meta:{id:'Owned::Serial'","meta:{id:'Owned::Serial',outputSidebar:{width:250,collapsed:false}")
styles='\n'.join((repo/'examples/editor-home/ui'/name).read_text() for name in ['style.css','consumer.css','runtime.css']);styles=re.sub(r'@import\s+url\([^)]*\)\s*;','',styles)
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*args,**kw):super().__init__(*args,directory=str(repo),**kw)
 def log_message(self,*args):pass
 def do_GET(self):
  if self.path=='/fixture':
   self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(('<style>'+styles+'</style><main id="workspace" style="height:840px;position:relative"></main>').encode())
  else:super().do_GET()
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
def checked(message):checks.append(message);print('PASS '+message,flush=True)
try:
 with sync_playwright()as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1280,'height':950});page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto('http://127.0.0.1:'+str(server.server_port)+'/fixture');page.evaluate(setup)
  root=page.locator('.blueprint-editor');doc=root.locator('.function-document')
  expect(doc).to_be_visible();expect(root.get_by_role('tab',name='논리 코드',exact=True)).to_have_attribute('aria-selected','true');expect(root.get_by_role('tab',name='네이티브 미리보기',exact=True)).to_be_disabled()
  assert doc.locator('[data-document-cell]').evaluate_all('(els)=>els.map(e=>e.dataset.documentCell)')==['$entry','first','second','$exit:return']
  assert page.evaluate('fixture.graph.nodes.map(n=>n.id)')==['second','first'];assert page.evaluate('fixture.inputs.size')==0
  cell=doc.locator('[data-document-cell=first]');left=cell.locator('.fd-inputs').bounding_box();right=cell.locator('.fd-outputs').bounding_box();assert left['x']+left['width']<right['x']
  checked('logic is default; actual next links determine top-to-bottom order without rewriting node order, with left inputs/right outputs')
  baseline=page.evaluate('({graph:JSON.stringify(fixture.graph),inputs:[...fixture.inputs],traffic:fixture.traffic.length,undo:fixture.w.authorUndo?.length||0,positions:JSON.stringify(fixture.w.meta.blueprintPositions||{})})')
  cell.locator('[data-document-fold]').click();expect(cell.locator('.fd-cell-content')).to_be_hidden();expect(cell.locator('.fd-cell-title')).to_be_visible();expect(cell.locator('.fd-cell-state')).to_be_visible()
  page.evaluate('async()=>{fixture.w.el.hidden=true;await fixture.open();fixture.w.el.hidden=false;window.dispatchEvent(new Event("resize"));}');expect(doc.locator('[data-document-cell=first] .fd-cell-content')).to_be_hidden()
  expect(root.get_by_role('tab',name='논리 코드',exact=True)).to_have_attribute('aria-selected','true');expect(root.locator('.bp-layout')).to_be_hidden()
  actual=root.locator('.bp-layout').evaluate('(el)=>el.style.getPropertyValue("--bp-output-width")');assert actual=='250px';assert page.evaluate('fixture.w.meta.outputSidebar.width')==250
  # Reopening performs the existing read; folds themselves emit no provider writes.
  assert page.evaluate('fixture.traffic.every(r=>["featureBodies","read"].includes(r.input.action))')
  doc.locator('[data-document-cell=first] [data-document-fold]').click()
  root.get_by_role('tab',name='블루프린트 보기',exact=True).click();expect(root.locator('.bp-viewport')).to_be_visible()
  root.get_by_role('tab',name='논리 코드',exact=True).click();expect(doc).to_be_visible()
  assert page.evaluate('JSON.stringify(fixture.graph)')==baseline['graph'];assert page.evaluate('fixture.inputs.size')==0;assert page.evaluate('fixture.w.authorUndo?.length||0')==baseline['undo'];assert page.evaluate('JSON.stringify(fixture.w.meta.blueprintPositions||{})')==baseline['positions']
  checked('cell folds survive reopening; view changes preserve graph, authored positions, pending inputs and source Undo')
  value=doc.locator('[data-document-value=first][data-document-port="field:n"]');value.click()
  menu=page.get_by_role('dialog',name='핀 값 선택');expect(menu).to_be_visible();search=menu.get_by_role('searchbox',name='값 검색');search.fill('123')
  uncommitted=page.evaluate('({inputs:JSON.stringify([...fixture.inputs]),graph:JSON.stringify(fixture.graph),undo:fixture.w.authorUndo?.length||0})')
  cell=doc.locator('[data-document-cell=first]');cell.locator('[data-document-fold]').click()
  assert page.evaluate('JSON.stringify([...fixture.inputs])')==uncommitted['inputs'];assert page.evaluate('JSON.stringify(fixture.graph)')==uncommitted['graph'];assert page.evaluate('fixture.w.authorUndo?.length||0')==uncommitted['undo']
  root.get_by_role('tab',name='블루프린트 보기',exact=True).click();root.get_by_role('tab',name='논리 코드',exact=True).click();cell=doc.locator('[data-document-cell=first]');cell.locator('[data-document-fold]').click();value=doc.locator('[data-document-value=first][data-document-port="field:n"]');value.click();search=page.get_by_role('dialog',name='핀 값 선택').get_by_role('searchbox',name='값 검색');expect(search).to_have_value('123');search.fill('9223372036854775807');search.press('Enter')
  value=doc.locator('[data-document-value=first][data-document-port="field:n"]');expect(value).to_have_text('9223372036854775807')
  assert page.evaluate('[...fixture.inputs.values()].find(v=>v.type==="argument:n").text')=='{"constant":9223372036854775807}'
  # Preserve the existing distinction: plain literal inputs do not add structural
  # history; expression structure does. Folds must not manufacture either kind.
  value.click();page.get_by_role('button',name='연산자 +',exact=True).click()
  expect(doc.locator('[data-document-value=first][data-document-port="field:n"]')).to_contain_text('+')
  doc.focus();page.keyboard.press('Control+z');expect(doc.locator('[data-document-value=first][data-document-port="field:n"]')).to_have_text('9223372036854775807')
  page.keyboard.press('Control+Shift+z');expect(doc.locator('[data-document-value=first][data-document-port="field:n"]')).to_contain_text('+')
  page.keyboard.press('Control+z');expect(doc.locator('[data-document-value=first][data-document-port="field:n"]')).to_have_text('9223372036854775807')
  root.locator('[data-bp-save]').click();page.evaluate('async()=>await fixture.settled()')
  if root.locator('.bp-status').inner_text()!='저장됨':
   print(json.dumps(page.evaluate('({inputs:[...fixture.inputs],traffic:fixture.traffic,errors:fixture.toasts})'),ensure_ascii=False),flush=True)
  expect(root.locator('.bp-status')).to_have_text('저장됨');assert page.evaluate('fixture.graph.nodes.find(n=>n.id==="first").arguments[0].valueJson')=='{"constant":9223372036854775807}'
  checked('existing typed value picker, exact long token, source Undo/Redo and explicit Save work from vertical cells')
  doc.locator('[data-document-code=first]').click();expect(page.get_by_role('dialog').last.locator('[data-code-source]')).to_be_visible();page.locator('[data-code-cancel]').click();assert page.evaluate('fixture.inputs.size')==0
  checked('native body edit opens the existing protected editor; Cancel does not create a source change')
  page.screenshot(path=str(case/'document.png'))
  page.evaluate('''async()=>{
   const {mountFunctionDocument}=await import('/examples/editor-home/ui/function-document.js');
   const root=document.createElement('section');root.className='blueprint-editor';root.style.cssText='position:fixed;inset:10px;z-index:50;background:#181818;display:flex;flex-direction:column';root.innerHTML='<div class="bp-toolbar"></div><div class="bp-layout"></div>';document.body.append(root);
   const node=(id,name,branches=[])=>({id,name,kind:'action',inputs:[],outputs:[],readonly:true,branches});
   const model={name:'조건 흐름',inputs:[],outputs:[],nodes:[node('$entry','시작'),node('work','하는 일',[{id:'case:yes',name:'값이 있을 때'},{id:'case:no',name:'값이 없을 때'}]),node('yes','값 사용'),node('no','값 준비'),node('after','계속')],links:[{from:'$entry',port:'next',to:'work'},{from:'work',port:'next',to:'after'},{from:'work',port:'case:yes',to:'yes'},{from:'work',port:'case:no',to:'no'}]};
   let writes=0,persists=0;const view={el:root,meta:{}},api={esc:fixture.api.esc,view,context:'branches',owns:()=>true,persist:()=>persists++,model:()=>model,values:()=>[],closeValues:()=>true,switchView:()=>{},graph:()=>{},write:()=>writes++};
   fixture.branches={root,model,view,writes:()=>writes,persists:()=>persists};mountFunctionDocument(root,api);
  }''')
  branch=page.locator('.blueprint-editor').last.locator('[data-document-cell=work]');branch.get_by_role('button',name='분기 내용 접기',exact=True).click();expect(branch.get_by_role('button',name='값이 있을 때',exact=True)).to_be_visible();expect(branch.locator('.fd-branch-panel').first).to_be_hidden()
  branch.get_by_role('button',name='분기 내용 펼치기',exact=True).click();branch.get_by_role('button',name='값이 없을 때',exact=True).click();expect(branch.locator('[data-document-cell=no]')).to_be_visible();expect(branch.locator('[data-document-cell=yes]')).to_be_hidden()
  branch.locator('[data-document-fold=work]').click();expect(branch.locator('.fd-branch-tabs')).to_be_hidden();expect(branch.locator('>.fd-cell-header .fd-cell-title')).to_be_visible();assert branch.locator('.fd-cell-content p').count()==0
  assert page.evaluate('fixture.branches.writes()')==0;assert page.evaluate('fixture.branches.persists()')>=4
  checked('group collapse retains condition tabs; parent collapse hides owned tabs and content without description rows or domain edits')
  page.screenshot(path=str(case/'folds.png'));assert not errors,errors;browser.close()
except Exception:
 try:
  page.screenshot(path=str(case/'failure.png'))
  (case/'failure-state.json').write_text(json.dumps(page.evaluate('({inputs:[...fixture.inputs],undo:(fixture.w.authorUndo||[]).map(v=>({...v,before:[...v.before],after:[...v.after]})),meta:fixture.w.meta,errors:fixture.toasts})'),ensure_ascii=False,indent=2))
 except Exception:pass
 print('FAILURE EVIDENCE '+str(case),flush=True)
 raise
finally:server.shutdown()
(case/'result.json').write_text(json.dumps(dict(checks=checks,controlledProvider=True,actualEngine=False,actualWindows=False,mockupVisualCompared=False,errors=errors),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(checks=checks,evidence=str(case),controlledProvider=True,actualEngine=False),ensure_ascii=False))
