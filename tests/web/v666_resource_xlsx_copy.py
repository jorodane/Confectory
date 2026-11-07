"""Finite XLSX editing source inventory; existing byte/permission/public contracts retained."""
import sys,pathlib,json,subprocess,hashlib,zipfile
r=pathlib.Path(sys.argv[1]);
if(r/'docs/v666-resource-webp-delta.json').exists():
 subprocess.run([sys.executable,str(r/'tests/web/v666_resource_webp_copy.py'),str(r)],check=True);raise SystemExit(0)
d=json.loads((r/'docs/v666-resource-xlsx-delta.json').read_text());git=lambda *a:subprocess.check_output(['git',*a],cwd=r,text=True)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed
for name,digest in d['productFiles'].items():assert hashlib.sha256((r/name).read_text().encode()).hexdigest()==digest,name
for path in ['src','targets','packs/file-stream','packs/project-resources/Request.csbody','packs/project-resources/DeletionRecords.csbody','packs/project-resources/pack.cpack','packs/web-ui','packs/browser-host','examples/editor-home/WebInvoke.csbody','examples/editor-home/Main.celem','examples/editor-home/ui/resource-content.js','examples/editor-home/ui/resource-pdf.js','examples/editor-home/ui/resource-images.js','examples/editor-home/ui/resource-browser.js','examples/editor-home/ui/resource-description.js']:
 assert not git('diff','--name-only',d['baseCommit'],'--',path),path
assert set(git('diff','--name-only',d['baseCommit'],'--','packs/editor-home-model').splitlines())=={'packs/editor-home-model/Resources.csbody'}
native=(r/'packs/editor-home-model/Resources.csbody').read_text();assert native.splitlines()[0]==git('show',d['baseCommit']+':packs/editor-home-model/Resources.csbody').splitlines()[0];assert 'DraftSnapshot.Invoke(path,4194304)'in native
p=(r/'examples/editor-home/WebBundle.csbody').read_text().split('"""');before=git('show',d['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""');assert p[0]==before[0]and p[2]==before[2];bundle=json.loads(p[1]);old=json.loads(before[1]);assert set(bundle)-set(old)=={'resource-xlsx.js','resource-xlsx-dom.js','resource-xlsx-worker.js'}
for name,row in bundle.items():
 raw=(r/'examples/editor-home/ui'/row['file']).read_bytes();raw=raw.replace(b'\r\n',b'\n')if row.get('bytePolicy')=='utf8-lf-v1'else raw;assert len(raw)==row.get('canonicalSize',row.get('size'))and hashlib.sha256(raw).hexdigest()==row.get('canonicalSha256',row.get('sha256')),name
 if name in old and 'examples/editor-home/ui/'+row['file']not in changed:assert row==old[name],name
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 original=z.read('Confectory-v666/dist/resource-edit.js').decode();assert all(text in original for text in ['columnIndex','sheetProtection','resource-sheet-cell','XLSX 내용 수정','fullCalcOnLoad','forceFullCalc']);css=z.read('Confectory-v666/dist/style.css').decode();current=(r/'examples/editor-home/ui/style.css').read_text();base=git('show',d['baseCommit']+':examples/editor-home/ui/style.css');assert current.startswith(base)
 for line in current[len(base):].splitlines():
  if line.startswith('.'):assert line in css,line
for name in ['resource-xlsx','resource-xlsx-dom','resource-xlsx-worker','resource-docx','resource-docx-dom','resource-docx-zip','resource-docx-worker','resource-office','resource-office-zip','resource-previews','v508-runtime']:subprocess.run(['node','--check',str(r/('examples/editor-home/ui/'+name+'.js'))],check=True)
print('PASS finite authored XLSX editor/layout, unchanged core/source/permissions/read/transport caps and other renderers; canonical asset bundle and optional private codec inventory')
