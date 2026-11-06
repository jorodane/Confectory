"""Reviewed typed-default search projection; every write/ownership contract stays exact."""
import hashlib,json,pathlib,re,subprocess,sys
r=pathlib.Path(sys.argv[1]).resolve()
if (r/'docs/v666-declaration-reload-delta.json').exists():
 subprocess.run([sys.executable,str(r/'tests/web/v666_declaration_reload_copy.py'),str(r)],check=True);raise SystemExit(0)
plan=json.loads((r/'docs/v666-finder-defaults-delta.json').read_text())
def old(name):return subprocess.check_output(['git','show',plan['baseCommit']+':'+name],cwd=r,text=True)
for name in {row['path']for row in plan['deltas']}:
 expected=old(name)
 for row in (v for v in plan['deltas']if v['path']==name):assert expected.count(row['before'])==row['count'];expected=expected.replace(row['before'],row['after'])
 assert (r/name).read_text()==expected,name
bundle='examples/editor-home/WebBundle.csbody';expected=old(bundle);name='finder-content.js';data=(r/'examples/editor-home/ui'/name).read_text().encode();pattern='("'+re.escape(name)+'":\\{"file":"'+re.escape(name)+'","mime":"text/javascript","bytePolicy":"utf8-lf-v1","canonicalSize":)\\d+(,"canonicalSha256":")[0-9a-f]+(")';expected,count=re.subn(pattern,lambda m:m[1]+str(len(data))+m[2]+hashlib.sha256(data).hexdigest()+m[3],expected);assert count==1 and(r/bundle).read_text()==expected
changed=set(subprocess.check_output(['git','diff','--name-only',plan['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert changed=={row['path']for row in plan['deltas']}|{bundle},changed
command='packs/editor-home-model/TableCommand.csbody';marker=' if(action=="browser-elements")';assert (r/command).read_text().split(marker,1)[1]==old(command).split(marker,1)[1]
for name in ['style.css','workspace.js','workspace-host.js','workspace-finder.js','v508-runtime.js','feature-authoring.js','run-windows.js','find.js']:
 path='examples/editor-home/ui/'+name;assert(r/path).read_text()==old(path),path
subprocess.run(['node','--check',str(r/'examples/editor-home/ui/finder-content.js')],check=True)
subprocess.run([sys.executable,str(r/'tests/web/v666_finder_defaults_spec.py'),str(r)],check=True)
print('PASS exact search-only default JSON projection + truthful text-budget status; generic Browser APIs, all contracts/Core/targets, source/CAS/Review/Undo/permissions/layout/Run retained')
