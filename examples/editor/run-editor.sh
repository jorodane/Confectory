#!/usr/bin/env bash
set -euo pipefail
editor_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$editor_root"
editor_dotnet="${CONFECTORY_DOTNET:-dotnet}"
if [[ "$editor_dotnet" == */* ]]; then export PATH="$(dirname -- "$editor_dotnet"):$PATH"; fi
export CONFECTORY_EDITOR_REPO="$editor_root"
"$editor_dotnet" build Confectory.sln -c Release
mkdir -p .confectory
"$editor_dotnet" src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll build examples/editor/project.cpack linux > .confectory/editor-launch.json
python - <<'PY'
import json,os
with open('.confectory/editor-launch.json',encoding='utf-8') as stream: report=json.load(stream)
if not report.get('tool',{}).get('ok'): raise SystemExit('Editor target build failed; see .confectory/editor-launch.json')
os.execvpe(report['run'][0],report['run'],os.environ)
PY
