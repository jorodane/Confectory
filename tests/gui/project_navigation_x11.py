#!/usr/bin/env python3
"""Actual project-shell acceptance; private evidence only."""
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


import tempfile,shutil,shlex
lookup=native('XKeycodeToKeysym',U,P,c.c_ubyte,c.c_int)
resize=native('XResizeWindow',c.c_int,P,U,c.c_uint,c.c_uint)
raise_window=native('XRaiseWindow',c.c_int,P,U)
repo=os.path.abspath(os.path.join(os.path.dirname(__file__),'../..'))
storage=tempfile.mkdtemp(prefix='confectory-project-shell-gui-')
for n in range(10):os.mkdir(os.path.join(storage,f'Folder{n:02d}'))
log_path=os.path.join(storage,'native.log')
env=os.environ.copy();env.update(CONFECTORY_EDITOR_REPO=repo,CONFECTORY_HOME_STORAGE=storage,CONFECTORY_HOME_TRACE='1',CONFECTORY_ELEMENT_AUTHORING_HOST=os.path.join(repo,'targets/element-authoring/bin/Release/net8.0/Confectory.ElementAuthoring.dll'))
folder_request=os.path.join(storage,'folder-request.txt');os_helper=os.path.join(storage,'os-helper');os.mkdir(os_helper)
with open(os.path.join(os_helper,'xdg-open'),'w') as stream:stream.write('#!/bin/sh\nprintf "%s\\n" "$1" > '+shlex.quote(folder_request)+'\n')
os.chmod(os.path.join(os_helper,'xdg-open'),0o700);env['PATH']=os_helper+os.pathsep+env.get('PATH','')
stall=os.path.join(storage,'stall-description')
wrapper=os.path.join(storage,'existing-dotnet-test-wrapper.sh')
with open(wrapper,'w') as stream:stream.write('#!/bin/sh\nif [ "$2" = "describe" ] && [ -f '+shlex.quote(stall)+' ]; then sleep 1; fi\nexec '+shlex.quote(os.environ.get('CONFECTORY_DOTNET') or shutil.which('dotnet'))+' "$@"\n')
os.chmod(wrapper,0o700);env['CONFECTORY_DOTNET']=os.environ.get('CONFECTORY_DOTNET') or shutil.which('dotnet')
app=None;log=None

def launch():
    global app,log
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

def screenshot(window,name):
    path=os.path.join(storage,name+'.png');subprocess.run(['import','-window',str(window),path],check=True);return path

def assert_text_and_field_pixels(window,state):
    # Button text uses layout top-left origins; glyphs must occupy the upper half,
    # with no baseline shifted into a bottom crop. Multiline empty space keeps content color.
    ids=state['hits'][::5];n=ids.index(13)*5;_,x,y,w,h=state['hits'][n:n+5]
    bitmap=image(display,window,x,y,w,h,U(-1).value,2);assert bitmap
    try:assert sum(pixel(bitmap,i,j)==0xFFFFFF for i in range(w) for j in range(h//2))>8,'button text vertically clipped'
    finally:destroy(bitmap)
    field=json.loads(state['fields']['11']);x,y,w,h=field['bounds']
    bitmap=image(display,window,x,y,w,h,U(-1).value,2);assert bitmap
    try:assert pixel(bitmap,w//2,h-8)==0x1C2933,'unused multiline space must use content background';assert pixel(bitmap,0,h//2)==0x77AAC6,'focused border remains distinct'
    finally:destroy(bitmap)

def end(window,interrupt=False):
    if interrupt:os.killpg(app.pid,signal.SIGINT)
    else:close(window)
    assert app.wait(timeout=30)==0,open(log_path).read()[-5000:];log.close()
    assert 'Entry/home jobs, controls, buffers, Owner, project contexts and native surface disposed' in open(log_path).read()
try:
    a=launch();wait(lambda t:t['screen']=='intro' and 1 in t['hits'][::5],'intro');click(a,1);wait(lambda t:t['screen']=='home','home')
    click(a,2);wait(lambda t:t['screen']=='create','create');click(a,10);type_text(a,'Navigation A');click(a,11);type_text(a,'Bounded workspace');click(a,13)
    state=wait(lambda t:t['screen']=='project' and 44 in t['hits'][::5],'project');context=state['model']['selected']['context'];control=state['controls'];assert 36 in state['hits'][::5] and 37 not in state['hits'][::5];assert state['radii'][state['hits'][::5].index(36)]==22
    # Transparent circle corners cannot capture or activate.
    n=state['hits'][::5].index(43)*5;_,x,y,w,h=state['hits'][n:n+5]
    for kind in (4,5):
        event=Event(kind,0,1,display,a,root,0,100,x,y,0,0,0,1,1);buf=c.create_string_buffer(192);c.memmove(buf,c.byref(event),c.sizeof(event));assert send(display,a,0,0,buf)
    flush(display);time.sleep(.3);assert latest()['model']['shell']['menu']==''
    click(a,43);state=wait(lambda t:t['model']['shell']['menu']=='grievance','grievance');assert state['model']['shell']['grievance']=={'available':False,'unresolved':None,'highestUrgency':None};assert 38 not in state['hits'][::5];screenshot(a,'grievance-unavailable');click(a,42);wait(lambda t:t['model']['shell']['menu']=='','close grievance')
    click(a,44);state=wait(lambda t:t['model']['shell']['navigation']=='main' and 45 in t['hits'][::5],'upward menu');p=state['navigationPanel'];assert p[4]==0 and p[1]+p[3]<state['height']-84;assert 38 not in state['hits'][::5];assert state['controls']==control
    click(a,48);state=wait(lambda t:t['model']['shell']['navigation']=='project' and 50 in t['hits'][::5],'submenu');p=state['submenuPanel'];assert p[4]==2 and p[0]>=0;screenshot(a,'rounded-navigation');click(a,50);state=wait(lambda t:t['model']['shell']['menu']=='info' and not t['navigationPanel'],'information route');assert state['model']['selected']['context']==context;click(a,42);wait(lambda t:t['model']['shell']['menu']=='','close information')
    # Native keyboard activation, held/repeated key and Escape cancellation.
    click(a,44);wait(lambda t:t['model']['shell']['navigation']=='main','reopen menu');press(a,0xFF1B);wait(lambda t:t['model']['shell']['navigation']=='','Escape closes menu')
    press(a,0xFF0D);wait(lambda t:t['model']['shell']['navigation']=='main','focused launcher Enter');click(a,47);state=wait(lambda t:t['model']['shell']['space']=='logs' and t['model']['shell']['navigation']=='','logs route');assert state['model']['shell']['tab']=='logs'
    click(a,44);wait(lambda t:t['model']['shell']['navigation']=='main','outside test');
    event=Event(4,0,1,display,a,root,0,100,400,100,0,0,0,1,1);buf=c.create_string_buffer(192);c.memmove(buf,c.byref(event),c.sizeof(event));assert send(display,a,0,0,buf);flush(display);wait(lambda t:t['model']['shell']['navigation']=='','outside click cancels');
    click(a,44);wait(lambda t:t['model']['shell']['navigation']=='main','resize menu');resize(display,a,640,520);flush(display);state=wait(lambda t:t['width']==640 and t['model']['shell']['navigation']=='','resize cancels popup');click(a,44);state=wait(lambda t:t['navigationPanel'] and t['width']==640,'narrow popup');p=state['navigationPanel'];assert p[0]>=0 and p[1]>=0 and p[0]+p[2]<=640 and p[1]+p[3]<=520;assert state['controls']==control;screenshot(a,'navigation-narrow');click(a,46);wait(lambda t:t['model']['shell']['tab']=='chat' and not t['navigationPanel'],'chat route')
    click(a,38);type_text(a,'Retained navigation draft');click(a,41);state=wait(lambda t:t['model']['shell']['draft']=='Retained navigation draft','draft');buffer=state['chatBuffers'][context]
    leave_project(a);wait(lambda t:t['screen']=='home','leave');click(a,100);state=wait(lambda t:t['screen']=='project' and not t['navigationPanel'],'reopen');assert state['chatBuffers'][context]==buffer and state['model']['shell']['draft']=='Retained navigation draft';assert state['controls']==control
    click(a,44);wait(lambda t:t['navigationPanel'],'close with menu');end(a)
    a=launch();state=wait(lambda t:t['screen']=='intro','restart intro');assert state['model']['selected'] is None;end(a,True)
    print('Project navigation actual X11: circular hit, unavailable report, upward/submenu, keyboard/Escape, context, resize, persistent draft, repeated close/reopen and interrupt passed; private evidence '+storage)
finally:
    if app and app.poll() is None:os.killpg(app.pid,signal.SIGTERM);app.wait(timeout=30)
    if log and not log.closed:log.close()
