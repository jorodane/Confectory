#!/usr/bin/env python3
"""Measure the actual editor-home with isolated owned source/cache copies.
Run separately for each compiler revision; evidence never enters the repository.
"""
import argparse,json,os,platform,re,shutil,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('cli');p.add_argument('evidence');p.add_argument('--target',default='linux');a=p.parse_args()
repo=Path(__file__).resolve().parents[2];root=Path(a.evidence).resolve()
if root.exists():raise SystemExit('Use a new evidence directory; preserve earlier runs')
root.mkdir(parents=True);home=root/'editor-home';owned=root/'base-ui'
ignore=shutil.ignore_patterns('.confectory','bin','obj','__pycache__')
shutil.copytree(repo/'examples/editor-home',home,ignore=ignore);shutil.copytree(repo/'packs/base-ui',owned,ignore=ignore)
project=home/'project.cpack';text=project.read_text()
def registry(m):
 path=(repo/'examples/editor-home'/m[2]).resolve()
 if m[1].split()[1]=='Confectory.BaseUI':path=owned/'pack.cpack'
 return m[1]+json.dumps(str(path))
project.write_text(re.sub(r'(registry\s+\S+\s+)"([^"]+)"',registry,text))
dotnet=os.environ['CONFECTORY_DOTNET'];results=[]
for scenario in ('cold','warm','implementation','contract'):
 if scenario=='implementation':
  # Change a selected BaseUI body without changing behavior.
  selected=sorted(k for k in report['implementationArtifacts']['Confectory.BaseUI']['implementations'])
  local=selected[0].split('::')[1];decl=(owned/(local+'.celem')).read_text()
  body=re.search(r'body common "([^"]+)"',decl)[1]
  with (owned/body).open('a') as f:f.write('\n// pack boundary measurement: implementation change\n')
 if scenario=='contract':
  # Rename a selected public parameter: real contract metadata change, same ABI types.
  # Implementations/imports remain compatible because parameter names are not call types.
  catalog=json.loads(Path(report['publicCatalog']).read_text())
  fn=next(x for x in catalog['functions'] if x['id'].startswith('Confectory.BaseUI::') and x['contract']['args'])
  arg=fn['contract']['args'][0];path=owned/(fn['id'].split('::')[1]+'.celem')
  source=path.read_text();old=arg['type']+' '+arg['name'];assert old in source
  path.write_text(source.replace(old,arg['type']+' '+arg['name']+'PackProbe',1))
 started=time.perf_counter();run=subprocess.run([dotnet,str(Path(a.cli).resolve()),'build',str(project),a.target],capture_output=True,text=True)
 elapsed=time.perf_counter()-started;(root/(scenario+'.json')).write_text(run.stdout);(root/(scenario+'.stderr')).write_text(run.stderr)
 if run.returncode:raise SystemExit(run.stdout+run.stderr)
 report=json.loads(run.stdout);st=report['statistics'];calls=st['targetInvocations']
 contracts={x['assembly'] for x in report['contractArtifacts'].values()};impls={v for x in report['implementationArtifacts'].values() for v in x['assemblies']}
 item=dict(scenario=scenario,seconds=round(elapsed,3),contractDlls=len(contracts),implementationDlls=len(impls),deployedDlls=len(list(Path(report['output']).glob('*.dll'))),compileContract=calls.get('compile-contract',0),compilePack=calls.get('compile-pack',0),link=calls.get('link',0),compiledPacks=st['compiledPacks'],reusedPacks=st['reusedPacks'],compiledContracts=st['compiledContracts'],reusedContractCount=len(st['reusedContracts']),artifactLayout=report.get('artifactLayout','element-v1'))
 results.append(item);print(json.dumps(item),flush=True)
 (root/'measurements.json').write_text(json.dumps(dict(host=platform.platform(),python=platform.python_version(),dotnet=dotnet,target=a.target,cli=str(Path(a.cli).resolve()),method='one sequential sample each; cold Confectory cache, OS/SDK caches retained; no runtime launch',results=results),indent=2)+'\n')
