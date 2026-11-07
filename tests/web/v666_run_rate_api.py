"""Actual authenticated producer/native rate and optional legacy packet guards."""
import json,sys,time,traceback
sys.argv.append('--software-output')
import v666_run_fullscreen_fixture as f
mode=sys.argv[3];view=None
if mode=='faults':
 p=f.projects[0].parent/'MainBody.celem';p.write_text(p.read_text().replace('body common','import Confectory.FrameControl::AttachOutput as Attach (string,object) -> void;body common'))
 (p.parent/'Main.csbody').write_text('''string loop=calls.Open.Invoke();int read=0;string a=new string('a',32),b=new string('b',32);calls.Attach.Invoke(loop,(Func<string,string>)(cursor=>{int n=System.Threading.Interlocked.Increment(ref read)-1;var bytes=new byte[]{1,2,3,255};var rate=new System.Text.Json.Nodes.JsonObject{["basis"]="software-present-v1",["observation"]="10",["ready"]=true,["frames"]="2",["windowMs"]=950};string runtime=n==11?b:a;var q=new System.Text.Json.Nodes.JsonObject{["available"]=true,["runtime"]=runtime,["revision"]="10",["cursor"]=runtime+":10",["format"]="rgba8",["encoding"]="base64url",["width"]=1,["height"]=1,["sha256"]=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(bytes)).ToLowerInvariant(),["unchanged"]=false,["pixels"]=Convert.ToBase64String(bytes).TrimEnd('='),["renderRate"]=rate};switch(n){case 1:rate["observation"]="9";break;case 2:rate["frames"]="3";break;case 3:rate["frames"]="11";break;case 4:rate["windowMs"]=899;break;case 5:rate["windowMs"]=1000;break;case 6:rate["observation"]="11";rate["ready"]=false;rate["frames"]="0";rate["windowMs"]=0;break;case 7:q.Remove("renderRate");break;case 8:rate["observation"]="01";break;case 9:rate.Remove("frames");break;case 10:rate["observation"]="11";rate["privateLeak"]="never-expose";break;case 11:q.Remove("renderRate");break;}return q.ToJsonString();}));try{while(true){System.Threading.Thread.Sleep(5);if(calls.Begin.Invoke(loop)==0)continue;calls.Complete.Invoke(loop);}}finally{calls.Close.Invoke(loop);}''')
 f.before={str(p):p.read_bytes()for m in f.projects for p in m.parent.rglob('*')if p.is_file()}
try:
 f.start(0);row=f.run('open',view='d'*32);f.start_run(row);row=f.connected(row);view=f.mount()
 def image(cursor=''):
  reply=f.raw(dict(op='observe',view=view['view'],scope=view['scope'],endpoint='runSurface',input=dict(view=row['view'],lease=row['lease'],handle=row['handle'],cursor=cursor)));assert reply.get('ok'),reply;return reply['result']
 first=image();assert first['available']and first['renderRate']['basis']=='software-present-v1',first
 assert not {'handle','lease','secret','frameRuntime','request'}.intersection(first)
 if mode=='faults':
  for n in range(1,10):assert not image()['available'],n
  valid=image();assert valid['available']and valid['renderRate']['observation']=='11'and'privateLeak'not in valid['renderRate'],valid
  legacy=image();assert legacy['available']and legacy['runtime']=='b'*32 and'renderRate'not in legacy,legacy
  assert not image()['available'];f.checked('native rate rejects stale/same-revision changed counts, impossible counts/windows, warmup rollback, disappearance and missing/canonical fields without replacing baseline; strips private fields and permits a new legacy publisher, never retired owner replay')
 else:
  current=first;end=time.monotonic()+3
  while time.monotonic()<end:
   current=image(current['cursor']);assert current['available'];rate=current['renderRate'];assert int(rate['frames'])<=int(current['revision'])and(rate['windowMs']==0 or 900<=rate['windowMs']<=999)
   if rate['ready']and int(rate['frames'])>0:break
   time.sleep(.05)
  assert current['renderRate']['ready']and int(current['renderRate']['frames'])>0,current
  # Surface observations deliberately do not send control heartbeats. Publication
  # stops when the real cooperative owner loses its metadata lease.
  end=time.monotonic()+3.3
  while time.monotonic()<end:
   current=image(current['cursor']);assert current['available'];time.sleep(.04)
  assert current['renderRate']['frames']=='0',current
  paused=f.run('read',row);assert paused['control']['mode']=='paused';f.checked('actual successful software publications yield bounded rate; repeated rate/pixel reads never renew heartbeat or advance frame/ACK, and real idle output decays to zero')
  for key in ['lease','handle','view']:
   q=dict(view=row['view'],lease=row['lease'],handle=row['handle']);q[key]='0'*32;assert not f.raw(dict(op='observe',view=view['view'],scope=view['scope'],endpoint='runSurface',input=q)).get('ok')
  f.checked('rate shares exact output owner/project/lease admission without source, grant or execution commands')
 f.run('close',row);f.original()
except Exception as error:
 (f.root/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 if view:
  try:f.raw(dict(op='dispose',view=view['view']))
  except Exception:pass
 f.save_evidence();f.stop()
print('RUN_RATE_API',f.root,flush=True)
