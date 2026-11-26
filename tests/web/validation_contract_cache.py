"""Real compiler-backed candidate validation with a disposable project-owned cache.

Arguments: checkout containing the built Linux target tool. The authoring host
and dotnet are selected through the normal fixture environment.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid

repo=Path(sys.argv[1]).resolve()
command=[os.environ['CONFECTORY_DOTNET'],os.environ['CONFECTORY_ELEMENT_AUTHORING_HOST']]

def exercise(root):
    def project(name):
        path=root/name
        shutil.copytree(repo/'examples/frame-loop',path,ignore=shutil.ignore_patterns('.confectory','bin','obj'))
        manifest=path/'project.cpack'
        manifest.write_text(manifest.read_text().replace('../../',str(repo)+'/'))
        return path
    profile=root/"profile";profile.mkdir()
    env=dict(os.environ,CONFECTORY_HOME_STORAGE=str(profile))
    def candidate(path,invalid=False):
        target=path/'.confectory'/'candidates'/uuid.uuid4().hex
        shutil.copytree(path,target,ignore=shutil.ignore_patterns('.confectory','bin','obj'))
        if invalid:(target/'Main.csbody').write_text('this is not valid C#;')
        request=dict(operation='validate',project=str(target/'project.cpack'),target='linux')
        result=subprocess.run(command,input=json.dumps(request),text=True,capture_output=True,timeout=120,check=True,env=env)
        shutil.rmtree(target)
        return json.loads(result.stdout)
    def dirs():return set((profile/'validation-contracts-v1').glob('*/'))
    def records(path):return {p.parent.name:(p,p.stat().st_mtime_ns) for p in path.glob('*/artifact.json')}
    first=project('first');second=project('second')
    original=(first/'Main.csbody').read_bytes()
    assert candidate(first)['ok']
    assert len(dirs())==1;first_cache=next(iter(dirs()))
    saved=records(first_cache);assert saved
    assert candidate(first)['ok']
    assert records(first_cache)==saved, 'same contract keys must not be republished'
    # A damaged compiler artifact must fail its existing content proof and be
    # rebuilt; a new candidate must never treat a failed implementation as valid.
    record=next(iter(saved.values()))[0]
    data=json.loads(record.read_text());assembly=record.parent/data['files']['assembly']['path']
    assembly.write_bytes(b'damaged compiler cache')
    assert candidate(first)['ok']
    repaired=json.loads(record.read_text());assert hashlib.sha256(assembly.read_bytes()).hexdigest()==repaired['files']['assembly']['hash']
    assert not candidate(first,invalid=True)['ok']
    assert (first/'Main.csbody').read_bytes()==original
    assert len(dirs())==1
    assert candidate(second)['ok']
    assert len(dirs())==2 and records(next(iter(dirs()-{first_cache})))
    # Change only a disposable copy of the actual tool configuration. A new
    # fingerprint must produce new contract keys rather than reuse old output.
    tool=root/'tool';tool.mkdir()
    for name in ('pack.cpack','portable.celem','linux.celem'):
        shutil.copyfile(repo/'targets/dotnet'/name,tool/name)
    shutil.copytree(repo/'targets/dotnet/bin/Release/net10.0',tool/'bin/Release/net10.0')
    manifest=first/'project.cpack';manifest.write_text(manifest.read_text().replace(str(repo/'targets/dotnet/pack.cpack'),str(tool/'pack.cpack')))
    assert candidate(first)['ok']
    before_tool_change=set(records(first_cache))
    config=tool/'bin/Release/net10.0/Confectory.Build.DotNet.runtimeconfig.json'
    config.write_bytes(config.read_bytes()+b'\n')
    assert candidate(first)['ok']
    assert set(records(first_cache))-before_tool_change,'changed tool fingerprint must produce new keys'
    blocked=root/'unavailable-profile';blocked.mkdir();(blocked/'validation-contracts-v1').write_text('not a directory')
    env['CONFECTORY_HOME_STORAGE']=str(blocked)
    assert candidate(first)['ok'], 'unavailable optional cache must use ordinary candidate compilation'
    print('PASS exact compiler contract reuse, damaged artifact rebuild, invalid implementation rejection, same-ID project isolation, tool fingerprint invalidation and unavailable-cache fallback')

with tempfile.TemporaryDirectory(prefix='confectory-validation-contracts-') as folder:
    exercise(Path(folder))
