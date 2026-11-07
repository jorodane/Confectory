"""Exact authored resource-entry inventory; unchanged storage, editor and permission contracts."""
import sys,pathlib,json,subprocess,hashlib,zipfile
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-resource-entry-delta.json').read_text());git=lambda *a:subprocess.check_output(['git',*a],cwd=r,text=True)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles'])=={'examples/editor-home/WebBundle.csbody','examples/editor-home/ui/resource-browser.js','examples/editor-home/ui/resource-layout.js'}
for name,digest in d['productFiles'].items():assert hashlib.sha256((r/name).read_text().encode()).hexdigest()==digest,name
for name in ['src','targets','packs','examples/editor-home/WebInvoke.csbody','examples/editor-home/ui/style.css','examples/editor-home/ui/app.js','examples/editor-home/ui/v508-runtime.js','examples/editor-home/ui/workspace-host.js','examples/editor-home/ui/resource-previews.js','examples/editor-home/ui/resource-images.js','examples/editor-home/ui/resource-description.js','examples/editor-home/ui/resource-content.js','examples/editor-home/ui/resource-selection.js','examples/editor-home/ui/resource-docx.js','examples/editor-home/ui/resource-xlsx.js','examples/editor-home/ui/resource-pdf.js']:
 assert not git('diff','--name-only',d['baseCommit'],'--',name),name
now=(r/'examples/editor-home/ui/resource-browser.js').read_text();old=git('show',d['baseCommit']+':examples/editor-home/ui/resource-browser.js');start=now.index(' async function choose(');end=now.index(' const selection=',start);assert now[start:end]==old[old.index(' async function choose('):old.index(' const selection=')]
parts=(r/'examples/editor-home/WebBundle.csbody').read_text().split('"""');prior=git('show',d['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""');assert parts[0]==prior[0]and parts[2]==prior[2];bundle=json.loads(parts[1]);before=json.loads(prior[1]);assert set(bundle)==set(before)
for name,row in bundle.items():
 raw=(r/'examples/editor-home/ui'/row['file']).read_bytes();raw=raw.replace(b'\r\n',b'\n')if row.get('bytePolicy')=='utf8-lf-v1'else raw;assert len(raw)==row.get('canonicalSize',row.get('size'))and hashlib.sha256(raw).hexdigest()==row.get('canonicalSha256',row.get('sha256')),name
 if name not in ['resource-browser.js','resource-layout.js']:assert row==before[name],name
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 app=z.read('Confectory-v666/dist/app.js').decode()
 assert "root.oncontextmenu=event=>{if(event.target.closest('[data-resource-id]'))return;event.preventDefault();event.stopPropagation();resourceCreateMenu(w,event)}"in app
 assert 'resourceCreateMenu(w,event,id)'in app and "[['자료 추가',"in app and "['새 카테고리',"in app
for name in ['resource-browser','resource-layout']:subprocess.run(['node','--check',str(r/('examples/editor-home/ui/'+name+'.js'))],check=True)
print('PASS authored blank-list/ProjectPack entry; exact three-file display inventory; native storage, permission, final CAS, ReviewConfirm, source, image decoders, editors, CSS and public contracts unchanged')
