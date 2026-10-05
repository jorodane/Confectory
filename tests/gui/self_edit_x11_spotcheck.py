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

import pathlib, threading
report=json.load(open(sys.argv[1],encoding='utf-8'));self_root=pathlib.Path(sys.argv[2]);project=self_root/'engine/project.cpack'
display=open_display(None);assert display;root=root_window(display)
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
        if all(n in result for n in ('Confectory editor A A', 'Confectory editor A B')): return result
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


logs=[];env=os.environ.copy();env.update(CONFECTORY_WINDOW_PREFIX='Confectory editor A',CONFECTORY_ELEMENT_UI='1',CONFECTORY_SELF_PROJECT=str(project),CONFECTORY_SELECTED_ELEMENT='Confectory.ElementView::LabelsBody/body:common',CONFECTORY_PRIME_PROJECT=str(self_root/'prime-project/project.cpack'),CONFECTORY_RENDER_TRACE='1',CONFECTORY_AUTHORING_TIMEOUT_MS='900000');env.pop('CONFECTORY_BASEUI_CLOSE_AFTER_MS',None);env.pop('CONFECTORY_BASEUI_SCRIPTED',None)
process=subprocess.Popen(report['run'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
thread=threading.Thread(target=lambda:logs.extend(iter(process.stdout.readline,'')),daemon=True);thread.start()
def wait_log(text,start=0):
 deadline=time.monotonic()+900
 while time.monotonic()<deadline:
  if any(text in line for line in logs[start:]):return
  if process.poll() is not None:raise AssertionError(process.stderr.read()+''.join(logs))
  time.sleep(.02)
 raise AssertionError('Missing '+text+': '+''.join(logs[start:]))
def await_named(name):
 deadline=time.monotonic()+900
 while time.monotonic()<deadline:
  result=windows()
  if name in result:return result[name]
  if process.poll() is not None:raise AssertionError(process.stderr.read())
  time.sleep(.02)
 raise AssertionError('No window '+name+''.join(logs))
keysym_at=native('XKeycodeToKeysym',U,P,c.c_ubyte,c.c_int)
clock=20
def key(window,symbol,state=0):
 global clock
 clock+=1;code=keycode(display,symbol);assert code,hex(symbol)
 event=PointerEvent(2,0,1,display,window,root,0,clock,0,0,0,0,state,code,1);buffer=c.create_string_buffer(192);c.memmove(buffer,c.byref(event),c.sizeof(event));assert send(display,window,0,0,buffer)
 event.type=3;c.memmove(buffer,c.byref(event),c.sizeof(event));assert send(display,window,0,0,buffer);flush(display)
def type_text(window,text):
 for char in text:
  if char=='\n':key(window,0xFF0D);continue
  symbol=ord(char);code=keycode(display,symbol);assert code,repr(char)
  state=0 if keysym_at(display,code,0)==symbol else 1
  assert keysym_at(display,code,state)==symbol,(char,code,state)
  key(window,symbol,state)
def action(window,letter,state):
 start=len(logs);key(window,ord(letter));wait_log('author view=0 state='+state,start)
try:
 a=await_named('Confectory editor A A');b=await_named('Confectory editor A B');action(a,'h','attached');wait_log('render Confectory editor A view=0 label=Card element')
 lock=json.loads((self_root/'engine/.pack-lock.json').read_text());pin=lock['pins']['Confectory.ElementView'];body=self_root/'engine'/pin['path'];body=body.parent/'Labels.csbody';original=body.read_text();user_text=original.replace('Card element','User authored card revision');assert user_text!=original
 key(a,0xFFBF);type_text(a,user_text);key(a,0xFFC0);wait_log('author view=0 state=draft-applied');assert body.read_text()==original
 action(a,'d','saved');action(a,'w','restored');assert body.read_text()==original;action(a,'f','confirmed');assert body.read_text()==user_text
 # A retains its loaded implementation while the source is independently changed.
 start=len(logs);pointer(a,4,50,125);pointer(a,5,50,125);flush(display);wait_log('render Confectory editor A view=0 label=Card element',start)
 key(a,ord('y'));prime=await_named('Confectory A-prime A');start=len(logs);key(prime,ord('o'));wait_log('project action view=0 action=1 context=open',start);start=len(logs);key(prime,ord('a'));wait_log('state=attached',start)
 # Child host drains stdout by contract; visual evidence is checked from actual pixels and distinct native windows.
 assert await_named('Confectory A-prime B')!=b
 start=len(logs);key(prime,ord('h'));wait_log('state=attached unit=Confectory.Engine::Main',start);wait_log('render Confectory A-prime view=0 label=User authored card revision',start)
 if len(sys.argv)>3:subprocess.run(['import','-window','root',sys.argv[3]],check=True)
 apps=[]
 for item in pathlib.Path('/proc').iterdir():
  if not item.name.isdigit():continue
  try:
   args=(item/'cmdline').read_bytes().decode(errors='replace').split('\0')
   apps.extend(arg for arg in args if str(self_root/'engine/.confectory/outputs/linux') in arg and arg.endswith('Confectory.App.dll'))
  except (FileNotFoundError,PermissionError,ProcessLookupError):pass
 assert len(set(apps))>=2,apps
 old_artifact=str(pathlib.Path(report['run'][0]).parent/'Confectory.App.dll');assert old_artifact in apps and pathlib.Path(old_artifact).exists(),'Loaded A artifact changed or disappeared'
 artifacts_before={str(path) for path in (self_root/'engine/.confectory/outputs/linux').glob('*/Confectory.App.dll')}
 print('Distinct loaded editor artifacts: '+json.dumps(sorted(set(apps))))
 # A failed arbitrary draft stays recoverable and never rewrites confirmed source.
 key(a,0xFFBF);type_text(a,'this is invalid C# source;');key(a,0xFFC0);wait_log('author view=0 state=draft-applied',start);action(a,'d','saved');action(a,'v','invalid');assert body.read_text()==user_text;assert {str(path) for path in (self_root/'engine/.confectory/outputs/linux').glob('*/Confectory.App.dll')}==artifacts_before
 key(a,0xFFBF);type_text(a,'retained user buffer');close(a);flush(display);time.sleep(.1);assert windows().get('Confectory editor A B')==b;key(b,ord('r'));a=await_named('Confectory editor A A');assert windows().get('Confectory A-prime A')==prime
 start=len(logs);key(a,0xFFC0);wait_log('author view=0 state=draft-applied',start);action(a,'d','saved');saved=list((self_root/'engine/.confectory/edit-workspaces').glob('*/draft.json'));assert any('retained user buffer' in path.read_text() for path in saved),'Unapplied buffer did not survive View close/reopen'
 process.send_signal(signal.SIGINT);process.wait(timeout=15);thread.join(timeout=2);assert process.returncode==0,process.stderr.read();assert not any(n.startswith('Confectory A-prime') or n.startswith('Confectory editor A') for n in windows())
 print('PASS actual X11 arbitrary source input, own pinned ElementView Save/restore/Confirm, live A versus independent A-prime, failed draft/source retention, close/reopen and child cleanup');print(''.join(logs))
except Exception:
 print('Failure windows: '+str(windows()),file=sys.stderr);print(''.join(logs),file=sys.stderr);raise
finally:
 if process.poll() is None:process.send_signal(signal.SIGINT);process.wait(timeout=15)
 close_display(display)
