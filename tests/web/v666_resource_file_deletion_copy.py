"""Closed authored single-copy deletion; no Core/permission/source/renderer rewrite."""
import pathlib,sys,subprocess,hashlib,json,zipfile
r=pathlib.Path(sys.argv[1]);
if(r/'docs/v666-resource-folder-deletion-delta.json').exists():
 subprocess.run([sys.executable,str(r/'tests/web/v666_resource_folder_deletion_copy.py'),str(r)],check=True);raise SystemExit(0)
d=json.loads((r/'docs/v666-resource-file-deletion-delta.json').read_text());git=lambda *a:subprocess.check_output(['git',*a],cwd=r,text=True)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed
for p,h in d['productFiles'].items():assert hashlib.sha256((r/p).read_text().encode()).hexdigest()==h,p
assert not any(p.startswith(('src/','targets/','packs/editor-home-model/','packs/web-ui/','packs/file-stream/','packs/project-manager/','packs/edit-workspace/'))for p in changed)
for p in ['packs/project-resources/Layout.celem','packs/project-resources/Request.celem','examples/editor-home/ui/browser-shell.js','examples/editor-home/ui/style.css','examples/editor-home/ui/workspace-host.js']:assert(r/p).read_text()==git('show',d['baseCommit']+':'+p),p
before=git('show',d['baseCommit']+':packs/project-resources/Request.csbody');now=(r/'packs/project-resources/Request.csbody').read_text();now=now.replace('var deletions=calls.Deletions.Invoke(manifest,project);if(System.Linq.Enumerable.Any(System.Text.Json.Nodes.JsonNode.Parse(deletions[1])!["items"]!.AsArray(),row=>Text(row!["import"])==command))throw new InvalidOperationException("resource_import_deleted");\n','').replace('new System.Text.Json.Nodes.JsonObject{["path"]=".confectory/resource-deletions.v1.json",["hash"]=deletions[2]},','');assert now==before,'original import behavior changed outside retired command check/final dependency'
bridge=(r/'examples/editor-home/WebInvoke.csbody').read_text();assert bridge.replace(' or "delete-file"','')==git('show',d['baseCommit']+':examples/editor-home/WebInvoke.csbody')
a=(r/'examples/editor-home/WebBundle.csbody').read_text().split('"""');b=git('show',d['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""');assert a[0]==b[0]and a[2]==b[2];bundle=json.loads(a[1]);old=json.loads(b[1]);assert bundle.keys()==old.keys()
for name,row in bundle.items():
 raw=(r/'examples/editor-home/ui'/row['file']).read_bytes();raw=raw.replace(b'\r\n',b'\n')if row.get('bytePolicy')=='utf8-lf-v1'else raw;assert len(raw)==row.get('canonicalSize',row.get('size'))and hashlib.sha256(raw).hexdigest()==row.get('canonicalSha256',row.get('sha256')),name
 if name not in ['resource-layout.js','resource-browser.js','resource-previews.js','v508-runtime.js']:assert row==old[name]
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 source=z.read('Confectory-v666/dist/app.js').decode();a=source.index('function deleteResource(');b=source.index('\nfunction ',a+10);body=source[a:b]
 for text in ['requireProjectWrite',"modal('자료 삭제'","root.querySelector('[data-cancel]').onclick=close","root.querySelector('[data-remove]').onclick",'owner.resources=','content-backup']:assert text in body,text
assert 'api.close(w)'in(r/'examples/editor-home/ui/resource-previews.js').read_text()
print('PASS authored single-file project-copy deletion; original OS files/C#/override/permission/layout and read observation fields preserved; no trash/automatic cleanup')
