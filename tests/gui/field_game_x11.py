#!/usr/bin/env python3
"""Actual X11 shared Field font metrics, pixels, drag/capture, viewport and lifetime."""
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

stamp=1000
def press(window,key,flags=0):
    global stamp
    stamp+=10
    for kind in (2,3):
        event=Event(kind,0,1,display,window,root,0,stamp,0,0,0,0,flags,keycode(display,key if isinstance(key,int) else ord(key)),1)
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


import tempfile
repo=os.path.abspath(os.path.join(os.path.dirname(__file__),'../..'));env=os.environ.copy();env.update(CONFECTORY_FIELD_GAME_GUI='1',CONFECTORY_FIELD_GAME_TRACE='1')
log_path=tempfile.mktemp(prefix='confectory-field-game-',suffix='.log')
log=open(log_path,'w',encoding='utf-8');app=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
def latest(view):
    result=None
    with open(log_path,encoding='utf-8') as stream:
        for line in stream:
            if line.startswith('FIELD_GAME_UI '):
                try:
                    data=json.loads(line[14:])
                    if data['view']==view:result=data
                except json.JSONDecodeError:pass
    return result
def wait(predicate,message,view=0):
    end=time.monotonic()+15
    while time.monotonic()<end:
        data=latest(view)
        if data and predicate(data):return data
        if app.poll() is not None:raise AssertionError(open(log_path).read()[-3000:])
        time.sleep(.02)
    raise AssertionError(message+' '+str(latest(view)))
def mouse(window,kind,x,y):
    event=Event(kind,0,1,display,window,root,0,200,x,y,0,0,0,1,1);buffer=c.create_string_buffer(192);c.memmove(buffer,c.byref(event),c.sizeof(event));assert send(display,window,0,0,buffer);flush(display)
def sample(window,x,y):
    bitmap=image(display,window,x,y,1,1,U(-1).value,2);assert bitmap
    try:return pixel(bitmap,0,0)&0xffffff
    finally:destroy(bitmap)
def wait_pixel(window,color):
    end=time.monotonic()+5
    while time.monotonic()<end:
        if sample(window,25,75)==color:return
        time.sleep(.01)
    raise AssertionError(f'Shared Button actual presentation {color:x} not painted')
grab=native('XGrabPointer',c.c_int,P,U,c.c_int,c.c_uint,c.c_int,c.c_int,U,U,U)
ungrab=native('XUngrabPointer',c.c_int,P,U)
sync=native('XSync',c.c_int,P,c.c_int)
resize=native('XResizeWindow',c.c_int,P,U,c.c_uint,c.c_uint)
lookup=native('XKeycodeToKeysym',U,P,c.c_ubyte,c.c_int)
set_focus=native('XSetInputFocus',c.c_int,P,U,c.c_int,U)
def capture(window,wanted):
    if wanted==1:wait(lambda t:t.get('pressed',0)!=0,'logical press processed before native capture probe')
    end=time.monotonic()+4
    while time.monotonic()<end:
        status=grab(display,window,0,76,1,1,0,0,0)
        if status==0:ungrab(display,0);sync(display,0)
        if status==wanted:return
        time.sleep(.02)
    raise AssertionError(f'Native capture status {status}, expected {wanted}')
def click_at(window,x,y):
    mouse(window,4,x,y);time.sleep(.06);mouse(window,5,x,y)
def type_text(window,text):
    global stamp
    press(window,0xFFC1)
    for char in text:
        stamp+=10;symbol=ord(char);code=keycode(display,symbol);assert code
        shift=1 if lookup(display,code,0)!=symbol and lookup(display,code,1)==symbol else 0
        for kind in (2,3):
            event=Event(kind,0,1,display,window,root,0,stamp,0,0,0,0,shift,code,1)
            buffer=c.create_string_buffer(192);c.memmove(buffer,c.byref(event),c.sizeof(event));assert send(display,window,0,0,buffer)
        flush(display)
    time.sleep(.1)
def alignment(window,frame):
    origin=frame['textOrigins'][:2];caret=frame['caret'];positions=frame['metrics']['lines'][0]['positions']
    assert caret[0]==origin[0]+positions[-1],(caret,origin,positions)
    assert caret[1]==origin[1] and caret[3]==frame['metrics']['height']
    end=time.monotonic()+4
    while time.monotonic()<end:
        if sample(window,caret[0],caret[1]+caret[3]//2)==0xFFDC80:break
        time.sleep(.02)
    else:raise AssertionError('Measured native end caret not painted at measured pixel')
    bitmap=image(display,window,*frame['content'][:2],*frame['content'][2:],U(-1).value,2);assert bitmap
    try:
        # Actual Unicode glyph paint must be present inside the supplied font-height clip.
        points=[]
        for yy in range(frame['content'][3]):
            for xx in range(frame['content'][2]):
                if pixel(bitmap,xx,yy)&0xffffff==0xFFFFFF:points.append((xx+frame['content'][0],yy+frame['content'][1]))
        assert points,'Native shaped glyph pixels absent'
        assert all(origin[1]<=yy<origin[1]+frame['metrics']['height'] for _,yy in points)
    finally:destroy(bitmap)
try:
    a=await_window(b'Confectory Field Game A');b=await_window(b'Confectory Field Game B')
    t=wait(lambda t:t['field1']['visible'],'initial fields');f=t['field1'];o=f['textOrigins'];pos=f['metrics']['lines'][0]['positions']
    click_at(a,o[0]+pos[1],o[1]+4);wait(lambda t:t['name'][2]=='1','native measured click caret')
    press(a,0xFF57);t=wait(lambda t:t['name'][2]=='6','end caret');alignment(a,t['field1'])
    assert pos[1]!=pos[2]-pos[1],'fixture must use variable width actual font'
    assert pos[3]>pos[2] and pos[4]>pos[3] and pos[5]==-1,'Korean glyph and emoji scalar metrics'
    unicode_shot=tempfile.mktemp(prefix='confectory-field-unicode-',suffix='.png');subprocess.run(['import','-window',str(a),unicode_shot],check=True)
    o=t['field1']['textOrigins'];mouse(a,4,o[0]+pos[1],o[1]+4);wait(lambda t:t['name'][2]=='1','range start');capture(a,1)
    mouse(a,6,o[0]+pos[4],o[1]+4);wait(lambda t:t['name'][4:6]==['1','4'],'drag measured range');mouse(a,5,o[0]+pos[4],o[1]+4);capture(a,0)
    press(a,'x');wait(lambda t:t['name'][1]=='Wx😀','range replacement');assert latest(1)['name'][1]=='Wi한글😀'
    # Actual capture survives dragging outside the window, then cancellation releases it.
    t=latest(0);o=t['field1']['textOrigins'];mouse(a,4,o[0],o[1]+4);wait(lambda t:t['name'][2]=='0','cancel start');capture(a,1)
    mouse(a,6,-20,o[1]+4);time.sleep(.1);assert latest(0)['name'][2]=='0','outside drag maps bounded scalar caret'
    event=Event(10,0,1,display,a,root,0,0,0,0,0,0,0,0,1);buffer=c.create_string_buffer(192);c.memmove(buffer,c.byref(event),c.sizeof(event));assert send(display,a,0,0,buffer);flush(display);capture(a,0)
    mouse(a,6,o[0]+50,o[1]+4);mouse(a,5,o[0]+50,o[1]+4);time.sleep(.2);assert latest(0)['name'][2]=='0','late drag after cancel changed caret'
    mouse(a,4,o[0],o[1]+4);capture(a,1);set_focus(display,b,1,0);set_focus(display,a,1,0);flush(display);capture(a,0)
    mouse(a,6,o[0]+50,o[1]+4);mouse(a,5,o[0]+50,o[1]+4);time.sleep(.15);assert latest(0)['name'][2]=='0','real transient other-window focus loss must cancel even after focus returns'
    type_text(a,'W'*90);press(a,0xFF57);t=wait(lambda t:len(t['name'][1])==90 and t['field1']['scrollX']>0,'horizontal scroll')
    alignment(a,t['field1']);f=t['field1'];o=f['textOrigins'];positions=f['metrics']['lines'][0]['positions'];x=f['content'][0]+f['metrics']['insetX']+10
    index=min((n for n,p in enumerate(positions) if p>=0),key=lambda n:abs(o[0]+positions[n]-x));click_at(a,x,o[1]+4);wait(lambda t:int(t['name'][2])==index,'scrolled click maps full run')
    type_text(a,'Player');press(a,0xFF50);press(a,0xFF53,1);wait(lambda t:t['name'][4:6]==['0','1'],'shift keyboard range');press(a,0xFF57);press(a,0xFF09);wait(lambda t:t['focus']==2,'Tab between generic fields');type_text(a,'oops');press(a,0xFF0D);wait(lambda t:t['error'] and t['score']==0 and t['amount'][1]=='oops','domain format rejection retains text')
    type_text(a,'2');press(a,0xFF0D);wait(lambda t:t['score']==2 and not t['error'],'valid generic JSON input');assert latest(1)['score']==0
    press(a,0xFF09);wait(lambda t:t['focus']==3,'button focus');press(a,0xFFC3);wait(lambda t:t['group']=='menu' and not t['field1']['visible'],'hidden fields')
    saved=latest(0)['name'][1];click_at(a,40,105);time.sleep(.1);assert latest(0)['name'][1]==saved,'hidden Field accepted pointer'
    press(a,0xFFC3);wait(lambda t:t['group']=='game' and t['field1']['visible'],'show fields')
    # Resize cancels native pointer capture without losing text/model state.
    t=latest(0);o=t['field2']['textOrigins'];mouse(a,4,o[0],o[1]+4);capture(a,1);resize(display,a,440,390);flush(display);capture(a,0)
    wait(lambda t:t['field1']['bounds'][2]==400,'responsive Stack geometry');mouse(a,5,o[0],o[1]+4)
    token=latest(0)['controlToken'];name=latest(0)['name'][1];close(a);before=latest(1)['frames'];wait(lambda t:t['frames']>before+5,'other view continues',1)
    press(b,0xFFC4);a=await_window(b'Confectory Field Game A');t=wait(lambda t:t['controlToken']!=token,'fresh reopened UI lifetime');assert t['name'][1]==name and t['score']==2
    screenshot=tempfile.mktemp(prefix='confectory-field-game-',suffix='.png');subprocess.run(['import','-window',str(a),screenshot],check=True)
    close(a);close(b);assert app.wait(timeout=15)==0;log.close();assert 'buffers/control/owner/native cleanup complete' in open(log_path).read()
    main_log_path=log_path;interrupt_log=tempfile.mktemp(prefix='confectory-field-interrupt-',suffix='.log');log_path=interrupt_log;log=open(interrupt_log,'w',encoding='utf-8');app=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    a=await_window(b'Confectory Field Game A');await_window(b'Confectory Field Game B');time.sleep(.15)
    mouse(a,4,40,105);capture(a,1);os.killpg(app.pid,signal.SIGINT);assert app.wait(timeout=15)==0;log.close();capture(root,0)
    assert 'buffers/control/owner/native cleanup complete' in open(interrupt_log).read(),'interrupt lost cleanup'
    print('Editor-free native Field measured font/caret pixels, Unicode, click/drag/capture/cancel, scrolling, format policy, resize/close/reopen and cleanup PASS')
    print('Private evidence:',main_log_path,unicode_shot,screenshot,interrupt_log)
finally:
    if app.poll() is None:os.killpg(app.pid,signal.SIGINT);app.wait(timeout=15)
    if not log.closed:log.close()
