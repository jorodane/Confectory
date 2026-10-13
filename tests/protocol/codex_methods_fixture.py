"""Owned Unix control-socket and Workspace API services. No account/model/network upstream."""
import base64, hashlib, http.server, json, pathlib, socket, struct, sys, threading
root=pathlib.Path(sys.argv[1]); root.mkdir(exist_ok=True)
records=[]; lock=threading.Lock()
def record(kind,value):
 with lock:
  records.append({'kind':kind,'value':value}); (root/'records.json').write_text(json.dumps(records))
def exact(stream,count):
 data=b''
 while len(data)<count:
  part=stream.recv(count-len(data))
  if not part: raise EOFError()
  data+=part
 return data
def ws_read(stream):
 a,b=exact(stream,2); length=b&127
 if length==126:length=struct.unpack('!H',exact(stream,2))[0]
 if length==127:length=struct.unpack('!Q',exact(stream,8))[0]
 assert length<=1048576 and b&128 and a&128
 mask=exact(stream,4); payload=exact(stream,length); payload=bytes(v^mask[i%4] for i,v in enumerate(payload))
 if a&15==8:raise EOFError()
 assert a&15==1
 return json.loads(payload)
def ws_send(stream,value):
 payload=json.dumps(value).encode(); length=len(payload)
 header=bytes([129,length]) if length<126 else bytes([129,126])+struct.pack('!H',length)
 stream.sendall(header+payload)
def control(stream,index):
 try:
  headers=b''
  while not headers.endswith(b'\r\n\r\n'):
   headers+=exact(stream,1); assert len(headers)<16384
  lines=headers.decode().split('\r\n'); assert lines[0].startswith('GET / ')
  fields={k.lower():v.strip() for k,v in (line.split(':',1) for line in lines[1:] if ':' in line)}
  assert 'authorization' not in fields and 'origin' not in fields
  accept=base64.b64encode(hashlib.sha1((fields['sec-websocket-key']+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()).decode()
  stream.sendall(('HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: '+accept+'\r\n\r\n').encode())
  thread='owned-socket-thread-'+str(index); turn='owned-socket-turn-'+str(index)
  while True:
   value=ws_read(stream);record('socket',value); method=value.get('method'); args=value.get('params',{}); result={}
   if method=='initialized':continue
   if method=='initialize':result={'userAgent':'OWNED SOCKET FIXTURE'}
   elif method=='account/read':
    assert args=={'refreshToken':False};result={'requiresOpenaiAuth':True,'account':{'type':'chatgpt','email':'OWNED FIXTURE ONLY','planType':'unknown'}}
   elif method=='config/read':result={'config':{}}
   elif method=='thread/start':
    assert args['environments']==[] and args['ephemeral'] and args['config']['web_search']=='disabled'
    assert all(v is False for k,v in args['config'].items() if k.startswith('features.'))
    result={'thread':{'id':thread,'environments':[]},'instructionSources':[]}
   elif method=='turn/start':
    assert args['threadId']==thread and args['environments']==[]
    text=json.loads(args['input'][0]['text']); assert text['projectId']=='owned-project' and text['context']['helper']=='owned-helper'
    assert all(key not in args['input'][0]['text'] for key in ('authorization','toolCapability','credentialReference'))
    ws_send(stream,{'id':value['id'],'result':{'turn':{'id':turn,'status':'inProgress'}}})
    if text['message']=='hold':continue
    ws_send(stream,{'method':'item/agentMessage/delta','params':{'threadId':thread,'turnId':turn,'itemId':'answer','delta':'OWNED SOCKET '}})
    ws_send(stream,{'method':'item/completed','params':{'threadId':thread,'turnId':turn,'item':{'id':'answer','type':'agentMessage','text':'OWNED SOCKET FIXTURE: scoped reply.'}}})
    ws_send(stream,{'method':'turn/completed','params':{'threadId':thread,'turn':{'id':turn,'status':'completed'}}});continue
   elif method=='turn/interrupt':assert args=={'threadId':thread,'turnId':turn}
   else:raise AssertionError(method)
   ws_send(stream,{'id':value['id'],'result':result})
 except (EOFError,BrokenPipeError,ConnectionResetError):pass
 except Exception as error:record('fixture-error',repr(error))
 finally:stream.close()
sock=root/'control.sock'; listener=socket.socket(socket.AF_UNIX);listener.bind(str(sock));listener.listen()
def accept():
 index=0
 while True:
  stream,_=listener.accept();index+=1;threading.Thread(target=control,args=(stream,index),daemon=True).start()
threading.Thread(target=accept,daemon=True).start()
class Workspace(http.server.BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def send(self,status,body):
  data=json.dumps(body).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
 def do_POST(self):
  try:
   assert self.path=='/workspace_agents/agtch_owned/trigger' and self.headers.get('Authorization') is None
   assert self.headers['OpenAI-Beta']=='workspace_agent_runs=v1' and self.headers['Idempotency-Key'].startswith('confectory-')
   body=json.loads(self.rfile.read(int(self.headers['Content-Length'])));content=json.loads(body['input']);assert content['projectId']=='owned-project' and content['context']['helper']=='owned-helper'
   assert all(key not in body['input'] for key in ('authorization','toolCapability','workspaceCredentialReference'))
   record('workspace-post',{'body':body,'idempotencyKey':self.headers['Idempotency-Key']});self.send(202,{'conversation_url':'https://chatgpt.com/c/owned-local-fixture','agent_trigger_run_id':'apirun_owned'})
  except Exception as error:record('fixture-error',repr(error));self.send(500,{})
 def do_GET(self):
  assert self.path=='/workspace_agents/agtch_owned/runs/apirun_owned';record('workspace-poll',self.path)
  self.send(200,{'id':'apirun_owned','api_trigger_id':'agtch_owned','status':'completed','text':'IGNORED FIXTURE FIELD: THIS IS NOT A RETRIEVABLE AGENT REPLY'})
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Workspace)
print(json.dumps({'socket':str(sock),'endpoint':'http://127.0.0.1:'+str(server.server_port)+'/workspace_agents'}),flush=True)
server.serve_forever()
