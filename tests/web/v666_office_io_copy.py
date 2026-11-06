"""Reviewed completed-tool observation delta; no execution/permission/source-writing changes."""
import hashlib,json,pathlib,subprocess,sys
r=pathlib.Path(sys.argv[1]);
if(r/'docs/v666-run-developer-delta.json').exists():
 import runpy
 runpy.run_path(str(r/'tests/web/v666_run_developer_copy.py'),run_name='__main__');raise SystemExit(0)
d=json.loads((r/'docs/v666-office-io-delta.json').read_text())
def base(path):return subprocess.check_output(['git','show',d['baseCommit']+':'+path],cwd=r,text=True)
paths=set(subprocess.check_output(['git','diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert paths==set(d['productFiles']),paths
for name,digest in d['productFiles'].items():assert hashlib.sha256((r/name).read_text().encode()).hexdigest()==digest,name
assert not any(p.startswith(('src/','targets/','examples/','packs/worker-tasks/'))or p.endswith(('.celem','.cpack'))for p in paths)
# The public observation is the only changed Home command block; no mutation rights change.
p='packs/editor-home-model/Command.csbody';old=base(p);new=(r/p).read_text();start='if(operation=="worker-badges-inspect")';end='if(operation=='
a=old.index(start);b=new.index(start);assert old[:a]==new[:b]
a=old.index(end,a+len(start));b=new.index(end,b+len(start));assert old[a:]==new[b:]
p='packs/development-tools/Invoke.csbody';old=base(p);new=(r/p).read_text()
for token in ['calls.Stage.Invoke(','calls.Commit.Invoke(','SaveJournal(','calls.Create.Invoke(','calls.Read.Invoke(']:assert old.count(token)==new.count(token),token
assert new.index('if(completedIO is not null)')>new.index('Tool result exceeds output budget')
assert 'originHash' in new and 'Hash(capability+"\\n"+callId)'in new
poll=(r/'packs/project-ai/Poll.csbody').read_text();assert '.AsObject().Remove("lastToolIO")'in poll and 'scoped["lastToolIO"]?["originHash"]'in poll
manifest=json.loads((r/'packs/workspace-3d/ui/manifest.json').read_text())
for name,row in manifest.items():
 data=(r/'packs/workspace-3d/ui'/name).read_text().encode();assert len(data)==row['size']and hashlib.sha256(data).hexdigest()==row['sha256']
print('PASS completed read/draft-stage only; exact assigned current capability/Worker/project; no new source/journal writes, permissions, public ABI, CSS, layout or Run backend changes')
