"""Actual HTTP fault/lifetime probe of the unchanged owner-thread contract.

Compiles the product Serve body with a deterministic owner; this does not replace
the separate full-engine/browser/package checks. Only generated loopback clients.
"""
import hashlib,json,os,pathlib,socket,subprocess,sys,time,urllib.error,urllib.request
repo=pathlib.Path(sys.argv[1]).resolve();out=pathlib.Path(sys.argv[2]).resolve();out.mkdir(parents=True,exist_ok=True)
program=r'''
using System.Text.Json;
using System.Security.Cryptography;
var calls=new Calls();int thread=Environment.CurrentManagedThreadId,requests=0,closed=0;
byte[] image=new byte[4*1024*1024];new Random(12).NextBytes(image);
calls.Resource=(_,path)=>{
 if(Environment.CurrentManagedThreadId!=thread)throw new Exception("Owner left host thread");
 byte[] bytes=path=="/large"?image:System.Text.Encoding.UTF8.GetBytes(path=="/counts"?JsonSerializer.Serialize(new{requests,closed}):"owned-resource");
 return new[]{"application/octet-stream",Convert.ToBase64String(bytes),Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant()};
};
calls.Request=(_,body)=>{
 if(Environment.CurrentManagedThreadId!=thread)throw new Exception("Owner left host thread");
 requests++;return body=="large"?new string('x',4*1024*1024):JsonSerializer.Serialize(new{body,requests});
};
calls.Close=_=>{closed++;if(closed!=1)throw new Exception("Owner closed twice");return true;};
calls.Run=token=>{
 var state=(object[])AppContext.GetData("Confectory.HostLoop."+token)!;
 _=System.Threading.Tasks.Task.Run(()=>{Console.ReadLine();((Action)state[2])();});
 var step=(Func<bool>)state[0];while(step())Thread.Sleep(2);
 Console.WriteLine("OWNER_CLOSED "+closed);return 0;
};
return Product(calls,"owned");
static int Product(Calls calls,string owner){
__BODY__
}
class Calls{
 public Func<string,string,string[]> Resource=null!;
 public Func<string,string,string> Request=null!;
 public Func<string,bool> Close=null!;
 public Func<string,int> Run=null!;
}
'''.replace('__BODY__',(repo/'packs/browser-host/Serve.csbody').read_text())
(out/'Program.cs').write_text(program);(out/'Probe.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>')
sdk=os.environ.get('CONFECTORY_DOTNET','dotnet');subprocess.run([sdk,'build',str(out/'Probe.csproj'),'-c','Release','--nologo'],check=True)
env=dict(os.environ,CONFECTORY_WEB_PORT='0');host=subprocess.Popen([sdk,str(out/'bin/Release/net10.0/Probe.dll')],env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);peers=[];checks=[]
def checked(text):checks.append(text);print('PASS '+text,flush=True)
def get(path='/counts',timeout=3):
 with urllib.request.urlopen(origin+path,timeout=timeout)as reply:return reply.read(),dict(reply.headers)
def peer(path='/large',body=None,token=None,length=None):
 s=socket.socket();s.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,1024);s.settimeout(3);s.connect(('127.0.0.1',port));peers.append(s)
 headers=('GET '+path+' HTTP/1.1\r\nHost: 127.0.0.1:'+str(port)+'\r\n')if body is None else ('POST /api/request HTTP/1.1\r\nHost: 127.0.0.1:'+str(port)+'\r\nContent-Length: '+str(length if length is not None else len(body))+'\r\nX-Confectory-Session: '+str(token)+'\r\n')
 s.sendall((headers+'Connection: keep-alive\r\n\r\n').encode()+(body or b''));return s
def retire(s):s.close();peers.remove(s)
try:
 line=host.stdout.readline().strip();assert line.startswith('CONFECTORY_WEB_UI '),line
 origin,token=line.split(' ',1)[1].split('/#');port=int(origin.rsplit(':',1)[1])
 slow=peer();time.sleep(.1);payload,headers=get('/small');assert payload==b'owned-resource';assert headers['ETag']=='"'+hashlib.sha256(payload).hexdigest()+'"';assert 'no-store'in headers['Cache-Control']and"default-src 'self'"in headers['Content-Security-Policy'];checked('unconsumed real 4MiB response does not block another asset; MIME/hash/CSP/cache policy retained')
 retire(slow);assert json.loads(get()[0])['requests']==0;checked('broken static response does not kill the host or invoke the owner API')
 slow=peer(body=b'{',token=token,length=1024);time.sleep(.1);assert json.loads(get()[0])['requests']==0;retire(slow);checked('authenticated partial POST never blocks the host or reaches the owner')
 for supplied,extra,expected in [('wrong',{},403),(token,{'Origin':'http://untrusted.invalid'},403),(token,{},200)]:
  request=urllib.request.Request(origin+'/api/request',data='원문 UTF-8'.encode(),headers={'X-Confectory-Session':supplied,**extra})
  try:
   with urllib.request.urlopen(request,timeout=3)as reply:status=reply.status;data=reply.read()
  except urllib.error.HTTPError as error:status=error.code;data=error.read()
  assert status==expected,(status,data)
  if status==200:assert json.loads(data)['body']=='원문 UTF-8'
 assert json.loads(get()[0])['requests']==1;checked('session/Origin admission stays fail-closed; exact Unicode body executes once on the owner thread')
 slow=peer(body=b'large',token=token);time.sleep(.1)
 assert json.loads(get()[0])['requests']==2;retire(slow);assert json.loads(get()[0])['requests']==2;checked('abandoning an executed API response neither blocks nor replays the owner operation')
 # Fill the bounded inbound set with admitted but incomplete generated bodies.
 time.sleep(.1)
 for _ in range(32):peer(body=b'{',token=token,length=1024)
 time.sleep(.2)
 excess=peer()
 try:rejected=excess.recv(1024)
 except ConnectionResetError:rejected=b''
 assert not rejected or rejected.startswith(b'HTTP/1.1 503 '),rejected
 retire(excess);checked('33rd stalled transfer is closed/503 before owner work')
 # Exercise the real 30-second cancellation rather than an injected timer.
 time.sleep(30.5);assert json.loads(get()[0])['requests']==2;checked('30-second deadline retires every partial request and recovers all admission slots')
 for s in peers[:]:retire(s)
 peer();peer(body=b'{',token=token,length=1024);time.sleep(.1)
 host.stdin.write('close\n');host.stdin.flush();stdout,stderr=host.communicate(timeout=5);assert host.returncode==0 and'OWNER_CLOSED 1'in stdout,(host.returncode,stdout,stderr);checked('shutdown cancels both unread output and incomplete input, closing owner exactly once')
 assert not stderr,stderr
finally:
 for s in peers:s.close()
 if host.poll()is None:host.kill();host.communicate(timeout=5)
 (out/'transport-evidence.json').write_text(json.dumps({'checks':checks,'exactProductBodySha256':hashlib.sha256((repo/'packs/browser-host/Serve.csbody').read_bytes()).hexdigest(),'ownerIsTestDouble':True,'actualHTTP':True},indent=2))
