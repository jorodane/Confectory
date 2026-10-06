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


import tempfile,shutil,shlex
lookup=native('XKeycodeToKeysym',U,P,c.c_ubyte,c.c_int)
resize=native('XResizeWindow',c.c_int,P,U,c.c_uint,c.c_uint)
raise_window=native('XRaiseWindow',c.c_int,P,U)
repo=os.path.abspath(os.path.join(os.path.dirname(__file__),'../..'))
storage=tempfile.mkdtemp(prefix='confectory-entry-home-gui-')
for n in range(10):os.mkdir(os.path.join(storage,f'Folder{n:02d}'))
log_path=os.path.join(storage,'native.log')
env=os.environ.copy();env.update(CONFECTORY_EDITOR_REPO=repo,CONFECTORY_HOME_STORAGE=storage,CONFECTORY_HOME_TRACE='1',CONFECTORY_ELEMENT_AUTHORING_HOST=os.path.join(repo,'targets/element-authoring/bin/Release/net8.0/Confectory.ElementAuthoring.dll'))
folder_request=os.path.join(storage,'folder-request.txt');os_helper=os.path.join(storage,'os-helper');os.mkdir(os_helper)
with open(os.path.join(os_helper,'xdg-open'),'w') as stream:stream.write('#!/bin/sh\nprintf "%s\\n" "$1" > '+shlex.quote(folder_request)+'\n')
os.chmod(os.path.join(os_helper,'xdg-open'),0o700);env['PATH']=os_helper+os.pathsep+env.get('PATH','')
stall=os.path.join(storage,'stall-description')
wrapper=os.path.join(storage,'existing-dotnet-test-wrapper.sh')
with open(wrapper,'w') as stream:stream.write('#!/bin/sh\nif [ "$2" = "describe" ] && [ -f '+shlex.quote(stall)+' ]; then sleep 1; fi\nexec '+shlex.quote(os.environ.get('CONFECTORY_DOTNET') or shutil.which('dotnet'))+' "$@"\n')
os.chmod(wrapper,0o700);env['CONFECTORY_DOTNET']=wrapper
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
    screenshot(window,'native-create-validation')
    # Button text uses layout top-left origins; glyphs must occupy the upper half,
    # with no baseline shifted into a bottom crop. Multiline empty space keeps content color.
    ids=state['hits'][::5];n=ids.index(13)*5;_,x,y,w,h=state['hits'][n:n+5]
    bitmap=image(display,window,x,y,w,h,U(-1).value,2);assert bitmap
    try:assert sum(pixel(bitmap,i,j)==0xFFFFFF for i in range(w) for j in range(h//2))>8,'button text vertically clipped'
    finally:destroy(bitmap)
    field=json.loads(state['fields']['11']);x,y,w,h=field['bounds']
    bitmap=image(display,window,x,y,w,h,U(-1).value,2);assert bitmap
    try:assert field['native'] and field['provider']=='gtk3';assert pixel(bitmap,w//2,h-8)==0xFFFFFF,'native multiline content remains visible'
    finally:destroy(bitmap)

def end(window,interrupt=False):
    if interrupt:os.killpg(app.pid,signal.SIGINT)
    else:close(window)
    assert app.wait(timeout=30)==0,open(log_path).read()[-5000:];log.close()
    assert 'Entry/home jobs, controls, buffers, Owner, project contexts and native surface disposed' in open(log_path).read()
try:
    a=launch();wait(lambda t:t['screen']=='intro' and 1 in t['hits'][::5],'optional startup');screenshot(a,'intro')
    click(a,6);wait(lambda t:t['screen']=='manage','connection presentation');assert latest()['model']['cards']==[]
    click(a,1);state=wait(lambda t:t['screen']=='home','Later offline');screenshot(a,'home-empty');token=state['controls'];buffers=state['buffers']
    click(a,2);wait(lambda t:t['screen']=='create','New');click(a,13);state=wait(lambda t:t['focus']==10 and 'required' in t['message'],'required name focus');assert state['fields']['10']
    click(a,10);type_text(a,'Gui Home');click(a,11);type_text(a,'Initial intent\nNo Agent required');state=wait(lambda t:'No Agent required' in json.loads(t['fields']['11'])['text'],'multiline intent');assert_text_and_field_pixels(a,state);screenshot(a,'create')
    # Tab exits multiline field through the shared configured navigation policy.
    press(a,0xFF09);wait(lambda t:t['focus']==12,'shared Tab navigation')
    click(a,12);native_controls.folder(find,await_window,storage);wait(lambda t:not t['nativePickerPending'] and 12 in t['hits'][::5],'native parent selected')
    click(a,13);state=wait(lambda t:t['screen']=='project','create enters project');assert state['model']['selected']['title']=='Gui Home';path=state['model']['selected']['path'];assert os.path.isfile(path)
    leave_project(a);state=wait(lambda t:t['screen']=='home' and len(t['model']['cards'])==1,'leave to cards');assert state['controls']==token and state['buffers']==buffers;screenshot(a,'home-card')
    click(a,101);assert open(folder_request).read().strip()==os.path.dirname(path),'OS folder request uses selected project directory'
    # First add card and project card occupy equal columns on the same row.
    ids=state['hits'][::5];new=state['hits'][ids.index(2)*5:ids.index(2)*5+5];card=state['hits'][ids.index(100)*5:ids.index(100)*5+5];assert card[1]>new[1] and abs(card[2]-new[2])<90
    resize(display,a,640,520);flush(display);state=wait(lambda t:t['width']==640 and 100 in t['hits'][::5],'responsive cards');assert state['controls']==token
    for i in range(0,len(state['hits']),5):_,x,y,w,h=state['hits'][i:i+5];assert 0<=x<x+w<=640 and 0<=y<y+h<=520
    screenshot(a,'home-narrow');click(a,7);wait(lambda t:not t['sidebar'],'collapse');click(a,7);wait(lambda t:t['sidebar'],'expand')
    click(a,100);wait(lambda t:t['screen']=='project','reopen existing');leave_project(a);wait(lambda t:t['screen']=='home','leave again')
    click(a,3);native_controls.folder(find,await_window,storage);wait(lambda t:t['model']['status'].startswith('Error:'),'invalid folder not registered');assert len(latest()['model']['cards'])==1
    click(a,3);native_controls.folder(find,await_window,cancel=True);wait(lambda t:not t['nativePickerPending'] and 3 in t['hits'][::5],'cancel native picker')
    click(a,102);wait(lambda t:t['screen']=='remove','explicit listing removal');click(a,18);wait(lambda t:t['screen']=='home' and len(t['model']['cards'])==1,'remove cancelled')
    end(a)
    # Seed additional valid copied projects as persistent catalog fixtures, then test actual card paging.
    catalog=json.load(open(os.path.join(storage,'projects.json')))
    for n in range(6):
        directory=os.path.join(storage,f'Recent{n}');shutil.copytree(os.path.dirname(path),directory)
        catalog.append({'path':os.path.join(directory,'project.cpack'),'title':f'Recent {n}','description':'Valid local project fixture'})
    with open(os.path.join(storage,'projects.json'),'w') as stream:json.dump(catalog,stream)
    a=launch();wait(lambda t:t['screen']=='intro' and 1 in t['hits'][::5],'restart intro');click(a,1);state=wait(lambda t:t['screen']=='home' and len(t['model']['cards'])==7,'restart catalog');assert state['controls']!=token
    click(a,4);wait(lambda t:2 not in t['hits'][::5] and 103 in t['hits'][::5],'project card next row');click(a,5);wait(lambda t:2 in t['hits'][::5] and 100 in t['hits'][::5],'project card previous row')
    click(a,102);wait(lambda t:t['screen']=='remove','remove listing');click(a,17);wait(lambda t:t['screen']=='home' and len(t['model']['cards'])==6,'remove persist');assert os.path.isfile(path)
    # Stall only the existing public description host in a private test wrapper.
    # Prove the UI keeps rendering during an owned in-flight project job, then joins it on SIGINT.
    open(stall,'w').close();click(a,3);native_controls.folder(find,await_window,os.path.dirname(path));wait(lambda t:t['job'],'in-flight description job remains responsive');end(a,interrupt=True)
    print('Entry/home actual X11 intro/connect/Later, offline create/required focus, multiline/Tab, native folder selection/validation/cancel, two-column cards/paging, OS folder request, stable controls/buffers, resize/collapse, repeated open, restart/removal, close and verified in-flight interrupt cleanup PASS')
    print('Private GUI evidence: '+storage)
finally:
    if app is not None and app.poll() is None:os.killpg(app.pid,signal.SIGTERM);app.wait(timeout=10)
    if log is not None and not log.closed:log.close()
