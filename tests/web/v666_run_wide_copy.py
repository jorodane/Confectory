"""Original 640x360 option within the existing immutable pixel and transport ceilings."""
import pathlib,json,subprocess,hashlib,sys,zipfile
r=pathlib.Path(sys.argv[1]);
if (r/'docs/v666-run-grid-delta.json').exists():
 subprocess.run([sys.executable,str(r/'tests/web/v666_run_grid_copy.py'),str(r)],check=True);sys.exit(0)
d=json.loads((r/'docs/v666-run-wide-delta.json').read_text());paths=set(subprocess.check_output(['git','diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert paths==set(d['productFiles'])
allowed={'packs/run-surface/README.md','packs/run-surface/Open.csbody','packs/project-execution/Surface.csbody','packs/project-execution/ResizeSurface.csbody','packs/editor-home-model/RunPresets.csbody','examples/editor-home/ui/run-surface.js','examples/editor-home/ui/run-windows.js','examples/editor-home/ui/run-auto-fit.js','examples/editor-home/ui/run-presets.js','examples/editor-home/WebBundle.csbody'};assert paths==allowed,paths
for p,h in d['productFiles'].items():assert hashlib.sha256((r/p).read_text().encode()).hexdigest()==h,p
for p in ['packs/frame-control/Open.csbody','examples/resizable-output/Main.csbody','examples/software-output/Main.csbody','examples/editor-home/ui/style.css']:
 assert (r/p).read_text()==subprocess.check_output(['git','show',d['baseCommit']+':'+p],cwd=r,text=True)
assert hashlib.sha256((r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip').read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip')as z:assert "['640x360','640 × 360']"in z.read('Confectory-v666/dist/app.js').decode()
assert 'rgba.Length>1398104'in(r/'packs/run-surface/Open.csbody').read_text()and'encoded.Length>1398102'in(r/'packs/project-execution/Surface.csbody').read_text()
bundle=json.loads((r/'examples/editor-home/WebBundle.csbody').read_text().split('"""')[1])
for name in ['run-windows.js','run-surface.js','run-auto-fit.js','run-presets.js']:
 data=(r/'examples/editor-home/ui'/name).read_text().encode();assert bundle[name]['canonicalSize']==len(data)and bundle[name]['canonicalSha256']==hashlib.sha256(data).hexdigest()
print('PASS authored 640x360, unchanged 1MiB pixels/pipe/heartbeat/source/layout/contracts/permission boundaries, exact product allowlist and resource pins')
