"""Retire a real authoring stream at its bounded frame limit through Call.csbody.

Run with CONFECTORY_DOTNET and CONFECTORY_ELEMENT_AUTHORING_HOST. The harness
compiles the actual caller body and uses a disposable local project.
"""
import os
from pathlib import Path
import subprocess
import tempfile

repo = Path(__file__).resolve().parents[2]
source = (repo / 'packs/schema-editing/Call.csbody').read_text()
with tempfile.TemporaryDirectory(prefix='confectory-authoring-rotation-') as tmp:
    root = Path(tmp)
    (root / 'probe.csproj').write_text(
        '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework>'
        '<OutputType>Exe</OutputType><ImplicitUsings>enable</ImplicitUsings>'
        '<Nullable>enable</Nullable></PropertyGroup></Project>')
    (root / 'project.cpack').write_text(
        'project Test.Rotation version "1" { standalone false; '
        'element Info schema "Info.celem"; element Record object "Record.celem"; }')
    (root / 'Info.celem').write_text('schema Test.Rotation::Info { field Count single general long; }')
    (root / 'Record.celem').write_text(
        'object Test.Rotation::Record { use schema Test.Rotation::Info; data Count = 2; }')
    program = r'''
using System.Text.Json.Nodes;
using System.Diagnostics;
class Probe {
 static string Call(string operation,string payload) {
 BODY
 }
 static void Need(bool condition,string detail){if(!condition)throw new Exception(detail);}
 static void Main(string[] args){
  string path=Path.GetFullPath(args[0]),folder=Path.GetDirectoryName(path)!;
  string info=Path.Combine(folder,"Info.celem"),record=Path.Combine(folder,"Record.celem");
  int streamed=0,oneShot=0;
  AppDomain.CurrentDomain.SetData("Confectory.Performance.Record",(Action<string,string,double,double>)((stage,op,ms,page)=>{
   if(op=="inspectEffective"){if(stage=="authoring-stream")streamed++;if(stage=="authoring-process")oneShot++;}
  }));
  object[]? pool=null;
  int previousPid=0;
  try{
   for(int i=0;i<257;i++){
    if(i==128)File.WriteAllText(info,"schema Test.Rotation::Info { field Count single general long; field Note single general string; }");
    var request=new JsonObject{["project"]=path,["manifest"]=File.ReadAllText(path),["id"]="Test.Rotation::Record",["kind"]="object",["text"]=File.ReadAllText(record),["drafts"]=new JsonArray(),["schemaView"]=true,["schemaReuseProof"]=true};
    var result=JsonNode.Parse(Call("inspectEffective",request.ToJsonString()))!;
    Need(result["effective"]?["status"]?.ToString()=="available","Effective schema unavailable at frame "+i);
    if(i>=128)Need(result.ToJsonString().Contains("Note",StringComparison.Ordinal),"Fresh external declaration missing");
    pool=(object[])AppDomain.CurrentDomain.GetData("Confectory.SchemaEditing.ReadPool")!;
    int pid=((Process)pool[0]).Id;
    Need(pool[4] is int count&&count==i%128+1,"Frame budget not tracked");
    if(i>0)Need((pid!=previousPid)==(i%128==0),"Unexpected stream rotation at frame "+i);
    previousPid=pid;
   }
   Need(streamed==257&&oneShot==0,$"Expected no failed-frame fallback, stream={streamed}, one-shot={oneShot}");
   Console.WriteLine("PASS 257 real frames; two bounded rotations; externally changed schema reread; zero one-shot fallback");
  }finally{
   if(pool?[0] is Process process){if(!process.HasExited){process.Kill(true);process.WaitForExit();}process.Dispose();}
  }
 }
}
'''
    (root / 'Program.cs').write_text(program.replace('BODY', source))
    env = dict(os.environ, DOTNET_CLI_HOME=str(root / 'dotnet-home'), DOTNET_SKIP_FIRST_TIME_EXPERIENCE='1',
               DOTNET_CLI_TELEMETRY_OPTOUT='1', DOTNET_GENERATE_ASPNET_CERTIFICATE='false',
               DOTNET_NOLOGO='1')
    subprocess.run([os.environ['CONFECTORY_DOTNET'], 'run', '--project',
                    str(root / 'probe.csproj'), '-c', 'Release', '--',
                    str(root / 'project.cpack')], env=env, check=True)
