"""Validate portable package data and run its real manifest command in a temp root."""
import hashlib,json,os,pathlib,subprocess,sys,tempfile,zipfile
import jsonschema
from mcp_client import Client

repo=pathlib.Path(sys.argv[1]).resolve();protected=[repo/'.agents/plugins/marketplace.json',repo/'.codex/config.toml'];before={p:p.read_bytes() if p.is_file() else None for p in protected}
with tempfile.TemporaryDirectory(prefix='confectory-mcp-package-') as temp:
 root=pathlib.Path(temp);archive=root/'plugin.zip';result=subprocess.run([sys.executable,str(repo/'tools/package_mcp_plugin.py'),'--output',str(archive)],check=True,capture_output=True,text=True);receipt=json.loads(result.stdout);assert not receipt['installed'] and not receipt['marketplaceRegistered']
 with zipfile.ZipFile(archive) as z:
  names=z.namelist();assert len(names)==len(set(names)) and all(n.startswith('confectory/') and '..' not in pathlib.PurePosixPath(n).parts and not n.startswith('/') for n in names);z.extractall(root)
 plugin=root/'confectory';manifest=json.loads((plugin/'plugin.json').read_text());mcp=json.loads((plugin/'mcp.json').read_text())
 for name,data in [('plugin',manifest),('mcp',mcp)]:
  schema=json.loads((repo/'tests/protocol/schemas'/(name+'.schema.json')).read_text());jsonschema.Draft202012Validator.check_schema(schema);jsonschema.validate(data,schema)
 skill=plugin/manifest['extensions']['com.openai']['onboardingSkill'];assert skill.resolve().is_relative_to(plugin) and skill.is_file()
 record=json.loads((plugin/'package-receipt.json').read_text());assert all(hashlib.sha256((plugin/name).read_bytes()).hexdigest()==digest for name,digest in record['files'].items())
 server=mcp['mcpServers']['confectory'];assert server['type']=='stdio' and server['command']=='dotnet';cwd=server['cwd'].replace('${PLUGIN_ROOT}',str(plugin));command=[server['command'],*server['args']];assert (pathlib.Path(cwd)/server['args'][0]).is_file()
 env=os.environ.copy();env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env.get('PATH','');(root/'data').mkdir();env['XDG_DATA_HOME']=str(root/'data')
 with Client(repo,root/'unused',env,command=command,cwd=cwd) as client:
  assert len(client.request('tools/list')['tools'])==4;result,error=client.call('confectory_instances');assert error and result['code']=='engine_not_running'
 assert all((p.read_bytes() if p.is_file() else None)==raw for p,raw in before.items())
 print('PASS MCP portable official-schema snapshots/package hashes/real manifest command; no installation or marketplace registration',flush=True)
