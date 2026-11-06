"""Finite authored viewport mode; unchanged native contracts, source and ownership."""
import pathlib,json,subprocess,hashlib,sys,zipfile
r=pathlib.Path(sys.argv[1]);
if (r/'docs/v666-run-wide-delta.json').exists():
 subprocess.run([sys.executable,str(r/'tests/web/v666_run_wide_copy.py'),str(r)],check=True);sys.exit(0)
d=json.loads((r/'docs/v666-run-auto-delta.json').read_text());paths=set(subprocess.check_output(['git','diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert paths==set(d['productFiles']),paths
assert paths=={'examples/editor-home/ui/run-auto-fit.js','examples/editor-home/ui/run-windows.js','examples/editor-home/WebBundle.csbody'},paths
for p,h in d['productFiles'].items():assert hashlib.sha256((r/p).read_text().encode()).hexdigest()==h,p
assert hashlib.sha256((r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip').read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip')as z:s=z.read('Confectory-v666/dist/app.js').decode();assert "dimensions=settings.resolution==='auto'?[availableWidth,availableHeight]"in s
s=(r/'examples/editor-home/ui/run-windows.js').read_text();assert "new Option('창에 맞춤','auto')"in s and 'new ResizeObserver'in s and 'screen.clientWidth,screen.clientHeight'in s
for token in ['resume','step','start']:assert "query(w,'"+token+"')"not in (r/'examples/editor-home/ui/run-auto-fit.js').read_text()
parts=(r/'examples/editor-home/WebBundle.csbody').read_text().split('"""');m=json.loads(parts[1])
for p in ['run-windows.js','run-auto-fit.js']:
 data=(r/'examples/editor-home/ui'/p).read_text().encode();assert m[p]['canonicalSize']==len(data)and m[p]['canonicalSha256']==hashlib.sha256(data).hexdigest()and m[p]['bytePolicy']=='utf8-lf-v1'
print('PASS original exact CSS viewport fit, pinned canonical resources, only owned UI controller changes; source/native/CAS/permission/audio/layout contracts unchanged')
