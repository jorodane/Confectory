#!/usr/bin/env python3
"""Real X11 pixels: declared harvest/craft, intermediate throw, landing/fuse/effect, close/reopen."""
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

def find():
    r,parent,children,count=U(),U(),P(),c.c_uint();query(display,root,c.byref(r),c.byref(parent),c.byref(children),c.byref(count))
    try:
        for window in c.cast(children,c.POINTER(U))[:count.value]:
            name=P();fetch(display,window,c.byref(name))
            if name:
                try:
                    if c.string_at(name)==b'Confectory Harvest single':return window
                finally:free(name)
    finally:
        if children:free(children)

def await_window():
    end=time.monotonic()+10
    while time.monotonic()<end:
        window=find()
        if window:return window
        time.sleep(.01)
    raise AssertionError('Game surface not mapped')

def press(window,key):
    for kind in (2,3):
        event=Event(kind,0,1,display,window,root,0,100,0,0,0,0,0,keycode(display,ord(key)),1)
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

env=os.environ.copy();env.pop('CONFECTORY_GAME_MODE',None);env.pop('CONFECTORY_GAME_CLOSE_MS',None);env.pop('CONFECTORY_COMPARISON_INPUT',None);env.pop('CONFECTORY_COMPARISON_CASE',None)
for repetition in range(2):
    process=subprocess.Popen(report['run'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    try:
        window=await_window();time.sleep(.05)
        # A rejected craft must not acquire an item or display a projectile.
        press(window,'c');time.sleep(.03);assert not colored(window,0xF4D12D)
        press(window,'h');time.sleep(.03);press(window,'c');time.sleep(.03);press(window,'t')
        intermediate=wait_color(window,0xF4D12D,lambda p:110<sum(x for x,y in p)/len(p)<285 and sum(y for x,y in p)/len(p)<180,.65)
        landed=wait_color(window,0xF4D12D,lambda p:315<=sum(x for x,y in p)/len(p)<=325 and 185<=sum(y for x,y in p)/len(p)<=195,.9)
        assert not colored(window,0xEB7130),'Effect appeared before fuse interval'
        effect=wait_color(window,0xEB7130,lambda p:len(p)>10,.6)
        time.sleep(.7);assert not colored(window,0xEB7130),'Effect lifetime did not end'
        close(window);out,err=process.communicate(timeout=10);assert process.returncode==0,err+out
        traces=[json.loads(line) for line in out.splitlines() if line.startswith('{')]
        events=[t['event'] for t in traces]
        for event in ('craft-rejected','harvest-applied','craft-applied','throw-applied','phase-landed','phase-burst','phase-spent','closed'):assert event in events,event
        assert 'game owner cleanup complete' in out
        print(f'PASS actual X11 game repetition {repetition+1}: motion pixels, landing/fuse/effect, cleanup')
    finally:
        if process.poll() is None:process.kill();process.communicate(timeout=5)
process=subprocess.Popen(report['run'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
try:
    window=await_window();time.sleep(.05);press(window,'h');time.sleep(.03);press(window,'c');time.sleep(.03);press(window,'t');time.sleep(.1)
    process.send_signal(signal.SIGINT);out,err=process.communicate(timeout=10)
    assert process.returncode==0 and 'game owner cleanup complete' in out,err+out
    assert not find(),'Game surface survived cooperative interruption'
    print('PASS actual X11 game SIGINT: active-flight owner cleanup')
finally:
    if process.poll() is None:process.kill();process.communicate(timeout=5)
print('PASS harvest game actual Linux GUI close/reopen/interruption')
