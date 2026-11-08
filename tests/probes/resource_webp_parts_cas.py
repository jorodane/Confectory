"""Actual production reader bodies; controlled final-read races, not user concurrency.
The UI/API fixture separately verifies engine/provider/observation wiring.
"""
import pathlib,sys,tempfile,subprocess,os,json,hashlib
r=pathlib.Path(sys.argv[1]).resolve();case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-webp-parts-cas-'))
paths={'DELETIONS_BODY':'packs/project-resources/DeletionRecords.csbody','LAYOUT_BODY':'packs/project-resources/Layout.csbody','RESOURCE_BODY':'packs/project-resources/Request.csbody','SNAPSHOT_BODY':'packs/file-stream/BoundedSnapshot.csbody','PLAN_BODY':'packs/file-stream/CommitPlan.csbody','WRITE_BODY':'packs/file-stream/WriteAtomic.csbody','LEASE_BODY':'packs/file-stream/LeasePath.csbody'}
(case/'probe.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>')
source=(r/'tests/fixtures/project-resources/WebPParts.cs').read_text()
for token,path in paths.items():source=source.replace(token,(r/path).read_text())
commit='e5ca3f1cd00f4e271e9f1d54159b341ff0cc57e4';legacy=subprocess.check_output(['git','show',commit+':packs/project-resources/Layout.csbody'],cwd=r,text=True);source=source.replace('OLD_LAYOUT',legacy);(case/'Program.cs').write_text(source)
result=subprocess.run([os.environ.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'),'run','--project',str(case/'probe.csproj'),'-c','Release','-p:UseSharedCompilation=false','--',str(case/'owned cases')],cwd=r)
(case/'evidence.json').write_text(json.dumps(dict(legacyCommit=commit,legacySha256=hashlib.sha256(legacy.encode()).hexdigest(),actualBodies={path:hashlib.sha256((r/path).read_text().encode()).hexdigest()for path in paths.values()},controlledFinalRead=True,actualPackWiring=False,actualWindows=False,passed=result.returncode==0),indent=2)+'\n')
print('RESOURCE_WEBP_PARTS_CAS_FIXTURE',case,flush=True);raise SystemExit(result.returncode)
