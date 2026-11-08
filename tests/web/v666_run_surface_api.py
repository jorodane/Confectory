"""Actual owned transport rejects malformed producer data; image reads do not renew heartbeat."""
import json,sys,time,traceback,base64,hashlib
sys.argv.append('--software-output')
import v666_run_fullscreen_fixture as f
mode=sys.argv[3]if len(sys.argv)>3 else'heartbeat'
if mode=='maximum':
 p=f.projects[0].parent/'Main.csbody';p.write_text(p.read_text().replace('64*36*4','512*512*4').replace('y<36','y<512').replace('x<64','x<512').replace('(y*64+x)','(y*512+x)').replace('surface,64,36','surface,512,512'));f.before={str(p):p.read_bytes()for m in f.projects for p in m.parent.rglob('*')if p.is_file()}
if mode=='faults':
 p=f.projects[0].parent/'MainBody.celem';p.write_text(p.read_text().replace('body common', 'import Confectory.FrameControl::AttachOutput as Attach (string,object) -> void;body common'))
 (p.parent/'Main.csbody').write_text('''string loop=calls.Open.Invoke();int read=0;string a=new string('a',32),b=new string('b',32);calls.Attach.Invoke(loop,(Func<string,string>)(cursor=>{int n=System.Threading.Interlocked.Increment(ref read)-1;var bytes=new byte[]{1,2,3,255};string runtime=n>=8?b:a;int revision=n>=8?1:10;var q=new System.Text.Json.Nodes.JsonObject{["available"]=true,["runtime"]=runtime,["revision"]=revision.ToString(),["cursor"]=runtime+":"+revision,["format"]="rgba8",["encoding"]="base64url",["width"]=1,["height"]=1,["sha256"]=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(bytes)).ToLowerInvariant(),["unchanged"]=false,["pixels"]=Convert.ToBase64String(bytes).TrimEnd('=').Replace('+','-').Replace('/','_')};switch(n){case 1:q["sha256"]=new string('0',64);break;case 2:q["pixels"]="AAAA";break;case 3:q["width"]=513;break;case 4:return "null";case 5:return "{\\"available\\":true}";case 6:q["revision"]="9";q["cursor"]=a+":9";break;case 7:q["width"]=2;break;case 9:q["runtime"]=a;q["cursor"]=a+":10";q["revision"]="10";break;case 10:q["unchanged"]=true;q.Remove("pixels");q["sha256"]=new string('0',64);break;}return q.ToJsonString();}));try{while(true){System.Threading.Thread.Sleep(5);if(calls.Begin.Invoke(loop)==0)continue;calls.Complete.Invoke(loop);}}finally{calls.Close.Invoke(loop);}''')
 f.before={str(p):p.read_bytes()for m in f.projects for p in m.parent.rglob('*')if p.is_file()}
view=None;mutations=[];native_raw=f.raw
def traced_raw(body):
 if body.get('op')=='invoke':mutations.append((body.get('endpoint'),body.get('input',{}).get('operation')))
 return native_raw(body)
f.raw=traced_raw
try:
 f.start(0);row=f.run('open',view='d'*32);f.start_run(row);row=f.connected(row);view=f.mount()
 def image(cursor=''):
  body={'op':'observe','view':view['view'],'scope':view['scope'],'endpoint':'runSurface','input':{'view':row['view'],'lease':row['lease'],'handle':row['handle'],'cursor':cursor}}
  reply=f.raw(body);assert reply.get('ok'),reply;return reply['result']
 first=image();assert first['available'],first
 if mode=='maximum':
  raw=base64.urlsafe_b64decode(first['pixels']+'='*((-len(first['pixels']))%4));assert first['width']==512 and first['height']==512 and len(raw)==1048576 and hashlib.sha256(raw).hexdigest()==first['sha256'];f.checked('maximum 1MiB pixels cross the real authenticated frame pipe, native parser and unretained WebUI response with full SHA intact')
 elif mode=='faults':
  for n in range(1,8):
   bad=image();assert not bad['available'],(n,bad)
  new=image();assert new['available']and new['runtime']=='b'*32,new
  for n in [9,10]:assert not image(new['cursor'])['available'],n
  assert image()['available'];row=f.run('read',row);assert row['control']['connected'];f.checked('native reader rejects SHA/length/dimensions/null/missing/stale revision/retired epoch/unverified unchanged without replacing valid receipt or stopping execution')
 else:
  began=time.monotonic();end=began+2.7;observations=[];successful=[];beforeHeartbeat=len(mutations)
  while time.monotonic()<end:
   value=image();elapsed=time.monotonic()-began;observations.append(dict(elapsed=elapsed,available=value.get('available'),reason=value.get('reason')))
   (f.root/'heartbeat-observations.json').write_text(json.dumps(observations,indent=2))
   if value.get('available'):successful.append(elapsed)
   else:assert value=={'available':False,'reason':'surface-unavailable'},value
   time.sleep(.04)
  assert successful and successful[-1]>=2.0 and len(mutations)==beforeHeartbeat,observations
  (f.root/'heartbeat-command-counts.json').write_text(json.dumps(dict(before=beforeHeartbeat,after=len(mutations)),indent=2))
  paused=f.run('read',row);assert paused['control']['mode']=='paused',paused;f.checked('repeated authenticated pixel observations neither acknowledge nor renew frame heartbeat; actual cooperative owner safely pauses after metadata lease expires')
  for key,value in [('lease','0'*32),('handle','0'*32),('view','0'*32)]:
   bad={'op':'observe','view':view['view'],'scope':view['scope'],'endpoint':'runSurface','input':{'view':row['view'],'lease':row['lease'],'handle':row['handle'],key:value}}
   assert not f.raw(bad)['ok'],key
  f.checked('pixel reads reject foreign lease/handle/view while retaining exact project/ownership scope')
 f.run('close',row);assert not f.raw({'op':'observe','view':view['view'],'scope':view['scope'],'endpoint':'runSurface','input':{'view':row['view'],'lease':row['lease'],'handle':row['handle']}})['ok']
 f.original()
except Exception as error:
 (f.root/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc())));raise
finally:
 if view:
  try:f.raw({'op':'dispose','view':view['view']})
  except Exception:pass
 f.save_evidence();f.stop()
print('RUN_SURFACE_API',f.root,flush=True)
