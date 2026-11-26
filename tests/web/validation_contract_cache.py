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
    # Use a disposable dependency copy so body and contract changes never touch
    # the installed pack or real project.
    dependency=root/'realtime';shutil.copytree(repo/'packs/realtime-update',dependency)
    for path in (first,second):
        manifest=path/'project.cpack';manifest.write_text(manifest.read_text().replace(str(repo/'packs/realtime-update/pack.cpack'),str(dependency/'pack.cpack')))
    def implementation_dirs():return set((profile/'validation-implementations-v1').glob('*/'))
    original=(first/'Main.csbody').read_bytes()
    assert candidate(first)['ok']
    assert len(dirs())==1;first_cache=next(iter(dirs()))
    saved=records(first_cache);assert saved
    assert len(implementation_dirs())==1;first_impl=next(iter(implementation_dirs()));saved_impl=records(first_impl);assert len(saved_impl)>=2,saved_impl
    assert candidate(first)['ok']
    assert records(first_cache)==saved, 'same contract keys must not be republished'
    assert records(first_impl)==saved_impl, 'unchanged imported implementation keys must not be republished'
    # A damaged compiler artifact must fail its existing content proof and be
    # rebuilt; a new candidate must never treat a failed implementation as valid.
    record=next(iter(saved.values()))[0]
    data=json.loads(record.read_text());assembly=record.parent/data['files']['assembly']['path']
    assembly.write_bytes(b'damaged compiler cache')
    assert candidate(first)['ok']
    repaired=json.loads(record.read_text());assert hashlib.sha256(assembly.read_bytes()).hexdigest()==repaired['files']['assembly']['hash']
    impl_record=next(iter(saved_impl.values()))[0]
    impl_data=json.loads(impl_record.read_text());impl_assembly=impl_record.parent/impl_data['files']['assembly']['path']
    impl_assembly.write_bytes(b'damaged imported artifact')
    assert candidate(first)['ok']
    repaired_impl=json.loads(impl_record.read_text());assert hashlib.sha256(impl_assembly.read_bytes()).hexdigest()==repaired_impl['files']['assembly']['hash']
    changed=dependency/'Advance.csbody';original_dependency=changed.read_bytes();before_change=records(first_impl);stamp=changed.stat()
    changed.write_bytes(original_dependency+b'\n// changed dependency body\n');os.utime(changed,ns=(stamp.st_atime_ns,stamp.st_mtime_ns))
    assert candidate(first)['ok']
    after_change=records(first_impl);assert len(set(after_change)-set(before_change))==1,'one changed imported pack must create one new artifact key'
    assert all(after_change[key]==value for key,value in before_change.items())
    changed.write_bytes(b'this is not valid C#;')
    assert not candidate(first)['ok'], 'an older successful imported artifact cannot validate changed invalid code'
    changed.write_bytes(original_dependency)
    assert candidate(first)['ok']
    contract=dependency/'Advance.celem';implementation=dependency/'AdvanceBody.celem'
    original_contract=contract.read_bytes();original_implementation=implementation.read_bytes()
    contract.write_bytes(original_contract.replace(b'int maximumSteps',b'long maximumSteps'))
    assert not candidate(first)['ok'], 'changed contract must reject the old caller and implementation'
    # A compatible declaration rename changes the generated contract and its
    # imported implementation key, while positional callers remain valid.
    before_contract=records(first_cache);before_impl=records(first_impl)
    contract.write_bytes(original_contract.replace(b'maximumSteps',b'maxSteps'))
    implementation.write_bytes(original_implementation.replace(b'maximumSteps',b'maxSteps'))
    changed.write_bytes(original_dependency.replace(b'maximumSteps',b'maxSteps'))
    assert candidate(first)['ok']
    assert set(records(first_cache))-set(before_contract)
    assert len(set(records(first_impl))-set(before_impl))==1
    contract.write_bytes(original_contract);implementation.write_bytes(original_implementation);changed.write_bytes(original_dependency)
    assert not candidate(first,invalid=True)['ok']
    assert (first/'Main.csbody').read_bytes()==original
    assert len(dirs())==1
    assert candidate(second)['ok']
    assert len(dirs())==2 and records(next(iter(dirs()-{first_cache})))
    assert len(implementation_dirs())==2 and records(next(iter(implementation_dirs()-{first_impl})))
    # Change only a disposable copy of the actual tool configuration. A new
    # fingerprint must produce new contract keys rather than reuse old output.
    tool=root/'tool';tool.mkdir()
    for name in ('pack.cpack','portable.celem','linux.celem'):
        shutil.copyfile(repo/'targets/dotnet'/name,tool/name)
    shutil.copytree(repo/'targets/dotnet/bin/Release/net10.0',tool/'bin/Release/net10.0')
    manifest=first/'project.cpack';manifest.write_text(manifest.read_text().replace(str(repo/'targets/dotnet/pack.cpack'),str(tool/'pack.cpack')))
    assert candidate(first)['ok']
    before_tool_change=set(records(first_cache));before_impl_tool=set(records(first_impl))
    config=tool/'bin/Release/net10.0/Confectory.Build.DotNet.runtimeconfig.json'
    config.write_bytes(config.read_bytes()+b'\n')
    assert candidate(first)['ok']
    assert set(records(first_cache))-before_tool_change,'changed tool fingerprint must produce new keys'
    assert set(records(first_impl))-before_impl_tool,'changed tool fingerprint must invalidate imported implementation keys'
    blocked=root/'unavailable-profile';blocked.mkdir();(blocked/'validation-contracts-v1').write_text('not a directory');(blocked/'validation-implementations-v1').write_text('not a directory')
    env['CONFECTORY_HOME_STORAGE']=str(blocked)
    assert candidate(first)['ok'], 'unavailable optional cache must use ordinary candidate compilation'
    print('PASS exact contract and imported implementation reuse, dependency body/contract changes, damaged artifacts, invalid compilation, same-ID isolation, tool invalidation and unavailable-cache fallback')

with tempfile.TemporaryDirectory(prefix='confectory-validation-contracts-') as folder:
    exercise(Path(folder))
