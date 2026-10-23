"""Controlled original renderer lifecycle: interrupted invalid enum input, no engine/account/grants."""
import http.server,pathlib,tempfile,threading,json,sys
from playwright.sync_api import sync_playwright,expect
repo=pathlib.Path(sys.argv[1]).resolve();case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-enum-reentry-'));checks=[];errors=[]
styles=''.join((repo/'examples/editor-home/ui'/n).read_text() for n in ['style.css','consumer.css','runtime.css'])
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(repo),**kw)
 def log_message(self,*a):pass
 def do_GET(self):
  if self.path=='/fixture':
   self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(('<style>'+styles+'</style><main id="workspace" class="workspace" style="height:840px;position:relative"></main>').encode())
  else:super().do_GET()
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();url='http://127.0.0.1:'+str(server.server_port)
bootstrap=r"""async()=>{
 const {createFeatureAuthoring}=await import('/examples/editor-home/ui/feature-authoring.js');
 const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)],esc=v=>String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;');
 const info={id:'Owned.General::F',description:'일반 enum',signature:{args:[],return:'void'}},id='Owned.General::Body/body:common';
 const data={id,rootId:id,privatePath:'',feature:info.id,featureDefinition:info,signature:info.signature,profile:'sync-acyclic-switch-v1',basis:'read-v1',checkpointHash:'c'.repeat(64),sources:[{id:info.id,hash:'a'.repeat(64),revision:0},{id,hash:'b'.repeat(64),revision:0},{id:id+'/node:choose',hash:'d'.repeat(64),revision:0}],nodes:[{id:'choose',kind:'code',control:'switch',displayName:'실행 선택',intent:'원본 순차 실행',signature:{args:[],return:'void'},sourceId:id+'/node:choose',source:'return Result.Ready;',helpers:'',renameable:true,definitionHash:'e'.repeat(64),executionEnum:{primary:'next',members:[{id:'next',name:'NoBranch',value:0},{id:'ready',name:'Ready',value:1}]}}],edges:[],exits:[],diagnostics:{state:'source-ready'}};
 const windows=new Map(),inputs=new Map(JSON.parse(sessionStorage.getItem('inputs')||'[]'));let controller;
 const w={key:'blueprint',meta:{id:info.id,blueprintGraph:id},el:document.createElement('section')};w.el.className='window feature-author-document has-blueprint-toolbar';Object.assign(w.el.style,{left:'40px',top:'40px',width:'850px',height:'600px'});w.el.innerHTML='<header class="window-title"><span class="caption"><strong>F</strong></span></header><div class="window-body"></div>';w.body=$('.window-body',w.el);$('#workspace').append(w.el);windows.set(w.key,w);
 const requests=[],toasts=[];const api={$, $$,esc,authorInputs:inputs,current:{projectId:'fixture-project'},windows,view:{update:async()=>{},call:async(endpoint,input)=>{requests.push({endpoint,input});if(endpoint==='blueprint'&&input.action==='read')return structuredClone(data);throw Error('Unexpected provider/mutation: '+endpoint);}},openWindow:()=>w,focus:()=>{},persist:()=>sessionStorage.setItem('inputs',JSON.stringify([...inputs])),persistCopyInputs:async()=>{},controls:()=>{},toast:t=>toasts.push(t),work:async fn=>{try{await fn();}catch(e){toasts.push(e.message);return false;}},modal:(title,html,mount)=>{const root=document.createElement('section');root.className='modal';root.setAttribute('role','dialog');root.setAttribute('aria-label',title);root.innerHTML='<h2>'+esc(title)+'</h2>'+html;document.body.append(root);mount(root,()=>root.remove());}};
 controller=createFeatureAuthoring(api);globalThis.fixture={api,w,data,inputs,requests,toasts,open:async()=>controller.restoreInWork({...w.meta,id:info.id,blueprintGraph:id})};await fixture.open();
}"""
def checked(t):checks.append(t);(case/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2));print('PASS '+t,flush=True)
def edit(d,region,text):
 field=d.locator('[data-code-source]');field.evaluate('(el,region)=>{const spans=[...el.closest(".bp-script-editor").querySelectorAll("[data-code-highlight]>span")],part=spans.find(p=>p.dataset.codeRegion===region);if(!part)throw Error("source region missing");const start=spans.slice(0,spans.indexOf(part)).reduce((n,p)=>n+p.textContent.length,0);el.setSelectionRange(start,start+part.textContent.length)}',region);page.keyboard.insert_text(text)
def open_code():page.locator('[data-internal-code]').click();return page.get_by_role('dialog',name='C# Script · 실행 선택',exact=True)
def cells():return page.evaluate('()=>[...fixture.inputs]')
def regions(d):return d.locator('[data-code-highlight]>span[data-code-region]').evaluate_all('els=>Object.fromEntries(els.map(e=>[e.dataset.codeRegion,e.textContent]))')
try:
 with sync_playwright() as p:
  expect.set_options(timeout=10000);browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1280,'height':900});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url+'/fixture');page.evaluate(bootstrap)
  d=open_code();bad='    NoBranch = 0,\n    Ready = , // 미완성 한글 😀\n';body='// 복원할 본문 한글 😀\nreturn Result.Ready;';helpers='private static int Keep() => 42;';edit(d,'enum',bad);edit(d,'body',body);edit(d,'helpers',helpers);page.evaluate('()=>fixture.open()');expect(page.locator('.bp-function-card')).to_have_count(1);saved=cells();assert len(saved)==1 and saved[0][1]['type']=='retained-conflict';held=json.loads(saved[0][1]['text']);assert held['sections']=={'enum':bad,'body':body,'helpers':helpers};assert page.evaluate('()=>fixture.data.nodes[0].source')=='return Result.Ready;';checked('강제 재진입은 불완전 enum/본문/보조 함수 원문을 보관하고 원본 카드·계약을 파괴하지 않는다')
  page.locator('[data-bp-add-branch]').click();assert cells()==saved;assert page.evaluate('()=>fixture.toasts.length')>0;assert not errors,errors;checked('불완전 C# 원문이 있을 때 다른 분기 편집은 안내와 함께 거절하고 원문을 덮어쓰지 않는다')
  d=open_code();assert regions(d)==held['sections'];d.locator('[data-code-save]').click();expect(d.locator('[data-code-error]')).to_be_visible();assert cells()==saved;d.locator('[data-code-cancel]').click();assert cells()==saved;checked('재진입 C# 창은 불완전 원문을 그대로 편집하며 잘못된 저장과 취소는 보관한 입력을 지우지 않는다')
  page.reload();page.evaluate(bootstrap);expect(page.locator('.bp-function-card')).to_have_count(1);assert cells()==saved;d=open_code();assert regions(d)==held['sections'];page.screenshot(path=str(case/'restored-incomplete-csharp.png'));edit(d,'enum','    NoBranch = 0,\n    Ready = 1,\n');d.locator('[data-code-save]').click();accepted=cells();assert len(accepted)==1 and accepted[0][1]['type']=='enum-code';v=json.loads(accepted[0][1]['text']);assert v['source']==body and v['helpers']==helpers and [m['id'] for m in v['executionEnum']['members']]==['next','ready'];assert not any(r['input'].get('action')!='read' for r in page.evaluate('()=>fixture.requests'));checked('새 렌더러에서 보관 원문을 복원하고 enum만 수정하면 같은 안정 ID/본문/보조 함수로 정상 개인 초안을 회복한다')
  before=accepted;page.evaluate("()=>{fixture.data.sources[1].hash='f'.repeat(64);fixture.data.basis='read-v2';return fixture.open();}");assert cells()==before;page.locator('[data-bp-save]').click();assert cells()==before;assert not any(r['input'].get('action')!='read' for r in page.evaluate('()=>fixture.requests'));assert any('바뀌었' in t for t in page.evaluate('()=>fixture.toasts'));checked('복원 중 원본이 실제 바뀌면 보관 입력을 새 버전으로 자동 승격하지 않고 저장을 거절한다')
  assert not errors,errors;browser.close()
finally:server.shutdown()
record={'controlledRenderer':True,'actualEngine':False,'checks':checks,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
