#!/usr/bin/python3
"""Owned fixture ONLY. No credential, OAuth, model, tool execution, or outbound network."""
import json,os,pathlib,sys,threading,time
ROOT=pathlib.Path('__OWNED_ROOT__')
def control():return json.loads((ROOT/'control.json').read_text()) if (ROOT/'control.json').exists() else {}
c=control()
if sys.argv[1:]==['--version']:
 (ROOT/'version-ready').write_text(str(os.getpid()))
 while control().get('holdVersion'):time.sleep(.02)
 print('codex '+c.get('version','0.159.0-alpha.3'));sys.exit(0)
with (ROOT/'process-starts').open('a') as process_log:process_log.write(str(os.getpid())+'\n')
args=sys.argv[1:];assert args[:4]==['app-server','--stdio','--strict-config','-c'] and args[4]=='web_search="disabled"'
denied={'shell_tool','shell_snapshot','apps','plugins','connectors','browser_use','computer_use','image_generation','imagegenext','in_app_browser','browser_use_external','code_mode','code_mode_host','multi_agent','multi_agent_v2','hooks','plugin_hooks','codex_hooks','remote_plugin','tool_suggest','tool_search','request_permissions_tool','deferred_executor','memories','memory_tool'}
assert {args[i+1] for i,a in enumerate(args) if a=='--disable'}==denied
assert args[-4:]==['-c','notify=[]','-c','plugins.unified-computer-use@openai-bundled.enabled=false']
assert os.environ.get('CODEX_HOME') and all(k not in os.environ for k in ['HOME','OPENAI_API_KEY','OPENAI_AUTH_TOKEN'])
home=pathlib.Path(os.environ['CODEX_HOME']);auth='cli_auth_credentials_store="file"' in args
if auth:assert (home/'config.toml').read_text()=='cli_auth_credentials_store = "file"\n'
outlock=threading.Lock()
def send(value):
 with outlock:print(json.dumps(value),flush=True)
def complete():
 while not (ROOT/'complete-login').exists():time.sleep(.02)
 (home/'.owned-signed-in').write_text('OWNED TEST METADATA ONLY')
 send({'method':'account/login/completed','params':{'loginId':'foreign' if control().get('foreignCompletion') else 'owned-login','success':True}})
for line in sys.stdin:
 message=json.loads(line);method=message.get('method');params=message.get('params',{})
 with (ROOT/'requests.jsonl').open('a') as log:log.write(json.dumps({'method':method,'params':params,'home':str(home),'login':auth})+'\n')
 result={}
 if method=='initialize':result={'userAgent':'confectory/'+control().get('version','0.159.0-alpha.3')+' (OWNED FIXTURE)'}
 elif method=='initialized':continue
 elif method=='account/login/start':
  assert auth and params=={'type':'chatgptDeviceCode'}
  result={'type':'chatgptDeviceCode','loginId':'owned-login','verificationUrl':'https://invalid.example/blocked' if control().get('invalidUrl') else 'https://auth.openai.com/codex/device','userCode':'TEST-4240'}
  send({'id':message['id'],'result':result});threading.Thread(target=complete,daemon=True).start();continue
 elif method=='account/login/cancel':
  assert auth and params=={'loginId':'owned-login'};result={'status':'canceled'}
 elif method=='account/read':
  assert params=={'refreshToken':False};result={'account':{'type':'chatgpt','email':'OWNED TEST ONLY','planType':'unknown'} if (home/'.owned-signed-in').exists() else None,'requiresOpenaiAuth':True}
 elif method=='config/read':result={'config':{'model_provider':'openai','model_providers':{},'features':{name:False for name in denied},'web_search':'disabled','plugins':{},'mcp_servers':{}}}
 elif method=='experimentalFeature/list':result={'data':[{'name':name,'enabled':False,'stage':'stable'} for name in denied-{'connectors','imagegenext','codex_hooks','memory_tool'}],'nextCursor':None}
 elif method=='configRequirements/read':result={'requirements':None}
 elif method=='model/list':result={'data':[{'id':'owned-protocol-fixture','model':'owned-protocol-fixture','displayName':'OWNED TEST MODEL','inputModalities':['text']}],'nextCursor':None}
 else:raise AssertionError('Preparation must never make model or tool calls: '+str(method))
 if 'id' in message:send({'id':message['id'],'result':result})
