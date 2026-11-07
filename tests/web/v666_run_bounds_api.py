"""Actual producer coordinates/packets and controlled malformed bounds rejection."""
import sys,json,time,traceback,base64,hashlib
sys.argv.append('--bounds-output')
import v666_run_fullscreen_fixture as f
mode=sys.argv[3];view=None
if mode=='faults':
 p=f.projects[0].parent/'MainBody.celem';p.write_text(p.read_text().replace('body common','import Confectory.FrameControl::AttachOutput as Attach (string,object) -> void;body common'))
 (p.parent/'Main.csbody').write_text('''string loop=calls.Open.Invoke();int read=0;string a=new string('a',32);calls.Attach.Invoke(loop,(Func<string,string>)(cursor=>{int n=System.Threading.Interlocked.Increment(ref read)-1;var bytes=new byte[]{220,80,20,255};var bounds=new System.Text.Json.Nodes.JsonObject{["space"]="rgba8-pixels-v1",["rectangles"]=new System.Text.Json.Nodes.JsonArray(0,0,1,1)};var q=new System.Text.Json.Nodes.JsonObject{["available"]=true,["runtime"]=a,["revision"]="10",["cursor"]=a+":10",["format"]="rgba8",["encoding"]="base64url",["width"]=1,["height"]=1,["sha256"]=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(bytes)).ToLowerInvariant(),["unchanged"]=false,["pixels"]=Convert.ToBase64String(bytes).TrimEnd('=').Replace('+','-').Replace('/','_'),["bounds"]=bounds};switch(n){case 1:bounds["rectangles"]=new System.Text.Json.Nodes.JsonArray(-1,0,1,1);break;case 2:bounds["rectangles"]=new System.Text.Json.Nodes.JsonArray(0,0,2,1);break;case 3:bounds["rectangles"]=new System.Text.Json.Nodes.JsonArray(0,0,1);break;case 4:bounds["rectangles"]=new System.Text.Json.Nodes.JsonArray(0,0,1.5,1);break;case 5:bounds["rectangles"]=new System.Text.Json.Nodes.JsonArray();for(int i=0;i<68;i++)bounds["rectangles"]!.AsArray().Add(1);break;case 6:bounds["space"]="world";break;case 7:bounds.Remove("rectangles");break;case 8:bounds["rectangles"]=new System.Text.Json.Nodes.JsonArray();break;case 9:q.Remove("bounds");break;case 10:bounds["privateLeak"]="never-expose";break;case 11:q["revision"]="11";q["cursor"]=a+":11";q.Remove("bounds");break;}return q.ToJsonString();}));try{while(true){System.Threading.Thread.Sleep(5);if(calls.Begin.Invoke(loop)==0)continue;calls.Complete.Invoke(loop);}}finally{calls.Close.Invoke(loop);}''')
 f.before={str(p):p.read_bytes()for m in f.projects for p in m.parent.rglob('*')if p.is_file()}
try:
 f.start(0);row=f.run('open',view='c'*32);f.start_run(row);row=f.connected(row);view=f.mount()
 def image(cursor=''):
  reply=f.raw(dict(op='observe',view=view['view'],scope=view['scope'],endpoint='runSurface',input=dict(view=row['view'],lease=row['lease'],handle=row['handle'],cursor=cursor)));assert reply.get('ok'),reply;return reply['result']
 first=image();assert first['available']and first['bounds']['space']=='rgba8-pixels-v1',first
 if mode=='faults':
  for n in range(1,10):assert not image()['available'],n
  valid=image();assert valid['available']and'privateLeak'not in valid['bounds'],valid
  legacy=image();assert legacy['available']and legacy['revision']=='11'and'bounds'not in legacy,legacy
  f.checked('native rejects invalid/oversized/missing/outside pixel geometry and same-frame change/disappearance without replacing valid baseline; private fields are stripped and a new legacy frame may opt out')
 else:
  assert first['bounds']['rectangles']==[4,4,16,12,32,8,24,20],first
  pixels=base64.urlsafe_b64decode(first['pixels']+'='*((-len(first['pixels']))%4));assert hashlib.sha256(pixels).hexdigest()==first['sha256']
  def pixel(x,y):return list(pixels[(y*64+x)*4:(y*64+x+1)*4])
  assert pixel(4,4)[:2]==[220,80]and pixel(19,15)[:2]==[220,80]and pixel(20,15)[:2]==[24,24];assert pixel(32,8)[:2]==[40,180]and pixel(55,27)[:2]==[40,180]and pixel(56,27)[:2]==[24,24]
  end=time.monotonic()+2.7
  while time.monotonic()<end:assert image()['available'];time.sleep(.04)
  assert f.run('read',row)['control']['mode']=='paused';f.checked('actual drawn rectangles and adjacent RGBA pixels match the atomically published bounds/SHA; repeated bounds observations never renew heartbeat or execute frames')
  for key in ['view','lease','handle']:
   q=dict(view=row['view'],lease=row['lease'],handle=row['handle']);q[key]='f'*32;assert not f.raw(dict(op='observe',view=view['view'],scope=view['scope'],endpoint='runSurface',input=q)).get('ok')
 f.run('close',row);f.original()
except Exception as error:
 (f.root/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 if view:
  try:f.raw(dict(op='dispose',view=view['view']))
  except Exception:pass
 f.save_evidence();f.stop()
print('RUN_BOUNDS_API',f.root,flush=True)
