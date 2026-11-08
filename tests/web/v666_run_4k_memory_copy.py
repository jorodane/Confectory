"""Source/contract boundary for the isolated4K allocation change; execution tests cover decoding."""
import sys,pathlib,json,subprocess,hashlib,ast
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-run-4k-memory-delta.json').read_text());git=lambda*a:subprocess.check_output(['git',*a],cwd=r,text=True)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines())|set(git('ls-files','--others','--exclude-standard','--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed^set(d['productFiles'])
for n,h in d['productFiles'].items():assert hashlib.sha256((r/n).read_text().encode()).hexdigest()==h,n
name='packs/project-execution/Surface.csbody';s=(r/name).read_text();old=git('show',d['baseCommit']+':'+name)
# Original ownership, pipe reader/I/O budgets, cursor guards and final publication remain exact.
a='  byte[]? decoded4K=null;';start='  if(parts){';end='  if(frame["available"]'
assert s.split(a)[0]==old.split(start)[0]
start='  System.Text.Json.Nodes.JsonObject? resize=null;';assert s.split(start)[1]==old.split(start)[1]
start='   string encoded=frame["pixels"]';end='acceptedPixels=pixels;';assert s.split(start)[1].split(end)[0]==old.split(start)[1].split(end)[0]
for token in ['ioBudget4K=uhd;','CancellationTokenSource(300)','connect.CancelAfter(25)','length is <1 or >1400000','maxPixels=uhd?8847360','if(!uhd){joined!.Append(data);continue;}']:
 assert token in s,token
# No ABI/profile/producer/UI/preset/layout/source/permission/contract edits in this increment.
assert set(d['productFiles'])=={name}
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
assert 'FRAME_MEMORY'not in s and 'MeasuredFrame'not in s
p=(r/'tools/verify_desktop.py').read_text();tree=ast.parse(p);branches=[n for n in ast.walk(tree)if isinstance(n,ast.If)and ast.unparse(n.test)=="args.suite == 'run-4k-memory'"];assert len(branches)==3
calls=[ast.unparse(n)for b in branches for statement in b.body for n in ast.walk(statement)if isinstance(n,ast.Call)]
for token in ["work.run(label + '-run-4k-boundary'","work.run(label + '-run-4k-tail-'","work.run('packaged-run-4k-tail'","work.run('restored-run-4k-tail'"]:assert sum(token in c for c in calls)==1,token
assert "memory_budget=(9 if args.suite in ['run-4k-memory','run-4k'] else 7)*1024*MIB"in p
print('PASS isolated4K decoder only; original profiles/wire/UI/storage/IDs/ownership/CAS and publication exact, measured9GiB preflight plus unchanged1GiB safety; final independent LF/CRLF/package/restore dispatch')
