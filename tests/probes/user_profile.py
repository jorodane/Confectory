"""Shipped display-profile storage using private fixture files; not an account/grant."""
import os,pathlib,subprocess,sys,tempfile
r=pathlib.Path(sys.argv[1]).resolve();root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-profile-'));(root/'probe.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>')
code=r'''
using System.Text.Json.Nodes;
class Probe{
 static string Hash(string t)=>Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(t))).ToLowerInvariant();
 class Calls{public int Reads;public Func<string,string[]> Snapshot;public Func<string,string[],string[],string[],string[]> Commit=(root,files,hashes,texts)=>{for(int i=0;i<files.Length;i++){string p=Path.Combine(root,files[i]);if((File.Exists(p)?Hash(File.ReadAllText(p)):"missing")!=hashes[i])return new[]{"conflict"};File.WriteAllText(p,texts[i]);}return new[]{"applied"};};public Calls(){Snapshot=p=>{Reads++;return File.Exists(p)?new[]{"exists",File.ReadAllText(p),Hash(File.ReadAllText(p))}:new[]{"missing","","missing"};};}}
 static string Invoke(Calls calls,string storage,string operation,string payload){BODY}
 static void Main(string[] a){string storage=a[0];Directory.CreateDirectory(storage);var calls=new Calls();int checks=0;JsonNode Call(string op,string input="{}")=>JsonNode.Parse(Invoke(calls,storage,op,input))!;void Check(bool v){if(!v)throw new Exception("profile "+checks);checks++;}void Denied(string input){bool deny=false;try{Call("save",input);}catch(Exception e)when(e is ArgumentException or InvalidOperationException or FormatException){deny=true;}Check(deny);}
 var fresh=Call("load");Check(fresh["status"]!.ToString()=="ready"&&fresh["revision"]!.ToString()=="missing"&&!File.Exists(Path.Combine(storage,"user-profile.json")));
 var value=fresh["value"]!.DeepClone();value["name"]="격리 표시 이름";value["introduction"]="Not an account";var input=new JsonObject{["revision"]=fresh["revision"]!.DeepClone(),["value"]=value};var saved=Call("save",input.ToJsonString());Check(saved["status"]!.ToString()=="ready");Check(Call("load")["value"]!["name"]!.ToString()=="격리 표시 이름");Denied(input.ToJsonString());input["revision"]=saved["revision"]!.DeepClone();
 foreach(var pair in new[]{("name",new string('x',41)),("title",new string('x',61)),("status",new string('x',121)),("introduction",new string('x',501)),("icon","data:text/html;base64,SGVsbG8=")}){var invalid=input.DeepClone();invalid["value"]![pair.Item1]=pair.Item2;Denied(invalid.ToJsonString());}
 var extra=input.DeepClone();extra["value"]!["accessToken"]="fixture";Denied(extra.ToJsonString());extra=input.DeepClone();extra["path"]="elsewhere";Denied(extra.ToJsonString());
 foreach(string icon in new[]{"data:image/webp;base64,AAAA","data:image/png;base64,AAAA","data:image/svg+xml;base64,AAAA",new string('x',129)}){var invalid=input.DeepClone();invalid["value"]!["icon"]=icon;Denied(invalid.ToJsonString());}
 var commit=calls.Commit;string file=Path.Combine(storage,"user-profile.json"),original=File.ReadAllText(file);calls.Commit=(_,_,_,_)=>new[]{"conflict"};Denied(input.ToJsonString());Check(File.ReadAllText(file)==original);calls.Commit=commit;
 File.WriteAllText(file,"invalid profile");Check(Call("load")["status"]!.ToString()=="unavailable");Denied(input.ToJsonString());Check(File.ReadAllText(file)=="invalid profile");File.WriteAllText(file,original);
 if(!OperatingSystem.IsWindows()){string aside=file+".owned";File.Move(file,aside);File.CreateSymbolicLink(file,aside);int reads=calls.Reads;Check(Call("load")["status"]!.ToString()=="unavailable"&&calls.Reads==reads);File.Delete(file);File.Move(aside,file);}
 Check(Call("load")["value"]!["name"]!.ToString()=="격리 표시 이름");Console.WriteLine($"PASS {checks} private display-profile persistence/CAS/bounds/image/symlink cases; no authentication or grant");}
}
'''.replace('BODY',(r/'packs/editor-home-model/UserProfile.csbody').read_text());(root/'Program.cs').write_text(code)
p=subprocess.run([os.environ.get('CONFECTORY_DOTNET','dotnet'),'run','--project',str(root/'probe.csproj'),'-c','Release','--',str(root/'owned')],capture_output=True,text=True,timeout=90);print(p.stdout+p.stderr,end='');print('ARTIFACT '+str(root));sys.exit(p.returncode)
