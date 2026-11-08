"""Finite existing DOCX paragraph flow, explicit bounded bytes/private receipts only."""
import sys,pathlib,json,subprocess,hashlib,zipfile,ast
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-resource-docx-parts-delta.json').read_text());git=lambda*a:subprocess.check_output(['git',*a],cwd=r,text=True)
actual=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines())|set(git('ls-files','--others','--exclude-standard','--','src','targets','packs','examples').splitlines());assert actual==set(d['productFiles']),actual^set(d['productFiles'])
for n,h in d['productFiles'].items():assert hashlib.sha256((r/n).read_text().encode()).hexdigest()==h,n
for p in ['src','targets','packs/file-stream','packs/project-resources/Request.csbody','packs/project-resources/DeletionRecords.csbody','packs/web-ui','examples/editor-home/ui/style.css','examples/editor-home/ui/index.html','examples/editor-home/ui/resource-docx-dom.js','examples/editor-home/ui/resource-xlsx.js','examples/editor-home/ui/resource-xlsx-worker.js','examples/editor-home/ui/resource-content.js','examples/editor-home/ui/run-windows.js','examples/editor-home/ui/resource-browser.js','examples/editor-home/ui/resource-descriptions.js','examples/editor-home/ui/assets']:
 assert not git('diff','--name-only',d['baseCommit'],'--',p),p
assert not[n for n in actual if n.endswith(('.celem','.cpack'))]
p=(r/'examples/editor-home/WebBundle.csbody').read_text().split('"""');old=git('show',d['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""');assert p[0]==old[0]and p[2].replace(',"readResourceContentDraftPart","readResourceDocxReceipt"','')==old[2];bundle=json.loads(p[1]);before=json.loads(old[1]);assert set(bundle)-set(before)=={'resource-docx-draft.js'}
for n,row in bundle.items():
 data=(r/'examples/editor-home/ui'/row['file']).read_bytes();data=data.replace(b'\r\n',b'\n')if row.get('bytePolicy')=='utf8-lf-v1'else data;assert len(data)==row.get('canonicalSize',row.get('size'))and hashlib.sha256(data).hexdigest()==row.get('canonicalSha256',row.get('sha256')),n
 if n in before and 'examples/editor-home/ui/'+row['file']not in actual:assert row==before[n],n
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 text=z.read('Confectory-v666/dist/resource-edit.js').decode();assert all(x in text for x in ['changeWordParagraph','protectedParagraph','DOCX 내용 수정','_xmlsignatures/'])
for n in ['resource-docx','resource-docx-draft','resource-docx-worker','resource-docx-zip','resource-office-zip','resource-previews']:subprocess.run(['node','--check',str(r/('examples/editor-home/ui/'+n+'.js'))],check=True)
tree=ast.parse((r/'tools/verify_desktop.py').read_text());branches=[n for n in ast.walk(tree)if isinstance(n,ast.If)and ast.unparse(n.test)=="args.suite == 'resource-docx-parts'"];assert len(branches)==3
calls=[ast.unparse(n)for b in branches for statement in b.body for n in ast.walk(statement)if isinstance(n,ast.Call)]
for token in ["work.run(label + '-resource-docx-parts-boundary'","work.run('packaged-resource-docx-parts-'","work.run('restored-resource-docx-parts-'"]:assert sum(token in x for x in calls)==1,token
print('PASS finite authored DOCX flow and canonical bundle; original core/contracts/layout/permissions/file/import/RPC defaults unchanged; explicit final LF/CRLF and fresh package/full restore routing')
