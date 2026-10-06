#!/usr/bin/env python3
"""Actual X11 circles/box collision, standalone and Stage worlds, stop/return/cleanup."""
import ctypes as c
import json
import os
import subprocess
import signal
import sys
import time
lib=c.CDLL('libX11.so.6'); P=c.c_void_p; U=c.c_ulong; L=c.c_long

def native(name,result,*args):
    fn=getattr(lib,name);fn.restype=result;fn.argtypes=list(args);return fn
open_display=native('XOpenDisplay',P,c.c_char_p)
root_window=native('XDefaultRootWindow',U,P)
query=native('XQueryTree',c.c_int,P,U,c.POINTER(U),c.POINTER(U),c.POINTER(P),c.POINTER(c.c_uint))
fetch=native('XFetchName',c.c_int,P,U,c.POINTER(P));free=native('XFree',c.c_int,P)
flush=native('XFlush',c.c_int,P);send=native('XSendEvent',c.c_int,P,U,c.c_int,L,P)
keycode=native('XKeysymToKeycode',c.c_ubyte,P,U)
image=native('XGetImage',P,P,U,c.c_int,c.c_int,c.c_uint,c.c_uint,U,c.c_int)
pixel=native('XGetPixel',U,P,c.c_int,c.c_int);destroy=native('XDestroyImage',c.c_int,P)
atom=native('XInternAtom',U,P,c.c_char_p,c.c_int)
class Event(c.Structure):
    _fields_=[('type',c.c_int),('serial',U),('send',c.c_int),('display',P),('window',U),('root',U),('subwindow',U),('time',U),('x',c.c_int),('y',c.c_int),('xr',c.c_int),('yr',c.c_int),('state',c.c_uint),('detail',c.c_uint),('same',c.c_int)]
display=open_display(None);assert display,'Live X11 DISPLAY required'
from native_x11_controls import NativeControls
native_controls=NativeControls(display)
root=root_window(display);report=json.load(open(sys.argv[1],encoding='utf-8'))

def find(wanted):
    r,parent,children,count=U(),U(),P(),c.c_uint();query(display,root,c.byref(r),c.byref(parent),c.byref(children),c.byref(count))
    try:
        for window in c.cast(children,c.POINTER(U))[:count.value]:
            name=P();fetch(display,window,c.byref(name))
            if name:
                try:
                    if c.string_at(name)==wanted:return window
                finally:free(name)
    finally:
        if children:free(children)

def await_window(wanted):
    end=time.monotonic()+10
    while time.monotonic()<end:
        window=find(wanted)
        if window:return window
        time.sleep(.01)
    raise AssertionError('Game surface not mapped')

def press(window,key):
    if 'latest' in globals():
        trace=latest();field=trace.get('fields',{}).get(str(trace.get('focus',0))) if trace else None
        if isinstance(field,str):field=json.loads(field)
        if field and field.get('native') and field.get('visible'):
            native_controls.key(int(field['nativeHandle']),key);return
    for kind in (2,3):
        event=Event(kind,0,1,display,window,root,0,100,0,0,0,0,0,keycode(display,key if isinstance(key,int) else ord(key)),1)
        buffer=c.create_string_buffer(192);c.memmove(buffer,c.byref(event),c.sizeof(event));assert send(display,window,0,0,buffer)
    flush(display)

def colored(window,color):
    bitmap=image(display,window,0,0,400,240,U(-1).value,2);assert bitmap
    try:
        points=[]
        for y in range(50,230,2):
            for x in range(70,380,2):
                if pixel(bitmap,x,y)&0xffffff==color:points.append((x,y))
        return points
    finally:destroy(bitmap)

def wait_color(window,color,predicate,seconds):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        points=colored(window,color)
        if points and predicate(points):return points
        time.sleep(.005)
    raise AssertionError(f'Expected visible color {color:x} position not observed')

def close(window):
    buffer=c.create_string_buffer(192);c.c_int.from_buffer(buffer,0).value=33
    U.from_buffer(buffer,32).value=window;U.from_buffer(buffer,40).value=atom(display,b'WM_PROTOCOLS',0)
    c.c_int.from_buffer(buffer,48).value=32;U.from_buffer(buffer,56).value=atom(display,b'WM_DELETE_WINDOW',0)
    assert send(display,window,0,0,buffer);flush(display)


# Editor-specific actual pointer/key workflow. All generated projects stay in /tmp.
import tempfile,shutil
lookup=native('XKeycodeToKeysym',U,P,c.c_ubyte,c.c_int)
resize=native('XResizeWindow',c.c_int,P,U,c.c_uint,c.c_uint)
raise_window=native('XRaiseWindow',c.c_int,P,U)
repo=os.path.abspath(os.path.join(os.path.dirname(__file__),'../..'))
storage=tempfile.mkdtemp(prefix='confectory-editor-gui-')
for n in range(20):os.mkdir(os.path.join(storage,f'Picker{n:02d}'))
log_path=os.path.join(storage,'gui.log')
env=os.environ.copy();env.update(CONFECTORY_EDITOR_REPO=repo,CONFECTORY_EDITOR_STORAGE=storage,CONFECTORY_EDITOR_TRACE='1')
app=None;log=None
def launch():
    global app,log
    log=open(log_path,'w',encoding='utf-8');app=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    return await_window(b'Confectory Editor A')
def latest(view=0):
    traces=[]
    try:
        with open(log_path,encoding='utf-8') as stream:
            for line in stream:
                if line.startswith('EDITOR_UI '):
                    try:
                        data=json.loads(line[10:])
                        if data['view']==view:traces.append(data)
                    except json.JSONDecodeError:pass
    except OSError:pass
    return traces[-1] if traces else None
def wait(predicate,message,view=0,seconds=40):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        trace=latest(view)
        if trace and predicate(trace):return trace
        if app.poll() is not None:raise AssertionError('Editor exited: '+open(log_path).read()[-3000:])
        time.sleep(.04)
    raise AssertionError(message+' '+str(latest(view)))
def click(window,id,view=0):
    raise_window(display,window);flush(display)
    trace=wait(lambda t:id in t['rects'][::5],f'Control {id} unavailable',view)
    field=trace.get('fields',{}).get(str(id))
    if isinstance(field,str):field=json.loads(field)
    if field and field.get('native'):
        native_controls.click(int(field['nativeHandle']),min(50,field['bounds'][2]//2),field['bounds'][3]//2);wait(lambda t:t['focus']==id,'native pointer focus',view);return
    n=trace['rects'][::5].index(id)*5;_,x,y,w,h=trace['rects'][n:n+5]
    for kind in (4,5):
        event=Event(kind,0,1,display,window,root,0,100,x+w//2,y+h//2,0,0,0,1,1)
        buf=c.create_string_buffer(192);c.memmove(buf,c.byref(event),c.sizeof(event));assert send(display,window,0,0,buf)
        flush(display);time.sleep(.03)
    time.sleep(.12)
def type_text(window,text,view=0):
    trace=wait(lambda t:t['focus'] in [int(k) for k in t.get('fields',{})],'native text focus',view);field=trace['fields'].get(str(trace['focus']))
    if isinstance(field,str):field=json.loads(field)
    assert field and field.get('native'),'Visible input must use a native widget'
    native_controls.text(int(field['nativeHandle']),text)

def project(trace,view=0):
    id=trace['model']['views'][str(view)]['project'];return next(p for p in trace['model']['projects'] if p['id']==id)
def select_body(window,view=0):
    click(window,30,view);trace=wait(lambda t:t['screen']=='element','element navigation',view)
    index=next(i for i,u in enumerate(project(trace,view)['units']) if u['kind']=='body')
    click(window,200+index,view);wait(lambda t:t['screen']=='element' and t['model']['lastOperation']=='select','selected body',view)
    click(window,44,view);wait(lambda t:t['screen']=='project','back to workspace',view)
def shutdown():
    for title in (b'Confectory Editor B',b'Confectory Editor A'):
        window=find(title)
        if window:close(window)
    assert app.wait(timeout=20)==0,open(log_path).read()[-4000:];log.close()
    assert 'owners, buffers, jobs, workspace and children disposed' in open(log_path).read()
try:
    a=launch();wait(lambda t:t['screen']=='home','home')
    subprocess.run(['import','-window',str(a),os.path.join(storage,'home.png')],check=True)
    click(a,1);wait(lambda t:t['screen']=='create','new project form')
    click(a,23);wait(lambda t:t['focus']==20,'required name focus')
    click(a,20);type_text(a,'Game');press(a,0xFF57)
    measured=wait(lambda t:t['fields']['20']['text']=='Game' and t['fields']['20']['caret']==4,'native create field caret')['fields']['20'];assert measured['provider']=='gtk3' and measured['native']
    handle=measured['nativeHandle'];native_controls.key(handle,0xFF50);native_controls.key(handle,0xFF53);native_controls.key(handle,0xFF53,(0xFFE1,));native_controls.key(handle,0xFF53,(0xFFE1,));native_controls.key(handle,'x');wait(lambda t:t['fields']['20']['text']=='Gxe','native Shift selection replacement')
    type_text(a,'W'*90);press(a,0xFF57);wait(lambda t:t['fields']['20']['caret']==90,'native horizontal editing caret')
    type_text(a,'GuiWorkflow');click(a,21);type_text(a,'A local designed editor workflow\nwith saved drafts.')
    subprocess.run(['import','-window',str(a),os.path.join(storage,'create.png')],check=True)
    click(a,22);native_controls.folder(find,await_window,storage);wait(lambda t:not t['nativePickerPending'] and 22 in t['rects'][::5],'native parent selected')
    click(a,23);trace=wait(lambda t:t['screen']=='project','created project')
    path=project(trace)['path'];folder=os.path.dirname(path);ns=project(trace)['namespace'];assert os.path.dirname(folder)==storage,'Native chooser selected a child rather than the typed parent'
    click(a,6);b=await_window(b'Confectory Editor B');wait(lambda t:str(1) in t['model']['views'],'shared view',1)
    click(a,30);wait(lambda t:t['screen']=='element','element list');click(a,41);type_text(a,'Counter');click(a,43);wait(lambda t:t['screen']=='project' and t['model']['views']['0']['element'].endswith('::Counter'),'new object')
    assert latest(1)['model']['views']['1']['element'].endswith('MainBody/body:common'),'selection leaked into sibling View'
    click(a,54);type_text(a,f'object {ns}::Counter {{ value count = 7; }}\n');click(a,34);wait(lambda t:t['model']['lastOperation']=='text' and t['model']['status']=='Applied text to local draft','object text')
    click(a,54);source_frame=wait(lambda t:t['focus']==54,'source focus')['fields']['54'];native_controls.key(source_frame['nativeHandle'],0xFF50,(0xFFE3,));press(a,0xFF57);at=wait(lambda t:t['focus']==54 and int(t['buffer'][2])==len(t['buffer'][1].rstrip('\n')),'native source line end');before_caret=int(at['buffer'][2]);press(a,0xFF51);press(a,0xFF51);old_buffer=wait(lambda t:t['focus']==54 and int(t['buffer'][2])==before_caret-2,'source caret')['buffer'];old_token=latest()['bufferToken']
    click(a,33);wait(lambda t:300 in t['rects'][::5],'property fallback');click(a,300);click(a,45);type_text(a,'9');click(a,46);wait(lambda t:t['model']['lastOperation']=='value' and 'Error:' not in t['model']['status'],'property edit')
    updated=latest();assert updated['bufferToken']==old_token,'clean source buffer identity recreated';assert int(updated['buffer'][2])==int(old_buffer[2])+len(updated['buffer'][1])-len(old_buffer[1]),'caret did not follow changed span';assert updated['buffer'][3]==old_buffer[3],'selection lost on source refresh'
    for n in range(10):
        click(a,30);wait(lambda t:t['screen']=='element','new object navigation');click(a,41);type_text(a,f'Extra{n:02d}');click(a,43);wait(lambda t:t['screen']=='project' and t['model']['views']['0']['element'].endswith(f'::Extra{n:02d}'),'repeated object create')
    click(a,30);wait(lambda t:t['screen']=='element','paged owned units');click(a,15);wait(lambda t:t['pages'][1]>0,'element next page');click(a,14);wait(lambda t:t['pages'][1]==0,'element previous page')
    click(a,44);wait(lambda t:t['screen']=='project','workspace');click(a,32);select_body(a);click(a,54);type_text(a,'this is deliberately invalid C#;');click(a,35);wait(lambda t:t['model']['lastOperation']=='save','Save invalid local draft');click(a,36);wait(lambda t:t['screen']=='review','invalid draft Review');click(a,15);review_page=wait(lambda t:t['pages'][2]>0,'Review next page');changes=review_page['model']['review']['changes'];row=changes[review_page['pages'][2]*4];click(a,400);wait(lambda t:row not in t['selected'],'scope checkbox removed');click(a,400);wait(lambda t:row in t['selected'],'scope checkbox restored');click(a,14);wait(lambda t:t['pages'][2]==0,'Review previous page');before=latest()['frames'];click(a,49);wait(lambda t:t.get('job')=='confirm','invalid Confirm active');close(b);invalid=wait(lambda t:t['model'].get('confirmResult',[''])[0]=='invalid','compiler error retained',seconds=120);assert invalid['frames']>before+3,'Confirm blocked presentation';wait(lambda t:'1' not in t['model']['views'],'closed View subscription drains after active job');assert not find(b'Confectory Editor B');assert open(os.path.join(folder,'main.csbody')).read()=='return 0;\n';click(a,50);wait(lambda t:t['screen']=='project','edit invalid draft');click(a,54);source='Console.WriteLine("Editor GUI run"); System.Threading.Thread.Sleep(60000); return 0;\n';type_text(a,source);click(a,35);wait(lambda t:t['model']['lastOperation']=='save' and t['model']['status'].startswith('Saved'),'Save')
    assert open(os.path.join(folder,'main.csbody')).read()=='return 0;\n','Save changed final source'
    raise_window(display,a);flush(display);time.sleep(.1)
    subprocess.run(['import','-window',str(a),os.path.join(storage,'workspace.png')],check=True)
    shutdown()
    a=launch();wait(lambda t:t['screen']=='home','restart home');click(a,2);native_controls.folder(find,await_window,folder)
    trace=wait(lambda t:t['screen']=='project','opened saved project');assert trace['model']['views']['0']['unit'][3]==source,'saved draft not restored'
    click(a,36);wait(lambda t:t['screen']=='review','Review');click(a,49);trace=wait(lambda t:t['model'].get('confirmResult',[''])[0]=='confirmed','Confirm',seconds=120)
    assert open(os.path.join(folder,'main.csbody')).read()==source,'Confirm final source'
    click(a,50);wait(lambda t:t['screen']=='project','workspace after Confirm');click(a,37);wait(lambda t:project(t)['execution']['state']=='running','Run',seconds=120);wait(lambda t:any('Editor GUI run' in line for line in project(t)['logs']),'child output')
    click(a,38);wait(lambda t:project(t)['execution']['state']=='stopped','Stop')
    click(a,6);b=await_window(b'Confectory Editor B');wait(lambda t:'1' in t['model']['views'],'reopened borrowed View',1)
    resize(display,a,640,520);flush(display);wait(lambda t:37 in t['rects'][::5] and t['rects'][t['rects'][::5].index(37)*5+1]<640,'resize footer')
    click(b,54,1);type_text(b,'this draft must remain local',1);close(b);wait(lambda t:'1' not in t['model']['views'],'close one View')
    click(a,6);b=await_window(b'Confectory Editor B');wait(lambda t:'1' in t['model']['views'],'reopen View',1)
    assert open(os.path.join(folder,'main.csbody')).read()==source,'pending View edits leaked into final source'
    raise_window(display,a);flush(display);time.sleep(.1)
    subprocess.run(['import','-window',str(a),os.path.join(storage,'confirmed.png')],check=True)
    # A stale dirty sibling must not overwrite a newer shared revision.
    click(a,54);type_text(a,'return 4;\n');click(a,34);wait(lambda t:t['model']['lastOperation']=='text' and not t['model']['status'].startswith('Error:'),'new shared revision')
    click(b,34,1);wait(lambda t:t['model']['status'].startswith('Error: Another draft revision'),'stale sibling rejected',1)
    click(a,36);wait(lambda t:t['screen']=='review','conflict Review');open(os.path.join(folder,'main.csbody'),'w').write('return 5;\n');click(a,49);wait(lambda t:t['model'].get('confirmResult',[''])[0]=='conflict','external conflict',seconds=120)
    assert open(os.path.join(folder,'main.csbody')).read()=='return 5;\n'
    click(a,52);wait(lambda t:t['screen']=='project' and t['model']['lastOperation']=='recover','explicit draft preserving recovery');assert latest()['model']['archives'],'old work context retained'
    # Cancel/join a real in-flight compiler job on application interruption.
    click(a,54);type_text(a,'return 6;\n');click(a,35);wait(lambda t:t['model']['lastOperation']=='save','saved interruption draft');click(a,36);wait(lambda t:t['screen']=='review','interruption Review');click(a,49);wait(lambda t:t.get('job')=='confirm','in-flight Confirm',seconds=20)
    os.killpg(app.pid,signal.SIGINT);assert app.wait(timeout=30)==0,open(log_path).read()[-4000:];log.close();assert 'owners, buffers, jobs, workspace and children disposed' in open(log_path).read()
    assert os.path.isfile(os.path.join(folder,'main.csbody'))
    assert not find(b'Confectory Editor A') and not find(b'Confectory Editor B')
    print('Editor native create/folder-open, element/source/property edit, Save/restart, Review/Confirm, Run/Stop/output, independent borrowed Views, resize/close/reopen, native folder select/cancel and element/review pagination, buffer identity/caret, compiler/stale/external errors, recovery, in-flight interrupt and cleanup PASS')
    print('Private evidence:',storage)
finally:
    if app and app.poll() is None:
        os.killpg(app.pid,signal.SIGINT)
        try:app.wait(timeout=20)
        except subprocess.TimeoutExpired:os.killpg(app.pid,signal.SIGKILL);app.wait()
    if log and not log.closed:log.close()
