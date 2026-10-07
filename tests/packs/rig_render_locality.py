#!/usr/bin/env python3
"""Real owned-provider rebuild gate; never mutate repository packs."""
import json,os,pathlib,shutil,subprocess,tempfile
repo=pathlib.Path(__file__).resolve().parents[2]
with tempfile.TemporaryDirectory(prefix='confectory-rig-locality-') as folder:
 root=pathlib.Path(folder);consumer=root/'consumer';shutil.copytree(repo/'examples/rig-lab',consumer,ignore=shutil.ignore_patterns('.confectory'))
 policies={}
 for name,namespace in [('rig-motion','RigMotion'),('render-authoring','RenderAuthoring')]:
  owned=root/name;shutil.copytree(repo/'packs'/name,owned,ignore=shutil.ignore_patterns('.confectory'));policies[namespace]=owned
 project=consumer/'verify.cpack';text=project.read_text().replace('../../',str(repo)+'/')
 for namespace,owned in policies.items():text=text.replace(str(repo/'packs'/owned.name/'pack.cpack'),str(owned/'pack.cpack'))
 project.write_text(text)
 def build():
  result=subprocess.run([os.environ['CONFECTORY_DOTNET'],str(repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(project),'linux'],capture_output=True,text=True);assert result.returncode==0,result.stdout+result.stderr;return json.loads(result.stdout)
 first=build();run=subprocess.run(first['run'],capture_output=True,text=True);assert run.returncode==0,run.stdout+run.stderr
 for namespace,owned in policies.items():
  body=owned/'Command.csbody';body.write_text(body.read_text()+'\n// owning '+namespace+' policy locality gate\n');changed=build();stats=changed['statistics'];assert stats['compiledImplementations']==['Confectory.'+namespace+'::CommandBody'],stats;assert stats['compiledContracts']==[],stats;print(namespace+' provider-only implementation, zero contracts PASS',flush=True)
