"""Package already-built managed MCP files; never installs or registers a plugin."""
import argparse,hashlib,json,pathlib,shutil,tempfile,zipfile

parser=argparse.ArgumentParser()
parser.add_argument('--output',required=True,type=pathlib.Path)
args=parser.parse_args()
repo=pathlib.Path(__file__).resolve().parents[1];built=repo/'targets/mcp-host/bin/Release/net10.0'
files=['Confectory.Mcp.dll','Confectory.Mcp.deps.json','Confectory.Mcp.runtimeconfig.json']
if not all((built/name).is_file() for name in files):raise SystemExit('Build targets/mcp-host/Confectory.Mcp.csproj with the existing .NET 10 SDK first. Nothing was installed.')
output=args.output.resolve();output.parent.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='confectory-plugin-package-') as temp:
 root=pathlib.Path(temp)/'confectory';shutil.copytree(repo/'plugins/confectory',root)
 (root/'server').mkdir()
 for name in files:shutil.copyfile(built/name,root/'server'/name)
 receipt={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file()}
 (root/'package-receipt.json').write_text(json.dumps(dict(version='0.1.0',runtime='net10.0',files=receipt),indent=2)+'\n')
 with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
  for p in sorted(root.rglob('*')):
   if p.is_file():archive.write(p,p.relative_to(root.parent).as_posix())
print(json.dumps(dict(path=str(output),sha256=hashlib.sha256(output.read_bytes()).hexdigest(),installed=False,marketplaceRegistered=False)))
