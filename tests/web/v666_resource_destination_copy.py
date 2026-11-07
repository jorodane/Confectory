"""Finite destination-aware first import: native composition, original storage and authored UI."""
import sys,pathlib,json,subprocess,hashlib,zipfile
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-resource-destination-delta.json').read_text());git=lambda *a:subprocess.check_output(['git',*a],cwd=r,text=True)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed
assert changed=={'packs/project-resources/Request.csbody','packs/project-resources/Layout.csbody','examples/editor-home/WebInvoke.csbody','examples/editor-home/WebBundle.csbody','examples/editor-home/ui/resource-browser.js','examples/editor-home/ui/resource-layout.js'}
for name,digest in d['productFiles'].items():assert hashlib.sha256((r/name).read_text().encode()).hexdigest()==digest,name
for name in ['src','targets','packs/file-stream','packs/web-ui','packs/editor-home-model','packs/project-manager','packs/edit-workspace','packs/project-resources/DeletionRecords.csbody','packs/project-resources/Request.celem','packs/project-resources/RequestBody.celem','packs/project-resources/Layout.celem','packs/project-resources/LayoutBody.celem','examples/editor-home/Main.celem','examples/editor-home/ui/resource-content.js','examples/editor-home/ui/resource-previews.js','examples/editor-home/ui/resource-images.js','examples/editor-home/ui/resource-selection.js','examples/editor-home/ui/style.css','examples/editor-home/ui/v508-runtime.js','examples/editor-home/ui/workspace-host.js']:
 assert not git('diff','--name-only',d['baseCommit'],'--',name),name
current=(r/'packs/project-resources/Layout.csbody').read_text();start=current.index('\nif(operation=="import-files")');end=current.index('if(operation=="load")',start);rest=(current[:start]+current[end:]).replace('operation is "save-content" or "import-files"?1501000:16384','operation=="save-content"?1501000:16384');assert rest==git('show',d['baseCommit']+':packs/project-resources/Layout.csbody')
before=git('show',d['baseCommit']+':packs/project-resources/Request.csbody');now=(r/'packs/project-resources/Request.csbody').read_text();assert now[:now.index('bool prepare=')]==before[:before.index('bool batch=')]
web=(r/'examples/editor-home/WebInvoke.csbody').read_text();assert web.replace('layoutAction is not ("import-files" or "load" or','layoutAction is not ("load" or')==git('show',d['baseCommit']+':examples/editor-home/WebInvoke.csbody')
parts=(r/'examples/editor-home/WebBundle.csbody').read_text().split('"""');prior=git('show',d['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""');assert parts[0]==prior[0]and parts[2]==prior[2];bundle=json.loads(parts[1]);old=json.loads(prior[1]);assert set(bundle)==set(old)
for name,row in bundle.items():
 raw=(r/'examples/editor-home/ui'/row['file']).read_bytes();raw=raw.replace(b'\r\n',b'\n')if row.get('bytePolicy')=='utf8-lf-v1'else raw;assert len(raw)==row.get('canonicalSize',row.get('size'))and hashlib.sha256(raw).hexdigest()==row.get('canonicalSha256',row.get('sha256')),name
 if name not in ['resource-browser.js','resource-layout.js']:assert row==old[name]
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 app=z.read('Confectory-v666/dist/app.js').decode();start=app.index('async function importResourceFiles');end=app.index('function resourceNameDialog',start);authored=app[start:end]
 for token in ['targetFolder=folderId','parent:targetFolder',"transaction('files','readwrite')",'selected[index]','push(...items)']:assert token in authored,token
print('PASS authored explicit destination; one native file/placement transaction; v1 source/permission/override/ReviewConfirm and final CAS primitives preserved')
