#!/usr/bin/env python3
"""Actual entry/home X11 acceptance; private evidence only."""
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


import tempfile,shutil,zipfile
raise_window=native('XRaiseWindow',c.c_int,P,U)
resize=native('XResizeWindow',c.c_int,P,U,c.c_uint,c.c_uint)
repo=os.environ.get('CONFECTORY_GUI_REPO',os.path.abspath(os.path.join(os.path.dirname(__file__),'../..')))
storage=tempfile.mkdtemp(prefix='confectory-source-workspace-gui-')
log_path=os.path.join(storage,'native.log')
env=os.environ.copy();env.update(CONFECTORY_EDITOR_REPO=repo,CONFECTORY_HOME_STORAGE=storage,CONFECTORY_HOME_TRACE='1',CONFECTORY_ELEMENT_AUTHORING_HOST=os.path.join(repo,'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'),CONFECTORY_PROJECT_EXECUTION_HOST=os.path.join(repo,'targets/project-execution-host/bin/Release/net10.0/Confectory.ProjectExecutionHost.dll'))
app=None;log=None;launch_count=0
def launch():
    global app,log,launch_count
    if launch_count and os.path.isfile(log_path):shutil.copy2(log_path,os.path.join(storage,f"native-launch-{launch_count}.log"))
    launch_count+=1
    log=open(log_path,'w',encoding='utf-8');app=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    return await_window(b'Confectory - Projects')
def latest():
    value=None
    with open(log_path,encoding='utf-8') as stream:
        for line in stream:
            if line.startswith('HOME_UI '):
                try:value=json.loads(line[8:])
                except json.JSONDecodeError:pass
    return value

def wait(predicate,message,seconds=30):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        state=latest()
        if state and predicate(state):return state
        if app.poll() is not None:raise AssertionError('Entry/home exited: '+open(log_path).read()[-3000:])
        time.sleep(.04)
    raise AssertionError(message+' '+str(latest()))
def click(window,id):
    raise_window(display,window);flush(display)
    state=wait(lambda t:id in t['hits'][::5],f'Control {id} unavailable')
    field=state.get('fields',{}).get(str(id))
    if isinstance(field,str):field=json.loads(field)
    if field and field.get('native'):
        native_controls.click(int(field['nativeHandle']),min(50,field['bounds'][2]//2),field['bounds'][3]//2);wait(lambda t:t['focus']==id,'native pointer focus');return
    n=state['hits'][::5].index(id)*5;_,x,y,w,h=state['hits'][n:n+5]
    for kind in (4,5):
        event=Event(kind,0,1,display,window,root,0,100,x+w//2,y+h//2,0,0,0,1,1)
        buf=c.create_string_buffer(192);c.memmove(buf,c.byref(event),c.sizeof(event));assert send(display,window,0,0,buf)
        flush(display);time.sleep(.04)
    time.sleep(.15)
def leave_project(window):
    click(window,33);wait(lambda t:t['model']['shell']['menu']=='project','project menu')
    click(window,15)

def type_text(window,text):
    trace=wait(lambda t:t['focus'] in [int(k) for k in t.get('fields',{})],'native text focus');field=trace['fields'].get(str(trace['focus']))
    if isinstance(field,str):field=json.loads(field)
    assert field and field.get('native'),'Visible input must use a native widget'
    native_controls.text(int(field['nativeHandle']),text)

def end(window,interrupt=False):
    if interrupt:os.killpg(app.pid,signal.SIGINT)
    else:close(window)
    assert app.wait(timeout=30)==0,open(log_path).read()[-5000:];log.close()
    assert 'Entry/home jobs, controls, buffers, Owner, project contexts and native surface disposed' in open(log_path).read()
def field_text(state,id):
    field=state['fields'].get(str(id))
    if isinstance(field,str):field=json.loads(field)
    return field['text'] if field else None

def export_save(path):
    dialog=await_window(b'Export working copy')
    native_controls.resize(display,dialog,800,600);flush(display);time.sleep(.3)
    native_controls.click(dialog,300,180)
    native_controls.key(dialog,'l',(0xFFE3,));native_controls.text(dialog,path)
    native_controls.key(dialog,0xFF0D);time.sleep(.3)
    if find(b'Export working copy'):
        native_controls.click(dialog,755,575)
    deadline=time.monotonic()+10
    while find(b'Export working copy') and time.monotonic()<deadline:time.sleep(.04)
    assert not find(b'Export working copy'),'Native export chooser did not close within original 10-second condition'

try:
    a=launch();wait(lambda t:t['screen']=='intro' and 1 in t['hits'][::5],'intro');click(a,1)
    state=wait(lambda t:t['screen']=='home','home');controls=state['controls'];buffers=state['buffers']
    click(a,2);wait(lambda t:t['screen']=='create','create');click(a,10);type_text(a,'Source Flow')
    click(a,11);type_text(a,'Persistent source draft')
    # Keep the normal parent chooser, original per-character driver and ten-second close gate.
    click(a,12);native_controls.folder(find,await_window,storage)
    wait(lambda t:not t['nativePickerPending'] and field_text(t,30)==storage,'parent picker')
    click(a,13);state=wait(lambda t:t['screen']=='project','actual project creation')
    manifest=state['model']['selected']['path'];source=os.path.join(os.path.dirname(manifest),'main.csbody')
    original=open(source,encoding='utf-8').read();assert original=='return 0;\n'
    click(a,55);state=wait(lambda t:t['model'].get('workspace') and 54 in t['fields'],'source editor')
    assert state['model']['workspace']['unit']['kind']=='body'
    click(a,54);type_text(a,'return 17;\n');wait(lambda t:field_text(t,54)=='return 17;\n','typed source')
    click(a,58);state=wait(lambda t:t['model']['status'].startswith('Local source draft saved'),'draft saved')
    assert open(source,encoding='utf-8').read()==original,'Save must retain final source'
    assert state['controls']==controls and state['buffers']==buffers,'no wholesale control recreation'
    source_handle=json.loads(state['fields']['54'])['nativeHandle']
    resize(display,a,760,620);flush(display)
    state=wait(lambda t:t['width']==760 and 54 in t['fields'] and field_text(t,54)=='return 17;\n','source editor responsive resize')
    assert state['controls']==controls and state['buffers']==buffers
    assert json.loads(state['fields']['54'])['nativeHandle']==source_handle,'resize preserves native source field'
    for i in range(0,len(state['hits']),5):
        _,x,y,w,h=state['hits'][i:i+5];assert 0<=x<x+w<=760 and 0<=y<y+h<=620,'responsive visible hit confined'
    resize(display,a,1000,760);flush(display)
    wait(lambda t:t['width']==1000 and field_text(t,54)=='return 17;\n','source editor expanded')
    leave_project(a);wait(lambda t:t['screen']=='home','leave');click(a,100);wait(lambda t:t['screen']=='project','reopen')
    click(a,55);state=wait(lambda t:field_text(t,54)=='return 17;\n','same-process restored draft')
    first_native=json.loads(state['fields']['54'])['nativeHandle'];click(a,58)
    wait(lambda t:t['model']['status'].startswith('Local source draft saved') and not t['job'],'repeat save')
    assert json.loads(latest()['fields']['54'])['nativeHandle']==first_native,'save preserves native source field'
    end(a)
    a=launch();wait(lambda t:t['screen']=='intro' and 1 in t['hits'][::5],'restart');click(a,1)
    state=wait(lambda t:t['screen']=='home' and len(t['model']['cards'])==1,'recent project persisted')
    assert state['controls']!=controls,'fresh process owner'
    click(a,100);wait(lambda t:t['screen']=='project','recent reopen');click(a,55)
    wait(lambda t:field_text(t,54)=='return 17;\n','process restart persisted source draft')
    archive=os.path.join(storage,'source-workcopy.zip');click(a,59);export_save(archive)
    wait(lambda t:not t['nativePickerPending'] and t['message']=='Working-copy ZIP saved','export acknowledgement')
    assert os.path.isfile(archive),'native save produced ZIP'
    with zipfile.ZipFile(archive) as z:
        names=z.namelist();assert 'project.cproj' in names and 'main.csbody' in names
        assert z.read('main.csbody').decode('utf-8')=='return 17;\n','ZIP overlays current source draft'
        assert 'standalone true' in z.read('project.cproj').decode('utf-8')
        assert any('ProjectInfo' in n or 'ProjectInfo' in z.read(n).decode('utf-8',errors='ignore') for n in names if not n.endswith('/')),'ZIP retains saved ProjectInfo'
    assert open(source,encoding='utf-8').read()==original,'Export must retain final source'
    end(a)
    print('Actual EditorHome Linux create/edit/save/leave/reopen/process-restart/native ZIP export, draft overlay and stable Owner cleanup PASS')
    print('Private evidence: '+storage)
finally:
    if app is not None and app.poll() is None:os.killpg(app.pid,signal.SIGTERM);app.wait(timeout=10)
    if log is not None and not log.closed:log.close()
