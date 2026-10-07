#!/usr/bin/env python3
"""Actual local tool UI and authoring: semantic/capture scope, seal/drag/discard, shared drafts, new resource/recipe, Confirm, read-only projection, comparison cleanup."""
import ctypes as c
import json
import os
import subprocess
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

def find(title):
    r,parent,children,count=U(),U(),P(),c.c_uint();query(display,root,c.byref(r),c.byref(parent),c.byref(children),c.byref(count))
    try:
        for window in c.cast(children,c.POINTER(U))[:count.value]:
            name=P();fetch(display,window,c.byref(name))
            if name:
                try:
                    if c.string_at(name)==title.encode():return window
                finally:free(name)
    finally:
        if children:free(children)

def await_window(title):
    end=time.monotonic()+10
    while time.monotonic()<end:
        window=find(title)
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

import shutil
import tempfile
import threading
import signal
repo=os.path.realpath(os.path.join(os.path.dirname(__file__),'../..'))
source=tempfile.mkdtemp(prefix='confectory-augment-gate-')
shutil.copytree(os.path.join(repo,'examples/projects/harvest-game'),source,dirs_exist_ok=True,ignore=shutil.ignore_patterns('.confectory'))
project=os.path.join(source,'project.cpack')
text=open(project,encoding='utf-8').read().replace('../../../packs/',repo+'/packs/').replace('../../../targets/',repo+'/targets/')
open(project,'w',encoding='utf-8').write(text)
env=os.environ.copy();env['CONFECTORY_AUGMENT_PROJECT']=project;env['CONFECTORY_PROJECT_EXECUTION_HOST']=os.path.join(repo,'targets/project-execution-host/bin/Release/net10.0/Confectory.ProjectExecutionHost.dll');env['CONFECTORY_AUGMENT_MODE']='ui';env['CONFECTORY_AUGMENT_DIR']=tempfile.mkdtemp(prefix='augment-history-')
process=subprocess.Popen(report['run'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
lines=[];errors=[]
def collect(stream,target):
    for line in stream:target.append(line.rstrip())
threads=[threading.Thread(target=collect,args=(process.stdout,lines),daemon=True),threading.Thread(target=collect,args=(process.stderr,errors),daemon=True)]
for thread in threads:thread.start()
def await_log(text,seconds=15,start=0):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        for line in lines[start:]:
            if text in line:return line
        assert process.poll() is None,'Workbench exited: '+ '\n'.join(lines+errors)
        time.sleep(.01)
    raise AssertionError('No log '+text+'\n'+'\n'.join(lines+errors))
def pointer(window,kind,x,y,state=0,detail=1):
    event=Event(kind,0,1,display,window,root,0,100,x,y,x,y,state,detail,1)
    buffer=c.create_string_buffer(192);c.memmove(buffer,c.byref(event),c.sizeof(event));assert send(display,window,0,0,buffer);flush(display)
def click(window,x,y):pointer(window,4,x,y);pointer(window,5,x,y)
def ctrl_y(window):
    for kind in (2,3):pointer(window,kind,0,0,4,keycode(display,ord('y')))
try:
    cards=await_window('Confectory Augment Cards');history=await_window('Confectory Augment History');await_log('ready')
    for attempt in range(2):
        start=len(lines);click(cards,30,300);await_log('reroll ordinary',start=start)
        start=len(lines);click(cards,30,70);await_log('selected; source unchanged',start=start)
        assert 'value yield = 2;' in open(os.path.join(source,'PowderPlant.celem')).read()
        start=len(lines);click(cards,30,345);await_log('selection cancelled',start=start)
    click(cards,30,255)
    for character in 'modest harvest':press(cards,character)
    start=len(lines);click(cards,160,300);await_log('reroll directed: modest harvest',start=start)
    start=len(lines);click(cards,440,345);await_log('ExactlyYogi',start=start)
    start=len(lines);click(cards,280,300);await_log('skipped; history retained',start=start)
    start=len(lines);click(cards,420,300);await_log('custom selected',start=start)
    start=len(lines);click(cards,30,345);await_log('selection cancelled',start=start)
    start=len(lines);click(cards,30,300);await_log('reroll ordinary',start=start)
    start=len(lines);click(cards,30,125);await_log('selected; source unchanged',start=start)
    start=len(lines);click(cards,130,345);await_log('draft staged',start=start)
    assert 'value yield = 2;' in open(os.path.join(source,'PowderPlant.celem')).read()
    start=len(lines);click(cards,230,345);await_log('reviewed;',start=start)
    start=len(lines);click(cards,330,345);await_log('Confirm confirmed',seconds=180,start=start)
    start=len(lines);click(cards,40,390);await_log('domain verified',start=start)
    data=json.load(open(os.path.join(env['CONFECTORY_AUGMENT_DIR'],'augment.json')));assert len(data['selections'])==4 and len(data['batches'])==4,data
    assert colored(cards,0x684040),'confirmed old proposals should visibly be stale'
    start=len(lines);click(cards,30,300);await_log('reroll ordinary',start=start)
    path=os.path.join(source,'PowderPlant.celem');saved=open(path).read();os.remove(path)
    try:
        wait_color(cards,0x684040,lambda points:True,15)
        start=len(lines);click(cards,30,70);await_log('rejected: stale/deleted proposal target',start=start)
    finally:open(path,'w').write(saved)
    open(path,'w').write(saved.replace('value yield = 3;','value yield = 4;'))
    try:
        wait_color(cards,0x684040,lambda points:True,15)
        start=len(lines);click(cards,30,70);await_log('rejected: stale/deleted proposal target',start=start)
    finally:open(path,'w').write(saved)
    close(history);assert process.wait(timeout=15)==0,errors
    for thread in threads:thread.join(2)
    assert 'Augment actual UI owner cleanup complete' in lines,lines
    before=json.load(open(os.path.join(env['CONFECTORY_AUGMENT_DIR'],'augment.json')))
    process=subprocess.Popen(report['run'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    lines=[];errors=[];threads=[threading.Thread(target=collect,args=(process.stdout,lines),daemon=True),threading.Thread(target=collect,args=(process.stderr,errors),daemon=True)]
    for thread in threads:thread.start()
    cards=await_window('Confectory Augment Cards');await_window('Confectory Augment History');await_log('ready')
    after=json.load(open(os.path.join(env['CONFECTORY_AUGMENT_DIR'],'augment.json')));assert before==after,'restart rewrote or replayed history'
    process.send_signal(signal.SIGINT);assert process.wait(timeout=15)==0,errors
    for thread in threads:thread.join(2)
    assert 'Augment actual UI owner cleanup complete' in lines,lines
    process=subprocess.Popen(report['run'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    lines=[];errors=[];threads=[threading.Thread(target=collect,args=(process.stdout,lines),daemon=True),threading.Thread(target=collect,args=(process.stderr,errors),daemon=True)]
    for thread in threads:thread.start()
    cards=await_window('Confectory Augment Cards');await_window('Confectory Augment History');await_log('ready')
    click(cards,30,255)
    for character in 'slow':press(cards,character)
    click(cards,160,300)
    end=time.monotonic()+15
    while time.monotonic()<end:
        pending=json.load(open(os.path.join(env['CONFECTORY_AUGMENT_DIR'],'augment.json')))
        if pending['batches'][-1]['state']=='generating':break
        time.sleep(.01)
    assert pending['batches'][-1]['state']=='generating','slow request was not reserved'
    assert colored(cards,0x283645),'UI surface absent during slow generation'
    subprocess.run(['import','-window','root','/tmp/augment-final-visual.png'],check=True)
    process.send_signal(signal.SIGINT);assert process.wait(timeout=15)==0,errors
    for thread in threads:thread.join(2)
    assert 'Augment actual UI owner cleanup complete' in lines,lines
    process=subprocess.Popen(report['run'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    lines=[];errors=[];threads=[threading.Thread(target=collect,args=(process.stdout,lines),daemon=True),threading.Thread(target=collect,args=(process.stderr,errors),daemon=True)]
    for thread in threads:thread.start()
    cards=await_window('Confectory Augment Cards');await_window('Confectory Augment History');await_log('ready')
    recovered=json.load(open(os.path.join(env['CONFECTORY_AUGMENT_DIR'],'augment.json')))
    assert recovered['batches'][-1]['state']=='interrupted','interrupted request replayed or lost'
    close(cards);assert process.wait(timeout=15)==0,errors
    for thread in threads:thread.join(2)
    assert 'Augment actual UI owner cleanup complete' in lines,lines
    print('Actual Linux Augment three-card repeated reroll/selection-cancel/direction/custom/skip/Exactly/stage/review/Confirm/domain/restart/SIGINT PASS')
finally:
    if process.poll() is None:process.kill();process.wait()
    print('\n'.join(lines));print('\n'.join(errors))
    shutil.rmtree(source,ignore_errors=True)
