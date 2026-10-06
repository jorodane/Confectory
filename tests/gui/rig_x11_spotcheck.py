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

import threading,shutil
repo=os.path.abspath(os.path.join(os.path.dirname(__file__),'../..'))
# Run reports are explicit arguments; authoring modifies only this private copy.
asset='/tmp/checkpoint12 GUI owned asset'
shutil.rmtree(asset,ignore_errors=True)
shutil.copytree(os.path.join(repo,'examples/rig-lab/asset-project'),asset,ignore=shutil.ignore_patterns('.confectory'))
p=os.path.join(asset,'project.cpack');text=open(p).read();open(p,'w').write(text.replace('../../../',repo+'/'))
def start(path,workbench=False):
    env=os.environ.copy();env.update(CONFECTORY_RIG_MODE='ui',CONFECTORY_RIG_TRACE='1',CONFECTORY_RIG_AUTHOR_PROJECT=p)
    process=subprocess.Popen(json.load(open(path))['run'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);lines=[];samples={'preview':[],0:[],1:[]}
    def reader():
        for line in process.stdout:
            lines.append(line.rstrip())
            if line.startswith('RIG_UI snapshot '):
                scope,payload=line[len('RIG_UI snapshot '):].split(' ',1);samples['preview' if scope=='preview' else int(scope)].append(json.loads(payload))
    processes.append(process);thread=threading.Thread(target=reader,daemon=True);thread.start();return process,thread,lines,samples

def until(test,reason,seconds=15):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        if test():return
        time.sleep(.02)
    raise AssertionError(reason)
def finish(process,thread,lines,interrupt=False):
    if interrupt:process.send_signal(signal.SIGINT)
    code=process.wait(timeout=60);thread.join(5);stderr=process.stderr.read();assert code==0,(code,stderr,lines[-4:]);assert any('cleanup complete' in x for x in lines)
def snap(window,path):
    subprocess.run(['import','-display',os.environ['DISPLAY'],'-window',str(window),path],check=True)
def layer_pixels(window,color):
    bitmap=image(display,window,0,0,480,360,U(-1).value,2);assert bitmap
    try:return sum(pixel(bitmap,x,y)&0xffffff==color for y in range(60,300,2) for x in range(40,440,2))
    finally:destroy(bitmap)

import atexit
processes=[]
def cleanup():
    for process in processes:
        if process.poll() is None:
            process.send_signal(signal.SIGINT)
            try:process.wait(timeout=30)
            except subprocess.TimeoutExpired:process.kill()
atexit.register(cleanup)
proc,thread,lines,samples=start(sys.argv[1]);w=await_window(b'Confectory Rig preview')
until(lambda:len(samples['preview'])>12,'preview did not render');first=samples['preview'][0];last=samples['preview'][-1];assert first['pose']!=last['pose'];assert layer_pixels(w,0x3baaf5)>0 and layer_pixels(w,0xf1c232)>0
press(w,' ');time.sleep(.12);paused=samples['preview'][-1]['pose']['time'];time.sleep(.15);assert samples['preview'][-1]['pose']['time']==paused
press(w,0xff53);until(lambda:samples['preview'][-1]['pose']['time']!=paused,'scrub did not update');assert find(b'Confectory Rig preview')==w
resize=native('XResizeWindow',c.c_int,P,U,c.c_uint,c.c_uint);resize(display,w,500,380);flush(display);time.sleep(.15);assert find(b'Confectory Rig preview')==w;bitmap=image(display,w,0,0,500,380,U(-1).value,2);assert bitmap
try:assert pixel(bitmap,10,365)&0xffffff==0x293847,'footer did not follow actual client resize'
finally:destroy(bitmap)
snap(w,'/tmp/checkpoint12-rig-preview.png');close(w);finish(proc,thread,lines);assert not find(b'Confectory Rig preview')
print('Standalone real X11 motion/pause/scrub/resize/persistent window/pixels/close PASS',flush=True)

proc,thread,lines,samples=start(sys.argv[2],True);a=await_window(b'Confectory Rig A');b=await_window(b'Confectory Rig B')
until(lambda:len(samples[0])>8 and len(samples[1])>8,'comparison frames absent');assert samples[0][-1]['playing'] and not samples[1][-1]['playing'];assert samples[0][-1]['snapshot']['plane']=='front' and samples[1][-1]['snapshot']['plane']=='side'
press(a,' ');until(lambda:not samples[0][-1]['playing'],'pause input absent');time.sleep(.12);frozen=samples[0][-1]['snapshot']['pose']['time'];press(b,0xff53);until(lambda:samples[1][-1]['snapshot']['pose']['time']>1,'comparison scrub absent');assert samples[0][-1]['snapshot']['pose']['time']==frozen
old=samples[0][-1]['snapshot']['documentHash']
for key in 'HPD':press(a,key);time.sleep(.1)
until(lambda:samples[0][-1]['snapshot']['documentHash']!=old,'authored pose did not update');assert find(b'Confectory Rig A')==a and find(b'Confectory Rig B')==b
press(a,'L');until(lambda:all(x['visible']==False for x in samples[0][-1]['snapshot']['layers'] if x['id']=='tool'),'visibility draft absent');time.sleep(.08);assert layer_pixels(a,0xf1c232)==0
press(a,'L');until(lambda:any(x['id']=='tool' and x['visible'] for x in samples[0][-1]['snapshot']['layers']),'layer restoration absent');press(a,'O');until(lambda:any(x['id']=='tool' and x['order']==0 for x in samples[0][-1]['snapshot']['layers']),'layer order absent');expected=samples[0][-1]['snapshot']['documentHash'];original=open(os.path.join(asset,'Rig.celem')).read()
press(a,'S');until(lambda:samples[0][-1]['status']=='draft saved','save absent');assert open(os.path.join(asset,'Rig.celem')).read()==original
press(a,'R');until(lambda:samples[0][-1]['status']=='saved draft reloaded','reload absent');assert samples[0][-1]['snapshot']['documentHash']==expected and find(b'Confectory Rig B')==b
snap(a,'/tmp/checkpoint12-rig-author-front.png');snap(b,'/tmp/checkpoint12-rig-author-side.png')
before=len(samples[0]);press(a,'C');until(lambda:samples[0][-1]['status']=='confirming; draft edits paused','background Confirm status absent');until(lambda:len(samples[0])>before+3,'rendering stopped during Confirm');until(lambda:any('RIG_UI confirm confirmed' in x for x in lines),'actual Confirm absent',120);assert open(os.path.join(asset,'Rig.celem')).read()!=original
close(a);until(lambda:not find(b'Confectory Rig A'),'selected view did not close');assert find(b'Confectory Rig B')==b;before=len(samples[1]);until(lambda:len(samples[1])>before+4,'surviving view stopped')
finish(proc,thread,lines,True);assert not find(b'Confectory Rig B')
proc,thread,lines,samples=start(sys.argv[2],True);await_window(b'Confectory Rig A');await_window(b'Confectory Rig B');until(lambda:len(samples[1])>2,'reopen frames absent');a=await_window(b'Confectory Rig A');press(a,'P');time.sleep(.08);press(a,'C');until(lambda:samples[0][-1]['status']=='confirming; draft edits paused','interrupt test did not start owned Confirm');finish(proc,thread,lines,True)
print('Two real X11 Views independent time/projection; H/P/D/L/O edits, persistent Save/reload, actual Confirm, selected close, reopen/SIGINT cleanup PASS',flush=True)
