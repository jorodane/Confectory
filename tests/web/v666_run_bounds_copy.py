"""Closed source/layout/permission delta for producer-reported pixel bounds."""
import pathlib,sys,json,hashlib,subprocess,zipfile
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-run-bounds-delta.json').read_text());git=lambda *a:subprocess.check_output(['git',*a],cwd=r,text=True)
paths=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines());assert paths==set(d['productFiles']),paths
for name,value in d['productFiles'].items():assert hashlib.sha256((r/name).read_text().encode()).hexdigest()==value,name
for name in ['packs/frame-control/Open.csbody','packs/frame-control/Begin.csbody','packs/frame-control/Complete.csbody','packs/frame-control/Close.csbody','packs/run-surface/Present.celem','packs/run-surface/Open.celem','packs/run-surface/ConfigureSize.celem','packs/project-execution/ResizeSurface.csbody','packs/project-execution/Audio.csbody','packs/web-ui/Open.csbody','packs/browser-host/Serve.csbody','examples/software-output/Main.csbody','examples/resizable-output/Main.csbody','examples/editor-home/ui/run-grid.js']:
 assert(r/name).read_text()==git('show',d['baseCommit']+':'+name),name
assert not any(name.startswith(('src/','targets/'))for name in paths)
manifest=json.loads((r/'examples/editor-home/WebBundle.csbody').read_text().split('"""')[1]);before=json.loads(git('show',d['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""')[1]);assert set(manifest)-set(before)=={'run-bounds.js'}and not set(before)-set(manifest)
for name in manifest:
 if name not in ['run-surface.js','run-windows.js','style.css','run-bounds.js']:assert manifest[name]==before[name],name
 else:
  raw=(r/'examples/editor-home/ui'/name).read_text().encode();assert manifest[name]['canonicalSize']==len(raw)and manifest[name]['canonicalSha256']==hashlib.sha256(raw).hexdigest(),name
launch=(r/'packs/project-execution/LaunchConfigured.csbody').read_text();original=git('show',d['baseCommit']+':packs/project-execution/LaunchConfigured.csbody');assert launch.replace('new System.Collections.Generic.Dictionary<long,long>()},null!,null!}};','new System.Collections.Generic.Dictionary<long,long>()},null!}};')==original
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 assert any('data-run-debug="bounds"'in z.read(n).decode()for n in z.namelist()if n.endswith('/dist/app.js'))
for name in ['packs/run-surface/Open.csbody','packs/project-execution/Surface.csbody']:
 s=(r/name).read_text();assert '139810'in s and '262144'in s and '640'in s
print('PASS closed bounds delta; original Invoke/source/ownership/ACK/resize/audio/transport budgets and authored layout retained; reference and bundle sealed')
