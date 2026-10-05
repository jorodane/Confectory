#!/usr/bin/env python3
"""Actual X11 event/resize/close/reopen and SIGINT check; no SDK installation."""
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

env = os.environ.copy(); env.pop('CONFECTORY_BASEUI_CLOSE_AFTER_MS', None); env.pop('CONFECTORY_BASEUI_SCRIPTED', None)
process = subprocess.Popen(report['run'], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
try:
    mapped = await_windows(); a, b = mapped['Confectory BaseUI A'], mapped['Confectory BaseUI B']
    pointer(a, 4, 30, 120); pointer(a, 5, 30, 120)
    pointer(a, 4, 30, 120); pointer(a, 5, 0, 0)
    enter = keycode(display, 0xFF0D)
    pointer(a, 2, detail=enter, timestamp=100)
    pointer(a, 3, detail=enter, timestamp=101); pointer(a, 2, detail=enter, timestamp=101)
    pointer(a, 3, detail=enter, timestamp=102)
    flush(display); time.sleep(.15)
    resize(display, a, 500, 350); flush(display); time.sleep(.05)
    pointer(a, 4, 40, 300); pointer(a, 6, 60, 315); pointer(a, 5, 60, 315)
    pointer(a, 4, detail=4)
    p = keycode(display, ord('p')); pointer(a, 2, detail=p); pointer(a, 3, detail=p)
    flush(display); time.sleep(.08)
    if len(sys.argv) > 2: subprocess.run(['import', '-window', 'root', sys.argv[2]], check=True)
    close(a); flush(display); time.sleep(.08)
    assert windows().get('Confectory BaseUI B') == b
    r = keycode(display, ord('r')); pointer(b, 2, detail=r); pointer(b, 3, detail=r); flush(display)
    reopened = await_windows(); assert reopened['Confectory BaseUI B'] == b
    close(reopened['Confectory BaseUI A']); close(b); flush(display)
    stdout, stderr = process.communicate(timeout=5)
    assert process.returncode == 0, stderr
    assert 'view 0 count=2 toggle=0' in stdout, stdout
    assert 'view 1 count=' not in stdout, stdout
    assert 'closed 0' in stdout and 'reopened 0' in stdout, stdout
    print('PASS actual X11 click/outside-release/autorepeat/resize/mixed-camera/close/reopen', stdout)
finally:
    if process.poll() is None: process.kill(); process.wait()

process = subprocess.Popen(report['run'], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
try:
    await_windows(); process.send_signal(signal.SIGINT)
    stdout, stderr = process.communicate(timeout=5)
    assert process.returncode == 0, (process.returncode, stderr)
    assert not any(name.startswith('Confectory BaseUI') for name in windows())
    print('PASS SIGINT cleanup', stdout)
finally:
    if process.poll() is None: process.kill(); process.wait()
    close_display(display)
