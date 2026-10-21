"""Shipped project review/window/CSS with controlled permission snapshots, no accounts.
UI boundary checks only; actual backend authorization is tested separately.
"""
import http.server,json,mimetypes,pathlib,re,subprocess,sys,tempfile,threading
from playwright.sync_api import sync_playwright,expect
repo=pathlib.Path(sys.argv[1]).resolve();root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-project-review-'))
source=(repo/'examples/editor-home/ui/v508-runtime.js').read_text();production=source[source.index('// Present the existing per-request'):source.index('function showAugment(')]
baseline=subprocess.check_output(['git','show','df9ef8263d0e422bc44657dc0507351942d7b113:examples/editor-home/ui/v508-runtime.js'],cwd=repo,text=True);before=baseline[baseline.index('function showPreview(){'):baseline.index('function showAugment(')]
policy=(repo/'packs/agent-codex/Permission.csbody').read_text();disclosures=json.loads('['+re.findall(r'\["disclosures"\]=new System.Text.Json.Nodes.JsonArray\((.*?)\),\["diagnostics"\]',policy)[-1]+']')
ids=['contentApproved','usageApproved','processApproved','managedCredentialApproved','managedConfigurationApproved','managedStorageApproved'];english=['Send reviewed project context and tool results','Consume model usage / possible charges','Run selected executable for this turn','Use my separately signed-in account','Read selected managed configuration','Write selected managed storage / scratch']
preview={'token':'owned-token','kind':'chat','connection':'Confectory.Agent.Codex::Connection','message':'지금 뭘 할 수 있지?','target':'','rights':'Current owned namespace: list/read/inspect and stage/create draft only; no Confirm or other projects. Provider process/credential rights require separate displayed consent.','helperContext':{'helper':'PRIVATE-helper-id','projectId':'PRIVATE-project-id','profile':{'personality':'친절하게 설명해요.','speciality':'프로젝트 제작'},'membership':{'kind':'global'},'memory':[{'scope':'project','text':'선택한 프로젝트 기억'},{'scope':'common','text':'선택한 공통 기억'}]},'pins':{'model':'fixture-model','connectionMethod':'local-cli','executable':'/PRIVATE/codex','managedHome':'/PRIVATE/home','protocolVerified':True,'verificationId':'PRIVATE-id','verificationFingerprint':'PRIVATE-proof'},'limits':{'maxTurns':1,'maxDynamicToolCalls':32,'turnTimeoutSeconds':90,'maxInputCharacters':65536,'maxDisplayedOutputBytes':32768,'maxModelRequests':None,'hardModelRequestCapEnforced':False},'diagnostics':{'accountVerified':True,'checks':[{'label':'선택한 Codex 실행 파일','status':'파일 있음 · 버전 미확인'},{'label':'기존 ChatGPT 로그인','status':'미확인 · 승인된 실행에서 공식 계정 조회 후 확인'}]},'disclosures':disclosures,'canStart':True,'approvals':{},'requirements':[{'id':id,'label':label} for id,label in zip(ids,english)]}
fixture='''<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/runtime.css"><style>body{margin:0}#workspace{position:relative;width:100vw;height:100vh;overflow:hidden}</style><div id="workspace"></div><script type="module">
import {createWorkspaceRuntime} from '/workspace.js';
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)],esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let busy=false,current={title:'테스트 프로젝트',aiPreview:PREVIEW};const helpers=[{id:'PRIVATE-helper-id',name:'루미'}],calls=[];
const project={objects:[],layout:[],workspaces:[],workspaceView:{x:0,y:0,scale:1}};
const workspaceRuntime=createWorkspaceRuntime({$,$$,esc,project,page:'work',persist(){},toast(){},contextMenu(){}}),windows=workspaceRuntime.state.windows;
const {openWindow,closeWindow}=workspaceRuntime;
function controls(){previewControls();}function updateHelperPresentations(){}
async function work(action){if(busy)return;busy=true;controls();try{await action();}catch(error){globalThis.lastError=error.message;}finally{busy=false;controls();}}
const view={async call(endpoint,input){calls.push({endpoint,input});const p=current.aiPreview;if(endpoint==='permission'){if(p.token!==input.token)throw Error('stale');p.approvals[input.id]=input.approved;}if(endpoint==='startAI'){if(!p.canStart||!p.requirements.every(r=>p.approvals[r.id]===true))throw Error('denied');}if(endpoint==='cancelPreview')current.aiPreview=null;}};
CODE
showPreview();globalThis.fixture={current,calls,show(){showPreview()},reset(p){current.aiPreview=structuredClone(p);showPreview()},clamp(){workspaceRuntime.clampWindows()}};
</script>'''.replace('PREVIEW',json.dumps(preview,ensure_ascii=False))
class Handler(http.server.BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  name=self.path.lstrip('/').split('?',1)[0]
  if name in ('after.html','before.html'):body=fixture.replace('CODE',production if name=='after.html' else before).encode();mime='text/html'
  else:
   path=repo/'examples/editor-home/ui'/name
   if pathlib.Path(name).name!=name or path.suffix not in ('.js','.css'):self.send_error(404);return
   body=path.read_bytes();mime=mimetypes.guess_type(name)[0]
  self.send_response(200);self.send_header('Content-Type',mime);self.end_headers();self.wfile.write(body)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();origin='http://127.0.0.1:'+str(server.server_port);errors=[];measurements=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu']);page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
  for variant in ('before','after'):
   page.goto(origin+'/'+variant+'.html');expect(page.locator('#ai-start')).to_be_disabled();expect(page.locator('[data-permission]')).to_have_count(6);page.screenshot(path=str(root/(variant+'.png')));measurements.append({'variant':variant,'window':page.locator('.window').bounding_box(),'bodyScrollHeight':page.locator('.window-body').evaluate('e=>e.scrollHeight'),'visibleTextLength':len(page.locator('.window-body').inner_text())})
  assert measurements[0]['window']==measurements[1]['window'],measurements
  body=page.locator('.window-body');text=body.inner_text();assert 'Codex · fixture-model' in text and '받는 서비스: OpenAI' in text and '금액 상한은 보장되지' in text and '다른 프로젝트 접근·최종 반영·프로젝트 실행은 허용하지' in text
  for forbidden in ('PRIVATE','Confectory.Agent.Codex::Connection','environments=[]','ten minutes','버전 미확인','계정 미확인','"pins"'):assert forbidden not in body.inner_text(),forbidden
  expect(page.locator('[data-chat-readiness]')).to_contain_text('정보 확인됨');assert not page.evaluate('fixture.calls.length');assert page.locator('[data-permission]:checked').count()==0
  # Exact optional transmitted settings/memory remain readable, without internal identity/path JSON.
  page.locator('summary').first.click();expect(body).to_contain_text('선택한 프로젝트 기억');expect(body).to_contain_text('선택한 공통 기억');assert 'PRIVATE' not in body.inner_text();page.locator('summary').first.click()
  for i,id in enumerate(ids):
   page.locator('[data-permission="'+id+'"]').check()
   if i<5:expect(page.locator('#ai-start')).to_be_disabled()
  expect(page.locator('#ai-start')).to_be_enabled();assert page.evaluate("fixture.calls.filter(c=>c.endpoint==='startAI').length")==0;page.locator('#ai-start').click();assert page.evaluate("fixture.calls.filter(c=>c.endpoint==='startAI').length")==1
  # New previews never reuse choices; unknown rights stay visible and require a choice.
  extra=json.loads(json.dumps(preview));extra['requirements'].append({'id':'extraApproved','label':'새 권한 설명'});page.evaluate('p=>fixture.reset(p)',extra);assert page.locator('[data-permission]:checked').count()==0
  for id in ids:page.locator('[data-permission="'+id+'"]').check()
  expect(page.locator('#ai-start')).to_be_disabled();expect(body).to_contain_text('추가 권한: 새 권한 설명');page.locator('#cancel-preview').click();assert page.evaluate("fixture.calls.filter(c=>c.endpoint==='startAI').length")==1;assert page.evaluate('fixture.current.aiPreview') is None
  for status in ('stale','missing','expired','cancelled'):
   value=json.loads(json.dumps(preview));value.update(canStart=False,blockedReason='연결 확인이 필요해요. [verification_'+status+']');value['pins']['protocolVerified']=False;value['diagnostics']['accountVerified']=False;page.evaluate('p=>fixture.reset(p)',value)
   expect(page.locator('[data-chat-readiness]')).to_contain_text('확인이 필요');expect(body).to_contain_text('[verification_'+status+']')
   for id in ids:page.locator('[data-permission="'+id+'"]').check()
   expect(page.locator('#ai-start')).to_be_disabled()
  page.evaluate('p=>fixture.reset(p)',preview)
  for width,height in ((900,760),(600,800),(375,667),(320,480)):
   page.set_viewport_size({'width':width,'height':height});page.evaluate('fixture.clamp()');page.locator('#cancel-preview').scroll_into_view_if_needed();r=page.locator('.window').bounding_box();assert r['width']<=width+1 and r['height']<=height+1;assert body.evaluate('e=>e.scrollWidth<=e.clientWidth+1');expect(page.locator('#cancel-preview')).to_be_in_viewport();expect(page.locator('[data-permission]')).to_have_count(6);page.screenshot(path=str(root/('after-'+str(width)+'.png')))
  assert not errors,errors;browser.close()
 (root/'evidence.json').write_text(json.dumps({'measurements':measurements,'checks':['unchanged window geometry','six unchecked explicit choices','no start until all choices','new preview choices empty','unknown right visible and unapproved','cancel does not dispatch','stale/missing/expired/cancelled cannot start','accurate evidence-derived readiness','visible material recipient/scope/cost/rights','readable exact optional context','small viewport internal scroll without horizontal overflow'],'actualBackendOrWindows':False},ensure_ascii=False,indent=2));print('PASS project review actual renderer/window + owned snapshots '+str(root))
finally:server.shutdown();server.server_close()
