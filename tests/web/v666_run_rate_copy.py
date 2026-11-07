"""Finite V8 rate delta over the reviewed output contracts, not a new renderer."""
import pathlib,sys,json,hashlib,subprocess
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-run-rate-delta.json').read_text());git=lambda *a:subprocess.check_output(['git',*a],cwd=r,text=True)
paths=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines());assert paths==set(d['productFiles']),paths
for name,value in d['productFiles'].items():assert hashlib.sha256((r/name).read_text().encode()).hexdigest()==value,name
for name in ['packs/frame-control/Open.csbody','packs/frame-control/Begin.csbody','packs/frame-control/Complete.csbody','packs/frame-control/Close.csbody','packs/run-surface/Present.celem','packs/run-surface/Open.celem','packs/run-surface/ConfigureSize.celem','packs/project-execution/ResizeSurface.csbody','packs/project-execution/Audio.csbody','packs/web-ui/Open.csbody','packs/browser-host/Serve.csbody','examples/software-output/Main.csbody','examples/resizable-output/Main.csbody']:
 assert(r/name).read_text()==git('show',d['baseCommit']+':'+name),name
assert not any(name.startswith(('src/','targets/'))for name in paths)
manifest=json.loads((r/'examples/editor-home/WebBundle.csbody').read_text().split('"""')[1]);before=json.loads(git('show',d['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""')[1]);assert set(manifest)==set(before)
for name in manifest:
 if name not in ['run-surface.js','run-windows.js']:assert manifest[name]==before[name],name
 else:
  raw=(r/'examples/editor-home/ui'/name).read_bytes();assert manifest[name]['canonicalSize']==len(raw)and manifest[name]['canonicalSha256']==hashlib.sha256(raw).hexdigest(),name
assert hashlib.sha256((r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip').read_bytes()).hexdigest()==d['referenceSha256']
launch=(r/'packs/project-execution/LaunchConfigured.csbody').read_text();original=git('show',d['baseCommit']+':packs/project-execution/LaunchConfigured.csbody');assert launch.replace('new System.Collections.Generic.Dictionary<long,long>()},null!}};','new System.Collections.Generic.Dictionary<long,long>()}}};')==original
for name in ['packs/run-surface/Open.csbody','packs/project-execution/Surface.csbody']:
 s=(r/name).read_text();assert '139810' in s and '262144'in s and '640'in s
assert 'rateBuckets=new long[10]'in(r/'packs/run-surface/Open.csbody').read_text()
assert 'requestAnimationFrame'not in(r/'examples/editor-home/ui/run-windows.js').read_text()
print('PASS finite software-publication rate delta; original source/Invoke/resize/audio/ACK/transport/ownership budgets and layout preserved; sealed bundle and reference, no new permissions or GPU/FPS invention')
