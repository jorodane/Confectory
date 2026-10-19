"""Owned JSON-RPC client for the actual packaged managed MCP server."""
import json,os,pathlib,queue,subprocess,threading

class Client:
 def __init__(self,repo,directory,env=None,command=None,cwd=None):
  self.process=subprocess.Popen(command or [os.environ.get('CONFECTORY_DOTNET','dotnet'),str(pathlib.Path(repo)/'targets/mcp-host/bin/Release/net10.0/Confectory.Mcp.dll'),'--instances',str(directory)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,bufsize=0,cwd=cwd)
  self.messages=queue.Queue();self.saved={};self.notifications=[];self.counter=0
  def read():
   try:
    while True:
     raw=self.process.stdout.readline(4194305)
     if not raw:break
     assert len(raw)<=4194304 and raw.endswith(b'\n');self.messages.put(json.loads(raw))
   except BaseException as error:self.messages.put(error)
   finally:self.messages.put(EOFError('MCP process closed'))
  self.reader=threading.Thread(target=read,daemon=True);self.reader.start()
  result=self.request('initialize',dict(protocolVersion='2025-06-18',capabilities={},clientInfo=dict(name='owned-confectory-test',version='1')))
  assert result['protocolVersion']=='2025-06-18' and result['capabilities']['tools']['listChanged'];self.notify('notifications/initialized',{})
 def send(self,method,params=None,id=None):
  self.counter+=1;id=self.counter if id is None else id;self.write(dict(jsonrpc='2.0',id=id,method=method,params=params or {}));return id
 def write(self,data):self.process.stdin.write((json.dumps(data,ensure_ascii=False)+'\n').encode());self.process.stdin.flush()
 def notify(self,method,params):self.write(dict(jsonrpc='2.0',method=method,params=params))
 def receive(self,id,timeout=30):
  if id in self.saved:return self.saved.pop(id)
  while True:
   item=self.messages.get(timeout=timeout)
   if isinstance(item,BaseException):raise item
   if 'id' not in item:self.notifications.append(item);continue
   if item['id']==id:return item
   self.saved[item['id']]=item
 def request(self,method,params=None,timeout=30):
  reply=self.receive(self.send(method,params),timeout);assert 'error' not in reply,reply;return reply['result']
 def call(self,name,arguments=None):
  reply=self.request('tools/call',dict(name=name,arguments=arguments or {}));return json.loads(reply['content'][0]['text']),reply['isError']
 def connect(self,instance):
  value,error=self.call('confectory_connect',dict(instanceId=instance));assert not error,(value,error);return value
 def close(self):
  if self.process.poll() is None:
   self.process.stdin.close()
   try:self.process.wait(timeout=8)
   except subprocess.TimeoutExpired:self.process.kill();self.process.wait();raise
  errors=self.process.stderr.read().decode();assert self.process.returncode==0,errors
 def __enter__(self):return self
 def __exit__(self,*args):self.close()
