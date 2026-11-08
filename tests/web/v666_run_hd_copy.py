"""Finite authored HD scope and unchanged authority/public/packet boundaries."""
import sys,pathlib,json,subprocess,hashlib,zipfile,ast
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-run-hd-delta.json').read_text());git=lambda *a:subprocess.check_output(['git',*a],cwd=r,text=True)
assert set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines())==set(d['productFiles'])
for name,digest in d['productFiles'].items():assert hashlib.sha256((r/name).read_text().encode()).hexdigest()==digest,name
for name in ['src','targets','packs/frame-control','packs/run-audio','packs/editor-home-model/RunWindows.csbody','examples/editor-home/WebInvoke.csbody','examples/editor-home/ui/style.css','examples/editor-home/ui/v508-runtime.js','examples/editor-home/ui/workspace-host.js','examples/editor-home/ui/resource-images.js','examples/editor-home/ui/resource-svg.js','examples/resizable-output','examples/software-output','examples/audio-output','examples/bounds-output']:
 assert not git('diff','--name-only',d['baseCommit'],'--',name),name
for name in ['Open.celem','Present.celem','PresentBounds.celem','ConfigureSize.celem','RequestedSize.celem','Close.celem']:
 file='packs/run-surface/'+name;assert not git('diff','--name-only',d['baseCommit'],'--',file),name
p=(r/'examples/editor-home/WebBundle.csbody').read_text().split('"""');old=git('show',d['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""');assert p[0]==old[0]and p[2]==old[2];current=json.loads(p[1]);before=json.loads(old[1]);assert set(current)==set(before)
for name,row in current.items():
 raw=(r/'examples/editor-home/ui'/row['file']).read_bytes();raw=raw.replace(b'\r\n',b'\n')if row.get('bytePolicy')=='utf8-lf-v1'else raw;assert len(raw)==row.get('canonicalSize',row.get('size'))and hashlib.sha256(raw).hexdigest()==row.get('canonicalSha256',row.get('sha256')),name
 if name not in ['run-surface.js','run-windows.js','run-auto-fit.js','run-presets.js']:assert row==before[name],name
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 app=z.read('Confectory-v666/dist/app.js').decode()
 for item in ["['1280x720','HD · 1280 × 720']","['720x1280','HD · 720 × 1280']","['1024x768','4:3 · 1024 × 768']"]:assert item in app
# Dedicated package/restore chains must not fall into unrelated generic header tests.
s=(r/'tools/verify_desktop.py').read_text();tree=ast.parse(s);branches=[node for node in ast.walk(tree)if isinstance(node,ast.If)and isinstance(node.test,ast.Compare)and isinstance(node.test.ops[0],ast.Eq)and any(isinstance(x,ast.Constant)and x.value=='run-hd'for x in node.test.comparators)];assert len(branches)==3
calls=[ast.get_source_segment(s,call)for node in branches for body in node.body for call in ast.walk(body)if isinstance(call,ast.Call)]
for token in ["work.run(label+'-run-hd-boundary'","work.run('packaged-run-hd-'","work.run('restored-run-hd-'"]:assert sum(token in call for call in calls)==1,token
for name in ['run-surface','run-windows','run-auto-fit','run-presets']:subprocess.run(['node','--check',str(r/('examples/editor-home/ui/'+name+'.js'))],check=True)
print('PASS authored HD landscape/portrait/4:3, exact source inventory, preserved old public ABI/authority/IPC ceilings and layout; dedicated package/restore routing')
