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
source=tempfile.mkdtemp(prefix='confectory-workbench-gate-')
shutil.copytree(os.path.join(repo,'examples/projects/harvest-game'),source,dirs_exist_ok=True,ignore=shutil.ignore_patterns('.confectory'))
project=os.path.join(source,'project.cpack')
text=open(project,encoding='utf-8').read().replace('../../../packs/',repo+'/packs/').replace('../../../targets/',repo+'/targets/')
open(project,'w',encoding='utf-8').write(text)
env=os.environ.copy();env['CONFECTORY_WORKBENCH_PROJECT']=project;env['CONFECTORY_PROJECT_EXECUTION_HOST']=os.path.join(repo,'targets/project-execution-host/bin/Release/net10.0/Confectory.ProjectExecutionHost.dll');env.pop('CONFECTORY_WORKBENCH_CLOSE_MS',None)
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
    table=await_window('Confectory Authoring Table');box=await_window('Confectory YogiBox');projection=await_window('Confectory Algorithm Projection')
    await_log('ready:')
    click(table,40,200);await_log('yield draft edited')
    assert 'value yield = 2;' in open(os.path.join(source,'PowderPlant.celem')).read(),'draft leaked into confirmed source'
    click(table,360,300);await_log('table closed/reopened')
    ctrl_y(table);await_log('ExactlyYogi selected semantic ID')
    click(box,220,200);await_log('only selected owned table region captured')
    click(box,430,65);await_log('selected item removed; draft unsealed')
    click(box,370,200);await_log('seal toggled')
    pointer(box,4,100,65);pointer(box,6,150,305);pointer(box,5,150,305)
    await_log('sealed package dragged to local inspector; immutable receipt')
    click(box,100,250);await_log('draft discarded; delivered attachments retained')
    click(box,370,200);await_log('operation rejected:')
    start=len(lines);ctrl_y(table);await_log('ExactlyYogi selected semantic ID',start=start)
    click(table,340,200);await_log('new resource draft; reusable plant and recipe')
    click(table,370,250);await_log('projection updated: syntax explanation only')
    click(table,100,300);await_log('functional source edit; one completed human batch projected locally')
    click(table,70,250);responsive=len(lines);click(box,370,200);await_log('seal toggled',seconds=2,start=responsive);await_log('Confirm: confirmed',seconds=150)
    assert 'SparkResource' in open(project).read(),'new resource manifest was not confirmed'
    plant=open(os.path.join(source,'PowderPlant.celem')).read();recipe=open(os.path.join(source,'BombRecipe.celem')).read()
    assert 'SparkResource' in plant and 'yield = 3' in plant and 'SparkResource' in recipe
    click(table,210,250);await_log('two isolated runtime handles')
    # Handles launch asynchronously; names contain a unique suffix.
    end=time.monotonic()+150
    while time.monotonic()<end:
        r,parent,children,count=U(),U(),P(),c.c_uint();query(display,root,c.byref(r),c.byref(parent),c.byref(children),c.byref(count));names=[]
        try:
            for window in c.cast(children,c.POINTER(U))[:count.value]:
                name=P();fetch(display,window,c.byref(name))
                if name:
                    try:names.append(c.string_at(name).decode())
                    finally:free(name)
        finally:
            if children:free(children)
        games=[name for name in names if name.startswith('Confectory Harvest A-') or name.startswith('Confectory Harvest B-')]
        if len(games)==2:break
        time.sleep(.02)
    assert len(games)==2,'Both actual comparison surfaces were not mapped'
    a=find(next(n for n in games if n.startswith('Confectory Harvest A-')));b=find(next(n for n in games if n.startswith('Confectory Harvest B-')))
    press(a,'h');time.sleep(.04);press(a,'c');time.sleep(.04);press(a,'t')
    wait_color(a,0xF4D12D,lambda p:110<sum(x for x,y in p)/len(p)<285,.7)
    assert not colored(b,0xF4D12D),'Unshared input changed the other runtime model'
    wait_color(a,0xEB7130,lambda p:len(p)>10,1.5)
    close(table);assert process.wait(timeout=15)==0,'\n'.join(errors)
    for thread in threads:thread.join(timeout=2)
    assert any('workbench owner cleanup complete' in line for line in lines)
    assert not find(games[0]) and not find(games[1]),'Comparison children survived owner close'
    print('PASS actual Linux workbench: Ctrl+Y, scoped LookAtYogi, remove/seal/drag/discard, immutable receipt, shared table reopen, new resource/recipe Confirm, source-batched read-only projection, two isolated games, visible motion/effect, owner cleanup')
    lines.clear();errors.clear()
    process=subprocess.Popen(report['run'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    threads=[threading.Thread(target=collect,args=(process.stdout,lines),daemon=True),threading.Thread(target=collect,args=(process.stderr,errors),daemon=True)]
    for thread in threads:thread.start()
    table=await_window('Confectory Authoring Table');await_window('Confectory YogiBox');await_window('Confectory Algorithm Projection');await_log('ready:')
    click(table,370,250);time.sleep(.01);process.send_signal(signal.SIGINT)
    assert process.wait(timeout=15)==0,'\n'.join(errors)
    for thread in threads:thread.join(timeout=2)
    assert any('workbench owner cleanup complete' in line for line in lines),'Owned projection job did not join during interruption'
    assert not find('Confectory Authoring Table') and not find('Confectory YogiBox') and not find('Confectory Algorithm Projection')
    print('PASS actual Linux workbench reopen/SIGINT: projection-job cancellation, joined ownership, closed surfaces')
finally:
    if process.poll() is None:process.kill();process.wait(timeout=5)
    for line in lines:print('workbench:',line)
    for line in errors:print('stderr:',line)
    shutil.rmtree(source,ignore_errors=True)
