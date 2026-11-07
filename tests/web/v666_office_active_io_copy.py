"""Finite live-I/O observation delta, keeping original mutation and critical snapshot boundaries."""
import hashlib,json,pathlib,subprocess,sys
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-office-active-io-delta.json').read_text())
paths=set(subprocess.check_output(['git','diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert paths==set(d['productFiles']),paths
for p,h in d['productFiles'].items():assert hashlib.sha256((r/p).read_text().encode()).hexdigest()==h,p
assert not any(p.startswith(('src/','targets/','examples/','packs/worker-tasks/','packs/edit-workspace/'))for p in paths)
assert hashlib.sha256((r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip').read_bytes()).hexdigest()==d['referenceSha256']
def base(p):return subprocess.check_output(['git','show',d['baseCommit']+':'+p],cwd=r,text=True)
p='packs/development-tools/Invoke.csbody';old=base(p);new=(r/p).read_text()
for token in ['calls.Stage.Invoke(','calls.Commit.Invoke(','SaveJournal(','calls.Create.Invoke(','calls.Read.Invoke(','chatGuard(']:assert old.count(token)==new.count(token),token
assert new.index('}ActiveIO(id,"draft-stage")')>new.index('expectedHash')and new.index('ActiveIO(id,"read")')>new.index('string id=Id()')
assert 'finally{System.Threading.Volatile.Write(ref state[9],null!);}'in new
assert (r/'packs/development-tools/Snapshot.csbody').read_text()==base('packs/development-tools/Snapshot.csbody')
assert (r/'packs/development-tools/Schema.csbody').read_text()==base('packs/development-tools/Schema.csbody')
s=(r/'packs/development-tools/Observe.csbody').read_text();assert 'Monitor.TryEnter' in s and 'Monitor.Enter('not in s and 'calls.Snapshot.Invoke'in s and 'if(busy)'in s
p='packs/editor-home-model/Command.csbody';old=base(p);new=(r/p).read_text();start='if(operation=="worker-badges-inspect")';end='if(operation=='
a=old.index(start);b=new.index(start);assert old[:a]==new[:b];a=old.index(end,a+len(start));b=new.index(end,b+len(start));assert old[a:]==new[b:]
m=json.loads((r/'packs/workspace-3d/ui/manifest.json').read_text())
for n,row in m.items():
 b=(r/'packs/workspace-3d/ui'/n).read_text().encode();assert len(b)==row['size']and hashlib.sha256(b).hexdigest()==row['sha256'],n
print('PASS exact active IO delta; unchanged source mutation/CAS/critical Snapshot and UI layout, task/permission/runtime contracts; narrow nonblocking observation and private origin validation only')
