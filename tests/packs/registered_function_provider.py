"""Read-only registered provider proposal; synthetic owned function declaration."""
import json, os, subprocess, sys, tempfile
from pathlib import Path
host=[os.environ['CONFECTORY_DOTNET'],sys.argv[1]]
window=(Path(sys.argv[2]).resolve()/'packs/window/pack.cpack')
with tempfile.TemporaryDirectory(prefix='cf-provider-') as folder:
    root=Path(folder); project=root/'project.cpack'; source=root/'main.celem'
    original='function Alpha::Main () -> int { // retain\n}\n'
    manifest=f'project Alpha version "1" {{ standalone true; entry Alpha::Main; registry Confectory.Window {json.dumps(str(window))}; dependency Confectory.Window version "0.1.0"; element Main function "main.celem"; }}'
    project.write_text(manifest);source.write_text(original)
    args=dict(operation='registeredFunctionProvider',project=str(project),manifest=manifest,text=original,function='Confectory.Window::Open',implementation='Confectory.Window::Native')
    def call(ok,**changes):
        reply=json.loads(subprocess.run(host,input=json.dumps(dict(args,**changes)),text=True,capture_output=True,check=True,timeout=30).stdout)
        assert reply['ok']==ok,reply
        return reply.get('result')
    candidate=call(True)
    assert 'provide Confectory.Window::Open with Confectory.Window::Native;' in candidate and '// retain' in candidate
    call(False,implementation='Confectory.Window::CloseBody')
    call(False,implementation='Other.Window::Native')
    call(False,function='Confectory.Window::Missing')
    call(False,manifest=manifest+' ')
    call(False,text=original+' ')
    assert project.read_text()==manifest and source.read_text()==original
    if os.name!='nt':
        retained=root/'retained.celem';source.rename(retained);source.symlink_to(retained)
        call(False)
        assert retained.read_text()==original
print('PASS exact owned source, direct registry, contract match, stale input rejection, no write')
