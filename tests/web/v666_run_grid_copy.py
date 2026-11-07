"""Authored ten-percent view overlay over real image dimensions; no renderer/source authority."""
import pathlib,json,subprocess,hashlib,sys,zipfile
r=pathlib.Path(sys.argv[1]);
if(r/'docs/v666-office-active-io-delta.json').exists():
 import runpy
 runpy.run_path(str(r/'tests/web/v666_office_active_io_copy.py'),run_name='__main__');raise SystemExit(0)
d=json.loads((r/'docs/v666-run-grid-delta.json').read_text());paths=set(subprocess.check_output(['git','diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert paths==set(d['productFiles'])
assert paths=={'examples/editor-home/ui/run-grid.js','examples/editor-home/ui/run-windows.js','examples/editor-home/ui/style.css','examples/editor-home/WebBundle.csbody'},paths
for p,h in d['productFiles'].items():assert hashlib.sha256((r/p).read_text().encode()).hexdigest()==h,p
assert hashlib.sha256((r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip').read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip')as z:
 css=z.read('Confectory-v666/dist/style.css').decode();start=css.index('.run-debug-grid{');end=css.index('.run-show-bounds',start);authored=css[start:end]
base=subprocess.check_output(['git','show',d['baseCommit']+':examples/editor-home/ui/style.css'],cwd=r,text=True);assert(r/'examples/editor-home/ui/style.css').read_text()==base+'\n'+authored+'.run-debug-grid[data-run-grid][hidden]{display:none}\n'
s=(r/'examples/editor-home/ui/run-grid.js').read_text()
for bad in ['fetch(','innerHTML','getContext','putImageData','api.','localStorage','setInterval','requestAnimationFrame']:assert bad not in s,bad
m=json.loads((r/'examples/editor-home/WebBundle.csbody').read_text().split('"""')[1])
for name in ['run-windows.js','run-grid.js','style.css']:
 data=(r/'examples/editor-home/ui'/name).read_text().encode();assert m[name]['canonicalSize']==len(data)and m[name]['canonicalSha256']==hashlib.sha256(data).hexdigest()
print('PASS exact authored grid styling and fixed product allowlist; native/source/contracts/permissions/storage and original layout unchanged, no command/pixel mutation in overlay')
