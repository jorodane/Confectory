"""Closed authored text/code edit and one-save backup, existing project ownership only."""
import sys,pathlib,json,subprocess,hashlib,zipfile
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-resource-content-delta.json').read_text());git=lambda *a:subprocess.check_output(['git',*a],cwd=r,text=True)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed
for p,h in d['productFiles'].items():assert hashlib.sha256((r/p).read_text().encode()).hexdigest()==h,p
assert not any(p.startswith(('src/','targets/','packs/web-ui/','packs/file-stream/','packs/project-manager/','packs/edit-workspace/'))for p in changed)
for p in ['packs/project-resources/Request.csbody','packs/project-resources/Request.celem','packs/project-resources/DeletionRecords.csbody','examples/editor-home/Main.celem','examples/editor-home/ui/workspace-host.js','examples/editor-home/ui/resource-layout.js','examples/editor-home/ui/resource-selection.js']:
 assert(r/p).read_text()==git('show',d['baseCommit']+':'+p),p
parts=(r/'examples/editor-home/WebBundle.csbody').read_text().split('"""');old=json.loads(git('show',d['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""')[1]);bundle=json.loads(parts[1]);assert set(bundle)==set(old)|{'resource-content.js'}
for name,row in bundle.items():
 raw=(r/'examples/editor-home/ui'/row['file']).read_bytes();raw=raw.replace(b'\r\n',b'\n')if row.get('bytePolicy')=='utf8-lf-v1'else raw;assert len(raw)==row.get('canonicalSize',row.get('size'))and hashlib.sha256(raw).hexdigest()==row.get('canonicalSha256',row.get('sha256')),name
 if name not in ['resource-content.js','resource-previews.js','resource-browser.js','v508-runtime.js','style.css']:assert row==old[name]
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 app=z.read('Confectory-v666/dist/app.js').decode();editor=z.read('Confectory-v666/dist/resource-edit.js').decode()
 for token in ['function writeResourceContent','content-backup','contentRevision','contentRestoreToggled','data-resource-content-edit','data-resource-content-save','data-resource-content-restore']:assert token in app,token
 for token in ['1 MB','textCodec','Ctrl+S 저장 · Esc 취소','resource-text-editor']:assert token in editor,token
css=(r/'examples/editor-home/ui/style.css').read_text();assert css.startswith(git('show',d['baseCommit']+':examples/editor-home/ui/style.css'))
print('PASS fixed v666 text editor/one-save backup; original import ABI, C#/override/layout/source/permission primitives and deletion receipts unchanged; private input transport stays inside existing 2MiB request/response cap')
