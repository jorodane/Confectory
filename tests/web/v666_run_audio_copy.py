"""Finite software PCM feature, pinned authored source and unaffected execution contracts."""
import pathlib,json,subprocess,hashlib,sys
r=pathlib.Path(sys.argv[1]);
if (r/'docs/v666-run-presets-delta.json').exists():
 subprocess.run([sys.executable,str(r/'tests/web/v666_run_presets_copy.py'),str(r)],check=True);sys.exit(0)
d=json.loads((r/'docs/v666-run-audio-delta.json').read_text());paths=set(subprocess.check_output(['git','diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert paths==set(d['productFiles']),paths
for p,digest in d['productFiles'].items():assert hashlib.sha256((r/p).read_text().encode()).hexdigest()==digest,p
assert not any(p.startswith(('src/','targets/','packs/web-ui/','packs/project-ai/','packs/development-tools/'))for p in paths)
for p in ['examples/software-output/Main.csbody','examples/resizable-output/Main.csbody','packs/frame-control/Begin.csbody','packs/frame-control/Complete.csbody','packs/project-execution/Surface.csbody','packs/project-execution/ResizeSurface.csbody','packs/run-surface/Open.csbody']:
 assert(r/p).read_text()==subprocess.check_output(['git','show',d['baseCommit']+':'+p],cwd=r,text=True),p
s=(r/'packs/frame-control/Open.csbody').read_text();a=s.index('else if(op=="audio")');b=s.index('else if(op=="observe")',a);assert'heartbeat='not in s[a:b]and'Ack('not in s[a:b]
s=(r/'packs/project-execution/Audio.csbody').read_text();assert'FrameCommand'not in s and'HashData(pcm)'in s and'196608'in s
s=(r/'examples/editor-home/ui/run-audio.js').read_text();assert'AudioContext'in s and'12000'in s and'createBufferSource()'in s and'crypto.subtle.digest'in s
for bad in ['fetch(','innerHTML','createElement','setInterval','api.invoke','requestAnimationFrame']:assert bad not in s,bad
s=(r/'examples/editor-home/WebBundle.csbody').read_text();manifest=json.loads(s.split('"""')[1])
for p in ['run-windows.js','run-audio.js','run-surface.js']:
 data=(r/'examples/editor-home/ui'/p).read_text().encode();assert manifest[p]['canonicalSize']==len(data)and manifest[p]['canonicalSha256']==hashlib.sha256(data).hexdigest(),p
assert hashlib.sha256((r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip').read_bytes()).hexdigest()==d['referenceSha256'];print('PASS explicit bounded PCM producer, scoped read/SHA/range and gesture-only local playback; no frame ACK/heartbeat, source rewrite or permission/layout change')
