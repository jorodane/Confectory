"""Compile the production pure planner, check TOML/argv isolation and optional real CLI.
The opt-in CLI probe denies child network syscalls and uses an empty owned profile;
only initialize/config/read are sent. Never credentials, login, models or inference.
"""
import hashlib,json,os,pathlib,re,selectors,shutil,subprocess,sys,tempfile,time,tomllib
repo=pathlib.Path(sys.argv[1]).resolve();dotnet=os.environ.get('CONFECTORY_DOTNET','dotnet')
root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-plugin-plan-'))
(root/'plan.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable><TreatWarningsAsErrors>true</TreatWarningsAsErrors></PropertyGroup></Project>')
body=(repo/'packs/agent-codex/PluginIsolation.csbody').read_text()
(root/'Program.cs').write_text('string Plan(string effective){\n'+body+'''
}
if(args.Length>0&&args[0]=="--argv"){Console.WriteLine(System.Text.Json.JsonSerializer.Serialize(args.Skip(1)));return;}
if(args.Length>0&&args[0]=="--launch-argv"){
 var plan=System.Text.Json.Nodes.JsonNode.Parse(Plan(Console.ReadLine()!))!;
 var start=new System.Diagnostics.ProcessStartInfo(Environment.ProcessPath!){UseShellExecute=false,RedirectStandardOutput=true};
 start.ArgumentList.Add(System.Reflection.Assembly.GetExecutingAssembly().Location);start.ArgumentList.Add("--argv");start.ArgumentList.Add("-c");start.ArgumentList.Add(plan["argument"]!.ToString());
 using var child=System.Diagnostics.Process.Start(start)!;Console.Write(child.StandardOutput.ReadToEnd());child.WaitForExit();if(child.ExitCode!=0)throw new Exception("Owned argv child failed");return;
}
while(Console.ReadLine() is string line){try{Console.WriteLine(Plan(line));}catch(Exception e){Console.WriteLine(System.Text.Json.JsonSerializer.Serialize(new{error=e.GetType().Name}));}}
''')
built=subprocess.run([dotnet,'build',str(root/'plan.csproj'),'-c','Release','--nologo'],text=True,capture_output=True,timeout=90);assert built.returncode==0,built.stdout+built.stderr
keys=['owned.a@fixture','owned-quote"\\name-한글🧁@fixture','owned-injection"},features={shell_tool=true},"@fixture','--disable apps -c x@fixture']
sample={key:{'enabled':True} for key in keys};sample['unified-computer-use@openai-bundled']={'enabled':False};sample['missing-enabled@fixture']={}
inputs=[sample,{},None,[],{'bad\nkey@fixture':{'enabled':True}},{'bad\x00key':{'enabled':True}},{'':{'enabled':True}},{'k'*1025:{'enabled':True}},{str(i):{'enabled':True} for i in range(129)},{str(i)+'x'*1000:{'enabled':True} for i in range(12)},{'disabled@fixture':{'enabled':False}},{'unconfirmed@fixture':{'enabled':'false'}}]
run=subprocess.run([dotnet,str(root/'bin/Release/net10.0/plan.dll')],input=''.join(json.dumps(value)+'\n' for value in inputs),text=True,capture_output=True,timeout=20);assert run.returncode==0,run.stderr
plans=[json.loads(line) for line in run.stdout.splitlines()];assert len(plans)==len(inputs) and all('error' not in x for x in plans),plans
first=plans[0];parsed=tomllib.loads(first['argument']);assert set(parsed)=={'plugins'};assert all(v=={'enabled':False} for v in parsed['plugins'].values());assert set(parsed['plugins'])==set(sample)
assert first['required'] is True and first['summary']=={'entries':len(sample),'enabledBundled':0,'enabledOther':len(keys),'unconfirmed':1,'bounded':True}
assert not plans[1]['required'] and not plans[2]['required'];assert plans[3]['required'] and plans[3]['summary']['bounded'] is False
for plan in plans[4:10]:assert plan['summary']['bounded'] is False and plan['argument']=='',plan
assert not plans[10]['required'] and plans[11]['required']
assert 'owned' not in json.dumps(first['summary']) and 'fixture' not in json.dumps(first['summary'])
# One ArgumentList item, without a shell: quotes, spaces, slashes and option-looking text
# must survive as data. TOML decodes only plugin enabled=false; no feature/option expansion.
argv=subprocess.check_output([dotnet,str(root/'bin/Release/net10.0/plan.dll'),'--launch-argv'],input=json.dumps(sample)+'\n',text=True)
assert json.loads(argv)==['-c',first['argument']]
record={'productionPlannerCompiled':True,'tomlQuotedKeysAndExactPluginOnlyScope':True,'singleArgvItemNoShell':True,'controlsEmptyMalformedAndArgumentBudgetRejected':True,'safeCountSummary':True,'platform':sys.platform,'windowsExecution':False,'actualLoginOrInference':False}
if len(sys.argv)>2:
 assert sys.platform=='linux'
 source=(repo/'tests/protocol/codex_offline_account.py').read_text();scope={'__file__':str(repo/'tests/protocol/codex_offline_account.py')};exec(source[:source.index('assert sys.platform')],scope);deny=scope['deny_child_network']
 home=root/'owned-home';home.mkdir();scratch=root/'scratch';scratch.mkdir();cfg=home/'config.toml'
 cfg.write_text(''.join('[plugins.'+json.dumps(k,ensure_ascii=False)+']\n'+('enabled = '+str(v['enabled']).lower()+'\n' if 'enabled' in v else '') for k,v in sample.items()))
 original=cfg.read_bytes();env={'CODEX_HOME':str(home),'TMPDIR':str(scratch),'TMP':str(scratch),'TEMP':str(scratch),'PATH':'/usr/bin:/bin'}
 features=re.findall(r'"([a-z0-9_]+)"',re.search(r'string\[\] deniedFeatures=\{([^}]+)\}',(repo/'packs/agent-codex/Provider.csbody').read_text()).group(1))
 records=[]
 for label,extra in [('static-only',[]),('empty-table',['-c','plugins={}']),('production-table',['-c',first['argument']])]:
  args=[sys.argv[2],'app-server','--stdio','--strict-config','-c','web_search="disabled"','-c','cli_auth_credentials_store="ephemeral"']
  for feature in features:args+=['--disable',feature]
  args+=['-c','notify=[]','-c','plugins.unified-computer-use@openai-bundled.enabled=false']+extra
  with (root/'stderr').open('wb') as err:
   p=subprocess.Popen(args,env=env,cwd=scratch,preexec_fn=deny,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,start_new_session=True);selector=selectors.DefaultSelector();selector.register(p.stdout,selectors.EVENT_READ);pending=bytearray();methods=[]
   def rpc(i,method,params):
    methods.append(method);p.stdin.write((json.dumps({'id':i,'method':method,'params':params})+'\n').encode());p.stdin.flush();end=time.monotonic()+10
    while time.monotonic()<end:
     if not selector.select(max(0,end-time.monotonic())):raise TimeoutError('bounded-rpc-timeout')
     chunk=os.read(p.stdout.fileno(),65536)
     if not chunk:raise RuntimeError('stdio-ended')
     pending.extend(chunk);assert len(pending)<=1048576
     while b'\n' in pending:
      line,_,rest=pending.partition(b'\n');pending[:]=rest;reply=json.loads(line)
      if reply.get('id')==i:
       assert 'error' not in reply,'owned configuration rejected'
       return reply['result']
    raise TimeoutError('bounded-rpc-timeout')
   try:
    initialized=rpc(1,'initialize',{'clientInfo':{'name':'confectory','version':'0.1.0'},'capabilities':{'experimentalApi':True}});assert initialized['userAgent'].startswith('confectory/0.159.0-alpha.3 ')
    p.stdin.write(b'{"method":"initialized","params":{}}\n');p.stdin.flush();effective=rpc(2,'config/read',{'includeLayers':False})['config']['plugins'];enabled=sum(value.get('enabled') is not False for value in effective.values())
    assert all(key in effective for key in sample);assert cfg.read_bytes()==original and not (home/'auth.json').exists();records.append({'case':label,'enabledEntries':enabled,'methods':methods,'configUnchanged':True,'authFileAbsent':True})
   finally:
    p.stdin.close()
    try:p.wait(timeout=2)
    except subprocess.TimeoutExpired:p.kill();p.wait(timeout=2)
    selector.close()
 assert records[0]['enabledEntries']>0 and records[1]['enabledEntries']>0 and records[2]['enabledEntries']==0,records
 record.update(officialPinnedLinuxCLI=records,childNetworkDenied=True)
shutil.rmtree(root);print(json.dumps(record,indent=2));print('PASS production plugin isolation TOML argv bounds and metadata checks')
