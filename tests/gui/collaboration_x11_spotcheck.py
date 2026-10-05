#!/usr/bin/env python3
"""Actual X11 ProjectManager controls and independent execution/lifetime check."""
import ctypes as c
import json
import os
import signal
import subprocess
import sys
import time

lib = c.CDLL('libX11.so.6')
P, U, L = c.c_void_p, c.c_ulong, c.c_long

def native(name, result, *args):
    f = getattr(lib, name); f.restype = result; f.argtypes = list(args); return f

open_display = native('XOpenDisplay', P, c.c_char_p)
root_window = native('XDefaultRootWindow', U, P)
query = native('XQueryTree', c.c_int, P, U, c.POINTER(U), c.POINTER(U), c.POINTER(P), c.POINTER(c.c_uint))
fetch_name = native('XFetchName', c.c_int, P, U, c.POINTER(P))
free = native('XFree', c.c_int, P)
flush = native('XFlush', c.c_int, P)
send = native('XSendEvent', c.c_int, P, U, c.c_int, L, P)
atom = native('XInternAtom', U, P, c.c_char_p, c.c_int)
resize = native('XResizeWindow', c.c_int, P, U, c.c_uint, c.c_uint)
keycode = native('XKeysymToKeycode', c.c_ubyte, P, U)
close_display = native('XCloseDisplay', c.c_int, P)

class PointerEvent(c.Structure):
    _fields_ = [('type', c.c_int), ('serial', U), ('send', c.c_int), ('display', P), ('window', U), ('root', U), ('subwindow', U), ('time', U), ('x', c.c_int), ('y', c.c_int), ('xr', c.c_int), ('yr', c.c_int), ('state', c.c_uint), ('detail', c.c_uint), ('same', c.c_int)]

import pathlib, tempfile, shutil, threading
report=json.load(open(sys.argv[1],encoding='utf-8'));display=open_display(None);assert display;root=root_window(display)
def windows():
    r, parent, children, count = U(), U(), P(), c.c_uint()
    query(display, root, c.byref(r), c.byref(parent), c.byref(children), c.byref(count))
    result = {}
    try:
        for window in c.cast(children, c.POINTER(U))[:count.value]:
            name = P(); fetch_name(display, window, c.byref(name))
            if name:
                try: result[c.string_at(name).decode()] = window
                finally: free(name)
    finally:
        if children: free(children)
    return result

def await_windows():
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        result = windows()
        if all(n in result for n in ('Confectory BaseUI A', 'Confectory BaseUI B')): return result
        time.sleep(.01)
    raise AssertionError('Both windows were not mapped')

def pointer(window, kind, x=0, y=0, detail=1, timestamp=10):
    event = PointerEvent(kind, 0, 1, display, window, root, 0, timestamp, x, y, x, y, 0, detail, 1)
    buffer = c.create_string_buffer(192); c.memmove(buffer, c.byref(event), c.sizeof(event))
    assert send(display, window, 0, 0, buffer)

def close(window):
    buffer = c.create_string_buffer(192)
    c.c_int.from_buffer(buffer, 0).value = 33
    U.from_buffer(buffer, 32).value = window
    U.from_buffer(buffer, 40).value = atom(display, b'WM_PROTOCOLS', 0)
    c.c_int.from_buffer(buffer, 48).value = 32
    U.from_buffer(buffer, 56).value = atom(display, b'WM_DELETE_WINDOW', 0)
    assert send(display, window, 0, 0, buffer)

private_root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-collaboration-ui-'));repo=pathlib.Path(__file__).resolve().parents[2]
shutil.copytree(repo/'examples/projects/authoring',private_root/'project',ignore=shutil.ignore_patterns('.confectory','bin','obj'));project=private_root/'project/project.cpack';project.write_text(project.read_text().replace('../../../targets/dotnet/pack.cpack',str(repo/'targets/dotnet/pack.cpack')))
env=os.environ.copy();env['CONFECTORY_COLLAB_PROJECT']=str(project);env['CONFECTORY_ELEMENT_AUTHORING_HOST']=str(repo/'targets/element-authoring/bin/Release/net8.0/Confectory.ElementAuthoring.dll');logs=[]
process=subprocess.Popen(report['run'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);thread=threading.Thread(target=lambda:logs.extend(iter(process.stdout.readline,'')),daemon=True);thread.start()
def await_named(name):
 deadline=time.monotonic()+30
 while time.monotonic()<deadline:
  result=windows()
  if name in result:return result[name]
  if process.poll() is not None:raise AssertionError(process.stderr.read())
  time.sleep(.02)
 raise AssertionError('Missing '+name)
def wait_log(text,start=0):
 deadline=time.monotonic()+120
 while time.monotonic()<deadline:
  if any(text in line for line in logs[start:]):return
  if process.poll() is not None:raise AssertionError(process.stderr.read()+''.join(logs))
  time.sleep(.02)
 raise AssertionError('Missing '+text+''.join(logs[start:]))
def key(window,letter):
 code=keycode(display,ord(letter));pointer(window,2,detail=code,timestamp=int(time.monotonic()*1000));pointer(window,3,detail=code,timestamp=int(time.monotonic()*1000));flush(display)
try:
 a=await_named('Confectory Collaboration Alice');b=await_named('Confectory Collaboration Bob');key(a,'i');wait_log('collab draft view=0 count=1');key(b,'i');wait_log('collab draft view=1 count=1');key(b,'i');wait_log('collab draft view=1 count=2');wait_log('collab notice view=0 kind=conflict');wait_log('collab notice view=1 kind=conflict');assert 'count = 0' in (private_root/'project/counter.celem').read_text()
 key(a,'d');wait_log('collab saved view=0');key(a,'f');key(b,'i');wait_log('collab draft view=1 count=3');wait_log('collab confirm view=0 state=confirmed');assert 'count = 1' in (private_root/'project/counter.celem').read_text();wait_log('collab notice view=1 kind=baseline-changed');key(b,'f');wait_log('collab confirm view=1 state=conflict');key(b,'d');wait_log('collab saved view=1');key(b,'b');wait_log('collab disconnected view=1');key(b,'r');wait_log('collab reconnected view=1');assert 'count = 1' in (private_root/'project/counter.celem').read_text();saves=list((private_root/'project/.confectory/edit-workspaces').glob('*/draft.json'));assert any('count = 3' in p.read_text() for p in saves)
 if len(sys.argv)>2:subprocess.run(['import','-window','root',sys.argv[2]],check=True)
 # Cancel an owned pending real validation; preserve saved local intent and peer source.
 start=len(logs);key(a,'i');wait_log('collab draft view=0 count=2',start);key(a,'f');time.sleep(.1);process.send_signal(signal.SIGINT);process.wait(timeout=15);thread.join(timeout=2);assert process.returncode==0,process.stderr.read();assert 'count = 1' in (private_root/'project/counter.celem').read_text();assert any('count = 2' in p.read_text() for p in (private_root/'project/.confectory/edit-workspaces').glob('*/draft.json'));assert not any(name.startswith('Confectory Collaboration') for name in windows());assert 'collab owner cleanup complete' in ''.join(logs)
 print('PASS actual X11 two-client private drafts, early peer conflict, responsive peer while Confirm, shared confirmed source, stale draft retention, disconnect/reconnect, pending-validation interruption and owner cleanup');print(''.join(logs))
except Exception:
 print(''.join(logs),file=sys.stderr);raise
finally:
 if process.poll() is None:process.send_signal(signal.SIGINT);process.wait(timeout=15)
 close_display(display);shutil.rmtree(private_root)
