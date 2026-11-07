"""Execute extracted production bodies with a controlled pre-CommitPlan race.
The separate pack consumer and engine UI tests cover actual DSL/provider wiring.
"""
import pathlib,sys,tempfile,subprocess,os,json,hashlib
r=pathlib.Path(sys.argv[1]).resolve();case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-description-final-cas-'))
paths={'DELETIONS_BODY':'packs/project-resources/DeletionRecords.csbody','LAYOUT_BODY':'packs/project-resources/Layout.csbody','RESOURCE_BODY':'packs/project-resources/Request.csbody','SNAPSHOT_BODY':'packs/file-stream/BoundedSnapshot.csbody','PLAN_BODY':'packs/file-stream/CommitPlan.csbody','WRITE_BODY':'packs/file-stream/WriteAtomic.csbody','LEASE_BODY':'packs/file-stream/LeasePath.csbody'}
(case/'probe.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>')
source=(r/'tests/fixtures/project-resources/DescriptionsCAS.cs').read_text()
for token,path in paths.items():source=source.replace(token,(r/path).read_text())
legacy=subprocess.check_output(['git','show','cc0beb9801f23f5e479a429ab721e207eb62f360:packs/project-resources/Layout.csbody'],cwd=r,text=True);source=source.replace('OLD_LAYOUT',legacy);(case/'Program.cs').write_text(source)
result=subprocess.run([os.environ.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'),'run','--project',str(case/'probe.csproj'),'-c','Release','-p:UseSharedCompilation=false','--',str(case/'owned cases')],cwd=r)
(case/'evidence.json').write_text(json.dumps(dict(legacyCommit='cc0beb9801f23f5e479a429ab721e207eb62f360',legacySha256=hashlib.sha256(legacy.encode()).hexdigest(),actualBodies={path:hashlib.sha256((r/path).read_text().encode()).hexdigest()for path in paths.values()},controlledPreCommitDependency=True,actualPackWiring=False,actualWindows=False,passed=result.returncode==0),indent=2)+'\n')
print('RESOURCE_FINAL_CAS_FIXTURE',case,flush=True);raise SystemExit(result.returncode)
