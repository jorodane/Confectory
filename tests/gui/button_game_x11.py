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


import tempfile
repo=os.path.abspath(os.path.join(os.path.dirname(__file__),'../..'));env=os.environ.copy();env.update(CONFECTORY_BUTTON_GAME_GUI='1',CONFECTORY_BUTTON_GAME_TRACE='1')
log_path=tempfile.mktemp(prefix='confectory-button-game-',suffix='.log')
log=open(log_path,'w',encoding='utf-8');app=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
def latest(view):
    result=None
    with open(log_path,encoding='utf-8') as stream:
        for line in stream:
            if line.startswith('BUTTON_GAME_UI '):
                try:
                    data=json.loads(line[15:])
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
try:
    a=await_window(b'Confectory Button Game A');b=await_window(b'Confectory Button Game B');wait(lambda t:t['score']==0,'initial score')
    wait_pixel(a,0x28465D);mouse(a,4,30,80);wait_pixel(a,0x1A3447);mouse(a,5,30,80);wait(lambda t:t['score']==1,'shared pointer activation');assert latest(1)['score']==0,'game state leaked to B'
    press(a,0xFF09);wait(lambda t:t['focus']==2,'shared button navigation');press(a,0xFF0D);wait(lambda t:t['score']==0,'shared keyboard reset')
    mouse(b,4,30,80);mouse(b,5,30,80);wait(lambda t:t['score']==1,'B independent activation',1);assert latest(0)['score']==0
    mouse(a,4,30,80);event=Event(10,0,1,display,a,root,0,200,0,0,0,0,0,0,1);buffer=c.create_string_buffer(192);c.memmove(buffer,c.byref(event),c.sizeof(event));assert send(display,a,0,0,buffer);flush(display);time.sleep(.05);mouse(a,5,30,80);time.sleep(.15);assert latest(0)['score']==0,'focus loss did not cancel shared press'
    press(a,0xFFC3);wait(lambda t:t['group']=='menu','configured game menu');mouse(a,4,30,80);mouse(a,5,30,80);time.sleep(.15);assert latest(0)['score']==0,'hidden button activated'
    screenshot=tempfile.mktemp(prefix='confectory-button-game-',suffix='.png');subprocess.run(['import','-window',str(b),screenshot],check=True)
    close(a);before=latest(1)['frames'];wait(lambda t:t['frames']>before+5,'one window close keeps other View',1);close(b);assert app.wait(timeout=15)==0;log.close();assert 'control/owner/native cleanup complete' in open(log_path).read()
    print('Editor-free native game shares BaseUI Button paint/hit/keyboard/navigation/cancel/hidden/lifetime with independent state PASS');print('Private evidence:',log_path,screenshot)
finally:
    if app.poll() is None:os.killpg(app.pid,signal.SIGINT);app.wait(timeout=15)
    if not log.closed:log.close()
