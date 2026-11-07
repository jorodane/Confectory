"""Final bounded display-metadata source and authored-layout inventory."""
import sys,pathlib,json,subprocess,hashlib,zipfile
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-resource-description-delta.json').read_text());git=lambda *a:subprocess.check_output(['git',*a],cwd=r,text=True)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed
for name,digest in d['productFiles'].items():assert hashlib.sha256((r/name).read_text().encode()).hexdigest()==digest,name
for path in ['src','targets','packs/file-stream','packs/project-resources/Request.csbody','packs/project-resources/DeletionRecords.csbody','packs/project-resources/pack.cpack','packs/web-ui','packs/edit-workspace','packs/editor-home-model','examples/editor-home/ui/style.css','examples/editor-home/ui/resource-content.js','examples/editor-home/ui/resource-pdf.js','examples/editor-home/ui/resource-office.js','examples/editor-home/ui/resource-layout.js']:
 assert not git('diff','--name-only',d['baseCommit'],'--',path),path
p=(r/'examples/editor-home/WebBundle.csbody').read_text().split('"""');old=git('show',d['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""');assert p[0]==old[0]and p[2]==old[2];bundle=json.loads(p[1]);before=json.loads(old[1]);assert set(bundle)-set(before)=={'resource-description.js'}
for name,row in bundle.items():
 raw=(r/'examples/editor-home/ui'/row['file']).read_bytes();raw=raw.replace(b'\r\n',b'\n')if row.get('bytePolicy')=='utf8-lf-v1'else raw;assert len(raw)==row.get('canonicalSize',row.get('size'))and hashlib.sha256(raw).hexdigest()==row.get('canonicalSha256',row.get('sha256')),name
 if name in before and 'examples/editor-home/ui/'+row['file']not in changed:assert row==before[name],name
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 original=z.read('Confectory-v666/dist/app.js').decode()
 for text in ['data-resource-description','aria-label="자료 설명"','maxlength="1000"','이 자료에 대한 설명',"item.description||''"]:assert text in original,text
for name in ['resource-description','resource-browser','resource-previews','workspace-host','v508-runtime']:subprocess.run(['node','--check',str(r/('examples/editor-home/ui/'+name+'.js'))],check=True)
print('PASS bounded optional description metadata, exact authored description/search surfaces, full bundle SHA, unchanged byte store/source/contracts/permission/renderers')
