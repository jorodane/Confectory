"""Render shipped Codex login controls for isolated presentation snapshots.
No account, process, provider request or permission is created by this harness.
Backend transitions are checked separately by editor_codex_onboarding.py.
"""
import json,pathlib,re,sys,tempfile
from playwright.sync_api import sync_playwright,expect

repo=pathlib.Path(sys.argv[1]).resolve();out=pathlib.Path(tempfile.mkdtemp(prefix='confectory-login-state-'))
source=(repo/'examples/editor-home/ui/v508-runtime.js').read_text()
presentation=source[source.index('function codexLoginPresentation('):source.index('let connectionDialogCleanup=')]
start=source.index(' const renderCodex=');render=source[start:source.index(' let renderedRevision=',start)]
styles='\n'.join((repo/'examples/editor-home/ui'/name).read_text() for name in ('style.css','consumer.css','runtime.css'))
# Keep the shipped CSS rules; omit the external font import in this offline harness.
styles=re.sub(r'@import\s+url\([^)]*\)\s*;','',styles)
script='''
const $=(s,r=document)=>r.querySelector(s),esc=v=>{const d=document.createElement('div');d.textContent=String(v??'');return d.innerHTML;};
const selected={id:'Confectory.Agent.Codex::Connection'},root=document.querySelector('.modal'),body=document.querySelector('[data-connection-form]');
let current={},flowStamp=null,browserRecord=null,codexReadinessAttempted=false;
globalThis.calls=[];const view={call:async(endpoint,args)=>{calls.push({endpoint,args});}},flowAction=(action,args={})=>calls.push({action,args}),run=async fn=>fn(),controls=()=>{},alive=()=>true,maybeFinishIntro=()=>{};
root._retireConnectionDialog=()=>calls.push({action:'close'});
PRESENTATION
RENDER
function render(){renderCodex(body);}
globalThis.snapshot=(value,attempted=false)=>{current=value;flowStamp=null;codexReadinessAttempted=attempted;calls.length=0;render();};
'''.replace('PRESENTATION',presentation).replace('RENDER',render)
identity={'fingerprint':'a'*64,'email':'fixture@fixture.invalid'}
def agent(state='ready',known=True):
 return {'id':'Confectory.Agent.Codex::Connection','state':state,'model':'fixture-model','accountIdentity':identity if known else None,'readiness':{'state':state,'code':'fixture-'+state,'message':'등록한 연결 확인 · '+state}}
def value(flow=None,a=None):return {'codexOnboarding':flow or {'state':'idle'},'helperAgents':{'agents':[a] if a else []}}
checks=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':900,'height':700});errors=[];external=[]
 page.on('pageerror',lambda e:errors.append(str(e)));page.route('**/*',lambda r:(external.append(r.request.url),r.abort()))
 page.set_content('<style>'+styles+'</style><main id="app"></main><div class="modal-overlay"><div class="modal agent-connect-modal"><button data-close>×</button><h2>Agent 추가</h2><div data-connection-form></div></div></div>');page.add_script_tag(content=script)
 def show(label,state):
  page.evaluate('v=>snapshot(v)',state);assert page.evaluate('calls.length')==0;checks.append(label)
 def initial(label,state):
  show(label,state);expect(page.locator('[data-cli-login]')).to_have_text('로그인');expect(page.locator('[data-cli-retry],[data-cli-change-account],[data-cli-new-login]')).to_have_count(0)
  assert '다른 계정' not in page.locator('[data-connection-form]').inner_text()
 initial('pristine',value());page.screenshot(path=str(out/'initial.png'))
 candidates=value();candidates['connectionSetup']={'mode':'existing','discovery':{'executables':[{'selectable':True}],'homes':[{'selectable':True}]}};initial('candidates alone do not imply account/login attempt',candidates)
 settings=value();settings['helperAgents']['savedSettings']={'Confectory.Agent.Codex::Connection':True};initial('saved settings alone',settings)
 initial('legacy unverified registration',value(a=agent('unverified',False)))
 malformed=agent('unverified');malformed['accountIdentity']={'fingerprint':'unverified','email':'unverified@fixture.invalid'};initial('invalid identity is not known account',value(a=malformed))
 initial('cancelled login',value({'state':'cancelled','message':'연결을 취소했어요.'}))
 blocked={'state':'failed','code':'provider-tool-policy-unsupported','failureAction':'setup','loginAttempted':False,'message':'Codex의 연결 제한을 확인하지 못했어요.','retryable':True,'canLogin':True,'diagnostics':{'failure':{'code':'provider-tool-policy-unsupported','stage':'policy-check','detail':'enabled-plugin-entry'}}}
 initial('pre-auth policy block keeps Login and real diagnostics',value(blocked));expect(page.locator('[role=status]')).to_contain_text('로그인은 아직 시작하지 않았어요');page.locator('[data-cli-diagnostics] summary').click();expect(page.locator('[data-cli-diagnostics] pre')).to_contain_text('enabled-plugin-entry');page.set_viewport_size({'width':640,'height':500});page.screenshot(path=str(out/'preparation-blocked.png'));assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.locator('[data-cli-login]').click();assert page.evaluate('calls[0].action')=='new-login'
 page.set_viewport_size({'width':900,'height':700})
 startblocked={**blocked,'canLogin':False};show('initial process failure repeats preparation through Login',value(startblocked));page.locator('[data-cli-login]').click();assert page.evaluate('calls[0].action')=='begin'
 failed={'state':'failed','failureAction':'login','loginAttempted':True,'message':'공식 로그인 완료를 확인하지 못했어요.','retryable':True,'canLogin':True}
 show('explicit login failure has login-specific retry',value(failed));expect(page.locator('[data-cli-retry]')).to_have_text('로그인 다시 시도');expect(page.locator('[data-cli-new-login]')).to_have_count(0);page.screenshot(path=str(out/'login-failed.png'));page.locator('[data-cli-retry]').click();assert page.evaluate('calls[0]')=={'action':'retry','args':{'approved':True}}
 show('explicit install failure has install-specific retry',value({**failed,'failureAction':'install'}));expect(page.locator('[data-cli-retry]')).to_have_text('설치 다시 시도')
 show('login complete does not mean connection ready',value({**failed,'failureAction':'connection','loginCompleted':True,'message':'Codex 연결 제한을 확인하지 못했어요.'}));expect(page.locator('[role=status]')).to_contain_text('로그인 절차는 끝났어요');expect(page.locator('[data-cli-retry]')).to_have_text('연결 다시 확인');expect(page.locator('[data-cli-new-login]')).to_have_count(0)
 show('known connected account',value(a=agent()));expect(page.locator('[data-cli-change-account]')).to_have_text('계정 변경');expect(page.locator('[data-cli-account-name]')).to_have_text(identity['email']);page.screenshot(path=str(out/'connected.png'))
 show('automatic registered check is not login failure',value(a=agent('blocked')));expect(page.locator('[data-cli-retry]')).to_have_text('연결 확인');page.locator('[data-cli-retry]').click();expect(page.locator('[data-cli-retry]')).to_have_text('연결 다시 확인');assert page.evaluate('calls[0].args.action')=='retry-readiness'
 show('registered auth-required allows account choice',value(a=agent('auth-required')));expect(page.locator('[data-cli-new-login]')).to_have_text('계정 변경')
 show('account mismatch does not enable check bypass',value(a=agent('account-mismatch')));expect(page.locator('[data-cli-retry]')).to_have_count(0);expect(page.locator('[data-cli-new-login]')).to_have_text('계정 변경')
 show('offline stays explicit reconnect',value(a=agent('offline')));expect(page.locator('[data-cli-login]')).to_have_text('다시 연결')
 show('cleanup failure cannot start another job',value({**failed,'retryable':False,'canLogin':False}));expect(page.locator('[data-cli-login],[data-cli-retry],[data-cli-new-login]')).to_have_count(0)
 show('discovered account is not registered account change',value({'state':'account-choice','accounts':[{'id':'owned','identity':identity}],'token':'fixture'}));expect(page.locator('[data-cli-new-login]')).to_have_text('로그인')
 assert not errors and not external,(errors,external);browser.close()
record={'checks':checks,'count':len(checks),'pageErrors':errors,'externalRequests':external,'actualLoginOrInference':False,'backendTransitionsExecuted':False,'evidence':str(out)};(out/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2));print('PASS shipped Codex first-login presentation and action matrix')
