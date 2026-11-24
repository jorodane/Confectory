#!/usr/bin/env python3
"""Installed GTK Home folder actions, real Thunar, and launcher failure fixtures."""
import ctypes as c
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from unittest.mock import patch

from editor_home_project_display_x11 import attach, editor, gtk, make_project, tile
from editor_lan_chat_x11 import P, bind, display, eventually, ui
from playwright.sync_api import expect, sync_playwright


def file_manager_windows():
    windows = subprocess.check_output(['xwininfo', '-root', '-children'], text=True)
    windows = re.findall(r'^\s+(0x[0-9a-f]+) .*: \("thunar" "Thunar"\)', windows, flags=re.MULTILINE)
    visible = set()
    for handle in windows:
        window = int(handle, 16)
        attributes = c.create_string_buffer(136)
        if ui.attributes(display, window, attributes) and c.c_int.from_buffer(attributes, 92).value == 2:
            visible.add(window)
    return visible


def folder_from_thunar(window):
    gtk_lib, gdk, glib = (c.CDLL(name) for name in ('libgtk-3.so.0', 'libgdk-3.so.0', 'libglib-2.0.so.0'))
    assert bind(gtk_lib, 'gtk_init_check', c.c_int, P, P)(None, None)
    atom = bind(gdk, 'gdk_atom_intern', P, c.c_char_p, c.c_int)(b'CLIPBOARD', 0)
    clipboard = bind(gtk_lib, 'gtk_clipboard_get', P, P)(atom)
    ui.key(window, 'l', (0xFFE3,))
    ui.key(window, 'a', (0xFFE3,))
    ui.key(window, 'c', (0xFFE3,))
    value = bind(gtk_lib, 'gtk_clipboard_wait_for_text', P, P)(clipboard)
    assert value, 'Thunar did not copy the visible location'
    try:
        return Path(c.string_at(value).decode())
    finally:
        bind(glib, 'g_free', None, P)(value)


def home_result(app, message):
    frame = app.wait(lambda row: row['screen'] == 'home' and message in row['message'], message)
    assert frame['model']['selected'] is None


def setup_profile(root):
    config = root / 'config'
    config.mkdir()
    (config / 'mimeapps.list').write_text('[Default Applications]\ninode/directory=thunar.desktop;\n')
    (config / 'xfce4').mkdir()
    (config / 'xfce4/helpers.rc').write_text('FileManager=thunar\n')
    runtime = root / 'run'
    runtime.mkdir(mode=0o700)
    return dict(XDG_CONFIG_HOME=str(config), XDG_DATA_HOME=str(root / 'data'),
                XDG_CACHE_HOME=str(root / 'cache'), XDG_RUNTIME_DIR=str(runtime),
                XDG_CURRENT_DESKTOP='XFCE', GIO_USE_VFS='local')


def workflow(package, root):
    (root / 'profile').mkdir()
    paths = [make_project(package, root, name)[0] for name in ('Alpha', 'Bravo')]
    special = root / "Alpha & (draft) # 100% 'folder'"
    paths[0].parent.rename(special)
    paths[0] = special / paths[0].name
    catalog = root / 'profile/projects.json'
    listings = [{'path': str(path), 'title': title, 'description': ''}
                for path, title in zip(paths, ('First fixture', 'Second fixture'))]
    catalog.write_text(json.dumps(listings))
    original = catalog.read_bytes(), catalog.stat().st_mtime_ns
    sources = {p: p.read_bytes() for path in paths for p in path.parent.iterdir()}

    def catalog_unchanged():
        assert (catalog.read_bytes(), catalog.stat().st_mtime_ns) == original

    native_env = setup_profile(root)
    with patch.dict(os.environ, native_env):
        assert not file_manager_windows(), 'Use a dedicated display without existing Thunar windows'
        try:
            with gtk(package, root, 'gtk-real-folders') as app:
                for index, manifest in enumerate(paths):
                    before = file_manager_windows()
                    app.menu(index)
                    app.click(449)
                    home_result(app, 'Folder request sent')
                    window, = eventually(lambda: file_manager_windows() - before,
                                         'The actual Thunar window did not open')
                    assert eventually(lambda: folder_from_thunar(window) == manifest.parent,
                                      'Thunar did not open the exact registered directory')
                    catalog_unchanged()
            assert file_manager_windows(), 'Editor close retired the external file manager'
        finally:
            if file_manager_windows():
                subprocess.run(['/usr/bin/thunar', '--quit'], check=True, timeout=10)
                eventually(lambda: not file_manager_windows(), 'Close owned Thunar windows')
    print('PASS GTK package opens both exact registered folders in real Thunar')

    # The controlled launcher proves argument boundaries and a nonzero process exit.
    fake_bin = root / 'fake-bin'
    fake_bin.mkdir()
    fake_launcher = fake_bin / 'xdg-open'
    fake_launcher.write_text('#!/bin/sh\n[ "$BROWSER" = /bin/false ] || exit 90\nprintf "%s\\0" "$@" >> "$CF_TEST_FOLDER_REQUESTS"\nsleep 1\nexit 4\n')
    fake_launcher.chmod(0o700)
    receipts = root / 'launches'
    with patch.dict(os.environ, dict(native_env, PATH=f'{fake_bin}:{os.environ["PATH"]}',
                                     CF_TEST_FOLDER_REQUESTS=str(receipts))):
        with gtk(package, root, 'gtk-failed-launcher') as app:
            app.click(101)
            home_result(app, 'Folder request sent')
            home_result(app, 'Unable to open folder: The Linux file manager could not open this folder (launcher exit 4).')
            expected_receipt = os.fsencode(paths[0].parent) + b'\0'
            assert receipts.read_bytes() == expected_receipt
            catalog_unchanged()

            missing = root / 'moved-fixture'
            paths[1].parent.rename(missing)
            try:
                app.menu(1)
                app.click(449)
                home_result(app, 'Unable to open folder: The registered project folder is no longer available.')
                assert receipts.read_bytes() == expected_receipt
                catalog_unchanged()
            finally:
                missing.rename(paths[1].parent)

            # Another owner of the same disposable catalog removes a row after Home rendered.
            catalog.write_text(json.dumps(listings[:1]))
            changed = catalog.read_bytes(), catalog.stat().st_mtime_ns
            app.menu(1)
            app.click(449)
            home_result(app, 'Unable to open folder: The project is no longer registered.')
            assert receipts.read_bytes() == expected_receipt
            assert (catalog.read_bytes(), catalog.stat().st_mtime_ns) == changed

    catalog.write_bytes(original[0])
    original = catalog.read_bytes(), catalog.stat().st_mtime_ns
    limited_bin = root / 'without-xdg-open'
    limited_bin.mkdir()
    for tool in ('setsid', 'env', 'dirname'):
        (limited_bin / tool).symlink_to('/usr/bin/' + tool)
    with patch.dict(os.environ, dict(native_env, PATH=str(limited_bin))):
        with gtk(package, root, 'gtk-no-launcher') as app:
            app.menu(1)
            app.click(449)
            home_result(app, 'Unable to open folder: The Linux file-manager launcher (xdg-open) could not be started.')
            catalog_unchanged()
    print('PASS GTK controlled launcher exit/missing, exact single argument, stale registration, and missing folder')

    with sync_playwright() as playwright:
        with playwright.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'],
                                        ignore_default_args=['--disable-dev-shm-usage']) as browser:
            with editor(package, root, 'chromium-folders') as url:
                page, errors = attach(browser, url)
                for title in ('First fixture', 'Second fixture'):
                    tile(page, title).locator('[data-enter]').click(button='right')
                    menu = page.locator('.context-menu')
                    expect(menu.get_by_role('button', name='이름 변경', exact=True)).to_be_visible()
                    expect(menu.get_by_role('button', name='폴더 열기', exact=True)).to_have_count(0)
                    page.keyboard.press('Escape')
                assert not errors, errors
                page.close()
    catalog_unchanged()
    assert all(path.read_bytes() == original_bytes for path, original_bytes in sources.items())
    print('PASS Chromium Home exposes no file-manager action; catalog and project sources preserved')


if __name__ == '__main__':
    expect.set_options(timeout=45000)
    assert os.environ.get('DBUS_SESSION_BUS_ADDRESS'), 'Use dbus-run-session on a dedicated Xorg display'
    package = Path(sys.argv[1]).resolve()
    with tempfile.TemporaryDirectory(prefix='gtk-home-folder-') as path:
        workflow(package, Path(path))
