"""Finite BMP display inventory; all native/public contracts and authored layout unchanged."""
import sys,pathlib,json,subprocess,hashlib,zipfile
r=pathlib.Path(sys.argv[1]);
if(r/'docs/v666-resource-transfer-delta.json').exists():
 subprocess.run([sys.executable,str(r/'tests/web/v666_resource_transfer_copy.py'),str(r)],check=True);raise SystemExit(0)
d=json.loads((r/'docs/v666-resource-bmp-delta.json').read_text());git=lambda *a:subprocess.check_output(['git',*a],cwd=r,text=True)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles'])=={'examples/editor-home/WebBundle.csbody','examples/editor-home/ui/resource-images.js','examples/editor-home/ui/resource-previews.js'}
for name,digest in d['productFiles'].items():assert hashlib.sha256((r/name).read_text().encode()).hexdigest()==digest,name
for name in ['src','targets','packs','examples/editor-home/WebInvoke.csbody','examples/editor-home/Main.celem','examples/editor-home/ui/style.css','examples/editor-home/ui/v508-runtime.js','examples/editor-home/ui/workspace-host.js','examples/editor-home/ui/resource-browser.js','examples/editor-home/ui/resource-layout.js','examples/editor-home/ui/resource-content.js','examples/editor-home/ui/resource-docx.js','examples/editor-home/ui/resource-docx-dom.js','examples/editor-home/ui/resource-docx-zip.js','examples/editor-home/ui/resource-xlsx.js','examples/editor-home/ui/resource-xlsx-dom.js','examples/editor-home/ui/resource-xlsx-worker.js','examples/editor-home/ui/resource-pdf.js','examples/editor-home/ui/resource-office.js']:assert not git('diff','--name-only',d['baseCommit'],'--',name),name
p=(r/'examples/editor-home/ui/resource-previews.js').read_text();old=git('show',d['baseCommit']+':examples/editor-home/ui/resource-previews.js');assert p==old.replace('정지 PNG/JPEG/WebP인지','정지 PNG/JPEG/WebP/BMP인지').replace('정지 PNG/JPEG/WebP 그림','정지 PNG/JPEG/WebP/BMP 그림')
p=(r/'examples/editor-home/ui/resource-images.js').read_text();old=git('show',d['baseCommit']+':examples/editor-home/ui/resource-images.js');start=p.index(" if(bytes.length>=2&&tag(0,2)==='BM')");end=p.index(' return null;\n}\nexport function mountResourceImage',start);rest=p[:start]+p[end:];assert rest.replace("['image/webp','image/bmp'].includes(info.type)","info.type==='image/webp'")==old
p=(r/'examples/editor-home/WebBundle.csbody').read_text().split('"""');before=git('show',d['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""');assert p[0]==before[0]and p[2]==before[2];bundle=json.loads(p[1]);prior=json.loads(before[1]);assert set(bundle)==set(prior)
for name,row in bundle.items():
 raw=(r/'examples/editor-home/ui'/row['file']).read_bytes();raw=raw.replace(b'\r\n',b'\n')if row.get('bytePolicy')=='utf8-lf-v1'else raw;assert len(raw)==row.get('canonicalSize',row.get('size'))and hashlib.sha256(raw).hexdigest()==row.get('canonicalSha256',row.get('sha256')),name
 if name not in ['resource-images.js','resource-previews.js']:assert row==prior[name],name
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 app=z.read('Confectory-v666/dist/app.js').decode();preview=z.read('Confectory-v666/dist/resource-preview.js').decode();css=z.read('Confectory-v666/dist/style.css').decode();assert "'gif','svg','bmp','avif'"in app
 for token in ["item.kind==='image'",'URL.createObjectURL(blob)',"element('img')",'image.alt=item.name',"show(image,'그림 미리보기')",'URL.revokeObjectURL(url)']:assert token in preview,token
 rule='.resource-preview.is-image-preview img{display:block;width:100%;height:100%;min-height:0;object-fit:contain}';assert rule in css and rule in(r/'examples/editor-home/ui/style.css').read_text()
for name in ['resource-images','resource-previews']:subprocess.run(['node','--check',str(r/('examples/editor-home/ui/'+name+'.js'))],check=True)
print('PASS finite authored static BMP panel; PNG/JPEG/WebP header and decode logic, CSS, native bytes/permissions/contracts/CAS/ReviewConfirm and completed editors unchanged; no new vendor/native API/assets')
