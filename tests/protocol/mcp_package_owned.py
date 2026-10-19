"""Resolve a bundled marketplace and run its real manifest after relocation."""
import hashlib,json,os,pathlib,shutil,subprocess,sys,tempfile,zipfile
import jsonschema
from mcp_client import Client

repo=pathlib.Path(sys.argv[1]).resolve();protected=[repo/'.agents/plugins/marketplace.json',repo/'.codex/config.toml'];before={p:p.read_bytes() if p.is_file() else None for p in protected}
with tempfile.TemporaryDirectory(prefix='confectory-mcp-package-') as temp:
 root=pathlib.Path(temp);archive=root/'source.zip';result=subprocess.run([sys.executable,str(repo/'tools/package_mcp_plugin.py'),'--output',str(archive)],check=True,capture_output=True,text=True);receipt=json.loads(result.stdout);assert not receipt['installed'] and not receipt['marketplaceRegistered']
 with zipfile.ZipFile(archive) as z:
  names=z.namelist();assert len(names)==len(set(names)) and all('\\' not in n and '..' not in pathlib.PurePosixPath(n).parts and not n.startswith('/') for n in names);z.extractall(root/'extracted')
 catalogs=list((root/'extracted').glob('*/.agents/plugins/marketplace.json'));assert len(catalogs)==1;marketplace_root=catalogs[0].parents[2]
 def resolve_plugin(directory):
  catalog=json.loads((directory/'.agents/plugins/marketplace.json').read_text());assert catalog['name']=='confectory-development' and catalog['interface']['displayName'];assert len(catalog['plugins'])==1
  entry=catalog['plugins'][0];assert entry['policy']==dict(installation='AVAILABLE',authentication='ON_INSTALL') and entry['category']=='Productivity';assert entry['source']['source']=='local';path=entry['source']['path'];assert path.startswith('./') and '..' not in pathlib.PurePosixPath(path).parts
  plugin=(directory/path).resolve();assert plugin.is_relative_to(directory.resolve()) and plugin!=directory.resolve();assert entry['name']==json.loads((plugin/'plugin.json').read_text())['name'];return plugin
 plugin=resolve_plugin(marketplace_root);manifest=json.loads((plugin/'plugin.json').read_text());mcp=json.loads((plugin/'mcp.json').read_text())
 for name,data in [('plugin',manifest),('mcp',mcp)]:
  schema=json.loads((repo/'tests/protocol/schemas'/(name+'.schema.json')).read_text());jsonschema.Draft202012Validator.check_schema(schema);jsonschema.validate(data,schema)
 skill=plugin/manifest['extensions']['com.openai']['onboardingSkill'];assert skill.resolve().is_relative_to(plugin) and skill.is_file()
 record=json.loads((marketplace_root/'package-receipt.json').read_text());assert record['version']==manifest['version']==receipt['pluginVersion'];assert record['marketplace']=='.agents/plugins/marketplace.json' and (marketplace_root/record['plugin']).resolve()==plugin
 assert set(record['files'])=={p.relative_to(marketplace_root).as_posix() for p in marketplace_root.rglob('*') if p.is_file() and p.name!='package-receipt.json'};assert all(hashlib.sha256((marketplace_root/name).read_bytes()).hexdigest()==digest for name,digest in record['files'].items())
 assert not (marketplace_root/'.codex/config.toml').exists() and not (plugin/'marketplace.example.json').exists()
 runtime=json.loads((plugin/'server/Confectory.Mcp.runtimeconfig.json').read_text())['runtimeOptions']['framework'];assert runtime['name']=='Microsoft.NETCore.App' and runtime['version'].startswith('10.')
 env=os.environ.copy();env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env.get('PATH','');(root/'data').mkdir();env['XDG_DATA_HOME']=str(root/'data')
 def run_manifest(directory):
  server=json.loads((directory/'mcp.json').read_text())['mcpServers']['confectory'];assert server['type']=='stdio' and server['command']=='dotnet';cwd=server['cwd'].replace('${PLUGIN_ROOT}',str(directory));command=[server['command'],*server['args']];assert (pathlib.Path(cwd)/server['args'][0]).is_file()
  with Client(repo,root/'unused',env,command=command,cwd=cwd) as client:
   assert len(client.request('tools/list')['tools'])==4;result,error=client.call('confectory_instances');assert error and result['code']=='engine_not_running'
 run_manifest(plugin)
 moved=root/'relocated source with spaces';shutil.copytree(marketplace_root,moved);run_manifest(resolve_plugin(moved))
 # A host may copy only the plugin into its cache; no catalog-root dependency.
 standalone=root/'isolated plugin copy';shutil.copytree(plugin,standalone);run_manifest(standalone)
 assert all((p.read_bytes() if p.is_file() else None)==raw for p,raw in before.items())
 evidence=dict(marketplaceRoot=marketplace_root.name,sourcePath=json.loads(catalogs[0].read_text())['plugins'][0]['source']['path'],catalogResolvesBundledPlugin=True,officialPortableSchemaSnapshots=True,allBundledHashes=True,realManifestCommand=True,relocatedRootWithSpaces=True,isolatedPluginCopy=True,requiredRuntime=runtime,actualChatGPTApp=False,installed=False,marketplaceRegistered=False,userConfigChanged=False)
 pathlib.Path('/workspace/scratch/confectory-mcp-marketplace-package.json').write_text(json.dumps(evidence,indent=2)+'\n')
 print('PASS MCP portable official-schema snapshots/package hashes/real manifest command; marketplace root/source path/relocation; no installation or marketplace registration '+json.dumps(evidence),flush=True)
