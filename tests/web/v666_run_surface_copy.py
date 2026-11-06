"""Closed reviewed source boundary; output is opt-in and never changes authored project bodies."""
import pathlib,subprocess,json,hashlib,sys,re,zipfile
r=pathlib.Path(sys.argv[1]);
if (r/'docs/v666-run-resolution-delta.json').exists():
 subprocess.run([sys.executable,str(r/'tests/web/v666_run_resolution_copy.py'),str(r)],check=True);raise SystemExit(0)
d=json.loads((r/'docs/v666-run-surface-delta.json').read_text());paths=set(subprocess.check_output(['git','diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert paths==set(d['productFiles']),paths
for p,digest in d['productFiles'].items():assert hashlib.sha256((r/p).read_text().encode()).hexdigest()==digest,p
for prefix in ['src/','targets/']:assert not any(p.startswith(prefix)for p in paths)
for p in ['packs/frame-control/Begin.csbody','packs/frame-control/Complete.csbody','packs/frame-control/Close.csbody','examples/frame-loop/Main.csbody']:
 assert(r/p).read_text()==subprocess.check_output(['git','show',d['baseCommit']+':'+p],cwd=r,text=True),p
s=(r/'packs/frame-control/Open.csbody').read_text();read=s[s.index('if(op=="surface")'):s.index('else if(op=="observe")')];assert'heartbeat='not in read and'Ack('not in read and'seq!=0'in read
s=(r/'packs/project-execution/LaunchConfigured.csbody').read_text();assert'CONFECTORY_SURFACE_'not in s and'confectory-surface-'not in s
s=(r/'packs/web-ui/Open.csbody').read_text();read=s[s.index('string Observation('):s.index('string Dispatch(')];assert'requests.Add'not in read and'Monitor.TryEnter(execution)'in read and'observe-after'in read
s=(r/'examples/editor-home/WebBundle.csbody').read_text();manifest=json.loads(s.split('"""')[1]);
for p in ['run-windows.js','run-surface.js','style.css']:
 b=(r/'examples/editor-home/ui'/p).read_text().encode();assert manifest[p]['canonicalSize']==len(b)and manifest[p]['canonicalSha256']==hashlib.sha256(b).hexdigest(),p
assert'"observations"'in s
s=(r/'examples/editor-home/ui/run-windows.js').read_text();assert"api.view.observe('runSurface'"in s and"api.view.observe('runWindowRead'"in s and'w.runSurfaceAbort?.abort()'in s and"if(!owns(w)||w.runPending||w.runClosing||w.runError)continue;"in s
for bad in ['AudioContext','requestAnimationFrame','performance.now','fetch(']:assert bad not in s,bad
assert hashlib.sha256((r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip').read_bytes()).hexdigest()==d['referenceSha256']
print('PASS bounded opt-in producer/owned existing channel/unretained scoped reads/unchanged ACK and user source; exact manifest/source/reference identities')
