"""Exact display-only delta from the verified 3D checkpoint; no backend authority changes."""
import hashlib,json,pathlib,subprocess,sys
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-office-workers-delta.json').read_text());base=d['baseCommit'];paths=set(subprocess.check_output(['git','diff','--name-only',base,'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert paths==set(d['productFiles']),paths
for name,digest in d['productFiles'].items():assert hashlib.sha256((r/name).read_text().encode()).hexdigest()==digest,name
assert not any(p.startswith(('src/','targets/','packs/editor-home-model/','packs/worker-tasks/'))for p in paths)
assert {p for p in paths if p.endswith(('.csbody','.celem','.cpack'))}=={'examples/editor-home/WebBundle.csbody'}
root=r/'packs/workspace-3d/ui';manifest=json.loads((root/'manifest.json').read_text())
for name,row in manifest.items():
 data=(root/name).read_text().encode();assert len(data)==row['size']and hashlib.sha256(data).hexdigest()==row['sha256']
for name in ['adapter.js','workers.js']:
 text=(root/name).read_text();assert not any(token in text for token in ['fetch(','view.call(','startAI','prepareWorker','runProject','confirmDraft'])
text=(root/'office.js').read_text();assert 'if(this.bridge.observedOnly)return;const d=event.detail;'in text
print('PASS exact public Worker observation display delta; backend/project permissions/ownership/Task journals/dispatch/contracts/CAS/ReviewConfirm and original licensed geometry unchanged')
