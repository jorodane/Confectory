"""Separate display pack, pinned upstream assets and unchanged domain boundaries."""
import hashlib,json,pathlib,subprocess,sys,re
from zipfile import ZipFile
r=pathlib.Path(sys.argv[1]);base='3a1d6df3643ebad6a64931249963a71c406061b3'
root=r/'packs/workspace-3d/ui';manifest=json.loads((root/'manifest.json').read_text())
for name,row in manifest.items():
 data=(root/name).read_text().encode();assert len(data)==row['size']and hashlib.sha256(data).hexdigest()==row['sha256']
with ZipFile(r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip')as z:
 for name in ['office-world.js','office-actors.js','voxel-character.js','assets/three.module-0.160.1.js']:
  text=z.read('Confectory-v666/dist/'+name).decode();text=re.sub(r"\./(office-world|office-actors|voxel-character)\.[0-9a-f]+\.js",r'./\1.js',text)
  assert(root/name).read_text()==text,name
 assert(root/'assets/three-LICENSE.txt').read_text()==z.read('Confectory-v666/dist/assets/three-LICENSE.txt').decode()
original=subprocess.check_output(['git','show',base+':examples/editor-home/ui/workspace-host.js'],cwd=r,text=True)
current=(r/'examples/editor-home/ui/workspace-host.js').read_text();assert 'filter(row=>row.owned===true)'in current and 'helpers:[]'in current
adapter=(root/'adapter.js').read_text();assert 'canWrite:()=>false,canArrange:()=>false,canInspectTask:()=>false'in adapter
assert not any(value in adapter for value in ['fetch(','view.call(','requestAnimationFrame(','startAI','runProject','prepareWorker','confirmDraft'])
expected={'examples/editor-home/WebBundle.csbody','examples/editor-home/WebBundleBody.celem','examples/editor-home/project.cpack','examples/editor-home/ui/workspace-host.js','examples/editor-home/ui/v508-runtime.js'}
changed=set(subprocess.check_output(['git','diff','--name-only',base,'--','src','targets','packs','examples'],cwd=r,text=True).splitlines())
assert {p for p in changed if not p.startswith('packs/workspace-3d/')}==expected,changed
print('PASS independent display pack/local pinned v666 renderer/license; only owned declared rooms; no Worker/ACL/dispatch/source/runtime/CAS/Review/Confirm changes')
