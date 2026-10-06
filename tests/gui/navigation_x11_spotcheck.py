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

import threading,atexit
process=None
def cleanup():
    if process is not None and process.poll() is None:
        process.send_signal(signal.SIGINT)
        try:process.wait(timeout=30)
        except subprocess.TimeoutExpired:process.kill()
atexit.register(cleanup)
env=os.environ.copy();env['CONFECTORY_NAV_TRACE']='1';process=subprocess.Popen(report['run'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);events={0:[],1:[]};lines=[]
def reader():
    for line in process.stdout:
        lines.append(line.rstrip())
        if line.startswith('NAV_UI event '):
            view,payload=line[len('NAV_UI event '):].split(' ',1);events[int(view)].append(json.loads(payload))
thread=threading.Thread(target=reader,daemon=True);thread.start()
def until(predicate,why):
    end=time.monotonic()+12
    while time.monotonic()<end:
        if predicate():return
        time.sleep(.02)
    raise AssertionError(why)
a=await_window(b'Confectory Navigation A');b=await_window(b'Confectory Navigation B')
press(a,0xff09);until(lambda:events[0] and events[0][-1]['active']=='inventory','Tab did not open inventory');assert not events[1] or events[1][-1]['active']=='game'
press(a,0xffc3);until(lambda:events[0][-1]['focus']==2,'F6 did not traverse internal group')
press(a,0xff09);until(lambda:events[0][-1]['active']=='game','same Tab did not close inventory');assert events[0][-1]['focus']==1
press(b,0xff09);until(lambda:events[1] and events[1][-1]['active']=='inventory','second window state absent');assert events[0][-1]['active']=='game'
press(a,'T');time.sleep(.08);press(a,0xff09);time.sleep(.12);assert events[0][-1]['active']=='game' and not events[0][-1]['consumed']
subprocess.run(['import','-display',os.environ['DISPLAY'],'-window',str(a),'/tmp/navigation-gui-game.png'],check=True);subprocess.run(['import','-display',os.environ['DISPLAY'],'-window',str(b),'/tmp/navigation-gui-inventory.png'],check=True)
close(a);until(lambda:not find(b'Confectory Navigation A'),'selected close failed');assert find(b'Confectory Navigation B')==b
process.send_signal(signal.SIGINT);assert process.wait(timeout=30)==0;thread.join(3);assert any('cleanup complete' in x for x in lines);assert not find(b'Confectory Navigation B')
print('Actual X11 Tab open/close, independent F6 traversal, two-window state, text gating, selected close/SIGINT cleanup PASS')
