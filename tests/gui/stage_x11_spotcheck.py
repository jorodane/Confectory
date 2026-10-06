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


import threading

def start():
    env=os.environ.copy();env.update(CONFECTORY_STAGE_MODE='ui',CONFECTORY_STAGE_TRACE='1')
    env.pop('CONFECTORY_STAGE_CLOSE_MS',None)
    process=subprocess.Popen(report['run'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    lines=[]
    def read():
        for line in process.stdout:lines.append(line.rstrip());print(line,end='',flush=True)
    thread=threading.Thread(target=read,daemon=True);thread.start()
    return process,lines,thread

def snapshot(lines,index):
    prefix='STAGE_UI snapshot '+str(index)+' '
    for line in reversed(lines):
        if line.startswith(prefix):return json.loads(line[len(prefix):])
    return None

def wait(predicate,message):
    end=time.monotonic()+10
    while time.monotonic()<end:
        if predicate():return
        time.sleep(.01)
    raise AssertionError(message)

process,lines,thread=start()
try:
    a=await_window(b'Confectory Stage A');b=await_window(b'Confectory Stage B')
    wait(lambda:snapshot(lines,0) and snapshot(lines,1),'two live coherent public snapshots')
    aid=snapshot(lines,0)['stage']['resource'];bid=snapshot(lines,1)['stage']['resource']
    press(a,65363)
    wait(lambda:snapshot(lines,0)['scene']['camera'][0]==15,'A arrow camera applied')
    assert snapshot(lines,1)['scene']['camera'][0]==0
    press(a,'s');wait(lambda:snapshot(lines,0)['stage']['status']=='stopped','A stopped')
    model=snapshot(lines,0)['stage']['model'];before=snapshot(lines,1)['stage']['model'][0]
    time.sleep(.15)
    assert snapshot(lines,0)['stage']['model']==model
    assert snapshot(lines,1)['stage']['model'][0]>before
    press(a,65363);time.sleep(.05);assert snapshot(lines,0)['scene']['camera'][0]==15
    press(a,'e');wait(lambda:snapshot(lines,0)['stage']['status']=='active','A returned')
    assert snapshot(lines,0)['stage']['resource']==aid and find(b'Confectory Stage A')==a
    assert snapshot(lines,0)['scene']['camera'][0]==15
    press(a,'t');wait(lambda:snapshot(lines,0)['stage']['status']=='stopped','stop-prior transition')
    assert snapshot(lines,1)['stage']['status']=='active' and snapshot(lines,1)['stage']['resource']==bid
    press(b,'b');wait(lambda:snapshot(lines,0)['stage']['status']=='active','both coexisting')
    subprocess.run(['import','-display',os.environ['DISPLAY'],'-window','root','/tmp/checkpoint10-stage-live.png'],check=True)
    press(a,'q');wait(lambda:find(b'Confectory Stage A') is None,'A closed only')
    assert find(b'Confectory Stage B')==b
    close(b);process.wait(timeout=10);thread.join(timeout=2)
    assert process.returncode==0,process.stderr.read()
    assert 'Stage owner cleanup complete' in lines
finally:
    if process.poll() is None:process.kill();process.wait()
# A fresh native run proves reopen and interrupt release of both Owners/surfaces.
process,lines,thread=start()
try:
    await_window(b'Confectory Stage A');await_window(b'Confectory Stage B')
    wait(lambda:any('STAGE_UI ready' in x for x in lines),'reopen ready')
    process.send_signal(signal.SIGINT);process.wait(timeout=10);thread.join(timeout=2)
    assert process.returncode==0,process.stderr.read()
    assert 'Stage owner cleanup complete' in lines
    wait(lambda:find(b'Confectory Stage A') is None and find(b'Confectory Stage B') is None,'interrupt surface cleanup')
finally:
    if process.poll() is None:process.kill();process.wait()
print('Stage actual X11 two-window camera/model isolation, stop/return/transition, close-other-survives, reopen and SIGINT PASS')
