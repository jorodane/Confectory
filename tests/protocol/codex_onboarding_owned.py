#!/usr/bin/python3
"""Owned protocol fixture. Fake account metadata only; no OAuth or network."""
import json,os,pathlib,sys,threading,time,tomllib
ROOT=pathlib.Path('__FIXTURE_ROOT__')
CASE=pathlib.Path(json.loads((ROOT/'active.json').read_text())['case'])
def control():return json.loads((CASE/'control.json').read_text())
def record(method,params=None):
 value={'method':method,'params':params or {},'home':os.environ.get('CODEX_HOME',''),'pid':os.getpid()}
 fd=os.open(CASE/'requests.jsonl',os.O_WRONLY|os.O_CREAT|os.O_APPEND,0o600)
 try:os.write(fd,(json.dumps(value)+'\n').encode())
 finally:os.close(fd)
if sys.argv[1:]==['--version']:
 record('--version');(CASE/'version-started').write_text('owned')
 while control().get('holdVersion'):time.sleep(.02)
 if control().get('preAuthFailure')=='process-start-error':os.chmod(sys.argv[0],0o600)
 print('codex-cli '+control().get('version','0.159.0-alpha.3'));sys.exit(0)
args=sys.argv[1:];assert args[:3]==['app-server','--stdio','--strict-config']
denied={'shell_tool','shell_snapshot','apps','plugins','connectors','browser_use','computer_use','image_generation','imagegenext','in_app_browser','browser_use_external','code_mode','code_mode_host','multi_agent','multi_agent_v2','hooks','plugin_hooks','codex_hooks','remote_plugin','tool_suggest','tool_search','request_permissions_tool','deferred_executor','memories','memory_tool'}
assert {args[i+1] for i,a in enumerate(args) if a=='--disable'}==denied
assert all(k not in os.environ for k in ('HOME','OPENAI_API_KEY','OPENAI_AUTH_TOKEN'))
home=pathlib.Path(os.environ['CODEX_HOME']);login='cli_auth_credentials_store="file"' in args
table_args=[args[i+1] for i,a in enumerate(args) if a=='-c' and args[i+1].startswith('plugins={')]
if table_args:
 for prior in (CASE/'requests.jsonl').read_text().splitlines():
  row=json.loads(prior)
  if row['method']=='process' and row['home']==str(home):
   try:os.kill(row['pid'],0)
   except ProcessLookupError:continue
   raise AssertionError('Prior same-home process still alive before isolation restart')
record('process',{'login':login,'isolationOverride':bool(table_args)})
if control().get('preAuthFailure')=='process-exit' and not login:sys.exit(23)
if table_args and control().get('isolationFailure')=='exit':sys.exit(29)
outlock=threading.Lock()
def send(value):
 # Include required lifecycle metadata from the retained official CLI schema.
 params=value.get('params',{})
 if value.get('method')=='item/completed':params.setdefault('completedAtMs',0)
 for container in [params,value.get('result',{})]:
  if isinstance(container.get('turn'),dict):container['turn'].setdefault('items',[])
 with outlock:
  with (CASE/'responses.jsonl').open('a') as capture:capture.write(json.dumps(value)+'\n')
  wire=(json.dumps(value,ensure_ascii=False)+'\n').encode('utf-8')
  if control().get('splitUtf8'):
   for byte in wire:sys.stdout.buffer.write(bytes([byte]));sys.stdout.buffer.flush()
  else:sys.stdout.buffer.write(wire);sys.stdout.buffer.flush()
def finish():
 while not (CASE/'complete-login').exists():time.sleep(.02)
 account={'type':'chatgpt','email':control().get('loginEmail','new-account@fixture.invalid'),'planType':'plus'}
 if not (control().get('failLogin',False) or control().get('loginExpired')):(home/'.owned-account.json').write_text(json.dumps(account))
 send({'method':'account/login/completed','params':{'loginId':'owned-login','success':not (control().get('failLogin',False) or control().get('loginExpired')),'error':'Login expired' if control().get('loginExpired') else None}})
for line in sys.stdin:
 value=json.loads(line);method=value.get('method');params=value.get('params',{});record(method,params);result={}
 failure=control().get('preAuthFailure')
 if failure=='mixed-account-error' and home.name=='account-0':failure='account-error'
 if not login and method=={'initialize-error':'initialize','account-error':'account/read','model-error':'model/list'}.get(failure):
  send({'id':value['id'],'error':{'code':-32603,'message':'PRIVATE fixture diagnostic /home/fake-user token=NEVER-EXPOSE'}});continue
 if table_args and control().get('isolationFailure')==method:
  send({'id':value['id'],'error':{'code':-32603,'message':'PRIVATE isolation restart diagnostic'}});continue
 if method=='initialize':result={'userAgent':'confectory/'+control().get('version','0.159.0-alpha.3')+' (OWNED FIXTURE)'}
 elif method=='initialized':continue
 elif method=='account/login/start':
  assert login and params in ({'type':'chatgpt'},{'type':'chatgptDeviceCode'})
  if control().get('loginPortError'):
   send({'id':value['id'],'error':{'code':-32603,'message':'Address already in use (os error 10048) PRIVATE'}});continue
  if params['type']=='chatgpt':
   url='https://auth.openai.com/oauth/authorize?response_type=code&client_id=owned-fixture&redirect_uri=http%3A%2F%2F127.0.0.1%3A1455%2Fauth%2Fcallback&state=owned-state&code_challenge='+'A'*43+'&code_challenge_method=S256'
   if control().get('invalidBrowserUrl'):url=url.replace('127.0.0.1','remote.fixture.invalid')
   send({'id':value['id'],'result':{'type':'chatgpt','loginId':'owned-login','authUrl':url}})
  else:send({'id':value['id'],'result':{'type':'chatgptDeviceCode','loginId':'owned-login','verificationUrl':'https://auth.openai.com/codex/device','userCode':'TEST-4240'}})
  threading.Thread(target=finish,daemon=True).start();continue
 elif method=='account/login/cancel':assert params=={'loginId':'owned-login'};result={'status':'canceled'}
 elif method=='account/read':
  while control().get('holdAccount'):time.sleep(.01)
  assert params=={'refreshToken':False};p=home/'.owned-account.json';account=json.loads(p.read_text()) if p.exists() else None
  if control().get('hideAccount'):account=None
  if account and control().get('readEmail'):account['email']=control()['readEmail']
  if account and control().get('changedIdentity') and any(json.loads(x).get('method')=='thread/start' for x in (CASE/'requests.jsonl').read_text().splitlines()):account['email']='changed@fixture.invalid'
  result={'requiresOpenaiAuth':True,'account':account}
 elif method=='config/read':
  result={'config':{'model_provider':'openai','model_providers':{},'features':{name:False for name in denied},'web_search':'enabled' if control().get('rejectSearch') else 'disabled','plugins':({'owned-unexpected@fixture':{'enabled':True}} if control().get('rejectExtension') else {'unified-computer-use@openai-bundled':{'enabled':'plugins.unified-computer-use@openai-bundled.enabled=false' not in args}} if control().get('bundledPolicy') else {}),'mcp_servers':{},**({'model':control()['configuredModel']} if control().get('configuredModel') else {})}}
  preset=control().get('pluginPreset')
  if preset:
   result['config']['plugins']={'unified-computer-use@openai-bundled':{'enabled':False},'owned.extra@openai-bundled':{'enabled':True},'PRIVATE.owned-quote"\\name-한글🧁@fixture':{'enabled':True},'PRIVATE.unconfirmed@fixture':{}}
   if preset=='budget':result['config']['plugins']={str(i)+'@fixture':{'enabled':True} for i in range(129)}
  if control().get('postLoginPlugins') and not login and (home/'.owned-account.json').exists():result['config']['plugins']['PRIVATE.after-browser@fixture']={'enabled':True}
  if table_args and not control().get('rejectExtension'):
   for k,v in tomllib.loads(table_args[-1])['plugins'].items():result['config']['plugins'].setdefault(k,{}).update(v)
  if preset=='changed-after-override' and table_args:result['config']['plugins']['PRIVATE.new@fixture']={'enabled':True}
  if not table_args and control().get('isolationFailure')=='start':os.chmod(sys.argv[0],0o600)
  if not table_args and control().get('isolationFailure')=='file-change':
   with open(sys.argv[0],'a') as executable:executable.write('\n# OWNED isolation executable mutation\n')
  if control().get('holdIsolation') and table_args:
   (CASE/'isolation-started').write_text('owned')
   while control().get('holdIsolation'):time.sleep(.02)

 elif method=='experimentalFeature/list':result={'data':[{'name':name,'enabled':False,'stage':'stable'} for name in denied-{'connectors','imagegenext','codex_hooks','memory_tool'}],'nextCursor':None}
 elif method=='configRequirements/read':result={'requirements':None}
 elif method=='model/list':
  models=[] if control().get('noModels') else [{'id':'fixture-one','model':'fixture-one','displayName':'Owned model one','inputModalities':['text'],'isDefault':not control().get('noDefault')}]
  if not control().get('singleModel') and not control().get('noModels'):models.append({'id':'fixture-two','model':'fixture-two','displayName':'Owned model two','inputModalities':['text'],'isDefault':False})
  result={'data':models,'nextCursor':None}
 elif method=='thread/start':
  assert params['environments']==[] and params['ephemeral'] and params['approvalPolicy']=='never'
  result={'thread':{'id':'owned-thread','environments':[]},'instructionSources':[],'model':params['model'],'modelProvider':'openai'}
 elif method=='turn/start':
  assert params['environments']==[];content=json.loads(params['input'][0]['text']);assert content['kind']=='helper-global-chat' or (control().get('projectChat') and content['kind']=='project-chat' and content['projectId']==content['context']['projectId'] and content['projectId'])
  failure=control().get('turnFailure')
  if failure=='rpc-error':send({'id':value['id'],'error':{'code':-32602,'message':'PRIVATE turn payload token=NEVER-EXPOSE /owned/secret'}});continue
  if failure=='exit':print('PRIVATE stderr token=NEVER-EXPOSE /owned/secret',file=sys.stderr,flush=True);sys.exit(37)
  send({'id':value['id'],'result':{'turn':{'id':'owned-turn','status':'inProgress'}}})
  if failure=='bad-json':print('PRIVATE invalid JSON token=NEVER-EXPOSE',flush=True);continue
  if failure=='remote-bad-request':send({'method':'error','params':{'threadId':'owned-thread','turnId':'owned-turn','willRetry':False,'error':{'message':'PRIVATE prompt/account details token=NEVER-EXPOSE','codexErrorInfo':'badRequest'}}});continue
  if failure=='foreign-event':send({'method':'item/agentMessage/delta','params':{'threadId':'foreign-thread','turnId':'owned-turn','itemId':'answer','delta':'PRIVATE MUST NOT RENDER'}});continue
  if failure=='remote-http':send({'method':'error','params':{'threadId':'owned-thread','turnId':'owned-turn','willRetry':False,'error':{'message':'PRIVATE service token=NEVER-EXPOSE','additionalDetails':'PRIVATE','codexErrorInfo':{'httpConnectionFailed':{'httpStatusCode':503}}}}});continue
  if failure=='completed-error':send({'method':'turn/completed','params':{'threadId':'owned-thread','turn':{'id':'owned-turn','status':'failed','error':{'message':'PRIVATE token=NEVER-EXPOSE','codexErrorInfo':{'httpConnectionFailed':{'httpStatusCode':403}}}}}});continue
  text=control().get('replyText','OWNED CLI HELPER REPLY')
  send({'method':'item/agentMessage/delta','params':{'threadId':'owned-thread','turnId':'owned-turn','itemId':'answer','delta':text}})
  if failure=='bad-json-after-delta':print('PRIVATE invalid JSON token=NEVER-EXPOSE',flush=True);continue
  if failure=='invalid-utf8':sys.stdout.buffer.write(b'\xff\n');sys.stdout.buffer.flush();continue
  send({'method':'item/completed','params':{'threadId':'owned-thread','turnId':'owned-turn','item':{'id':'answer','type':'agentMessage','text':text}}})
  send({'method':'turn/completed','params':{'threadId':'owned-thread','turn':{'id':'owned-turn','status':'completed'}}});continue
 elif method=='turn/interrupt':result={}
 else:raise AssertionError('Undeclared owned fixture method: '+str(method))
 if 'id' in value:send({'id':value['id'],'result':result})
