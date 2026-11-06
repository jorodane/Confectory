"""Actual owned transport rejects malformed producer data; image reads do not renew heartbeat."""
import json,sys,time,traceback,base64,hashlib
sys.argv.append('--software-output')
import v666_run_fullscreen_fixture as f
mode=sys.argv[3]if len(sys.argv)>3 else'heartbeat'
if mode=='wide':
 p=f.projects[0].parent/'Main.csbody';p.write_text(p.read_text().replace('64*36*4','640*360*4').replace('y<36','y<360').replace('x<64','x<640').replace('(y*64+x)','(y*640+x)').replace('surface,64,36','surface,640,360'));f.before={str(p):p.read_bytes()for m in f.projects for p in m.parent.rglob('*')if p.is_file()}
if mode=='capabilities':
 p=f.projects[0].parent/'MainBody.celem';p.write_text(p.read_text().replace('body common', 'import Confectory.FrameControl::AttachOutput as Attach (string,object) -> void;body common'))
 (p.parent/'Main.csbody').write_text('''string loop=calls.Open.Invoke();int read=0;string a=new string('a',32),b=new string('b',32);calls.Attach.Invoke(loop,(Func<string,string>)(cursor=>{int n=System.Threading.Interlocked.Increment(ref read)-1;var bytes=new byte[]{1,2,3,255};string runtime=n>=8?b:a;var size=new System.Text.Json.Nodes.JsonObject{["sequence"]=0,["ack"]=0,["command"]="",["width"]=1,["height"]=1,["min"]=240,["max"]=640,["maxPixels"]=262144};var q=new System.Text.Json.Nodes.JsonObject{["available"]=true,["runtime"]=runtime,["revision"]="1",["cursor"]=runtime+":1",["format"]="rgba8",["encoding"]="base64url",["width"]=1,["height"]=1,["sha256"]=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(bytes)).ToLowerInvariant(),["unchanged"]=false,["pixels"]=Convert.ToBase64String(bytes).TrimEnd('=').Replace('+','-').Replace('/','_'),["resize"]=size};switch(n){case 1:size["maxPixels"]=1048576;break;case 2:size.Remove("maxPixels");break;case 3:size["max"]=512;size.Remove("maxPixels");break;case 4:q["width"]=640;q["height"]=640;break;case 5:size["width"]=640;size["height"]=640;break;case 6:size["max"]=1280;break;case 8:size["max"]=512;size.Remove("maxPixels");break;case 9:q["runtime"]=a;q["cursor"]=a+":1";break;}return q.ToJsonString();}));try{while(true){System.Threading.Thread.Sleep(5);if(calls.Begin.Invoke(loop)==0)continue;calls.Complete.Invoke(loop);}}finally{calls.Close.Invoke(loop);}''')
 f.before={str(p):p.read_bytes()for m in f.projects for p in m.parent.rglob('*')if p.is_file()}
view=None
try:
 f.start(0);row=f.run('open',view='d'*32);f.start_run(row);row=f.connected(row);view=f.mount()
 def image(cursor=''):
  body={'op':'observe','view':view['view'],'scope':view['scope'],'endpoint':'runSurface','input':{'view':row['view'],'lease':row['lease'],'handle':row['handle'],'cursor':cursor}}
  reply=f.raw(body);assert reply.get('ok'),reply;return reply['result']
 first=image();assert first['available'],first
 if mode=='wide':
  raw=base64.urlsafe_b64decode(first['pixels']+'='*((-len(first['pixels']))%4));assert first['width']==640 and first['height']==360 and len(raw)==921600 and hashlib.sha256(raw).hexdigest()==first['sha256'];f.checked('actual 640x360 pixels within unchanged 1MiB budget cross the real authenticated frame pipe, native parser and unretained WebUI response with full SHA intact')
 elif mode=='capabilities':
  for n in range(1,7):assert not image()['available'],n
  assert image()['available'];legacy=image();assert legacy['available']and legacy['resize']['max']==512 and'maxPixels'not in legacy['resize'];assert not image()['available'];f.checked('native fixed area/axis capability validation rejects missing/enlarged/changed limits without replacing receipt; new publisher can retain legacy512 and retired publisher stays rejected')
 else:
  end=time.monotonic()+2.7
  while time.monotonic()<end:assert image()['available'];time.sleep(.04)
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
