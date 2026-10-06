#!/usr/bin/env bash
set -euo pipefail
home_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$home_root"
home_dotnet="${CONFECTORY_DOTNET:-dotnet}"
if [[ "$home_dotnet" == */* ]]; then export PATH="$(dirname -- "$home_dotnet"):$PATH"; fi
export CONFECTORY_EDITOR_REPO="$home_root"
"$home_dotnet" build Confectory.sln -c Release
mkdir -p .confectory
"$home_dotnet" src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/editor-home/project.cpack linux > .confectory/home-launch.json
python - <<'PY'
import json,os
with open('.confectory/home-launch.json',encoding='utf-8') as stream: report=json.load(stream)
if not report.get('tool',{}).get('ok'): raise SystemExit('Entry/home build failed; see .confectory/home-launch.json')
os.execvpe(report['run'][0],report['run'],os.environ)
PY
