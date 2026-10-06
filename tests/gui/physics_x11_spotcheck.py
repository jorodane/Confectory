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



import threading

def start(report_path):
    run=json.load(open(report_path))['run'];env=os.environ.copy();env.update(CONFECTORY_PHYSICS_MODE='ui',CONFECTORY_PHYSICS_TRACE='1')
    process=subprocess.Popen(run,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);lines=[];samples={'preview':[],0:[],1:[]}
    def reader():
        for line in process.stdout:
            lines.append(line.rstrip())
            if line.startswith('PHYSICS_UI snapshot '):
                scope,payload=line[len('PHYSICS_UI snapshot '):].split(' ',1);samples['preview' if scope=='preview' else int(scope)].append(json.loads(payload))
            else:print(line,end='',flush=True)
    thread=threading.Thread(target=reader,daemon=True);thread.start();return process,lines,samples,thread

def wait(predicate,message,seconds=10):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        if predicate():return
        time.sleep(.005)
    raise AssertionError(message)

def center(window,color):
    bitmap=image(display,window,0,0,480,320,U(-1).value,2);assert bitmap
    try:
        points=[]
        for y in range(32,295):
            for x in range(32,465):
                if pixel(bitmap,x,y)&0xffffff==color:points.append((x,y))
        assert points,'Actual colored circle pixels absent'
        return (sum(x for x,y in points)/len(points),sum(y for x,y in points)/len(points))
    finally:destroy(bitmap)

process,lines,samples,thread=start(sys.argv[1])
try:
    window=await_window(b'Confectory Physics preview');wait(lambda:len(samples['preview'])>2,'preview samples')
    initial=center(window,0xF4D12D)
    wait(lambda: samples['preview'][-1]['bodies'][1]['displayY']<1.2,'visible downward motion')
    fallen=center(window,0xF4D12D);assert fallen[1]>initial[1]+45
    wait(lambda:any(x['latestSequence']>0 for x in samples['preview']),'real collision events')
    wait(lambda:samples['preview'][-1]['bodies'][1]['vy']>0 and samples['preview'][-1]['bodies'][1]['displayY']>1.15,'post-contact upward velocity/motion')
    rebound=center(window,0xF4D12D);assert rebound[1]<240,'circle bounced above contact plane'
    subprocess.run(['import','-display',os.environ['DISPLAY'],'-window','root','/tmp/checkpoint11-physics-preview.png'],check=True)
    close(window);process.wait(timeout=10);thread.join(timeout=2)
    assert process.returncode==0,process.stderr.read();assert 'Physics preview cleanup complete' in lines
finally:
    if process.poll() is None:process.kill();process.wait()

for repetition in range(2):
    process,lines,samples,thread=start(sys.argv[2])
    try:
        a=await_window(b'Confectory Physics A');b=await_window(b'Confectory Physics B')
        wait(lambda:len(samples[0])>2 and len(samples[1])>2,'two Stage samples')
        aid=samples[0][-1]['world']['world'];bid=samples[1][-1]['world']['world'];assert aid!=bid
        wait(lambda:any(x['world']['latestSequence']>0 for x in samples[0]) and any(x['world']['latestSequence']>0 for x in samples[1]),'both worlds visibly collided')
        assert center(a,0xF4D12D) and center(b,0x49BEF4)
        if repetition==0:
            press(a,'s');wait(lambda:samples[0][-1]['stage']['status']=='stopped','stop only A')
            tick=samples[0][-1]['world']['tick'];before=samples[1][-1]['world']['tick'];time.sleep(.15)
            assert samples[0][-1]['world']['tick']==tick and samples[1][-1]['world']['tick']>before
            press(a,'e');wait(lambda:samples[0][-1]['stage']['status']=='active','return A')
            assert samples[0][-1]['world']['world']==aid and find(b'Confectory Physics A')==a
            subprocess.run(['import','-display',os.environ['DISPLAY'],'-window','root','/tmp/checkpoint11-physics-stages.png'],check=True)
            press(a,'q');wait(lambda:find(b'Confectory Physics A') is None,'close A only');assert find(b'Confectory Physics B')==b
            close(b)
        else:process.send_signal(signal.SIGINT)
        process.wait(timeout=10);thread.join(timeout=2);assert process.returncode==0,process.stderr.read()
        assert 'Physics Stage cleanup complete' in lines
        wait(lambda:find(b'Confectory Physics A') is None and find(b'Confectory Physics B') is None,'all surfaces released')
    finally:
        if process.poll() is None:process.kill();process.wait()
print('Physics actual X11 standalone visible fall/contact/bounce, two isolated Stage worlds, stop/return/selected close, reopen/SIGINT PASS')
