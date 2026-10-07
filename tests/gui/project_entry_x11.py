"""Actual desktop file-entry startup race, existing inbox, draft retention, no project execution."""
import ctypes as c, json, os, pathlib, subprocess, sys, tempfile, time
from native_x11_controls import NativeControls
P=c.c_void_p;U=c.c_ulong
x=c.CDLL('libX11.so.6')
def bind(name,result,args):
 f=getattr(x,name);f.restype=result;f.argtypes=args;return f
display=bind('XOpenDisplay',P,[c.c_char_p])(None);assert display
native=NativeControls(display);fetch=bind('XFetchName',c.c_int,[P,U,c.POINTER(P)]);atom=bind('XInternAtom',U,[P,c.c_char_p,c.c_int]);send=bind('XSendEvent',c.c_int,[P,U,c.c_int,c.c_long,P])
repo=pathlib.Path(sys.argv[1]);dotnet=os.environ['CONFECTORY_DOTNET'];host=repo/'targets/desktop-entry/bin/Release/net8.0/Confectory.DesktopEntry.dll'
with tempfile.TemporaryDirectory(prefix='confectory-file-entry-') as folder:
 root=pathlib.Path(folder);env=os.environ.copy();env.update(CONFECTORY_ENTRY_SCOPE=str(root/'scope'),CONFECTORY_ENTRY_STORAGE=str(root/'inboxes'),CONFECTORY_HOME_STORAGE=str(root/'settings'),CONFECTORY_HOME_TRACE='1',CONFECTORY_EDITOR_REPO=str(repo))
 project=root/'한글 공백 프로젝트.cproj';project.write_text('project UserProject version "1" { standalone true; entry UserProject::Main; registry Evil "UNTRUSTED_BUILD_TOOL_DO_NOT_LOAD"; target linux Evil::Build; target windows Evil::Build; }',encoding='utf8')
 other=root/'library.cpack';other.write_text('pack PlainLibrary version "1" { standalone false; }')
 def invoke(path):return subprocess.Popen([dotnet,str(host),'open',str(path),'--repository',str(repo)],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 def reply(process,timeout=230):
  output,error=process.communicate(timeout=timeout)
  return process.returncode,json.loads(output.strip().splitlines()[-1]),error
 def latest():
  logs=list((root/'inboxes').glob('*/engine.log'))
  if not logs:return None
  for line in reversed(logs[0].read_text(errors='replace').splitlines()):
   if line.startswith('HOME_UI '):
    try:return json.loads(line[8:])
    except ValueError:pass
 def wait(predicate,reason,seconds=15):
  until=time.monotonic()+seconds
  while time.monotonic()<until:
   s=latest()
   if s and predicate(s):return s
   time.sleep(.04)
  raise AssertionError(reason+' '+str(latest()))
 def windows():
  r,parent,children,count=U(),U(),P(),c.c_uint();native.query(display,native.root,c.byref(r),c.byref(parent),c.byref(children),c.byref(count));found=[]
  try:
   for window in c.cast(children,c.POINTER(U))[:count.value]:
    name=P();fetch(display,window,c.byref(name))
    if name:
     try:
      if c.string_at(name)==b'Confectory - Projects':found.append(window)
     finally:native.free(name)
  finally:
   if children:native.free(children)
  return found
 def close(window):
  data=c.create_string_buffer(192);c.c_int.from_buffer(data).value=33;U.from_buffer(data,32).value=window;U.from_buffer(data,40).value=atom(display,b'WM_PROTOCOLS',0);c.c_int.from_buffer(data,48).value=32;U.from_buffer(data,56).value=atom(display,b'WM_DELETE_WINDOW',0);assert send(display,window,0,0,data);native.flush(display)
 clients=[];baseline=set(windows());window=0
 try:
  broken=root/'bad.cproj';broken.write_text('invalid declaration');code,result,_=reply(invoke(broken));assert code!=0 and result['status']=='failed' and not (root/'inboxes').exists(),'invalid file must not start an engine'
  clients=[invoke(project),invoke(project)];results=[reply(p) for p in clients];assert all(code==0 for code,_,_ in results),results;assert sorted(r['status'] for _,r,_ in results)==['already-open','opened'],results
  s=wait(lambda s:s['screen']=='project' and s['model']['selected']['path']==str(project),'startup opens requested Unicode path');created=set(windows())-baseline;assert len(created)==1,'startup race launched duplicate engine';window=created.pop();assert not (root/'.confectory').exists(),'file open ran project build hooks'
  field=json.loads(s['fields']['38']);b=field['bounds'];native.click(window,b[0]+16,b[1]+16);native.text(int(field['nativeHandle']),'unfinished local draft');wait(lambda s:json.loads(s['fields']['38'])['text']=='unfinished local draft','native unsubmitted text')
  code,result,_=reply(invoke(project),30);assert code==0 and result['status']=='already-open';wait(lambda s:json.loads(s['fields']['38'])['text']=='unfinished local draft','duplicate preserves native draft/focus')
  code,result,_=reply(invoke(other),30);assert code!=0 and result['status'] in ('busy','failed');s=wait(lambda s:s['model']['selected']['path']==str(project) and json.loads(s['fields']['38'])['text']=='unfinished local draft','other file cannot silently replace work');assert not (root/'.confectory').exists()
  # Explicit existing Leave policy, then library file opens in the same engine without Run.
  hit=s['hits'];box=next(hit[n+1:n+5] for n in range(0,len(hit),5) if hit[n]==33);native.click(window,box[0]+16,box[1]+box[3]//2);s=wait(lambda s:s['model']['shell']['menu']=='project','project menu');hit=s['hits'];box=next(hit[n+1:n+5] for n in range(0,len(hit),5) if hit[n]==15);native.click(window,box[0]+16,box[1]+box[3]//2);wait(lambda s:s['screen']=='home' and s['model']['selected'] is None,'explicit leave retains draft')
  code,result,_=reply(invoke(other),30);assert code==0 and result['status']=='opened';s=wait(lambda s:s['model']['selected'] and s['model']['selected']['path']==str(other),'plain library opens');assert s['model']['selected']['standalone'] is False and 36 not in s['hits'][::5] and len(set(windows())-baseline)==1 and not (root/'.confectory').exists()
  close(window);window=0;until=time.monotonic()+8
  while time.monotonic()<until and set(windows())-baseline:time.sleep(.05)
  assert not set(windows())-baseline
  logs=list((root/'inboxes').glob('*/engine.log'));until=time.monotonic()+10
  while time.monotonic()<until and 'Entry/home jobs, controls, buffers, Owner, project contexts and native surface disposed' not in logs[0].read_text(errors='replace'):time.sleep(.05)
  assert 'Entry/home jobs, controls, buffers, Owner, project contexts and native surface disposed' in logs[0].read_text(errors='replace'),'owned engine cleanup after external entry'
  # Closing/reopening uses the retained startup marker without a second live instance.
  code,result,_=reply(invoke(other),30);assert code==0 and result['status']=='opened',(code,result)
  wait(lambda s:s['model']['selected'] and s['model']['selected']['path']==str(other),'warm restart opens requested pack');created=set(windows())-baseline;assert len(created)==1;window=created.pop();close(window);window=0;until=time.monotonic()+8
  while time.monotonic()<until and set(windows())-baseline:time.sleep(.05)
  assert not set(windows())-baseline
  print('ProjectEntry actual X11 PASS: cold race, existing instance, Unicode path, duplicate, unsubmitted draft refusal, explicit leave/library open, no project execution, cleanup/reopen')
 finally:
  native.button(display,1,0,0);native.flush(display)
  if window:close(window)
  for process in clients:
   if process.poll() is None:process.kill();process.wait()
