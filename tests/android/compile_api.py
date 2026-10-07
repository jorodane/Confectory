#!/usr/bin/env python3
"""Compile exported native C# against installed Android references, without claiming APK coverage."""
import pathlib
import subprocess
import sys
import tempfile

if len(sys.argv) != 3:
    raise SystemExit('usage: compile_api.py EXPORT_DIRECTORY DOTNET_SDK_ROOT')
export = pathlib.Path(sys.argv[1]).resolve()
sdk = pathlib.Path(sys.argv[2]).resolve()
def newest(pattern):
    found = list(sdk.glob(pattern))
    if not found:
        raise SystemExit('missing installed prerequisite: ' + pattern)
    return max(found, key=lambda p: tuple(int(x) for x in p.parts[-3].split('.') if x.isdigit()))
net = newest('packs/Microsoft.NETCore.App.Ref/*/ref/net10.0')
android = newest('packs/Microsoft.Android.Ref.34/*/ref/net10.0')
compilers = list(sdk.glob('sdk/*/Roslyn/bincore/csc.dll'))
if not compilers:
    raise SystemExit('missing installed C# compiler')
compiler = max(compilers, key=lambda p: tuple(int(x) for x in p.parts[-4].split('.') if x.isdigit()))
with tempfile.TemporaryDirectory(prefix='confectory-android-api-') as temp:
    work = pathlib.Path(temp)
    implicit = work / 'GlobalUsings.cs'
    implicit.write_text('global using System; global using System.Collections.Generic; global using System.Linq; global using System.Threading;\n')
    refs = list(net.glob('*.dll')) + list(android.glob('*.dll')) + list((export / 'Managed').glob('*.dll'))
    sources = [export / 'MainActivity.cs', export / 'AndroidSurfaceBridge.cs', implicit] + list((export / 'Generated').glob('*.cs'))
    args = ['-nologo', '-target:library', '-nullable:enable', '-langversion:12', '-out:' + str(work / 'ApiProbe.dll')]
    args += ['-r:' + str(p) for p in refs] + [str(p) for p in sources]
    response = work / 'compile.rsp'
    response.write_text('\n'.join('"' + arg + '"' for arg in args))
    result = subprocess.run([str(sdk / 'dotnet'), str(compiler), '@' + str(response)])
    if result.returncode:
        raise SystemExit(result.returncode)
print('PASS Android native C# API compilation; SDK packaging/APK/runtime NOT exercised')
