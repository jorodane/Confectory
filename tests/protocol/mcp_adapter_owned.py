"""Actual managed stdio adapter against a clearly owned local IPC protocol fixture."""
import hashlib,json,os,pathlib,socket,tempfile,threading,time,uuid,sys
from mcp_client import Client
repo=pathlib.Path(sys.argv[1]).resolve();root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-mcp-protocol-'));directory=root/'instances';directory.mkdir(mode=0o700)
owner=hashlib.sha256(str(pathlib.Path.home()).encode()).hexdigest()[:16];ipc=pathlib.Path(tempfile.gettempdir())/('confectory-mcp-'+owner);ipc.mkdir(mode=0o700,exist_ok=True);assert ipc.stat().st_mode&0o077==0
class Engine:
 def __init__(self,title):
  self.id=uuid.uuid4().hex;self.address=ipc/(self.id+'.sock');self.title=title;self.mode='ok';self.calls=[];self.entered=threading.Event();self.release=threading.Event();self.stopped=False;self.listener=socket.socket(socket.AF_UNIX);self.listener.bind(str(self.address));self.listener.listen();self.listener.settimeout(.2)
  self.file=directory/(self.id+'.json');self.file.write_text(json.dumps(dict(schema=1,instance=self.id,pid=os.getpid(),transport='unix',address=str(self.address))));self.file.chmod(0o600)
  self.thread=threading.Thread(target=self.run,daemon=True);self.thread.start()
 def run(self):
  while not self.stopped:
   try:connection,_=self.listener.accept()
   except socket.timeout:continue
   except OSError:return
   with connection:
    try:
     data=b''
     while b'\n' not in data:data+=connection.recv(65536)
     request=json.loads(data.split(b'\n')[0]);operation=request['operation'];self.calls.append(request)
     if self.mode=='malformed':connection.sendall(b'null\n');continue
     if operation=='status':reply=dict(ok=True,result=dict(state='ready',projectId=self.title,instance=self.id,title=self.title,readOnly=True,node=''))
     elif operation=='tools/list':reply=dict(ok=True,result=[dict(name='workspace_read',description='Owned synthetic fixture source',parameters=dict(type='object',properties=dict(projectId=dict(type='string'),id=dict(type='string')),required=['projectId','id'],additionalProperties=False))])
     elif operation=='tools/call':
      if self.mode=='slow':self.entered.set();self.release.wait(8)
      args=request['payload']['arguments'];reply=dict(ok=True,result=dict(id=args['id'],text='OWNED_FIXTURE_'+self.title)) if args.get('projectId')==self.title else dict(ok=False,code='scope_changed')
     else:reply=dict(ok=False,code='operation_refused')
     connection.sendall((json.dumps(reply)+'\n').encode())
    except (BrokenPipeError,ConnectionResetError,OSError):pass
 def close(self):self.stopped=True;self.release.set();self.listener.close();self.thread.join(timeout=3);self.file.unlink(missing_ok=True);self.address.unlink(missing_ok=True)
engines=[]
try:
 with Client(repo,directory) as client:
  result,error=client.call('confectory_instances');assert error and result['code']=='engine_not_running';assert len(client.request('tools/list')['tools'])==4
  result,error=client.call('confectory_connect',dict(instanceId='0'*32));assert error and result['code']=='instance_not_found'
  a=Engine('A');b=Engine('B');engines=[a,b]
  result,error=client.call('confectory_instances');assert not error and result['selectionRequired'] and len(result['instances'])==2
  client.connect(a.id);names=[r['name'] for r in client.request('tools/list')['tools']];assert 'workspace_read' in names and not {'workspace_stage','shell','confirm'}.intersection(names)
  result,error=client.call('workspace_read',dict(projectId='A',id='A::Value'));assert not error and result['text']=='OWNED_FIXTURE_A'
  result,error=client.call('workspace_read',dict(projectId='B',id='A::Value'));assert error and result['code']=='scope_changed'
  result,error=client.call('shell',dict(command='must-not-run'));assert error and result['code']=='operation_refused'
  a.mode='slow';request=client.send('tools/call',dict(name='workspace_read',arguments=dict(projectId='A',id='A::Value')));assert a.entered.wait(5);client.notify('notifications/cancelled',dict(requestId=request));cancelled=client.receive(request)['result'];assert cancelled['isError'] and json.loads(cancelled['content'][0]['text'])['code']=='cancelled';a.release.set();a.mode='ok'
  assert not client.call('workspace_read',dict(projectId='A',id='A::Value'))[1]
  a.entered.clear();a.release.clear();a.mode='slow';request=client.send('tools/call',dict(name='workspace_read',arguments=dict(projectId='A',id='A::Value')));assert a.entered.wait(5);client.connect(b.id);a.release.set();late=client.receive(request)['result'];assert late['isError'] and json.loads(late['content'][0]['text'])['code']=='scope_changed';assert client.call('confectory_status')[0]['projectId']=='B'
  b.mode='malformed';result,error=client.call('confectory_status');assert error and result['code']=='invalid_engine_response';b.mode='ok';client.connect(b.id)
  client.call('confectory_disconnect');assert client.call('workspace_read',dict(projectId='B',id='B::Value'))[0]['code']=='no_engine_selected';client.connect(b.id)
  # Same scalar request ID and input returns the cached result; changed input is refused.
  request=client.send('ping',{},id='repeat');first=client.receive(request);client.send('ping',{},id='repeat');assert client.receive('repeat')==first;client.send('tools/list',{},id='repeat');assert client.receive('repeat')['error']['code']==-32600
  b.close();engines.remove(b);assert client.call('confectory_status')[0]['code']=='engine_unavailable'
  client.write(dict(jsonrpc='2.0',id='unknown',method='not-an-mcp-method'));assert client.receive('unknown')['error']['code']==-32601
  assert any(n['method']=='notifications/tools/list_changed' for n in client.notifications)
 with Client(repo,directory) as fresh:assert fresh.call('confectory_status')[0]['code']=='no_engine_selected'
 evidence=dict(actualManagedStdio=True,engineSide='owned synthetic Unix IPC fixture',initialization=True,toolsAndRead=True,multipleEnginesRequireSelection=True,foreignProjectRefused=True,noShellConfirm=True,cancelAndLateReplyFence=True,malformedResponse=True,disconnectReconnectAndRestart=True,duplicateRequestIdentity=True,realChatGPTApp=False)
 (root/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n');pathlib.Path('/workspace/scratch/confectory-mcp-protocol.json').write_text(json.dumps(evidence,indent=2)+'\n');print('PASS MCP managed stdio/owned IPC scope, malformed reply, cancellation, reconnect, duplicate ID '+str(root),flush=True)
finally:
 for engine in engines:engine.close()
