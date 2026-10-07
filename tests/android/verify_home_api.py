"""Compile the Home Activity against installed Android reference APIs; never package or sign."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

repo = Path(sys.argv[1]).resolve()
export = Path(sys.argv[2]).resolve()
dotnet = Path(os.environ.get('CONFECTORY_DOTNET') or shutil.which('dotnet') or '').resolve()
root = dotnet.parent
sdk = sorted((root / 'sdk').glob('*/Roslyn/bincore/csc.dll'))[-1]
net = sorted((root / 'packs/Microsoft.NETCore.App.Ref').glob('*/ref/net8.0'))[-1]
android = sorted((root / 'packs/Microsoft.Android.Ref.34').glob('*/ref/net8.0'))[-1]
core = repo / 'src/Confectory.Core/bin/Release/net8.0/Confectory.Core.dll'
assert core.is_file(), 'Build Core/AndroidExport first'
with tempfile.TemporaryDirectory(prefix='confectory-home-android-api-') as temporary:
    work = Path(temporary)
    globals_file = work / 'Globals.cs'
    globals_file.write_text('global using System; global using System.Collections.Generic; global using System.Linq; global using System.Threading;')
    references = list(net.glob('*.dll')) + list(android.glob('*.dll')) + list((export / 'Managed').glob('*.dll')) + [core]
    sources = [repo / 'targets/android-export/templates/EditorHomeActivity.cs', repo / 'targets/android-export/templates/NativeFieldHost.cs',
               export / 'Generated/PackCalls.cs', export / 'Generated/Bindings.cs', globals_file]
    assert all(p.is_file() for p in sources), 'Export Home generated bindings first'
    response = work / 'compile.rsp'
    response.write_text('\n'.join(['-nologo', '-target:library', '-nullable:enable', '-langversion:12', f'-out:"{work / "Home.dll"}"'] +
                                 [f'-r:"{p}"' for p in references] + [f'"{p}"' for p in sources]))
    subprocess.run([str(dotnet), str(sdk), '@' + str(response)], check=True)
print('Android Home API compilation PASS; APK/AAB packaging and device behavior NOT exercised')
