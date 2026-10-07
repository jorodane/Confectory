#!/usr/bin/env python3
"""Actual X11 reusable card/table drafts, asynchronous preview, Save/restore and Confirm."""
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

report = json.load(open(sys.argv[1], encoding='utf-8'))
display = open_display(None)
assert display, 'A live X11 DISPLAY is required; headless success is not GUI coverage.'
root = root_window(display)

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

import threading
import pathlib
logs = []
env = os.environ.copy(); env.pop('CONFECTORY_BASEUI_CLOSE_AFTER_MS', None); env.pop('CONFECTORY_BASEUI_SCRIPTED', None)
import tempfile, shutil
private_root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-authoring-gui-'))
repo=pathlib.Path(__file__).resolve().parents[2]
shutil.copytree(repo/'examples/projects/authoring',private_root/'project',ignore=shutil.ignore_patterns('.confectory','bin','obj'))
project=private_root/'project/project.cpack'
project.write_text(project.read_text().replace('../../../targets/dotnet/pack.cpack',str(repo/'targets/dotnet/pack.cpack')))
env['CONFECTORY_ELEMENT_UI']='1';env['CONFECTORY_PROJECT_A']=str(project);env['CONFECTORY_PROJECT_B']=str(project)
env['CONFECTORY_ELEMENT_AUTHORING_HOST']=str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')
env['CONFECTORY_PROJECT_EXECUTION_HOST']=str(repo/'targets/project-execution-host/bin/Release/net10.0/Confectory.ProjectExecutionHost.dll')
process = subprocess.Popen(report['run'], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
thread = threading.Thread(target=lambda: logs.extend(iter(process.stdout.readline, '')), daemon=True); thread.start()
def wait_log(text):
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        if text in ''.join(logs): return
        if process.poll() is not None: raise AssertionError('Engine exited early: ' + process.stderr.read())
        time.sleep(.02)
    raise AssertionError('Missing log ' + text + ': ' + ''.join(logs))
def click(window, x, y):
    pointer(window,4,x,y);pointer(window,5,x,y);flush(display)
def key(window, letter):
    code=keycode(display,ord(letter));pointer(window,2,detail=code);pointer(window,3,detail=code);flush(display)
def wait_author(view,state,start=0):
    deadline=time.monotonic()+120
    wanted=f'author view={view} state={state}'
    while time.monotonic()<deadline:
        found=[line for line in logs[start:] if wanted in line]
        if found:return found[-1]
        if process.poll() is not None:raise AssertionError(process.stderr.read()+''.join(logs))
        time.sleep(.02)
    raise AssertionError(wanted+': '+''.join(logs[start:]))
try:
    mapped=await_windows();a,b=mapped['Confectory BaseUI A'],mapped['Confectory BaseUI B']
    move=native('XMoveWindow',c.c_int,P,U,c.c_int,c.c_int);move(display,a,10,10);move(display,b,510,10);flush(display)
    click(a,50,685);click(b,50,685);wait_log('project action view=0 action=1 context=open');wait_log('project action view=1 action=1 context=open')
    key(a,'a');wait_author(0,'attached');key(b,'a');wait_author(1,'attached')
    click(a,50,386);wait_author(0,'edited');wait_log('element projection view=1 unit=Example.Authoring::Counter revision=1')
    assert 'count = 0' in (private_root/'project/counter.celem').read_text(),'Draft edit changed final source'
    if len(sys.argv)>2:subprocess.run(['import','-window','root',sys.argv[2]],check=True)
    key(a,'n');created=wait_author(0,'created');assert '::Created' in created
    start=len(logs);key(a,'i');wait_author(0,'edited',start)
    key(a,'e');wait_author(0,'body edited');start=len(logs);key(a,'v')
    # A real compile/run is in progress; B's independent basic control must remain responsive.
    click(b,50,125);wait_log('view 1 count=1 toggle=0');preview=wait_author(0,'preview',start);assert 'Edited authoring draft runs' in preview,preview
    assert 'Authoring baseline runs' in (private_root/'project/main.csbody').read_text()
    key(a,'d');wait_author(0,'saved');key(a,'w');wait_author(0,'restored')
    assert 'Authoring baseline runs' in (private_root/'project/main.csbody').read_text()
    start=len(logs);key(a,'f');wait_author(0,'confirmed',start)
    assert 'Edited authoring draft runs' in (private_root/'project/main.csbody').read_text()
    assert not (private_root/'project/elements').exists(),'Selective body Confirm also published creation'
    start=len(logs);key(a,'g');wait_author(0,'confirmed',start)
    assert list((private_root/'project/elements').glob('Created*.celem')),'Creation/registration not actually published'
    # B is still bound to Counter; an external final change must preserve B's new draft.
    start=len(logs);key(b,'i');wait_author(1,'edited',start)
    (private_root/'project/counter.celem').write_text('object Example.Authoring::Counter { value count = 99; }\n')
    key(b,'f');wait_author(1,'conflict',start);assert 'count = 99' in (private_root/'project/counter.celem').read_text()
    close(a);flush(display);time.sleep(.05);assert windows().get('Confectory BaseUI B')==b
    key(b,'r');mapped=await_windows();assert mapped['Confectory BaseUI B']==b;a=mapped['Confectory BaseUI A']
    # Interrupt a pending real preview: owner-scoped process cancellation must finish cleanup.
    start=len(logs);key(a,'v');time.sleep(.1);process.send_signal(signal.SIGINT);process.wait(timeout=10);thread.join(timeout=2)
    assert process.returncode==0,process.stderr.read()
    assert not any(n.startswith('Confectory BaseUI') for n in windows())
    print('PASS actual X11 shared card/table edit/create, responsive async preview, Save/restore, selective Confirm/conflict, View reopen and pending-job interruption')
    print(''.join(logs))
except Exception:
    print(''.join(logs),file=sys.stderr);raise
finally:
    if process.poll() is None:process.send_signal(signal.SIGINT);process.wait(timeout=10)
    close_display(display);shutil.rmtree(private_root)
