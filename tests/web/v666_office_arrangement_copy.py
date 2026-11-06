"""Exact private display-layout delta: no source/execution/permission backend changes."""
import hashlib,json,pathlib,subprocess,sys
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-office-arrangement-delta.json').read_text());paths=set(subprocess.check_output(['git','diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert paths==set(d['productFiles']),paths
for name,digest in d['productFiles'].items():assert hashlib.sha256((r/name).read_text().encode()).hexdigest()==digest,name
assert not any(p.startswith(('src/','targets/','packs/editor-home-model/','packs/worker-tasks/'))for p in paths)
assert {p for p in paths if p.endswith(('.csbody','.celem','.cpack'))}=={'examples/editor-home/WebBundle.csbody'}
root=r/'packs/workspace-3d/ui';manifest=json.loads((root/'manifest.json').read_text())
for name,row in manifest.items():
 data=(root/name).read_text().encode();assert len(data)==row['size']and hashlib.sha256(data).hexdigest()==row['sha256']
for name in ['adapter.js','arrangement.js']:
 text=(root/name).read_text();assert not any(t in text for t in ['fetch(','view.call(','startAI','runProject','confirmDraft','prepareWorker'])
assert 'office?.captureSnapshot(value);return value;'in(r/'examples/editor-home/ui/workspace-host.js').read_text()
print('PASS exact private arrangement/snapshot delta; public contracts/C# originals/Task journals/permissions/ReviewConfirm/source CAS unchanged')
