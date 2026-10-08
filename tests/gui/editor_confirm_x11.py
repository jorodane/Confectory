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
storage=tempfile.mkdtemp(prefix='confectory-confirm-workspace-gui-',dir=os.environ.get('CONFECTORY_TEST_EVIDENCE_ROOT'))
owned=os.path.join(storage,'actual-owned-editor');os.mkdir(owned)
for name in os.listdir(os.path.join(repo,'examples/editor-home')):
    source=os.path.join(repo,'examples/editor-home',name)
    if os.path.isfile(source):
        shutil.copy2(source,os.path.join(owned,name))
        if name.endswith('.cpack'):
            with open(source) as stream:content=stream.read().replace('../../',repo+'/')
            with open(os.path.join(owned,name),'w') as stream:stream.write(content)
manifest=os.path.join(owned,'project.cpack');source=os.path.join(owned,'Main.csbody')
with open(source) as stream:original=stream.read()
with open(os.path.join(storage,'projects.json'),'w') as stream:json.dump([{'path':manifest,'title':'Owned editor pack','description':'Controlled actual source copy'}],stream)
log_path=os.path.join(storage,'native.log')
env=os.environ.copy();env.update(CONFECTORY_EDITOR_REPO=repo,CONFECTORY_HOME_STORAGE=storage,CONFECTORY_HOME_TRACE='1',CONFECTORY_ELEMENT_AUTHORING_HOST=os.path.join(repo,'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'),CONFECTORY_PROJECT_EXECUTION_HOST=os.path.join(repo,'targets/project-execution-host/bin/Release/net10.0/Confectory.ProjectExecutionHost.dll'))
app=None;log=None;launch_count=0
def launch():
    global app,log,launch_count,trace_offset,trace_value
    trace_offset=0;trace_value=None
    if launch_count and os.path.isfile(log_path):shutil.copy2(log_path,os.path.join(storage,f"native-launch-{launch_count}.log"))
    launch_count+=1
    log=open(log_path,'w',encoding='utf-8');app=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    return await_window(b'Confectory - Projects')
trace_offset=0;trace_value=None
def latest():
    global trace_offset,trace_value
    if os.path.getsize(log_path)<trace_offset:trace_offset=0;trace_value=None
    with open(log_path,encoding='utf-8') as stream:
        stream.seek(trace_offset)
        while True:
            line=stream.readline()
            if not line:break
            if not line.endswith('\n'):break
            trace_offset=stream.tell()
            if line.startswith('HOME_UI '):
                try:trace_value=json.loads(line[8:])
                except json.JSONDecodeError:pass
    return trace_value

def wait(predicate,message,seconds=30):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        state=latest()
        if state and predicate(state):return state
        if app.poll() is not None:raise AssertionError('Entry/home exited: '+open(log_path).read()[-3000:])
        time.sleep(.04)
    state=latest();review=(state['model'].get('workspace') or {}).get('review') or {}
    raise AssertionError(message+' '+str({'screen':state['screen'],'job':state['job'],'reviewStatus':review.get('status'),'status':state['model']['status'][:512]}))
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
    if find(b'Export working copy') and os.environ.get('CONFECTORY_DIALOG_FAILURE_SCREENSHOT'):
        subprocess.run(['import','-window',str(dialog),os.environ['CONFECTORY_DIALOG_FAILURE_SCREENSHOT']],check=False)
    assert not find(b'Export working copy'),'Native export chooser did not close within original 10-second condition'

def edit_at(window,position,text,expected):
    click(window,54);state=latest();f=state['fields']['54'];f=json.loads(f) if isinstance(f,str) else f
    handle=int(f['nativeHandle']);native_controls.key(handle,position,(0xFFE3,))
    for char in text:
        symbol=0xFF0D if char=='\n' else ord(char);code=native_controls.code(display,symbol)
        modifiers=(0xFFE1,) if native_controls.lookup(display,code,0)!=symbol and native_controls.lookup(display,code,1)==symbol else ()
        native_controls.key(handle,symbol,modifiers)
    wait(lambda t:field_text(t,54)==expected,'native edit')
def ready_source(window):
    click(window,55);return wait(lambda t:t['model'].get('workspace') and '54' in t['fields'],'source view')
def final():
    with open(source) as stream:return stream.read()
try:
    a=launch();wait(lambda t:t['screen']=='intro' and 1 in t['hits'][::5],'intro');click(a,1);wait(lambda t:t['screen']=='home','home');click(a,100);wait(lambda t:t['screen']=='project','owned actual editor');state=ready_source(a)
    assert state['model']['workspace']['unit']['path']=='Main.csbody'
    edited='Console.WriteLine("CONFIRMED_CHILD_ACTUAL_PACK");\n'+original
    edit_at(a,0xFF50,'Console.WriteLine("CONFIRMED_CHILD_ACTUAL_PACK");\n',edited);click(a,58);wait(lambda t:'saved' in t.get('message','').lower() or 'saved' in t['model']['status'].lower(),'save');assert final()==original
    click(a,64);state=wait(lambda t:t['model']['workspace'].get('review') and '67' in t['fields'] and '68' in t['fields'],'review')
    assert state['model']['workspace']['review']['path']=='Main.csbody' and field_text(state,67)==original and field_text(state,68)==edited
    assert state['model']['workspace']['review']['status']=='ready';assert 54 not in state['hits'][::5],'underlying source field accepts input during modal'
    subprocess.run(['import','-window',str(a),'/tmp/confectory-confirm-review.png'],check=True)
    click(a,66);wait(lambda t:t['model']['workspace'].get('review') is None and '54' in t['fields'],'cancel');assert final()==original and field_text(latest(),54)==edited
    leave_project(a);wait(lambda t:t['screen']=='home','leave');click(a,100);wait(lambda t:t['screen']=='project','reopen');ready_source(a);assert field_text(latest(),54)==edited
    # External final source changes after the user has reviewed: Confirm must refuse.
    click(a,64);wait(lambda t:t['model']['workspace'].get('review') and 65 in t['hits'][::5],'review again')
    external=original+'\n// independently edited final source\n'
    with open(source,'w') as stream:stream.write(external)
    click(a,65);wait(lambda t:t['model']['workspace'].get('review',{}).get('status')=='conflict' and not t['job'],'external conflict');assert final()==external
    click(a,66);wait(lambda t:t['model']['workspace'].get('review') is None,'cancel conflict');assert field_text(latest(),54)==edited
    # Restore the controlled fixture, not any user source, for the next independent failure.
    with open(source,'w') as stream:stream.write(original)
    invalid=edited+'\nBROKEN_CANDIDATE';edit_at(a,0xFF57,'\nBROKEN_CANDIDATE',invalid);click(a,64);wait(lambda t:t['model']['workspace'].get('review') and 65 in t['hits'][::5],'invalid review');click(a,65)
    wait(lambda t:t['model']['workspace'].get('review',{}).get('status')=='invalid' and not t['job'],'validation failure',340);assert final()==original
    click(a,66);wait(lambda t:t['model']['workspace'].get('review') is None,'cancel invalid');assert field_text(latest(),54)==invalid
    leave_project(a);wait(lambda t:t['screen']=='home','before restart');end(a,interrupt=True)
    a=launch();wait(lambda t:t['screen']=='intro' and 1 in t['hits'][::5],'restart intro');click(a,1);wait(lambda t:t['screen']=='home','restart');click(a,100);wait(lambda t:t['screen']=='project','restart open');ready_source(a);assert field_text(latest(),54)==invalid and final()==original
    click(a,54);f=json.loads(latest()['fields']['54']);handle=int(f['nativeHandle']);native_controls.key(handle,0xFF57,(0xFFE3,));native_controls.key(handle,0xFF50,(0xFFE1,));native_controls.key(handle,0xFF08);edited=edited+'\n';wait(lambda t:field_text(t,54)==edited,'repair invalid line');click(a,64);wait(lambda t:t['model']['workspace'].get('review') and 65 in t['hits'][::5],'valid review');click(a,65)
    wait(lambda t:t['model']['workspace'].get('review') is None and t['model']['status'].startswith('Confirm confirmed') and not t['job'],'successful confirm',340);assert final()==edited
    assert not latest()['model']['workspace']['unit']['dirty'];assert latest()['model']['workspace']['unit']['text']==edited
    click(a,36);state=wait(lambda t:t['model']['execution']['state']=='running' and any('CONFIRMED_CHILD_ACTUAL_PACK' in line for line in t['model']['shell']['logs']),'confirmed child editor',340)
    # Parent source View remains owned, while confirmed pack's actual Main creates a separate child.
    assert app.poll() is None and state['screen']=='project' and field_text(state,54)==edited
    r,parent,children,count=U(),U(),P(),c.c_uint();query(display,root,c.byref(r),c.byref(parent),c.byref(children),c.byref(count));named=[]
    try:
        for win in c.cast(children,c.POINTER(U))[:count.value]:
            name=P();fetch(display,win,c.byref(name))
            if name:
                try:
                    if c.string_at(name)==b'Confectory - Projects':named.append(win)
                finally:free(name)
    finally:free(children)
    assert len(named)>=2,'child did not open actual editor native window'
    subprocess.run(['import','-window',str(a),'/tmp/confectory-confirm-parent-after-run.png'],check=True)
    click(a,37);wait(lambda t:t['model']['execution']['state']=='stopped','stop child');leave_project(a);wait(lambda t:t['screen']=='home','final leave');end(a)
    print('PASS actual editor-home GUI owned self-pack Save-draft/review paths-before-after/cancel/reopen/external conflict/invalid compile/restart retention/explicit Confirm/confirmed-source child editor Run/parent isolation/Stop/cleanup')
    print('Private evidence: '+storage)
finally:
    if app is not None and app.poll() is None:os.killpg(app.pid,signal.SIGTERM);app.wait(timeout=10)
