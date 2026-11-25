"""Exercise the native host's platform-neutral file writer (not WebView2 itself).

Run from a checkout with CONFECTORY_DOTNET pointing to the .NET 10 SDK.
"""
import os, pathlib, shutil, subprocess, tempfile

repo=pathlib.Path(__file__).resolve().parents[2]
dotnet=os.environ.get('CONFECTORY_DOTNET','dotnet')
with tempfile.TemporaryDirectory(prefix='confectory-performance-writer-') as root:
    root=pathlib.Path(root)
    shutil.copy2(repo/'targets/webview-windows/PerformanceCapture.cs',root/'PerformanceCapture.cs')
    (root/'probe.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>')
    (root/'Program.cs').write_text('''using System.Diagnostics;
using System.Text.Json;
var path=Path.Combine(Environment.CurrentDirectory,"webview.jsonl");
Environment.SetEnvironmentVariable("CONFECTORY_PERFORMANCE_RENDERER_FILE",path);
Environment.SetEnvironmentVariable("CONFECTORY_PERFORMANCE_EPOCH",Stopwatch.GetTimestamp().ToString());
Environment.SetEnvironmentVariable("CONFECTORY_PERFORMANCE",null);
using(var disabled=new PerformanceCapture()){if(disabled.Enabled)throw new Exception("default enabled");disabled.Mark("webview-message","request",disabled.Start());}
if(File.Exists(path))throw new Exception("default file created");
Environment.SetEnvironmentVariable("CONFECTORY_PERFORMANCE","1");
using(var capture=new PerformanceCapture()){
 if(!capture.Enabled)throw new Exception("explicit capture disabled");
 capture.Mark("PRIVATE_SENTINEL","request",capture.Start());
 capture.Mark("webview-message","PRIVATE_SENTINEL",capture.Start());
 for(int i=0;i<4200;i++)capture.Mark("webview-message","request",capture.Start());
}
var lines=File.ReadAllLines(path);if(lines.Length!=4096||!lines[^1].Contains("capture-limit")||lines.Any(l=>l.Contains("PRIVATE_SENTINEL")))throw new Exception("record privacy/budget failed");
foreach(string line in lines){using var record=JsonDocument.Parse(line);if(record.RootElement.EnumerateObject().Count()!=4||!record.RootElement.GetProperty("elapsedMs").TryGetDouble(out _))throw new Exception("unexpected record");}
using(var duplicate=new PerformanceCapture())if(duplicate.Enabled)throw new Exception("existing diagnostic file overwritten");
Console.WriteLine("PASS native host writer: default off, numeric-only, bounded, no overwrite");''')
    subprocess.run([dotnet,'run','--project',str(root/'probe.csproj'),'-c','Release'],cwd=root,check=True,timeout=120)
