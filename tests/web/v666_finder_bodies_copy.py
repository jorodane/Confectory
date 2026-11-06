"""Reviewed V9 declaration search only; existing native edits and ownership remain intact."""
import hashlib,json,pathlib,re,subprocess,sys,zipfile
r=pathlib.Path(sys.argv[1]).resolve()
if (r/'docs/v666-finder-defaults-delta.json').exists():
 subprocess.run([sys.executable,str(r/'tests/web/v666_finder_defaults_copy.py'),str(r)],check=True);raise SystemExit(0)
plan=json.loads((r/'docs/v666-finder-bodies-delta.json').read_text())
def old(name):return subprocess.check_output(['git','show',plan['baseCommit']+':'+name],cwd=r,text=True)
for name in {row['path']for row in plan['deltas']}:
 expected=old(name)
 for row in (v for v in plan['deltas']if v['path']==name):assert expected.count(row['before'])==row['count'];expected=expected.replace(row['before'],row['after'])
 assert (r/name).read_text()==expected,name
for name,digest in plan['newFiles'].items():assert hashlib.sha256((r/name).read_text().encode()).hexdigest()==digest,name
bundle='examples/editor-home/WebBundle.csbody';expected=old(bundle)
for name in ['finder-content.js','workspace-finder.js','v508-runtime.js']:
 data=(r/'examples/editor-home/ui'/name).read_text().encode();pattern='("'+re.escape(name)+'":\\{"file":"'+re.escape(name)+'","mime":"text/javascript","bytePolicy":"utf8-lf-v1","canonicalSize":)\\d+(,"canonicalSha256":")[0-9a-f]+(")';expected,n=re.subn(pattern,lambda m:m[1]+str(len(data))+m[2]+hashlib.sha256(data).hexdigest()+m[3],expected);assert n==1
expected=expected.replace('"finderContent","editBrowserElement"','"finderContent","finderBody","editBrowserElement"');assert (r/bundle).read_text()==expected
changed=set(subprocess.check_output(['git','diff','--name-only',plan['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());expected_names={row['path']for row in plan['deltas']}|set(plan['newFiles'])|{bundle};tracked_new={n for n in plan['newFiles']if subprocess.run(['git','ls-files','--error-unmatch',n],cwd=r,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0};assert changed==expected_names-(set(plan['newFiles'])-tracked_new),changed
for name in ['find.js','style.css','workspace.js','workspace-host.js','feature-authoring.js','run-windows.js']:
 path='examples/editor-home/ui/'+name;assert (r/path).read_text()==old(path),path
for name in ['finder-content.js','workspace-finder.js','v508-runtime.js']:subprocess.run(['node','--check',str(r/'examples/editor-home/ui'/name)],check=True)
with zipfile.ZipFile(r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip')as z:
 source=z.read('Confectory-v666/dist/app.js').decode();assert all(name in source for name in ['openWorkspaceFinder','workspaceSearchText','workspaceNodeSearchInfo'])
print('PASS exact bounded registered body read/cursor binding/draft-version extension only; original Read, storage/CAS/ReviewConfirm/undo semantics, public execution/override contracts, ownership, layout, completed authoring/Run retained')
