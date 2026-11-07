"""Closed static PNG/JPEG display, unchanged native read/storage/source/permission contracts."""
import sys,pathlib,json,hashlib,subprocess,zipfile
r=pathlib.Path(sys.argv[1]);
if(r/'docs/v666-resource-batch-delta.json').exists():
 subprocess.run([sys.executable,str(r/'tests/web/v666_resource_batch_copy.py'),str(r)],check=True);raise SystemExit(0)
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-resource-images-delta.json').read_text());git=lambda *a:subprocess.check_output(['git',*a],cwd=r,text=True)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed
assert changed=={'examples/editor-home/WebBundle.csbody','examples/editor-home/ui/resource-previews.js','examples/editor-home/ui/resource-images.js','examples/editor-home/ui/style.css'}
for name,digest in d['productFiles'].items():assert hashlib.sha256((r/name).read_text().encode()).hexdigest()==digest,name
for name in ['src','targets','packs','examples/editor-home/WebInvoke.csbody','examples/editor-home/Main.celem','examples/editor-home/ui/resource-content.js','examples/editor-home/ui/v508-runtime.js','examples/editor-home/ui/workspace-host.js','examples/editor-home/ui/resource-browser.js','examples/editor-home/ui/resource-layout.js']:assert not git('diff','--name-only',d['baseCommit'],'--',name),name
parts=(r/'examples/editor-home/WebBundle.csbody').read_text().split('"""');prior=git('show',d['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""');assert parts[0]==prior[0]and parts[2]==prior[2];bundle=json.loads(parts[1]);old=json.loads(prior[1]);assert set(bundle)==set(old)|{'resource-images.js'}
for name,row in bundle.items():
 raw=(r/'examples/editor-home/ui'/row['file']).read_bytes();raw=raw.replace(b'\r\n',b'\n')if row.get('bytePolicy')=='utf8-lf-v1'else raw;assert len(raw)==row.get('canonicalSize',row.get('size'))and hashlib.sha256(raw).hexdigest()==row.get('canonicalSha256',row.get('sha256')),name
 if name not in ['resource-images.js','resource-previews.js','style.css']:assert row==old[name]
assert(r/'examples/editor-home/ui/style.css').read_text().startswith(git('show',d['baseCommit']+':examples/editor-home/ui/style.css'))
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 text=z.read('Confectory-v666/dist/resource-preview.js').decode();css=z.read('Confectory-v666/dist/style.css').decode()
 for token in ["item.kind==='image'",'URL.createObjectURL(blob)',"element('img')",'image.alt=item.name',"show(image,'그림 미리보기')",'URL.revokeObjectURL(url)']:assert token in text,token
 rule='.resource-preview.is-image-preview img{display:block;width:100%;height:100%;min-height:0;object-fit:contain}';assert rule in css and rule in(r/'examples/editor-home/ui/style.css').read_text()
print('PASS authored static raster panel; native read/bytes/storage/permissions/C#/override/ReviewConfirm/CAS and completed text editor unchanged; no vendor, external URL or active SVG renderer')
