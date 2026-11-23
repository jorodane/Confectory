#!/usr/bin/env python3
"""Native GTK LAN chat on one isolated Xorg display, with no ports published.

Pass the Linux EditorHome build report and a local fixture image containing sh,
cat, sleep, dirname and the system ELF interpreter. Runtime libraries are
mounted read-only from the Linux test host. No invitation is printed.
"""
import ctypes as c
from contextlib import contextmanager
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import sys
import tempfile
import time
import uuid

from native_x11_controls import NativeControls

repo = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo / 'tests/packs'))
from editor_private_lan_fixture import DOCKER, GUEST, HOST, docker, internal_network

dotnet = Path(os.environ['CONFECTORY_DOTNET']).resolve()
xdisplay = os.environ['DISPLAY']
assert xdisplay.startswith(':') and xdisplay[1:].isdigit(), 'Use a dedicated local Xorg display'
xsocket = Path('/tmp/.X11-unix') / ('X' + xdisplay[1:])
authority = Path(os.environ['XAUTHORITY']).resolve()
P, U = c.c_void_p, c.c_ulong
x11 = c.CDLL('libX11.so.6')


def bind(lib, name, result, *args):
    method = getattr(lib, name)
    method.restype, method.argtypes = result, list(args)
    return method


display = bind(x11, 'XOpenDisplay', P, c.c_char_p)(None)
assert display, 'Use an owned Xorg display'
ui = NativeControls(display)
fetch = bind(x11, 'XFetchName', c.c_int, P, U, c.POINTER(P))
atom = bind(x11, 'XInternAtom', U, P, c.c_char_p, c.c_int)
send_event = bind(x11, 'XSendEvent', c.c_int, P, U, c.c_int, c.c_long, P)


def native_windows(title=b'Confectory - Projects'):
    root, parent, children, count = U(), U(), P(), c.c_uint()
    assert ui.query(display, ui.root, c.byref(root), c.byref(parent), c.byref(children), c.byref(count))
    windows = set()
    try:
        for window in c.cast(children, c.POINTER(U))[:count.value]:
            value = P()
            if fetch(display, window, c.byref(value)) and value:
                try:
                    if c.string_at(value) == title:
                        windows.add(window)
                finally:
                    ui.free(value)
    finally:
        if children:
            ui.free(children)
    return windows


def eventually(predicate, label, timeout=35):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result = predicate()
        if result:
            return result
        time.sleep(.04)
    raise AssertionError(label)


def clipboard_invite(version):
    # Read only the synthetic selection on this owned X server. Keep it in memory.
    gtk, gdk, glib = (c.CDLL(lib) for lib in ('libgtk-3.so.0', 'libgdk-3.so.0', 'libglib-2.0.so.0'))
    assert bind(gtk, 'gtk_init_check', c.c_int, P, P)(None, None)
    selection = bind(gdk, 'gdk_atom_intern', P, c.c_char_p, c.c_int)(b'CLIPBOARD', 0)
    clipboard = bind(gtk, 'gtk_clipboard_get', P, P)(selection)
    value = bind(gtk, 'gtk_clipboard_wait_for_text', P, P)(clipboard)
    assert value, 'GTK clipboard selection is empty'
    try:
        try:
            card = json.loads(c.string_at(value))
            assert card['version'] == version and len(card['code']) == 64
            return card
        except (AssertionError, KeyError, TypeError, ValueError):
            raise AssertionError('GTK clipboard did not contain the expected invitation') from None
    finally:
        bind(glib, 'g_free', None, P)(value)


class NativeEditor:
    def __init__(self, container, profile, checkout):
        self.container, self.profile, self.checkout = container, profile, checkout
        self.log = profile / 'gtk.log'
        self.offset = 0
        self.last = None

    def command(self, command, setup=False, **variables):
        writable = dict(CONFECTORY_DOTNET=str(dotnet), CONFECTORY_EDITOR_REPO=str(self.checkout),
                        CONFECTORY_HOME_STORAGE=str(self.profile), CONFECTORY_ENTRY_STORAGE=str(self.profile / 'entry'),
                        CONFECTORY_ENTRY_SCOPE=str(self.profile / 'bridge'), CONFECTORY_HOME_TRACE='1',
                        CONFECTORY_MCP_DIRECTORY=str(self.profile / 'instances'),
                        PATH=f'{dotnet.parent}:/usr/bin:/bin', DISPLAY=xdisplay, XAUTHORITY=str(authority),
                        GSETTINGS_BACKEND='memory', XDG_CACHE_HOME=str(self.profile / 'cache'),
                        XDG_CONFIG_HOME=str(self.profile / 'config'), XDG_DATA_HOME=str(self.profile / 'data'),
                        LIBGL_ALWAYS_SOFTWARE='1', **variables)
        options = [entry for key, value in writable.items() for entry in ('--env', f'{key}={value}')]
        return [*DOCKER, 'exec', *(['-i'] if setup else []), *options, self.container, *command]

    def launch(self, command, setup=None):
        prior = native_windows()
        self.offset, self.last = 0, None
        self.stream = self.log.open('w')
        variables = {'CONFECTORY_TEST_PUBLIC_CHAT_RELAY': '1'} if setup else {}
        self.child = subprocess.Popen(self.command(command, setup=setup is not None, **variables),
                                      stdin=subprocess.PIPE if setup else None, text=True,
                                      stdout=self.stream, stderr=subprocess.STDOUT)
        if setup:
            self.child.stdin.write(json.dumps(setup) + '\n')
            self.child.stdin.close()
        self.window, = eventually(lambda: native_windows() - prior, 'Native GTK window did not map')
        self.wait(lambda row: row['screen'] == 'intro' and 1 in row['hits'][::5], 'Startup Later button')
        self.click(1)
        self.wait(lambda row: row['screen'] == 'home', 'GTK Home')

    def state(self):
        with self.log.open() as stream:
            stream.seek(self.offset)
            while line := stream.readline():
                if not line.endswith('\n'):
                    break
                self.offset = stream.tell()
                if line.startswith('HOME_UI '):
                    self.last = json.loads(line[8:])
        return self.last

    def wait(self, condition, label, timeout=35):
        def read():
            assert self.child.poll() is None, 'Editor exited before expected GUI state'
            state = self.state()
            return state if state and condition(state) else None
        return eventually(read, label, timeout)

    def click(self, control):
        state = self.wait(lambda row: control in row['hits'][::5], f'Enabled native control {control}')
        index = state['hits'][::5].index(control) * 5
        x, y, w, h = state['hits'][index+1:index+5]
        ui.click(self.window, x+w//2, y+h//2)

    @staticmethod
    def field(row, control):
        return json.loads(row['fields'].get(str(control), '{}'))

    def key(self, control, key, *mods):
        state = self.wait(lambda row: self.field(row, control).get('visible'), f'Visible GTK field {control}')
        ui.key(int(self.field(state, control)['nativeHandle']), key, mods)

    def fill(self, control, value):
        self.click(control)
        state = self.wait(lambda row: self.field(row, control).get('visible'), f'GTK input {control}')
        ui.text(int(self.field(state, control)['nativeHandle']), value)
        self.wait(lambda row: self.field(row, control).get('text') == value, f'GTK input reflected {control}')

    def create(self, title, draft):
        self.click(2)
        self.wait(lambda row: row['screen'] == 'create', 'Create form')
        self.fill(10, title)
        self.click(12)
        parent = str(self.profile.parent / 'projects')
        def find(title):
            return next(iter(native_windows(title)), None)
        ui.folder(find, lambda title: eventually(lambda: find(title), 'Native folder picker'), parent)
        self.wait(lambda row: self.field(row, 30).get('text') == parent and not row['nativePickerPending'], 'Selected parent folder')
        self.click(13)
        opened = self.wait(lambda row: row['screen'] == 'project' and row['model']['shell'], 'Created project')
        self.fill(38, draft)
        return opened['model']['selected']

    def issue(self, validate=False):
        self.click(450)
        self.click(452)
        self.fill(454, HOST)
        if validate:
            self.fill(455, '192.0.2.9')
            self.click(452)
            self.wait(lambda row: 'Could not issue' in row['lanStatus'], 'Refuse a non-private destination')
            assert not self.listeners()
        self.fill(455, GUEST)
        self.click(452)
        self.wait(lambda row: row['lanMode'] == 'hosting', 'Issue LAN invitation')
        assert set(address for address, _ in self.listeners()) == {HOST}

    def copy_invite(self, version=2):
        self.click(456)
        self.key(456, 'a', 0xFFE3)
        self.key(456, 'c', 0xFFE3)
        assert self.field(self.state(), 456).get('text') == '', 'Secret reached diagnostic trace'
        return clipboard_invite(version)

    def review(self, host, port):
        self.click(450)
        self.click(453)
        self.click(456)
        self.key(456, 'v', 0xFFE3)
        self.fill(457, 'Native fixture guest')
        self.click(453)
        row = self.wait(lambda row: row['lanMode'] == 'review', 'Inspect clipboard invitation')
        assert self.field(row, 456).get('text') == ''
        assert any(f'Host: {HOST}:{port}' in text for text in row['texts'])
        assert any('Project: GTK Host' in text for text in row['texts'])
        assert any('Host certificate SHA-256' in text for text in row['texts'])
        assert port not in host.established_ports()

    def send(self, message):
        self.fill(459, message)
        self.click(460)
        self.wait(lambda row: row['lanStatus'] == 'Public message sent.', 'Confirmed public message')
        self.wait(lambda row: self.field(row, 459).get('text') == '', 'Committed public input cleared')

    def tcp(self):
        return [line.split() for line in docker('exec', self.container, 'cat', '/proc/net/tcp').stdout.splitlines()[1:]]

    def listeners(self):
        result = set()
        for cells in self.tcp():
            hexadecimal, port = cells[1].split(':')
            address = socket.inet_ntoa(struct.pack('<I', int(hexadecimal, 16)))
            if cells[3] == '0A' and not address.startswith('127.'):
                result.add((address, int(port, 16)))
        return result

    def established_ports(self):
        return {int(row[1].split(':')[1], 16) for row in self.tcp() if row[3] == '01'}

    def close(self):
        raw = c.create_string_buffer(192)
        c.c_int.from_buffer(raw,0).value = 33
        U.from_buffer(raw,32).value = self.window
        U.from_buffer(raw,40).value = atom(display,b'WM_PROTOCOLS',0)
        c.c_int.from_buffer(raw,48).value = 32
        U.from_buffer(raw,56).value = atom(display,b'WM_DELETE_WINDOW',0)
        assert send_event(display,self.window,0,0,raw)
        ui.flush(display)
        assert self.child.wait(timeout=25) == 0, 'Native application did not close cleanly'
        self.stream.close()


@contextmanager
def peer(root, network, image_id, address, checkout=repo, other_network=None):
    directory = root / address
    profile = directory / 'profile'
    profile.mkdir(parents=True)
    (directory / 'projects').mkdir()
    machine = directory / 'fixture-machine-id'
    machine.write_text(uuid.uuid4().hex + '\n')
    passwd = directory / 'fixture-passwd'
    passwd.write_text(f'fixture:x:{os.getuid()}:{os.getgid()}:Owned LAN fixture:/tmp:/bin/sh\n')
    container = network + '-' + address.replace('.', '-')
    mounts = [(repo, repo, True), (dotnet.parent, dotnet.parent, True), (directory, directory, False),
              (machine, '/etc/machine-id', True), (passwd, '/etc/passwd', True), (xsocket, xsocket, True), (authority, authority, True)]
    mounts.extend((path, path, True) for path in ('/usr/lib/x86_64-linux-gnu', '/usr/share/fonts',
                                                  '/usr/share/glib-2.0/schemas', '/usr/share/mime', '/usr/share/icons', '/etc/fonts'))
    if checkout != repo:
        mounts.append((checkout, checkout, True))
    options = [item for src,dst,readonly in mounts for item in
               ('--mount', f'type=bind,src={src},dst={dst}' + (',readonly' if readonly else ''))]
    networks = ['--network', f'name={network},ip={address}']
    expected = {network}
    if other_network:
        other, other_address = other_network
        networks += ['--network', f'name={other},ip={other_address}', '--sysctl', 'net.ipv4.ip_forward=0']
        expected.add(other)
    docker('run', '--pull=never', '--detach', '--name', container, *networks,
           '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', f'{os.getuid()}:{os.getgid()}',
           '--workdir', str(repo), *options, image_id, '/usr/bin/sleep', '900')
    try:
        settings, = json.loads(docker('inspect', container).stdout)
        assert not settings['HostConfig']['PortBindings'] and set(settings['NetworkSettings']['Networks']) == expected
        routes = docker('exec', container, 'cat', '/proc/net/route').stdout.splitlines()[1:]
        assert all(row.split()[1] != '00000000' for row in routes if row.strip())
        yield NativeEditor(container, profile, checkout)
    finally:
        docker('rm', '--force', container)


if __name__ == '__main__':
    report = json.loads(Path(sys.argv[1]).read_text())
    assert report['target'] == 'linux'
    image = sys.argv[2]
    root = Path(tempfile.mkdtemp(prefix='cf-native-lan-test-'))
    print('Native LAN fixture logs at', root, flush=True)
    with internal_network(image) as (network, image_id), \
         peer(root, network, image_id, HOST) as host, peer(root, network, image_id, GUEST) as guest:
        host.launch(report['run']); guest.launch(report['run'])
        owner = host.create('GTK Host', 'Host private draft')
        participant = guest.create('GTK Guest', 'Guest private draft')
        manifests = {Path(project['path']): Path(project['path']).read_bytes() for project in (owner, participant)}
        assert not host.listeners() and not guest.listeners()
        host.click(450); host.click(452)
        host.fill(454, HOST); host.fill(455, GUEST)
        host.click(451)
        host.wait(lambda row: host.field(row,38).get('text') == 'Host private draft', 'Host draft after cancelling issue')
        host.fill(38, 'Host private draft edited after cancel')
        assert not host.listeners() and not (host.profile / 'project-chat').exists()
        host.issue(validate=True)
        _, port = next(iter(host.listeners()))
        host.send('Before admission')
        secret = host.copy_invite()['code']
        guest.review(host, port)
        guest.click(451)
        guest.wait(lambda row: guest.field(row,38).get('text') == 'Guest private draft', 'Guest draft after cancelling join')
        guest.fill(38, 'Guest private draft edited after cancel')
        assert port not in host.established_ports() and not (guest.profile / 'project-chat').exists()
        assert host.copy_invite()['code'] == secret
        guest.review(host, port)
        guest.click(458)
        guest.wait(lambda row: guest.field(row,461).get('text') == 'No messages yet.', 'First LAN inbox is empty')
        print('PASS cancel before issue or join preserves keyboard input and does not open or consume an invitation', flush=True)
        assert guest.state()['model']['selected']['projectId'] == participant['projectId']
        assert 38 not in guest.state()['hits'][::5] and 452 not in guest.state()['hits'][::5]
        host.send('Public host text'); guest.send('Public guest text')
        host.wait(lambda row: 'Public guest text' in host.field(row,461).get('text',''), 'Guest text rendered on host')
        guest.wait(lambda row: 'Public host text' in guest.field(row,461).get('text',''), 'Host text rendered on guest')
        print('PASS isolated GTK issue, Ctrl+C/Ctrl+V, review, empty admission and bidirectional public text', flush=True)

        guest.click(451)
        guest.wait(lambda row: guest.field(row,38).get('text') == 'Guest private draft edited after cancel', 'Guest Helper draft retained')
        assert host.copy_invite()['code'] == secret
        guest.review(host, port)
        guest.click(458)
        guest.wait(lambda row: 'Could not join' in row['lanStatus'], 'Reject consumed invitation')
        guest.click(451); host.click(451)
        host.wait(lambda row: host.field(row,38).get('text') == 'Host private draft edited after cancel', 'Host Helper draft retained')
        eventually(lambda: not host.listeners(), 'Host listener remained after explicit end')
        host.issue(); _, port = next(iter(host.listeners()))
        fresh = host.copy_invite()['code']
        assert fresh != secret
        guest.review(host, port); guest.click(458)
        guest.wait(lambda row: guest.field(row,461).get('text') == 'No messages yet.', 'Fresh LAN inbox is empty')
        host.close()
        guest.wait(lambda row: row['lanMode'] == 'closed' and 'disconnected' in row['lanStatus'], 'Closing host cleared guest connection')
        assert not host.listeners()
        guest.close()
        assert not (guest.profile / 'project-chat').exists()
        journal, = (host.profile / 'project-chat').glob('*.json')
        stored = journal.read_text()
        assert [row['text'] for row in json.loads(stored)['messages']] == ['Before admission','Public host text','Public guest text']
        assert all(path.read_bytes() == before for path, before in manifests.items())
        for editor, expected in ((host,'Host private draft edited after cancel'),(guest,'Guest private draft edited after cancel')):
            saved, = (editor.profile / 'project-chat-drafts').glob('*.json')
            assert json.loads(saved.read_text())['draft'] == expected
        observable = stored + host.log.read_text() + guest.log.read_text()
        assert all(code not in observable for code in (secret, fresh)), 'Invitation leaked to logs or journal'
        print('PASS consumed/reissued invitations, native close, host-only durable history, private drafts and original files', flush=True)
