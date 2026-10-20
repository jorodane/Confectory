"""Portable tests of the production native URL/open guard, plus optional pinned schema.
No OS browser, callback server, account, credentials or OAuth is used.
"""
import json,os,pathlib,subprocess,sys,tempfile
repo=pathlib.Path(sys.argv[1]).resolve();root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-browser-guard-'));dotnet=os.environ.get('CONFECTORY_DOTNET','dotnet')
(root/'guard.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable><TreatWarningsAsErrors>true</TreatWarningsAsErrors></PropertyGroup><ItemGroup><Compile Include="'+str(repo/'targets/webview-windows/CodexBrowserLogin.cs').replace('&','&amp;').replace(chr(34),'&quot;')+'" Link="CodexBrowserLogin.cs" /></ItemGroup></Project>')
(root/'Program.cs').write_text('''using Confectory.WebView;
string good="https://auth.openai.com/oauth/authorize?response_type=code&client_id=owned-fixture&redirect_uri=http%3A%2F%2F127.0.0.1%3A1455%2Fauth%2Fcallback&state=owned-state&code_challenge="+new string('A',43)+"&code_challenge_method=S256";
if(!CodexBrowserLogin.Allowed(good))throw new Exception("Valid official browser URL rejected");
string[] bad={good.Replace("https:","http:"),good.Replace("auth.openai.com","auth.openai.com.evil.invalid"),good.Replace("127.0.0.1","remote.fixture.invalid"),good.Replace("127.0.0.1","127.0.0.2"),good.Replace("%3A1455","%3A0"),good.Replace("%2Fauth%2Fcallback","%2Fother"),good.Replace("S256","plain"),good+"&state=duplicate",good+"#fragment",good.Replace("auth.openai.com","user@auth.openai.com"),"file:///tmp/fixture","javascript:alert(1)","https://auth.openai.com/oauth/authorize"};
int starts=0;foreach(string value in bad)if(CodexBrowserLogin.TryOpen(value,_=>starts++))throw new Exception("Unsafe browser URL opened");if(starts!=0)throw new Exception("Denied URLs reached OS launcher");
if(CodexBrowserLogin.TryOpen(good,_=>throw new System.ComponentModel.Win32Exception(2)))throw new Exception("OS launch failure hidden");
if(!CodexBrowserLogin.TryOpen(good,_=>starts++)||starts!=1)throw new Exception("Explicit launch retry failed");
if(!CodexBrowserLogin.TryOpen("https://auth.openai.com/codex/device",_=>starts++)||starts!=2)throw new Exception("Device fallback page denied");
string opened="";if(!CodexBrowserLogin.TryOpen(good+"&extra=\\\"quoted\\\"",value=>opened=value)||opened.Contains('\\\"'))throw new Exception("OS launcher received unescaped URI quotes");
Console.WriteLine("PASS production native browser URL allowlist, zero denied dispatch, OS failure and explicit retry; simulated OS launcher");''')
result=subprocess.run([dotnet,'run','--project',str(root/'guard.csproj'),'-c','Release','--nologo'],cwd=root,env=os.environ.copy(),capture_output=True,text=True,timeout=90);assert result.returncode==0,result.stdout+result.stderr;print(result.stdout.strip())
if len(sys.argv)>2:
 import jsonschema
 schema_dir=pathlib.Path(sys.argv[2]);params=json.loads(next(schema_dir.rglob('LoginAccountParams.json')).read_text());response=json.loads(next(schema_dir.rglob('LoginAccountResponse.json')).read_text())
 for kind in ['chatgpt','chatgptDeviceCode']:jsonschema.validate({'type':kind},params)
 jsonschema.validate({'type':'chatgpt','loginId':'owned-login','authUrl':'https://auth.openai.com/oauth/authorize'},response)
 if len(sys.argv)>3:
  rows=[json.loads(line) for line in pathlib.Path(sys.argv[3]).read_text().splitlines()];calls=[row['params'] for row in rows if row['method']=='account/login/start'];assert calls
  for call in calls:jsonschema.validate(call,params)
 print('PASS pinned generated official browser/device schema; no actual login')
