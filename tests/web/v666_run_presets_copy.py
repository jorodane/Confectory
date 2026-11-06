"""Fixed v666 preset flow, owner-only private storage and unchanged execution contracts."""
import pathlib,json,subprocess,hashlib,sys
r=pathlib.Path(sys.argv[1]);
if (r/'docs/v666-run-auto-delta.json').exists():
 subprocess.run([sys.executable,str(r/'tests/web/v666_run_auto_copy.py'),str(r)],check=True);sys.exit(0)
d=json.loads((r/'docs/v666-run-presets-delta.json').read_text());paths=set(subprocess.check_output(['git','diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert paths==set(d['productFiles']),paths
for p,h in d['productFiles'].items():assert hashlib.sha256((r/p).read_text().encode()).hexdigest()==h,p
assert not any(p.startswith(('src/','targets/','packs/frame-control/','packs/project-execution/','packs/run-surface/','packs/run-audio/','packs/project-ai/','packs/development-tools/'))for p in paths)
for directory in ['examples/resizable-output','examples/software-output','examples/audio-output']:
 assert not subprocess.check_output(['git','diff',d['baseCommit'],'--',directory],cwd=r,text=True)
s=(r/'packs/editor-home-model/RunPresets.csbody').read_text();assert'calls.Commit.Invoke(root,new[]{relative},new[]{snapshot[2]}'in s and'run-resolution-presets/'in s and'calls.Identity.Invoke'in s and'run_preset_command_reused'in s
for bad in ['calls.Launch','calls.Control','calls.Resize','File.Delete','Review','Confirm','GetEnvironmentVariable']:assert bad not in s,bad
s=(r/'examples/editor-home/ui/run-presets.js').read_text();assert"api.view.observe('runPresetRead'"in s and"api.view.call('runPresets'"in s
for bad in ['innerHTML','fetch(','localStorage','setInterval','surface-size']:assert bad not in s,bad
bundle=(r/'examples/editor-home/WebBundle.csbody').read_text();m=json.loads(bundle.split('"""')[1]);
for p in ['run-presets.js','run-windows.js','run-audio.js','run-surface.js']:
 data=(r/'examples/editor-home/ui'/p).read_text().encode();assert m[p]['canonicalSize']==len(data)and m[p]['canonicalSha256']==hashlib.sha256(data).hexdigest(),p
assert'"runPresetRead"'in bundle and'"runPresets"'in bundle
assert hashlib.sha256((r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip').read_bytes()).hexdigest()==d['referenceSha256'];print('PASS original preset controls, dedicated context-owned private CAS/replay store, inert names; source/permission/override/frame/size/audio contracts and authored layout unchanged')
