#!/usr/bin/env python3
"""Exercise the Linux desktop package on an owned Xorg display.

Pass a linux-x64 package directory and the local image from editor_lan_chat_x11.py.
Use the same CONFECTORY_DOTNET, DISPLAY and XAUTHORITY setup. Only the extracted
package, installed OS/runtime dependencies and an empty fixture home are mounted.
"""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import uuid

from editor_lan_chat_x11 import (
    DOCKER, NativeEditor, authority, docker, dotnet, native_windows, xdisplay, xsocket,
)
from editor_lay_chat_x11 import open_project

INSTALL = '/opt/Confectory Linux'
TITLE = 'Packaged GTK Project'
DRAFT = 'Unsent packaged GTK draft'
OUTPUT = 'Packaged GTK source confirmed'


class InstalledEditor(NativeEditor):
    def command(self, command, setup=False, **variables):
        assert not setup
        settings = dict(HOME=str(self.home), PATH='/opt/dotnet:/usr/bin:/bin',
                        CONFECTORY_HOME_TRACE='1', DISPLAY=xdisplay, XAUTHORITY='/run/Xauthority',
                        GSETTINGS_BACKEND='memory', DOTNET_CLI_TELEMETRY_OPTOUT='1', **variables)
        if self.sdk:
            settings.update(CONFECTORY_EDITOR_REPO='/missing-development-checkout', CONFECTORY_UI='web')
        args = [part for key, value in settings.items() for part in ('--env', f'{key}={value}')]
        return [*DOCKER, 'exec', *args, self.container, *command]

    def invoke(self, *args, **env):
        return subprocess.run(self.command(args, **env), check=True, capture_output=True, text=True, timeout=30)


@contextmanager
def installed_editor(case, package, image, *, sdk):
    home = case / 'home'
    projects, work, temporary = case / 'projects', case / 'work', case / 'tmp'
    for directory in (home, projects, work, temporary):
        directory.mkdir(parents=True)
    # Precreate the mount point so the unprivileged runner owns its cleanup.
    socket_mount = temporary / '.X11-unix' / xsocket.name
    socket_mount.parent.mkdir()
    socket_mount.touch()
    for directory in (home, projects, work):
        if directory.is_relative_to('/tmp'):
            (temporary / directory.relative_to('/tmp')).mkdir(parents=True, exist_ok=True)
    passwd = case / 'passwd'
    passwd.write_text(f'fixture:x:{os.getuid()}:{os.getgid()}:Package fixture:{home}:/bin/sh\n')
    machine = case / 'machine-id'
    machine.write_text(uuid.uuid4().hex + '\n')
    mounts = [(machine, '/etc/machine-id', True), (package, INSTALL, True), (home, home, False), (projects, projects, False), (work, work, True),
              (passwd, '/etc/passwd', True), (temporary, '/tmp', False), (xsocket, xsocket, True), (authority, '/run/Xauthority', True)]
    for path in ('/usr/lib/x86_64-linux-gnu', '/usr/share/fonts', '/usr/share/glib-2.0/schemas',
                 '/usr/share/mime', '/usr/share/icons', '/etc/fonts'):
        mounts.append((path, path, True))
    if sdk:
        mounts.append((dotnet.parent, '/opt/dotnet', True))
    else:
        mounts.extend((dotnet.parent / name, '/opt/dotnet/' + name, True)
                      for name in ('dotnet', 'host', 'shared'))
    options = [part for src, dst, ro in mounts
               for part in ('--mount', f'type=bind,src={src},dst={dst}' + (',readonly' if ro else ''))]
    container = f'confectory-package-{case.parent.name}-{case.name}'.lower()
    docker('run', '--pull=never', '--detach', '--name', container, '--network', 'none', '--cap-drop', 'ALL',
           '--security-opt', 'no-new-privileges', '--user', f'{os.getuid()}:{os.getgid()}',
           '--workdir', str(work), *options, image, '/usr/bin/sleep', '600')
    app = InstalledEditor(container, home / '.local/share/Confectory/EditorHome', package)
    app.home, app.log, app.sdk = home, case / 'gtk.log', sdk
    try:
        inspect, = json.loads(docker('inspect', container).stdout)
        assert inspect['HostConfig']['NetworkMode'] == 'none' and not inspect['HostConfig']['PortBindings']
        app.invoke('/bin/sh', '-ec', 'test "$(id -u)" -ne 0; test ! -e /workspace; test ! -e .git')
        assert bool(app.invoke('dotnet', '--list-sdks').stdout.strip()) is sdk
        assert not any(home.iterdir()), 'The app must start with a clean HOME'
        yield app, projects
    except BaseException:
        if app.log.exists():
            for line in app.log.read_text().splitlines()[-25:]:
                if not line.startswith('HOME_UI '):
                    print(line, file=sys.stderr)
        raise
    finally:
        docker('rm', '--force', container)


def open_source(app):
    app.click(55)
    return app.wait(lambda row: (row['model'].get('workspace') or {}).get('unit', {}).get('kind') == 'body'
                    and app.field(row, 54).get('visible'), 'Packaged GTK Source')


def compile_and_run(app, marker):
    marker.unlink(missing_ok=True)
    app.click(36)
    row = app.wait(lambda state: (state['model'].get('execution') or {}).get('state') in ('exited', 'failed'),
                   'Packaged project process exit', timeout=120)
    assert (row['model']['execution']['state'], row['model']['execution']['exit']) == ('exited', '0'), row['model']['status']
    assert marker.read_text() == OUTPUT


def test_package(package, image, case):
    launcher = [INSTALL + '/run']
    with installed_editor(case / 'runtime', package, image, sdk=False) as (app, projects):
        plan = json.loads(app.invoke(*launcher, '--check-package').stdout)
        assert plan['rid'] == 'linux-x64' and plan['linuxExecuted'] is False
        env = plan['environment']
        assert env['CONFECTORY_UI'] == 'native' and 'CONFECTORY_WEBVIEW_HOST' not in env
        assert env['CONFECTORY_EDITOR_REPO'] == INSTALL + '/content'
        assert Path(env['CONFECTORY_HOME_STORAGE']) == app.profile and not app.profile.exists()
        missing_runtime = subprocess.run(app.command(launcher, CONFECTORY_DOTNET='/absent/dotnet'),
                                         capture_output=True, text=True, timeout=30)
        assert missing_runtime.returncode == 1 and 'requires .NET Runtime 10.0 x64' in missing_runtime.stderr
        app.launch(launcher)
        assert not app.state()['model']['cards']
        app.create('Runtime only', '', projects)
        app.click(36)
        app.wait(lambda row: (row['model'].get('execution') or {}).get('state') == 'failed'
                 and any('installed .NET 10 SDK' in text for text in row['texts']), 'Run explains missing SDK')
        app.close()
    print('PASS runtime-only GTK first launch and explicit SDK requirement on Run', flush=True)

    with installed_editor(case / 'sdk', package, image, sdk=True) as (app, projects):
        # An inherited development setting must never redirect the installed launcher.
        app.launch(launcher)
        model = app.state()['model']
        assert not model['cards'] and not model['helperAgents']['agents'] and not app.listeners()
        project = app.create(TITLE, DRAFT, projects)
        source = Path(project['path']).parent / 'main.csbody'
        original = source.read_bytes()
        assert original == b'return 0;\n'
        assert (app.profile / 'project-creators' / (project['projectId'] + '.json')).exists()
        marker = app.home / 'executed.txt'
        edited = f'System.IO.File.WriteAllText({json.dumps(str(marker))}, "{OUTPUT}");\nreturn 0;\n'
        assert app.field(open_source(app), 54)['text'] == original.decode()
        app.fill(54, edited)
        app.click(58)
        app.wait(lambda row: row['message'] == 'Local source draft saved; final sources unchanged', 'GTK draft Save')
        app.click(64)
        app.wait(lambda row: 65 in row['hits'][::5], 'GTK Review')
        app.click(66)
        app.wait(lambda row: row['model']['workspace'].get('review') is None, 'GTK Review cancellation')
        assert source.read_bytes() == original
        app.click(64)
        app.wait(lambda row: 65 in row['hits'][::5], 'Fresh GTK Review')
        app.click(65)
        app.wait(lambda row: row['model']['status'].startswith('Confirm confirmed'), 'Explicit GTK Confirm', timeout=120)
        assert source.read_text() == edited
        compile_and_run(app, marker)
        app.close()
        assert app.window not in native_windows()
        print('PASS packaged GTK Later, folder picker, create, Source Save/Review/Confirm and Run', flush=True)

        app.launch(launcher)
        reopened = open_project(app, TITLE)
        assert reopened['projectId'] == project['projectId']
        app.wait(lambda row: app.field(row, 38).get('text') == DRAFT, 'Persisted local chat draft')
        assert app.field(open_source(app), 54)['text'] == edited
        compile_and_run(app, marker)
        assert not app.listeners()
        app.close()
    print('PASS full packaged GTK restart, Recent, confirmed source, local draft and second Run', flush=True)


if __name__ == '__main__':
    package, image = Path(sys.argv[1]).resolve(), sys.argv[2]
    with tempfile.TemporaryDirectory(prefix='cf-install-') as scratch:
        case = Path(scratch)
        archive = case / 'linux.tar.gz'
        with tarfile.open(archive, 'w:gz') as bundle:
            bundle.add(package, arcname='extract')
        with tarfile.open(archive) as bundle:
            bundle.extractall(case, filter='data')
        archive.unlink()
        test_package(case / 'extract', image, case)
