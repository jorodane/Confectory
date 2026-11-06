"""Exact declaration reread/input-discard fence; no source/backend/layout mutation."""
import hashlib,json,pathlib,re,subprocess,sys
r=pathlib.Path(sys.argv[1]).resolve()
if(r/'docs/v666-review-guidance-copy.json').exists():
 import runpy
 runpy.run_path(str(pathlib.Path(__file__).with_name('v666_guidance_review_copy.py')),run_name='__main__')
 raise SystemExit(0)
plan=json.loads((r/'docs/v666-declaration-reload-delta.json').read_text())
def old(name):return subprocess.check_output(['git','show',plan['baseCommit']+':'+name],cwd=r,text=True)
for name in {row['path']for row in plan['deltas']}:
 expected=old(name)
 for row in(v for v in plan['deltas']if v['path']==name):assert expected.count(row['before'])==row['count'];expected=expected.replace(row['before'],row['after'])
 assert(r/name).read_text()==expected,name
bundle='examples/editor-home/WebBundle.csbody';expected=old(bundle);name='declarations.js';data=(r/'examples/editor-home/ui'/name).read_text().encode();pattern='("'+re.escape(name)+'":\\{"file":"'+re.escape(name)+'","mime":"text/javascript","bytePolicy":"utf8-lf-v1","canonicalSize":)\\d+(,"canonicalSha256":")[0-9a-f]+(")';expected,count=re.subn(pattern,lambda m:m[1]+str(len(data))+m[2]+hashlib.sha256(data).hexdigest()+m[3],expected);assert count==1 and(r/bundle).read_text()==expected
changed=set(subprocess.check_output(['git','diff','--name-only',plan['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert changed=={row['path']for row in plan['deltas']}|{bundle},changed
for name in ['style.css','workspace.js','workspace-host.js','v508-runtime.js','feature-authoring.js','declaration-icons.js','run-windows.js','finder-content.js','workspace-finder.js']:
 path='examples/editor-home/ui/'+name;assert(r/path).read_text()==old(path),path
source=(r/'examples/editor-home/ui/declarations.js').read_text();before=old('examples/editor-home/ui/declarations.js');start='  async function stage(';end='  for(const field of';assert source[source.index(start):source.index(end)]==before[before.index(start):before.index(end)]
subprocess.run(['node','--check',str(r/'examples/editor-home/ui/declarations.js')],check=True)
print('PASS exact explicit declaration-input discard/epoch/scope fence + canonical resource; original Apply revision/hash, all contracts/Core/targets/packs/permissions/Review/CAS/Undo/layout/Run retained')
