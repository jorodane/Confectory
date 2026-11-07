"""Finite category-name overlay; unchanged bytes/topology, old decoder compatibility and existing authority."""
import pathlib,sys,subprocess,hashlib,json,zipfile
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-resource-folder-names-delta.json').read_text());git=lambda *a:subprocess.check_output(['git',*a],cwd=r,text=True)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed
for path,digest in d['productFiles'].items():assert hashlib.sha256((r/path).read_text().encode()).hexdigest()==digest,path
assert not any(p.startswith(('src/','targets/','packs/web-ui/','packs/file-stream/','packs/project-manager/','packs/edit-workspace/','packs/editor-home-model/'))for p in changed)
for path in ['packs/project-resources/Request.csbody','packs/project-resources/Layout.celem','packs/project-resources/LayoutBody.celem','packs/project-resources/pack.cpack','examples/editor-home/Main.celem','examples/editor-home/ui/v508-runtime.js','examples/editor-home/ui/resource-previews.js','examples/editor-home/ui/browser-shell.js','examples/editor-home/ui/style.css']:assert (r/path).read_text()==git('show',d['baseCommit']+':'+path),path
bridge=(r/'examples/editor-home/WebInvoke.csbody').read_text();assert bridge.replace('"load" or "create-folder" or "move" or "rename-folder"','"load" or "create-folder" or "move"')==git('show',d['baseCommit']+':examples/editor-home/WebInvoke.csbody')
parts=(r/'examples/editor-home/WebBundle.csbody').read_text().split('"""');before=git('show',d['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""');assert parts[0]==before[0]and parts[2]==before[2]
bundle=json.loads(parts[1]);prior=json.loads(before[1]);assert set(bundle)==set(prior)
for name,row in bundle.items():
 raw=(r/'examples/editor-home/ui'/row['file']).read_bytes();raw=raw.replace(b'\r\n',b'\n')if row.get('bytePolicy')=='utf8-lf-v1'else raw;assert len(raw)==row.get('canonicalSize',row.get('size'))and hashlib.sha256(raw).hexdigest()==row.get('canonicalSha256',row.get('sha256')),name
 if name not in ['resource-layout.js','resource-browser.js','workspace-host.js']:assert row==prior[name],name
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 source=z.read('Confectory-v666/dist/app.js').decode();a=source.index('function renameResourceInline');b=source.index('\nfunction ',a+10);rename=source[a:b]
 for phrase in ["input.maxLength=180","event.key==='Enter'","event.key==='Escape'","input.onblur=()=>finish(false)","item.name=value"]:assert phrase in rename,phrase
print('PASS authored category inline names only; independent name overlay leaves file store/import receipts/original layout format, source/override/permissions and primitives unchanged')
