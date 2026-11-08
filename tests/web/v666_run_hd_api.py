"""Actual authenticated HD parts and reject-before-publication; generated owned projects only."""
import json,sys,time,traceback,base64,hashlib,uuid
sys.argv.append('--resizable-output')
import v666_run_fullscreen_fixture as f
mode=sys.argv[3]if len(sys.argv)>3 else'normal';p=f.projects[0].parent/'MainBody.celem';p.write_text(p.read_text().replace('Confectory.RunSurface::Open as OpenSurface','Confectory.RunSurface::OpenHD as OpenSurface'));p=f.projects[0].parent/'Main.csbody';p.write_text(p.read_text().replace('surface,64,36','surface,1280,720').replace('Thread.Sleep(16)','Thread.Sleep(50)'))
if mode=='faults':
 p=f.projects[0].parent/'MainBody.celem';p.write_text(p.read_text().replace('body common', 'import Confectory.FrameControl::AttachOutput as Attach (string,object) -> void;body common'))
 (p.parent/'Main.csbody').write_text('''string loop=calls.Open.Invoke(),runtime=new string('a',32);int generation=0;var bytes=new byte[1280*720*4];uint noise=0x1730489Du;for(int i=0;i<bytes.Length;i++){noise^=noise<<13;noise^=noise>>17;noise^=noise<<5;bytes[i]=(byte)noise;}string sha=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(bytes)).ToLowerInvariant(),encoded=Convert.ToBase64String(bytes).TrimEnd('=').Replace('+','-').Replace('/','_');
 calls.Attach.Invoke(loop,(Func<string,string>)(cursor=>{bool unchanged=cursor==runtime+":1";int part=cursor.StartsWith("part:")?int.Parse(cursor[(cursor.LastIndexOf(':')+1)..]):0;if(part==0&&!unchanged)generation++;int n=unchanged?1:generation;var size=new System.Text.Json.Nodes.JsonObject{["sequence"]=0,["ack"]=0,["command"]="",["width"]=1280,["height"]=720,["min"]=240,["max"]=1280,["maxPixels"]=921600};var q=new System.Text.Json.Nodes.JsonObject{["available"]=true,["runtime"]=runtime,["revision"]=n.ToString(),["cursor"]=runtime+":"+n,["format"]="rgba8",["encoding"]=unchanged?"base64url":"base64url-parts-v1",["width"]=1280,["height"]=720,["sha256"]=sha,["unchanged"]=unchanged,["resize"]=size};if(!unchanged){q["part"]=part;q["parts"]=5;q["pixels"]=encoded.Substring(part*1048576,Math.Min(1048576,encoded.Length-part*1048576));switch(n){case 2:if(part==1)q["runtime"]=new string('b',32);break;case 3:if(part==1){string text=q["pixels"]!.GetValue<string>();q["pixels"]=(text[0]=='A'?"B":"A")+text[1..];}break;case 4:q["parts"]=6;break;case 5:size["maxPixels"]=921601;break;case 6:q["height"]=721;break;case 7:q["part"]=1;break;}}return q.ToJsonString();}));try{while(true){System.Threading.Thread.Sleep(5);if(calls.Begin.Invoke(loop)==0)continue;calls.Complete.Invoke(loop);}}finally{calls.Close.Invoke(loop);}''')
f.before={str(p):p.read_bytes()for m in f.projects for p in m.parent.rglob('*')if p.is_file()};view=None
try:
 f.start(0);row=f.run('open',view='d'*32);f.start_run(row);row=f.connected(row);
 if mode=='faults':row=f.control(row,'pause');row=f.wait(row,lambda q:q['control'].get('mode')=='paused'and q['control'].get('pending')==0)
 view=f.mount()
 def image(cursor='',updates=None):
  q=dict(view=row['view'],lease=row['lease'],handle=row['handle'],cursor=cursor);q.update(updates or{});reply=f.raw(dict(op='observe',view=view['view'],scope=view['scope'],endpoint='runSurface',input=q));assert reply.get('ok'),reply;return reply['result']
 def complete(first):
  assert first['available']and first['encoding']=='base64url-parts-v1'and first['part']==0 and first['parts']==5,first
  pieces=[first]
  for i in range(1,5):
   if mode=='normal':time.sleep(.08)
   pieces.append(image('slice:'+first['cursor']+':'+str(i)))
  raw=b''
  for i,q in enumerate(pieces):
   assert q['available']and all(q[k]==first[k]for k in['runtime','revision','cursor','sha256','width','height','resize','parts'])and q['part']==i
   raw+=base64.urlsafe_b64decode(q['pixels']+'='*((-len(q['pixels']))%4))
  assert len(raw)==1280*720*4 and hashlib.sha256(raw).hexdigest()==first['sha256'];return raw
 first=image();raw=complete(first);
 if mode=='normal':row=f.run('read',row);row=f.control(row,'pause');row=f.wait(row,lambda q:q['control'].get('mode')=='paused'and q['control'].get('pending')==0);first=image();complete(first)
 saved=first['cursor'];same=image(saved);assert same['available']and same['unchanged']and 'pixels'not in same;f.checked('actual high-entropy1280x720 output crosses bounded authenticated child parts and unretained native/browser parts with exact overall SHA; same completed cursor remains unchanged')
 if mode=='normal':
  assert len(set(raw[0::4]))==1 and set(raw[3::4])=={255}
  for x,y in[(0,0),(1279,719),(300,300),(0,500)]:assert raw[(y*1280+x)*4+1:(y*1280+x)*4+4]==bytes([(x*4)%256,(y*7)%256,255])
  for key in['lease','view','handle']:
   q=dict(view=row['view'],lease=row['lease'],handle=row['handle'],cursor='slice:'+saved+':1');q[key]='0'*32;assert not f.raw(dict(op='observe',view=view['view'],scope=view['scope'],endpoint='runSurface',input=q)).get('ok'),key
  for cursor in['slice:'+'f'*32+':1:1','slice:'+saved+':4','slice:'+saved+':9']:
   try:q=image(cursor)
   except AssertionError:continue
   assert not q['available'],q
  accepted=image();assert accepted['available'];f.run('stop',row);assert not image('slice:'+accepted['cursor']+':1')['available'];f.checked('single coherent RGBA frame despite source activity; foreign lease/view/handle, retired/out-of-range/completed transfer and stopped execution cannot publish cached pixels')
 elif mode=='faults':
  for n in range(2,8):
   q=image();assert not q['available'],(n,q);prior=image(saved);assert prior['available']and prior['unchanged'],(n,prior)
  recovered=image();complete(recovered);assert recovered['revision']=='8';f.checked('native rejects mixed publisher, actual wrong SHA, excessive/missing parts, malformed capability and dimensions before replacing trusted revision; exact prior remains valid and a later clean frame recovers')
 else:raise AssertionError(mode)
 f.run('close',row);f.original()
except Exception as error:
 (f.root/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc())));raise
finally:
 if view:
  try:f.raw(dict(op='dispose',view=view['view']))
  except Exception:pass
 f.save_evidence();f.stop()
print('RUN_HD_API',f.root,flush=True)
