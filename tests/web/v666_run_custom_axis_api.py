"""Actual authenticated CUSTOM_AXIS parts and reject-before-publication; generated owned projects only."""
import json,sys,time,traceback,base64,hashlib,uuid
sys.argv.append('--resizable-output')
import v666_run_fullscreen_fixture as f
mode=sys.argv[3]if len(sys.argv)>3 else'normal';portrait=mode=='portrait';mode='normal'if portrait else mode;p=f.projects[0].parent/'MainBody.celem';p.write_text(p.read_text().replace('Confectory.RunSurface::Open as OpenSurface','Confectory.RunSurface::OpenCustom as OpenSurface'));p=f.projects[0].parent/'Main.csbody';p.write_text(p.read_text().replace('surface,64,36','surface,8192,1080').replace('Thread.Sleep(16)','Thread.Sleep(50)'))
if mode=='faults':
 p=f.projects[0].parent/'MainBody.celem';p.write_text(p.read_text().replace('body common', 'import Confectory.FrameControl::AttachOutput as Attach (string,object) -> void;body common'))
 (p.parent/'Main.csbody').write_text('''string loop=calls.Open.Invoke(),runtime=new string('a',32);int generation=0,confirmed=0;bool armed=false;var bytes=new byte[8192*1080*4];uint noise=0x1730489Du;for(int i=0;i<bytes.Length;i++){noise^=noise<<13;noise^=noise>>17;noise^=noise<<5;bytes[i]=(byte)noise;}string sha=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(bytes)).ToLowerInvariant(),encoded=Convert.ToBase64String(bytes).TrimEnd('=').Replace('+','-').Replace('/','_');
 calls.Attach.Invoke(loop,(Func<string,string>)(cursor=>{bool unchanged=cursor==runtime+":1"||cursor==runtime+":12"||cursor==runtime+":14";int part=cursor.StartsWith("part:")?int.Parse(cursor[(cursor.LastIndexOf(':')+1)..]):0;if(unchanged){armed=true;confirmed=Math.Max(confirmed,int.Parse(cursor[(runtime.Length+1)..]));}if(part==0&&!unchanged){if(armed){if(generation is not (12 or 14)||confirmed>=generation)generation++;}else generation=1;}int n=unchanged?int.Parse(cursor[(runtime.Length+1)..]):generation;if(!unchanged&&part==0)System.IO.File.AppendAllText(__GEN_LOG__,n.ToString()+Environment.NewLine);if(n==13)System.Threading.Thread.Sleep(15);var size=new System.Text.Json.Nodes.JsonObject{["sequence"]=0,["ack"]=0,["command"]="",["width"]=8192,["height"]=1080,["min"]=240,["max"]=8192,["maxPixels"]=8847360};var q=new System.Text.Json.Nodes.JsonObject{["available"]=true,["runtime"]=runtime,["revision"]=n.ToString(),["cursor"]=runtime+":"+n,["format"]="rgba8",["encoding"]=unchanged?"base64url":"base64url-parts-v1",["width"]=8192,["height"]=1080,["sha256"]=sha,["unchanged"]=unchanged,["resize"]=size};if(!unchanged){q["part"]=part;q["parts"]=45;q["pixels"]=encoded.Substring(part*1048576,Math.Min(1048576,encoded.Length-part*1048576));switch(n){case 2:if(part==1)q["runtime"]=new string('b',32);break;case 3:if(part==1){string text=q["pixels"]!.GetValue<string>();q["pixels"]=(text[0]=='A'?"B":"A")+text[1..];}break;case 4:q["parts"]=46;break;case 5:size["maxPixels"]=8847361;break;case 6:q["height"]=1081;break;case 7:q["part"]=1;break;case 8:if(part==1)q["pixels"]=q["pixels"]!.GetValue<string>().Replace('-','+');break;case 9:if(part==1)q["pixels"]=q["pixels"]!.GetValue<string>().Replace('_','/');break;case 10:if(part==1)q["pixels"]=q["pixels"]!.GetValue<string>().Replace('A',' ');break;case 11:if(part==1)q["pixels"]=q["pixels"]!.GetValue<string>().Replace('A','Ａ');break;}}return q.ToJsonString();}));try{while(true){System.Threading.Thread.Sleep(5);if(calls.Begin.Invoke(loop)==0)continue;calls.Complete.Invoke(loop);}}finally{calls.Close.Invoke(loop);}'''.replace('__GEN_LOG__',json.dumps(str(f.root/'fault-generations.log'))))
if portrait:
 p=f.projects[0].parent/'Main.csbody';p.write_text(p.read_text().replace('surface,8192,1080','surface,1080,8192'))
f.before={str(p):p.read_bytes()for m in f.projects for p in m.parent.rglob('*')if p.is_file()};view=None
mutations=[];native_raw=f.raw
def traced_raw(body):
 if body.get('op')=='invoke':mutations.append(dict(endpoint=body.get('endpoint'),operation=body.get('input',{}).get('operation')))
 return native_raw(body)
f.raw=traced_raw
try:
 f.start(0);row=f.run('open',view='d'*32);f.start_run(row);row=f.connected(row);
 if mode=='faults':row=f.control(row,'pause');row=f.wait(row,lambda q:q['control'].get('mode')=='paused'and q['control'].get('pending')==0)
 view=f.mount()
 def image(cursor='',updates=None):
  q=dict(view=row['view'],lease=row['lease'],handle=row['handle'],cursor=cursor);q.update(updates or{});reply=f.raw(dict(op='observe',view=view['view'],scope=view['scope'],endpoint='runSurface',input=q));assert reply.get('ok'),reply;return reply['result']
 def complete(first):
  assert first['available']and first['encoding']=='base64url-parts-v1'and first['part']==0 and first['parts']==45,first
  pieces=[first]
  for i in range(1,45):
   if mode=='normal':time.sleep(.08)
   pieces.append(image('slice:'+first['cursor']+':'+str(i)))
  raw=b''
  for i,q in enumerate(pieces):
   assert q['available']and all(q[k]==first[k]for k in['runtime','revision','cursor','sha256','width','height','resize','parts'])and q['part']==i
   raw+=base64.urlsafe_b64decode(q['pixels']+'='*((-len(q['pixels']))%4))
  assert len(raw)==8192*1080*4 and hashlib.sha256(raw).hexdigest()==first['sha256'];return raw
 if mode in ['normal','faults']:
  initial=[];commands=len(mutations)
  for attempt in range(20):
   first=image()
   if first.get('available'):break
   assert first=={'available':False,'reason':'surface-unavailable'}or first=={'available':False,'reason':'no-frame'},first
   initial.append(dict(attempt=attempt+1,result=first));time.sleep(.05)
  (f.root/'initial-frame-observations.json').write_text(json.dumps(dict(observations=initial,invokeCountBefore=commands,invokeCountAfter=len(mutations)),indent=2));assert first.get('available'),dict(initial=initial,state=f.run('read',row));assert len(mutations)==commands
  if initial:f.checked('bounded initial unavailable observation recovery uses reads only, with unchanged command count: '+json.dumps(initial))
 else:raise AssertionError(mode)
 raw=complete(first);
 if mode=='normal':
  row=f.run('read',row);row=f.control(row,'pause');row=f.wait(row,lambda q:q['control'].get('mode')=='paused'and q['control'].get('pending')==0);postPause=[];beforeRead=len(mutations)
  for attempt in range(20):
   first=image()
   if first.get('available'):break
   assert first=={'available':False,'reason':'surface-unavailable'}or first=={'available':False,'reason':'no-frame'},first
   postPause.append(dict(attempt=attempt+1,result=first));time.sleep(.05)
  (f.root/'post-pause-observations.json').write_text(json.dumps(dict(observations=postPause,invokeCountBefore=beforeRead,invokeCountAfter=len(mutations)),indent=2));assert first.get('available')and len(mutations)==beforeRead,postPause;complete(first)
  if postPause:f.checked('bounded post-pause read-only recovery without new command: '+json.dumps(postPause))
 saved=first['cursor'];same=image(saved);assert same['available']and same['unchanged']and 'pixels'not in same;f.checked('actual complete8192x1080 output crosses bounded authenticated child parts and unretained native/browser parts with exact overall SHA; same completed cursor remains unchanged')
 if mode=='normal':
  assert len(set(raw[0::4]))==1 and set(raw[3::4])=={255}
  for x,y in[(0,0),(1079,8191)if portrait else(8191,1079),(300,300),(0,500)]:assert raw[(y*(1080 if portrait else 8192)+x)*4+1:(y*(1080 if portrait else 8192)+x)*4+4]==bytes([(x*4)%256,(y*7)%256,255])
  for key in['lease','view','handle']:
   q=dict(view=row['view'],lease=row['lease'],handle=row['handle'],cursor='slice:'+saved+':1');q[key]='0'*32;assert not f.raw(dict(op='observe',view=view['view'],scope=view['scope'],endpoint='runSurface',input=q)).get('ok'),key
  for cursor in['slice:'+'f'*32+':1:1','slice:'+saved+':4','slice:'+saved+':44']:
   try:q=image(cursor)
   except AssertionError:continue
   assert not q['available'],q
  unavailable=[]
  for attempt in range(20):
   accepted=image()
   if accepted['available']:break
   unavailable.append(accepted);time.sleep(.05)
  assert accepted['available'],dict(observations=unavailable,state=f.run('read',row))
  if unavailable:f.checked('bounded read-only snapshot recovery before Stop: '+json.dumps(unavailable))
  f.run('stop',row);assert not image('slice:'+accepted['cursor']+':1')['available'];f.checked('single coherent RGBA frame despite source activity; foreign lease/view/handle, retired/out-of-range/completed transfer and stopped execution cannot publish cached pixels')
 elif mode=='faults':
  for n in range(2,12):
   q=image();assert not q['available'],(n,q);prior=image(saved);assert prior['available']and prior['unchanged'],(n,prior)
  def positive(expected):
   commands=len(mutations);observations=[]
   for attempt in range(20):
    q=image()
    if q.get('available'):break
    assert q=={'available':False,'reason':'surface-unavailable'}or q=={'available':False,'reason':'no-frame'},q
    observations.append(dict(attempt=attempt+1,result=q));time.sleep(.05)
   (f.root/('positive-'+expected+'-observations.json')).write_text(json.dumps(dict(observations=observations,invokeCountBefore=commands,invokeCountAfter=len(mutations)),indent=2));assert q.get('available')and q['revision']==expected and len(mutations)==commands,q;complete(q);return q
  recovered=positive('12');confirmed=image(recovered['cursor']);assert confirmed['available']and confirmed['unchanged'];beforeSlow=len(mutations);slow=image();assert not slow['available'];prior=image(recovered['cursor']);assert prior['available']and prior['unchanged'];final=positive('14');assert len(mutations)==beforeSlow
  generations=[int(line)for line in(f.root/'fault-generations.log').read_text().splitlines()]
  for n in [*range(2,12),13]:assert generations.count(n)==1,(n,generations)
  f.checked('only valid1/12/14 generations may wait for read confirmation; each invalid generation2..11/13 emitted once, with no command replay: '+json.dumps(generations));f.checked('cumulative child delay across45 parts exceeds original300ms I/O budget and is rejected before replacing trusted revision12; clean revision14 recovers read-only with unchanged invoke count');f.checked('native rejects mixed publisher, actual wrong SHA, excessive/missing parts, malformed capability/dimensions and noncanonical +/slash/whitespace/Unicode wire data before replacing trusted revision; exact prior remains valid and a later clean frame recovers')
 else:raise AssertionError(mode)
 f.run('close',row);f.original()
except Exception as error:
 (f.root/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc())));raise
finally:
 if view:
  try:f.raw(dict(op='dispose',view=view['view']))
  except Exception:pass
 f.save_evidence();f.stop()
print('RUN_CUSTOM_AXIS_API',f.root,flush=True)
