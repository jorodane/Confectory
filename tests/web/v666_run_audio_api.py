"""Real registered PCM producer and authenticated scoped pipe; digital samples, no speaker claim."""
import json,sys,time,traceback,base64,hashlib,struct,math
sys.argv.append('--audio-output')
import v666_run_fullscreen_fixture as f
mode=sys.argv[3];view=None
if mode=='faults':
 p=f.projects[0].parent/'MainBody.celem';p.write_text(p.read_text().replace('body common','import Confectory.FrameControl::AttachAudio as AttachAudio (string,object) -> void;body common'))
 (p.parent/'Main.csbody').write_text('''string loop=calls.Open.Invoke();int reads=0;string a=new string('a',32),b=new string('b',32);calls.AttachAudio.Invoke(loop,(Func<string,string>)(cursor=>{int n=System.Threading.Interlocked.Increment(ref reads)-1;bool reset=cursor.Length==0||n==13;string pub=n>=13?b:a;byte[] bytes=new byte[]{1,0,2,0};var chunk=new System.Text.Json.Nodes.JsonObject{["sequence"]="2",["start"]="2",["samples"]=2,["sha256"]=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(bytes)).ToLowerInvariant(),["pcm"]=Convert.ToBase64String(bytes).TrimEnd('=').Replace('+','-').Replace('/','_')};var q=new System.Text.Json.Nodes.JsonObject{["available"]=true,["runtime"]=pub,["sequence"]=reset?"1":"2",["samples"]=reset?"2":"4",["oldest"]="1",["oldestSample"]="0",["cursor"]=pub+(reset?":1":":2"),["format"]="pcm16le",["rate"]=16000,["channels"]=1,["reset"]=reset,["reason"]=reset?(n==13?"publisher":"baseline"):"",["fromSample"]="2",["chunks"]=reset?new System.Text.Json.Nodes.JsonArray():new System.Text.Json.Nodes.JsonArray(chunk)};switch(n){case 1:chunk["sha256"]=new string('0',64);break;case 2:q["rate"]=48000;break;case 3:chunk["sequence"]="3";break;case 4:chunk["start"]="3";break;case 5:chunk["samples"]=3;break;case 6:q.Remove("oldestSample");break;case 7:q["reset"]=true;break;case 8:q["runtime"]=a+"\\n";break;case 9:q["sequence"]="0";break;case 10:chunk["pcm"]="AQACAA=";break;case 14:q["runtime"]=a;q["cursor"]=a+":2";break;}return q.ToJsonString();}));try{while(true){System.Threading.Thread.Sleep(5);if(calls.Begin.Invoke(loop)==0)continue;calls.Complete.Invoke(loop);}}finally{calls.Close.Invoke(loop);}''')
 f.before={str(p):p.read_bytes()for m in f.projects for p in m.parent.rglob('*')if p.is_file()}
try:
 f.start(0);row=f.run('open',view='a'*32);f.start_run(row);row=f.connected(row);view=f.mount()
 def read(cursor=''):
  reply=f.raw({'op':'observe','view':view['view'],'scope':view['scope'],'endpoint':'runAudio','input':{'view':row['view'],'lease':row['lease'],'handle':row['handle'],'cursor':cursor}});assert reply.get('ok'),reply;return reply['result']
 first=read();assert first['available']and first['reset']and first['reason']=='baseline'and not first['chunks'],first
 if mode=='faults':
  for n in range(1,11):assert not read(first['cursor'])['available'],n
  valid=read(first['cursor']);assert valid['available']and len(valid['chunks'])==1,valid
  # n12 is a valid repeat from the baseline; n13 replaces publisher without replaying any samples.
  assert read(first['cursor'])['available'];new=read(valid['cursor']);assert new['available']and new['runtime']=='b'*32 and new['reason']=='publisher'and not new['chunks'],new
  assert not read(new['cursor'])['available'];assert f.run('read',row)['control']['connected'];f.checked('authenticated native reader rejects bad SHA/format/order/offset/count/missing/reset/GUID/regression/noncanonical base64 and retired publisher without corrupting the last valid receipt')
 else:
  baseline=first;end=time.monotonic()+2.7
  while time.monotonic()<end:assert read()['available'];time.sleep(.04)
  paused=f.run('read',row);assert paused['control']['mode']=='paused',paused;steady=read();assert steady['reset']and not steady['chunks'];quiet=read(steady['cursor']);assert quiet['available']and not quiet['chunks']and quiet['fromSample']==steady['samples'];f.checked('baseline skips old PCM; audio-only reads do not acknowledge frames or renew heartbeat, real cooperative owner pauses; repeated exact cursor produces no replay')
  f.control(paused,'step');after=f.wait(row,lambda q:q['control']['mode']=='paused'and int(q['control']['frame'])==int(paused['control']['frame'])+1);packet=read(steady['cursor']);assert packet['available']and not packet['reset']and len(packet['chunks'])==1,packet
  chunk=packet['chunks'][0];raw=base64.urlsafe_b64decode(chunk['pcm']+'='*((-len(chunk['pcm']))%4));assert len(raw)==chunk['samples']*2 and hashlib.sha256(raw).hexdigest()==chunk['sha256'];values=struct.unpack('<'+'h'*chunk['samples'],raw);start=int(chunk['start']);assert all(abs(value-round(math.sin((start+i)*2*math.pi*440/16000)*8192))<=1 for i,value in enumerate(values));assert not read(packet['cursor'])['chunks'];f.checked('one explicit Step publishes one actual generated PCM16 block, full SHA and sample phase verified; exact cursor reread emits no duplicate block')
  # Resume long enough to overrun retention while renewing only through metadata.
  f.control(after,'resume');end=time.monotonic()+2.3
  while time.monotonic()<end:f.run('read',row);time.sleep(.08)
  current=f.run('read',row);f.control(current,'pause');f.wait(row,lambda q:q['control']['mode']=='paused');gap=read(baseline['cursor']);assert gap['available']and gap['reset']and gap['reason']=='gap'and not gap['chunks'],gap;f.checked('bounded live retention reports an explicit gap and establishes a fresh baseline without inventing or replaying missing audio')
  for key,value in [('lease','0'*32),('handle','0'*32),('view','0'*32)]:
   body={'op':'observe','view':view['view'],'scope':view['scope'],'endpoint':'runAudio','input':{'view':row['view'],'lease':row['lease'],'handle':row['handle'],key:value}};assert not f.raw(body)['ok'],key
  # PCM is never retained in ordinary invoke/update result rows.
  assert not f.raw({'op':'invoke','view':view['view'],'scope':view['scope'],'expectedRevision':view['revision'],'requestId':'b'*32,'endpoint':'runWindow','input':{'operation':'audio','view':row['view'],'lease':row['lease'],'handle':row['handle']}})['ok'];f.checked('foreign view/lease/handle and normal mutation entry are rejected; PCM stays on unretained scoped observations')
 f.run('close',row);assert not f.raw({'op':'observe','view':view['view'],'scope':view['scope'],'endpoint':'runAudio','input':{'view':row['view'],'lease':row['lease'],'handle':row['handle']}})['ok'];f.original()
except Exception as error:
 (f.root/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc())));raise
finally:
 if view:
  try:f.raw({'op':'dispose','view':view['view']})
  except Exception:pass
 f.save_evidence();f.stop()
print('RUN_AUDIO_API',f.root,flush=True)
