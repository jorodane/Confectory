"""Reviewed finite resolution path; authored source and old output remain compatible."""
import pathlib,json,subprocess,hashlib,sys,re
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-run-resolution-delta.json').read_text());paths=set(subprocess.check_output(['git','diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert paths==set(d['productFiles']),paths
for p,digest in d['productFiles'].items():assert hashlib.sha256((r/p).read_text().encode()).hexdigest()==digest,p
assert not any(p.startswith(('src/','targets/','packs/web-ui/','packs/project-ai/','packs/development-tools/'))for p in paths)
for p in ['examples/software-output/Main.csbody','examples/software-output/MainBody.celem','examples/software-output/project.cpack','packs/frame-control/Begin.csbody','packs/frame-control/Complete.csbody']:
 assert(r/p).read_text()==subprocess.check_output(['git','show',d['baseCommit']+':'+p],cwd=r,text=True),p
s=(r/'packs/frame-control/Open.csbody').read_text();a=s.index('else if(op=="surface-command")');b=s.index('else if(op=="observe")',a);assert'heartbeat='not in s[a:b]and'Ack('not in s[a:b]
s=(r/'packs/run-surface/Open.csbody').read_text();assert'width==requestedWidth&&height==requestedHeight)sizeAck=sizeSequence'in s and'Configure explicitly once before first pixels'in s
s=(r/'examples/editor-home/ui/run-windows.js').read_text();assert"query(w,'surface-size',request)"in s and'width.disabled=height.disabled=!current()||!w.runSizeEditing;'in s
for bad in ['AudioContext','requestAnimationFrame','performance.now','fetch(']:assert bad not in s
s=(r/'examples/editor-home/WebBundle.csbody').read_text();manifest=json.loads(s.split('"""')[1]);
for p in ['run-windows.js','run-surface.js']:
 data=(r/'examples/editor-home/ui'/p).read_text().encode();assert manifest[p]['canonicalSize']==len(data)and manifest[p]['canonicalSha256']==hashlib.sha256(data).hexdigest()
assert hashlib.sha256((r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip').read_bytes()).hexdigest()==d['referenceSha256'];print('PASS explicit size opt-in/actual image ACK/CAS/same owned channel; no frame heartbeat or automatic Step, no source rewrite/permission/layout changes')
