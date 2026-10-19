"""Bundle a complete local marketplace source; never installs or registers it."""
import argparse,hashlib,json,pathlib,shutil,tempfile,zipfile

parser=argparse.ArgumentParser()
parser.add_argument('--output',required=True,type=pathlib.Path)
args=parser.parse_args()
repo=pathlib.Path(__file__).resolve().parents[1];built=repo/'targets/mcp-host/bin/Release/net10.0'
files=['Confectory.Mcp.dll','Confectory.Mcp.deps.json','Confectory.Mcp.runtimeconfig.json']
if not all((built/name).is_file() for name in files):raise SystemExit('Build targets/mcp-host/Confectory.Mcp.csproj with the existing .NET 10 SDK first. Nothing was installed.')
output=args.output.resolve();output.parent.mkdir(parents=True,exist_ok=True)
catalog=json.loads((repo/'plugins/marketplace.example.json').read_text())
if len(catalog['plugins'])!=1:raise SystemExit('Exactly one development plugin is required.')
entry=catalog['plugins'][0];source=entry['source'];relative=pathlib.PurePosixPath(source['path'])
if source['source']!='local' or not source['path'].startswith('./') or '\\' in source['path'] or relative.is_absolute() or '..' in relative.parts:raise SystemExit('A local marketplace source within its root is required.')
with tempfile.TemporaryDirectory(prefix='confectory-plugin-package-') as temp:
 root=pathlib.Path(temp)/'confectory-development';plugin=root/relative
 if not plugin.resolve().is_relative_to(root.resolve()) or plugin==root:raise SystemExit('Plugin source must stay within its marketplace root.')
 shutil.copytree(repo/'plugins/confectory',plugin)
 manifest=json.loads((plugin/'plugin.json').read_text())
 if entry['name']!=manifest['name']:raise SystemExit('Marketplace entry and plugin manifest must identify the same plugin.')
 (plugin/'server').mkdir()
 for name in files:shutil.copyfile(built/name,plugin/'server'/name)
 marketplace=root/'.agents/plugins/marketplace.json';marketplace.parent.mkdir(parents=True);shutil.copyfile(repo/'plugins/marketplace.example.json',marketplace)
 shutil.copyfile(repo/'plugins/MARKETPLACE.md',root/'README.md')
 receipt={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file()}
 (root/'package-receipt.json').write_text(json.dumps(dict(version=manifest['version'],runtime='net10.0',marketplace='.agents/plugins/marketplace.json',plugin=relative.as_posix(),files=receipt),indent=2)+'\n')
 with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
  for p in sorted(root.rglob('*')):
   if p.is_file():archive.write(p,p.relative_to(root.parent).as_posix())
print(json.dumps(dict(path=str(output),sha256=hashlib.sha256(output.read_bytes()).hexdigest(),marketplaceRoot='confectory-development',pluginVersion=manifest['version'],installed=False,marketplaceRegistered=False)))
