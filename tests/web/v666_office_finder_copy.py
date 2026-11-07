"""Closed office search/navigation delta; native contracts/rights and authored design retained."""
import pathlib,sys,json,hashlib,subprocess,zipfile
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-office-finder-delta.json').read_text());git=lambda *a:subprocess.check_output(['git',*a],cwd=r,text=True)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed
for name,value in d['productFiles'].items():assert hashlib.sha256((r/name).read_text().encode()).hexdigest()==value,name
assert not any(n.startswith(('src/','targets/'))or n.endswith('.celem')for n in changed)
s=(r/'examples/editor-home/WebBundle.csbody').read_text().split('"""');old=git('show',d['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""');assert s[0]==old[0]and s[2]==old[2]and'\n'not in s[1];now=json.loads(s[1]);before=json.loads(old[1]);assert now.keys()==before.keys()
for name in now:
 if name in ['workspace-finder.js','workspace-host.js','v508-runtime.js','style.css']:
  raw=(r/'examples/editor-home/ui'/name).read_text().encode();assert now[name]['canonicalSize']==len(raw)and now[name]['canonicalSha256']==hashlib.sha256(raw).hexdigest()
 else:assert now[name]==before[name],name
name='packs/workspace-3d/ui/manifest.json';now=json.loads((r/name).read_text());before=json.loads(git('show',d['baseCommit']+':'+name));assert set(now)-set(before)=={'finder.js'}and not set(before)-set(now)
for name in now:
 raw=(r/'packs/workspace-3d/ui'/name).read_text().encode();assert len(raw)==now[name]['size']and hashlib.sha256(raw).hexdigest()==now[name]['sha256'],name
 if name not in ['adapter.js','finder.js']:assert now[name]==before[name],name
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 original=z.read('Confectory-v666/dist/style.css').decode();rules=[line for line in original.splitlines()if line.startswith(('.workspace-find-zones','.workspace-find-matches','.workspace-find-helper','.workspace-find-worker'))]
 current=(r/'examples/editor-home/ui/style.css').read_text();baseline=git('show',d['baseCommit']+':examples/editor-home/ui/style.css');assert current==baseline+'\n/* Authored v666 office finder sections. */\n'+'\n'.join(rules)+'\n'
print('PASS authored office finder layout, sealed display pack/bundle; all native source/contract/permission/IO/CAS/ReviewConfirm and existing renderer are unchanged')
