"""Run the compiled target's integrity gate against preserved good and bad real bundles."""
import json,os,pathlib,subprocess,sys,tempfile
if len(sys.argv)!=4:raise SystemExit('usage: verify_browser_bundle.py TARGET_DLL GOOD_REPORT BAD_REPORT')
tool=pathlib.Path(sys.argv[1]).resolve()
good=str(pathlib.Path(json.load(open(sys.argv[2]))['output'])/'site')
bad=str(pathlib.Path(json.load(open(sys.argv[3]))['output'])/'site')
with tempfile.TemporaryDirectory(prefix='confectory-bundle-gate-') as temporary:
 root=pathlib.Path(temporary)
 (root/'Check.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings></PropertyGroup></Project>')
 (root/'NuGet.Config').write_text('<configuration><packageSources><clear/></packageSources></configuration>')
 (root/'Program.cs').write_text('''using System.Reflection;
System.Runtime.Loader.AssemblyLoadContext.Default.Resolving+=(context,name)=>{string path=Path.Combine(Path.GetDirectoryName(args[0])!,name.Name+".dll");return File.Exists(path)?context.LoadFromAssemblyPath(path):null;};
var assembly=Assembly.LoadFrom(args[0]);var method=assembly.GetTypes().SelectMany(t=>t.GetMethods(BindingFlags.NonPublic|BindingFlags.Static)).Single(m=>m.Name.Contains("g__VerifyBundle|")&&m.GetParameters().Length==1);
method.Invoke(null,new object[]{args[1]});Console.WriteLine("PASS preserved good bundle");
try{method.Invoke(null,new object[]{args[2]});throw new Exception("Broken bundle was incorrectly accepted");}catch(TargetInvocationException error) when(error.InnerException is IOException failure&&failure.Message.Contains("integrity mismatch")){Console.WriteLine("PASS preserved bad bundle rejected: "+failure.Message);}
''')
 dotnet=os.environ.get('CONFECTORY_DOTNET','dotnet')
 subprocess.run([dotnet,'run','--project',str(root/'Check.csproj'),'-c','Release','--',str(tool),good,bad],check=True)
