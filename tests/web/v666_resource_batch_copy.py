"""Closed authored transactional multi-file import with unchanged v1 storage and ownership."""
import sys,pathlib,json,subprocess,hashlib,zipfile
r=pathlib.Path(sys.argv[1]);
if(r/'docs/v666-resource-destination-delta.json').exists():
 subprocess.run([sys.executable,str(r/'tests/web/v666_resource_destination_copy.py'),str(r)],check=True);raise SystemExit(0)
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-resource-batch-delta.json').read_text());git=lambda *a:subprocess.check_output(['git',*a],cwd=r,text=True)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed
assert changed=={'packs/project-resources/Request.csbody','examples/editor-home/WebInvoke.csbody','examples/editor-home/WebBundle.csbody','examples/editor-home/ui/resource-browser.js'}
for p,digest in d['productFiles'].items():assert hashlib.sha256((r/p).read_text().encode()).hexdigest()==digest,p
for p in ['src','targets','packs/file-stream','packs/web-ui','packs/editor-home-model','packs/project-manager','packs/edit-workspace','packs/project-resources/Layout.csbody','packs/project-resources/DeletionRecords.csbody','examples/editor-home/Main.celem','examples/editor-home/ui/resource-content.js','examples/editor-home/ui/resource-previews.js','examples/editor-home/ui/resource-images.js','examples/editor-home/ui/resource-layout.js','examples/editor-home/ui/resource-selection.js','examples/editor-home/ui/style.css']:
 assert not git('diff','--name-only',d['baseCommit'],'--',p),p
old=git('show',d['baseCommit']+':packs/project-resources/Request.csbody');now=(r/'packs/project-resources/Request.csbody').read_text();assert now[:now.index('string Reply(')]==old[:old.index('string Reply(')]
web=(r/'examples/editor-home/WebInvoke.csbody').read_text();assert web.replace('resourceAction is not ("load" or "read" or "import" or "import-many")','resourceAction is not ("load" or "read" or "import")')==git('show',d['baseCommit']+':examples/editor-home/WebInvoke.csbody')
parts=(r/'examples/editor-home/WebBundle.csbody').read_text().split('"""');before=git('show',d['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""');assert parts[0]==before[0]and parts[2]==before[2];bundle=json.loads(parts[1]);prior=json.loads(before[1]);assert set(bundle)==set(prior)
for name,row in bundle.items():
 raw=(r/'examples/editor-home/ui'/row['file']).read_bytes();raw=raw.replace(b'\r\n',b'\n')if row.get('bytePolicy')=='utf8-lf-v1'else raw;assert len(raw)==row.get('canonicalSize',row.get('size'))and hashlib.sha256(raw).hexdigest()==row.get('canonicalSha256',row.get('sha256')),name
 if name!='resource-browser.js':assert row==prior[name]
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 app=z.read('Confectory-v666/dist/app.js').decode();start=app.index('async function importResourceFiles');end=app.index('function resourceNameDialog',start);original=app[start:end]
 for token in ["transaction('files','readwrite')",'items.forEach','selected[index]','transaction.oncomplete=resolve','push(...items)']:assert token in original,token
print('PASS authored all-file transaction; v1 record validation/receipts, native permissions, source/override/ReviewConfirm and final CAS primitives preserved')
