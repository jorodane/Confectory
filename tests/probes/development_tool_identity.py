"""Compile the shipped Open body with owned metadata calls and both OS case policies.
This exercises the real ownership guard; it is not native Windows filesystem QA.
"""
import os, pathlib, subprocess, sys, tempfile
repo=pathlib.Path(sys.argv[1]).resolve();root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-tool-identity-'))
body=(repo/'packs/development-tools/Open.csbody').read_text()
(root/'probe.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>')
source=r'''
using System.Text.Json.Nodes;
class Probe {
 static class OperatingSystem { public static bool Windows; public static bool IsWindows()=>Windows; }
 class Calls {
  public string Manifest="Owned::ProjectManifest",Kind="project",File="project.cproj"; public int Closed;
  public Func<string,string,string,string> OpenView=(_,_,_)=>"view";
  public Func<string,string> Draft=_=>"draft";
  public Func<string,string[]> List=>_=>new[]{Manifest};
  public Func<string,string,string[]> Read=>(_,_)=>new[]{Manifest,Kind,File};
  public Func<string,string[],string[],string[],string[]> Commit=(_,_,_,_)=>new[]{"applied"};
  public Action<string> CloseView=>_=>Closed++;
 }
 static string Open(Calls calls,string project,string projectId,string namespaceId,string owner,string context) {
 BODY
 }
 static int Main(string[] args) {
  string project=Path.Combine(args[0],"project.cproj");int checks=0;
  foreach(bool windows in new[]{false,true}) {
   OperatingSystem.Windows=windows;
   foreach(var row in new[]{("Owned::ProjectManifest","project","project.cproj",true),
    ("Owned::ProjectManifest","project","PROJECT.CPROJ",windows),
    ("Foreign::ProjectManifest","project","project.cproj",false),
    ("Owned::ProjectManifest","object","project.cproj",false),
    ("Owned::ProjectManifest","project","other.cproj",false),
    ("Owned::ProjectManifest","project","../project.cproj",false)}) {
    var calls=new Calls{Manifest=row.Item1,Kind=row.Item2,File=row.Item3};bool accepted=false;
    try{Open(calls,project,"owned-project","Owned","owner","editor");accepted=true;}catch(ArgumentException){}
    if(accepted!=row.Item4||(!accepted&&calls.Closed!=1))throw new Exception($"Identity policy failed: windows={windows}, file={row.Item3}, accepted={accepted}");checks++;
   }
  }
  Console.WriteLine($"PASS {checks} production ownership guard cases (Windows policy simulated; no native Windows run)");return 0;
 }
}
'''.replace('BODY',body)
(root/'Program.cs').write_text(source)
result=subprocess.run([os.environ.get('CONFECTORY_DOTNET','dotnet'),'run','--project',str(root/'probe.csproj'),'--configuration','Release','--',str(root/'owned')],text=True,capture_output=True,timeout=90)
print(result.stdout+result.stderr,end='');print('ARTIFACT '+str(root));sys.exit(result.returncode)
