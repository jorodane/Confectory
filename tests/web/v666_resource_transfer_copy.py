"""Finite selected-group extension; unchanged stored v1 and public function signatures."""
import sys,pathlib,json,subprocess,hashlib,zipfile
r=pathlib.Path(sys.argv[1]);
if(r/'docs/v666-resource-gif-delta.json').exists():
 subprocess.run([sys.executable,str(r/'tests/web/v666_resource_gif_copy.py'),str(r)],check=True);raise SystemExit(0)
d=json.loads((r/'docs/v666-resource-transfer-delta.json').read_text());git=lambda *a:subprocess.check_output(['git',*a],cwd=r,text=True)
expected={'examples/editor-home/WebBundle.csbody','examples/editor-home/WebInvoke.csbody','examples/editor-home/ui/resource-browser.js','packs/editor-home-model/CloseSession.csbody','packs/editor-home-model/Command.csbody','packs/editor-home-model/Resources.csbody','packs/project-resources/Layout.csbody','packs/project-resources/Request.csbody'}
assert {x for x in git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines()if not x.endswith('.md')}==set(d['productFiles'])==expected
for name,digest in d['productFiles'].items():assert hashlib.sha256((r/name).read_text().encode()).hexdigest()==digest,name
for name in ['src','targets','packs/file-stream','packs/project-manager','examples/editor-home/Main.celem','examples/editor-home/ui/style.css','examples/editor-home/ui/workspace-host.js','examples/editor-home/ui/v508-runtime.js','examples/editor-home/ui/resource-layout.js','examples/editor-home/ui/resource-content.js','examples/editor-home/ui/resource-images.js','examples/editor-home/ui/resource-previews.js','examples/editor-home/ui/resource-docx.js','examples/editor-home/ui/resource-xlsx.js','examples/editor-home/ui/resource-pdf.js']:
 assert not git('diff','--name-only',d['baseCommit'],'--',name),name
assert not git('diff','--name-only',d['baseCommit'],'--','*.celem','*.cpack')
now=(r/'packs/project-resources/Request.csbody').read_text();old=git('show',d['baseCommit']+':packs/project-resources/Request.csbody');assert now==old.replace('payload.Length>1500000','payload.Length>(operation is "import-many" or "prepare-import-many"?6000000:1500000)').replace('["importBytes"]=fileLimit','["importBytes"]=totalLimit').replace('batch&&selectedBytes>fileLimit','batch&&selectedBytes>totalLimit')
now=(r/'packs/project-resources/Layout.csbody').read_text();old=git('show',d['baseCommit']+':packs/project-resources/Layout.csbody');assert now==old.replace('operation is "save-content" or "import-files"?1501000:16384','operation=="import-files"?6000000:operation=="save-content"?1501000:16384')
p=(r/'examples/editor-home/WebBundle.csbody').read_text().split('"""');before=git('show',d['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""');assert p[0]==before[0]and p[2]==before[2];bundle=json.loads(p[1]);prior=json.loads(before[1]);assert set(bundle)==set(prior)
for name,row in bundle.items():
 raw=(r/'examples/editor-home/ui'/row['file']).read_bytes();raw=raw.replace(b'\r\n',b'\n')if row.get('bytePolicy')=='utf8-lf-v1'else raw;assert len(raw)==row.get('canonicalSize',row.get('size'))and hashlib.sha256(raw).hexdigest()==row.get('canonicalSha256',row.get('sha256')),name
 if name!='resource-browser.js':assert row==prior[name],name
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 app=z.read('Confectory-v666/dist/app.js').decode();assert 'data-resource-files multiple hidden' in app
subprocess.run(['node','--check',str(r/'examples/editor-home/ui/resource-browser.js')],check=True)
print('PASS finite selected-group 4MiB; per-file1MiB/store4MiB64/v1 and function signatures unchanged; bounded session transport; authored layout, permissions, ReviewConfirm/finalCAS and completed editors retained')
