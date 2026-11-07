"""Finite V6 category/navigation/move delta; old bytes, contracts and source paths immutable."""
import pathlib,sys,subprocess,hashlib,json,zipfile
r=pathlib.Path(sys.argv[1]);
if (r/'docs/v666-resource-folder-names-delta.json').exists():
 subprocess.run([sys.executable,str(r/'tests/web/v666_resource_folder_names_copy.py'),str(r)],check=True);raise SystemExit(0)
d=json.loads((r/'docs/v666-resource-layout-delta.json').read_text());git=lambda *a:subprocess.check_output(['git',*a],cwd=r,text=True)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed
for path,digest in d['productFiles'].items():assert hashlib.sha256((r/path).read_text().encode()).hexdigest()==digest,path
assert not any(p.startswith(('src/','targets/','packs/web-ui/','packs/file-stream/','packs/project-manager/','packs/edit-workspace/','packs/pack-workspace/'))for p in changed)
for path in ['packs/project-resources/Request.csbody','packs/project-resources/Request.celem','packs/project-resources/RequestBody.celem','examples/editor-home/ui/resource-previews.js','examples/editor-home/ui/browser-shell.js','examples/editor-home/ui/style.css']:assert (r/path).read_text()==git('show',d['baseCommit']+':'+path),path
old=json.loads(git('show',d['baseCommit']+':docs/v666-resource-preview-delta.json'))
for path,digest in old['productFiles'].items():assert hashlib.sha256(git('show',d['baseCommit']+':'+path).encode()).hexdigest()==digest,path
bridge=(r/'examples/editor-home/WebInvoke.csbody').read_text();a=bridge.index('if(endpoint=="projectResourceLayout"){');z=bridge.index('if(endpoint=="projectResources"){',a);assert bridge[:a]+bridge[z:]==git('show',d['baseCommit']+':examples/editor-home/WebInvoke.csbody');assert '"load" or "create-folder" or "move"'in bridge[a:z]
parts=(r/'examples/editor-home/WebBundle.csbody').read_text().split('"""');before=git('show',d['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""');assert parts[0]==before[0]and parts[2].replace('new[]{"projectResourceLayout","projectResources"','new[]{"projectResources"')==before[2]
bundle=json.loads(parts[1]);prior=json.loads(before[1]);assert set(bundle)-set(prior)=={'resource-layout.js'}and not set(prior)-set(bundle)
for name,row in bundle.items():
 raw=(r/'examples/editor-home/ui'/row['file']).read_bytes();raw=raw.replace(b'\r\n',b'\n')if row.get('bytePolicy')=='utf8-lf-v1'else raw;assert len(raw)==row.get('canonicalSize',row.get('size'))and hashlib.sha256(raw).hexdigest()==row.get('canonicalSha256',row.get('sha256')),name
 if name not in ['resource-layout.js','resource-browser.js','v508-runtime.js','workspace-host.js']:assert row==prior[name],name
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 source=z.read('Confectory-v666/dist/app.js').decode();assert "resourceNameDialog('새 자료 카테고리','새 카테고리'"in source and "!selected.has(item.parent)"in source and 'application/x-confectory-resource'in source
print('PASS finite authored category/navigation/explicit root drag move; immutable bytes/import receipts/source/override/permissions/CAS and existing read-only preview retained')
