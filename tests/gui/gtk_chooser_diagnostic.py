#!/usr/bin/env python3
"""Standalone GTK comparison, using the unchanged native chooser input helper.

Run on an owned X11 display. Evidence stays in the normal temporary directory;
this probe neither empties that directory nor changes GTK settings or timeouts.
It is a diagnostic baseline, not a replacement for editor_workspace_x11.py.
"""
import ctypes as c
import json
import os
from pathlib import Path
import resource
import select
import subprocess
import sys
import tempfile
import time

P = c.c_void_p
U = c.c_ulong


def bind(lib, name, result, *args):
    function = getattr(lib, name)
    function.restype = result
    function.argtypes = list(args)
    return function


def drive(path, cycles):
    from native_x11_controls import NativeControls
    x = c.CDLL('libX11.so.6')
    display = bind(x, 'XOpenDisplay', P, c.c_char_p)(None)
    assert display, 'Live owned DISPLAY required'
    ui = NativeControls(display)
    query = bind(x, 'XQueryTree', c.c_int, P, U, c.POINTER(U), c.POINTER(U), c.POINTER(P), c.POINTER(c.c_uint))
    fetch = bind(x, 'XFetchName', c.c_int, P, U, c.POINTER(P))

    def find(title):
        root, parent, children, count = U(), U(), P(), c.c_uint()
        assert query(display, ui.root, c.byref(root), c.byref(parent), c.byref(children), c.byref(count))
        try:
            for window in c.cast(children, c.POINTER(U))[:count.value]:
                name = P()
                fetch(display, window, c.byref(name))
                if name:
                    try:
                        if c.string_at(name) == title:
                            return window
                    finally:
                        ui.free(name)
        finally:
            if children:
                ui.free(children)
        return 0

    def wait(title):
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            window = find(title)
            if window:
                return window
            time.sleep(.02)
        raise AssertionError('GTK chooser did not map')

    for cycle in range(cycles):
        print('OPEN', flush=True)
        ui.folder(find, wait, cancel=True)
        print('OPEN', flush=True)
        ui.folder(find, wait, path)
        print('GTK cancel/retry/select cycle', cycle, 'PASS', flush=True)


def probe(cycles):
    assert 1 <= cycles <= 100, 'Diagnostic must retain at least one original selection gate'
    gtk = c.CDLL('libgtk-3.so.0')
    gdk = c.CDLL('libgdk-3.so.0')
    obj = c.CDLL('libgobject-2.0.so.0')
    glib = c.CDLL('libglib-2.0.so.0')
    assert bind(gtk, 'gtk_init_check', c.c_int, P, P)(None, None), 'GTK display unavailable'
    new = bind(gtk, 'gtk_window_new', P, c.c_int)
    title = bind(gtk, 'gtk_window_set_title', None, P, c.c_char_p)
    show = bind(gtk, 'gtk_widget_show_all', None, P)
    destroy = bind(gtk, 'gtk_widget_destroy', None, P)
    realize = bind(gtk, 'gtk_widget_realize', None, P)
    native = bind(gtk, 'gtk_widget_get_window', P, P)
    transient = bind(gdk, 'gdk_window_set_transient_for', None, P, P)
    modal = bind(gtk, 'gtk_window_set_modal', None, P, c.c_int)
    chooser = bind(gtk, 'gtk_file_chooser_dialog_new', P, c.c_char_p, P, c.c_int, c.c_char_p, c.c_int, c.c_char_p, c.c_int, P)
    current = bind(gtk, 'gtk_file_chooser_set_current_folder', c.c_int, P, c.c_char_p)
    filename = bind(gtk, 'gtk_file_chooser_get_filename', P, P)
    free = bind(glib, 'g_free', None, P)
    connect = bind(obj, 'g_signal_connect_data', U, P, c.c_char_p, P, P, P, c.c_int)
    pending = bind(gtk, 'gtk_events_pending', c.c_int)
    iterate = bind(gtk, 'gtk_main_iteration_do', c.c_int, c.c_int)
    focus = bind(gtk, 'gtk_window_get_focus', P, P)
    entry_type = bind(gtk, 'gtk_entry_get_type', c.c_size_t)
    isa = bind(obj, 'g_type_check_instance_is_a', c.c_int, P, c.c_size_t)
    text = bind(gtk, 'gtk_entry_get_text', c.c_char_p, P)
    keyval = bind(gdk, 'gdk_event_get_keyval', c.c_int, P, c.POINTER(c.c_uint))
    event_time = bind(gdk, 'gdk_event_get_time', c.c_uint, P)

    folder = Path(tempfile.mkdtemp(prefix='confectory-gtk-chooser-diagnostic-'))
    for index in range(10):
        (folder / f'Folder{index:02d}').mkdir()
    evidence = {'directory': str(folder.parent), 'entryCount': len(os.listdir(folder.parent)),
                'cycles': cycles, 'responses': [], 'keys': [], 'maxIterationSeconds': 0.0}
    evidence['gtkVersion'] = '.'.join(str(bind(gtk, 'gtk_get_' + component + '_version', c.c_uint)())
                                    for component in ('major', 'minor', 'micro'))
    parent = new(0)
    title(parent, b'Confectory GTK standalone diagnostic')
    show(parent)
    active = None
    reopen = 0.0

    @c.CFUNCTYPE(None, P, c.c_int, P)
    def response(widget, result, data):
        nonlocal active, reopen
        value = filename(widget)
        try:
            selected = c.string_at(value).decode('utf-8') if value else None
            evidence['responses'].append({'response': result, 'path': selected})
        finally:
            if value:
                free(value)
            destroy(widget)
            active = None
            reopen = time.monotonic() + 1

    @c.CFUNCTYPE(c.c_int, P, P, P)
    def key(widget, event, data):
        value = c.c_uint()
        keyval(event, c.byref(value))
        focused = focus(widget)
        before = text(focused) if focused and isa(focused, entry_type()) else None
        evidence['keys'].append({'receipt': time.monotonic(), 'key': value.value,
                                 'nativeEventTimeMilliseconds': event_time(event),
                                 'textBefore': before.decode('utf-8') if before else ''})
        return 0

    def open_dialog():
        nonlocal active
        active = chooser(b'Select folder', None, 2, b'Cancel', -6, b'Select', -3, None)
        connect(active, b'response', c.cast(response, P), None, None, 0)
        connect(active, b'key-press-event', c.cast(key, P), None, None, 0)
        modal(active, 1)
        assert current(active, str(folder).encode('utf-8'))
        realize(active)
        transient(native(active), native(parent))
        show(active)

    driver = subprocess.Popen([sys.executable, __file__, '--drive', str(folder), str(cycles)], stdout=subprocess.PIPE, bufsize=0)
    os.set_blocking(driver.stdout.fileno(), False)
    requested = False
    try:
        deadline = time.monotonic() + cycles * 40 + 20
        while driver.poll() is None:
            assert time.monotonic() < deadline, 'Standalone diagnostic process deadline'
            count = 0
            while count < 4096 and pending():
                started = time.monotonic()
                iterate(0)
                evidence['maxIterationSeconds'] = max(evidence['maxIterationSeconds'], time.monotonic() - started)
                count += 1
            # The driver must observe destruction before a new same-title dialog
            # is opened, otherwise its unchanged find(title) gate sees the retry.
            if select.select([driver.stdout], [], [], 0)[0]:
                line = driver.stdout.readline().decode('utf-8').strip()
                if line == 'OPEN':
                    assert active is None and not requested, 'Overlapping diagnostic dialogs'
                    requested = True
                elif line:
                    print(line, flush=True)
            if requested and time.monotonic() >= reopen:
                open_dialog()
                requested = False
            time.sleep(.002)
        assert driver.returncode == 0, 'Original native chooser input gate failed'
        assert len(evidence['responses']) == cycles * 2, evidence['responses']
        for index, observed in enumerate(evidence['responses']):
            # Escape emits GTK_RESPONSE_DELETE_EVENT; Cancel emits RESPONSE_CANCEL.
            assert observed['response'] in ((-6, -4) if index % 2 == 0 else (-3,)), observed
            if index % 2:
                assert observed['path'] == str(folder), 'GTK selected a child instead of the typed directory'
        print('Standalone GTK original input/cancel/retry/exact selection PASS')
    finally:
        if driver.poll() is None:
            driver.terminate()
            driver.wait(timeout=10)
        driver.stdout.close()
        if active is not None:
            destroy(active)
        destroy(parent)
        usage = resource.getrusage(resource.RUSAGE_SELF)
        evidence['processUsage'] = {'userCpuSeconds': usage.ru_utime, 'systemCpuSeconds': usage.ru_stime,
                                    'maximumRssKiB': usage.ru_maxrss, 'majorFaults': usage.ru_majflt}
        (folder / 'diagnostic.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')
        print('Private GTK diagnostic evidence:', folder, flush=True)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--drive':
        drive(sys.argv[2], int(sys.argv[3]))
    else:
        probe(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
