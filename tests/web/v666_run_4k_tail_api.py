"""Real owned pipe: both partial base64 tails must be canonical before trust changes."""
import json,sys,time,traceback,base64,hashlib
sys.argv.append('--resizable-output')
import v666_run_fullscreen_fixture as f
height=int(sys.argv[3]);assert height in [514,515]
width=512;size=width*height*4;count=(size+786431)//786432
phase=f.root/'phase';phase.write_text('1');trace=f.root/'generations.log'
p=f.projects[0].parent/'MainBody.celem'
p.write_text(p.read_text().replace('body common','import Confectory.FrameControl::AttachOutput as Attach (string,object) -> void;body common'))
(p.parent/'Main.csbody').write_text('''string loop=calls.Open.Invoke(),runtime=new string('a',32);var bytes=new byte[__WIDTH__*__HEIGHT__*4];uint noise=0x1730489Du;for(int i=0;i<bytes.Length;i++){noise^=noise<<13;noise^=noise>>17;noise^=noise<<5;bytes[i]=(byte)noise;}string sha=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(bytes)).ToLowerInvariant(),encoded=Convert.ToBase64String(bytes).TrimEnd('=').Replace('+','-').Replace('/','_'),alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";
 calls.Attach.Invoke(loop,(Func<string,string>)(cursor=>{bool unchanged=cursor==runtime+":1"||cursor==runtime+":3";int generation=unchanged?int.Parse(cursor[(runtime.Length+1)..]):int.Parse(System.IO.File.ReadAllText(__PHASE__)),part=cursor.StartsWith("part:")?int.Parse(cursor[(cursor.LastIndexOf(':')+1)..]):0;if(!unchanged&&part==0)System.IO.File.AppendAllText(__TRACE__,generation.ToString()+Environment.NewLine);var q=new System.Text.Json.Nodes.JsonObject{["available"]=true,["runtime"]=runtime,["revision"]=generation.ToString(),["cursor"]=runtime+":"+generation,["format"]="rgba8",["encoding"]=unchanged?"base64url":"base64url-parts-v1",["width"]=__WIDTH__,["height"]=__HEIGHT__,["sha256"]=sha,["unchanged"]=unchanged,["resize"]=new System.Text.Json.Nodes.JsonObject{["sequence"]=0,["ack"]=0,["command"]="",["width"]=__WIDTH__,["height"]=__HEIGHT__,["min"]=240,["max"]=4096,["maxPixels"]=8847360}};if(!unchanged){q["part"]=part;q["parts"]=__COUNT__;string data=encoded.Substring(part*1048576,Math.Min(1048576,encoded.Length-part*1048576));if(generation==2&&part==__COUNT__-1)data=data[..^1]+alphabet[alphabet.IndexOf(data[^1])|1];q["pixels"]=data;}return q.ToJsonString();}));try{while(true){System.Threading.Thread.Sleep(5);if(calls.Begin.Invoke(loop)==0)continue;calls.Complete.Invoke(loop);}}finally{calls.Close.Invoke(loop);}'''.replace('__WIDTH__',str(width)).replace('__HEIGHT__',str(height)).replace('__COUNT__',str(count)).replace('__PHASE__',json.dumps(str(phase))).replace('__TRACE__',json.dumps(str(trace))))
f.before={str(p):p.read_bytes()for m in f.projects for p in m.parent.rglob('*')if p.is_file()};view=None;mutations=[];native=f.raw
def traced(body):
 if body.get('op')=='invoke':mutations.append(body.get('endpoint'))
 return native(body)
f.raw=traced
try:
 f.start(0);row=f.run('open',view='d'*32);f.start_run(row);row=f.connected(row);row=f.control(row,'pause');row=f.wait(row,lambda q:q['control'].get('mode')=='paused'and q['control'].get('pending')==0);view=f.mount()
 def image(cursor=''):
  reply=f.raw(dict(op='observe',view=view['view'],scope=view['scope'],endpoint='runSurface',input=dict(view=row['view'],lease=row['lease'],handle=row['handle'],cursor=cursor)));assert reply.get('ok'),reply;return reply['result']
 def complete(first):
  assert first['available']and first['encoding']=='base64url-parts-v1'and first['part']==0 and first['parts']==count,first
  chunks=[first]+[image('slice:'+first['cursor']+':'+str(i))for i in range(1,count)]
  raw=b''
  for i,q in enumerate(chunks):
   assert q['available']and all(q[k]==first[k]for k in ['runtime','revision','cursor','sha256','width','height','resize','parts'])and q['part']==i
   raw+=base64.urlsafe_b64decode(q['pixels']+'='*((-len(q['pixels']))%4))
  assert len(raw)==size and hashlib.sha256(raw).hexdigest()==first['sha256']
  canonical=base64.urlsafe_b64encode(raw).decode().rstrip('=');alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';noncanonical=canonical[:-1]+alphabet[alphabet.index(canonical[-1])|1]
  assert noncanonical!=canonical and base64.urlsafe_b64decode(noncanonical+'='*((-len(noncanonical))%4))==raw
  return raw
 def positive(generation):
  before=len(mutations);observations=[]
  for attempt in range(20):
   first=image()
   if first.get('available'):break
   assert first==dict(available=False,reason='surface-unavailable')or first==dict(available=False,reason='no-frame'),first
   observations.append(first);time.sleep(.05)
  assert first.get('available')and first['revision']==str(generation)and len(mutations)==before,(first,observations);complete(first);return first
 first=positive(1);saved=first['cursor'];assert image(saved)['unchanged'];commands=len(mutations);phase.write_text('2');bad=image();assert bad==dict(available=False,reason='surface-unavailable'),bad;assert image(saved)['unchanged'];phase.write_text('3');recovered=positive(3);assert image(recovered['cursor'])['unchanged'];generations=[int(n)for n in trace.read_text().splitlines()];assert generations.count(2)==1 and len(mutations)==commands,generations
 f.checked('actual4K-cap native reader accepts canonical two-part raw tail remainder '+str(size%3)+', rejects identical-decoded-bytes nonzero unused tail bits before publication, preserves trusted1 and recovers canonical3 via reads only; malformed generation emitted once: '+json.dumps(generations));f.run('close',row);f.original()
except Exception as error:
 (f.root/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc())));raise
finally:
 if view:
  try:f.raw(dict(op='dispose',view=view['view']))
  except Exception:pass
 f.save_evidence();f.stop()
print('RUN_4K_TAIL',height,f.root,flush=True)
