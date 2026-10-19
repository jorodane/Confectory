#!/usr/bin/python3
import json,sys,time,os
control_path=os.path.join(os.path.dirname(__file__),'owned-control.json')
control=json.load(open(control_path)) if os.path.exists(control_path) else {}
if sys.argv[1:]==['--version']:print('codex '+control.get('version','0.159.0-alpha.3'));sys.exit(0)
thread="owned-thread-"+str(os.getpid());turn="owned-turn-"+str(os.getpid())
assert sys.argv[1:5]==['app-server','--stdio','--strict-config','-c']
assert sys.argv[5]=='web_search="disabled"'
assert sys.argv[6:56:2]==['--disable']*25 and sys.argv[56:]==['-c','notify=[]']
denied={'shell_tool','shell_snapshot','apps','plugins','connectors','browser_use','computer_use','image_generation','imagegenext','in_app_browser','browser_use_external','code_mode','code_mode_host','multi_agent','multi_agent_v2','hooks','plugin_hooks','codex_hooks','remote_plugin','tool_suggest','tool_search','request_permissions_tool','deferred_executor','memories','memory_tool'}
assert set(sys.argv[7:56:2])==denied
open(os.path.join(os.path.dirname(__file__),'owned-launch.json'),'w').write(json.dumps(sys.argv[1:]))
assert os.environ.get("CODEX_HOME") and "OPENAI_API_KEY" not in os.environ and "HOME" not in os.environ
def read():
 line=sys.stdin.readline()
 if not line:sys.exit(0)
 x=json.loads(line)
 with open(os.path.join(os.path.dirname(__file__),'owned-requests.jsonl'),'a') as f:f.write(json.dumps(x)+'\n')
 return x
def send(x):print(json.dumps(x),flush=True)
def hold(method):
 if control.get('holdMethod')!=method:return
 marker=os.path.join(os.path.dirname(__file__),control['holdId'])
 open(marker+'-ready','w').write(str(os.getpid()))
 deadline=time.monotonic()+20
 while not os.path.exists(marker+'-release'):
  assert time.monotonic()<deadline;time.sleep(.01)
a=read();assert a['method']=='initialize' and a['params']['capabilities']['experimentalApi'];send({'id':a['id'],'result':{'userAgent':'confectory/'+control.get('version','0.159.0-alpha.3')+' (OWNED FIXTURE ONLY)'}})
assert read()['method']=='initialized'
a=read();assert a['method']=='account/read' and a['params']=={'refreshToken':False}
hold('account/read')
account=None if 'no-account' in __file__ or control.get('noAccount') else {'type':'apiKey'} if 'api-account' in __file__ else {'type':'chatgpt','email':'OWNED FIXTURE, NOT A REAL ACCOUNT','planType':'unknown'}
send({'id':a['id'],'result':{'account':account,'requiresOpenaiAuth':True}})
if not account or account['type']!='chatgpt':read();sys.exit(0)
a=read();assert a['method']=='config/read' and a['params']=={'includeLayers':False}
while control.get('holdCheck'):
 time.sleep(.01)
 control=json.load(open(control_path))
send({'id':a['id'],'result':{'config':{'model_provider':'openai','model_providers':{'owned-unreviewed':{}} if 'custom-provider' in __file__ else {},'features':{name:bool(control.get('unsafeTools') and name=='shell_tool') for name in sorted(denied,reverse=bool(os.getpid()%2))},'web_search':'disabled','plugins':{},'mcp_servers':{},'ownedRevision':control.get('configRevision',0)}}})
a=read();assert a['method']=='experimentalFeature/list';send({'id':a['id'],'result':{'data':[{'name':name,'enabled':bool(control.get('runtimeUnsafe') and name=='apps'),'stage':'stable'} for name in sorted(denied-{'connectors','imagegenext','codex_hooks','memory_tool'})],'nextCursor':None}})
a=read();assert a['method']=='configRequirements/read';send({'id':a['id'],'result':{'requirements':None}})
pages=control.get('modelPages',[['owned-protocol-fixture']])
for index,models in enumerate(pages):
 a=read();assert a['method']=='model/list'
 assert a['params'].get('cursor')==(str(index) if index else None)
 send({'id':a['id'],'result':{'data':[{'id':model,'model':model,'displayName':'OWNED FIXTURE ONLY '+model,'inputModalities':['text']} for model in models],'nextCursor':str(index+1) if index+1<len(pages) else None}})
a=read();assert a['method']=='thread/start' and a['params']['ephemeral'] and a['params']['sandbox']=='read-only' and a['params']['approvalPolicy']=='never'
assert a['params']['environments']==[]
assert a['params']['allowProviderModelFallback'] is False
dynamic_tools=a['params']['dynamicTools']
assert all(t['type']=='function' and 'inputSchema' in t for t in a['params']['dynamicTools'])
assert os.getcwd()==a['params']['cwd'];hold('thread/start');send({'id':a['id'],'result':{'thread':{'id':thread,'environments':['unexpected'] if 'retained-environment' in __file__ else []},'instructionSources':[{'path':'owned-unreviewed-instruction'}] if 'instruction-source' in __file__ else [],'model':'owned-protocol-fixture','modelProvider':'openai'}})
a=read();assert a['method']=='turn/start' and a['params']['sandboxPolicy']=={'type':'readOnly','networkAccess':False}
assert a['params']['environments']==[]
open(os.path.join(os.path.dirname(__file__),'turn-start-'+os.path.basename(__file__)),'w').write('started')
text=a['params']['input'][0]['text'];assert 'authorization' not in text and 'toolCapability' not in text and 'credentialReference' not in text
mode=json.loads(text)['message'];send({'method':'turn/started','params':{'threadId':thread,'turn':{'id':turn,'status':'inProgress'}}});send({'id':a['id'],'result':{'turn':{'id':turn,'status':'inProgress'}}})
if mode.startswith('global-'):
 payload=json.loads(text);assert payload['kind']=='helper-global-chat' and payload['projectId']=='' and payload['context']['projectId']=='' and payload['context']['membership']['kind']=='global'
 assert dynamic_tools==[] and all(m['scope']=='common' for m in payload['context']['memory'])
 assert 'PROJECT PRIVATE' not in text and 'LEGACY PRIVATE' not in text
 if mode=='global-hold':
  b=read();assert b['method']=='turn/interrupt';sys.exit(0)
 send({'method':'item/completed','params':{'threadId':thread,'turnId':turn,'item':{'id':'answer','type':'agentMessage','text':'OWNED GLOBAL CODEX FIXTURE: actual adapter, no account or inference.'}}})
 send({'method':'turn/completed','params':{'threadId':thread,'turn':{'id':turn,'status':'completed'}}});read();sys.exit(0)
if mode.startswith('ui-'):
 if mode=='ui-hold':
  b=read();assert b['method']=='turn/interrupt' and b['params']=={'threadId':thread,'turnId':turn};open(os.path.join(os.path.dirname(__file__),'owned-interrupt-marker'),'w').write(turn);sys.exit(0)
 send({'method':'item/completed','params':{'threadId':thread,'turnId':turn,'item':{'id':'answer','type':'agentMessage','text':'OWNED UI FIXTURE: no real Codex account or inference.'}}})
 send({'method':'turn/completed','params':{'threadId':thread,'turn':{'id':turn,'status':'completed'}}});read();sys.exit(0)
if mode in ('hold-a','hold-b'):
 assert json.loads(text)['context']['profile']['helper']==mode
 open(os.path.join(os.path.dirname(__file__),mode+'-ready'),'w').write(turn)
 if mode=='hold-a':
  b=read();assert b['method']=='turn/interrupt' and b['params']=={'threadId':thread,'turnId':turn}
  open(os.path.join(os.path.dirname(__file__),'hold-a-interrupted'),'w').write(turn);sys.exit(0)
 deadline=time.monotonic()+20
 while not os.path.exists(os.path.join(os.path.dirname(__file__),'release-helper-b')):
  assert time.monotonic()<deadline;time.sleep(.01)
 send({'method':'item/completed','params':{'threadId':thread,'turnId':turn,'item':{'id':'answer','type':'agentMessage','text':'OWNED LOOPBACK FIXTURE: helper B kept running.'}}})
 send({'method':'turn/completed','params':{'threadId':thread,'turn':{'id':turn,'status':'completed'}}})
 read();sys.exit(0)
if mode=='missing-turn':
 send({'method':'item/agentMessage/delta','params':{'threadId':thread,'itemId':'answer','delta':'UNOWNED OUTPUT'}});read();sys.exit(0)
if mode=='conflicting-message':
 send({'method':'item/agentMessage/delta','params':{'threadId':thread,'turnId':turn,'itemId':'answer','delta':'OWNED PREFIX'}})
 send({'method':'item/completed','params':{'threadId':thread,'turnId':turn,'item':{'id':'answer','type':'agentMessage','text':'DIFFERENT MESSAGE'}}});read();sys.exit(0)
if mode in ('usage-error','foreign-error'):
 send({'method':'error','params':{'threadId':thread if mode=='usage-error' else 'foreign-thread','turnId':turn,'willRetry':True,'error':{'message':'SECRET FIXTURE DETAIL MUST NOT BE DISPLAYED','codexErrorInfo':'usageLimitExceeded'}}})
 read();sys.exit(0)
if mode=='interrupted':
 send({'method':'turn/completed','params':{'threadId':thread,'turn':{'id':turn,'status':'interrupted'}}});read();sys.exit(0)
if mode=='cancel':
 b=read();assert b['method']=='turn/interrupt' and b['params']=={'threadId':thread,'turnId':turn};open(os.path.join(os.path.dirname(__file__),'owned-interrupt-marker'),'w').write(turn);sys.exit(0)
if mode=='foreign':
 send({'id':'foreign-request','method':'item/tool/call','params':{'threadId':'another-project','turnId':turn,'callId':'foreign','tool':'workspace_stage','arguments':{}}});time.sleep(1);sys.exit(0)
if mode=='namespace':
 send({'id':'outside-namespace','method':'item/tool/call','params':{'threadId':thread,'turnId':turn,'callId':'outside-namespace','tool':'workspace_read','arguments':{'projectId':'A','id':'Other.Project::Secret'}}});time.sleep(1);sys.exit(0)
if mode=='approval':
 send({'id':'native-request','method':'item/fileChange/requestApproval','params':{'threadId':thread,'turnId':turn}});b=read();assert b['id']=='native-request' and 'error' in b;sys.exit(0)
for n in range(2):
 send({'id':'rpc-'+str(n),'method':'item/tool/call','params':{'threadId':thread,'turnId':turn,'callId':'same-call','tool':'workspace_stage','arguments':{'projectId':'A','id':'Example.EditWorkspace::Counter','expectedRevision':0,'text':'object Example.EditWorkspace::Counter {value count = 3;}'}}})
 b=read();assert b['id']=='rpc-'+str(n) and b['result']['success'] and b['result']['contentItems'][0]['type']=='inputText'
 if n==0:first=b['result']
 else:assert b['result']==first
send({'method':'item/agentMessage/delta','params':{'threadId':thread,'turnId':turn,'itemId':'answer','delta':'Owned fixture staged '}})
for _ in range(2):
 send({'method':'item/completed','params':{'threadId':thread,'turnId':turn,'item':{'id':'answer','type':'agentMessage','text':'Owned fixture staged draft; review required.'}}})
send({'method':'turn/completed','params':{'threadId':thread,'turn':{'id':turn,'status':'completed'}}})
read()
