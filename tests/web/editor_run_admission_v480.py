import json,os,pathlib,subprocess,tempfile,time,shutil,sys,signal,urllib.request
from playwright.sync_api import sync_playwright,expect
expect.set_options(timeout=30000)
repo=pathlib.Path(sys.argv[1]).resolve();report=json.load(open(sys.argv[2]));root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-run-admission-v480-'))
project=root/'ordinary-frame-loop';shutil.copytree(repo/'examples/frame-loop',project,ignore=shutil.ignore_patterns('.confectory'));manifest=project/'project.cpack';manifest.write_text(manifest.read_text().replace('../../',str(repo)+'/'))
before={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file()}
env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(root/'storage'),CONFECTORY_ENTRY_STORAGE=str(root/'storage'),CONFECTORY_WEB_PROJECT=str(manifest),PATH=str(pathlib.Path(env.get('CONFECTORY_DOTNET','dotnet')).parent)+os.pathsep+env['PATH'])
def start(n):
 log=root/f'host-{n}.log';stream=log.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
 deadline=time.monotonic()+60
 while time.monotonic()<deadline:
  for line in log.read_text().splitlines():
   if line.startswith('CONFECTORY_WEB_UI '):return host,stream,line.split(' ',1)[1]
  if host.poll() is not None:raise AssertionError(log.read_text())
  time.sleep(.1)
 os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=10);stream.close();raise AssertionError(log.read_text())
def stop(host,stream):
 os.killpg(host.pid,signal.SIGTERM)
 try:host.wait(timeout=10)
 except subprocess.TimeoutExpired:os.killpg(host.pid,signal.SIGKILL);host.wait()
 stream.close()
def saved():
 files=list((root/'storage/presentations').glob('*.json'));assert len(files)==1,files
 return json.loads(files[0].read_text())
def public_state(url):
 token=url.split('#',1)[1];endpoint=url.split('#',1)[0]+'api/request'
 def send(body):
  request=urllib.request.Request(endpoint,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token})
  with urllib.request.urlopen(request,timeout=30) as reply:return json.load(reply)
 for _ in range(150):
  mounted=send({'op':'mount'})
  if mounted['ok']:break
  assert mounted.get('error',{}).get('code')=='busy',mounted
  time.sleep(.02)
 else:raise AssertionError(mounted)
 try:return mounted['state']
 finally:assert send({'op':'dispose','view':mounted['view']})['ok']
def rpc(url,endpoint,input):
 token=url.split('#',1)[1];address=url.split('#',1)[0]+'api/request'
 def send(body):
  req=urllib.request.Request(address,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token})
  with urllib.request.urlopen(req,timeout=30) as response:return json.load(response)
 for attempt in range(8):
  view=send({'op':'mount'});assert view['ok'],view;rid='owned-run-probe-'+str(time.time_ns());envelope={'view':view['view'],'scope':view['scope']}
  try:
   accepted=send(dict(envelope,op='invoke',endpoint=endpoint,input=input,expectedRevision=view['revision'],requestId=rid));assert accepted['ok'],accepted
   for _ in range(300):
    result=send(dict(envelope,op='update'));assert result['ok'],result
    rows=[row for row in result['results'] if row['requestId']==rid]
    if rows:
     if rows[0].get('error',{}).get('code')=='stale_revision':break
     return rows[0],result['state']
    time.sleep(.01)
   else:raise AssertionError('pending actual command')
  finally:assert send(dict(envelope,op='dispose'))['ok']
 raise AssertionError('stale actual request after explicit fixture retries')
def child_ids(pid):
 parents={}
 for line in subprocess.check_output(['ps','-eo','pid=,ppid='],text=True).splitlines():
  child,parent=map(int,line.split());parents.setdefault(parent,[]).append(child)
 def walk(parent):
  result=[]
  for child in parents.get(parent,[]):result.append(child);result.extend(walk(child))
  return result
 return walk(pid)
def live(pid):
 try:return pathlib.Path('/proc/'+str(pid)+'/stat').read_text().split(') ',1)[1].split()[0]!='Z'
 except FileNotFoundError:return False
host,stream,url=start(0)
try:
 token=url.split('#',1)[1];address=url.split('#',1)[0]+'api/request'
 def send(body):
  request=urllib.request.Request(address,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token})
  with urllib.request.urlopen(request,timeout=30) as response:return json.load(response)
 view=send({'op':'mount'});assert view['ok'],view
 envelope={'view':view['view'],'scope':view['scope']}
 def update():
  end=time.monotonic()+10
  while time.monotonic()<end:
   result=send(dict(envelope,op='update'));assert result['ok'],result
   if not result.get('busy'):return result
   time.sleep(.01)
  raise AssertionError('busy state did not settle')
 def invoke(endpoint,input,snapshot):
  rid='single-intent-'+str(time.time_ns());accepted=send(dict(envelope,op='invoke',endpoint=endpoint,input=input,expectedRevision=snapshot['revision'],requestId=rid));assert accepted['ok'],accepted
  time.sleep(.05) # Let the single queued intent enter its serialized admission before any client state read.
  end=time.monotonic()+15
  while time.monotonic()<end:
   result=update();rows=[row for row in result['results'] if row['requestId']==rid]
   if rows:return rows[0],result
   time.sleep(.01)
  raise AssertionError('single request did not complete')
 outcome,snapshot=invoke('runProject',{'target':'linux'},view);assert outcome['ok'],outcome
 end=time.monotonic()+180
 while time.monotonic()<end:
  snapshot=update();control=snapshot['state'].get('executionControl') or {}
  if control.get('available') and int(control.get('frame','0'))>2:break
  assert snapshot['state']['executionState']!='failed',snapshot['state'];time.sleep(.03)
 else:raise AssertionError('actual frame runtime did not start')
 handle=snapshot['state']['executionHandle'];control=snapshot['state']['executionControl'];published_revision=snapshot['revision'];published_frame=control['frame']
 # No client/state read occurs during this interval. Simulation advances, but no newer model revision has been published.
 time.sleep(.4)
 outcome,paused=invoke('runControl',{'handle':handle,'action':'pause','runtime':control['runtime'],'ack':str(control['ack']),'sequence':str(control['sequence'])},snapshot)
 assert outcome['ok'],('State refresh inside admission changed the published revision',outcome,published_revision)
 end=time.monotonic()+10
 while time.monotonic()<end:
  paused=update();control=paused['state']['executionControl']
  if control.get('ack')==1 and control.get('mode')=='paused':break
  time.sleep(.02)
 else:raise AssertionError(control)
 frame=control['frame'];old=paused
 changed,current=invoke('runHistory',{'page':0},paused);assert changed['ok'] and current['revision']>old['revision']
 refused,after=invoke('runControl',{'handle':handle,'action':'step','runtime':control['runtime'],'ack':'1','sequence':'1'},old)
 assert not refused['ok'] and refused['error']['code']=='stale_revision',refused
 assert after['state']['executionControl']['ack']==1 and after['state']['executionControl']['frame']==frame,'stale Step was replayed or executed'
 stopped,after=invoke('stopProject',{'handle':handle},after);assert stopped['ok'] and after['state']['executionState']=='stopped'
 assert all((project/name).read_bytes()==data for name,data in before.items())
 (root/'admission-observation.json').write_text(json.dumps({'publishedRevision':published_revision,'publishedFrame':published_frame,'pauseAcceptedOnce':True,'pauseAck':1,'actualOtherViewRevision':current['revision'],'staleStepError':refused['error']['code'],'staleStepDidNotExecute':True,'sourceBytesUnchanged':True},indent=2));print('PASS command admission reads published state without hidden poll; actual revision change rejects stale Step without replay '+str(root),flush=True)
finally:stop(host,stream)
