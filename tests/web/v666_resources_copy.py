"""Finite V6 delta, authored browser chrome and unchanged source/security primitives."""
import pathlib,sys,json,hashlib,subprocess,zipfile
r=pathlib.Path(sys.argv[1]);
# The next explicit read-only UI slice audits this immutable checkpoint and its closed extension.
if (r/'docs/v666-resource-preview-delta.json').exists():
 subprocess.run([sys.executable,str(r/'tests/web/v666_resource_preview_copy.py'),str(r)],check=True);raise SystemExit(0)
delta=json.loads((r/'docs/v666-resource-import-delta.json').read_text());git=lambda *args:subprocess.check_output(['git',*args],cwd=r,text=True)
changed=set(git('diff','--name-only',delta['baseCommit'],'--','src','targets','packs','examples').splitlines());assert changed==set(delta['productFiles']),changed
for path,digest in delta['productFiles'].items():assert hashlib.sha256((r/path).read_text().encode()).hexdigest()==digest,path
assert not any(path.startswith(('src/','targets/','packs/file-stream/','packs/web-ui/','packs/edit-workspace/','packs/pack-workspace/'))for path in changed)
assert {path for path in changed if path.startswith('packs/project-manager/')}=={'packs/project-manager/pack.cpack','packs/project-manager/ReadIdentity.celem','packs/project-manager/ReadIdentityBody.celem','packs/project-manager/ReadIdentity.csbody'}
main=(r/'examples/editor-home/Main.celem').read_text();before=git('show',delta['baseCommit']+':examples/editor-home/Main.celem');assert main.replace('provide Confectory.EditorHome.Model::Resources with Confectory.EditorHome.Model::ResourcesBody;\n','').replace('provide Confectory.ProjectResources::Request with Confectory.ProjectResources::RequestBody;\n','').replace('provide Confectory.ProjectManager::ReadIdentity with Confectory.ProjectManager::ReadIdentityBody;\n','')==before
now=(r/'examples/editor-home/WebBundle.csbody').read_text().split('"""');old=git('show',delta['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""');assert now[0]==old[0]and now[2].replace('new[]{"projectResources","runWindow"','new[]{"runWindow"')==old[2]and'\n'not in now[1]
bundle=json.loads(now[1]);original=json.loads(old[1]);assert set(bundle)-set(original)=={'resource-browser.js'}and not set(original)-set(bundle)
for name,row in bundle.items():
 if name in ['resource-browser.js','v508-runtime.js','workspace-host.js','style.css']:
  raw=(r/'examples/editor-home/ui'/name).read_text().encode();assert row['canonicalSha256']==hashlib.sha256(raw).hexdigest()and row['canonicalSize']==len(raw)
 else:assert row==original[name],name
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==delta['referenceSha256']
with zipfile.ZipFile(reference)as z:
 source=z.read('Confectory-v666/dist/app.js').decode();styles=z.read('Confectory-v666/dist/style.css').decode();rules=[line for line in styles.splitlines()if line.startswith(('.resource-browser-status','.resource-filename'))]
 current=(r/'examples/editor-home/ui/style.css').read_text();assert current==git('show',delta['baseCommit']+':examples/editor-home/ui/style.css')+'\n/* Authored v666 resource browser status and filenames. */\n'+'\n'.join(rules)+'\n'
 start=source.index('function fitResourceFileNames');end=source.index('function refreshResourceViews',start);assert source[start:end]in(r/'examples/editor-home/ui/resource-browser.js').read_text()
print('PASS independent bounded resource pack and active-context adapter only; original file-name layout/chrome, existing signatures/override/source/security/CAS/ReviewConfirm primitives remain unchanged')
