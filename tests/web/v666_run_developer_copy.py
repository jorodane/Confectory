"""Exact original Run developer chrome and read-only frame facts; no backend/permission changes."""
import pathlib,json,hashlib,subprocess,sys,zipfile,re
r=pathlib.Path(sys.argv[1]);
if (r/'docs/v666-run-surface-delta.json').exists():
 subprocess.run([sys.executable,str(r/'tests/web/v666_run_surface_copy.py'),str(r)],check=True);raise SystemExit(0)
d=json.loads((r/'docs/v666-run-developer-delta.json').read_text())
def old(p):return subprocess.check_output(['git','show',d['baseCommit']+':'+p],cwd=r,text=True)
paths=set(subprocess.check_output(['git','diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert paths==set(d['productFiles'])=={'examples/editor-home/ui/run-windows.js','examples/editor-home/ui/style.css','examples/editor-home/WebBundle.csbody'},paths
for name,digest in d['productFiles'].items():assert hashlib.sha256((r/name).read_text().encode()).hexdigest()==digest,name
with zipfile.ZipFile(r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip')as z:
 css=z.read('Confectory-v666/dist/style.css').decode()
 for row in d['referenceCss']:assert row in css
assert (r/'examples/editor-home/ui/style.css').read_text()==old('examples/editor-home/ui/style.css')+'\n/* Authored v666 Run developer menu and diagnostic overlay. */\n'+'\n'.join(d['referenceCss'])+'\n'
p='examples/editor-home/ui/run-windows.js';before=old(p);after=(r/p).read_text();a=' async function query(';b=' function show(';assert before[before.index(a):before.index(b)]==after[after.index(a):after.index(b)]
assert 'if(!owns(w)||w.runPending||w.runClosing||w.runError)continue;'in after
for token in ['api.view.call(',"query(w,'start'","query(w,'control'"]:assert before.count(token)==after.count(token),token
for token in ['AudioContext','requestAnimationFrame','performance.now','fetch(','localStorage']:assert token not in after
assert (r/'packs/editor-home-model/RunWindows.csbody').read_text()==old('packs/editor-home-model/RunWindows.csbody')
p='examples/editor-home/WebBundle.csbody';expected=old(p)
for name,mime in [('run-windows.js','text/javascript'),('style.css','text/css')]:
 data=(r/'examples/editor-home/ui'/name).read_text().encode();pattern=r'("'+re.escape(name)+r'":\{"file":"'+re.escape(name)+r'","mime":"'+re.escape(mime)+r'","bytePolicy":"utf8-lf-v1","canonicalSize":)\d+(,"canonicalSha256":")[a-f0-9]+(")';expected,n=re.subn(pattern,lambda m:m[1]+str(len(data))+m[2]+hashlib.sha256(data).hexdigest()+m[3],expected);assert n==1
assert(r/p).read_text()==expected
print('PASS exact original developer chrome/read-only diagnostics; native process/lease/ACK/source permissions/ABI/CAS unchanged; no simulated renderer/audio, implicit execution or settings persistence')
