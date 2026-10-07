#!/usr/bin/env python3
"""Prepare a consumer-local self-edit ProjectPack through the public PackManager example."""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

repo = pathlib.Path(__file__).resolve().parents[2]
root = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(tempfile.mkdtemp(prefix='confectory-self-edit-'))
root.mkdir(parents=True, exist_ok=True)
dotnet = os.environ.get('CONFECTORY_DOTNET', 'dotnet')
cli = repo / 'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'
for name, source in [('engine', repo/'examples/engine'), ('prime-project', repo/'examples/projects/authoring'), ('pin-tool', repo/'examples/pack-manager')]:
    destination = root/name
    if destination.exists():
        raise SystemExit(f'Refusing to replace existing source: {destination}')
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns('.confectory', 'bin', 'obj'))
    for manifest in destination.glob('*.cpack'):
        text = re.sub(r'(registry\s+\S+\s+")([^"]+)(")', lambda match: match[1]+str((source/match[2]).resolve())+match[3], manifest.read_text())
        manifest.write_text(text)
(root/'pin-tool/main.csbody').write_text('''
string project=Environment.GetEnvironmentVariable("CONFECTORY_SELF_PROJECT")!;
string session=calls.PackManagerOpen.Invoke(project);
try
{
 string transaction=calls.PackManagerStage.Invoke(session,"update",Environment.GetEnvironmentVariable("CONFECTORY_PIN_SOURCE")!,"Confectory.ElementView","0.1.0",false);
 var result=calls.PackManagerApply.Invoke(session,transaction,"linux");Console.WriteLine(string.Join("|",result));if(result[0]!="applied")return 1;
}
finally{calls.PackManagerClose.Invoke(session);}
return 0;
''')
env = os.environ.copy()
env.update(CONFECTORY_SELF_PROJECT=str(root/'engine/project.cpack'), CONFECTORY_PIN_SOURCE=str(repo/'packs/element-view/pack.cpack'), CONFECTORY_ELEMENT_AUTHORING_HOST=str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'), CONFECTORY_AUTHORING_TIMEOUT_MS='900000')
subprocess.run([dotnet, str(cli), 'run', str(root/'pin-tool/project.cpack'), 'portable'], env=env, check=True)
report = subprocess.run([dotnet, str(cli), 'build', str(root/'engine/project.cpack'), 'linux'], env=env, capture_output=True, text=True, check=True)
json.loads(report.stdout)
(root/'editor-A.json').write_text(report.stdout)
print(f'Prepared {root}; run self_edit_x11_spotcheck.py {root}/editor-A.json {root}')
