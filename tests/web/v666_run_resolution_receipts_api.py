"""Malformed output size receipts are rejected on the authenticated native path, not simulated as success."""
import json,sys,traceback,time
sys.argv.append('--software-output')
import v666_run_fullscreen_fixture as f
p=f.projects[0].parent/'MainBody.celem';p.write_text(p.read_text().replace('body common','import Confectory.FrameControl::AttachOutput as Attach (string,object) -> void;body common'))
(p.parent/'Main.csbody').write_text('''string loop=calls.Open.Invoke();int reads=0;string runtime=new string('a',32),command=new string('c',32);calls.Attach.Invoke(loop,(Func<string,string>)(cursor=>{int n=System.Threading.Interlocked.Increment(ref reads)-1,w=n>=9?240:1,h=w;byte[] pixels=new byte[w*h*4];var size=new System.Text.Json.Nodes.JsonObject{["sequence"]=n>=7&&n!=8?1:0,["ack"]=n>=9?1:0,["command"]=n>=7&&n!=8?command:"",["width"]=n>=7&&n!=8?240:1,["height"]=n>=7&&n!=8?240:1,["min"]=240,["max"]=512};switch(n){case 1:size["sequence"]=65;break;case 2:size["ack"]=1;break;case 3:size["sequence"]=1;size["ack"]=1;size["command"]=command;size["width"]=240;size["height"]=240;break;case 4:size.Remove("max");break;case 5:size.Remove("command");break;case 6:size["width"]=0;break;case 10:size["ack"]=0;break;case 11:size["width"]=320;break;}return new System.Text.Json.Nodes.JsonObject{["available"]=true,["runtime"]=n==13?runtime+"\\n":runtime,["revision"]=n>=9?"11":"10",["cursor"]=(n==13?runtime+"\\n":runtime)+(n>=9?":11":":10"),["format"]="rgba8",["encoding"]="base64url",["width"]=w,["height"]=h,["sha256"]=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(pixels)).ToLowerInvariant(),["unchanged"]=false,["pixels"]=Convert.ToBase64String(pixels).TrimEnd('=').Replace('+','-').Replace('/','_'),["resize"]=size}.ToJsonString();}));try{while(true){System.Threading.Thread.Sleep(5);if(calls.Begin.Invoke(loop)==0)continue;calls.Complete.Invoke(loop);}}finally{calls.Close.Invoke(loop);}''')
f.before={str(p):p.read_bytes()for m in f.projects for p in m.parent.rglob('*')if p.is_file()};v=None
try:
 f.start(0);row=f.run('open',view='e'*32);f.start_run(row);row=f.connected(row);v=f.mount()
 def read():
  p=f.raw({'op':'observe','view':v['view'],'scope':v['scope'],'endpoint':'runSurface','input':{'view':row['view'],'lease':row['lease'],'handle':row['handle']}});assert p['ok'],p;return p['result']
 first=read();assert first['available']and first['resize']['sequence']==0,first
 for n in range(1,7):
  bad=read();assert not bad['available'],(n,bad)
 pending=read();assert pending['available']and pending['resize']['sequence']==1 and pending['resize']['ack']==0,pending
 assert not read()['available'];applied=read();assert applied['available']and applied['width']==240 and applied['resize']['ack']==1,applied
 for n in [10,11]:assert not read()['available'],n
 assert read()['available'];assert not read()['available'];assert read()['available'];assert f.run('read',row)['control']['connected'];f.run('close',row);f.original();f.checked('native size receipt rejects oversized sequence, future ACK, dimensions without actual pixels, missing/foreign fields and sequence/ACK regression; valid pending/applied receipts recover without corrupting cache or execution')
except Exception as error:
 (f.root/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc())));raise
finally:
 if v:
  try:f.raw({'op':'dispose','view':v['view']})
  except Exception:pass
 f.save_evidence();f.stop()
print('RUN_RESOLUTION_RECEIPTS',f.root,flush=True)
