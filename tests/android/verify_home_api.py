"""Compatibility entry: compile actual exported entry and generic host, never package or sign."""
import os
from pathlib import Path
import shutil
import subprocess
import sys

if len(sys.argv) != 3:
    raise SystemExit('usage: verify_home_api.py REPOSITORY EXPORT_DIRECTORY')
repo = Path(sys.argv[1]).resolve()
export = Path(sys.argv[2]).resolve()
dotnet = os.environ.get('CONFECTORY_DOTNET') or shutil.which('dotnet')
if not dotnet:
    raise SystemExit('missing installed dotnet prerequisite')
subprocess.run([sys.executable, str(repo / 'tests/android/compile_api.py'), str(export), str(Path(dotnet).resolve().parent)], check=True)
