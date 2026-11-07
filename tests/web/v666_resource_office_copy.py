"""Closed authored Office display; unchanged native ownership/read/save contracts."""
import sys,pathlib,json,hashlib,subprocess,zipfile
r=pathlib.Path(sys.argv[1]);
if(r/'docs/v666-resource-pdf-delta.json').exists():
 subprocess.run([sys.executable,str(r/'tests/web/v666_resource_pdf_copy.py'),str(r)],check=True);raise SystemExit(0)
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-resource-office-delta.json').read_text());git=lambda *a:subprocess.check_output(['git',*a],cwd=r,text=True)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed
assert changed=={'examples/editor-home/WebBundle.csbody','examples/editor-home/ui/resource-previews.js','examples/editor-home/ui/resource-office.js','examples/editor-home/ui/resource-office-worker.js','examples/editor-home/ui/resource-office-zip.js','examples/editor-home/ui/style.css'}
for name,digest in d['productFiles'].items():assert hashlib.sha256((r/name).read_text().encode()).hexdigest()==digest,name
for name in ['src','targets','packs','examples/editor-home/WebInvoke.csbody','examples/editor-home/Main.celem','examples/editor-home/ui/resource-content.js','examples/editor-home/ui/resource-images.js','examples/editor-home/ui/resource-browser.js','examples/editor-home/ui/resource-layout.js','examples/editor-home/ui/v508-runtime.js','examples/editor-home/ui/workspace-host.js']:assert not git('diff','--name-only',d['baseCommit'],'--',name),name
parts=(r/'examples/editor-home/WebBundle.csbody').read_text().split('"""');prior=git('show',d['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""');assert parts[0]==prior[0]and parts[2]==prior[2];bundle=json.loads(parts[1]);old=json.loads(prior[1]);assert set(bundle)==set(old)|{'resource-office.js','resource-office-worker.js','resource-office-zip.js'}
for name,row in bundle.items():
 raw=(r/'examples/editor-home/ui'/row['file']).read_bytes();raw=raw.replace(b'\r\n',b'\n')if row.get('bytePolicy')=='utf8-lf-v1'else raw;assert len(raw)==row.get('canonicalSize',row.get('size'))and hashlib.sha256(raw).hexdigest()==row.get('canonicalSha256',row.get('sha256')),name
 if name not in ['resource-previews.js','style.css','resource-office.js','resource-office-worker.js','resource-office-zip.js']:assert row==old[name]
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 text=z.read('Confectory-v666/dist/resource-preview.js').decode();css=z.read('Confectory-v666/dist/style.css').decode();now=(r/'examples/editor-home/ui/style.css').read_text();before=git('show',d['baseCommit']+':examples/editor-home/ui/style.css');assert now.startswith(before)
 for line in now[len(before):].splitlines():
  if line.startswith('.'):assert line in css,line
 for token in ['word/document.xml','xl/workbook.xml','content.xml','워크시트당 최대 200행','문서 내용 미리보기','슬라이드 ']:assert token in text,token
preview=(r/'examples/editor-home/ui/resource-previews.js').read_text();previous=git('show',d['baseCommit']+':examples/editor-home/ui/resource-previews.js');start=preview.index(' const read=async');end=preview.index("    const mime=",start);oldstart=previous.index(' const read=async');oldend=previous.index("    const mime=",oldstart);assert preview[start:end]==previous[oldstart:oldend]
assert 'fetch('not in(r/'examples/editor-home/ui/resource-office-worker.js').read_text()
print('PASS six-file authored Office text/value display; original native read proof, storage/permissions/C#/override/ReviewConfirm/CAS and completed image/text editors unchanged')
