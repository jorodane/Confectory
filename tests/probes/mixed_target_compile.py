"""Force a confirmed isolated fixture's common BP and Windows C# call paths to compile.
Never runs the resulting program or accepts a user project as its source.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

repo, source = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
assert source.name == 'owned project' and source.parent.name.startswith('confectory-wide-mixed-')
assert source.is_relative_to(Path(os.environ['TMPDIR']).resolve())
assert 'project Owned.Elements ' in (source / 'project.cproj').read_text()
assert all((source / name).is_file() for name in ['FreeInfo.celem', 'CallerBody.celem', 'mixed-windows.csbody', 'mixed-caller-windows.csbody'])
before = {str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob('*') if p.is_file()}
case = Path(tempfile.mkdtemp(prefix='confectory-mixed-compile-'))
project = case / 'compile only copy'
shutil.copytree(source, project, ignore=shutil.ignore_patterns('.confectory'))
# Earlier persisted fixtures named an unavailable target declaration. The
# product uses Portable with the windows body key; normalize only this copy.
manifest = project / 'project.cproj'
manifest.write_text(manifest.read_text().replace('target windows Confectory.Build.DotNet::Windows;', 'target windows Confectory.Build.DotNet::Portable;'))
main = project / 'MainBody.celem'
main.write_text(main.read_text().replace('{', '{import Owned.Elements::Caller as MixedCaller (long,long) -> long;', 1))
(project / 'Main.csbody').write_text('return checked((int)calls.MixedCaller.Invoke(7,9));')
checks = []
for target in ['portable', 'windows']:
    result = subprocess.run([os.environ['CONFECTORY_DOTNET'], str(repo / 'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'), 'build', str(project / 'project.cproj'), target], capture_output=True, text=True)
    (case / (target + '.json')).write_text(result.stdout)
    (case / (target + '.err')).write_text(result.stderr)
    assert result.returncode == 0, result.stdout + result.stderr
    build = json.loads(result.stdout)
    assert not build['warnings'], build['warnings']
    fn = 'Owned.Elements::FreeInfo_Function_' + 'a' * 32 + 'Body'
    if target == 'portable':
        assert build['blueprints'][fn]['graphMap']['path'] == 'function.graph.json'
        assert build['blueprints']['Owned.Elements::CallerBody']['graphMap']['path'] == 'caller.graph.json'
    else:
        assert fn not in build['blueprints'] and 'Owned.Elements::CallerBody' not in build['blueprints']
        read = {Path(path).name for path in build['statistics']['readDocuments']}
        assert {'mixed-windows.csbody', 'mixed-caller-windows.csbody'} <= read
    checks.append(target)
    print('PASS 실제 ' + target + ' target이 정보 scope의 혼합 호출 경로를 컴파일하고 실행하지 않는다', flush=True)
assert before == {str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob('*') if p.is_file()}
print(json.dumps({'checks': checks, 'evidence': str(case), 'originalFixtureUnchanged': True, 'compiledOnly': True, 'executed': False}, ensure_ascii=False))
