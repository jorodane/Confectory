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
process = subprocess.Popen(report['run'], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
thread = threading.Thread(target=lambda: logs.extend(iter(process.stdout.readline, '')), daemon=True); thread.start()
def wait_log(text):
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        if text in ''.join(logs): return
        if process.poll() is not None: raise AssertionError('Engine exited early: ' + process.stderr.read())
        time.sleep(.02)
    raise AssertionError('Missing log ' + text + ': ' + ''.join(logs))
def click(window, x):
    pointer(window, 4, x, 345); pointer(window, 5, x, 345); flush(display)
try:
    mapped=await_windows(); a,b=mapped['Confectory BaseUI A'],mapped['Confectory BaseUI B']
    click(a, 50); click(b, 50)
    wait_log('project action view=0 action=1 context=open execution=none'); wait_log('project action view=1 action=1 context=open execution=none')
    click(a, 160); click(b, 160)
    wait_log('execution view=0 state=running'); wait_log('execution view=1 state=running')
    owned_workers=[]
    for entry in pathlib.Path('/proc').iterdir():
        if not entry.name.isdigit(): continue
        try:
            fields=(entry/'stat').read_text().split(') ',1)[1].split()
            if int(fields[1])==process.pid and 'Confectory.ProjectExecutionHost.dll' in (entry/'cmdline').read_bytes().decode(errors='replace'): owned_workers.append(entry)
        except (FileNotFoundError,ProcessLookupError,PermissionError): pass
    assert len(owned_workers)==2, 'Expected two owned strategy workers'
    if len(sys.argv)>2: subprocess.run(['import','-window','root',sys.argv[2]],check=True)
    click(a, 390); wait_log('project action view=0 action=4 context=closed execution=running')
    close(a); flush(display); time.sleep(.1)
    assert windows().get('Confectory BaseUI B') == b
    r=keycode(display, ord('r')); pointer(b,2,detail=r); pointer(b,3,detail=r); flush(display)
    mapped=await_windows(); a=mapped['Confectory BaseUI A']; assert mapped['Confectory BaseUI B']==b
    click(a,50); wait_log('project action view=0 action=1 context=open execution=running')
    click(a,280); wait_log('execution view=0 state=stopped')
    click(b,390); wait_log('project action view=1 action=4 context=closed execution=running')
    click(b,280); wait_log('execution view=1 state=stopped')
    close(a); close(b); flush(display); process.wait(timeout=10);thread.join(timeout=2)
    assert process.returncode==0,process.stderr.read()
    assert not any(entry.exists() for entry in owned_workers), 'Owned worker survived caller cleanup'
    assert not any(n.startswith('Confectory BaseUI') for n in windows())
    print('PASS actual X11 A/B Open/Start/Observe/Stop, context close, View close/reopen, independent native windows and Owner cleanup')
    print(''.join(logs))
finally:
    if process.poll() is None: process.send_signal(signal.SIGINT);process.wait(timeout=10)
    close_display(display)
