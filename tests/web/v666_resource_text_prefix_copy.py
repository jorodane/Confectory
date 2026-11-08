"""Finite prefix extension; unchanged storage, ownership, editing and layout contracts."""
import sys,pathlib,json,subprocess,hashlib,zipfile,ast
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-resource-text-prefix-delta.json').read_text());git=lambda *a:subprocess.check_output(['git',*a],cwd=r,text=True)
expected={'examples/editor-home/WebBundle.csbody','examples/editor-home/WebInvoke.csbody','examples/editor-home/ui/resource-previews.js','examples/editor-home/ui/resource-text-prefix.js','packs/editor-home-model/Resources.csbody','packs/project-resources/Layout.csbody','packs/project-resources/README.md'}
assert set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines())==set(d['productFiles'])==expected
for name,digest in d['productFiles'].items():assert hashlib.sha256((r/name).read_text().encode()).hexdigest()==digest,name
for name in ['src','targets','packs/file-stream','packs/project-manager','packs/project-resources/Request.csbody','packs/project-execution','packs/run-surface','packs/frame-control','packs/run-audio','examples/editor-home/ui/style.css','examples/editor-home/ui/workspace-host.js','examples/editor-home/ui/v508-runtime.js','examples/editor-home/ui/resource-content.js','examples/editor-home/ui/resource-description.js','examples/editor-home/ui/resource-browser.js','examples/editor-home/ui/resource-images.js','examples/editor-home/ui/resource-svg.js','examples/editor-home/ui/resource-office.js','examples/editor-home/ui/resource-docx.js','examples/editor-home/ui/resource-xlsx.js','examples/editor-home/ui/resource-pdf.js','examples/editor-home/ui/resource-layout.js']:
 assert not git('diff','--name-only',d['baseCommit'],'--',name),name
assert not git('diff','--name-only',d['baseCommit'],'--','*.celem','*.cpack')
p=(r/'examples/editor-home/WebBundle.csbody').read_text().split('"""');before=git('show',d['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""');assert p[0]==before[0]and p[2]==before[2].replace('JsonArray("readProjectResource",','JsonArray("previewProjectResourceText","readProjectResource",');bundle=json.loads(p[1]);prior=json.loads(before[1]);assert set(bundle)==set(prior)|{'resource-text-prefix.js'}
for name,row in bundle.items():
 raw=(r/'examples/editor-home/ui'/row['file']).read_bytes();raw=raw.replace(b'\r\n',b'\n')if row.get('bytePolicy')=='utf8-lf-v1'else raw;assert len(raw)==row.get('canonicalSize',row.get('size'))and hashlib.sha256(raw).hexdigest()==row.get('canonicalSha256',row.get('sha256')),name
 if name not in ['resource-previews.js','resource-text-prefix.js']:assert row==prior[name],name
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 source=z.read('Confectory-v666/dist/resource-preview.js').decode();assert 'blob.slice(0,1024*1024).arrayBuffer()'in source and '파일의 앞부분 1 MB까지 표시합니다.'in source
tree=ast.parse((r/'tools/verify_desktop.py').read_text());branches=[n for n in ast.walk(tree)if isinstance(n,ast.If)and ast.unparse(n.test)=="args.suite == 'resource-prefix'"];assert len(branches)==3
calls=[ast.unparse(n)for branch in branches for statement in branch.body for n in ast.walk(statement)if isinstance(n,ast.Call)]
for token in ["work.run(label + '-resource-prefix-boundary'","work.run('packaged-resource-prefix'","work.run('restored-resource-prefix'"]:assert sum(token in call for call in calls)==1,token
for file in ['resource-previews.js','resource-text-prefix.js']:subprocess.run(['node','--check',str(r/'examples/editor-home/ui'/file)],check=True)
print('PASS exact seven-file prefix scope, original first1MiB rule, immutable storage/public/permission/layout/editing contracts, canonical assets and three final suite branches')
